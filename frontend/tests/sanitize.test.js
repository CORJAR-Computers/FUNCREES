import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { sanitizeHTML } from '../src/lib/utils/sanitize.ts';

describe('sanitizeHTML()', () => {
	test('escapa tags HTML para prevenir XSS', () => {
		assert.equal(sanitizeHTML('<script>alert(1)</script>'), '&lt;script&gt;alert(1)&lt;/script&gt;');
	});

	test('escapa comillas y atributos', () => {
		assert.equal(sanitizeHTML('<img src="x" onerror="alert(1)">'), '&lt;img src=&quot;x&quot; onerror=&quot;alert(1)&quot;&gt;');
	});

	test('devuelve string vacío para null o undefined', () => {
		assert.equal(sanitizeHTML(null), '');
		assert.equal(sanitizeHTML(undefined), '');
	});

	test('preserva texto plano', () => {
		assert.equal(sanitizeHTML('Hola mundo'), 'Hola mundo');
	});
});
