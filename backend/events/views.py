from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Event, Ticket
from .serializers import EventSerializer, TicketSerializer

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista de eventos activos (solo lectura).
    """
    queryset = Event.objects.filter(activo=True).order_by('fecha')
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def numeros_disponibles(self, request, pk=None):
        """Retorna los números de boleta disponibles para este evento"""
        evento = self.get_object()
        tickets_vendidos = Ticket.objects.filter(
            evento=evento, 
            estado_pago__in=['pendiente', 'pagado']
        ).values_list('numero_ticket', flat=True)
        
        vendidos_set = set(tickets_vendidos)
        disponibles = [
            n for n in range(evento.numeracion_min, evento.numeracion_max + 1)
            if n not in vendidos_set
        ]
        
        # Limitar para no enviar un JSON inmenso si hay miles
        if len(disponibles) > 500:
            return Response({"disponibles": disponibles[:500], "total_disponibles": len(disponibles), "nota": "Mostrando primeros 500"})
        return Response({"disponibles": disponibles, "total_disponibles": len(disponibles)})

class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """Solo para comprobación de tickets por código"""
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]
    lookup_field = 'codigo_verificacion'
