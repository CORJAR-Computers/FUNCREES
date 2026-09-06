/**
 * URL canónica del sitio. En producción debe coincidir con el dominio real
 * (https://funcreescolombia.org). Override con VITE_SITE_URL si cambia.
 * (Acceso defensivo: import.meta.env no existe fuera de Vite, p.ej. en tests.)
 */
interface ViteEnv {
	VITE_SITE_URL?: string;
}
const metaEnv: ViteEnv = (import.meta as unknown as { env?: ViteEnv }).env ?? {};
export const SITE_URL: string = metaEnv.VITE_SITE_URL || 'https://funcreescolombia.org';

/** Nombre legal y datos de la fundación (usados en JSON-LD y metadatos). */
export const SITE_NAME = 'Fundación Crece Una Esperanza Social (FUNCREES) Colombia';
export const SITE_DESCRIPTION =
	'Fundación Funcrees Colombia en Sincelejo. Soluciones sociales innovadoras para un impacto positivo, dignificación y atención integral al adulto mayor en Sucre.';

/** URL de imagen Open Graph (reutiliza el hero del sitio). */
export const SITE_OG_IMAGE = `${SITE_URL}/assets/Foto%20Fundación.png`;

/**
 * Construye la URL absoluta de una ruta relativa para metadatos canónicos.
 */
export function absoluteUrl(path: string): string {
	return `${SITE_URL}${path}`;
}
