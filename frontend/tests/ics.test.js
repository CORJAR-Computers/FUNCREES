import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { escapeIcsText, foldIcsLine, buildIcsCalendar } from '../src/lib/utils/ics.ts';

describe('escapeIcsText()', () => {
        test('escapa coma, punto y coma y barra invertida', () => {
                assert.equal(escapeIcsText('Bingo, Cena; Rifa'), 'Bingo\\, Cena\\; Rifa');
                assert.equal(escapeIcsText('a\\b'), 'a\\\\b');
        });

        test('convierte saltos de línea en \\n literal', () => {
                assert.equal(escapeIcsText('línea1\nlínea2'), 'línea1\\nlínea2');
                assert.equal(escapeIcsText('a\r\nb'), 'a\\nb');
        });
});

describe('foldIcsLine()', () => {
        test('no pliega líneas cortas', () => {
                assert.equal(foldIcsLine('SUMMARY:Hola'), 'SUMMARY:Hola');
        });

        test('pliega a 75 octetos con espacio de continuación', () => {
                const line = 'DESCRIPTION:' + 'x'.repeat(200);
                const physical = foldIcsLine(line).split('\r\n');
                // Primera línea física <= 75, continuaciones <= 75 (1 espacio + 74)
                assert.ok(physical[0].length <= 75);
                for (const p of physical.slice(1)) {
                        assert.ok(p.length <= 75, `continuación de ${p.length} excede 75`);
                        assert.ok(p.startsWith(' '), 'toda continuación empieza con espacio');
                }
                // El plegado es reversible: quitar "\r\n " restaura la línea original
                assert.equal(physical.join('\r\n').replaceAll('\r\n ', ''), line);
        });
});

const now = new Date('2026-09-07T12:00:00Z');
const seed = new Date('2026-09-07T12:00:00Z');

function ev(overrides) {
        return {
                id: 'bingo-2026',
                titulo: 'Bingo Solidario 2026',
                fecha: '2026-10-10',
                hora: '15:00',
                lugar: 'Salón Comunal, Sincelejo',
                descripcion: 'Gran bingo benéfico',
                ...overrides
        };
}

describe('buildIcsCalendar()', () => {
        const base = {
                now,
                seed
        };

        test('estructura VCALENDAR válida con VTIMEZONE de Bogotá', () => {
                const ics = buildIcsCalendar([ev({})], base);
                assert.ok(ics.startsWith('BEGIN:VCALENDAR\r\n'));
                assert.ok(ics.includes('VERSION:2.0'));
                assert.ok(ics.includes('PRODID:-//Fundacion Funcrees Colombia//Calendario de Eventos//ES'));
                assert.ok(ics.includes('X-WR-CALNAME:Eventos FUNCREES Colombia'));
                assert.ok(ics.includes('TZID:America/Bogota'));
                assert.ok(ics.trimEnd().endsWith('END:VCALENDAR'));
                // Todas las líneas usan CRLF (sin \n suelto)
                assert.ok(!/[^\r]\n/.test(ics));
        });

        test('evento con hora: DTSTART/DTEND con TZID y duración de 2h', () => {
                const ics = buildIcsCalendar([ev({})], base);
                assert.ok(ics.includes('DTSTART;TZID=America/Bogota:20261010T150000'));
                assert.ok(ics.includes('DTEND;TZID=America/Bogota:20261010T170000'));
        });

        test('evento sin hora: todo el día con DTEND exclusivo', () => {
                const ics = buildIcsCalendar([ev({ hora: null })], base);
                assert.ok(ics.includes('DTSTART;VALUE=DATE:20261010'));
                assert.ok(ics.includes('DTEND;VALUE=DATE:20261011'));
        });

        test('fin de mes: DTEND de evento de todo el día cruza al mes siguiente', () => {
                const ics = buildIcsCalendar([ev({ fecha: '2026-10-31', hora: null })], base);
                assert.ok(ics.includes('DTEND;VALUE=DATE:20261101'));
        });

        test('escapa comas del lugar y del título en el VEVENT', () => {
                const ics = buildIcsCalendar(
                        [ev({ titulo: 'Bingo, cena y rifa', lugar: 'Cra. 15b #41c-07, Sincelejo' })],
                        base
                );
                assert.ok(ics.includes('SUMMARY:Bingo\\, cena y rifa'));
                assert.ok(ics.includes('LOCATION:Cra. 15b #41c-07\\, Sincelejo'));
        });

        test('UID y URL incluyen el id del evento', () => {
                const ics = buildIcsCalendar([ev({})], base);
                assert.ok(ics.includes('UID:bingo-2026@funcreescolombia.org'));
                assert.ok(ics.includes('URL:https://funcreescolombia.org/eventos/bingo-2026'));
        });

        test('DTSTAMP es DATE-TIME UTC (YYYYMMDDTHHMMSSZ)', () => {
                const ics = buildIcsCalendar([ev({})], base);
                assert.ok(ics.includes('DTSTAMP:20260907T120000Z'));
        });

        test('excluye campañas sin fecha y eventos pasados', () => {
                const ics = buildIcsCalendar(
                        [
                                ev({ id: 'campania-permanente', fecha: null }),
                                ev({ id: 'pasado', fecha: '2026-01-01' }),
                                ev({})
                        ],
                        base
                );
                assert.equal((ics.match(/BEGIN:VEVENT/g) ?? []).length, 1);
                assert.ok(ics.includes('UID:bingo-2026@'));
        });

        test('incluye eventos de HOY (borde inferior inclusivo)', () => {
                const ics = buildIcsCalendar([ev({ fecha: '2026-09-07' })], base);
                assert.equal((ics.match(/BEGIN:VEVENT/g) ?? []).length, 1);
        });

        test('sin eventos futuros: VCALENDAR válido pero sin VEVENT', () => {
                const ics = buildIcsCalendar([ev({ fecha: '2020-01-01' })], base);
                assert.ok(ics.includes('BEGIN:VCALENDAR'));
                assert.equal((ics.match(/BEGIN:VEVENT/g) ?? []).length, 0);
                assert.ok(ics.includes('END:VCALENDAR'));
        });

        test('descripción incluye enlace profundo al detalle', () => {
                const ics = buildIcsCalendar([ev({})], base);
                // Tras desplegar el plegado, la descripción contiene el enlace al detalle
                const desplegado = ics.replaceAll('\r\n ', '');
                assert.ok(desplegado.includes('Más información: https://funcreescolombia.org/eventos/bingo-2026'));
        });
});
