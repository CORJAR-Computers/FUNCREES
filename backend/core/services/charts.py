"""
Renderizador del gráfico "Recaudado por mes" como imagen PNG (Pillow).

Lo consume el resumen semanal por correo: el PNG se adjunta embebido (CID)
al mensaje y la plantilla lo referencia con <img src="cid:...">.

Restricciones respetadas:
- Solo Pillow, que ya es dependencia del proyecto (redimensionado de
  imágenes del panel). Sin matplotlib ni paquetes nuevos.
- Tipografía bitmap de Pillow (load_default(size=...)) con fallback a Arial
  de Windows cuando existe: evita depender de fuentes del sistema operativo.

La estética replica el panel del admin: paleta verde de FUNCREES (#2d502d /
#578c57), fondo crema, mes actual con borde resaltado.
"""
import io
import os

from PIL import Image, ImageDraw, ImageFont

# ── Paleta (coherente con el correo HTML y el panel del admin) ──────────
VERDE_OSCURO = (45, 80, 45)     # barras / textos importantes (#2d502d)
VERDE_MEDIO = (87, 140, 87)     # degradado de barra (#578c57)
VERDE_CLARO = (176, 206, 176)   # borde del mes actual
TEXTO_SUAVE = (110, 120, 110)
FONDO = (255, 255, 255)
FONDO_TARJETA = (240, 247, 240)
LINEA = (229, 239, 229)
CREMA = (244, 247, 244)

# Dimensiones (px @1x; el email se envía @2x con width/height a la mitad)
W, H = 1200, 560
MARGEN_IZQ = 110
MARGEN_DER = 60
MARGEN_SUP = 140  # deja aire para título + subtítulo + valor de la barra más alta
MARGEN_INF = 130

NUM_BARRAS = 6


def _font(tamano: int):
    """Fuente de tamaño dado: Arial si existe, si no la bitmap de Pillow."""
    for ruta in (
        'C:/Windows/Fonts/arialbd.ttf' if tamano >= 20 else 'C:/Windows/Fonts/arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ):
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, tamano)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=tamano)
    except TypeError:
        return ImageFont.load_default()


def _texto_ancho(draw, texto, font) -> int:
    bbox = draw.textbbox((0, 0), texto, font=font)
    return bbox[2] - bbox[0]


def _formato_cop_corto(valor: int) -> str:
    """$750 mil / $1,2 M — mismo criterio que core/services.py."""
    if valor >= 1_000_000:
        s = f'{valor / 1_000_000:.1f}'.rstrip('0').rstrip('.').replace('.', ',')
        return f'${s} M'
    if valor >= 1_000:
        return f'${valor // 1000} mil'
    return f'${valor}'


def _formato_cop(valor: int) -> str:
    return '$' + f'{int(valor):,}'.replace(',', '.')


def generar_grafico_mensual(serie_mensual: list) -> bytes:
    """
    Dibuja el gráfico de barras a partir de la serie de core.services
    (misma fuente de datos que el panel del admin).

    Args:
        serie_mensual: lista de dicts con claves mes, total, es_actual
                        (claves producidas por resumen_fundacion()).
    Returns:
        PNG como bytes.
    """
    datos = list(serie_mensual)[-NUM_BARRAS:]
    max_total = max((int(d.get('total') or 0) for d in datos), default=0) or 1

    img = Image.new('RGB', (W, H), FONDO)
    draw = ImageDraw.Draw(img)

    f_titulo = _font(34)
    f_sub = _font(22)
    f_valor = _font(26)
    f_eje = _font(24)
    f_cero = _font(24)

    # ── Título ────────────────────────────────────────────────────────
    draw.text((60, 28), 'Recaudado por mes — últimos 6 meses', font=f_titulo, fill=VERDE_OSCURO)
    draw.text((60, 74), 'Donaciones completadas (confirmadas por Wompi) · COP', font=f_sub, fill=TEXTO_SUAVE)

    # ── Área de trazado ───────────────────────────────────────────────
    plot_w = W - MARGEN_IZQ - MARGEN_DER
    plot_h = H - MARGEN_SUP - MARGEN_INF
    plot_top = MARGEN_SUP
    plot_bottom = plot_top + plot_h
    base_y = plot_bottom

    # Línea base
    draw.line([(MARGEN_IZQ, base_y), (W - MARGEN_DER, base_y)], fill=LINEA, width=3)

    ancho_slot = plot_w / len(datos)
    ancho_barra = min(96, int(ancho_slot * 0.5))

    for i, d in enumerate(datos):
        total = int(d.get('total') or 0)
        cx = int(MARGEN_IZQ + ancho_slot * (i + 0.5))

        # ── Valor encima de la barra ─────────────────────────────────
        etiqueta_valor = _formato_cop_corto(total)
        h_barra = int(total / max_total * (plot_h - 46)) if total > 0 else 0
        top_barra = base_y - max(h_barra, 0)

        if total > 0:
            # Degradado vertical simulado con líneas horizontales (rápido)
            for y in range(top_barra, base_y):
                t = (y - top_barra) / max(h_barra, 1)
                color = tuple(int(VERDE_MEDIO[c] + (VERDE_OSCURO[c] - VERDE_MEDIO[c]) * t) for c in range(3))
                draw.line([(cx - ancho_barra // 2, y), (cx + ancho_barra // 2, y)], fill=color)
            # Etiqueta de valor encima de la barra
            draw.text(
                (cx - _texto_ancho(draw, etiqueta_valor, f_valor) // 2, top_barra - 38),
                etiqueta_valor, font=f_valor, fill=VERDE_OSCURO,
            )
        else:
            # Mes sin datos: marca pequeña en la base + etiqueta $0
            draw.line(
                [(cx - 14, base_y - 3), (cx + 14, base_y - 3)],
                fill=VERDE_CLARO, width=4,
            )
            draw.text(
                (cx - _texto_ancho(draw, etiqueta_valor, f_cero) // 2, base_y - 36),
                etiqueta_valor, font=f_cero, fill=TEXTO_SUAVE,
            )

        # ── Marco del mes actual ─────────────────────────────────────
        if d.get('es_actual'):
            draw.rounded_rectangle(
                [(cx - ancho_barra // 2 - 12, top_barra - 50), (cx + ancho_barra // 2 + 12, base_y + 6)],
                radius=14, outline=VERDE_CLARO, width=3,
            )

        # ── Etiqueta del mes ─────────────────────────────────────────
        draw.text(
            (cx - _texto_ancho(draw, d['mes'], f_eje) // 2, base_y + 18),
            d['mes'], font=f_eje, fill=VERDE_OSCURO,
        )

    # ── Pie: tarjeta con la cifra destacada del mes actual ───────────
    actual = next((d for d in datos if d.get('es_actual')), datos[-1] if datos else None)
    if actual is not None:
        texto_pie = f"{actual['mes']}: {_formato_cop(int(actual.get('total') or 0))} recaudados este mes"
        ancho_pie = _texto_ancho(draw, texto_pie, f_sub)
        x0 = (W - ancho_pie) // 2 - 24
        y0 = H - 62
        draw.rounded_rectangle(
            [(x0, y0), (x0 + ancho_pie + 48, y0 + 46)],
            radius=12, fill=FONDO_TARJETA,
        )
        draw.text(((W - ancho_pie) // 2, y0 + 10), texto_pie, font=f_sub, fill=VERDE_OSCURO)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()
