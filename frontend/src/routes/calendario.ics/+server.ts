import type { RequestHandler } from './$types';
import { SITE_URL } from '$lib/seo';
import { buildIcsCalendar, type IcsEventInput } from '$lib/utils/ics';

/**
 * Feed de calendario iCalendar suscribible: /calendario.ics
 *
 * Google Calendar ("Desde URL"), Apple Calendar ("Suscribirse a un calendario")
 * y Outlook pueden consumir esta URL para mostrar automáticamente los eventos
 * públicos de la fundación — sin duplicar mantenimiento en el panel.
 *
 * Degradación elegante: si la API no responde, se entrega un VCALENDAR válido
 * pero vacío (los clientes de calendario reintentarán en su próximo refresco).
 */

interface ApiEventForIcs {
	id?: string;
	titulo?: string;
	fecha?: string | null;
	hora?: string | null;
	lugar?: string | null;
	descripcion?: string | null;
}

/** VCALENDAR mínimo pero 100% válido para clientes de calendario. */
const EMPTY_ICS = [
	'BEGIN:VCALENDAR',
	'VERSION:2.0',
	'PRODID:-//Fundacion Funcrees Colombia//Calendario de Eventos//ES',
	'CALSCALE:GREGORIAN',
	'METHOD:PUBLISH',
	'X-WR-CALNAME:Eventos FUNCREES Colombia',
	'X-WR-TIMEZONE:America/Bogota',
	'END:VCALENDAR'
].join('\r\n') + '\r\n';

/** Consulta la API pública de eventos en SSR; null si falla. */
async function fetchEventos(fetchFn: typeof fetch): Promise<IcsEventInput[] | null> {
	try {
		const res = await fetchFn('/api/events/', {
			headers: { accept: 'application/json' },
			signal: AbortSignal.timeout(4000)
		});
		if (!res.ok) return null;
		const data = (await res.json()) as ApiEventForIcs[] | { results?: ApiEventForIcs[] };
		const list = Array.isArray(data) ? data : (data.results ?? []);
		return list
			.filter((ev): ev is Required<Pick<ApiEventForIcs, 'id' | 'titulo'>> & ApiEventForIcs =>
				Boolean(ev?.id && ev?.titulo))
			// Solo IDs seguros (el panel permite ids legibles tipo bingo-2026)
			.filter((ev) => /^[a-zA-Z0-9._-]+$/.test(ev.id))
			.map((ev) => ({
				id: ev.id,
				titulo: ev.titulo,
				fecha: ev.fecha ?? null,
				hora: ev.hora ?? null,
				lugar: ev.lugar ?? null,
				descripcion: ev.descripcion ?? null
			}));
	} catch {
		return null;
	}
}

export const GET: RequestHandler = async ({ fetch }) => {
	const eventos = await fetchEventos(fetch);
	const body = eventos ? buildIcsCalendar(eventos, { siteUrl: SITE_URL }) : EMPTY_ICS;

	return new Response(body, {
		headers: {
			'Content-Type': 'text/calendar; charset=utf-8',
			// inline: los clientes pueden suscribirse directamente; filename para
			// quien descargue el archivo manualmente.
			'Content-Disposition': 'inline; filename="calendario-funcrees.ics"',
			'Cache-Control': 'public, max-age=1800'
		}
	});
};
