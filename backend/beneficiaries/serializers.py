from rest_framework import serializers
from .models import Beneficiary


class BeneficiarySerializer(serializers.ModelSerializer):
    """
    Serializa beneficiarios para el sitio público.

    Prioridad de imagen: `foto` (archivo subido en el admin) > `foto_url`
    (URL externa). El frontend recibe siempre `foto` como URL absoluta lista
    para <img src>, y `tiene_foto` para saber si es personalizada.
    """
    # URL absoluta de la foto (archivo subido) o None si no hay
    foto = serializers.ImageField(use_url=True, required=False, allow_null=True, read_only=True)

    class Meta:
        model = Beneficiary
        fields = ['id', 'nombre', 'historia', 'testimonio', 'edad', 'ciudad', 'foto', 'foto_url', 'video_url', 'apadrinado', 'apadrinadores_count']
        read_only_fields = ['foto']

    def to_representation(self, instance):
        """Unifica la fuente de imagen: archivo subido tiene prioridad."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        uploaded = None
        if instance.foto and request is not None:
            uploaded = request.build_absolute_uri(instance.foto.url)
        data['foto'] = uploaded
        # El frontend usa foto_url como fallback si no hay archivo subido
        if uploaded:
            data['foto_url'] = uploaded
        return data
