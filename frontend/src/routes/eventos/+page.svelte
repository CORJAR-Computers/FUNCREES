<script lang="ts">
        import { page } from '$app/state';
        import { parseCOP, formatMoneyNumber } from '$lib/utils/currency';
        import { toast } from '$lib/stores/toast.svelte';
        import Seo from '$lib/components/Seo.svelte';
        import Modal from '$lib/components/Modal.svelte';
        import { initiateDonation, pollDonationStatus, ApiError } from '$lib/api/client';
        import type { UiEvent, WompiPaymentSession } from '$lib/types';

        type CheckoutStep = 'form' | 'loading' | 'success' | 'error';

        interface Props {
                data: { eventos: UiEvent[]; usingFallback: boolean };
        }

        const { data }: Props = $props();

        const eventos = $derived(data.eventos);
        let searchQuery = $state('');
        let selectedCategory = $state('todos');

        // Modal de Boletas
        let selectedEvent = $state<UiEvent | null>(null);
        let ticketQuantity = $state(1);
        let selectedGateway = $state<'wompi' | 'whatsapp'>('wompi');
        let checkoutStep = $state<CheckoutStep>('form');
        let checkoutError = $state('');
        let referencia = $state('');
        let paymentSession = $state<WompiPaymentSession | null>(null);
        let pollAbort = $state<AbortController | null>(null);

        // Datos del comprador
        let compradorNombre = $state('');
        let compradorEmail = $state('');
        let compradorTelefono = $state('');

        // Countdown
        let now = $state(new Date());

        $effect(() => {
                const id = setInterval(() => {
                        now = new Date();
                }, 1000);
                return () => clearInterval(id);
        });

        /**
         * Deep-link desde la página de detalle: /eventos?evento=<id> abre el
         * checkout del bono automáticamente (solo eventos con bono pagable; las
         * campañas libres coordinan por WhatsApp y no deben abrir ventanas solas).
         */
        let deepLinkAplicado = $state(false);

        $effect(() => {
                if (deepLinkAplicado) return;
                const deepLinkId = page.url.searchParams.get('evento');
                if (!deepLinkId) return;
                const ev = eventos.find((e) => e.id === deepLinkId);
                if (ev && parseCOP(ev.costo) > 0) {
                        deepLinkAplicado = true;
                        openTicketModal(ev);
                }
        });

        const categories = [
                { id: 'todos', label: 'Todos' },
                { id: 'evento', label: 'Eventos Solidarios' },
                { id: 'campania', label: 'Campañas' }
        ];

        const filteredEvents = $derived(
                eventos.filter((ev) => {
                        const matchesCat = selectedCategory === 'todos' || ev.category === selectedCategory;
                        const q = searchQuery.toLowerCase().trim();
                        const matchesSearch =
                                !q ||
                                ev.titulo.toLowerCase().includes(q) ||
                                ev.desc.toLowerCase().includes(q) ||
                                ev.lugar.toLowerCase().includes(q);
                        return matchesCat && matchesSearch;
                })
        );

        /**
         * Calcula el tiempo restante para un evento.
         */
        function getCountdown(dateObj: string | null): { passed: boolean; days?: number; hours?: number; minutes?: number; seconds?: number } | null {
                if (!dateObj) return null;
                const target = new Date(dateObj);
                const diff = target.getTime() - now.getTime();
                if (diff <= 0) return { passed: true };

                const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);

                return { passed: false, days, hours, minutes, seconds };
        }

        function openTicketModal(ev: UiEvent): void {
                if (parseCOP(ev.costo) <= 0) {
                        // Campañas sin costo definido: coordinar por WhatsApp directamente.
                        const msg = encodeURIComponent(
                                `Hola Fundación FUNCREESCOLOMBIA, deseo apoyar la campaña "${ev.titulo}".`
                        );
                        window.open(`https://wa.me/573137924439?text=${msg}`, '_blank');
                        return;
                }
                selectedEvent = ev;
                ticketQuantity = 1;
                selectedGateway = 'wompi';
                checkoutStep = 'form';
                checkoutError = '';
                referencia = '';
                paymentSession = null;
        }

        function closeTicketModal(): void {
                pollAbort?.abort();
                pollAbort = null;
                selectedEvent = null;
                checkoutStep = 'form';
        }

        function changeQuantity(delta: number): void {
                const next = ticketQuantity + delta;
                if (next >= 1 && next <= 10) {
                        ticketQuantity = next;
                }
        }

        /**
         * Abre el Widget/checkout de Wompi (mismo flujo que donaciones).
         */
        function openWompiWidget(): void {
                if (!paymentSession) return;
                const checkoutUrl =
                        `${paymentSession.wompiCheckoutUrl}?` +
                        `public-key=${encodeURIComponent(paymentSession.publicKey)}&` +
                        `currency=COP&amount-in-cents=${paymentSession.amountInCents}&` +
                        `reference=${encodeURIComponent(paymentSession.reference)}&` +
                        `signature:integrity=${encodeURIComponent(paymentSession.integritySignature)}&` +
                        `customer-email=${encodeURIComponent(paymentSession.customerEmail)}&` +
                        `redirect-url=${encodeURIComponent(paymentSession.redirectUrl)}`;
                const w = window.open(checkoutUrl, 'wompi-checkout', 'width=480,height=680');
                w?.focus();
        }

        async function processCheckout(): Promise<void> {
                if (!selectedEvent) return;

                if (selectedGateway === 'whatsapp') {
                        const numericCost = parseCOP(selectedEvent.costo);
                        const total = numericCost * ticketQuantity;
                        const msg = encodeURIComponent(
                                `Hola Fundación FUNCREESCOLOMBIA, deseo adquirir ${ticketQuantity} bono(s) para "${selectedEvent.titulo}" por un valor de $${formatMoneyNumber(total)} COP.`
                        );
                        window.open(`https://wa.me/573137924439?text=${msg}`, '_blank');
                        return;
                }

                checkoutStep = 'loading';
                checkoutError = '';

                const unitCost = parseCOP(selectedEvent.costo);
                const total = unitCost * ticketQuantity;
                // El backend genera la referencia; tipo 'boleta' con el id del evento
                // queda documentado en la descripción de la transacción Wompi.
                const payload = {
                        tipo: 'boleta' as const,
                        monto: total,
                        donante_nombre: compradorNombre || 'Comprador Anónimo',
                        donante_email: compradorEmail || 'boleta@funcreescolombia.org',
                        donante_telefono: compradorTelefono || undefined,
                        metodo_pago: 'card' as const,
                        beneficiario_id: null,
                        autorizacion_datos: true
                };

                try {
                        const res = await initiateDonation(payload);
                        referencia = res.referencia;
                        paymentSession = res.paymentSession;
                        openWompiWidget();
                        await waitForPayment();
                } catch (err) {
                        checkoutStep = 'error';
                        checkoutError =
                                err instanceof ApiError
                                        ? err.message
                                        : 'No se pudo conectar con la pasarela de pagos. Verifica tu conexión e intenta de nuevo.';
                }
        }

        async function waitForPayment(): Promise<void> {
                pollAbort = new AbortController();
                try {
                        const donacion = await pollDonationStatus(referencia, { signal: pollAbort.signal });
                        if (donacion.estado === 'completado') {
                                checkoutStep = 'success';
                                toast.show('¡Bono solidario adquirido exitosamente!', 'success');
                        } else if (donacion.estado === 'fallido' || donacion.estado === 'reembolsado') {
                                checkoutStep = 'error';
                                checkoutError =
                                        'El pago no se completó. Si fuiste debitado, contáctanos por WhatsApp con tu referencia: ' + referencia;
                        } else {
                                checkoutStep = 'error';
                                checkoutError =
                                        'El pago sigue en procesamiento. Confirmaremos por correo. Referencia: ' + referencia;
                        }
                } catch {
                        checkoutStep = 'error';
                        checkoutError = 'No se pudo verificar el estado del pago. Referencia: ' + referencia;
                }
        }

        async function recheckStatus(): Promise<void> {
                if (!referencia) return;
                checkoutStep = 'loading';
                await waitForPayment();
        }

        function resetCheckout(): void {
                checkoutStep = 'form';
                checkoutError = '';
                referencia = '';
                paymentSession = null;
        }
</script>

<Seo
        title="Eventos Solidarios | Fundación Funcrees Colombia"
        description="Participa en los eventos benéficos, rifas y campañas de la Fundación Funcrees en Sincelejo. Adquiere tus bonos de apoyo solidario."
        path="/eventos"
/>

<section id="eventos" class="view-section active">
        <div class="section">
                <div class="section-header">
                        <span class="section-subtitle">Encuentros y Solidaridad</span>
                        <h1 class="section-title">Eventos y Campañas Benéficas</h1>
                        <p class="section-description">
                                Tu participación en nuestros eventos financia los comedores comunitarios, medicamentos y terapias de nuestros adultos mayores.
                        </p>
                        <div class="eventos-cta-row">
                                <a href="/boletas" class="btn btn-outline">
                                        <i class="fa-solid fa-ticket-simple"></i> ¿Ya compraste tu boleta? Consúltala aquí
                                </a>
                                <a
                                        href="/calendario.ics"
                                        download="calendario-funcrees.ics"
                                        class="btn btn-outline"
                                        title="Agrega nuestros eventos a Google Calendar, Apple Calendar u Outlook"
                                >
                                        <i class="fa-regular fa-calendar-plus"></i> Suscribirse al calendario
                                </a>
                        </div>
                        <p class="eventos-cta-tip">
                                <i class="fa-solid fa-lightbulb" aria-hidden="true"></i>
                                Tip: en Google Calendar usa «Desde URL» con esta dirección para recibir los eventos automáticamente.
                        </p>
                        {#if data.usingFallback}
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
                                        <i class="fa-solid fa-circle-info"></i> Mostrando programación de referencia — no se pudo conectar con el servidor en este momento.
                                </p>
                        {/if}
                </div>

                <!-- Filtros y Búsqueda -->
                <div style="max-width: 850px; margin: 0 auto 2.5rem; display: flex; flex-direction: column; gap: 1.25rem;">
                        <div style="position: relative; width: 100%;">
                                <input
                                        type="text"
                                        bind:value={searchQuery}
                                        placeholder="Buscar evento por nombre, lugar o temática..."
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

                        <div style="display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap;">
                                {#each categories as cat (cat.id)}
                                        <button
                                                class="evento-filter-btn"
                                                class:active={selectedCategory === cat.id}
                                                onclick={() => selectedCategory = cat.id}
                                        >
                                                {cat.label}
                                        </button>
                                {/each}
                        </div>
                </div>

                <!-- Lista de Eventos -->
                {#if filteredEvents.length > 0}
                        <div class="eventos-grid" id="eventos-grid-container">
                                {#each filteredEvents as ev (ev.id)}
                                        {@const countdown = getCountdown(ev.dateObj)}
                                        <div class="evento-card">
                                                {#if ev.imagen}
                                                        <div class="evento-img-box">
                                                                <picture>
                                                                        {#if ev.imagen_webp_srcset}
                                                                                <source
                                                                                        srcset={ev.imagen_webp_srcset}
                                                                                        sizes="(max-width: 576px) 100vw, 46vw"
                                                                                        type="image/webp"
                                                                                />
                                                                        {/if}
                                                                        <img class="evento-img" src={ev.imagen} alt="{ev.titulo} — Fundación FUNCREES" loading="lazy" />
                                                                </picture>
                                                        </div>
                                                {/if}
                                                <div class="evento-badge-panel">
                                                        <div class="evento-date-badge">
                                                                <span class="evento-date-day">{ev.fecha.split(' ')[1] || ev.fecha.substring(0, 2) || '26'}</span>
                                                                <span class="evento-date-month">{ev.fecha.split(' ')[0] || 'Evento'}</span>
                                                        </div>
                                                        <div style="margin-left: 1.5rem; flex: 1;">
                                                                <div class="evento-meta-detail">🕒 {ev.hora}</div>
                                                                <div class="evento-meta-detail">📍 {ev.lugar}</div>
                                                        </div>
                                                </div>

                                                <!-- Cuenta regresiva reactiva -->
                                                {#if countdown}
                                                        <div class="evento-countdown">
                                                                {#if countdown.passed}
                                                                        <span class="evento-countdown-ended-text">Evento Finalizado</span>
                                                                {:else}
                                                                        <div class="evento-countdown-item">
                                                                                <span class="evento-countdown-value">{countdown.days}</span>
                                                                                <span class="evento-countdown-label">Días</span>
                                                                        </div>
                                                                        <div class="evento-countdown-item">
                                                                                <span class="evento-countdown-value">{String(countdown.hours).padStart(2, '0')}</span>
                                                                                <span class="evento-countdown-label">Horas</span>
                                                                        </div>
                                                                        <div class="evento-countdown-item">
                                                                                <span class="evento-countdown-value">{String(countdown.minutes).padStart(2, '0')}</span>
                                                                                <span class="evento-countdown-label">Min</span>
                                                                        </div>
                                                                        <div class="evento-countdown-item">
                                                                                <span class="evento-countdown-value">{String(countdown.seconds).padStart(2, '0')}</span>
                                                                                <span class="evento-countdown-label">Seg</span>
                                                                        </div>
                                                                {/if}
                                                        </div>
                                                {/if}

                                                <div class="evento-info">
                                                        <h3 class="evento-titulo">{ev.titulo}</h3>
                                                        <p class="evento-text-desc">{ev.desc}</p>
                                                        <a class="evento-detalle-link" href="/eventos/{ev.id}">
                                                                Ver detalles <i class="fa-solid fa-arrow-right" aria-hidden="true"></i>
                                                        </a>
                                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; flex-wrap: wrap; gap: 1rem;">
                                                                <span style="font-weight: 700; color: var(--primary-dark); font-size: 1.1rem;">
                                                                        {parseCOP(ev.costo) > 0 ? `Bono: ${ev.costo} COP` : ev.costo || 'Aporte voluntario'}
                                                                </span>
                                                                <button class="btn btn-secondary" onclick={() => openTicketModal(ev)}>
                                                                        {parseCOP(ev.costo) > 0 ? 'Adquirir Bono +' : 'Quiero Apoyar +'}
                                                                </button>
                                                        </div>
                                                </div>
                                        </div>
                                {/each}
                        </div>
                {:else}
                        <div class="evento-empty-state">
                                <div class="evento-empty-icon"><i class="fa-solid fa-calendar-xmark"></i></div>
                                <h3 class="evento-empty-title">No hay eventos en esta categoría</h3>
                                <p class="evento-empty-desc">No encontramos eventos que coincidan con la búsqueda. Intenta con otra categoría.</p>
                                <button class="btn btn-outline" onclick={() => { selectedCategory = 'todos'; searchQuery = ''; }}>
                                        Ver Todos los Eventos
                                </button>
                        </div>
                {/if}
        </div>
</section>

<!-- Modal de Adquisición de Bonos -->
{#if selectedEvent}
        {@const unitCost = parseCOP(selectedEvent.costo)}
        {@const totalCost = unitCost * ticketQuantity}

        <Modal open={!!selectedEvent} onclose={closeTicketModal} labelledby="ticket-modal-title">
                {#if checkoutStep === 'form'}
                        <div class="modal-checkout-header">
                                <h2 class="modal-checkout-title" id="ticket-modal-title">Adquirir Bono Solidario</h2>
                                <p class="modal-checkout-desc">{selectedEvent.titulo}</p>
                        </div>

                        <div style="background: var(--bg-secondary); padding: 1.25rem; border-radius: 12px; margin-bottom: 1.5rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                        <span style="font-weight: 600; color: var(--text);">Cantidad de Bonos:</span>
                                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                                                <button
                                                        type="button"
                                                        class="btn btn-outline"
                                                        style="width: 38px; height: 38px; padding: 0; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;"
                                                        onclick={() => changeQuantity(-1)}
                                                        disabled={ticketQuantity <= 1}
                                                >-</button>
                                                <span style="font-weight: 800; font-size: 1.2rem; min-width: 24px; text-align: center;">
                                                        {ticketQuantity}
                                                </span>
                                                <button
                                                        type="button"
                                                        class="btn btn-outline"
                                                        style="width: 38px; height: 38px; padding: 0; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;"
                                                        onclick={() => changeQuantity(1)}
                                                        disabled={ticketQuantity >= 10}
                                                >+</button>
                                        </div>
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed var(--border-color); padding-top: 0.75rem;">
                                        <span style="color: var(--text-muted);">Valor Unitario:</span>
                                        <span style="font-weight: 600;">${formatMoneyNumber(unitCost)} COP</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; font-size: 1.15rem;">
                                        <span style="font-weight: 700; color: var(--secondary);">Total a Donar:</span>
                                        <span style="font-weight: 800; color: var(--primary-dark);">${formatMoneyNumber(totalCost)} COP</span>
                                </div>
                        </div>

                        <!-- Datos del comprador -->
                        <div style="display: flex; flex-direction: column; gap: 0.85rem; margin-bottom: 1.5rem;">
                                <div>
                                        <label class="form-label" for="comprador-nombre" style="font-size: 0.85rem;">Nombre completo:</label>
                                        <input id="comprador-nombre" type="text" bind:value={compradorNombre} class="form-control" placeholder="Tu nombre" required />
                                </div>
                                <div>
                                        <label class="form-label" for="comprador-email" style="font-size: 0.85rem;">Correo electrónico:</label>
                                        <input id="comprador-email" type="email" bind:value={compradorEmail} class="form-control" placeholder="tucorreo@ejemplo.com" required />
                                </div>
                                <div>
                                        <label class="form-label" for="comprador-tel" style="font-size: 0.85rem;">Teléfono (opcional):</label>
                                        <input id="comprador-tel" type="tel" bind:value={compradorTelefono} class="form-control" placeholder="3001234567" />
                                </div>
                        </div>

                        <!-- Métodos de Pago -->
                        <div style="margin-bottom: 1.5rem;">
                                <span class="form-label" style="font-weight: 600; margin-bottom: 0.75rem; display: block;">
                                        Selecciona Medio de Pago:
                                </span>
                                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                                        <label
                                                style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer;"
                                        >
                                                <input type="radio" name="gateway" value="wompi" bind:group={selectedGateway} />
                                                <span style="font-weight: 600;">Wompi Bancolombia (PSE, Tarjetas, Nequi, Corresponsal)</span>
                                        </label>
                                        <label
                                                style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer;"
                                        >
                                                <input type="radio" name="gateway" value="whatsapp" bind:group={selectedGateway} />
                                                <span style="font-weight: 600;"><i class="fa-brands fa-whatsapp" style="color: #25D366;"></i> Coordinar por WhatsApp con Asesor</span>
                                        </label>
                                </div>
                        </div>

                        <button
                                class="btn btn-primary"
                                style="width: 100%; padding: 1rem; font-size: 1.05rem;"
                                onclick={processCheckout}
                        >
                                Adquirir {ticketQuantity} Bono(s) por ${formatMoneyNumber(totalCost)} COP
                        </button>
                {:else if checkoutStep === 'loading'}
                        <div style="text-align: center; padding: 3rem 1rem;">
                                <div class="spinner" style="margin: 0 auto 1.5rem;"></div>
                                <h3 style="color: var(--secondary);">Procesando orden de bonos solidarios...</h3>
                                <p style="color: var(--text-muted); margin-top: 0.5rem;">
                                        Se abrió la ventana de Wompi. Completa el pago ahí; esta ventana se actualizará sola.
                                </p>
                        </div>
                {:else if checkoutStep === 'success'}
                        <div style="text-align: center; padding: 1.5rem 0.5rem;">
                                <div class="success-shield" style="margin-bottom: 1rem;">✓</div>
                                <h2 style="color: var(--secondary); margin-bottom: 0.5rem;">¡Bono Solidario Confirmado!</h2>
                                <p style="color: var(--text-muted); max-width: 460px; margin: 0 auto 1.5rem;">
                                        Muchas gracias por tu colaboración. Tu aporte beneficia directamente a los adultos mayores de Funcrees en Sincelejo.
                                </p>

                                <div style="background: var(--bg-secondary); border: 1px dashed var(--primary); padding: 1.25rem; border-radius: 12px; text-align: left; font-family: monospace; font-size: 0.85rem; margin-bottom: 1.5rem; white-space: pre-line;">
========================================
     COMPROBANTE DE BONO - FUNCREES
========================================
Referencia:     {referencia}
Fecha:          {new Date().toLocaleString('es-CO')}
Evento:         {selectedEvent?.titulo}
Cantidad:       {ticketQuantity} Bono(s)
Total Pagado:   ${formatMoneyNumber(totalCost)} COP
Estado:         CONFIRMADO POR LA PASARELA
========================================
   ¡TE ESPERAMOS EN NUESTRO EVENTO!
========================================
                                </div>

                                <button class="btn btn-primary" onclick={closeTicketModal} style="padding: 0.75rem 2rem;">
                                        Listo, Cerrar
                                </button>
                        </div>
                {:else if checkoutStep === 'error'}
                        <div style="text-align: center; padding: 1.5rem 0.5rem;">
                                <div class="success-shield" style="margin-bottom: 1rem; background: #dc2626;">✕</div>
                                <h2 style="color: var(--secondary); margin-bottom: 0.5rem;">No se completó la operación</h2>
                                <p style="color: var(--text-muted); max-width: 460px; margin: 0 auto 1.5rem;">{checkoutError}</p>
                                <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                                        {#if referencia}
                                                <button class="btn btn-outline" onclick={recheckStatus}>Verificar de nuevo</button>
                                        {/if}
                                        <button class="btn btn-primary" onclick={resetCheckout}>Intentar de nuevo</button>
                                </div>
                        </div>
                {/if}
        </Modal>
{/if}

<style>
        /* Enlace "Ver detalles" de cada tarjeta -> /eventos/[id] */
        .evento-detalle-link {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                margin-top: 0.65rem;
                font-size: 0.88rem;
                font-weight: 700;
                color: var(--primary);
                text-decoration: none;
                transition: gap 0.2s ease, color 0.2s ease;
        }

        .evento-detalle-link:hover,
        .evento-detalle-link:focus-visible {
                gap: 0.75rem;
                color: var(--primary-dark, var(--primary));
        }

        .evento-detalle-link:focus-visible {
                outline: 2px solid var(--primary);
                outline-offset: 3px;
                border-radius: 4px;
        }

        @media (prefers-reduced-motion: reduce) {
                .evento-detalle-link {
                        transition: none;
                }
        }

        /* Fila de CTAs secundarios (consulta de boleta + suscripción al calendario) */
        .eventos-cta-row {
                margin-top: 1rem;
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
        }

        .eventos-cta-row .btn {
                display: inline-flex;
                align-items: center;
                gap: 0.55rem;
                padding: 0.7rem 1.4rem;
                transition:
                        transform 0.2s ease,
                        box-shadow 0.2s ease,
                        border-color 0.2s ease,
                        color 0.2s ease,
                        background 0.2s ease;
        }

        .eventos-cta-row .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px -10px var(--primary-trans, rgba(0, 0, 0, 0.3));
        }

        .eventos-cta-tip {
                font-size: 0.8rem;
                color: var(--text-muted);
                margin-top: 0.35rem;
        }

        @media (prefers-reduced-motion: reduce) {
                .eventos-cta-row .btn {
                        transition: none;
                }
                .eventos-cta-row .btn:hover {
                        transform: none;
                }
        }
</style>
