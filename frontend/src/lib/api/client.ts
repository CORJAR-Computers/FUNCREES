/**
 * Cliente API para la comunicación con el backend Django REST Framework.
 * TypeScript: los tipos viven en $lib/types.ts (espejo de los serializers DRF).
 */
import type {
        Beneficiary,
        ApiEvent,
        InitiateDonationPayload,
        InitiateDonationResponse,
        DonationStatus,
        ContactPayload,
        UiEvent,
        UiBeneficiary,
        PublicStats,
        UiStat,
        ApiTicket
} from '$lib/types';

/**
 * Base de la API. En dev el proxy de Vite reenvía /api al backend :8000;
 * en producción Nginx enruta /api/ a Gunicorn en el mismo origen (sin CORS).
 * Override opcional vía VITE_API_BASE para despliegues con API en otro host.
 * (Acceso defensivo: import.meta.env no existe fuera de Vite, p.ej. en tests.)
 */
interface ViteEnv {
        VITE_API_BASE?: string;
}
const metaEnv: ViteEnv = (import.meta as unknown as { env?: ViteEnv }).env ?? {};
const API_BASE = metaEnv.VITE_API_BASE || '/api';

const REQUEST_TIMEOUT_MS = 8000;

/** Error de la API con código HTTP para manejo fino en la UI. */
export class ApiError extends Error {
        status: number;

        constructor(message: string, status: number) {
                super(message);
                this.name = 'ApiError';
                this.status = status;
        }
}

async function fetchWithTimeout(
        fetchFn: typeof fetch,
        path: string,
        init: RequestInit = {}
): Promise<Response> {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
        try {
                return await fetchFn(`${API_BASE}${path}`, { ...init, signal: controller.signal });
        } finally {
                clearTimeout(timeout);
        }
}

/**
 * Datos semilla / fallback en caso de indisponibilidad temporal de la API.
 * Se muestran solo si el backend no responde (ver load functions).
 */
export const FALLBACK_BENEFICIARIES: UiBeneficiary[] = [
        {
                id: 'carmen',
                nombre: 'Carmen Martínez',
                edad: 82,
                ciudad: 'Sincelejo, Sucre',
                testimonio:
                        'Desde que estoy en la fundación, siento que tengo una nueva familia y un propósito para sonreír cada mañana.',
                historia:
                        'Carmen quedó viuda hace diez años y vivía sola en condiciones de extrema vulnerabilidad en Sincelejo. En Funcrees, encontró un espacio de afecto, terapia ocupacional y alimentos calientes todos los días. Le encanta liderar el taller de tejidos tradicionales.',
                img: 'https://images.unsplash.com/photo-1552642986-ccb41e7059e9?w=400&h=400&fit=crop&crop=face'
        },
        {
                id: 'pedro',
                nombre: 'Pedro Nel Suárez',
                edad: 79,
                ciudad: 'Sincelejo, Sucre',
                testimonio:
                        'El huerto comunitario me devolvió la energía. Aquí siembro vida y cosecho la alegría de sentirme útil.',
                historia:
                        "Don Pedro trabajó toda su vida en la agricultura en los campos de Sucre, pero al envejecer perdió el acceso al suelo y a un sustento digno. Funcrees lo vinculó como el líder principal del proyecto de 'Huertos Sostenibles', donde comparte su sabiduría con niños de la comunidad.",
                img: 'https://images.unsplash.com/photo-1594951475736-2396e9597c23?w=400&h=400&fit=crop&crop=face'
        },
        {
                id: 'ligia',
                nombre: 'Ligia de la Ossa',
                edad: 85,
                ciudad: 'Sincelejo, Sucre',
                testimonio:
                        'Aprender a usar el celular me permitió volver a escuchar la voz de mis nietos que están lejos. Es como magia.',
                historia:
                        'Ligia sufría de aislamiento severo al no poder comunicarse con su familia fuera de la ciudad. A través del programa de Inclusión Digital, aprendió a realizar videollamadas. Su risa contagia a todos en las sesiones semanales de informática.',
                img: 'https://images.unsplash.com/photo-1582772821626-d343469e6b52?w=400&h=400&fit=crop&crop=face'
        },
        {
                id: 'samuel',
                nombre: 'Samuel Arrieta',
                edad: 76,
                ciudad: 'Sincelejo, Sucre',
                testimonio:
                        'La música y el dominó con mis compañeros son mi mejor medicina. La soledad ya no vive en mi casa.',
                historia:
                        'Samuel es un apasionado del folclor y la música de viento. Tras enfrentar serios problemas de movilidad y depresión, el equipo de salud preventiva y fisioterapia de Funcrees le ha ayudado a recuperar fuerza física y su ánimo jovial.',
                img: 'https://images.unsplash.com/photo-1493060232230-6b3a0c641ef6?w=400&h=400&fit=crop&crop=face'
        }
];

export const FALLBACK_EVENTS: UiEvent[] = [
        {
                id: 'bingo',
                titulo: 'Bingo Solidario Pro-Alimentos',
                fecha: 'Octubre 26',
                hora: '7:00 PM',
                costo: '15.000',
                lugar: 'Sede Funcrees Sincelejo',
                desc: 'Una gran noche de premios, música en vivo y deliciosa comida típica para financiar el comedor comunitario de nuestros abuelitos.',
                dateObj: new Date(new Date().getFullYear(), 9, 26, 19, 0, 0).toISOString(),
                category: 'evento'
        },
        {
                id: 'rifa',
                titulo: 'Gran Rifa de la Esperanza',
                fecha: 'Noviembre 15',
                hora: 'Sorteo Oficial',
                costo: '10.000',
                lugar: 'Lotería de Sinuano',
                desc: 'Participa por un espectacular combo tecnológico para el hogar y un bono de mercado. El 100% recaudado apoya la salud de la fundación.',
                dateObj: new Date(new Date().getFullYear(), 10, 15, 12, 0, 0).toISOString(),
                category: 'evento'
        },
        {
                id: 'libros',
                titulo: 'Venta de Libros Culturales',
                fecha: 'Permanente',
                hora: 'Horario de Oficina',
                costo: 'Libre donación',
                lugar: 'Biblioteca Central Sincelejo',
                desc: 'Adquiere libros donados por la comunidad a precios de aporte. Una oportunidad de aprender y apoyar a la vez.',
                dateObj: null,
                category: 'campania'
        },
        {
                id: 'donaciones',
                titulo: 'Campaña de Recaudación de Fondos',
                fecha: 'Campaña Activa',
                hora: 'Online / Sede',
                costo: 'Aporte Voluntario',
                lugar: 'Nacional',
                desc: 'Apoya directamente con recursos para mejorar la infraestructura de los huertos y adquirir nuevos elementos didácticos.',
                dateObj: null,
                category: 'campania'
        }
];

/** Formatea una fecha ISO (YYYY-MM-DD) como "26 Octubre". */
function formatFechaLegible(fechaISO: string | null): string {
        if (!fechaISO) return 'Permanente';
        const meses = [
                'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ];
        const d = new Date(`${fechaISO}T00:00:00`);
        if (Number.isNaN(d.getTime())) return fechaISO;
        return `${d.getDate()} ${meses[d.getMonth()]}`;
}

/** Formatea una hora HH:MM:SS como "7:00 PM". */
function formatHoraLegible(hora: string | null): string {
        if (!hora) return 'Horario de Oficina';
        const [hStr, mStr] = hora.split(':');
        const h = parseInt(hStr ?? '0', 10);
        const m = mStr ?? '00';
        if (Number.isNaN(h)) return hora;
        const period = h >= 12 ? 'PM' : 'AM';
        const h12 = h % 12 === 0 ? 12 : h % 12;
        return `${h12}:${m} ${period}`;
}

/**
 * Obtiene la lista de adultos mayores beneficiarios.
 * Lanza ApiError si el backend falla — el caller decide el fallback.
 *
 * @param fetchFn En SSR debe ser el `fetch` del load function de SvelteKit
 *                (resuelve URLs relativas en el servidor). En el navegador
 *                se usa el fetch global.
 */
export async function getBeneficiaries(fetchFn: typeof fetch = fetch): Promise<UiBeneficiary[]> {
        const res = await fetchWithTimeout(fetchFn, '/beneficiaries/');
        if (!res.ok) throw new ApiError(`HTTP ${res.status}`, res.status);
        const data = (await res.json()) as Beneficiary[] | { results: Beneficiary[] };
        const results = Array.isArray(data) ? data : data.results;
        return results.map((ab) => ({
                id: String(ab.id),
                nombre: ab.nombre,
                edad: ab.edad,
                ciudad: ab.ciudad || 'Sincelejo, Sucre',
                testimonio: ab.testimonio,
                historia: ab.historia,
                img: ab.foto_url || FALLBACK_BENEFICIARIES[0].img,
                img_webp_srcset: ab.foto_webp_srcset || null
        }));
}

/**
 * Obtiene la lista de eventos solidarios.
 * Lanza ApiError si el backend falla — el caller decide el fallback.
 * Ver getBeneficiaries para el parámetro fetchFn.
 */
export async function getEvents(fetchFn: typeof fetch = fetch): Promise<UiEvent[]> {
        const res = await fetchWithTimeout(fetchFn, '/events/');
        if (!res.ok) throw new ApiError(`HTTP ${res.status}`, res.status);
        const data = (await res.json()) as ApiEvent[] | { results: ApiEvent[] };
        const results = Array.isArray(data) ? data : data.results;
        return results.map((ev) => {
                let dateObj: string | null = null;
                if (ev.fecha && ev.hora) {
                        const d = new Date(`${ev.fecha}T${ev.hora}`);
                        if (!Number.isNaN(d.getTime())) dateObj = d.toISOString();
                }
                return {
                        id: String(ev.id),
                        titulo: ev.titulo,
                        fecha: formatFechaLegible(ev.fecha),
                        hora: formatHoraLegible(ev.hora),
                        costo: String(ev.costo_bono ?? ''),
                        lugar: ev.lugar || 'Sede Funcrees',
                        desc: ev.descripcion || '',
                        category: ev.categoria || 'evento',
                        imagen: ev.imagen || ev.imagen_url || null,
                        imagen_webp_srcset: ev.imagen_webp_srcset || null,
                        dateObj
                };
        });
}

/**
 * Inicia una donación real contra el backend (POST /api/donations/initiate/).
 * El backend crea el registro, firma la petición Wompi y devuelve la
 * configuración del Widget. Lanza ApiError con el status HTTP si falla.
 */
export async function initiateDonation(
        payload: InitiateDonationPayload
): Promise<InitiateDonationResponse> {
        const res = await fetchWithTimeout(fetch, '/donations/initiate/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
        });

        if (!res.ok) {
                let message = 'No se pudo iniciar la donación. Intenta nuevamente.';
                try {
                        const body = (await res.json()) as { error?: string; errors?: Record<string, unknown> };
                        if (body.error) {
                                message = body.error;
                        } else if (body.errors) {
                                const first = Object.values(body.errors)[0];
                                if (Array.isArray(first) && first.length > 0) message = String(first[0]);
                        }
                } catch {
                        // Respuesta sin JSON — usar mensaje genérico
                }
                throw new ApiError(message, res.status);
        }

        return (await res.json()) as InitiateDonationResponse;
}

/**
 * Consulta el estado de una donación por su referencia.
 * Lanza ApiError(404) si no existe.
 */
export async function getDonationStatus(referencia: string): Promise<DonationStatus> {
        const res = await fetchWithTimeout(fetch, `/donations/${encodeURIComponent(referencia)}/status/`);
        if (!res.ok) throw new ApiError('Donación no encontrada', res.status);
        return (await res.json()) as DonationStatus;
}

/**
 * Polling del estado de una donación hasta que sea terminal o se agote
 * el tiempo máximo. Intervalos de 3s, máximo 40 intentos (~2 min).
 * @returns el último estado conocido.
 */
export async function pollDonationStatus(
        referencia: string,
        opts: { intervalMs?: number; maxAttempts?: number; signal?: AbortSignal } = {}
): Promise<DonationStatus['donacion']> {
        const intervalMs = opts.intervalMs ?? 3000;
        const maxAttempts = opts.maxAttempts ?? 40;
        const TERMINALES = ['completado', 'fallido', 'reembolsado'];

        let last: DonationStatus['donacion'] | null = null;
        for (let i = 0; i < maxAttempts; i++) {
                if (opts.signal?.aborted) break;
                try {
                        const data = await getDonationStatus(referencia);
                        last = data.donacion;
                        if (TERMINALES.includes(last.estado)) return last;
                } catch {
                        // 404 transitorio (referencia aún propagándose) — reintentar
                }
                await new Promise((r) => setTimeout(r, intervalMs));
        }
        if (!last) throw new ApiError('No se pudo verificar el estado del pago', 503);
        return last;
}

/**
 * Envía un mensaje desde el formulario de contacto.
 * Lanza ApiError si el backend rechaza el mensaje — la UI debe mostrar
 * el error real y ofrecer reintento (nunca fingir éxito).
 */
/**
 * Formatea un entero al estándar colombiano (puntos de miles).
 * Duplicado a propósito de utils/currency: client.ts NO debe tener
 * value-imports de $lib (los tests de Node con strip-types no resuelven
 * el alias y fallarían).
 */
function fmtEntero(n: number): string {
        const v = Math.round(Number(n) || 0);
        return String(v).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

/**
 * Datos semilla para "Nuestros números" si la API no responde: cifras de
 * referencia claramente identificadas como demostrativas en la UI.
 */
export const FALLBACK_STATS: PublicStats = {
        recaudado_total: 0,
        recaudado_total_fmt: '$0',
        donaciones_count: 0,
        donacion_promedio: 0,
        donacion_promedio_fmt: '$0',
        beneficiarios_activos: 0,
        beneficiarios_apadrinados: 0,
        ciudades_atendidas: 0,
        apadrinamientos_activos: 0,
        serie_mensual: [],
        actualizado_en: new Date(0).toISOString()
};

/**
 * Convierte PublicStats en las tarjetas destacadas de la página.
 * El backend preformatea el dinero al estándar colombiano; aquí solo
 * se etiqueta y se elige el icono.
 */
export function mapStatsToCards(stats: PublicStats): UiStat[] {
        return [
                {
                        key: 'recaudado',
                        icon: 'fa-solid fa-hand-holding-heart',
                        label: 'Recaudado para la causa',
                        value: `${stats.recaudado_total_fmt} COP`
                },
                {
                        key: 'donaciones',
                        icon: 'fa-solid fa-receipt',
                        label: 'Donaciones confirmadas',
                        value: fmtEntero(stats.donaciones_count)
                },
                {
                        key: 'beneficiarios',
                        icon: 'fa-solid fa-person-cane',
                        label: 'Adultos mayores acompañados',
                        value: fmtEntero(stats.beneficiarios_activos)
                },
                {
                        key: 'apadrinados',
                        icon: 'fa-solid fa-people-roof',
                        label: 'Con padrino o madrina',
                        value: fmtEntero(stats.beneficiarios_apadrinados)
                },
                {
                        key: 'ciudades',
                        icon: 'fa-solid fa-map-location-dot',
                        label: 'Ciudades atendidas',
                        value: fmtEntero(stats.ciudades_atendidas)
                },
                {
                        key: 'apadrinamientos',
                        icon: 'fa-solid fa-handshake',
                        label: 'Apadrinamientos activos',
                        value: fmtEntero(stats.apadrinamientos_activos)
                }
        ];
}

/**
 * Obtiene las cifras públicas agregadas (GET /api/stats/).
 * Solo lectura y sin datos personales: sumas, conteos y serie mensual.
 * Lanza ApiError si el backend falla — el caller decide el fallback.
 * Ver getBeneficiaries para el parámetro fetchFn.
 */
export async function getPublicStats(fetchFn: typeof fetch = fetch): Promise<PublicStats> {
        const res = await fetchWithTimeout(fetchFn, '/stats/');
        if (!res.ok) throw new ApiError(`HTTP ${res.status}`, res.status);
        return (await res.json()) as PublicStats;
}

/**
 * Consulta una boleta por su código de verificación (GET /api/tickets/<codigo>/).
 * El código de 10 caracteres actúa como secreto compartido entre el comprador
 * y la Fundación: quien lo tenga puede ver la boleta (endpoint público con
 * throttle 'anon' contra fuerza bruta).
 * Lanza ApiError(404) si el código no existe; ApiError(otros) si el backend falla.
 */
export async function getTicket(codigo: string, fetchFn: typeof fetch = fetch): Promise<ApiTicket> {
        const res = await fetchWithTimeout(fetchFn, `/tickets/${encodeURIComponent(codigo)}/`);
        if (res.status === 404) throw new ApiError('No encontramos una boleta con ese código.', 404);
        if (!res.ok) throw new ApiError(`HTTP ${res.status}`, res.status);
        return (await res.json()) as ApiTicket;
}

/**
 * Envía un mensaje desde el formulario de contacto.
 * Lanza ApiError si el backend rechaza el mensaje — la UI debe mostrar
 * el error real y ofrecer reintento (nunca fingir éxito).
 */
export async function sendContactMessage(payload: ContactPayload): Promise<void> {
        const res = await fetchWithTimeout(fetch, '/contact/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
        });
        if (!res.ok) {
                let message = 'Error al enviar el mensaje. Verifica los datos e intenta de nuevo.';
                try {
                        const body = (await res.json()) as Record<string, unknown>;
                        const first = Object.values(body)[0];
                        if (Array.isArray(first) && first.length > 0) message = String(first[0]);
                } catch {
                        // Sin JSON en la respuesta
                }
                throw new ApiError(message, res.status);
        }
}
