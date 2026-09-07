import csv

from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from .models import Event, Ticket
from .services.email_service import send_payment_reminder, send_ticket_email


class AsistioListFilter(admin.SimpleListFilter):
    """Filtro "¿Asistió?" para el changelist de boletas.

    No usamos BooleanFieldListFilter sobre checkin_en (DateTimeField):
    ese filtro convierte el parámetro a True/False y la consulta
    checkin_en__exact='1' explota como IncorrectLookupParameters
    (redirect ?e=1). Un SimpleListFilter con isnull es correcto y da
    etiquetas claras al personal.
    """

    title = 'Asistió'
    parameter_name = 'asistio'

    def lookups(self, request, model_admin):
        return (
            ('si', 'Sí — con entrada registrada'),
            ('no', 'No — sin entrada'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.filter(checkin_en__isnull=False)
        if self.value() == 'no':
            return queryset.filter(checkin_en__isnull=True)
        return queryset


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_formateada', 'costo_bono', 'cupos_texto', 'boletas_vendidas', 'asistencia_barra', 'vista_previa', 'activo')
    list_display_links = ('titulo',)
    list_filter = (
        ('activo', ChoicesDropdownFilter),
        ('categoria', ChoicesDropdownFilter),
        'fecha',
    )
    search_fields = ('titulo', 'id', 'lugar')
    search_help_text = 'Busque por título, ID corto o lugar.'
    readonly_fields = ('boletas_vendidas', 'vista_previa_grande')

    class Media:
        css = {'all': ('admin/asistencia.css',)}

    fieldsets = (
        ('Datos del evento', {
            'fields': ('id', 'titulo', 'categoria', 'descripcion'),
            'description': '💡 El <b>ID</b> es el nombre corto que usa el sistema (ej. <code>bingo-2026</code>, <code>rifa</code>). '
                           'Escríbalo en minúsculas y sin espacios; no lo cambie después de crear el evento.',
        }),
        ('📅 Fecha y lugar', {
            'fields': ('fecha', 'hora', 'lugar'),
            'description': 'Deje la fecha vacía para campañas permanentes (ej. recolecta de pañales).',
        }),
        ('🖼️ Imagen del evento', {
            'fields': ('vista_previa_grande', 'imagen', 'imagen_url'),
            'description': '📸 Suba una imagen desde su computadora (opción recomendada). '
                           'La URL externa queda como alternativa avanzada. La imagen se optimiza automáticamente para la web.',
        }),
        ('🎟️ Boletas y cupos', {
            'fields': ('costo_bono', 'cupo_maximo', 'cupo_disponible', 'numeracion_min', 'numeracion_max', 'permite_seleccion_numero', 'boletas_vendidas'),
            'description': 'Si el evento no tiene límite de cupo, deje "cupo máximo" vacío. '
                           '"Cupo disponible" se muestra al público: réstelo a medida que se venden boletas.',
        }),
        ('Estado', {
            'fields': ('activo',),
            'description': 'Desmarque para ocultar el evento del sitio web sin borrar su información.',
        }),
    )

    @admin.display(description='Fecha', ordering='fecha')
    def fecha_formateada(self, obj):
        if not obj.fecha:
            return '— (permanente)'
        return obj.fecha.strftime('%d %b %Y')

    @admin.display(description='Cupo')
    def cupos_texto(self, obj):
        if obj.cupo_maximo is None:
            return 'Sin límite'
        disp = obj.cupo_disponible if obj.cupo_disponible is not None else obj.cupo_maximo
        return f'{disp} de {obj.cupo_maximo}'

    @admin.display(description='Vendidas')
    def boletas_vendidas(self, obj):
        return obj.tickets.filter(estado_pago='pagado').count()

    @admin.display(description='Asistencia (entradas / pagadas)')
    def asistencia_barra(self, obj):
        """Barra de progreso con entradas registradas vs boletas pagadas.
        Enlaza al listado de boletas del evento filtrado por asistidas."""
        pagadas = obj.tickets.filter(estado_pago='pagado').count()
        asistidas = obj.tickets.filter(checkin_en__isnull=False).count()
        pct = round(asistidas / pagadas * 100) if pagadas else 0
        pct = max(0, min(100, pct))
        enlace = reverse('admin:events_ticket_changelist')
        url = f'{enlace}?evento__id__exact={obj.pk}&asistio=si'
        return format_html(
            '<a class="asistencia-link" href="{}" title="Ver boletas con entrada registrada">'
            '<span class="asistencia-track"><span class="asistencia-bar" style="width:{}%"></span></span>'
            '<span class="asistencia-num">{} / {}</span></a>',
            url, pct, asistidas, pagadas,
        )

    @admin.display(description='Imagen')
    def vista_previa(self, obj):
        url = None
        if obj and obj.pk:
            url = obj.imagen.url if obj.imagen else obj.imagen_url
        if url:
            return format_html(
                '<img src="{}" style="width:56px;height:40px;object-fit:cover;border-radius:6px;" />',
                url,
            )
        return '—'

    @admin.display(description='Vista previa de la imagen')
    def vista_previa_grande(self, obj):
        if obj and obj.pk:
            url = obj.imagen.url if obj.imagen else obj.imagen_url
            if url:
                return format_html(
                    '<img src="{}" style="max-width:420px;max-height:240px;object-fit:cover;'
                    'border-radius:12px;border:1px solid #ddd;" />',
                    url,
                )
        return format_html('<p style="color:#9ca3af;">Aún no hay imagen para este evento.</p>')


@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = ('numero_ticket', 'evento', 'comprador_nombre', 'comprador_email', 'monto_pagado', 'estado_pago', 'ticket_enviado', 'asistio_badge')
    list_display_links = ('numero_ticket',)
    list_filter = (
        ('estado_pago', ChoicesDropdownFilter),
        ('seleccion_tipo', ChoicesDropdownFilter),
        ('ticket_enviado', ChoicesDropdownFilter),
        AsistioListFilter,
        'evento',
    )
    search_fields = ('comprador_nombre', 'comprador_email', 'codigo_verificacion')
    search_help_text = 'Busque por nombre, email o código de verificación de la boleta.'
    readonly_fields = ('codigo_verificacion', 'donacion_id', 'checkin_en', 'checkin_por')
    actions = ('marcar_como_enviado', 'enviar_boleta_por_email', 'recordar_pago_pendiente', 'exportar_csv')

    fieldsets = (
        ('Boleta', {
            'fields': ('evento', 'numero_ticket', 'seleccion_tipo', 'codigo_verificacion'),
            'description': 'El código de verificación lo recibe el comprador para consultar su boleta. No se puede modificar.',
        }),
        ('Comprador', {
            'fields': ('comprador_nombre', 'comprador_email', 'comprador_telefono'),
        }),
        ('Pago', {
            'fields': ('monto_pagado', 'estado_pago', 'referencia_wompi', 'donacion_id', 'ticket_enviado'),
        }),
        ('🚪 Check-in (solo lectura)', {
            'fields': ('checkin_en', 'checkin_por'),
            'description': 'La entrada se registra desde la pantalla '
                           '<a href="checkin/">Check-in en puerta</a> escaneando el QR de la boleta.',
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        propias = [
            path(
                'checkin/',
                self.admin_site.admin_view(self.checkin_view),
                name='events_ticket_checkin',
            ),
        ]
        return propias + urls

    @admin.display(description='Asistió', boolean=True)
    def asistio_badge(self, obj):
        """Marca ✔/✘ de asistencia (columna ordenable por checkin_en vía
        ordering del campo; el booleano dibuja el check verde de Django)."""
        return obj.asistio

    @admin.action(description='⬇️ Exportar boletas a CSV (Excel)')
    def exportar_csv(self, request, queryset):
        """Lista de boletas (idealmente filtradas por evento) para imprimir
        o compartir con el equipo en puerta. Delimitador ';' porque el
        Excel configurado en español usa coma como separador decimal y
        ';' como separador de listas — con ',' abriría en una sola columna.
        """
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        fecha = timezone.localdate().strftime('%Y-%m-%d')
        response['Content-Disposition'] = f'attachment; filename=boletas-{fecha}.csv'
        # BOM para que Excel detecte UTF-8 (tildes y ñ correctas)
        response.write('\ufeff')
        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Evento', 'Boleta N.º', 'Comprador', 'Email', 'Estado',
            'Valor (COP)', 'Código de verificación', 'Entrada registrada',
            'Registrada por',
        ])
        for t in queryset.select_related('evento', 'checkin_por'):
            writer.writerow([
                t.evento.titulo,
                t.numero_ticket,
                t.comprador_nombre,
                t.comprador_email,
                t.get_estado_pago_display(),
                t.monto_pagado,
                t.codigo_verificacion,
                timezone.localtime(t.checkin_en).strftime('%Y-%m-%d %H:%M') if t.checkin_en else 'No',
                t.checkin_por.get_username() if t.checkin_por else '',
            ])
        return response

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['checkin_url'] = reverse('admin:events_ticket_checkin')
        return super().changelist_view(request, extra_context)

    # ── Check-in en puerta ────────────────────────────────────────────
    # Flujo Post/Redirect/Get: el POST registra y redirige con ?ok=1 para
    # que F5 no registre la entrada dos veces. La búsqueda usa GET con
    # ?codigo=, así el escáner de QR (que actúa como teclado) puede
    # autofiltrar sin pasos extra.

    def checkin_view(self, request):
        """Pantalla para registrar la entrada de una boleta el día del evento."""
        codigo = (request.GET.get('codigo') or request.POST.get('codigo') or '').strip().upper()
        ticket = Ticket.objects.select_related('evento').filter(codigo_verificacion=codigo).first()

        if request.method == 'POST':
            return self._checkin_post(request, ticket, codigo)

        contexto = {
            'codigo': codigo,
            'ticket': ticket,
            'registrado_ok': request.GET.get('ok') == '1',
            'title': 'Check-in en puerta',
            'opts': Ticket._meta,
        }
        return render(request, 'admin/events/ticket/checkin.html', contexto)

    def _checkin_post(self, request, ticket, codigo):
        destino = reverse('admin:events_ticket_checkin')
        query = f'?codigo={codigo}' if codigo else ''

        if ticket is None:
            messages.error(request, f'No existe una boleta con el código «{codigo or "(vacío)"}».')
            return HttpResponseRedirect(destino)

        if ticket.estado_pago == 'cancelado':
            messages.error(
                request,
                f'La boleta N.º {ticket.numero_ticket} está CANCELADA: no se permite registrar entrada.',
            )
            return HttpResponseRedirect(f'{destino}{query}')

        if ticket.asistio:
            messages.warning(
                request,
                f'La entrada de la boleta N.º {ticket.numero_ticket} ya estaba registrada '
                f'el {timezone.localtime(ticket.checkin_en):%d/%m/%Y %H:%M} '
                f'por {ticket.checkin_por.get_username() if ticket.checkin_por else "—"}. '
                'No se registró nada nuevo.',
            )
            return HttpResponseRedirect(f'{destino}{query}')

        if ticket.estado_pago == 'pendiente' and request.POST.get('autorizar') != '1':
            messages.warning(
                request,
                f'La boleta N.º {ticket.numero_ticket} está PENDIENTE de pago. Marque '
                '"autorizar entrada" si decide dejarla pasar igualmente.',
            )
            return HttpResponseRedirect(f'{destino}{query}')

        ticket.checkin_en = timezone.now()
        ticket.checkin_por = request.user
        ticket.save(update_fields=['checkin_en', 'checkin_por'])
        messages.success(
            request,
            f'✅ Entrada registrada: boleta N.º {ticket.numero_ticket} — {ticket.comprador_nombre}.',
        )
        return HttpResponseRedirect(f'{destino}{query}&ok=1' if query else f'{destino}?ok=1')

    @admin.action(description='Marcar como boleta enviada')
    def marcar_como_enviado(self, request, queryset):
        actualizados = queryset.update(ticket_enviado=True)
        self.message_user(request, f'{actualizados} boletas marcadas como enviadas.', level=messages.SUCCESS)

    @admin.action(description='📧 Enviar boleta por email al comprador')
    def enviar_boleta_por_email(self, request, queryset):
        """Envía la boleta oficial (con código y QR) al correo del comprador.

        Errores por ticket (SMTP caído, email inválido) no interrumpen el
        lote: se cuentan y se informan al final. Solo los envíos exitosos
        marcan `ticket_enviado=True`.
        """
        enviadas, fallidas = 0, 0
        for ticket in queryset:
            if send_ticket_email(ticket):
                ticket.ticket_enviado = True
                ticket.save(update_fields=['ticket_enviado'])
                enviadas += 1
            else:
                fallidas += 1

        if enviadas and not fallidas:
            self.message_user(
                request,
                f'📧 {enviadas} boleta(s) enviada(s) por email correctamente.',
                level=messages.SUCCESS,
            )
        elif enviadas and fallidas:
            self.message_user(
                request,
                f'📧 {enviadas} enviada(s); ⚠️ {fallidas} con error (revise el correo del comprador o los logs SMTP).',
                level=messages.WARNING,
            )
        else:
            self.message_user(
                request,
                'No se pudo enviar ninguna boleta. Verifique la configuración de email (SMTP) en el servidor.',
                level=messages.ERROR,
            )

    @admin.action(description='⏰ Recordar pago pendiente por email')
    def recordar_pago_pendiente(self, request, queryset):
        """Envía el recordatorio de pago a las boletas seleccionadas que
        siguen 'pendiente'. Las boletas pagadas/canceladas se omiten con
        aviso para evitar correos fuera de contexto."""
        elegibles = queryset.filter(estado_pago='pendiente')
        omitidas = queryset.count() - elegibles.count()

        enviadas, fallidas = 0, 0
        for ticket in elegibles:
            if send_payment_reminder(ticket):
                enviadas += 1
            else:
                fallidas += 1

        prefijo = f'{omitidas} boleta(s) omitida(s) por no estar pendientes. ' if omitidas else ''
        if enviadas and not fallidas:
            self.message_user(
                request, f'{prefijo}⏰ {enviadas} recordatorio(s) enviado(s).',
                level=messages.SUCCESS,
            )
        elif enviadas and fallidas:
            self.message_user(
                request,
                f'{prefijo}⏰ {enviadas} enviado(s); ⚠️ {fallidas} con error (revise logs SMTP).',
                level=messages.WARNING,
            )
        elif fallidas:
            self.message_user(
                request,
                'No se pudo enviar ningún recordatorio. Verifique la configuración SMTP.',
                level=messages.ERROR,
            )
        else:
            self.message_user(
                request,
                f'{prefijo}No hay boletas pendientes entre las seleccionadas.',
                level=messages.INFO,
            )
