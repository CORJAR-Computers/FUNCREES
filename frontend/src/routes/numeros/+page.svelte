<script lang="ts">
	import Seo from '$lib/components/Seo.svelte';
	import { mapStatsToCards } from '$lib/api/client';
	import { formatMoneyNumber } from '$lib/utils/currency';

	interface Props {
		data: { cifras: import('$lib/types').PublicStats; usingFallback: boolean };
	}

	let { data }: Props = $props();

	let cifras = $derived(data.cifras);
	let tarjetas = $derived(mapStatsToCards(cifras));
	let serie = $derived(cifras.serie_mensual);

	/** Fecha legible de última actualización: "5 de septiembre de 2026, 14:32". */
	let actualizadoLegible = $derived.by(() => {
		const d = new Date(cifras.actualizado_en);
		if (Number.isNaN(d.getTime())) return '';
		// toLocaleString puede terminar en punto ("... 07:03 p. m."): se quita
		// para no duplicarlo con el punto final de la oración.
		return d
			.toLocaleString('es-CO', {
				day: 'numeric',
				month: 'long',
				year: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			})
			.replace(/\.$/, '');
	});

	/** Etiqueta accesible del gráfico, en texto plano. */
	let ariaSerie = $derived(
		serie.map((m) => `${m.mes} ${m.anio}: ${m.total_fmt_corto}`).join(', ')
	);
</script>

<Seo
	title="Nuestros Números | Fundación Funcrees Colombia"
	description="Transparencia en cifras: total recaudado, donaciones confirmadas mes a mes, adultos mayores acompañados y apadrinamientos activos de la Fundación Funcrees Colombia."
	path="/numeros"
/>

<section id="numeros" class="view-section active">
	<div class="section">
		<div class="section-header">
			<span class="section-subtitle">Transparencia</span>
			<h1 class="section-title">Nuestros Números</h1>
			<p class="section-description">
				Rendimos cuentas con datos reales: cada cifra proviene de donaciones
				<strong>confirmadas por la pasarela de pagos</strong>, no de promesas pendientes.
			</p>
			{#if data.usingFallback}
				<p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
					<i class="fa-solid fa-circle-info"></i> No se pudo conectar con el servidor en este
					momento — las cifras se mostrarán en cuanto se restablezca la conexión.
				</p>
			{/if}
		</div>

		<!-- Tarjetas de cifras destacadas -->
		<div class="numeros-grid">
			{#each tarjetas as t (t.key)}
				<div class="numeros-card">
					<div class="numeros-card-icon"><i class={t.icon}></i></div>
					<p class="numeros-card-value">{t.value}</p>
					<p class="numeros-card-label">{t.label}</p>
				</div>
			{/each}
		</div>

		<!-- Gráfico: recaudado por mes (últimos 12 meses) -->
		{#if serie.length > 0}
			<div class="numeros-chart-card">
				<h2 class="numeros-chart-title">
					<i class="fa-solid fa-chart-column"></i>
					Recaudado por mes — últimos 12 meses
				</h2>
				<div
					class="numeros-chart"
					role="img"
					aria-label="Gráfico de barras del total recaudado por mes. {ariaSerie}."
				>
					{#each serie as m, i (m.anio + '-' + m.mes)}
						<div class="numeros-col" class:actual={m.es_actual}>
							<span class="numeros-col-value">{m.total_fmt_corto}</span>
							<div class="numeros-bar-area">
								<div
									class="numeros-bar"
									style="height: {m.pct}%; min-height: {m.pct > 0 ? '6px' : '3px'};"
									title="{m.mes} {m.anio}: {m.total_fmt} COP en {formatMoneyNumber(m.cantidad)} donaci{m.cantidad === 1 ? 'ón' : 'ones'}"
								></div>
							</div>
							<span class="numeros-col-label">{m.mes}</span>
							<span class="numeros-col-anio">{m.anio}</span>
						</div>
					{/each}
				</div>
				<p class="numeros-chart-hint">
					Mes destacado: el período en curso. Pasa el cursor sobre cada barra para ver el detalle.
				</p>
			</div>
		{/if}

		<!-- Nota de alcance -->
		<div class="numeros-nota">
			<p>
				<i class="fa-solid fa-shield-heart"></i>
				Datos agregados de la Fundación: {cifras.recaudado_total_fmt} COP recaudados en
				{formatMoneyNumber(cifras.donaciones_count)}
				donaci{cifras.donaciones_count === 1 ? 'ón' : 'ones'} confirmada{cifras.donaciones_count === 1 ? '' : 's'}
				{#if cifras.donaciones_count > 0}(promedio: {cifras.donacion_promedio_fmt} COP){/if}.
				Este panel se actualiza automáticamente con cada donación confirmada.
				{#if actualizadoLegible}Última actualización: {actualizadoLegible}.{/if}
			</p>
			<a href="/donaciones" class="btn btn-primary">Quiero Donar Ahora</a>
		</div>
	</div>
</section>
