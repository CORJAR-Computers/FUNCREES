import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_donation_email(donation, pdf_buffer: bytes):
    """Envía el email de confirmación con el certificado adjunto."""
    try:
        subject = f"Confirmación de {donation.get_tipo_display()} — Funcrees Colombia"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@funcreescolombia.org')
        to_email = [donation.donante_email]

        # Contexto para el template
        context = {
            'nombre': donation.donante_nombre,
            'tipo_label': donation.get_tipo_display(),
            'referencia': donation.referencia,
            'monto': f"${int(donation.monto):,} COP".replace(',', '.'),
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
