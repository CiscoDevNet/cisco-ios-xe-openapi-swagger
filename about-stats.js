// about-stats.js — hydrate the About page "By the numbers" cards from
// version-stats.json so they reflect the current default release instead of
// drifting hand-maintained counts. CSP-safe: external 'self' script + 'self'
// fetch only.
(function () {
    'use strict';
    function fmt(n) {
        return (n == null) ? '\u2014' : Number(n).toLocaleString();
    }
    fetch('version-stats.json', { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .catch(function () { return null; })
        .then(function (data) {
            if (!data || !data.totals) return;
            var ver = data.default_version;
            var t = data.totals[ver];
            if (!t) return;
            var heading = document.getElementById('stats-h');
            if (heading) heading.textContent = 'By the numbers (' + ver + ' default)';
            document.querySelectorAll('[data-stat-about]').forEach(function (el) {
                var key = el.getAttribute('data-stat-about');
                if (t[key] != null) el.textContent = fmt(t[key]);
            });
        });
})();
