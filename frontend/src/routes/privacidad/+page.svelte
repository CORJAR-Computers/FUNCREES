<script lang="ts">
	import LegalPage from '$lib/components/LegalPage.svelte';
</script>

<LegalPage
	title="Política de Privacidad y Tratamiento de Datos Personales"
	description="Cómo la Fundación FUNCREES Colombia recoge, usa, protege y elimina tus datos personales, conforme a la Ley 1581 de 2012 (Habeas Data)."
	path="/privacidad"
	updated="1 de septiembre de 2026"
>
	<div class="legal-note">
		<strong>Resumen en una línea:</strong> solo pedimos los datos mínimos para procesar tu
		donación, certificado o solicitud; los protegemos con cifrado y nunca los vendemos.
	</div>

	<h2 id="responsable">1. ¿Quién es responsable del tratamiento?</h2>
	<p>
		<strong>Fundación Crece Una Esperanza Social (FUNCREES)</strong>, identificada con NIT
		902036173-3, con domicilio en Carrera 15b #41c - 07, Sincelejo, Sucre, Colombia, es la
		responsable del tratamiento de los datos personales que nos proporcionas a través de este
		sitio web. Correo de contacto para temas de datos:
		<a href="mailto:fundacioncreceunaesperanza@gmail.com">fundacioncreceunaesperanza@gmail.com</a>.
	</p>

	<h2 id="marco-legal">2. Marco legal</h2>
	<p>
		Este tratamiento se rige por la <strong>Ley 1581 de 2012</strong> (régimen general de
		protección de datos personales), el Decreto 1377 de 2013 y la Ley 1266 de 2008 cuando aplique,
		así como por la jurisprudencia de la Corte Constitucional (Sentencia C-748 de 2011).
	</p>

	<h2 id="datos-recogidos">3. ¿Qué datos recogemos y para qué?</h2>
	<table>
		<thead>
			<tr>
				<th>Canal</th>
				<th>Datos solicitados</th>
				<th>Finalidad</th>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td>Formulario de contacto</td>
				<td>Nombre, correo electrónico, teléfono (opcional), mensaje y motivo</td>
				<td>Responder tu consulta de apadrinamiento, alianza, voluntariado o eventos</td>
			</tr>
			<tr>
				<td>Donaciones (Wompi)</td>
				<td>Nombre, correo, documento y teléfono. El documento y el teléfono se guardan <strong>cifrados</strong></td>
				<td>Procesar el pago, emitir el certificado de donación y contactarte si hay novedades</td>
			</tr>
			<tr>
				<td>Patrocinio y voluntariado</td>
				<td>Nombre de la empresa o persona, correo, teléfono, mensaje</td>
				<td>Gestionar la alianza o la postulación</td>
			</tr>
			<tr>
				<td>Cookies</td>
				<td>Preferencias de consentimiento (localStorage)</td>
				<td>Recordar tu elección sobre cookies (ver <a href="/cookies">Política de Cookies</a>)</td>
			</tr>
		</tbody>
	</table>
	<p>
		No recogemos datos sensibles (salud, religión, etnia, opinión política). Las historias y
		fotografías de beneficiarios se publican con el consentimiento informado de cada persona o de
		su acudiente.
	</p>

	<h2 id="base">4. Autorización y base del tratamiento</h2>
	<p>
		El tratamiento se realiza con tu <strong>consentimiento previo, expreso e informado</strong>,
		que otorgas al marcar la casilla de autorización antes de enviar un formulario o procesar una
		donación. Puedes revocar la autorización o solicitar la supresión de tus datos en cualquier
		momento, salvo obligación legal de conservación (p. ej., soportes contables de donaciones).
	</p>

	<h2 id="derechos">5. Tus derechos (Ley 1581, art. 8)</h2>
	<ul>
		<li><strong>Acceder</strong> a tus datos y conocer cómo están siendo tratados.</li>
		<li><strong>Actualizar y rectificar</strong> datos parciales, inexactos o desactualizados.</li>
		<li><strong>Solicitar prueba</strong> de la autorización otorgada.</li>
		<li><strong>Solicitar la supresión</strong> de tus datos cuando no exista deber legal de conservarlos.</li>
		<li><strong>Revocar</strong> la autorización en los términos de la ley.</li>
		<li><strong>Conocer</strong> las modificaciones a esta política antes de aplicarlas a tus datos.</li>
	</ul>
	<div class="legal-note">
		Para ejercer tus derechos escribe a
		<a href="mailto:fundacioncreceunaesperanza@gmail.com">fundacioncreceunaesperanza@gmail.com</a>
		con el asunto <em>"Protección de datos"</em>. Responderemos en máximo
		<strong>10 días hábiles</strong> (Decreto 1377 de 2013). Si consideras que no fuiste
		atendido, puedes acudir a la Superintendencia de Industria y Comercio (SIC).
	</div>

	<h2 id="seguridad">6. ¿Cómo protegemos tus datos?</h2>
	<ul>
		<li><strong>Cifrado en reposo (Fernet, AES128-CBC + HMAC)</strong> para documento y teléfono de donantes.</li>
		<li><strong>HTTPS/TLS</strong> obligatorio en todo el sitio y en la transmisión de pagos.</li>
		<li><strong>Acceso restringido</strong>: solo personal autorizado de la fundación consulta el panel administrativo, con cuentas individuales.</li>
		<li><strong>Verificación de firmas y límites de tasa</strong> en los formularios públicos contra abuso y suplantación.</li>
		<li><strong>Mínimo dato</strong>: no pedimos información que no necesitamos para la finalidad declarada.</li>
	</ul>

	<h2 id="terceros">7. Terceros que tratan tus datos</h2>
	<ul>
		<li><strong>Wompi (Bancolombia)</strong>: procesa el pago con tarjeta, PSE, Nequi u otros medios. Los datos de pago viajan directo a Wompi bajo su política de privacidad; FUNCREES no almacena números de tarjeta ni claves.</li>
		<li><strong>Proveedor de hosting y correo electrónico</strong>: infraestructura para operar el sitio y enviarte certificados/respuestas.</li>
		<li><strong>Autoridades</strong>: únicamente cuando exista requerimiento legal.</li>
	</ul>
	<p>No vendemos, alquilamos ni cedemos tus datos con fines publicitarios.</p>

	<h2 id="conservacion">8. Tiempo de conservación y eliminación</h2>
	<p>
		Conservamos los datos de donaciones mientras existan obligaciones contables y tributarias
		(5–10 años según la norma colombiana). Los mensajes de contacto se eliminan al cabo de
		<strong>24 meses</strong> si no generaron una relación continua. Cuando solicites supresión y
		no exista deber legal de conservar, eliminamos los datos de forma segura e irreversible.
	</p>

	<h2 id="cambios">9. Cambios a esta política</h2>
	<p>
		Cualquier modificación sustancial se publicará en esta página y, cuando afecte derechos, se
		informará a los titulares registrados por correo antes de su aplicación.
	</p>

	<div class="legal-note">
		<strong>Nota:</strong> este documento fue preparado para la operación del sitio web de
		FUNCREES y debe ser revisado y aprobado por el representante legal de la fundación antes de
		su publicación definitiva. No constituye asesoría jurídica.
	</div>
</LegalPage>
