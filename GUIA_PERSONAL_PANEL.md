# 📘 Guía rápida del panel — Personal FUNCREES

**Tu panel:** `https://funcreescolombia.org/admin/` · **Tu usuario:** el que te asignaron
(cada persona la suya — **nunca compartas tu contraseña**).

Esta guía cabe en una hoja. Explica lo que el personal hace a diario. Los detalles
técnicos viven en `DEPLOY.md` y el plan de emergencias en `PLAN_ROLLBACK.md`.

---

## ✅ Tu rutina diaria (5–10 minutos)

| # | Qué hacer | Dónde |
|---|---|---|
| 1 | **Abre el "Resumen de la Fundación"** (es lo primero que ves al entrar): recaudado del mes, **boletas del mes**, gráfico de 6 meses, mensajes nuevos y pagos pendientes. | Inicio del panel |
| 2 | **Revisa "⏳ Pagos por confirmar con Wompi"** si aparece: son pagos con más de 1 hora sin confirmar. Selecciona cada uno y usa la acción **"🔄 Verificar con Wompi"** para consultar el estado real. Si dejó teléfono, escríbele por el botón verde de **WhatsApp**. | Sección ámbar del inicio o Donaciones |
| 3 | **Revisa "🎟️ Boletas pendientes de pago (más de 48h)"** si aparece: son reservas sin pagar a las que el recordatorio del viernes ya escribió. Usa la acción **"⏰ Recordar pago pendiente"** en Boletas/Tickets o coordina por WhatsApp. | Sección ámbar del inicio o Boletas |
| 4 | **Lee los mensajes nuevos** (los que muestran "✉ nuevo"): contéstalos por correo y márcalos con las acciones **"Marcar como leído"** y **"Marcar como respondido"**. | Mensajes de Contacto |
| 5 | **Revisa el correo del lunes** (7:00 a.m.): trae las cifras de la semana —incluidas las boletas del mes—, el gráfico y los pagos pendientes. Es el mismo dato del panel — nunca hay que "cuadrar" a mano. | Correo de la directiva |

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

## 🎟️ Boletas: enviar el código al comprador

Cuando registres (o confirme el pago de) una boleta, el comprador necesita su
**código de verificación** para consultarla en el sitio y entrar al evento.

1. Ve a **Boletas/Tickets** en el panel y busca la boleta del comprador.
2. Marca la casilla de la boleta (o varias a la vez).
3. En el menú **Acción**, elige **"📧 Enviar boleta por email al comprador"** y pulsa **Ir**.
4. El comprador recibe un correo con: número de boleta, **código destacado**, un
   **QR** y el enlace para consultarla. La columna "boleta enviada" queda marcada sola.

Si el correo sale con error (⚠️), revisa que el email del comprador esté bien
escrito; corrígelo en la boleta y vuelve a enviar.

### 📊 Las tarjetas de boletas del inicio

La segunda fila del "Resumen de la Fundación" muestra, siempre:

| Tarjeta | Qué significa |
|---|---|
| 🎟️ **Boletas registradas (mes)** | Reservas creadas este mes y cuántas ya están pagadas |
| 💵 **Recaudo boletas (mes)** | Dinero confirmado por boletas este mes, con variación vs. el mes anterior |
| ⏳ **Boletas pendientes de pago** | Cuántas reservas siguen sin pagar; en ámbar si alguna supera las 48 horas |
| 📧 **Pagadas sin email enviado** | Boletas pagadas cuyo comprador **todavía no recibe su código** — ¡envíalo! |

Y si hay boletas sin pagar con más de 48 horas, aparece además una sección
ámbar con la lista para gestionarlas de una en una.

---

## 💸 Recordar un pago pendiente a un donante

Si una donación quedó **pendiente** (la persona empezó el pago y no lo terminó):

1. Ve a **Donaciones** y filtra por estado **Pendiente** (o usa el filtro
   "⏳ Pagos por confirmar" del inicio).
2. Selecciona la(s) donación(es) y elige la acción
   **"⏰ Recordar pago pendiente (email al donante)"** → **Ir**.
3. El donante recibe un correo amable con su referencia y el botón para
   completar su aporte (para apadrinamientos mensuales, el correo orienta a
   WhatsApp en vez del formulario).
4. Las donaciones ya confirmadas se omiten solas — no hay riesgo de correos
   fuera de contexto.

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

**FUNCREES Colombia · Guía del personal v1.1 (sep 2026)** — acompaña a
`CHECKLIST_ENTREGA.md` §10 (sesión de capacitación).
