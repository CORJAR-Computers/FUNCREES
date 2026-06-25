from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Beneficiary
from .serializers import BeneficiarySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class BeneficiaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista pública de beneficiarios (solo lectura).
    Permite filtrar por ciudad y estado de apadrinamiento, y buscar por nombre.
    """
    queryset = Beneficiary.objects.filter(activo=True)
    serializer_class = BeneficiarySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ciudad', 'apadrinado']
    search_fields = ['nombre', 'historia', 'testimonio']
