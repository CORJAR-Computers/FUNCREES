# 🚀 Guía de Deploy — FUNCREES Colombia (v2.0)

Guía paso a paso para desplegar el sitio web de la Fundación Funcrees Colombia.

> **Arquitectura v2.0:** Frontend **SvelteKit SSR** (adapter-node en Node.js :3000)
> + Backend **Django REST Framework** (Gunicorn :8000), ambos detrás de **Nginx**
> en el mismo dominio (sin CORS, un solo certificado TLS).

---

## 📋 Requisitos Previos

| Componente | Versión mínima |
|------------|---------------|
| Sistema operativo | Ubuntu 22.04 LTS / Debian 12 |
| Python | 3.12+ |
| Node.js | 22 LTS |
| PostgreSQL | 14+ |
| Nginx | 1.18+ |

### 💡 Recomendación de hosting

**Hostinger VPS Corporativo (KVM 2 o superior)** es la opción sugerida para la
fundación: buen precio, soporte en español, snapshots y panel sencillo. También
funciona en DigitalOcean, Hetzner o AWS Lightsail. El despliegue es idéntico en
cualquier VPS Ubuntu.

---

## 1️⃣ Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib \
  nginx certbot python3-certbot-nginx git curl

# Node.js 22 LTS (NodeSource)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Crear directorios necesarios
sudo mkdir -p /var/log/funcrees /var/run/funcrees
sudo chown www-data:www-data /var/log/funcrees /var/run/funcrees
```

---

## 2️⃣ Clonar el Proyecto

```bash
sudo mkdir -p /var/www/funcrees
sudo chown $USER:$USER /var/www/funcrees
cd /var/www/funcrees

git clone https://github.com/TU_USUARIO/funcrees-colombia.git .

# Estructura del proyecto (v2.0)
# /var/www/funcrees/
# ├── frontend/            ← SvelteKit (SSR, adapter-node)
# │   ├── src/
# │   ├── build/           ← generado por npm run build
# │   └── node_modules/
# ├── backend/             ← Django REST Framework
# └── deploy_nginx.conf    ← configuración de Nginx lista para usar
```

---

## 3️⃣ Configurar Base de Datos PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE USER funcrees_user WITH PASSWORD 'TU_PASSWORD_SEGURO';
CREATE DATABASE funcrees_db OWNER funcrees_user;
GRANT ALL PRIVILEGES ON DATABASE funcrees_db TO funcrees_user;
\q
```

---

## 4️⃣ Configurar Backend (Django)

```bash
cd /var/www/funcrees/backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus valores reales (ver abajo)
```

### Variables de Entorno Requeridas (backend/.env)

```bash
# Django
DEBUG=False
SECRET_KEY=tu-clave-secreta-generada
ALLOWED_HOSTS=funcreescolombia.org,www.funcreescolombia.org

# Base de datos
DATABASE_URL=postgresql://funcrees_user:tu_password@localhost:5432/funcrees_db

# CORS — en esta arquitectura el frontend y la API comparten dominio,
# pero se conservan los orígenes para el admin y herramientas locales.
CORS_ALLOWED_ORIGINS=https://funcreescolombia.org,https://www.funcreescolombia.org

# Frontend (URL a la que Wompi redirige tras el pago)
FRONTEND_URL=https://funcreescolombia.org

# Email
DEFAULT_FROM_EMAIL=contacto@funcreescolombia.org
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
EMAIL_USE_TLS=True

# Wompi (Pagos)
WOMPI_ENV=production
WOMPI_PUBLIC_KEY=tu-public-key
WOMPI_PRIVATE_KEY=tu-private-key
WOMPI_INTEGRITY_SECRET=tu-integrity-secret

# Encriptación (Ley 1581)
ENCRYPTION_KEY=tu-clave-fernet-generada
```

### Generar Claves Secretas

```bash
# SECRET_KEY de Django
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# ENCRYPTION_KEY para datos sensibles (Ley 1581)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Migraciones, estáticos y superusuario

```bash
source venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput
mkdir -p media   # fotos de beneficiarios e imágenes de eventos subidas desde el admin
python manage.py createsuperuser
```

> **🖼️ Optimización de imágenes:** cada foto subida desde el panel genera
> automáticamente variantes **WebP** (200/400/800w en beneficiarios,
> hasta 1200w en eventos) para que `/historias` y `/eventos` carguen rápido:
> el navegador elige la variante que necesita vía `srcset` (~70% menos peso).
> Las imágenes subidas **antes** de instalar este sistema necesitan un
> backfill único: `python manage.py generate_image_variants` (idempotente;
> ver `--dry-run` para contar primero). Es obligatorio ejecutarlo en el VPS
> si el directorio `media/` se restauró desde un backup anterior.

---

## 5️⃣ Construir el Frontend (SvelteKit)

```bash
cd /var/www/funcrees/frontend

# Instalar dependencias y compilar (genera build/index.js)
npm ci
npm run build

# Prueba rápida local (opcional):
PORT=3000 node build   # Ctrl+C para salir
```

Variables opcionales de build (archivo `frontend/.env`):

```bash
# Dominio canónico para SEO/sitemap (solo cambia si es distinto)
VITE_SITE_URL=https://funcreescolombia.org
```

---

## 6️⃣ Servicios systemd

### Backend (Gunicorn)

```bash
sudo nano /etc/systemd/system/funcrees.service
```

```ini
[Unit]
Description=FUNCREES Backend (Django + Gunicorn)
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/funcrees/backend
ExecStart=/var/www/funcrees/backend/venv/bin/gunicorn --config gunicorn.conf.py core.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Frontend (SvelteKit adapter-node)

El archivo `funcrees-web.service` viene incluido en la raíz del repositorio:

```bash
sudo cp /var/www/funcrees/funcrees-web.service /etc/systemd/system/
```

### Activar ambos servicios

```bash
sudo chown -R www-data:www-data /var/www/funcrees
sudo systemctl daemon-reload
sudo systemctl enable --now funcrees
sudo systemctl enable --now funcrees-web
sudo systemctl status funcrees funcrees-web
```

---

## 7️⃣ Configurar Nginx

```bash
sudo cp /var/www/funcrees/deploy_nginx.conf /etc/nginx/sites-available/funcrees
sudo ln -sf /etc/nginx/sites-available/funcrees /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

> 💡 El archivo incluye el proxy a Node (:3000) para `/` y a Gunicorn (:8000)
> para `/api/`, `/admin/` y `/static/`, con CSP ajustada a Google Fonts,
> Font Awesome, Unsplash, OpenStreetMap y Wompi.

---

## 8️⃣ Configurar SSL con Certbot

```bash
sudo certbot --nginx -d funcreescolombia.org -d www.funcreescolombia.org

# Verificar renovación automática
sudo certbot renew --dry-run
```

Después de que Certbot escriba los certificados, descomentar en
`/etc/nginx/sites-available/funcrees` las líneas:

```nginx
# ssl_certificate     /etc/letsencrypt/live/funcreescolombia.org/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/funcreescolombia.org/privkey.pem;
```

y ejecutar `sudo nginx -t && sudo systemctl reload nginx`.

---

## 9️⃣ Permisos y Seguridad

```bash
# Permisos de archivos
sudo chown -R www-data:www-data /var/www/funcrees
sudo chmod 600 /var/www/funcrees/backend/.env

# Firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## 🔟 Verificar el Deploy

```bash
# Health check del backend
curl https://funcreescolombia.org/api/health/
# Debe retornar: {"status":"ok"}

# SSR del frontend (debe devolver HTML con contenido, no un shell vacío)
curl -s https://funcreescolombia.org/ | grep -o "<title>[^<]*</title>"
# Debe retornar: <title>Fundación Funcrees Colombia | Crece Una Esperanza</title>

# Sitemap
curl -s https://funcreescolombia.org/sitemap.xml | head -5
```

Abrir en navegador:
- Sitio: `https://funcreescolombia.org`
- Admin: `https://funcreescolombia.org/admin/`

### Verificar el flujo de pagos (sandbox)

1. En `backend/.env`: `WOMPI_ENV=sandbox` + llaves sandbox de Wompi.
2. Donar desde `/donaciones` con una tarjeta de prueba de Wompi.
3. Verificar: la donación aparece en el admin (`/admin/donations/donation/`),
   llega el certificado PDF por correo y el webhook quedó registrado.

---

## 🔧 Comandos Útiles

```bash
# Reiniciar servicios
sudo systemctl restart funcrees funcrees-web

# Logs
sudo journalctl -u funcrees -f        # backend
sudo journalctl -u funcrees-web -f    # frontend
sudo tail -f /var/log/nginx/funcrees_error.log

# Actualizar código (después de git pull)
cd /var/www/funcrees/backend && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput

cd /var/www/funcrees/frontend
npm ci && npm run build

sudo systemctl restart funcrees funcrees-web
```

---

## 💾 Backup Automático (Base de Datos)

```bash
sudo nano /usr/local/bin/funcrees-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/funcrees"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
sudo -u postgres pg_dump funcrees_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
echo "[$(date)] Backup completado: db_$DATE.sql.gz" >> /var/log/funcrees/backup.log
```

```bash
sudo chmod +x /usr/local/bin/funcrees-backup.sh
sudo crontab -e
# Agregar: 0 2 * * * /usr/local/bin/funcrees-backup.sh
```

---

## 📧 Resumen Semanal por Correo

Todos los lunes a las 7:00 a.m. (hora Colombia) el sistema envía a la
directiva un correo con: total recaudado del mes (y variación vs. mes
anterior), apadrinamientos activos con su monto mensual comprometido,
mensajes sin leer, el gráfico mensual como imagen embebida y accesos al panel.

**⏳ Pagos por confirmar con Wompi (sección condicional):** si existen
donaciones `pendiente`/`procesando` con más de 1 hora de creadas, el correo
incluye una sección ámbar con cada caso (referencia, donante, monto, horas
esperando) y un enlace directo al listado filtrado del panel
(`/admin/donations/donation/?pendientes=si`), donde la acción "Verificar con
Wompi" confirma el pago. Usa exactamente los mismos datos que la alerta del
panel de administración; si no hay nada estancado, la sección no aparece.

**Configuración (una sola vez) en `backend/.env`:**

```bash
# Destinatarios del resumen (separados por coma). Vacío = desactivado.
DIGEST_TO=directiva@funcrees.org,contabilidad@funcrees.org
```

**Probar manualmente antes de programar el cron:**

```bash
cd /var/www/funcrees/backend && source venv/bin/activate
python manage.py send_weekly_digest --dry-run   # ver cifras en consola
python manage.py send_weekly_digest --to tu-correo@funcrees.org  # envío real de prueba
```

**Programar el envío (cron del sistema, usa la zona horaria del servidor):**

```bash
sudo crontab -e
# Lunes 12:00 UTC = 7:00 a.m. en Colombia (UTC-5, sin horario de verano)
0 12 * * 1 cd /var/www/funcrees/backend && venv/bin/python manage.py send_weekly_digest >> /var/log/funcrees/digest.log 2>&1
```

> 💡 Si el servidor usa otra zona horaria, ajusta la hora: el comando usa la
> configuración `TIME_ZONE` de Django (America/Bogota) para calcular las
> cifras del mes, así que solo importa la hora *del servidor* en el cron.

---

## 📊 Monitoreo y Log Rotation

```bash
# Log rotation
sudo nano /etc/logrotate.d/funcrees
```

```
/var/log/funcrees/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload funcrees > /dev/null 2>&1 || true
    endscript
}
```

### 🟢 Monitor de disponibilidad con alertas por correo

El comando `check_uptime` verifica cada 5 minutos que el backend (gunicorn +
Django + base de datos, vía `/api/health/`) y el frontend (SvelteKit :3000)
respondan, y avisa por correo al personal cuando algo se cae:

| Situación | Acción del monitor |
|---|---|
| Todo OK | Silencio (nunca hay correos "todo bien" en producción) |
| Servicio caído (2 fallos seguidos ≈ 10 min) | **Un correo** con todos los servicios afectados |
| Sigue caído | Recordatorio cada 2 horas |
| Se recupera | Correo de confirmación con la duración de la caída |

```bash
# Instalar el cron (junto al del resumen semanal):
sudo crontab -e
# Agregar:
*/5 * * * * cd /var/www/funcrees/backend && venv/bin/python manage.py check_uptime >> /var/log/funcrees/uptime.log 2>&1
```

Configuración en `backend/.env` (todas opcionales, ver `.env.example`):

```
UPTIME_ALERT_TO=directiva@funcrees.org,tecnico@funcrees.org   # vacío => usa DIGEST_TO
UPTIME_BACKEND_URL=http://127.0.0.1:8000/api/health/          # interno (rápido, sin DNS/SSL externos)
UPTIME_FRONTEND_URL=http://127.0.0.1:3000/                    # o https://funcreescolombia.org/ para probar también Nginx/SSL
UPTIME_FALLOS_PARA_ALERTA=2        # anti-ruido: ~10 min de caída real antes de avisar
UPTIME_REMINDER_HOURS=2            # recordatorio mientras siga caído
UPTIME_TIMEOUT=10                  # segundos de espera por respuesta
UPTIME_HEARTBEAT_URL=              # opcional, ver abajo
```

**Prueba después de instalar el cron:**

```bash
python manage.py check_uptime --dry-run        # verificación en consola, sin efectos
python manage.py check_uptime --force-email    # llega el correo "✅ todo funciona" (prueba de SMTP)
```

Si algo está caído, el correo incluye el error concreto y el comando de
reinicio (`systemctl status/restart funcrees funcrees-web`). El estado del
monitor vive en `backend/logs/uptime_state.json` (gitignored); bórralo para
reiniciar el histórico de alertas.

**Recomendado — heartbeat externo (cubre caída total del VPS):** si el
servidor entero se cae, ni el monitor ni el correo pueden ejecutarse. Crea un
check gratuito en [healthchecks.io](https://healthchecks.io), pega su URL de
ping en `UPTIME_HEARTBEAT_URL` y listo: el monitor solo hace ping cuando TODO
está bien, así que si el ping deja de llegar, el servicio externo alerta por
su cuenta (correo/Slack) aunque FUNCREES esté completamente fuera de línea.

---

## ⚠️ Solución de Problemas

| Problema | Solución |
|----------|----------|
| Error 502 Bad Gateway (sitio) | Verificar Node: `sudo systemctl status funcrees-web` |
| Error 502 Bad Gateway (API) | Verificar Gunicorn: `sudo systemctl status funcrees` |
| "Cannot find module build/index.js" | Ejecutar `npm run build` en `frontend/` |
| Donaciones fallan con 503 | Llaves de Wompi mal configuradas en `.env` (verificar `WOMPI_ENV`) |
| Certificados no llegan por email | Revisar `EMAIL_HOST_PASSWORD` (contraseña de aplicación Gmail) |
| CSRF Error | Verificar `CSRF_TRUSTED_ORIGINS` en `.env` |
| Páginas no cargan | `sudo nginx -t` y `sudo journalctl -u funcrees-web -n 50` |

---

## 📝 Notas Importantes para el Cliente

1. **NUNCA** subir el archivo `.env` a repositorios (contiene llaves de Wompi y encriptación)
2. **NUNCA** compartir la `SECRET_KEY` o `ENCRYPTION_KEY` — perder la Fernet key = perder los datos cifrados
3. **SIEMPRE** hacer backup antes de actualizar el código
4. Probar siempre primero en `WOMPI_ENV=sandbox` antes de producción
5. El admin de Django está en: `https://funcreescolombia.org/admin/`
6. El health check está en: `https://funcreescolombia.org/api/health/`
7. Los comprobantes de bonos/donaciones son reales: cada transacción queda registrada en Wompi y en el admin

---

**Versión del proyecto:** 2.0.0
**Última actualización:** Septiembre 2026
