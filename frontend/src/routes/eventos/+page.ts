import type { PageLoad } from './$types';
import { getEvents, FALLBACK_EVENTS } from '$lib/api/client';
import type { UiEvent } from '$lib/types';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const eventos = await getEvents(fetch);
		return { eventos, usingFallback: false };
	} catch {
		// Fallback: seed data si el backend no responde (p.ej. mantenimiento).
		return { eventos: FALLBACK_EVENTS as UiEvent[], usingFallback: true };
	}
};
