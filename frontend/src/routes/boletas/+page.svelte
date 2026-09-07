<script lang="ts">
	import Seo from '$lib/components/Seo.svelte';
	import { getTicket, ApiError } from '$lib/api/client';
	import type { ApiTicket } from '$lib/types';

	/**
	 * Consulta pública de boletas: el comprador ingresa el código de
	 * verificación de 10 caracteres (impreso en su comprobante/WhatsApp)
	 * y ve el estado de pago de su boleta sin llamar a la fundación.
	 * El endpoint es público pero con throttle 'anon' (anti fuerza bruta).
	 */

	let codigo = $state('');
	let ticket = $state<ApiTicket | null>(null);
	let isConsultando = $state(false);
	let errorConsulta = $state('');
	let notFound = $state(false);
	/** Rastreo del último código consultado para el mensaje de reintento. */
	let ultimoCodigo = $state('');

	const CODIGO_PATTERN = /^[A-Z0-9]{10}$/;

	/** Formatea un monto Decimal (string) al estándar colombiano. */
	function fmtCOP(valor: string): string {
		const n = Number(valor);
		if (Number.isNaN(n)) return valor;
		return '$' + String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
	}

	/** Metadatos visuales del estado de pago (badge con color e icono). */
	const ESTADO_META: Record<string, { label: string; icon: string; css: string }> = {
		pagado: { label: 'Pago Confirmado', icon: 'fa-circle-check', css: 'badge-pagado' },
		pendiente: { label: 'Pago Pendiente', icon: 'fa-clock', css: 'badge-pendiente' },
		cancelado: { label: 'Cancelada', icon: 'fa-circle-xmark', css: 'badge-cancelado' }
	};

	async function handleConsulta(e: SubmitEvent): Promise<void> {
		e.preventDefault();
		const normalizado = codigo.trim().toUpperCase();
		if (!CODIGO_PATTERN.test(normalizado)) {
			errorConsulta = 'El código tiene 10 caracteres (letras y números), sin espacios. Ej: A1B2C3D4E5.';
			notFound = false;
			ticket = null;
			return;
		}

		isConsultando = true;
		errorConsulta = '';
		notFound = false;
		ticket = null;
		ultimoCodigo = normalizado;

		try {
			ticket = await getTicket(normalizado);
		} catch (err) {
			if (err instanceof ApiError && err.status === 404) {
				notFound = true;
			} else {
				errorConsulta =
					err instanceof ApiError
						? err.message
						: 'No pudimos verificar la boleta en este momento. Intenta de nuevo o escríbenos por WhatsApp.';
			}
		} finally {
			isConsultando = false;
		}
	}

	function handleInput(): void {
		// Normalización en vivo: mayúsculas y sin espacios accidentales.
		codigo = codigo.toUpperCase().replace(/\s+/g, '');
		if (errorConsulta || notFound) {
			errorConsulta = '';
			notFound = false;
		}
	}
</script>

<Seo
	title="Consulta tu Boleta | Fundación Funcrees Colombia"
	description="Consulta el estado de tu boleta solidaria con tu código de verificación. Eventos y rifas de la Fundación Funcrees Colombia en Sincelejo."
	path="/boletas"
/>

<section class="view-section active" style="padding: 4rem 1rem 3rem; background: var(--bg-secondary);">
	<div style="max-width: 720px; margin: 0 auto;">
		<div class="section-header" style="margin-bottom: 2.5rem;">
			<span class="section-subtitle">Eventos Solidarios</span>
			<h1 class="section-title">Consulta tu Boleta</h1>
			<p class="section-description">
				¿Compraste una boleta para nuestro bingo, rifa o campaña? Ingresa el
				<strong>código de verificación</strong> de 10 caracteres que recibiste por WhatsApp
				o correo, y verifica aquí el estado de tu compra.
			</p>
		</div>

		<div class="boletas-card">
			<form class="boletas-form" onsubmit={handleConsulta} aria-describedby="boletas-ayuda">
				<div class="form-group" style="margin-bottom: 0;">
					<label class="form-label" for="boleta-codigo">Código de Verificación:</label>
					<div class="boletas-input-row">
						<input
							type="text"
							id="boleta-codigo"
							bind:value={codigo}
							oninput={handleInput}
							class="form-input boletas-codigo-input"
							placeholder="A1B2C3D4E5"
							maxlength="10"
							autocomplete="off"
							spellcheck="false"
							aria-required="true"
							required
						/>
						<button type="submit" class="btn btn-primary boletas-btn" disabled={isConsultando}>
							{#if isConsultando}
								<i class="fa-solid fa-spinner fa-spin"></i> Consultando...
							{:else}
								<i class="fa-solid fa-magnifying-glass"></i> Consultar
							{/if}
						</button>
					</div>
					<p id="boletas-ayuda" class="boletas-ayuda">
						<i class="fa-solid fa-circle-info"></i> El código llega junto a tu boleta al confirmar la compra.
					</p>
				</div>
			</form>

			{#if errorConsulta}
				<div class="boletas-alerta boletas-alerta-error" role="alert">
					<i class="fa-solid fa-triangle-exclamation"></i>
					<div>
						<strong>No se pudo consultar.</strong> {errorConsulta}
					</div>
				</div>
			{/if}

			{#if notFound}
				<div class="boletas-alerta boletas-alerta-aviso" role="status">
					<i class="fa-solid fa-ticket-simple"></i>
					<div>
						<strong>No encontramos una boleta con el código <code>{ultimoCodigo}</code>.</strong>
						<br />Verifica que esté completo y sin espacios. Si acabas de comprar, el registro
						puede tardar unos minutos. Ante dudas, escríbenos al
						<a href="https://wa.me/573137924439" target="_blank" rel="noopener noreferrer">WhatsApp +57 313 792 4439</a>.
					</div>
				</div>
			{/if}

			{#if ticket}
				<article class="boletas-resultado" aria-live="polite">
					<header class="boletas-resultado-header">
						<div>
							<span class="boletas-evento-label"><i class="fa-solid fa-calendar-star"></i> {ticket.evento_titulo}</span>
							<h2 class="boletas-numero">Boleta N.º {ticket.numero_ticket}</h2>
							<span class="boletas-comprador">A nombre de: <strong>{ticket.comprador_nombre}</strong></span>
						</div>
						<span class="boletas-badge {ESTADO_META[ticket.estado_pago]?.css ?? ''}">
							<i class="fa-solid {ESTADO_META[ticket.estado_pago]?.icon ?? 'fa-circle-question'}"></i>
							{ESTADO_META[ticket.estado_pago]?.label ?? ticket.estado_pago}
						</span>
					</header>

					<footer class="boletas-resultado-footer">
						<span><i class="fa-solid fa-tags"></i> Valor: <strong>{fmtCOP(ticket.monto_pagado)} COP</strong></span>
						<span><i class="fa-solid fa-hashtag"></i> Referencia interna: <code class="boletas-codigo-chip">{ticket.id.slice(0, 8).toUpperCase()}</code></span>
					</footer>

					{#if ticket.estado_pago === 'pendiente'}
						<p class="boletas-nota-estado">
							<i class="fa-solid fa-hourglass-half"></i> Tu pago aún se está confirmando.
							Si pagaste por Wompi, la confirmación puede tardar unos minutos; si pagaste
							por transferencia, nosotros la verificamos manualmente en horario hábil.
						</p>
					{:else if ticket.estado_pago === 'pagado'}
						<p class="boletas-nota-estado boletas-nota-ok">
							<i class="fa-solid fa-circle-check"></i> ¡Gracias por apoyar a nuestros abuelitos!
							Conserve su código de verificación: lo necesitará para ingresar al evento y reclamar premios.
						</p>
					{/if}
				</article>
			{/if}
		</div>

		<aside class="boletas-privacidad">
			<h2><i class="fa-solid fa-shield-halved"></i> Tu privacidad</h2>
			<p>
				Solo puedes consultar una boleta con su código exacto: no hay listados públicos de
				compradores. Tratamos tu nombre y teléfono conforme a la
				<a href="/privacidad">Política de Privacidad (Ley 1581 de 2012)</a> — el teléfono se
				almacena cifrado.
			</p>
		</aside>
	</div>
</section>

<style>
	/* Tarjeta principal de consulta */
	.boletas-card {
		background: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-lg);
		padding: 1.75rem;
		box-shadow: var(--shadow-md);
	}

	.boletas-input-row {
		display: flex;
		gap: 0.75rem;
		flex-wrap: wrap;
	}

	.boletas-codigo-input {
		flex: 1 1 220px;
		font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, monospace;
		font-size: 1.15rem;
		font-weight: 700;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		text-align: center;
	}

	.boletas-btn {
		flex: 0 0 auto;
		padding: 0.85rem 1.6rem;
		min-height: 44px; /* objetivo táctil WCAG */
	}

	.boletas-btn:disabled {
		opacity: 0.65;
		cursor: progress;
	}

	.boletas-ayuda {
		margin-top: 0.6rem;
		font-size: 0.82rem;
		color: var(--text-muted);
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	/* Alertas */
	.boletas-alerta {
		display: flex;
		gap: 0.75rem;
		align-items: flex-start;
		padding: 0.9rem 1rem;
		border-radius: 10px;
		font-size: 0.9rem;
		margin-top: 1.1rem;
		line-height: 1.5;
	}

	.boletas-alerta code {
		font-weight: 700;
		letter-spacing: 0.1em;
	}

	.boletas-alerta-error {
		background: #fef2f2;
		border: 1px solid #fca5a5;
		color: #991b1b;
	}

	.boletas-alerta-aviso {
		background: #fffbeb;
		border: 1px solid #fcd34d;
		color: #92400e;
	}

	.boletas-alerta a {
		color: inherit;
		font-weight: 600;
		text-decoration: underline;
	}

	/* Resultado: tarjeta tipo "boleto" con borde superior de marca */
	.boletas-resultado {
		margin-top: 1.4rem;
		border: 2px solid var(--primary);
		border-radius: 14px;
		overflow: hidden;
		animation: boletas-aparecer 0.35s ease both;
	}

	@keyframes boletas-aparecer {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.boletas-resultado-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
		padding: 1.25rem 1.4rem;
		background: var(--primary-trans);
		flex-wrap: wrap;
	}

	.boletas-evento-label {
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--primary);
		font-weight: 700;
		display: inline-flex;
		gap: 0.4rem;
		align-items: center;
	}

	.boletas-numero {
		margin: 0.3rem 0 0.2rem;
		font-size: 1.6rem;
		line-height: 1.15;
		color: var(--text-main);
	}

	.boletas-comprador {
		font-size: 0.92rem;
		color: var(--text-muted);
	}

	/* Badge de estado */
	.boletas-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		padding: 0.45rem 0.9rem;
		border-radius: 999px;
		font-size: 0.85rem;
		font-weight: 700;
		white-space: nowrap;
	}

	.badge-pagado {
		background: #dcfce7;
		color: #166534;
		border: 1px solid #86efac;
	}

	.badge-pendiente {
		background: #fef9c3;
		color: #854d0e;
		border: 1px solid #fde047;
		animation: boletas-latido 2.2s ease-in-out infinite;
	}

	.badge-cancelado {
		background: #fee2e2;
		color: #991b1b;
		border: 1px solid #fca5a5;
	}

	@keyframes boletas-latido {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.75;
		}
	}

	.boletas-resultado-footer {
		display: flex;
		gap: 1.5rem;
		flex-wrap: wrap;
		padding: 1rem 1.4rem;
		border-top: 1px dashed var(--border-color);
		font-size: 0.92rem;
		color: var(--text-muted);
	}

	.boletas-codigo-chip {
		background: var(--primary-soft);
		border: 1px solid var(--border-color);
		border-radius: 6px;
		padding: 0.15rem 0.5rem;
		font-weight: 700;
		letter-spacing: 0.1em;
	}

	.boletas-nota-estado {
		margin: 0;
		padding: 0.9rem 1.4rem 1.2rem;
		font-size: 0.88rem;
		color: var(--text-muted);
		display: flex;
		gap: 0.55rem;
		align-items: flex-start;
	}

	.boletas-nota-estado i {
		margin-top: 0.15rem;
		color: var(--primary);
	}

	/* Nota de privacidad */
	.boletas-privacidad {
		margin-top: 1.5rem;
		padding: 1.1rem 1.3rem;
		background: var(--bg-card);
		border-radius: 12px;
		font-size: 0.86rem;
		color: var(--text-muted);
		line-height: 1.6;
	}

	.boletas-privacidad h2 {
		font-size: 0.95rem;
		margin: 0 0 0.4rem;
		color: var(--text-main);
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.boletas-privacidad a {
		color: var(--primary);
		font-weight: 600;
	}

	/* Respeto a reduce-motion (WCAG 2.1) */
	@media (prefers-reduced-motion: reduce) {
		.boletas-resultado,
		.badge-pendiente {
			animation: none;
		}
	}

	@media (max-width: 480px) {
		.boletas-card {
			padding: 1.25rem;
		}

		.boletas-input-row {
			flex-direction: column;
		}

		.boletas-btn {
			width: 100%;
		}

		.boletas-resultado-header {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
