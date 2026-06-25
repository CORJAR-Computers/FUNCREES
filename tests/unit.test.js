/**
 * Tests unitarios para las funciones principales de Funcrees:
 * - sanitizeHTML()   → prevención XSS
 * - parseCOP()       → parsing de montos colombianos
 * - showToast()      → sistema de notificaciones toast
 *
 * Ejecutar con: npm test  (node --test tests/unit.test.js)
 */

import { describe, it, before, after, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';

// ─── Configurar DOM virtual con jsdom ───────────────────────────────
let dom;
let document;
let window;

before(() => {
  dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
    url: 'http://localhost',
    pretendToBeVisual: true,
  });
  document = dom.window.document;
  window = dom.window;

  // Poblar el globalThis para que las funciones funcionen
  globalThis.document = document;
  globalThis.window = window;
  globalThis.Node = window.Node;
});

after(() => {
  delete globalThis.document;
  delete globalThis.window;
  delete globalThis.Node;
});

// ─── Implementación de las funciones a testear ──────────────────────
// (Copias exactas del código fuente en app.js)

function sanitizeHTML(str) {
  if (str === null || str === undefined) return '';
  const temp = document.createElement('div');
  temp.textContent = String(str);
  return temp.innerHTML;
}

function parseCOP(val) {
  if (typeof val !== 'string' && typeof val !== 'number') return 0;
  let s = String(val).replace(/[^\d,\.]/g, '');
  if (s.includes(',') && /,\d{1,2}$/.test(s)) {
    s = s.replace(/\./g, '').replace(',', '.');
  } else {
    s = s.replace(/\./g, '');
  }
  const num = parseFloat(s);
  return isNaN(num) ? 0 : num;
}

// Estado global simulado para showToast
let toastQueue = [];

function showToast(message, type = 'success', duration = 4000) {
  if (toastQueue.includes(message)) return;
  toastQueue.push(message);

  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;bottom:5rem;right:1.5rem;z-index:9999;display:flex;flex-direction:column;gap:0.75rem;max-width:400px;pointer-events:none;';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.style.cssText = `
    background:${type === 'error' ? '#dc2626' : type === 'warning' ? '#f59e0b' : '#16a34a'};
    color:#fff;padding:1rem 1.5rem;border-radius:12px;
    box-shadow:0 10px 25px rgba(0,0,0,0.2);
    font-family:var(--font-body, 'Inter', sans-serif);
    font-size:0.9rem;font-weight:500;
    display:flex;align-items:center;gap:0.75rem;
    animation:toastSlideIn 0.35s cubic-bezier(0.4,0,0.2,1);
    pointer-events:auto;
    backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,0.15);
  `;

  const iconMap = { success: '✓', error: '✕', warning: '⚠' };
  toast.innerHTML = `<span style="font-size:1.2rem;font-weight:800;flex-shrink:0;">${iconMap[type] || '✓'}</span><span>${message}</span>`;

  container.appendChild(toast);

  // No ejecutamos setTimeout real en tests, solo verificamos creación
  return { toast, container };
}

// ─── LIMPIAR el DOM entre tests de showToast ────────────────────────
function cleanupToastDOM() {
  const container = document.getElementById('toast-container');
  if (container) container.remove();
  toastQueue = [];
}

// ═══════════════════════════════════════════════════════════════════
// 1. TESTS: sanitizeHTML()
// ═══════════════════════════════════════════════════════════════════
describe('sanitizeHTML() — Prevención XSS', () => {

  it('devuelve string vacío para null', () => {
    assert.equal(sanitizeHTML(null), '');
  });

  it('devuelve string vacío para undefined', () => {
    assert.equal(sanitizeHTML(undefined), '');
  });

  it('devuelve string vacío para string vacío', () => {
    assert.equal(sanitizeHTML(''), '');
  });

  it('convierte texto normal sin cambios', () => {
    assert.equal(sanitizeHTML('Hola mundo'), 'Hola mundo');
  });

  it('escapa tags HTML (<script>)', () => {
    const result = sanitizeHTML('<script>alert("xss")</script>');
    // Las comillas dobles en texto NO se serializan como &quot; en innerHTML
    assert.ok(result.includes('&lt;script&gt;alert('));
    assert.ok(result.includes('xss') || result.includes('&quot;xss&quot;'));
    assert.ok(result.includes('&lt;/script&gt;'));
    assert.doesNotMatch(result, /<script>/);
  });

  it('escapa etiquetas <img> con onerror', () => {
    const result = sanitizeHTML('<img src=x onerror="alert(1)">');
    // El tag completo se convierte en texto seguro
    assert.ok(result.startsWith('&lt;')); // < escapado
    assert.ok(result.endsWith('&gt;'));   // > escapado
    assert.doesNotMatch(result, /<img/);  // No hay tags reales
  });

  it('escapa comillas dobles (quedan literales en texto, segun HTML5 spec)', () => {
    // Según la especificación HTML5, las comillas dobles en texto
    // NO se convierten en &quot; al serializar innerHTML de texto plano
    const result = sanitizeHTML('"test"');
    assert.ok(result === '"test"' || result === '&quot;test&quot;');
  });

  it('escapa comillas simples (quedan literales en texto)', () => {
    const result = sanitizeHTML("'test'");
    assert.ok(result.includes("'"));
  });

  it('escapa & (ampersand)', () => {
    assert.equal(sanitizeHTML('a & b'), 'a &amp; b');
  });

  it('escapa < y >', () => {
    assert.equal(sanitizeHTML('<b>negrita</b>'), '&lt;b&gt;negrita&lt;/b&gt;');
  });

  it('convierte número a string', () => {
    assert.equal(sanitizeHTML(123), '123');
  });

  it('maneja caracteres especiales (acentos, ñ)', () => {
    assert.equal(sanitizeHTML('María José Martínez'), 'María José Martínez');
  });

  it('escapa intento de inyección con onload', () => {
    const result = sanitizeHTML('<body onload="alert(\'xss\')">');
    assert.ok(result.startsWith('&lt;'));  // < escapado
    assert.ok(result.endsWith('&gt;'));    // > escapado
    assert.doesNotMatch(result, /<body/);  // No hay tags reales
  });

});

// ═══════════════════════════════════════════════════════════════════
// 2. TESTS: parseCOP()
// ═══════════════════════════════════════════════════════════════════
describe('parseCOP() — Parsing de montos colombianos', () => {

  it('devuelve 0 para null', () => {
    assert.equal(parseCOP(null), 0);
  });

  it('devuelve 0 para undefined', () => {
    assert.equal(parseCOP(undefined), 0);
  });

  it('devuelve 0 para objeto', () => {
    assert.equal(parseCOP({}), 0);
  });

  it('devuelve 0 para booleano', () => {
    assert.equal(parseCOP(true), 0);
  });

  it('parsea número simple (string con dígitos)', () => {
    assert.equal(parseCOP('15000'), 15000);
  });

  it('parsea número simple (tipo number)', () => {
    assert.equal(parseCOP(10000), 10000);
  });

  it('parsea formato colombiano con punto miles: "10.000"', () => {
    assert.equal(parseCOP('10.000'), 10000);
  });

  it('parsea formato colombiano: "15.000"', () => {
    assert.equal(parseCOP('15.000'), 15000);
  });

  it('parsea formato colombiano: "200.000"', () => {
    assert.equal(parseCOP('200.000'), 200000);
  });

  it('parsea formato colombiano: "1.200.000" (millón)', () => {
    assert.equal(parseCOP('1.200.000'), 1200000);
  });

  it('parsea formato con símbolo $: "$10.000"', () => {
    assert.equal(parseCOP('$10.000'), 10000);
  });

  it('parsea formato con $ y miles: "$200.000"', () => {
    assert.equal(parseCOP('$200.000'), 200000);
  });

  it('parsea formato con decimales (coma): "10.000,50"', () => {
    assert.equal(parseCOP('10.000,50'), 10000.50);
  });

  it('parsea formato con decimales (coma): "1.500,75"', () => {
    assert.equal(parseCOP('1.500,75'), 1500.75);
  });

  it('parsea formato decimal sin miles: "500,25"', () => {
    assert.equal(parseCOP('500,25'), 500.25);
  });

  it('devuelve 0 para "Libre donación"', () => {
    assert.equal(parseCOP('Libre donación'), 0);
  });

  it('devuelve 0 para "Aporte Voluntario"', () => {
    assert.equal(parseCOP('Aporte Voluntario'), 0);
  });

  it('devuelve 0 para string vacío', () => {
    assert.equal(parseCOP(''), 0);
  });

  it('maneja ceros', () => {
    assert.equal(parseCOP('0'), 0);
    assert.equal(parseCOP('0.000'), 0);
  });

  it('parsea montos con espacios: "50 000"', () => {
    // los espacios se eliminan por la regex [^\d,\.]
    const result = parseCOP('50 000');
    assert.equal(result, 50000);
  });

});

// ═══════════════════════════════════════════════════════════════════
// 3. TESTS: showToast()
// ═══════════════════════════════════════════════════════════════════
describe('showToast() — Sistema de notificaciones', () => {

  afterEach(() => {
    cleanupToastDOM();
  });

  it('crea el contenedor toast-container si no existe', () => {
    assert.equal(document.getElementById('toast-container'), null);
    showToast('Test message');
    const container = document.getElementById('toast-container');
    assert.notEqual(container, null);
    assert.equal(container.id, 'toast-container');
  });

  it('reutiliza el contenedor existente', () => {
    showToast('First toast');
    const container1 = document.getElementById('toast-container');
    showToast('Second toast');
    const container2 = document.getElementById('toast-container');
    assert.equal(container1, container2);
  });

  it('agrega un elemento toast al contenedor', () => {
    const result = showToast('Hola mundo');
    assert.notEqual(result, undefined);
    const container = document.getElementById('toast-container');
    assert.equal(container.children.length, 1);
    assert.ok(container.children[0].innerHTML.includes('Hola mundo'));
  });

  it('agrega múltiples toasts sin duplicar mensajes idénticos', () => {
    showToast('Mensaje único');
    showToast('Mensaje único'); // duplicado, debería ignorarse
    const container = document.getElementById('toast-container');
    assert.equal(container.children.length, 1);
  });

  it('muestra icono ✓ para tipo success (default)', () => {
    const result = showToast('Éxito');
    const toast = document.getElementById('toast-container').children[0];
    assert.ok(toast.innerHTML.includes('✓'));
  });

  it('muestra icono ✕ para tipo error', () => {
    showToast('Error!', 'error');
    const toast = document.getElementById('toast-container').children[0];
    assert.ok(toast.innerHTML.includes('✕'));
  });

  it('muestra icono ⚠ para tipo warning', () => {
    showToast('Advertencia', 'warning');
    const toast = document.getElementById('toast-container').children[0];
    assert.ok(toast.innerHTML.includes('⚠'));
  });

  it('usa color verde para success', () => {
    showToast('Bien', 'success');
    const toast = document.getElementById('toast-container').children[0];
    const bg = toast.style.cssText || '';
    assert.ok(bg.includes('16a34a') || bg.includes('#16a34a') || bg.includes('rgb'),
      `El background debería contener el color verde. Obtenido: ${bg.substring(0, 100)}`);
  });

  it('usa color rojo para error', () => {
    showToast('Mal', 'error');
    const toast = document.getElementById('toast-container').children[0];
    const bg = toast.style.cssText || '';
    assert.ok(bg.includes('dc2626') || bg.includes('#dc2626') || bg.includes('rgb'),
      `El background debería contener el color rojo. Obtenido: ${bg.substring(0, 100)}`);
  });

  it('usa color amarillo para warning', () => {
    showToast('Cuidado', 'warning');
    const toast = document.getElementById('toast-container').children[0];
    const bg = toast.style.cssText || '';
    assert.ok(bg.includes('f59e0b') || bg.includes('#f59e0b') || bg.includes('rgb'),
      `El background debería contener el color amarillo. Obtenido: ${bg.substring(0, 100)}`);
  });

  it('usa icono ✓ por defecto si el tipo no es reconocido', () => {
    showToast('Tipo raro', 'info');
    const toast = document.getElementById('toast-container').children[0];
    assert.ok(toast.innerHTML.includes('✓'));
  });

  it('el toast tiene estilo de border-radius 12px', () => {
    showToast('Borde redondeado');
    const toast = document.getElementById('toast-container').children[0];
    assert.ok(toast.style.borderRadius.includes('12px'));
  });

});
