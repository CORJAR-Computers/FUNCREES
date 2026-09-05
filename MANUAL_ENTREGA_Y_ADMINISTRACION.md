# 📋 Manual de Entrega y Administración — FUNCREES Colombia

**Fundación Crece Una Esperanza Social**  
*Soluciones Sociales Innovadoras para un Impacto Positivo y Duradero.*  
NIT: 902036173-3 | Sincelejo, Sucre, Colombia  

---

## 📑 1. Ficha Técnica y Acta de Entrega

| Parámetro | Detalle |
|-----------|---------|
| **Proyecto** | Plataforma Web Institucional y Sistema de Gestión Social |
| **Cliente** | Fundación Crece Una Esperanza Social (FUNCREESCOLOMBIA) |
| **Representante Legal** | William Romero Hernández |
| **Proveedor Tecnológico** | **CORJAR Computers Solutions** (RUT: 92520615) |
| **Director Técnico** | Ing. de Sistemas y Soluciones de Software |
| **Contacto Proveedor** | (+57) 317 746-7035 \| corjarcomputers@gmail.com |
| **Versión del Sistema** | **v1.1.0** (Arquitectura Fullstack SvelteKit 5 + Django REST API) |
| **Fecha de Entrega** | Septiembre de 2026 |

---

## 🏛️ 2. Arquitectura de la Plataforma

La plataforma ha sido construida con una arquitectura desacoplada de última generación:

1. **Frontend Institucional (SvelteKit 2 + Svelte 5 Runes + Vite 8)**:
   - Experiencia de usuario ultra rápida y fluida sin recargas bruscas de página.
   - Diseño responsivo compatible con computadores, tablets y teléfonos móviles.
   - Sistema de accesibilidad universal integrado (agrandar texto, alto contraste, fuente para dislexia y sintetizador de voz/lector en pantalla).
   - Banner de cookies y consentimiento informado conforme a la **Ley 1581 de 2012 (Hábeas Data)**.
   - Mapa interactivo de ubicación institucional (Sincelejo, Sucre) con Leaflet.js.

2. **Backend de Gestión y API REST (Django 5.x + Django REST Framework + Unfold Admin)**:
   - Panel de administración centralizado, elegante e intuitivo.
   - Cifrado simétrico **Fernet (AES-128)** para proteger documentos de identidad y números telefónicos.
   - Módulos autónomos para Beneficiarios, Donaciones, Eventos y Formulario de Contacto.

---

## 🔑 3. Plantilla de Credenciales y Accesos Oficiales

> [!IMPORTANT]
> Entregar este apartado impreso o mediante canal cifrado. Se recomienda cambiar las contraseñas temporales tras el primer inicio de sesión.

### A. Acceso al Panel de Administración de la Fundación

| Recurso | Enlace / Parámetro | Valor Inicial |
|---------|--------------------|---------------|
| **URL del Panel Admin** | `https://tudominio.org/admin/` | *(o http://127.0.0.1:8000/admin/ en local)* |
| **Usuario Administrador** | `admin` | *(o correo oficial de la dirección)* |
| **Contraseña Temporal** | `[DEFINIR_PASSWORD_SEGURO]` | *(Cambiar inmediatamente al ingresar)* |
| **Nivel de Acceso** | Superusuario | Control total de contenidos |

### B. Pasarela de Pagos (Wompi Colombia)

Para recibir aportes económicos directamente en la cuenta bancaria de la fundación:

| Llave / Configuración | Modo Sandbox (Pruebas) | Modo Producción (Real) |
|-----------------------|-------------------------|------------------------|
| **Llave Pública (Public Key)** | Configurada en frontend | `pub_prod_...` (Aportada por Wompi) |
| **Llave Privada (Private Key)** | Configurada en backend | `prv_prod_...` (Aportada por Wompi) |
| **Event Secret (Webhook)** | Configurada en backend | Proporcionada en el portal Wompi |
| **Integridad de Firma** | Algoritmo SHA-256 | Configurada en backend |

---

## 🖥️ 4. Guía de Uso del Panel de Administración para la Fundación

El panel está disponible en `/admin/`. Una vez autenticado, la fundación puede gestionar de forma autónoma los siguientes módulos:

### 4.1. Módulo: Adultos Mayores (Beneficiarios)
* **¿Dónde se encuentra?** Menú lateral > `Beneficiarios` > `Adultos Mayores`.
* **Para registrar un nuevo beneficiario:**
  1. Clic en **"Añadir Adulto Mayor"**.
  2. Completar: Nombre, edad, foto, historia de vida y necesidades principales (alimentación, medicinas, vestuario, etc.).
  3. Indicar si se encuentra activo y disponible para apadrinamiento.
  4. Guardar. El nuevo perfil aparecerá de inmediato en la sección **"Historias de Vida"** del sitio web.

### 4.2. Módulo: Eventos Solidarios y Boletas
* **¿Dónde se encuentra?** Menú lateral > `Eventos` > `Eventos Solidarios`.
* **Para publicar un evento o banquete de solidaridad:**
  1. Clic en **"Añadir Evento"**.
  2. Definir: Título, descripción, fecha y hora del evento, lugar, aforo (cupo máximo) y valor del bono de solidaridad.
  3. El portal web calculará automáticamente la cuenta regresiva en vivo y permitirá a los usuarios seleccionar la cantidad de boletas y registrar su aporte.

### 4.3. Módulo: Donaciones y Apadrinamiento
* **¿Dónde se encuentra?** Menú lateral > `Donaciones` > `Donaciones Realizadas`.
* **Funcionalidad:**
  - Consulta en tiempo real de aportes recibidos con su estado (`Aprobada`, `Pendiente`, `Rechazada`).
  - Detalle del donante (nombre, correo, tipo de donación: Semilla, Raíz, Legado o Libre).
  - Emisión y descarga de recibos digitales y certificados de donación en PDF.

### 4.4. Módulo: Mensajes de Contacto y Alianzas
* **¿Dónde se encuentra?** Menú lateral > `Contacto` > `Mensajes Recibidos`.
* **Funcionalidad:**
  - Visualización ordenada de consultas ciudadanas, ofertas de voluntariado y propuestas de responsabilidad social empresarial (RSE).

---

## 🚀 5. Instrucciones de Despliegue y Puesta en Marcha

Para consultar el despliegue técnico a fondo en servidores Ubuntu / Nginx / PostgreSQL, remitirse al documento [DEPLOY.md](DEPLOY.md).

### Pasos Resumen para la Puesta en Producción:
1. **Dominio:** Adquirir dominio institucional (ej. `funcreescolombia.org` o `funcrees.org`).
2. **Servidor:** Configurar un VPS en la nube (Hostinger, DigitalOcean o AWS) o plataforma PaaS (Vercel para frontend + Render/Railway para backend).
3. **Certificado SSL:** Habilitar cifrado seguro `https://` mediante Certbot (Let's Encrypt).
4. **Activación Wompi:** Vincular la cuenta bancaria de FUNCREES en el portal de comercios de Wompi Colombia e ingresar las credenciales de producción en el archivo de entorno `.env`.

---

## 🛡️ 6. Cumplimiento Legal y Seguridad (Ley 1581 de 2012)

1. **Cifrado de Información:** Los datos privados de donantes y beneficiarios cuentan con cifrado criptográfico simétrico AES-128 en base de datos.
2. **Consentimiento:** Todo formulario exige al usuario marcar la casilla de aceptación de la Política de Tratamiento de Datos Personales.
3. **Gestión de Cookies:** El portal cuenta con un banner configurable que permite al visitante aceptar, rechazar o configurar cookies técnicas y analíticas.

---

## 🤝 7. Soporte Técnico y Garantía

**CORJAR Computers Solutions** otorga soporte técnico y acompañamiento post-entrega para asegurar la continuidad operativa de la plataforma:

- **Soporte Telefónico / WhatsApp:** (+57) 317 746-7035
- **Correo Electrónico:** corjarcomputers@gmail.com
- **Mantenimiento Preventivo:** Monitoreo de seguridad, respaldo periódico de bases de datos y actualización de certificados SSL.

---

*Desarrollado con dedicación y compromiso social por CORJAR Computers Solutions para la Fundación Crece Una Esperanza Social.*
