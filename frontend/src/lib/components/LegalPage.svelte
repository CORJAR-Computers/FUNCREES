<script lang="ts">
        import type { Snippet } from 'svelte';
        import Seo from '$lib/components/Seo.svelte';

        interface Props {
                title: string;
                description: string;
                /** Ruta canónica para SEO (ej: "/privacidad"). */
                path: string;
                /** Fecha de última actualización mostrada al lector (texto libre). */
                updated: string;
                /** Contenido del documento legal (snippets de la página). */
                children?: Snippet;
        }

        const { title, description, path, updated, children }: Props = $props();
</script>

<Seo {title} {description} {path} />

<section class="legal-page">
        <div class="legal-container">
                <header class="section-header legal-header">
                        <span class="section-subtitle">Información Legal</span>
                        <h1 class="section-title">{title}</h1>
                        <p class="legal-updated">
                                <i class="fa-regular fa-calendar-check" aria-hidden="true"></i>
                                Última actualización: <strong>{updated}</strong>
                        </p>
                </header>

                <article class="legal-prose">
                        {@render children?.()}
                </article>

                <div class="legal-contact-box">
                        <h2>¿Dudas sobre este documento?</h2>
                        <p>
                                Escríbenos a
                                <a href="mailto:fundacioncreceunaesperanza@gmail.com">fundacioncreceunaesperanza@gmail.com</a>
                                o llámanos/WhatsApp al <a href="tel:+573137924439">+57 313 792 4439</a>.
                        </p>
                        <p class="legal-contact-addr">
                                Fundación Crece Una Esperanza Social (FUNCREES) · NIT 902036173-3 ·
                                Carrera 15b #41c - 07, Sincelejo, Sucre, Colombia
                        </p>
                </div>
        </div>
</section>
