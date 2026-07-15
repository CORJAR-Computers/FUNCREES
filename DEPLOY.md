# 🚀 Guía de Deploy — FUNCREES Colombia

Guía paso a paso para desplegar el sitio web de la Fundación Funcrees Colombia en un servidor VPS (ej: Hostinger, DigitalOcean, AWS).

---

## 📋 Requisitos Previos

| Componente | Versión mínima |
|------------|---------------|
| Sistema operativo | Ubuntu 22.04 LTS / Debian 12 |
| Python | 3.10+ |
| PostgreSQL | 14+ |
| Nginx | 1.18+ |
| Node.js (solo para tests) | 18+ |

---

## 1️⃣ Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx git curl mailutils

# Crear directorios necesarios
sudo mkdir -p /var/log/funcrees
sudo mkdir -p /var/run/funcrees
sudo chown www-data:www-data /var/log/funcrees /var/run/funcrees
```

---

## 2️⃣ Clonar el Proyecto

```bash
# Crear directorio del proyecto
sudo mkdir -p /var/www/funcrees/frontend
sudo chown $USER:$USER /var/www/funcrees

# Clonar el repositorio
cd /var/www/funcrees
git clone https://github.com/TU_USUARIO/funcrees-colombia.git .

# Organizar archivos del frontend
sudo cp -r *.html *.css *.js assets/ /var/www/funcrees/frontend/
sudo chown -R www-data:www-data /var/www/funcrees/frontend

# Estructura del proyecto
# /var/www/funcrees/
# ├── frontend/           ← Archivos estáticos del sitio web
# │   ├── index.html
# │   ├── app.js
# │   ├── styles.css
# │   └── assets/
# └── backend/            ← Backend Django
```

---

## 3️⃣ Configurar Base de Datos PostgreSQL

```bash
# Entrar al usuario de PostgreSQL
sudo -u postgres psql

# Crear base de datos y usuario
CREATE USER funcrees_user WITH PASSWORD 'TU_PASSWORD_SEGURO';
CREATE DATABASE funcrees_db OWNER funcrees_user;
GRANT ALL PRIVILEGES ON DATABASE funcrees_db TO funcrees_user;
\q
```

---

## 4️⃣ Configurar Backend (Django)

```bash
# Navegar al directorio backend
cd /var/www/funcrees/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus valores reales
```

### Variables de Entorno Requeridas (.env)

```bash
# Django
DEBUG=False
SECRET_KEY=tu-clave-secreta-generada
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Base de datos
DATABASE_URL=postgresql://funcrees_user:tu_password@localhost:5432/funcrees_db

# CORS
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com

# Frontend
FRONTEND_URL=https://tudominio.com

# Email
DEFAULT_FROM_EMAIL=contacto@tudominio.com
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

# ENCRYPTION_KEY para datos sensibles
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Ejecutar Migraciones y Crear Superusuario

```bash
cd /var/www/funcrees/backend
source venv/bin/activate

# Aplicar migraciones
python manage.py migrate --noinput

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario para el admin
python manage.py createsuperuser
```

---

## 5️⃣ Configurar Gunicorn (Servidor de Producción)

Crear servicio systemd:

```bash
sudo nano /etc/systemd/system/funcrees.service
```

Contenido del servicio:

```ini
[Unit]
Description=FUNCREES Backend (Django + Gunicorn)
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/funcrees/backend
ExecStart=/var/www/funcrees/backend/venv/bin/gunicorn \
          --config gunicorn.conf.py \
          core.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Iniciar y habilitar el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl start funcrees
sudo systemctl enable funcrees

# Verificar estado
sudo systemctl status funcrees
```

---

## 6️⃣ Configurar Nginx (Frontend + Proxy)

```bash
sudo nano /etc/nginx/sites-available/funcrees
```

Usar el archivo `deploy_nginx.conf` incluido en el proyecto, o crear manualmente:

```nginx
# Frontend (SPA)
location / {
    root /var/www/funcrees/frontend;
    index index.html;
    try_files $uri $uri/ /index.html;
}

# Backend API
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Admin Django
location /admin/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Archivos estáticos
location /static/ {
    alias /var/www/funcrees/backend/staticfiles/;
    expires 30d;
}
```

Activar sitio:

```bash
sudo ln -s /etc/nginx/sites-available/funcrees /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 7️⃣ Configurar SSL con Certbot

```bash
# Instalar certificado SSL gratuito
sudo certbot --nginx -d tudominio.com -d www.tudominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## 8️⃣ Permisos y Seguridad

```bash
# Permisos de archivos
sudo chown -R www-data:www-data /var/www/funcrees
sudo chmod -R 755 /var/www/funcrees

# Proteger archivos sensibles
sudo chmod 600 /var/www/funcrees/backend/.env
sudo chmod 600 /var/www/funcrees/backend/core/settings.py

# Firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## 9️⃣ Verificar el Deploy

### Health Check

```bash
curl https://tudominio.com/api/health/
# Debe retornar: {"status": "ok"}
```

### Verificar Frontend

Abrir en navegador: `https://tudominio.com`

### Verificar Admin

Abrir en navegador: `https://tudominio.com/admin/`

---

## 🔧 Comandos Útiles

```bash
# Reiniciar backend
sudo systemctl restart funcrees

# Ver logs de Gunicorn
sudo journalctl -u funcrees -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/funcrees_access.log

# Actualizar código (después de git pull)
cd /var/www/funcrees/backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart funcrees
```

---

## 🔐 Validación de Variables de Entorno

Antes de iniciar el servidor, ejecutar este script para verificar que todas las variables críticas estén configuradas:

```bash
cd /var/www/funcrees/backend
source venv/bin/activate

# Script de validación (usa django-environ que ya está en requirements.txt)
python3 -c "
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Cargar variables del .env usando django-environ
import environ
env = environ.Env()
environ.Env.read_env(os.path.join(os.getcwd(), '.env'))

required = ['SECRET_KEY', 'DATABASE_URL', 'ALLOWED_HOSTS', 'WOMPI_PUBLIC_KEY', 'ENCRYPTION_KEY']
missing = [v for v in required if not env.str(v, default=None)]

if missing:
    print('❌ Faltan variables: ' + ', '.join(missing))
    sys.exit(1)
else:
    print('✅ Todas las variables de entorno están configuradas')
"
```

---

## 💾 Configurar Backup Automático

### Backup de Base de Datos (diario)

```bash
# Crear script de backup
sudo nano /usr/local/bin/funcrees-backup.sh
```

Contenido:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/funcrees"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup de PostgreSQL
sudo -u postgres pg_dump funcrees_db > $BACKUP_DIR/db_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/db_$DATE.sql

# Eliminar backups mayores a 30 días
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "[$(date)] Backup completado: db_$DATE.sql.gz" >> /var/log/funcrees/backup.log
```

```bash
# Hacer ejecutable
sudo chmod +x /usr/local/bin/funcrees-backup.sh

# Agregar a cron (ejecutar diario a las 2 AM)
sudo crontab -e
# Agregar: 0 2 * * * /usr/local/bin/funcrees-backup.sh
```

---

## 📊 Configurar Log Rotation

```bash
sudo nano /etc/logrotate.d/funcrees
```

Contenido:

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

---

## 📡 Configurar Monitoreo de Health Check

```bash
# Agregar cron job para monitoreo
sudo crontab -e
```

Agregar línea:

```
# Verificar salud de FUNCREES cada 5 minutos
*/5 * * * * curl -sf https://tudominio.com/api/health/ | grep -q '"status":"ok"' || echo "$(date): FUNCREES health check failed" >> /var/log/funcrees/monitor.log
```

---

## 🔄 Renovación Automática de SSL

Certbot instala un cron job automáticamente, pero verificar:

```bash
# Verificar cron de certbot
sudo systemctl list-timers | grep certbot

# Probar renovación manual
sudo certbot renew --dry-run
```

Si no existe, agregar manualmente:

```bash
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
```

---

## ⚠️ Solución de Problemas

| Problema | Solución |
|----------|----------|
| Error 502 Bad Gateway | Verificar que Gunicorn esté corriendo: `sudo systemctl status funcrees` |
| Error de BD | Verificar que PostgreSQL esté activo: `sudo systemctl status postgresql` |
| CSRF Error | Verificar `CSRF_TRUSTED_ORIGINS` en `.env` |
| CORS Error | Verificar `CORS_ALLOWED_ORIGINS` en `.env` |
| Páginas no cargan | Verificar configuración de Nginx: `sudo nginx -t` |

---

## 📁 Estructura Final del Servidor

```
/var/www/funcrees/
├── frontend/                    ← Archivos estáticos (Nginx sirve desde aquí)
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── themes.css
│   ├── responsive.css
│   ├── base.css
│   ├── components.css
│   └── assets/
│       ├── Logo.png
│       └── Foto Fundación.png
└── backend/                     ← Aplicación Django
    ├── manage.py
    ├── requirements.txt
    ├── .env                     ← Variables de entorno (NO subir a git)
    ├── gunicorn.conf.py
    ├── core/
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── beneficiaries/
    ├── donations/
    ├── events/
    ├── contact/
    ├── staticfiles/             ← Archivos estáticos de Django
    └── templates/
```

---

## 📝 Notas Importantes para el Cliente

1. **NUNCA** subir el archivo `.env` a repositorios públicos
2. **NUNCA** compartir la `SECRET_KEY` o `ENCRYPTION_KEY`
3. **SIEMPRE** usar HTTPS en producción
4. **SIEMPRE** hacer backup antes de actualizar el código
5. El admin de Django está en: `https://tudominio.com/admin/`
6. El health check está en: `https://tudominio.com/api/health/`

---

---

**Versión del proyecto:** 1.0.0  
**Última actualización:** Julio 2026
