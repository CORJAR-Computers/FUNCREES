# FUNCREES Colombia — Sitio Web

**Fundación Crece Una Esperanza Social (FUNCREES)** · NIT 902036173-3 · Sincelejo, Sucre, Colombia

Sitio web institucional con donaciones en línea (Wompi), eventos solidarios,
apadrinamiento de adultos mayores y panel administrativo.

**Stack:** SvelteKit 2 (SSR, TypeScript, Svelte 5 runes) · Django 5 + Django REST Framework · PostgreSQL · Nginx · Wompi

---

## 📁 Estructura

```
funcrees/
├── frontend/              ← SvelteKit (SSR + TypeScript)
│   ├── src/routes/        ← Páginas (/, /quienes-somos, /proyectos, /historias,
│   │                         /donaciones, /eventos, /contacto + +error + sitemap.xml)
│   ├── src/lib/           ← api/ (cliente DRF), components/, stores/, utils/, types.ts
│   ├── tests/             ← Tests de Node (node --test)
│   └── build/             ← Salida de producción (adapter-node)
├── backend/               ← Django REST Framework
│   ├── core/              ← settings, urls (health check en /api/health/)
│   ├── beneficiaries/     ← API pública de beneficiarios
│   ├── events/            ← Eventos y boletas
│   ├── donations/         ← Donaciones + Wompi (initiate, webhook, certificados PDF)
│   ├── contact/           ← Formulario de contacto
│   └── templates/         ← Emails y errores
├── deploy_nginx.conf      ← Config de Nginx para producción
├── funcrees-web.service   ← Servicio systemd del frontend
├── DEPLOY.md              ← Guía de despliegue completa
└── requirements.txt       ← (raíz, referencia) usar backend/requirements.txt
```

---

## 🚀 Desarrollo Local (Windows)

Requisitos: Node 22+, Python 3.12+, Git.

```bash
# 1. Backend (primera vez)
cd backend
python -m venv venv
venv\Scripts\pip install -r requirements.txt
copy .env.example .env        # y edita los valores (DEBUG=True está bien en local)
venv\Scripts\python manage.py migrate

# 2. Frontend (primera vez)
cd ../frontend
npm install

# 3. Correr todo (raíz del proyecto) — levanta Django :8000 y Vite :5173
npm run dev
```

- Sitio: http://localhost:5173 (el proxy de Vite reenvía `/api` → `:8000`)
- API: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/

> En Linux/Mac ajusta las rutas de `venv\Scripts\python` a `venv/bin/python`.

---

## 🧪 Tests y Verificación

```bash
# Frontend
npm run frontend:check        # svelte-check (TypeScript + a11y + Svelte)
npm run frontend:test         # node --test (27 tests: utils + cliente API)
npm run frontend:build        # build de producción (adapter-node)

# Backend (desde backend/)
venv\Scripts\python manage.py test          # donations, contact, beneficiaries
venv\Scripts\python manage.py check --deploy  # validación de seguridad de producción
```

El CI (`.github/workflows/test.yml`) ejecuta todo esto en cada push/PR:
svelte-check + build + tests de Node (Node 22/24) y `check --deploy` +
tests de Django (Python 3.12/3.13).

---

## 💳 Pagos (Wompi)

El flujo de donación/bonos es real:

1. `POST /api/donations/initiate/` — el backend valida (serializer con límites,
   Habeas Data), crea la donación en estado `pendiente` y firma la petición
   (firma de integridad SHA256 con `WOMPI_INTEGRITY_SECRET`).
2. El frontend abre el checkout de Wompi con esa configuración.
3. Wompi notifica en `POST /api/donations/webhook/` — el backend verifica la
   firma (HMAC en tiempo constante), es idempotente (`select_for_update`) y al
   aprobarse genera el certificado PDF y lo envía por correo.
4. El frontend hace polling de `GET /api/donations/{ref}/status/` y muestra el
   estado real al donante.

Probar en sandbox: `WOMPI_ENV=sandbox` + llaves sandbox en `backend/.env`.

---

## 🔐 Seguridad y cumplimiento

- **Ley 1581 (Habeas Data):** documento y teléfono del donante cifrados con
  Fernet en reposo (`EncryptedCharField`); autorización de datos obligatoria.
- **Webhook Wompi:** firma verificada con propiedades fijas (no controlables
  por el atacante) y comparación en tiempo constante; idempotente ante reenvíos.
- **API:** throttle por scope (donaciones 10/h, contacto 5/h), CORS explícito,
  CSRF restringido por origen, `DATA_UPLOAD_MAX_*` acotados.
- **Producción:** HSTS, SSL redirect, cookies seguras, cabeceras en Nginx y
  Django, health check sin fuga de información.

---

## 📦 Deploy a Producción

Ver **[DEPLOY.md](DEPLOY.md)** — guía completa para VPS Ubuntu (recomendado:
Hostinger VPS Corporativo) con PostgreSQL, Gunicorn, SvelteKit adapter-node,
Nginx, Certbot, backups y monitoreo.

---

## 📝 Notas

- La URL canónica para SEO se configura con `VITE_SITE_URL` (default
  `https://funcreescolombia.org`).
- Si la API vive en otro dominio, configura `VITE_API_BASE` en el build del
  frontend y agrega ese origen a `CORS_ALLOWED_ORIGINS` del backend.
- El sitemap se genera dinámicamente en `/sitemap.xml`; `robots.txt` vive en
  `frontend/static/`.

---

&copy; 2026 Fundación Crece Una Esperanza (Funcrees) Colombia · Diseñado por CORJAR Computer Solutions
