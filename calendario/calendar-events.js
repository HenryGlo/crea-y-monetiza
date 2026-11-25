(function (root) {
  'use strict';
  function create({ url, storage = root.localStorage, fetch = root.fetch.bind(root), events = root, key = 'advent-events-v1' }) {
    let pending = [], sending = false;
    try { pending = JSON.parse(storage.getItem(key) || '[]'); } catch (_) {}
    if (!Array.isArray(pending)) pending = [];
    function save() { try { storage.setItem(key, JSON.stringify(pending)); } catch (_) {} }
    async function flush() {
      if (sending || !url) return;
      sending = true;
      try {
        while (pending.length) {
          const response = await fetch(url, { method: 'POST', credentials: 'omit', keepalive: true,
            headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(pending[0]) });
          if (!response.ok && ![400, 413, 422].includes(response.status)) {
            events.setTimeout?.(flush, 30000); break;
          }
          pending.shift(); save();
        }
      } catch (_) { events.setTimeout?.(flush, 30000); }
      finally { sending = false; }
    }
    function enqueue(event) { pending.push(event); save(); return flush(); }
    events.addEventListener('online', flush);
    flush();
    return { enqueue, flush };
  }
  root.AdventEvents = { create };
  if (typeof module !== 'undefined') module.exports = root.AdventEvents;
})(typeof window === 'undefined' ? globalThis : window);
