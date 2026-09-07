# 🛠️ GUÍA DEL PROVEEDOR DE DESPLIEGUE — FUNCREES Colombia v2.0

**¿Para quién es este documento?** Para la persona o empresa contratada para
poner el sitio en producción (o re-desplegarlo en un servidor nuevo). Asume
competencia técnica básica en Linux/Nginx/Django, pero **no** conocimiento
previo del proyecto.

**El objetivo de esta guía es que llegues, sepas exactamente qué leer, qué se
te exige y qué se te prohíbe — y que la aceptación final no sea una sorpresa
para nadie.**

---

## 1 · Orden de lectura (30–40 min antes de tocar un servidor)

| # | Documento | Para qué | Tiempo |
|---|---|---|---|
| 1 | Este documento | alcance, límites y criterios de aceptación | 10 min |
| 2 | `RUNBOOK_VPS.md` (o PARTE 1 de `PAQUETE_ENTREGA.md`) | guion paso a paso del despliegue | 15 min |
| 3 | `DEPLOY.md` | referencia completa de comandos y variables | consulta |
| 4 | `PLAN_ROLLBACK.md` | qué hacer si un paso rompe algo | 10 min |
| 5 | `CHECKLIST_ENTREGA.md` | verificaciones funcionales exigidas al final | consulta |

> Si el runbook y DEPLOY.md difieren en algún detalle, **manda el runbook**
> (es la versión consolidada y actualizada para la entrega v2.0).

---

## 2 · Requisitos previos (verificar ANTES de empezar)

Cada casilla debe estar resuelta con el cliente antes de la ventana de trabajo:

- ☐ Acceso **root/SSH** al VPS (Ubuntu 22.04 / Debian 12, 2 vCPU / 4 GB mínimo
  recomendado) y confirmación de quién paga la factura.
- ☐ **DNS** del dominio `funcreescolombia.org` administrable (registro A hacia
  el VPS) — y confirmación de que el dominio está a nombre de la Fundación
  (`INVENTARIO_CUENTAS_Y_ACCESOS.md`).
- ☐ Llaves **Wompi de producción** (`WOMPI_PUBLIC_KEY`, `WOMPI_PRIVATE_KEY`,
  `WOMPI_INTEGRITY_SECRET`) y URL del webhook ya acordada:
  `https://funcreescolombia.org/api/donations/wompi/webhook/`.
- ☐ Credenciales **SMTP** con el remitente autorizado
  (certificados de donación salen de ahí).
- ☐ Cadena de conexión **PostgreSQL** (Neon o servidor propio) con usuario y
  contraseña NUEVOS de producción — nunca reutilizar los de desarrollo.
- ☐ `SECRET_KEY` y `ENCRYPTION_KEY` de producción generadas para este entorno
  (la ENCRYPTION_KEY cifra datos sensibles: si se pierde, los datos cifrados
  no se recuperan — respáldala en el gestor de contraseñas del cliente).
- ☐ Ventana agendada con el cliente + canal de comunicación definido.

**Si algo de esto falta, detente y solicítalo.** El único factor de retraso
real de este tipo de proyectos es empezar sin credenciales completas.

---

## 3 · Qué se te exige (definición de "hecho")

El despliegue se considera terminado cuando **todos** estos ítems se cumplen:

1. **Las 10 fases del RUNBOOK** completadas con sus checkpoints ✔ marcados en
   la hoja impresa (Fase 0 a Fase 10).
2. `python manage.py check --deploy` sin advertencias bloqueantes.
3. Verificación funcional completa de `CHECKLIST_ENTREGA.md` ejecutada **en
   presencia del representante de la Fundación** (no vale "yo lo probé").
4. Automatizaciones activas y comprobadas:
   - certificado de donación por correo (probar con donación sandbox→real),
   - resumen semanal (cron lunes 7:00 a.m. America/Bogota),
   - monitor de disponibilidad con alerta,
   - backup diario con retención de 30 días **+ una restauración de prueba**.
5. Cero datos de prueba visibles en producción (cifras públicas en cero real).
6. HTTPS válido (A+ en evaluador SSL preferible), HSTS activo.
7. Entrega de credenciales al gestor de contraseñas de la Fundación y checklist
   de `INVENTARIO_CUENTAS_Y_ACCESOS.md` marcado.
8. **Acta de aceptación** (`ACTA_DE_ACEPTACION.md`) firmada por ambas partes.

---

## 4 · Qué NO hacer (prohibiciones)

1. 🚫 **No reutilices credenciales de desarrollo** ni de otros clientes.
2. 🚫 **No envíes credenciales por WhatsApp/correo plano** — todo al gestor de
   contraseñas del cliente.
3. 🚫 **No ejecutes migraciones ni reinicios sin backup previo** (Fase 8 se
   puede y se debe correr antes de la primera migración real si hay datos).
4. 🚫 **No edites código directamente en el servidor** (`nano views.py` en el
   VPS es la forma más rápida de perder la trazabilidad del sitio). Todo cambio
   pasa por git y CI.
5. 🚫 **No despliegues código que no esté verde en CI** — el pipeline de GitHub
   Actions (228 pruebas) es la red de seguridad acordada.
6. 🚫 **No des acceso root a terceros** sin registro escrito de quién y cuándo.
7. 🚫 **No apagues el monitor ni los crons** para "hacer una prueba rápida".

---

## 5 · Los 3 errores más caros (léelo dos veces)

| Error | Consecuencia | Prevención |
|---|---|---|
| Perder la `ENCRYPTION_KEY` de producción | Los datos cifrados (documentos y teléfonos de donantes) se vuelven irrecuperables | Respaldo inmediato en el gestor del cliente + copia física en sobre |
| Webhook de Wompi mal configurado | Las donaciones se cobran pero el sitio nunca las marca como pagadas | Verificar URL, firma y hacer UNA donación real de $1 antes de firmar el acta |
| Dominio/correo de recuperación a nombre del contratista | Secuestro del activo cuando la relación termina | Sección 2 de `INVENTARIO_CUENTAS_Y_ACCESOS.md` — condición de pago |

---

## 6 · Después del despliegue (primeros 7 días)

- ☐ Día 1–2: vigilar logs de gunicorn/nginx y el monitor; atender dudas del
  personal (la `GUIA_PERSONAL_PANEL.md` y `QUE_HACER_SI_ALGO_FALLA.md` son el
  material de referencia — NO improvises canales de soporte paralelos).
- ☐ Día 7: revisar que el primer resumen semanal salió, que hay ≥7 backups y
  cerrar con el cliente la lista de pendientes del acta.

---

*FUNCREES Colombia · Entrega v2.0 · Documento de trabajo del proveedor — no
sustituye el contrato comercial; define los criterios técnicos de aceptación.*
