"""
Tests del recordatorio de donaciones pendientes (simetría con boletas).

Correr con: python manage.py test donations.tests_reminder --settings=core.test_settings

Cubre:
- send_donation_reminder: subject con referencia, monto y enlace; variante
  recurrente (apadrinamiento) sin CTA de checkout; fallo SMTP → False.
- Acción del panel "recordar_pago_pendiente": envía solo a pendientes,
  omite confirmadas y avisa cuando no hay nada que recordar.
"""
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Donation
from .services.email_service import send_donation_reminder

User = get_user_model()


class DonationReminderServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pendiente = Donation.objects.create(
            referencia='REM-001',
            tipo='general',
            monto=50000,
            donante_nombre='María Pérez',
            donante_email='maria@example.com',
            metodo_pago='Wompi',
            estado='pendiente',
        )
        cls.mensual = Donation.objects.create(
            referencia='REM-002',
            tipo='apadrinamiento',
            monto=30000,
            donante_nombre='Carlos Ruiz',
            donante_email='carlos@example.com',
            metodo_pago='Wompi',
            estado='pendiente',
        )

    def test_envio_exitoso_con_datos_del_aporte(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            ok = send_donation_reminder(self.pendiente)

        self.assertTrue(ok)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertIn('maria@example.com', msg.to)
        self.assertIn('REM-001', msg.subject)
        self.assertIn('REM-001', msg.body)
        html = msg.alternatives[0][0]
        self.assertIn('REM-001', html)
        self.assertIn('$50.000,00', html)
        self.assertIn('/donaciones', html)

    def test_apadrinamiento_no_ofrece_checkout(self):
        """El aporte mensual se coordina por WhatsApp, no reintentando checkout."""
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            ok = send_donation_reminder(self.mensual)

        self.assertTrue(ok)
        html = mail.outbox[0].alternatives[0][0]
        self.assertNotIn('Completar mi aporte', html)
        self.assertIn('WhatsApp', html)

    def test_fallo_smtp_retorna_false_sin_lanzar(self):
        with mock.patch('donations.services.email_service.render_to_string',
                        side_effect=Exception('SMTP caído')):
            ok = send_donation_reminder(self.pendiente)
        self.assertFalse(ok)


class DonationReminderAdminActionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_rem_don', 'admindon@funcrees.org', 'x')
        cls.changelist = reverse('admin:donations_donation_changelist')
        cls.pendiente = Donation.objects.create(
            referencia='REM-A-1', tipo='general', monto=20000,
            donante_nombre='Pendiente Uno', donante_email='p1@example.com',
            metodo_pago='Wompi', estado='pendiente',
        )
        cls.completada = Donation.objects.create(
            referencia='REM-A-2', tipo='general', monto=20000,
            donante_nombre='Ya Pagó', donante_email='p2@example.com',
            metodo_pago='Wompi', estado='completado',
        )

    def _post_action(self, action, donaciones):
        self.client.force_login(self.staff)
        data = {
            'action': action,
            '_selected_action': [str(d.pk) for d in donaciones],
        }
        return self.client.post(self.changelist, data)

    def test_accion_envia_solo_a_pendientes(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            res = self._post_action('recordar_pago_pendiente', [self.pendiente, self.completada])

        self.assertEqual(res.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('p1@example.com', mail.outbox[0].to)
        mensajes = [str(m) for m in get_messages(res.wsgi_request)]
        self.assertTrue(any('omitida' in m for m in mensajes))

    def test_accion_sin_pendientes_no_envia_nada(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            res = self._post_action('recordar_pago_pendiente', [self.completada])

        self.assertEqual(res.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)
        mensajes = [str(m) for m in get_messages(res.wsgi_request)]
        self.assertTrue(any('Ninguna donación' in m for m in mensajes))

    def test_accion_sobrevive_fallo_smtp(self):
        def envio_falso(donation):
            return donation.pk != self.pendiente.pk

        with mock.patch('donations.admin.send_donation_reminder', side_effect=envio_falso):
            res = self._post_action('recordar_pago_pendiente', [self.pendiente])

        self.assertEqual(res.status_code, 302)
        mensajes = [str(m) for m in get_messages(res.wsgi_request)]
        self.assertTrue(any('error de envío' in m for m in mensajes))
