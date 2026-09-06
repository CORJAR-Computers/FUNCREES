import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { parseCOP, formatMoneyNumber } from '../src/lib/utils/currency.ts';

describe('parseCOP()', () => {
	test('parsea formato colombiano con punto de miles: "10.000"', () => {
		assert.equal(parseCOP('10.000'), 10000);
	});

	test('parsea formato con símbolo $: "$200.000"', () => {
		assert.equal(parseCOP('$200.000'), 200000);
	});

	test('parsea número entero sin formato', () => {
		assert.equal(parseCOP(50000), 50000);
	});

	test('devuelve 0 para entradas inválidas o vacías', () => {
		assert.equal(parseCOP(''), 0);
		assert.equal(parseCOP(null), 0);
		assert.equal(parseCOP(undefined), 0);
		assert.equal(parseCOP('abc'), 0);
	});
});

describe('formatMoneyNumber()', () => {
	test('formatea 50000 como "50.000"', () => {
		assert.equal(formatMoneyNumber(50000), '50.000');
	});

	test('formatea 1000000 como "1.000.000"', () => {
		assert.equal(formatMoneyNumber(1000000), '1.000.000');
	});

	test('formatea 0 como "0"', () => {
		assert.equal(formatMoneyNumber(0), '0');
	});

	test('trunca decimales a 2 posiciones', () => {
		assert.equal(formatMoneyNumber(1000.555), '1.000,55');
	});
});
