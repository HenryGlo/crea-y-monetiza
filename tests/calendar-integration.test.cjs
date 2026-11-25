const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('calendario/index.html', 'utf8');
const dayFunction = html.slice(html.indexOf('window.diaDeHoy = function'), html.indexOf('window.estaBloqueada ='));

test('public query parameters cannot advance the release date or enable student mode', () => {
  const context = { window: {}, ALUMNAS: false, PREVIEW: false, modoAlumna: () => 'todo',
    ANIO: 2026, AdventClock: { localDay: () => 0 }, location: { search: '?dia=24&vista' }, LS: { get: () => '24' }, K: { dia: 'day' } };
  vm.runInNewContext(dayFunction, context);
  assert.equal(context.window.diaDeHoy(), 0);
});

test('approved student version retains both daily and all-open modes', () => {
  let mode = 'dia';
  const context = { window: {}, ALUMNAS: true, PREVIEW: false, modoAlumna: () => mode,
    ANIO: 2026, AdventClock: { localDay: () => 6 } };
  vm.runInNewContext(dayFunction, context);
  assert.equal(context.window.diaDeHoy(), 6);
  mode = 'todo';
  assert.equal(context.window.diaDeHoy(), 24);
});

test('requires reconfirmation after 48 hours and supports disabling reconfirmation', () => {
  const fn = html.slice(html.indexOf('  function registrada(){'), html.indexOf('  const eventQueue'));
  let elapsed = 47 * 3600000;
  const context = { REGISTRO: { activo: true, volverAPedirHoras: 48 }, leerReg: () => ({ correo: 'test@example.com', confirmado: 1000 }), Date: { now: () => 1000 + elapsed } };
  vm.runInNewContext(fn, context);
  assert.equal(context.registrada(), true);
  elapsed = 48 * 3600000;
  assert.equal(context.registrada(), false);
  context.REGISTRO.volverAPedirHoras = 0;
  assert.equal(context.registrada(), true);
});

test('keeps the approved campus destination and marks unfinished gift CTAs', () => {
  assert.match(html, /campus:\s*'https:\/\/campuscreaymonetiza\.com\/'/);
  assert.match(html, /if \(!day.enlace\) day.pendiente = true/);
  assert.doesNotMatch(html, /const PREVIEW = .*location.search/);
});
