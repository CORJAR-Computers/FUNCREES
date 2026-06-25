# 🚀 Guía de Despliegue — FUNCREES Colombia en Hostinger VPS

> **Destino:** Hostinger Business VPS (Ubuntu 22.04 LTS)
> **Stack:** Django 5.1 + PostgreSQL 15 + Nginx + Gunicorn + Certbot (SSL)

---

## 📋 Prerrequisitos

- [ ] Hostinger Business VPS contratado (o similar)
- [ ] Dominio comprado (ej. `funcreescolombia.org`)
- [ ] Acceso SSH al servidor
- [ ] Claves de Wompi (producción)
- [ ] Clave de encriptación Fernet generada

---

## 1️⃣ Conectar al servidor

```bash
ssh root@IP_DEL_SERVIDOR
```

## 2️⃣ Instalar dependencias del sistema

```bash
apt update && apt upgrade -y
apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib \
               certbot python3-certbot-nginx git curl
```

## 3️⃣ Configurar PostgreSQL

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE funcrees_db;
CREATE USER funcrees_user WITH PASSWORD 'tu_password_segura';
ALTER ROLE funcrees_user SET client_encoding TO 'utf8';
ALTER ROLE funcrees_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE funcrees_user SET timezone TO 'America/Bogota';
GRANT ALL PRIVILEGES ON DATABASE funcrees_db TO funcrees_user;
\q
```

## 4️⃣ Clonar el proyecto

```bash
cd /var/www
git clone https://github.com/tu-usuario/funcrees.git
cd funcrees
```

## 5️⃣ Configurar variables de entorno

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Editar con los valores reales:

```env
DEBUG=False
SECRET_KEY=<generada con python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
ALLOWED_HOSTS=funcreescolombia.org,www.funcreescolombia.org
DATABASE_URL=postgresql://funcrees_user:tu_password_segura@localhost:5432/funcrees_db
CORS_ALLOWED_ORIGINS=https://funcreescolombia.org,https://www.funcreescolombia.org
FRONTEND_URL=https://funcreescolombia.org

# Email
DEFAULT_FROM_EMAIL=contacto@funcreescolombia.org
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app

# Wompi
WOMPI_ENV=production
WOMPI_PUBLIC_KEY=pub_prod_xxxx
WOMPI_PRIVATE_KEY=prv_prod_xxxx
WOMPI_INTEGRITY_SECRET=prod_integrity_xxxx

# Encriptación
ENCRYPTION_KEY=<generada con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
```

## 6️⃣ Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

## 7️⃣ Migraciones y archivos estáticos

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 8️⃣ Probar Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 core.wsgi:application
# Abre http://IP_DEL_SERVIDOR:8000/admin/ para probar
# Ctrl+C para detener
```

## 9️⃣ Configurar Gunicorn como servicio systemd

```bash
nano /etc/systemd/system/funcrees.service
```

Pegar:

```ini
[Unit]
Description=FUNCREES Gunicorn service
After=network.target postgresql.service

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/funcrees/backend
EnvironmentFile=/var/www/funcrees/backend/.env
ExecStart=/var/www/funcrees/venv/bin/gunicorn \
    --config gunicorn.conf.py \
    core.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
mkdir -p /var/log/funcrees /var/run/funcrees
systemctl daemon-reload
systemctl start funcrees
systemctl enable funcrees
systemctl status funcrees
```

## 🔟 Configurar Nginx como proxy inverso

```bash
nano /etc/nginx/sites-available/funcrees
```

Pegar:

```nginx
server {
    listen 80;
    server_name funcreescolombia.org www.funcreescolombia.org;

    # Frontend estático (index.html, styles.css, app.js, assets/)
    root /var/www/funcrees;
    index index.html;

    # Servir el frontend SPA
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API backend - proxy hacia Gunicorn
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Admin panel
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Archivos estáticos de Django (WhiteNoise)
    location /static/ {
        alias /var/www/funcrees/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Assets del frontend (imágenes)
    location /assets/ {
        alias /var/www/funcrees/assets/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Activar:

```bash
ln -s /etc/nginx/sites-available/funcrees /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

## 1️⃣1️⃣ SSL con Certbot (Let's Encrypt)

```bash
certbot --nginx -d funcreescolombia.org -d www.funcreescolombia.org

# Verificar renovación automática
certbot renew --dry-run
```

## 1️⃣2️⃣ Actualizar API_URL en el frontend

Editar `index.html` y cambiar `window.__FUNCREES_CONFIG.API_BASE`:

```javascript
window.__FUNCREES_CONFIG = {
  API_BASE: 'https://funcreescolombia.org/api'
};
```

## ✅ Verificación final

```bash
# Revisar que todo esté corriendo
systemctl status funcrees
systemctl status nginx
systemctl status postgresql

# Logs
tail -f /var/log/funcrees/error.log
tail -f /var/log/nginx/access.log

# Probar desde el navegador
# https://funcreescolombia.org
# https://funcreescolombia.org/api/beneficiaries/
# https://funcreescolombia.org/admin/
```

---

## 🔄 Actualizaciones futuras

```bash
cd /var/www/funcrees
git pull
source venv/bin/activate
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart funcrees
```

## 🆘 Comandos útiles

```bash
# Logs en tiempo real
journalctl -u funcrees -f

# Reiniciar servicios
systemctl restart funcrees
systemctl reload nginx

# Respaldar base de datos
pg_dump funcrees_db > backup_$(date +%Y%m%d).sql

# Restaurar base de datos
psql funcrees_db < backup.sql
```
