# 📘 Documentación Técnica - Portal Institucional FUNCREES Colombia

> **Fundación Crece Una Esperanza Social (Funcrees)**
> Documento técnico de empalme y referencia para el equipo de mantenimiento y operatividad.

---

## 1. Descripción General del Proyecto

El portal institucional de Funcrees es una plataforma web híbrida que se compone de una **Single Page Application (SPA)** en el Frontend y una **API RESTful** en el Backend. Su objetivo es gestionar beneficiarios (adultos mayores), recibir donaciones (únicas y apadrinamientos), organizar eventos solidarios y facilitar el contacto con la fundación.

---

## 2. Stack Tecnológico (Lenguajes y Herramientas)

### 🎨 FrontEnd
El frontend ha sido desarrollado sin frameworks pesados para garantizar un rendimiento óptimo y máxima accesibilidad:
- **Lenguajes:** HTML5 (semántico), CSS3 (Vanilla con variables HSL), JavaScript ES6+ (Nativo/Vanilla).
- **Diseño:** Sistema UI Premium (Glassmorphism), fuentes de Google (Inter y Outfit).
- **Accesibilidad (WCAG 2.1):** Lector de voz nativo (Web Speech API), escalado de fuente, modo alto contraste, fuente especial para dislexia, persistencia en `localStorage`.

### ⚙️ BackEnd
El backend está construido con Python y expone servicios mediante una API REST para el portal web:
- **Lenguaje:** Python 3.11+
- **Framework Web:** Django (>=5.0, <5.2)
- **API REST:** Django REST Framework (DRF >=3.14)
- **Panel de Administración:** `django-unfold` (interfaz de administración moderna).
- **Utilidades Adicionales:** 
  - `django-cors-headers` (manejo de CORS frontend-backend).
  - `django-filter` (filtros avanzados de API).
  - `django-environ` (manejo de variables de entorno).
  - `reportlab` y `qrcode` (generación de certificados PDF y códigos QR para boletas).
  - `cryptography` (Fernet) para cifrado **simétrico** de datos sensibles.

### 🗄️ Base de Datos y Servidor
- **Desarrollo Local:** SQLite3 (por defecto en Django).
- **Producción Recomendada:** PostgreSQL 15+ (`psycopg2-binary`).
- **Despliegue Recomendado:** Nginx (proxy inverso), Gunicorn (servidor WSGI), Certbot (certificados SSL).

---

## 3. Estructura del Proyecto

El proyecto está dividido físicamente en la carpeta raíz (para el FrontEnd) y una subcarpeta `/backend/` (para el BackEnd):

```text
e:/FUNCREES/
├── index.html              # Frontend: Estructura principal SPA (6 vistas integradas)
├── styles.css              # Frontend: Sistema de diseño, temas y accesibilidad
├── app.js                  # Frontend: Motor JavaScript (Navegación, TTS, Pagos)
├── propuesta.html          # Vista de propuesta comercial (CORJAR)
├── requirements.txt        # Dependencias del entorno Python
├── start.bat               # Script para levantar el entorno de desarrollo local (Windows)
├── /assets/                # Recursos estáticos: Logos, imágenes corporativas
└── /backend/               # 🐍 Proyecto Django (API REST y CMS)
    ├── manage.py           # CLI principal de Django
    ├── .env                # Archivo de variables de entorno (Oculto en control de versiones)
    ├── db.sqlite3          # Base de datos local
    ├── core/               # Configuración global de Django (settings, urls, asgi, wsgi)
    ├── beneficiaries/      # App: Gestión de adultos mayores
    ├── donations/          # App: Gestión de donaciones y apadrinamientos
    ├── events/             # App: Gestión de eventos solidarios y boletería
    └── contact/            # App: Recepción de formularios de contacto
```

---

## 4. Arquitectura del BackEnd (Modelos Principales)

El backend está modularizado en "Apps" de Django para una fácil escalabilidad:

1. **Beneficiaries (`beneficiaries/`):**
   - **Modelo `Beneficiary`**: Almacena UUID, nombre, historia biográfica, multimedia (fotos/videos), estado activo y métricas de apadrinamiento.
2. **Donations (`donations/`):**
   - **Modelo `Donation`**: Registra transacciones con referencia única, tipo (general, boleta, apadrinamiento), estado del pago. Cifra el documento del donante (AES-128 Fernet, cifrado simétrico) para cumplir con la Ley Habeas Data (1581).
   - **Modelo `Sponsorship`**: Maneja configuraciones de suscripciones o apadrinamientos recurrentes.
3. **Events (`events/`):**
   - **Modelo `Event`**: Detalles del evento, fechas, aforo.
   - **Modelo `Ticket`**: Boletas emitidas vinculadas a un evento, con códigos y generación de QR.
4. **Contact (`contact/`):**
   - **Modelo `ContactMessage`**: Buzón de mensajes entrantes del portal web.

---

## 5. Endpoints de la API REST

El frontend consume la información e inyecta los datos mediante el prefijo de API:

| Método | Endpoint                  | Acción Operativa                           |
|--------|---------------------------|--------------------------------------------|
| GET    | `/api/beneficiaries/`     | Obtener el catálogo de beneficiarios       |
| GET    | `/api/beneficiaries/{id}/`| Detalle completo de un beneficiario        |
| GET    | `/api/events/`            | Obtener la cartelera de eventos disponibles|
| POST   | `/api/tickets/`           | Compra y emisión de tickets / boletas      |
| POST   | `/api/donations/`         | Registrar una nueva donación               |
| POST   | `/api/contact/`           | Procesar y almacenar mensaje de contacto   |
| GET    | `/admin/`                 | Acceso web al Panel de Administración      |

---

## 6. Integración de Pagos (Pasarelas)

El sistema maneja flujos de pago que pueden integrar servicios de terceros:
- **PSE (ACH Colombia)** y **Wompi (Bancolombia):** Requieren llaves reales configuradas en el archivo `.env` (`WOMPI_PUBLIC_KEY`, `WOMPI_PRIVATE_KEY`, `WOMPI_INTEGRITY_SECRET`).
- **Transferencia Manual:** Incluye verificación administrativa manual por parte del equipo interno.

> ⚠️ **Nota de Seguridad Crítica:** Todo dato sensible recolectado de donantes es cifrado utilizando la llave maestra `ENCRYPTION_KEY` definida en el `.env`. Si esta llave se pierde, la base de datos cifrada será irrecuperable.

---

## 7. Operatividad y Mantenimiento de Despliegue

### Requisitos Típicos de Servidor
- **Servidor:** Instancia VPS (Ej. Hostinger Business VPS, AWS EC2, DigitalOcean).
- **Sistema Operativo:** Ubuntu 22.04 LTS (recomendado).
- **Dependencias base:** Python 3.11+, PostgreSQL, Nginx, Certbot (para SSL).

### Gestión de Variables de Entorno
El portal **NO** operará en producción sin el archivo `.env` configurado adecuadamente. Incluye:
- `DEBUG=False` (Vital para evitar fugas de información).
- `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` (Autorización exclusiva de dominios).
- `DATABASE_URL` (Cadena de conexión segura).
- Variables SMTP (Para envío de correos).

### Operaciones Comunes de Mantenimiento (Comandos)
Cualquier actualización de código requiere los siguientes pasos estándar dentro del entorno virtual del servidor:

```bash
# 1. Aplicar actualizaciones de Base de Datos (Si hay cambios en los Modelos)
python manage.py migrate

# 2. Recopilar nuevos archivos estáticos (CSS, JS, imágenes del admin)
python manage.py collectstatic --noinput

# 3. Reiniciar el servicio WSGI para aplicar cambios de Python
sudo systemctl restart gunicorn
```

---
*Documento generado para el equipo técnico y de operaciones. Este manual facilita la comprensión arquitectónica para el empalme y mantenimiento a largo plazo.*
