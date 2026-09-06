import type { PageLoad } from './$types';
import { getBeneficiaries, FALLBACK_BENEFICIARIES } from '$lib/api/client';
import type { UiBeneficiary } from '$lib/types';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const abuelitos = await getBeneficiaries(fetch);
		return { abuelitos, usingFallback: false };
	} catch {
		// Fallback: seed data si el backend no responde.
		return { abuelitos: FALLBACK_BENEFICIARIES as UiBeneficiary[], usingFallback: true };
	}
};
