// Funcrees Colombia - Core JavaScript Application Engine
// Encapsulado en IIFE para evitar contaminación del scope global
(function() {
  'use strict';

document.addEventListener('DOMContentLoaded', async () => {
  // Load dynamic data from Django API
  await loadDataFromAPI();

  // Initialize Application Components
  initNavigation();
  initAccessibility();
  renderProjects();
  renderAbuelitos();
  initProjectSearch();
  initAbuelitoSearch();
  renderEvents();
  initCheckoutSystem();
  initContactForm();
  initTestimonialCarousel();
  initDarkModeToggle();
  initLeafletMap();
  initEventFilters();
  initStatsCounter();
});

// API URL configurable desde window.__FUNCREES_CONFIG (definido en index.html)
const API_BASE = window.__FUNCREES_CONFIG?.API_BASE || 'http://127.0.0.1:8000/api';

// Constante para el número de WhatsApp (evitar hardcodeo)
const WHATSAPP_NUMBER = '573137924439';

// Cola de toasts activos (para evitar duplicados)
let toastQueue = [];

/**
 * Sistema de Toast Notifications no bloqueante.
 * Reemplaza alert() para mejor experiencia de usuario.
 */
function showToast(message, type = 'success', duration = 4000) {
  // Evitar toasts duplicados idénticos
  if (toastQueue.includes(message)) return;
  toastQueue.push(message);

  // Crear o reutilizar contenedor de toasts
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

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => {
      if (toast.parentNode) toast.remove();
      const idx = toastQueue.indexOf(message);
      if (idx !== -1) toastQueue.splice(idx, 1);
      if (container.children.length === 0) container.remove();
    }, 300);
  }, duration);
}

// Registrar animación para toasts
const toastStyle = document.createElement('style');
toastStyle.textContent = `
  @keyframes toastSlideIn {
    from { opacity: 0; transform: translateX(100px); }
    to { opacity: 1; transform: translateX(0); }
  }
`;
document.head.appendChild(toastStyle);

/**
 * Obtiene el token CSRF desde la cookie de Django.
 */
function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return '';
}

/**
 * Sanitiza strings antes de inyectarlos en innerHTML para prevenir XSS.
 * Convierte caracteres especiales a entidades HTML.
 */
function sanitizeHTML(str) {
  if (str === null || str === undefined) return '';
  const temp = document.createElement('div');
  temp.textContent = String(str);
  return temp.innerHTML;
}

/**
 * Convierte un string de monto en formato colombiano a número.
 * Maneja formatos: "10.000", "10000", "10.000,00", "$10.000"
 */
function parseCOP(val) {
  if (typeof val !== 'string' && typeof val !== 'number') return 0;
  let s = String(val).replace(/[^\d,\.]/g, ''); // Remove símbolos no numéricos
  // Si tiene coma decimal (formato 10.000,50)
  if (s.includes(',') && /,\d{1,2}$/.test(s)) {
    s = s.replace('\.', '').replace(',', '.');
  } else {
    // Formato colombiano: puntos como separadores de miles
    s = s.replace('\.', '');
  }
  const num = parseFloat(s);
  return isNaN(num) ? 0 : num;
}

async function loadDataFromAPI() {
  try {
    const controller = new AbortController();
    // 12 segundos: tiempo suficiente para el cold start de Neon PostgreSQL
    const timeoutId = setTimeout(() => controller.abort(), 12000);

    const [abuelitosRes, eventsRes] = await Promise.all([
      fetch(`${API_BASE}/beneficiaries/`, { signal: controller.signal }),
      fetch(`${API_BASE}/events/`, { signal: controller.signal })
    ]);

    clearTimeout(timeoutId);

    if (abuelitosRes.ok) {
      const data = await abuelitosRes.json();
      const results = data.results || data;
      ABUELITOS_DATA = results.map(ab => ({
        id: ab.id,
        nombre: ab.nombre,
        edad: ab.edad,
        ciudad: ab.ciudad,
        testimonio: ab.testimonio,
        historia: ab.historia,
        img: ab.foto_url
      }));
      console.log(`✅ API: ${ABUELITOS_DATA.length} beneficiarios cargados`);
    }

    if (eventsRes.ok) {
      const data = await eventsRes.json();
      const results = data.results || data;
      EVENTOS_DATA = results.map(ev => ({
        id: ev.id,
        titulo: ev.titulo,
        fecha: ev.fecha,
        hora: ev.hora,
        costo: String(ev.costo_bono),
        lugar: ev.lugar,
        desc: ev.descripcion,
        dateObj: ev.fecha && ev.hora ? new Date(`${ev.fecha}T${ev.hora}`).toISOString() : null,
        category: ev.categoria
      }));
      console.log(`✅ API: ${EVENTOS_DATA.length} eventos cargados`);
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      console.warn("⚠️ API: Tiempo de espera agotado. Usando datos locales.");
    } else {
      console.warn("⚠️ API: No se pudo conectar con el servidor. Usando datos locales.", err.message);
    }
    // Mantener los datos hardcodeados como fallback
  }
}

// ==========================================
// 1. DATA MODELS
// ==========================================

const PROYECTOS_DATA = [
  {
    id: 1,
    title: "Protección y Dignificación del Adulto Mayor",
    tag: "Adulto Mayor",
    slogan: "Devolviendo la esperanza a través del cuidado afectivo y la autonomía.",
    desc: "Modelo de intervención biopsicosocial integral que trasciende la asistencia básica: atención clínica, acompañamiento psicosocial, gimnasia cognitiva, recreación terapéutica y seguridad alimentaria para adultos mayores en zonas de vulnerabilidad social.",
    img: "https://images.unsplash.com/photo-1544006659-f0b21884ce1d?w=800&h=600&fit=crop"
  },
  {
    id: 2,
    title: "Mentes Transformadoras, Juventud con Propósito",
    tag: "Juventud",
    slogan: "Sanando emociones, formando líderes para transformar territorios.",
    desc: "Formación en salud mental, inteligencia emocional, liderazgo y emprendimiento social para jóvenes de 18 a 24 años en zonas rurales de Sucre, promoviendo resiliencia, autonomía económica y proyectos de vida sostenibles.",
    img: "https://images.unsplash.com/photo-1529390079861-591de354faf1?w=800&h=600&fit=crop"
  },
  {
    id: 3,
    title: "Empoderamiento Integral y Liderazgo Femenino Rural",
    tag: "Mujer Rural",
    slogan: "Despertando liderazgo y construyendo autonomía.",
    desc: "Fortalecimiento psicosocial, asociatividad, orientación jurídica y proyectos productivos para consolidar la autonomía económica y el liderazgo comunitario de mujeres rurales emprendedoras de Sucre.",
    img: "https://images.unsplash.com/photo-1542744095-291d1f67b221?w=800&h=600&fit=crop"
  },
  {
    id: 4,
    title: "Semilleros de Excelencia Académica",
    tag: "Educación",
    slogan: "Cultivando conocimiento, cosechando futuro.",
    desc: "Acompañamiento académico personalizado, apoyo psicopedagógico y metodologías innovadoras de aprendizaje activo para potenciar la motivación escolar y prevenir la deserción en la niñez rural.",
    img: "https://images.unsplash.com/photo-1516574187841-cb93c95e7cc3?w=800&h=600&fit=crop"
  },
  {
    id: 5,
    title: "Desarrollo Agropecuario Sostenible",
    tag: "Soberanía Alimentaria",
    slogan: "Sembramos esperanza, recogemos futuro.",
    desc: "Implementación de huertas comunitarias y sistemas agrícolas tecnificados y orgánicos para asegurar la soberanía alimentaria y la independencia económica de comunidades rurales en Sucre.",
    img: "https://images.unsplash.com/photo-1592477353930-b99b380f70a5?w=800&h=600&fit=crop"
  },
  {
    id: 6,
    title: "Gestión Integral de Cultura, Recreación y Deporte",
    tag: "Cultura",
    slogan: "Unidos por el talento y la tradición.",
    desc: "Rescate del patrimonio cultural y potenciación de habilidades deportivas en zonas vulnerables a través de la creación de espacios seguros y profesionales de formación artística y deportiva.",
    img: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&h=600&fit=crop"
  },
  {
    id: 7,
    title: "Ecomunidad Sostenible",
    tag: "Ecología",
    slogan: "Transformando lo ordinario en un futuro extraordinario.",
    desc: "Estrategia de economía circular basada en el reciclaje y transformación de materiales (Upcycling), cuyos fondos financian directamente la reforestación del \"Bosque de la Esperanza\".",
    img: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&h=600&fit=crop"
  },
  {
    id: 8,
    title: "Centro de Capacitación, Gestión y Consultorías",
    tag: "Consultoría",
    slogan: "Conocimiento que orienta, consultoría que transforma.",
    desc: "Servicios de consultoría estratégica, análisis de datos, formación empresarial e inteligencia territorial para fortalecer la sostenibilidad institucional y el impacto social de organizaciones públicas, privadas y comunitarias.",
    img: "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&h=600&fit=crop"
  },
  {
    id: 9,
    title: "Infancia con Dignidad",
    tag: "Niñez",
    slogan: "Cuidar hoy, para transformar mañana.",
    desc: "Red itinerante de protección para la niñez rural en extrema vulnerabilidad, integrando la entrega de insumos básicos con entornos lúdico-recreativos seguros que garantizan la dignidad en la infancia.",
    img: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&h=600&fit=crop"
  },
  {
    id: 10,
    title: "Red de Servicios Técnicos y Emprendimiento Productivo",
    tag: "Emprendimiento",
    slogan: "Un contrato de servicio, un legado de autonomía.",
    desc: "Programa enfocado en la cultura del mantenimiento preventivo y la profesionalización de oficios técnicos, generando independencia económica y fuentes de ingreso digno para jóvenes de zonas vulnerables.",
    img: "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&h=600&fit=crop"
  },
  {
    id: 11,
    title: 'Centro de Esperanza "Huella Canina"',
    tag: "Bienestar Animal",
    slogan: "Un ladrido de gratitud, una vida de lealtad.",
    desc: "Red de protección, rescate médico, rehabilitación y adopción responsable de caninos en situación de abandono, complementada con educación comunitaria sobre tenencia responsable de mascotas.",
    img: "https://images.unsplash.com/photo-1552642986-ccb41e7059e9?w=800&h=600&fit=crop"
  }
];

let ABUELITOS_DATA = [
  {
    id: "carmen",
    nombre: "Carmen Martínez",
    edad: 82,
    ciudad: "Sincelejo",
    testimonio: "Desde que estoy en la fundación, siento que tengo una nueva familia y un propósito para sonreír cada mañana.",
    historia: "Carmen quedó viuda hace diez años y vivía sola en condiciones de extrema vulnerabilidad en Sincelejo. En Funcrees, encontró un espacio de afecto, terapia ocupacional y alimentos calientes todos los días. Le encanta liderar el taller de tejidos tradicionales.",
    img: "https://images.unsplash.com/photo-1552642986-ccb41e7059e9?w=400&h=400&fit=crop&crop=face"
  },
  {
    id: "pedro",
    nombre: "Pedro Nel Suárez",
    edad: 79,
    ciudad: "Sincelejo",
    testimonio: "El huerto comunitario me devolvió la energía. Aquí siembro vida y cosecho la alegría de sentirme útil.",
    historia: "Don Pedro trabajó toda su vida en la agricultura en los campos de Sucre, pero al envejecer perdió el acceso al suelo y a un sustento digno. Funcrees lo vinculó como el líder principal del proyecto de 'Huertos Sostenibles', donde comparte su sabiduría con niños de la comunidad.",
    img: "https://images.unsplash.com/photo-1594951475736-2396e9597c23?w=400&h=400&fit=crop&crop=face"
  },
  {
    id: "ligia",
    nombre: "Ligia de la Ossa",
    edad: 85,
    ciudad: "Sincelejo",
    testimonio: "Aprender a usar el celular me permitió volver a escuchar la voz de mis nietos que están lejos. Es como magia.",
    historia: "Ligia sufría de aislamiento severo al no poder comunicarse con su familia fuera de la ciudad. A través del programa de Inclusión Digital, aprendió a realizar videollamadas. Su risa contagia a todos en las sesiones semanales de informática.",
    img: "https://images.unsplash.com/photo-1582772821626-d343469e6b52?w=400&h=400&fit=crop&crop=face"
  },
  {
    id: "samuel",
    nombre: "Samuel Arrieta",
    edad: 76,
    ciudad: "Sincelejo",
    testimonio: "La música y el dominó con mis compañeros son mi mejor medicina. La soledad ya no vive en mi casa.",
    historia: "Samuel es un apasionado del folclor y la música de viento. Tras enfrentar serios problemas de movilidad y depresión, el equipo de salud preventiva y fisioterapia de Funcrees le ha ayudado a recuperar fuerza física y su ánimo jovial.",
    img: "https://images.unsplash.com/photo-1493060232230-6b3a0c641ef6?w=400&h=400&fit=crop&crop=face"
  }
];

let EVENTOS_DATA = [
  {
    id: "bingo",
    titulo: "Bingo Solidario Pro-Alimentos",
    fecha: "Octubre 26",
    hora: "7:00 PM",
    costo: "15.000",
    lugar: "Sede Funcrees Sincelejo",
    desc: "Una gran noche de premios, música en vivo y deliciosa comida típica para financiar el comedor comunitario de nuestros abuelitos.",
    dateObj: new Date(new Date().getFullYear(), 9, 26, 19, 0, 0).toISOString(),
    category: "evento"
  },
  {
    id: "rifa",
    titulo: "Gran Rifa de la Esperanza",
    fecha: "Noviembre 15",
    hora: "Sorteo Oficial",
    costo: "10.000",
    lugar: "Lotería de Sinuano",
    desc: "Participa por un espectacular combo tecnológico para el hogar y un bono de mercado. El 100% recaudado apoya la salud de la fundación.",
    dateObj: new Date(new Date().getFullYear(), 10, 15, 12, 0, 0).toISOString(),
    category: "evento"
  },
  {
    id: "libros",
    titulo: "Venta de Libros Culturales",
    fecha: "Permanente",
    hora: "Horario de Oficina",
    costo: "Libre donación",
    lugar: "Biblioteca Central Sincelejo",
    desc: "Adquiere libros donados por la comunidad a precios de aporte. Una oportunidad de aprender y apoyar a la vez.",
    dateObj: null,
    category: "campania"
  },
  {
    id: "donaciones",
    titulo: "Campaña de Recaudación de Fondos",
    fecha: "Campaña Activa",
    hora: "Online / Sede",
    costo: "Aporte Voluntario",
    lugar: "Nacional",
    desc: "Apoya directamente con recursos para mejorar la infraestructura de los huertos y adquirir nuevos elementos didácticos.",
    dateObj: null,
    category: "campania"
  }
];

// ==========================================
// 2. SPA NAVIGATION SYSTEM
// ==========================================

function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link, .footer-link');
  const sections = document.querySelectorAll('.view-section');
  const menuToggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('.nav-menu');

  // Helper: navigate to a target section by id
  function navigateTo(targetId) {
    if (!targetId) return;

    // Update active links
    navLinks.forEach(l => l.classList.remove('active'));
    document.querySelectorAll(`[data-target="${targetId}"]`).forEach(l => l.classList.add('active'));

    // Switch active section
    sections.forEach(sec => {
      sec.classList.remove('active');
      if (sec.id === targetId) {
        sec.classList.add('active');
      }
      // Testimonials section is always shown with 'inicio'
      if (sec.id === 'testimonials-section') {
        if (targetId === 'inicio') {
          sec.classList.add('active');
        }
      }
    });

    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Close mobile menu if open
    if (navMenu && navMenu.classList.contains('active')) {
      navMenu.classList.remove('active');
    }

    // Actualizar URL e historial del navegador (SPA history.pushState)
    const sectionNames = {
      'inicio': 'inicio',
      'quienes-somos': 'quienes-somos',
      'nuestros-proyectos': 'nuestros-proyectos',
      'historias-de-vida': 'historias-de-vida',
      'donaciones-aliados': 'donaciones-aliados',
      'eventos': 'eventos',
      'contacto-footer': 'contacto'
    };
    const hash = sectionNames[targetId] || targetId;
    history.pushState({ section: targetId }, '', `#${hash}`);

    // Re-init map if navigating to contacto to fix Leaflet render bug
    if (targetId === 'contacto-footer') {
      setTimeout(() => {
        if (window.__funcreesMap) {
          window.__funcreesMap.invalidateSize();
        }
      }, 300);
    }

    // Cleanup para evitar memory leaks
    cleanupMapObserver();
  }

  // Manejar navegación con historial (botón Atrás/Adelante del navegador)
  window.addEventListener('popstate', (e) => {
    if (e.state && e.state.section) {
      navigateTo(e.state.section);
    }
  });

  // Al cargar la página, restaurar sección desde hash si existe
  const initialHash = window.location.hash.replace('#', '');
  if (initialHash) {
    // Mapear hash a targetId
    const hashToSection = {
      'inicio': 'inicio',
      'quienes-somos': 'quienes-somos',
      'nuestros-proyectos': 'nuestros-proyectos',
      'historias-de-vida': 'historias-de-vida',
      'donaciones-aliados': 'donaciones-aliados',
      'eventos': 'eventos',
      'contacto': 'contacto-footer'
    };
    const sectionId = hashToSection[initialHash] || 'inicio';
    setTimeout(() => navigateTo(sectionId), 50);
  }

  // SPA tab switcher
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('data-target');
      navigateTo(targetId);
    });
  });

  // Logo click navigation to inicio
  const logoWrapper = document.querySelector('.logo-wrapper');
  if (logoWrapper) {
    logoWrapper.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo('inicio');
    });
  }

  // Mobile menu toggle
  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });
  }

  // Bind home-hero CTA buttons
  const btnConoceLabor = document.getElementById('btn-conoce-labor');
  const btnUneteAliado = document.getElementById('btn-unete-aliado');

  if (btnConoceLabor) {
    btnConoceLabor.addEventListener('click', () => {
      document.querySelector('[data-target="quienes-somos"]').click();
    });
  }
  if (btnUneteAliado) {
    btnUneteAliado.addEventListener('click', () => {
      document.querySelector('[data-target="donaciones-aliados"]').click();
    });
  }
}

// ==========================================
// 3. ACCESIBILITY ENGINE (A+, A-, High Contrast, Dyslexia Font, Voice Reader)
// ==========================================

let appAccessibilityState = {
  fontScale: 1.0,
  highContrast: false,
  dyslexiaFont: false,
  ttsEnabled: false
};

function initAccessibility() {
  const widgetBtn = document.getElementById('acc-widget-btn');
  const accPanel = document.getElementById('acc-panel');
  const closeBtn = document.getElementById('acc-close-btn');

  // Toggle Accessibility Panel
  if (widgetBtn && accPanel) {
    widgetBtn.addEventListener('click', () => {
      accPanel.classList.toggle('active');
    });
  }

  if (closeBtn && accPanel) {
    closeBtn.addEventListener('click', () => {
      accPanel.classList.remove('active');
    });
  }

  // Null check: si faltan elementos del DOM, salir temprano
  const btnFontInc = document.getElementById('btn-font-inc');
  const btnFontDec = document.getElementById('btn-font-dec');
  const btnContrastToggle = document.getElementById('btn-contrast-toggle');
  const btnDyslexiaToggle = document.getElementById('btn-dyslexia-toggle');
  const btnVoiceToggle = document.getElementById('btn-voice-toggle');

  if (!btnFontInc || !btnFontDec || !btnContrastToggle || !btnDyslexiaToggle || !btnVoiceToggle) {
    console.warn('Accessibility: faltan elementos del DOM para inicializar correctamente.');
    return;
  }

  // Load from localStorage
  const storedState = localStorage.getItem('funcrees_acc_settings');
  if (storedState) {
    try {
      appAccessibilityState = JSON.parse(storedState);
    } catch (e) {
      console.error("Error reading accessibility settings", e);
    }
  }

  // Apply Initial States
  applyAccessibilityStyles();

  // Control Buttons Event Listeners
  // Font Size
  document.getElementById('btn-font-inc').addEventListener('click', () => {
    if (appAccessibilityState.fontScale < 1.4) {
      appAccessibilityState.fontScale += 0.1;
      saveAndApplyAccSettings();
    }
  });

  document.getElementById('btn-font-dec').addEventListener('click', () => {
    if (appAccessibilityState.fontScale > 0.8) {
      appAccessibilityState.fontScale -= 0.1;
      saveAndApplyAccSettings();
    }
  });

  // High Contrast
  btnContrastToggle.addEventListener('click', () => {
    appAccessibilityState.highContrast = !appAccessibilityState.highContrast;
    saveAndApplyAccSettings();
  });

  // Dyslexia Font
  btnDyslexiaToggle.addEventListener('click', () => {
    appAccessibilityState.dyslexiaFont = !appAccessibilityState.dyslexiaFont;
    saveAndApplyAccSettings();
  });

  // Voice Reader (TTS Simulator)
  btnVoiceToggle.addEventListener('click', () => {
    appAccessibilityState.ttsEnabled = !appAccessibilityState.ttsEnabled;
    saveAndApplyAccSettings();
    showToast(appAccessibilityState.ttsEnabled 
      ? 'Lector de voz activado. Busca los iconos 🔊 junto al texto.' 
      : 'Lector de voz desactivado.', 'success');
  });
}

function saveAndApplyAccSettings() {
  localStorage.setItem('funcrees_acc_settings', JSON.stringify(appAccessibilityState));
  applyAccessibilityStyles();
}

function applyAccessibilityStyles() {
  const body = document.body;

  // 1. Font scale
  document.documentElement.style.setProperty('--font-scale', appAccessibilityState.fontScale);

  // 2. High Contrast class toggle
  const btnContrast = document.getElementById('btn-contrast-toggle');
  if (btnContrast) {
    if (appAccessibilityState.highContrast) {
      body.classList.add('high-contrast');
      btnContrast.classList.add('active');
    } else {
      body.classList.remove('high-contrast');
      btnContrast.classList.remove('active');
    }
  }

  // 3. Dyslexia Font class toggle
  const btnDyslexia = document.getElementById('btn-dyslexia-toggle');
  if (btnDyslexia) {
    if (appAccessibilityState.dyslexiaFont) {
      body.classList.add('dyslexia-font');
      btnDyslexia.classList.add('active');
    } else {
      body.classList.remove('dyslexia-font');
      btnDyslexia.classList.remove('active');
    }
  }

  // 4. Voice Reader icons display toggler
  const btnVoice = document.getElementById('btn-voice-toggle');
  if (btnVoice) {
    if (appAccessibilityState.ttsEnabled) {
      btnVoice.classList.add('active');
      enableVoiceReaderTriggers();
    } else {
      btnVoice.classList.remove('active');
      disableVoiceReaderTriggers();
    }
  }
}

// Voice synthesis engine (TTS) helpers
let currentSpeechUtterance = null;

function enableVoiceReaderTriggers() {
  // Select target text blocks
  const targetElements = document.querySelectorAll(
    'p, .section-title, .hero-title, .mv-title, .valor-title, .abuelito-nombre, .abuelito-testimonio, .proyecto-title, .evento-titulo, .testimonial-quote, .testimonial-author'
  );

  targetElements.forEach(el => {
    // Check if it already has a speaker trigger
    if (!el.querySelector('.tts-trigger-btn') && !el.classList.contains('tts-trigger-btn')) {
      const button = document.createElement('button');
      button.className = 'tts-trigger-btn';
      button.innerHTML = '🔊';
      button.setAttribute('aria-label', 'Escuchar este texto en voz alta');
      button.setAttribute('title', 'Escuchar texto');
      
      button.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent modal opening
        
        // Stop any current reading
        window.speechSynthesis.cancel();
        
        if (currentSpeechUtterance) {
          // Remove highlight class from old element
          document.querySelectorAll('.tts-highlight').forEach(x => x.classList.remove('tts-highlight'));
        }

        // Get text to read (excluding the button itself)
        const textToRead = el.textContent.replace('🔊', '').trim();
        
        // Highlight element
        el.classList.add('tts-highlight');

        const utterance = new SpeechSynthesisUtterance(textToRead);
        utterance.lang = 'es-CO'; // Colombian Spanish or standard Spanish
        
        // Handle end of speech
        utterance.onend = () => {
          el.classList.remove('tts-highlight');
        };
        utterance.onerror = () => {
          el.classList.remove('tts-highlight');
        };

        currentSpeechUtterance = utterance;
        window.speechSynthesis.speak(utterance);
      });

      el.appendChild(button);
    }
  });
}

function disableVoiceReaderTriggers() {
  window.speechSynthesis.cancel();
  document.querySelectorAll('.tts-highlight').forEach(x => x.classList.remove('tts-highlight'));
  document.querySelectorAll('.tts-trigger-btn').forEach(btn => btn.remove());
}

// ==========================================
// 4. DYNAMIC RENDER FUNCTIONS
// ==========================================

// Map a project tag string to its CSS ptag class
function getTagClass(tag) {
  const map = {
    'Adulto Mayor':        'ptag-adulto-mayor',
    'Juventud':            'ptag-juventud',
    'Mujer Rural':         'ptag-mujer-rural',
    'Educaci\u00f3n':          'ptag-educacion',
    'Soberan\u00eda Alimentaria': 'ptag-soberania',
    'Cultura':             'ptag-cultura',
    'Ecolog\u00eda':            'ptag-ecologia',
    'Consultor\u00eda':         'ptag-consultoria',
    'Ni\u00f1ez':               'ptag-ninez',
    'Emprendimiento':      'ptag-emprendimiento',
    'Bienestar Animal':    'ptag-bienestar-animal'
  };
  return map[tag] || '';
}

function renderProjects() {
  const container = document.getElementById('proyectos-grid-container');
  if (!container) return;

  const searchInput = document.getElementById('proyectos-search-input');
  const searchText = searchInput ? searchInput.value.toLowerCase().trim() : '';

  const filtered = searchText
    ? PROYECTOS_DATA.filter(p => {
        const searchable = `${p.title} ${p.desc} ${p.tag} ${p.slogan || ''}`.toLowerCase();
        return searchable.includes(searchText);
      })
    : PROYECTOS_DATA;

  const rawSearch = searchInput ? searchInput.value.trim() : '';

  // Update results count
  const resultsCount = document.getElementById('proyectos-results-count');
  if (resultsCount) {
    const total = PROYECTOS_DATA.length;
    const showing = filtered.length;
    resultsCount.textContent = showing === total ? `${total} proyectos` : `Mostrando ${showing} de ${total} proyectos`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="section-empty-state">
        <div class="section-empty-icon"><i class="fa-solid fa-folder-open"></i></div>
        <h3 class="section-empty-title">No se encontraron proyectos</h3>
        <p class="section-empty-desc">Ning\u00fan proyecto coincide con tu b\u00fasqueda. Intenta con otros t\u00e9rminos.</p>
        <button class="btn btn-outline" onclick="document.getElementById('proyectos-search-input').value='';renderProjects();">Limpiar B\u00fasqueda</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(proj => {
    const tagClass = getTagClass(proj.tag);
    const sloganHtml = proj.slogan
      ? `<p class="proyecto-slogan">${sanitizeHTML(proj.slogan)}</p>`
      : '';
    return `
    <div class="proyecto-card">
      <div class="proyecto-img-container">
        <span class="proyecto-tag ptag ${tagClass}">${sanitizeHTML(proj.tag)}</span>
        <img class="proyecto-img" src="${sanitizeHTML(proj.img)}" alt="${sanitizeHTML(proj.title)}" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.style.display='block'">
        <div class="proyecto-img" style="display:none; background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); width:100%; height:100%;"></div>
      </div>
      <div class="proyecto-info">
        ${sloganHtml}
        <h3 class="proyecto-title">${highlightText(sanitizeHTML(proj.title), rawSearch)}</h3>
        <p class="proyecto-desc">${highlightText(sanitizeHTML(proj.desc), rawSearch)}</p>
        <button class="btn btn-outline btn-text-explorar" style="margin-top:auto;" onclick="openProjectModal(${proj.id})">Explorar Proyecto +</button>
      </div>
    </div>`;
  }).join('');
}

function renderAbuelitos() {
  const container = document.getElementById('abuelitos-grid-container');
  if (!container) return;

  const searchInput = document.getElementById('abuelitos-search-input');
  const searchText = searchInput ? searchInput.value.toLowerCase().trim() : '';

  const filtered = searchText
    ? ABUELITOS_DATA.filter(ab => {
        const searchable = `${ab.nombre} ${ab.testimonio} ${ab.historia} ${ab.ciudad}`.toLowerCase();
        return searchable.includes(searchText);
      })
    : ABUELITOS_DATA;

  const rawSearch = searchInput ? searchInput.value.trim() : '';

  // Update results count
  const resultsCount = document.getElementById('abuelitos-results-count');
  if (resultsCount) {
    const total = ABUELITOS_DATA.length;
    const showing = filtered.length;
    resultsCount.textContent = showing === total ? `${total} abuelitos` : `Mostrando ${showing} de ${total} abuelitos`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="section-empty-state">
        <div class="section-empty-icon"><i class="fa-solid fa-heart-crack"></i></div>
        <h3 class="section-empty-title">No se encontraron abuelitos</h3>
        <p class="section-empty-desc">Ningún perfil coincide con tu búsqueda. Intenta con otros términos.</p>
        <button class="btn btn-outline" onclick="document.getElementById('abuelitos-search-input').value='';renderAbuelitos();">Limpiar Búsqueda</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(ab => `
    <div class="abuelito-card">
      <div class="abuelito-img-box">
        <img class="abuelito-img" src="${sanitizeHTML(ab.img)}" alt="${sanitizeHTML(ab.nombre)}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
        <div style="display:none; background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--primary-soft) 100%); width:100%; height:100%; align-items:center; justify-content:center; font-size:3rem; color:var(--primary-dark)">👴👵</div>
        <div class="abuelito-overlay-info">
          <h3 class="abuelito-nombre">${highlightText(sanitizeHTML(ab.nombre), rawSearch)}</h3>
          <div class="abuelito-meta">
            <span>${sanitizeHTML(String(ab.edad))} Años</span>
            <span>•</span>
            <span>${sanitizeHTML(ab.ciudad || 'Sincelejo')}</span>
          </div>
        </div>
      </div>
      <div class="abuelito-details">
        <p class="abuelito-testimonio">${highlightText(sanitizeHTML(ab.testimonio), rawSearch)}</p>
        <button class="btn btn-primary" onclick="openAbuelitoStoryModal('${sanitizeHTML(ab.id)}')">Conocer su Historia +</button>
      </div>
    </div>
  `).join('');
}

function renderEvents() {
  const container = document.getElementById('eventos-grid-container');
  if (!container) return;

  const activeFilter = document.querySelector('.evento-filter-btn.active');
  const filterValue = activeFilter ? activeFilter.dataset.filter : 'todos';

  // Search text filter
  const searchInput = document.getElementById('evento-search-input');
  const searchText = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const rawSearch = searchInput ? searchInput.value.trim() : '';

  const filteredEvents = EVENTOS_DATA.filter(ev => {
    // Category filter
    if (filterValue !== 'todos' && ev.category !== filterValue) return false;
    // Text search filter
    if (searchText) {
      const searchable = `${ev.titulo} ${ev.desc} ${ev.lugar} ${ev.fecha}`.toLowerCase();
      if (!searchable.includes(searchText)) return false;
    }
    return true;
  });

  // Update results counter (before early return for empty state)
  const resultsCount = document.getElementById('evento-results-count');
  if (resultsCount) {
    const total = EVENTOS_DATA.length;
    const showing = filteredEvents.length;
    if (showing === total) {
      resultsCount.textContent = `${total} eventos`;
    } else {
      resultsCount.textContent = `Mostrando ${showing} de ${total} eventos`;
    }
  }

  if (filteredEvents.length === 0) {
    container.innerHTML = `
      <div class="evento-empty-state">
        <div class="evento-empty-icon"><i class="fa-solid fa-calendar-xmark"></i></div>
        <h3 class="evento-empty-title">No hay eventos en esta categoría</h3>
        <p class="evento-empty-desc">Actualmente no encontramos eventos que coincidan con el filtro seleccionado. Intenta con otra categoría o vuelve pronto para ver nuevas actividades.</p>
        <button class="btn btn-outline" onclick="filterEvents('todos')">Ver Todos los Eventos</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filteredEvents.map(ev => {
    // Countdown HTML
    let countdownHTML = '';
    if (ev.dateObj) {
      const eventDate = new Date(ev.dateObj);
      const now = new Date();
      const diff = eventDate - now;
      if (diff > 0) {
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        countdownHTML = `
          <div class="evento-countdown" data-event-id="${ev.id}">
            <div class="evento-countdown-unit">
              <span class="evento-countdown-value">${days}</span>
              <span class="evento-countdown-label">Días</span>
            </div>
            <span class="evento-countdown-sep">:</span>
            <div class="evento-countdown-unit">
              <span class="evento-countdown-value">${String(hours).padStart(2, '0')}</span>
              <span class="evento-countdown-label">Horas</span>
            </div>
            <span class="evento-countdown-sep">:</span>
            <div class="evento-countdown-unit">
              <span class="evento-countdown-value">${String(minutes).padStart(2, '0')}</span>
              <span class="evento-countdown-label">Min</span>
            </div>
          </div>`;
      } else {
        countdownHTML = '<div class="evento-countdown evento-countdown-ended"><span class="evento-countdown-ended-text">Evento pasado</span></div>';
      }
    } else {
      countdownHTML = '<div class="evento-permanent-badge"><i class="fa-solid fa-infinity"></i> Siempre Activo</div>';
    }

    const dateDay = (ev.fecha || '').split(' ')[1] || 'Activa';
    const dateMonth = (ev.fecha || '').split(' ')[0] || 'Camp.';

    return `
    <div class="evento-card" data-category="${ev.category}">
      <div class="evento-badge-panel">
        <div class="evento-date-badge">
          <span class="evento-date-day">${dateDay}</span>
          <span class="evento-date-month">${dateMonth}</span>
        </div>
        <div style="margin-left: 1.5rem; flex:1;">
          <div class="evento-meta-detail">🕒 ${ev.hora}</div>
          <div class="evento-meta-detail">📍 ${ev.lugar}</div>
        </div>
      </div>
      ${countdownHTML}
      <div class="evento-info">
        <h3 class="evento-titulo">${highlightText(ev.titulo, rawSearch)}</h3>
        <p class="evento-text-desc">${highlightText(ev.desc, rawSearch)}</p>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1.5rem;">
          <span style="font-weight:700; color:var(--primary-dark); font-size:1.1rem;">Bono: ${ev.costo} COP</span>
          <button class="btn btn-secondary" onclick="openTicketModal('${ev.id}')">
            ${ev.id === 'rifa' ? 'Comprar Boleta +' : 'Adquirir Bono +'}
          </button>
        </div>
      </div>
    </div>
  `}).join('');

  // Start countdown interval for real-time updates — guardar referencia para limpiar al cambiar sección
  if (window.__eventosCountdownInterval) {
    clearInterval(window.__eventosCountdownInterval);
  }
  window.__eventosCountdownInterval = setInterval(updateEventCountdowns, 60000);
}

// Cleanup all intervals and observers on page unload / navigation
function cleanupIntervals() {
  if (window.__eventosCountdownInterval) {
    clearInterval(window.__eventosCountdownInterval);
    window.__eventosCountdownInterval = null;
  }
  cleanupMapObserver();
  stopAutoPlay();
}

// Registrar cleanup al descargar la página
window.addEventListener('beforeunload', cleanupIntervals);

// Limpieza adicional cuando se navega entre secciones SPA


// Update countdown timers every minute
function updateEventCountdowns() {
  if (!document.querySelector('.view-section.active#eventos')) return;
  document.querySelectorAll('.evento-countdown[data-event-id]').forEach(el => {
    const ev = EVENTOS_DATA.find(x => x.id === el.dataset.eventId);
    if (!ev || !ev.dateObj) return;
    const eventDate = new Date(ev.dateObj);
    const now = new Date();
    const diff = eventDate - now;
    if (diff <= 0) {
      el.innerHTML = '<span class="evento-countdown-ended-text">Evento pasado</span>';
      return;
    }
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const values = el.querySelectorAll('.evento-countdown-value');
    if (values.length >= 3) {
      values[0].textContent = days;
      values[1].textContent = String(hours).padStart(2, '0');
      values[2].textContent = String(minutes).padStart(2, '0');
    }
  });
}

// Filter events by category
function filterEvents(category) {
  // Update active button
  document.querySelectorAll('.evento-filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === category);
  });
  // Re-render with filter
  renderEvents();
}

// ==========================================
// 5. INTERACTIVE MODALS & CHECKOUT
// ==========================================

// Global Modal handlers
const modalsState = {
  activeModal: null,
  activeAbuelitoId: null
};

function openAbuelitoStoryModal(id) {
  const abuelito = ABUELITOS_DATA.find(x => x.id === id);
  if (!abuelito) return;

  const modalBackdrop = document.getElementById('global-modal-backdrop');
  const modalContainer = document.getElementById('global-modal-card-container');

  modalsState.activeModal = 'story';
  modalsState.activeAbuelitoId = id;

  const safeNombre = sanitizeHTML(abuelito.nombre);
  const safeHistoria = sanitizeHTML(abuelito.historia);
  const safeTestimonio = sanitizeHTML(abuelito.testimonio);
  const firstNombre = safeNombre.split(' ')[0];

  modalContainer.innerHTML = `
    <button class="modal-close-corner" onclick="closeActiveModal()">✕</button>
    <div class="modal-body-story">
      <div class="modal-story-banner">
        <img class="modal-story-img" src="${sanitizeHTML(abuelito.img)}" alt="${safeNombre}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
        <div style="display:none; background: linear-gradient(135deg, var(--secondary) 0%, var(--primary-dark) 100%); width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-size:6rem;">👵👴</div>
        <div class="modal-story-meta">
          <h2 class="abuelito-nombre" style="font-size:2rem; margin-bottom:0.4rem;">${safeNombre}</h2>
          <div class="abuelito-meta">
            <span>Edad: ${sanitizeHTML(String(abuelito.edad))} años</span>
            <span>•</span>
            <span>Ciudad: Sincelejo, Sucre</span>
          </div>
        </div>
      </div>
      <div class="modal-story-content">
        <h3 style="color:var(--secondary); margin-bottom:1rem; font-size:1.3rem;">Historia de Vida</h3>
        <div class="modal-story-biografia">
          <p>${safeHistoria}</p>
          <p style="font-style: italic; margin-top: 1.5rem; color: var(--primary-dark); border-left: 3px solid var(--primary); padding-left: 1rem;">
            "${safeTestimonio}"
          </p>
        </div>
        <div style="display:flex; gap:1rem; margin-top:2rem;">
          <button class="btn btn-primary" style="flex:1;" onclick="triggerSponsorshipFromStory('${sanitizeHTML(abuelito.id)}')">
            🤝 Apadrinar a ${firstNombre}
          </button>
          <button class="btn btn-outline" style="flex:1;" onclick="closeActiveModal()">Volver</button>
        </div>
      </div>
    </div>
  `;

  modalBackdrop.classList.add('active');
  modalBackdrop.setAttribute('role', 'dialog');
  modalBackdrop.setAttribute('aria-modal', 'true');
  document.body.classList.add('modal-open');
  // Re-apply voice reader triggers inside modal if TTS is active
  if (appAccessibilityState.ttsEnabled) {
    enableVoiceReaderTriggers();
  }
  // Focus trap: enfocar el primer elemento interactivo
  setTimeout(() => {
    const firstFocusable = modalContainer.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (firstFocusable) firstFocusable.focus();
  }, 100);
};

function openProjectModal(id) {
  const proj = PROYECTOS_DATA.find(x => x.id === id);
  if (!proj) return;

  const modalBackdrop = document.getElementById('global-modal-backdrop');
  const modalContainer = document.getElementById('global-modal-card-container');

  modalsState.activeModal = 'project';

  const safeTag = sanitizeHTML(proj.tag);
  const safeTitle = sanitizeHTML(proj.title);
  const safeDesc = sanitizeHTML(proj.desc);

  modalContainer.innerHTML = `
    <button class="modal-close-corner" onclick="closeActiveModal()">✕</button>
    <div style="padding:3rem;">
      <div style="display:inline-block; background-color:var(--primary-trans); color:var(--primary-dark); font-weight:700; padding:0.4rem 1rem; border-radius:50px; font-size:0.8rem; margin-bottom:1rem;">
        Proyecto: ${safeTag}
      </div>
      <h2 style="font-size:2rem; color:var(--secondary); margin-bottom:1.5rem; line-height:1.2;">${safeTitle}</h2>
      
      <div style="height:220px; border-radius:var(--radius-md); background:linear-gradient(135deg, var(--primary-dark) 0%, var(--accent) 100%); margin-bottom:2rem; display:flex; align-items:center; justify-content:center; font-size:4rem;">🌱</div>
      
      <p style="color:var(--text-muted); font-size:1.05rem; line-height:1.7; margin-bottom:1.5rem;">
        Este proyecto forma parte del núcleo estratégico de la Fundación Funcrees para la transformación social en Sincelejo. Nuestro objetivo es establecer soluciones duraderas mediante el empoderamiento y la participación comunitaria.
      </p>
      
      <p style="color:var(--text-muted); font-size:1.05rem; line-height:1.7; margin-bottom:2rem;">
        ${safeDesc} Actualmente beneficiamos a más de 120 personas directas e indirectas, logrando un cambio sustentado en la ética, la solidaridad y la inclusión social.
      </p>
      
      <div style="display:flex; gap:1.25rem;">
        <button class="btn btn-primary" style="flex:1;" onclick="triggerGeneralDonationFromProject()">Apoyar este Proyecto</button>
        <button class="btn btn-outline" style="flex:1;" onclick="closeActiveModal()">Cerrar</button>
      </div>
    </div>
  `;

  modalBackdrop.classList.add('active');
  if (appAccessibilityState.ttsEnabled) {
    enableVoiceReaderTriggers();
  }
};

function closeActiveModal() {
  const modalBackdrop = document.getElementById('global-modal-backdrop');
  modalBackdrop.classList.remove('active');
  modalBackdrop.removeAttribute('role');
  modalBackdrop.removeAttribute('aria-modal');
  
  // Restaurar scroll del body
  document.body.classList.remove('modal-open');
  
  // Stop TTS if reading
  window.speechSynthesis.cancel();
};

// Checkout state values
let checkoutModalState = {
  type: 'apadrinamiento', // apadrinamiento, donacion, patrocinio, voluntariado
  amountSelected: '50000',
  gateway: 'pse',
  preselectedAbuelito: ''
};

function openDonationModal(type = 'apadrinamiento', abuelitoId = '') {
  checkoutModalState.type = type;
  checkoutModalState.preselectedAbuelito = abuelitoId;
  checkoutModalState.amountSelected = '50000';
  checkoutModalState.gateway = 'pse';

  renderCheckoutModal();
};

function triggerSponsorshipFromStory(abuelitoId) {
  closeActiveModal();
  setTimeout(() => {
    openDonationModal('apadrinamiento', abuelitoId);
  }, 250);
};

function triggerGeneralDonationFromProject() {
  closeActiveModal();
  setTimeout(() => {
    openDonationModal('donacion');
  }, 250);
};

function renderCheckoutModal() {
  const modalBackdrop = document.getElementById('global-modal-backdrop');
  const modalContainer = document.getElementById('global-modal-card-container');

  modalsState.activeModal = 'checkout';

  const isApadrinamiento = checkoutModalState.type === 'apadrinamiento';
  const isDonacion = checkoutModalState.type === 'donacion';
  const isPatrocinio = checkoutModalState.type === 'patrocinio';
  const isVoluntariado = checkoutModalState.type === 'voluntariado';

  let checkoutFormHTML = '';

  if (isApadrinamiento || isDonacion) {
    // Abuelitos select markup if apadrinamiento
    let abuelitosSelect = '';
    if (isApadrinamiento) {
      abuelitosSelect = `
        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label class="form-label" style="color:var(--secondary)">Selecciona el Abuelito que deseas apadrinar:</label>
          <select id="checkout-abuelito-select" class="form-input" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color); width:100%;">
            <option value="">-- Apadrinamiento General (Fondo Común) --</option>
            ${ABUELITOS_DATA.map(ab => `
              <option value="${sanitizeHTML(ab.id)}" ${checkoutModalState.preselectedAbuelito === ab.id ? 'selected' : ''}>
                ${sanitizeHTML(ab.nombre)} (${sanitizeHTML(String(ab.edad))} Años) - ${sanitizeHTML(ab.ciudad || 'Sincelejo')}
              </option>
            `).join('')}
          </select>
        </div>
      `;
    }

    checkoutFormHTML = `
      <div id="checkout-form-container">
        <div class="modal-checkout-header">
          <h2 class="modal-checkout-title">
            ${isApadrinamiento ? 'Apadrina a un Abuelito' : 'Donación General'}
          </h2>
          <p class="modal-checkout-desc">Tu contribución aporta directamente a su alimentación, salud preventiva y talleres ocupacionales.</p>
        </div>

        <div class="checkout-tabs">
          <button class="checkout-tab ${isApadrinamiento ? 'active' : ''}" onclick="openDonationModal('apadrinamiento', '${checkoutModalState.preselectedAbuelito}')">Apadrinamiento</button>
          <button class="checkout-tab ${isDonacion ? 'active' : ''}" onclick="openDonationModal('donacion')">Donaciones Generales</button>
          <button class="checkout-tab" onclick="openDonationModal('patrocinio')">Patrocinio Empresarial</button>
        </div>

        ${abuelitosSelect}

        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label class="form-label" style="color:var(--secondary)">Selecciona el Monto (COP):</label>
          <div class="amount-selector-grid">
            <button class="amount-btn ${checkoutModalState.amountSelected === '30000' ? 'active' : ''}" onclick="setCheckoutAmount('30000')">$30.000</button>
            <button class="amount-btn ${checkoutModalState.amountSelected === '50000' ? 'active' : ''}" onclick="setCheckoutAmount('50000')">$50.000</button>
            <button class="amount-btn ${checkoutModalState.amountSelected === '100000' ? 'active' : ''}" onclick="setCheckoutAmount('100000')">$100.000</button>
            <button class="amount-btn ${checkoutModalState.amountSelected === '200000' ? 'active' : ''}" onclick="setCheckoutAmount('200000')">$200.000</button>
          </div>
          <input type="number" id="custom-amount-input" class="form-input" placeholder="Otro monto personalizado ($ COP)" 
            style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color); width:100%; margin-top:0.5rem;"
            value="${['30000','50000','100000','200000'].includes(checkoutModalState.amountSelected) ? '' : checkoutModalState.amountSelected}"
            oninput="setCustomCheckoutAmount(this.value)">
        </div>

        <div class="form-group" style="margin-bottom: 1.5rem; display:flex; gap:1rem;">
          <div style="flex:1;">
            <label class="form-label" style="color:var(--secondary)">Tu Nombre:</label>
            <input type="text" id="checkout-nombre-input" class="form-input" placeholder="Ej. Juan Pérez" style="width:100%;">
          </div>
          <div style="flex:1;">
            <label class="form-label" style="color:var(--secondary)">Tu Correo Electrónico:</label>
            <input type="email" id="checkout-email-input" class="form-input" placeholder="Ej. juan@correo.com" style="width:100%;">
          </div>
        </div>

        <div class="form-group" style="margin-bottom: 2rem;">
          <label class="form-label" style="color:var(--secondary)">Método de Recaudo en Colombia:</label>
          <div class="gateway-list">
            <div class="gateway-item ${checkoutModalState.gateway === 'pse' ? 'active' : ''}" data-gateway="pse" onclick="setCheckoutGateway('pse')">
              <span style="font-size:1.5rem;">🏦</span>
              <span class="gateway-name">PSE (Débito)</span>
            </div>
            <div class="gateway-item ${checkoutModalState.gateway === 'wompi' ? 'active' : ''}" data-gateway="wompi" onclick="setCheckoutGateway('wompi')">
              <span style="font-size:1.5rem;">💳</span>
              <span class="gateway-name">Wompi / Tarjetas</span>
            </div>
            <div class="gateway-item ${checkoutModalState.gateway === 'transferencia' ? 'active' : ''}" data-gateway="transferencia" onclick="setCheckoutGateway('transferencia')">
              <span style="font-size:1.5rem;">📲</span>
              <span class="gateway-name">Bancolombia</span>
            </div>
          </div>
        </div>

        <button class="btn btn-primary" style="width:100%; padding:1rem;" onclick="processSimulationCheckout()">
          Proceder con el Aporte de $${formatMoneyNumber(checkoutModalState.amountSelected)} COP
        </button>
      </div>

      <div id="checkout-loading-simulator" class="checkout-simulation-loader">
        <div class="spinner"></div>
        <h3 style="color:var(--secondary);">Conectando con la pasarela bancaria...</h3>
        <p style="color:var(--text-muted); font-size:0.9rem;">Por favor, no cierres esta ventana. Estamos procesando de forma segura.</p>
      </div>

      <div id="checkout-success-simulator" class="checkout-simulation-loader">
        <div class="success-shield">✓</div>
        <h2 style="color:var(--secondary);">¡Donación Completada Exitosamente!</h2>
        <p style="color:var(--text-muted); max-width:480px; margin:0 auto;">
          Tu generosidad es la semilla del cambio. Hemos enviado un correo electrónico de confirmación de tu aporte para la Fundación Funcrees Colombia.
        </p>
        <div class="receipt-box" id="donation-receipt-content">
          <!-- Populated by JS -->
        </div>
        <button class="btn btn-primary" onclick="closeActiveModal()" style="padding:0.75rem 2rem;">Cerrar Ventana</button>
      </div>
    `;
  } else if (isPatrocinio) {
    checkoutFormHTML = `
      <div>
        <div class="modal-checkout-header">
          <h2 class="modal-checkout-title">Patrocinio Empresarial</h2>
          <p class="modal-checkout-desc">Alianzas que transforman la Responsabilidad Social Empresarial (RSE) en soluciones duraderas.</p>
        </div>

        <div class="checkout-tabs">
          <button class="checkout-tab" onclick="openDonationModal('apadrinamiento')">Apadrinamiento</button>
          <button class="checkout-tab" onclick="openDonationModal('donacion')">Donaciones</button>
          <button class="checkout-tab active" onclick="openDonationModal('patrocinio')">Patrocinio Empresarial</button>
        </div>

        <form id="patrocinio-form" onsubmit="submitFormSimulation(event, 'Patrocinio')" class="contact-form" style="background:none; padding:0;">
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">Nombre de la Empresa / Institución:</label>
            <input type="text" name="empresa" class="form-input" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color);" required>
          </div>
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">Persona de Contacto:</label>
            <input type="text" name="nombre" class="form-input" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color);" required>
          </div>
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">Correo Electrónico Corporativo:</label>
            <input type="email" name="email" class="form-input" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color);" required>
          </div>
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">Mensaje / Propuesta de Alianza:</label>
            <textarea name="mensaje" class="form-input form-textarea" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color);" required placeholder="Cuéntanos cómo te gustaría vincularte..."></textarea>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%; padding:1rem; margin-top:1rem;">Enviar Propuesta de Patrocinio</button>
        </form>
      </div>

      <div id="checkout-loading-simulator" class="checkout-simulation-loader">
        <div class="spinner"></div>
        <h3 style="color:var(--secondary);">Enviando información al equipo institucional...</h3>
      </div>

      <div id="checkout-success-simulator" class="checkout-simulation-loader">
        <div class="success-shield">✓</div>
        <h2 style="color:var(--secondary);">¡Contacto de Patrocinio Recibido!</h2>
        <p style="color:var(--text-muted); max-width:480px; margin:0 auto; margin-bottom:1.5rem;">
          Muchas gracias por tu interés institucional. Un representante de Relaciones Aliadas de la Fundación se pondrá en contacto contigo en las próximas 24 horas laborables.
        </p>
        <button class="btn btn-primary" onclick="closeActiveModal()" style="padding:0.75rem 2rem;">Entendido</button>
      </div>
    `;
  } else if (isVoluntariado) {
    checkoutFormHTML = `
      <div>
        <div class="modal-checkout-header">
          <h2 class="modal-checkout-title">Súmate como Voluntario</h2>
          <p class="modal-checkout-desc">Comparte tu tiempo, talento y amor con los adultos mayores de Sincelejo.</p>
        </div>

        <form id="voluntario-form" onsubmit="submitFormSimulation(event, 'Voluntariado')" class="contact-form" style="background:none; padding:0;">
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">Nombre Completo:</label>
            <input type="text" name="nombre" class="form-input" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color);" required>
          </div>
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">Correo Electrónico:</label>
            <input type="email" name="email" class="form-input" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color);" required>
          </div>
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">Teléfono Móvil (WhatsApp):</label>
            <input type="tel" name="telefono" class="form-input" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color);" required>
          </div>
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">Área de Interés / Ocupación:</label>
            <select name="area" class="form-input" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color); width:100%;" required>
              <option value="">-- Selecciona un área --</option>
              <option value="salud">Salud Preventiva / Psicología / Fisioterapia</option>
              <option value="huertos">Huertos Comunitarios / Agronomía</option>
              <option value="talleres">Talleres Lúdicos / Música / Manualidades</option>
              <option value="tecnologia">Alfabetización Digital</option>
              <option value="logistica">Logística / Comedor Solidario</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label" style="color:var(--secondary)">¿Por qué quieres unirte a nosotros?</label>
            <textarea name="mensaje" class="form-input form-textarea" style="background-color:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-color);" required placeholder="Cuéntanos un poco sobre ti y tu motivación..."></textarea>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%; padding:1rem; margin-top:1rem;">Registrar como Voluntario</button>
        </form>
      </div>

      <div id="checkout-loading-simulator" class="checkout-simulation-loader">
        <div class="spinner"></div>
        <h3 style="color:var(--secondary);">Procesando postulación...</h3>
      </div>

      <div id="checkout-success-simulator" class="checkout-simulation-loader">
        <div class="success-shield">✓</div>
        <h2 style="color:var(--secondary);">¡Registro de Voluntariado Exitoso!</h2>
        <p style="color:var(--text-muted); max-width:480px; margin:0 auto; margin-bottom:1.5rem;">
          ¡Bienvenido a la familia Funcrees! Estaremos revisando tu postulación y te contactaremos por WhatsApp para coordinar tu inducción al programa de voluntarios.
        </p>
        <button class="btn btn-primary" onclick="closeActiveModal()" style="padding:0.75rem 2rem;">Cerrar</button>
      </div>
    `;
  }

  modalContainer.innerHTML = `
    <button class="modal-close-corner" onclick="closeActiveModal()">✕</button>
    <div class="modal-checkout-body">
      ${checkoutFormHTML}
    </div>
  `;

  modalBackdrop.classList.add('active');
  if (appAccessibilityState.ttsEnabled) {
    enableVoiceReaderTriggers();
  }
}

// Interactive helper setters for checkout form
function setCheckoutAmount(amount) {
  checkoutModalState.amountSelected = amount;
  // Update button active states without re-rendering entire modal
  document.querySelectorAll('.amount-btn').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.trim().includes(formatMoneyNumber(amount)) || btn.dataset.amount === amount);
  });
  // Clear custom input if a preset was selected
  const customInput = document.getElementById('custom-amount-input');
  if (customInput) customInput.value = '';
};

function setCustomCheckoutAmount(val) {
  checkoutModalState.amountSelected = val;
  // Deselect all preset amount buttons when custom value is entered
  document.querySelectorAll('.amount-btn').forEach(btn => btn.classList.remove('active'));
};

function setCheckoutGateway(gw) {
  checkoutModalState.gateway = gw;
  // Update gateway item active states without re-rendering
  document.querySelectorAll('.gateway-item').forEach(item => {
    item.classList.toggle('active', item.dataset.gateway === gw);
  });
};

async function processSimulationCheckout() {
  const amount = parseFloat(checkoutModalState.amountSelected);
  const nombre = document.getElementById('checkout-nombre-input')?.value.trim();
  const email = document.getElementById('checkout-email-input')?.value.trim();

  if (!amount || amount <= 0) {
    showToast('Por favor, ingresa un monto válido de donación.', 'warning');
    return;
  }
  if (!nombre || !email) {
    showToast('Por favor ingresa tu nombre y correo para enviarte el certificado.', 'warning');
    return;
  }

  const formContainer = document.getElementById('checkout-form-container');
  const loadingContainer = document.getElementById('checkout-loading-simulator');
  const successContainer = document.getElementById('checkout-success-simulator');

  // Fade out form, show loader
  formContainer.style.display = 'none';
  loadingContainer.classList.add('active');

  const abuelitoSelect = document.getElementById('checkout-abuelito-select');
  const selectedAbuelitoId = abuelitoSelect ? abuelitoSelect.value : null;

  // El UUID del beneficiario viene directamente del value del <select> (ya es UUID)
  let abuelitoUuid = selectedAbuelitoId || null;

  const payload = {
    tipo: checkoutModalState.type === 'apadrinamiento' ? 'apadrinamiento' : 'general',
    monto: amount,
    donante_nombre: nombre,
    donante_email: email,
    metodo_pago: checkoutModalState.gateway,
    autorizacion_datos: true,
    beneficiario_id: abuelitoUuid
  };

  try {
    const res = await fetch(`${API_BASE}/donations/initiate/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(payload)
    });
    
    if (res.ok) {
      const data = await res.json();
      
      const gateway = checkoutModalState.gateway;
      
      if (gateway === 'wompi') {
        const ps = data.paymentSession;
        // Integración Widget Wompi Real
        const script = document.createElement('script');
        script.src = 'https://checkout.wompi.co/widget.js';
        script.setAttribute('data-render', 'button');
        script.setAttribute('data-public-key', ps.publicKey);
        script.setAttribute('data-currency', ps.currency);
        script.setAttribute('data-amount-in-cents', ps.amountInCents);
        script.setAttribute('data-reference', ps.reference);
        script.setAttribute('data-signature:integrity', ps.integritySignature);
        script.setAttribute('data-redirect-url', ps.redirectUrl);
        script.setAttribute('data-customer-data:email', ps.customerEmail);
        
        loadingContainer.innerHTML = `
          <h3 style="color:var(--secondary); margin-bottom:1rem;">Pago Seguro con Wompi</h3>
          <p style="color:var(--text-muted); margin-bottom:2rem;">Por favor haz clic en el botón de abajo para completar tu donación en la pasarela de Wompi.</p>
          <div id="wompi-btn-container"></div>
        `;
        document.getElementById('wompi-btn-container').appendChild(script);
      } else if (gateway === 'pse') {
        loadingContainer.innerHTML = `
          <h3 style="color:var(--secondary); margin-bottom:1rem;">Redirigiendo a PSE</h3>
          <p style="color:var(--text-muted); margin-bottom:2rem;">Serás redirigido a la pasarela de PSE para completar el pago desde tu banco.</p>
          <div class="spinner"></div>
        `;
        // Simular redirección a PSE
        setTimeout(() => {
          loadingContainer.classList.remove('active');
          const successContainer = document.getElementById('checkout-success-simulator');
          successContainer.classList.add('active');
          const receiptContent = document.getElementById('donation-receipt-content');
          const dateStr = new Date().toLocaleString();
          receiptContent.innerHTML = `
========================================
       COMPROBANTE DE DONACIÓN - FUNCREES
========================================
ID Transacción: PSE-${Math.floor(100000 + Math.random() * 900000)}
Fecha:          ${dateStr}
Donante:        ${nombre}
Email:          ${email}
Monto:          $${formatMoneyNumber(amount)} COP
Método Pago:    PSE
Estado:         Completado
========================================
  ¡Gracias por tu generosidad!
  Tu apoyo transforma vidas en Sincelejo.
========================================
          `;
        }, 2000);
      } else {
        // Bancolombia / transferencia - mostrar datos de cuenta
        loadingContainer.classList.remove('active');
        const successContainer = document.getElementById('checkout-success-simulator');
        successContainer.classList.add('active');
        
        const receiptContent = document.getElementById('donation-receipt-content');
        receiptContent.innerHTML = `
========================================
    DATOS DE TRANSFERENCIA BANCOLOMBIA
========================================
Titular: Fundación Crece Una Esperanza Social
Tipo: Cuenta de Ahorros
Número: 123-456789-01
NIT: 902036173-3
Monto: $${formatMoneyNumber(amount)} COP
Referencia: ${data.referencia || 'Donación Funcrees'}
========================================
Una vez realices la transferencia,
envíanos el comprobante por WhatsApp
al +57 313 792 4439 para confirmar tu aporte.
========================================
        `;
      }
    } else {
      throw new Error('No se pudo inicializar el pago');
    }
  } catch (err) {
    console.error(err);
    showToast('Ocurrió un error al iniciar la pasarela de pagos. Por favor intenta de nuevo.', 'error');
    closeActiveModal();
  }
};

async function submitFormSimulation(e, formName) {
  e.preventDefault();

  const form = e.target;
  const loadingContainer = document.getElementById('checkout-loading-simulator');
  const successContainer = document.getElementById('checkout-success-simulator');

  // Recoger datos del formulario
  const inputs = form.querySelectorAll('input, textarea, select');
  const formData = {};
  inputs.forEach(input => {
    if (input.name) formData[input.name] = input.value;
  });

  // Mapear tipo de formulario a tipo de ContactMessage
  const tipoMap = { 'Patrocinio': 'alianza', 'Voluntariado': 'voluntariado' };
  const tipo = tipoMap[formName] || 'consulta';

  // Construir payload para el endpoint de contacto
  const payload = {
    nombre: formData.nombre || formData.empresa || Object.values(formData)[0] || 'Sin nombre',
    email: formData.email || Object.values(formData).find(v => v.includes('@')) || '',
    telefono: formData.telefono || '',
    tipo: tipo,
    mensaje: formData.mensaje || Object.values(formData).filter(v => v.length > 30)[0] || `Formulario de ${formName}`
  };

  // Validar que tengamos email
  if (!payload.email) {
    showToast('Por favor ingresa un correo electrónico válido.', 'warning');
    return;
  }

  form.style.display = 'none';
  loadingContainer.classList.add('active');

  try {
    const response = await fetch(`${API_BASE}/contact/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      loadingContainer.classList.remove('active');
      successContainer.classList.add('active');
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (err) {
    console.error(`Error enviando formulario de ${formName}:`, err);
    form.style.display = '';
    loadingContainer.classList.remove('active');
    showToast('Ocurrió un error al enviar el formulario. Por favor intenta de nuevo.', 'error');
  }
};

// Event Tickets flow modal
let ticketsCheckoutState = {
  eventId: '',
  quantity: 1,
  gateway: 'pse'
};

function openTicketModal(eventId) {
  const ev = EVENTOS_DATA.find(x => x.id === eventId);
  if (!ev) return;

  ticketsCheckoutState.eventId = eventId;
  ticketsCheckoutState.quantity = 1;
  ticketsCheckoutState.gateway = 'pse';

  renderTicketsCheckout();
};

function renderTicketsCheckout() {
  const ev = EVENTOS_DATA.find(x => x.id === ticketsCheckoutState.eventId);
  const modalBackdrop = document.getElementById('global-modal-backdrop');
  const modalContainer = document.getElementById('global-modal-card-container');

  modalsState.activeModal = 'tickets';

  const numericCost = parseCOP(ev.costo);
  const totalPrice = numericCost * ticketsCheckoutState.quantity;

  let ticketFormsHTML = `
    <div id="checkout-form-container">
      <div class="modal-checkout-header">
        <span style="background-color:var(--primary-trans); color:var(--primary-dark); font-weight:700; padding:0.4rem 1rem; border-radius:50px; font-size:0.75rem; display:inline-block; margin-bottom:0.75rem;">
          Bono Solidario: ${ev.fecha}
        </span>
        <h2 class="modal-checkout-title" style="font-size:1.6rem; color:var(--secondary);">${ev.titulo}</h2>
        <p class="modal-checkout-desc">${ev.desc}</p>
      </div>

      <div class="form-group" style="margin-bottom:1.5rem;">
        <label class="form-label" style="color:var(--secondary)">Cantidad de Bonos / Boletas:</label>
        <div style="display:flex; align-items:center; gap:1.5rem;">
          <button class="btn btn-outline" style="width:40px; height:40px; padding:0; border-radius:var(--radius-round); font-size:1.2rem;" 
            onclick="updateTicketQty(-1)">-</button>
          <span id="ticket-qty-display" style="font-size:1.3rem; font-weight:700; color:var(--secondary); min-width:30px; text-align:center;">${ticketsCheckoutState.quantity}</span>
          <button class="btn btn-outline" style="width:40px; height:40px; padding:0; border-radius:var(--radius-round); font-size:1.2rem;" 
            onclick="updateTicketQty(1)">+</button>
        </div>
      </div>

      <div class="form-group" style="margin-bottom: 2rem;">
        <label class="form-label" style="color:var(--secondary)">Método de Pago:</label>
        <div class="gateway-list" id="ticket-gateway-list">
          <div class="gateway-item ${ticketsCheckoutState.gateway === 'pse' ? 'active' : ''}" data-gateway="pse" onclick="setTicketGateway('pse')">
            <span style="font-size:1.5rem;">🏦</span>
            <span class="gateway-name">PSE</span>
          </div>
          <div class="gateway-item ${ticketsCheckoutState.gateway === 'wompi' ? 'active' : ''}" data-gateway="wompi" onclick="setTicketGateway('wompi')">
            <span style="font-size:1.5rem;">💳</span>
            <span class="gateway-name">Wompi / TC</span>
          </div>
          <div class="gateway-item ${ticketsCheckoutState.gateway === 'whatsapp' ? 'active' : ''}" data-gateway="whatsapp" onclick="setTicketGateway('whatsapp')">
            <span style="font-size:1.5rem;">💬</span>
            <span class="gateway-name">WhatsApp (Manual)</span>
          </div>
        </div>
      </div>

      <button class="btn btn-primary" style="width:100%; padding:1rem;" onclick="processTicketsCheckout()">
        <span id="ticket-total-display">Adquirir Bonos por $${formatMoneyNumber(totalPrice)} COP</span>
      </button>
    </div>

    <div id="checkout-loading-simulator" class="checkout-simulation-loader">
      <div class="spinner"></div>
      <h3 style="color:var(--secondary);">Procesando orden de compra...</h3>
      <p style="color:var(--text-muted); font-size:0.9rem;">Por favor, espera un momento.</p>
    </div>

    <div id="checkout-success-simulator" class="checkout-simulation-loader">
      <div class="success-shield">✓</div>
      <h2 style="color:var(--secondary);">¡Bono Solidario Generado!</h2>
      <p style="color:var(--text-muted); max-width:480px; margin:0 auto;">
        Muchas gracias por tu valiosa colaboración. Tu aporte beneficia directamente el bienestar y desarrollo integral de nuestros adultos mayores.
      </p>
      <div class="receipt-box" id="tickets-receipt-content">
        <!-- Populated by JS -->
      </div>
      <button class="btn btn-primary" onclick="closeActiveModal()" style="padding:0.75rem 2rem;">Listo</button>
    </div>
  `;

  modalContainer.innerHTML = `
    <button class="modal-close-corner" onclick="closeActiveModal()">✕</button>
    <div class="modal-checkout-body">
      ${ticketFormsHTML}
    </div>
  `;

  modalBackdrop.classList.add('active');
  if (appAccessibilityState.ttsEnabled) {
    enableVoiceReaderTriggers();
  }
}

function updateTicketQty(diff) {
  const newQty = ticketsCheckoutState.quantity + diff;
  if (newQty >= 1 && newQty <= 10) {
    ticketsCheckoutState.quantity = newQty;
    // Update just the display without re-rendering the whole modal
    const qtySpan = document.getElementById('ticket-qty-display');
    if (qtySpan) qtySpan.textContent = newQty;
    // Update total price
    const ev = EVENTOS_DATA.find(x => x.id === ticketsCheckoutState.eventId);
    if (ev) {
      const numericCost = parseCOP(ev.costo);
      const totalPrice = numericCost * newQty;
      const totalSpan = document.getElementById('ticket-total-display');
      if (totalSpan) totalSpan.textContent = `Adquirir Bonos por $${formatMoneyNumber(totalPrice)} COP`;
    }
  }
};

function setTicketGateway(gw) {
  ticketsCheckoutState.gateway = gw;
  // Update gateway item active states without re-rendering
  document.querySelectorAll('#ticket-gateway-list .gateway-item').forEach(item => {
    item.classList.toggle('active', item.dataset.gateway === gw);
  });
};

function processTicketsCheckout() {
  const ev = EVENTOS_DATA.find(x => x.id === ticketsCheckoutState.eventId);
  
  if (ticketsCheckoutState.gateway === 'whatsapp') {
    // Direct WhatsApp redirect simulation
    const numericCost = parseCOP(ev.costo);
    const totalPrice = numericCost * ticketsCheckoutState.quantity;
    const message = encodeURIComponent(`Hola Fundación FUNCREESCOLOMBIA, me gustaría coordinar la compra de ${ticketsCheckoutState.quantity} bono(s) para el evento "${ev.titulo}" por un valor de $${totalPrice.toLocaleString('es-CO')} COP.`);
    
    closeActiveModal();
    window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${message}`, '_blank');
    return;
  }

  const formContainer = document.getElementById('checkout-form-container');
  const loadingContainer = document.getElementById('checkout-loading-simulator');
  const successContainer = document.getElementById('checkout-success-simulator');

  formContainer.style.display = 'none';
  loadingContainer.classList.add('active');

  setTimeout(() => {
    loadingContainer.classList.remove('active');
    successContainer.classList.add('active');

    // Generate ticket numbers
    const ticketNumbers = [];
    for (let i = 0; i < ticketsCheckoutState.quantity; i++) {
      ticketNumbers.push(`BOLETA-#${Math.floor(1000 + Math.random() * 9000)}`);
    }

    const numericCost = parseCOP(ev.costo);
    const totalPrice = numericCost * ticketsCheckoutState.quantity;
    const dateStr = new Date().toLocaleString();

    const receiptContent = document.getElementById('tickets-receipt-content');
    receiptContent.innerHTML = `
========================================
     COMPROBANTE DE BONO - FUNCREES
========================================
ID Transacción: EVT-${Math.floor(100000 + Math.random() * 900000)}
Fecha:          ${dateStr}
Evento:         ${ev.titulo}
Cantidad:       ${ticketsCheckoutState.quantity} Bonos
Total Cobrado:  $${formatMoneyNumber(totalPrice)} COP
Método Pago:    ${ticketsCheckoutState.gateway.toUpperCase()}
Códigos de Boleta:
${ticketNumbers.map((n, i) => `  ${i+1}. [ ${n} ]`).join('\n')}
========================================
   ¡TE ESPERAMOS EN NUESTRO EVENTO!
========================================
    `;
  }, 1800);
};

// ==========================================
// 6. LEAFLET INTERACTIVE MAP
// ==========================================

function initLeafletMap() {
  const mapContainer = document.getElementById('funcrees-map');
  if (!mapContainer || typeof L === 'undefined') return;

  // Sincelejo, Sucre coordinates
  const sincelejoCoords = [9.3046, -75.3906];

  // Choose tile layer based on dark mode
  const isDark = document.body.classList.contains('dark-mode');
  const tileUrl = isDark
    ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const attribution = isDark
    ? '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
    : '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

  const map = L.map('funcrees-map', {
    center: sincelejoCoords,
    zoom: 15,
    zoomControl: true,
    scrollWheelZoom: true
  });

  const tileLayer = L.tileLayer(tileUrl, {
    attribution: attribution,
    maxZoom: 19
  }).addTo(map);

  // Custom red marker icon
  const redIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  // Add marker with popup
  const marker = L.marker(sincelejoCoords, { icon: redIcon }).addTo(map);
  marker.bindPopup(
    '<strong>🏢 SEDE FUNCREESCOLOMBIA</strong><br>' +
    'Carrera 15b #41c - 07<br>' +
    'Sincelejo, Sucre, Colombia<br>' +
    '<hr style="margin:6px 0;border:none;border-top:1px solid var(--border-color, #ddd);">' +
    '📞 +57 313 792 4439<br>' +
    '✉️ fundacioncreceunaesperanza@gmail.com'
  );

  // Fix map rendering inside hidden section
  // Invalidate size when the section becomes visible
  const observer = new MutationObserver(() => {
    const contactSection = document.getElementById('contacto-footer');
    if (contactSection && contactSection.classList.contains('active')) {
      setTimeout(() => map.invalidateSize(), 100);
    }
  });

  // Store observer reference for cleanup
  window.__funcreesMapObserver = observer;

  // Observe nav link clicks to invalidate map size
  document.querySelectorAll('[data-target="contacto-footer"]').forEach(el => {
    el.addEventListener('click', () => {
      setTimeout(() => map.invalidateSize(), 200);
    });
  });

  // Also invalidate on window resize
  window.addEventListener('resize', () => {
    setTimeout(() => map.invalidateSize(), 100);
  });

  // Store for dark mode toggle
  window.__funcreesMap = map;
  window.__funcreesTileLayer = tileLayer;

  // Initial dark mode check on load
  const body = document.body;
  if (body.classList.contains('dark-mode')) {
    updateMapTheme(true);
  }
}

// Cleanup MutationObserver when changing sections or unloading
function cleanupMapObserver() {
  if (window.__funcreesMapObserver) {
    window.__funcreesMapObserver.disconnect();
    window.__funcreesMapObserver = null;
  }
}

// Update map tiles when dark mode toggles
function updateMapTheme(isDark) {
  if (!window.__funcreesMap || !window.__funcreesTileLayer) return;

  const newTileUrl = isDark
    ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const newAttribution = isDark
    ? '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
    : '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

  window.__funcreesMap.removeLayer(window.__funcreesTileLayer);

  window.__funcreesTileLayer = L.tileLayer(newTileUrl, {
    attribution: newAttribution,
    maxZoom: 19
  }).addTo(window.__funcreesMap);

  setTimeout(() => window.__funcreesMap.invalidateSize(), 100);
}

// Dark mode toggle handler - wires up the theme toggle button and map tiles
function initDarkModeToggle() {
  const darkBtn = document.getElementById('dark-mode-btn');
  if (!darkBtn) return;

  // Check localStorage for saved preference
  const savedTheme = localStorage.getItem('funcrees_theme');
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-mode');
    const svg = darkBtn.querySelector('.icon-svg');
    if (svg) {
      svg.innerHTML = '<circle cx="12" cy="12" r="5" /><g stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" /></g>';
    }
  }

  darkBtn.addEventListener('click', () => {
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem('funcrees_theme', isDark ? 'dark' : 'light');

    // Update icon between moon and sun
    const svg = darkBtn.querySelector('.icon-svg');
    if (svg) {
      if (isDark) {
        svg.innerHTML = '<circle cx="12" cy="12" r="5" /><g stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" /></g>';
      } else {
        svg.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
      }
    }

    // Update map tiles for dark/light mode
    if (window.updateMapTheme) {
      window.updateMapTheme(isDark);
    }
  });
}

// ==========================================
// 8. CHECKOUT SYSTEM INITIALIZATION
// ==========================================

function initCheckoutSystem() {
  // Bind any dynamic checkout buttons if needed
  // All major checkout flows are triggered via onclick handlers
}

// ==========================================
// 9. STATS COUNTER — Animated Impact Numbers
// ==========================================

function initStatsCounter() {
  const statElements = document.querySelectorAll('.stat-number[data-target]');
  if (!statElements.length) return;

  // Easing function for smooth deceleration
  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-target'), 10);
    const prefix = el.getAttribute('data-prefix') || '';
    const duration = 1800; // ms
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOutCubic(progress);
      const current = Math.round(easedProgress * target);
      el.textContent = prefix + current;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = prefix + target;
      }
    }

    requestAnimationFrame(update);
  }

  // Use IntersectionObserver to trigger on scroll
  let hasAnimated = false;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !hasAnimated) {
        hasAnimated = true;
        statElements.forEach(el => animateCounter(el));
        observer.disconnect();
      }
    });
  }, { threshold: 0.4 });

  const banner = document.querySelector('.stats-banner');
  if (banner) observer.observe(banner);
}

// ==========================================
// 10. CONTACT & ALIANZAS FORM INTERACTION
// ==========================================

function initContactForm() {
  const contactForm = document.getElementById('footer-contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const oldText = submitBtn.textContent;
      
      submitBtn.disabled = true;
      submitBtn.textContent = 'Enviando...';        const formData = new FormData(contactForm);
      const data = {
        nombre: document.getElementById('contact-name').value || 'Anónimo',
        email: document.getElementById('contact-email').value,
        telefono: document.getElementById('contact-telefono')?.value || '',
        mensaje: document.getElementById('contact-msg').value,
        tipo: 'consulta'
      };
      
      try {
        const response = await fetch(`${API_BASE}/contact/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          },
          body: JSON.stringify(data)
        });

        if (response.ok) {
          submitBtn.textContent = '✓ Mensaje Enviado';
          contactForm.reset();
          
          setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = oldText;
            showToast('¡Muchas gracias! Tu mensaje ha sido enviado correctamente. Nos pondremos en contacto contigo pronto.', 'success');
          }, 1500);
        } else {
          throw new Error('Error en la API');
        }
      } catch (error) {
        console.error(error);
        submitBtn.disabled = false;
        submitBtn.textContent = oldText;
        showToast('Ocurrió un error al enviar tu mensaje. Por favor intenta de nuevo más tarde.', 'error');
      }
    });
  }
}



// ==========================================
// 8. TESTIMONIAL CAROUSEL
// ==========================================

let testimonialState = {
  currentIndex: 0,
  totalItems: 0,
  autoPlayInterval: null,
  isAnimating: false
};

function initTestimonialCarousel() {
  const track = document.getElementById('testimonial-track');
  const dots = document.getElementById('testimonial-dots');
  const prevBtn = document.getElementById('testimonial-prev');
  const nextBtn = document.getElementById('testimonial-next');

  if (!track) return;

  // Render cards
  track.innerHTML = ABUELITOS_DATA.map((ab, i) => {
    const avatarImg = ab.img || '';
    const avatarGradient = [
      'linear-gradient(135deg, #ff9a9e, #fecfef)',
      'linear-gradient(135deg, #f6d365, #fda085)',
      'linear-gradient(135deg, #84fab0, #8fd3f4)',
      'linear-gradient(135deg, #a1c4fd, #c2e9fb)'
    ][i % 4];

    return `
      <div class="testimonial-card" role="group" aria-label="Testimonio de ${sanitizeHTML(ab.nombre)}">
        <div class="testimonial-stars">★★★★★</div>
        <div class="testimonial-quote">
          "${sanitizeHTML(ab.testimonio)}"
        </div>
        <img class="testimonial-avatar" src="${sanitizeHTML(avatarImg)}" alt="${sanitizeHTML(ab.nombre)}"
          onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
          loading="lazy">
        <div style="display:none; width:90px; height:90px; border-radius:50%; background:${avatarGradient}; margin-bottom:1.5rem; align-items:center; justify-content:center; font-size:2.5rem; border:4px solid var(--primary);">👴</div>
        <span class="testimonial-author">${sanitizeHTML(ab.nombre)}</span>
        <span class="testimonial-age"><i class="fa-solid fa-heart" style="color:var(--primary);"></i> ${sanitizeHTML(String(ab.edad))} años · Sincelejo, Sucre</span>
      </div>
    `;
  }).join('');

  testimonialState.totalItems = ABUELITOS_DATA.length;
  testimonialState.currentIndex = 0;

  // Create dots
  dots.innerHTML = ABUELITOS_DATA.map((_, i) =>
    `<button class="testimonial-dot${i === 0 ? ' active' : ''}" data-index="${i}" aria-label="Ir al testimonio ${i + 1}"></button>`
  ).join('');

  // Event listeners
  if (prevBtn) {
    prevBtn.addEventListener('click', () => slideTestimonial(-1));
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', () => slideTestimonial(1));
  }

  // Dot clicks
  dots.addEventListener('click', (e) => {
    const dot = e.target.closest('.testimonial-dot');
    if (dot) {
      const idx = parseInt(dot.dataset.index);
      goToTestimonial(idx);
      resetAutoPlay();
    }
  });

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    const carousel = document.getElementById('testimonial-carousel');
    if (!carousel) return;
    const isVisible = carousel.closest('.view-section.active') || carousel.closest('#inicio.view-section.active');
    if (!isVisible && !document.getElementById('inicio').classList.contains('active')) return;

    if (e.key === 'ArrowLeft') slideTestimonial(-1);
    if (e.key === 'ArrowRight') slideTestimonial(1);
  });

  // Touch/swipe support
  let touchStartX = 0;
  let touchEndX = 0;

  track.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  track.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    const diff = touchStartX - touchEndX;
    if (Math.abs(diff) > 50) {
      if (diff > 0) slideTestimonial(1);
      else slideTestimonial(-1);
      resetAutoPlay();
    }
  }, { passive: true });

  // Start auto-play
  startAutoPlay();

  // Pause on hover
  const carousel = document.getElementById('testimonial-carousel');
  if (carousel) {
    carousel.addEventListener('mouseenter', stopAutoPlay);
    carousel.addEventListener('mouseleave', startAutoPlay);
  }
}

function slideTestimonial(direction) {
  if (testimonialState.isAnimating) return;
  const newIndex = testimonialState.currentIndex + direction;
  if (newIndex < 0) {
    goToTestimonial(testimonialState.totalItems - 1);
  } else if (newIndex >= testimonialState.totalItems) {
    goToTestimonial(0);
  } else {
    goToTestimonial(newIndex);
  }
}

function goToTestimonial(index) {
  if (testimonialState.isAnimating) return;
  if (index < 0 || index >= testimonialState.totalItems) return;

  testimonialState.isAnimating = true;
  testimonialState.currentIndex = index;

  const track = document.getElementById('testimonial-track');
  const dots = document.querySelectorAll('.testimonial-dot');

  if (track) {
    track.style.transform = `translateX(-${index * 100}%)`;
  }

  // Update dots
  dots.forEach((dot, i) => {
    dot.classList.toggle('active', i === index);
  });

  setTimeout(() => {
    testimonialState.isAnimating = false;
  }, 500);
}

function startAutoPlay() {
  stopAutoPlay();
  testimonialState.autoPlayInterval = setInterval(() => {
    slideTestimonial(1);
  }, 5000);
}

function stopAutoPlay() {
  if (testimonialState.autoPlayInterval) {
    clearInterval(testimonialState.autoPlayInterval);
    testimonialState.autoPlayInterval = null;
  }
}

function resetAutoPlay() {
  stopAutoPlay();
  startAutoPlay();
}



// ==========================================
// 11. EVENT FILTERS INITIALIZATION
// ==========================================

function initEventFilters() {
  // Filter category buttons
  const filterBtns = document.querySelectorAll('.evento-filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterEvents(btn.dataset.filter);
    });
  });

  // Search input with debounce
  const searchInput = document.getElementById('evento-search-input');
  const searchClear = document.getElementById('evento-search-clear');
  let searchDebounce = null;

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        renderEvents();
      }, 300);
    });

    // Clear on Escape
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        searchInput.value = '';
        renderEvents();
        searchInput.blur();
      }
    });
  }

  if (searchClear) {
    searchClear.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      renderEvents();
      if (searchInput) searchInput.focus();
    });
  }
}


// ==========================================
// 12. SEARCH INITIALIZATION (Proyectos & Abuelitos)
// ==========================================

function initProjectSearch() {
  const input = document.getElementById('proyectos-search-input');
  const clear = document.getElementById('proyectos-search-clear');
  let debounce = null;
  if (input) {
    input.addEventListener('input', () => {
      clearTimeout(debounce);
      debounce = setTimeout(renderProjects, 300);
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { input.value = ''; renderProjects(); input.blur(); }
    });
  }
  if (clear) {
    clear.addEventListener('click', () => { if (input) input.value = ''; renderProjects(); if (input) input.focus(); });
  }
}

function initAbuelitoSearch() {
  const input = document.getElementById('abuelitos-search-input');
  const clear = document.getElementById('abuelitos-search-clear');
  let debounce = null;
  if (input) {
    input.addEventListener('input', () => {
      clearTimeout(debounce);
      debounce = setTimeout(renderAbuelitos, 300);
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { input.value = ''; renderAbuelitos(); input.blur(); }
    });
  }
  if (clear) {
    clear.addEventListener('click', () => { if (input) input.value = ''; renderAbuelitos(); if (input) input.focus(); });
  }
}

// ==========================================
// 13. UTILS & FORMATTERS
// ==========================================

function formatMoneyNumber(val) {
  const num = parseFloat(val);
  if (isNaN(num)) return '0';
  return num.toLocaleString('es-CO');
}

// Highlight matching search terms in text
// NOTA: text ya debe venir sanitizado con sanitizeHTML() antes de llamar a highlightText
function highlightText(text, searchTerm) {
  if (!searchTerm || !text) return text;
  const escaped = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escaped})`, 'gi');
  // Sanitizar el texto de salida por si searchTerm contiene HTML malicioso
  const safeText = String(text);
  return safeText.replace(regex, '<mark class="search-highlight">$1</mark>');
}

// ─── Exponer al scope global solo lo que necesita HTML onclick ─────
// Funciones llamadas desde atributos onclick en index.html
window.openDonationModal = openDonationModal;
window.openAbuelitoStoryModal = openAbuelitoStoryModal;
window.openProjectModal = openProjectModal;
window.closeActiveModal = closeActiveModal;
window.openTicketModal = openTicketModal;
window.setCheckoutAmount = setCheckoutAmount;
window.setCustomCheckoutAmount = setCustomCheckoutAmount;
window.setCheckoutGateway = setCheckoutGateway;
window.processSimulationCheckout = processSimulationCheckout;
window.submitFormSimulation = submitFormSimulation;
window.updateTicketQty = updateTicketQty;
window.setTicketGateway = setTicketGateway;
window.processTicketsCheckout = processTicketsCheckout;
window.triggerSponsorshipFromStory = triggerSponsorshipFromStory;
window.triggerGeneralDonationFromProject = triggerGeneralDonationFromProject;

// Funciones declaradas con 'function' que son invocadas desde HTML
window.filterEvents = filterEvents;
window.renderProjects = renderProjects;
window.renderAbuelitos = renderAbuelitos;
window.updateMapTheme = updateMapTheme;

// Sanitize se expone para tests y posibles usos externos
window.sanitizeHTML = sanitizeHTML;
window.parseCOP = parseCOP;

})();
