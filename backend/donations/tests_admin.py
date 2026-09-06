"""
Tests del admin renovado: acceso al panel, exportación CSV y verificación
manual de pagos con Wompi.

Correr con: python manage.py test donations --settings=core.test_settings
"""
import csv
import io
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Donation

User = get_user_model()


class DonationAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_don', 'admin@funcrees.org', 'x')
        cls.changelist_url = reverse('admin:donations_donation_changelist')

    def test_changelist_requiere_login(self):
        res = self.client.get(self.changelist_url)
        self.assertEqual(res.status_code, 302)
        self.assertIn('admin/login', res.url)

    def test_changelist_carga_con_datos(self):
        Donation.objects.create(
            referencia='TEST-001',
            tipo='general',
            monto=50000,
            donante_nombre='María Pérez',
            donante_email='maria@example.com',
            metodo_pago='PSE',
            estado='completado',
        )
        self.client.force_login(self.staff)
        res = self.client.get(self.changelist_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'María Pérez')
        self.assertContains(res, 'TEST-001')

    def test_accion_exportar_csv(self):
        Donation.objects.create(
            referencia='TEST-CSV-1',
            tipo='apadrinamiento',
            monto=30000,
            donante_nombre='Juan López',
            donante_email='juan@example.com',
            metodo_pago='CARD',
            estado='completado',
        )
        self.client.force_login(self.staff)
        res = self.client.post(
            self.changelist_url,
            {'action': 'exportar_csv', '_selected_action': [str(Donation.objects.get(referencia='TEST-CSV-1').id)]},
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res['Content-Type'])
        rows = list(csv.reader(io.StringIO(res.content.decode('utf-8-sig'))))
        self.assertEqual(rows[0][0], 'Referencia')
        data = [r for r in rows if r and r[0] == 'TEST-CSV-1']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][1], 'Juan López')
        self.assertIn('30000', data[0][3])


class VerificarConWompiTests(TestCase):
    """Acción "Verificar con Wompi" sobre donaciones pendientes."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_ver', 'admin@funcrees.org', 'x')
        cls.changelist = reverse('admin:donations_donation_changelist')

    def _pendiente(self, referencia):
        return Donation.objects.create(
            referencia=referencia,
            tipo='general',
            monto=50000,
            donante_nombre=f'Donante {referencia}',
            donante_email=f'{referencia.lower()}@example.com',
            metodo_pago='PSE',
            estado='pendiente',
        )

    def _post_accion(self, *donaciones):
        return self.client.post(
            self.changelist,
            {'action': 'verificar_con_wompi', '_selected_action': [str(d.id) for d in donaciones]},
        )

    def test_aprueba_pago_pendiente_y_envia_certificado(self):
        d = self._pendiente('VER-APPROVED-1')
        tx_wompi = {'id': 'tx-123', 'status': 'APPROVED', 'reference': 'VER-APPROVED-1'}
        self.client.force_login(self.staff)
        with mock.patch('donations.admin.get_transaction_by_reference', return_value=tx_wompi), \
             mock.patch('donations.views.generate_donation_certificate', return_value=b'pdf'), \
             mock.patch('donations.views.send_donation_email'):
            res = self._post_accion(d)
        self.assertEqual(res.status_code, 302)
        d.refresh_from_db()
        self.assertEqual(d.estado, 'completado')
        self.assertEqual(d.referencia_pasarela, 'tx-123')
        self.assertTrue(d.certificado_enviado)

    def test_declined_marca_fallido_sin_certificado(self):
        d = self._pendiente('VER-DECLINED-1')
        tx_wompi = {'id': 'tx-456', 'status': 'DECLINED', 'reference': 'VER-DECLINED-1'}
        self.client.force_login(self.staff)
        with mock.patch('donations.admin.get_transaction_by_reference', return_value=tx_wompi):
            self._post_accion(d)
        d.refresh_from_db()
        self.assertEqual(d.estado, 'fallido')
        self.assertFalse(d.certificado_enviado)

    def test_wompi_sin_informacion_no_toca_la_donacion(self):
        d = self._pendiente('VER-SININFO-1')
        self.client.force_login(self.staff)
        with mock.patch('donations.admin.get_transaction_by_reference', return_value=None):
            self._post_accion(d)
        d.refresh_from_db()
        self.assertEqual(d.estado, 'pendiente')

    def test_omite_donaciones_ya_confirmadas(self):
        d = Donation.objects.create(
            referencia='VER-OK-1',
            tipo='general',
            monto=10000,
            donante_nombre='Ya Completo',
            donante_email='ok@example.com',
            metodo_pago='CARD',
            estado='completado',
        )
        self.client.force_login(self.staff)
        with mock.patch('donations.admin.get_transaction_by_reference') as m_tx:
            res = self._post_accion(d)
        m_tx.assert_not_called()  # nunca consulta Wompi para las ya completadas
        d.refresh_from_db()
        self.assertEqual(d.estado, 'completado')
