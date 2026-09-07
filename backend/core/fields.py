"""
Campos de modelos cifrados a nivel de campo (Fernet simétrico).

Ubicado en `core` para que cualquier app (donations, events, ...) pueda
cifrar datos personales sin dependencias cruzadas entre apps.

Cumplimiento Ley 1581 de 2012 (Colombia): los teléfonos y documentos de
tercero se almacenan cifrados en reposo; la clave vive SOLO en la variable
de entorno ENCRYPTION_KEY (nunca en el repo, ver .env.example y RUNBOOK).

Nota de migraciones: las migraciones históricas de `donations` resuelven la
clase como `donations.models.EncryptedCharField`; por eso `donations/models.py`
mantiene el import con el mismo nombre (alias) y las rutas de las migraciones
antiguas siguen resolviendo sin cambios.
"""

import logging

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models

# Logger por app; si la app no define handler, cae al logger raíz de Django.
logger = logging.getLogger('core.fields')


def get_fernet() -> Fernet:
    """Instancia Fernet con la clave configurada en el entorno."""
    return Fernet(settings.ENCRYPTION_KEY)


class EncryptedCharField(models.CharField):
    """CharField que cifra el valor antes de guardar y descifra al leer.

    - get_prep_value: cifra en escritura (Fernet produce texto Base64, por lo
      que max_length en BD debe ser generoso — usar 500+).
    - from_db_value: descifra en lectura; si falla (corrupción, rotación de
      clave, dato legado en claro pendiente de migrar) devuelve None en lugar
      de filtrar el ciphertext a la UI, y lo registra con nivel ERROR.
    """

    def get_prep_value(self, value):
        if not value:
            return value
        f = get_fernet()
        return f.encrypt(str(value).encode('utf-8')).decode('utf-8')

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            f = get_fernet()
            return f.decrypt(value.encode('utf-8')).decode('utf-8')
        except Exception:
            # Seguridad: NUNCA devolver el ciphertext como si fuera plaintext.
            # Si el desencriptado falla, lo más probable es:
            #   (a) corrupción del valor almacenado,
            #   (b) rotación de ENCRYPTION_KEY (la clave actual no es la que
            #       se usó para cifrar este valor), o
            #   (c) el valor aún está en plaintext pendiente de migración de
            #       cifrado masivo.
            # Devolver None evita exponer datos ilegibles como si fueran
            # válidos y deja traza diagnosable en los logs.
            logger.error(
                "Decryption failed for field: %s. Possible causes: corrupted "
                "value, ENCRYPTION_KEY rotation, or data may be plaintext "
                "pending backfill migration.",
                self.name,
                exc_info=True,
            )
            return None
