"""
Cifras públicas de la Fundación para la página "Nuestros números".

Consumido por el endpoint público GET /api/stats/ (core.views.public_stats).
Garantías de privacidad: SOLO agregados (sumas, conteos, promedios) — nunca
nombres, correos, referencias de pago ni datos de contacto de donantes.
Las cifras corresponden a donaciones CONFIRMADAS por la pasarela
(estado 'completado'), nunca promesas pendientes: lo publicado debe ser
verificable ante donantes y aliados.

Consultas de solo lectura y ligeras (agregados sobre fechas). Si el tráfico
del endpoint creciera, puede añadirse cache_page(60) en la vista sin tocar
este módulo.
"""
import datetime as dt
from datetime import date

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from beneficiaries.models import Beneficiary
from donations.models import Donation, Sponsorship

from .metrics import MESES_CORTOS_ES, formato_cop, formato_cop_corto


def _aware(d: date) -> dt.datetime:
    """Fecha → datetime consciente de zona (hora local de la Fundación)."""
    return timezone.make_aware(dt.datetime(d.year, d.month, d.day))


def _next_month(year: int, month: int) -> date:
    if month == 12:
        return date(year + 1, 1, 1)
    return date(year, month + 1, 1)


def cifras_publicas() -> dict:
    """
    Calcula las cifras agregadas publicables. Nunca lanza sobre tablas vacías:
    los agregados devuelven 0/None y se normalizan a 0.
    """
    today = timezone.localdate()

    # ── Totales globales (solo confirmadas) ──────────────────────────────
    agg = Donation.objects.filter(estado='completado').aggregate(
        total=Sum('monto'), cantidad=Count('id')
    )
    recaudado_total = agg['total'] or 0
    donaciones_count = agg['cantidad'] or 0
    donacion_promedio = (
        round(recaudado_total / donaciones_count) if donaciones_count else 0
    )

    # ── Beneficiarios ────────────────────────────────────────────────────
    beneficiarios_activos = Beneficiary.objects.filter(activo=True).count()
    beneficiarios_apadrinados = Beneficiary.objects.filter(
        activo=True, apadrinado=True
    ).count()
    ciudades_atendidas = (
        Beneficiary.objects.filter(activo=True)
        .exclude(ciudad__isnull=True)
        .exclude(ciudad__exact='')
        .values('ciudad')
        .distinct()
        .count()
    )

    # ── Apadrinamientos ──────────────────────────────────────────────────
    apadrinamientos_activos = Sponsorship.objects.filter(estado='activo').count()

    # ── Serie de 12 meses (una sola consulta agrupada) ───────────────────
    meses = []
    y, m = today.year, today.month
    for _ in range(12):
        meses.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    meses.reverse()

    inicio = _aware(date(meses[0][0], meses[0][1], 1))
    fin = _aware(_next_month(today.year, today.month))

    filas = (
        Donation.objects.filter(
            estado='completado', creado_en__gte=inicio, creado_en__lt=fin
        )
        .annotate(mes_trunc=TruncMonth('creado_en'))
        .values('mes_trunc')
        .annotate(total=Sum('monto'), cantidad=Count('id'))
    )
    por_mes = {}
    for fila in filas:
        if fila['mes_trunc'] is None:
            continue
        ld = timezone.localdate(fila['mes_trunc'])
        por_mes[(ld.year, ld.month)] = (fila['total'] or 0, fila['cantidad'])

    max_total = max((por_mes.get(k, (0, 0))[0] for k in meses), default=0)
    serie_mensual = []
    for (yy, mm) in meses:
        total, cantidad = por_mes.get((yy, mm), (0, 0))
        # Altura de barra en % relativa al mejor mes; mínimo 5% para que los
        # meses de poco recaudo sigan siendo visibles (igual que el panel admin).
        pct = round(total / max_total * 100) if max_total > 0 else 0
        if 0 < pct < 5:
            pct = 5
        serie_mensual.append({
            'mes': MESES_CORTOS_ES[mm - 1],
            'anio': yy,
            'total': total,
            'total_fmt': formato_cop(total),
            'total_fmt_corto': formato_cop_corto(total),
            'cantidad': cantidad,
            'pct': pct,
            'es_actual': (yy == today.year and mm == today.month),
        })

    return {
        'recaudado_total': recaudado_total,
        'recaudado_total_fmt': formato_cop(recaudado_total),
        'donaciones_count': donaciones_count,
        'donacion_promedio': donacion_promedio,
        'donacion_promedio_fmt': formato_cop(donacion_promedio),
        'beneficiarios_activos': beneficiarios_activos,
        'beneficiarios_apadrinados': beneficiarios_apadrinados,
        'ciudades_atendidas': ciudades_atendidas,
        'apadrinamientos_activos': apadrinamientos_activos,
        'serie_mensual': serie_mensual,
        'actualizado_en': timezone.now().isoformat(),
    }
