import uuid
from django.db import models

class ContactMessage(models.Model):
    TIPO_CHOICES = [
        ('consulta', 'Consulta General'),
        ('alianza', 'Alianza Corporativa'),
        ('voluntariado', 'Voluntariado'),
        ('donacion', 'Donación'),
        ('otro', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='consulta')
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)
    ip_origen = models.GenericIPAddressField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensaje de Contacto'
        verbose_name_plural = 'Mensajes de Contacto'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_display()}"
