<script>
  import { onMount } from 'svelte';

  let isVisible = $state(false);
  let showConfig = $state(false);
  let analyticsCookies = $state(false);
  let marketingCookies = $state(false);

  onMount(() => {
    const saved = localStorage.getItem('funcrees_cookie_consent');
    if (!saved) {
      isVisible = true;
    } else {
      try {
        const parsed = JSON.parse(saved);
        analyticsCookies = !!parsed.analytics;
        marketingCookies = !!parsed.marketing;
      } catch {
        // Formato antiguo o inválido
      }
    }
  });

  /**
   * @param {boolean} analytics
   * @param {boolean} marketing
   */
  function saveConsent(analytics, marketing) {
    const consent = {
      essential: true,
      analytics,
      marketing,
      date: new Date().toISOString()
    };
    localStorage.setItem('funcrees_cookie_consent', JSON.stringify(consent));
    isVisible = false;
  }

  function acceptAll() {
    saveConsent(true, true);
  }

  function acceptEssential() {
    saveConsent(false, false);
  }

  function saveCustomPrefs() {
    saveConsent(analyticsCookies, marketingCookies);
  }
</script>

{#if isVisible}
  <div
    class="cookie-banner"
    id="cookie-banner"
    role="dialog"
    aria-modal="false"
    aria-labelledby="cookie-title"
    aria-describedby="cookie-desc"
  >
    <div class="cookie-banner__inner">
      <div class="cookie-banner__header">
        <span class="cookie-banner__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" focusable="false" width="24" height="24">
            <path d="M21.6 11.2c-.3-.2-.7-.2-1-.1-.4.1-.8 0-1.1-.3-.3-.3-.4-.7-.3-1.1.1-.4 0-.8-.3-1.1-.3-.3-.7-.4-1.1-.3-.4.1-.8 0-1.1-.3-.3-.3-.4-.7-.3-1.1.1-.4 0-.8-.3-1.1-.3-.3-.7-.4-1.1-.3-.4.1-.8 0-1.1-.3-.3-.3-.4-.7-.3-1.1.1-.4 0-.8-.3-1.1-.5-.5-1.3-.5-1.8 0L8.6 5.6c-3.1 1.5-5.2 4.7-5.2 8.4 0 5.2 4.2 9.4 9.4 9.4 4.1 0 7.6-2.6 8.9-6.3.1-.3.3-.6.6-.7.4-.2.6-.6.6-1V12c0-.3-.1-.6-.3-.8zM12 21c-3.9 0-7-3.1-7-7 0-3 1.9-5.5 4.5-6.5.2.4.6.7 1.1.8.4.1.7.4.8.8.1.4.4.7.8.8.4.1.7.4.8.8.1.4.4.7.8.8.4.1.7.4.8.8.1.4.4.7.8.8.3.1.6.3.8.6C19.5 18.5 16.1 21 12 21z"/>
            <circle cx="9" cy="14" r="1.2"/>
            <circle cx="12" cy="17" r="1.2"/>
            <circle cx="15" cy="14" r="1.2"/>
          </svg>
        </span>
        <h3 class="cookie-banner__title" id="cookie-title">Cookies &amp; Privacidad</h3>
      </div>

      <p class="cookie-banner__desc" id="cookie-desc">
        Usamos cookies esenciales para el funcionamiento del sitio y cookies analíticas para mejorar tu experiencia según la Ley 1581 de 2012 de Colombia.
      </p>

      <div class="cookie-banner__actions">
        <button type="button" class="cookie-btn cookie-btn-accept" onclick={acceptAll}>
          Aceptar todas
        </button>
        <button type="button" class="cookie-btn cookie-btn-essential" onclick={acceptEssential}>
          Solo esenciales
        </button>
        <button
          type="button"
          class="cookie-btn cookie-btn-config"
          onclick={() => showConfig = !showConfig}
          aria-expanded={showConfig}
        >
          {showConfig ? 'Ocultar ajustes' : 'Configurar'}
        </button>
      </div>

      {#if showConfig}
        <div class="cookie-prefs">
          <div class="cookie-prefs__row">
            <div class="cookie-prefs__info">
              <span class="cookie-prefs__label">Cookies esenciales</span>
              <span class="cookie-prefs__desc">Necesarias para el funcionamiento del sitio web.</span>
            </div>
            <span style="font-size: 0.85rem; font-weight: 700; color: var(--primary-dark);">Siempre activas</span>
          </div>

          <div class="cookie-prefs__row">
            <div class="cookie-prefs__info">
              <span class="cookie-prefs__label">Cookies analíticas</span>
              <span class="cookie-prefs__desc">Nos ayudan a entender de forma anónima cómo navegan los usuarios.</span>
            </div>
            <label class="cookie-switch">
              <input type="checkbox" bind:checked={analyticsCookies} aria-label="Activar cookies analíticas" />
              <span class="cookie-switch__track"></span>
            </label>
          </div>

          <div class="cookie-prefs__row">
            <div class="cookie-prefs__info">
              <span class="cookie-prefs__label">Cookies de difusión social</span>
              <span class="cookie-prefs__desc">Permiten compartir contenido en redes sociales y campañas.</span>
            </div>
            <label class="cookie-switch">
              <input type="checkbox" bind:checked={marketingCookies} aria-label="Activar cookies de marketing" />
              <span class="cookie-switch__track"></span>
            </label>
          </div>

          <button type="button" class="cookie-btn cookie-btn-save" onclick={saveCustomPrefs}>
            Guardar preferencias
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}
