/**
 * Cliente API para la comunicación con el backend Django REST Framework.
 */

const API_BASE = '/api';

/**
 * Datos semilla / fallback en caso de indisponibilidad temporal de la API.
 */
export const FALLBACK_BENEFICIARIES = [
  {
    id: "carmen",
    nombre: "Carmen Martínez",
    edad: 82,
    ciudad: "Sincelejo, Sucre",
    testimonio: "Desde que estoy en la fundación, siento que tengo una nueva familia y un propósito para sonreír cada mañana.",
    historia: "Carmen quedó viuda hace diez años y vivía sola en condiciones de extrema vulnerabilidad en Sincelejo. En Funcrees, encontró un espacio de afecto, terapia ocupacional y alimentos calientes todos los días. Le encanta liderar el taller de tejidos tradicionales.",
    img: "https://images.unsplash.com/photo-1552642986-ccb41e7059e9?w=400&h=400&fit=crop&crop=face"
  },
  {
    id: "pedro",
    nombre: "Pedro Nel Suárez",
    edad: 79,
    ciudad: "Sincelejo, Sucre",
    testimonio: "El huerto comunitario me devolvió la energía. Aquí siembro vida y cosecho la alegría de sentirme útil.",
    historia: "Don Pedro trabajó toda su vida en la agricultura en los campos de Sucre, pero al envejecer perdió el acceso al suelo y a un sustento digno. Funcrees lo vinculó como el líder principal del proyecto de 'Huertos Sostenibles', donde comparte su sabiduría con niños de la comunidad.",
    img: "https://images.unsplash.com/photo-1594951475736-2396e9597c23?w=400&h=400&fit=crop&crop=face"
  },
  {
    id: "ligia",
    nombre: "Ligia de la Ossa",
    edad: 85,
    ciudad: "Sincelejo, Sucre",
    testimonio: "Aprender a usar el celular me permitió volver a escuchar la voz de mis nietos que están lejos. Es como magia.",
    historia: "Ligia sufría de aislamiento severo al no poder comunicarse con su familia fuera de la ciudad. A través del programa de Inclusión Digital, aprendió a realizar videollamadas. Su risa contagia a todos en las sesiones semanales de informática.",
    img: "https://images.unsplash.com/photo-1582772821626-d343469e6b52?w=400&h=400&fit=crop&crop=face"
  },
  {
    id: "samuel",
    nombre: "Samuel Arrieta",
    edad: 76,
    ciudad: "Sincelejo, Sucre",
    testimonio: "La música y el dominó con mis compañeros son mi mejor medicina. La soledad ya no vive en mi casa.",
    historia: "Samuel es un apasionado del folclor y la música de viento. Tras enfrentar serios problemas de movilidad y depresión, el equipo de salud preventiva y fisioterapia de Funcrees le ha ayudado a recuperar fuerza física y su ánimo jovial.",
    img: "https://images.unsplash.com/photo-1493060232230-6b3a0c641ef6?w=400&h=400&fit=crop&crop=face"
  }
];

export const FALLBACK_EVENTS = [
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

/**
 * Obtiene la lista de adultos mayores beneficiarios.
 * @returns {Promise<Array<any>>}
 */
export async function getBeneficiaries() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    const res = await fetch(`${API_BASE}/beneficiaries/`, { signal: controller.signal });
    clearTimeout(timeout);

    if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
    const data = await res.json();
    const results = data.results || data;
    return results.map(/** @param {any} ab */ (ab) => ({
      id: String(ab.id),
      nombre: ab.nombre,
      edad: ab.edad,
      ciudad: ab.ciudad || "Sincelejo, Sucre",
      testimonio: ab.testimonio,
      historia: ab.historia,
      img: ab.foto_url || ab.img || FALLBACK_BENEFICIARIES[0].img
    }));
  } catch (err) {
    return FALLBACK_BENEFICIARIES;
  }
}

/**
 * Obtiene la lista de eventos solidarios.
 * @returns {Promise<Array<any>>}
 */
export async function getEvents() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    const res = await fetch(`${API_BASE}/events/`, { signal: controller.signal });
    clearTimeout(timeout);

    if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
    const data = await res.json();
    const results = data.results || data;
    return results.map(/** @param {any} ev */ (ev) => ({
      id: String(ev.id),
      titulo: ev.titulo,
      fecha: ev.fecha,
      hora: ev.hora,
      costo: String(ev.costo_bono || ev.costo),
      lugar: ev.lugar,
      desc: ev.descripcion || ev.desc,
      category: ev.categoria || ev.category || "evento",
      dateObj: ev.fecha && ev.hora ? new Date(`${ev.fecha}T${ev.hora}`).toISOString() : null
    }));
  } catch (err) {
    return FALLBACK_EVENTS;
  }
}

/**
 * Envía un mensaje desde el formulario de contacto.
 * @param {{ nombre: string, email: string, telefono: string, mensaje: string, asunto: string }} payload
 */
export async function sendContactMessage(payload) {
  const res = await fetch(`${API_BASE}/contact/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error('Error al enviar el mensaje');
  }
  return await res.json();
}
