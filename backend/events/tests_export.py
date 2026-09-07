"""
Tests del export CSV de boletas y la barra de asistencia por evento.

Correr con: python manage.py test events.tests_export --settings=core.test_settings

Cubre:
- Acción "Exportar boletas a CSV": delimitador ';' (Excel en español usa
  coma como separador decimal), BOM UTF-8, columnas de check-in y nombre
  de archivo con fecha.
- Columna "Asistencia (entradas / pagadas)" del listado de eventos con
  enlace al listado de boletas filtrado.
"""
import csv
import io

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event, Ticket

User = get_user_model()


class ExportCsvBoletasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('exporta', 'exporta@funcrees.org', 'x')
        cls.evento = Event.objects.create(
            id='bingo-export',
            titulo='Bingo Export Área Ñ',  # tildes/ñ para probar el BOM
            costo_bono=50000,
        )
        cls.pagada = Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=1,
            comprador_nombre='Ana Saldaña',
            comprador_email='ana@example.com',
            monto_pagado=50000,
            estado_pago='pagado',
        )
        cls.pendiente = Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=2,
            comprador_nombre='Beto Pérez',
            comprador_email='beto@example.com',
            monto_pagado=50000,
            estado_pago='pendiente',
        )
        # Ana ya entró al evento
        cls.pagada.checkin_en = timezone.now()
        cls.pagada.checkin_por = cls.staff
        cls.pagada.save(update_fields=['checkin_en', 'checkin_por'])

    def _exporta(self, ids):
        self.client.force_login(self.staff)
        return self.client.post(
            reverse('admin:events_ticket_changelist'),
            {'action': 'exportar_csv', '_selected_action': [str(t.pk) for t in ids]},
        )

    def test_respuesta_csv_con_bom_y_delimitador_punto_y_coma(self):
        res = self._exporta([self.pagada, self.pendiente])
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res['Content-Type'])
        self.assertIn('attachment', res['Content-Disposition'])
        self.assertIn('.csv', res['Content-Disposition'])
        contenido = res.content.decode('utf-8-sig')
        self.assertTrue(contenido.startswith('Evento;'), 'el delimitador debe ser ";"')

    def test_incluye_datos_de_checkin_en_el_csv(self):
        res = self._exporta([self.pagada])
        rows = list(csv.reader(io.StringIO(res.content.decode('utf-8-sig')), delimiter=';'))
        self.assertEqual(rows[0][7], 'Entrada registrada')
        self.assertEqual(rows[0][8], 'Registrada por')
        fila = next(r for r in rows if r[1] == '1')
        self.assertEqual(fila[2], 'Ana Saldaña')
        self.assertEqual(fila[4], 'Pagado')
        self.assertEqual(fila[6], self.pagada.codigo_verificacion)
        self.assertNotEqual(fila[7], 'No')  # tiene fecha de entrada
        self.assertEqual(fila[8], 'exporta')

    def test_pendiente_sin_entrada_exporta_como_no(self):
        res = self._exporta([self.pendiente])
        rows = list(csv.reader(io.StringIO(res.content.decode('utf-8-sig')), delimiter=';'))
        fila = next(r for r in rows if r[1] == '2')
        self.assertEqual(fila[4], 'Pendiente')
        self.assertEqual(fila[7], 'No')
        self.assertEqual(fila[8], '')

    def test_exporta_filas_tildes_legibles(self):
        res = self._exporta([self.pagada])
        contenido = res.content.decode('utf-8-sig')
        self.assertIn('Bingo Export Área Ñ', contenido)
        self.assertIn('Ana Saldaña', contenido)

    def test_civil_no_puede_exportar(self):
        civil = User.objects.create_user('civilx', password='x', is_staff=False)
        self.client.force_login(civil)
        res = self.client.post(
            reverse('admin:events_ticket_changelist'),
            {'action': 'exportar_csv', '_selected_action': [str(self.pagada.pk)]},
        )
        self.assertIn(res.status_code, (302, 403))


class AsistenciaPorEventoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('porta', 'porta@funcrees.org', 'x')
        cls.evento = Event.objects.create(id='bingo-asistencia', titulo='Bingo Asistencia', costo_bono=10000)
        cls.pagada = Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=1,
            comprador_nombre='Ana',
            comprador_email='ana@example.com',
            monto_pagado=10000,
            estado_pago='pagado',
        )
        Ticket.objects.create(
            evento=cls.evento,
            numero_ticket=2,
            comprador_nombre='Beto',
            comprador_email='beto@example.com',
            monto_pagado=10000,
            estado_pago='pagado',
        )

    def _changelist(self):
        self.client.force_login(self.staff)
        return self.client.get(reverse('admin:events_event_changelist'))

    def test_columna_muestra_cero_de_dos_sin_checkin(self):
        res = self._changelist()
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '0 / 2')

    def test_columna_actualiza_tras_checkin(self):
        self.pagada.checkin_en = timezone.now()
        self.pagada.save(update_fields=['checkin_en'])
        res = self._changelist()
        self.assertContains(res, '1 / 2')
        self.assertContains(res, 'asistencia-bar')

    def test_enlace_filtra_boletas_asistidas(self):
        self.pagada.checkin_en = timezone.now()
        self.pagada.save(update_fields=['checkin_en'])
        res = self._changelist()
        self.assertContains(res, f'evento__id__exact={self.evento.pk}')
        self.assertContains(res, 'asistio=si')
        # El filtro realmente devuelve solo las asistidas
        self.client.force_login(self.staff)
        res2 = self.client.get(
            reverse('admin:events_ticket_changelist'),
            {'evento__id__exact': self.evento.pk, 'asistio': 'si'},
        )
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, 'Ana')
        self.assertNotContains(res2, 'Beto')

    def test_filtro_asistio_no_redirige_con_error(self):
        """Regresión: BooleanFieldListFilter sobre DateTimeField mandaba
        ?e=1 (IncorrectLookupParameters). El SimpleListFilter no debe."""
        self.client.force_login(self.staff)
        for valor in ('si', 'no'):
            res = self.client.get(
                reverse('admin:events_ticket_changelist'), {'asistio': valor}
            )
            self.assertEqual(res.status_code, 200, f'valor={valor}')
            self.assertNotIn('e=1', res.get('Location', ''))
