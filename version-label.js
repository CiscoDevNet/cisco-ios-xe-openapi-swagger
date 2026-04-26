/* version-label.js — small bootstrap shared by top-level pages without
 * a full version selector (tree-compare, yang-accountability, etc).
 *
 * Reads the active IOS-XE release from ?ver= / #ver= / localStorage and
 * rewrites:
 *   - every element with class .header-version (textContent → version)
 *   - document.title (regex replace of "Cisco IOS-XE <ver>" or
 *     "IOS-XE <ver>" — keeps the rest of the title intact)
 *
 * Falls back silently to the static text already in the HTML if no version
 * is detectable. CSP-safe: external file, no eval.
 */
(function () {
    'use strict';

    function detectVer() {
        try {
            var qs = new URLSearchParams(location.search);
            if (qs.get('ver')) return qs.get('ver');
            var hm = location.hash.match(/[#&]ver=([^&]+)/);
            if (hm) return decodeURIComponent(hm[1]);
            var stored = localStorage.getItem('iosxe-active-version');
            if (stored) return stored;
        } catch (_) { /* noop */ }
        return null;
    }

    function applyHeaderVersion() {
        var v = detectVer();
        if (!v) return;
        try {
            document.querySelectorAll('.header-version').forEach(function (el) {
                el.textContent = v;
            });
            if (document.title) {
                document.title = document.title.replace(
                    /IOS-XE [0-9.x]+/, 'IOS-XE ' + v);
            }
        } catch (_) { /* noop */ }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyHeaderVersion);
    } else {
        applyHeaderVersion();
    }
})();
