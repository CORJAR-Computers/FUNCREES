"""
Tests del endpoint público de contacto.

Correr con: python manage.py test contact
"""
import json

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage


@override_settings(RATELIMIT_ENABLE=True)
class ContactMessageTests(TestCase):
    """POST /api/contact/"""

    def setUp(self):
        self.url = reverse('contact-list')
        self.valid_payload = {
            'nombre': 'María López',
            'email': 'maria@example.com',
            'telefono': '3001234567',
            'tipo': 'consulta',
            'mensaje': 'Quisiera información sobre el apadrinamiento.',
        }

    def _post(self, payload):
        return self.client.post(self.url, data=json.dumps(payload), content_type='application/json')

    def test_creacion_exitosa(self):
        res = self._post(self.valid_payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.nombre, 'María López')
        self.assertEqual(msg.ip_origen, '127.0.0.1')

    def test_telefono_invalido_rechazado(self):
        payload = dict(self.valid_payload, telefono='123')
        res = self._post(payload)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_mensaje_demasiado_largo_rechazado(self):
        payload = dict(self.valid_payload, mensaje='x' * 2001)
        res = self._post(payload)
        self.assertEqual(res.status_code, 400)

    def test_telefono_con_formato_internacional_aceptado(self):
        payload = dict(self.valid_payload, telefono='+57 300 123 4567')
        res = self._post(payload)
        self.assertEqual(res.status_code, 201)

    def test_get_no_permitido_solo_create(self):
        res = self.client.get(self.url)
        self.assertIn(res.status_code, (403, 405))
