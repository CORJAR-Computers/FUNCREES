<script lang="ts">
	import '../lib/styles/base.css';
	import '../lib/styles/components.css';
	import '../lib/styles/themes.css';
	import '../lib/styles/responsive.css';

	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';
	import CookieBanner from '$lib/components/CookieBanner.svelte';
	import AccessibilityWidget from '$lib/components/AccessibilityWidget.svelte';
	import FloatingActions from '$lib/components/FloatingActions.svelte';

	let { children } = $props();
</script>

<a href="#main-content" class="skip-link">
	Saltar al contenido principal
</a>

<Navbar />

<main class="main-content" id="main-content" tabindex="-1">
	{@render children()}
</main>

<Footer />

<!-- Componentes Flotantes Globales -->
<ToastContainer />
<AccessibilityWidget />
<FloatingActions />
<CookieBanner />
