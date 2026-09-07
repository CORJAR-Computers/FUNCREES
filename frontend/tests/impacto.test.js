import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import {
        calcularImpacto,
        equivalenciaPrincipal,
        COSTOS_IMPACTO
} from '../src/lib/utils/impacto.ts';

describe('calcularImpacto()', () => {
        test('un almuerzo con el mínimo ($8.000)', () => {
                const r = calcularImpacto(8000);
                assert.equal(r.almuerzos, 1);
                assert.equal(r.sesionesTerapia, 0);
                assert.equal(r.kitsMedicamentos, 0);
                assert.equal(r.vacio, false);
        });

        test('monto intermedio redondea hacia abajo (no promete fracciones)', () => {
                const r = calcularImpacto(49000);
                assert.equal(r.almuerzos, 6); // 48.000/8.000
                assert.equal(r.sesionesTerapia, 1); // 25.000
                assert.equal(r.kitsMedicamentos, 1); // 40.000
        });

        test('montos no múltiplos usan floor por partida', () => {
                const r = calcularImpacto(15999);
                assert.equal(r.almuerzos, 1);
                assert.equal(r.sesionesTerapia, 0);
                assert.equal(r.kitsMedicamentos, 0);
        });

        test('monto por debajo del mínimo queda vacío', () => {
                const r = calcularImpacto(7999);
                assert.equal(r.vacio, true);
        });

        test('entradas inválidas no explotan y quedan vacías', () => {
                for (const entrada of [0, -5, NaN, Infinity, 'abc', null, undefined]) {
                        const r = calcularImpacto(entrada);
                        assert.equal(r.vacio, true, `entrada ${String(entrada)}`);
                        assert.equal(r.almuerzos, 0);
                }
        });

        test('aporte de apadrinamiento Raíz ($378.000) da cifras grandes', () => {
                const r = calcularImpacto(378000);
                assert.equal(r.almuerzos, 47);
                assert.equal(r.sesionesTerapia, 15);
                assert.equal(r.kitsMedicamentos, 9);
        });
});

describe('equivalenciaPrincipal()', () => {
        test('prioriza kit de medicamentos cuando el monto lo alcanza', () => {
                assert.equal(
                        equivalenciaPrincipal(40000),
                        'financia 1 kit de medicamentos mensuales'
                );
                assert.equal(
                        equivalenciaPrincipal(120000),
                        'financia 3 kits de medicamentos mensuales'
                );
        });

        test('usa sesiones de terapia cuando aún no hay kit completo', () => {
                assert.equal(equivalenciaPrincipal(25000), 'financia 1 sesión de terapia');
                assert.equal(equivalenciaPrincipal(30000), 'financia 1 sesión de terapia');
                assert.equal(equivalenciaPrincipal(39999), 'financia 1 sesión de terapia');
        });

        test('usa almuerzos como nivel base con singular/plural', () => {
                assert.equal(
                        equivalenciaPrincipal(8000),
                        'financia 1 almuerzo en nuestro comedor comunitario'
                );
                assert.equal(
                        equivalenciaPrincipal(24000),
                        'financia 3 almuerzos en nuestro comedor comunitario'
                );
        });

        test('devuelve "" cuando nada se alcanza', () => {
                assert.equal(equivalenciaPrincipal(100), '');
                assert.equal(equivalenciaPrincipal(0), '');
        });

        test('los costos unitarios son la fuente única esperada', () => {
                assert.deepEqual(COSTOS_IMPACTO, { ALMUERZO: 8000, KIT_MEDICAMENTOS: 40000, SESION_TERAPIA: 25000 });
        });
});
