<script lang="ts">
	import { PROYECTOS, getTagClass } from '$lib/data/proyectos';
	import type { Proyecto } from '$lib/data/proyectos';
	import Seo from '$lib/components/Seo.svelte';
	import Modal from '$lib/components/Modal.svelte';

	let searchQuery = $state('');
	let selectedTag = $state('Todos');
	let selectedProject = $state<Proyecto | null>(null);

	const tags = [
		'Todos',
		'Adulto Mayor',
		'Juventud',
		'Mujer Rural',
		'Educación',
		'Soberanía Alimentaria',
		'Cultura',
		'Ecología',
		'Emprendimiento',
		'Bienestar Animal'
	];

	let filteredProjects = $derived(
		PROYECTOS.filter((p) => {
			const matchesTag = selectedTag === 'Todos' || p.tag === selectedTag;
			const query = searchQuery.toLowerCase().trim();
			const matchesSearch =
				!query ||
				p.title.toLowerCase().includes(query) ||
				p.desc.toLowerCase().includes(query) ||
				p.tag.toLowerCase().includes(query) ||
				(p.slogan && p.slogan.toLowerCase().includes(query));
			return matchesTag && matchesSearch;
		})
	);

	function openProjectModal(project: Proyecto): void {
		selectedProject = project;
	}

	function closeProjectModal(): void {
		selectedProject = null;
	}

	function clearFilters(): void {
		searchQuery = '';
		selectedTag = 'Todos';
	}
</script>

<Seo
	title="Nuestros Proyectos | Fundación Funcrees Colombia"
	description="Explora los proyectos sociales de Funcrees Colombia: atención al adulto mayor, empoderamiento juvenil, soberanía alimentaria y bienestar comunitario en Sucre."
	path="/proyectos"
/>

<section id="nuestros-proyectos" class="view-section active">
	<div class="section">
		<div class="section-header">
			<span class="section-subtitle">Impacto Sostenible</span>
			<h1 class="section-title">Nuestros Proyectos Sociales</h1>
			<p class="section-description">
				Modelos de intervención integral diseñados para transformar comunidades desde la raíz, fomentando autonomía y dignidad.
			</p>
		</div>

		<!-- Barra de Búsqueda y Filtros -->
		<div style="max-width: 900px; margin: 0 auto 2.5rem; display: flex; flex-direction: column; gap: 1.25rem;">
			<div style="position: relative; width: 100%;">
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Buscar proyecto por nombre, palabra clave o impacto..."
					class="form-control"
					style="padding-left: 2.75rem; padding-right: 2.5rem; font-size: 1rem; border-radius: 9999px;"
				/>
				<i class="fa-solid fa-magnifying-glass" style="position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
				{#if searchQuery}
					<button
						onclick={() => searchQuery = ''}
						style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); background: transparent; border: none; font-size: 1.2rem; cursor: pointer; color: var(--text-muted);"
						aria-label="Limpiar búsqueda"
					>×</button>
				{/if}
			</div>

			<!-- Filtros por Categoría -->
			<div style="display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center;">
				{#each tags as tag}
					<button
						class="evento-filter-btn"
						class:active={selectedTag === tag}
						onclick={() => selectedTag = tag}
					>
						{tag}
					</button>
				{/each}
			</div>

			<!-- Contador de Resultados -->
			<div style="text-align: center; font-size: 0.9rem; color: var(--text-muted);">
				{#if filteredProjects.length === PROYECTOS.length}
					Mostrando todos los {PROYECTOS.length} proyectos
				{:else}
					Mostrando {filteredProjects.length} de {PROYECTOS.length} proyectos
				{/if}
			</div>
		</div>

		<!-- Grilla de Proyectos -->
		{#if filteredProjects.length > 0}
			<div class="proyectos-grid" id="proyectos-grid-container">
				{#each filteredProjects as proj (proj.id)}
					<div class="proyecto-card">
						<div class="proyecto-img-container">
							<span class="proyecto-tag ptag {getTagClass(proj.tag)}">{proj.tag}</span>
							<img
								class="proyecto-img"
								src={proj.img}
								alt={proj.title}
								loading="lazy"
							/>
						</div>
						<div class="proyecto-info">
							{#if proj.slogan}
								<p class="proyecto-slogan">{proj.slogan}</p>
							{/if}
							<h3 class="proyecto-title">{proj.title}</h3>
							<p class="proyecto-desc">{proj.desc}</p>
							<button
								class="btn btn-outline btn-text-explorar"
								style="margin-top: auto;"
								onclick={() => openProjectModal(proj)}
							>
								Explorar Proyecto +
							</button>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<div class="section-empty-state">
				<div class="section-empty-icon"><i class="fa-solid fa-folder-open"></i></div>
				<h3 class="section-empty-title">No se encontraron proyectos</h3>
				<p class="section-empty-desc">Ningún proyecto coincide con los criterios de búsqueda.</p>
				<button class="btn btn-outline" onclick={clearFilters}>Limpiar Filtros</button>
			</div>
		{/if}
	</div>
</section>

<!-- Modal de Detalle del Proyecto -->
{#if selectedProject}
	<Modal open={!!selectedProject} onclose={closeProjectModal} labelledby="proyecto-modal-title">
		<div style="max-height: 75vh; overflow-y: auto; padding-right: 0.5rem;">
			<span class="proyecto-tag ptag {getTagClass(selectedProject.tag)}" style="display: inline-block; margin-bottom: 1rem;">
				{selectedProject.tag}
			</span>
			<h2 id="proyecto-modal-title" style="color: var(--secondary); margin-bottom: 0.75rem;">{selectedProject.title}</h2>
			{#if selectedProject.slogan}
				<p style="font-style: italic; color: var(--primary-dark); font-weight: 600; margin-bottom: 1.25rem;">
					"{selectedProject.slogan}"
				</p>
			{/if}
			<img
				src={selectedProject.img}
				alt={selectedProject.title}
				style="width: 100%; max-height: 320px; object-fit: cover; border-radius: 12px; margin-bottom: 1.5rem;"
			/>
			<h4 style="margin-bottom: 0.5rem; color: var(--text);">Descripción del Programa</h4>
			<p style="color: var(--text-muted); line-height: 1.7; margin-bottom: 2rem;">
				{selectedProject.desc}
			</p>
			<div style="display: flex; gap: 1rem; flex-wrap: wrap;">
				<a href="/donaciones" class="btn btn-primary" onclick={closeProjectModal}>
					Apoyar Este Proyecto 🤝
				</a>
				<button class="btn btn-outline" onclick={closeProjectModal}>Cerrar</button>
			</div>
		</div>
	</Modal>
{/if}
