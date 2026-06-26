from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from django.db.models import F
from .models import Event, Ticket
from .serializers import EventSerializer, TicketSerializer

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista de eventos activos (solo lectura).
    """
    # nulls_last=True: los eventos permanentes (sin fecha) aparecen al final
    # del listado en lugar de primero (NULL se ordena antes que cualquier
    # valor en la mayoría de BDs por defecto).
    queryset = Event.objects.filter(activo=True).order_by(
        F('fecha').asc(nulls_last=True)
    )
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def numeros_disponibles(self, request, pk=None):
        """Retorna los números de boleta disponibles para este evento.

        Optimización: usar diferencia de conjuntos en memoria en lugar de un
        list comprehension que recorre todo el rango y consulta `in` por cada
        número (O(n*m)). Aquí traemos sólo los vendidos (un query) y
        calculamos set(range) - set(vendidos) en O(n+m).
        """
        evento = self.get_object()
        vendidos_set = set(
            Ticket.objects.filter(
                evento=evento,
                estado_pago__in=['pendiente', 'pagado']
            ).values_list('numero_ticket', flat=True)
        )

        todos_set = set(range(evento.numeracion_min, evento.numeracion_max + 1))
        disponibles = sorted(todos_set - vendidos_set)

        # Limitar para no enviar un JSON inmenso si hay miles
        if len(disponibles) > 500:
            return Response({"disponibles": disponibles[:500], "total_disponibles": len(disponibles), "nota": "Mostrando primeros 500"})
        return Response({"disponibles": disponibles, "total_disponibles": len(disponibles)})

class TicketViewSet(RetrieveModelMixin, GenericViewSet):
    """
    Seguridad: hereda únicamente RetrieveModelMixin (NO list) para evitar
    exponer PII (nombre, documento, email) de todos los compradores de
    boletas. La consulta se hace por `codigo_verificacion`, que actúa como
    secreto compartido entre el comprador y la Fundación.
    """
    # Seguridad: select_related('evento') para evitar N+1 al serializar el
    # evento relacionado en cada retrieve.
    queryset = Ticket.objects.select_related('evento').all()
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]
    # Throttle: limita fuerza bruta sobre códigos de verificación.
    # Se reutiliza el scope 'anon' global (100/hora) para no añadir un scope nuevo.
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'anon'
    lookup_field = 'codigo_verificacion'
