from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
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
    # Seguridad: limitar abuso/spam del formulario con throttle scope 'contact'.
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact'

    def get_client_ip(self):
        """
        Captura la IP real del cliente incluso detrás de Nginx como proxy.

        Seguridad: X-Forwarded-For puede contener una lista
        `client, proxy1, proxy2`. Tomamos el ÚLTIMO valor (no el primero) bajo
        el supuesto de que el proxy inverso confiable más cercano a Django
        (p.ej. Nginx) es quien APENDIZA la IP del cliente que lo contactó al
        final de la cadena. El primer valor, en cambio, podría estar
        controlado por el cliente (spoofing) si un proxy intermedio no validó
        la cabecera.
        SUPONE: se ejecuta detrás de un proxy confiable que reescribe / valida
        X-Forwarded-For. Si no hay proxy, se usa REMOTE_ADDR.
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Última IP de la cadena, sin espacios.
            return x_forwarded_for.split(',')[-1].strip()
        return self.request.META.get('REMOTE_ADDR')

    def perform_create(self, serializer):
        serializer.save(ip_origen=self.get_client_ip())
