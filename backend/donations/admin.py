import csv

from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from .models import Donation, Sponsorship
from .services.email_service import send_donation_reminder
from .services.wompi import get_transaction_by_reference
from .views import procesar_transaccion_wompi


class PendientesWompiFilter(SimpleListFilter):
    """
    Filtro rápido "Pagos por confirmar": donaciones en pendiente/procesando
    con más de 1 hora de creadas (el webhook de Wompi confirma en segundos;
    si sigue pendiente tras una hora, algo requiere atención manual).
    """
    title = 'pagos por confirmar'
    parameter_name = 'pendientes'

    def lookups(self, request, model_admin):
        return (('si', '⏳ Pendientes de confirmar'),)

    def queryset(self, request, queryset):
        if self.value() == 'si':
            from django.utils import timezone
            import datetime as dt
            limite = timezone.now() - dt.timedelta(hours=1)
            return queryset.filter(estado__in=['pendiente', 'procesando'], creado_en__lt=limite)
        return queryset


@admin.register(Donation)
class DonationAdmin(ModelAdmin):
    ESTADO_COLORES = {
        'pendiente': '#d97706',
        'procesando': '#2563eb',
        'completado': '#16a34a',
        'fallido': '#dc2626',
        'reembolsado': '#7c3aed',
    }

    list_display = ('referencia', 'donante_nombre', 'monto_formateado', 'tipo', 'estado_badge', 'vista_pendiente', 'revision_badge', 'certificado_enviado', 'creado_en')
    list_display_links = ('referencia',)
    list_filter = (
        ('estado', ChoicesDropdownFilter),
        ('tipo', ChoicesDropdownFilter),
        ('certificado_enviado', ChoicesDropdownFilter),
        ('revision_requerida', ChoicesDropdownFilter),
        PendientesWompiFilter,
        'creado_en',
    )
    search_fields = ('referencia', 'donante_nombre', 'donante_email', 'referencia_pasarela')
    search_help_text = 'Busque por referencia, nombre, email del donante o referencia de Wompi.'
    date_hierarchy = 'creado_en'
    list_per_page = 25
    readonly_fields = (
        'donante_documento_cifrado', 'donante_telefono_cifrado', 'referencia_pasarela',
        'wompi_response', 'creado_en', 'ip_origen',
    )
    actions = ('exportar_csv', 'verificar_con_wompi', 'recordar_pago_pendiente')

    fieldsets = (
        ('Resumen del pago', {
            'fields': ('referencia', 'tipo', 'monto', 'estado'),
        }),
        ('Datos del donante', {
            'fields': ('donante_nombre', 'donante_email', 'donante_documento_cifrado', 'donante_telefono_cifrado'),
            'description': '🔒 Documento y teléfono se guardan cifrados (Ley 1581 de Habeas Data).',
        }),
        ('Pasarela de pago (Wompi)', {
            'fields': ('metodo_pago', 'referencia_pasarela', 'wompi_response'),
            'classes': ('collapse',),
        }),
        ('Otros datos', {
            'fields': ('beneficiario', 'certificado_enviado', 'revision_requerida', 'autorizacion_datos', 'ip_origen', 'creado_en'),
            'classes': ('collapse',),
        }),
    )

    @admin.action(description='🔄 Verificar con Wompi (consulta el estado real del pago)')
    def verificar_con_wompi(self, request, queryset):
        """
        Consulta a Wompi el estado real de cada donación pendiente.

        Usa el mismo pipeline del webhook (procesar_transaccion_wompi):
        idempotencia, mapeo de estados y envío de certificado si aprueba.
        Si Wompi aún no reporta la transacción, la donación no se toca.
        """
        verificables = queryset.filter(estado__in=['pendiente', 'procesando'])
        omitidas = queryset.count() - verificables.count()

        aprobadas, rechazadas, sin_info = 0, 0, 0
        for donation in verificables:
            tx = get_transaction_by_reference(donation.referencia)
            if not tx:
                sin_info += 1
                continue
            estado_wompi = tx.get('status', '')
            procesar_transaccion_wompi(donation.referencia, tx)
            if estado_wompi == 'APPROVED':
                aprobadas += 1
            elif estado_wompi in ('DECLINED', 'VOIDED', 'ERROR'):
                rechazadas += 1
            else:
                sin_info += 1

        partes = []
        if aprobadas:
            partes.append(f'{aprobadas} aprobada(s) ✅')
        if rechazadas:
            partes.append(f'{rechazadas} rechazada(s) ❌')
        if sin_info:
            partes.append(f'{sin_info} sin información en Wompi todavía')
        if omitidas:
            partes.append(f'{omitidas} omitida(s) (ya estaban confirmadas)')

        if not partes:
            self.message_user(
                request,
                'No hay donaciones pendientes por verificar en la selección.',
                level=messages.WARNING,
            )
            return

        nivel = messages.SUCCESS if aprobadas and not rechazadas else messages.WARNING
        self.message_user(request, 'Resultado de la verificación: ' + ' · '.join(partes), level=nivel)

    @admin.display(description='Monto', ordering='monto')
    def monto_formateado(self, obj):
        return '$' + f'{obj.monto:,.0f}'.replace(',', '.')

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        color = self.ESTADO_COLORES.get(obj.estado, '#6b7280')
        return format_html('<span style="color:{};font-weight:600;">● {}</span>', color, obj.get_estado_display())

    @admin.display(description='⚠️ Revisión', boolean=True)
    def revision_badge(self, obj):
        """True si el webhook detectó un monto alterado (revisar manual)."""
        return obj.revision_requerida

    @admin.display(description='Atención')
    def vista_pendiente(self, obj):
        """Aviso visual para donaciones sin confirmar tras más de 1 hora."""
        if obj.estado in ('pendiente', 'procesando'):
            from django.utils import timezone
            import datetime as dt
            if obj.creado_en and obj.creado_en < timezone.now() - dt.timedelta(hours=1):
                return format_html(
                    '<span style="color:#d97706;font-weight:700;" title="Sin confirmación de Wompi tras más de 1 hora">⏳ por confirmar</span>'
                )
            return format_html('<span style="color:#6b7280;">recién creada</span>')
        return '—'

    @admin.action(description='⏰ Recordar pago pendiente (email al donante)')
    def recordar_pago_pendiente(self, request, queryset):
        """
        Envía el recordatorio de aporte pendiente a cada donante seleccionado.

        Omite silenciosamente las donaciones ya confirmadas/fallidas (enviar
        ese correo sería confuso) y reporta el conteo. Un fallo SMTP por fila
        no interrumpe el lote (send_donation_reminder nunca lanza).
        """
        pendientes = queryset.filter(estado__in=['pendiente', 'procesando'])
        omitidas = queryset.count() - pendientes.count()

        if not pendientes.exists():
            self.message_user(
                request,
                'Ninguna donación de la selección está pendiente: no se envió ningún correo.',
                level=messages.WARNING,
            )
            return

        enviados, fallidos = 0, 0
        for donation in pendientes:
            if send_donation_reminder(donation):
                enviados += 1
            else:
                fallidos += 1

        partes = [f'{enviados} recordatorio(s) enviado(s) ✅']
        if fallidos:
            partes.append(f'{fallidos} con error de envío ❌')
        if omitidas:
            partes.append(f'{omitidas} omitida(s) (no están pendientes)')

        nivel = messages.SUCCESS if not fallidos else messages.WARNING
        self.message_user(request, 'Resultado del recordatorio: ' + ' · '.join(partes), level=nivel)

    @admin.action(description='Exportar seleccionadas a CSV (Excel)')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=donaciones.csv'
        # BOM para que Excel detecte UTF-8 (tildes y ñ correctas)
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['Referencia', 'Donante', 'Email', 'Monto (COP)', 'Tipo', 'Estado', 'Beneficiario', 'Certificado enviado', 'Fecha'])
        for d in queryset:
            writer.writerow([
                d.referencia,
                d.donante_nombre,
                d.donante_email,
                d.monto,
                d.get_tipo_display(),
                d.get_estado_display(),
                d.beneficiario.nombre if d.beneficiario else '',
                'Sí' if d.certificado_enviado else 'No',
                d.creado_en.strftime('%Y-%m-%d %H:%M'),
            ])
        return response


@admin.register(Sponsorship)
class SponsorshipAdmin(ModelAdmin):
    list_display = ('donante_nombre', 'beneficiario', 'monto_mensual', 'tipo', 'estado', 'fecha_inicio')
    list_display_links = ('donante_nombre',)
    list_filter = (
        ('estado', ChoicesDropdownFilter),
        ('tipo', ChoicesDropdownFilter),
        'fecha_inicio',
    )
    search_fields = ('donante_nombre', 'donante_email')
    search_help_text = 'Busque por nombre o email del padrino/madrina.'
    readonly_fields = ('wompi_subscription_id', 'wompi_token_card', 'fecha_inicio', 'ciclos_completados', 'fecha_ultimo_cobro')

    fieldsets = (
        ('Padrino / Madrina', {
            'fields': ('donante_nombre', 'donante_email'),
        }),
        ('Beneficiario y aporte', {
            'fields': ('beneficiario', 'monto_mensual', 'tipo', 'estado'),
        }),
        ('Datos de la pasarela', {
            'fields': ('wompi_subscription_id', 'wompi_token_card'),
            'classes': ('collapse',),
            'description': '🔒 El token de tarjeta se guarda cifrado (Ley 1581 de Habeas Data).',
        }),
        ('Histórico de cobros', {
            'fields': ('fecha_inicio', 'fecha_proximo_cobro', 'fecha_ultimo_cobro', 'ciclos_completados', 'motivo_cancelacion'),
            'classes': ('collapse',),
        }),
    )
