from django import forms
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from .models import Beneficiary


class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = '__all__'
        help_texts = {
            'historia': 'Cuéntanos la historia de vida del beneficiario. Se muestra en la página "Historias de Vida".',
            'testimonio': 'Una frase corta y conmovedora en primera persona (aparece entre comillas en su tarjeta).',
            'edad': 'Edad en años cumplidos.',
            'ciudad': 'Municipio donde vive (ej. Sincelejo, Tolú, La Unión).',
            'activo': 'Desmarque para ocultar al beneficiario del sitio web sin borrar su información.',
            'apadrinado': 'Marque cuando el beneficiario cuente con un padrino/madrina activo.',
        }


@admin.register(Beneficiary)
class BeneficiaryAdmin(ModelAdmin):
    form = BeneficiaryForm
    list_display = ('nombre', 'edad', 'ciudad', 'apadrinado', 'activo', 'vista_previa')
    list_display_links = ('nombre',)
    list_filter = (
        ('apadrinado', ChoicesDropdownFilter),
        ('activo', ChoicesDropdownFilter),
        'ciudad',
    )
    search_fields = ('nombre', 'ciudad', 'historia')
    search_help_text = 'Busque por nombre, ciudad o contenido de la historia.'
    ordering = ('nombre',)
    readonly_fields = ('vista_previa_grande', 'apadrinadores_count', 'creado_en', 'actualizado_en')
    list_per_page = 25

    fieldsets = (
        ('Información personal', {
            'fields': ('nombre', 'edad', 'ciudad'),
        }),
        ('Foto', {
            'fields': ('vista_previa_grande', 'foto', 'foto_url'),
            'description': '📸 Suba una foto desde su computadora (opción recomendada). '
                           'La opción de URL externa queda como alternativa avanzada. '
                           'La imagen se optimiza automáticamente para la web.',
        }),
        ('Historia y testimonio', {
            'fields': ('historia', 'testimonio'),
        }),
        ('Estado en el sitio web', {
            'fields': ('activo', 'apadrinado', 'apadrinadores_count'),
        }),
        ('Video (opcional)', {
            'fields': ('video_url',),
            'classes': ('collapse',),
        }),
        ('Fechas del sistema', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Foto')
    def vista_previa(self, obj):
        """Miniatura en la lista de beneficiarios."""
        url = None
        if obj and obj.foto:
            url = obj.foto.url
        elif obj and obj.foto_url:
            url = obj.foto_url
        if url:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:50%;" />',
                url,
            )
        return format_html(
            '<span style="display:inline-block;width:48px;height:48px;border-radius:50%;'
            'background:#e5e7eb;text-align:center;line-height:48px;color:#9ca3af;">👤</span>'
        )

    @admin.display(description='Vista previa de la foto')
    def vista_previa_grande(self, obj):
        """Vista previa grande en el formulario de edición."""
        if obj and obj.pk:
            url = obj.foto.url if obj.foto else obj.foto_url
            if url:
                return format_html(
                    '<img src="{}" style="max-width:320px;max-height:320px;'
                    'object-fit:cover;border-radius:12px;border:1px solid #ddd;" />',
                    url,
                )
        return format_html('<p style="color:#9ca3af;">Aún no hay foto para este beneficiario.</p>')
