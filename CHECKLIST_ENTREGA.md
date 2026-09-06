# 📦 Checklist de Entrega — FUNCREES Colombia

Guía de verificación **previa a la entrega** del sitio. Complementa (no reemplaza)
`DEPLOY.md`, que contiene el despliegue completo paso a paso.

> Marca cada casilla al completarla. Los pasos están en orden: los primeros
> bloquean a los demás.

---

## 0️⃣ Rotar la credencial de Neon — ANTES DE NADA

La cadena de conexión de Neon (que incluye la contraseña) fue compartida en
conversaciones de desarrollo. **Esa credencial debe considerarse comprometida.**

- [ ] Entrar al dashboard de Neon → proyecto `neondb` → **Reset password** del rol `neondb_owner`.
- [ ] Copiar la **nueva** cadena de conexión (con `?sslmode=require`).
- [ ] Actualizar `DATABASE_URL` en el `.env` del servidor (y en el local de desarrollo, si se sigue usando Neon).
- [ ] Confirmar que el `.env` del servidor queda con permisos `600` (`chmod 600 backend/.env`) y **jamás** entra a git (ya cubierto por `.gitignore`, verificado con `git check-ignore`).
- [ ] Verificar reconexión: `python manage.py check` y `curl https://.../api/health/` → `{"status":"ok"}`.

> 💡 Aprovecha el reset para crear un rol dedicado (p.ej. `funcrees_app`) con
> permisos solo sobre `neondb` en lugar de usar el owner. En Neon: Roles → New role.

---

## 1️⃣ Variables de entorno de producción (`backend/.env`)

Partir de `backend/.env.example`. Los valores con ⚠️ bloquean el arranque si faltan.

```bash
# --- Django ---
DEBUG=False                      # ⚠️ activa HTTPS forzado y cookies seguras
SECRET_KEY=<generar, ver comando abajo>
ALLOWED_HOSTS=funcreescolombia.org,www.funcreescolombia.org

# --- Base de datos (Neon, credencial YA ROTADA) ---
DATABASE_URL=postgresql://<usuario>:<nueva_password>@ep-...-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require

# --- CORS/CSRF (se derivan si se omiten, pero explícito es más claro) ---
CORS_ALLOWED_ORIGINS=https://funcreescolombia.org,https://www.funcreescolombia.org

# --- Frontend ---
FRONTEND_URL=https://funcreescolombia.org   # redirect de Wompi + enlace del correo semanal

# --- Resumen semanal (correo de los lunes 7:00 a.m.) ---
DIGEST_TO=directiva@funcrees.org,contabilidad@funcrees.org   # vacío = desactivado

# --- Email SMTP ---
DEFAULT_FROM_EMAIL=contacto@funcreescolombia.org
EMAIL_HOST=smtp.gmail.com        # o SendGrid/Mailgun/Hostinger
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=<contraseña de APLICACIÓN, no la del correo>
EMAIL_USE_TLS=True

# --- Wompi (producción real) ---
WOMPI_ENV=production
WOMPI_PUBLIC_KEY=pub_prod_...
WOMPI_PRIVATE_KEY=prv_prod_...
WOMPI_INTEGRITY_SECRET=prod_integrity_...

# --- Encriptación (Ley 1581) ---
ENCRYPTION_KEY=<la clave elegida para la Fundación — ver sección 2>
```

Generar claves nuevas:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

> ⚠️ Con `DEBUG=False`, un `ALLOWED_HOSTS` sin el dominio real devuelve
> `400 DisallowedHost` en todas las páginas. Es el fallo #1 en entregas.

---

## 2️⃣ ENCRYPTION_KEY — una sola clave para la Fundación (sin legado que preservar)

**Situación actual (sep 2026):** la limpieza de datos de demostración dejó la
base con **0 donaciones y 0 apadrinamientos**, es decir, **ningún dato cifrado
depende de una clave anterior**. Ya no hay restricción de "heredar" la clave
vieja: la Fundación elige una clave Fernet **nueva** y la usa desde el día uno.

**La única regla que sí (o siempre) aplica:** local y producción comparten la
misma base de datos (opción A, Neon), así que **la misma `ENCRYPTION_KEY` debe
estar en el `.env` del VPS Y en el `.env` local de desarrollo**. Lo que local
cifra, producción debe poder descifrar, y viceversa.

- [x] ~~Arreglar el `.env` local~~ — **hecho (sep 2026)**: se generaron `SECRET_KEY` y
      `ENCRYPTION_KEY` válidas; el flujo de donación quedó probado de punta a
      punta (escritura cifrada, descifrado, WhatsApp, certificado PDF + correo).
- [ ] **Decidir la clave definitiva de la Fundación.** Camino simple: copiar al
      `.env` del VPS **la misma `ENCRYPTION_KEY` del `.env` local** (la generada
      en sep 2026, ya validada). Alternativa: generar una nueva en el VPS y
      actualizar **ambos** `.env` con ella.
- [ ] Guardar la clave en el **gestor de contraseñas**: perderla = perder los
      documentos/teléfonos de donantes que se cifren a partir de ahora.
- [ ] **Antes del go-live, borrar del admin las donaciones sandbox** que se
      hayan creado probando desde local: quedaron cifradas con la clave local y
      son datos de prueba (así `/numeros` y el panel arrancan en cero real).

| Opción de base de datos | Qué hacer | Regla de la clave |
|---|---|---|
| **A. Seguir usando Neon** (recomendado) | Solo rotar credencial (sección 0) y apuntar el `.env` del VPS a Neon | La misma clave en local y VPS (comparten BD) |
| **B. Migrar a PostgreSQL local del VPS** | `pg_dump` desde Neon → restore en el VPS; ajustar el backup diario de `DEPLOY.md` §💾 | El dump trae los datos YA cifrados: la clave del VPS debe coincidir con la que los cifró (si se migran filas de prueba, es la clave local) |

> ⚠️ Nunca mezclar claves "por ambiente" con una BD compartida: el modelo
> devuelve `None` ante un descifrado fallido y lo registra en el log — síntoma
> inconfundible de clave desalineada.

---

## 3️⃣ Wompi: llaves de producción y webhook

- [ ] Crear/entrar a la cuenta de Wompi de la fundación → **producción** (requiere verificación de identidad mercantil).
- [ ] Copiar las 3 llaves (`pub_prod_`, `prv_prod_`, `prod_integrity_`) al `.env`. **Nunca** por chat/correo sin cifrar.
- [ ] `WOMPI_ENV=production` (con `sandbox`, el botón de donación apuntaría a `sandbox.wompi.co` y no cobraría real).
- [ ] Registrar la **URL de eventos (webhook)** en el dashboard de Wompi:
      `https://funcreescolombia.org/api/donations/webhook/`
- [ ] Configurar en Wompi la URL de redirección: `https://funcreescolombia.org?pago=exitoso` (el backend ya la construye con `FRONTEND_URL`).
- [ ] Evidencia de donante/transacción de prueba en sandbox ANTES del go-live (ver sección 8).

---

## 4️⃣ Correo SMTP

- [ ] Cuenta de correo real de la fundación (p.ej. Google Workspace) + **contraseña de aplicación** (Gmail: requiere 2FA activado).
- [ ] Enviar un correo de prueba real: certificado de donación en sandbox o `send_weekly_digest --to tu-correo`.
- [ ] Revisar carpeta de spam del destinatario; si cae en spam, configurar SPF/DKIM del dominio antes de la entrega.

---

## 5️⃣ Construir, migrar y levantar servicios

```bash
# Backend
cd /var/www/funcrees/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput          # contra la BD elegida en sección 2
python manage.py collectstatic --noinput
mkdir -p media                              # imprescindible para las fotos del admin

# Frontend
cd ../frontend
npm ci && npm run build

# Servicios
sudo systemctl enable --now funcrees funcrees-web
```

- [ ] `sudo systemctl status funcrees funcrees-web` → ambos *active (running)*.
- [ ] Nginx: `sudo nginx -t` OK, certificado SSL emitido con Certbot y renovación probada (`certbot renew --dry-run`).

---

## 6️⃣ Cron del resumen semanal (lunes 7:00 a.m. Colombia)

```bash
sudo crontab -e
# 12:00 UTC = 07:00 Colombia (UTC-5, sin DST). Django calcula las cifras con
# TIME_ZONE=America/Bogota, así que solo importa la hora del servidor.
0 12 * * 1 cd /var/www/funcrees/backend && venv/bin/python manage.py send_weekly_digest >> /var/log/funcrees/digest.log 2>&1
```

- [ ] Probar antes de programar:
      `python manage.py send_weekly_digest --dry-run` (cifras en consola) y
      `python manage.py send_weekly_digest --to correo-de-prueba` (HTML real con el gráfico PNG y el enlace al panel).
- [ ] El correo incluye la sección condicional **"⏳ Pagos por confirmar con Wompi"**:
      donaciones `pendiente`/`procesando` con más de 1 hora, cada una con
      referencia, donante, monto y horas esperando (máximo 8 filas; si hay más,
      indica el total), más un enlace directo al listado filtrado del panel
      (`/admin/donations/donation/?pendientes=si`) donde la acción
      "Verificar con Wompi" confirma el pago. Sin pagos estancados la sección
      no aparece. Espejo exacto de la alerta del panel de administración.
- [ ] Si el servidor no está en UTC, ajustar la hora del cron (NO tocar Django).
- [ ] Confirmar que `DIGEST_TO` tiene los correos reales de la directiva (sección 1).
- [ ] Añadir el cron del **monitor de disponibilidad** de `DEPLOY.md` §📊 (check_uptime cada 5 min: alerta por correo si el sitio o la API se caen) y el pg_dump diario.
- [ ] **Monitor de disponibilidad (check_uptime):** probar `--dry-run` (verificación en consola) y `--force-email` con `--to` (llega el correo "✅ todo funciona" = SMTP y cron listos). Confirmar `UPTIME_ALERT_TO` en `.env` (vacío usa `DIGEST_TO`). Recomendado: heartbeat gratuito en healthchecks.io (`UPTIME_HEARTBEAT_URL`) para cubrir caída total del VPS. El estado vive en `backend/logs/uptime_state.json`. **El día 2, ejecutar el simulacro completo con `DIA2_MONITOREO.md`.**

---

## 7️⃣ Verificar subida de media en el VPS (fotos del admin)

El panel permite subir fotos de beneficiarios/eventos que se guardan en
`backend/media/`. En producción las sirve **Nginx** (`location /media/` ya está
en `deploy_nginx.conf`).

- [ ] `deploy_nginx.conf` copiado a sites-enabled **incluye** el bloque `location /media/ { alias /var/www/funcrees/backend/media/; }`.
- [ ] Permisos: `sudo chown -R www-data:www-data /var/www/funcrees/backend/media` (Gunicorn escribe como `www-data`; sin esto la subida falla con 500).
- [ ] Entra al admin → Beneficiarios → edita uno → **sube una foto real** desde el computador.
- [ ] Verifica: la miniatura se ve en el listado del admin Y la foto aparece en `https://funcreescolombia.org/historias` (cargada desde `/media/beneficiarios/...`, no desde una URL externa).
- [ ] Repite con la imagen de un **evento** y confirma que se ve en `/eventos`.
- [ ] Sube una foto grande (>800px) y confirma que el sitio la redimensiona automáticamente (no debe pesar megas).
- [ ] **Variantes WebP:** la misma subida debe crear junto al original los archivos `-200w.webp` y `-400w.webp` (y `-800w.webp` si la foto es grande) en `backend/media/...`; el API expone `foto_webp_srcset` y `/historias` renderiza `<picture><source type="image/webp">`. Si el `media/` del VPS se restauró de un backup anterior, ejecutar `python manage.py generate_image_variants` (backfill único).
- [ ] `backend/media/` fuera de git (ya en `.gitignore`) y **incluido** en el plan de backup (rsync del directorio o volumen del VPS).

---

## 8️⃣ Pruebas de humo finales (con el sitio ya en producción)

**Público:**

- [ ] `curl https://funcreescolombia.org/api/health/` → `{"status":"ok"}`
- [ ] `curl -s https://funcreescolombia.org/api/stats/` → JSON de cifras con `Cache-Control: public, max-age=120` (página *Nuestros Números*)
- [ ] `/`, `/quienes-somos`, `/proyectos`, `/historias`, `/donaciones`, `/eventos`, `/numeros`, `/contacto` → todas cargan con contenido SSR y datos reales.
- [ ] `https://funcreescolombia.org/sitemap.xml` incluye `/numeros`.
- [ ] El candado del navegador muestra HTTPS en todas las páginas (con `DEBUG=False`, cualquier `http://` redirige a `https://` — así debe ser).

**Panel de administración (`/admin/`):**

- [ ] Login con el superusuario de producción (crear con `createsuperuser`; el `admin` actual de Neon tiene password conocido solo por el cliente).
- [ ] Crear usuarios **staff reales** para el personal (cada persona, su cuenta; nada de compartir el superusuario).
- [ ] El panel "Resumen de la Fundación" carga con cifras, gráfico de 6 meses y sección de pagos por confirmar.
- [ ] Acción "🔄 Verificar con Wompi" visible en Donaciones (se probará de verdad con la donación sandbox del paso siguiente).

**Pagos (una pasada completa en sandbox → otra en producción con monto pequeño):**

- [ ] Donación desde `/donaciones` → se abre Wompi → pago aprobado → donación `completado` en el admin → **certificado PDF llega por correo**.
- [ ] La cifra de `/numeros` y el total del panel reflejan la donación en ≤ 2 minutos (cache de `/api/stats/`).
- [ ] Formulario de contacto envía y aparece en el admin ("✉ nuevo").

**Limpieza pre-entrega:**

- [x] ~~Borrar donaciones de prueba `DONA-TEST*`~~ — **hecho (sep 2026)**: se eliminaron las 10 (2 pendientes + 8 completado, la totalidad del histórico ficticio de $750.000) y se marcaron los 2 mensajes de contacto como leídos. La BD arranca limpia: 0 donaciones, 0 pendientes, 0 sin leer; los 50 beneficiarios, 4 eventos y cifras de beneficiarios son reales.
- [ ] Tras la primera donación real, verificar que `/numeros`, el gráfico del panel y el correo del lunes la reflejan (≤ 2 min por la cache de `/api/stats/`).

---

## 9️⃣ Seguridad y monitoreo (segundo día)

- [ ] `sudo ufw allow 'Nginx Full' && sudo ufw allow OpenSSH && sudo ufw enable`.
- [ ] `chmod 600 backend/.env`; confirmar que no hay `.env` en ningún commit (`git status` limpio).
- [ ] Activar snapshots automáticos del VPS (Hostinger los ofrece en el panel).
- [ ] Logrotate instalado (`DEPLOY.md` §📊) y crons de monitoreo activos.
- [ ] **Monitor con alertas activo:** un reinicio manual de un servicio (`sudo systemctl restart funcrees-web`) debe producir: sin correo en el primer fallo → alerta 🔴 al 2.º chequeo fallido (~10 min) → correo ✅ al recuperarse. Si no llega nada, revisar `UPTIME_ALERT_TO` y el log `/var/log/funcrees/uptime.log`.
- [ ] Revisar al día siguiente: `journalctl -u funcrees -n 100` sin errores recurrentes; digest.log sin fallos si ya pasó el lunes.

---

## 🔟 Paquete de entrega al cliente

| Credencial / acceso | Dónde vive | Notas |
|---|---|---|
| Panel admin | `https://funcreescolombia.org/admin/` | Crear cuentas individuales por persona |
| Superusuario | En la BD de producción | `manage.py changepassword <user>` si se pierde |
| Dashboard Neon | neon.tech | Nueva password YA rotada; 2FA activado |
| Dashboard Wompi | wompi.co | Llaves de producción + webhook configurado |
| Correo SMTP | Proveedor elegido | Contraseña de aplicación documentada |
| ENCRYPTION_KEY / SECRET_KEY | Gestor de contraseñas | Copias de la clave de la Fundación (sección 2) |
| VPS (SSH + panel Hostinger) | Hostinger | Recomendar 2FA en la cuenta del hosting |
| Dominio DNS | Registrador | Verificar que apunta al VPS y renovación al día |

- [ ] Todo lo anterior en un **gestor de contraseñas** (Bitwarden/1Password), nunca en correo, WhatsApp ni documentos sueltos.
- [ ] Sesión de capacitación con el personal: subir fotos, crear eventos, revisar donaciones y el panel de resumen, marcar mensajes leídos, exportar CSV de donaciones. **Usar `AGENDA_CAPACITACION.md`** (sesión de 90 min con prácticas) y **entregar `GUIA_PERSONAL_PANEL.md` impresa** a cada participante.
- [ ] Entregar impresa/PDF: el **`PAQUETE_ENTREGA.md`** (documento combinado: runbook + rollback + guía del personal + agenda + acta de firmas), `DEPLOY.md` (operación), este checklist firmado, y las URLs clave.

---

**Checklist generado:** septiembre 2026 · Proyecto FUNCREES v2.0.0
