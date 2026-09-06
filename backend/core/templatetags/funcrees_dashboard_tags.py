"""
Panel "Resumen de la Fundación" para el índice del admin.

La lógica de cálculo vive en core/services.py (fuente única compartida con
el resumen semanal por correo). Este módulo solo expone el template tag y
los filtros de formato que usan las plantillas.
"""
from django import template

from contact.models import ContactMessage
from core.services import formato_cop, resumen_fundacion

register = template.Library()

TIPO_MENSAJE = dict(ContactMessage.TIPO_CHOICES)


@register.filter
def cop(value) -> str:
    """Formato corto de dinero: 12345678 → $12.345.678"""
    return formato_cop(value)


@register.filter
def cop_full(value) -> str:
    """Formato con decimales: 50000.00 → $50.000,00"""
    try:
        entero, decimal = f'{float(value):.2f}'.split('.')
        return f'${int(entero):,}'.replace(',', '.') + f',{decimal}'
    except (TypeError, ValueError):
        return '$0'


@register.filter
def tipo_display(value: str) -> str:
    """Etiqueta legible del tipo de mensaje de contacto."""
    return TIPO_MENSAJE.get(value, value)


@register.filter
def fecha_corta(value) -> str:
    """Fecha compacta sin depender del locale: 05/09/2026 14:32"""
    try:
        return value.strftime('%d/%m/%Y %H:%M')
    except AttributeError:
        return ''


@register.filter
def join_por_mes(serie_mensual) -> str:
    """Descripción textual de la serie mensual para el aria-label del gráfico."""
    try:
        return '; '.join(
            f"{m['mes_nombre']}: {m['total_fmt']} ({m['cantidad']} donaciones)"
            for m in serie_mensual
        )
    except (TypeError, KeyError):
        return ''


@register.inclusion_tag('admin/funcrees_dashboard.html')
def funcrees_dashboard():
    """Contexto del panel: exactamente las mismas cifras del correo semanal."""
    return resumen_fundacion()
