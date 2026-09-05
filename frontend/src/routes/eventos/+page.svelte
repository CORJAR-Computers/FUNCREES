<script>
  import { onMount, onDestroy } from 'svelte';
  import { getEvents, FALLBACK_EVENTS } from '$lib/api/client.js';
  import { parseCOP, formatMoneyNumber } from '$lib/utils/currency.js';
  import { toast } from '$lib/stores/toast.svelte.js';

  /** @type {Array<any>} */
  let eventos = $state([]);
  let isLoading = $state(true);
  let searchQuery = $state('');
  let selectedCategory = $state('todos');

  // Modal de Boletas
  /** @type {any|null} */
  let selectedEvent = $state(null);
  let ticketQuantity = $state(1);
  let selectedGateway = $state('wompi');
  let checkoutStep = $state('form'); // 'form' | 'loading' | 'success'
  /** @type {Array<string>} */
  let generatedTickets = $state([]);
  let transactionId = $state('');
  let now = $state(new Date());

  /** @type {any} */
  let timerInterval;

  const categories = [
    { id: 'todos', label: 'Todos' },
    { id: 'evento', label: 'Eventos Solidarios' },
    { id: 'campania', label: 'Campañas' }
  ];

  onMount(async () => {
    try {
      eventos = await getEvents();
    } catch {
      eventos = FALLBACK_EVENTS;
    } finally {
      isLoading = false;
    }

    timerInterval = setInterval(() => {
      now = new Date();
    }, 1000);
  });

  onDestroy(() => {
    if (timerInterval) clearInterval(timerInterval);
  });

  let filteredEvents = $derived(
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
   * @param {string|null} dateObj
   */
  function getCountdown(dateObj) {
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

  /**
   * @param {any} ev
   */
  function openTicketModal(ev) {
    selectedEvent = ev;
    ticketQuantity = 1;
    selectedGateway = 'wompi';
    checkoutStep = 'form';
    generatedTickets = [];
  }

  function closeTicketModal() {
    selectedEvent = null;
    checkoutStep = 'form';
  }

  /**
   * @param {number} delta
   */
  function changeQuantity(delta) {
    const next = ticketQuantity + delta;
    if (next >= 1 && next <= 10) {
      ticketQuantity = next;
    }
  }

  function processCheckout() {
    if (!selectedEvent) return;

    if (selectedGateway === 'whatsapp') {
      const numericCost = parseCOP(selectedEvent.costo);
      const total = numericCost * ticketQuantity;
      const msg = encodeURIComponent(
        `Hola Fundación FUNCREESCOLOMBIA, deseo adquirir ${ticketQuantity} bono(s) para "${selectedEvent.titulo}" por un valor de $${formatMoneyNumber(total)} COP.`
      );
      closeTicketModal();
      window.open(`https://wa.me/573137924439?text=${msg}`, '_blank');
      return;
    }

    checkoutStep = 'loading';

    setTimeout(() => {
      transactionId = `EVT-${Math.floor(100000 + Math.random() * 900000)}`;
      generatedTickets = Array.from(
        { length: ticketQuantity },
        () => `BOLETA-#${Math.floor(1000 + Math.random() * 9000)}`
      );
      checkoutStep = 'success';
      toast.show('¡Bono solidario adquirido exitosamente!', 'success');
    }, 1200);
  }
</script>

<svelte:head>
  <title>Eventos Solidarios | Fundación Funcrees Colombia</title>
  <meta name="description" content="Participa en los eventos benéficos, rifas y campañas de la Fundación Funcrees en Sincelejo. Adquiere tus bonos de apoyo solidario." />
</svelte:head>

<section id="eventos" class="view-section active">
  <div class="section">
    <div class="section-header">
      <span class="section-subtitle">Encuentros y Solidaridad</span>
      <h1 class="section-title">Eventos y Campañas Benéficas</h1>
      <p class="section-description">
        Tu participación en nuestros eventos financia los comedores comunitarios, medicamentos y terapias de nuestros adultos mayores.
      </p>
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
        {#each categories as cat}
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
    {#if isLoading}
      <div style="text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
        <i class="fa-solid fa-spinner fa-spin" style="font-size: 2.5rem; color: var(--primary); margin-bottom: 1rem;"></i>
        <p>Cargando programación de eventos...</p>
      </div>
    {:else if filteredEvents.length > 0}
      <div class="eventos-grid" id="eventos-grid-container">
        {#each filteredEvents as ev (ev.id)}
          {@const countdown = getCountdown(ev.dateObj)}
          <div class="evento-card">
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
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; flex-wrap: wrap; gap: 1rem;">
                <span style="font-weight: 700; color: var(--primary-dark); font-size: 1.1rem;">
                  Bono: {ev.costo} COP
                </span>
                <button class="btn btn-secondary" onclick={() => openTicketModal(ev)}>
                  {ev.id === 'rifa' ? 'Comprar Boleta +' : 'Adquirir Bono +'}
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

<!-- Modal de Adquisición de Boletas -->
{#if selectedEvent}
  {@const unitCost = parseCOP(selectedEvent.costo)}
  {@const totalCost = unitCost * ticketQuantity}

  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <div
    class="modal-backdrop active"
    role="dialog"
    aria-modal="true"
    tabindex="-1"
    onclick={closeTicketModal}
    onkeydown={(e) => e.key === 'Escape' && closeTicketModal()}
  >
    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <div
      class="modal-card"
      role="document"
      tabindex="-1"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
    >
      <button class="modal-close" onclick={closeTicketModal} aria-label="Cerrar modal">✕</button>

      {#if checkoutStep === 'form'}
        <div>
          <div class="modal-checkout-header">
            <h2 class="modal-checkout-title">Adquirir Bono Solidario</h2>
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

            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed var(--border); padding-top: 0.75rem;">
              <span style="color: var(--text-muted);">Valor Unitario:</span>
              <span style="font-weight: 600;">${formatMoneyNumber(unitCost)} COP</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; font-size: 1.15rem;">
              <span style="font-weight: 700; color: var(--secondary);">Total a Donar:</span>
              <span style="font-weight: 800; color: var(--primary-dark);">${formatMoneyNumber(totalCost)} COP</span>
            </div>
          </div>

          <!-- Métodos de Pago -->
          <div style="margin-bottom: 1.5rem;">
            <span class="form-label" style="font-weight: 600; margin-bottom: 0.75rem; display: block;">
              Selecciona Medio de Pago:
            </span>
            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
              <label
                style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; cursor: pointer;"
                class:active={selectedGateway === 'wompi'}
              >
                <input type="radio" name="gateway" value="wompi" bind:group={selectedGateway} />
                <span style="font-weight: 600;">Wompi Bancolombia (PSE, Tarjetas, Nequi, Corresponsal)</span>
              </label>
              <label
                style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; cursor: pointer;"
                class:active={selectedGateway === 'whatsapp'}
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
        </div>
      {:else if checkoutStep === 'loading'}
        <div style="text-align: center; padding: 3rem 1rem;">
          <div class="spinner" style="margin: 0 auto 1.5rem;"></div>
          <h3 style="color: var(--secondary);">Procesando orden de bonos solidarios...</h3>
          <p style="color: var(--text-muted); margin-top: 0.5rem;">Conectando de forma segura con la pasarela.</p>
        </div>
      {:else if checkoutStep === 'success'}
        <div style="text-align: center; padding: 1.5rem 0.5rem;">
          <div class="success-shield" style="margin-bottom: 1rem;">✓</div>
          <h2 style="color: var(--secondary); margin-bottom: 0.5rem;">¡Bono Solidario Generado!</h2>
          <p style="color: var(--text-muted); max-width: 460px; margin: 0 auto 1.5rem;">
            Muchas gracias por tu colaboración. Tu aporte beneficia directamente a los adultos mayores de Funcrees en Sincelejo.
          </p>

          <div style="background: var(--bg-secondary); border: 1px dashed var(--primary); padding: 1.25rem; border-radius: 12px; text-align: left; font-family: monospace; font-size: 0.85rem; margin-bottom: 1.5rem; white-space: pre-line;">
========================================
     COMPROBANTE DE BONO - FUNCREES
========================================
ID Transacción: {transactionId}
Fecha:          {new Date().toLocaleString('es-CO')}
Evento:         {selectedEvent.titulo}
Cantidad:       {ticketQuantity} Bono(s)
Total Pagado:   ${formatMoneyNumber(totalCost)} COP
Método:         {selectedGateway.toUpperCase()}
Boletas Asignadas:
{#each generatedTickets as t, i}
  {i + 1}. [ {t} ]
{/each}
========================================
   ¡TE ESPERAMOS EN NUESTRO EVENTO!
========================================
          </div>

          <button class="btn btn-primary" onclick={closeTicketModal} style="padding: 0.75rem 2rem;">
            Listo, Cerrar
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}
