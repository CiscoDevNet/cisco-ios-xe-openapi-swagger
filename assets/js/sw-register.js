/*
 * Service-worker registration + "new version available" toast.
 *
 * This file is loaded as an external script (rather than inlined) so
 * that pages with a strict CSP `script-src 'self'` (no 'unsafe-inline')
 * can still register the SW. Fail-silent on every branch — a broken
 * update path must never break the page.
 *
 * SW URL + scope are derived from this script's own location so the
 * same file works from the site root (e.g. /index.html → /service-worker.js)
 * and from viewer subdirectories (e.g. /swagger-cfg-model/index.html →
 * also /service-worker.js, scope /).
 */
(function () {
    // Microsoft Clarity bootstrap (shared across all pages that include this file).
    // Kept here (external JS) so we do not need inline script tags per page.
    try {
        var CLARITY_PROJECT_ID = 'x8i204pxvc';
        if (CLARITY_PROJECT_ID && typeof window !== 'undefined' && typeof document !== 'undefined') {
            window.clarity = window.clarity || function () {
                (window.clarity.q = window.clarity.q || []).push(arguments);
            };
            if (!document.querySelector('script[data-clarity-loader="1"]')) {
                var ct = document.createElement('script');
                ct.async = true;
                ct.src = 'https://www.clarity.ms/tag/' + encodeURIComponent(CLARITY_PROJECT_ID);
                ct.setAttribute('data-clarity-loader', '1');
                var cy = document.getElementsByTagName('script')[0];
                if (cy && cy.parentNode) cy.parentNode.insertBefore(ct, cy);
                else document.head.appendChild(ct);
            }
            setClarityTags();
            // Viewers/compare pages mutate the hash as the user picks a spec,
            // module, or release without a full navigation — re-tag on change so
            // the dashboards reflect what is actually on screen.
            window.addEventListener('hashchange', setClarityTags);
        }
    } catch (e) { }

    // Derive a small set of custom dimensions from the URL + path so the
    // Clarity dashboard can filter by release, model flavour/type, page, and
    // the specific spec/module a user is looking at. Pure string parsing — no
    // dependency on any page-specific globals, fail-silent on every branch.
    function setClarityTags() {
        try {
            if (typeof window.clarity !== 'function') return;
            var set = function (k, v) {
                if (v == null || v === '') return;
                try { window.clarity('set', k, String(v)); } catch (e) { /* noop */ }
            };

            var path = (location.pathname || '');
            var segs = path.split('/').filter(Boolean);
            var last = segs.length ? segs[segs.length - 1] : 'index.html';
            var dir = segs.length > 1 ? segs[segs.length - 2] : '';

            // --- release / version: ?ver= → #ver= → hub global → localStorage ---
            var ver = '';
            try {
                ver = new URLSearchParams(location.search).get('ver') || '';
                if (!ver) {
                    var hm = (location.hash || '').match(/[#&]ver=([^&]+)/);
                    if (hm) ver = decodeURIComponent(hm[1]);
                }
                if (!ver && window.__IOSXE_ACTIVE_VERSION__) ver = window.__IOSXE_ACTIVE_VERSION__;
                if (!ver) { try { ver = localStorage.getItem('iosxe-active-version') || ''; } catch (e) { } }
            } catch (e) { /* noop */ }
            set('release', ver);

            // --- model category / flavour: swagger-<cat>-model dir, or
            //     ?category= / #category= / #cat= params on hub tools ---
            var cat = '';
            var dm = dir.match(/^swagger-(.+)-model$/);
            if (dm) cat = dm[1];
            if (!cat) {
                try {
                    cat = new URLSearchParams(location.search).get('category') || '';
                    if (!cat) {
                        var cm = (location.hash || '').match(/[#&](?:category|cat)=([^&]+)/);
                        if (cm) cat = decodeURIComponent(cm[1]);
                    }
                } catch (e) { /* noop */ }
            }
            set('model_category', cat);

            // --- page type: friendly label for the surface being viewed ---
            var page;
            if (dm) page = 'swagger-viewer';
            else if (last === '' || last === 'index.html') page = 'hub';
            else page = last.replace(/\.html?$/i, '');
            set('page', page);

            // --- spec / module: #spec= (viewers) or ?spec=/#spec= (code-gen) ---
            var spec = '';
            try {
                var sm = (location.hash || '').match(/[#&]spec=([^&]+)/);
                if (sm) spec = decodeURIComponent(sm[1]);
                if (!spec) spec = new URLSearchParams(location.search).get('spec') || '';
            } catch (e) { /* noop */ }
            set('spec', spec);
        } catch (e) { /* noop */ }
    }

    if (!('serviceWorker' in navigator)) return;
    if (location.protocol !== 'https:' && location.hostname !== 'localhost') return;
    var self = document.currentScript;
    if (!self || !self.src) return;
    // sw-register.js lives at <root>/assets/js/sw-register.js — so the
    // service worker is two URL segments up.
    var swUrl, scope;
    try {
        swUrl = new URL('../../service-worker.js', self.src).href;
        scope = new URL('../../', self.src).pathname;
    } catch (e) { return; }

    window.addEventListener('load', function () {
        navigator.serviceWorker.register(swUrl, { scope: scope }).then(function (reg) {
            function show(w) {
                if (document.getElementById('iosxe-sw-toast')) return;
                var t = document.createElement('div');
                t.id = 'iosxe-sw-toast';
                t.setAttribute('role', 'status');
                t.setAttribute('aria-live', 'polite');
                t.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:99999;'
                    + 'background:#1565c0;color:#fff;padding:10px 14px;border-radius:8px;'
                    + 'box-shadow:0 4px 12px rgba(0,0,0,.25);'
                    + 'font:14px/1.4 system-ui,-apple-system,sans-serif;'
                    + 'display:flex;gap:10px;align-items:center;max-width:90vw';
                var s = document.createElement('span');
                s.textContent = 'New version available.';
                var b = document.createElement('button');
                b.type = 'button';
                b.textContent = 'Reload';
                b.style.cssText = 'background:#fff;color:#1565c0;border:0;padding:6px 12px;'
                    + 'border-radius:6px;font:600 13px system-ui,-apple-system,sans-serif;cursor:pointer';
                var x = document.createElement('button');
                x.type = 'button';
                x.textContent = '\u00d7';
                x.setAttribute('aria-label', 'Dismiss update notification');
                x.style.cssText = 'background:transparent;color:#fff;border:0;'
                    + 'font:18px/1 system-ui,sans-serif;cursor:pointer;padding:0 4px';
                var reloaded = false;
                navigator.serviceWorker.addEventListener('controllerchange', function () {
                    if (reloaded) return;
                    reloaded = true;
                    location.reload();
                });
                b.addEventListener('click', function () {
                    try { w.postMessage({ type: 'SKIP_WAITING' }); } catch (e) { }
                });
                x.addEventListener('click', function () { t.remove(); });
                t.appendChild(s);
                t.appendChild(b);
                t.appendChild(x);
                document.body.appendChild(t);
            }
            if (reg.waiting && navigator.serviceWorker.controller) show(reg.waiting);
            reg.addEventListener('updatefound', function () {
                var nw = reg.installing;
                if (!nw) return;
                nw.addEventListener('statechange', function () {
                    if (nw.state === 'installed' && navigator.serviceWorker.controller) show(nw);
                });
            });
        }).catch(function () { });
    });
})();
