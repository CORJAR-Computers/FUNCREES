import re
from decimal import Decimal
from rest_framework import serializers
from .models import Donation, Sponsorship

# Choices de método de pago aceptados por la Fundación. Se definen aquí (no en
# el modelo) porque el modelo usa un CharField libre por compatibilidad con
# futuros métodos. Limitar aquí evita que un atacante envíe valores arbitrarios
# que luego rompan la integración con Wompi.
METODO_PAGO_CHOICES = [
    ('card', 'Tarjeta'),
    ('pse', 'PSE'),
    ('bancolombia', 'Bancolombia'),
]

# Regex para teléfonos colombianos: opcionalmente +57, luego un 3 (los móviles
# colombianos empiezan por 3) y 9 dígitos más. Se mantiene permisivo: también
# acepta fijos (7 dígitos en algunas ciudades) sin prefijo.
# Ejemplos válidos: 3001234567, +573001234567, 573001234567, 601234567.
TELEFONO_REGEX = re.compile(r'^\+?57?3\d{9}$|^\d{7,10}$')


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['id', 'referencia', 'tipo', 'monto', 'donante_nombre', 'estado', 'beneficiario', 'creado_en']
        read_only_fields = ['id', 'referencia', 'estado', 'creado_en']


class InitiateDonationSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=Donation.TIPO_CHOICES, default='general')
    # Limitar el monto: mínimo 1.000 COP (ya estaba), máximo 100M COP para evitar
    # DoS o abuso con montos absurdos que saturarían Wompi o el cálculo de fees.
    monto = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('1000'),
        max_value=Decimal('100000000'),
    )
    donante_nombre = serializers.CharField(max_length=200)
    donante_email = serializers.EmailField()
    # Documento: longitud acotada (5-20) para evitar payloads enormes y
    # validar formatos razonables (cédulas 8-11, CE, pasaportes hasta 20).
    donante_documento = serializers.CharField(
        max_length=20,
        min_length=5,
        required=False,
        allow_blank=True,
    )
    donante_telefono = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )
    metodo_pago = serializers.ChoiceField(choices=METODO_PAGO_CHOICES)
    beneficiario_id = serializers.UUIDField(required=False, allow_null=True)
    autorizacion_datos = serializers.BooleanField(required=True)

    def validate_donante_telefono(self, value):
        """Valida el teléfono contra una regex colombiana permisiva pero acotada."""
        if not value:
            return value
        if not TELEFONO_REGEX.match(value):
            raise serializers.ValidationError(
                "Teléfono inválido. Use formato colombiano: 3001234567 o +573001234567."
            )
        return value
