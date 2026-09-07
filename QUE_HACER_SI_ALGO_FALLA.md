# 🚨 ¿QUÉ HACER SI ALGO FALLA? — Guía para el personal de FUNCREES

**¿Para quién es esta guía?** Para cualquier persona de la Fundación, **sin
conocimientos técnicos**. Imprímela y déjala junto al teléfono.

**La regla de oro — tres pasos, en este orden:**

1. **🚫 NO toques nada** dentro del panel más allá de lo que esta guía diga.
   (Los arreglos improvisados suelen convertir un problema pequeño en uno grande.)
2. **📝 Anota** la información del cuadro "Qué anotar siempre" (abajo).
3. **📞 Llama o escribe** al contacto de soporte (sección final) y pégale esa
   información. Espera su indicación.

Los **backups automáticos diarios** existen: en el peor caso se pierde como
máximo un día de información. Nada es catastrófico si se actúa con calma.

---

## 1 · Problemas comunes y qué hacer

### 😰 "La página no abre" (o sale un mensaje raro)

**Qué significa:** normalmente el servidor o el dominio. 9 de cada 10 veces se
resuelve en menos de una hora.

**Qué hacer:**
- ☐ Entra desde otro dispositivo/red (por ejemplo, datos móviles del celular).
  Si allá funciona, el problema es tu internet — avisa al equipo y sigue normal.
- ☐ Si no abre en ningún lado: anota el mensaje exacto que ves
  (ej. "502 Bad Gateway", "Este sitio no está disponible").
- ☐ Llama al soporte técnico. No es urgencia de medianoche salvo que haya una
  campaña de donación activa en ese momento.

**Expectativa:** el proveedor del servidor restablece el servicio; el soporte
técnico verifica que todo quedó bien.

---

### 😕 "La página abre pero se ve rota / sin colores / sin fotos"

**Qué hacer:**
- ☐ Presiona **Ctrl + F5** (forzar recarga). La mitad de estos casos se
  resuelven aquí.
- ☐ Prueba en otro navegador (Chrome, Firefox) o modo incógnito.
- ☐ Si sigue rota: captura de pantalla + llamada al soporte.

---

### 💳 "Una donación no aparece" o un donante dice que pagó y no recibió certificado

**Qué significa:** el pago puede estar *aprobado pero pendiente de confirmación*
de Wompi (puede tardar minutos u horas con PSE/Bancolombia), o el correo del
donante quedó mal escrito.

**Qué hacer:**
- ☐ Entra al **Panel → Donaciones** y busca por nombre o referencia.
  - Si aparece como **"Pendiente"**: es normal; Wompi la confirmará sola.
    Puedes usar el botón **"Verificar con Wompi"** de la donación.
  - Si aparece **"Pagada"**: el certificado ya salió; pídele al donante revisar
    spam/correo no deseado.
  - Si **no aparece**: el donante no completó el pago → con el número de
    recibo/transacción, escríbele al soporte Wompi (ver contactos).
- ☐ Anota: nombre del donante, monto, fecha, número de transacción Wompi
  (aparece en el recibo del banco), y captura del recibo del donante.

---

### 🎫 "Una boleta se pagó pero la persona no la recibió"

**Qué hacer:**
- ☐ Panel → Boletas → buscar por código (el comprador la puede ver también en
  `funcreescolombia.org/boletas` con su código).
- ☐ Si está **pagada**: en la boleta hay botón para **reenviar el correo**.
- ☐ Si está **pendiente**: el pago no se confirmó aún → mismos pasos que el
  caso de donaciones.

---

### 🔒 "No puedo entrar al panel" (olvidé la contraseña)

**Qué hacer:**
- ☐ Usa "¿Olvidaste tu contraseña?" en la pantalla de ingreso del panel.
- ☐ Si no llega el correo: revisa spam. Si sigue sin llegar, pídele a otro
  usuario con permisos que te la restablezca desde Panel → Usuarios.
- ☐ Si NADIE puede entrar: llamada al soporte técnico (requiere acción suya).

---

### ✉️ "No llegan los correos del sitio" (certificados, resumen del lunes)

**Qué hacer:**
- ☐ Revisa si el problema es de UN destinatario (su buzón lo filtra como spam)
  o de TODOS (el servicio de envío se agotó o falla).
- ☐ Si es de todos: llama al soporte técnico — el servicio de correo puede
  haber alcanzado su límite diario o vencido el plan.

---

### 🛑 "Apareció contenido extraño / creo que nos hackearon"

**Qué hacer (esto SÍ es urgente):**
- ☐ Captura de pantalla con fecha y hora.
- ☐ Llama INMEDIATAMENTE al soporte técnico y avísale a la dirección.
- ☐ No publiques nada al respecto hasta tener el diagnóstico.
- ☐ No intentes "arreglar" publicaciones desde el panel.

---

## 2 · Qué anotar siempre (léelo al teléfono)

| Dato | Ejemplo |
|---|---|
| ¿Qué día y hora notaste el problema? | "hoy 10:40 a.m." |
| ¿En qué página exactamente? | "funcreescolombia.org/donaciones" |
| ¿Qué mensaje sale? (texto literal o captura) | "502 Bad Gateway" |
| ¿En qué dispositivo y navegador? | "celular Android, Chrome" |
| ¿Desde qué red? | wifi de la oficina / datos móviles |
| ¿Lo probaste en otro dispositivo? | "sí, y allí sí abre" |
| Si es un pago: nombre, monto, referencia Wompi | "María Pérez, $50.000, ref ABC-123" |

---

## 3 · A quién llamar (completar durante la entrega)

| Situación | Contacto | Teléfono / correo | Horario |
|---|---|---|---|
| Problemas del sitio (1ª línea) | ______________________ | ______________ | ______ |
| Proveedor del servidor (VPS) | ______________________ | ______________ | ______ |
| Pagos / Wompi | soporte de Wompi | soportemercados@wompi.co | días hábiles |
| Dominio / renovación | ______________________ | ______________ | ______ |
| Responsable interno designado | ______________________ | ______________ | ______ |

> 📌 **Sugerencia:** acuerda con el proveedor técnico un tiempo de respuesta
> (ej. "2 horas en horario hábil, 6 horas si hay campaña activa") y escríbelo
> aquí mismo. Un acuerdo verbal se olvida; uno escrito se cumple.

---

## 4 · Qué NO hacer (las 5 trampas clásicas)

1. ❌ **No des tu contraseña del panel a nadie** que llame "de soporte" — el
   soporte legítimo jamás la pide.
2. ❌ **No instales "actualizaciones"** ni plugins que te sugieran por teléfono.
3. ❌ **No edites textos/precios** del sitio desde el panel sin avisar al
   responsable designado (los cambios en la página de donaciones afectan pagos).
4. ❌ **No compartas el archivo de base de datos ni backups** por correo/WhatsApp.
5. ❌ **No canceles ni dejes de pagar** ninguna cuenta del
   `INVENTARIO_CUENTAS_Y_ACCESOS.md` sin avisar al responsable técnico.

---

*FUNCREES Colombia · Entrega v2.0 · Complementa: `INVENTARIO_CUENTAS_Y_ACCESOS.md`
(qué cuentas existen) y `PLAN_ROLLBACK.md` (guía técnica del proveedor).*
