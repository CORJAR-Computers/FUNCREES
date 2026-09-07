# 💰 COSTOS Y CALENDARIO DE OPERACIÓN — FUNCREES Colombia

**¿Para quién es esta guía?** Para la dirección administrativa de la Fundación.
**No requiere conocimientos técnicos.** Su propósito: que no haya sorpresas ni
en la factura ni en el calendario.

---

## 1 · Costos recurrentes del sitio

> Los valores son **estimados de mercado (2026) en referencia**; confirma el
> precio exacto con cada proveedor y actualiza esta tabla al contratar.

| Concepto | Proveedor típico | Costo estimado | Frecuencia | ¿Qué pasa si no se paga? |
|---|---|---|---|---|
| 🌐 Dominio `funcreescolombia.org` | Namecheap / Hostinger | ~USD 12–15 / año (~COP 55–65 mil) | Anual | El sitio desaparece; alguien podría comprar el nombre |
| 🖥️ Servidor VPS | Hostinger (plan Corporativo) | ~USD 8–20 / mes | Mensual | El sitio se apaga; tras ~1–2 semanas se borran datos |
| 🗄️ Base de datos | Neon (plan gratuito inicial) | $0 (gratis hasta ~0,5 GB); plan pago ~USD 19/mes si crece | Mensual (si crece) | El sitio deja de guardar registros |
| 📧 Envío de correos | Brevo / similar | $0 (hasta ~300/día); plan pago ~USD 9/mes | Mensual (si crece) | No llegan certificados, recordatorios ni resumen semanal |
| 💳 Comisión Wompi | Wompi | ~2,99 % + IVA **por transacción** (no hay cuota fija) | Por donación | — (es el único costo que solo existe si hay donaciones) |

**Resumen para presupuesto anual (escenario inicial):**

| Escenario | Costo anual aproximado |
|---|---|
| Arranque (todo en planes gratuitos/básicos) | ~COP 250.000–350.000 (dominio + VPS) |
| En crecimiento (db y correos de pago) | ~COP 1.200.000–1.500.000 |

> 💡 **Wompi no se "contrata":** las comisiones se descuentan automáticamente de
> cada donación antes de que llegue el dinero a la cuenta de la Fundación.

---

## 2 · Calendario anual de vencimientos (completar al contratar)

| Concepto | Fecha de vencimiento | Quién vigila | Recordatorio |
|---|---|---|---|
| Dominio | ____ / ____ de cada año | ____________ | ☐ agenda con aviso 30 días antes |
| VPS (facturación) | día ____ de cada mes | ____________ | ☐ medio de pago con fondos |
| Plan de base de datos | ____ / ____ | ____________ | ☐ |
| Plan de correos | ____ / ____ | ____________ | ☐ |
| Renovación SSL | Automática (Certbot) | el servidor | ☐ el monitor alerta si falla |

> ⚠️ **El vencimiento del dominio es el riesgo #1.** Configura el aviso en la
> agenda del correo institucional de la Fundación el mismo día de la entrega.

---

## 3 · Rutina de operación — quién hace qué y cada cuánto

### 🟢 Todos los días (nadie: 0 minutos)

Nada. El sistema se cuida solo: backups diarios, monitor de disponibilidad,
SSL automático.

### 📬 Una vez por semana (lunes, 5 minutos)

- ☐ **Leer el resumen semanal** que llega 7:00 a.m. al correo de la dirección:
  donaciones de la semana, boletas vendidas, mensajes de contacto nuevos.
- ☐ Si el resumen **no llegó**: avisar al responsable técnico (puede indicar un
  fallo en los correos o del propio servidor — ver `QUE_HACER_SI_ALGO_FALLA.md`).

### 🗓️ Una vez por mes (30 minutos, personal administrativo)

- ☐ **Verificar el backup:** descargar el backup más reciente y comprobar que
  pesa un valor razonable y abre (pedir al técnico el enlace/procedimiento una
  vez, luego es rutina).
- ☐ Revisar que **no haya alertas** del monitor pendientes de atender.
- ☐ Revisar donaciones **pendientes** viejas (>7 días) y usar
  "Verificar con Wompi" si es necesario.
- ☐ Registrar en el cuaderno de operación: fecha, backup verificado, novedades.

### 🔄 Una vez por trimestre (1–2 horas, requiere técnico)

- ☐ Actualizar dependencias de seguridad (lo ejecuta el proveedor técnico).
- ☐ Revisar que los certificados y planes vigentes siguen siendo los óptimos.
- ☐ Repasar usuarios del panel: desactivar quienes ya no pertenecen
  (`INVENTARIO_CUENTAS_Y_ACCESOS.md`, sección offboarding).

### 📅 Una vez por año (media jornada, con técnico)

- ☐ Renovar/verificar el dominio (si no es multi-año).
- ☐ Restauración de prueba completa del backup en entorno aislado.
- ☐ Revisión de contraseñas y rotación de las críticas.

---

## 4 · Señales de que toca subir de plan (no antes)

| Señal | Acción |
|---|---|
| La base de datos se acerca a ~0,4 GB (80 % del plan gratis de Neon) | Plan pago (~USD 19/mes) |
| Los correos diarios superan ~250–300 | Plan pago del proveedor SMTP |
| El sitio responde lento en horarios pico o el monitor marca lentitud constante | Subir plan del VPS (más RAM/CPU) |
| Campañas grandes planificadas (> 5.000 visitas/día esperadas) | Avisar al técnico con 2 semanas de anticipación |

---

## 5 · Qué NO es costo del sitio (no confundir)

- El **desarrollo de nuevas funcionalidades** (se cotiza aparte con el proveedor).
- El **arte/logo/branding** (proveedor gráfico).
- Las **donaciones mismas** (es el ingreso, no un costo 🙂).
- Publicidad o campañas de redes sociales.

---

*FUNCREES Colombia · Entrega v2.0 · Complementa: `INVENTARIO_CUENTAS_Y_ACCESOS.md`
(quién paga cada cuenta) y `QUE_HACER_SI_ALGO_FALLA.md` (cuándo llamar al técnico).*
