"""
Tests de subida de imágenes y del pipeline admin → API.

Correr con: python manage.py test beneficiaries --settings=core.test_settings
"""
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Beneficiary


def make_test_image(width=1600, height=1000, fmt='JPEG'):
    """Genera una imagen de prueba en memoria (sin tocar el disco)."""
    buffer = BytesIO()
    img = Image.new('RGB', (width, height), color=(52, 152, 219))
    img.save(buffer, format=fmt)
    return SimpleUploadedFile('foto_prueba.jpg', buffer.getvalue(), content_type='image/jpeg')


class BeneficiaryImageUploadTests(TestCase):
    """Subida de fotos desde el admin (el flujo del personal de FUNCREES)."""

    def test_foto_subida_tiene_prioridad_sobre_url(self):
        b = Beneficiary.objects.create(
            nombre='Carmen Martínez',
            historia='Historia de prueba',
            foto_url='https://example.com/vieja.jpg',
        )
        b.foto.save('carmen.jpg', make_test_image(), save=True)
        res = self.client.get(reverse('beneficiary-list'))
        results = res.json()
        results = results['results'] if isinstance(results, dict) and 'results' in results else results
        item = next(x for x in results if x['nombre'] == 'Carmen Martínez')
        # El serializer unifica: foto y foto_url apuntan al archivo subido
        self.assertIn('/media/beneficiarios/', item['foto'])
        self.assertEqual(item['foto'], item['foto_url'])

    def test_foto_url_usada_cuando_no_hay_archivo(self):
        Beneficiary.objects.create(
            nombre='Sin archivo',
            historia='Historia',
            foto_url='https://example.com/externa.jpg',
        )
        res = self.client.get(reverse('beneficiary-list'))
        results = res.json()
        results = results['results'] if isinstance(results, dict) and 'results' in results else results
        item = next(x for x in results if x['nombre'] == 'Sin archivo')
        self.assertIsNone(item['foto'])
        self.assertEqual(item['foto_url'], 'https://example.com/externa.jpg')

    def test_imagen_grande_se_redimensiona(self):
        b = Beneficiary.objects.create(nombre='Grande', historia='Historia')
        b.foto.save('grande.jpg', make_test_image(width=1600, height=1000), save=True)
        b.refresh_from_db()
        with Image.open(b.foto.path) as img:
            self.assertLessEqual(max(img.width, img.height), 800)

    def test_imagen_pequena_no_se_alarga(self):
        b = Beneficiary.objects.create(nombre='Pequeña', historia='Historia')
        b.foto.save('pequena.jpg', make_test_image(width=400, height=300), save=True)
        b.refresh_from_db()
        with Image.open(b.foto.path) as img:
            self.assertEqual((img.width, img.height), (400, 300))
