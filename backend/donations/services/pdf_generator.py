import io
import qrcode
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.conf import settings

GREEN_DARK = colors.HexColor('#2d502d')
GREEN_MID = colors.HexColor('#578c57')
GREEN_LIGHT = colors.HexColor('#e8f5e9')

def generate_donation_certificate(nombre, documento, monto, referencia, tipo, fecha) -> bytes:
    """Genera un certificado de donación en PDF y lo retorna en bytes."""
    buffer = io.BytesIO()
    
    # A4: 595.27 x 841.89 points
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Fondo Superior Verde ---
    c.setFillColor(GREEN_DARK)
    c.rect(0, height - 200, width, 200, fill=1, stroke=0)

    # --- Encabezado ---
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2.0, height - 70, "FUNCREES COLOMBIA")
    
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2.0, height - 105, "Fundación Crece Una Esperanza Social")

    c.setFillColor(colors.HexColor('#a8d5a2'))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2.0, height - 145, "C E R T I F I C A D O   D E   D O N A C I Ó N")

    # --- Cuerpo ---
    c.setFillColor(colors.HexColor('#333333'))
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 260, "Por medio del presente certificado, la")

    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(width / 2.0, height - 280, "Fundación Crece Una Esperanza Social")

    c.setFillColor(colors.HexColor('#333333'))
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 305, "hace constar que:")

    # --- Donante ---
    c.setFillColor(GREEN_MID)
    c.rect(80, height - 390, width - 160, 55, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2.0, height - 373, str(nombre).upper())

    # --- Detalle ---
    c.setFillColor(colors.HexColor('#333333'))
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 440, "Ha realizado una")

    tipo_label = {
        'general': 'Donación General Solidaria',
        'apadrinamiento': 'Apadrinamiento de Adulto Mayor',
        'patrocinio': 'Patrocinio Empresarial',
        'boleta': 'Adquisición de Bono Solidario'
    }.get(tipo, 'Donación Solidaria')

    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 465, tipo_label)

    # --- Monto ---
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 26)
    formatted_monto = f"${int(monto):,} COP".replace(',', '.')
    c.drawCentredString(width / 2.0, height - 515, formatted_monto)

    # --- Datos extra ---
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, height - 600, "REFERENCIA DE PAGO:")
    c.drawString(100, height - 620, "IDENTIFICACIÓN DONANTE:")
    c.drawString(width / 2.0 + 30, height - 600, "FECHA DE DONACIÓN:")
    c.drawString(width / 2.0 + 30, height - 620, "NIT FUNDACIÓN:")

    c.setFont("Helvetica", 10)
    c.drawString(240, height - 600, str(referencia))
    c.drawString(240, height - 620, str(documento) if documento else "No registrada")
    c.drawString(width / 2.0 + 150, height - 600, fecha.strftime('%d/%m/%Y'))
    c.drawString(width / 2.0 + 150, height - 620, "900.000.000-0")

    # --- Pie ---
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2.0, 150, "Este certificado es un soporte de su aporte solidario. Para efectos tributarios según la Ley 1819 de 2016,")
    c.drawCentredString(width / 2.0, 135, "consulte con su asesor contable. La Fundación está legalmente constituida y autorizada para recibir donaciones.")

    c.setFillColor(GREEN_DARK)
    c.rect(0, 0, width, 60, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.drawCentredString(width / 2.0, 25, "Sincelejo, Sucre | contacto@funcrees.org | www.funcrees.org")

    c.showPage()
    c.save()
    
    return buffer.getvalue()


def generate_event_ticket(comprador, evento_titulo, numero_ticket, codigo_verificacion, monto, fecha) -> bytes:
    """Genera boleta de evento en PDF con código QR."""
    buffer = io.BytesIO()
    
    # Custom ticket size: 14 cm x 7 cm
    ticket_width = 14 * cm
    ticket_height = 7 * cm
    c = canvas.Canvas(buffer, pagesize=(ticket_width, ticket_height))

    # --- Base ---
    c.setFillColor(colors.HexColor('#fafafa'))
    c.rect(0, 0, ticket_width, ticket_height, fill=1, stroke=0)

    # --- Franja Izquierda ---
    c.setFillColor(GREEN_DARK)
    c.rect(0, 0, 4.5 * cm, ticket_height, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(2.25 * cm, ticket_height / 2 - 10, str(numero_ticket).zfill(4))
    
    c.setFont("Helvetica", 8)
    c.drawCentredString(2.25 * cm, ticket_height - 1.5 * cm, "BOLETA N°")

    # --- Info derecha ---
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(5.5 * cm, ticket_height - 1.5 * cm, str(evento_titulo)[:30])

    c.setFillColor(colors.HexColor('#555555'))
    c.setFont("Helvetica", 8)
    c.drawString(5.5 * cm, ticket_height - 2.5 * cm, f"Comprador: {comprador}")
    c.drawString(5.5 * cm, ticket_height - 3.2 * cm, f"Valor: ${int(monto):,} COP".replace(',', '.'))
    if fecha:
        c.drawString(5.5 * cm, ticket_height - 3.9 * cm, f"Fecha Evento: {fecha.strftime('%d/%m/%Y')}")
    c.drawString(5.5 * cm, ticket_height - 4.6 * cm, f"Código: {codigo_verificacion}")

    # --- Código QR ---
    frontend_url = getattr(settings, 'FRONTEND_URL', 'https://funcrees.org')
    qr_url = f"{frontend_url}/verificar-ticket?code={codigo_verificacion}"
    
    # Generar QR Image
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to temp memory
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        img.save(tf, format="PNG")
        tf.flush()
        # Dibujar en el PDF
        c.drawImage(tf.name, ticket_width - 3.5 * cm, ticket_height / 2 - 1.5 * cm, width=3*cm, height=3*cm)
    
    import os
    os.remove(tf.name)

    c.showPage()
    c.save()
    
    return buffer.getvalue()
