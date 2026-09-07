"""
Envío por email de la boleta al comprador, con su código de verificación.

Historia: hasta ahora el comprador recibía el código solo si un operador lo
enviaba manualmente (WhatsApp/llamada) y `ticket_enviado` se marcaba a mano.
Con este servicio, el staff envía la boleta oficial desde el panel con un
clic (acción "Enviar boleta por email") y la marca queda registrada.

El correo incluye:
- Datos del evento (título, fecha, lugar).
- Número de boleta y código de verificación destacado.
- Un QR con la URL de consulta (/boletas?codigo=...) para mostrar en la puerta.
- Enlace directo que prellena el código en la página pública de consulta.
"""
import base64
import io
import logging

import qrcode
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _qr_data_uri(content: str) -> str | None:
    """Genera un PNG del QR como data URI para incrustar en el HTML del correo.

    Devuelve None si la librería falla: el correo debe enviarse igual y el QR
    es un extra de cortesía, no un requisito.
    """
    try:
        img = qrcode.make(content, box_size=8, border=2)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:  # pragma: no cover - depends on Pillow internals
        logger.warning("No se pudo generar el QR de la boleta: %s", e)
        return None


def build_consulta_url(codigo: str) -> str:
    """URL pública de consulta con el código prellenado."""
    frontend_url = getattr(settings, 'FRONTEND_URL', 'https://funcreescolombia.org')
    return f"{frontend_url.rstrip('/')}/boletas?codigo={codigo}"


def send_ticket_email(ticket) -> bool:
    """Envía la boleta al comprador. Retorna True si el correo salió.

    Nunca lanza: los errores se registran y retornan False para que el panel
    pueda informar "X enviadas, Y fallidas" sin romper la acción en lote.
    """
    try:
        subject = f"Tu boleta N.º {ticket.numero_ticket} — {ticket.evento.titulo} | Funcrees Colombia"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@funcreescolombia.org')
        to_email = [ticket.comprador_email]

        consulta_url = build_consulta_url(ticket.codigo_verificacion)
        context = {
            'nombre': ticket.comprador_nombre,
            'evento_titulo': ticket.evento.titulo,
            'evento_fecha': ticket.evento.fecha,
            'evento_hora': ticket.evento.hora,
            'evento_lugar': ticket.evento.lugar or 'Por confirmar',
            'numero_ticket': ticket.numero_ticket,
            'codigo': ticket.codigo_verificacion,
            'monto': f"${ticket.monto_pagado:,.0f}".replace(',', '.'),
            'estado_pago': ticket.get_estado_pago_display(),
            'consulta_url': consulta_url,
            'frontend_url': getattr(settings, 'FRONTEND_URL', 'https://funcreescolombia.org'),
            'qr_data_uri': _qr_data_uri(consulta_url),
        }

        html_content = render_to_string('emails/ticket_confirmation.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

        logger.info(
            "Boleta enviada por email a %s (evento=%s, ticket #%s, código=%s)",
            ticket.comprador_email, ticket.evento_id, ticket.numero_ticket,
            ticket.codigo_verificacion,
        )
        return True
    except Exception as e:
        logger.error(
            "Error enviando boleta #%s a %s: %s",
            getattr(ticket, 'numero_ticket', '?'),
            getattr(ticket, 'comprador_email', '?'),
            e,
        )
        return False


def send_payment_reminder(ticket) -> bool:
    """Recordatorio amable para boletas con pago 'pendiente'.

    Caso de uso: el comprador coordinó por WhatsApp/transferencia pero el
    pago aún no se confirma (o pagó y falta verificar). El email le recuerda
    completar el pago y le da el enlace de consulta para verificar si ya
    quedó confirmado. Mismo contrato que send_ticket_email: nunca lanza.
    """
    try:
        subject = (
            f"Recordatorio de pago — Boleta N.º {ticket.numero_ticket} "
            f"{ticket.evento.titulo} | Funcrees Colombia"
        )
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@funcreescolombia.org')
        to_email = [ticket.comprador_email]

        context = {
            'nombre': ticket.comprador_nombre,
            'evento_titulo': ticket.evento.titulo,
            'evento_fecha': ticket.evento.fecha,
            'evento_hora': ticket.evento.hora,
            'evento_lugar': ticket.evento.lugar or 'Por confirmar',
            'numero_ticket': ticket.numero_ticket,
            'codigo': ticket.codigo_verificacion,
            'monto': f"${ticket.monto_pagado:,.0f}".replace(',', '.'),
            'consulta_url': build_consulta_url(ticket.codigo_verificacion),
            'whatsapp_url': 'https://wa.me/573137924439',
            'frontend_url': getattr(settings, 'FRONTEND_URL', 'https://funcreescolombia.org'),
        }

        html_content = render_to_string('emails/ticket_payment_reminder.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

        logger.info(
            "Recordatorio de pago enviado a %s (evento=%s, ticket #%s)",
            ticket.comprador_email, ticket.evento_id, ticket.numero_ticket,
        )
        return True
    except Exception as e:
        logger.error(
            "Error enviando recordatorio #%s a %s: %s",
            getattr(ticket, 'numero_ticket', '?'),
            getattr(ticket, 'comprador_email', '?'),
            e,
        )
        return False
