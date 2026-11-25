const { test } = require('node:test');
const assert = require('node:assert/strict');
const { create } = require('../calendario/calendar-events.js');
function storage() { const values = new Map(); return { getItem: k => values.get(k), setItem: (k, v) => values.set(k, v) }; }

test('retries failed registration before subsequent openings and keeps the same event id', async () => {
  const cache = storage(), sent = [], events = { addEventListener() {} };
  let online = false;
  const queue = create({ url: '/events', storage: cache, events, fetch: async (_url, options) => {
    const body = JSON.parse(options.body); sent.push(body.event_id); return { ok: online };
  } });
  await queue.enqueue({ event_id: 'registration-1' });
  await queue.enqueue({ event_id: 'opening-2' });
  assert.equal(JSON.parse(cache.getItem('advent-events-v1')).length, 2);
  online = true; await queue.flush();
  assert.deepEqual(sent.slice(-2), ['registration-1', 'opening-2']);
  assert.equal(JSON.parse(cache.getItem('advent-events-v1')).length, 0);
});

test('restores unsent events after reloading and retries on reconnection', async () => {
  const cache = storage(); cache.setItem('advent-events-v1', JSON.stringify([{ event_id: 'saved-event' }]));
  let reconnect, sent = 0;
  const queue = create({ url: '/events', storage: cache, events: { addEventListener(_name, fn) { reconnect = fn; } },
    fetch: async () => { sent++; throw new Error('Offline'); } });
  await queue.flush();
  assert.equal(JSON.parse(cache.getItem('advent-events-v1')).length, 1);
  await reconnect();
  assert.ok(sent >= 1);
});
