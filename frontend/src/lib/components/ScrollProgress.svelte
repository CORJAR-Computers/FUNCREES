<script lang="ts">
	import { onMount } from 'svelte';

	/**
	 * Barra de progreso de lectura (site-wide):
	 * - Línea de 3px en el borde superior que crece con el scroll.
	 * - Refuerza la sensación de profundidad del sitio (historias, legales,
	 *   eventos largos) sin distraer: usa el verde institucional.
	 * - Solo se activa en cliente (window) y es puramente decorativa:
	 *   aria-hidden y role="presentation" para no ensuciar el árbol a11y.
	 * - respeta prefers-reduced-motion: sin transición (el ancho cambia seco).
	 */

	let progreso = $state(0);

	function medir(): void {
		const doc = document.documentElement;
		const total = doc.scrollHeight - window.innerHeight;
		progreso = total > 0 ? Math.min(1, Math.max(0, window.scrollY / total)) : 0;
	}

	onMount(() => {
		medir();
		window.addEventListener('scroll', medir, { passive: true });
		window.addEventListener('resize', medir, { passive: true });
		return () => {
			window.removeEventListener('scroll', medir);
			window.removeEventListener('resize', medir);
		};
	});
</script>

<div class="scroll-progress" role="presentation" aria-hidden="true">
	<div class="scroll-progress__bar" style="transform: scaleX({progreso})"></div>
</div>

<style>
	.scroll-progress {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		z-index: 1101; /* sobre el navbar sticky (1000) */
		background: transparent;
		pointer-events: none;
	}
	.scroll-progress__bar {
		height: 100%;
		width: 100%;
		transform-origin: 0 50%;
		transform: scaleX(0);
		background: linear-gradient(
			90deg,
			var(--primary) 0%,
			color-mix(in srgb, var(--primary) 70%, var(--accent, #8bc34a)) 100%
		);
		transition: transform 90ms linear;
	}
	@media (prefers-reduced-motion: reduce) {
		.scroll-progress__bar {
			transition: none;
		}
	}
</style>
