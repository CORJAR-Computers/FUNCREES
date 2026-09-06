# -*- coding: utf-8 -*-
"""
Genera la versión imprimible del paquete de entrega:

  HTML  →  PAQUETE_ENTREGA.html   (para navegador: Ctrl+P → Guardar como PDF)
  PDF   →  PAQUETE_ENTREGA.pdf    (directo, sin navegador — ideal en el VPS)

Uso (desde la raíz del repo):
    backend/venv/Scripts/python scripts/build_print_pack.py          # HTML
    backend/venv/Scripts/python scripts/build_print_pack.py --pdf    # PDF

Requisitos:
- HTML: Node/npx en el PATH (usa `npx -y marked`; no instala nada en el
  proyecto — el paquete vive en la caché de npx).
- PDF: lo anterior + `xhtml2pdf` (ya está en backend/requirements.txt;
  se apoya en reportlab, que el proyecto ya usa para los certificados).

El PDF usa únicamente las fuentes base-14 (Helvetica/Courier), por lo que NO
depende de fuentes instaladas en el servidor. Como esas fuentes no cubren
emojis ni símbolos técnicos, `--pdf` normaliza el texto:
    ☐→[ ]   ✅✔✓→[OK]   →→->   ≥→>=   ≤→<=   ⚠→[!]   🔴🚨→[ALERTA]   ⏳→[PENDIENTE]
y elimina los emojis decorativos de los títulos. El HTML del navegador los
conserva intactos.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "PAQUETE_ENTREGA.md"
OUT_HTML = ROOT / "PAQUETE_ENTREGA.html"
OUT_PDF = ROOT / "PAQUETE_ENTREGA.pdf"

# ─── Normalización de símbolos para el PDF ───────────────────────────
# Fuentes base-14 = Latin-1/CP1252. Sustituciones con significado claro.
MAPA_SIMBOLOS_PDF = {
    "\u2610": "[ ]",            # ☐ casilla de verificación
    "\u2705": "[OK]",           # ✅
    "\u2714": "[OK]",           # ✔
    "\u2713": "[OK]",           # ✓
    "\u2192": "->",             # →
    "\u2265": ">=",             # ≥
    "\u2264": "<=",             # ≤
    "\u26a0": "[!]",            # ⚠
    "\U0001f534": "[ALERTA]",   # 🔴
    "\U0001f6a8": "[ALERTA]",   # 🚨
    "\u23f3": "[PENDIENTE]",    # ⏳
}
# Emojis decorativos (títulos, viñetas): se quitan sin reemplazo.
EMOJIS_DECORATIVOS = (
    "\U0001f4e6\U0001f9ef\U0001f519\U0001f4ca\U0001f51f\U0001f4c4\U0001f9ed"
    "\U0001f6e0\U0001f4cb\U0001f4a1\U0001f4f8\U0001f4b3\U0001f512\U0001f4dd"
    "\U0001f504\U0001f4be\u270d\u2709"
)
# Variantes de selección (emoji VS16) y cualquier resto no Latin-1 → fuera.
RE_VS16 = re.compile("\ufe0f")
RE_NO_LATIN = re.compile(r"[^\x00-\x7f\u00a1-\u00ff\u20ac\u2018\u2019\u201c"
                         r"\u201d\u2013\u2014\u2026\u2020\u2021\u2022\u2122]")

CSS_HTML = """
:root {
  --verde: #0b6e4f;
  --verde-oscuro: #084c36;
  --gris: #5a6b66;
  --borde: #d7dedb;
  --fondo-codigo: #f4f6f5;
}
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.5;
  color: #1c2422;
  max-width: 186mm;
  margin: 0 auto;
  padding: 8mm 0 4mm;
}
@page {
  size: A4;
  margin: 16mm 12mm 14mm;
  @bottom-center {
    content: "FUNCREES Colombia · Paquete de entrega — página " counter(page) " de " counter(pages);
    font-size: 8pt;
    color: #7a8a84;
    font-family: "Segoe UI", Arial, sans-serif;
  }
}
h1 {
  break-before: page;
  break-after: avoid;
  font-size: 17pt;
  color: var(--verde-oscuro);
  border-bottom: 2.5pt solid var(--verde);
  padding-bottom: 3mm;
  margin: 0 0 6mm;
  line-height: 1.25;
}
body > h1:first-child { break-before: auto; }
h2 {
  break-after: avoid;
  font-size: 13pt;
  color: var(--verde);
  margin: 7mm 0 3mm;
  border-left: 3pt solid var(--verde);
  padding-left: 3mm;
}
h3 { break-after: avoid; font-size: 11.5pt; color: #24352f; margin: 5mm 0 2.5mm; }
p, li { orphans: 3; widows: 3; }
pre {
  break-inside: avoid;
  background: var(--fondo-codigo);
  border: 0.6pt solid var(--borde);
  border-left: 2.5pt solid var(--gris);
  border-radius: 2pt;
  padding: 3mm 3.5mm;
  font-family: Consolas, "Courier New", monospace;
  font-size: 8.6pt;
  line-height: 1.45;
  white-space: pre-wrap;
  overflow-wrap: break-word;
  margin: 3mm 0;
}
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 0.92em;
  background: var(--fondo-codigo);
  padding: 0.3pt 2pt;
  border-radius: 2pt;
}
pre code { background: none; padding: 0; }
table { break-inside: avoid; border-collapse: collapse; width: 100%; margin: 3mm 0; font-size: 9.5pt; }
th { background: #e7f0ec; color: var(--verde-oscuro); text-align: left; }
th, td { border: 0.6pt solid var(--borde); padding: 1.6mm 2.4mm; vertical-align: top; }
ul, ol { padding-left: 6mm; margin: 2mm 0 3mm; }
li { margin-bottom: 1.1mm; }
body > h1:first-child {
  text-align: center;
  font-size: 21pt;
  border-bottom: none;
  border-top: 3pt solid var(--verde);
  border-bottom: 3pt solid var(--verde);
  padding: 10mm 0;
  margin-top: 18mm;
}
blockquote {
  break-inside: avoid;
  margin: 3mm 0;
  padding: 2.5mm 4mm;
  background: #f0f6f3;
  border-left: 3pt solid var(--verde);
  color: #2c3a35;
}
blockquote p { margin: 1mm 0; }
a { color: var(--verde); text-decoration: none; }
hr { border: none; border-top: 0.8pt solid var(--borde); margin: 6mm 0; }
strong { color: #14201c; }
"""

# CSS para xhtml2pdf: sintaxis limitada (sin variables, sin selectores modernos).
CSS_PDF = """
body { font-family: Helvetica; font-size: 9.5pt; color: #1c2422; line-height: 1.45; }
h1 { font-size: 15pt; color: #084c36; border-bottom: 1.5pt solid #0b6e4f; padding-bottom: 4pt; margin: 4pt 0 10pt; }
h2 { font-size: 12pt; color: #0b6e4f; margin: 12pt 0 5pt; }
h3 { font-size: 10.5pt; color: #24352f; margin: 9pt 0 4pt; }
pre { font-family: Courier; font-size: 7.8pt; color: #24352f; background-color: #f4f6f5; margin: 4pt 0; }
code { font-family: Courier; font-size: 8.2pt; color: #24352f; }
table { margin: 4pt 0; font-size: 8.5pt; }
th { background-color: #e7f0ec; color: #084c36; }
th, td { border: 0.5pt solid #b9c6c1; padding: 3pt 4pt; }
blockquote { color: #2c3a35; background-color: #f0f6f3; margin: 4pt 0; padding: 5pt; font-size: 9pt; }
li { margin: 1pt 0; }
hr { color: #d7dedb; }
"""

SHELL_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>FUNCREES Colombia — Paquete de Entrega (imprimible)</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""

SHELL_PDF = """<html><head>
<meta name="author" content="FUNCREES Colombia">
<title>FUNCREES Colombia — Paquete de Entrega</title>
<style>
{css}
@page {{
  size: a4 portrait;
  margin: 1.9cm 1.6cm 2.2cm;
  @frame footer_frame {{
    -pdf-frame-content: footer_content;
    left: 47pt; width: 500pt; top: 806pt; height: 20pt;
  }}
}}
</style></head><body>
<div id="footer_content" style="font-size: 7.5pt; color: #7a8a84; text-align: center;">
FUNCREES Colombia · Paquete de entrega — p&aacute;gina <pdf:pagenumber> de <pdf:pagecount>
</div>
{body}
</body></html>
"""


def normalizar_para_pdf(texto: str) -> str:
    """Sustituye símbolos/emojis que las fuentes base-14 no pueden dibujar."""
    for simbolo, reemplazo in MAPA_SIMBOLOS_PDF.items():
        texto = texto.replace(simbolo, reemplazo)
    for emoji in EMOJIS_DECORATIVOS:
        texto = texto.replace(emoji, "")
    texto = RE_VS16.sub("", texto)
    # Cualquier otro carácter fuera de Latin-1/CP1252: espacio (no debería ocurrir).
    texto = RE_NO_LATIN.sub(" ", texto)
    return texto


def markdown_a_html(md_texto: str) -> str:
    """Convierte Markdown a HTML con `npx -y marked` (sin instalar nada).

    En Windows `npx` es npx.cmd y subprocess no lo resuelve solo: se
    localiza con shutil.which (si falla, falta Node/npx en el PATH).
    """
    npx = shutil.which("npx")
    if not npx:
        print("ERROR: no se encontró npx. Instala Node.js o revísalo con `npx -v`.")
        sys.exit(1)
    with tempfile.TemporaryDirectory() as tmp:
        entrada = pathlib.Path(tmp) / "input.md"
        body = pathlib.Path(tmp) / "body.html"
        entrada.write_text(md_texto, encoding="utf-8")
        subprocess.run(
            [npx, "-y", "marked", str(entrada), "-o", str(body)],
            check=True,
            cwd=str(ROOT),
        )
        return body.read_text(encoding="utf-8")


def generar_html() -> None:
    body = markdown_a_html(SRC.read_text(encoding="utf-8"))
    OUT_HTML.write_text(SHELL_HTML.format(css=CSS_HTML, body=body), encoding="utf-8")
    print(f"OK  {OUT_HTML.name}  ({OUT_HTML.stat().st_size / 1024:.0f} kB, {body.count('<h1')} secciones)")
    print("    Imprimir: abrir en el navegador → Ctrl+P → Guardar como PDF (A4).")


def generar_pdf() -> None:
    try:
        from xhtml2pdf import pisa
        import pypdf
    except ImportError:
        print("ERROR: falta xhtml2pdf (o pypdf). En el VPS basta `pip install -r requirements.txt`.")
        print("       En Windows (no está en requirements): backend/venv/Scripts/python -m pip install xhtml2pdf")
        sys.exit(1)

    from io import BytesIO

    body = markdown_a_html(normalizar_para_pdf(SRC.read_text(encoding="utf-8")))
    # Salto de página real antes de cada PARTE/acta (todos los h1 menos el primero).
    partes = body.split("<h1>")
    body = partes[0] + "".join(f"<pdf:nextpage /><h1>{p}" for p in partes[1:])
    # Repetir encabezados de tabla al saltar de página.
    body = body.replace("<table>", '<table repeat="1">')

    html = SHELL_PDF.format(css=CSS_PDF, body=body)
    buffer = BytesIO()
    resultado = pisa.CreatePDF(html, dest=buffer, encoding="utf-8")
    if resultado.err:
        print(f"ERROR: xhtml2pdf reportó {resultado.err} problema(s); revisa el HTML fuente.")
        sys.exit(1)

    OUT_PDF.write_bytes(buffer.getvalue())
    paginas = len(pypdf.PdfReader(str(OUT_PDF)).pages)
    print(f"OK  {OUT_PDF.name}  ({OUT_PDF.stat().st_size / 1024:.0f} kB, {paginas} páginas, {body.count('<h1')} secciones)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera la versión imprimible de PAQUETE_ENTREGA.md")
    parser.add_argument("--pdf", action="store_true", help="genera el PDF directamente (sin navegador)")
    args = parser.parse_args()

    if not SRC.exists():
        print(f"ERROR: no existe {SRC}")
        return 1
    if args.pdf:
        generar_pdf()
    else:
        generar_html()
    return 0


if __name__ == "__main__":
    sys.exit(main())
