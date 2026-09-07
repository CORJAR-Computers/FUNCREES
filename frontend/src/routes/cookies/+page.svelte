<script lang="ts">
	import LegalPage from '$lib/components/LegalPage.svelte';
</script>

<LegalPage
	title="Política de Cookies"
	description="Qué cookies y almacenamiento local usa el sitio de FUNCREES Colombia, para qué sirven y cómo configurarlos."
	path="/cookies"
	updated="1 de septiembre de 2026"
>
	<div class="legal-note">
		Este sitio es <strong>ligero en rastreo</strong>: no usamos cookies publicitarias ni de
		profilación de terceros. Solo lo esencial para que el sitio funcione y, si tú lo autorizas,
		métricas anónimas de uso.
	</div>

	<h2 id="que-son">1. ¿Qué son las cookies y el localStorage?</h2>
	<p>
		Las cookies son pequeños archivos que el sitio guarda en tu navegador para recordar
		información entre visitas. El <em>localStorage</em> cumple una función similar pero vive
		exclusivamente en tu dispositivo y no se envía al servidor en cada petición.
	</p>

	<h2 id="cuales">2. ¿Cuáles usamos?</h2>
	<table>
		<thead>
			<tr>
				<th>Tipo</th>
				<th>Nombre / mecanismo</th>
				<th>Finalidad</th>
				<th>Duración</th>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td>Esenciales</td>
				<td>Cookie de sesión/CSRF de Django <code>csrftoken</code>, <code>sessionid</code></td>
				<td>Seguridad de formularios y sesión del panel administrativo</td>
				<td>Sesión / 1 año</td>
			</tr>
			<tr>
				<td>Preferencias</td>
				<td><code>localStorage: funcrees_cookie_consent</code></td>
				<td>Recordar qué cookies autorizaste, para no preguntarte cada visita</td>
				<td>Hasta que borres tus datos de navegación</td>
			</tr>
			<tr>
				<td>Preferencias</td>
				<td><code>localStorage: tema</code></td>
				<td>Recordar tu elección de modo claro/oscuro</td>
				<td>Hasta que borres tus datos de navegación</td>
			</tr>
			<tr>
				<td>Analíticas (opcional)</td>
				<td>Solo si autorizas en el banner</td>
				<td>Métricas agregadas de páginas visitadas para mejorar contenidos</td>
				<td>Según herramienta, máx. 13 meses</td>
			</tr>
		</tbody>
	</table>

	<h2 id="terceros">3. Servicios de terceros</h2>
	<ul>
		<li><strong>Google Fonts</strong>: carga las tipografías Inter y Outfit. Google puede registrar tu dirección IP al servir la fuente (ver <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">su política</a>).</li>
		<li><strong>Wompi</strong>: si donas, su widget opera en ventana aparte con sus propias cookies de seguridad de pago.</li>
	</ul>

	<h2 id="configurar">4. ¿Cómo configurar o eliminar cookies?</h2>
	<p>
		Puedes aceptar "Solo esenciales" desde el banner, o borrar cookies y datos de sitio desde la
		configuración de tu navegador (Chrome, Firefox, Safari y Edge lo permiten por sitio o en
		general). Ten en cuenta que bloquear cookies esenciales puede impedir el funcionamiento
		correcto de formularios y del panel administrativo.
	</p>

	<h2 id="consentimiento">5. Consentimiento</h2>
	<p>
		Al llegar por primera vez al sitio mostramos un banner donde puedes
		<strong>aceptar todo, aceptar solo lo esencial o configurar</strong> tus preferencias. Tu
		elección queda guardada y puedes cambiarla cuando quieras borrando el almacenamiento local
		o escribiéndonos.
	</p>
</LegalPage>
