"""
Resumen semanal por correo para el personal de FUNCREES.

Uso manual:
    python manage.py send_weekly_digest
    python manage.py send_weekly_digest --to directiva@funcrees.org,contabilidad@funcrees.org

En producción se programa con cron (lunes 7:00 a.m. hora Colombia):
    0 7 * * 1  cd /var/www/funcrees/backend && venv/bin/python manage.py send_weekly_digest
Ver DEPLOY.md, sección "📧 Resumen Semanal por Correo".

Comportamiento:
- Sin destinatarios configurados (DIGEST_TO vacía): no envía nada y lo avisa.
- Los errores de SMTP no detienen el cron: se registran y el comando termina
  con exit code 1 para que sistemas de monitoreo detecten el fallo.
"""
import logging
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.services import formato_cop, generar_grafico_mensual, resumen_fundacion

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Envía el resumen semanal de la Fundación por correo (lunes por la mañana).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            dest='to',
            default=None,
            help='Destinatarios separados por coma. Por defecto usa DIGEST_TO del .env.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra el resumen en consola sin enviar el correo.',
        )

    def handle(self, *args, **options):
        resumen = resumen_fundacion()

        if options['dry_run']:
            self.stdout.write(self.style.HTTP_INFO('— MODO DRY-RUN (no se envía nada) —'))
            self.stdout.write(f"Mes: {resumen['mes_nombre']}")
            self.stdout.write(f"Recaudado: ${resumen['total_mes']:,.0f} en {resumen['cantidad_mes']} donaciones")
            self.stdout.write(f"Mensajes sin leer: {resumen['no_leidos']}")
            self.stdout.write(f"Apadrinamientos activos: {resumen['apadrinamientos_activos']}")
            return

        # Destinatarios: --to tiene prioridad, si no DIGEST_TO del .env
        raw = options['to'] or getattr(settings, 'DIGEST_TO', '')
        recipients = [r.strip() for r in raw.split(',') if r.strip()]
        if not recipients:
            self.stdout.write(self.style.WARNING(
                'Sin destinatarios: agrega DIGEST_TO=correo1@funcrees.org,correo2@funcrees.org '
                'al backend/.env o usa --to.'
            ))
            return

        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://funcreescolombia.org')
        # Cifras de dinero preformateadas (estándar colombiano) para la plantilla
        context = {
            **resumen,
            'admin_url': f'{frontend_url}/admin/',
            'total_mes_fmt': formato_cop(resumen['total_mes']),
            'monto_mensual_fmt': formato_cop(resumen['monto_mensual_apadrinamientos']),
            'recaudado_total_fmt': formato_cop(resumen['recaudado_total']),
            'recaudo_boletas_mes_fmt': formato_cop(resumen['recaudo_boletas_mes']),
        }

        subject = (
            f"Resumen FUNCREES · {resumen['mes_nombre']} · {formato_cop(resumen['total_mes'])}"
        )
        html_content = render_to_string('emails/weekly_digest.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@funcreescolombia.org'),
            to=recipients,
        )
        msg.attach_alternative(html_content, 'text/html')

        # Gráfico mensual embebido (inline CID): el HTML lo referencia como
        # <img src="cid:grafico-mensual">. Mismo pipeline de datos que el
        # panel del admin (resumen_fundacion), así los números coinciden.
        png = generar_grafico_mensual(resumen['serie_mensual'])
        img_part = MIMEImage(png, _subtype='png')
        img_part.add_header('Content-Id', '<grafico-mensual>')
        img_part.add_header('Content-Disposition', 'inline', filename='grafico-mensual.png')
        msg.attach(img_part)

        try:
            msg.send()
            logger.info('Resumen semanal enviado a %s', ', '.join(recipients))
            self.stdout.write(self.style.SUCCESS(
                f'Resumen enviado a {len(recipients)} destinatario(s): {", ".join(recipients)}'
            ))
        except Exception as exc:
            logger.error('Error enviando el resumen semanal: %s', exc)
            self.stderr.write(self.style.ERROR(f'No se pudo enviar el correo: {exc}'))
            raise SystemExit(1)
