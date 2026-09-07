from django.contrib import admin, messages
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from .models import Event, Ticket
from .services.email_service import send_ticket_email


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_formateada', 'costo_bono', 'cupos_texto', 'boletas_vendidas', 'vista_previa', 'activo')
    list_display_links = ('titulo',)
    list_filter = (
        ('activo', ChoicesDropdownFilter),
        ('categoria', ChoicesDropdownFilter),
        'fecha',
    )
    search_fields = ('titulo', 'id', 'lugar')
    search_help_text = 'Busque por título, ID corto o lugar.'
    readonly_fields = ('boletas_vendidas', 'vista_previa_grande')

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
    list_display = ('numero_ticket', 'evento', 'comprador_nombre', 'comprador_email', 'monto_pagado', 'estado_pago', 'ticket_enviado')
    list_display_links = ('numero_ticket',)
    list_filter = (
        ('estado_pago', ChoicesDropdownFilter),
        ('seleccion_tipo', ChoicesDropdownFilter),
        ('ticket_enviado', ChoicesDropdownFilter),
        'evento',
    )
    search_fields = ('comprador_nombre', 'comprador_email', 'codigo_verificacion')
    search_help_text = 'Busque por nombre, email o código de verificación de la boleta.'
    readonly_fields = ('codigo_verificacion', 'donacion_id')
    actions = ('marcar_como_enviado', 'enviar_boleta_por_email')

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
    )

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
