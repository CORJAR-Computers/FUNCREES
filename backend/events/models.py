import uuid
import secrets
import string
from django.db import models

# Ley 1581: el teléfono del comprador es dato personal y se cifra en reposo
# con el mismo campo Fernet que ya usa donations (documento/teléfono).
from core.fields import EncryptedCharField

class Event(models.Model):
    CATEGORIA_CHOICES = [
        ('evento', 'Evento (Bingo, Cena, etc)'),
        ('campania', 'Campaña Permanente'),
    ]

    id = models.CharField(max_length=50, primary_key=True, help_text="ID legible: bingo-2026, rifa, etc.")
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True, help_text="NULL para eventos permanentes/campañas")
    hora = models.CharField(max_length=20, blank=True, null=True)
    lugar = models.CharField(max_length=200, blank=True, null=True)
    costo_bono = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio del bono/boleta en COP")
    cupo_maximo = models.PositiveIntegerField(blank=True, null=True, help_text="NULL = sin límite de cupo")
    cupo_disponible = models.PositiveIntegerField(blank=True, null=True)
    numeracion_min = models.PositiveIntegerField(default=1, help_text="Número mínimo de boleta")
    numeracion_max = models.PositiveIntegerField(default=1000, help_text="Número máximo de boleta")
    permite_seleccion_numero = models.BooleanField(default=True, help_text="Si el usuario puede elegir su número de boleta")
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='evento')
    activo = models.BooleanField(default=True)

    # Sello temporal para SEO: el sitemap dinámico del frontend usa esta fecha
    # como <lastmod> de /eventos/<id>, informando a los buscadores cuándo
    # cambió realmente el contenido (y no la fecha del deploy).
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    # Imagen subida desde el panel (opción amigable)
    imagen = models.ImageField(
        upload_to='eventos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Imagen (subir archivo)',
        help_text='Imagen promocional del evento. Se optimiza y genera variantes WebP automáticamente.',
    )
    # Compatibilidad: imagen por URL externa (opción avanzada)
    imagen_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='Imagen (URL externa)')

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        """Redimensiona la imagen subida a máx 1200x1200 px y genera variantes
        WebP (200/400/800/1200w) para que el navegador descargue la más ligera."""
        super().save(*args, **kwargs)
        if self.imagen:
            self._resize_image()
            self._generar_webp()

    def _resize_image(self):
        from PIL import Image

        MAX = 1200
        try:
            img = Image.open(self.imagen.path)
            if img.width > MAX or img.height > MAX:
                img.thumbnail((MAX, MAX), Image.LANCZOS)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                img.save(self.imagen.path, quality=85, optimize=True)
        except Exception:
            # No bloquear el guardado si Pillow no puede procesar el archivo
            pass

    def _generar_webp(self):
        from core.services.images import generar_variantes_webp
        generar_variantes_webp(self.imagen)

def generate_verification_code():
    """
    Genera un código de verificación de 10 caracteres alfanuméricos.

    Seguridad: usa `secrets` (CSPRNG) en lugar de `random` (PRNG no cripto).
    El código actúa como secreto compartido entre el comprador y la Fundación
    para consultar la boleta en /api/tickets/<codigo>/, por lo que debe ser
    impredecible. `random.choices` es vulnerable a predicción si un atacante
    puede observar varios códigos generados consecutivos.
    """
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(10))

class Ticket(models.Model):
    SELECCION_CHOICES = [
        ('automatico', 'Automático'),
        ('manual', 'Manual (Elegido por usuario)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    numero_ticket = models.PositiveIntegerField(help_text="Número del cartón/boleta — único por evento")
    comprador_nombre = models.CharField(max_length=200)
    comprador_email = models.EmailField()
    comprador_telefono = EncryptedCharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Teléfono (Cifrado)",
        help_text="Cifrado en reposo (Ley 1581). El valor ronda los 150+ caracteres por el padding Fernet.",
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_verificacion = models.CharField(max_length=20, unique=True, default=generate_verification_code)
    codigo_qr = models.TextField(blank=True, null=True, help_text="Contenido del QR o URL")
    estado_pago = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado'), ('cancelado', 'Cancelado')], default='pendiente')
    referencia_wompi = models.CharField(max_length=200, blank=True, null=True)
    donacion_id = models.UUIDField(blank=True, null=True, help_text="Referencia a la donación/pago")
    ticket_enviado = models.BooleanField(default=False)
    seleccion_tipo = models.CharField(max_length=20, choices=SELECCION_CHOICES, default='automatico')

    class Meta:
        verbose_name = 'Boleta/Ticket'
        verbose_name_plural = 'Boletas/Tickets'
        unique_together = ('evento', 'numero_ticket')

    def __str__(self):
        return f"Ticket #{self.numero_ticket} - {self.evento.titulo}"
