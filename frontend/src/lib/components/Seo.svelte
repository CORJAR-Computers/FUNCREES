<script lang="ts">
        import { SITE_NAME, SITE_URL, SITE_OG_IMAGE } from '$lib/seo';

        interface Props {
                title: string;
                description: string;
                /** Ruta canónica, ej: "/donaciones". Default: la ruta actual. */
                path?: string;
                /** Datos JSON-LD adicionales (schema.org) específicos de la página. */
                jsonLd?: Record<string, unknown>;
        }

        const { title, description, path = '', jsonLd = undefined }: Props = $props();

        const canonical = $derived(`${SITE_URL}${path}`);
        const orgLd = {
                '@context': 'https://schema.org',
                '@type': 'NGO',
                name: SITE_NAME,
                url: SITE_URL,
                logo: `${SITE_URL}/assets/logo-512.png`,
                image: SITE_OG_IMAGE,
                address: {
                        '@type': 'PostalAddress',
                        streetAddress: 'Carrera 15b #41c - 07',
                        addressLocality: 'Sincelejo',
                        addressRegion: 'Sucre',
                        addressCountry: 'CO'
                },
                telephone: '+57 313 792 4439',
                email: 'fundacioncreceunaesperanza@gmail.com',
                sameAs: [
                        'https://www.facebook.com/Funcreescolombia',
                        'https://www.instagram.com/funcreescolombia2026'
                ]
        };
</script>

<svelte:head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <link rel="canonical" href={canonical} />

        <!-- Open Graph -->
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content={SITE_NAME} />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:url" content={canonical} />
        <meta property="og:image" content={SITE_OG_IMAGE} />
        <meta property="og:locale" content="es_CO" />

        <!-- Twitter Card -->
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <meta name="twitter:image" content={SITE_OG_IMAGE} />

        {@html `<script type="application/ld+json">${JSON.stringify([orgLd, ...(jsonLd ? [jsonLd] : [])])}<\/script>`}
</svelte:head>
