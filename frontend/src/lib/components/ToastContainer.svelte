<script>
  import { toast } from '$lib/stores/toast.svelte.js';

  /** @type {Record<string, string>} */
  const iconMap = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };
</script>

{#if toast.toasts.length > 0}
  <div class="toast-container" id="toast-container" aria-live="polite">
    {#each toast.toasts as item (item.id)}
      <div class="toast-item {item.type}" role="alert">
        <span class="toast-icon">{iconMap[item.type] || '✓'}</span>
        <span class="toast-message">{item.message}</span>
        <button class="toast-close" onclick={() => toast.remove(item.id)} aria-label="Cerrar notificación">×</button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .toast-container {
    position: fixed;
    bottom: 5rem;
    right: 1.5rem;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    max-width: 400px;
    pointer-events: none;
  }
  .toast-item {
    pointer-events: auto;
    color: #fff;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    font-family: var(--font-body, 'Inter', sans-serif);
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    animation: toastSlideIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
  }
  .toast-item.success { background: #16a34a; }
  .toast-item.error { background: #dc2626; }
  .toast-item.warning { background: #f59e0b; }
  .toast-item.info { background: #0284c7; }

  .toast-icon {
    font-size: 1.2rem;
    font-weight: 800;
    flex-shrink: 0;
  }
  .toast-message {
    flex-grow: 1;
  }
  .toast-close {
    background: transparent;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    line-height: 1;
    opacity: 0.8;
  }
  .toast-close:hover {
    opacity: 1;
  }

  @keyframes toastSlideIn {
    from {
      opacity: 0;
      transform: translateX(100px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
</style>
