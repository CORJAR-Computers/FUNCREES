"""
Monitor de disponibilidad del sitio público de FUNCREES.

Verifica que el backend (Django/gunicorn + base de datos, vía /api/health/)
y el frontend (SvelteKit adapter-node) respondan. Cuando un servicio se cae,
el comando `check_uptime` avisa por correo al personal; cuando se recupera,
envía la confirmación con la duración de la caída.

Diseño (sin dependencias nuevas, usa `requests` que ya trae el proyecto):
- Anti-ruido: una caída se declara tras UPTIME_FALLOS_PARA_ALERTA fallos
  consecutivos, para no avisar por micro-cortes durante un despliegue.
- Recordatorios: mientras siga caído, se re-avisa cada UPTIME_REMINDER_HOURS.
- Estado: backend/logs/uptime_state.json (gitignored). Permite saber si algo
  ya estaba caído antes del chequeo actual y cuánto tiempo lleva.
- Un solo correo por ejecución: si backend y frontend fallan a la vez, el
  personal recibe UNA alerta con ambos, no dos correos.

Lo consume exclusivamente el comando de gestión `check_uptime` (cron cada
5 minutos en producción; ver DEPLOY.md, sección "🟢 Monitor de disponibilidad").
"""
import json
import logging
import os
import time
import datetime as dt
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Servicios que se verifican, en orden de importancia.
SERVICIOS = ('backend', 'frontend')

NOMBRE_SERVICIO = {
    'backend': 'Backend (API y base de datos)',
    'frontend': 'Sitio web (frontend)',
}


# ═══════════════════════════════════════════════════════════════════
# Estado persistente
# ═══════════════════════════════════════════════════════════════════

def _ruta_estado():
    return getattr(settings, 'UPTIME_STATE_FILE', None)


def cargar_estado() -> dict:
    """Lee el estado previo del monitor. Nunca falla: archivo ausente
    (primera ejecución, situación normal) => estado limpio y sin ruido en el
    log; contenido corrupto o con otra estructura => estado limpio con aviso."""
    path = _ruta_estado()
    if not path:
        return {'servicios': {}}
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict) or not isinstance(data.get('servicios', {}), dict):
            raise ValueError('estructura inesperada')
        data.setdefault('servicios', {})
        return data
    except FileNotFoundError:
        return {'servicios': {}}  # primera ejecución: normal, sin ruido
    except (OSError, ValueError) as exc:
        # ValueError cubre JSONDecodeError (contenido corrupto).
        logger.warning('Estado del monitor ilegible (%s); se reinicia.', exc)
        return {'servicios': {}}


def guardar_estado(estado: dict) -> None:
    """Persiste el estado de forma atómica (escribe .tmp y renombra) para que
    una ejecución interrumpida nunca deje un JSON a medias."""
    path = _ruta_estado()
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f'{path}.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


# ═══════════════════════════════════════════════════════════════════
# Verificación
# ═══════════════════════════════════════════════════════════════════

def _urls_por_defecto() -> dict:
    return {
        'backend': getattr(settings, 'UPTIME_BACKEND_URL', 'http://127.0.0.1:8000/api/health/'),
        'frontend': getattr(settings, 'UPTIME_FRONTEND_URL', 'http://127.0.0.1:3000/'),
    }


def verificar_servicios(urls: dict | None = None) -> list[dict]:
    """Verifica cada servicio y devuelve resultados:

        [{'servicio': 'backend', 'url': ..., 'ok': True,
          'http_status': 200, 'latencia_ms': 42, 'error': None}, ...]

    Criterio: respuesta con estado < 500 => el servidor está vivo (un 404 de
    una ruta reescrita no es una caída); 5xx, timeout o error de conexión => caída.
    Nunca lanza excepciones: un servicio caído es un resultado, no un error del monitor.
    """
    urls = urls or _urls_por_defecto()
    timeout_total = getattr(settings, 'UPTIME_TIMEOUT', 10)
    resultados = []
    for nombre in SERVICIOS:
        url = urls.get(nombre)
        if not url:
            continue
        inicio = time.monotonic()
        ok, status, error = False, None, None
        try:
            resp = requests.get(url, timeout=(5, timeout_total))
            status = resp.status_code
            ok = status < 500
            if not ok:
                error = f'HTTP {status}'
        except requests.RequestException as exc:
            error = type(exc).__name__ + (f': {exc}' if str(exc) else '')
            error = error[:200]  # el texto va al correo; no necesita el detalle completo
        latencia_ms = int((time.monotonic() - inicio) * 1000)
        resultados.append({
            'servicio': nombre,
            'url': url,
            'ok': ok,
            'http_status': status,
            'latencia_ms': latencia_ms,
            'error': error,
        })
    return resultados


# ═══════════════════════════════════════════════════════════════════
# Máquina de estados: resultados → eventos notificables
# ═══════════════════════════════════════════════════════════════════

def actualizar_estado(estado: dict, resultados: list[dict], ahora=None) -> tuple[dict, list[dict]]:
    """Integra los resultados de esta ronda en el estado y devuelve
    (estado, eventos_nuevos). Eventos posibles:

        {'tipo': 'caida',        'servicio': ..., 'error': ..., 'desde': dt}
        {'tipo': 'recuperacion', 'servicio': ..., 'desde': dt, 'duracion': timedelta}

    La caída se declara en el fallo consecutivo N (configurable) y la
    recuperación en el primer éxito. `estado` se muta in place y también se
    retorna por comodidad."""
    ahora = ahora or timezone.now()
    umbral = getattr(settings, 'UPTIME_FALLOS_PARA_ALERTA', 2)
    eventos = []
    for r in resultados:
        s = estado['servicios'].setdefault(r['servicio'], {})
        s['last_check'] = ahora.isoformat()
        s['latencia_ms'] = r['latencia_ms']
        if r['ok']:
            s['fallos'] = 0
            s['last_error'] = None
            s['last_ok'] = ahora.isoformat()
            if s.get('down_since'):
                desde = _a_datetime(s['down_since'])
                eventos.append({
                    'tipo': 'recuperacion',
                    'servicio': r['servicio'],
                    'desde': desde,
                    'duracion': ahora - desde,
                })
                s['down_since'] = None
                s['last_notified'] = None
        else:
            s['fallos'] = s.get('fallos', 0) + 1
            s['last_error'] = r['error']
            if s['fallos'] >= umbral and not s.get('down_since'):
                s['down_since'] = ahora.isoformat()
                eventos.append({
                    'tipo': 'caida',
                    'servicio': r['servicio'],
                    'error': r['error'],
                    'desde': ahora,
                })
    return estado, eventos


def eventos_a_notificar(estado: dict, eventos: list[dict], ahora=None) -> list[dict]:
    """De los eventos de la ronda + el estado previo, decide qué se notifica:

    - caídas y recuperaciones nuevas: siempre.
    - servicios que SIGUEN caídos (sin evento nuevo esta ronda): recordatorio
      solo si pasó UPTIME_REMINDER_HOURS desde la última notificación.

    Marca `last_notified` en el estado de cada evento incluido. Devuelve la
    lista en orden caída → recordatorio → recuperación (prioridad del correo)."""
    ahora = ahora or timezone.now()
    intervalo = dt.timedelta(hours=getattr(settings, 'UPTIME_REMINDER_HOURS', 2.0))

    notificar = [ev for ev in eventos if ev['tipo'] in ('caida', 'recuperacion')]
    con_evento_nuevo = {ev['servicio'] for ev in notificar}

    for ev in notificar:
        estado['servicios'].setdefault(ev['servicio'], {})['last_notified'] = ahora.isoformat()

    for nombre in SERVICIOS:
        s = estado['servicios'].get(nombre)
        if not s or not s.get('down_since') or nombre in con_evento_nuevo:
            continue
        last_n = _a_datetime(s['last_notified']) if s.get('last_notified') else None
        if last_n is None or (ahora - last_n) >= intervalo:
            s['last_notified'] = ahora.isoformat()
            notificar.append({
                'tipo': 'recordatorio',
                'servicio': nombre,
                'error': s.get('last_error'),
                'desde': _a_datetime(s['down_since']),
                'duracion': ahora - _a_datetime(s['down_since']),
            })

    orden = {'caida': 0, 'recordatorio': 1, 'recuperacion': 2}
    notificar.sort(key=lambda ev: orden.get(ev['tipo'], 3))
    return notificar


def _a_datetime(valor) -> dt.datetime | None:
    """ISO string guardado en el estado → datetime consciente. None/inválido → None."""
    if isinstance(valor, dt.datetime):
        return valor
    if not valor:
        return None
    try:
        d = dt.datetime.fromisoformat(valor)
        if d.tzinfo is None:
            d = timezone.make_aware(d)
        return d
    except (ValueError, TypeError):
        return None


# ═══════════════════════════════════════════════════════════════════
# Presentación
# ═══════════════════════════════════════════════════════════════════

def formato_duracion(delta: dt.timedelta | None) -> str:
    """ timedelta → texto corto en español: '45s', '12 min', '3h 5min', '2d 4h'."""
    if delta is None:
        return '—'
    total = max(0, int(delta.total_seconds()))
    if total < 60:
        return f'{total}s'
    minutos = total // 60
    if minutos < 60:
        return f'{minutos} min'
    horas, mins = divmod(minutos, 60)
    if horas < 24:
        return f'{horas}h {mins}min' if mins else f'{horas}h'
    dias, h = divmod(horas, 24)
    return f'{dias}d {h}h' if h else f'{dias}d'


def nombre_servicio(nombre: str) -> str:
    return NOMBRE_SERVICIO.get(nombre, nombre)


def ping_heartbeat(url: str) -> bool:
    """Notifica a un servicio externo (p.ej. healthchecks.io) que el monitor
    corrió y TODO está bien. Si el VPS entero se cae, el servicio externo
    detecta el silencio y alerta por su cuenta. Nunca lanza: devuelve False
    ante cualquier error y solo deja registro."""
    if not url:
        return False
    try:
        requests.get(url, timeout=10)
        return True
    except requests.RequestException as exc:
        logger.warning('Heartbeat externo falló (el sitio está bien): %s', exc)
        return False


def dominio_de(url: str) -> str:
    """'http://127.0.0.1:3000/' → '127.0.0.1:3000' (para mostrar en el correo)."""
    try:
        return urlparse(url).netloc or url
    except (ValueError, AttributeError):
        return url
