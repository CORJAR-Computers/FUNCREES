from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from rest_framework.routers import DefaultRouter
from beneficiaries.views import BeneficiaryViewSet
from events.views import EventViewSet, TicketViewSet
from contact.views import ContactMessageViewSet
from donations.views import DonationViewSet

router = DefaultRouter()
router.register(r'beneficiaries', BeneficiaryViewSet, basename='beneficiary')
router.register(r'events', EventViewSet, basename='event')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'contact', ContactMessageViewSet, basename='contact')
router.register(r'donations', DonationViewSet, basename='donation')


def health_check(request):
    """
    Endpoint de health check para monitoreo del servidor.
    Usado por Hostinger y servicios de monitoreo para verificar
    que el servidor esté funcionando correctamente.

    Seguridad: NO expone `settings.DEBUG` ni el mensaje de error de la BD
    en la respuesta JSON, ya que esa información puede filtrar detalles
    internos (configuración, versiones, mensajes SQL) a un atacante.
    Solo retorna 'ok' o 'error'.
    """
    import django.db
    try:
        # Verificar conexión real a la base de datos
        django.db.connection.ensure_connection()
    except Exception:
        # No exponer el mensaje de error original.
        return JsonResponse({"status": "error"}, status=503)

    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # Health check: una sola ruta (api/health/) para evitar duplicados que
    # confunden a los servicios de monitoreo y complican la rotación de logs.
    path('api/health/', health_check, name='health-check'),
]
