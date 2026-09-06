"""
Tests del monitor de disponibilidad (comando check_uptime + servicios).

Correr con: python manage.py test core.tests_uptime --settings=core.test_settings

Garantías que se prueban:
- Verificación de URLs con respuestas simuladas (200 → ok, 5xx/timeout → caído).
- Anti-ruido: 1 fallo NO alerta; el 2.º consecutivo declara la caída.
- Recordatorio cuando sigue caído (y no-aviso antes del intervalo).
- Correo de recuperación con la duración de la caída.
- Un solo correo por ronda cuando backend y frontend caen juntos.
- --dry-run nunca escribe estado ni envía correo.
- --force-email envía correo y el asunto nunca miente.
- Heartbeat externo: solo pega cuando todo está bien.
- Exit codes: 0 todo bien, 1 si algo está caído.
"""
import datetime as dt
import tempfile
from pathlib import Path
from unittest import mock

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from core.services.uptime import (
    actualizar_estado,
    cargar_estado,
    dominio_de,
    eventos_a_notificar,
    formato_duracion,
    guardar_estado,
    verificar_servicios,
)

OK_BACKEND = {'servicio': 'backend', 'url': 'http://b/', 'ok': True, 'http_status': 200, 'latencia_ms': 12, 'error': None}
OK_FRONTEND = {'servicio': 'frontend', 'url': 'http://f/', 'ok': True, 'http_status': 200, 'latencia_ms': 20, 'error': None}
FALLA_BACKEND = {**OK_BACKEND, 'ok': False, 'http_status': None, 'error': 'ConnectionError'}
FALLA_FRONTEND = {**OK_FRONTEND, 'ok': False, 'http_status': None, 'error': 'ConnectionError'}


def _run(rondas):
    """Ejecuta la máquina de estados con la secuencia de rondas dada y
    devuelve (estado, notificaciones de la última ronda)."""
    estado = {'servicios': {}}
    a_notificar = []
    for resultados in rondas:
        estado, eventos = actualizar_estado(estado, resultados)
        a_notificar = eventos_a_notificar(estado, eventos)
    return estado, a_notificar


class _Captura:
    """stdout/stderr en memoria para call_command."""

    def __init__(self):
        self.contenido = ''

    def write(self, texto):
        self.contenido += str(texto)

    def flush(self):
        pass


class FormatoDuracionTests(TestCase):
    def test_formatos(self):
        self.assertEqual(formato_duracion(dt.timedelta(seconds=45)), '45s')
        self.assertEqual(formato_duracion(dt.timedelta(minutes=12)), '12 min')
        self.assertEqual(formato_duracion(dt.timedelta(hours=3, minutes=5)), '3h 5min')
        self.assertEqual(formato_duracion(dt.timedelta(hours=3)), '3h')
        self.assertEqual(formato_duracion(dt.timedelta(days=2, hours=4)), '2d 4h')
        self.assertEqual(formato_duracion(None), '—')


class DominioTests(TestCase):
    def test_dominio_de(self):
        self.assertEqual(dominio_de('http://127.0.0.1:3000/'), '127.0.0.1:3000')
        self.assertEqual(dominio_de('https://funcreescolombia.org/api/health/'), 'funcreescolombia.org')


class VerificarServiciosTests(TestCase):
    def _ejecutar(self, lado):
        """Llama verificar_servicios simulando `requests.get` con `lado`."""
        with mock.patch('core.services.uptime.requests.get', side_effect=lado):
            return verificar_servicios({
                'backend': 'http://bak/api/health/',
                'frontend': 'http://fro/',
            })

    def test_200_es_ok(self):
        resp = mock.Mock(status_code=200)
        res = self._ejecutar([resp, resp])
        self.assertTrue(all(r['ok'] for r in res))
        self.assertTrue(all(r['latencia_ms'] >= 0 for r in res))
        self.assertIsNone(res[0]['error'])

    def test_5xx_y_timeout_son_caidas(self):
        import requests
        resp = mock.Mock(status_code=502)
        timeout = requests.exceptions.ConnectTimeout('tardó')
        res = self._ejecutar([resp, timeout])
        self.assertEqual([r['ok'] for r in res], [False, False])
        self.assertIn('502', res[0]['error'])
        self.assertIn('ConnectTimeout', res[1]['error'])

    def test_404_cuenta_como_vivo(self):
        """Un 404 NO es caída: el servidor respondió (p.ej. reescritura de Nginx)."""
        resp = mock.Mock(status_code=404)
        res = self._ejecutar([resp, resp])
        self.assertTrue(all(r['ok'] for r in res))


class EstadoTests(TestCase):
    def test_estado_corrupto_reinicia_limpio(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / 'estado.json'
            ruta.write_text('{no soy json', encoding='utf-8')
            with override_settings(UPTIME_STATE_FILE=str(ruta)):
                self.assertEqual(cargar_estado(), {'servicios': {}})

    def test_estado_guarda_y_carga(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / 'estado.json'
            with override_settings(UPTIME_STATE_FILE=str(ruta)):
                estado = {'servicios': {'backend': {'fallos': 1}}}
                guardar_estado(estado)
                self.assertEqual(cargar_estado()['servicios']['backend']['fallos'], 1)
                # Guardado atómico: no debe quedar ningún .tmp suelto
                self.assertEqual(list(Path(d).glob('*.tmp')), [])


@override_settings(UPTIME_FALLOS_PARA_ALERTA=2, UPTIME_REMINDER_HOURS=2.0)
class MaquinaEstadosTests(TestCase):
    def test_un_fallo_no_alerta(self):
        estado, notif = _run([[FALLA_BACKEND, OK_FRONTEND]])
        self.assertEqual(notif, [])
        self.assertEqual(estado['servicios']['backend']['fallos'], 1)
        self.assertIsNone(estado['servicios']['backend'].get('down_since'))

    def test_segundo_fallo_declara_caida(self):
        estado, notif = _run([[FALLA_BACKEND, OK_FRONTEND]] * 2)
        self.assertEqual(len(notif), 1)
        ev = notif[0]
        self.assertEqual(ev['tipo'], 'caida')
        self.assertEqual(ev['servicio'], 'backend')
        self.assertEqual(ev['error'], 'ConnectionError')
        self.assertIsNotNone(estado['servicios']['backend']['down_since'])

    def test_recuperacion_al_primer_exito(self):
        estado, notif = _run([
            [FALLA_BACKEND, OK_FRONTEND],
            [FALLA_BACKEND, OK_FRONTEND],
            [OK_BACKEND, OK_FRONTEND],
        ])
        self.assertEqual([ev['tipo'] for ev in notif], ['recuperacion'])
        rec = notif[0]
        self.assertEqual(rec['servicio'], 'backend')
        self.assertIsNone(estado['servicios']['backend']['down_since'])
        self.assertGreaterEqual(rec['duracion'], dt.timedelta(0))

    def test_dos_servicios_caidos_un_evento_por_servicio(self):
        """Backend y frontend caen juntos: un evento por servicio en la MISMA
        ronda (el comando los agrupa en UN correo), no duplicados."""
        estado, notif = _run([[FALLA_BACKEND, FALLA_FRONTEND]] * 2)
        self.assertEqual([ev['servicio'] for ev in notif], ['backend', 'frontend'])
        self.assertEqual([ev['tipo'] for ev in notif], ['caida', 'caida'])

    def test_recordatorio_solo_tras_el_intervalo(self):
        ahora = timezone.now()
        estado = {'servicios': {}}
        # Dos rondas fallidas: la 2.ª declara la caída
        estado, ev1 = actualizar_estado(estado, [FALLA_BACKEND, OK_FRONTEND], ahora=ahora)
        estado, ev2 = actualizar_estado(estado, [FALLA_BACKEND, OK_FRONTEND], ahora=ahora + dt.timedelta(minutes=5))
        self.assertEqual(ev1, [])
        self.assertEqual([ev['tipo'] for ev in ev2], ['caida'])
        eventos_a_notificar(estado, ev2, ahora=ahora + dt.timedelta(minutes=5))

        # Ronda ANTES del intervalo (2h): sin recordatorio
        antes = eventos_a_notificar(estado, [], ahora=ahora + dt.timedelta(minutes=40))
        self.assertEqual(antes, [])
        # Ronda DESPUÉS del intervalo: recordatorio
        despues = eventos_a_notificar(estado, [], ahora=ahora + dt.timedelta(hours=2, minutes=10))
        self.assertEqual([ev['tipo'] for ev in despues], ['recordatorio'])
        self.assertEqual(despues[0]['servicio'], 'backend')

    def test_recordatorio_sin_notificacion_previa(self):
        """Si el proceso murió justo tras declarar la caída (sin last_notified),
        el siguiente cron envía el recordatorio igualmente."""
        ahora = timezone.now()
        estado = {
            'servicios': {
                'backend': {
                    'down_since': (ahora - dt.timedelta(hours=3)).isoformat(),
                    'last_error': 'ConnectionError',
                    'fallos': 999,
                    # sin last_notified
                },
                'frontend': {},
            }
        }
        notif = eventos_a_notificar(estado, [], ahora=ahora)
        self.assertEqual([ev['tipo'] for ev in notif], ['recordatorio'])

    def test_recuperacion_limpia_el_recordatorio(self):
        """Tras recuperarse, el servicio no debe volver a notificar nada."""
        ahora = timezone.now()
        estado = {
            'servicios': {
                'backend': {
                    'down_since': (ahora - dt.timedelta(hours=3)).isoformat(),
                    'last_notified': (ahora - dt.timedelta(hours=1)).isoformat(),
                    'last_error': 'ConnectionError',
                    'fallos': 3,
                },
                'frontend': {},
            }
        }
        estado, eventos = actualizar_estado(estado, [OK_BACKEND, OK_FRONTEND], ahora=ahora)
        notif = eventos_a_notificar(estado, eventos, ahora=ahora)
        self.assertEqual([ev['tipo'] for ev in notif], ['recuperacion'])
        # Y una ronda después, nada:
        notif2 = eventos_a_notificar(estado, [], ahora=ahora + dt.timedelta(hours=5))
        self.assertEqual(notif2, [])


class ComandoTests(TestCase):
    """El comando completo con requests simulado, estado aislado y reloj
    controlado (el comando usa exit codes: 0 OK, 1 caído)."""

    def _config(self, **kw):
        tmp = tempfile.mkdtemp(prefix='uptime-test-')
        cfg = {
            'UPTIME_STATE_FILE': str(Path(tmp) / 'estado.json'),
            'UPTIME_BACKEND_URL': 'http://bak/api/health/',
            'UPTIME_FRONTEND_URL': 'http://fro/',
            'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
        }
        cfg.update(kw)
        return override_settings(**cfg)

    def _simular(self, ok_backend=True, ok_frontend=True):
        def lado(url, timeout=None):
            if 'bak' in url:
                return mock.Mock(status_code=200 if ok_backend else 503)
            return mock.Mock(status_code=200 if ok_frontend else 503)
        return lado

    def _correr(self, *args, **kwargs):
        """call_command capturando SystemExit; devuelve el exit code."""
        try:
            call_command(*args, **kwargs)
            return 0
        except SystemExit as e:
            return e.code or 0

    def test_todo_ok_no_envia_nada(self):
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular()):
                self.assertEqual(self._correr('check_uptime'), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_caida_envia_un_correo_con_ambos_servicios(self):
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            lado = self._simular(ok_backend=False, ok_frontend=False)
            with mock.patch('core.services.uptime.requests.get', side_effect=lado):
                self.assertEqual(self._correr('check_uptime'), 1)  # ronda 1: aún bajo umbral
                self.assertEqual(self._correr('check_uptime'), 1)  # ronda 2: declara caída
            self.assertEqual(len(mail.outbox), 1)
            msg = mail.outbox[0]
            self.assertEqual(msg.to, ['ops@funcrees.org'])
            self.assertIn('🔴 FUNCREES caído', msg.subject)
            self.assertIn('Backend', msg.subject)
            self.assertIn('Sitio web', msg.subject)
            html = next(a for a in msg.alternatives if a[1] == 'text/html')[0]
            self.assertIn('CAÍDA', html)
            self.assertIn('systemctl', html)  # sugerencia de acción
            self.assertIn('Verificado el', html)

    def test_recordatorio_cuando_sigue_caido(self):
        """Tras la alerta inicial, el recordatorio llega solo cuando pasa el
        intervalo (reloj simulado: +2h01m entre rondas)."""
        base = timezone.now()
        momentos = [base, base, base + dt.timedelta(hours=2, minutes=1)]
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            lado = self._simular(ok_backend=False)
            with mock.patch('core.services.uptime.requests.get', side_effect=lado):
                with mock.patch(
                    'core.management.commands.check_uptime.timezone.now',
                    side_effect=momentos,
                ):
                    self._correr('check_uptime')  # fallo 1
                    self._correr('check_uptime')  # caída → correo 1
                    self._correr('check_uptime')  # +2h01m → recordatorio → correo 2
            self.assertEqual(len(mail.outbox), 2)
            self.assertIn('🔴 FUNCREES caído', mail.outbox[1].subject)
            html = mail.outbox[1].alternatives[0][0]
            self.assertIn('SIGUE CAÍDO', html)

    def test_sin_recordatorio_antes_del_intervalo(self):
        base = timezone.now()
        momentos = [base, base, base + dt.timedelta(minutes=10)]
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            lado = self._simular(ok_backend=False)
            with mock.patch('core.services.uptime.requests.get', side_effect=lado):
                with mock.patch(
                    'core.management.commands.check_uptime.timezone.now',
                    side_effect=momentos,
                ):
                    self._correr('check_uptime')
                    self._correr('check_uptime')  # caída → correo 1
                    self._correr('check_uptime')  # +10 min: aún sin recordatorio
            self.assertEqual(len(mail.outbox), 1)

    def test_recuperacion_envia_confirmacion_con_duracion(self):
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular(ok_backend=False)):
                self._correr('check_uptime')
                self._correr('check_uptime')  # caída
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular()):
                self.assertEqual(self._correr('check_uptime'), 0)  # recuperación
            self.assertEqual(len(mail.outbox), 2)
            msg = mail.outbox[1]
            self.assertIn('✅ FUNCREES en línea de nuevo', msg.subject)
            self.assertIn('Backend', msg.subject)
            self.assertIn('estuvo caído', msg.subject)
            html = msg.alternatives[0][0]
            self.assertIn('RECUPERADO', html)
            self.assertIn('Estuvo caído', html)

    def test_recuperacion_de_frontend_con_backend_caido(self):
        """Frontend se recupera mientras el backend sigue caído: el asunto debe
        seguir rojo (lo que manda es lo que está caído AHORA)."""
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular(ok_backend=False, ok_frontend=False)):
                self._correr('check_uptime')
                self._correr('check_uptime')  # ambos caídos
            self.assertEqual(len(mail.outbox), 1)
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular(ok_backend=False)):
                self._correr('check_uptime')  # frontend ok, backend no
            self.assertEqual(len(mail.outbox), 2)
            self.assertIn('🔴 FUNCREES caído', mail.outbox[1].subject)
            self.assertIn('Backend', mail.outbox[1].subject)
            html = mail.outbox[1].alternatives[0][0]
            self.assertIn('RECUPERADO', html)   # frontend
            # El backend aparece caído en la tabla de verificación; el panel
            # "SIGUE CAÍDO" llega solo con el recordatorio (+2h), no aquí.
            self.assertIn('🔴 Caído', html)
            self.assertNotIn('SIGUE CAÍDO', html)

    def test_destinatarios_fallback_a_digest_to(self):
        with self._config(UPTIME_ALERT_TO='', DIGEST_TO='directiva@funcrees.org'):
            lado = self._simular(ok_backend=False)
            with mock.patch('core.services.uptime.requests.get', side_effect=lado):
                self._correr('check_uptime')
                self._correr('check_uptime')
            self.assertEqual(mail.outbox[0].to, ['directiva@funcrees.org'])

    def test_sin_destinatarios_avisa_y_no_envia(self):
        with self._config(UPTIME_ALERT_TO='', DIGEST_TO=''):
            lado = self._simular(ok_backend=False)
            out = _Captura()
            with mock.patch('core.services.uptime.requests.get', side_effect=lado):
                self._correr('check_uptime')
                codigo = self._correr('check_uptime', stdout=out)
            self.assertEqual(codigo, 1)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn('destinatarios', out.contenido.lower())

    def test_dry_run_no_guarda_ni_envia(self):
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            lado = self._simular(ok_backend=False)
            out = _Captura()
            with mock.patch('core.services.uptime.requests.get', side_effect=lado):
                codigo = self._correr('check_uptime', '--dry-run', stdout=out)
                codigo = self._correr('check_uptime', '--dry-run', stdout=out)
            self.assertEqual(codigo, 1)  # algo caído aunque sea dry-run
            self.assertEqual(len(mail.outbox), 0)
            # El estado NO se escribió: el archivo ni siquiera existe
            from django.conf import settings as s
            self.assertFalse(Path(s.UPTIME_STATE_FILE).exists())
            self.assertIn('DRY-RUN', out.contenido)
            self.assertIn('🔴', out.contenido)

    def test_force_email_envia_resumen_ok(self):
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular()):
                self.assertEqual(self._correr('check_uptime', '--force-email'), 0)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, '✅ FUNCREES monitor: todo funciona')
            html = mail.outbox[0].alternatives[0][0]
            self.assertIn('Todo funciona', html)

    def test_force_email_durante_caida_mantiene_asunto_rojo(self):
        """--force-email con un servicio caído: envía el correo, pero el asunto
        NO dice que todo funciona."""
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            lado = self._simular(ok_backend=False)
            with mock.patch('core.services.uptime.requests.get', side_effect=lado):
                self._correr('check_uptime', '--force-email')
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('🔴 FUNCREES caído', mail.outbox[0].subject)
            self.assertNotIn('todo funciona', mail.outbox[0].subject.lower())

    def test_heartbeat_solo_cuando_todo_ok(self):
        # ping_heartbeat se importa en el namespace del comando: parchar ahí
        with self._config(UPTIME_HEARTBEAT_URL='https://hc.example/ping'):
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular()):
                with mock.patch('core.management.commands.check_uptime.ping_heartbeat') as hb:
                    self._correr('check_uptime')
            hb.assert_called_once_with('https://hc.example/ping')
        # Con backend caído: el heartbeat NO se ejecuta
        with self._config(UPTIME_HEARTBEAT_URL='https://hc.example/ping', UPTIME_ALERT_TO=''):
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular(ok_backend=False)):
                with mock.patch('core.management.commands.check_uptime.ping_heartbeat') as hb:
                    self._correr('check_uptime')
        hb.assert_not_called()

    def test_exit_codes(self):
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular()):
                self.assertEqual(self._correr('check_uptime'), 0)
        with self._config(UPTIME_ALERT_TO='ops@funcrees.org'):
            with mock.patch('core.services.uptime.requests.get', side_effect=self._simular(ok_backend=False)):
                self.assertEqual(self._correr('check_uptime'), 1)  # fallo sin alerta
                self.assertEqual(self._correr('check_uptime'), 1)  # caída + correo
