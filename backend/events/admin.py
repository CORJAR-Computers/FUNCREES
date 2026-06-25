from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Event, Ticket

@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ('id', 'titulo', 'fecha', 'costo_bono', 'cupo_disponible', 'activo')
    list_filter = ('activo', 'categoria', 'fecha')
    search_fields = ('titulo', 'id')

@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = ('evento', 'numero_ticket', 'comprador_nombre', 'estado_pago', 'codigo_verificacion')
    list_filter = ('estado_pago', 'seleccion_tipo', 'evento')
    search_fields = ('comprador_nombre', 'comprador_email', 'codigo_verificacion')
    readonly_fields = ('codigo_verificacion', 'donacion_id')
