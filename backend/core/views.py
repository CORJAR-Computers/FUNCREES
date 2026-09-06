"""
Vistas transversales de la app core (fuera de los routers de DRF).
"""
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from core.services import cifras_publicas


class StatsThrottle(AnonRateThrottle):
    """
    Throttle propio para /api/stats/ (scope 'stats' en DEFAULT_THROTTLE_RATES).

    Nota: se usa una subclase de AnonRateThrottle y NO ScopedRateThrottle
    porque @api_view no copia el atributo `throttle_scope` de la función a la
    vista envuelta, y sin él ScopedRateThrottle no limita nada (trampa de DRF).
    """
    scope = 'stats'


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([StatsThrottle])
# Decoradores de Django SIEMPRE por debajo de @api_view (igual que en
# health_check): cache_page es inner-most para cachear la función cruda.
@cache_page(120, key_prefix='stats')
@vary_on_headers('Accept-Language')
def public_stats(request):
    """
    GET /api/stats/ — Cifras públicas agregadas de la Fundación.

    Solo lectura y SIN datos personales: únicamente sumas, conteos y la serie
    mensual de donaciones CONFIRMADAS (alimenta la página "Nuestros números").

    Cache: 2 min en servidor (TTL corto porque la página publica cifras "en
    vivo" tras cada donación confirmada) + Cache-Control public para el CDN.
    El decorador never_cache evita que un throttle 429 quede cacheado.

    Throttle: scope 'stats' (30/h por IP) contra scraping masivo.
    """
    response = Response(cifras_publicas())
    response.headers['Cache-Control'] = 'public, max-age=120'
    return response
