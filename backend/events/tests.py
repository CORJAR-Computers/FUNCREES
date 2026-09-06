"""
Tests de subida de imágenes de eventos y del pipeline admin → API.

Correr con: python manage.py test events --settings=core.test_settings
"""
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Event


def make_test_image(width=1600, height=900, fmt='JPEG'):
    """Genera una imagen de prueba en memoria (sin tocar el disco)."""
    buffer = BytesIO()
    img = Image.new('RGB', (width, height), color=(46, 204, 113))
    img.save(buffer, format=fmt)
    return SimpleUploadedFile('imagen_prueba.jpg', buffer.getvalue(), content_type='image/jpeg')


class EventImageUploadTests(TestCase):
    """Subida de imágenes desde el admin (el flujo del personal de FUNCREES)."""

    def test_foto_subida_tiene_prioridad_sobre_url(self):
        e = Event.objects.create(
            id='test-evento',
            titulo='Evento de prueba',
            costo_bono=10000,
            imagen_url='https://example.com/vieja.jpg',
        )
        e.imagen.save('evento.jpg', make_test_image(), save=True)
        res = self.client.get(reverse('event-list'))
        results = res.json()
        results = results['results'] if isinstance(results, dict) and 'results' in results else results
        item = next(x for x in results if x['id'] == 'test-evento')
        self.assertIn('/media/eventos/', item['imagen'])
        self.assertEqual(item['imagen'], item['imagen_url'])

    def test_imagen_grande_se_redimensiona(self):
        e = Event.objects.create(id='grande', titulo='Grande', costo_bono=10000)
        e.imagen.save('grande.jpg', make_test_image(width=2000, height=1200), save=True)
        e.refresh_from_db()
        with Image.open(e.imagen.path) as img:
            self.assertLessEqual(max(img.width, img.height), 1200)


def _variantes_de(fieldfile):
    """Nombres de las variantes WebP existentes en disco para un archivo."""
    import os
    carpeta = os.path.dirname(fieldfile.path)
    base = os.path.splitext(os.path.basename(fieldfile.path))[0]
    return sorted(
        n for n in os.listdir(carpeta)
        if n.startswith(base + '-') and n.endswith('.webp')
    )


class EventWebpVariantsTests(TestCase):
    """Variantes WebP para el srcset responsive de /eventos."""

    def test_subida_genera_variantes_webp(self):
        e = Event.objects.create(id='webp-ev', titulo='Con WebP', costo_bono=10000)
        e.imagen.save('promo.jpg', make_test_image(width=2000, height=1200), save=True)
        variantes = _variantes_de(e.imagen)
        # 1200px es el ancho real tras el redimensionado; 200/400/800 son menores
        # (orden lexicográfico del helper: '1200w' < '200w')
        self.assertEqual(
            variantes,
            ['promo-1200w.webp', 'promo-200w.webp', 'promo-400w.webp', 'promo-800w.webp'],
        )
        with Image.open(e.imagen.path.replace('.jpg', '-400w.webp')) as img:
            self.assertEqual(img.format, 'WEBP')
            self.assertEqual(img.width, 400)

    def test_api_expone_srcset_con_urls_absolutas(self):
        e = Event.objects.create(id='srcset-ev', titulo='Srcset', costo_bono=10000)
        e.imagen.save('srcset.jpg', make_test_image(), save=True)
        res = self.client.get(reverse('event-list'))
        results = res.json()
        results = results['results'] if isinstance(results, dict) and 'results' in results else results
        item = next(x for x in results if x['id'] == 'srcset-ev')
        srcset = item['imagen_webp_srcset']
        self.assertIsNotNone(srcset)
        self.assertIn('200w', srcset)
        self.assertTrue(srcset.startswith('http://'))

    def test_api_sin_archivo_devuelve_srcset_nulo(self):
        """Evento con solo imagen_url externa: el frontend usa el <img> plano."""
        Event.objects.create(
            id='externa-ev', titulo='Externa', costo_bono=10000,
            imagen_url='https://example.com/externa.jpg',
        )
        res = self.client.get(reverse('event-list'))
        results = res.json()
        results = results['results'] if isinstance(results, dict) and 'results' in results else results
        item = next(x for x in results if x['id'] == 'externa-ev')
        self.assertIsNone(item['imagen_webp_srcset'])
