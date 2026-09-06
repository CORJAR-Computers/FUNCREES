# 🩺 Día 2 — Monitor de disponibilidad y latido externo

**Cuándo:** el día siguiente al despliegue · **Duración:** ~15 minutos · **Quién:** quien administra el VPS
**Objetivo:** dejar probado que, si el sitio se cae, el personal recibe un correo — y que si el VPS entero muere, alguien se entera igual.

> Complementa `RUNBOOK_VPS.md` (Fase 8) y `PLAN_ROLLBACK.md`. Imprime esta hoja y marca cada ☐.

**Antes de empezar (del despliegue, ya hecho):**
- [ ] Sitio y API responden (`https://funcreescolombia.org` y `/api/health/` → `{"status": "ok"}`)
- [ ] Crons instalados (Fase 8), incluido `check_uptime` cada 5 minutos
- [ ] `UPTIME_ALERT_TO` con correos reales del personal en `backend/.env`

---

## Parte A — Latido externo en healthchecks.io (5–10 min)

*Cubre el caso que el monitor interno no puede ver: el VPS completo apagado o sin red.*
*El monitor solo hace ping a healthchecks.io cuando **TODO está bien**; si el VPS muere, el silencio dispara la alerta externa.*

- [ ] **A1.** Crear cuenta gratuita en **healthchecks.io** con un correo del personal
- [ ] **A2.** **Add Check** → nombre `FUNCREES sitio` → Schedule **Period: 5 min + Grace: 10 min**
- [ ] **A3.** Copiar la **URL de ping** del check (Formato: `https://hc-ping.com/<uuid>`)
- [ ] **A4.** En el VPS: `sudo nano /var/www/funcrees/backend/.env` → pegar la URL:
      `UPTIME_HEARTBEAT_URL=https://hc-ping.com/<uuid>`
- [ ] **A5.** Forzar un ciclo ahora (sin esperar 5 min):
      ```bash
      cd /var/www/funcrees/backend && venv/bin/python manage.py check_uptime
      ```
- [ ] **A6.** En healthchecks.io el check pasa a **verde "up"** con la hora del último ping
- [ ] **A7.** Verificar correos de alerta: en el check → **Integrations** → añadir/confirmar **Email** del personal

## Parte B — Simulacro de caída (5 min)

*Prueba real de la cadena completa: fallo → alerta → recuperación.*

- [ ] **B1.** Apagar el sitio a propósito:
      ```bash
      sudo systemctl stop funcrees-web
      ```
- [ ] **B2.** **Silencio en el 1.er ciclo** (~5 min): nada llega — es el anti-ruido de 2 fallos
- [ ] **B3.** En el 2.º ciclo (~10 min): llega 📧 **🔴 ALERTA: sitio caído** al personal
- [ ] **B4.** El check de healthchecks.io sigue en verde (correcto: el ping externo solo refleja un estado; el drill no lo evalúa)
- [ ] **B5.** Levantar el servicio:
      ```bash
      sudo systemctl start funcrees-web
      curl -s --max-time 10 http://127.0.0.1:3000/ | grep -o "<title>[^<]*</title>"
      ```
- [ ] **B6.** Llega 📧 **✅ RECUPERADO** con la duración de la caída (~10 min)

---

## ✅ Confirmación final

Si B3 y B6 llegaron al correo del personal, quedan garantizadas las **dos redes de seguridad**:

| Fallo | Quién avisa | Cuándo |
|---|---|---|
| Backend o sitio web caídos | Monitor interno (`check_uptime`) | ~10 min, y recordatorio cada 2 h |
| VPS completo fuera de línea | healthchecks.io (silencio del latido) | Período 5 min + tolerancia 10 min |

**Cierre del día 2:**
- [ ] Borrar correos de prueba · registrar el drill con fecha y resultado en la bitácora de la Fundación
- [ ] Dejar este documento firmado junto al acta de entrega (`PAQUETE_ENTREGA.md`)

*Si una alerta no llegó: `tail /var/log/funcrees/uptime.log` y verificar `UPTIME_ALERT_TO`/`DIGEST_TO` en `backend/.env` (ver PLAN_ROLLBACK.md §2B).*
