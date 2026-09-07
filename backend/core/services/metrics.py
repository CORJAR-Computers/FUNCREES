"""
Servicio de cifras de la Fundación.

Fuente única de verdad para el "Resumen de la Fundación": lo consumen el
panel del admin (template tag `funcrees_dashboard`) y el resumen semanal
por correo (comando `send_weekly_digest`), garantizando que ambos muestren
siempre los mismos números.

Todas las consultas son de solo lectura y ligeras (agregados sobre columnas
con índice natural de fecha).
"""
import datetime as dt
from datetime import date
from urllib.parse import quote

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from beneficiaries.models import Beneficiary
from contact.models import ContactMessage
from donations.models import Donation, Sponsorship
from events.models import Event, Ticket

MESES_ES = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
MESES_CORTOS_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


def _next_month(year: int, month: int) -> date:
    if month == 12:
        return date(year + 1, 1, 1)
    return date(year, month + 1, 1)


def _aware(d: date) -> dt.datetime:
    """Fecha → datetime consciente de zona (hora local de la Fundación)."""
    return timezone.make_aware(dt.datetime(d.year, d.month, d.day))


def formato_cop(value) -> str:
    """Formato colombiano de dinero: 12345678 → '$12.345.678'"""
    try:
        return '$' + f'{int(value):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return '$0'


def formato_cop_corto(value) -> str:
    """Formato abreviado para etiquetas de gráficos: 1200000 → '$1,2 M', 45000 → '$45 mil'"""
    try:
        v = int(value or 0)
    except (TypeError, ValueError):
        return '$0'
    if v >= 1_000_000:
        s = f'{v / 1_000_000:.1f}'.rstrip('0').rstrip('.').replace('.', ',')
        return f'${s} M'
    if v >= 1_000:
        return f'${v // 1000} mil'
    return f'${v}'


def _whatsapp_del_donante(nombre: str, referencia: str, telefono_cifrado) -> dict:
    """
    Construye el enlace wa.me de seguimiento para una donación pendiente.

    Devuelve {'wa_url': ...} si el donante dejó teléfono legible, o
    {'wa_url': None} en caso contrario (sin teléfono, cifrado ilegible por
    rotación de ENCRYPTION_KEY, o número extranjero sin código de país).
    Nunca lanza: un teléfono roto no debe romper el panel.
    """
    tel = None
    try:
        if telefono_cifrado:
            tel = str(telefono_cifrado)
    except Exception:
        tel = None

    if not tel:
        return {'wa_url': None}

    # Normalizar: solo dígitos; incluir código de país 57 si es un celular
    # colombiano de 10 dígitos (wa.me exige código internacional).
    digitos = ''.join(c for c in tel if c.isdigit())
    if len(digitos) == 10 and digitos.startswith(('3', '60')):
        digitos = '57' + digitos
    if not digitos.startswith('57') or len(digitos) < 10:
        return {'wa_url': None}

    msg = (
        f"Hola {nombre}, somos FUNCREES Colombia. Tu donación con referencia "
        f"{referencia} está pendiente de confirmación por la pasarela Wompi. "
        "¿Podemos ayudarte con algo?"
    )
    return {'wa_url': f"https://wa.me/{digitos}?text={quote(msg)}"}


def resumen_fundacion() -> dict:
    """
    Calcula todas las cifras del resumen del mes en curso y acumuladas.
    Nunca lanza: los conteos sobre tablas vacías devuelven 0/None.
    """
    today = timezone.localdate()
    month_start = date(today.year, today.month, 1)
    next_month_start = _next_month(today.year, today.month)
    if today.month == 1:
        prev_start = date(today.year - 1, 12, 1)
        prev_next_start = date(today.year, 1, 1)
    else:
        prev_start = date(today.year, today.month - 1, 1)
        prev_next_start = month_start

    completado = Q(estado='completado')

    # ── Donaciones del mes actual vs mes anterior ────────────────────────
    mes_actual = Donation.objects.filter(creado_en__gte=_aware(month_start), creado_en__lt=_aware(next_month_start))
    mes_previo = Donation.objects.filter(creado_en__gte=_aware(prev_start), creado_en__lt=_aware(prev_next_start))

    agg_actual = mes_actual.filter(completado).aggregate(total=Sum('monto'), cantidad=Count('id'))
    agg_previo = mes_previo.filter(completado).aggregate(total=Sum('monto'), cantidad=Count('id'))
    pendientes = mes_actual.filter(estado__in=['pendiente', 'procesando']).count()

    # ── Pagos por confirmar: pendientes con más de 1 hora ───────────────
    # El webhook de Wompi confirma en segundos; si sigue pendiente tras una
    # hora, algo requiere atención manual (sección del panel del admin).
    limite = timezone.now() - dt.timedelta(hours=1)
    por_confirmar_qs = (
        Donation.objects.filter(estado__in=['pendiente', 'procesando'], creado_en__lt=limite)
        .order_by('creado_en')[:8]
    )
    ahora = timezone.now()
    por_confirmar = [
        {
            'id': d.id,
            'referencia': d.referencia,
            'donante_nombre': d.donante_nombre,
            'monto': d.monto,
            'monto_fmt': formato_cop(d.monto),
            'estado': d.estado,
            'horas': max(1, int((ahora - d.creado_en).total_seconds() // 3600)),
            **_whatsapp_del_donante(d.donante_nombre, d.referencia, d.donante_telefono_cifrado),
        }
        for d in por_confirmar_qs
    ]
    por_confirmar_total = Donation.objects.filter(
        estado__in=['pendiente', 'procesando'], creado_en__lt=limite
    ).count()

    # ── Serie mensual (últimos 6 meses) para el gráfico del panel ────────
    # Una sola consulta agrupada por mes (TruncMonth respeta la zona horaria
    # local, America/Bogota). Solo donaciones completadas, igual que el total
    # del mes: la directiva compara cifras confirmadas, no promesas.
    meses_serie = []
    y, m = today.year, today.month
    for _ in range(6):
        meses_serie.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    meses_serie.reverse()

    inicio_serie = _aware(date(meses_serie[0][0], meses_serie[0][1], 1))
    filas_por_mes = (
        Donation.objects.filter(
            completado,
            creado_en__gte=inicio_serie,
            creado_en__lt=_aware(next_month_start),
        )
        .annotate(mes_trunc=TruncMonth('creado_en'))
        .values('mes_trunc')
        .annotate(total=Sum('monto'), cantidad=Count('id'))
    )
    totales_por_mes = {}
    for fila in filas_por_mes:
        if fila['mes_trunc'] is None:
            continue
        ld = timezone.localdate(fila['mes_trunc'])
        totales_por_mes[(ld.year, ld.month)] = (fila['total'] or 0, fila['cantidad'])

    max_total = max(
        (totales_por_mes.get(key, (0, 0))[0] for key in meses_serie),
        default=0,
    )
    serie_mensual = []
    for (yy, mm) in meses_serie:
        total, cantidad = totales_por_mes.get((yy, mm), (0, 0))
        # Altura de la barra en % relativa al mejor mes (escala común).
        pct = round(total / max_total * 100) if max_total > 0 else 0
        if 0 < pct < 5:
            pct = 5  # los meses con poco recaudo siguen siendo visibles
        serie_mensual.append({
            'mes': MESES_CORTOS_ES[mm - 1],
            'mes_nombre': f'{MESES_ES[mm - 1]} {yy}',
            'total': total,
            'total_fmt': formato_cop(total),
            'total_fmt_corto': formato_cop_corto(total),
            'cantidad': cantidad,
            'pct': pct,
            'es_actual': (yy == today.year and mm == today.month),
        })

    total_actual = agg_actual['total'] or 0
    total_previo = agg_previo['total'] or 0

    # Variación % vs mes anterior (None = sin base de comparación)
    variacion = None
    if total_previo > 0:
        variacion = round((total_actual - total_previo) / total_previo * 100)
    if variacion is None or variacion == 0:
        variacion_direccion = 'flat'
    elif variacion > 0:
        variacion_direccion = 'up'
    else:
        variacion_direccion = 'down'

    # ── Mensajes de contacto recientes ───────────────────────────────────
    mensajes = list(
        ContactMessage.objects.order_by('-creado_en').values(
            'id', 'nombre', 'email', 'tipo', 'leido', 'respondido', 'creado_en'
        )[:5]
    )
    no_leidos = ContactMessage.objects.filter(leido=False).count()

    # ── Apadrinamientos ──────────────────────────────────────────────────
    apadrinamientos = Sponsorship.objects.aggregate(
        activos=Count('id', filter=Q(estado='activo')),
        total=Count('id'),
    )
    monto_mensual = (
        Sponsorship.objects.filter(estado='activo').aggregate(s=Sum('monto_mensual'))['s'] or 0
    )

    # ── Cifras generales ─────────────────────────────────────────────────
    recaudado_total = Donation.objects.filter(completado).aggregate(s=Sum('monto'))['s'] or 0
    beneficiarios_activos = Beneficiary.objects.filter(activo=True).count()
    beneficiarios_apadrinados = Beneficiary.objects.filter(apadrinado=True).count()
    eventos_activos = Event.objects.filter(activo=True).count()
    boletas_pagadas = Ticket.objects.filter(estado_pago='pagado').count()

    # ── Boletas del mes (usa creado_en, añadido en migración events/0006) ─
    boletas_actual_q = Ticket.objects.filter(
        creado_en__gte=_aware(month_start), creado_en__lt=_aware(next_month_start)
    )
    boletas_previo_q = Ticket.objects.filter(
        creado_en__gte=_aware(prev_start), creado_en__lt=_aware(prev_next_start)
    )
    boletas_vendidas_mes = boletas_actual_q.count()
    boletas_pagadas_mes = boletas_actual_q.filter(estado_pago='pagado').count()
    recaudo_boletas_mes = (
        boletas_actual_q.filter(estado_pago='pagado').aggregate(s=Sum('monto_pagado'))['s'] or 0
    )
    boletas_pagadas_previo = boletas_previo_q.filter(estado_pago='pagado').count()

    variacion_boletas = None
    if boletas_pagadas_previo > 0:
        variacion_boletas = round(
            (boletas_pagadas_mes - boletas_pagadas_previo) / boletas_pagadas_previo * 100
        )
    if variacion_boletas is None or variacion_boletas == 0:
        variacion_boletas_direccion = 'flat'
    elif variacion_boletas > 0:
        variacion_boletas_direccion = 'up'
    else:
        variacion_boletas_direccion = 'down'

    # Cola de cobro: pendientes con más de 48 horas (el recordatorio semanal
    # automático ya les escribió; aquí quedan visibles para acción manual).
    limite_boletas = timezone.now() - dt.timedelta(hours=48)
    boletas_pendientes_filtro = Q(estado_pago='pendiente')
    por_cobrar_qs = (
        Ticket.objects.filter(boletas_pendientes_filtro, creado_en__lt=limite_boletas)
        .select_related('evento')
        .order_by('creado_en')[:8]
    )
    boletas_por_cobrar = [
        {
            'id': t.id,
            'numero': t.numero_ticket,
            'evento_id': t.evento_id,
            'evento_titulo': t.evento.titulo,
            'comprador': t.comprador_nombre,
            'monto_fmt': formato_cop(t.monto_pagado),
            'dias': max(1, int((ahora - t.creado_en).total_seconds() // 86400)),
            'enviado': t.ticket_enviado,
        }
        for t in por_cobrar_qs
    ]
    boletas_por_cobrar_total = Ticket.objects.filter(
        boletas_pendientes_filtro, creado_en__lt=limite_boletas
    ).count()
    boletas_pendientes_total = Ticket.objects.filter(estado_pago='pendiente').count()
    # Pagadas cuyo email con el código aún no se ha enviado (acción del panel)
    boletas_sin_enviar = Ticket.objects.filter(estado_pago='pagado', ticket_enviado=False).count()

    # Recaudo por evento (top 5 con boletas registradas)
    eventos_con_boletas = (
        Event.objects.annotate(
            boletas_vendidas=Count('tickets'),
            boletas_pagadas_n=Count('tickets', filter=Q(tickets__estado_pago='pagado')),
            recaudo=Sum('tickets__monto_pagado', filter=Q(tickets__estado_pago='pagado')),
        )
        .filter(boletas_vendidas__gt=0)
        .order_by('-recaudo', '-boletas_vendidas')[:5]
    )
    boletas_por_evento = [
        {
            'id': e.id,
            'titulo': e.titulo,
            'vendidas': e.boletas_vendidas,
            'pagadas': e.boletas_pagadas_n,
            'recaudo_fmt': formato_cop(e.recaudo or 0),
        }
        for e in eventos_con_boletas
    ]

    return {
        'mes_nombre': f'{MESES_ES[today.month - 1]} {today.year}',
        # Donaciones
        'total_mes': total_actual,
        'cantidad_mes': agg_actual['cantidad'] or 0,
        'total_previo': total_previo,
        'variacion': variacion,
        'variacion_abs': abs(variacion) if variacion is not None else None,
        'variacion_direccion': variacion_direccion,
        'donaciones_pendientes': pendientes,
        # Pagos por confirmar (atención manual)
        'por_confirmar': por_confirmar,
        'por_confirmar_total': por_confirmar_total,
        # Gráfico: recaudado por mes (últimos 6 meses)
        'serie_mensual': serie_mensual,
        # Contacto
        'mensajes': mensajes,
        'no_leidos': no_leidos,
        # Apadrinamientos
        'apadrinamientos_activos': apadrinamientos['activos'],
        'apadrinamientos_total': apadrinamientos['total'],
        'monto_mensual_apadrinamientos': monto_mensual,
        # Generales
        'recaudado_total': recaudado_total,
        'beneficiarios_activos': beneficiarios_activos,
        'beneficiarios_apadrinados': beneficiarios_apadrinados,
        'eventos_activos': eventos_activos,
        'boletas_pagadas': boletas_pagadas,
        # Boletas del mes (métricas por fecha)
        'boletas_vendidas_mes': boletas_vendidas_mes,
        'boletas_pagadas_mes': boletas_pagadas_mes,
        'boletas_pagadas_previo': boletas_pagadas_previo,
        'recaudo_boletas_mes': recaudo_boletas_mes,
        'variacion_boletas': variacion_boletas,
        'variacion_boletas_abs': abs(variacion_boletas) if variacion_boletas is not None else None,
        'variacion_boletas_direccion': variacion_boletas_direccion,
        'boletas_pendientes_total': boletas_pendientes_total,
        'boletas_por_cobrar': boletas_por_cobrar,
        'boletas_por_cobrar_total': boletas_por_cobrar_total,
        'boletas_sin_enviar': boletas_sin_enviar,
        'boletas_por_evento': boletas_por_evento,
    }
