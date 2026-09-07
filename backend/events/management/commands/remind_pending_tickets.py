"""
Recordatorio de pago para boletas pendientes.

Envía un email amable a los compradores cuya boleta sigue en estado
'pendiente'. Pensado para un cron del VPS (p.ej. cada 3 días) y para uso
manual del personal.

Uso:
    python manage.py remind_pending_tickets                 # envía a todos
    python manage.py remind_pending_tickets --evento bingo-2026
    python manage.py remind_pending_tickets --dias 3        # solo boletas con +3 días de creadas
    python manage.py remind_pending_tickets --dry-run       # lista sin enviar
    python manage.py remind_pending_tickets --limit 100     # tope de envíos por corrida

El email es informativo y no muta datos: reenviarlo a la misma boleta no
corrompe nada, pero el --limit y el cron del VPS evitan spam accidenta.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from events.models import Ticket
from events.services.email_service import send_payment_reminder


class Command(BaseCommand):
    help = "Envía recordatorios de pago a compradores con boletas pendientes."

    def add_arguments(self, parser):
        parser.add_argument('--evento', type=str, default=None,
                            help='Limita a un evento por ID (ej. bingo-2026).')
        parser.add_argument('--dias', type=int, default=0,
                            help='Solo boletas registradas hace N o más días (0 = todas).')
        parser.add_argument('--limit', type=int, default=200,
                            help='Tope de correos por corrida (protección SMTP).')
        parser.add_argument('--dry-run', action='store_true',
                            help='Muestra a quién se escribiría sin enviar nada.')

    def handle(self, *args, **options):
        evento_id = options['evento']
        dias = options['dias']
        limit = options['limit']
        dry_run = options['dry_run']

        if limit < 1:
            raise CommandError('--limit debe ser >= 1')
        if dias < 0:
            raise CommandError('--dias no puede ser negativo')

        qs = Ticket.objects.filter(estado_pago='pendiente').select_related('evento')
        if evento_id:
            qs = qs.filter(evento_id=evento_id)
        if dias > 0:
            qs = qs.filter(creado_en__lte=timezone.now() - timedelta(days=dias))

        pendientes = list(qs[:limit])
        self.stdout.write(
            f"Boletas pendientes a notificar: {len(pendientes)}"
            + (" (dry-run: no se enviará nada)" if dry_run else "")
        )

        enviados, fallos = 0, 0
        for t in pendientes:
            linea = f"  #{t.numero_ticket} {t.evento.titulo} -> {t.comprador_email}"
            if dry_run:
                self.stdout.write(f"[dry-run]{linea}")
                continue
            if send_payment_reminder(t):
                enviados += 1
                self.stdout.write(self.style.SUCCESS(f"[ok]{linea}"))
            else:
                fallos += 1
                self.stdout.write(self.style.ERROR(f"[fail]{linea}"))

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry-run: {len(pendientes)} recordatorio(s) omitido(s)."))
        elif fallos:
            self.stdout.write(self.style.ERROR(f"Listo: {enviados} enviados, {fallos} con error."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Listo: {enviados} recordatorio(s) enviados."))
