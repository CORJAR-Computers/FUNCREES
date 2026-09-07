import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { buildBoletaDeepLink, CODIGO_PATTERN } from '../src/lib/utils/qr.ts';

describe('buildBoletaDeepLink()', () => {
	test('construye la URL de consulta con el código en mayúsculas', () => {
		assert.equal(
			buildBoletaDeepLink('https://funcreescolombia.org', 'ofmrhoozyt'),
			'https://funcreescolombia.org/boletas?codigo=OFMRHOOZYT'
		);
	});

	test('normaliza espacios y minúsculas del código', () => {
		assert.equal(
			buildBoletaDeepLink('https://x.org', ' a1b2c3d4e5 '),
			'https://x.org/boletas?codigo=A1B2C3D4E5'
		);
	});

	test('tolera origin con barra final sin duplicar slash', () => {
		assert.equal(
			buildBoletaDeepLink('https://x.org///', 'A1B2C3D4E5'),
			'https://x.org/boletas?codigo=A1B2C3D4E5'
		);
	});

	test('devuelve null si el código no tiene 10 caracteres alfanuméricos', () => {
		assert.equal(buildBoletaDeepLink('https://x.org', 'CORTO'), null);
		assert.equal(buildBoletaDeepLink('https://x.org', 'A1B2C3D4E!'), null);
		assert.equal(buildBoletaDeepLink('https://x.org', ''), null);
	});

	test('devuelve null si el origin está vacío', () => {
		assert.equal(buildBoletaDeepLink('', 'A1B2C3D4E5'), null);
		assert.equal(buildBoletaDeepLink('   ', 'A1B2C3D4E5'), null);
	});

	test('CODIGO_PATTERN coincide con el patrón oficial de 10 caracteres', () => {
		assert.equal(CODIGO_PATTERN.test('OFMRHOOZYT'), true);
		assert.equal(CODIGO_PATTERN.test('A1B2C3D4E5'), true);
		assert.equal(CODIGO_PATTERN.test('a1b2c3d4e5'), false); // exige mayúsculas
		assert.equal(CODIGO_PATTERN.test('A1B2C3D4E'), false); // 9
	});
});
