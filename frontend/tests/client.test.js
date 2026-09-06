/**
 * Tests del cliente API con fetch mockeado (Node nativo --experimental-strip-types).
 */
import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';

const originalFetch = globalThis.fetch;

describe('API client — initiateDonation()', async () => {
	let client;

	beforeEach(async () => {
		// Import fresco del módulo para cada test
		client = await import('../src/lib/api/client.ts');
	});

	afterEach(() => {
		globalThis.fetch = originalFetch;
	});

	test('retorna paymentSession en respuesta 201', async () => {
		const fakeSession = {
			publicKey: 'pub_test',
			reference: 'GEN-ABC12345',
			amountInCents: 5000000,
			currency: 'COP',
			integritySignature: 'sig',
			redirectUrl: 'https://x.dev?pago=exitoso',
			customerEmail: 'a@b.co',
			description: 'Donación',
			wompiCheckoutUrl: 'https://sandbox.wompi.co/en-us/checkout/pub_test'
		};
		globalThis.fetch = async () =>
			new Response(JSON.stringify({ success: true, referencia: 'GEN-ABC12345', paymentSession: fakeSession }), {
				status: 201
			});

		const res = await client.initiateDonation({
			tipo: 'general',
			monto: 50000,
			donante_nombre: 'Test',
			donante_email: 'a@b.co',
			metodo_pago: 'card',
			autorizacion_datos: true
		});

		assert.equal(res.referencia, 'GEN-ABC12345');
		assert.equal(res.paymentSession.amountInCents, 5000000);
	});

	test('lanza ApiError con mensaje del backend en error 400', async () => {
		globalThis.fetch = async () =>
			new Response(JSON.stringify({ error: 'Debe aceptar el tratamiento de datos.' }), { status: 400 });

		await assert.rejects(
			client.initiateDonation({
				tipo: 'general',
				monto: 50000,
				donante_nombre: 'Test',
				donante_email: 'a@b.co',
				metodo_pago: 'card',
				autorizacion_datos: false
			}),
			(err) => {
				assert.ok(err instanceof client.ApiError);
				assert.equal(err.message, 'Debe aceptar el tratamiento de datos.');
				assert.equal(err.status, 400);
				return true;
			}
		);
	});
});

describe('API client — pollDonationStatus()', async () => {
	let client;

	beforeEach(async () => {
		client = await import('../src/lib/api/client.ts');
	});

	afterEach(() => {
		globalThis.fetch = originalFetch;
	});

	test('retorna inmediatamente en estado terminal', async () => {
		let calls = 0;
		globalThis.fetch = async () => {
			calls++;
			return new Response(
				JSON.stringify({
					success: true,
					donacion: { referencia: 'R1', estado: 'completado' }
				}),
				{ status: 200 }
			);
		};

		const donacion = await client.pollDonationStatus('R1', { intervalMs: 1, maxAttempts: 5 });
		assert.equal(donacion.estado, 'completado');
		assert.equal(calls, 1);
	});

	test('reintenta en estados no terminales hasta llegar a terminal', async () => {
		let calls = 0;
		globalThis.fetch = async () => {
			calls++;
			const estado = calls < 3 ? 'pendiente' : 'completado';
			return new Response(
				JSON.stringify({ success: true, donacion: { referencia: 'R2', estado } }),
				{ status: 200 }
			);
		};

		const donacion = await client.pollDonationStatus('R2', { intervalMs: 1, maxAttempts: 10 });
		assert.equal(donacion.estado, 'completado');
		assert.equal(calls, 3);
	});

	test('retorna el último estado conocido si nunca llega a terminal', async () => {
		globalThis.fetch = async () =>
			new Response(
				JSON.stringify({ success: true, donacion: { referencia: 'R3', estado: 'pendiente' } }),
				{ status: 200 }
			);

		// No rechaza: devuelve el último estado para que la UI informe honestamente
		const donacion = await client.pollDonationStatus('R3', { intervalMs: 1, maxAttempts: 2 });
		assert.equal(donacion.estado, 'pendiente');
	});
});

describe('API client — sendContactMessage()', async () => {
	let client;

	beforeEach(async () => {
		client = await import('../src/lib/api/client.ts');
	});

	afterEach(() => {
		globalThis.fetch = originalFetch;
	});

	test('resuelve sin valor en 201', async () => {
		globalThis.fetch = async () => new Response(JSON.stringify({ id: 'x' }), { status: 201 });
		await assert.doesNotReject(() => client.sendContactMessage({ nombre: 'A', email: 'a@b.co', mensaje: 'hola' }));
	});

	test('lanza ApiError con detalle de validación en 400', async () => {
		globalThis.fetch = async () =>
			new Response(JSON.stringify({ telefono: ['El teléfono debe tener 10 dígitos (ej: 3101234567) o 12 con prefijo internacional (ej: 573101234567).'] }), { status: 400 });

		await assert.rejects(
			() => client.sendContactMessage({ nombre: 'A', email: 'a@b.co', telefono: '123', mensaje: 'x' }),
			(err) => {
				assert.ok(err instanceof client.ApiError);
				assert.match(err.message, /teléfono/i);
				return true;
			}
		);
	});
});
