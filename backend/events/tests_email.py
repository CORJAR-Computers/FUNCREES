"""
Tests del servicio de email de boletas y de la acción del panel.

Correr con: python manage.py test events.tests_email --settings=core.test_settings

Cubre:
- send_ticket_email: subject, código en el cuerpo, URL de consulta, QR adjunto
  al HTML y retorno True/False.
- Acción de admin "enviar_boleta_por_email": marca ticket_enviado solo en
  éxitos y reporta fallos sin romper el lote.
"""
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Event, Ticket
from .services.email_service import build_consulta_url, send_ticket_email

User = get_user_model()


class TicketEmailServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.evento = Event.objects.create(
            id='bingo-2026',
            titulo='Gran Bingo Pro-Aguinaldos',
            fecha='2026-10-10',
            hora='15:00',
            lugar='Sincelejo',
            costo_bono=20000,
        )
        cls.ticket = Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=7,
            comprador_nombre='María Pérez',
            comprador_email='maria@example.com',
            monto_pagado=20000,
            estado_pago='pagado',
        )

    def test_envio_exitoso_registra_email(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            ok = send_ticket_email(self.ticket)

        self.assertTrue(ok)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertIn('maria@example.com', msg.to)
        self.assertIn(str(self.ticket.numero_ticket), msg.subject)
        self.assertIn(self.evento.titulo, msg.subject)
        # El código de verificación debe llegar en el cuerpo (texto plano y HTML)
        self.assertIn(self.ticket.codigo_verificacion, msg.body)
        html = msg.alternatives[0][0]
        self.assertIn(self.ticket.codigo_verificacion, html)
        # URL de consulta con el código prellenado
        self.assertIn(f'codigo={self.ticket.codigo_verificacion}', html)
        # El QR se incrusta como data URI en el HTML
        self.assertIn('data:image/png;base64,', html)

    def test_url_consulta_incluye_codigo(self):
        url = build_consulta_url('ABCD123456')
        self.assertTrue(url.endswith('/boletas?codigo=ABCD123456'))
        self.assertTrue(url.startswith('http'))

    def test_fallo_smtp_retorna_false_sin_lanzar(self):
        with mock.patch('events.services.email_service.render_to_string',
                        side_effect=Exception('SMTP caído')):
            ok = send_ticket_email(self.ticket)
        self.assertFalse(ok)


class TicketAdminEmailActionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_mail', 'admin@funcrees.org', 'x')
        cls.evento = Event.objects.create(
            id='rifa-test', titulo='Rifa de Prueba', costo_bono=10000,
        )
        cls.t1 = Ticket.objects.create(
            evento=cls.evento, numero_ticket=1,
            comprador_nombre='Uno', comprador_email='uno@example.com',
            monto_pagado=10000,
        )
        cls.t2 = Ticket.objects.create(
            evento=cls.evento, numero_ticket=2,
            comprador_nombre='Dos', comprador_email='dos@example.com',
            monto_pagado=10000,
        )

    def _post_action(self, action, tickets):
        self.client.force_login(self.staff)
        data = {
            'action': action,
            '_selected_action': [str(t.pk) for t in tickets],
        }
        return self.client.post(reverse('admin:events_ticket_changelist'), data)

    def test_accion_envia_y_marca_ticket_enviado(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            res = self._post_action('enviar_boleta_por_email', [self.t1])
        self.assertEqual(res.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.t1.refresh_from_db()
        self.assertTrue(self.t1.ticket_enviado)
        self.t2.refresh_from_db()
        self.assertFalse(self.t2.ticket_enviado)

    def test_accion_sobrevive_fallo_smtp(self):
        # Determinista: falla SOLO para t2 (por pk), sin depender del orden
        # en que el admin itere el queryset seleccionado.
        def envio_falso(ticket):
            return ticket.pk == self.t1.pk

        with mock.patch('events.admin.send_ticket_email', side_effect=envio_falso):
            res = self._post_action('enviar_boleta_por_email', [self.t1, self.t2])
        self.assertEqual(res.status_code, 302)
        self.t1.refresh_from_db()
        self.t2.refresh_from_db()
        self.assertTrue(self.t1.ticket_enviado)
        self.assertFalse(self.t2.ticket_enviado)  # la fallida NO se marca


class PaymentReminderTests(TestCase):
    """Recordatorio de pago: servicio, comando de gestión y acción admin."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_rem', 'adminrem@funcrees.org', 'x')
        cls.evento = Event.objects.create(
            id='bingo-rem', titulo='Bingo Recordatorio', costo_bono=20000,
        )
        cls.pendiente = Ticket.objects.create(
            evento=cls.evento, numero_ticket=10,
            comprador_nombre='Pendiente Uno', comprador_email='pend@example.com',
            monto_pagado=20000, estado_pago='pendiente',
        )
        cls.pagado = Ticket.objects.create(
            evento=cls.evento, numero_ticket=11,
            comprador_nombre='Pagado Uno', comprador_email='pag@example.com',
            monto_pagado=20000, estado_pago='pagado',
        )

    def test_recordatorio_email_contiene_datos(self):
        from events.services.email_service import send_payment_reminder
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            ok = send_payment_reminder(self.pendiente)
        self.assertTrue(ok)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertIn('Recordatorio', msg.subject)
        self.assertIn(str(self.pendiente.numero_ticket), msg.subject)
        html = msg.alternatives[0][0]
        self.assertIn(self.pendiente.codigo_verificacion, html)
        self.assertIn('pendiente', html.lower())

    def test_comando_dry_run_no_envia(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            call_command('remind_pending_tickets', dry_run=True, stdout=out)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn('dry-run', out.getvalue().lower())
        self.assertIn('pend@example.com', out.getvalue())

    def test_comando_envia_solo_pendientes(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            call_command('remind_pending_tickets', stdout=out)
        # 1 pendiente en la BD de esta clase de tests (la pagada se omite)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('pend@example.com', mail.outbox[0].to)

    def test_comando_filtro_dias(self):
        from io import StringIO
        from datetime import timedelta
        from django.core.management import call_command
        from django.utils import timezone
        # Boleta recién creada: con --dias 1 no debe incluirse
        out = StringIO()
        call_command('remind_pending_tickets', dias=1, dry_run=True, stdout=out)
        self.assertIn('Boletas pendientes a notificar: 0', out.getvalue())
        # Antigüedad simulada: sí se incluye
        Ticket.objects.filter(pk=self.pendiente.pk).update(
            creado_en=timezone.now() - timedelta(days=5))
        out = StringIO()
        call_command('remind_pending_tickets', dias=1, dry_run=True, stdout=out)
        self.assertIn('Boletas pendientes a notificar: 1', out.getvalue())

    def test_accion_admin_omite_no_pendientes(self):
        self.client.force_login(self.staff)
        data = {
            'action': 'recordar_pago_pendiente',
            '_selected_action': [str(self.pendiente.pk), str(self.pagado.pk)],
        }
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            res = self.client.post(reverse('admin:events_ticket_changelist'), data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('pend@example.com', mail.outbox[0].to)
