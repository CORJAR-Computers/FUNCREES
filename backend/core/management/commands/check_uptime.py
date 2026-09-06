"""
Monitor de disponibilidad: verifica el sitio y avisa por correo cuando algo
se cae (y cuando se recupera).

Uso manual:
    python manage.py check_uptime --dry-run
    python manage.py check_uptime --to tecnico@funcrees.org

En producción se programa con cron cada 5 minutos:
    */5 * * * 1-7  cd /var/www/funcrees/backend && venv/bin/python manage.py check_uptime
Ver DEPLOY.md, sección "🟢 Monitor de disponibilidad".

Comportamiento:
- Todo OK: no envía nada (silencio = todo bien). Si UPTIME_HEARTBEAT_URL está
  configurada, hace ping a ese servicio externo (cubre caída total del VPS).
- Servicio caído (tras UPTIME_FALLOS_PARA_ALERTA fallos seguidos): UN correo
  con todos los servicios afectados.
- Sigue caído: recordatorio cada UPTIME_REMINDER_HOURS.
- Se recupera: correo de confirmación con la duración de la caída.
- --force-email: envía un correo "todo funciona" aunque no haya novedades
  (útil para probar la configuración de correo tras instalar el cron).

Exit codes (visibles para cron/sistemas de monitoreo):
    0  todo respondió y (si tocaba) el correo salió bien
    1  algún servicio está caído, o falló el envío del correo
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from core.services.uptime import (
    actualizar_estado,
    cargar_estado,
    dominio_de,
    eventos_a_notificar,
    formato_duracion,
    guardar_estado,
    nombre_servicio,
    ping_heartbeat,
    verificar_servicios,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Verifica que el backend y el frontend respondan; alerta por correo '
        'cuando un servicio se cae, sigue caído o se recupera.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            dest='to',
            default=None,
            help='Destinatarios separados por coma. Prioridad sobre UPTIME_ALERT_TO y DIGEST_TO.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Verifica y muestra el resultado sin guardar estado ni enviar correo.',
        )
        parser.add_argument(
            '--force-email',
            action='store_true',
            help='Envía un correo de estado aunque todo esté OK (prueba de configuración).',
        )
        parser.add_argument(
            '--backend-url',
            default=None,
            help='URL a verificar como backend (override de UPTIME_BACKEND_URL para esta ejecución).',
        )
        parser.add_argument(
            '--frontend-url',
            default=None,
            help='URL a verificar como frontend (override de UPTIME_FRONTEND_URL para esta ejecución).',
        )

    def handle(self, *args, **options):
        urls = {}
        if options['backend_url']:
            urls['backend'] = options['backend_url']
        if options['frontend_url']:
            urls['frontend'] = options['frontend_url']

        resultados = verificar_servicios(urls or None)
        ahora = timezone.now()

        estado = cargar_estado()
        estado, eventos = actualizar_estado(estado, resultados, ahora=ahora)
        a_notificar = eventos_a_notificar(estado, eventos, ahora=ahora)
        todos_ok = all(r['ok'] for r in resultados)

        if options['dry_run']:
            self._imprimir_dry_run(resultados, a_notificar)
            # Útil en scripts: exit 1 si algo no responde, incluso en dry-run.
            raise SystemExit(0 if todos_ok else 1)

        guardar_estado(estado)

        # Heartbeat externo: solo cuando TODO está bien (el silencio le dice
        # al servicio externo que algo va mal).
        if todos_ok:
            heartbeat = getattr(settings, 'UPTIME_HEARTBEAT_URL', '')
            if heartbeat:
                ping_heartbeat(heartbeat)

        if not a_notificar and not options['force_email']:
            # Ejecución normal sin novedades: el silencio es la señal de salud.
            if not todos_ok:
                # Caído pero aún bajo el umbral de alerta (primer fallo):
                # no se avisa todavía, pero el cron ve el exit code.
                self.stdout.write(self.style.WARNING(
                    'Servicio con fallos (aún no alcanza el umbral de alerta): '
                    + ', '.join(r['servicio'] for r in resultados if not r['ok'])
                ))
            raise SystemExit(0 if todos_ok else 1)

        if not options['to']:
            raw = getattr(settings, 'UPTIME_ALERT_TO', '') or getattr(settings, 'DIGEST_TO', '')
            destinatarios = [d.strip() for d in raw.split(',') if d.strip()]
        else:
            destinatarios = [d.strip() for d in options['to'].split(',') if d.strip()]

        if not destinatarios:
            self.stdout.write(self.style.WARNING(
                'Hay novedades que notificar pero no hay destinatarios: configura '
                'UPTIME_ALERT_TO (o DIGEST_TO) en backend/.env o usa --to.'
            ))
            raise SystemExit(0 if todos_ok else 1)

        subject = self._asunto(resultados, a_notificar, todos_ok)
        context = self._contexto(
            resultados, a_notificar, todos_ok, urls, ahora,
            forzado=options['force_email'] and todos_ok,
        )

        html_content = render_to_string('emails/uptime_alert.html', context)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_content),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@funcreescolombia.org'),
            to=destinatarios,
        )
        msg.attach_alternative(html_content, 'text/html')

        try:
            msg.send()
        except Exception as exc:
            # El estado ya guardó last_notified; anularlo para que el próximo
            # cron reintente la alerta en lugar de esperar el recordatorio.
            for ev in a_notificar:
                s = estado['servicios'].get(ev['servicio'])
                if s:
                    s['last_notified'] = None
            guardar_estado(estado)
            logger.error('Error enviando la alerta de disponibilidad: %s', exc)
            self.stderr.write(self.style.ERROR(f'No se pudo enviar la alerta: {exc}'))
            raise SystemExit(1)

        resumen = '; '.join(
            f"{ev['tipo']} {ev['servicio']}" for ev in a_notificar
        ) or 'estado OK (forzado)'
        logger.info('Alerta de disponibilidad enviada a %s (%s)', ', '.join(destinatarios), resumen)
        self.stdout.write(self.style.SUCCESS(
            f'Correo enviado a {len(destinatarios)} destinatario(s): {subject}'
        ))
        raise SystemExit(0 if todos_ok else 1)

    # ------------------------------------------------------------------

    def _imprimir_dry_run(self, resultados, a_notificar):
        self.stdout.write(self.style.HTTP_INFO('— MODO DRY-RUN (no se guarda estado ni se envía correo) —'))
        for r in resultados:
            if r['ok']:
                linea = f"✅ {nombre_servicio(r['servicio'])} — {r['latencia_ms']} ms — {r['url']}"
                self.stdout.write(self.style.SUCCESS(linea))
            else:
                self.stdout.write(self.style.ERROR(
                    f"🔴 {nombre_servicio(r['servicio'])} — {r['error']} — {r['url']}"
                ))
        if a_notificar:
            self.stdout.write('')
            self.stdout.write('Se notificaría:')
            for ev in a_notificar:
                detalle = ev.get('error') or ''
                dur = formato_duracion(ev.get('duracion'))
                if dur != '—':
                    detalle = f'{detalle} ({"caído " if ev["tipo"] != "recuperacion" else "estuvo caído "}{dur})'.strip()
                self.stdout.write(f"  · [{ev['tipo']}] {nombre_servicio(ev['servicio'])} {detalle}")
        else:
            self.stdout.write('Sin novedades: no se enviaría ningún correo.')

    def _asunto(self, resultados, a_notificar, todos_ok):
        # Lo que manda es lo que está caído AHORA: si algo sigue caído el
        # asunto es rojo aunque esta ronda también traiga una recuperación.
        caidos = [nombre_servicio(r['servicio']) for r in resultados if not r['ok']]
        if caidos:
            return f"🔴 FUNCREES caído: {' + '.join(caidos)}"
        rec = next((ev for ev in a_notificar if ev['tipo'] == 'recuperacion'), None)
        if rec:
            return (
                f'✅ FUNCREES en línea de nuevo: {nombre_servicio(rec["servicio"])} '
                f'(estuvo caído {formato_duracion(rec["duracion"])})'
            )
        return '✅ FUNCREES monitor: todo funciona'

    def _contexto(self, resultados, a_notificar, todos_ok, urls, ahora, forzado=False):
        url_por_servicio = {r['servicio']: r['url'] for r in resultados}

        eventos_ctx = []
        for ev in a_notificar:
            eventos_ctx.append({
                'tipo': ev['tipo'],
                'nombre': nombre_servicio(ev['servicio']),
                'error': ev.get('error'),
                'host': dominio_de(url_por_servicio.get(ev['servicio'], '')),
                'desde_fmt': (
                    timezone.localtime(ev['desde']).strftime('%d/%m/%Y %H:%M')
                    if ev.get('desde') else ''
                ),
                'duracion_fmt': formato_duracion(ev.get('duracion')),
            })

        resultados_ctx = []
        for r in resultados:
            resultados_ctx.append({
                'nombre': nombre_servicio(r['servicio']),
                'ok': r['ok'],
                'host': dominio_de(r['url']),
                'detalle': f"{r['latencia_ms']} ms" if r['ok'] else (r['error'] or f"HTTP {r['http_status']}"),
            })

        return {
            'eventos': eventos_ctx,
            'resultados': resultados_ctx,
            'hay_caida': any(not r['ok'] for r in resultados),
            'todos_ok': todos_ok,
            'forzado': forzado,
            'generado_fmt': timezone.localtime(ahora).strftime('%d/%m/%Y %H:%M'),
        }
