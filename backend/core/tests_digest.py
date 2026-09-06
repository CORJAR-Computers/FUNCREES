"""
Tests del resumen semanal por correo (send_weekly_digest).

Correr con: python manage.py test core --settings=core.test_settings
"""
import datetime as dt
import io

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image

from donations.models import Donation


def _this_month(day=15, hour=12):
    today = timezone.localdate()
    return timezone.make_aware(dt.datetime(today.year, today.month, min(day, today.day), hour))


@override_settings(DIGEST_TO='directiva@funcrees.org')
class WeeklyDigestTests(TestCase):
    def _donacion(self, referencia, monto, estado, antiguedad=None):
        """Crea una donación del mes en curso. auto_now_add ignora creado_en
        en create(), así que la antigüedad se aplica con update() posterior."""
        d = Donation.objects.create(
            referencia=referencia,
            tipo='general',
            monto=monto,
            donante_nombre=f'Donante {referencia}',
            donante_email=f'{referencia.lower()}@example.com',
            metodo_pago='PSE',
            estado=estado,
            creado_en=_this_month(),
        )
        if antiguedad is not None:
            Donation.objects.filter(pk=d.pk).update(creado_en=timezone.now() - antiguedad)
            d.refresh_from_db()
        return d

    def test_dry_run_no_envia_correo(self):
        self._donacion('DRY-1', 50000, 'completado')
        mail.outbox = []
        call_command('send_weekly_digest', '--dry-run', stdout=type('O', (), {'write': lambda *a: None})())
        self.assertEqual(len(mail.outbox), 0)

    def test_envia_a_destinatarios_de_to(self):
        self._donacion('MAIL-1', 75000, 'completado')
        call_command('send_weekly_digest', '--to', 'uno@funcrees.org, dos@funcrees.org')
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(sorted(msg.to), ['dos@funcrees.org', 'uno@funcrees.org'])
        self.assertIn('Resumen FUNCREES', msg.subject)
        self.assertIn('$75.000', msg.subject)
        html = next(a for a in msg.alternatives if a[1] == 'text/html')[0]
        self.assertIn('$75.000', html)
        self.assertIn('Apadrinamientos activos', html)
        self.assertIn('/admin/', html)  # botón hacia el panel
        self.assertIn('Ver cifras en vivo', html)  # enlace bajo el gráfico

    def test_no_cuenta_pendientes_en_el_total(self):
        self._donacion('OK-1', 20000, 'completado')
        self._donacion('PEND-1', 999999, 'pendiente')
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        self.assertNotIn('$999.999', mail.outbox[0].subject)
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn('pendiente', html)  # sí se mencionan como pendientes

    @override_settings(DIGEST_TO='')
    def test_sin_destinatarios_no_envia_nada(self):
        call_command('send_weekly_digest')
        self.assertEqual(len(mail.outbox), 0)

    def test_correo_vacio_cuando_no_hay_datos(self):
        """Sin donaciones del mes el correo se envía igual, con $0."""
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('$0', mail.outbox[0].subject)

    def _png_adjunto(self):
        msg = mail.outbox[0]
        pngs = [a for a in msg.attachments if a.get_content_type() == 'image/png']
        return pngs[0] if pngs else None

    def test_correo_incluye_grafico_embebido(self):
        """El correo lleva el PNG embebido (CID) para mostrarlo inline."""
        self._donacion('IMG-1', 75000, 'completado')
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        parte = self._png_adjunto()
        self.assertIsNotNone(parte, 'el correo debe traer un PNG adjunto')
        self.assertEqual(parte['Content-Id'], '<grafico-mensual>')
        self.assertIn('inline', (parte['Content-Disposition'] or '').lower())
        img = Image.open(io.BytesIO(parte.get_payload(decode=True)))
        self.assertEqual(img.format, 'PNG')
        self.assertEqual(img.size[0], 1200)  # ancho del lienzo @2x

    def test_grafico_pinta_la_barra_del_mes_con_datos(self):
        """La barra del mes actual se dibuja en verde de la paleta FUNCREES."""
        self._donacion('IMG-BIG', 1000000, 'completado')
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        parte = self._png_adjunto()
        img = Image.open(io.BytesIO(parte.get_payload(decode=True))).convert('RGB')
        # Base de la barra del último mes (mes actual): verde oscuro del degradado
        px = img.getpixel((1054, 380))
        r, g, b = px
        self.assertTrue(g > r and g > b, f'la barra debería ser verde, salió {px}')

    def test_correo_lista_pagos_por_confirmar(self):
        """Pendientes >1h aparecen en la sección ámbar con enlace directo al filtro del panel."""
        self._donacion('PEND-STALE', 50000, 'pendiente', antiguedad=dt.timedelta(hours=3))
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn('Pagos por confirmar con Wompi', html)
        self.assertIn('PEND-STALE', html)
        self.assertIn('$50.000', html)
        self.assertIn('3h esperando', html)
        # Enlace profundo al listado filtrado del admin (mismo criterio >1h)
        self.assertIn('/admin/donations/donation/?pendientes=si', html)
        self.assertIn('Verificar con Wompi', html)

    def test_correo_no_muestra_pendientes_recientes(self):
        """Un pago de hace minutos todavía no exige atención: no aparece en la sección."""
        self._donacion('PEND-RECENT', 50000, 'pendiente', antiguedad=dt.timedelta(minutes=10))
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        html = mail.outbox[0].alternatives[0][0]
        self.assertNotIn('Pagos por confirmar con Wompi', html)
        self.assertNotIn('PEND-RECENT', html)

    def test_correo_indica_total_cuando_hay_mas_de_ocho(self):
        """La lista muestra máximo 8 filas; si hay más, informa el total completo."""
        for i in range(10):
            self._donacion(f'PEND-MUCHOS-{i:02d}', 10000, 'pendiente', antiguedad=dt.timedelta(hours=2))
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn('(10 en total)', html)
        # Solo 8 filas de detalle (cada una con su "Xh esperando")
        self.assertEqual(html.count('h esperando'), 8)

    def test_grafico_tiene_enlace_al_panel(self):
        """Bajo el gráfico hay un enlace al panel (cifras en vivo)."""
        self._donacion('LINK-1', 50000, 'completado')
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn('cid:grafico-mensual', html)
        # El enlace aparece después de la imagen, dentro de la misma tarjeta
        self.assertLess(html.index('cid:grafico-mensual'), html.index('Ver cifras en vivo'))
        self.assertIn('href="https://funcreescolombia.org/admin/"', html)

    def test_grafico_meses_sin_datos_en_cero(self):
        """Con datos solo en el mes actual, los otros meses se etiquetan $0."""
        self._donacion('IMG-SOLO', 30000, 'completado')
        call_command('send_weekly_digest', '--to', 'x@funcrees.org')
        parte = self._png_adjunto()
        # El PNG debe existir y ser una imagen válida aunque haya 5 barras vacías
        img = Image.open(io.BytesIO(parte.get_payload(decode=True)))
        self.assertEqual(img.size, (1200, 560))
