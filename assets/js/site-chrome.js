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
    }

    // React to OS-level theme changes if user has not chosen one
    if (window.matchMedia) {
        var mq = window.matchMedia('(prefers-color-scheme: dark)');
        var listener = function () { if (!getStoredTheme()) applyTheme(currentTheme()); };
        if (mq.addEventListener) mq.addEventListener('change', listener);
        else if (mq.addListener) mq.addListener(listener);
    }
})();
