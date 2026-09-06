# 📦 PAQUETE DE ENTREGA — FUNCREES Colombia · Sitio Web v2.0

**Documento combinado para imprimir y firmar.** Reúne los cuatro documentos oficiales
de la entrega en el orden de uso. Cada parte es idéntica a su archivo fuente en el
repositorio (si un fuente cambia, se regenera este paquete).

| Identificación | |
|---|---|
| Proyecto | Sitio web FUNCREES Colombia — Fundación Crece Una Esperanza Social |
| Versión | v2.0.0 (SvelteKit SSR + Django REST Framework) |
| Fecha de entrega | ______________________ |
| Entrega (responsable técnico) | ______________________ |
| Recibe (representante FUNCREES) | ______________________ |
| Repositorio | `CORJAR-Computers/FUNCREES` · commit entregado: ____________ |

**Índice**

| Parte | Documento | Uso |
|---|---|---|
| 1 | RUNBOOK VPS — Despliegue completo | Día del despliegue (ejecución + checkpoints) |
| 2 | Plan de Rollback | Si algo falla antes, durante o después |
| 3 | Guía rápida del panel (personal) | Entregar impresa a cada participante |
| 4 | Agenda de capacitación | Sesión de 90 min con el personal |
| ✍️ | Acta de entrega y firmas | Al finalizar todo |

---
---

# PARTE 1 · RUNBOOK VPS — Despliegue completo de FUNCREES Colombia

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
# Los ajustes finos del monitor (umbrales, timeout, URLs a verificar) son
# opcionales y tienen valores por defecto sensatos: ver backend/.env.example.
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

> 📄 Plan completo en la **PARTE 2** de este paquete. Aquí va el resumen operativo:

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

### Registro de ejecución del despliegue

| Fase | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|------|---|---|---|---|---|---|---|---|---|----|
| **Fecha/hora** | | | | | | | | | | |
| **Ejecutada por** | | | | | | | | | | |
| **Checkpoint OK** | | | | | | | | | | |

---
---

# PARTE 2 · Plan de Rollback — FUNCREES Colombia

Documento de recuperación para el día del despliegue y para operación normal.
**Audiencia:** la persona técnica que administra el VPS (puede ser el personal de la
Fundación siguiendo las instrucciones al pie de la letra).

**Filosofía en una línea:** el **código** se revierte en minutos y sin riesgo; la
**base de datos NUNCA se toca** salvo que el problema sea demostrablemente de datos.
El orden de lectura de este plan es: diagnosticar → decidir → ejecutar → verificar.

---

## 🚦 Regla de oro (léela primero)

1. **Ante la duda, el sitio anterior se recupera así** (2–3 minutos):

   ```bash
   cd /var/www/funcrees
   git log --oneline -5                  # 1) identifica el SHA del commit BUENO anterior
   git checkout <SHA-bueno>              # 2) vuelve al código que funcionaba
   cd backend && source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate --noinput
   python manage.py collectstatic --noinput
   cd ../frontend && npm ci && npm run build
   sudo systemctl restart funcrees funcrees-web
   curl http://127.0.0.1:8000/api/health/ && curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/
   ```

   Si ambos comandos responden bien (el `curl` muestra `{"status":"ok"}` y `200`),
   el sitio está recuperado. Termina aquí en el 95% de los casos.

2. **La base de datos no se restaura** salvo que hayas confirmado pérdida o
   corrupción de datos. Restaurar reemplaza TODO el contenido por el del backup:
   cualquier donación o mensaje recibido **después** de ese backup se pierde.

3. **Nunca edites a mano** el `.env` de producción durante un incidente sin anotar
   qué cambiaste: la mitad de los "incidentes" son un valor mal escrito.

---

## 🧭 Paso 1 — Diagnosticar: ¿qué tipo de fallo es?

| Síntoma | Tipo | Ir a |
|---|---|---|
| Página en blanco, 502, o el sitio no abre | **Servicio** | 2A |
| `400 DisallowedHost` | **Configuración** | 2B |
| Una página falla pero el resto funciona | **Código** | 2C |
| Donaciones rechazadas / 503 en el pago | **Configuración** | 2B |
| No llegan correos (certificados, resumen, alertas) | **Configuración** | 2B |
| Datos que no cuadran (donación desaparecida, cifras imposibles) | **Datos** | 2D |
| El propio servidor no responde por SSH | **Infraestructura** | 2E |

**Comandos de diagnóstico** (corre estos tres antes de decidir cualquier cosa):

```bash
sudo systemctl status funcrees funcrees-web      # ¿están "active (running)"?
sudo journalctl -u funcrees -n 50 --no-pager     # últimas 50 líneas del log del backend
sudo tail -n 30 /var/log/nginx/funcrees_error.log
```

> Consejo: copia/pega esas salidas en tu nota de incidente ANTES de tocar nada.
> Si pides ayuda, esa información es lo primero que te van a pedir.

---

## 🛠️ Paso 2 — Solución por tipo de fallo

### 2A · Servicio caído (502 / sitio no abre)

```bash
sudo systemctl restart funcrees funcrees-web
sleep 3
sudo systemctl status funcrees funcrees-web      # ¿ambos active (running)?
```

- **Node (funcrees-web) no arranca** → falta el build: `cd /var/www/funcrees/frontend && npm ci && npm run build`.
- **Gunicorn (funcrees) no arranca** → mira el log del `journalctl`: casi siempre es
  un error en el `.env` (variable faltante) o en la base de datos. Corre
  `python manage.py check` que te dirá exactamente qué falta.

### 2B · Configuración (400 DisallowedHost, pagos 503, correos que no salen)

No hay que revertir nada: se corrige el valor y se reinicia.

```bash
nano /var/www/funcrees/backend/.env              # corrige SOLO la variable culpable
sudo systemctl restart funcrees
```

| Variable | Síntoma cuando está mal |
|---|---|
| `ALLOWED_HOSTS` | `400 DisallowedHost` en todas las páginas |
| `WOMPI_ENV` / llaves Wompi | El pago se rechaza o apunta a sandbox |
| `EMAIL_HOST_PASSWORD` | No salen correos (debe ser contraseña de APLICACIÓN) |
| `CORS_ALLOWED_ORIGINS` | Error CSRF en el panel |
| `ENCRYPTION_KEY` | El modelo devuelve `None` en documentos/teléfonos (ver C§2) |

Después de corregir: `curl https://funcreescolombia.org/api/health/` → `{"status":"ok"}`.

### 2C · Código: una actualización rompió el sitio

**Escenario 1 — recién desplegaste un cambio nuevo.** Vuelve al commit anterior
(el bloque de la 🚦 Regla de oro). Apunta en tu nota: SHA nuevo (malo), SHA al que
volviste (bueno), hora.

**Escenario 2 — el deploy del día 1 mismo está fallando** (sucedió algo a mitad del
runbook). Sigue el **RUNBOOK (PARTE 1)** desde la fase donde se detuvo; cada checkpoint
te dice qué debe funcionar antes de continuar. Si un paso no pasa su checkpoint, ese
paso es el problema — no avances "a ver si funciona".

**Escenario 3 — solo una página específica falla.** Revisa el último commit que tocó
esa zona (`git log --oneline -3`) y decide: revertir todo (Regla de oro) o esperar un
arreglo. Con público en el sitio, revertir siempre gana: primero estabilidad, luego
corrección.

**Después de cualquier revert:** borra la caché del navegador o prueba en incógnito
para confirmar que lo que ves es el código revertido y no una página guardada.

### 2D · Datos: restaurar la base de datos (solo con pérdida confirmada)

**Solo si el Paso 1 confirmó corrupción o pérdida de datos.** Son 15 minutos y el
sitio queda detenido mientras corre.

```bash
# 1) Mira qué backups tienes (el cron diario deja 30 días):
ls -lh /var/backups/funcrees/

# 2) Detén el backend para que nadie escriba mientras restauras:
sudo systemctl stop funcrees

# 3) Guarda el estado actual por si acaso (¡no lo saltes!):
sudo -u postgres pg_dump funcrees_db | gzip > /var/backups/funcrees/PRE_RESTAURE_$(date +%Y%m%d_%H%M%S).sql.gz

# 4) Restaura el backup elegido (sustituye la fecha):
gunzip -c /var/backups/funcrees/db_<fecha>.sql.gz | sudo -u postgres psql funcrees_db

# 5) Levanta y verifica:
sudo systemctl start funcrees
python manage.py check
curl https://funcreescolombia.org/api/health/          # {"status":"ok"}
curl -s https://funcreescolombia.org/api/stats/        # cifras coherentes con el backup
```

**Con Neon (opción A)**, cambia los pasos 3–4 por:

```bash
set -a; source /var/www/funcrees/backend/.env; set +a   # carga DATABASE_URL sin imprimirla
pg_dump "$DATABASE_URL" | gzip > /var/backups/funcrees/PRE_RESTAURE_$(date +%Y%m%d_%H%M%S).sql.gz
gunzip -c /var/backups/funcrees/db_<fecha>.sql.gz | psql "$DATABASE_URL"
```

**Regla de la clave de cifrado:** si el backup trae donaciones antiguas, la
`ENCRYPTION_KEY` del `.env` debe ser la MISMA con la que se cifraron. Si tras restaurar
los documentos/teléfonos aparecen vacíos en el admin, la clave está desalineada —
**no intentes adivinar claves**: repón la correcta en el `.env`, reinicia, verifica.

**Después de un restore, siempre:** avisa a la directiva qué ventana de datos se
perdió (desde la hora del backup hasta ahora) y revisa juntos si hay donaciones que
re-ingresar (Wompi conserva el historial de transacciones; el webhook puede volver a
confirmarlas o se usa la acción "Verificar con Wompi" del panel).

### 2E · Infraestructura: el servidor entero no responde

- **No hay SSH ni panel** → soporte del proveedor (Hostinger) con el ticket; mientras,
  el monitor interno no puede avisar: es exactamente para esto el heartbeat externo
  (`UPTIME_HEARTBEAT_URL` en healthchecks.io), que alerta por su cuenta.
- **SSH responde pero el sitio no** → vuelve al Paso 1: casi siempre es 2A o 2B.
- **Disco lleno** (síntoma clásico: servicios que mueren sin explicación):

  ```bash
  df -h /                                    # si / está al 100%…
  sudo journalctl --vacuum-size=200M         # …libera logs viejos
  sudo find /var/backups/funcrees -name "*.gz" -mtime +30 -delete
  sudo systemctl restart funcrees funcrees-web
  ```

---

## 📋 Paso 3 — Cerrar el incidente

- [ ] `curl https://funcreescolombia.org/api/health/` → `{"status":"ok"}`
- [ ] Las 8 páginas abren con contenido (lista en `CHECKLIST_ENTREGA.md` §8).
- [ ] Una donación de prueba sandbox se completa de punta a punta (si tocaste pagos).
- [ ] Nota de incidente guardada: hora, síntoma, diagnóstico, SHA/config de vuelta,
      quién ejecutó y qué falta (tareas pendientes del arreglo definitivo).
- [ ] Si el rollback fue por código: el arreglo correcto se hace **después, con
      calma**, se prueba localmente (suite: `python manage.py test`) y se vuelve a
      desplegar siguiendo el runbook — nunca se "parchea" en caliente sobre producción.
- [ ] Si hubo restore de BD: aviso a la directiva sobre la ventana de datos perdida.

---
---

# PARTE 3 · Guía rápida del panel — Personal FUNCREES

**Tu panel:** `https://funcreescolombia.org/admin/` · **Tu usuario:** el que te asignaron
(cada persona la suya — **nunca compartas tu contraseña**).

Esta guía cabe en una hoja. Explica lo que el personal hace a diario.

---

## ✅ Tu rutina diaria (5–10 minutos)

| # | Qué hacer | Dónde |
|---|---|---|
| 1 | **Abre el "Resumen de la Fundación"** (es lo primero que ves al entrar): recaudado del mes, gráfico de 6 meses, mensajes nuevos y pagos pendientes. | Inicio del panel |
| 2 | **Revisa "⏳ Pagos por confirmar con Wompi"** si aparece: son pagos con más de 1 hora sin confirmar. Selecciona cada uno y usa la acción **"🔄 Verificar con Wompi"** para consultar el estado real. Si dejó teléfono, escríbele por el botón verde de **WhatsApp**. | Sección ámbar del inicio o Donaciones |
| 3 | **Lee los mensajes nuevos** (los que muestran "✉ nuevo"): contéstalos por correo y márcalos con las acciones **"Marcar como leído"** y **"Marcar como respondido"**. | Mensajes de Contacto |
| 4 | **Revisa el correo del lunes** (7:00 a.m.): trae las cifras de la semana, el gráfico y los pagos pendientes. Es el mismo dato del panel — nunca hay que "cuadrar" a mano. | Correo de la directiva |

> 💡 **El panel y la página pública "Nuestros Números"** (`/numeros`) se actualizan solos
> con cada pago confirmado por Wompi (puede tardar hasta 2 minutos en reflejarse).

---

## 📸 Subir fotos (beneficiarios y eventos)

1. Entra a **Beneficiarios** (o **Eventos**) → clic sobre el nombre → baja a
   **"Foto (subir archivo)"** → **Elige un archivo** → guarda.
2. **No necesitas editar la foto:** el sistema la reduce y crea copias ligeras (WebP)
   para que la página cargue rápido. Solo evita archivos de más de ~10 MB.
3. **Verifica:** la foto se ve en la lista del panel y en el sitio
   (`/historias` o `/eventos`) tras recargar la página.
4. Para **ocultar** a alguien sin borrarlo: desmarca **Activo** y guarda.

**Eventos — dos reglas de oro:** el **ID** se escribe en minúsculas y sin espacios
(ej. `bingo-2026`) y **no se cambia después**. La **fecha** se deja vacía solo para
campañas permanentes (ej. recolecta de pañales).

---

## 💳 Donaciones y apadrinamientos

- Cada pago confirmado queda registrado con su certificado PDF enviado al donante.
- **Exportar a Excel:** Donaciones → filtra o busca → selecciona las filas →
  acción **"Exportar seleccionadas a CSV (Excel)"**.
- Los **documentos y teléfonos de donantes están cifrados** (Ley 1581). Se ven solo
  dentro del panel — no los copies a WhatsApp ni a correos personales.

---

## 🚨 Si algo anda mal

| Situación | Qué hacer |
|---|---|
| Una foto no aparece en el sitio | Recarga con Ctrl+F5; si sigue, espera 2 minutos y reintenta |
| Un pago no aparece como confirmado | Usa "🔄 Verificar con Wompi"; si sigue pendiente más de 1 día, reporta |
| No puedes entrar (contraseña) | Pide al administrador que te la restablezca — no insistas más de 3 veces |
| El sitio no abre para nadie | Llama al contacto técnico: el sistema avisa solo, pero confírmalo |

---

## 🔒 Tres reglas de seguridad

1. **Tu contraseña es personal**: no la compartas ni la anotes en el escritorio.
2. **Cierra sesión** al terminar (esquina inferior del menú del panel).
3. Si ves algo raro (donaciones que no reconoces, mensajes borrados), **repórtalo el
   mismo día** — no lo corrijas por tu cuenta.

---
---

# PARTE 4 · Agenda de Capacitación — Entrega del sitio

Sesión presencial de **90 minutos** para el personal que administrará el panel.
Materiales: un computador por participante (o proyector + 1 equipo), esta agenda,
la **Guía rápida (PARTE 3)** impresa por participante y conexión a internet.

**Objetivo:** que cada participante termine la sesión habiendo hecho **con sus propias
manos** cada tarea de su rutina diaria, y sepa a quién llamar cuando algo falle.

**Antes de empezar (organizador):**
- [ ] Cuentas staff individuales creadas (nunca compartir el superusuario) y probadas.
- [ ] Datos reales cargados: beneficiarios, eventos y mensajes de ejemplo para practicar.
- [ ] Proyector con el panel abierto en `https://funcreescolombia.org/admin/`.

---

## Bloque 1 · Bienvenida y reglas (10 min)

- Qué es el panel y por qué se cambió al sistema nuevo (1 diapositiva o palabra hablada).
- **Reglas de seguridad** de la guía (contraseñas personales, cerrar sesión, reportar).
- Entrega de usuarios y primer ingreso: **cada participante entra a su cuenta ahora**.

> ✅ Resultado del bloque: todos dentro del panel con su usuario propio.

## Bloque 2 · El Resumen de la Fundación (15 min)

- Recorrido de la pantalla de inicio: recaudado del mes, **gráfico de 6 meses**,
  mensajes nuevos, y la alerta ámbar **"⏳ Pagos por confirmar con Wompi"**.
- Cómo se lee el gráfico (barras = recaudado por mes) y de dónde salen las cifras.
- Explicar la regla de oro: **el panel y la página pública "Nuestros Números" dicen
  siempre la misma verdad** — no se cuadran a mano, se actualizan solos (≤ 2 min).

> ✅ Resultado del bloque: cada participante explica en voz alta qué ve en su inicio.

## Bloque 3 · Donaciones: revisar, verificar, exportar (20 min)

1. Entrar a **Donaciones** y usar el buscador y los filtros (estado, mes).
2. **Práctica con un pago pendiente real o de prueba:** seleccionarlo → acción
   **"🔄 Verificar con Wompi"** → leer el mensaje de resultado.
3. **Botón de WhatsApp** en el panel de pagos por confirmar: qué mensaje envía y
   cuándo usarlo (solo si el donante dejó teléfono).
4. **Exportar a Excel:** filtrar un mes → seleccionar filas →
   **"Exportar seleccionadas a CSV (Excel)"** → abrir el archivo descargado.
5. Abrir una donación completada y mostrar el **certificado PDF** que recibió el donante.

> ✅ Resultado del bloque: cada participante verifica un pago y exporta un CSV.

## Bloque 4 · Mensajes de contacto (10 min)

- Bandeja de **Mensajes de Contacto**: qué significa "✉ nuevo", "✓ leído", "✓ respondido".
- **Práctica:** leer un mensaje, contestarlo por correo, y marcarlo con
  **"Marcar como leído"** y **"Marcar como respondido"**.
- Relación con el correo del lunes: los mensajes sin leer aparecen con etiqueta
  **NUEVO** en el resumen semanal de la directiva.

> ✅ Resultado del bloque: ningún mensaje queda "sin leer" al final del día.

## Bloque 5 · Beneficiarios y fotos (20 min)

1. Recorrer **Beneficiarios**: búsqueda por nombre/ciudad, filtro "apadrinado".
2. **Práctica principal — subir una foto:** editar un beneficiario →
   **"Foto (subir archivo)"** → elegir una foto grande del escritorio → guardar →
   verla en el panel y en **`/historias`** (recargar con Ctrl+F5).
3. Explicar qué hizo el sistema: redujo la foto y creó copias ligeras (WebP) —
   por eso no hay que editar fotos antes de subirlas.
4. **Ocultar sin borrar:** desmarcar **Activo** → comprobar que desapareció del sitio
   → volver a activarlo.
5. **Eventos:** crear un evento de práctica siguiendo las dos reglas de oro
   (ID en minúsculas y sin espacios, no se cambia después; fecha vacía = campaña
   permanente). Revisarlo en `/eventos`. *(Si hay boletas activas, mostrar el
   buscador de boletas por código de verificación.)*

> ✅ Resultado del bloque: cada participante sube una foto y la ve en el sitio.

## Bloque 6 · El correo del lunes y las alertas (10 min)

- Mostrar un **correo real del resumen semanal** (enviar uno de práctica con
  `--to` antes de la sesión): cifras, gráfico embebido, sección de pagos pendientes,
  enlace "Ver cifras en vivo en el panel".
- Explicar las **alertas automáticas**: si el sitio se cae, el sistema avisa por
  correo a la dirección de alertas. Quién recibe esas alertas y qué hacer al
  recibirlas (llamar al contacto técnico; no intentar arreglos por su cuenta).
- Repasar la sección **"🚨 Si algo anda mal"** de la guía: los 4 casos más comunes.

> ✅ Resultado del bloque: los participantes saben qué correos esperan y a quién llamar.

## Bloque 7 · Práctica libre y cierre (5–15 min)

- **Ejercicio integrador:** cada participante hace su rutina completa del día
  (abrir resumen → revisar pagos → leer mensajes → responder/marcar) sin ayuda,
  usando solo la guía impresa.
- **Cierre:** entrega del paquete (guía impresa, contactos de soporte), recordatorio
  de las 3 reglas de seguridad y espacio de preguntas.
- **Firma de la lista de asistencia** (abajo, junto al acta de entrega).

---

## ✅ Checklist del organizador después de la sesión

- [ ] Todos los participantes entraron con su cuenta propia y practicaron cada tarea.
- [ ] Limpieza de los **datos de práctica** (evento/beneficiario de prueba): borrarlos
      o marcarlos inactivos para que el sitio quede limpio.
- [ ] El correo semanal de prueba quedó desactivado (si se usó `--to` temporal).
- [ ] Guías impresas entregadas; archivo digital en el gestor de contraseñas/documentos.
- [ ] Lista de asistencia firmada archivada con el acta de entrega.
- [ ] Contacto técnico confirmado y probado (un mensaje de prueba recibido ese día).

---

### 📝 Lista de asistencia — sesión de capacitación

| # | Nombre completo | Rol en la Fundación | Cuenta del panel | Firma |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |

Fecha de la sesión: ____________ · Quien capacita: ____________________ Firma: ____________

---
---

# ✍️ ACTA DE ENTREGA — Sitio Web FUNCREES Colombia v2.0

Quien suscribe, **______________________________**, en calidad de **responsable técnico**,
hace entrega del sitio web de la Fundación Crece Una Esperanza Social (FUNCREES) Colombia
(`https://funcreescolombia.org`), versión **2.0**, incluyendo:

1. Despliegue completado según el **RUNBOOK (Parte 1)**, con todos los checkpoints ✔.
2. Base de datos en producción con la credencial de Neon **rotada** y las cifras
   públicas en cero real (sin datos de prueba).
3. Automatizaciones activas: certificados de donación por correo, resumen semanal
   (lunes 7:00 a.m. Colombia), monitor de disponibilidad con alertas y backup diario.
4. Sesión de capacitación realizada según la **Agenda (Parte 4)**, con lista de
   asistencia firmada, y **Guía del panel (Parte 3)** entregada a cada participante.
5. Plan de recuperación (**Parte 2**) entregado y explicado.
6. Credenciales transferidas al gestor de contraseñas de la Fundación (panel admin,
   Neon, Wompi, SMTP, VPS, DNS, claves SECRET_KEY y ENCRYPTION_KEY).

**Observaciones de la entrega:**

________________________________________________________________________

________________________________________________________________________

| | Entrega (responsable técnico) | Recibe (representante FUNCREES) |
|---|---|---|
| **Nombre** | | |
| **Documento** | | |
| **Firma** | | |
| **Fecha** | | |

---

*Paquete de entrega generado: septiembre 2026 · FUNCREES v2.0 · Fuentes: `RUNBOOK_VPS.md`,
`PLAN_ROLLBACK.md`, `GUIA_PERSONAL_PANEL.md`, `AGENDA_CAPACITACION.md` (regenerar el
paquete si un fuente cambia).*
