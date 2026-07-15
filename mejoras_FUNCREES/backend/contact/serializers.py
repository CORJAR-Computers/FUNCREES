import re

from rest_framework import serializers
from django.core.exceptions import ValidationError

from .models import ContactMessage


def _validate_telefono_colombiano(value: str) -> str:
    """
    Valida que el teléfono tenga formato colombiano razonable:
    - 10 dígitos (fijo o móvil sin prefijo internacional), o
    - 12 dígitos si incluye prefijo +57.
    Se permiten espacios, guiones y paréntesis como separadores.
    """
    if not value:
        return value  # El campo es opcional; allow_blank se encarga

    # Eliminar separadores comunes para validar solo los dígitos
    digits = re.sub(r'[\s\-\(\)\+]', '', value)

    if not re.fullmatch(r'(\d{10}|\d{12})', digits):
        raise ValidationError(
            "El teléfono debe tener 10 dígitos (ej: 3101234567) "
            "o 12 con prefijo internacional (ej: 573101234567)."
        )

    return value


class ContactMessageSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(
        min_length=2,
        max_length=200,
        help_text="Nombre del remitente (mínimo 2 caracteres).",
    )
    mensaje = serializers.CharField(
        max_length=2000,
        help_text="Mensaje del contacto (máximo 2000 caracteres).",
    )
    telefono = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        validators=[_validate_telefono_colombiano],
        help_text=(
            "Teléfono de contacto (opcional). "
            "10 dígitos o 12 con prefijo +57."
        ),
    )

    class Meta:
        model = ContactMessage
        fields = ['id', 'nombre', 'email', 'telefono', 'tipo', 'mensaje']