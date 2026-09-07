<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		/** Controla apertura/cierre desde el estado de la página. */
		open: boolean;
		/** Callback al cerrar (Escape, click en backdrop o botón cerrar). */
		onclose: () => void;
		/** id del título (h2) para aria-labelledby. */
		labelledby: string;
		children: Snippet;
	}

	const { open, onclose, labelledby, children }: Props = $props();

	let dialogEl = $state<HTMLDialogElement | null>(null);

	$effect(() => {
		if (!dialogEl) return;
		if (open && !dialogEl.open) {
			dialogEl.showModal();
		} else if (!open && dialogEl.open) {
			dialogEl.close();
		}
	});
</script>

<!--
	<dialog> nativo: focus trap automático, Escape nativo (evento cancel -> close)
	y pseudo-elemento ::backdrop. El click fuera se detecta en el propio dialog.
-->
<div style="display: contents;">
	<dialog
		bind:this={dialogEl}
		class="modal-dialog"
		aria-labelledby={labelledby}
		onclose={onclose}
		onclick={(e) => {
			// Click directo sobre el dialog = click en el backdrop (fuera del card).
			if (e.target === dialogEl) onclose();
		}}
	>
		<button class="modal-close" onclick={onclose} aria-label="Cerrar modal">✕</button>
		{@render children()}
	</dialog>
</div>

<style>
	/*
	 * Reutiliza las variables del design system (components.css .modal-card)
	 * sobrescribiendo los estilos por defecto de <dialog>.
	 */
	.modal-dialog {
		border: 1px solid var(--border-color);
		border-radius: var(--radius-lg);
		background-color: var(--bg-card);
		color: var(--text);
		box-shadow: var(--shadow-lg);
		width: min(620px, calc(100vw - 2rem));
		max-width: 620px;
		max-height: min(90vh, 900px);
		overflow-y: auto;
		padding: 2rem;
		margin: auto;
		animation: modalSlideIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
	}

	.modal-dialog::backdrop {
		background-color: rgba(12, 35, 48, 0.6);
		backdrop-filter: blur(4px);
	}

	.modal-close {
		position: absolute;
		top: 1.5rem;
		right: 1.5rem;
		width: 36px;
		height: 36px;
		border-radius: var(--radius-round);
		background-color: var(--bg-primary);
		border: none;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		color: var(--text-muted);
		font-size: 1.2rem;
		transition: var(--transition);
		z-index: 5;
	}

	.modal-close:hover {
		background-color: var(--primary-trans);
		color: var(--primary-dark);
	}

	@keyframes modalSlideIn {
		from {
			opacity: 0;
			transform: translateY(24px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
