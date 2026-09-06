"""
Backfill: genera variantes WebP para las imágenes ya subidas a media/.

Las fotos que se suban desde el panel generan sus variantes WebP
automáticamente al guardar. Este comando procesa las imágenes anteriores
al sistema, para que /historias y /eventos también carguen rápido con ellas.

Uso:
    python manage.py generate_image_variants            # genera
    python manage.py generate_image_variants --dry-run  # solo cuenta

Idempotente: regenerar sobreescribe las variantes con el original como
fuente (útil si cambian los anchos o la calidad en core/services/images.py).
"""
from django.core.management.base import BaseCommand

from beneficiaries.models import Beneficiary
from core.services.images import generar_variantes_webp
from events.models import Event


class Command(BaseCommand):
    help = 'Genera variantes WebP (srcset responsive) para las imágenes ya subidas.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra cuántas imágenes se procesarían sin generar nada.',
        )

    def handle(self, *args, **options):
        beneficiarios = Beneficiary.objects.exclude(foto='').exclude(foto=None)
        eventos = Event.objects.exclude(imagen='').exclude(imagen=None)
        total_b, total_e = beneficiarios.count(), eventos.count()

        self.stdout.write(
            f'Imágenes a procesar: {total_b} beneficiarios, {total_e} eventos'
        )
        if options['dry_run']:
            return

        con_variantes = sin_variantes = 0
        for b in beneficiarios:
            if generar_variantes_webp(b.foto):
                con_variantes += 1
            else:
                sin_variantes += 1
        for e in eventos:
            if generar_variantes_webp(e.imagen):
                con_variantes += 1
            else:
                sin_variantes += 1

        self.stdout.write(self.style.SUCCESS(
            f'Completado: {con_variantes} imágenes con variantes WebP, '
            f'{sin_variantes} sin variantes (error o imagen menor a 200px).'
        ))
