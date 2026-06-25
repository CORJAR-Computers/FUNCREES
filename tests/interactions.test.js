/**
 * Tests de interacción para navegación SPA, modales y checkout.
 * Funciones puras y helpers del sistema de checkout.
 *
 * Ejecutar con: npm test
 */

import { describe, it, before, after, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';

let dom, document, window;

before(() => {
  dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
    url: 'http://localhost',
    pretendToBeVisual: true,
  });
  document = dom.window.document;
  window = dom.window;

  globalThis.document = document;
  globalThis.window = window;
  globalThis.Node = window.Node;
});

after(() => {
  delete globalThis.document;
  delete globalThis.window;
  delete globalThis.Node;
});

// ─── Implementaciones de funciones puras ──────────────────────────

function formatMoneyNumber(val) {
  const num = parseFloat(val);
  if (isNaN(num)) return '0';
  return num.toLocaleString('es-CO');
}

function highlightText(text, searchTerm) {
  if (!searchTerm || !text) return text;
  const escaped = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escaped})`, 'gi');
  const safeText = String(text);
  return safeText.replace(regex, '<mark class="search-highlight">$1</mark>');
}

function getTagClass(tag) {
  const map = {
    'Adulto Mayor':        'ptag-adulto-mayor',
    'Juventud':            'ptag-juventud',
    'Mujer Rural':         'ptag-mujer-rural',
    'Educación':           'ptag-educacion',
    'Soberanía Alimentaria':'ptag-soberania',
    'Cultura':             'ptag-cultura',
    'Ecología':            'ptag-ecologia',
    'Consultoría':         'ptag-consultoria',
    'Niñez':               'ptag-ninez',
    'Emprendimiento':      'ptag-emprendimiento',
    'Bienestar Animal':    'ptag-bienestar-animal'
  };
  return map[tag] || '';
}

// ─── Helpers de checkout (state + DOM UI) ─────────────────────────

let checkoutModalState = { amountSelected: '50000', gateway: 'pse' };
let ticketsCheckoutState = { eventId: 'bingo', quantity: 1, gateway: 'pse' };

function cleanupCheckoutDOM() {
  document.querySelectorAll('.amount-btn').forEach(b => b.remove());
  const customInput = document.getElementById('custom-amount-input');
  if (customInput) customInput.remove();
  document.querySelectorAll('.gateway-item').forEach(b => b.remove());
  const qtySpan = document.getElementById('ticket-qty-display');
  if (qtySpan) qtySpan.remove();
  const totalSpan = document.getElementById('ticket-total-display');
  if (totalSpan) totalSpan.remove();
  document.querySelectorAll('#ticket-gateway-list .gateway-item').forEach(b => b.remove());
  const backdrop = document.getElementById('global-modal-backdrop');
  if (backdrop) backdrop.remove();
  const body = document.body;
  body.classList.remove('modal-open');
}

function closeActiveModal() {
  const modalBackdrop = document.getElementById('global-modal-backdrop');
  if (!modalBackdrop) return;
  modalBackdrop.classList.remove('active');
  modalBackdrop.removeAttribute('role');
  modalBackdrop.removeAttribute('aria-modal');
  document.body.classList.remove('modal-open');
}

function setCheckoutAmount(amount) {
  checkoutModalState.amountSelected = amount;
  document.querySelectorAll('.amount-btn').forEach(btn => {
    const matchesText = btn.textContent.trim().includes(formatMoneyNumber(amount));
    const matchesData = btn.dataset.amount === amount;
    btn.classList.toggle('active', matchesText || matchesData);
  });
  const customInput = document.getElementById('custom-amount-input');
  if (customInput) customInput.value = '';
}

function setCustomCheckoutAmount(val) {
  checkoutModalState.amountSelected = val;
  document.querySelectorAll('.amount-btn').forEach(btn => btn.classList.remove('active'));
}

function setCheckoutGateway(gw) {
  checkoutModalState.gateway = gw;
  document.querySelectorAll('.gateway-item').forEach(item => {
    item.classList.toggle('active', item.dataset.gateway === gw);
  });
}

function updateTicketQty(diff) {
  const newQty = ticketsCheckoutState.quantity + diff;
  if (newQty >= 1 && newQty <= 10) {
    ticketsCheckoutState.quantity = newQty;
    const qtySpan = document.getElementById('ticket-qty-display');
    if (qtySpan) qtySpan.textContent = newQty;
    const totalSpan = document.getElementById('ticket-total-display');
    if (totalSpan) {
      const numericCost = 15000;
      const totalPrice = numericCost * newQty;
      totalSpan.textContent = `Adquirir Bonos por $${formatMoneyNumber(totalPrice)} COP`;
    }
  }
}

function setTicketGateway(gw) {
  ticketsCheckoutState.gateway = gw;
  document.querySelectorAll('#ticket-gateway-list .gateway-item').forEach(item => {
    item.classList.toggle('active', item.dataset.gateway === gw);
  });
}

function filterEvents(category) {
  document.querySelectorAll('.evento-filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === category);
  });
}

// ═══════════════════════════════════════════════════════════════════
// 1. TESTS: formatMoneyNumber()
// ═══════════════════════════════════════════════════════════════════
describe('formatMoneyNumber() — Formateo de montos a COP', () => {

  it('formatea 50000 como "50.000"', () => {
    assert.equal(formatMoneyNumber(50000), '50.000');
  });

  it('formatea 1500 como "1.500"', () => {
    assert.equal(formatMoneyNumber(1500), '1.500');
  });

  it('formatea 0 como "0"', () => {
    assert.equal(formatMoneyNumber(0), '0');
  });

  it('formatea 1000000 como "1.000.000"', () => {
    assert.equal(formatMoneyNumber(1000000), '1.000.000');
  });

  it('devuelve "0" para NaN', () => {
    assert.equal(formatMoneyNumber(NaN), '0');
  });

  it('formatea string numérico', () => {
    assert.equal(formatMoneyNumber('30000'), '30.000');
  });

  it('formatea decimales (10.000,50)', () => {
    const result = formatMoneyNumber(10000.50);
    assert.ok(result.includes('10.000'));
  });

});

// ═══════════════════════════════════════════════════════════════════
// 2. TESTS: highlightText()
// ═══════════════════════════════════════════════════════════════════
describe('highlightText() — Resaltado de términos de búsqueda', () => {

  it('devuelve el texto original si no hay searchTerm', () => {
    assert.equal(highlightText('Hola mundo', ''), 'Hola mundo');
  });

  it('devuelve el texto original si searchTerm es null', () => {
    assert.equal(highlightText('Hola mundo', null), 'Hola mundo');
  });

  it('envuelve el término en <mark>', () => {
    const result = highlightText('Hola mundo', 'mundo');
    assert.equal(result, 'Hola <mark class="search-highlight">mundo</mark>');
  });

  it('es case-insensitive', () => {
    const result = highlightText('Hola Mundo', 'mundo');
    assert.equal(result, 'Hola <mark class="search-highlight">Mundo</mark>');
  });

  it('resalta múltiples ocurrencias', () => {
    const result = highlightText('foo bar foo baz', 'foo');
    const matches = result.match(/<mark/g);
    assert.equal(matches.length, 2);
  });

  it('escapa caracteres especiales en searchTerm', () => {
    const result = highlightText('precio $100.00', '$100');
    assert.ok(result.includes('<mark'));
    assert.ok(result.includes('$100'));
  });

  it('no modifica texto si searchTerm no existe', () => {
    const result = highlightText('Hola mundo', 'xyz');
    assert.equal(result, 'Hola mundo');
  });

  it('maneja textos vacíos', () => {
    assert.equal(highlightText('', 'term'), '');
  });

});

// ═══════════════════════════════════════════════════════════════════
// 3. TESTS: getTagClass()
// ═══════════════════════════════════════════════════════════════════
describe('getTagClass() — Mapeo de tags a clases CSS', () => {

  it('mapea "Adulto Mayor" → "ptag-adulto-mayor"', () => {
    assert.equal(getTagClass('Adulto Mayor'), 'ptag-adulto-mayor');
  });

  it('mapea "Juventud" → "ptag-juventud"', () => {
    assert.equal(getTagClass('Juventud'), 'ptag-juventud');
  });

  it('mapea "Educación" → "ptag-educacion"', () => {
    assert.equal(getTagClass('Educación'), 'ptag-educacion');
  });

  it('mapea "Emprendimiento" → "ptag-emprendimiento"', () => {
    assert.equal(getTagClass('Emprendimiento'), 'ptag-emprendimiento');
  });

  it('mapea "Bienestar Animal" → "ptag-bienestar-animal"', () => {
    assert.equal(getTagClass('Bienestar Animal'), 'ptag-bienestar-animal');
  });

  it('devuelve string vacío para tag desconocido', () => {
    assert.equal(getTagClass('Tag Inexistente'), '');
  });

  it('cubre todos los tags del proyecto', () => {
    const tags = ['Adulto Mayor','Juventud','Mujer Rural','Educación',
      'Soberanía Alimentaria','Cultura','Ecología','Consultoría',
      'Niñez','Emprendimiento','Bienestar Animal'];
    for (const tag of tags) {
      assert.notEqual(getTagClass(tag), '', `Tag "${tag}" debería tener una clase asociada`);
    }
  });

});

// ═══════════════════════════════════════════════════════════════════
// 4. TESTS: closeActiveModal()
// ═══════════════════════════════════════════════════════════════════
describe('closeActiveModal() — Cierre de modal', () => {

  afterEach(cleanupCheckoutDOM);

  it('no falla si no hay backdrop', () => {
    assert.doesNotThrow(() => closeActiveModal());
  });

  it('remueve clase "active" del backdrop', () => {
    const backdrop = document.createElement('div');
    backdrop.id = 'global-modal-backdrop';
    backdrop.classList.add('active');
    document.body.appendChild(backdrop);

    closeActiveModal();
    assert.equal(backdrop.classList.contains('active'), false);
  });

  it('remueve role="dialog" del backdrop', () => {
    const backdrop = document.createElement('div');
    backdrop.id = 'global-modal-backdrop';
    backdrop.setAttribute('role', 'dialog');
    document.body.appendChild(backdrop);

    closeActiveModal();
    assert.equal(backdrop.hasAttribute('role'), false);
  });

  it('remueve aria-modal del backdrop', () => {
    const backdrop = document.createElement('div');
    backdrop.id = 'global-modal-backdrop';
    backdrop.setAttribute('aria-modal', 'true');
    document.body.appendChild(backdrop);

    closeActiveModal();
    assert.equal(backdrop.hasAttribute('aria-modal'), false);
  });

  it('remueve clase "modal-open" del body', () => {
    const backdrop = document.createElement('div');
    backdrop.id = 'global-modal-backdrop';
    document.body.appendChild(backdrop);
    document.body.classList.add('modal-open');

    closeActiveModal();
    assert.equal(document.body.classList.contains('modal-open'), false);
  });

});

// ═══════════════════════════════════════════════════════════════════
// 5. TESTS: setCheckoutAmount()
// ═══════════════════════════════════════════════════════════════════
describe('setCheckoutAmount() — Selección de monto', () => {

  afterEach(cleanupCheckoutDOM);

  it('actualiza amountSelected en el estado', () => {
    setCheckoutAmount('30000');
    assert.equal(checkoutModalState.amountSelected, '30000');
  });

  it('marca el botón correspondiente como active', () => {
    const btn = document.createElement('button');
    btn.className = 'amount-btn';
    btn.textContent = '$50.000';
    document.body.appendChild(btn);

    setCheckoutAmount('50000');
    assert.equal(btn.classList.contains('active'), true);
  });

  it('desmarca otros botones', () => {
    const btn1 = document.createElement('button');
    btn1.className = 'amount-btn';
    btn1.textContent = '$30.000';
    document.body.appendChild(btn1);

    const btn2 = document.createElement('button');
    btn2.className = 'amount-btn';
    btn2.textContent = '$50.000';
    document.body.appendChild(btn2);

    setCheckoutAmount('30000');
    assert.equal(btn1.classList.contains('active'), true);
    assert.equal(btn2.classList.contains('active'), false);
  });

  it('limpia el input custom-amount al seleccionar preset', () => {
    const customInput = document.createElement('input');
    customInput.id = 'custom-amount-input';
    customInput.value = '75000';
    document.body.appendChild(customInput);

    setCheckoutAmount('100000');
    assert.equal(customInput.value, '');
  });

});

// ═══════════════════════════════════════════════════════════════════
// 6. TESTS: setCustomCheckoutAmount()
// ═══════════════════════════════════════════════════════════════════
describe('setCustomCheckoutAmount() — Monto personalizado', () => {

  afterEach(cleanupCheckoutDOM);

  it('actualiza amountSelected con el valor personalizado', () => {
    setCustomCheckoutAmount('75000');
    assert.equal(checkoutModalState.amountSelected, '75000');
  });

  it('desmarca todos los botones de preset', () => {
    const btn = document.createElement('button');
    btn.className = 'amount-btn';
    btn.classList.add('active');
    document.body.appendChild(btn);

    setCustomCheckoutAmount('99999');
    assert.equal(btn.classList.contains('active'), false);
  });

});

// ═══════════════════════════════════════════════════════════════════
// 7. TESTS: setCheckoutGateway()
// ═══════════════════════════════════════════════════════════════════
describe('setCheckoutGateway() — Selección de pasarela', () => {

  afterEach(cleanupCheckoutDOM);

  it('actualiza gateway en el estado', () => {
    setCheckoutGateway('wompi');
    assert.equal(checkoutModalState.gateway, 'wompi');
  });

  it('marca el ítem correspondiente como active', () => {
    const item = document.createElement('div');
    item.className = 'gateway-item';
    item.dataset.gateway = 'pse';
    document.body.appendChild(item);

    setCheckoutGateway('pse');
    assert.equal(item.classList.contains('active'), true);
  });

  it('desmarca otros ítems', () => {
    const item1 = document.createElement('div');
    item1.className = 'gateway-item';
    item1.dataset.gateway = 'pse';
    document.body.appendChild(item1);

    const item2 = document.createElement('div');
    item2.className = 'gateway-item';
    item2.dataset.gateway = 'wompi';
    document.body.appendChild(item2);

    setCheckoutGateway('wompi');
    assert.equal(item1.classList.contains('active'), false);
    assert.equal(item2.classList.contains('active'), true);
  });

});

// ═══════════════════════════════════════════════════════════════════
// 8. TESTS: updateTicketQty()
// ═══════════════════════════════════════════════════════════════════
describe('updateTicketQty() — Cantidad de boletas', () => {

  afterEach(() => {
    cleanupCheckoutDOM();
    ticketsCheckoutState.quantity = 1;
  });

  it('incrementa cantidad en 1', () => {
    const span = document.createElement('span');
    span.id = 'ticket-qty-display';
    document.body.appendChild(span);

    updateTicketQty(1);
    assert.equal(ticketsCheckoutState.quantity, 2);
  });

  it('decrementa cantidad en 1', () => {
    ticketsCheckoutState.quantity = 3;
    const span = document.createElement('span');
    span.id = 'ticket-qty-display';
    span.textContent = '3';
    document.body.appendChild(span);

    updateTicketQty(-1);
    assert.equal(ticketsCheckoutState.quantity, 2);
  });

  it('no permite cantidad menor a 1', () => {
    ticketsCheckoutState.quantity = 1;
    updateTicketQty(-1);
    assert.equal(ticketsCheckoutState.quantity, 1);
  });

  it('no permite cantidad mayor a 10', () => {
    ticketsCheckoutState.quantity = 10;
    updateTicketQty(1);
    assert.equal(ticketsCheckoutState.quantity, 10);
  });

  it('actualiza el display de cantidad', () => {
    const span = document.createElement('span');
    span.id = 'ticket-qty-display';
    document.body.appendChild(span);

    updateTicketQty(1);
    assert.equal(span.textContent, '2');
  });

  it('actualiza el total', () => {
    const qtySpan = document.createElement('span');
    qtySpan.id = 'ticket-qty-display';
    document.body.appendChild(qtySpan);

    const totalSpan = document.createElement('span');
    totalSpan.id = 'ticket-total-display';
    document.body.appendChild(totalSpan);

    updateTicketQty(1);
    assert.ok(totalSpan.textContent.includes('30.000')); // 2 × 15.000
  });

});

// ═══════════════════════════════════════════════════════════════════
// 9. TESTS: setTicketGateway()
// ═══════════════════════════════════════════════════════════════════
describe('setTicketGateway() — Pasarela para tickets', () => {

  afterEach(cleanupCheckoutDOM);

  it('actualiza gateway en ticketsCheckoutState', () => {
    setTicketGateway('whatsapp');
    assert.equal(ticketsCheckoutState.gateway, 'whatsapp');
  });

  it('marca el ítem activo en #ticket-gateway-list', () => {
    const list = document.createElement('div');
    list.id = 'ticket-gateway-list';
    const item = document.createElement('div');
    item.className = 'gateway-item';
    item.dataset.gateway = 'pse';
    list.appendChild(item);
    document.body.appendChild(list);

    setTicketGateway('pse');
    assert.equal(item.classList.contains('active'), true);
  });

});

// ═══════════════════════════════════════════════════════════════════
// 10. TESTS: filterEvents()
// ═══════════════════════════════════════════════════════════════════
describe('filterEvents() — Filtro de eventos', () => {

  afterEach(cleanupCheckoutDOM);

  it('marca el botón correcto como active', () => {
    const btn1 = document.createElement('button');
    btn1.className = 'evento-filter-btn';
    btn1.dataset.filter = 'todos';
    document.body.appendChild(btn1);

    const btn2 = document.createElement('button');
    btn2.className = 'evento-filter-btn';
    btn2.dataset.filter = 'evento';
    document.body.appendChild(btn2);

    filterEvents('evento');
    assert.equal(btn1.classList.contains('active'), false);
    assert.equal(btn2.classList.contains('active'), true);
  });

  it('desmarca otros botones al cambiar filtro', () => {
    const btn1 = document.createElement('button');
    btn1.className = 'evento-filter-btn active';
    btn1.dataset.filter = 'todos';
    document.body.appendChild(btn1);

    filterEvents('campania');
    assert.equal(btn1.classList.contains('active'), false);
  });

});
