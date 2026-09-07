# Migración de datos + esquema: cifra los teléfonos de compradores existentes
# (almacenados como plaintext en el CharField original) ANTES de cambiar el
# tipo de campo a EncryptedCharField. Espejo de donations/0002_encrypt_wompi_
# token_card.py.

import logging

import core.fields
from django.db import migrations, connection

logger = logging.getLogger(__name__)


def forward(apps, schema_editor):
    """
    Cifra `comprador_telefono` existente ANTES del AlterField.

    Usa SQL crudo (connection.cursor()) para evitar que el ORM aplique
    auto-cifrado/descifrado durante el proceso. Cada fila se examina:
    - Si el valor desencripta correctamente con Fernet, ya estaba cifrado
      (idempotente) y se omite.
    - Si falla el descifrado, se asume plaintext y se cifra.
    """
    from cryptography.fernet import InvalidToken

    from core.fields import get_fernet

    fernet = get_fernet()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, comprador_telefono FROM events_ticket "
            "WHERE comprador_telefono IS NOT NULL AND comprador_telefono != ''"
        )
        rows = cursor.fetchall()

    updated = 0
    skipped = 0
    for row_id, telefono in rows:
        if not telefono:
            continue

        # Detectar si ya está cifrado: intentar desencriptar.
        try:
            fernet.decrypt(telefono.encode('utf-8'))
            # Desencriptó correctamente -> ya estaba cifrado. Skip.
            skipped += 1
            continue
        except (InvalidToken, Exception):
            # No es un token Fernet válido -> está en plaintext -> cifrar.
            pass

        encrypted = fernet.encrypt(telefono.encode('utf-8')).decode('utf-8')
        # SQL crudo: evita que get_prep_value() vuelva a cifrar el valor.
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE events_ticket SET comprador_telefono = %s WHERE id = %s",
                [encrypted, row_id],
            )
        updated += 1

    logger.info(
        "[migración events/0004] teléfonos cifrados: %d, ya estaban cifrados: %d",
        updated, skipped,
    )


def reverse(apps, schema_editor):
    """
    Reverso intencionalmente NO desencripta los teléfonos por seguridad
    (Ley 1581): dejar datos personales en plaintext sería un retroceso.
    El campo vuelve a CharField pero el contenido queda opaco (cifrado).
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_event_imagen'),
    ]

    operations = [
        # 1) Migrar datos existentes (plaintext -> cifrado) ANTES de cambiar
        #    el tipo de campo.
        migrations.RunPython(forward, reverse_code=reverse),
        # 2) Cambiar el tipo de campo a EncryptedCharField.
        migrations.AlterField(
            model_name='ticket',
            name='comprador_telefono',
            field=core.fields.EncryptedCharField(blank=True, help_text='Cifrado en reposo (Ley 1581). El valor ronda los 150+ caracteres por el padding Fernet.', max_length=500, null=True, verbose_name='Teléfono (Cifrado)'),
        ),
    ]
