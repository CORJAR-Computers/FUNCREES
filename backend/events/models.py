import uuid
import secrets
import string
from django.db import models

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
    imagen_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.titulo

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
    comprador_telefono = models.CharField(max_length=20, blank=True, null=True)
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
