"""
Tests del admin de mensajes de contacto: acciones de seguimiento.

Correr con: python manage.py test contact --settings=core.test_settings
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage

User = get_user_model()


class ContactAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_ct', 'admin@funcrees.org', 'x')
        cls.m1 = ContactMessage.objects.create(
            nombre='Rosa Díaz', email='rosa@example.com', tipo='voluntariado', mensaje='Quiero ayudar'
        )
        cls.m2 = ContactMessage.objects.create(
            nombre='Empresa SA', email='info@empresa.com', tipo='alianza', mensaje='Propuesta de alianza', leido=True
        )

    def test_changelist_muestra_mensajes(self):
        self.client.force_login(self.staff)
        res = self.client.get(reverse('admin:contact_contactmessage_changelist'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Rosa Díaz')
        self.assertContains(res, 'Empresa SA')

    def test_accion_marcar_leido(self):
        self.client.force_login(self.staff)
        self.client.post(
            reverse('admin:contact_contactmessage_changelist'),
            {'action': 'marcar_como_leido', '_selected_action': [str(self.m1.id)]},
        )
        self.m1.refresh_from_db()
        self.assertTrue(self.m1.leido)

    def test_accion_marcar_respondido(self):
        self.client.force_login(self.staff)
        self.client.post(
            reverse('admin:contact_contactmessage_changelist'),
            {'action': 'marcar_como_respondido', '_selected_action': [str(self.m1.id), str(self.m2.id)]},
        )
        self.m1.refresh_from_db()
        self.m2.refresh_from_db()
        self.assertTrue(self.m1.respondido)
        self.assertTrue(self.m2.respondido)
