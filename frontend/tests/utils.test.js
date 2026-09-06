import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { parseCOP, formatMoneyNumber } from '../src/lib/utils/currency.ts';
import { sanitizeHTML } from '../src/lib/utils/sanitize.ts';

describe('SvelteKit Utils — parseCOP()', () => {
  test('parsea formato colombiano con punto de miles: "10.000"', () => {
    assert.equal(parseCOP('10.000'), 10000);
  });

  test('parsea formato con símbolo $: "$200.000"', () => {
    assert.equal(parseCOP('$200.000'), 200000);
  });

  test('devuelve 0 para entradas inválidas o vacías', () => {
    assert.equal(parseCOP(''), 0);
    assert.equal(parseCOP(null), 0);
  });
});

describe('SvelteKit Utils — formatMoneyNumber()', () => {
  test('formatea 50000 como "50.000"', () => {
    assert.equal(formatMoneyNumber(50000), '50.000');
  });

  test('formatea 1000000 como "1.000.000"', () => {
    assert.equal(formatMoneyNumber(1000000), '1.000.000');
  });

  test('formatea 0 como "0"', () => {
    assert.equal(formatMoneyNumber(0), '0');
  });
});

describe('SvelteKit Utils — sanitizeHTML()', () => {
  test('escapa tags HTML para prevenir XSS', () => {
    assert.equal(sanitizeHTML('<script>alert(1)</script>'), '&lt;script&gt;alert(1)&lt;/script&gt;');
  });

  test('devuelve string vacío para null o undefined', () => {
    assert.equal(sanitizeHTML(null), '');
    assert.equal(sanitizeHTML(undefined), '');
  });
});
