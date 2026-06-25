from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from .models import ContactMessage
from .serializers import ContactMessageSerializer


class ContactMessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Endpoint para recibir mensajes desde el formulario de contacto público.
    Solo permite POST (crear).
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def get_client_ip(self):
        """Captura la IP real del cliente incluso detrás de Nginx como proxy."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR')

    def perform_create(self, serializer):
        serializer.save(ip_origen=self.get_client_ip())
