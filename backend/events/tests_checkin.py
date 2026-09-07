"""
Tests del check-in en puerta: vista del panel, permisos y reglas de negocio.

Correr con: python manage.py test events --settings=core.test_settings
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event, Ticket

User = get_user_model()
CHECKIN_URL = '/admin/events/ticket/checkin/'


class CheckinViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('puerta1', 'puerta@funcrees.org', 'x')
        cls.civil = User.objects.create_user('civil', password='x', is_staff=False)
        cls.evento = Event.objects.create(
            id='bingo-checkin',
            titulo='Bingo de Prueba Check-in',
            costo_bono=50000,
        )
        cls.pagada = Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=1,
            comprador_nombre='Ana Pagada',
            comprador_email='ana@example.com',
            monto_pagado=50000,
            estado_pago='pagado',
        )
        cls.pendiente = Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=2,
            comprador_nombre='Beto Pendiente',
            comprador_email='beto@example.com',
            monto_pagado=50000,
            estado_pago='pendiente',
        )
        cls.cancelada = Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=3,
            comprador_nombre='Clara Cancelada',
            comprador_email='clara@example.com',
            monto_pagado=50000,
            estado_pago='cancelado',
        )

    # ── Acceso ────────────────────────────────────────────────────────
    def test_anonimo_redirige_a_login(self):
        res = self.client.get(CHECKIN_URL)
        self.assertEqual(res.status_code, 302)
        self.assertIn('login', res['Location'])

    def test_civil_no_entra(self):
        self.client.force_login(self.civil)
        res = self.client.get(CHECKIN_URL)
        self.assertIn(res.status_code, (302, 403))

    def test_staff_ve_formulario(self):
        self.client.force_login(self.staff)
        res = self.client.get(CHECKIN_URL)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Check-in en puerta')
        self.assertContains(res, 'name="codigo"')

    # ── Búsqueda ──────────────────────────────────────────────────────
    def test_busqueda_normaliza_minusculas(self):
        self.client.force_login(self.staff)
        res = self.client.get(CHECKIN_URL, {'codigo': self.pagada.codigo_verificacion.lower()})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Ana Pagada')

    def test_codigo_desconocido_muestra_error(self):
        self.client.force_login(self.staff)
        res = self.client.get(CHECKIN_URL, {'codigo': 'XXZZYY9988'})
        self.assertContains(res, 'No existe una boleta')

    def test_sin_codigo_muestra_solo_formulario(self):
        self.client.force_login(self.staff)
        res = self.client.get(CHECKIN_URL)
        self.assertNotContains(res, 'class="chk-card"')

    # ── Registro de entrada ───────────────────────────────────────────
    def test_registra_entrada_de_pagada(self):
        self.client.force_login(self.staff)
        res = self.client.post(CHECKIN_URL, {'codigo': self.pagada.codigo_verificacion})
        self.assertEqual(res.status_code, 302)
        self.pagada.refresh_from_db()
        self.assertIsNotNone(self.pagada.checkin_en)
        self.assertEqual(self.pagada.checkin_por, self.staff)
        # Redirect/Get muestra el banner de éxito
        res2 = self.client.get(CHECKIN_URL, {'codigo': self.pagada.codigo_verificacion, 'ok': '1'})
        self.assertContains(res2, 'Entrada registrada')

    def test_duplicado_no_sobrescribe(self):
        original = timezone.now() - timezone.timedelta(hours=2)
        self.pagada.checkin_en = original
        self.pagada.checkin_por = self.staff
        self.pagada.save(update_fields=['checkin_en', 'checkin_por'])

        self.client.force_login(self.staff)
        res = self.client.post(CHECKIN_URL, {'codigo': self.pagada.codigo_verificacion}, follow=True)
        self.pagada.refresh_from_db()
        self.assertEqual(self.pagada.checkin_en, original)
        self.assertContains(res, 'ya estaba registrada')
        # En la tarjeta del GET aparece el aviso persistente
        res2 = self.client.get(CHECKIN_URL, {'codigo': self.pagada.codigo_verificacion})
        self.assertContains(res2, 'Entrada ya registrada')

    def test_pendiente_sin_autorizacion_no_registra(self):
        self.client.force_login(self.staff)
        res = self.client.post(CHECKIN_URL, {'codigo': self.pendiente.codigo_verificacion}, follow=True)
        self.pendiente.refresh_from_db()
        self.assertIsNone(self.pendiente.checkin_en)
        self.assertContains(res, 'pendiente de pago')

    def test_pendiente_con_autorizacion_registra(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            CHECKIN_URL,
            {'codigo': self.pendiente.codigo_verificacion, 'autorizar': '1'},
        )
        self.assertEqual(res.status_code, 302)
        self.pendiente.refresh_from_db()
        self.assertIsNotNone(self.pendiente.checkin_en)
        self.assertEqual(self.pendiente.checkin_por, self.staff)

    def test_cancelado_nunca_registra(self):
        self.client.force_login(self.staff)
        res = self.client.post(
            CHECKIN_URL,
            {'codigo': self.cancelada.codigo_verificacion, 'autorizar': '1'},
            follow=True,
        )
        self.cancelada.refresh_from_db()
        self.assertIsNone(self.cancelada.checkin_en)
        self.assertContains(res, 'no se permite registrar entrada')

    def test_codigo_desconocido_post_no_explota(self):
        self.client.force_login(self.staff)
        res = self.client.post(CHECKIN_URL, {'codigo': 'NADAXX9988'}, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'No existe una boleta')
        self.assertEqual(Ticket.objects.filter(checkin_en__isnull=False).count(), 0)

    # ── Integración con el listado ────────────────────────────────────
    def test_changelist_muestra_columna_asistio_y_boton(self):
        self.client.force_login(self.staff)
        res = self.client.get(reverse('admin:events_ticket_changelist'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Asistió')
        self.assertContains(res, CHECKIN_URL)

    def test_change_form_muestra_checkin_solo_lectura(self):
        self.client.force_login(self.staff)
        res = self.client.get(reverse('admin:events_ticket_change', args=[self.pagada.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Check-in (solo lectura)')

    def test_asistio_property(self):
        self.assertFalse(self.pagada.asistio)
        self.pagada.checkin_en = timezone.now()
        self.assertTrue(self.pagada.asistio)
