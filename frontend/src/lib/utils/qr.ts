/**
 * Utilidades del código QR de la boleta.
 *
 * El QR codifica el deep-link público de consulta:
 *   {origin}/boletas?codigo=XXXXXXXXXX
 * así el personal de la fundación (o cualquier asistente) escanea la
 * boleta impresa / en el teléfono y aterriza directamente en la
 * verificación, sin tipear el código a mano.
 *
 * Funciones puras (testeadas en tests/qr.test.js); la generación del SVG
 * se aísla en generarQrSvg() para poder mockear/omitir en Node.
 */

/** Patrón oficial del código de verificación de 10 caracteres. */
export const CODIGO_PATTERN = /^[A-Z0-9]{10}$/;

/**
 * Construye la URL absoluta de consulta para codificar en el QR.
 * Devuelve `null` si el código no cumple el formato oficial, de modo
 * que nunca se genere un QR roto/inútil en la boleta.
 */
export function buildBoletaDeepLink(origin: string, codigo: string): string | null {
	const limpio = (codigo ?? '').trim().toUpperCase();
	if (!CODIGO_PATTERN.test(limpio)) return null;
	const base = (origin ?? '').trim().replace(/\/+$/, '');
	if (!base) return null;
	return `${base}/boletas?codigo=${limpio}`;
}

/**
 * Genera el código QR como string SVG (seguro de incrustar: es producido
 * íntegramente por la librería `qrcode` a partir de la URL construida
 * aquí, sin ninguna entrada de usuario).
 * Devuelve '' ante cualquier fallo — la UI simplemente oculta el QR.
 */
export async function generarQrSvg(texto: string): Promise<string> {
	if (!texto) return '';
	try {
		const mod = (await import('qrcode')) as { default: { toString: (t: string, o: object) => Promise<string> } };
		return await mod.default.toString(texto, {
			type: 'svg',
			margin: 1,
			width: 176,
			errorCorrectionLevel: 'M',
			color: { dark: '#1b3a2a', light: '#ffffff' }
		});
	} catch {
		return '';
	}
}
