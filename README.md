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

`
e:/FUNCREES/
│
├── 📄 index.html              # Frontend SPA principal (6 vistas integradas)
├── 🎨 styles.css              # Entry point (importa los 4 archivos CSS)
├── 🎨 base.css                # Reset, variables CSS, keyframes
├── 🎨 components.css          # Estilos de componentes (~2500 líneas)
├── 🎨 themes.css              # Modo oscuro, alto contraste, dislexia
├── 🎨 responsive.css          # Todos los media queries
├── ⚡ app.js                  # Motor JavaScript (IIFE, 21 exports en window)
├── 📑 propuesta.html          # Generador de propuesta comercial CORJAR
├── 📦 package.json            # Scripts npm (dev, test, test:coverage, etc.)
├── 🔒 package-lock.json       # Lockfile de dependencias npm
├── 📦 requirements.txt        # Dependencias Python del backend
├── 🚀 start.bat               # Script de arranque rápido del servidor
├── ⚙️ start_backend.bat       # Batch file para backend en Windows
├── 📖 README.md               # Este archivo
│
├── 📁 assets/                 # Recursos visuales del sitio
│   ├── Logo.png               # Logotipo oficial de Fundación Funcrees Colombia
│   ├── Foto Fundación.png     # Fotografía institucional principal
│   └── corjar_logo.png        # Logotipo CORJAR Computers Solutions
│
├── 📁 backend/                # API REST con Django 5.x
│   ├── manage.py              # Punto de entrada de Django
│   ├── populate_db.py         # Script de datos semilla (seed data)
│   ├── .env                   # Variables de entorno (NO subir a Git)
│   ├── 📁 venv/               # Entorno virtual Python (NO subir a Git)
│   │
│   ├── 📁 core/               # Configuración central del proyecto Django
│   │   ├── settings.py        # Configuración global (DB, CORS, Unfold, DRF)
│   │   ├── urls.py            # Enrutador principal + registro de API endpoints
│   │   ├── asgi.py            # Servidor ASGI (despliegue async)
│   │   └── wsgi.py            # Servidor WSGI (despliegue tradicional)
│   │
│   ├── 📁 beneficiaries/      # App: Gestión de adultos mayores beneficiarios
│   │   ├── models.py          # Modelo Beneficiary (UUID, nombre, historia, foto, estado)
│   │   ├── views.py           # ViewSet REST para CRUD de beneficiarios
│   │   ├── serializers.py     # Serializadores DRF
│   │   ├── admin.py           # Panel admin (Unfold UI)
│   │   └── migrations/        # Migraciones de base de datos
│   │
│   ├── 📁 donations/          # App: Donaciones, apadrinamiento y patrocinios
│   │   ├── models.py          # Modelos: Donation, Sponsorship (cifrado Fernet)
│   │   ├── views.py           # ViewSet REST para donaciones
│   │   ├── serializers.py     # Serializadores DRF
│   │   ├── admin.py           # Panel admin con vista de donaciones cifradas
│   │   └── migrations/        # Migraciones de base de datos
│   │
│   ├── 📁 events/             # App: Eventos solidarios y venta de boletas
│   │   ├── models.py          # Modelos: Event, Ticket (código único generado)
│   │   ├── views.py           # ViewSet REST para eventos y tickets
│   │   ├── serializers.py     # Serializadores DRF
│   │   ├── admin.py           # Panel admin para gestión de eventos
│   │   └── migrations/        # Migraciones de base de datos
│   │
│   └── 📁 contact/            # App: Formulario de contacto y alianzas
│       ├── models.py          # Modelo ContactMessage
│       ├── views.py           # ViewSet REST para mensajes de contacto
│       ├── serializers.py     # Serializadores DRF
│       ├── admin.py           # Panel admin de mensajes
│       └── migrations/        # Migraciones de base de datos
│
├── 📁 .github/workflows/      # CI: GitHub Action (push/PR a main)
│   └── test.yml               # Tests con Node 20/22 matrix
│
├── 📁 tests/                  # Tests unitarios
│   ├── unit.test.js               # 45 tests (sanitizeHTML, parseCOP, showToast)
│   ├── iife-encapsulation.test.js  # 44 tests (encapsulación IIFE)
│   └── interactions.test.js        # 46 tests (modales, checkout, filtros)
│
├── 📄 .gitattributes           # Forzar LF en JS para CI cross-platform
`

---

## 🛠️ Stack Tecnológico

### Frontend
| Tecnología | Versión | Uso |
|---|---|---|
| **HTML5** | Semántico | Estructura SPA de 6 vistas integradas |
| **CSS3 / Vanilla CSS** | Variables HSL | Sistema de diseño premium con glassmorphism |
| **JavaScript (ES6+)** | Nativo | Motor SPA, TTS, pasarelas simuladas |
| **Google Fonts** | Inter + Outfit | Tipografía moderna y accesible |
| **Web Speech API** | Nativa | Lector de pantalla TTS en español |
| **localStorage** | Nativa | Persistencia de configuración de accesibilidad |

### Backend
| Tecnología | Versión | Uso |
|---|---|---|
| **Python** | 3.11+ | Lenguaje base del servidor |
| **Django** | ≥5.0, <5.2 | Framework web principal |
| **Django REST Framework** | ≥3.14, <3.16 | API REST con ViewSets y serializadores |
| **django-unfold** | ≥0.40.0 | Panel de administración moderno con branding |
| **django-cors-headers** | ≥4.3, <4.5 | Gestión de peticiones CORS (frontend ↔ backend) |
| **django-filter** | ≥24.2, <25.0 | Filtros avanzados en endpoints de la API |
| **django-environ** | ≥0.11, <0.12 | Manejo seguro de variables de entorno |
| **whitenoise** | ≥6.6, <7.0 | Servicio de archivos estáticos en producción |
| **gunicorn** | ≥21.2, <23.0 | Servidor WSGI para producción |
| **psycopg2-binary** | ≥2.9, <3.0 | Driver PostgreSQL para producción |
| **cryptography (Fernet)** | — | Cifrado de datos sensibles (Ley Habeas Data 1581) |
| **reportlab** | ≥4.1, <5.0 | Generación de recibos/certificados en PDF |
| **qrcode** | ≥7.4, <8.0 | Generación de QR para boletas y recibos |
| **requests** | ≥2.31, <3.0 | Integración con APIs externas (Wompi, PSE) |

### Base de Datos
| Entorno | Motor | Estado |
|---|---|---|
| **Desarrollo local** | SQLite 3 | ✅ Activo (backend/db.sqlite3) |
| **Producción (recomendado)** | PostgreSQL 15+ | 🔧 Pendiente configurar |

> **¿Por qué PostgreSQL para producción?** PostgreSQL ofrece mejor manejo de concurrencia, soporte nativo para UUID, campos JSONB (usados en wompi_response), extensiones para búsqueda de texto completo en español y mayor estabilidad frente a múltiples escrituras simultáneas (crítico en campañas de donación).

---

## 🔌 API Endpoints

El backend expone una **REST API** en el prefijo /api/ con las siguientes colecciones:

| Método | Endpoint | Descripción |
|---|---|---|
| GET | /api/beneficiaries/ | Lista todos los adultos mayores activos |
| GET | /api/beneficiaries/{id}/ | Detalle de un beneficiario |
| GET | /api/events/ | Lista de eventos solidarios activos |
| POST | /api/tickets/ | Compra y generación de boleta con código único |
| POST | /api/donations/ | Registrar una donación o apadrinamiento |
| POST | /api/contact/ | Enviar mensaje de contacto / alianza |
| GET | /admin/ | Panel de administración (Unfold UI) |

---

## 🎨 Diseño y Accesibilidad (WCAG 2.1)

### Sistema de Color HSL
`
--primary:    hsl(148, 64%, 38%)   /* Verde Esperanza - Acción principal */
--secondary:  hsl(215, 60%, 24%)   /* Azul Noche - Fondos y énfasis */
--accent:     hsl(165, 55%, 68%)   /* Menta - Detalles y hover */
--bg-main:    hsl(140, 35%, 97%)   /* Crema - Fondo base */
`

### Funciones de Accesibilidad Implementadas
- ✅ **Escalado de fuente**: Botones A+ / A- con valores rem que escalan todo el sitio
- ✅ **Modo alto contraste**: Fondo negro profundo con textos amarillos de alta luminancia
- ✅ **Fuente para dislexia**: Tipografía de peso asimétrico con mayor interletrado
- ✅ **Lector de voz TTS**: Síntesis de voz en español (Web Speech API)
- ✅ **Navegación por teclado**: tabIndex y aria-label en elementos interactivos
- ✅ **HTML semántico**: Uso de main, section, nav, article, aside

---

## 💳 Sistema de Pagos (Simulado en Prototipo)

| Pasarela | Estado en Prototipo | Integración Real |
|---|---|---|
| **PSE** (ACH Colombia) | Simulado (flujo completo) | Requiere cuenta en Wompi/PayU |
| **Wompi** (Bancolombia) | Simulado (flujo completo) | Requiere cuenta comercial Wompi |
| **Transferencia Bancolombia** | Simulado (instrucciones) | Verificación manual por WhatsApp |

### Flujo de Apadrinamiento
1. Usuario elige Apadrinar → Selecciona beneficiario
2. Elige monto (SEMILLA /mes | RAÍZ /mes | LEGADO /mes en USD)
3. Selecciona pasarela de pago
4. Autoriza tratamiento de datos (Habeas Data — Ley 1581)
5. Sistema simula procesamiento → Genera comprobante con QR

---

## 🏗️ Modelos de Datos Principales

### Beneficiary (Beneficiarios)
- id: UUID (Primary Key)
- 
ombre, historia, 	estimonio: Datos biográficos
- edad, ciudad, oto_url, ideo_url: Multimedia
- ctivo, padrinado, padrinadores_count: Estado de apadrinamiento

### Donation (Donaciones)
- id: UUID (Primary Key)
- eferencia: Código único de transacción
- 	ipo: [general | apadrinamiento | patrocinio | boleta]
- monto, donante_nombre, donante_email
- donante_documento_cifrado: AES-128 Fernet (Cumplimiento Ley 1581)
- metodo_pago: [PSE | Wompi | Bancolombia]
- estado: [pendiente | procesando | completado | fallido | reembolsado]
- eneficiario: ForeignKey → Beneficiary

### Sponsorship (Apadrinamientos Recurrentes)
- 	ipo: [debito_automatico | suscripcion_manual]
- estado: [activo | pausado | cancelado | vencido]
- monto_mensual, eneficiario → FK Beneficiary
- wompi_subscription_id, echa_proximo_cobro

---

## 🚀 Instrucciones de Instalación y Ejecución Local

### Pre-requisitos
- **Python** 3.11 o superior instalado en Windows
- **Node.js** 20+ (v26.3.0 recomendado)
- **npm** incluido con Node.js
- Entorno virtual Python en `backend/venv/`

### Inicio Rápido (Recomendado)
```bash
# Instalar dependencias del frontend
npm install

# Iniciar backend + frontend simultáneamente
npm run dev
```

> `npm run dev` libera puertos automáticamente e inicia ambos servidores.
> Frontend: http://localhost:5500 · Backend: http://localhost:8000

### Opciones Alternativas de Inicio
```bash
# Opción 1: Solo backend (Django)
cd backend && venv\Scripts\python manage.py runserver

# Opción 2: Solo frontend (servidor estático)
npm start

# Opción 3: Desarrollo en ventanas separadas (Windows)
npm run dev:win

# Opción 4: Doble clic en start.bat (Explorador de Windows)
start.bat
```

### Primera Configuración (Solo una vez)
```bash
# Backend: activar entorno virtual e instalar dependencias
cd e:/FUNCREES/backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python populate_db.py          # Cargar datos de ejemplo
python manage.py createsuperuser

# Frontend: instalar dependencias npm
cd ..
npm install
```

### Scripts de Desarrollo Disponibles

| Script | Comando | Descripción |
|---|---|---|
| **Desarrollo** | `npm run dev` | Mata puertos + inicia backend (8000) y frontend (5500) simultáneamente |
| **Desarrollo (Windows)** | `npm run dev:win` | Igual que `dev` pero abre backend en ventana cmd separada |
| **Solo frontend** | `npm start` | Sirve el frontend estático en el puerto 5500 |
| **Matar puertos** | `npm run dev:kill` | Libera los puertos 5500 y 8000 |
| **Tests** | `npm test` | Ejecuta los 135 tests (node --test) |
| **Tests (watch)** | `npm run test:watch` | Re-ejecuta tests automáticamente al detectar cambios |
| **Cobertura** | `npm run test:coverage` | Genera reporte de cobertura de tests |

### URLs Locales
- **Frontend**: http://localhost:5500/
- **Backend API**: http://localhost:8000/api/
- **Panel Admin**: http://localhost:8000/admin/
- **Propuesta Comercial**: Abrir e:/FUNCREES/propuesta.html en el navegador

> ℹ️ `npm run dev` ejecuta `dev:kill` automáticamente para liberar puertos antes de iniciar.
> Si un proceso falla, el otro se detiene gracias a `--kill-others` en concurrently.

---

## 🔒 Seguridad y Cumplimiento Legal

| Medida | Implementación |
|---|---|
| **Ley 1581 (Habeas Data)** | Campos sensibles cifrados con AES-128 (Fernet) en BD |
| **Variables de entorno** | SECRET_KEY, DATABASE_URL y claves de pasarelas en .env |
| **CORS configurado** | django-cors-headers con lista blanca de orígenes |
| **CSRF Protection** | Habilitado por defecto en Django |
| **Autorización explícita** | Checkbox de consentimiento requerido antes de pago |

---

## 🌐 Plan de Migración a Producción (Hostinger VPS)

### Infraestructura Recomendada
`
Hostinger Business VPS
├── Ubuntu 22.04 LTS
├── Nginx (reverse proxy + SSL termination)
├── Gunicorn (servidor WSGI Python)
├── PostgreSQL 15 (base de datos principal)
├── Certbot (SSL/TLS gratuito — Let's Encrypt)
└── Dominio: funcreescolombia.org (por confirmar)
`

### Variables de Entorno para Producción (.env)
`
DEBUG=False
SECRET_KEY=<clave-segura-generada>
ALLOWED_HOSTS=funcreescolombia.org,www.funcreescolombia.org
DATABASE_URL=postgresql://user:pass@localhost:5432/funcrees_db
WOMPI_PUBLIC_KEY=<clave-publica-wompi>
WOMPI_PRIVATE_KEY=<clave-privada-wompi>
ENCRYPTION_KEY=<clave-fernet-base64>
`

---

## 📅 Historial de Versiones

| Versión | Fecha | Descripción |
|---|---|---|
| v0.1.0 | Jun 2026 | Prototipo frontend SPA completo |
| v0.2.0 | Jun 2026 | Backend REST API Django con SQLite local |
| v0.3.0 | Jun 2026 | Propuesta comercial interactiva CORJAR |
| v0.4.0 | Jun 2026 | Refactor: IIFE encapsulation, CSS dividido, 89 tests, CI/CD, scripts dev |
| v0.4.1 | Jun 2026 | 46 tests de interacción (modales, checkout, filtros), CI fix (glob en Linux), .gitattributes, workflow optimizado |
| v1.0.0 | Pendiente | Despliegue en producción con PostgreSQL y pasarelas reales |

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
*Versión v0.4.1 · Junio 2026 · Todos los derechos reservados © CORJAR Computers Solutions*
