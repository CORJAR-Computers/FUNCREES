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
    """
    import django.db
    try:
        # Verificar conexión real a la base de datos
        django.db.connection.ensure_connection()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
        return JsonResponse({
            "status": "unhealthy",
            "version": "1.0.0",
            "debug": settings.DEBUG,
            "database": db_status,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }, status=503)

    return JsonResponse({
        "status": "healthy",
        "version": "1.0.0",
        "debug": settings.DEBUG,
        "database": db_status,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/health/', health_check, name='health-check'),
    path('health/', health_check, name='health-check-alt'),
]
