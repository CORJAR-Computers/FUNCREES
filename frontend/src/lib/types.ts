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
        /** srcset de variantes WebP (200w/400w/800w); null si aún no hay variantes. */
        foto_webp_srcset: string | null;
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
        /** srcset de variantes WebP (200w/400w/800w/1200w); null si aún no hay variantes. */
        imagen_webp_srcset: string | null;
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
/**
 * Valores válidos de `tipo` según TIPO_CHOICES del modelo ContactMessage
 * (backend/contact/models.py). El serializer de DRF rechaza cualquier otro.
 */
export type ContactTipo =
        | 'consulta'
        | 'apadrinamiento'
        | 'alianza'
        | 'voluntariado'
        | 'eventos'
        | 'donacion'
        | 'otro';

export interface ContactPayload {
        nombre: string;
        email: string;
        telefono?: string;
        /** Código del motivo (TIPO_CHOICES del backend). Antes se enviaba `asunto`
         *  y DRF lo ignoraba: el motivo real nunca llegaba al inbox del admin. */
        tipo: ContactTipo;
        mensaje: string;
}

/** Evento ya mapeado para la UI (formato interno del frontend) */
export interface UiEvent {
        /** URL de la imagen promocional (subida desde el admin o URL externa). */
        imagen?: string | null;
        /** srcset WebP para <source> (null si la imagen es externa o no tiene variantes). */
        imagen_webp_srcset?: string | null;
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
        /** srcset WebP para <source> (null si la foto es externa o no tiene variantes). */
        img_webp_srcset?: string | null;
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

/** GET /api/tickets/<codigo>/ — TicketSerializer (consulta pública por código) */
export type TicketEstado = 'pendiente' | 'pagado' | 'cancelado';

/** Ticket tal como lo devuelve el backend DRF (campos públicos y seguros). */
export interface ApiTicket {
        id: string;
        evento: string; // id legible del evento (bingo-2026, ...)
        evento_titulo: string;
        numero_ticket: number;
        comprador_nombre: string;
        monto_pagado: string; // Decimal serializado como string
        estado_pago: TicketEstado;
        seleccion_tipo: 'automatico' | 'manual';
}
