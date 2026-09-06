/**
 * Tests de cifras públicas (/numeros): mapeo a tarjetas y cliente API.
 * Corre con: node --test (mismo runner que los demás tests del frontend).
 */
import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';

const originalFetch = globalThis.fetch;

/** PublicStats de ejemplo (formatos como los entrega el backend Django). */
const STATS_FIXTURE = {
	recaudado_total: 750000,
	recaudado_total_fmt: '$750.000',
	donaciones_count: 8,
	donacion_promedio: 93750,
	donacion_promedio_fmt: '$93.750',
	beneficiarios_activos: 50,
	beneficiarios_apadrinados: 13,
	ciudades_atendidas: 4,
	apadrinamientos_activos: 2,
	serie_mensual: [
		{ mes: 'Jun', anio: 2026, total: 750000, total_fmt: '$750.000', total_fmt_corto: '$750 mil', cantidad: 8, pct: 100, es_actual: false },
		{ mes: 'Sep', anio: 2026, total: 0, total_fmt: '$0', total_fmt_corto: '$0', cantidad: 0, pct: 0, es_actual: true }
	],
	actualizado_en: '2026-09-05T12:00:00-05:00'
};

describe('mapStatsToCards()', async () => {
	let client;

	beforeEach(async () => {
		client = await import('../src/lib/api/client.ts');
	});

	test('genera una tarjeta por cifra, con icono y etiqueta', () => {
		const cards = client.mapStatsToCards(STATS_FIXTURE);
		assert.equal(cards.length, 6);
		assert.ok(cards.every((c) => c.key && c.icon && c.label && typeof c.value === 'string'));
	});

	test('el total recaudado usa el formato del backend + COP', () => {
		const cards = client.mapStatsToCards(STATS_FIXTURE);
		const recaudado = cards.find((c) => c.key === 'recaudado');
		assert.equal(recaudado.value, '$750.000 COP');
	});

	test('los conteos se formatean al estándar colombiano', () => {
		const cards = client.mapStatsToCards(STATS_FIXTURE);
		assert.equal(cards.find((c) => c.key === 'beneficiarios').value, '50');
		assert.equal(cards.find((c) => c.key === 'donaciones').value, '8');
	});

	test('formatea miles con punto: 1234 → "1.234"', () => {
		const cards = client.mapStatsToCards({ ...STATS_FIXTURE, beneficiarios_activos: 1234 });
		assert.equal(cards.find((c) => c.key === 'beneficiarios').value, '1.234');
	});
});

describe('API client — getPublicStats()', async () => {
	let client;

	beforeEach(async () => {
		client = await import('../src/lib/api/client.ts');
	});

	afterEach(() => {
		globalThis.fetch = originalFetch;
	});

	test('retorna las cifras en respuesta 200', async () => {
		globalThis.fetch = async () =>
			new Response(JSON.stringify(STATS_FIXTURE), { status: 200 });

		const stats = await client.getPublicStats();
		assert.equal(stats.recaudado_total_fmt, '$750.000');
		assert.equal(stats.serie_mensual.length, 2);
		assert.equal(stats.serie_mensual[1].es_actual, true);
	});

	test('lanza ApiError con status HTTP si el backend falla', async () => {
		globalThis.fetch = async () => new Response('error', { status: 503 });

		await assert.rejects(
			() => client.getPublicStats(),
			(err) => {
				assert.ok(err instanceof client.ApiError);
				assert.equal(err.status, 503);
				return true;
			}
		);
	});
});
