<script>
  import { parseCOP, formatMoneyNumber } from '$lib/utils/currency.js';
  import { toast } from '$lib/stores/toast.svelte.js';

  let activeTab = $state('donacion'); // 'donacion' | 'apadrinamiento' | 'patrocinio' | 'voluntariado'
  let selectedPreset = $state(50000);
  let customAmount = $state('');
  let selectedGateway = $state('wompi');
  let checkoutStep = $state('idle'); // 'idle' | 'modal' | 'loading' | 'success'
  let isRecurring = $state(false);

  // Formulario patrocinio / voluntariado
  let empresa = $state('');
  let nombre = $state('');
  let email = $state('');
  let telefono = $state('');
  let area = $state('');
  let mensaje = $state('');
  let donationReceipt = $state({ id: '', amount: 0, date: '', type: '' });

  const presets = [20000, 50000, 100000, 200000];

  let currentAmount = $derived(
    customAmount ? parseCOP(customAmount) : selectedPreset
  );

  /**
   * @param {number} amount
   */
  function selectPreset(amount) {
    selectedPreset = amount;
    customAmount = '';
  }

  /**
   * @param {'donacion' | 'apadrinamiento' | 'patrocinio' | 'voluntariado'} tab
   * @param {number} [presetAmount]
   */
  function openModal(tab, presetAmount) {
    activeTab = tab;
    if (presetAmount) {
      selectedPreset = presetAmount;
      customAmount = '';
    }
    checkoutStep = 'modal';
  }

  function closeModal() {
    checkoutStep = 'idle';
  }

  function submitDonation() {
    if (currentAmount <= 0 && activeTab !== 'patrocinio' && activeTab !== 'voluntariado') {
      toast.show('Por favor ingresa un monto válido', 'warning');
      return;
    }

    if (selectedGateway === 'whatsapp') {
      const msg = encodeURIComponent(
        `Hola Fundación FUNCREESCOLOMBIA, deseo realizar un aporte de $${formatMoneyNumber(currentAmount)} COP (${isRecurring ? 'Aporte Mensual' : 'Aporte Único'}) para la labor social.`
      );
      closeModal();
      window.open(`https://wa.me/573137924439?text=${msg}`, '_blank');
      return;
    }

    checkoutStep = 'loading';

    setTimeout(() => {
      donationReceipt = {
        id: `DON-${Math.floor(100000 + Math.random() * 900000)}`,
        amount: currentAmount,
        date: new Date().toLocaleString('es-CO'),
        type: activeTab === 'apadrinamiento' ? 'Apadrinamiento Mensual' : 'Donación Solidaria'
      };
      checkoutStep = 'success';
      toast.show('¡Donación procesada con éxito! Muchas gracias.', 'success');
    }, 1500);
  }

  /**
   * @param {SubmitEvent} e
   */
  function handleCorporateSubmit(e) {
    e.preventDefault();
    checkoutStep = 'loading';
    setTimeout(() => {
      checkoutStep = 'success';
      toast.show('Información enviada. Un asesor se comunicará en breve.', 'success');
    }, 1200);
  }
</script>

<svelte:head>
  <title>Donaciones y Aliados | Fundación Funcrees Colombia</title>
  <meta name="description" content="Apoya la labor de la Fundación Funcrees en Sincelejo: apadrina un adulto mayor, realiza donaciones o vincula a tu empresa como aliada estratégica." />
</svelte:head>

<section id="donaciones-aliados" class="view-section active">
  <div class="section">
    <div class="section-header">
      <span class="section-subtitle">Sostenibilidad Colectiva</span>
      <h1 class="section-title">Tu Apoyo es la Semilla del Cambio</h1>
      <p class="section-description">
        Tu generosidad nos ayuda a garantizar alimentación balanceada, salud preventiva integral y afecto diario a los adultos mayores de Sincelejo y Sucre.
      </p>
    </div>

    <!-- Pestañas de Navegación Rápida -->
    <div class="donaciones-grid">
      <div class="donacion-card">
        <div class="donacion-icon"><i class="fa-solid fa-users"></i></div>
        <h3 class="donacion-title">Apadrinamiento</h3>
        <p class="donacion-text">
          Conecta directamente con un adulto mayor y aporta mensualmente a su nutrición, medicamentos y terapias.
        </p>
        <button class="btn btn-primary" onclick={() => openModal('apadrinamiento')}>Ver Modalidades +</button>
      </div>

      <div class="donacion-card">
        <div class="donacion-icon"><i class="fa-solid fa-hand-holding-dollar"></i></div>
        <h3 class="donacion-title">Donaciones Directas</h3>
        <p class="donacion-text">
          Aportes únicos o recurrentes para financiar los comedores comunitarios y suministros hospitalarios de la fundación.
        </p>
        <button class="btn btn-secondary" onclick={() => openModal('donacion')}>Donar Ahora +</button>
      </div>

      <div class="donacion-card">
        <div class="donacion-icon"><i class="fa-solid fa-building-circle-arrow-right"></i></div>
        <h3 class="donacion-title">Patrocinio Empresarial</h3>
        <p class="donacion-text">
          Alianzas de Responsabilidad Social (RSE) para que empresas financien huertos urbanos y brigadas de salud.
        </p>
        <button class="btn btn-outline" onclick={() => openModal('patrocinio')}>Ver Alianzas +</button>
      </div>

      <div class="donacion-card">
        <div class="donacion-icon"><i class="fa-solid fa-heart-circle-plus"></i></div>
        <h3 class="donacion-title">Voluntariado Activo</h3>
        <p class="donacion-text">
          Súmate con tus habilidades profesionales en salud, psicología, artes, recreación o pedagogía comunitaria.
        </p>
        <button class="btn btn-outline" style="border-color: orange; color: orange;" onclick={() => openModal('voluntariado')}>Unirse +</button>
      </div>
    </div>

    <!-- Niveles de Apadrinamiento (Pricing Tiers) -->
    <div class="pricing-tiers-section">
      <div style="text-align: center; max-width: 650px; margin: 0 auto 2.5rem;">
        <span class="section-subtitle">Elige tu Nivel de Impacto</span>
        <h2 style="color: var(--secondary);">Niveles de Apadrinamiento</h2>
        <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.75rem;">
          Cada nivel impacta directamente la vida de personas mayores, jóvenes y comunidades rurales en Sucre.
        </p>
      </div>

      <div class="pricing-tiers-grid">
        <!-- SEMILLA -->
        <div class="pricing-card pricing-card--semilla">
          <span class="pricing-level">🌱 Semilla</span>
          <div class="pricing-amount">
            <span class="pricing-usd">$30 <small style="font-size: 1rem;">USD</small></span>
            <span class="pricing-cop">≈ $126.000 COP</span>
            <span class="pricing-period">por mes</span>
          </div>
          <p class="pricing-name">Padrino Semilla</p>
          <p class="pricing-target">Para personas comprometidas con el cambio social</p>
          <ul class="pricing-features">
            <li>Alimentación balanceada y seguimiento nutricional</li>
            <li>Atención básica en salud preventiva</li>
            <li>Acompañamiento emocional directo</li>
            <li>Reporte mensual de impacto y bienestar</li>
          </ul>
          <button class="pricing-btn pricing-btn--semilla" onclick={() => openModal('apadrinamiento', 126000)}>
            Ser Padrino Semilla
          </button>
        </div>

        <!-- RAÍZ -->
        <div class="pricing-card pricing-card--raiz">
          <span class="pricing-badge pricing-badge--popular">Más Popular</span>
          <span class="pricing-level">🌿 Raíz</span>
          <div class="pricing-amount">
            <span class="pricing-usd">$90 <small style="font-size: 1rem;">USD</small></span>
            <span class="pricing-cop">≈ $378.000 COP</span>
            <span class="pricing-period">por mes</span>
          </div>
          <p class="pricing-name">Padrino Raíz</p>
          <p class="pricing-target">Para familias, Pymes y grupos solidarios</p>
          <ul class="pricing-features">
            <li>Todo lo incluido en Semilla</li>
            <li>Fortalecimiento de capacidades operativas</li>
            <li>Seguridad alimentaria estructural</li>
            <li>Visibilidad como aliado en redes y eventos</li>
            <li>Certificado de donación oficial</li>
          </ul>
          <button class="pricing-btn pricing-btn--raiz" onclick={() => openModal('apadrinamiento', 378000)}>
            Ser Padrino Raíz
          </button>
        </div>

        <!-- LEGADO -->
        <div class="pricing-card pricing-card--legado">
          <span class="pricing-badge pricing-badge--premium">⭐ Premium</span>
          <span class="pricing-level">🏆 Legado</span>
          <div class="pricing-amount">
            <span class="pricing-usd">$130 <small style="font-size: 1rem;">USD</small></span>
            <span class="pricing-cop">≈ $546.000 COP</span>
            <span class="pricing-period">por mes</span>
          </div>
          <p class="pricing-name">Padrino Legado</p>
          <p class="pricing-target">Para empresas y donantes de alto impacto</p>
          <ul class="pricing-features">
            <li>Todo lo incluido en Raíz</li>
            <li>Expansión de huertos a nuevos municipios</li>
            <li>Nombramiento como Embajador Corporativo</li>
            <li>Co-branding institucional y medios digitales</li>
            <li>Acceso exclusivo a rendición de cuentas</li>
          </ul>
          <button class="pricing-btn pricing-btn--legado" onclick={() => openModal('patrocinio')}>
            Ser Padrino Legado ✨
          </button>
        </div>
      </div>
    </div>

    <!-- Medios de Recaudo en Colombia -->
    <div style="background-color: var(--bg-secondary); border-radius: var(--radius-lg); padding: 2.5rem; text-align: center; max-width: 800px; margin: 3rem auto 0;">
      <h3 style="color: var(--secondary); margin-bottom: 0.75rem; font-size: 1.35rem;">Medios de Pago Seguros en Colombia</h3>
      <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.5rem; line-height: 1.6;">
        Aceptamos transacciones directas a través de <strong>PSE (todos los bancos)</strong>, <strong>Wompi Bancolombia</strong> (Tarjetas de Crédito, Nequi, Daviplata), transferencia a cuenta de ahorros y corresponsales bancarios.
      </p>
      <div style="display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;">
        <span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">PSE</span>
        <span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">Wompi</span>
        <span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">Bancolombia</span>
        <span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">Nequi</span>
        <span style="background: var(--bg-card); padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 700; color: var(--secondary); border: 1px solid var(--border-color);">Efecty</span>
      </div>
    </div>
  </div>
</section>

<!-- Modal de Checkout / Donaciones -->
{#if checkoutStep !== 'idle'}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <div
    class="modal-backdrop active"
    role="dialog"
    aria-modal="true"
    tabindex="-1"
    onclick={closeModal}
    onkeydown={(e) => e.key === 'Escape' && closeModal()}
  >
    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <div
      class="modal-card"
      role="document"
      tabindex="-1"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
    >
      <button class="modal-close" onclick={closeModal} aria-label="Cerrar modal">✕</button>

      {#if checkoutStep === 'modal'}
        <div class="modal-checkout-header">
          <h2 class="modal-checkout-title">
            {#if activeTab === 'apadrinamiento'}
              Apadrinar un Adulto Mayor
            {:else if activeTab === 'donacion'}
              Realizar una Donación Solidaria
            {:else if activeTab === 'patrocinio'}
              Alianza de Patrocinio Empresarial
            {:else}
              Postulación de Voluntariado
            {/if}
          </h2>
          <p class="modal-checkout-desc">
            Cada peso donado llega directamente a los comedores y bienestar de la fundación.
          </p>
        </div>

        <!-- Pestañas de Modal -->
        <div class="checkout-tabs" style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border);">
          <button
            class="checkout-tab"
            class:active={activeTab === 'donacion'}
            onclick={() => activeTab = 'donacion'}
            style="padding: 0.5rem 1rem; border: none; background: transparent; cursor: pointer; font-weight: 600; border-bottom: 2px solid transparent;"
          >Donación</button>
          <button
            class="checkout-tab"
            class:active={activeTab === 'apadrinamiento'}
            onclick={() => activeTab = 'apadrinamiento'}
            style="padding: 0.5rem 1rem; border: none; background: transparent; cursor: pointer; font-weight: 600; border-bottom: 2px solid transparent;"
          >Apadrinamiento</button>
          <button
            class="checkout-tab"
            class:active={activeTab === 'patrocinio'}
            onclick={() => activeTab = 'patrocinio'}
            style="padding: 0.5rem 1rem; border: none; background: transparent; cursor: pointer; font-weight: 600; border-bottom: 2px solid transparent;"
          >Empresas</button>
          <button
            class="checkout-tab"
            class:active={activeTab === 'voluntariado'}
            onclick={() => activeTab = 'voluntariado'}
            style="padding: 0.5rem 1rem; border: none; background: transparent; cursor: pointer; font-weight: 600; border-bottom: 2px solid transparent;"
          >Voluntariado</button>
        </div>

        {#if activeTab === 'donacion' || activeTab === 'apadrinamiento'}
          <!-- Selector de Frecuencia -->
          <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
            <button
              type="button"
              class="btn"
              class:btn-primary={!isRecurring}
              class:btn-outline={isRecurring}
              style="flex: 1;"
              onclick={() => isRecurring = false}
            >Aporte Único</button>
            <button
              type="button"
              class="btn"
              class:btn-primary={isRecurring}
              class:btn-outline={isRecurring}
              style="flex: 1;"
              onclick={() => isRecurring = true}
            >Aporte Mensual 🔁</button>
          </div>

          <!-- Selección de Montos -->
          <span class="form-label" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">
            Selecciona el Monto:
          </span>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1rem;">
            {#each presets as amount}
              <button
                type="button"
                class="amount-btn"
                class:active={!customAmount && selectedPreset === amount}
                onclick={() => selectPreset(amount)}
                style="padding: 0.75rem; border: 1px solid var(--border); border-radius: 8px; font-weight: 700; cursor: pointer; background: var(--bg-card); color: var(--text);"
              >
                ${formatMoneyNumber(amount)} COP
              </button>
            {/each}
          </div>

          <!-- Monto Personalizado -->
          <div style="margin-bottom: 1.5rem;">
            <label for="custom-amount-input" class="form-label" style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.25rem; display: block;">
              O ingresa otro valor:
            </label>
            <input
              id="custom-amount-input"
              type="text"
              placeholder="Ej: 75.000"
              class="form-control"
              bind:value={customAmount}
              style="font-size: 1.1rem; font-weight: 700;"
            />
          </div>

          <!-- Medio de Pago -->
          <div style="margin-bottom: 1.5rem;">
            <span class="form-label" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">
              Medio de Pago:
            </span>
            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
              <label style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; border: 1px solid var(--border); border-radius: 8px; cursor: pointer;">
                <input type="radio" name="gateway" value="wompi" bind:group={selectedGateway} />
                <span>Wompi Bancolombia (PSE, Tarjetas, Nequi)</span>
              </label>
              <label style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; border: 1px solid var(--border); border-radius: 8px; cursor: pointer;">
                <input type="radio" name="gateway" value="whatsapp" bind:group={selectedGateway} />
                <span><i class="fa-brands fa-whatsapp" style="color: #25D366;"></i> Coordinar por WhatsApp</span>
              </label>
            </div>
          </div>

          <button
            class="btn btn-primary"
            style="width: 100%; padding: 1rem; font-size: 1.1rem;"
            onclick={submitDonation}
          >
            Donar ${formatMoneyNumber(currentAmount)} COP {#if isRecurring}(Mensual){/if}
          </button>
        {:else if activeTab === 'patrocinio'}
          <!-- Formulario Patrocinio -->
          <form onsubmit={handleCorporateSubmit} style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
              <label for="empresa-input" class="form-label">Nombre de la Empresa o Institución:</label>
              <input id="empresa-input" type="text" bind:value={empresa} class="form-control" required />
            </div>
            <div>
              <label for="contacto-nombre-input" class="form-label">Persona de Contacto:</label>
              <input id="contacto-nombre-input" type="text" bind:value={nombre} class="form-control" required />
            </div>
            <div>
              <label for="contacto-email-input" class="form-label">Correo Electrónico Corporativo:</label>
              <input id="contacto-email-input" type="email" bind:value={email} class="form-control" required />
            </div>
            <div>
              <label for="contacto-mensaje-input" class="form-label">Mensaje o Propuesta de Alianza:</label>
              <textarea id="contacto-mensaje-input" bind:value={mensaje} class="form-control" rows="3" placeholder="Cuéntanos sobre tu interés..." required></textarea>
            </div>
            <button type="submit" class="btn btn-primary" style="padding: 0.9rem;">
              Enviar Propuesta de Alianza
            </button>
          </form>
        {:else}
          <!-- Formulario Voluntariado -->
          <form onsubmit={handleCorporateSubmit} style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
              <label for="voluntario-nombre-input" class="form-label">Nombre Completo:</label>
              <input id="voluntario-nombre-input" type="text" bind:value={nombre} class="form-control" required />
            </div>
            <div>
              <label for="voluntario-email-input" class="form-label">Correo Electrónico:</label>
              <input id="voluntario-email-input" type="email" bind:value={email} class="form-control" required />
            </div>
            <div>
              <label for="voluntario-tel-input" class="form-label">Teléfono (WhatsApp):</label>
              <input id="voluntario-tel-input" type="tel" bind:value={telefono} class="form-control" required />
            </div>
            <div>
              <label for="voluntario-area-input" class="form-label">Área de Interés:</label>
              <select id="voluntario-area-input" bind:value={area} class="form-control" required>
                <option value="">-- Selecciona un área --</option>
                <option value="salud">Salud Preventiva / Psicología / Fisioterapia</option>
                <option value="huertos">Huertos Comunitarios / Agronomía</option>
                <option value="talleres">Talleres Lúdicos / Música / Manualidades</option>
                <option value="tecnologia">Alfabetización Digital</option>
                <option value="logistica">Logística / Comedor Solidario</option>
              </select>
            </div>
            <button type="submit" class="btn btn-primary" style="padding: 0.9rem;">
              Registrarme como Voluntario
            </button>
          </form>
        {/if}
      {:else if checkoutStep === 'loading'}
        <div style="text-align: center; padding: 3rem 1rem;">
          <div class="spinner" style="margin: 0 auto 1.5rem;"></div>
          <h3 style="color: var(--secondary);">Procesando con la pasarela de pagos...</h3>
          <p style="color: var(--text-muted); margin-top: 0.5rem;">Por favor espera un momento.</p>
        </div>
      {:else if checkoutStep === 'success'}
        <div style="text-align: center; padding: 1.5rem 0.5rem;">
          <div class="success-shield" style="margin-bottom: 1rem;">✓</div>
          <h2 style="color: var(--secondary); margin-bottom: 0.5rem;">¡Aporte Recibido con Éxito!</h2>
          <p style="color: var(--text-muted); max-width: 480px; margin: 0 auto 1.5rem;">
            Tu generosidad transforma vidas en Sincelejo y Sucre. Te hemos enviado la confirmación a tu correo.
          </p>

          {#if donationReceipt.id}
            <div style="background: var(--bg-secondary); border: 1px dashed var(--primary); padding: 1.25rem; border-radius: 12px; text-align: left; font-family: monospace; font-size: 0.85rem; margin-bottom: 1.5rem; white-space: pre-line;">
========================================
     COMPROBANTE DE DONACIÓN - FUNCREES
========================================
ID Donación:    {donationReceipt.id}
Fecha:          {donationReceipt.date}
Concepto:       {donationReceipt.type}
Monto Total:    ${formatMoneyNumber(donationReceipt.amount)} COP
Estado:         CONFIRMADA Y REGISTRADA
========================================
   ¡GRACIAS POR CRECER ESTA ESPERANZA!
========================================
            </div>
          {/if}

          <button class="btn btn-primary" onclick={closeModal} style="padding: 0.75rem 2rem;">
            Cerrar Ventana
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}
