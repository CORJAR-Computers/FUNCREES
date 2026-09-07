import logging
from urllib.parse import quote

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

WHATSAPP_URL = 'https://wa.me/573137924439'


def send_donation_email(donation, pdf_buffer: bytes):
    """Envía el email de confirmación con el certificado adjunto."""
    try:
        subject = f"Confirmación de {donation.get_tipo_display()} — Funcrees Colombia"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@funcreescolombia.org')
        to_email = [donation.donante_email]

        # Contexto para el template
        # Precisión: usar formato Decimal seguro (no int() que trunca centavos).
        # Formato colombiano: '.' para miles, ',' para decimales.
        _monto_str = (
            f"{donation.monto:,.2f}"
            .replace(',', 'X').replace('.', ',').replace('X', '.')
        )
        context = {
            'nombre': donation.donante_nombre,
            'tipo_label': donation.get_tipo_display(),
            'referencia': donation.referencia,
            'monto': f"${_monto_str} COP",
            'frontend_url': getattr(settings, 'FRONTEND_URL', 'https://funcreescolombia.org')
        }

        html_content = render_to_string('emails/donation_confirmation.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")

        # Adjuntar PDF si está disponible
        if pdf_buffer:
            msg.attach(f"Certificado-{donation.referencia}.pdf", pdf_buffer, "application/pdf")

        msg.send()
        logger.info(f"Email de confirmación enviado a {to_email} (Ref: {donation.referencia})")
        return True
    except Exception as e:
        logger.error(f"Error enviando email a {donation.donante_email}: {e}")
        return False


def send_donation_reminder(donation) -> bool:
    """
    Recordatorio amable para donaciones pendientes: "tu aporte sigue en marcha".

    Simetría con el recordatorio de boletas (events/services/email_service.py):
    - Nunca lanza: retorna True/False y registra el error (un fallo SMTP no
      debe romper una acción del panel ni un comando de cron).
    - Para aportes mensuales (apadrinamiento) el mensaje orienta a WhatsApp
      en lugar del checkout, porque la domiciliación se coordina 1:1.
    """
    try:
        es_recurrente = donation.tipo == 'apadrinamiento'
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://funcreescolombia.org')

        # Precisión Decimal + formato colombiano ('.' miles, ',' decimales)
        _monto_str = (
            f"{donation.monto:,.2f}"
            .replace(',', 'X').replace('.', ',').replace('X', '.')
        )

        mensaje = (
            f"Hola {donation.donante_nombre}, somos FUNCREES Colombia. "
            f"Tu aporte con referencia {donation.referencia} quedó pendiente. "
            "¿Te ayudamos a completarlo?"
        )
        context = {
            'nombre': donation.donante_nombre,
            'tipo_label': donation.get_tipo_display(),
            'referencia': donation.referencia,
            'monto': f"${_monto_str}",
            'es_recurrente': es_recurrente,
            'donar_url': f'{frontend_url}/donaciones',
            'whatsapp_url': f'{WHATSAPP_URL}?text={quote(mensaje)}',
        }

        subject = f"Tu aporte sigue pendiente (Ref. {donation.referencia}) — Funcrees Colombia"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@funcreescolombia.org')

        html_content = render_to_string('emails/donation_payment_reminder.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [donation.donante_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Recordatorio de donación pendiente enviado a {donation.donante_email} (Ref: {donation.referencia})")
        return True
    except Exception as e:
        logger.error(f"Error enviando recordatorio de donación a {donation.donante_email}: {e}")
        return False
