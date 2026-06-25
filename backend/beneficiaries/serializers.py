from rest_framework import serializers
from .models import Beneficiary

class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = ['id', 'nombre', 'historia', 'testimonio', 'edad', 'ciudad', 'foto_url', 'video_url', 'apadrinado', 'apadrinadores_count']
