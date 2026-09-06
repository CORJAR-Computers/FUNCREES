<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from '$lib/stores/toast.svelte';

	let isOpen = $state(false);
	let fontScale = $state(1.0);
	let highContrast = $state(false);
	let dyslexiaFont = $state(false);
	let ttsEnabled = $state(false);

	function applySettings(): void {
		document.documentElement.style.setProperty('--font-scale', String(fontScale));
		document.body.classList.toggle('high-contrast', highContrast);
		document.body.classList.toggle('dyslexia-font', dyslexiaFont);

		localStorage.setItem(
			'funcrees_acc_settings',
			JSON.stringify({ fontScale, highContrast, dyslexiaFont, ttsEnabled })
		);
	}

	function incFontSize(): void {
		if (fontScale < 1.4) {
			fontScale = parseFloat((fontScale + 0.1).toFixed(1));
			applySettings();
		}
	}

	function decFontSize(): void {
		if (fontScale > 0.8) {
			fontScale = parseFloat((fontScale - 0.1).toFixed(1));
			applySettings();
		}
	}

	function toggleContrast(): void {
		highContrast = !highContrast;
		applySettings();
	}

	function toggleDyslexia(): void {
		dyslexiaFont = !dyslexiaFont;
		applySettings();
	}

	function toggleVoiceReader(): void {
		ttsEnabled = !ttsEnabled;
		applySettings();
		if (ttsEnabled) {
			toast.show('Lector de voz activado. Selecciona texto para escuchar.', 'success');
			const u = new SpeechSynthesisUtterance('Lector de pantalla activado para la Fundación Funcrees Colombia.');
			u.lang = 'es-CO';
			window.speechSynthesis?.speak(u);
		} else {
			window.speechSynthesis?.cancel();
			toast.show('Lector de voz desactivado.', 'info');
		}
	}

	onMount(() => {
		const saved = localStorage.getItem('funcrees_acc_settings');
		if (saved) {
			try {
				const parsed = JSON.parse(saved) as Partial<{
					fontScale: number;
					highContrast: boolean;
					dyslexiaFont: boolean;
					ttsEnabled: boolean;
				}>;
				fontScale = parsed.fontScale ?? 1.0;
				highContrast = !!parsed.highContrast;
				dyslexiaFont = !!parsed.dyslexiaFont;
				ttsEnabled = !!parsed.ttsEnabled;
				applySettings();
			} catch {
				// Formato no válido
			}
		}
	});
</script>

<div class="accessibility-widget">
	<button
		class="acc-btn-main"
		id="acc-widget-btn"
		aria-label="Abrir panel de opciones de accesibilidad visual"
		aria-expanded={isOpen}
		title="Opciones de Accesibilidad"
		onclick={() => isOpen = !isOpen}
	>
		<i class="fa-solid fa-universal-access"></i>
	</button>

	{#if isOpen}
		<div class="acc-panel active" id="acc-panel" role="region" aria-label="Panel de opciones de accesibilidad">
			<div class="acc-panel-header">
				<h3 class="acc-panel-title"><i class="fa-solid fa-sliders"></i> Accesibilidad</h3>
				<button class="acc-panel-close" onclick={() => isOpen = false} aria-label="Cerrar panel de accesibilidad">✕</button>
			</div>

			<!-- Tamaño del Texto -->
			<div class="acc-control-group">
				<span class="acc-control-label">Tamaño del Texto ({Math.round(fontScale * 100)}%)</span>
				<div class="acc-btn-row">
					<button class="acc-action-btn" onclick={decFontSize} aria-label="Reducir tamaño de letra" disabled={fontScale <= 0.8}>
						<i class="fa-solid fa-minus"></i> A-
					</button>
					<button class="acc-action-btn" onclick={incFontSize} aria-label="Aumentar tamaño de letra" disabled={fontScale >= 1.4}>
						<i class="fa-solid fa-plus"></i> A+
					</button>
				</div>
			</div>

			<!-- Alto Contraste -->
			<div class="acc-control-group">
				<span class="acc-control-label">Contraste de Pantalla</span>
				<button
					class="acc-action-btn"
					class:active={highContrast}
					onclick={toggleContrast}
					aria-label="Alternar modo de alto contraste para baja visión"
				>
					<i class="fa-solid fa-circle-half-stroke"></i> Alto Contraste
				</button>
			</div>

			<!-- Tipografía Dislexia -->
			<div class="acc-control-group">
				<span class="acc-control-label">Tipo de Letra</span>
				<button
					class="acc-action-btn"
					class:active={dyslexiaFont}
					onclick={toggleDyslexia}
					aria-label="Alternar tipografía adaptada para dislexia"
				>
					<i class="fa-solid fa-font"></i> Fuente Fácil Lectura
				</button>
			</div>

			<!-- Lector de Voz -->
			<div class="acc-control-group">
				<span class="acc-control-label">Lector de Voz</span>
				<button
					class="acc-action-btn"
					class:active={ttsEnabled}
					onclick={toggleVoiceReader}
					aria-label="Alternar lector de pantalla simulado por voz"
				>
					<i class="fa-solid fa-volume-high"></i> {ttsEnabled ? 'Lector Activado' : 'Activar Lector por Voz'}
				</button>
			</div>
		</div>
	{/if}
</div>
