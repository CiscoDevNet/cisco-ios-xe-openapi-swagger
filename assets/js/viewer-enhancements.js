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
        label.textContent = 'Switch IOS-XE release';
        var sel = document.createElement('select');
        sel.id = 'viewerVersionPicker';
        sel.title = 'Switch IOS-XE release (preserves current spec & operation)';
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
