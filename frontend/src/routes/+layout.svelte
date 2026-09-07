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
        import ScrollProgress from '$lib/components/ScrollProgress.svelte';

        const { children } = $props();
</script>

<svelte:head>
        <!-- Autodescubrimiento del calendario suscribible (iCalendar/RFC 5545):
             clientes y extensiones lo detectan como un feed más del sitio. -->
        <link
                rel="alternate"
                type="text/calendar; charset=utf-8"
                title="Eventos FUNCREES Colombia"
                href="/calendario.ics"
        />
</svelte:head>

<a href="#main-content" class="skip-link">
        Saltar al contenido principal
</a>

<ScrollProgress />

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
