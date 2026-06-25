import hashlib
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


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
    Wompi firma los eventos con propiedades específicas.
    """
    try:
        cfg = _get_wompi_config()
        signature_data = payload.get('signature', {})
        properties = signature_data.get('properties', [])
        data = payload.get('data', {})
        sent_at = payload.get('sent_at', '')

        string_to_sign = ""
        for prop in properties:
            keys = prop.split('.')
            value = data
            for key in keys:
                value = value.get(key, {}) if isinstance(value, dict) else value
            string_to_sign += str(value) if value else ""

        string_to_sign += f"{sent_at}{cfg['integrity_secret']}"
        expected_signature = hashlib.sha256(string_to_sign.encode('utf-8')).hexdigest()

        return expected_signature == received_signature
    except Exception as e:
        logger.error(f"Error verificando firma de Wompi: {e}")
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
