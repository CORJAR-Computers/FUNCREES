"""
Tests del endpoint público de cifras: GET /api/stats/.

Correr con: python manage.py test core.tests_stats --settings=core.test_settings

Garantías que se prueban:
- Público (sin autenticación) y de solo lectura (POST rechazado).
- Solo cuenta donaciones CONFIRMADAS (completado); pendientes/fallidas no.
- NUNCA expone datos personales de donantes (nombres, correos, referencias).
- Serie mensual de 12 meses con el mes actual marcado.
- Cacheable: cabecera Cache-Control.
- Throttle scope 'stats' activo (prueba explícita con override_settings).
"""
import datetime as dt
import json

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from donations.models import Donation


def _this_month(day=15, hour=12):
    today = timezone.localdate()
    return timezone.make_aware(dt.datetime(today.year, today.month, min(day, today.day), hour))


class PublicStatsTests(TestCase):
    def setUp(self):
        # Aislamiento: la vista usa cache_page, y LocMemCache persiste entre
        # tests del mismo proceso (serviría respuestas viejas entre tests).
        cache.clear()

    def _donacion(self, referencia, monto, estado, creado_en=None):
        """Crea una donación. auto_now_add ignora creado_en en create(),
        por eso se retrodata con update() cuando hace falta."""
        d = Donation.objects.create(
            referencia=referencia,
            tipo='general',
            monto=monto,
            donante_nombre=f'Donante {referencia}',
            donante_email=f'{referencia.lower()}@example.com',
            metodo_pago='PSE',
            estado=estado,
        )
        if creado_en is not None:
            Donation.objects.filter(pk=d.pk).update(creado_en=creado_en)
            d.refresh_from_db()
        return d

    def test_publico_sin_autenticacion(self):
        res = self.client.get(reverse('public-stats'))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertIn('recaudado_total', data)
        self.assertIn('serie_mensual', data)

    def test_solo_metodo_get(self):
        res = self.client.post(reverse('public-stats'), data={}, content_type='application/json')
        # 405 Method Not Allowed: solo lectura por diseño.
        self.assertEqual(res.status_code, 405)

    def test_solo_cuenta_donaciones_completadas(self):
        self._donacion('STAT-OK', 75000, 'completado', _this_month())
        self._donacion('STAT-PEND', 500000, 'pendiente', _this_month())
        self._donacion('STAT-FAIL', 300000, 'fallido', _this_month())
        res = self.client.get(reverse('public-stats'))
        data = json.loads(res.content)
        self.assertEqual(data['recaudado_total'], 75000)
        self.assertEqual(data['donaciones_count'], 1)

    def test_no_expone_datos_personales(self):
        self._donacion('STAT-SECRETO', 120000, 'completado', _this_month())
        body = self.client.get(reverse('public-stats')).content.decode('utf-8')
        self.assertNotIn('STAT-SECRETO', body)
        self.assertNotIn('Donante STAT-SECRETO', body)
        self.assertNotIn('stat-secreto@example.com', body)

    def test_serie_mensual_doce_meses_mes_actual_marcado(self):
        res = self.client.get(reverse('public-stats'))
        data = json.loads(res.content)
        self.assertEqual(len(data['serie_mensual']), 12)
        marcados = [m for m in data['serie_mensual'] if m['es_actual']]
        self.assertEqual(len(marcados), 1)
        # El último elemento de la serie es el mes en curso
        self.assertTrue(data['serie_mensual'][-1]['es_actual'])

    def test_base_de_datos_vacia_devuelve_ceros_validos(self):
        res = self.client.get(reverse('public-stats'))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data['recaudado_total'], 0)
        self.assertEqual(data['donaciones_count'], 0)
        self.assertEqual(data['donacion_promedio'], 0)
        self.assertEqual(len(data['serie_mensual']), 12)

    def test_respuesta_cacheable(self):
        res = self.client.get(reverse('public-stats'))
        self.assertIn('public', res['Cache-Control'])
        self.assertIn('max-age=120', res['Cache-Control'])

    @override_settings(
        CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
    )
    def test_throttle_scope_stats(self):
        """El throttle limita el endpoint aunque el anon general sea alto."""
        # DRF lee DEFAULT_THROTTLE_RATES al importar (snapshot): override_settings
        # no afecta throttles ya definidos. Se parchea get_rate(), que es lo que
        # cada instancia consulta al crearse.
        from core.views import StatsThrottle
        get_rate_original = StatsThrottle.get_rate
        StatsThrottle.get_rate = lambda self: '3/hour'
        try:
            for _ in range(3):
                res = self.client.get(reverse('public-stats'))
                self.assertEqual(res.status_code, 200)
            res = self.client.get(reverse('public-stats'))
            self.assertEqual(res.status_code, 429)
        finally:
            StatsThrottle.get_rate = get_rate_original
