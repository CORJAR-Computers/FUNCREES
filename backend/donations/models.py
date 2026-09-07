import uuid
import logging
from django.db import models

# Campo cifrado unificado en core/fields.py (compartido con events).
# IMPORTANTE: mantener los nombres `EncryptedCharField` y `get_fernet` en este
# namespace — las migraciones históricas (0002_encrypt_wompi_token_card y
# siguientes) los resuelven como `donations.models.<name>`.
from core.fields import EncryptedCharField, get_fernet

# Usamos el logger 'donations' (definido en LOGGING de settings.py) para que
# los errores de desencriptación queden en el archivo de log de donaciones.
logger = logging.getLogger('donations')

class Donation(models.Model):
    TIPO_CHOICES = [
        ('general', 'Donación General'),
        ('apadrinamiento', 'Apadrinamiento Mensual'),
        ('patrocinio', 'Patrocinio Empresarial'),
        ('boleta', 'Compra de Boleta/Evento'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referencia = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    donante_nombre = models.CharField(max_length=200)
    donante_email = models.EmailField()
    
    # Campos cifrados para Habeas Data (Ley 1581)
    donante_documento_cifrado = EncryptedCharField(max_length=500, blank=True, null=True, verbose_name="Documento (Cifrado)")
    donante_telefono_cifrado = EncryptedCharField(max_length=500, blank=True, null=True, verbose_name="Teléfono (Cifrado)")
    
    metodo_pago = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    referencia_pasarela = models.CharField(max_length=200, blank=True, null=True)
    wompi_response = models.JSONField(blank=True, null=True)
    beneficiario = models.ForeignKey('beneficiaries.Beneficiary', on_delete=models.SET_NULL, null=True, blank=True, related_name='donaciones')
    certificado_enviado = models.BooleanField(default=False)
    # Defensa en profundidad: se activa si el webhook de Wompi reporta un
    # monto distinto al acordado (firma válida pero monto alterado o bug).
    # La donación NO se aprueba automáticamente; requiere revisión manual.
    revision_requerida = models.BooleanField(default=False, verbose_name="Revisión requerida")
    autorizacion_datos = models.BooleanField(default=False)
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Donación'
        verbose_name_plural = 'Donaciones'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.referencia} - {self.donante_nombre} (${self.monto})"

class Sponsorship(models.Model):
    TIPO_CHOICES = [
        ('debito_automatico', 'Débito Automático'),
        ('suscripcion_manual', 'Suscripción Manual'),
    ]

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('cancelado', 'Cancelado'),
        ('vencido', 'Vencido'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donante_nombre = models.CharField(max_length=200)
    donante_email = models.EmailField()
    beneficiario = models.ForeignKey('beneficiaries.Beneficiary', on_delete=models.CASCADE, related_name='apadrinamientos')
    monto_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    wompi_subscription_id = models.CharField(max_length=200, blank=True, null=True)
    wompi_token_card = EncryptedCharField(max_length=1000, blank=True, null=True, verbose_name="Token Tarjeta (Cifrado)")
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_proximo_cobro = models.DateField(blank=True, null=True)
    fecha_ultimo_cobro = models.DateTimeField(blank=True, null=True)
    ciclos_completados = models.PositiveIntegerField(default=0)
    motivo_cancelacion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Apadrinamiento'
        verbose_name_plural = 'Apadrinamientos'

    def __str__(self):
        return f"Apadrinamiento de {self.beneficiario.nombre} por {self.donante_nombre}"
