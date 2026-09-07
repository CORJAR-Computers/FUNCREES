import { SITE_URL } from '$lib/seo';
import type { RequestHandler } from './$types';

/**
 * Sitemap dinámico.
 * - Rutas estáticas con <lastmod> = fecha de arranque del servidor (deploy),
 *   señal honesta para buscadores de cuándo el contenido pudo cambiar.
 * - Páginas legales con prioridad baja (existen y son indexables).
 * - Rutas dinámicas /eventos/<id> consultadas en vivo a la API del backend,
 *   cada una con su <lastmod> REAL (Event.actualizado_en, editado desde el
 *   panel). Si la API no responde, el sitemap sigue válido solo con las
 *   rutas estáticas — nunca rompe ni bloquea el render.
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
        { path: '/boletas', priority: '0.6', changefreq: 'monthly' },
        { path: '/preguntas-frecuentes', priority: '0.6', changefreq: 'monthly' },
        { path: '/numeros', priority: '0.7', changefreq: 'weekly' },
        { path: '/contacto', priority: '0.7', changefreq: 'monthly' },
        { path: '/privacidad', priority: '0.3', changefreq: 'yearly' },
        { path: '/terminos', priority: '0.3', changefreq: 'yearly' },
        { path: '/cookies', priority: '0.2', changefreq: 'yearly' },
        { path: '/transparencia', priority: '0.4', changefreq: 'monthly' }
];

/** Fecha (YYYY-MM-DD) del arranque del proceso Node = momento del deploy. */
const LASTMOD = new Date().toISOString().slice(0, 10);

/** Evento mínimo que el sitemap necesita de la API pública. */
interface ApiEventForSitemap {
        id: string;
        actualizado_en?: string | null;
}

function escapeXml(value: string): string {
        return value
                .replaceAll('&', '&amp;')
                .replaceAll('<', '&lt;')
                .replaceAll('>', '&gt;')
                .replaceAll('"', '&quot;')
                .replaceAll("'", '&apos;');
}

function urlEntry(loc: string, lastmod: string, changefreq: string, priority: string): string {
        return `\t<url>
                <loc>${escapeXml(loc)}</loc>
                <lastmod>${lastmod}</lastmod>
                <changefreq>${changefreq}</changefreq>
                <priority>${priority}</priority>
        </url>`;
}

/** Consulta la API de eventos en SSR; null si falla (degradación elegante). */
async function fetchEventos(fetchFn: typeof fetch): Promise<ApiEventForSitemap[] | null> {
        try {
                const res = await fetchFn('/api/events/', {
                        headers: { accept: 'application/json' },
                        signal: AbortSignal.timeout(4000)
                });
                if (!res.ok) return null;
                const data = (await res.json()) as ApiEventForSitemap[] | { results?: ApiEventForSitemap[] };
                return Array.isArray(data) ? data : (data.results ?? []);
        } catch {
                return null;
        }
}

export const GET: RequestHandler = async ({ fetch }) => {
        const urls = STATIC_ROUTES.map((r) =>
                urlEntry(`${SITE_URL}${r.path}`, LASTMOD, r.changefreq, r.priority)
        );

        // Rutas dinámicas de eventos con lastmod real de cada evento.
        const eventos = await fetchEventos(fetch);
        if (eventos) {
                for (const ev of eventos) {
                        if (!ev?.id) continue;
                        // Solo IDs seguros para URL (el panel permite ids legibles tipo bingo-2026)
                        if (!/^[a-zA-Z0-9._-]+$/.test(ev.id)) continue;
                        const lastmodEvento =
                                ev.actualizado_en && !Number.isNaN(new Date(ev.actualizado_en).getTime())
                                        ? new Date(ev.actualizado_en).toISOString().slice(0, 10)
                                        : LASTMOD;
                        urls.push(
                                urlEntry(`${SITE_URL}/eventos/${encodeURIComponent(ev.id)}`, lastmodEvento, 'weekly', '0.7')
                        );
                }
        }

        const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join('\n')}
</urlset>`;

        return new Response(xml, {
                headers: {
                        'Content-Type': 'application/xml',
                        'Cache-Control': 'public, max-age=3600'
                }
        });
};
