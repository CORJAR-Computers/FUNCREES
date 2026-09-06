"""
Variantes WebP y srcset responsive para las imágenes subidas desde el panel.

Objetivo: que /historias y /eventos carguen más rápido. Cada foto subida
(beneficiarios y eventos) genera copias WebP a varios anchos; el serializer
las expone como `srcset` y el navegador elige la más ligera que su pantalla
necesite. WebP pesa ~25-35% menos que un JPEG equivalente.

- Solo Pillow (dependencia existente del proyecto).
- Idempotente: regenerar sobreescribe las variantes con el original como
  fuente (útil tras un backfill o si cambian los parámetros).
- El archivo original NUNCA se modifica ni borra: los navegadores sin WebP
  (hoy casi ninguno) reciben el original vía <img> de respaldo.
- El pipeline de subida no bloquea el guardado ante un error de imagen.

Consumido por: modelos Beneficiary/Event (al guardar), serializers públicos
(`foto_webp_srcset` / `imagen_webp_srcset`) y el comando de backfill
`generate_image_variants` para imágenes ya existentes.
"""
import logging
import os
import re

from django.conf import settings
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

# Anchos estándar de las variantes. Además se genera una variante al ancho
# real del original (tras el redimensionado de los modelos: 800px
# beneficiarios, 1200px eventos) para no perder nitidez en pantallas grandes.
ANCHOS_VARIANTES = (200, 400, 800, 1200)

# Calidad WebP: 80 es el punto dulce tamaño/nitidez para fotos de retrato.
CALIDAD_WEBP = 80

# 'carmen-200w.webp' → ('carmen', 200)
PATRON_VARIANTE = re.compile(r'^(?P<base>.+)-(?P<ancho>\d+)w\.webp$')


def _rel_a_url(fieldfile, ruta_absoluta: str) -> str:
    """Ruta absoluta en MEDIA_ROOT → URL pública ('/media/...')."""
    rel = os.path.relpath(ruta_absoluta, settings.MEDIA_ROOT).replace('\\', '/')
    return fieldfile.storage.url(rel)


def _preparar_imagen(img: Image.Image) -> Image.Image:
    """Normaliza el modo de color para guardar WebP sin sorpresas:
    paleta con transparencia → RGBA; paleta sin transparencia, CMYK,
    escala de grises, etc. → RGB."""
    if img.mode == 'P':
        return img.convert('RGBA' if 'transparency' in img.info else 'RGB')
    if img.mode not in ('RGB', 'RGBA'):
        return img.convert('RGB')
    return img


def generar_variantes_webp(fieldfile) -> list:
    """
    Genera las variantes WebP de la imagen subida. Devuelve la lista de
    variantes como [{'ancho': 200, 'url': '/media/...-200w.webp'}, ...]
    (ordenada por ancho); lista vacía si no hay archivo o falla el proceso.

    Nunca lanza: un error de imagen no debe impedir guardar en el admin.
    """
    if not fieldfile:
        return []
    try:
        with Image.open(fieldfile.path) as img:
            # Respeta la rotación EXIF de las fotos de celular: las variantes
            # quedan "horneadas" en la misma orientación que muestra el navegador.
            img = ImageOps.exif_transpose(img)
            ancho_original = img.width
            base, _ = os.path.splitext(fieldfile.path)
            anchos = [a for a in ANCHOS_VARIANTES if a <= ancho_original]
            if ancho_original not in anchos and ancho_original <= ANCHOS_VARIANTES[-1]:
                anchos.append(ancho_original)

            variantes = []
            for ancho in anchos:
                destino = f'{base}-{ancho}w.webp'
                alto = max(1, round(img.height * ancho / img.width))
                variante = _preparar_imagen(img.resize((ancho, alto), Image.LANCZOS))
                variante.save(destino, 'WEBP', quality=CALIDAD_WEBP, method=4)
                variantes.append({'ancho': ancho, 'url': _rel_a_url(fieldfile, destino)})
            return variantes
    except Exception as exc:
        logger.warning('No se pudieron generar variantes WebP de %s: %s', fieldfile, exc)
        return []


def construir_srcset(fieldfile, request=None) -> str:
    """
    Construye el atributo `srcset` con las variantes WebP existentes en disco:

        '/media/beneficiarios/...-200w.webp 200w, /media/...-400w.webp 400w'

    Devuelve None si no hay archivo o aún no hay variantes (las imágenes
    subidas antes de este sistema las reciben al ejecutar el backfill
    `generate_image_variants`); en ese caso el frontend usa el <img> original.
    Si se pasa `request`, las URLs salen absolutas (consistente con `foto`).
    """
    if not fieldfile:
        return None
    carpeta = os.path.dirname(fieldfile.path)
    nombre_original = os.path.basename(fieldfile.path)
    base = os.path.splitext(nombre_original)[0]
    try:
        archivos = os.listdir(carpeta)
    except OSError:
        return None

    variantes = []
    for nombre in archivos:
        m = PATRON_VARIANTE.match(nombre)
        if m and m.group('base') == base:
            ruta = os.path.join(carpeta, nombre)
            variantes.append((int(m.group('ancho')), _rel_a_url(fieldfile, ruta)))

    if not variantes:
        return None
    variantes.sort()

    srcset = ', '.join(f'{url} {ancho}w' for ancho, url in variantes)
    if request is not None:
        srcset = ', '.join(
            f'{request.build_absolute_uri(url)} {ancho}w'
            for ancho, url in variantes
        )
    return srcset
