#!/usr/bin/env node
/**
 * Resolvedor multiplataforma del intérprete Python del venv del backend.
 *
 * Antes, los scripts de package.json codificaban `venv\Scripts\python`
 * (solo Windows): `npm run dev` y `npm test` fallaban en Linux/Mac —
 * incluido el VPS de producción. Uso:
 *
 *   node scripts/py.mjs <cwd-relative-to-root> <args...>
 *
 * Ejemplos:
 *   node scripts/py.mjs backend manage.py runserver 0.0.0.0:8000
 *   node scripts/py.mjs backend manage.py test --settings=core.test_settings
 */
import { existsSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(new URL('.', import.meta.url)), '..');
const [cwdArg, ...args] = process.argv.slice(2);

if (!cwdArg || args.length === 0) {
	console.error('Uso: node scripts/py.mjs <directorio> <comando...>');
	process.exit(2);
}

const candidates =
	process.platform === 'win32'
		? [join(root, cwdArg, 'venv', 'Scripts', 'python.exe'), join(root, cwdArg, 'venv', 'Scripts', 'python')]
		: [join(root, cwdArg, 'venv', 'bin', 'python'), join(root, cwdArg, 'venv', 'bin', 'python3')];

const venvPython = candidates.find((p) => existsSync(p));
const command = venvPython ?? 'python3';

if (!venvPython) {
	console.warn(
		`[py.mjs] Aviso: no se encontró venv en ${cwdArg}/venv; usando "${command}" del sistema.`
	);
}

const child = spawn(command, args, {
	cwd: join(root, cwdArg),
	stdio: 'inherit',
	env: process.env
});

child.on('error', (err) => {
	console.error(`[py.mjs] No se pudo ejecutar "${command}": ${err.message}`);
	console.error('[py.mjs] Crea el venv primero: cd backend && python3 -m venv venv && venv/bin/pip install -r requirements.txt');
	process.exit(1);
});

child.on('exit', (code, signal) => {
	if (signal) process.kill(process.pid, signal);
	process.exit(code ?? 0);
});
