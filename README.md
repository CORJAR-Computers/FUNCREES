# 🌱 FUNCREES Colombia — Plataforma Web Institucional

[![Tests](https://github.com/CORJAR-Computers/FUNCREES/actions/workflows/test.yml/badge.svg)](https://github.com/CORJAR-Computers/FUNCREES/actions)

> **Fundación Crece Una Esperanza Social**
> *Soluciones Sociales Innovadoras para un Impacto Positivo y Duradero.*
> NIT: 902036173-3 | Sincelejo, Sucre, Colombia

---

## 📋 Descripción General

Plataforma web institucional de alta fidelidad para la **Fundación Funcrees Colombia**, desarrollada por **CORJAR Computers Solutions**. El sistema integra una moderna arquitectura desacoplada:
- **Frontend SvelteKit (Svelte 5):** Aplicación web reactiva, modular y accesible con renderizado del lado del servidor (SSR), enrutamiento basado en archivos y compilador Vite.
- **Backend REST API (Django 5.x):** Gestión centralizada de beneficiarios (adultos mayores), donaciones cifradas, bonos/eventos solidarios y formularios de contacto.
- **Frontend SPA Clásico (Legacy):** Versión monolítica en Vanilla JS (`index.html` + `app.js`) conservada para compatibilidad.

---

## 🗂️ Estructura del Proyecto

```
FUNCREES/
│
├── 📁 frontend/               # ⭐ NUEVO: Frontend moderno en SvelteKit (Svelte 5)
│   ├── 📁 src/
│   │   ├── app.html           # HTML base con tipografías y FontAwesome
│   │   ├── 📁 lib/
│   │   │   ├── 📁 api/        # Cliente API asíncrono para Django REST
│   │   │   ├── 📁 components/ # Componentes (Navbar, Footer, LeafletMap, Toast, etc.)
│   │   │   ├── 📁 data/       # Catálogo de proyectos y modelos locales
│   │   │   ├── 📁 stores/     # Estado reactivo global con Svelte 5 Runes ($state)
│   │   │   ├── 📁 styles/     # Hojas de estilo CSS institucionales
│   │   │   └── 📁 utils/      # Utilidades (parseCOP, formatMoneyNumber, sanitizeHTML)
│   │   └── 📁 routes/         # Enrutamiento basado en archivos
│   │       ├── +layout.svelte # Layout global, widgets flotantes y banner de cookies
│   │       ├── +page.svelte   # Inicio (Hero Banner y Métricas de impacto)
│   │       ├── quienes-somos/ # Identidad, Misión, Visión 2030 y Valores
│   │       ├── proyectos/     # Catálogo con búsqueda reactiva y filtros
│   │       ├── historias/     # Beneficiarios con API Django y modal
│   │       ├── eventos/       # Eventos, cuentas regresivas y bonos
│   │       ├── donaciones/    # Tiers de apadrinamiento, Wompi y formularios
│   │       └── contacto/      # Contacto con Django, Mapa Leaflet y Aliados
│   ├── 📁 static/             # Assets estáticos (Logo oficial, fotos)
│   ├── 📁 tests/              # Suite de pruebas unitarias con node:test
│   ├── svelte.config.js       # Configuración del framework
│   ├── vite.config.js         # Configuración Vite + Proxy a Django (/api)
│   └── package.json           # Dependencias frontend (Svelte 5, Vite 8)
│
├── 📁 backend/                # API REST con Django 5.x
│   ├── manage.py              # Punto de entrada de Django
│   ├── populate_db.py         # Script de datos semilla (seed data)
│   ├── .env.example           # Plantilla de variables de entorno
│   ├── 📁 core/               # Configuración global (DB, CORS, Unfold, DRF)
│   ├── 📁 beneficiaries/      # App: Gestión de adultos mayores beneficiarios
│   ├── 📁 donations/          # App: Donaciones, apadrinamiento y Wompi
│   ├── 📁 events/             # App: Eventos solidarios y venta de boletas
│   ├── 📁 contact/            # App: Mensajes de contacto y alianzas
│   └── requirements.txt       # Dependencias Python del backend
│
├── 📁 legacy/                 # 📦 Versión anterior (SPA Vanilla JS, estilos y 135 tests)
│   ├── index.html             # Frontend SPA clásico
│   ├── app.js                 # Motor JS clásico
│   ├── 📁 assets/             # Recursos estáticos clásicos
│   ├── 📁 tests/              # Suite de 135 tests unitarios clásicos
│   └── 🎨 base.css, components.css, themes.css, responsive.css
│
├── 📦 package.json            # Scripts npm unificados (desarrollo, build, tests)
├── 🚀 start.bat               # Script Windows para iniciar backend y frontend juntos
├── 📖 README.md               # Este archivo
└── 📖 DEPLOY.md               # Guía de deployment
```

---

## 🛠️ Stack Tecnológico

### Frontend (SvelteKit 5 + Vanilla Legacy)

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **SvelteKit** | 2.63.x | Framework de aplicaciones fullstack con enrutamiento basado en archivos y SSR |
| **Svelte 5** | 5.56.x | Sistema de reactividad moderno con Runes (`$state`, `$derived`, `$props`) |
| **Vite** | 8.0.x | Entorno de desarrollo rápido, bundler optimizado y proxy inverso a Django REST |
| **Leaflet.js** | 1.9.4 | Mapa interactivo de ubicación institucional (Sincelejo, Sucre) |
| **CSS3 / Variables HSL** | Nativo | Glassmorphism, diseño responsivo y accesibilidad (Alto contraste, Dislexia, TTS) |
| **Google Fonts** | Inter + Outfit | Tipografía institucional moderna y legible |
| **FontAwesome** | 6.4.0 | Iconografía vectorial del sitio |
| **Vanilla JS (Legacy)** | ES6+ | SPA clásica conservada en raíz (`index.html` + `app.js`) para compatibilidad |

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

### Frontend Moderno (SvelteKit 5 - Recomendado)

```bash
# Opción A: Desde la raíz del proyecto
npm run frontend:dev      # Inicia Vite en http://localhost:5173 con proxy inverso a Django (/api)
npm run frontend:build    # Compila para producción SSR
npm run frontend:check    # Verificación de tipos y componentes Svelte con svelte-check
npm run frontend:test     # Ejecuta pruebas unitarias de utilidades frontend

# Opción B: Directamente en la carpeta frontend
cd frontend
npm install
npm run dev
```

### Frontend Clásico (Legacy Vanilla JS)

```bash
# Desde la raíz del proyecto
npm install
npm start                 # Abre servidor local en http://localhost:5500
```

### Scripts Disponibles

| Script | Comando | Descripción |
|--------|---------|-------------|
| **Frontend SvelteKit (Dev)** | `npm run frontend:dev` | Inicia servidor Vite en `http://localhost:5173` con proxy a `/api` |
| **Frontend SvelteKit (Build)** | `npm run frontend:build` | Genera bundle optimizado SSR/producción con SvelteKit |
| **Frontend SvelteKit (Check)** | `npm run frontend:check` | Diagnóstico de tipos y sintaxis Svelte con `svelte-check` |
| **Frontend SvelteKit (Tests)** | `npm run frontend:test` | Ejecuta suite de tests de utilidades frontend (`node:test`) |
| **Desarrollo completo (Legacy)**| `npm run dev` | Inicia backend Django y frontend SPA clásico juntos |
| **Solo frontend clásico** | `npm start` | Sirve SPA clásica en puerto 5500 (`serve`) |
| **Tests SPA clásica** | `npm test` | Ejecuta los 135 tests unitarios de la versión clásica |
| **Tests SPA (watch)** | `npm run test:watch` | Re-ejecuta tests clásicos al detectar cambios |
| **Cobertura SPA clásica** | `npm run test:coverage` | Genera reporte de cobertura de la versión clásica |

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

El proyecto cuenta con dos suites automatizadas de pruebas:

### 1. Tests Frontend SvelteKit (`frontend/tests/`)
Pruebas unitarias sobre utilidades de formato monetario y saneamiento contra vulnerabilidades XSS:

| Archivo | Tests | Cubre |
|---------|-------|-------|
| `currency.test.js` | 4 | `parseCOP()`, `formatMoneyNumber()`, sanitización de valores vacíos e inválidos |
| `sanitize.test.js` | 4 | `sanitizeHTML()`, prevención XSS y neutralización de atributos maliciosos |

```bash
# Ejecutar tests de frontend moderno
npm run frontend:test

# Verificación estática y de tipos
npm run frontend:check
```

### 2. Tests SPA Clásica Legacy (`tests/`)
Suite integral de **135 tests unitarios** para la versión clásica:

| Archivo | Tests | Cubre |
|---------|-------|-------|
| `unit.test.js` | 45 | `sanitizeHTML()`, `parseCOP()`, `showToast()` |
| `iife-encapsulation.test.js` | 44 | Encapsulación IIFE, exports, aislamiento global |
| `interactions.test.js` | 46 | Modales, checkout, filtros, navegación |

```bash
# Ejecutar tests clásicos
npm test

# Ejecutar con cobertura
npm run test:coverage
```

---

## 🌐 Deployment

Para instrucciones detalladas de deployment en producción, consultar [DEPLOY.md](DEPLOY.md).

### Resumen Rápido

1. Configurar servidor Ubuntu 22.04 con Nginx, PostgreSQL, Python, Node.js
2. Clonar proyecto en `/var/www/funcrees`
3. Configurar variables de entorno en `.env` y frontend
4. Ejecutar migraciones Django y build de SvelteKit (`npm run frontend:build`)
5. Configurar Gunicorn / Node adapter como servicios systemd
6. Configurar Nginx como reverse proxy para API y Frontend
7. Instalar certificado SSL con Certbot

---

## 📅 Historial de Versiones

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| **v1.1.0** | Septiembre 2026 | **Migración Frontend SvelteKit**: Arquitectura modular con **Svelte 5 Runes** (`$state`), Vite 8, proxy inverso integrado a Django REST API, mapas interactivos con Leaflet.js, catálogo reactivo de proyectos, apadrinamiento con cálculo dinámico y widgets de accesibilidad universal (TTS, dislexia, alto contraste). |
| v1.0.0 | Julio 2026 | Producción: Backend Django + Frontend SPA clásico |
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
