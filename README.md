# 🌱 FUNCREES Colombia — Plataforma Web Institucional

[![Tests](https://github.com/CORJAR-Computers/FUNCREES/actions/workflows/test.yml/badge.svg)](https://github.com/CORJAR-Computers/FUNCREES/actions)

> **Fundación Crece Una Esperanza Social**
> *Soluciones Sociales Innovadoras para un Impacto Positivo y Duradero.*
> NIT: 902036173-3 | Sincelejo, Sucre, Colombia

---

## 📋 Descripción General

Plataforma web institucional de alta fidelidad para la **Fundación Funcrees Colombia**, desarrollada por **CORJAR Computers Solutions**. El sistema integra un **frontend SPA (Single Page Application)** moderno y accesible con un **backend REST API** en Django para la gestión de beneficiarios, donaciones, eventos y contactos.

---

## 🗂️ Estructura del Proyecto

```
FUNCREES/
│
├── 📄 index.html              # Frontend SPA principal (6 vistas integradas)
├── 🎨 base.css                # Reset, variables CSS, keyframes
├── 🎨 components.css          # Estilos de componentes
├── 🎨 themes.css              # Modo oscuro, alto contraste, dislexia
├── 🎨 responsive.css          # Todos los media queries
├── ⚡ app.js                  # Motor JavaScript (IIFE, 21 exports en window)
├── 📑 propuesta.html          # Generador de propuesta comercial CORJAR
├── 📦 package.json            # Scripts npm (dev, test, test:coverage, etc.)
├── 📦 requirements.txt        # Dependencias Python del backend
├── 📖 README.md               # Este archivo
├── 📖 DEPLOY.md               # Guía de deployment para el cliente
│
├── 📁 assets/                 # Recursos visuales del sitio
│   ├── Logo.png               # Logotipo oficial
│   └── Foto Fundación.png     # Fotografía institucional principal
│
├── 📁 backend/                # API REST con Django 5.x
│   ├── manage.py              # Punto de entrada de Django
│   ├── populate_db.py         # Script de datos semilla (seed data)
│   ├── .env                   # Variables de entorno (NO subir a Git)
│   ├── .env.example           # Plantilla de variables de entorno
│   ├── gunicorn.conf.py       # Configuración Gunicorn para producción
│   │
│   ├── 📁 core/               # Configuración central del proyecto Django
│   │   ├── settings.py        # Configuración global (DB, CORS, Unfold, DRF)
│   │   ├── urls.py            # Enrutador principal + registro de API endpoints
│   │   ├── asgi.py            # Servidor ASGI (despliegue async)
│   │   └── wsgi.py            # Servidor WSGI (despliegue tradicional)
│   │
│   ├── 📁 beneficiaries/      # App: Gestión de adultos mayores beneficiarios
│   │   ├── models.py          # Modelo Beneficiary (UUID, nombre, historia, foto)
│   │   ├── views.py           # ViewSet REST para CRUD de beneficiarios
│   │   ├── serializers.py     # Serializadores DRF
│   │   └── migrations/        # Migraciones de base de datos
│   │
│   ├── 📁 donations/          # App: Donaciones, apadrinamiento y patrocinios
│   │   ├── models.py          # Modelos: Donation, Sponsorship (cifrado Fernet)
│   │   ├── views.py           # ViewSet REST para donaciones
│   │   ├── serializers.py     # Serializadores DRF
│   │   ├── services/          # Servicios externos
│   │   │   ├── wompi.py       # Integración con pasarela de pagos Wompi
│   │   │   ├── email_service.py # Servicio de envío de emails
│   │   │   └── pdf_generator.py # Generación de certificados PDF
│   │   └── migrations/        # Migraciones de base de datos
│   │
│   ├── 📁 events/             # App: Eventos solidarios y venta de boletas
│   │   ├── models.py          # Modelos: Event, Ticket (código único generado)
│   │   ├── views.py           # ViewSet REST para eventos y tickets
│   │   ├── serializers.py     # Serializadores DRF
│   │   └── migrations/        # Migraciones de base de datos
│   │
│   ├── 📁 contact/            # App: Formulario de contacto y alianzas
│   │   ├── models.py          # Modelo ContactMessage
│   │   ├── views.py           # ViewSet REST para mensajes de contacto
│   │   ├── serializers.py     # Serializadores DRF
│   │   └── migrations/        # Migraciones de base de datos
│   │
│   ├── 📁 templates/          # Templates de email y páginas de error
│   │   ├── emails/
│   │   │   └── donation_confirmation.html
│   │   ├── 404.html
│   │   └── 500.html
│   │
│   └── 📁 scripts/            # Scripts utilitarios
│       └── migrate_to_postgresql.py
│
├── 📁 tests/                  # Tests unitarios (135 tests)
│   ├── unit.test.js           # 45 tests (sanitizeHTML, parseCOP, showToast)
│   ├── iife-encapsulation.test.js # 44 tests (encapsulación IIFE)
│   └── interactions.test.js   # 46 tests (modales, checkout, filtros)
│
├── 📁 .github/workflows/      # CI: GitHub Action (push/PR a main)
│   └── test.yml               # Tests con Node 20/22 matrix
│
└── 📁 mejoras_FUNCREES/       # Documentación de mejoras de seguridad
    ├── apply_frontend_patches.py
    ├── RESUMEN_CAMBIOS_FRONTEND.md
    └── backend/
        └── (configuraciones de referencia)
```

---

## 🛠️ Stack Tecnológico

### Frontend

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **HTML5** | Semántico | Estructura SPA de 6 vistas integradas |
| **CSS3 / Vanilla CSS** | Variables HSL | Sistema de diseño premium con glassmorphism |
| **JavaScript (ES6+)** | Nativo | Motor SPA, TTS, pasarelas simuladas |
| **Google Fonts** | Inter + Outfit | Tipografía moderna y accesible |
| **Leaflet.js** | 1.9.4 | Mapa interactivo de ubicación |
| **FontAwesome** | 6.4.0 | Iconografía del sitio |

### Backend

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.10+ | Lenguaje base del servidor |
| **Django** | ≥5.0, <5.3 | Framework web principal |
| **Django REST Framework** | ≥3.14, <3.17 | API REST con ViewSets y serializadores |
| **django-unfold** | ≥0.40.0 | Panel de administración moderno |
| **django-cors-headers** | ≥4.3, <4.6 | Gestión de peticiones CORS |
| **django-filter** | ≥24.2, <26.0 | Filtros avanzados en endpoints |
| **django-environ** | ≥0.11, <0.13 | Manejo seguro de variables de entorno |
| **whitenoise** | ≥6.6, <7.0 | Servicio de archivos estáticos |
| **gunicorn** | ≥21.2, <24.0 | Servidor WSGI para producción |
| **psycopg2-binary** | ≥2.9, <3.0 | Driver PostgreSQL |
| **cryptography (Fernet)** | ≥41.0, <45.0 | Cifrado de datos sensibles (Ley 1581) |
| **reportlab** | ≥4.1, <5.0 | Generación de certificados PDF |
| **qrcode** | ≥7.4, <9.0 | Generación de QR para boletas |

### Base de Datos

| Entorno | Motor | Estado |
|---------|-------|--------|
| **Desarrollo local** | SQLite 3 | ✅ Activo |
| **Producción** | PostgreSQL 14+ | 🔧 Requerido |

---

## 🚀 Instrucciones de Instalación

### Pre-requisitos

- **Python** 3.10 o superior
- **Node.js** 18+ (para tests y herramientas de desarrollo)
- **PostgreSQL** 14+ (para producción)

### Inicio Rápido (Desarrollo Local)

```bash
# 1. Clonar el repositorio
git clone https://github.com/CORJAR-Computers/FUNCREES.git
cd FUNCREES

# 2. Configurar backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 4. Ejecutar migraciones
python manage.py migrate
python populate_db.py  # Cargar datos de ejemplo

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Iniciar servidor
python manage.py runserver
```

### Frontend (desarrollo)

```bash
# Desde la raíz del proyecto
npm install
npm start  # Abre http://localhost:5500
```

### Scripts Disponibles

| Script | Comando | Descripción |
|--------|---------|-------------|
| **Desarrollo completo** | `npm run dev` | Inicia backend y frontend juntos |
| **Solo frontend** | `npm start` | Sirve archivos estáticos en puerto 5500 |
| **Tests** | `npm test` | Ejecuta los 135 tests unitarios |
| **Tests (watch)** | `npm run test:watch` | Re-ejecuta tests al detectar cambios |
| **Cobertura** | `npm run test:coverage` | Genera reporte de cobertura |

---

## 🔌 API Endpoints

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/beneficiaries/` | Lista beneficiarios activos | Pública |
| GET | `/api/beneficiaries/{id}/` | Detalle de beneficiario | Pública |
| GET | `/api/events/` | Lista de eventos | Pública |
| GET | `/api/events/{id}/` | Detalle de evento | Pública |
| POST | `/api/donations/initiate/` | Iniciar proceso de donación | Pública |
| POST | `/api/donations/webhook/` | Webhook de Wompi | Pública |
| GET | `/api/donations/{referencia}/status/` | Estado de donación | Pública |
| POST | `/api/contact/` | Enviar mensaje de contacto | Pública |
| GET | `/api/health/` | Health check del servidor | Pública |
| GET | `/admin/` | Panel de administración | Admin |

---

## 🔒 Seguridad

| Medida | Implementación |
|--------|----------------|
| **Cifrado de datos sensibles** | Fernet (AES-128) para documentos, teléfonos y tokens de tarjeta |
| **Variables de entorno** | SECRET_KEY, DATABASE_URL, claves de Wompi en `.env` |
| **CORS configurado** | Lista blanca explícita de orígenes permitidos |
| **CSRF Protection** | Habilitado por defecto en Django |
| **Content Security Policy** | Configurada en `index.html` |
| **Rate Limiting** | Throttling en endpoints públicos (donaciones, contacto) |
| **HSTS** | Habilitado en producción (1 año) |
| **Autorización de datos** | Checkbox de consentimiento requerido (Ley 1581) |

---

## 🧪 Tests

El proyecto cuenta con **135 tests unitarios** organizados en 3 archivos:

| Archivo | Tests | Cubre |
|---------|-------|-------|
| `unit.test.js` | 45 | `sanitizeHTML()`, `parseCOP()`, `showToast()` |
| `iife-encapsulation.test.js` | 44 | Encapsulación IIFE, exports, aislamiento global |
| `interactions.test.js` | 46 | Modales, checkout, filtros, navegación |

```bash
# Ejecutar todos los tests
npm test

# Ejecutar con cobertura
npm run test:coverage
```

---

## 🌐 Deployment

Para instrucciones detalladas de deployment en producción, consultar [DEPLOY.md](DEPLOY.md).

### Resumen Rápido

1. Configurar servidor Ubuntu 22.04 con Nginx, PostgreSQL, Python
2. Clonar proyecto en `/var/www/funcrees`
3. Configurar variables de entorno en `.env`
4. Ejecutar migraciones y collectstatic
5. Configurar Gunicorn como servicio systemd
6. Configurar Nginx como reverse proxy
7. Instalar certificado SSL con Certbot

---

## 📅 Historial de Versiones

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| v1.0.0 | Julio 2026 | Producción: Backend Django + Frontend SPA (En preparación) |
| v0.4.1 | Junio 2026 | Tests de interacción, CI/CD, .gitattributes |
| v0.4.0 | Junio 2026 | IIFE encapsulation, CSS dividido, 89 tests |
| v0.3.0 | Junio 2026 | Propuesta comercial interactiva |
| v0.2.0 | Junio 2026 | Backend REST API Django |
| v0.1.0 | Junio 2026 | Prototipo frontend SPA |

---

## 👨‍💻 Desarrollado por

**CORJAR Computers Solutions**
- RUT: 92520615
- Teléfono: +57 (317) 746-7035
- Email: corjarcomputers@gmail.com

**Cliente:** Fundación Crece Una Esperanza Social — FUNCREESCOLOMBIA
- Director General: William Romero Hernández — (+57) 313 792 4439
- Email: fundacioncreceunaesperanza@gmail.com

---

## 📄 Licencia

© 2026 Fundación Crece Una Esperanza Social. Todos los derechos reservados.

*Desarrollado con ❤️ por CORJAR Computers Solutions*
