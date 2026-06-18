/* viewer-enhancements.js — small UX layer shared by every
 * swagger-*-model/index.html viewer.
 *
 * Responsibilities (intentionally small + side-effect-only — the viewers
 * keep all their existing logic):
 *
 *   1. Mirror `?ver=<release>` from the query string into the URL hash
 *      so window.__DeepLink.copyShareLink() captures the active release.
 *      The viewer's own __activeVer() already reads from both, so this is
 *      purely a share-link fix.
 *
 *   2. Inject a "switch release" <select> next to the version pill in the
 *      header. Selecting another release reloads the same spec/op in the
 *      target release (or warns if the spec doesn't exist there yet).
 *
 *   3. Global `/` keyboard shortcut that focuses the sidebar module search
 *      box (matches GitHub's convention).
 *
 *   4. window.__showViewerToast(message, kind) — a tiny toast helper used
 *      by the viewer's spec-load error path. Falls back gracefully if the
 *      page already provides showToast() (e.g. via site-chrome.js).
 *
 * No external dependencies. Safe to load on every viewer.
 */
(function () {
    'use strict';

    // ---------- (1) sync ?ver= → hash so Copy Share Link captures it ----
    function syncQueryVerIntoHash() {
        try {
            var q = new URLSearchParams(window.location.search);
            var ver = q.get('ver');
            if (!ver) return;
            var raw = (window.location.hash || '').replace(/^#/, '');
            if (/(^|&)ver=/.test(raw)) return;          // already present
            var newHash = 'ver=' + encodeURIComponent(ver) + (raw ? '&' + raw : '');
            // Use replaceState so we don't churn history and don't fire
            // hashchange (which would trigger the viewer's checkHash early).
            if (window.history && window.history.replaceState) {
                window.history.replaceState(null, '', window.location.pathname
                    + window.location.search + '#' + newHash);
            } else {
                window.location.hash = '#' + newHash;
            }
        } catch (_) { /* noop */ }
    }

    // ---------- (2) version switcher in header --------------------------
    function injectVersionSwitcher() {
        // Reuse the allow-list baked into the viewer by
        // scripts/patch_viewers_version_aware.py so we don't fetch
        // releases/index.json a second time.
        var allowed = window.__IOSXE_ALLOWED_VERS__;
        if (!allowed || !allowed.length) return;
        var pill = document.querySelector('.header-version');
        if (!pill) return;
        if (document.getElementById('viewerVersionPicker')) return;

        var active = (typeof window.__IOSXE_ACTIVE_VERSION__ === 'string')
            ? window.__IOSXE_ACTIVE_VERSION__ : allowed[0];

        var wrap = document.createElement('span');
        wrap.className = 'viewer-version-switcher';
        var label = document.createElement('label');
        label.setAttribute('for', 'viewerVersionPicker');
        label.className = 'sr-only';
        label.textContent = 'Switch IOS XE release';
        var sel = document.createElement('select');
        sel.id = 'viewerVersionPicker';
        sel.title = 'Switch IOS XE release (preserves current spec & operation)';
        allowed.forEach(function (v) {
            var opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            if (v === active) opt.selected = true;
            sel.appendChild(opt);
        });
        sel.addEventListener('change', function () {
            var newVer = sel.value;
            try { localStorage.setItem('iosxe-active-version', newVer); }
            catch (_) {}
            // Rebuild the URL: keep #spec/#op, swap ver=. Use ?ver= so the
            // viewer's __activeVer() picks it up before the hash is parsed.
            var url = new URL(window.location.href);
            url.searchParams.set('ver', newVer);
            // Rebuild hash with stable order ver=,spec=,op=.
            var raw = (url.hash || '').replace(/^#/, '');
            var parts = raw.split('&').filter(function (p) { return p && !/^ver=/.test(p); });
            parts.unshift('ver=' + encodeURIComponent(newVer));
            url.hash = '#' + parts.join('&');
            // Hard navigate — the new release's api/ + tree links must be
            // re-fetched cleanly, easier than re-running viewer init().
            window.location.assign(url.toString());
        });
        // Place after the version pill text node.
        wrap.appendChild(label);
        wrap.appendChild(sel);
        if (pill.parentNode) pill.parentNode.insertBefore(wrap, pill.nextSibling);
    }

    // ---------- (3) `/` focuses the sidebar search box ------------------
    function attachSlashFocus() {
        document.addEventListener('keydown', function (e) {
            if (e.key !== '/') return;
            var t = e.target;
            // Don't hijack while the user is typing in an input/textarea/etc.
            if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA'
                    || t.tagName === 'SELECT' || t.isContentEditable)) return;
            var box = document.getElementById('searchBox')
                || document.getElementById('universalSearch');
            if (!box) return;
            e.preventDefault();
            box.focus();
            try { box.select(); } catch (_) {}
        });
    }

    // ---------- (4) toast helper ---------------------------------------
    function ensureToastEl() {
        var t = document.getElementById('iosxe-viewer-toast');
        if (t) return t;
        t = document.createElement('div');
        t.id = 'iosxe-viewer-toast';
        t.setAttribute('role', 'status');
        t.setAttribute('aria-live', 'polite');
        t.style.cssText =
            'position:fixed;right:16px;bottom:16px;z-index:99999;'
            + 'background:#1565c0;color:#fff;padding:10px 14px;border-radius:8px;'
            + 'box-shadow:0 4px 12px rgba(0,0,0,.25);'
            + 'font:14px/1.4 system-ui,-apple-system,sans-serif;'
            + 'max-width:90vw;display:none;';
        document.body.appendChild(t);
        return t;
    }
    window.__showViewerToast = function (msg, kind) {
        // Prefer a page-provided showToast if any (e.g. site-chrome.js).
        try {
            if (typeof window.showToast === 'function') {
                window.showToast(msg, kind || 'info');
                return;
            }
        } catch (_) {}
        var t = ensureToastEl();
        t.textContent = msg;
        t.style.background = (kind === 'error')   ? '#c62828'
                           : (kind === 'warning') ? '#b26500'
                           : (kind === 'success') ? '#2e7d32'
                                                   : '#1565c0';
        t.style.display = 'block';
        clearTimeout(t.__hideTimer);
        t.__hideTimer = setTimeout(function () { t.style.display = 'none'; }, 4000);
    };

    // ---------- bootstrap ----------------------------------------------
    function boot() {
        syncQueryVerIntoHash();
        injectVersionSwitcher();
        injectSidebarToggle();
        attachSlashFocus();
        attachOperationTracking();
        attachTreeViewTracking();
        attachNotificationsPanel();
    }

    // ---------- (4d) per-module notifications capability panel -----------
    // When a module is selected in any Swagger viewer, surface whether it
    // defines YANG notifications (the catalog the per-model OpenAPI specs do
    // not include — MIB SNMP traps in particular). Reads the shared
    // notifications index once and injects a compact panel above the spec,
    // linking to the full catalog filtered to this module. Fail-silent.
    var _notifIndex = undefined;   // undefined=not loaded, null=unavailable
    function attachNotificationsPanel() {
        try {
            if (!document.getElementById('swagger-ui')) return;
            updateNotificationsPanel();
            window.addEventListener('hashchange', updateNotificationsPanel);
        } catch (_) { /* noop */ }
    }

    function _currentSpecFromHash() {
        try {
            var m = (location.hash || '').match(/[#&]spec=([^&]+)/);
            if (m) {
                var v = decodeURIComponent(m[1]);
                // Some viewers encode spec as "<category>/<module>"; keep the tail.
                return v.indexOf('/') >= 0 ? v.split('/').pop() : v;
            }
        } catch (_) { /* noop */ }
        return '';
    }

    function _notifIndexUrls() {
        // Version-aware, viewer pages live one directory deep.
        var ver = '';
        try {
            ver = new URLSearchParams(location.search).get('ver') || '';
            if (!ver) {
                var hm = (location.hash || '').match(/[#&]ver=([^&]+)/);
                if (hm) ver = decodeURIComponent(hm[1]);
            }
            if (!ver && window.__IOSXE_ACTIVE_VERSION__) ver = window.__IOSXE_ACTIVE_VERSION__;
            if (!ver) { ver = localStorage.getItem('iosxe-active-version') || ''; }
        } catch (_) { /* noop */ }
        var urls = [];
        if (ver) urls.push('../releases/' + encodeURIComponent(ver) + '/notifications.json');
        urls.push('../notifications.json');   // default-release root copy
        return urls;
    }

    function _loadNotifIndex() {
        if (_notifIndex !== undefined) return Promise.resolve(_notifIndex);
        var urls = _notifIndexUrls();
        var i = 0;
        function tryNext() {
            if (i >= urls.length) { _notifIndex = null; return _notifIndex; }
            var url = urls[i++];
            return fetch(url, { cache: 'default' })
                .then(function (r) { return r.ok ? r.json() : tryNext(); })
                .then(function (doc) {
                    if (doc && doc.modules) {
                        _notifIndex = {};
                        doc.modules.forEach(function (m) { _notifIndex[m.module] = m; });
                        return _notifIndex;
                    }
                    return tryNext();
                })
                .catch(function () { return tryNext(); });
        }
        return Promise.resolve(tryNext());
    }

    function _ensurePanelEl() {
        var panel = document.getElementById('iosxe-notif-panel');
        if (panel) return panel;
        var ui = document.getElementById('swagger-ui');
        if (!ui || !ui.parentNode) return null;
        panel = document.createElement('div');
        panel.id = 'iosxe-notif-panel';
        panel.style.cssText =
            'display:none;margin:0 0 12px;padding:10px 14px;border:1px solid #e0c068;'
            + 'border-left:4px solid #EF6C00;border-radius:4px;background:#fff8ec;'
            + 'font:13px/1.5 system-ui,-apple-system,sans-serif;color:#333;';
        ui.parentNode.insertBefore(panel, ui);
        return panel;
    }

    function updateNotificationsPanel() {
        var spec = _currentSpecFromHash();
        var panel = document.getElementById('iosxe-notif-panel');
        if (!spec) { if (panel) panel.style.display = 'none'; return; }
        _loadNotifIndex().then(function (idx) {
            if (!idx) return;
            var mod = idx[spec];
            panel = _ensurePanelEl();
            if (!panel) return;
            if (!mod || !mod.notification_count) { panel.style.display = 'none'; return; }
            var names = (mod.notifications || []).map(function (n) { return n.name; });
            var consume = mod.restconf_consumable
                ? '<span style="color:#2E7D32;font-weight:600;">consumed via NETCONF subscription / gRPC dial-out</span>'
                : '<span style="color:#9E6000;font-weight:600;">delivered over SNMP (not RESTCONF/NETCONF)</span>';
            var href = '../notifications.html?q=' + encodeURIComponent(spec);
            panel.innerHTML =
                '<strong>' + mod.notification_count + ' YANG notification'
                + (mod.notification_count === 1 ? '' : 's')
                + '</strong> defined by this module &mdash; ' + consume + '.'
                + (mod.consumption ? '<div style="margin-top:3px;color:#6a5a3a;font-size:12px;">' + mod.consumption.replace(/[<>]/g, '') + '</div>' : '')
                + '<div style="margin-top:4px;color:#555;font-family:Consolas,Monaco,monospace;font-size:12px;">'
                + names.map(function (n) { return n.replace(/[&<>"]/g, ''); }).slice(0, 6).join(' &middot; ')
                + (names.length > 6 ? ' &middot; +' + (names.length - 6) + ' more' : '')
                + '</div>'
                + '<a href="' + href + '" style="display:inline-block;margin-top:6px;color:#EF6C00;'
                + 'font-weight:600;text-decoration:none;">View payloads &amp; examples in Notification Catalog &rarr;</a>';
            panel.style.display = 'block';
        });
    }

    // ---------- (4b) analytics: which operation, for which module -------
    // Capture every time a user expands an operation in the Swagger UI so the
    // Clarity dashboard can answer "which method (GET/POST/DELETE/…) for which
    // module/path". One delegated listener covers both direct opblock clicks
    // and the paths-search "jump to operation" flow (which clicks the opblock
    // for us). Fail-silent; a no-op when Clarity / the tracker is absent.
    function attachOperationTracking() {
        try {
            var _lastOpKey = '';
            document.addEventListener('click', function (ev) {
                try {
                    var t = ev.target;
                    if (!t || typeof t.closest !== 'function') return;
                    var summary = t.closest('.opblock-summary');
                    if (!summary) return;

                    var methodEl = summary.querySelector('.opblock-summary-method');
                    var pathEl = summary.querySelector('.opblock-summary-path');
                    var method = methodEl ? (methodEl.textContent || '').trim().toUpperCase() : '';
                    var opPath = '';
                    if (pathEl) {
                        opPath = pathEl.getAttribute('data-path')
                            || (pathEl.textContent || '').trim();
                    }
                    if (!method && !opPath) return;

                    // Current module/spec from the hash (#spec=<name>).
                    var spec = '';
                    try {
                        var sm = (location.hash || '').match(/[#&]spec=([^&]+)/);
                        if (sm) spec = decodeURIComponent(sm[1]);
                    } catch (_) { /* noop */ }

                    // De-dupe repeated expand/collapse clicks on the same op.
                    var key = method + ' ' + spec + ' ' + opPath;
                    if (key === _lastOpKey) return;
                    _lastOpKey = key;

                    if (typeof window.__iosxeTrack === 'function') {
                        window.__iosxeTrack('operation_selected', {
                            http_method: method,
                            spec: spec,
                            op_path: opPath
                        });
                    }
                } catch (_) { /* noop */ }
            }, true);
        } catch (_) { /* noop */ }
    }

    // ---------- (4c) analytics: which module's YANG tree view is opened --
    // The "View YANG Tree" button opens the standalone pyang tree page for the
    // current module in a new tab. Those generated tree pages (under releases/)
    // carry no shared script, so we record the intent here at click time — the
    // dashboard can then answer "is anyone looking at the <module> tree view"
    // (e.g. an RPC module's tree). One delegated listener; fail-silent.
    function attachTreeViewTracking() {
        try {
            document.addEventListener('click', function (ev) {
                try {
                    var t = ev.target;
                    if (!t || typeof t.closest !== 'function') return;
                    var link = t.closest('#treeLink, a[data-tree-view]');
                    if (!link) return;

                    // Module: prefer the hash spec; fall back to the tree file
                    // name in the link href (<treeBase>/<module>.html).
                    var spec = '';
                    try {
                        var sm = (location.hash || '').match(/[#&]spec=([^&]+)/);
                        if (sm) spec = decodeURIComponent(sm[1]);
                    } catch (_) { /* noop */ }
                    if (!spec) {
                        try {
                            var href = link.getAttribute('href') || '';
                            var file = href.split('/').pop() || '';
                            spec = file.replace(/\.html?$/i, '');
                        } catch (_) { /* noop */ }
                    }

                    // Model category from the swagger-<cat>-model directory.
                    var cat = '';
                    try {
                        var segs = (location.pathname || '').split('/').filter(Boolean);
                        var dir = segs.length > 1 ? segs[segs.length - 2] : '';
                        var dm = dir.match(/^swagger-(.+)-model$/);
                        if (dm) cat = dm[1];
                    } catch (_) { /* noop */ }

                    // Release from ?ver / #ver / hub global / localStorage.
                    var ver = '';
                    try {
                        ver = new URLSearchParams(location.search).get('ver') || '';
                        if (!ver) {
                            var hm = (location.hash || '').match(/[#&]ver=([^&]+)/);
                            if (hm) ver = decodeURIComponent(hm[1]);
                        }
                        if (!ver && window.__IOSXE_ACTIVE_VERSION__) ver = window.__IOSXE_ACTIVE_VERSION__;
                        if (!ver) { ver = localStorage.getItem('iosxe-active-version') || ''; }
                    } catch (_) { /* noop */ }

                    if (typeof window.__iosxeTrack === 'function') {
                        window.__iosxeTrack('tree_viewed', { spec: spec, model_category: cat, release: ver });
                    }
                } catch (_) { /* noop */ }
            }, true);
        } catch (_) { /* noop */ }
    }

    // ---------- (5) phone/tablet hamburger -----------------------------
    // viewer.css hides the sidebar at/below 768px and reveals .sidebar-toggle.
    // We inject the button + a click-out backdrop here so every viewer
    // page gets the same behaviour without touching its inline markup.
    function injectSidebarToggle() {
        var sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;
        if (document.querySelector('.sidebar-toggle')) return;
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'sidebar-toggle';
        btn.setAttribute('aria-label', 'Toggle module list');
        btn.setAttribute('aria-controls', sidebar.id || 'sidebar');
        btn.setAttribute('aria-expanded', 'false');
        btn.innerHTML = '&#9776;';   // hamburger glyph (U+2630)
        var backdrop = document.createElement('div');
        backdrop.className = 'sidebar-backdrop';
        function close() {
            sidebar.classList.remove('open');
            backdrop.style.display = 'none';
            btn.setAttribute('aria-expanded', 'false');
        }
        btn.addEventListener('click', function () {
            var open = !sidebar.classList.contains('open');
            sidebar.classList.toggle('open', open);
            backdrop.style.display = open ? 'block' : 'none';
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
        backdrop.addEventListener('click', close);
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sidebar.classList.contains('open')) close();
        });
        // Auto-close when the user picks a module on small screens.
        sidebar.addEventListener('click', function (e) {
            if (window.innerWidth > 768) return;
            if (e.target.closest('a, .module-list li, .tree-row, .tree-label')) {
                setTimeout(close, 50);
            }
        });
        document.body.appendChild(btn);
        document.body.appendChild(backdrop);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
