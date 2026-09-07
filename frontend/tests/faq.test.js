import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { FAQ_ITEMS, parsearRespuesta, buildFaqJsonLd } from '../src/lib/data/faq.ts';

describe('FAQ_ITEMS (datos)', () => {
	test('hay contenido suficiente para una página de FAQ (≥8)', () => {
		assert.ok(FAQ_ITEMS.length >= 8, `solo hay ${FAQ_ITEMS.length}`);
	});

	test('ids únicos, válidos como ancla y sin campos vacíos', () => {
		const ids = new Set();
		for (const item of FAQ_ITEMS) {
			assert.ok(!ids.has(item.id), `id duplicado: ${item.id}`);
			ids.add(item.id);
			assert.match(item.id, /^[a-z0-9-]+$/, `id no anclable: ${item.id}`);
			assert.ok(item.pregunta.trim().length >= 10, `pregunta muy corta: ${item.id}`);
			assert.ok(item.respuesta.trim().length >= 30, `respuesta muy corta: ${item.id}`);
		}
	});

	test('los enlaces internos [[/ruta]] apuntan a rutas reales del sitio', () => {
		const rutasValidas = new Set([
			'/donaciones',
			'/boletas',
			'/numeros',
			'/privacidad',
			'/contacto',
			'/preguntas-frecuentes'
		]);
		for (const item of FAQ_ITEMS) {
			for (const m of item.respuesta.matchAll(/\[\[([^\]]+)\]\]/g)) {
				assert.ok(rutasValidas.has(m[1]), `ruta no reconocida en ${item.id}: ${m[1]}`);
			}
		}
	});
});

describe('parsearRespuesta()', () => {
	test('texto sin marcado devuelve un único segmento plano', () => {
		assert.deepEqual(parsearRespuesta('Respuesta simple.'), [
			{ texto: 'Respuesta simple.', href: null }
		]);
	});

	test('convierte [[/ruta]] en un segmento enlazado', () => {
		const segs = parsearRespuesta('Donando [[/donaciones]] hoy.');
		assert.equal(segs.length, 3);
		assert.equal(segs[0].texto, 'Donando ');
		assert.deepEqual(segs[1], { texto: 'aquí', href: '/donaciones' });
		assert.equal(segs[2].texto, ' hoy.');
	});

	test('varios enlaces en la misma respuesta', () => {
		const segs = parsearRespuesta('A [[/donaciones]] y B [[/boletas]].');
		const hrefs = segs.filter((s) => s.href).map((s) => s.href);
		assert.deepEqual(hrefs, ['/donaciones', '/boletas']);
	});

	test('respuesta vacía no explota', () => {
		assert.deepEqual(parsearRespuesta(''), [{ texto: '', href: null }]);
	});
});

describe('buildFaqJsonLd()', () => {
	test('estructura FAQPage con mainEntity por pregunta', () => {
		const ld = buildFaqJsonLd();
		assert.equal(ld['@context'], 'https://schema.org');
		assert.equal(ld['@type'], 'FAQPage');
		assert.equal(ld.mainEntity.length, FAQ_ITEMS.length);
		assert.equal(ld.mainEntity[0]['@type'], 'Question');
		assert.equal(ld.mainEntity[0].acceptedAnswer['@type'], 'Answer');
	});

	test('elimina el marcado [[/ruta]] del texto indexado por Google', () => {
		const conMarcado = [{ id: 'x', pregunta: '¿P?', respuesta: 'Ver [[/donaciones]] y listo.' }];
		const ld = buildFaqJsonLd(conMarcado);
		assert.equal(ld.mainEntity[0].acceptedAnswer.text, 'Ver  y listo.');
		assert.ok(!ld.mainEntity[0].acceptedAnswer.text.includes('[['));
	});

	test('serializa a JSON sin errores (lo que irá al <head>)', () => {
		assert.ok(JSON.stringify(buildFaqJsonLd()).length > 100);
	});
});
