"""
Tests del panel de resumen (dashboard) del admin.

Correr con: python manage.py test core --settings=core.test_settings
"""
import datetime as dt

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from contact.models import ContactMessage
from donations.models import Donation

User = get_user_model()


def _this_month(day=15, hour=12):
    today = timezone.localdate()
    return timezone.make_aware(dt.datetime(today.year, today.month, min(day, today.day), hour))


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('admin_dash', 'admin@funcrees.org', 'x')

    def _get_index_html(self):
        self.client.force_login(self.staff)
        res = self.client.get(reverse('admin:index'))
        self.assertEqual(res.status_code, 200)
        return res.content.decode('utf-8')

    def test_panel_presente_en_el_indice(self):
        html = self._get_index_html()
        self.assertIn('Resumen de la Fundación', html)

    def test_muestra_donacion_completada_del_mes(self):
        Donation.objects.create(
            referencia='DASH-001',
            tipo='general',
            monto=75000,
            donante_nombre='Donante Visible',
            donante_email='visible@example.com',
            metodo_pago='PSE',
            estado='completado',
            creado_en=_this_month(),
        )
        html = self._get_index_html()
        self.assertIn('$75.000', html)

    def test_no_cuenta_donaciones_pendientes_en_el_total(self):
        Donation.objects.create(
            referencia='DASH-PEND',
            tipo='general',
            monto=999999,
            donante_nombre='Pendiente',
            donante_email='p@example.com',
            metodo_pago='CARD',
            estado='pendiente',
            creado_en=_this_month(),
        )
        html = self._get_index_html()
        self.assertNotIn('$999.999', html)
        self.assertIn('pendiente', html)

    def test_muestra_mensajes_recientes(self):
        ContactMessage.objects.create(
            nombre='Visitante Nuevo', email='nuevo@example.com', tipo='consulta', mensaje='Hola'
        )
        html = self._get_index_html()
        self.assertIn('Visitante Nuevo', html)
        self.assertIn('nuevo', html)

    def _donacion(self, referencia, estado='pendiente', antiguedad=None):
        """Crea una donación; auto_now_add ignora creado_en en create(),
        por eso se retrodata con update()."""
        d = Donation.objects.create(
            referencia=referencia,
            tipo='general',
            monto=45000,
            donante_nombre=f'Donante {referencia}',
            donante_email=f'{referencia.lower()}@example.com',
            metodo_pago='PSE',
            estado=estado,
        )
        if antiguedad is not None:
            Donation.objects.filter(pk=d.pk).update(creado_en=timezone.now() - antiguedad)
            d.refresh_from_db()
        return d

    def test_seccion_por_confirmar_aparece_con_pendientes(self):
        """Donaciones pendientes >1h aparecen en la sección del panel."""
        self._donacion('PANEL-PEND', antiguedad=dt.timedelta(hours=3))
        html = self._get_index_html()
        self.assertIn('Pagos por confirmar con Wompi', html)  # sección de atención visible
        self.assertIn('PANEL-PEND', html)

    def test_pendientes_recientes_no_aparecen_en_la_seccion(self):
        """Una donación de hace minutos no exige atención todavía."""
        self._donacion('PANEL-RECENT', antiguedad=dt.timedelta(minutes=10))
        html = self._get_index_html()
        self.assertNotIn('Pagos por confirmar con Wompi', html)

    def test_grafico_barras_seis_meses(self):
        """El gráfico muestra 6 columnas; el mes con donaciones tiene barra."""
        self._donacion('GRAF-1', estado='completado')  # $45.000 en el mes actual
        html = self._get_index_html()
        self.assertIn('Recaudado por mes', html)
        # El mes actual es el único con datos → barra al 100% del máximo
        self.assertIn('style="height: 100%;"', html)
        # Los otros 5 meses quedan en cero (estilo en línea, no la regla CSS)
        self.assertEqual(html.count('style="height: 0%;"'), 5)
        # Etiqueta abreviada colombiana
        self.assertIn('$45 mil', html)

    def test_grafico_formato_millones(self):
        """Montos de 7 dígitos se etiquetan abreviados: $1,5 M."""
        d = self._donacion('GRAF-BIG', estado='completado')
        Donation.objects.filter(pk=d.pk).update(monto=1500000)
        html = self._get_index_html()
        self.assertIn('$1,5 M', html)

    def test_whatsapp_visible_cuando_el_donante_dejo_telefono(self):
        """Fila con teléfono legible: botón WhatsApp con mensaje prellenado."""
        d = self._donacion('WA-CON-TEL', antiguedad=dt.timedelta(hours=3))
        Donation.objects.filter(pk=d.pk).update(donante_telefono_cifrado='3137924439')
        html = self._get_index_html()
        self.assertIn('https://wa.me/573137924439', html)
        self.assertIn('Escribir a Donante WA-CON-TEL', html)
        # Mensaje prellenado con la referencia del pago
        self.assertIn('WA-CON-TEL', html)

    def test_whatsapp_oculto_sin_telefono(self):
        """Sin teléfono del donante no se muestra el botón (no enlaces rotos)."""
        self._donacion('WA-SIN-TEL', antiguedad=dt.timedelta(hours=3))
        html = self._get_index_html()
        self.assertIn('WA-SIN-TEL', html)  # la fila sí aparece
        self.assertNotIn('wa.me', html)

    def test_whatsapp_oculto_con_telefono_extranjero(self):
        """Número sin código +57: no se construye enlace (evitar wa.me inválido)."""
        d = self._donacion('WA-EXTRANJ', antiguedad=dt.timedelta(hours=3))
        Donation.objects.filter(pk=d.pk).update(donante_telefono_cifrado='+1 555 123 4567')
        html = self._get_index_html()
        self.assertIn('WA-EXTRANJ', html)
        self.assertNotIn('wa.me', html)

    def test_requiere_login(self):
        res = self.client.get(reverse('admin:index'))
        self.assertEqual(res.status_code, 302)
