<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { parseCOP, formatMoneyNumber } from '$lib/utils/currency';
	import { toast } from '$lib/stores/toast.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import Modal from '$lib/components/Modal.svelte';
	import { initiateDonation, getDonationStatus, pollDonationStatus, ApiError } from '$lib/api/client';
	import type { UiBeneficiary } from '$lib/types';

	type Tab = 'donacion' | 'apadrinamiento' | 'patrocinio' | 'voluntariado';
	type CheckoutStep = 'form' | 'loading' | 'success' | 'error';
	type EstadoDonacion = 'pendiente' | 'procesando' | 'completado' | 'fallido' | 'reembolsado';

	let activeTab = $state<Tab>('donacion');
	let selectedPreset = $state(50000);
	let customAmount = $state('');
	let selectedGateway = $state<'wompi' | 'whatsapp'>('wompi');
	let modalOpen = $state(false);
	let isRecurring = $state(false);

	// Flujo de checkout real
	let checkoutStep = $state<CheckoutStep>('form');
	let checkoutError = $state('');
	let referencia = $state('');
	let paymentSession = $state<import('$lib/types').WompiPaymentSession | null>(null);
	let estadoFinal = $state<EstadoDonacion | null>(null);
	let pollAbort = $state<AbortController | null>(null);
	let submittedPayload = $state<import('$lib/types').InitiateDonationPayload | null>(null);

	// Formulario patrocinio / voluntariado
	let empresa = $state('');
	let nombre = $state('');
	let email = $state('');
	let telefono = $state('');
	let area = $state('');
	let mensaje = $state('');

	// Beneficiario opcional (apadrinamiento): recibido por query ?beneficiario=uuid
	let beneficiarioId = $state<string | null>(null);
	let beneficiarioNombre = $state('');

	const presets = [20000, 50000, 100000, 200000];

	// Precarga desde la página de historias: /donaciones?beneficiario=<id>&nombre=...
	$effect(() => {
		const bid = page.url.searchParams.get('beneficiario');
		const bnombre = page.url.searchParams.get('nombre');
		if (bid) {
			beneficiarioId = bid;
			beneficiarioNombre = bnombre ?? '';
			activeTab = 'apadrinamiento';
			openModal('apadrinamiento');
		}
	});

	let currentAmount = $derived(customAmount ? parseCOP(customAmount) : selectedPreset);

	function selectPreset(amount: number): void {
		selectedPreset = amount;
		customAmount = '';
	}

	function openModal(tab: Tab, presetAmount?: number): void {
		activeTab = tab;
		if (presetAmount) {
			selectedPreset = presetAmount;
			customAmount = '';
		}
		checkoutStep = 'form';
		checkoutError = '';
		modalOpen = true;
	}

	function closeModal(): void {
		pollAbort?.abort();
		pollAbort = null;
		modalOpen = false;
	}

	/**
	 * Abre el Widget de Wompi en una ventana emergente y hace polling del
	 * estado de la donación por referencia hasta que sea terminal.
	 * Wompi redirige a `redirectUrl` (= esta página con ?pago=exitoso&ref=)
	 * al terminar; si la ventana sigue abierta, el polling actualiza la UI.
	 */
	function openWompiWidget(): void {
		if (!paymentSession) return;
		const W = window as unknown as { WompiWidget?: unknown };
		// El widget oficial se inserta con el script de Wompi; usamos la URL de
		// checkout directa (link de pago) como vía robusta sin dependencias.
		const checkoutUrl =
			`${paymentSession.wompiCheckoutUrl}?` +
			`public-key=${encodeURIComponent(paymentSession.publicKey)}&` +
			`currency=COP&amount-in-cents=${paymentSession.amountInCents}&` +
			`reference=${encodeURIComponent(paymentSession.reference)}&` +
			`signature:integrity=${encodeURIComponent(paymentSession.integritySignature)}&` +
			`customer-email=${encodeURIComponent(paymentSession.customerEmail)}&` +
			`redirect-url=${encodeURIComponent(paymentSession.redirectUrl)}`;

		const w = window.open(checkoutUrl, 'wompi-checkout', 'width=480,height=680');
		w?.focus();
	}

	async function submitDonation(): Promise<void> {
		if (currentAmount <= 0) {
			toast.show('Por favor ingresa un monto válido', 'warning');
			return;
		}

		if (selectedGateway === 'whatsapp') {
			const msg = encodeURIComponent(
				`Hola Fundación FUNCREESCOLOMBIA, deseo realizar un aporte de $${formatMoneyNumber(currentAmount)} COP (${isRecurring ? 'Aporte Mensual' : 'Aporte Único'}) para la labor social.`
			);
			window.open(`https://wa.me/573137924439?text=${msg}`, '_blank');
			return;
		}

		checkoutStep = 'loading';
		checkoutError = '';

		const payload = {
			tipo: (activeTab === 'apadrinamiento' ? 'apadrinamiento' : 'general') as 'apadrinamiento' | 'general',
			monto: currentAmount,
			donante_nombre: nombre || 'Donante Anónimo',
			donante_email: email || 'anonimo@funcreescolombia.org',
			donante_telefono: telefono || undefined,
			metodo_pago: 'card' as const,
			beneficiario_id: beneficiarioId,
			autorizacion_datos: true
		};

		try {
			const res = await initiateDonation(payload);
			referencia = res.referencia;
			paymentSession = res.paymentSession;
			submittedPayload = payload;
			openWompiWidget();
			await waitForPayment();
		} catch (err) {
			checkoutStep = 'error';
			checkoutError =
				err instanceof ApiError
					? err.message
					: 'No se pudo conectar con la pasarela de pagos. Verifica tu conexión e intenta de nuevo.';
		}
	}

	/** Polling del estado hasta estado terminal (~2 min máximo). */
	async function waitForPayment(): Promise<void> {
		pollAbort = new AbortController();
		try {
			const donacion = await pollDonationStatus(referencia, { signal: pollAbort.signal });
			estadoFinal = donacion.estado;
			if (donacion.estado === 'completado') {
				checkoutStep = 'success';
				toast.show('¡Donación procesada con éxito! Muchas gracias.', 'success');
			} else if (donacion.estado === 'fallido' || donacion.estado === 'reembolsado') {
				checkoutStep = 'error';
				checkoutError =
					'El pago no se completó. Si fuiste debitado y el problema persiste, contáctanos por WhatsApp con tu referencia: ' +
					referencia;
			} else {
				// pendiente/procesando tras el timeout: informar honestamente
				checkoutStep = 'error';
				checkoutError =
					'El pago sigue en procesamiento. Te contactaremos al confirmarse. Referencia: ' + referencia;
			}
		} catch {
			checkoutStep = 'error';
			checkoutError = 'No se pudo verificar el estado del pago. Referencia: ' + referencia;
		}
	}

	/** Reintenta el polling tras un error (sin crear otra donación). */
	async function recheckStatus(): Promise<void> {
		if (!referencia) return;
		checkoutStep = 'loading';
		await waitForPayment();
	}

	/**
	 * Formulario de patrocinio empresarial / voluntariado: se envía por
	 * contacto con el asunto adecuado (mismo endpoint, mismo inbox del admin).
	 */
	async function handleCorporateSubmit(e: SubmitEvent): Promise<void> {
		e.preventDefault();
		const { sendContactMessage } = await import('$lib/api/client');
		try {
			checkoutStep = 'loading';
			if (activeTab === 'patrocinio') {
				await sendContactMessage({
					nombre: nombre || empresa,
					email,
					telefono: telefono || undefined,
					asunto: 'Alianza Corporativa / RSE',
					mensaje: `Empresa: ${empresa}\nContacto: ${nombre}\n${mensaje}`
				});
			} else {
				await sendContactMessage({
					nombre,
					email,
					telefono: telefono || undefined,
					asunto: 'Postulación de Voluntariado',
					mensaje: `Área de interés: ${area || 'No especificada'}\n${mensaje}`
				});
			}
			checkoutStep = 'success';
			estadoFinal = null;
			toast.show('Información enviada. Un asesor se comunicará en breve.', 'success');
		} catch (err) {
			checkoutStep = 'error';
			checkoutError =
				err instanceof ApiError ? err.message : 'No se pudo enviar la información. Intenta de nuevo.';
		}
	}

	/** Limpia el estado de checkout al reintentar desde el step de error. */
	function resetCheckout(): void {
		checkoutStep = 'form';
		checkoutError = '';
		estadoFinal = null;
		referencia = '';
		paymentSession = null;
		submittedPayload = null;
	}
</script>

<Seo
	title="Donaciones y Aliados | Fundación Funcrees Colombia"
	description="Apoya la labor de la Fundación Funcrees en Sincelejo: apadrina un adulto mayor, realiza donaciones o vincula a tu empresa como aliada estratégica."
	path="/donaciones"
/>

<section id="donaciones-aliados" class="view-section active">
	<div class="section">
		<div class="section-header">
			<span class="section-subtitle">Sostenibilidad Colectiva</span>
			<h1 class="section-title">Tu Apoyo es la Semilla del Cambio</h1>
			<p class="section-description">
				Tu generosidad nos ayuda a garantizar alimentación balanceada, salud preventiva integral y afecto diario a los adultos mayores de Sincelejo y Sucre.
			</p>
		</div>

		<!-- Pestañas de Navegación Rápida -->
		<div class="donaciones-grid">
			<div class="donacion-card">
				<div class="donacion-icon"><i class="fa-solid fa-users"></i></div>
				<h3 class="donacion-title">Apadrinamiento</h3>
				<p class="donacion-text">
					Conecta directamente con un adulto mayor y aporta mensualmente a su nutrición, medicamentos y terapias.
				</p>
				<button class="btn btn-primary" onclick={() => openModal('apadrinamiento')}>Ver Modalidades +</button>
			</div>

			<div class="donacion-card">
				<div class="donacion-icon"><i class="fa-solid fa-hand-holding-dollar"></i></div>
				<h3 class="donacion-title">Donaciones Directas</h3>
				<p class="donacion-text">
					Aportes únicos o recurrentes para financiar los comedores comunitarios y suministros hospitalarios de la fundación.
				</p>
				<button class="btn btn-secondary" onclick={() => openModal('donacion')}>Donar Ahora +</button>
			</div>

			<div class="donacion-card">
				<div class="donacion-icon"><i class="fa-solid fa-building-circle-arrow-right"></i></div>
				<h3 class="donacion-title">Patrocinio Empresarial</h3>
				<p class="donacion-text">
					Alianzas de Responsabilidad Social (RSE) para que empresas financien huertos urbanos y brigadas de salud.
				</p>
				<button class="btn btn-outline" onclick={() => openModal('patrocinio')}>Ver Alianzas +</button>
			</div>

			<div class="donacion-card">
				<div class="donacion-icon"><i class="fa-solid fa-heart-circle-plus"></i></div>
				<h3 class="donacion-title">Voluntariado Activo</h3>
				<p class="donacion-text">
					Súmate con tus habilidades profesionales en salud, psicología, artes, recreación o pedagogía comunitaria.
				</p>
				<button class="btn btn-outline" style="border-color: orange; color: orange;" onclick={() => openModal('voluntariado')}>Unirse +</button>
			</div>
		</div>

		<!-- Niveles de Apadrinamiento (Pricing Tiers) -->
		<div class="pricing-tiers-section">
			<div style="text-align: center; max-width: 650px; margin: 0 auto 2.5rem;">
				<span class="section-subtitle">Elige tu Nivel de Impacto</span>
				<h2 style="color: var(--secondary);">Niveles de Apadrinamiento</h2>
				<p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.75rem;">
					Cada nivel impacta directamente la vida de personas mayores, jóvenes y comunidades rurales en Sucre.
				</p>
			</div>

			<div class="pricing-tiers-grid">
				<!-- SEMILLA -->
				<div class="pricing-card pricing-card--semilla">
					<span class="pricing-level">🌱 Semilla</span>
					<div class="pricing-amount">
						<span class="pricing-usd">$30 <small style="font-size: 1rem;">USD</small></span>
						<span class="pricing-cop">≈ $126.000 COP</span>
						<span class="pricing-period">por mes</span>
					</div>
					<p class="pricing-name">Padrino Semilla</p>
					<p class="pricing-target">Para personas comprometidas con el cambio social</p>
					<ul class="pricing-features">
						<li>Alimentación balanceada y seguimiento nutricional</li>
						<li>Atención básica en salud preventiva</li>
						<li>Acompañamiento emocional directo</li>
						<li>Reporte mensual de impacto y bienestar</li>
					</ul>
					<button class="pricing-btn pricing-btn--semilla" onclick={() => openModal('apadrinamiento', 126000)}>
						Ser Padrino Semilla
					</button>
				</div>

				<!-- RAÍZ -->
				<div class="pricing-card pricing-card--raiz">
					<span class="pricing-badge pricing-badge--popular">Más Popular</span>
					<span class="pricing-level">🌿 Raíz</span>
					<div class="pricing-amount">
						<span class="pricing-usd">$90 <small style="font-size: 1rem;">USD</small></span>
						<span class="pricing-cop">≈ $378.000 COP</span>
						<span class="pricing-period">por mes</span>
					</div>
					<p class="pricing-name">Padrino Raíz</p>
					<p class="pricing-target">Para familias, Pymes y grupos solidarios</p>
					<ul class="pricing-features">
						<li>Todo lo incluido en Semilla</li>
						<li>Fortalecimiento de capacidades operativas</li>
						<li>Seguridad alimentaria estructural</li>
						<li>Visibilidad como aliado en redes y eventos</li>
						<li>Certificado de donación oficial</li>
					</ul>
					<button class="pricing-btn pricing-btn--raiz" onclick={() => openModal('apadrinamiento', 378000)}>
						Ser Padrino Raíz
					</button>
				</div>

				<!-- LEGADO -->
				<div class="pricing-card pricing-card--legado">
					<span class="pricing-badge pricing-badge--premium">⭐ Premium</span>
					<span class="pricing-level">🏆 Legado</span>
					<div class="pricing-amount">
						<span class="pricing-usd">$130 <small style="font-size: 1rem;">USD</small></span>
						<span class="pricing-cop">≈ $546.000 COP</span>
						<span class="pricing-period">por mes</span>
					</div>
					<p class="pricing-name">Padrino Legado</p>
					<p class="pricing-target">Para empresas y donantes de alto impacto</p>
					<ul class="pricing-features">
						<li>Todo lo incluido en Raíz</li>
						<li>Expansión de huertos a nuevos municipios</li>
						<li>Nombramiento como Embajador Corporativo</li>
						<li>Co-branding institucional y medios digitales</li>
						<li>Acceso exclusivo a rendición de cuentas</li>
					</ul>
					<button class="pricing-btn pricing-btn--legado" onclick={() => openModal('patrocinio')}>
						Ser Padrino Legado ✨
					</button>
				</div>
			</div>
		</div>

		<!-- Medios de Recaudo en Colombia -->
		<div style="background-color: var(--bg-secondary); border-radius: var(--radius-lg); padding: 2.5rem; text-align: center; max-width: 800px; margin: 3rem auto 0;">
			<h3 style="color: var(--secondary); margin-bottom: 0.75rem; font-size: 1.35rem;">Medios de Pago Seguros en Colombia</h3>
			<p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.5rem; line-height: 1.6;">
				Aceptamos transacciones directas a través de <strong>PSE (todos los bancos)</strong>, <strong>Wompi Bancolombia</strong> (Tarjetas de Crédito, Nequi, Daviplata), transferencia a cuenta de ahorros y corresponsales bancarios.
			</p>
			<div style="display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;">
				<span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">PSE</span>
				<span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">Wompi</span>
				<span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">Bancolombia</span>
				<span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">Nequi</span>
				<span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">Efecty</span>
			</div>
		</div>
	</div>
</section>

<!-- Modal de Checkout / Donaciones -->
{#if modalOpen}
	<Modal open={modalOpen} onclose={closeModal} labelledby="checkout-modal-title">
		{#if checkoutStep === 'form' && (activeTab === 'donacion' || activeTab === 'apadrinamiento')}
			<div class="modal-checkout-header">
				<h2 class="modal-checkout-title" id="checkout-modal-title">
					{activeTab === 'apadrinamiento' ? 'Apadrinar un Adulto Mayor' : 'Realizar una Donación Solidaria'}
				</h2>
				<p class="modal-checkout-desc">
					{#if beneficiarioNombre}
						Tu aporte apadrinará a <strong>{beneficiarioNombre}</strong>.
					{:else}
						Cada peso donado llega directamente a los comedores y bienestar de la fundación.
					{/if}
				</p>
			</div>

			<!-- Selector de Frecuencia -->
			<div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
				<button
					type="button"
					class="btn"
					class:btn-primary={!isRecurring}
					class:btn-outline={isRecurring}
					style="flex: 1;"
					onclick={() => isRecurring = false}
				>Aporte Único</button>
				<button
					type="button"
					class="btn"
					class:btn-primary={isRecurring}
					class:btn-outline={isRecurring}
					style="flex: 1;"
					onclick={() => isRecurring = true}
				>Aporte Mensual 🔁</button>
			</div>

			<!-- Datos del donante -->
			<div style="display: flex; flex-direction: column; gap: 0.85rem; margin-bottom: 1.5rem;">
				<div>
					<label class="form-label" for="donante-nombre" style="font-size: 0.85rem;">Nombre completo:</label>
					<input id="donante-nombre" type="text" bind:value={nombre} class="form-control" placeholder="Tu nombre" required />
				</div>
				<div>
					<label class="form-label" for="donante-email" style="font-size: 0.85rem;">Correo electrónico (enviaremos tu certificado):</label>
					<input id="donante-email" type="email" bind:value={email} class="form-control" placeholder="tucorreo@ejemplo.com" required />
				</div>
				<div>
					<label class="form-label" for="donante-tel" style="font-size: 0.85rem;">Teléfono (opcional):</label>
					<input id="donante-tel" type="tel" bind:value={telefono} class="form-control" placeholder="3001234567" />
				</div>
			</div>

			<!-- Selección de Montos -->
			<span class="form-label" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">
				Selecciona el Monto:
			</span>
			<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1rem;">
				{#each presets as amount}
					<button
						type="button"
						class="amount-btn"
						class:active={!customAmount && selectedPreset === amount}
						onclick={() => selectPreset(amount)}
					>
						${formatMoneyNumber(amount)} COP
					</button>
				{/each}
			</div>

			<!-- Monto Personalizado -->
			<div style="margin-bottom: 1.5rem;">
				<label for="custom-amount-input" class="form-label" style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.25rem; display: block;">
					O ingresa otro valor:
				</label>
				<input
					id="custom-amount-input"
					type="text"
					placeholder="Ej: 75.000"
					class="form-control"
					bind:value={customAmount}
					style="font-size: 1.1rem; font-weight: 700;"
				/>
			</div>

			<!-- Medio de Pago -->
			<div style="margin-bottom: 1.5rem;">
				<span class="form-label" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">
					Medio de Pago:
				</span>
				<div style="display: flex; flex-direction: column; gap: 0.5rem;">
					<label style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer;">
						<input type="radio" name="gateway" value="wompi" bind:group={selectedGateway} />
						<span>Wompi Bancolombia (PSE, Tarjetas, Nequi)</span>
					</label>
					<label style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer;">
						<input type="radio" name="gateway" value="whatsapp" bind:group={selectedGateway} />
						<span><i class="fa-brands fa-whatsapp" style="color: #25D366;"></i> Coordinar por WhatsApp</span>
					</label>
				</div>
			</div>

			<!-- Habeas Data -->
			<label style="display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.82rem; color: var(--text-muted); margin-bottom: 1.25rem;">
				<input type="checkbox" checked disabled style="margin-top: 0.2rem;" />
				<span>Autorizo el tratamiento de mis datos personales conforme a la Ley 1581 de 2012 (Habeas Data) para procesar mi donación y emitir el certificado.</span>
			</label>

			<button
				class="btn btn-primary"
				style="width: 100%; padding: 1rem; font-size: 1.1rem;"
				onclick={submitDonation}
			>
				Donar ${formatMoneyNumber(currentAmount)} COP {#if isRecurring}(Mensual){/if}
			</button>
		{:else if checkoutStep === 'form' && (activeTab === 'patrocinio' || activeTab === 'voluntariado')}
			<div class="modal-checkout-header">
				<h2 class="modal-checkout-title" id="checkout-modal-title">
					{activeTab === 'patrocinio' ? 'Alianza de Patrocinio Empresarial' : 'Postulación de Voluntariado'}
				</h2>
				<p class="modal-checkout-desc">
					Completa el formulario y un asesor de la fundación te contactará.
				</p>
			</div>

			{#if activeTab === 'patrocinio'}
				<form onsubmit={handleCorporateSubmit} style="display: flex; flex-direction: column; gap: 1rem;">
					<div>
						<label for="empresa-input" class="form-label">Nombre de la Empresa o Institución:</label>
						<input id="empresa-input" type="text" bind:value={empresa} class="form-control" required />
					</div>
					<div>
						<label for="contacto-nombre-input" class="form-label">Persona de Contacto:</label>
						<input id="contacto-nombre-input" type="text" bind:value={nombre} class="form-control" required />
					</div>
					<div>
						<label for="contacto-email-input" class="form-label">Correo Electrónico Corporativo:</label>
						<input id="contacto-email-input" type="email" bind:value={email} class="form-control" required />
					</div>
					<div>
						<label for="contacto-mensaje-input" class="form-label">Mensaje o Propuesta de Alianza:</label>
						<textarea id="contacto-mensaje-input" bind:value={mensaje} class="form-control" rows="3" placeholder="Cuéntanos sobre tu interés..." required></textarea>
					</div>
					<button type="submit" class="btn btn-primary" style="padding: 0.9rem;">
						Enviar Propuesta de Alianza
					</button>
				</form>
			{:else}
				<form onsubmit={handleCorporateSubmit} style="display: flex; flex-direction: column; gap: 1rem;">
					<div>
						<label for="voluntario-nombre-input" class="form-label">Nombre Completo:</label>
						<input id="voluntario-nombre-input" type="text" bind:value={nombre} class="form-control" required />
					</div>
					<div>
						<label for="voluntario-email-input" class="form-label">Correo Electrónico:</label>
						<input id="voluntario-email-input" type="email" bind:value={email} class="form-control" required />
					</div>
					<div>
						<label for="voluntario-tel-input" class="form-label">Teléfono (WhatsApp):</label>
						<input id="voluntario-tel-input" type="tel" bind:value={telefono} class="form-control" required />
					</div>
					<div>
						<label for="voluntario-area-input" class="form-label">Área de Interés:</label>
						<select id="voluntario-area-input" bind:value={area} class="form-control" required>
							<option value="">-- Selecciona un área --</option>
							<option value="salud">Salud Preventiva / Psicología / Fisioterapia</option>
							<option value="huertos">Huertos Comunitarios / Agronomía</option>
							<option value="talleres">Talleres Lúdicos / Música / Manualidades</option>
							<option value="tecnologia">Alfabetización Digital</option>
							<option value="logistica">Logística / Comedor Solidario</option>
						</select>
					</div>
					<button type="submit" class="btn btn-primary" style="padding: 0.9rem;">
						Registrarme como Voluntario
					</button>
				</form>
			{/if}
		{:else if checkoutStep === 'loading'}
			<div style="text-align: center; padding: 3rem 1rem;">
				<div class="spinner" style="margin: 0 auto 1.5rem;"></div>
				<h3 style="color: var(--secondary);">Procesando con la pasarela de pagos...</h3>
				<p style="color: var(--text-muted); margin-top: 0.5rem;">
					{#if paymentSession}
						Se abrió la ventana de Wompi. Completa el pago ahí; esta ventana se actualizará sola.
					{:else}
						Por favor espera un momento.
					{/if}
				</p>
			</div>
		{:else if checkoutStep === 'success'}
			<div style="text-align: center; padding: 1.5rem 0.5rem;">
				<div class="success-shield" style="margin-bottom: 1rem;">✓</div>
				<h2 style="color: var(--secondary); margin-bottom: 0.5rem;">¡Aporte Confirmado!</h2>
				<p style="color: var(--text-muted); max-width: 480px; margin: 0 auto 1.5rem;">
					Tu generosidad transforma vidas en Sincelejo y Sucre. En breve recibirás el certificado de donación en tu correo.
				</p>

				<div style="background: var(--bg-secondary); border: 1px dashed var(--primary); padding: 1.25rem; border-radius: 12px; text-align: left; font-family: monospace; font-size: 0.85rem; margin-bottom: 1.5rem; white-space: pre-line;">
========================================
     COMPROBANTE DE DONACIÓN - FUNCREES
========================================
Referencia:     {referencia}
Fecha:          {new Date().toLocaleString('es-CO')}
Concepto:       {activeTab === 'apadrinamiento' ? 'Apadrinamiento' : 'Donación Solidaria'}
Monto:          ${formatMoneyNumber(currentAmount)} COP
Estado:         CONFIRMADA POR LA PASARELA
========================================
   ¡GRACIAS POR CRECER ESTA ESPERANZA!
========================================
				</div>

				<button class="btn btn-primary" onclick={closeModal} style="padding: 0.75rem 2rem;">
					Cerrar Ventana
				</button>
			</div>
		{:else if checkoutStep === 'error'}
			<div style="text-align: center; padding: 1.5rem 0.5rem;">
				<div class="success-shield" style="margin-bottom: 1rem; background: #dc2626;">✕</div>
				<h2 style="color: var(--secondary); margin-bottom: 0.5rem;">No se completó la operación</h2>
				<p style="color: var(--text-muted); max-width: 480px; margin: 0 auto 1.5rem;">{checkoutError}</p>
				<div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
					{#if referencia}
						<button class="btn btn-outline" onclick={recheckStatus}>Verificar de nuevo</button>
					{/if}
					<button class="btn btn-primary" onclick={resetCheckout}>Intentar de nuevo</button>
				</div>
			</div>
		{/if}
	</Modal>
{/if}
