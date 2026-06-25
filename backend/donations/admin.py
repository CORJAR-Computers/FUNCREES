from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Donation, Sponsorship

@admin.register(Donation)
class DonationAdmin(ModelAdmin):
    list_display = ('referencia', 'donante_nombre', 'monto', 'tipo', 'estado', 'creado_en')
    list_filter = ('estado', 'tipo', 'creado_en')
    search_fields = ('referencia', 'donante_nombre', 'donante_email')
    readonly_fields = ('donante_documento_cifrado', 'donante_telefono_cifrado', 'referencia_pasarela', 'wompi_response', 'creado_en', 'ip_origen')

@admin.register(Sponsorship)
class SponsorshipAdmin(ModelAdmin):
    list_display = ('donante_nombre', 'beneficiario', 'monto_mensual', 'tipo', 'estado', 'fecha_inicio')
    list_filter = ('estado', 'tipo', 'fecha_inicio')
    search_fields = ('donante_nombre', 'donante_email')
    readonly_fields = ('wompi_subscription_id', 'wompi_token_card', 'fecha_inicio', 'ciclos_completados', 'fecha_ultimo_cobro')
