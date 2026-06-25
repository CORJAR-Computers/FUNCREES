"""
Gunicorn configuration for FUNCREES Colombia
Production server settings for Hostinger VPS
"""

import multiprocessing
import os
from pathlib import Path

# Directorio base del proyecto (un nivel arriba de este archivo)
BASE_DIR = Path(__file__).resolve().parent

# ============================================
# SOCKET BINDING
# ============================================
bind = "0.0.0.0:8000"

# ============================================
# WORKER PROCESSES
# ============================================
# 2-4 workers per CPU core is recommended
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# ============================================
# TIMEOUTS
# ============================================
timeout = 120
graceful_timeout = 30
keepalive = 5

# ============================================
# LOGGING
# En producción (Linux/VPS): usa rutas absolutas /var/log/funcrees/
# En desarrollo o si las rutas no existen: usa rutas relativas al proyecto
# ============================================

_LOG_DIR_PROD = Path("/var/log/funcrees")
_PID_DIR_PROD = Path("/var/run/funcrees")

if _LOG_DIR_PROD.exists():
    accesslog = str(_LOG_DIR_PROD / "access.log")
    errorlog = str(_LOG_DIR_PROD / "error.log")
else:
    # Fallback a directorio de logs del proyecto
    _LOCAL_LOG_DIR = BASE_DIR / "logs"
    _LOCAL_LOG_DIR.mkdir(exist_ok=True)
    accesslog = str(_LOCAL_LOG_DIR / "gunicorn_access.log")
    errorlog = str(_LOCAL_LOG_DIR / "gunicorn_error.log")

loglevel = "info"

# PID file
if _PID_DIR_PROD.exists():
    pidfile = str(_PID_DIR_PROD / "gunicorn.pid")
else:
    pidfile = str(BASE_DIR / "gunicorn.pid")

# ============================================
# PROCESS NAME
# ============================================
proc_name = "funcrees"

# ============================================
# SECURITY
# ============================================
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# ============================================
# SERVER MECHANICS
# ============================================
daemon = False
preload_app = True  # Carga la app antes de hacer fork (mejor rendimiento de memoria)

# ============================================
# SSL (configurado en Nginx en lugar de aquí)
# ============================================
# keyfile = "/etc/letsencrypt/live/funcreescolombia.org/privkey.pem"
# certfile = "/etc/letsencrypt/live/funcreescolombia.org/fullchain.pem"
