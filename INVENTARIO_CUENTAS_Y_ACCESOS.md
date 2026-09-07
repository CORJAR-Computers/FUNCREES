# 🔑 INVENTARIO DE CUENTAS Y ACCESOS — FUNCREES Colombia

**¿Para quién es esta guía?** Para la dirección y el personal administrativo de la
Fundación. **No requiere conocimientos técnicos.**

**¿Por qué es el documento más importante de la entrega?** Porque el sitio web no
vive solo en el código: vive en una serie de **cuentas contratadas** (dominio,
servidor, pasarela de pagos, correos). Si la Fundación no es **propietaria** de
todas ellas, cualquier persona que se vaya (colaborador, contratista, proveedor)
podría dejar al sitio "secuestrado". Este documento existe para evitarlo.

> 🔒 **Regla de oro:** la Fundación debe ser la **titular** de todas las cuentas.
> Los terceros (CORJAR, el proveedor de despliegue, un consultor) reciben acceso,
> nunca propiedad. El acceso se comparte a través de un **gestor de contraseñas**,
> nunca por WhatsApp, correo o papel.

---

## 1 · Cuentas que existen (completar durante la entrega)

Marca ☑ cuando la Fundación sea propietaria y tenga la credencial en su gestor
de contraseñas.

### 🌐 Dominio y DNS — `funcreescolombia.org`

| Pregunta | Respuesta (completar) |
|---|---|
| ¿Dónde está registrado? (Namecheap, GoDaddy, Hostinger…) | ☐ ______________________ |
| ¿A qué correo llega la renovación anual? | ☐ ______________________ |
| ¿Quién es el PROPIETARIO de la cuenta? | ☐ Fundación / ☐ Tercero |
| Fecha de renovación | ☐ ____ / ____ / 20____ |
| Costo anual aproximado | ☐ $ ____________ USD/COP |

⚠️ **Riesgo si se pierde:** el sitio deja de existir para el mundo y alguien
podría comprar el dominio. **Es el activo más importante de esta lista.**
📌 Si hoy está a nombre de un tercero: transferir a una cuenta de la Fundación
**antes** de cerrar la entrega.

### 🖥️ Servidor (VPS / Hosting)

| Pregunta | Respuesta (completar) |
|---|---|
| Proveedor (recomendado: Hostinger VPS) | ☐ ______________________ |
| ¿Quién paga la factura mensual? | ☐ ______________________ |
| ¿Quién tiene acceso de administrador (root/SSH)? | ☐ ______________________ |
| Fecha de corte de facturación | ☐ día ____ de cada mes |

⚠️ **Riesgo si se pierde:** el sitio se apaga y la base de datos puede borrarse
si se deja de pagar. Guardar las facturas al correo institucional de la Fundación.

### 🗄️ Base de datos (Neon PostgreSQL)

| Pregunta | Respuesta (completar) |
|---|---|
| Proveedor (recomendado: Neon) | ☐ ______________________ |
| ¿Quién es el PROPIETARIO del proyecto? | ☐ Fundación / ☐ Tercero |
| ¿Quién puede descargar backups? | ☐ ______________________ |

⚠️ **Riesgo si se pierde:** aquí viven los registros de donantes, padrinazgos y
boletas. Sin acceso, la operación continúa pero sin historia ni respaldos.

### 💳 Wompi (pasarela de pagos)

| Pregunta | Respuesta (completar) |
|---|---|
| ¿La cuenta merchant es de la Fundación (NIT propio)? | ☐ Sí / ☐ No |
| ¿Quién recibe el dinero de las donaciones? | ☐ ______________________ |
| ¿Quién administra las llaves públicas/privadas? | ☐ ______________________ |
| Correo de soporte/login | ☐ ______________________ |

⚠️ **Riesgo si se pierde:** no se pueden actualizar llaves, revisar pagos ni
cambiar la cuenta bancaria de destino. **La cuenta Wompi DEBE estar a nombre de
la Fundación** (es la receptorá del dinero — nunca a nombre de un tercero).

### 📧 Correo/envío de emails (SMTP)

| Pregunta | Respuesta (completar) |
|---|---|
| Proveedor (Brevo, Gmail, Zoho…) | ☐ ______________________ |
| ¿Quién administra la cuenta? | ☐ ______________________ |
| Límite de envíos del plan actual | ☐ ____________ correos/día |

⚠️ **Riesgo si se pierde:** dejan de llegar los certificados de donación, los
recordatorios de pago y el resumen semanal. Los donantes no se enteran de nada.

### 🐙 Código fuente (GitHub — CORJAR-Computers/FUNCREES)

| Pregunta | Respuesta (completar) |
|---|---|
| ¿Quién es propietario de la organización? | ☐ CORJAR-Computers |
| ¿La Fundación tiene una cuenta propia? | ☐ Sí / ☐ No — usuario: ________ |
| ¿Cómo obtiene el código un nuevo proveedor técnico? | clon del repo + invitación |

📌 El código es de la Fundación según el contrato; GitHub es la herramienta.
Un nuevo proveedor técnico debe recibir acceso de lectura (mínimo) al repo.

### 🔐 Gestor de contraseñas

| Pregunta | Respuesta (completar) |
|---|---|
| Herramienta elegida (Bitwarden gratuito, 1Password, KeePass…) | ☐ ____________ |
| ¿Quién es el "propietario" de la bóveda? | ☐ Dirección de la Fundación |
| ¿Quién más tiene acceso de emergencia? | ☐ ______________________ |
| Códigos de recuperación impresos y guardados en physical safe | ☐ Sí / ☐ No |

---

## 2 · Reglas de convivencia con terceros

1. **Propiedad vs. acceso.** La Fundación es propietaria; los terceros reciben
   *invitaciones* de acceso con el mínimo permiso necesario.
2. **Todo credencial nuevo** que se cree durante la operación (llaves de API,
   contraseñas de servicio) va al gestor de contraseñas el mismo día.
3. **Doble factor (2FA) activado** en: dominio, VPS, Wompi, GitHub y el gestor
   mismo. Guardar los códigos de recuperación impresos en sobre sellado.
4. **Nunca compartir contraseñas por chat/correo.** Se comparte acceso al gestor
   (Bitwarden permite enviar una credencial sin mostrarla).
5. **Correo de recuperación:** las cuentas deben recuperarse con correos
   **institucionales** de la Fundación (ej. `direccion@funcreescolombia.org`),
   no con correos personales de colaboradores.

---

## 3 · Cuando una persona se va (offboarding)

Día en que alguien deja la Fundación o termina su contrato:

- ☐ Quitar su acceso en el gestor de contraseñas.
- ☐ Cerrar sus sesiones en el panel admin (Panel → usuarios → desactivar).
- ☐ Rotar las contraseñas que conocía (mínimo: panel y SMTP).
- ☐ Si conocía llaves del VPS o del código: pedir al proveedor técnico que
  rote las llaves SSH y tokens.
- ☐ Verificar que ningún correo personal quede como recuperación de cuentas.

---

## 4 · Checklist de transferencia (firmar con la entrega técnica)

- ☐ Dominio a nombre de la Fundación + renovación visible en el calendario.
- ☐ Cuenta de VPS pagada y a nombre de la Fundación.
- ☐ Proyecto de base de datos transferido o duplicado a cuenta de la Fundación.
- ☐ Cuenta Wompi a nombre de la Fundación con cuenta bancaria propia.
- ☐ Cuenta SMTP a nombre de la Fundación.
- ☐ Bóveda del gestor de contraseñas creada y poblada con TODAS las credenciales.
- ☐ 2FA activado y códigos de recuperación impresos.
- ☐ Acceso de lectura al repositorio de código para el contacto técnico designado.
- ☐ Este documento firmado por ambas partes (ver `ACTA_DE_ACEPTACION.md`).

---

*FUNCREES Colombia · Entrega v2.0 · Complementa: `ACTA_DE_ACEPTACION.md` ·
Última revisión: septiembre 2026*
