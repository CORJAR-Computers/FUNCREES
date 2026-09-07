import uuid
from django.db import models


class Beneficiary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    historia = models.TextField()
    testimonio = models.TextField(blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)

    # Foto subida desde el panel (opción amigable para el personal)
    foto = models.ImageField(
        upload_to='beneficiarios/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Foto (subir archivo)',
        help_text='Foto del beneficiario. Formatos: JPG, PNG. Se optimiza y genera variantes WebP automáticamente.',
    )
    # Compatibilidad: foto por URL externa (opción avanzada)
    foto_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='Foto (URL externa)')

    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='Video (URL, ej. YouTube)')
    activo = models.BooleanField(default=True)
    apadrinado = models.BooleanField(default=False)
    apadrinadores_count = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Beneficiario'
        verbose_name_plural = 'Beneficiarios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        """Redimensiona la foto subida a máx 800x800 px y genera variantes
        WebP (200/400/800w) para que el navegador descargue la más ligera."""
        super().save(*args, **kwargs)
        if self.foto:
            self._resize_image()
            self._generar_webp()

    def _resize_image(self):
        from PIL import Image

        MAX = 800
        try:
            img = Image.open(self.foto.path)
            if img.width > MAX or img.height > MAX:
                img.thumbnail((MAX, MAX), Image.LANCZOS)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                img.save(self.foto.path, quality=85, optimize=True)
        except Exception:
            # No bloquear el guardado si Pillow no puede procesar el archivo
            pass

    def _generar_webp(self):
        from core.services.images import generar_variantes_webp
        generar_variantes_webp(self.foto)
