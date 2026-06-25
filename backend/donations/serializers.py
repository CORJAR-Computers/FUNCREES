from decimal import Decimal
from rest_framework import serializers
from .models import Donation, Sponsorship

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['id', 'referencia', 'tipo', 'monto', 'donante_nombre', 'estado', 'beneficiario', 'creado_en']
        read_only_fields = ['id', 'referencia', 'estado', 'creado_en']

class InitiateDonationSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=Donation.TIPO_CHOICES, default='general')
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('1000'))
    donante_nombre = serializers.CharField(max_length=200)
    donante_email = serializers.EmailField()
    donante_documento = serializers.CharField(max_length=50, required=False, allow_blank=True)
    donante_telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    metodo_pago = serializers.CharField(max_length=50)
    beneficiario_id = serializers.UUIDField(required=False, allow_null=True)
    autorizacion_datos = serializers.BooleanField(required=True)
