from rest_framework import serializers
from .models import Event, Ticket


class EventSerializer(serializers.ModelSerializer):
    """
    Serializa eventos para el sitio público.

    Prioridad de imagen: `imagen` (archivo subido en el admin) > `imagen_url`
    (URL externa). La respuesta expone la URL final lista para el frontend.
    """
    imagen = serializers.ImageField(use_url=True, required=False, allow_null=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'titulo', 'descripcion', 'fecha', 'hora', 'lugar', 'costo_bono', 'cupo_maximo', 'cupo_disponible', 'numeracion_min', 'numeracion_max', 'permite_seleccion_numero', 'categoria', 'imagen', 'imagen_url']
        read_only_fields = ['imagen']

    def to_representation(self, instance):
        """Unifica la fuente de imagen: archivo subido tiene prioridad."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        uploaded = None
        if instance.imagen and request is not None:
            uploaded = request.build_absolute_uri(instance.imagen.url)
        if uploaded:
            data['imagen'] = uploaded
            data['imagen_url'] = uploaded
        return data


class TicketSerializer(serializers.ModelSerializer):
    evento_titulo = serializers.ReadOnlyField(source='evento.titulo')

    class Meta:
        model = Ticket
        fields = ['id', 'evento', 'evento_titulo', 'numero_ticket', 'comprador_nombre', 'monto_pagado', 'estado_pago', 'seleccion_tipo']
