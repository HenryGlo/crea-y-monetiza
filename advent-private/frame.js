// Archive scripts have an opaque origin: they cannot read the CRM session,
// document or storage. Only namespaced preference storage and resource navigation
// cross this bridge; all resource URLs still require a revocable access ticket.
(function (root) {
  'use strict';
  function childBootstrap(snapshot, assetRoot) {
    const values = new Map(Object.entries(snapshot));
    const storage = {
      getItem(key) { return values.has(String(key)) ? values.get(String(key)) : null; },
      setItem(key, value) {
        key = String(key); value = String(value); values.set(key, value);
        parent.postMessage({ type: 'experience-storage', key, value }, '*');
      },
      removeItem(key) {
        key = String(key); values.delete(key);
        parent.postMessage({ type: 'experience-storage', key, value: null }, '*');
      },
      clear() { for (const key of [...values.keys()]) this.removeItem(key); },
      key(index) { return [...values.keys()][index] ?? null; },
      get length() { return values.size; }
    };
    Object.defineProperty(window, 'localStorage', { value: storage, configurable: true });
    window.addEventListener('message', event => {
      if (event.source !== parent || event.data?.type !== 'experience-assets') return;
      assetRoot = event.data.asset_root;
      document.querySelector('base').href = event.data.base_url;
    });
    document.addEventListener('click', event => {
      const anchor = event.target.closest?.('a[href]');
      if (!anchor || anchor.getAttribute('href').startsWith('#')) return;
      const url = new URL(anchor.href);
      if (!url.href.startsWith(assetRoot)) return;
      event.preventDefault();
      parent.postMessage({ type: 'experience-navigation', url: url.href, newTab: anchor.target === '_blank' }, '*');
    }, true);
  }

  function initialize(environment = root) {
    const element = environment.document.getElementById('experience-document');
    if (!element) return;
    const config = JSON.parse(element.textContent);
    const frame = environment.document.getElementById('experience-frame');
    const namespace = `public-experience:${config.site_slug}:`;
    const snapshot = {};
    try {
      for (let index = 0; index < environment.localStorage.length; index++) {
        const key = environment.localStorage.key(index);
        if (key.startsWith(namespace)) snapshot[key.slice(namespace.length)] = environment.localStorage.getItem(key);
      }
    } catch (_) {}
    environment.addEventListener('message', event => {
      if (event.source !== frame.contentWindow) return;
      const data = event.data;
      if (!data || typeof data !== 'object') return;
      if (data.type === 'experience-storage' && typeof data.key === 'string' && data.key.length <= 200) {
        if (data.value !== null && (typeof data.value !== 'string' || data.value.length > 100000)) return;
        try {
          if (data.value === null) environment.localStorage.removeItem(namespace + data.key);
          else environment.localStorage.setItem(namespace + data.key, data.value);
        } catch (_) {}
      }
      if (data.type === 'experience-navigation' && typeof data.url === 'string') {
        const url = new URL(data.url, environment.location.href);
        if (url.origin !== environment.location.origin || !url.href.startsWith(config.asset_root)) return;
        if (data.newTab) environment.open(url.href, '_blank', 'noopener');
        else environment.location.assign(url.href);
      }
    });
    if (config.lease_url) {
      let lastRefresh = Date.now();
      const renew = async () => {
        if (Date.now() - lastRefresh < 25 * 60000) return;
        try {
          const response = await environment.fetch(config.lease_url, { headers: { Accept: 'application/json' } });
          if (!response.ok) return;
          const lease = await response.json();
          config.asset_root = lease.asset_root;
          lastRefresh = Date.now();
          frame.contentWindow.postMessage({ type: 'experience-assets', ...lease }, '*');
        } catch (_) {}
      };
      environment.setInterval(renew, 30 * 60000);
      environment.addEventListener('focus', renew);
      environment.document.addEventListener('visibilitychange', renew);
    }
    const encode = value => JSON.stringify(value).replace(/</g, '\\u003c');
    const escape = value => value.replace(/[&<>"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char]));
    const bootstrap = `<meta name="referrer" content="no-referrer"><base href="${escape(config.base_url)}"><script>(${childBootstrap.toString()})(${encode(snapshot)},${encode(config.asset_root)})<\/script>`;
    frame.srcdoc = config.html.replace(/<head[^>]*>/i, match => match + bootstrap);
  }
  if (typeof module !== 'undefined') module.exports = { initialize, childBootstrap };
  else initialize();
})(typeof window === 'undefined' ? globalThis : window);
