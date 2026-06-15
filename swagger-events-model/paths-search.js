/* paths-search.js — cross-chunk operation search for the Native Config viewer.
 *
 * Runs on every active release. On older releases the script detects the version and
 * becomes a silent no-op so legacy behaviour is unchanged.
 *
 * What it does
 * ------------
 * - Fetches `_paths_index.json` (built by scripts/build_paths_index.py) once
 *   the viewer has loaded its module list.
 * - When the user types in the existing #searchBox, in addition to filtering
 *   the module list the script renders an "Operations matching" section above
 *   the module list with up to MAX_HITS path hits across all chunks.
 * - Click → loadSpec(spec) → after Swagger UI renders, scroll/expand the
 *   operation by anchoring on `#operations-<tag>-<operationId>` and using
 *   the existing __DeepLink helper if present.
 *
 * The script reads the viewer's existing globals: __activeVer(), __apiBase(),
 * __IOSXE_DEFAULT_VER__, escapeHtml, loadSpec, allModules.
 */
(function () {
    'use strict';

    var TARGET_VER = '26.1.1';
    var MAX_HITS = 60;
    var MIN_QUERY = 2;

    var __index = null;          // {v, c, n, ops:[{s,p,t,sm,ms,ids}]}
    var __indexLoading = false;
    var __indexFailed = false;

    function activeVer() {
        try { return window.__activeVer ? window.__activeVer() : window.__IOSXE_ACTIVE_VERSION__; }
        catch (_) { return null; }
    }
    function apiBase() {
        try { return window.__apiBase ? window.__apiBase() : 'api'; }
        catch (_) { return 'api'; }
    }
    function esc(s) {
        try { return window.escapeHtml(String(s == null ? '' : s)); }
        catch (_) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];
        }); }
    }

    function ensureUi() {
        // Inject a minimal style + container above #sidebarContent on first use.
        if (document.getElementById('opMatches')) return true;
        var sc = document.getElementById('sidebarContent');
        if (!sc) return false;

        var style = document.createElement('style');
        style.textContent = [
            '.op-matches { border-bottom: 1px solid #e0e0e0; background: #fffbe6; }',
            '.op-matches .om-head { padding: 8px 16px; font-size: 11px; font-weight: 600; color: #5d4037; text-transform: uppercase; letter-spacing: 0.5px; background: #fff3cd; border-bottom: 1px solid #ffe082; display: flex; justify-content: space-between; align-items: center; }',
            '.op-matches .om-head .count { font-weight: normal; color: #8d6e63; }',
            '.op-matches ul { list-style: none; max-height: 280px; overflow-y: auto; }',
            '.op-matches li { border-bottom: 1px dotted #efebe9; }',
            '.op-matches a { display: block; padding: 6px 16px; color: #333; text-decoration: none; font-size: 11px; line-height: 1.35; }',
            '.op-matches a:hover { background: #fff8e1; }',
            '.op-matches .ms { display: inline-block; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 9px; padding: 1px 4px; border-radius: 3px; background: #1565c0; color: #fff; margin-right: 4px; }',
            '.op-matches .pp { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: #1a237e; word-break: break-all; }',
            '.op-matches .pp mark { background: #ffe082; padding: 0; }',
            '.op-matches .sub { display: block; color: #757575; font-size: 10px; margin-top: 2px; }'
        ].join('\n');
        document.head.appendChild(style);

        var box = document.createElement('div');
        box.id = 'opMatches';
        box.className = 'op-matches';
        box.style.display = 'none';
        sc.parentNode.insertBefore(box, sc);
        return true;
    }

    function loadIndex() {
        if (__index || __indexLoading || __indexFailed) return;
        __indexLoading = true;
        var url = apiBase() + '/_paths_index.json';
        fetch(url, { cache: 'no-cache' })
            .then(function (r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function (data) {
                __index = data;
                __indexLoading = false;
                // Re-run any active search now that the index is here.
                if (typeof window.filterModules === 'function') {
                    try { window.filterModules(); } catch (_) {}
                }
            })
            .catch(function (err) {
                console.warn('[paths-search] index load failed:', err);
                __indexFailed = true;
                __indexLoading = false;
            });
    }

    function highlight(text, q) {
        if (!q) return esc(text);
        var idx = text.toLowerCase().indexOf(q);
        if (idx < 0) return esc(text);
        return esc(text.substring(0, idx))
             + '<mark>' + esc(text.substring(idx, idx + q.length)) + '</mark>'
             + esc(text.substring(idx + q.length));
    }

    function methodBadge(ms) {
        // Show abbreviated method list, GET first if present.
        var order = ['get','put','patch','post','delete','head','options'];
        var sorted = order.filter(function (m) { return ms.indexOf(m) >= 0; });
        var rest = ms.filter(function (m) { return order.indexOf(m) < 0; });
        return sorted.concat(rest).map(function (m) {
            return '<span class="ms">' + m.toUpperCase() + '</span>';
        }).join('');
    }

    function findHits(q) {
        if (!__index || !__index.ops) return [];
        var qq = q.toLowerCase();
        var hits = [];
        var ops = __index.ops;
        for (var i = 0; i < ops.length; i++) {
            var o = ops[i];
            // Match path, summary, tag, or any operationId.
            if (o.p.toLowerCase().indexOf(qq) >= 0
             || (o.sm && o.sm.toLowerCase().indexOf(qq) >= 0)
             || (o.t && o.t.toLowerCase().indexOf(qq) >= 0)
             || (o.kw && o.kw.indexOf(qq) >= 0)
             || (o.ids && o.ids.some(function (x) { return x && x.toLowerCase().indexOf(qq) >= 0; }))) {
                hits.push(o);
                if (hits.length >= MAX_HITS) break;
            }
        }
        return hits;
    }

    function render(q, hits) {
        var box = document.getElementById('opMatches');
        if (!box) return;
        if (!q || q.length < MIN_QUERY) {
            box.style.display = 'none';
            box.innerHTML = '';
            return;
        }
        if (!__index) {
            box.style.display = 'block';
            box.innerHTML = '<div class="om-head">Operations matching <span class="count">' + (__indexFailed ? '(index unavailable)' : 'loading…') + '</span></div>';
            return;
        }
        if (hits.length === 0) {
            box.style.display = 'none';
            box.innerHTML = '';
            return;
        }
        var total = __index.n || __index.ops.length;
        var html = '<div class="om-head">'
                 + 'Operations matching <code>' + esc(q) + '</code>'
                 + ' <span class="count">' + hits.length + (hits.length >= MAX_HITS ? '+' : '') + ' of ' + total + ' paths</span>'
                 + '</div><ul>';
        for (var i = 0; i < hits.length; i++) {
            var h = hits[i];
            var attrs = ' data-spec="' + esc(h.s) + '"'
                      + ' data-tag="'  + esc(h.t || '') + '"'
                      + ' data-opid="' + esc((h.ids && h.ids[0]) || '') + '"'
                      + ' data-method="' + esc((h.ms && h.ms[0]) || 'get') + '"';
            html += '<li><a href="#" class="op-hit"' + attrs + '>'
                  + methodBadge(h.ms || ['get'])
                  + '<span class="pp">' + highlight(h.p, q.toLowerCase()) + '</span>'
                  + '<span class="sub">' + esc(h.s) + (h.sm ? ' — ' + esc(h.sm) : '') + '</span>'
                  + '</a></li>';
        }
        html += '</ul>';
        box.innerHTML = html;
        box.style.display = 'block';

        // Wire click handlers.
        var anchors = box.querySelectorAll('a.op-hit');
        for (var j = 0; j < anchors.length; j++) {
            anchors[j].addEventListener('click', onHitClick);
        }
    }

    function onHitClick(ev) {
        ev.preventDefault();
        var a = ev.currentTarget;
        var spec   = a.getAttribute('data-spec');
        var tag    = a.getAttribute('data-tag') || '';
        var opid   = a.getAttribute('data-opid') || '';
        var method = a.getAttribute('data-method') || 'get';
        if (!spec || typeof window.loadSpec !== 'function') return;

        // Trigger the same load path the sidebar uses; re-use the spec's
        // sidebar <a> if present so the .selected highlight tracks.
        var sidebarLink = document.querySelector('.module-list a[data-module="' + (window.CSS && CSS.escape ? CSS.escape(spec) : spec) + '"]');
        try { window.loadSpec(spec, sidebarLink); }
        catch (e) { console.warn('[paths-search] loadSpec failed:', e); return; }

        // Update deep-link hash so the URL is shareable.
        if (opid && window.__DeepLink && window.__DeepLink.setSpec) {
            try {
                window.__DeepLink.setSpec(spec);
                if (window.__DeepLink.setOp) window.__DeepLink.setOp(opid);
            } catch (_) {}
        }

        // Swagger UI 5.x anchor format: "operations-<tag>-<operationId>".
        // Fall back to operationId-only if tag is missing.
        if (!opid) return;
        var anchor = tag
            ? 'operations-' + tag + '-' + opid
            : 'operations-' + opid;

        // Wait until Swagger UI has rendered the operation list, then scroll.
        var attempts = 0;
        var timer = setInterval(function () {
            attempts++;
            var el = document.getElementById(anchor)
                  || document.querySelector('[id$="-' + opid + '"]');
            if (el) {
                clearInterval(timer);
                try { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (_) {}
                // Click the operation toggle to expand it.
                var toggle = el.querySelector('.opblock-summary');
                if (toggle && el.querySelector('.opblock-body') == null) {
                    try { toggle.click(); } catch (_) {}
                }
            } else if (attempts > 40) {  // ~6s max
                clearInterval(timer);
            }
        }, 150);
    }

    // Patch into the existing search box.
    function init() {
        // Runs on every release; loadIndex() is a no-op if _paths_index.json is missing.
        if (!ensureUi()) return;
        loadIndex();

        var box = document.getElementById('searchBox');
        if (!box) return;
        // Use input + a debounce to avoid re-rendering on every keystroke.
        var t = null;
        box.addEventListener('input', function () {
            clearTimeout(t);
            t = setTimeout(function () {
                var q = (box.value || '').trim();
                if (q.length < MIN_QUERY) { render('', []); return; }
                render(q, findHits(q));
            }, 80);
        });
    }

    // Wait for the viewer to populate allModules; that's when the sidebar UI
    // exists and a search is meaningful. The viewer calls renderSidebar() on
    // load, so polling for #sidebarContent's first child is reliable.
    function waitForSidebar(retries) {
        retries = retries || 0;
        var sc = document.getElementById('sidebarContent');
        if (sc && sc.firstChild && sc.textContent.trim() !== 'Loading...') {
            init();
            return;
        }
        if (retries > 60) return;     // ~6s
        setTimeout(function () { waitForSidebar(retries + 1); }, 100);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { waitForSidebar(0); });
    } else {
        waitForSidebar(0);
    }
})();
