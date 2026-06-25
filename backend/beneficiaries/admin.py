from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Beneficiary

@admin.register(Beneficiary)
class BeneficiaryAdmin(ModelAdmin):
    list_display = ('nombre', 'ciudad', 'edad', 'apadrinado', 'apadrinadores_count', 'activo')
    list_filter = ('activo', 'apadrinado', 'ciudad')
    search_fields = ('nombre', 'ciudad', 'historia')
    readonly_fields = ('apadrinadores_count', 'creado_en', 'actualizado_en')
