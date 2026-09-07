/**
 * Calculadora de impacto de donaciones.
 *
 * Traduce un monto en COP a equivalencias concretas del trabajo de la
 * fundación, para que el donante vea QUÉ financia antes de dar. Los
 * costos unitarios son estimaciones operativas documentadas (COP 2026)
 * y viven aquí como única fuente de verdad para UI y tests.
 */

export const COSTOS_IMPACTO = {
	/** Un almuerzo balanceado en el comedor comunitario. */
	ALMUERZO: 8_000,
	/** Kit de medicamentos de un adulto mayor por un mes. */
	KIT_MEDICAMENTOS: 40_000,
	/** Una sesión de terapia física/grupal. */
	SESION_TERAPIA: 25_000
} as const;

export interface ImpactoEquivalencias {
	almuerzos: number;
	kitsMedicamentos: number;
	sesionesTerapia: number;
	/** true si el monto no alcanza para ninguna equivalencia. */
	vacio: boolean;
}

/**
 * Calcula cuántos ítems concretos financia un monto (redondeo hacia
 * abajo: no prometemos fracciones de almuerzo).
 */
export function calcularImpacto(monto: number): ImpactoEquivalencias {
	const n = Number(monto);
	const seguro = Number.isFinite(n) && n > 0 ? Math.floor(n) : 0;
	const almuerzos = Math.floor(seguro / COSTOS_IMPACTO.ALMUERZO);
	const kitsMedicamentos = Math.floor(seguro / COSTOS_IMPACTO.KIT_MEDICAMENTOS);
	const sesionesTerapia = Math.floor(seguro / COSTOS_IMPACTO.SESION_TERAPIA);
	return {
		almuerzos,
		kitsMedicamentos,
		sesionesTerapia,
		vacio: almuerzos === 0 && kitsMedicamentos === 0 && sesionesTerapia === 0
	};
}

/**
 * La equivalencia "estrella" para el encabezado de la tarjeta:
 * prioriza el ítem más significativo alcanzado por el monto.
 * Devuelve un string listo para mostrar o '' si no hay nada.
 */
export function equivalenciaPrincipal(monto: number): string {
	const r = calcularImpacto(monto);
	if (r.kitsMedicamentos >= 1) {
		return `financia ${r.kitsMedicamentos} ${r.kitsMedicamentos === 1 ? 'kit' : 'kits'} de medicamentos mensuales`;
	}
	if (r.sesionesTerapia >= 1) {
		return `financia ${r.sesionesTerapia} ${r.sesionesTerapia === 1 ? 'sesión' : 'sesiones'} de terapia`;
	}
	if (r.almuerzos >= 1) {
		return `financia ${r.almuerzos} ${r.almuerzos === 1 ? 'almuerzo' : 'almuerzos'} en nuestro comedor comunitario`;
	}
	return '';
}
