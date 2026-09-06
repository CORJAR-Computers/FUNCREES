"""
Tests del admin de eventos: formulario amigable, métricas y acciones.

Correr con: python manage.py test events --settings=core.test_settings
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Event, Ticket

User = get_user_model()


class EventAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_evt', 'admin@funcrees.org', 'x')
        cls.evento = Event.objects.create(
            id='bingo-2026',
            titulo='Gran Bingo Pro-Aguinaldos',
            costo_bono=20000,
            cupo_maximo=100,
            cupo_disponible=97,
        )
        Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=1,
            comprador_nombre='Comprador Uno',
            comprador_email='uno@example.com',
            monto_pagado=20000,
            estado_pago='pagado',
        )
        Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=2,
            comprador_nombre='Comprador Dos',
            comprador_email='dos@example.com',
            monto_pagado=20000,
            estado_pago='pendiente',
        )

    def test_changelist_carga(self):
        self.client.force_login(self.staff)
        res = self.client.get(reverse('admin:events_event_changelist'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Gran Bingo Pro-Aguinaldos')

    def test_boletas_vendidas_cuenta_solo_pagadas(self):
        self.client.force_login(self.staff)
        res = self.client.get(reverse('admin:events_event_change', args=[self.evento.pk]))
        self.assertEqual(res.status_code, 200)
        # Solo la boleta pagada cuenta como vendida
        self.assertContains(res, '1')

    def test_crear_evento_desde_panel(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse('admin:events_event_add'),
            {
                'id': 'cena-2026',
                'titulo': 'Cena de Gala',
                'categoria': 'evento',
                'descripcion': 'Cena benéfica anual',
                'fecha': '2026-12-15',
                'hora': '19:00',
                'lugar': 'Club Sincelejo',
                'costo_bono': '80000',
                'cupo_maximo': '50',
                'cupo_disponible': '50',
                'numeracion_min': '1',
                'numeracion_max': '1000',
                'permite_seleccion_numero': 'on',
                'activo': 'on',
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Event.objects.filter(id='cena-2026').exists())


class TicketAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_tick', 'admin@funcrees.org', 'x')
        cls.evento = Event.objects.create(id='rifa', titulo='Rifa de la Esperanza', costo_bono=10000)
        cls.ticket = Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=5,
            comprador_nombre='Ana Gómez',
            comprador_email='ana@example.com',
            monto_pagado=10000,
            estado_pago='pendiente',
        )

    def test_accion_marcar_enviado(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            reverse('admin:events_ticket_changelist'),
            {'action': 'marcar_como_enviado', '_selected_action': [str(self.ticket.id)]},
        )
        self.assertEqual(res.status_code, 302)
        self.ticket.refresh_from_db()
        self.assertTrue(self.ticket.ticket_enviado)
