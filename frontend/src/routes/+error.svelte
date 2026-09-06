<script lang="ts">
	import { page } from '$app/state';
</script>

<section class="error-page">
	<div class="error-card">
		<span class="error-code">{page.status}</span>
		<h1 class="error-title">
			{page.status === 404 ? 'Página no encontrada' : 'Algo salió mal'}
		</h1>
		<p class="error-desc">
			{page.status === 404
				? 'La página que buscas no existe o fue movida. Pero hay muchas formas de sembrar esperanza hoy.'
				: 'Ocurrió un error inesperado. Nuestro equipo ya fue notificado; por favor intenta nuevamente en unos minutos.'}
		</p>
		<div class="error-actions">
			<a href="/" class="btn btn-primary">Volver al Inicio</a>
			<a href="/donaciones" class="btn btn-outline">Quiero Donar 🤝</a>
		</div>
	</div>
</section>

<style>
	.error-page {
		min-height: 70vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 4rem 1rem;
		background: var(--bg-secondary);
	}
	.error-card {
		text-align: center;
		max-width: 560px;
		background: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		padding: 3.5rem 2.5rem;
	}
	.error-code {
		display: block;
		font-family: var(--font-heading, 'Outfit', sans-serif);
		font-size: 5rem;
		font-weight: 800;
		line-height: 1;
		color: var(--primary);
		margin-bottom: 0.5rem;
	}
	.error-title {
		color: var(--secondary);
		font-size: 1.6rem;
		margin-bottom: 0.75rem;
	}
	.error-desc {
		color: var(--text-muted);
		line-height: 1.6;
		margin-bottom: 2rem;
	}
	.error-actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}
</style>
