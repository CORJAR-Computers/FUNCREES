import hashlib
import hmac
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Propiedades FIJAS definidas por Wompi que componen el string a firmar para
# verificar la autenticidad de un webhook. Orden IMPORTANTE: debe coincidir
# exactamente con el que Wompi usa al generar la firma.
# NOTA DE SEGURIDAD: esta lista es HARDCODED (no se lee del payload). En una
# versión anterior el código iteraba sobre `payload.signature.properties`,
# pero ese campo viaja en el payload y es controlable por el atacante, lo que
# permite forjar firmas válidas (p.ej. enviando una lista vacía).
# El último elemento, `integrity_signature`, NO viene del payload: es el
# secreto compartido (`WOMPI_INTEGRITY_SECRET`) configurado en settings.
WOMPI_SIGNATURE_PROPERTIES = [
    'reference',
    'amount_in_cents',
    'currency',
    'integrity_signature',
]


def _get_wompi_config():
    """Retorna la configuración de Wompi desde settings (leída en tiempo de ejecución, no de módulo)."""
    wompi_env = settings.WOMPI_ENV
    return {
        'env': wompi_env,
        'base_url': 'https://production.wompi.co/v1' if wompi_env == 'production' else 'https://sandbox.wompi.co/v1',
        'public_key': settings.WOMPI_PUBLIC_KEY,
        'private_key': settings.WOMPI_PRIVATE_KEY,
        'integrity_secret': settings.WOMPI_INTEGRITY_SECRET,
    }


def generate_integrity_signature(reference: str, amount_cop: float) -> str:
    """
    Genera la firma de integridad SHA256 para Wompi (usada al iniciar el pago).
    """
    cfg = _get_wompi_config()
    amount_cents = int(amount_cop * 100)
    string_to_sign = f"{reference}{amount_cents}COP{cfg['integrity_secret']}"
    return hashlib.sha256(string_to_sign.encode('utf-8')).hexdigest()


def verify_webhook_signature(payload: dict, received_signature: str) -> bool:
    """
    Verifica que el webhook entrante provenga realmente de Wompi.

    Seguridad:
    - Construye el string a firmar a partir de propiedades FIJAS definidas por
      Wompi (WOMPI_SIGNATURE_PROPERTIES). Las tres primeras se leen del
      `payload.data.transaction`; la última, `integrity_signature`, es el
      secreto compartido (`WOMPI_INTEGRITY_SECRET`) y se toma de settings,
      NO del payload. Jamás se itera sobre `payload.signature.properties`,
      ya que ese campo es controlado por el atacante y podría manipularse para
      forjar una firma válida (por ejemplo, enviando una lista vacía).
    - Usa `hmac.compare_digest` para comparación en tiempo constante y prevenir
      timing attacks sobre la firma esperada.
    - Retorna `bool` (True sólo si la firma esperada coincide con la recibida).
    """
    # Guard temprano: received_signature debe ser un string no vacío.
    if not received_signature or not isinstance(received_signature, str):
        return False

    try:
        cfg = _get_wompi_config()
        data = payload.get('data', {}) or {}
        transaction = data.get('transaction', {}) or {}

        # Resolución de cada propiedad FIJA a su valor concreto:
        # - Las tres primeras se leen del payload (data.transaction).
        # - `integrity_signature` se resuelve al secreto compartido de settings.
        values = []
        for prop in WOMPI_SIGNATURE_PROPERTIES:
            if prop == 'integrity_signature':
                # Secreto compartido: NO viene en el payload.
                values.append(cfg['integrity_secret'] or '')
            else:
                values.append(str(transaction.get(prop, '') or ''))

        # Concatenación en el orden definido por WOMPI_SIGNATURE_PROPERTIES.
        string_to_sign = ''.join(values)
        expected_signature = hashlib.sha256(
            string_to_sign.encode('utf-8')
        ).hexdigest()

        # Seguridad: comparación en tiempo constante para prevenir timing attacks.
        return hmac.compare_digest(expected_signature, received_signature)
    except Exception:
        logger.error("Error verificando firma de Wompi", exc_info=True)
        return False


def create_payment_session(reference: str, amount_cop: float, description: str, customer_email: str, redirect_url: str):
    """
    Retorna la configuración necesaria para el Widget de Wompi en el Frontend.
    """
    cfg = _get_wompi_config()
    amount_cents = int(amount_cop * 100)
    integrity_signature = generate_integrity_signature(reference, amount_cop)

    return {
        "publicKey": cfg['public_key'],
        "reference": reference,
        "amountInCents": amount_cents,
        "currency": "COP",
        "integritySignature": integrity_signature,
        "redirectUrl": redirect_url,
        "customerEmail": customer_email,
        "description": description,
        "wompiCheckoutUrl": f"{cfg['base_url'].replace('/v1', '')}/en-us/checkout/{cfg['public_key']}"
    }


def get_transaction_by_reference(reference: str):
    """
    Consulta a Wompi para ver el estado de una transacción.
    """
    cfg = _get_wompi_config()
    try:
        response = requests.get(
            f"{cfg['base_url']}/transactions",
            params={'reference': reference},
            headers={'Authorization': f"Bearer {cfg['private_key']}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get('data'):
            return data['data'][0]
        return None
    except requests.RequestException as e:
        logger.error(f"Error consultando Wompi API para ref {reference}: {e}")
        return None
