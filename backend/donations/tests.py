"""
Tests del flujo de donaciones y el webhook de Wompi.

Se mockea la comunicación con la API de Wompi (no se hace HTTP real).
Correr con: python manage.py test donations
"""
import hashlib
import json
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Donation

TEST_INTEGRITY_SECRET = 'test_integrity_secret'


def _make_webhook_payload(reference: str, amount_in_cents: int, status: str = 'APPROVED') -> dict:
    """Construye un payload de webhook con firma válida (como lo haría Wompi)."""
    transaction = {
        'reference': reference,
        'amount_in_cents': amount_in_cents,
        'currency': 'COP',
        'status': status,
        'id': f'txn-test-{reference}',
    }
    string_to_sign = (
        transaction['reference']
        + str(transaction['amount_in_cents'])
        + transaction['currency']
        + TEST_INTEGRITY_SECRET
    )
    checksum = hashlib.sha256(string_to_sign.encode('utf-8')).hexdigest()
    return {'event': 'transaction.updated', 'data': {'transaction': transaction}, 'signature': {'checksum': checksum}}


@override_settings(
    WOMPI_ENV='sandbox',
    WOMPI_PUBLIC_KEY='pub_test',
    WOMPI_PRIVATE_KEY='prv_test',
    WOMPI_INTEGRITY_SECRET=TEST_INTEGRITY_SECRET,
)
class InitiateDonationTests(TestCase):
    """POST /api/donations/initiate/"""

    def setUp(self):
        self.url = reverse('donation-initiate')
        self.valid_payload = {
            'tipo': 'general',
            'monto': '50000.00',
            'donante_nombre': 'Juan Pérez',
            'donante_email': 'juan@example.com',
            'metodo_pago': 'card',
            'autorizacion_datos': True,
        }

    def test_initiate_exitoso_retorna_payment_session(self):
        fake_session = {
            'publicKey': 'pub_test',
            'reference': 'GEN-XXXXXXXX',
            'amountInCents': 5000000,
            'currency': 'COP',
            'integritySignature': 'abc123',
            'redirectUrl': 'https://funcreescolombia.org',
            'customerEmail': 'juan@example.com',
            'description': 'Donación general - Funcrees',
            'wompiCheckoutUrl': 'https://sandbox.wompi.co/en-us/checkout/pub_test',
        }
        with mock.patch('donations.views.create_payment_session', return_value=fake_session):
            res = self.client.post(
                self.url,
                data=json.dumps(self.valid_payload),
                content_type='application/json',
            )

        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('referencia', data)
        self.assertIn('paymentSession', data)
        # La donación quedó registrada como pendiente
        self.assertTrue(Donation.objects.filter(referencia=data['referencia']).exists())
        self.assertEqual(Donation.objects.get(referencia=data['referencia']).estado, 'pendiente')

    def test_initiate_sin_autorizacion_datos_rechazado(self):
        payload = dict(self.valid_payload, autorizacion_datos=False)
        res = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_initiate_monto_menor_al_minimo_rechazado(self):
        payload = dict(self.valid_payload, monto='500.00')
        res = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 422)

    def test_initiate_telefono_invalido_rechazado(self):
        payload = dict(self.valid_payload, donante_telefono='abc123!!')
        res = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 422)

    def test_initiate_error_de_wompi_revierte_y_responde_503(self):
        with mock.patch(
            'donations.views.create_payment_session',
            side_effect=Exception('Wompi timeout'),
        ):
            res = self.client.post(
                self.url,
                data=json.dumps(self.valid_payload),
                content_type='application/json',
            )

        self.assertEqual(res.status_code, 503)
        # Atomicidad: no quedan donaciones huérfanas
        self.assertFalse(Donation.objects.exists())


@override_settings(
    WOMPI_ENV='sandbox',
    WOMPI_PUBLIC_KEY='pub_test',
    WOMPI_PRIVATE_KEY='prv_test',
    WOMPI_INTEGRITY_SECRET=TEST_INTEGRITY_SECRET,
)
class WebhookTests(TestCase):
    """POST /api/donations/webhook/"""

    def setUp(self):
        self.url = reverse('donation-webhook')
        self.donation = Donation.objects.create(
            referencia='TEST-0001',
            tipo='general',
            monto=50000,
            donante_nombre='Juan Pérez',
            donante_email='juan@example.com',
            metodo_pago='card',
        )

    def _post_webhook(self, payload: dict):
        return self.client.post(self.url, data=json.dumps(payload), content_type='application/json')

    def test_webhook_firma_valida_actualiza_a_completado(self):
        res = self._post_webhook(_make_webhook_payload('TEST-0001', 5000000, 'APPROVED'))
        self.assertEqual(res.status_code, 200)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.estado, 'completado')
        self.assertEqual(self.donation.referencia_pasarela, 'txn-test-TEST-0001')

    def test_webhook_firma_invalida_rechazado(self):
        payload = _make_webhook_payload('TEST-0001', 5000000, 'APPROVED')
        payload['signature']['checksum'] = 'firma-falsificada'
        res = self._post_webhook(payload)
        self.assertEqual(res.status_code, 400)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.estado, 'pendiente')

    def test_webhook_declined_marca_fallido(self):
        res = self._post_webhook(_make_webhook_payload('TEST-0001', 5000000, 'DECLINED'))
        self.assertEqual(res.status_code, 200)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.estado, 'fallido')

    def test_webhook_es_idempotente(self):
        self._post_webhook(_make_webhook_payload('TEST-0001', 5000000, 'APPROVED'))
        # Wompi reenvía el mismo webhook
        res = self._post_webhook(_make_webhook_payload('TEST-0001', 5000000, 'APPROVED'))
        self.assertEqual(res.status_code, 200)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.estado, 'completado')

    def test_webhook_referencia_inexistente_no_falla(self):
        res = self._post_webhook(_make_webhook_payload('NO-EXISTE', 5000000, 'APPROVED'))
        self.assertEqual(res.status_code, 200)

    def test_webhook_completado_genera_y_envia_certificado(self):
        pdf_bytes = b'%PDF-1.4 test'
        with mock.patch('donations.views.generate_donation_certificate', return_value=pdf_bytes) as m_pdf, \
             mock.patch('donations.views.send_donation_email') as m_email:
            self._post_webhook(_make_webhook_payload('TEST-0001', 5000000, 'APPROVED'))

        m_pdf.assert_called_once()
        m_email.assert_called_once()
        self.donation.refresh_from_db()
        self.assertTrue(self.donation.certificado_enviado)

    def test_webhook_error_de_email_no_rompe_el_webhook(self):
        with mock.patch('donations.views.generate_donation_certificate', return_value=b'pdf'), \
             mock.patch('donations.views.send_donation_email', side_effect=Exception('SMTP down')):
            res = self._post_webhook(_make_webhook_payload('TEST-0001', 5000000, 'APPROVED'))

        # El webhook responde 200 aunque el email haya fallado
        self.assertEqual(res.status_code, 200)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.estado, 'completado')
        self.assertFalse(self.donation.certificado_enviado)


class DonationStatusTests(TestCase):
    """GET /api/donations/{referencia}/status/"""

    def setUp(self):
        self.donation = Donation.objects.create(
            referencia='TEST-STATUS',
            tipo='general',
            monto=25000,
            donante_nombre='Ana Gómez',
            donante_email='ana@example.com',
            metodo_pago='pse',
        )

    def test_status_retorna_datos_publicos(self):
        res = self.client.get(reverse('donation-status', kwargs={'referencia': 'TEST-STATUS'}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        don = data['donacion']
        self.assertEqual(don['referencia'], 'TEST-STATUS')
        # Nunca expone campos cifrados o sensibles
        self.assertNotIn('donante_documento_cifrado', don)
        self.assertNotIn('wompi_response', don)
        self.assertNotIn('ip_origen', don)

    def test_status_404_para_referencia_inexistente(self):
        res = self.client.get(reverse('donation-status', kwargs={'referencia': 'NO-EXISTE'}))
        self.assertEqual(res.status_code, 404)


class EncryptedCharFieldTests(TestCase):
    """Cifrado Fernet en reposo (Ley 1581)."""

    def test_valor_se_cifra_en_base_de_datos(self):
        Donation.objects.create(
            referencia='TEST-CRYPT',
            tipo='general',
            monto=10000,
            donante_nombre='Test',
            donante_email='t@example.com',
            metodo_pago='card',
            donante_telefono_cifrado='3001234567',
        )
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT donante_telefono_cifrado FROM donations_donation WHERE referencia='TEST-CRYPT'")
            raw = cursor.fetchone()[0]

        self.assertIsNotNone(raw)
        # El valor en la BD NO es el plaintext
        self.assertNotEqual(raw, '3001234567')
        # Y es descifrable con la clave actual
        obj = Donation.objects.get(referencia='TEST-CRYPT')
        self.assertEqual(obj.donante_telefono_cifrado, '3001234567')
