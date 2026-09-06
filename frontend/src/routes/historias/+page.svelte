<script lang="ts">
	import { toast } from '$lib/stores/toast.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import Modal from '$lib/components/Modal.svelte';
	import type { UiBeneficiary } from '$lib/types';

	interface Props {
		data: { abuelitos: UiBeneficiary[]; usingFallback: boolean };
	}

	let { data }: Props = $props();

	let abuelitos = $derived(data.abuelitos);
	let searchQuery = $state('');
	let selectedAbuelito = $state<UiBeneficiary | null>(null);

	let filteredAbuelitos = $derived(
		abuelitos.filter((ab) => {
			const q = searchQuery.toLowerCase().trim();
			if (!q) return true;
			const searchable = `${ab.nombre} ${ab.testimonio} ${ab.historia} ${ab.ciudad}`.toLowerCase();
			return searchable.includes(q);
		})
	);

	function openStoryModal(abuelito: UiBeneficiary): void {
		selectedAbuelito = abuelito;
	}

	function closeStoryModal(): void {
		selectedAbuelito = null;
	}

	function clearSearch(): void {
		searchQuery = '';
	}

	/** Deep-link a donaciones con el beneficiario preseleccionado. */
	function apadrinar(ab: UiBeneficiary): void {
		closeStoryModal();
		toast.show(`Vinculando apadrinamiento para: ${ab.nombre}`, 'success');
	}
</script>

<Seo
	title="Historias de Vida | Fundación Funcrees Colombia"
	description="Conoce los rostros, testimonios e historias de vida de nuestros adultos mayores en Sincelejo y Sucre. Apadrina hoy y transforma un destino."
	path="/historias"
/>

<section id="historias-de-vida" class="view-section active">
	<div class="section">
		<div class="section-header">
			<span class="section-subtitle">Vidas que Inspiran</span>
			<h1 class="section-title">Historias de Vida y Sabiduría</h1>
			<p class="section-description">
				Detrás de cada arruga hay una historia de esfuerzo. Conoce a nuestros abuelitos y descubre cómo tu solidaridad dignifica su presente.
			</p>
			{#if data.usingFallback}
				<p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
					<i class="fa-solid fa-circle-info"></i> Mostrando perfiles de referencia — no se pudo conectar con el servidor en este momento.
				</p>
			{/if}
		</div>

		<!-- Buscador de Abuelitos -->
		<div style="max-width: 650px; margin: 0 auto 2.5rem; display: flex; flex-direction: column; gap: 1rem;">
			<div style="position: relative; width: 100%;">
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Buscar abuelito por nombre, historia o municipio..."
					class="form-control"
					style="padding-left: 2.75rem; padding-right: 2.5rem; font-size: 1rem; border-radius: 9999px;"
				/>
				<i class="fa-solid fa-magnifying-glass" style="position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
				{#if searchQuery}
					<button
						onclick={clearSearch}
						style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); background: transparent; border: none; font-size: 1.2rem; cursor: pointer; color: var(--text-muted);"
						aria-label="Limpiar búsqueda"
					>×</button>
				{/if}
			</div>

			<div style="text-align: center; font-size: 0.9rem; color: var(--text-muted);">
				{#if filteredAbuelitos.length === abuelitos.length}
					Mostrando todos los {abuelitos.length} abuelitos
				{:else}
					Mostrando {filteredAbuelitos.length} de {abuelitos.length} abuelitos
				{/if}
			</div>
		</div>

		<!-- Grilla de Abuelitos -->
		{#if filteredAbuelitos.length > 0}
			<div class="abuelitos-grid" id="abuelitos-grid-container">
				{#each filteredAbuelitos as ab (ab.id)}
					<div class="abuelito-card">
						<div class="abuelito-img-box">
							<img
								class="abuelito-img"
								src={ab.img}
								alt={ab.nombre}
								loading="lazy"
							/>
							<div class="abuelito-overlay-info">
								<h3 class="abuelito-nombre">{ab.nombre}</h3>
								<div class="abuelito-meta">
									<span>{ab.edad} Años</span>
									<span>•</span>
									<span>{ab.ciudad || 'Sincelejo'}</span>
								</div>
							</div>
						</div>
						<div class="abuelito-details">
							<p class="abuelito-testimonio">"{ab.testimonio}"</p>
							<button
								class="btn btn-primary"
								style="margin-top: auto;"
								onclick={() => openStoryModal(ab)}
							>
								Conocer su Historia +
							</button>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<div class="section-empty-state">
				<div class="section-empty-icon"><i class="fa-solid fa-heart-crack"></i></div>
				<h3 class="section-empty-title">No se encontraron abuelitos</h3>
				<p class="section-empty-desc">Ningún perfil coincide con tu búsqueda.</p>
				<button class="btn btn-outline" onclick={clearSearch}>Ver Todos</button>
			</div>
		{/if}
	</div>
</section>

<!-- Modal de Historia Completa -->
{#if selectedAbuelito}
	<Modal open={!!selectedAbuelito} onclose={closeStoryModal} labelledby="story-modal-title">
		<div class="modal-body-story">
			<div class="modal-story-banner">
				<img
					class="modal-story-img"
					src={selectedAbuelito.img}
					alt={selectedAbuelito.nombre}
				/>
				<div class="modal-story-meta">
					<h2 class="abuelito-nombre" id="story-modal-title" style="font-size: 2rem; margin-bottom: 0.4rem; color: #fff;">
						{selectedAbuelito.nombre}
					</h2>
					<div class="abuelito-meta" style="color: rgba(255, 255, 255, 0.9);">
						<span>Edad: {selectedAbuelito.edad} años</span>
						<span>•</span>
						<span>Ciudad: {selectedAbuelito.ciudad || 'Sincelejo, Sucre'}</span>
					</div>
				</div>
			</div>

			<div class="modal-story-content">
				<h3 style="color: var(--secondary); margin-bottom: 1rem; font-size: 1.3rem;">Historia de Vida</h3>
				<div class="modal-story-biografia">
					<p style="line-height: 1.7; color: var(--text);">{selectedAbuelito.historia}</p>
					<p style="font-style: italic; margin-top: 1.5rem; color: var(--primary-dark); border-left: 3px solid var(--primary); padding-left: 1rem;">
						"{selectedAbuelito.testimonio}"
					</p>
				</div>

				<div style="display: flex; gap: 1rem; margin-top: 2rem; flex-wrap: wrap;">
					<a
						href="/donaciones?beneficiario={selectedAbuelito.id}&nombre={encodeURIComponent(selectedAbuelito.nombre)}"
						class="btn btn-primary"
						style="flex: 1; min-width: 200px; text-align: center;"
						onclick={() => apadrinar(selectedAbuelito!)}
					>
						🤝 Apadrinar a {selectedAbuelito.nombre.split(' ')[0]}
					</a>
					<button class="btn btn-outline" style="flex: 1; min-width: 120px;" onclick={closeStoryModal}>
						Volver
					</button>
				</div>
			</div>
		</div>
	</Modal>
{/if}
