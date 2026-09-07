import type { PageLoad } from './$types';
import { getEventDetail, ApiError } from '$lib/api/client';
import type { UiEventDetail } from '$lib/types';

export const load: PageLoad = async ({ fetch, params }) => {
	try {
		const evento = await getEventDetail(params.id, fetch);
		return { evento, notFound: false };
	} catch (err) {
		// 404 real (id inexistente o evento inactivo) u otro fallo (red/timeout):
		// la página muestra un estado amable con CTA a la lista; el SSR no crashea.
		const status = err instanceof ApiError ? err.status : 0;
		return {
			evento: null as UiEventDetail | null,
			notFound: status === 404,
			id: params.id
		};
	}
};
