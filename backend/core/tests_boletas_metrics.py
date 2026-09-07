"""
Tests de las métricas de boletas del panel ("Resumen de la Fundación").

Correr con: python manage.py test core.tests_boletas_metrics --settings=core.test_settings

Cubre la sección de boletas añadida a resumen_fundacion():
- Conteos del mes (registradas / pagadas) y recaudo confirmado del mes.
- Variación % de pagadas vs mes anterior (up/down/flat/sin base).
- Cola de cobro: solo pendientes con más de 48 horas, tope de lista.
- Pagadas sin email del código enviado.
- Agregado por evento (vendidas, pagadas, recaudo).
"""
import datetime as dt
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from core.services import resumen_fundacion
from events.models import Event, Ticket


class BoletasMetricsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.evento = Event.objects.create(
            id='bingo-metricas',
            titulo='Bingo de Métricas',
            fecha='2026-12-01',
            lugar='Sincelejo',
            costo_bono=20000,
        )
        # Mes actual: 2 pagadas + 1 pendiente reciente (no entra a la cola)
        Ticket.objects.create(
            evento=cls.evento, numero_ticket=1,
            comprador_nombre='Ana', comprador_email='ana@example.com',
            monto_pagado=Decimal('20000.00'), estado_pago='pagado',
        )
        Ticket.objects.create(
            evento=cls.evento, numero_ticket=2,
            comprador_nombre='Beto', comprador_email='beto@example.com',
            monto_pagado=Decimal('20000.00'), estado_pago='pagado',
        )
        cls.pendiente_reciente = Ticket.objects.create(
            evento=cls.evento, numero_ticket=3,
            comprador_nombre='Cata', comprador_email='cata@example.com',
            monto_pagado=Decimal('20000.00'), estado_pago='pendiente',
        )
        # Mes anterior: 1 pagada (creado_en retroactivo vía update, porque
        # auto_now_add ignora el valor del constructor)
        cls.pagada_previa = Ticket.objects.create(
            evento=cls.evento, numero_ticket=4,
            comprador_nombre='Diana', comprador_email='diana@example.com',
            monto_pagado=Decimal('20000.00'), estado_pago='pagado',
        )
        Ticket.objects.filter(pk=cls.pagada_previa.pk).update(
            creado_en=timezone.now() - dt.timedelta(days=35)
        )

    def _resumen(self):
        return resumen_fundacion()

    def test_conteos_del_mes_y_recaudo(self):
        r = self._resumen()
        self.assertEqual(r['boletas_vendidas_mes'], 3)
        self.assertEqual(r['boletas_pagadas_mes'], 2)
        self.assertEqual(r['recaudo_boletas_mes'], Decimal('40000.00'))
        # La del mes anterior NO cuenta en el mes actual
        self.assertEqual(r['boletas_pagadas_previo'], 1)

    def test_variacion_positiva_vs_mes_anterior(self):
        r = self._resumen()
        self.assertEqual(r['variacion_boletas'], 100)  # 1 → 2 pagadas
        self.assertEqual(r['variacion_boletas_direccion'], 'up')
        self.assertEqual(r['variacion_boletas_abs'], 100)

    def test_colas_y_aviso_sin_enviar(self):
        # La pendiente reciente está pendiente pero NO en la cola (>48h)
        r = self._resumen()
        self.assertEqual(r['boletas_pendientes_total'], 1)
        self.assertEqual(r['boletas_por_cobrar'], [])
        self.assertEqual(r['boletas_por_cobrar_total'], 0)
        # Las 3 pagadas (2 del mes + 1 del mes previo) aún sin email del código
        self.assertEqual(r['boletas_sin_enviar'], 3)

    def test_cola_cobro_solo_mayores_de_48h(self):
        Ticket.objects.filter(pk=self.pendiente_reciente.pk).update(
            creado_en=timezone.now() - dt.timedelta(days=3)
        )
        r = self._resumen()
        self.assertEqual(r['boletas_por_cobrar_total'], 1)
        self.assertEqual(len(r['boletas_por_cobrar']), 1)
        fila = r['boletas_por_cobrar'][0]
        self.assertEqual(fila['numero'], 3)
        self.assertEqual(fila['evento_titulo'], 'Bingo de Métricas')
        self.assertEqual(fila['monto_fmt'], '$20.000')
        self.assertGreaterEqual(fila['dias'], 3)

    def test_agregado_por_evento(self):
        r = self._resumen()
        por_evento = {e['titulo']: e for e in r['boletas_por_evento']}
        self.assertIn('Bingo de Métricas', por_evento)
        fila = por_evento['Bingo de Métricas']
        self.assertEqual(fila['vendidas'], 4)   # 2 pagadas + 2 creadas en setUp (incluye la del mes previo)
        self.assertEqual(fila['pagadas'], 3)    # 2 del mes + 1 del mes previo
        self.assertEqual(fila['recaudo_fmt'], '$60.000')

    def test_asistidas_cuenta_solo_checkin(self):
        # Sin check-ins todavía: cero. Tras registrar uno en una boleta
        # pendiente (autorizada en puerta), cuenta igual — la persona entró.
        r = self._resumen()
        self.assertEqual(r['boletas_asistidas'], 0)
        self.pendiente_reciente.checkin_en = timezone.now()
        self.pendiente_reciente.save(update_fields=['checkin_en'])
        r = self._resumen()
        self.assertEqual(r['boletas_asistidas'], 1)

    def test_sin_boletas_no_explota(self):
        Ticket.objects.all().delete()
        r = self._resumen()
        self.assertEqual(r['boletas_vendidas_mes'], 0)
        self.assertEqual(r['recaudo_boletas_mes'], 0)
        self.assertEqual(r['variacion_boletas_direccion'], 'flat')
        self.assertEqual(r['boletas_por_evento'], [])
