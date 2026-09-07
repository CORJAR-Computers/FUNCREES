// ESLint 9 (flat config) para el frontend SvelteKit 2 + Svelte 5.
// Filosofía: detectar errores reales y variables muertas; el tipado fuerte
// ya lo cubre svelte-check, así que no duplicamos reglas de estilo de código.
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';

/** Globals navegador + Node que el código usa directamente (sin imports). */
const browserGlobals = {
	window: 'readonly',
	document: 'readonly',
	localStorage: 'readonly',
	console: 'readonly',
	fetch: 'readonly',
	Response: 'readonly',
	Request: 'readonly',
	Headers: 'readonly',
	AbortSignal: 'readonly',
	AbortController: 'readonly',
	FormData: 'readonly',
	HTMLElement: 'readonly',
	URL: 'readonly',
	URLSearchParams: 'readonly',
	SubmitEvent: 'readonly',
	Event: 'readonly',
	KeyboardEvent: 'readonly',
	MouseEvent: 'readonly',
	SpeechSynthesisUtterance: 'readonly',
	ShareData: 'readonly',
	HTMLDivElement: 'readonly',
	HTMLDialogElement: 'readonly',
	HTMLInputElement: 'readonly',
	HTMLButtonElement: 'readonly',
	HTMLTextAreaElement: 'readonly',
	HTMLSelectElement: 'readonly',
	HTMLImageElement: 'readonly',
	IntersectionObserver: 'readonly',
	ResizeObserver: 'readonly',
	requestAnimationFrame: 'readonly',
	cancelAnimationFrame: 'readonly',
	getComputedStyle: 'readonly',
	matchMedia: 'readonly',
	navigator: 'readonly',
	location: 'readonly',
	history: 'readonly',
	process: 'readonly',
	setInterval: 'readonly',
	clearInterval: 'readonly',
	setTimeout: 'readonly',
	clearTimeout: 'readonly'
};

export default tseslint.config(
	js.configs.recommended,
	...tseslint.configs.recommended,
	...svelte.configs['flat/recommended'],
	{
		ignores: [
			'.svelte-kit/**',
			'build/**',
			'node_modules/**',
			'static/**',
			'*.config.js',
			'*.config.ts'
		]
	},
	{
		files: ['**/*.js', '**/*.ts', '**/*.svelte'],
		languageOptions: {
			ecmaVersion: 2023,
			sourceType: 'module',
			globals: browserGlobals
		},
		rules: {
			'no-unused-vars': 'off',
			'@typescript-eslint/no-unused-vars': [
				'error',
				{ argsIgnorePattern: '^_', varsIgnorePattern: '^_', ignoreRestSiblings: true }
			],
			eqeqeq: ['warn', 'smart'],
			'prefer-const': 'warn'
		}
	},
	{
		// Módulos con runas (toast.svelte.ts): TS normal para el parser.
		files: ['**/*.svelte.ts'],
		languageOptions: { parser: tseslint.parser }
	},
	{
		// Svelte: parser TS para <script lang="ts"> y runas de Svelte 5.
		files: ['**/*.svelte'],
		languageOptions: {
			parserOptions: {
				parser: tseslint.parser,
				svelteFeatures: { runes: true }
			}
		},
		rules: {
			// Convención del proyecto: hrefs de SvelteKit como string literal
			// ("/donaciones"). Migrar todo a resolve() es una pasada futura;
			// la regla se desactiva para no generar ruido en cada página.
			'svelte/no-navigation-without-resolve': 'off',
			// El <\/script> escapado dentro del template literal del JSON-LD es
			// NECESARIO: un </script> literal rompería el parsing del documento.
			'no-useless-escape': 'off',
			// Único {@html} del sitio: JSON-LD en Seo.svelte generado con
			// JSON.stringify de datos internos (nunca entrada de usuario).
			'svelte/no-at-html-tags': 'off'
		}
	}
);
