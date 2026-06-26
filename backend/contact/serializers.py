from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    # Limitar longitudes para evitar mensajes gigantes que saturarían la BD y
    # el inbox del admin. El modelo usa TextField (sin max_length), así que
    # acotamos aquí a nivel de API.
    mensaje = serializers.CharField(max_length=2000)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = ContactMessage
        fields = ['id', 'nombre', 'email', 'telefono', 'tipo', 'mensaje']
