from django.db import models
import uuid

class Beneficiary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    historia = models.TextField()
    testimonio = models.TextField(blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    foto_url = models.URLField(max_length=500, blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
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
