"""
Configuración de Gunicorn para FUNCREES — Backend en producción.
=================================================================
Diseñado para una VPS pequeña (1–2 núcleos).  Los workers se
limitan a un máximo de 5 para no agotar la memoria RAM.
"""

import multiprocessing
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Bind — escucha en todas las interfaces (Nginx se encarga de filtrar).
# ---------------------------------------------------------------------------
bind = "0.0.0.0:8000"

# ---------------------------------------------------------------------------
# Workers: fórmula estándar (cores * 2 + 1) pero con un máximo razonable
# para una VPS pequeña.  Evita que un servidor con muchos núcleos genere
# un número excesivo de procesos que consuman toda la RAM.
# ---------------------------------------------------------------------------
cores = multiprocessing.cpu_count()
workers = min(cores * 2 + 1, 5)

# ---------------------------------------------------------------------------
# Worker class y tiempos de espera
# ---------------------------------------------------------------------------
worker_class = "sync"
timeout = 120
graceful_timeout = 30
keepalive = 5

# ---------------------------------------------------------------------------
# Reciclaje de workers para prevenir fugas de memoria.
# Cada worker atiende máximo 1000 peticiones antes de reiniciarse.
# El jitter (±50) evita que todos los workers se reciclen al mismo tiempo.
# ---------------------------------------------------------------------------
max_requests = 1000
max_requests_jitter = 50

# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------
_LOG_DIR_PROD = Path("/var/log/funcrees")
_PID_DIR_PROD = Path("/var/run/funcrees")

# En contenedores Docker/Kubernetes no existe el directorio de producción,
# así que se usa un directorio local.  Si se ejecuta en un contenedor con
# redirección de logs a stdout, se puede sobreescribir con GUNICORN_CMD_ARGS.
if _LOG_DIR_PROD.exists():
    accesslog = str(_LOG_DIR_PROD / "access.log")
    errorlog = str(_LOG_DIR_PROD / "error.log")
else:
    _LOCAL_LOG_DIR = BASE_DIR / "logs"
    _LOCAL_LOG_DIR.mkdir(exist_ok=True)
    accesslog = str(_LOCAL_LOG_DIR / "gunicorn_access.log")
    errorlog = str(_LOCAL_LOG_DIR / "gunicorn_error.log")

# En entornos de contenedores (Docker, Kubernetes) es habitual enviar
# los access logs a stdout para que el orquestador los capture.
# Descomentar la siguiente línea si se ejecuta en contenedores:
# accesslog = '-'

loglevel = "info"

# ---------------------------------------------------------------------------
# PID file
# ---------------------------------------------------------------------------
if _PID_DIR_PROD.exists():
    pidfile = str(_PID_DIR_PROD / "gunicorn.pid")
else:
    pidfile = str(BASE_DIR / "gunicorn.pid")

# ---------------------------------------------------------------------------
# Nombre del proceso (visible en ps / top)
# ---------------------------------------------------------------------------
proc_name = "funcrees"

# ---------------------------------------------------------------------------
# Límites de tamaño de petición (protección DoS a nivel de Gunicorn)
# ---------------------------------------------------------------------------
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# ---------------------------------------------------------------------------
# Modo de ejecución y pre-carga de la aplicación
# ---------------------------------------------------------------------------
daemon = False
preload_app = True