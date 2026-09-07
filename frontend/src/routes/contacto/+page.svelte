<script lang="ts">
        import { page } from '$app/state';
        import LeafletMap from '$lib/components/LeafletMap.svelte';
        import Seo from '$lib/components/Seo.svelte';
        import { sendContactMessage, ApiError } from '$lib/api/client';
        import { toast } from '$lib/stores/toast.svelte';
        import type { ContactTipo } from '$lib/types';

        let nombre = $state('');
        let email = $state('');
        let telefono = $state('');
        /** Código de TIPO_CHOICES (backend). Antes se enviaba `asunto` display y DRF
         *  lo ignoraba silenciosamente: todo mensaje llegaba como 'consulta'. */
        let tipo = $state<ContactTipo>('consulta');
        let mensaje = $state('');
        let isSubmitting = $state(false);
        let submitError = $state('');

        /** Deep-link desde otras páginas: /contacto?tipo=eventos&asunto=<texto>
         *  preselecciona el motivo y arranca el mensaje (ej. desde el detalle
         *  de un evento). Solo aplica una vez y valida contra TIPO_CHOICES. */
        const TIPOS_VALIDOS: ContactTipo[] = [
                'consulta', 'apadrinamiento', 'alianza',
                'voluntariado', 'eventos', 'donacion', 'otro'
        ];
        let deepLinkAplicado = $state(false);

        $effect(() => {
                if (deepLinkAplicado) return;
                const tipoParam = page.url.searchParams.get('tipo');
                const asuntoParam = page.url.searchParams.get('asunto');
                if (!tipoParam && !asuntoParam) return;
                deepLinkAplicado = true;
                if (tipoParam && TIPOS_VALIDOS.includes(tipoParam as ContactTipo)) {
                        tipo = tipoParam as ContactTipo;
                }
                if (asuntoParam) {
                        mensaje = `Hola, tengo una consulta sobre: ${asuntoParam}. `;
                }
        });

        async function handleSubmit(e: SubmitEvent): Promise<void> {
                e.preventDefault();
                isSubmitting = true;
                submitError = '';

                try {
                        await sendContactMessage({
                                nombre,
                                email,
                                telefono: telefono || undefined,
                                tipo,
                                mensaje
                        });
                        toast.show('¡Mensaje enviado con éxito! Nos pondremos en contacto pronto.', 'success');
                        nombre = '';
                        email = '';
                        telefono = '';
                        mensaje = '';
                } catch (err) {
                        // Error honesto: el mensaje NO fue registrado. Ofrecer alternativas.
                        submitError =
                                err instanceof ApiError
                                        ? err.message
                                        : 'No se pudo enviar el mensaje en este momento. Puedes escribirnos directamente por WhatsApp.';
                        toast.show(submitError, 'error', 6000);
                } finally {
                        isSubmitting = false;
                }
        }
</script>

<Seo
        title="Contacto y Alianzas | Fundación Funcrees Colombia"
        description="Ponte en contacto con la Fundación Funcrees en Sincelejo, Sucre. Escríbenos para apadrinamientos, donaciones, voluntariado o alianzas estratégicas."
        path="/contacto"
/>

<section id="contacto-footer" class="view-section active" style="padding: 4rem 1rem; background: var(--bg-secondary);">
        <div style="max-width: 1280px; margin: 0 auto;">
                <div class="section-header" style="margin-bottom: 3rem;">
                        <span class="section-subtitle">Estamos Aquí para Ti</span>
                        <h1 class="section-title">Contacto y Alianzas Institucionales</h1>
                        <p class="section-description">
                                ¿Tienes dudas sobre los programas de apadrinamiento, quieres proponer una alianza corporativa o registrarte como voluntario? Escríbenos, con gusto te atenderemos.
                                Si tu pregunta es sobre donaciones, boletas o certificados, quizá ya la respondimos en las
                                <a href="/preguntas-frecuentes" style="color: var(--primary); font-weight: 600; text-decoration: underline; text-underline-offset: 3px;">Preguntas Frecuentes</a>.
                        </p>
                </div>

                <div class="contact-section-grid">
                        <!-- Columna del Formulario de Contacto -->
                        <div class="contact-form-side">
                                <form class="contact-form" onsubmit={handleSubmit}>
                                        <div class="form-group">
                                                <label class="form-label" for="contact-name">Nombre Completo:</label>
                                                <input
                                                        type="text"
                                                        id="contact-name"
                                                        bind:value={nombre}
                                                        class="form-input"
                                                        placeholder="Ingresa tu nombre..."
                                                        required
                                                />
                                        </div>

                                        <div class="form-group">
                                                <label class="form-label" for="contact-email">Correo Electrónico:</label>
                                                <input
                                                        type="email"
                                                        id="contact-email"
                                                        bind:value={email}
                                                        class="form-input"
                                                        placeholder="ejemplo@correo.com"
                                                        required
                                                />
                                        </div>

                                        <div class="form-group">
                                                <label class="form-label" for="contact-telefono">Teléfono (WhatsApp):</label>
                                                <input
                                                        type="tel"
                                                        id="contact-telefono"
                                                        bind:value={telefono}
                                                        class="form-input"
                                                        placeholder="+57 313 792 4439"
                                                />
                                        </div>

                                        <div class="form-group">
                                                <label class="form-label" for="contact-asunto">Motivo de Contacto:</label>
                                                <select id="contact-asunto" bind:value={tipo} class="form-input">
                                                        <option value="consulta">Consulta General</option>
                                                        <option value="apadrinamiento">Apadrinamiento de Adulto Mayor</option>
                                                        <option value="alianza">Alianza Corporativa / RSE</option>
                                                        <option value="voluntariado">Postulación de Voluntariado</option>
                                                        <option value="eventos">Eventos y Bonos Solidarios</option>
                                                </select>
                                        </div>

                                        <div class="form-group">
                                                <label class="form-label" for="contact-msg">Mensaje o Consulta:</label>
                                                <textarea
                                                        id="contact-msg"
                                                        bind:value={mensaje}
                                                        class="form-input form-textarea"
                                                        placeholder="Escribe tu mensaje detallado aquí..."
                                                        required
                                                ></textarea>
                                        </div>

                                        {#if submitError}
                                                <div role="alert" style="background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b; padding: 0.85rem 1rem; border-radius: 8px; font-size: 0.88rem; margin-bottom: 0.75rem;">
                                                        <strong>No se pudo enviar tu mensaje.</strong> {submitError}
                                                </div>
                                        {/if}

                                        <button
                                                type="submit"
                                                class="btn btn-primary"
                                                style="margin-top: 1rem; padding: 0.85rem 2rem; width: 100%;"
                                                disabled={isSubmitting}
                                        >
                                                {#if isSubmitting}
                                                        <i class="fa-solid fa-spinner fa-spin"></i> Enviando...
                                                {:else}
                                                        Enviar Mensaje ✉️
                                                {/if}
                                        </button>
                                </form>
                        </div>

                        <!-- Columna del Mapa Interactivo Leaflet -->
                        <div
                                class="contact-map-side"
                                style="display: flex; flex-direction: column; min-height: 480px; padding: 0; position: relative; overflow: hidden; border-radius: var(--radius-lg);"
                        >
                                <LeafletMap />

                                <!-- Overlay de Información de Contacto -->
                                <div class="map-info-overlay" style="margin: 1.5rem; position: relative; z-index: 1000; pointer-events: auto;">
                                        <h3 class="map-info-title"><i class="fa-solid fa-building-circle-check"></i> Sede Administrativa</h3>
                                        <div class="map-info-text">
                                                <i class="fa-solid fa-map-location-dot"></i> Carrera 15b #41c - 07, Sincelejo, Sucre
                                        </div>
                                        <div class="map-info-text">
                                                <i class="fa-solid fa-phone"></i> +57 313 792 4439
                                        </div>
                                        <div class="map-info-text">
                                                <i class="fa-solid fa-envelope"></i> fundacioncreceunaesperanza@gmail.com
                                        </div>
                                        <div style="margin-top: 1rem;">
                                                <a
                                                        href="https://wa.me/573137924439?text=Hola%20Fundaci%C3%B3n%20FUNCREESCOLOMBIA%2C%20quisiera%20m%C3%A1s%20informaci%C3%B3n."
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        class="btn btn-secondary"
                                                        style="padding: 0.5rem 1rem; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 0.5rem;"
                                                >
                                                        <i class="fa-brands fa-whatsapp"></i> Chatear por WhatsApp
                                                </a>
                                        </div>
                                </div>
                        </div>
                </div>
        </div>
</section>

<!-- Programa Embajadores de Esperanza -->
<section class="embajadores-section">
        <div class="embajadores-gold-bar"></div>
        <div class="embajadores-container">
                <span class="embajadores-icon-wrap">🌟</span>
                <span class="embajadores-eyebrow">Programa Especial</span>
                <h2 class="embajadores-title">Convierte tu Influencia<br>en Transformación Social</h2>
                <p class="embajadores-desc">
                        Si eres líder de opinión, empresario o profesional con visión de impacto, te invitamos a ser nuestra voz en el territorio. Como Embajador de Esperanza, tu liderazgo multiplica el alcance de nuestra misión.
                </p>
                <div class="embajadores-benefits">
                        <div class="embajador-benefit">
                                <i class="fa-solid fa-medal"></i>
                                <span>Distinción Oficial de Embajador</span>
                        </div>
                        <div class="embajador-benefit">
                                <i class="fa-solid fa-calendar-star"></i>
                                <span>Acceso a Eventos Exclusivos</span>
                        </div>
                        <div class="embajador-benefit">
                                <i class="fa-solid fa-certificate"></i>
                                <span>Certificación Institucional</span>
                        </div>
                </div>
                <a href="https://wa.me/573137924439?text=Hola%2C%20quisiera%20postularme%20como%20Embajador%20de%20Esperanza." target="_blank" rel="noopener noreferrer" class="embajadores-cta">
                        <i class="fa-solid fa-star" style="margin-right: 0.5rem;"></i>Quiero ser Embajador
                </a>
        </div>
</section>

<!-- Aliados Colaboradores -->
<section class="aliados-section">
        <h3 class="carousel-title">Nuestros Aliados Colaboradores</h3>
        <div class="carousel-track-wrapper">
                <div class="carousel-track">
                        <div class="aliado-badge">
                                <svg class="aliado-logo" viewBox="0 0 140 40" width="140" height="40" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <rect width="100%" height="100%" rx="20" fill="#f5f5f5" class="aliado-bg-rect" />
                                        <circle cx="25" cy="20" r="10" fill="#ef3829" />
                                        <circle cx="25" cy="20" r="6" stroke="#ffffff" stroke-width="2" />
                                        <text x="48" y="25" fill="#333333" font-family="Outfit" font-weight="800" font-size="14">Claro</text>
                                </svg>
                        </div>
                        <div class="aliado-badge">
                                <svg class="aliado-logo" viewBox="0 0 140 40" width="140" height="40" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <rect width="100%" height="100%" rx="20" fill="#f5f5f5" class="aliado-bg-rect" />
                                        <circle cx="25" cy="20" r="10" fill="#002f6c" />
                                        <path d="M20 22 L23 18 L26 21 L30 17" stroke="#ffffff" stroke-width="2" stroke-linecap="round" />
                                        <text x="48" y="25" fill="#002f6c" font-family="Outfit" font-weight="800" font-size="14">USAID</text>
                                </svg>
                        </div>
                        <div class="aliado-badge">
                                <svg class="aliado-logo" viewBox="0 0 140 40" width="140" height="40" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <rect width="100%" height="100%" rx="20" fill="#f5f5f5" class="aliado-bg-rect" />
                                        <path d="M18 12 L25 8 L32 12 V22 C32 26 25 30 25 30 C25 30 18 26 18 22 V12 Z" fill="#2e7d32" />
                                        <path d="M25 8 V30" stroke="#ffb300" stroke-width="2" />
                                        <text x="48" y="25" fill="#2e7d32" font-family="Outfit" font-weight="800" font-size="12">SUCRE</text>
                                </svg>
                        </div>
                        <div class="aliado-badge">
                                <svg class="aliado-logo" viewBox="0 0 140 40" width="140" height="40" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <rect width="100%" height="100%" rx="20" fill="#f5f5f5" class="aliado-bg-rect" />
                                        <path d="M18 12 H32 V28 H18 Z" fill="#1565c0" />
                                        <path d="M25 12 L32 20 L25 28 L18 20 Z" fill="#ffd54f" />
                                        <text x="48" y="25" fill="#1565c0" font-family="Outfit" font-weight="800" font-size="11">SINCELEJO</text>
                                </svg>
                        </div>
                        <div class="aliado-badge">
                                <svg class="aliado-logo" viewBox="0 0 140 40" width="140" height="40" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <rect width="100%" height="100%" rx="20" fill="#f5f5f5" class="aliado-bg-rect" />
                                        <circle cx="25" cy="20" r="9" fill="#0d47a1" />
                                        <path d="M21 20 H29 M25 16 V24" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" />
                                        <text x="44" y="25" fill="#0d47a1" font-family="Outfit" font-weight="800" font-size="11">MINSALUD</text>
                                </svg>
                        </div>
                </div>
        </div>
</section>
