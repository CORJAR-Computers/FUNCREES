# 🔙 Plan de Rollback — FUNCREES Colombia

Documento de recuperación para el día del despliegue y para operación normal.
**Audiencia:** la persona técnica que administra el VPS (puede ser el personal de la
Fundación siguiendo las instrucciones al pie de la letra). Complementa `RUNBOOK_VPS.md`
(despliegue) y `CHECKLIST_ENTREGA.md` (verificaciones).

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
runbook). Sigue `RUNBOOK_VPS.md` desde la fase donde se detuvo; cada checkpoint del
runbook te dice qué debe funcionar antes de continuar. Si un paso no pasa su
checkpoint, ese paso es el problema — no avances "a ver si funciona".

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

**Con Neon (opción A del runbook)**, cambia los pasos 3–4 por:

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

## 🗂️ Referencias cruzadas

| Tema | Documento |
|---|---|
| Despliegue completo paso a paso | `RUNBOOK_VPS.md` (y `DEPLOY.md` con detalle) |
| Verificaciones de entrega | `CHECKLIST_ENTREGA.md` |
| Backups automáticos (instalación del cron) | `DEPLOY.md` §💾 |
| Monitor de caídas con alertas | `DEPLOY.md` §📊 ("Monitor de disponibilidad") |
| Clave de cifrado y su regla | `CHECKLIST_ENTREGA.md` §2 |

---

**Plan de rollback generado:** septiembre 2026 · FUNCREES v2.0 · Última revisión: antes de la entrega
