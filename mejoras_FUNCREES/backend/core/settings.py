"""
Ajustes del proyecto FUNCREES — Backend Django 5.1
===================================================
Fundación Creativa para la Reconciliación y la Esperanza Social (FUNCREES).
Cumplimiento Habeas Data mediante cifrado Fernet (Ley 1581/2012 - Colombia).
"""

import os
from pathlib import Path
from cryptography.fernet import Fernet
import logging

# ---------------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Efecto secundario a nivel de módulo: creación del directorio de logs.
# Se ejecuta una sola vez al importar settings, lo cual es aceptable porque
# Django garantiza que settings se importa una vez por proceso.
# ---------------------------------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Modo DEBUG / Producción
# ---------------------------------------------------------------------------
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-cambiar-en-produccion-funcrees-2024",
)

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1"
).split(",")

# ---------------------------------------------------------------------------
# Aplicaciones instaladas
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros
    "rest_framework",
    "corsheaders",
    "django_filters",
    # Locales
    "core",
    "beneficiaries",
    "events",
    "donations",
    "contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": os.environ.get("DB_USER", ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
    }
}

# ---------------------------------------------------------------------------
# Validación de contraseñas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estáticos
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Campo auto-generado por defecto (BigAutoField en Django 5.x)
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===================================================================
# SEGURIDAD — Cabeceras HTTP
# ===================================================================

# Evita que el navegador infiera tipos MIME (MIME-sniffing).
SECURE_CONTENT_TYPE_NOSNIFF = True

# Impide que la aplicación sea embebida en iframes de cualquier origen.
# Usar DENY en lugar del valor por defecto (SAMEORIGIN) porque FUNCREES
# no necesita ser embebido en marcos externos.
X_FRAME_OPTIONS = "DENY"

# Política de referer: envía el origen completo solo en navegación del
# mismo sitio; en peticiones cross-origin envía solo el origen (sin path).
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# HSTS — Solo se activa cuando DEBUG=False y se sirve sobre HTTPS.
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000          # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ===================================================================
# SEGURIDAD — Límites de carga de datos
# ===================================================================

# Limita a 10 MB la carga de datos en memoria (evita ataques DoS por
# payloads excesivamente grandes en memoria).
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# Número máximo de campos aceptados en un formulario / request.
# Previene ataques de denegación de servicio enviando miles de campos.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ===================================================================
# Django REST Framework
# ===================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    # Limitación de tasa: usuarios anónimos y autenticados.
    # Se añade límite 'user' para que los usuarios autenticados también
    # estén sujetos a throttle (por defecto DRF solo limita anónimos).
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "200/hour",
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

# ===================================================================
# CORS
# ===================================================================
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500",
).split(",")

CORS_ALLOW_CREDENTIALS = True

# ===================================================================
# Wompi — Pasarela de pagos
# ===================================================================
WOMPI_PUBLIC_KEY = os.environ.get("WOMPI_PUBLIC_KEY", "")
WOMPI_PRIVATE_KEY = os.environ.get("WOMPI_PRIVATE_KEY", "")
WOMPI_EVENTS_KEY = os.environ.get("WOMPI_EVENTS_KEY", "")
WOMPI_INTEGRATOR_ID = os.environ.get("WOMPI_INTEGRATOR_ID", "")
WOMPI_REDIRECT_URL = os.environ.get("WOMPI_REDIRECT_URL", "")
WOMPI_API_BASE_URL = os.environ.get(
    "WOMPI_API_BASE_URL", "https://production.wompi.co/v1"
)

# ===================================================================
# Frontend — URL del frontend para redirecciones post-pago
# ===================================================================
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5500")

# ===================================================================
# Cifrado Fernet — Habeas Data (Ley 1581/2012 Colombia)
# ===================================================================
FERNET_KEY = os.environ.get("FERNET_KEY", Fernet.generate_key().decode())
_fernet = Fernet(FERNET_KEY.encode())


def encrypt_field(value: str) -> str:
    """Cifra un valor plano y retorna el token base64."""
    if not value:
        return ""
    return _fernet.encrypt(value.encode()).decode()


def decrypt_field(token: str) -> str:
    """Descifra un token base64 y retorna el valor plano."""
    if not token:
        return ""
    return _fernet.decrypt(token.encode()).decode()


# ===================================================================
# Correo electrónico
# ===================================================================
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "noreply@funcrees.org"
)

# ===================================================================
# Logging
# ===================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "{asctime} [{levelname}] {module}.{funcName} "
                "(PID {process:d}|TID {thread:d}): {message}"
            ),
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{asctime} {levelname} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file_info": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "info.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "INFO",
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "error.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["console", "file_info", "file_error"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}