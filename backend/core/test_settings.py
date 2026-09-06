"""
Settings de pruebas: hereda de core.settings y fuerza SQLite en memoria
para que `manage.py test` funcione sin PostgreSQL local ni en CI.

Uso: python manage.py test --settings=core.test_settings
"""
from .settings import *  # noqa: F401,F403
from cryptography.fernet import Fernet

# Garantizar una ENCRYPTION_KEY válida aunque el .env local tenga una inválida.
try:
    Fernet(ENCRYPTION_KEY)
except Exception:
    ENCRYPTION_KEY = Fernet.generate_key().decode()

# El test client usa http://testserver: desactivar redirecciones/cookies HTTPS
# (el .env local puede tener DEBUG=False => SECURE_SSL_REDIRECT=True => 301).
DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Acelerar tests: hashing simple en lugar de PBKDF2 con muchas iteraciones
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Throttles desactivados por defecto en tests unitarios (los tests de
# contacto prueban validación, no rate limiting).
RATELIMIT_ENABLE = False

# Media a un directorio temporal: los tests que suben imágenes no ensucian
# backend/media/ y Django limpia el directorio al terminar la suite.
import tempfile
MEDIA_ROOT = tempfile.mkdtemp(prefix='funcrees-test-media-')
