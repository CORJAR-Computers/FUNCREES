from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('nombre', 'email', 'tipo', 'leido', 'respondido', 'creado_en')
    list_filter = ('leido', 'respondido', 'tipo', 'creado_en')
    search_fields = ('nombre', 'email', 'mensaje')
    readonly_fields = ('ip_origen', 'creado_en')
