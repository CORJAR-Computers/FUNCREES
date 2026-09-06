import { SITE_URL } from '$lib/seo';
import type { RequestHandler } from './$types';

const STATIC_ROUTES = [
	{ path: '/', priority: '1.0', changefreq: 'weekly' },
	{ path: '/quienes-somos', priority: '0.8', changefreq: 'monthly' },
	{ path: '/proyectos', priority: '0.8', changefreq: 'monthly' },
	{ path: '/historias', priority: '0.9', changefreq: 'weekly' },
	{ path: '/donaciones', priority: '1.0', changefreq: 'weekly' },
	{ path: '/eventos', priority: '0.9', changefreq: 'weekly' },
	{ path: '/numeros', priority: '0.7', changefreq: 'weekly' },
	{ path: '/contacto', priority: '0.7', changefreq: 'monthly' }
];

export const GET: RequestHandler = async () => {
	const urls = STATIC_ROUTES.map(
		(r) => `\t<url>
		<loc>${SITE_URL}${r.path}</loc>
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
