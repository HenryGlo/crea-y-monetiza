(function (root) {
  'use strict';
  function localDay(year, limit, now = new Date()) {
    if (now < new Date(year, 11, 1)) return 0;
    if (now >= new Date(year, 11, limit + 1)) return limit;
    return now.getDate();
  }
  function localDate(now = new Date()) {
    return [now.getFullYear(), String(now.getMonth() + 1).padStart(2, '0'), String(now.getDate()).padStart(2, '0')].join('-');
  }
  function nextMidnight(now = new Date()) {
    return new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1).getTime() - now.getTime();
  }
  function watch(year, repaint, environment = root) {
    let previous = localDate(), timer;
    function check() {
      const current = localDate();
      if (current !== previous) { previous = current; repaint(); }
      environment.clearTimeout(timer);
      // The bounded timer also catches clock/time-zone changes while the page
      // stays open; focus/visibility handle suspended laptops and mobile tabs.
      timer = environment.setTimeout(check, Math.min(nextMidnight() + 25, 30000));
    }
    environment.addEventListener('focus', check);
    environment.addEventListener('pageshow', check);
    environment.document.addEventListener('visibilitychange', check);
    check();
  }
  root.AdventClock = { localDay, localDate, nextMidnight, watch };
  if (typeof module !== 'undefined') module.exports = root.AdventClock;
})(typeof window === 'undefined' ? globalThis : window);
