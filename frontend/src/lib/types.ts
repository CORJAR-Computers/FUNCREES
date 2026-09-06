/**
 * Tipos compartidos que reflejan los serializers de Django REST Framework.
 * Fuente de verdad: los archivos serializers.py del backend Django.
 */

/** GET /api/beneficiaries/ — BeneficiarySerializer */
export interface Beneficiary {
	id: string;
	nombre: string;
	historia: string;
	testimonio: string;
	edad: number;
	ciudad: string | null;
	foto_url: string | null;
	video_url: string | null;
	apadrinado: boolean;
	apadrinadores_count: number;
}

/** GET /api/events/ — EventSerializer */
export interface ApiEvent {
	id: string;
	titulo: string;
	descripcion: string | null;
	fecha: string | null; // ISO date (YYYY-MM-DD) o null para campañas permanentes
	hora: string | null; // HH:MM:SS
	lugar: string | null;
	costo_bono: string; // Decimal serializado como string
	cupo_maximo: number | null;
	cupo_disponible: number | null;
	numeracion_min: number;
	numeracion_max: number;
	permite_seleccion_numero: boolean;
	categoria: 'evento' | 'campania';
	/** URL absoluta de la imagen subida desde el admin (o null). */
	imagen: string | null;
	imagen_url: string | null;
}

/** POST /api/donations/initiate/ — InitiateDonationSerializer */
export interface InitiateDonationPayload {
	tipo: 'general' | 'apadrinamiento' | 'patrocinio' | 'boleta';
	monto: number;
	donante_nombre: string;
	donante_email: string;
	donante_documento?: string;
	donante_telefono?: string;
	metodo_pago: 'card' | 'pse' | 'bancolombia';
	beneficiario_id?: string | null;
	autorizacion_datos: boolean;
}

/** Configuración del Widget de Wompi retornada por /api/donations/initiate/ */
export interface WompiPaymentSession {
	publicKey: string;
	reference: string;
	amountInCents: number;
	currency: 'COP';
	integritySignature: string;
	redirectUrl: string;
	customerEmail: string;
	description: string;
	wompiCheckoutUrl: string;
}

/** Respuesta de POST /api/donations/initiate/ */
export interface InitiateDonationResponse {
	success: boolean;
	referencia: string;
	paymentSession: WompiPaymentSession;
}

/** GET /api/donations/{referencia}/status/ — DonationSerializer */
export interface DonationStatus {
	success: boolean;
	donacion: {
		id: string;
		referencia: string;
		tipo: string;
		monto: string;
		donante_nombre: string;
		estado: 'pendiente' | 'procesando' | 'completado' | 'fallido' | 'reembolsado';
		beneficiario: string | null;
		creado_en: string;
	};
}

/** POST /api/contact/ — ContactMessageSerializer */
export interface ContactPayload {
	nombre: string;
	email: string;
	telefono?: string;
	asunto?: string;
	mensaje: string;
}

/** Evento ya mapeado para la UI (formato interno del frontend) */
export interface UiEvent {
	/** URL de la imagen promocional (subida desde el admin o URL externa). */
	imagen?: string | null;
	id: string;
	titulo: string;
	fecha: string; // texto legible: "26 Octubre"
	hora: string;
	costo: string;
	lugar: string;
	desc: string;
	category: string;
	dateObj: string | null; // ISO datetime para el countdown
}

/** Beneficiario ya mapeado para la UI */
export interface UiBeneficiary {
	id: string;
	nombre: string;
	edad: number;
	ciudad: string;
	testimonio: string;
	historia: string;
	img: string;
}

/** GET /api/stats/ — cifras públicas agregadas (core.services.cifras_publicas) */
export interface ApiMonthStat {
	mes: string; // 'Ene', 'Feb', ...
	anio: number;
	total: number;
	total_fmt: string; // '$750.000' (formato colombiano, preformateado)
	total_fmt_corto: string; // '$750 mil' / '$1,2 M'
	cantidad: number;
	pct: number; // altura de barra % relativa al mejor mes
	es_actual: boolean;
}

export interface PublicStats {
	recaudado_total: number;
	recaudado_total_fmt: string;
	donaciones_count: number;
	donacion_promedio: number;
	donacion_promedio_fmt: string;
	beneficiarios_activos: number;
	beneficiarios_apadrinados: number;
	ciudades_atendidas: number;
	apadrinamientos_activos: number;
	serie_mensual: ApiMonthStat[];
	actualizado_en: string; // ISO datetime
}

/** Cifra ya lista para tarjetas de la UI */
export interface UiStat {
	key: string;
	icon: string; // clase FontAwesome
	label: string;
	value: string;
}
