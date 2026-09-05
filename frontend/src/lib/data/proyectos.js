/**
 * @typedef {Object} Proyecto
 * @property {number} id
 * @property {string} title
 * @property {string} tag
 * @property {string} slogan
 * @property {string} desc
 * @property {string} img
 */

/** @type {Proyecto[]} */
export const PROYECTOS = [
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
    title: "Centro de Esperanza \"Huella Canina\"",
    tag: "Bienestar Animal",
    slogan: "Un ladrido de gratitud, una vida de lealtad.",
    desc: "Red de protección, rescate médico, rehabilitación y adopción responsable de caninos en situación de abandono, complementada con educación comunitaria sobre tenencia responsable de mascotas.",
    img: "https://images.unsplash.com/photo-1552642986-ccb41e7059e9?w=800&h=600&fit=crop"
  }
];

/**
 * Mapea un tag de proyecto a su clase CSS correspondiente.
 * @param {string} tag
 * @returns {string}
 */
export function getTagClass(tag) {
  /** @type {Record<string, string>} */
  const map = {
    'Adulto Mayor': 'ptag-adulto-mayor',
    'Juventud': 'ptag-juventud',
    'Mujer Rural': 'ptag-mujer-rural',
    'Educación': 'ptag-educacion',
    'Soberanía Alimentaria': 'ptag-soberania',
    'Cultura': 'ptag-cultura',
    'Ecología': 'ptag-ecologia',
    'Consultoría': 'ptag-consultoria',
    'Niñez': 'ptag-ninez',
    'Emprendimiento': 'ptag-emprendimiento',
    'Bienestar Animal': 'ptag-bienestar-animal'
  };
  return map[tag] || '';
}
