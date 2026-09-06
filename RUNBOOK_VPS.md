# 🖨️ RUNBOOK VPS — Despliegue completo de FUNCREES Colombia

Documento único y ordenado para ejecutar la entrega en un VPS Ubuntu 22.04 / Debian 12.
Fusiona `DEPLOY.md` (comandos completos) y `CHECKLIST_ENTREGA.md` (verificaciones) en un
solo guion: imprímelo y ve marcando cada **☐** en orden. Cada fase indica de dónde viene
(`D§` = DEPLOY.md, `C§` = Checklist).

**Duración estimada:** 90–120 min · **Origen:** RUNBOOK generado sep 2026 (FUNCREES v2.0)
**Convenciones:** los bloques `bash` se pegan tal cual; `<ángulos>` = valor que debes
sustituir; cada fase termina en un **✔ checkpoint** — si falla, ve a 🧯 al final.

**Red de seguridad:** el restore de base de datos está en la sección 🔙 y el script de
backup se instala en la Fase 8. Ningún paso de este runbook es irreversible salvo
borrar datos a mano — ante la duda, respalda primero (Fase 8 se puede ejecutar antes).

---

## FASE 0 · En tu equipo, ANTES de tocar el VPS

☐ **Código completo en git.** El deploy clona el repositorio; el árbol debe estar
   committed y pushed (incluye monitor de disponibilidad y WebP):

```bash
git status --short        # debe salir vacío (o solo artefactos ignorados)
git log --oneline -1      # apunta este SHA: lo usarás en la Fase 2
git push
```

☐ **Credencial de Neon ya rotada** (C§0 — se consideró comprometida): nueva password de
   `neondb_owner` (o rol dedicado `funcrees_app`) desde el dashboard; nueva cadena con
   `?sslmode=require` a mano. NUNCA la pegues en chats.

☐ **Prueba local**: `python manage.py check` sin errores y `curl http://127.0.0.1:8000/api/health/`
   → `{"status":"ok"}` con la NUEVA credencial.

☐ **Decisión tomada (C§2):** la `ENCRYPTION_KEY` definitiva de la Fundación es la del
   `.env` local (sep 2026, ya validada) y va al gestor de contraseñas. Regla: **misma
   clave en local y VPS** mientras ambos compartan la BD.

---

## FASE 1 · Servidor base `D§1`

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib \
  nginx certbot python3-certbot-nginx git curl
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
sudo mkdir -p /var/log/funcrees /var/run/funcrees
sudo chown www-data:www-data /var/log/funcrees /var/run/funcrees
```

☐ **✔ Checkpoint:** `node -v` muestra v22.x · `nginx -v` responde.

---

## FASE 2 · Código y variables de entorno `D§2 + C§1`

```bash
sudo mkdir -p /var/www/funcrees && sudo chown $USER:$USER /var/www/funcrees
cd /var/www/funcrees
git clone https://github.com/<TU_USUARIO>/funcrees-colombia.git .
git checkout <SHA-apuntado-en-Fase-0>   # opcional: fija exactamente lo probado
```

☐ **Crear `backend/.env`** (partir de `.env.example`). Valores que BLOQUEAN si faltan ⚠️:

```bash
DEBUG=False                                          # ⚠️ activa HTTPS forzado
SECRET_KEY=<generar abajo>                           # ⚠️
ALLOWED_HOSTS=funcreescolombia.org,www.funcreescolombia.org   # ⚠️ sin esto: 400 en todo
DATABASE_URL=postgresql://<usuario>:<password-ROTADA>@ep-...-pooler...neon.tech/neondb?sslmode=require
CORS_ALLOWED_ORIGINS=https://funcreescolombia.org,https://www.funcreescolombia.org
FRONTEND_URL=https://funcreescolombia.org
DIGEST_TO=directiva@funcrees.org,contabilidad@funcrees.org
UPTIME_ALERT_TO=<mismo u otro correo de alertas>     # vacío = usa DIGEST_TO
UPTIME_HEARTBEAT_URL=                                # opcional (healthchecks.io), Fase 8
DEFAULT_FROM_EMAIL=contacto@funcreescolombia.org
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<correo-de-la-fundación>
EMAIL_HOST_PASSWORD=<contraseña-de-APLICACIÓN>       # Gmail: requiere 2FA
EMAIL_USE_TLS=True
WOMPI_ENV=production
WOMPI_PUBLIC_KEY=pub_prod_...
WOMPI_PRIVATE_KEY=prv_prod_...
WOMPI_INTEGRITY_SECRET=prod_integrity_...
ENCRYPTION_KEY=<la clave decidida en Fase 0>         # ⚠️ misma que local (comparten BD)
```

Generar claves nuevas (solo las que aún no tengas decididas):

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

```bash
chmod 600 backend/.env
```

☐ **✔ Checkpoint:** `grep -c '=' backend/.env` ≥ 15 · `chmod 600` aplicado · ningún
   valor real pegado en chat/correo.

---

## FASE 3 · Base de datos (elige UNA) `D§3 + C§0/C§2`

**Opción A — Neon (recomendada, cero migración):** no hay nada que instalar aquí; la
`DATABASE_URL` de la Fase 2 ya apunta a Neon con la credencial rotada. ☐

**Opción B — PostgreSQL local del VPS:**

```bash
sudo -u postgres psql
# CREATE USER funcrees_user WITH PASSWORD '<password-segura>';
# CREATE DATABASE funcrees_db OWNER funcrees_user;
# GRANT ALL PRIVILEGES ON DATABASE funcrees_db TO funcrees_user;
# \q
```

…y `DATABASE_URL` del `.env` apunta a `localhost:5432/funcrees_db`. Si migras datos,
hazlo con `pg_dump` desde Neon ANTES de la Fase 4 y recuerda: la clave que cifró los
datos debe ser la del VPS (C§2 tabla de opciones). ☐

---

## FASE 4 · Backend: instalar, migrar, estáticos `D§4 + C§5`

```bash
cd /var/www/funcrees/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
mkdir -p media
python manage.py createsuperuser
```

☐ **✔ Checkpoint 1:** `python manage.py check` sin errores y

```bash
python manage.py runserver 0.0.0.0:8080   # prueba temporal, Ctrl+C después
curl http://127.0.0.1:8080/api/health/    # → {"status":"ok"}
```

---

## FASE 5 · Frontend: build `D§5 + C§5`

```bash
cd /var/www/funcrees/frontend
npm ci && npm run build
```

☐ **✔ Checkpoint 2:** existe `frontend/build/index.js`.

---

## FASE 6 · Servicios systemd `D§6`

El repo trae `funcrees-web.service`; el unit del backend se crea a mano:

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

```bash
sudo cp /var/www/funcrees/funcrees-web.service /etc/systemd/system/
sudo chown -R www-data:www-data /var/www/funcrees
sudo systemctl daemon-reload
sudo systemctl enable --now funcrees funcrees-web
sudo systemctl status funcrees funcrees-web     # ambos active (running)
```

☐ **✔ Checkpoint 3 (aún sin dominio):**

```bash
curl http://127.0.0.1:8000/api/health/   # → {"status":"ok"}   (gunicorn+BD)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/   # → 200   (node SSR)
```

---

## FASE 7 · Nginx + SSL `D§7 + D§8`

**Requisito previo:** el DNS del dominio ya apunta a la IP de este VPS.

```bash
sudo cp /var/www/funcrees/deploy_nginx.conf /etc/nginx/sites-available/funcrees
sudo ln -sf /etc/nginx/sites-available/funcrees /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

sudo certbot --nginx -d funcreescolombia.org -d www.funcreescolombia.org
sudo certbot renew --dry-run
```

Cuando Certbot escriba los certificados, descomenta en
`/etc/nginx/sites-available/funcrees` las dos líneas `ssl_certificate …` y:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

> El conf incluye `location /media/` (imprescindible para las fotos del admin) y
> proxys a Node :3000 (`/`) y Gunicorn :8000 (`/api/`, `/admin/`, `/static/`).

☐ **✔ Checkpoint 4 (dominio real):**

```bash
curl https://funcreescolombia.org/api/health/                     # {"status":"ok"}
curl -s https://funcreescolombia.org/ | grep -o "<title>[^<]*</title>"   # título completo SSR
curl -s -o /dev/null -w "%{http_code}\n" http://funcreescolombia.org/    # 301 → https
curl -s https://funcreescolombia.org/sitemap.xml | grep -c numeros       # ≥ 1
```

---

## FASE 8 · Crons: resumen, monitor, backup `C§6 + D§💾 + D§📊`

☐ **Añadir al sistema el script de backup diario:**

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
```

> Con Neon (opción A) sustituye la línea `pg_dump` por:
> `pg_dump "$DATABASE_URL" | gzip > $BACKUP_DIR/db_$DATE.sql.gz` exportando la URL
> dentro del script (léela del .env; no la pegues en el crontab).

☐ **Logrotate** (contenido en `DEPLOY.md` §📊 → `/etc/logrotate.d/funcrees`). ☐

☐ **Programar los tres crons** (`sudo crontab -e`; 12:00 UTC = 7:00 a.m. Colombia):

```cron
0 12 * * 1  cd /var/www/funcrees/backend && venv/bin/python manage.py send_weekly_digest >> /var/log/funcrees/digest.log 2>&1
*/5 * * * * cd /var/www/funcrees/backend && venv/bin/python manage.py check_uptime >> /var/log/funcrees/uptime.log 2>&1
0 2 * * *   /usr/local/bin/funcrees-backup.sh
```

☐ **Probar ANTES de confiar en ellos:**

```bash
python manage.py send_weekly_digest --dry-run
python manage.py send_weekly_digest --to <tu-correo>     # llega HTML real con gráfico
python manage.py check_uptime --dry-run                  # ✅ Backend / ✅ Sitio web
python manage.py check_uptime --force-email --to <tu-correo>   # llega "✅ todo funciona"
```

☐ **Heartbeat externo (recomendado):** check gratuito en healthchecks.io → su URL de
   ping en `UPTIME_HEARTBEAT_URL` del `.env`. Cubre la caída TOTAL del VPS (cuando ni
   el monitor puede avisar). ☐

☐ **✔ Checkpoint 5:** los dos correos de prueba llegaron (revisar spam; si cae en spam,
   configurar SPF/DKIM antes de entregar) y `/var/backups/funcrees/` tiene un `.sql.gz`.

---

## FASE 9 · Verificación funcional `C§7 + C§8`

**Media + WebP (el flujo del personal):**

☐ Admin → Beneficiarios → edita uno → **sube una foto real grande (>800px)**.
☐ Se ve en el listado del admin y en `https://funcreescolombia.org/historias` desde `/media/...`.
☐ En `backend/media/...` aparecen junto al original `-200w.webp` y `-400w.webp`
   (y `-800w.webp` si la foto era grande); el API expone `foto_webp_srcset`.
☐ Repite con la imagen de un evento → se ve en `/eventos`.
☐ `sudo chown -R www-data:www-data /var/www/funcrees/backend/media` (sin esto, la
   siguiente subida falla con 500).

**Smoke público:**

☐ Las 8 páginas cargan con contenido SSR: `/`, `/quienes-somos`, `/proyectos`,
  `/historias`, `/donaciones`, `/eventos`, `/numeros`, `/contacto`.
☐ `curl -sI https://funcreescolombia.org/api/stats/ | grep -i cache-control`
  → `public, max-age=120`.

**Panel:**

☐ Login con el superusuario; panel "Resumen de la Fundación" con cifras y gráfico.
☐ Crear cuentas **staff individuales** para el personal (nadie comparte el superusuario).

**Pagos (pasada completa):**

☐ Donación sandbox → aprobada → `completado` en admin → **certificado PDF por correo** →
  `/numeros` y panel la reflejan en ≤ 2 min (cache de `/api/stats/`).
☐ Con llaves de producción ya puestas: una donación real de monto pequeño.
☐ **Limpieza pre-entrega:** borrar del admin las donaciones de prueba (sandbox/local);
  así `/numeros` arranca en cero real. Los datos de beneficiarios y eventos son reales.

☐ **✔ Checkpoint 6:** todo lo anterior marcado. El sitio está funcionalmente entregable.

---

## FASE 10 · Seguridad, simulacro y entrega `C§9 + C§🔟`

```bash
sudo ufw allow 'Nginx Full' && sudo ufw allow OpenSSH && sudo ufw enable
sudo chmod 600 /var/www/funcrees/backend/.env
git status --short    # sin .env ni secretos en el árbol
```

☐ Snapshots automáticos del VPS activados (panel Hostinger).
☐ **Simulacro del monitor (day-2):** `sudo systemctl restart funcrees-web` →
  sin correo en el 1.er fallo → 🔴 alerta al 2.º (~10 min) → reinicia de nuevo →
  correo ✅ de recuperación. Si no llega nada: `UPTIME_ALERT_TO` y
  `/var/log/funcrees/uptime.log`.
☐ Al día siguiente: `journalctl -u funcrees -n 100` sin errores recurrentes.

**Paquete de entrega (C§🔟):** credenciales al gestor de contraseñas (admin, Neon, Wompi,
SMTP, VPS+2FA, DNS, ENCRYPTION_KEY/SECRET_KEY) · sesión de capacitación (subir fotos,
crear eventos, revisar donaciones y panel, marcar mensajes leídos, exportar CSV) ·
entregar `DEPLOY.md` + este runbook firmado.

☐ **✔ Cierre:** sitio entregado.

---

## 🧯 Si algo falla — triage rápido

| Síntoma | Causa más probable | Primer diagnóstico |
|---|---|---|
| Todas las páginas → `400 DisallowedHost` | `ALLOWED_HOSTS` sin el dominio real (fallo #1) | `grep ALLOWED_HOSTS backend/.env` |
| 502 en el sitio | Node caído o build ausente | `systemctl status funcrees-web`; existe `build/index.js`? |
| 502 en `/api/*` o `/admin/` | Gunicorn caído | `systemctl status funcrees`; `journalctl -u funcrees -n 50` |
| Donaciones fallan con 503 | Llaves Wompi mal puestas | `grep WOMPI_ENV backend/.env` → `production` |
| Certificados no llegan | SMTP mal configurado | `EMAIL_HOST_PASSWORD` = contraseña de APLICACIÓN |
| Error CSRF en el admin | Orígenes de confianza | `CSRF_TRUSTED_ORIGINS`/`CORS_ALLOWED_ORIGINS` con `https://dominio` |
| Subida de foto → 500 | Permisos de `media/` | `chown -R www-data:www-data backend/media` |
| Foto no se ve en el sitio | Nginx sin bloque `/media/` | `grep -n "location /media/" /etc/nginx/sites-available/funcrees` |
| No llegan alertas del monitor | Sin destinatarios | `UPTIME_ALERT_TO`/`DIGEST_TO` y `/var/log/funcrees/uptime.log` |
| `manage.py` no arranca | `.env` incompleto | `python manage.py check` dice exactamente qué falta |

Logs maestros: `journalctl -u funcrees -f` (backend) · `journalctl -u funcrees-web -f`
(frontend) · `tail -f /var/log/nginx/funcrees_error.log`.

---

## 🔙 Rollback — revertir código y recuperar el sitio

**Código (volver al deploy anterior que funcionaba):**

```bash
cd /var/www/funcrees
git log --oneline -5                    # identifica el SHA bueno anterior
git checkout <SHA-bueno>                # o: git revert <SHA-malo> (mantiene historia)
cd backend && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput      # solo si el rollback lo requiere
python manage.py collectstatic --noinput
cd ../frontend && npm ci && npm run build
sudo systemctl restart funcrees funcrees-web
curl http://127.0.0.1:8000/api/health/ && curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/
```

**Base de datos (solo si un migrate dañó datos — operación excepcional):**

```bash
# Detener escritura mientras restauras:
sudo systemctl stop funcrees
# Opción B (PG local):
gunzip -c /var/backups/funcrees/db_<fecha>.sql.gz | sudo -u postgres psql funcrees_db
# Opción A (Neon): restaurar contra la cadena de conexión:
# gunzip -c db_<fecha>.sql.gz | pg_dump no — usar psql "$DATABASE_URL" < dump.sql
sudo systemctl start funcrees
python manage.py check && curl https://funcreescolombia.org/api/health/
```

> El restore reemplaza TODO el contenido de la BD por el del backup: cualquier donación
> o mensaje recibido DESPUÉS de ese backup se pierde — por eso el backup corre a diario
> y por eso se detiene el backend antes de restaurar.

**Regla de oro:** ante cualquier fallo durante el deploy, el sitio anterior se recupera
con `git checkout <SHA-anterior>` + rebuild + restart (2–3 min). La BD nunca se toca a
menos que el problema sea demostrablemente de datos.

---

**Runbook generado:** septiembre 2026 · FUNCREES v2.0 · Fuentes: `DEPLOY.md` + `CHECKLIST_ENTREGA.md`

| Fase | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|------|---|---|---|---|---|---|---|---|---|----|
| **Fecha/hora** | | | | | | | | | | |
| **Ejecutada por** | | | | | | | | | | |
