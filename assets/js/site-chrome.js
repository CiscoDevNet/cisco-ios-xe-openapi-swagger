/* site-chrome.js — shared cross-page UI niceties.
 * - Unifies the two legacy dark-mode mechanisms ([data-theme="dark"] + body.dark)
 * - Persists user preference via localStorage
 * - Honors prefers-color-scheme on first visit
 * - Injects a Skip-to-content link if the page doesn't have one
 * - Adds a floating theme toggle on pages that don't already render one
 * - Adds aria-labels to existing toggle controls
 *
 * Safe to load on every page. CSP: ships from 'self', no eval, no inline.
 */
(function () {
    'use strict';

    // Site-wide build identifier — surfaced in the shared footer and useful
    // when triaging cache / SW issues. Keep in sync with the SW CACHE_VERSION
    // and the round entry in CHANGELOG.md.
    var SITE_BUILD = 'v10-2026.05.23 (round 17)';

    // Share the key with legacy page-specific handlers (index-app.js, tree-compare.js)
    var STORAGE_KEY = 'theme';

    function getStoredTheme() {
        try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
    }
    function setStoredTheme(v) {
        try { localStorage.setItem(STORAGE_KEY, v); } catch (e) { /* ignore */ }
    }

    function currentTheme() {
        var stored = getStoredTheme();
        if (stored === 'dark' || stored === 'light') return stored;
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
        return 'light';
    }

    function applyTheme(theme) {
        var dark = theme === 'dark';
        // Legacy mechanism #1: data-theme attribute on <html>
        document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
        // Legacy mechanism #2: body.dark class
        if (document.body) {
            document.body.classList.toggle('dark', dark);
        }
        // Update any toggle buttons
        document.querySelectorAll('[data-theme-toggle], .dark-mode-toggle, .theme-toggle').forEach(function (btn) {
            btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
            btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
            // If the existing button uses emoji text, swap it
            var txt = btn.textContent.trim();
            if (txt === '🌙' || txt === '☀️' || txt === '') {
                btn.textContent = dark ? '☀️' : '🌙';
            }
        });
    }

    function toggleTheme() {
        var next = currentTheme() === 'dark' ? 'light' : 'dark';
        setStoredTheme(next);
        applyTheme(next);
    }
    // Expose for any inline handlers / existing toggles that look for window.toggleTheme
    window.toggleTheme = toggleTheme;
    window.toggleDarkMode = toggleTheme;

    function ensureSkipLink() {
        if (document.querySelector('.skip-link')) return;
        // Find a likely main landmark
        var target = document.querySelector('main, [role="main"], #main, .content, .container');
        if (!target) return;
        if (!target.id) target.id = 'main-content';
        var skip = document.createElement('a');
        skip.className = 'skip-link';
        skip.href = '#' + target.id;
        skip.textContent = 'Skip to content';
        document.body.insertBefore(skip, document.body.firstChild);
    }

    function ensureToggle() {
        // Only inject if no existing toggle is present
        if (document.querySelector('[data-theme-toggle], .dark-mode-toggle, .theme-toggle')) return;
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'theme-toggle';
        btn.setAttribute('data-theme-toggle', '');
        btn.addEventListener('click', toggleTheme);
        document.body.appendChild(btn);
    }

    function wireExistingToggles() {
        document.querySelectorAll('.dark-mode-toggle, .theme-toggle, [data-theme-toggle]').forEach(function (btn) {
            // Avoid double-binding: tag once-handled buttons
            if (btn.dataset.themeBound) return;
            btn.dataset.themeBound = '1';
            btn.addEventListener('click', function (e) {
                // Prevent page-specific handlers from also firing duplicate toggles
                e.stopImmediatePropagation();
                e.preventDefault();
                toggleTheme();
            }, true);
        });
    }

    // Apply ASAP to prevent flash; run again after DOM ready for body.dark + chrome injection
    applyTheme(currentTheme());

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        applyTheme(currentTheme());
        ensureSkipLink();
        ensureToggle();
        wireExistingToggles();
        decorateVersionLabels();
        installShortcutHelp();
        installBackToTop();
        installFooter();
        installPwaInstallPrompt();
    }

    // === PWA install prompt =============================================
    // Listens for `beforeinstallprompt` and surfaces a small, dismissable
    // toast offering "Install app". The toast remembers a per-user "no
    // thanks" choice in localStorage for 30 days so it doesn't nag.
    // Opt-out: set <body data-pwa-prompt="off">.
    function installPwaInstallPrompt() {
        if (!document.body) return;
        if (document.body.getAttribute('data-pwa-prompt') === 'off') return;
        var DISMISS_KEY = 'iosxe-pwa-dismissed-until';
        try {
            var until = parseInt(localStorage.getItem(DISMISS_KEY) || '0', 10);
            if (until && Date.now() < until) return;
        } catch (_) { /* storage disabled — proceed */ }
        var deferred = null;
        window.addEventListener('beforeinstallprompt', function (e) {
            // Prevent the default mini-infobar; we'll surface our own UI.
            e.preventDefault();
            deferred = e;
            showPwaToast();
        });
        // If the user has already installed, never prompt again.
        window.addEventListener('appinstalled', function () {
            try { localStorage.setItem(DISMISS_KEY, String(Date.now() + 365 * 24 * 3600 * 1000)); } catch (_) {}
            dismissPwaToast();
        });

        function showPwaToast() {
            if (document.getElementById('iosxe-pwa-toast')) return;
            var t = document.createElement('div');
            t.id = 'iosxe-pwa-toast';
            t.setAttribute('role', 'dialog');
            t.setAttribute('aria-live', 'polite');
            t.setAttribute('aria-label', 'Install this site as an app');
            t.className = 'pwa-install-toast';
            t.innerHTML =
                '<div class="pwa-install-text">' +
                    '<strong>Install this site?</strong><br>' +
                    '<span>Open offline-ready, faster startup, dedicated window.</span>' +
                '</div>' +
                '<div class="pwa-install-actions">' +
                    '<button type="button" class="pwa-install-btn" data-pwa="install">Install</button>' +
                    '<button type="button" class="pwa-install-btn pwa-install-secondary" data-pwa="dismiss">Not now</button>' +
                '</div>';
            document.body.appendChild(t);
            t.querySelector('[data-pwa="install"]').addEventListener('click', function () {
                if (!deferred) { dismissPwaToast(); return; }
                deferred.prompt();
                deferred.userChoice.then(function (choice) {
                    if (choice && choice.outcome === 'dismissed') {
                        // 7-day cooldown if they tap Install but back out.
                        try { localStorage.setItem(DISMISS_KEY, String(Date.now() + 7 * 24 * 3600 * 1000)); } catch (_) {}
                    }
                    deferred = null;
                    dismissPwaToast();
                });
            });
            t.querySelector('[data-pwa="dismiss"]').addEventListener('click', function () {
                // 30-day "not now".
                try { localStorage.setItem(DISMISS_KEY, String(Date.now() + 30 * 24 * 3600 * 1000)); } catch (_) {}
                dismissPwaToast();
            });
        }
        function dismissPwaToast() {
            var t = document.getElementById('iosxe-pwa-toast');
            if (t && t.parentNode) t.parentNode.removeChild(t);
        }
    }

    // === Shared footer ===========================================
    // Injects a minimal footer with the SITE_BUILD identifier + key
    // navigation links. Pages may suppress it with
    // <body data-footer="off"> (used on Swagger UI viewers that have
    // their own scroll containers).
    function installFooter() {
        if (!document.body) return;
        if (document.body.getAttribute('data-footer') === 'off') return;
        if (document.querySelector('.site-footer')) return;
        // Resolve "home" relative to current path so subdir viewers link
        // back to the hub correctly.
        var depth = (window.location.pathname.split('/').filter(Boolean).length - 1);
        // GH Pages serves the site under a /<repo>/ prefix in production;
        // count the path segment that names the page as well.
        var here = window.location.pathname.replace(/\/+$/, '');
        var isSubdir = /\/swagger-[a-z-]+-model$/.test(here.replace(/\/index\.html$/, ''));
        var prefix = isSubdir ? '../' : '';
        var year = new Date().getFullYear();
        var f = document.createElement('footer');
        f.className = 'site-footer';
        f.setAttribute('role', 'contentinfo');
        f.innerHTML =
            '<div class="site-footer-inner">' +
                '<div class="site-footer-links">' +
                    '<a href="' + prefix + 'index.html">Home</a>' +
                    ' <span class="site-footer-sep">\u00b7</span> ' +
                    '<a href="' + prefix + 'about.html">About</a>' +
                    ' <span class="site-footer-sep">\u00b7</span> ' +
                    '<a href="' + prefix + 'yang-accountability.html">Accountability</a>' +
                    ' <span class="site-footer-sep">\u00b7</span> ' +
                    '<a href="' + prefix + 'tree-compare.html">Compare</a>' +
                    ' <span class="site-footer-sep">\u00b7</span> ' +
                    '<a href="' + prefix + 'exports.html">Exports</a>' +
                    ' <span class="site-footer-sep">\u00b7</span> ' +
                    '<a href="https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger/issues/new" target="_blank" rel="noopener noreferrer">Open an issue</a>' +
                    ' <span class="site-footer-sep">\u00b7</span> ' +
                    '<a href="' + prefix + 'CHANGELOG.md">Changelog</a>' +
                '</div>' +
                '<div class="site-footer-meta">' +
                    '<span>Cisco IOS-XE OpenAPI / YANG Explorer</span>' +
                    ' <span class="site-footer-sep">\u00b7</span> ' +
                    '<a class="site-footer-build" href="' + prefix + 'CHANGELOG.md#unreleased" title="View what changed in this build">Build ' + escapeHtml(SITE_BUILD) + '</a>' +
                    ' <span class="site-footer-sep">\u00b7</span> ' +
                    '<span>\u00a9 ' + year + ' Cisco Systems</span>' +
                '</div>' +
            '</div>';
        document.body.appendChild(f);
    }

    // === Back-to-top floating button ====================================
    // Appears after the user scrolls past ~400px. Opt-out: pages may set
    // <body data-back-to-top="off"> to suppress (useful on Swagger UI viewers
    // that have their own scroll containers).
    function installBackToTop() {
        if (!document.body) return;
        if (document.body.getAttribute('data-back-to-top') === 'off') return;
        if (document.querySelector('.back-to-top')) return;
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'back-to-top';
        btn.setAttribute('aria-label', 'Back to top');
        btn.setAttribute('title', 'Back to top');
        btn.innerHTML = '\u2191';
        btn.addEventListener('click', function () {
            try { window.scrollTo({ top: 0, behavior: 'smooth' }); }
            catch (e) { window.scrollTo(0, 0); }
            // Move focus to skip-link or first heading for keyboard users
            var target = document.querySelector('#main-content, main, h1');
            if (target && typeof target.focus === 'function') {
                target.setAttribute('tabindex', '-1');
                setTimeout(function () { target.focus({ preventScroll: true }); }, 350);
            }
        });
        document.body.appendChild(btn);
        var threshold = 400;
        var ticking = false;
        function update() {
            ticking = false;
            var y = window.pageYOffset || document.documentElement.scrollTop || 0;
            btn.classList.toggle('visible', y > threshold);
        }
        window.addEventListener('scroll', function () {
            if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
        }, { passive: true });
        update();
    }

    // === Keyboard shortcut help dialog ('?' to open) ====================
    // Lists the global shortcuts that work on every page. Pages may register
    // additional shortcuts by pushing { keys:'g h', desc:'Go to hub' } onto
    // window.__SHORTCUTS before this script runs (or after — re-rendered on
    // open). Closes on Esc or backdrop click. Restores focus on close.

    var SHORTCUT_DIALOG_ID = 'kbd-help-dialog';
    var SHORTCUT_RETURN_FOCUS = null;

    function defaultShortcuts() {
        return [
            { keys: ['?'],               desc: 'Show this keyboard shortcuts help' },
            { keys: ['/', 'Ctrl', 'K'],  desc: 'Focus the search box' },
            { keys: ['Esc'],             desc: 'Close dialogs, clear search, dismiss menus' },
            { keys: ['Tab'],             desc: 'Move focus to next control' },
            { keys: ['Shift', 'Tab'],    desc: 'Move focus to previous control' },
            { keys: ['Enter'],           desc: 'Activate focused button/link or submit search' }
        ];
    }

    function allShortcuts() {
        var base = defaultShortcuts();
        var extra = Array.isArray(window.__SHORTCUTS) ? window.__SHORTCUTS : [];
        // Normalize extras: accept either keys:string or keys:array
        extra.forEach(function (s) {
            if (!s) return;
            var keys = s.keys;
            if (typeof keys === 'string') keys = keys.split(/\s+/);
            base.push({ keys: keys || [], desc: s.desc || s.description || '' });
        });
        return base;
    }

    function renderShortcutBody() {
        var rows = allShortcuts().map(function (s) {
            var kbd = (s.keys || []).map(function (k) {
                return '<kbd>' + escapeHtml(k) + '</kbd>';
            }).join('<span class="kbd-plus">+</span>');
            return '<tr><td class="kbd-cell">' + kbd + '</td><td>' + escapeHtml(s.desc) + '</td></tr>';
        }).join('');
        return '<table class="kbd-table"><tbody>' + rows + '</tbody></table>';
    }

    function escapeHtml(s) {
        return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function ensureShortcutDialog() {
        var dlg = document.getElementById(SHORTCUT_DIALOG_ID);
        if (dlg) return dlg;
        injectShortcutStyles();
        dlg = document.createElement('div');
        dlg.id = SHORTCUT_DIALOG_ID;
        dlg.className = 'kbd-help-backdrop';
        dlg.setAttribute('role', 'dialog');
        dlg.setAttribute('aria-modal', 'true');
        dlg.setAttribute('aria-labelledby', 'kbd-help-title');
        dlg.hidden = true;
        dlg.innerHTML =
            '<div class="kbd-help-panel" tabindex="-1">' +
                '<div class="kbd-help-header">' +
                    '<h2 id="kbd-help-title">Keyboard Shortcuts</h2>' +
                    '<button type="button" class="kbd-help-close" aria-label="Close keyboard shortcuts">\u00d7</button>' +
                '</div>' +
                '<div class="kbd-help-body"></div>' +
                '<div class="kbd-help-foot">Press <kbd>?</kbd> any time to reopen this dialog.</div>' +
            '</div>';
        document.body.appendChild(dlg);
        dlg.addEventListener('click', function (e) {
            if (e.target === dlg || e.target.classList.contains('kbd-help-close')) {
                closeShortcutHelp();
            }
        });
        return dlg;
    }

    function injectShortcutStyles() {
        if (document.getElementById('kbd-help-styles')) return;
        var st = document.createElement('style');
        st.id = 'kbd-help-styles';
        st.textContent =
            '.kbd-help-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:99998;' +
                'display:flex;align-items:center;justify-content:center;padding:20px;}' +
            '.kbd-help-backdrop[hidden]{display:none;}' +
            '.kbd-help-panel{background:var(--c-surface-0,#fff);color:var(--c-text,#222);' +
                'border-radius:10px;max-width:520px;width:100%;max-height:80vh;overflow:auto;' +
                'box-shadow:0 12px 36px rgba(0,0,0,.35);font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;outline:none;}' +
            '[data-theme="dark"] .kbd-help-panel,body.dark .kbd-help-panel{background:#23262d;color:#e8e8e8;}' +
            '.kbd-help-header{display:flex;align-items:center;justify-content:space-between;' +
                'padding:14px 18px;border-bottom:1px solid rgba(127,127,127,.25);}' +
            '.kbd-help-header h2{margin:0;font-size:1.1rem;}' +
            '.kbd-help-close{background:transparent;border:0;color:inherit;font-size:1.6rem;line-height:1;' +
                'cursor:pointer;padding:0 6px;border-radius:4px;}' +
            '.kbd-help-close:hover,.kbd-help-close:focus{background:rgba(127,127,127,.18);outline:none;}' +
            '.kbd-help-body{padding:12px 18px;}' +
            '.kbd-help-foot{padding:10px 18px;border-top:1px solid rgba(127,127,127,.25);font-size:.82rem;opacity:.8;}' +
            '.kbd-table{width:100%;border-collapse:collapse;}' +
            '.kbd-table td{padding:6px 4px;vertical-align:middle;}' +
            '.kbd-table td.kbd-cell{width:1%;white-space:nowrap;padding-right:14px;}' +
            '.kbd-help-panel kbd{display:inline-block;min-width:1.6em;padding:2px 7px;border:1px solid rgba(127,127,127,.45);' +
                'border-bottom-width:2px;border-radius:4px;background:rgba(127,127,127,.10);' +
                'font:600 12px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;text-align:center;}' +
            '.kbd-plus{display:inline-block;margin:0 4px;opacity:.55;}';
        document.head.appendChild(st);
    }

    function openShortcutHelp() {
        var dlg = ensureShortcutDialog();
        var body = dlg.querySelector('.kbd-help-body');
        if (body) body.innerHTML = renderShortcutBody();
        SHORTCUT_RETURN_FOCUS = document.activeElement;
        dlg.hidden = false;
        var panel = dlg.querySelector('.kbd-help-panel');
        if (panel) panel.focus();
    }

    function closeShortcutHelp() {
        var dlg = document.getElementById(SHORTCUT_DIALOG_ID);
        if (!dlg || dlg.hidden) return;
        dlg.hidden = true;
        if (SHORTCUT_RETURN_FOCUS && typeof SHORTCUT_RETURN_FOCUS.focus === 'function') {
            try { SHORTCUT_RETURN_FOCUS.focus(); } catch (_) {}
        }
        SHORTCUT_RETURN_FOCUS = null;
    }

    function isTypingTarget(el) {
        if (!el) return false;
        var tag = el.tagName;
        if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true;
        if (el.isContentEditable) return true;
        return false;
    }

    function installShortcutHelp() {
        document.addEventListener('keydown', function (e) {
            // '?' opens the help dialog. On most keyboards this is Shift+/, so
            // also accept e.key === '?' or (e.shiftKey && e.key === '/').
            var isQuestion = e.key === '?' || (e.shiftKey && e.key === '/');
            if (isQuestion && !isTypingTarget(e.target)) {
                e.preventDefault();
                var dlg = document.getElementById(SHORTCUT_DIALOG_ID);
                if (dlg && !dlg.hidden) closeShortcutHelp();
                else openShortcutHelp();
                return;
            }
            if (e.key === 'Escape') {
                var d = document.getElementById(SHORTCUT_DIALOG_ID);
                if (d && !d.hidden) {
                    e.preventDefault();
                    closeShortcutHelp();
                }
            }
        });
        // Expose for programmatic open (e.g., a Help link in the nav)
        window.__openShortcutHelp = openShortcutHelp;
    }

    /**
     * Wrap any .header-version element that lives inside a header (and isn't
     * already pill-wrapped) with .version-pill, so the active IOS-XE release
     * is visually discoverable on every page.
     */
    function decorateVersionLabels() {
        var labels = document.querySelectorAll('.header, header, .site-header')
        if (!labels.length) return;
        document.querySelectorAll('.header-version').forEach(function (el) {
            // Skip if already inside a pill or hidden
            if (el.closest('.version-pill')) return;
            // Only decorate version-labels that sit inside the page hero
            var inHero = el.closest('.header, header, .site-header');
            if (!inHero) return;
            var pill = document.createElement('span');
            pill.className = 'version-pill';
            pill.title = 'Active IOS-XE release';
            el.parentNode.insertBefore(pill, el);
            pill.appendChild(el);
        });
    }

    // React to OS-level theme changes if user has not chosen one
    if (window.matchMedia) {
        var mq = window.matchMedia('(prefers-color-scheme: dark)');
        var listener = function () { if (!getStoredTheme()) applyTheme(currentTheme()); };
        if (mq.addEventListener) mq.addEventListener('change', listener);
        else if (mq.addListener) mq.addListener(listener);
    }
})();
