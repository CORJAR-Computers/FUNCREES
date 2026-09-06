from django.contrib import admin, messages
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'tipo', 'leido_icono', 'respondido_icono', 'creado_en')
    list_display_links = ('nombre',)
    list_filter = (
        ('leido', ChoicesDropdownFilter),
        ('respondido', ChoicesDropdownFilter),
        ('tipo', ChoicesDropdownFilter),
        'creado_en',
    )
    search_fields = ('nombre', 'email', 'telefono', 'mensaje')
    search_help_text = 'Busque por nombre, email, teléfono o contenido del mensaje.'
    date_hierarchy = 'creado_en'
    readonly_fields = ('ip_origen', 'creado_en')
    actions = ('marcar_como_leido', 'marcar_como_respondido')

    fieldsets = (
        ('Remitente', {
            'fields': ('nombre', 'email', 'telefono', 'tipo', 'creado_en'),
        }),
        ('Mensaje', {
            'fields': ('mensaje',),
        }),
        ('Seguimiento', {
            'fields': ('leido', 'respondido'),
            'description': 'Marque "leído" cuando revise el mensaje y "respondido" cuando conteste al remitente.',
        }),
        ('Datos técnicos', {
            'fields': ('ip_origen',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Leído')
    def leido_icono(self, obj):
        return '✓' if obj.leido else '✉ nuevo'

    @admin.display(description='Respondido')
    def respondido_icono(self, obj):
        return '✓' if obj.respondido else '—'

    @admin.action(description='Marcar como leído')
    def marcar_como_leido(self, request, queryset):
        actualizados = queryset.update(leido=True)
        self.message_user(request, f'{actualizados} mensajes marcados como leídos.', level=messages.SUCCESS)

    @admin.action(description='Marcar como respondido')
    def marcar_como_respondido(self, request, queryset):
        actualizados = queryset.update(respondido=True)
        self.message_user(request, f'{actualizados} mensajes marcados como respondidos.', level=messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        # Si un administrador edita el mensaje desde el panel, se asume que ya
        # fue revisado (salvo que esté cambiando el estado de lectura a mano).
        if change and 'leido' not in form.changed_data:
            obj.leido = True
        super().save_model(request, obj, form, change)
