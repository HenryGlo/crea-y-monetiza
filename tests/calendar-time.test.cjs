const { test } = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const file = path.resolve('calendario/calendar-time.js');
for (const timezone of ['America/Caracas', 'Europe/Madrid', 'Pacific/Auckland', 'America/Los_Angeles']) {
  test(`unlocks at device-local midnight in ${timezone}`, () => {
    execFileSync(process.execPath, ['-e', `
      const a = require(${JSON.stringify(file)}), assert = require('node:assert/strict');
      assert.equal(a.localDay(2026, 24, new Date(2026, 10, 30, 23, 59, 59)), 0);
      assert.equal(a.localDay(2026, 24, new Date(2026, 11, 1, 0, 0)), 1);
      assert.equal(a.localDay(2026, 24, new Date(2026, 11, 5, 23, 59, 59)), 5);
      assert.equal(a.localDay(2026, 24, new Date(2026, 11, 6, 0, 0)), 6);
      assert.equal(a.localDay(2026, 24, new Date(2027, 0, 1)), 24);
      assert.equal(a.nextMidnight(new Date(2026, 11, 5, 23, 59, 59)), 1000);
      assert.equal(a.localDate(new Date(2026, 11, 5, 23, 59)), '2026-12-05');
    `], { env: { ...process.env, TZ: timezone } });
  });
}

test('refreshes the grid at midnight and after a suspended tab resumes', () => {
  const RealDate = Date;
  let now = new RealDate(2026, 11, 5, 23, 59, 59), redraws = 0, callback;
  global.Date = class extends RealDate { constructor(...args) { super(...(args.length ? args : [now.getTime()])); } };
  const listeners = {};
  const environment = { clearTimeout() {}, setTimeout(fn) { callback = fn; return 1; },
    addEventListener(name, fn) { listeners[name] = fn; }, document: { addEventListener(name, fn) { listeners[name] = fn; } } };
  try {
    require(file).watch(2026, () => redraws++, environment);
    assert.equal(redraws, 0);
    now = new RealDate(2026, 11, 6, 0, 0); callback();
    assert.equal(redraws, 1);
    now = new RealDate(2026, 11, 8, 12, 0); listeners.visibilitychange();
    assert.equal(redraws, 2);
  } finally { global.Date = RealDate; }
});
