// Hub-level cross-category Operation Search
// ------------------------------------------
// Augments the universal search box on index.html with a section that surfaces
// individual API operations across all 9 viewer categories. Lazy-loads each
// category's `_paths_index.json` (built by scripts/build_paths_index.py) on
// first user query, caches in memory, and renders deep-link hits that target
// `swagger-<cat>-model/index.html#spec=<module>&op=<operationId>` (handled
// by deeplink.js in each viewer).
//
// CSP: same-origin script, no eval, no inline. Strict 'self' compatible.

(function () {
    'use strict';

    var TARGET_VER = '26.1.1';
    var CATEGORIES = ['cfg', 'events', 'ietf', 'mib', 'native-config', 'openconfig', 'oper', 'other', 'rpc'];
    var CAT_LABEL = {
        'cfg': 'Config',
        'events': 'Events',
        'ietf': 'IETF',
        'mib': 'MIB',
        'native-config': 'Native',
        'openconfig': 'OpenConfig',
        'oper': 'Operational',
        'other': 'Other',
        'rpc': 'RPC'
    };
    var METHOD_COLOR = {
        get: '#10B981', post: '#F59E0B', put: '#3B82F6',
        patch: '#8B5CF6', delete: '#EF4444', head: '#6B7280', options: '#6B7280'
    };
    var MIN_QUERY = 3;
    var DEBOUNCE_MS = 150;
    var MAX_HITS = 80;

    var indexes = null;          // per-category: {c, ops:[...]}, null until loaded
    var loadingPromise = null;
    var lastQuery = '';
    var debounceTimer = null;
    var sectionEl = null;

    function escHtml(s) {
        if (s == null) return '';
        return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function activeVersion() {
        return (typeof window !== 'undefined' && window.__IOSXE_ACTIVE_VERSION__) || TARGET_VER;
    }

    function indexUrl(cat) {
        return 'releases/' + encodeURIComponent(activeVersion())
            + '/swagger-' + cat + '-model/api/_paths_index.json';
    }

    function ensureSection() {
        if (sectionEl && document.body.contains(sectionEl)) return sectionEl;
        var host = document.getElementById('searchResults');
        if (!host || !host.parentNode) return null;
        sectionEl = document.createElement('div');
        sectionEl.id = 'globalOpsResults';
        sectionEl.className = 'search-results';
        sectionEl.style.cssText = 'margin-bottom:16px;';
        host.parentNode.insertBefore(sectionEl, host);
        return sectionEl;
    }

    function loadAll() {
        if (loadingPromise) return loadingPromise;
        loadingPromise = Promise.all(CATEGORIES.map(function (cat) {
            return fetch(indexUrl(cat))
                .then(function (r) { return r.ok ? r.json() : null; })
                .catch(function () { return null; });
        })).then(function (results) {
            indexes = results.map(function (data, i) {
                return data && Array.isArray(data.ops)
                    ? { c: CATEGORIES[i], ops: data.ops }
                    : { c: CATEGORIES[i], ops: [] };
            });
            return indexes;
        });
        return loadingPromise;
    }

    function search(q) {
        var needle = q.toLowerCase();
        var hits = [];
        for (var i = 0; i < indexes.length; i++) {
            var cat = indexes[i].c;
            var rows = indexes[i].ops;
            for (var j = 0; j < rows.length; j++) {
                var row = rows[j];
                var hay = row.p.toLowerCase();
                var matched = hay.indexOf(needle) !== -1;
                if (!matched && row.sm && row.sm.toLowerCase().indexOf(needle) !== -1) matched = true;
                if (!matched && row.kw && row.kw.indexOf(needle) !== -1) matched = true;
                if (!matched && row.ids) {
                    for (var k = 0; k < row.ids.length; k++) {
                        if (row.ids[k] && row.ids[k].toLowerCase().indexOf(needle) !== -1) { matched = true; break; }
                    }
                }
                if (matched) {
                    hits.push({ cat: cat, row: row });
                    if (hits.length >= MAX_HITS + 1) return hits;
                }
            }
        }
        return hits;
    }

    function renderEmpty() {
        var s = ensureSection();
        if (s) s.innerHTML = '';
    }

    function renderLoading(q) {
        var s = ensureSection();
        if (!s) return;
        s.innerHTML = '<div class="search-stats" style="padding:8px 12px;">'
            + 'Loading operation index for ' + escHtml(activeVersion()) + ' ...'
            + '</div>';
    }

    function renderHits(q, hits) {
        var s = ensureSection();
        if (!s) return;
        if (!hits.length) {
            s.innerHTML = '';
            return;
        }
        var truncated = hits.length > MAX_HITS;
        if (truncated) hits = hits.slice(0, MAX_HITS);

        var header = '<div class="search-stats" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
            + '<strong>Operations matching "' + escHtml(q) + '"</strong>: '
            + hits.length + (truncated ? '+' : '') + ' hit' + (hits.length !== 1 ? 's' : '')
            + (truncated ? ' (showing first ' + MAX_HITS + ')' : '')
            + ' <span style="font-size:0.78rem;color:var(--text-secondary,#888);">across all categories in '
            + escHtml(activeVersion()) + '</span>'
            + '</div>';

        var rowsHtml = hits.map(function (h) {
            var cat = h.cat, row = h.row;
            var label = escHtml(CAT_LABEL[cat] || cat);
            var pathHtml = escHtml(row.p);
            var summary = row.sm ? '<div style="font-size:0.78rem;color:var(--text-secondary,#666);margin-top:2px;">' + escHtml(row.sm) + '</div>' : '';

            var methods = (row.ms || []).map(function (m, i) {
                var opId = (row.ids && row.ids[i]) || '';
                var color = METHOD_COLOR[m] || '#6B7280';
                var url = 'swagger-' + cat + '-model/index.html#spec='
                    + encodeURIComponent(row.s)
                    + (opId ? '&op=' + encodeURIComponent(opId) : '');
                return '<a href="' + escHtml(url) + '" '
                    + 'style="display:inline-block;padding:1px 8px;margin-right:4px;border-radius:4px;'
                    + 'background:' + color + ';color:#fff;font-size:0.72rem;font-weight:600;'
                    + 'text-decoration:none;letter-spacing:0.04em;" '
                    + 'title="Open ' + escHtml(opId || row.p) + '">'
                    + m.toUpperCase() + '</a>';
            }).join('');

            return '<div class="search-result-card" style="border-left-color:#1565C0;padding:8px 12px;">'
                + '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
                + '<span class="search-result-badge" style="background:#E3F2FD;color:#0D47A1;">'
                + label + '</span>'
                + '<span style="font-size:0.8rem;color:var(--text-secondary,#666);">' + escHtml(row.s) + '</span>'
                + methods
                + '</div>'
                + '<div style="font-family:ui-monospace,Consolas,monospace;font-size:0.82rem;margin-top:4px;word-break:break-all;">'
                + pathHtml + '</div>'
                + summary
                + '</div>';
        }).join('');

        s.innerHTML = header + rowsHtml;
    }

    function runQuery(q) {
        if (!q || q.length < MIN_QUERY) {
            renderEmpty();
            return;
        }
        if (indexes === null) {
            renderLoading(q);
            loadAll().then(function () {
                if (lastQuery === q) renderHits(q, search(q));
            });
            return;
        }
        renderHits(q, search(q));
    }

    function onInput(e) {
        var q = (e && e.target ? e.target.value : '').trim();
        lastQuery = q;
        if (debounceTimer) clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function () { runQuery(q); }, DEBOUNCE_MS);
    }

    function init() {
        var input = document.getElementById('universalSearch');
        if (!input) return;
        input.addEventListener('input', onInput);
        // If the box already has a value (e.g., restored from URL), kick once.
        if (input.value && input.value.trim().length >= MIN_QUERY) {
            lastQuery = input.value.trim();
            runQuery(lastQuery);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
