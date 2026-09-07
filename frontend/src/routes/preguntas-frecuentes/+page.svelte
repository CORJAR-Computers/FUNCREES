<script lang="ts">
        import Seo from '$lib/components/Seo.svelte';
        import { FAQ_ITEMS, buildFaqJsonLd, parsearRespuesta } from '$lib/data/faq';

        /**
         * Página de Preguntas Frecuentes.
         * - Acordeón con <details>/<summary> nativos: accesible (Enter/Espacio,
         *   lectores de pantalla) y funciona sin JS.
         * - JSON-LD FAQPage para resultados enriquecidos en Google.
         * - El buscador filtra en cliente (pregunta + respuesta).
         */
        const jsonLd = buildFaqJsonLd();
        /** Etiqueta <script type="application/ld+json"> lista para {@html}.
         *  El cierre se arma trozado para no confundir al parser de Svelte. */
        const jsonLdTag = `<script type="application/ld+json">${JSON.stringify(jsonLd)}` + '</' + 'script>';

        let busqueda = $state('');

        const filtradas = $derived.by(() => {
                const q = busqueda.trim().toLowerCase();
                if (!q) return FAQ_ITEMS;
                return FAQ_ITEMS.filter(
                        (f) => f.pregunta.toLowerCase().includes(q) || f.respuesta.toLowerCase().includes(q)
                );
        });

        function handleInput(): void {
                busqueda = busqueda.slice(0, 120);
        }
</script>

<Seo
        title="Preguntas Frecuentes | Fundación Funcrees Colombia"
        description="Respuestas sobre donaciones, apadrinamiento, boletas de eventos, certificados, seguridad de pagos y protección de datos de la Fundación Funcrees Colombia."
        path="/preguntas-frecuentes"
/>

<svelte:head>
        {@html jsonLdTag}
</svelte:head>

<section class="view-section active faq-section">
        <div class="container">
                <div class="section-header">
                        <span class="section-subtitle">Estamos para ayudarte</span>
                        <h1 class="section-title">Preguntas Frecuentes</h1>
                        <p class="section-description">
                                Resolvemos las dudas más comunes sobre donaciones, apadrinamiento, boletas y tus datos.
                                ¿No encuentras tu respuesta? <a href="/contacto" class="faq-inline-link">Escríbenos</a> y te
                                respondemos en horario hábil.
                        </p>
                </div>

                <div class="faq-busqueda">
                        <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
                        <input
                                type="search"
                                bind:value={busqueda}
                                oninput={handleInput}
                                placeholder="Buscar en las preguntas… (ej: certificado, Wompi, boleta)"
                                aria-label="Buscar en las preguntas frecuentes"
                        />
                </div>

                {#if filtradas.length === 0}
                        <div class="faq-vacio" role="status">
                                <i class="fa-regular fa-face-frown" aria-hidden="true"></i>
                                <p>
                                        No encontramos coincidencias para <strong>“{busqueda}”</strong>.
                                        Escríbenos por el <a href="/contacto">formulario de contacto</a> y te ayudamos.
                                </p>
                        </div>
                {:else}
                        <div class="faq-lista" aria-label="Lista de preguntas frecuentes">
                                {#each filtradas as item, i (item.id)}
                                        <details class="faq-item" id={item.id} open={i === 0 && !busqueda}>
                                                <summary class="faq-pregunta">
                                                        <span class="faq-pregunta-texto">{item.pregunta}</span>
                                                        <span class="faq-indicador" aria-hidden="true">
                                                                <i class="fa-solid fa-plus"></i>
                                                        </span>
                                                </summary>
                                                <div class="faq-respuesta">
                                                        <p>
                                                                {#each parsearRespuesta(item.respuesta) as seg, j (j)}
                                                                        {#if seg.href}
                                                                                <a href={seg.href}>aquí</a>
                                                                        {:else}
                                                                                {seg.texto}
                                                                        {/if}
                                                                {/each}
                                                        </p>
                                                </div>
                                        </details>
                                {/each}
                        </div>
                {/if}

                <aside class="faq-cta">
                        <h2>¿Sigues con dudas?</h2>
                        <p>Nuestro equipo responde por WhatsApp y correo en horario hábil.</p>
                        <div class="faq-cta-botones">
                                <a class="btn btn-primary" href="/contacto"><i class="fa-regular fa-envelope" aria-hidden="true"></i> Contactar</a>
                                <a class="btn btn-outline" href="/donaciones"><i class="fa-solid fa-hand-holding-heart" aria-hidden="true"></i> Cómo donar</a>
                        </div>
                </aside>
        </div>
</section>

<style>
        .faq-section {
                padding: 4rem 1rem 3rem;
                background: var(--bg-secondary);
        }

        .container {
                max-width: 780px;
                margin: 0 auto;
        }

        .section-header {
                text-align: center;
                margin-bottom: 2rem;
        }

        .faq-inline-link {
                color: var(--primary);
                font-weight: 600;
                text-decoration: underline;
                text-underline-offset: 3px;
        }
        .faq-inline-link:hover {
                text-decoration-thickness: 2px;
        }

        /* Buscador */
        .faq-busqueda {
                display: flex;
                align-items: center;
                gap: 0.65rem;
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 999px;
                padding: 0.75rem 1.25rem;
                margin: 0 auto 1.75rem;
                max-width: 560px;
                box-shadow: var(--shadow-sm);
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .faq-busqueda:focus-within {
                border-color: var(--primary);
                box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 18%, transparent);
        }
        .faq-busqueda i {
                color: var(--text-muted);
        }
        .faq-busqueda input {
                flex: 1;
                border: none;
                background: transparent;
                color: var(--text-main);
                font-size: 0.95rem;
                outline: none;
                min-width: 0;
        }

        /* Acordeón */
        .faq-lista {
                display: flex;
                flex-direction: column;
                gap: 0.85rem;
        }

        .faq-item {
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-sm);
                overflow: hidden;
                transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }
        .faq-item:hover {
                border-color: color-mix(in srgb, var(--primary) 45%, var(--border-color));
                box-shadow: var(--shadow-md);
        }
        .faq-item[open] {
                border-color: var(--primary);
                box-shadow: var(--shadow-md);
        }

        .faq-pregunta {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                list-style: none;
                cursor: pointer;
                padding: 1.1rem 1.25rem;
                font-weight: 600;
                color: var(--text-main);
                min-height: 44px; /* objetivo táctil */
        }
        .faq-pregunta::-webkit-details-marker {
                display: none;
        }
        .faq-pregunta:focus-visible {
                outline: 3px solid var(--primary);
                outline-offset: -3px;
                border-radius: var(--radius-md);
        }

        .faq-pregunta-texto {
                flex: 1;
                line-height: 1.45;
                font-size: 1rem;
        }

        .faq-indicador {
                flex: 0 0 auto;
                width: 30px;
                height: 30px;
                display: grid;
                place-items: center;
                border-radius: 50%;
                background: color-mix(in srgb, var(--primary) 12%, transparent);
                color: var(--primary);
                transition: transform 0.3s ease, background 0.3s ease;
        }
        .faq-item[open] .faq-indicador {
                transform: rotate(45deg);
                background: var(--primary);
                color: #fff;
        }

        .faq-respuesta {
                padding: 0 1.25rem 1.15rem;
                color: var(--text-muted);
                line-height: 1.65;
                font-size: 0.95rem;
                animation: faq-aparecer 0.25s ease;
        }
        .faq-respuesta a {
                color: var(--primary);
                font-weight: 600;
                text-decoration: underline;
                text-underline-offset: 3px;
        }

        @keyframes faq-aparecer {
                from {
                        opacity: 0;
                        transform: translateY(-4px);
                }
                to {
                        opacity: 1;
                        transform: translateY(0);
                }
        }

        /* Estado vacío */
        .faq-vacio {
                text-align: center;
                background: var(--bg-card);
                border: 1px dashed var(--border-color);
                border-radius: var(--radius-md);
                padding: 2rem 1.25rem;
                color: var(--text-muted);
        }
        .faq-vacio i {
                font-size: 1.8rem;
                color: var(--text-muted);
                margin-bottom: 0.5rem;
        }
        .faq-vacio a {
                color: var(--primary);
                font-weight: 600;
        }

        /* CTA final */
        .faq-cta {
                margin-top: 2.5rem;
                text-align: center;
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: var(--radius-lg);
                padding: 2rem 1.25rem;
                box-shadow: var(--shadow-sm);
        }
        .faq-cta h2 {
                color: var(--secondary);
                font-size: 1.35rem;
                margin-bottom: 0.4rem;
        }
        .faq-cta p {
                color: var(--text-muted);
                margin-bottom: 1.25rem;
        }
        .faq-cta-botones {
                display: flex;
                justify-content: center;
                gap: 0.9rem;
                flex-wrap: wrap;
        }
        .faq-cta-botones .btn {
                min-height: 44px;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
        }

        @media (max-width: 640px) {
                .faq-section {
                        padding: 3rem 1rem 2.5rem;
                }
                .faq-pregunta {
                        padding: 0.95rem 1rem;
                }
                .faq-respuesta {
                        padding: 0 1rem 1rem;
                }
        }

        @media (prefers-reduced-motion: reduce) {
                .faq-item,
                .faq-indicador,
                .faq-busqueda {
                        transition: none;
                }
                .faq-respuesta {
                        animation: none;
                }
        }
</style>
