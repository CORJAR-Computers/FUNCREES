<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	let showScrollTop = $state(false);

	function checkScroll(): void {
		if (browser) {
			showScrollTop = window.scrollY > 300;
		}
	}

	function scrollToTop(): void {
		if (browser) {
			window.scrollTo({ top: 0, behavior: 'smooth' });
		}
	}

	onMount(() => {
		if (browser) {
			window.addEventListener('scroll', checkScroll, { passive: true });
			return () => window.removeEventListener('scroll', checkScroll);
		}
	});
</script>

<!-- Botón Scroll to Top -->
{#if showScrollTop}
	<button
		type="button"
		class="scroll-top active"
		aria-label="Volver al inicio de la página"
		title="Volver arriba"
		onclick={scrollToTop}
	>
		<i class="fa-solid fa-chevron-up" aria-hidden="true"></i>
		<span class="scroll-top__tooltip">Volver arriba</span>
	</button>
{/if}

<!-- Botón Flotante de WhatsApp -->
<a
	href="https://wa.me/573137924439?text=Hola%20Fundaci%C3%B3n%20FUNCREESCOLOMBIA%2C%20quisiera%20saber%20m%C3%A1s%20sobre%20c%C3%B3mo%20puedo%20apoyar."
	target="_blank"
	rel="noopener noreferrer"
	class="whatsapp-float"
	aria-label="Contactar por WhatsApp"
	title="Chatear con nosotros"
>
	<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" width="28" height="28">
		<path fill="#ffffff" d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946C.06 5.348 5.397.01 12.008.01c3.202.001 6.212 1.246 8.477 3.514 2.266 2.268 3.507 5.28 3.505 8.484-.004 6.657-5.34 11.997-11.953 11.997-2.005-.001-3.973-.502-5.724-1.455L0 24zm6.835-3.321c1.644.976 3.51 1.49 5.409 1.491 5.541 0 10.051-4.506 10.054-10.047a9.92 9.92 0 0 0-2.93-7.11 9.925 9.925 0 0 0-7.114-2.923C6.722 2.093 2.212 6.6 2.209 12.14c0 1.95.509 3.856 1.478 5.525L2.732 21.69l4.16-1.011zm12.022-7.234c-.329-.164-1.948-.961-2.247-1.07-.3-.11-.518-.164-.735.164-.217.329-.841 1.07-1.031 1.288-.19.218-.38.245-.71.082-.329-.164-1.389-.512-2.647-1.633-.978-.873-1.637-1.95-1.829-2.28-.192-.329-.02-.507.145-.671.148-.147.329-.384.494-.576.164-.192.219-.329.329-.548.11-.219.055-.411-.028-.576-.082-.164-.735-1.771-1.007-2.43-.265-.636-.53-.55-.735-.56-.19-.007-.408-.007-.626-.007-.218 0-.571.082-.871.411-.3.329-1.147 1.122-1.147 2.736 0 1.614 1.174 3.175 1.338 3.394.164.22 2.313 3.532 5.6 4.951.782.338 1.39.54 1.868.692.788.25 1.505.215 2.07.13.63-.094 1.948-.795 2.222-1.564.275-.769.275-1.428.193-1.563-.083-.136-.3-.219-.629-.383z" />
	</svg>
	<span class="whatsapp-tooltip">¿Cómo podemos ayudarte?</span>
</a>
