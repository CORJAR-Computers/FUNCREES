import type { PageLoad } from './$types';
import { getPublicStats, FALLBACK_STATS } from '$lib/api/client';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const cifras = await getPublicStats(fetch);
		return { cifras, usingFallback: false };
	} catch {
		// Fallback: cifras en cero si el backend no responde (la UI avisa).
		return { cifras: FALLBACK_STATS, usingFallback: true };
	}
};
