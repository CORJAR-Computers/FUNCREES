"""
URLs principales del proyecto FUNCREES.
Incluye endpoints de la API REST, health-check y vista de requisitos
de DRF para monitoreo operativo.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.throttling import AnonRateThrottle

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
    """Comprueba que la aplicación y la conexión a BD están operativas."""
    import django.db
    try:
        django.db.connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})


# Clase de throttle dedicada al health-check para evitar abuso.
# Se permite un máximo de 30 peticiones por hora desde una misma IP.
class HealthCheckThrottle(AnonRateThrottle):
    rate = '30/hour'


# Vista de health-check con rate-limiting aplicado mediante atributo.
health_check.throttle_classes = [HealthCheckThrottle]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/health/', health_check, name='health-check'),
]

# ---------------------------------------------------------------------------
# Vista de requisitos de DRF — solo disponible cuando DEBUG=True.
# Útil en monitoreo para verificar rápidamente las dependencias del entorno.
# En producción (DEBUG=False) esta ruta se omite por seguridad.
# ---------------------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += [
        path(
            'api/requirements/',
            lambda r: JsonResponse({
                "framework": "Django REST Framework",
                "version": getattr(settings, 'REST_FRAMEWORK_VERSION', 'disponible en DRF 3.15+'),
            }),
            name='api-requirements',
        ),
    ]