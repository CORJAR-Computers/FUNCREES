# 📜 ACTA DE ACEPTACIÓN Y ENTREGA — Sitio Web FUNCREES Colombia v2.0

**Entre las partes:**

- **ENTREGA:** CORJAR Computer Solutions (o el proveedor técnico que suscriba)
  — Representada por: ______________________, CC ______________
- **RECIBE:** Fundación Crece Una Esperanza Social (FUNCREES), NIT 902036173-3
  — Representada por: ______________________, CC ______________

**Fecha:** ____ / ____ / 2026   **Ciudad:** Sincelejo, Sucre

---

## 1 · Objeto

Entrega del sitio web institucional **funcreescolombia.org v2.0** con:
página pública informativa, donaciones en línea (Wompi), eventos solidarios con
boletas y QR de ingreso, apadrinamiento de adultos mayores, panel administrativo,
emails automáticos (certificados, recordatorios, resumen semanal), cumplimiento
Ley 1581 (Habeas Data), SEO y bitácora técnica automatizada (CI).

**Código entregado:** repositorio `CORJAR-Computers/FUNCREES`, rama `main`,
commit `fd304a4` (estado verificado con todos los tests en verde: 228 pruebas
automáticas + pipeline de integración continua aprobado).

**Modalidad de despliegue:** la puesta en producción será realizada
[ ] por CORJAR  [ ] por un proveedor contratado por la Fundación  [ ] por el
personal técnico de la Fundación, conforme a `DEPLOY.md` / `RUNBOOK_VPS.md` y a
la `GUIA_DEL_PROVEEDOR_DESPLIEGUE.md`.

---

## 2 · Verificación funcional (la realiza la persona que RECIBE — sin ayuda técnica)

Marca cada casilla al comprobarlo en `https://funcreescolombia.org`. Si algo no
coincide, no firmes: anótalo en la sección 5.

### Sitio público

- ☐ La página de inicio abre y muestra la información de la Fundación.
- ☐ Los botones del menú llevan a: Proyectos, Eventos, Donaciones, Contacto.
- ☐ El sitio se ve bien en el **celular** (probar 2 páginas mínimo).
- ☐ La página de **Preguntas Frecuentes** abre y las preguntas se abren/cierran.
- ☐ La búsqueda de la caja "¿En qué año…?" del menú legal (privacidad, términos)
  muestra las páginas correspondientes.

### Donaciones

- ☐ En **Donar**, el bloque "¿Cuánto alcanza mi aporte?" mueve la barra y muestra
  equivalentes (almuerzos, kits, terapias).
- ☐ Con un monto y datos de prueba, el botón lleva a la pasarela Wompi (sandbox)
  y permite iniciar un pago de prueba.
- ☐ Tras un pago de prueba aprobado, la página muestra el estado **pagada** y
  llega (o queda en cola de) el correo con el certificado.

### Eventos y boletas

- ☐ Un evento con boletas activas permite comprar (prueba sandbox) y entrega
  código de boleta.
- ☐ En `funcreescolombia.org/boletas`, con el código de una boleta pagada se ve
  el **código QR** con borde verde.
- ☐ El QR escaneado desde un celular abre la verificación correcta.

### Panel administrativo

- ☐ El personal designado ingresa al panel con su usuario.
- ☐ Se puede crear/editar un evento y aparece en el sitio público.
- ☐ La lista de donaciones muestra estados (pendiente/pagada) y permite
  "Verificar con Wompi".
- ☐ La vista **Check-in en puerta** abre la cámara/lector y marca una boleta
  como asistida (probar con el QR del punto anterior).
- ☐ La lista de asistencia se exporta a **Excel** desde el panel.
- ☐ El correo del **resumen semanal** llega los lunes 7:00 a.m. (o quedó
  programado y se muestra el cron activo).

### Legal y datos

- ☐ Las páginas **Privacidad (Ley 1581)**, Términos y Cookies están visibles
  desde el pie de página.
- ☐ El formulario de contacto exige aceptar el tratamiento de datos y guarda
  el mensaje en el panel.

---

## 3 · Lo que se entrega además del código (documentos)

- ☐ `PAQUETE_ENTREGA.pdf` — runbook de despliegue, rollback, guía del panel,
  agenda de capacitación y acta, en un solo documento imprimible.
- ☐ `GUIA_PERSONAL_PANEL.md` — manual del panel para el personal.
- ☐ `QUE_HACER_SI_ALGO_FALLA.md` — guía de contingencia en lenguaje llano.
- ☐ `INVENTARIO_CUENTAS_Y_ACCESOS.md` — cuentas, propietarios y transferencias.
- ☐ `COSTOS_Y_CALENDARIO_OPERACION.md` — costos recurrentes y vencimientos.
- ☐ `GUIA_DEL_PROVEEDOR_DESPLIEGUE.md` — para quien ponga el sitio en producción.
- ☐ `CHECKLIST_ENTREGA.md` firmado — verificación técnica completa.
- ☐ Capacitación realizada según `AGENDA_CAPACITACION.md` (lista de asistencia
  anexa: ☐).

---

## 4 · Limitaciones conocidas al momento de la entrega (declaradas)

1. **Logo y foto principal (hero):** se usan piezas provisionales mientras la
   Fundación aporta el arte definitivo; su reemplazo está contemplado y no
   requiere programación (lo realiza el proveedor técnico en minutos).
2. **Cifras de impacto:** los equivalentes (almuerzo $8.000, kit $40.000,
   terapia $25.000) son valores provisionales documentados; deben confirmarse
   con las cifras oficiales de los programas de la Fundación.
3. **Despliegue en producción:** no incluido en esta entrega de código (según
   la modalidad marcada en la sección 1); se rige por el documento del
   proveedor de despliegue.
4. Otros: _______________________________________________________________

---

## 5 · Pendientes acordados (compromisos post-entrega)

| # | Pendiente | Responsable | Fecha límite |
|---|---|---|---|
| 1 | Arte definitivo (logo/hero) | Fundación → proveedor técnico | ____/____/____ |
| 2 | Cifras oficiales de impacto | Fundación | ____/____/____ |
| 3 | ____________________________ | ____________ | ____/____/____ |

---

## 6 · Soporte posterior (acordado entre las partes)

- **Garantía de defectos:** durante ____ semanas posteriores a la firma, el
  proveedor técnico corrige sin costo los defectos del software entregado.
- **Mantenimiento y soporte continuo:** [ ] incluido  [ ] contrato aparte con
  ______________________ por $ ____________ /mes.
- **Tiempo de respuesta acordado:** ______ horas en horario hábil;
  ______ horas si hay campaña activa.

---

## 7 · Conformidad

El que RECIBE declara haber comprobado los puntos de la sección 2, recibir los
documentos de la sección 3 y conocer las limitaciones de la sección 4 y los
pendientes de la sección 5. El que ENTREGA declara que el software corresponde
al alcance acordado y que los accesos/credenciales se transfieren según
`INVENTARIO_CUENTAS_Y_ACCESOS.md`.


| | ENTREGA (proveedor técnico) | RECIBE (FUNCREES Colombia) |
|---|---|---|
| **Nombre completo** | | |
| **C.C.** | | |
| **Cargo** | | |
| **Firma** | ______________________ | ______________________ |
| **Fecha** | ____/____/2026 | ____/____/2026 |


**Testigo (opcional):** ______________________ CC ______________ Firma: ____________

---

*Anexos: lista de asistencia de la capacitación · capturas de la verificación
funcional (recomendado) · copia de `CHECKLIST_ENTREGA.md` firmado.*
