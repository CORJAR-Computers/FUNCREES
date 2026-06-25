/**
 * Tests de encapsulación IIFE — Verifica que el patrón módulo
 * funcione correctamente: las funciones internas NO deben filtrarse
 * al scope global (window), mientras que las exportadas explícitamente SÍ.
 *
 * Ejecutar con: npm test
 */

import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
let win;

before(() => {
  const dom = new JSDOM(
    '<!DOCTYPE html><html><head></head><body>' +
    '<div id="global-modal-backdrop"></div>' +
    '<div id="global-modal-card-container"></div>' +
    '</body></html>',
    { url: 'http://localhost', pretendToBeVisual: true }
  );
  win = dom.window;
  const doc = dom.window.document;

  // localStorage es read-only en JSDOM
  Object.defineProperty(win, 'localStorage', {
    value: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
    writable: false, configurable: true,
  });

  win.fetch = async () => ({ ok: false });

  // Mock Leaflet
  win.L = {
    map: () => ({ setView(){}, addTo(){}, removeLayer(){}, invalidateSize(){}, on(){} }),
    tileLayer: () => ({ addTo(){} }),
    marker: () => ({ addTo(){}, bindPopup(){} }),
    icon: () => ({}),
    control: { zoom(){} },
  };

  win.speechSynthesis = { cancel(){}, speak(){} };
  win.SpeechSynthesisUtterance = function() {};

  win.IntersectionObserver = class {
    constructor() { this.observe = () => {}; }
    observe() {}
    disconnect() {}
  };

  win.MutationObserver = class {
    constructor() { this.observe = () => {}; }
    observe() {}
    disconnect() {}
  };

  // Sincronizar globalThis para que app.js pueda acceder a estos globales
  globalThis.window = win;
  globalThis.document = doc;
  globalThis.Node = win.Node;
  globalThis.localStorage = win.localStorage;
  globalThis.fetch = win.fetch;
  globalThis.L = win.L;
  globalThis.IntersectionObserver = win.IntersectionObserver;
  globalThis.MutationObserver = win.MutationObserver;
  globalThis.speechSynthesis = win.speechSynthesis;
  globalThis.SpeechSynthesisUtterance = win.SpeechSynthesisUtterance;

  // Cargar app.js y ejecutar en el contexto del DOM virtual
  const appJsPath = path.resolve(__dirname, '..', 'app.js');
  const appJsCode = fs.readFileSync(appJsPath, 'utf-8');

  try {
    win.eval(appJsCode);
  } catch (err) {
    // Si hay error, lo guardamos para diagnosticar
    win.__iifeError = err.message;
    throw err;
  }
});

after(() => {
  ['window','document','Node','localStorage','fetch','L',
   'IntersectionObserver','MutationObserver',
   'speechSynthesis','SpeechSynthesisUtterance'].forEach(k => delete globalThis[k]);
});

// ═══════════════════════════════════════════════════════════════
// TEST 1: Exportaciones explícitas — DEBEN estar en window
// ═══════════════════════════════════════════════════════════════
describe('IIFE — Exportaciones explícitas deben estar en window', () => {

  const exported = [
    'openDonationModal','openAbuelitoStoryModal','openProjectModal',
    'closeActiveModal','openTicketModal',
    'setCheckoutAmount','setCustomCheckoutAmount','setCheckoutGateway',
    'processSimulationCheckout','submitFormSimulation',
    'updateTicketQty','setTicketGateway','processTicketsCheckout',
    'triggerSponsorshipFromStory','triggerGeneralDonationFromProject',
    'filterEvents','renderProjects','renderAbuelitos','updateMapTheme',
    'sanitizeHTML','parseCOP',
  ];

  for (const name of exported) {
    it(`window.${name} es función`, () => {
      assert.equal(typeof win[name], 'function', `Se esperaba que ${name} fuera una función en window`);
    });
  }
});

// ═══════════════════════════════════════════════════════════════
// TEST 2: Funciones internas — NO deben estar en window
// ═══════════════════════════════════════════════════════════════
describe('IIFE — Funciones internas NO deben filtrarse a window', () => {

  const internal = [
    'showToast','getCSRFToken','loadDataFromAPI','initNavigation',
    'initAccessibility','saveAndApplyAccSettings','applyAccessibilityStyles',
    'enableVoiceReaderTriggers','disableVoiceReaderTriggers',
    'renderEvents','cleanupIntervals','updateEventCountdowns',
    'renderTicketsCheckout','initLeafletMap','cleanupMapObserver',
    'initDarkModeToggle','initCheckoutSystem','initStatsCounter',
    'initContactForm','initTestimonialCarousel',
    'formatMoneyNumber','highlightText',
  ];

  for (const name of internal) {
    it(`${name} NO está en window`, () => {
      assert.equal(typeof win[name], 'undefined', `${name} no debería estar en window (encapsulación IIFE)`);
    });
  }

  const stateVars = [
    'appAccessibilityState','checkoutModalState','ticketsCheckoutState',
    'testimonialState','toastQueue','currentSpeechUtterance','modalsState',
    'ABUELITOS_DATA','EVENTOS_DATA','PROYECTOS_DATA',
    'API_BASE','WHATSAPP_NUMBER',
  ];

  it('Variables de estado NO están en window', () => {
    for (const v of stateVars) {
      assert.equal(typeof win[v], 'undefined', `${v} no debería estar en window`);
    }
  });
});
