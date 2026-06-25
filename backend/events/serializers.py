from rest_framework import serializers
from .models import Event, Ticket

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'titulo', 'descripcion', 'fecha', 'hora', 'lugar', 'costo_bono', 'cupo_maximo', 'cupo_disponible', 'numeracion_min', 'numeracion_max', 'permite_seleccion_numero', 'categoria', 'imagen_url']

class TicketSerializer(serializers.ModelSerializer):
    evento_titulo = serializers.ReadOnlyField(source='evento.titulo')
    
    class Meta:
        model = Ticket
        fields = ['id', 'evento', 'evento_titulo', 'numero_ticket', 'comprador_nombre', 'monto_pagado', 'estado_pago', 'seleccion_tipo']
