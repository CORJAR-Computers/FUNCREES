import { SITE_URL } from '$lib/seo';
import type { RequestHandler } from './$types';

/**
 * Sitemap dinámico.
 * - Rutas estáticas con <lastmod> = fecha de arranque del servidor (deploy),
 *   señal honesta para buscadores de cuándo el contenido pudo cambiar.
 * - Las páginas legales se incluyen con prioridad baja (existen y son
 *   indexables; antes de esta versión el footer enlazaba a rutas 404).
 */
interface SitemapRoute {
	path: string;
	priority: string;
	changefreq: string;
}

const STATIC_ROUTES: SitemapRoute[] = [
	{ path: '/', priority: '1.0', changefreq: 'weekly' },
	{ path: '/quienes-somos', priority: '0.8', changefreq: 'monthly' },
	{ path: '/proyectos', priority: '0.8', changefreq: 'monthly' },
	{ path: '/historias', priority: '0.9', changefreq: 'weekly' },
	{ path: '/donaciones', priority: '1.0', changefreq: 'weekly' },
	{ path: '/eventos', priority: '0.9', changefreq: 'weekly' },
	{ path: '/numeros', priority: '0.7', changefreq: 'weekly' },
	{ path: '/contacto', priority: '0.7', changefreq: 'monthly' },
	{ path: '/privacidad', priority: '0.3', changefreq: 'yearly' },
	{ path: '/terminos', priority: '0.3', changefreq: 'yearly' },
	{ path: '/cookies', priority: '0.2', changefreq: 'yearly' },
	{ path: '/transparencia', priority: '0.4', changefreq: 'monthly' }
];

/** Fecha (YYYY-MM-DD) del arranque del proceso Node = momento del deploy. */
const LASTMOD = new Date().toISOString().slice(0, 10);

function escapeXml(value: string): string {
	return value
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&apos;');
}

export const GET: RequestHandler = async () => {
	const urls = STATIC_ROUTES.map(
		(r) => `\t<url>
		<loc>${escapeXml(`${SITE_URL}${r.path}`)}</loc>
		<lastmod>${LASTMOD}</lastmod>
		<changefreq>${r.changefreq}</changefreq>
		<priority>${r.priority}</priority>
	</url>`
	).join('\n');

	const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

	return new Response(xml, {
		headers: {
			'Content-Type': 'application/xml',
			'Cache-Control': 'public, max-age=3600'
		}
	});
};
