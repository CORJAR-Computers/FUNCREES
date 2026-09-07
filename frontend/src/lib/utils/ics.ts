/**
 * Generador de calendario iCalendar (RFC 5545) para los eventos públicos.
 *
 * Lo consume el endpoint /calendario.ics (SSR) y permite a los seguidores
 * suscribirse al calendario de la fundación desde Google Calendar, Apple
 * Calendar u Outlook — sin mantener un calendario aparte en el panel.
 *
 * Decisiones de diseño:
 * - Funciones puras y sin dependencias para poder testearlas con node --test.
 * - Colombia no maneja horario de verano (UTC-5 fijo desde 1993), por lo que
 *   se incluye un VTIMEZONE mínimo y exacto para America/Bogota.
 * - Las líneas se pliegan a 75 octetos (RFC 5545 §3.1) con continuación CRLF+espacio.
 * - Los eventos sin fecha (campañas permanentes) no califican para VEVENT.
 * - Solo se publican eventos con fecha >= hoy: un feed suscribible debe
 *   mostrar lo próximo, no llenarse de eventos pasados.
 */

/** Campos mínimos que el feed necesita de un evento (los mismos de /api/events/). */
export interface IcsEventInput {
        id: string;
        titulo: string;
        fecha: string | null | undefined; // YYYY-MM-DD
        hora: string | null | undefined; // "HH:MM" 24h, hora local Colombia
        lugar: string | null | undefined;
        descripcion: string | null | undefined;
}

export interface BuildIcsOptions {
        /** Fecha de referencia para filtrar eventos pasados (default: ahora). */
        now?: Date;
        /** Marca de tiempo del feed (default: now). Congelable en tests. */
        seed?: Date;
        /** Dominio para los UID y URL de cada evento. */
        siteUrl?: string;
}

/** Escapa texto según RFC 5545 §3.3.11 (coma, punto y coma, barra y saltos). */
export function escapeIcsText(value: string): string {
        return value
                .replaceAll('\\', '\\\\')
                .replaceAll(';', '\\;')
                .replaceAll(',', '\\,')
                .replaceAll('\r\n', '\\n')
                .replaceAll('\n', '\\n');
}

/**
 * Pliega una línea de contenido a máximo 75 octetos por línea física.
 * Las continuaciones usan CRLF + un espacio (RFC 5545 §3.1).
 */
export function foldIcsLine(line: string): string {
        const MAX = 75;
        if (line.length <= MAX) return line;
        const parts: string[] = [];
        let rest = line;
        let first = true;
        while (rest.length > 0) {
                const limit = first ? MAX : MAX - 1; // la continuación deja 1 espacio al inicio
                parts.push(first ? rest.slice(0, limit) : ` ${rest.slice(0, limit)}`);
                rest = rest.slice(limit);
                first = false;
        }
        return parts.join('\r\n');
}

/** YYYYMMDDTHHMMSSZ en UTC (formato DATE-TIME de RFC 5545). */
function toUtcStamp(d: Date): string {
        return (
                `${d.getUTCFullYear()}` +
                `${String(d.getUTCMonth() + 1).padStart(2, '0')}` +
                `${String(d.getUTCDate()).padStart(2, '0')}T` +
                `${String(d.getUTCHours()).padStart(2, '0')}` +
                `${String(d.getUTCMinutes()).padStart(2, '0')}` +
                `${String(d.getUTCSeconds()).padStart(2, '0')}Z`
        );
}

/**
 * VTIMEZONE mínimo y válido para America/Bogota: Colombia no observa DST
 * (última vez en 1993), así que una sola regla STANDARD con offset -0500 fijo
 * es correcta para cualquier fecha actual o futura.
 */
const VTIMEZONE_BOGOTA = [
        'BEGIN:VTIMEZONE',
        'TZID:America/Bogota',
        'BEGIN:STANDARD',
        'DTSTART:19700101T000000',
        'TZOFFSETFROM:-0500',
        'TZOFFSETTO:-0500',
        'TZNAME:COT',
        'END:STANDARD',
        'END:VTIMEZONE'
];

/** Convierte "2026-10-10" + "15:00" a minutos desde medianoche; null si es inválido. */
function parseHoraMinutos(hora: string | null | undefined): number | null {
        if (!hora) return null;
        const m = /^(\d{1,2}):(\d{2})/.exec(hora.trim());
        if (!m) return null;
        const h = parseInt(m[1], 10);
        const min = parseInt(m[2], 10);
        if (Number.isNaN(h) || Number.isNaN(min) || h > 23 || min > 59) return null;
        return h * 60 + min;
}

/** "2026-10-10" -> Date a medianoche local-Bogotá representado en sus partes. */
function parseFechaParts(fecha: string | null | undefined): { y: number; m: number; d: number } | null {
        if (!fecha) return null;
        const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(fecha.trim());
        if (!m) return null;
        return { y: parseInt(m[1], 10), m: parseInt(m[2], 10), d: parseInt(m[3], 10) };
}

function pad2(n: number): string {
        return String(n).padStart(2, '0');
}

/**
 * Construye las líneas de un VEVENT para un evento con fecha.
 * - Con hora: DTSTART/DTEND con TZID=America/Bogota y duración de 2 horas
 *   (misma suposición del botón "Añadir a Google Calendar" del sitio).
 * - Sin hora: evento de todo el día (VALUE=DATE, DTEND exclusivo = día siguiente).
 */
export function buildVevent(ev: IcsEventInput, opts: Required<Pick<BuildIcsOptions, 'seed' | 'siteUrl'>>): string[] {
        const lines: string[] = ['BEGIN:VEVENT'];
        const uidHost = 'funcreescolombia.org';
        lines.push(`UID:${escapeIcsText(ev.id)}@${uidHost}`);
        lines.push(`DTSTAMP:${toUtcStamp(opts.seed)}`);

        const f = parseFechaParts(ev.fecha);
        const minutos = parseHoraMinutos(ev.hora);

        if (f && minutos != null) {
                // Evento con hora local Colombia (UTC-5 fijo)
                const endMin = minutos + 2 * 60;
                const endH = Math.floor(endMin / 60) % 24;
                lines.push(`DTSTART;TZID=America/Bogota:${f.y}${pad2(f.m)}${pad2(f.d)}T${pad2(Math.floor(minutos / 60))}${pad2(minutos % 60)}00`);
                lines.push(`DTEND;TZID=America/Bogota:${f.y}${pad2(f.m)}${pad2(f.d)}T${pad2(endH)}${pad2(endMin % 60)}00`);
        } else if (f) {
                // Todo el día: DTEND exclusivo (día siguiente; Date resuelve el mes/año)
                const end = new Date(f.y, f.m - 1, f.d + 1);
                lines.push(`DTSTART;VALUE=DATE:${f.y}${pad2(f.m)}${pad2(f.d)}`);
                lines.push(`DTEND;VALUE=DATE:${end.getFullYear()}${pad2(end.getMonth() + 1)}${pad2(end.getDate())}`);
        }

        lines.push(`SUMMARY:${escapeIcsText(ev.titulo)}`);
        if (ev.lugar) lines.push(`LOCATION:${escapeIcsText(ev.lugar)}`);
        const desc = ev.descripcion
                ? `${ev.descripcion} — Más información: ${opts.siteUrl}/eventos/${ev.id}`
                : `Evento solidario de Fundación Funcrees Colombia. Más información: ${opts.siteUrl}/eventos/${ev.id}`;
        lines.push(`DESCRIPTION:${escapeIcsText(desc)}`);
        lines.push(`URL:${opts.siteUrl}/eventos/${encodeURIComponent(ev.id)}`);
        lines.push('STATUS:CONFIRMED');
        lines.push('END:VEVENT');
        return lines;
}

/**
 * Construye el calendario completo (VCALENDAR) a partir de eventos de la API.
 * Devuelve el archivo ICS completo con CRLF como separador (RFC 5545 §3.4).
 * Si no hay eventos futuros, devuelve un VCALENDAR válido pero vacío.
 */
export function buildIcsCalendar(
        eventos: IcsEventInput[],
        options: BuildIcsOptions = {}
): string {
        const now = options.now ?? new Date();
        const seed = options.seed ?? now;
        const siteUrl = (options.siteUrl ?? 'https://funcreescolombia.org').replace(/\/$/, '');

        const hoy = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const futuros = eventos.filter((ev) => {
                const f = parseFechaParts(ev.fecha);
                if (!f) return false; // campañas permanentes sin fecha no califican
                const fechaEvento = new Date(f.y, f.m - 1, f.d);
                return fechaEvento.getTime() >= hoy.getTime();
        });

        const head = [
                'BEGIN:VCALENDAR',
                'VERSION:2.0',
                'PRODID:-//Fundacion Funcrees Colombia//Calendario de Eventos//ES',
                'CALSCALE:GREGORIAN',
                'METHOD:PUBLISH',
                'X-WR-CALNAME:Eventos FUNCREES Colombia',
                'X-WR-TIMEZONE:America/Bogota',
                'X-PUBLISHED-TTL:PT1H'
        ];

        const body = futuros.flatMap((ev) => buildVevent(ev, { seed, siteUrl }));

        const all = [...head, ...VTIMEZONE_BOGOTA, ...body, 'END:VCALENDAR'];
        // El VTIMEZONE solo es necesario si hay eventos con hora; pero incluirlo
        // siempre es válido y simplifica. Plegado a 75 octetos:
        return all.map(foldIcsLine).join('\r\n') + '\r\n';
}
