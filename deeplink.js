/* deeplink.js — shared deep-link helper for the swagger-*-model/index-v2.html viewers.
 *
 * Hash format: #spec=<module-name>&op=<operationId>
 *   - spec=<module-name>  → which OpenAPI spec to load (existing behavior)
 *   - op=<operationId>    → optional; expand & scroll to that operation row
 *
 * Public API (window.__DeepLink):
 *   parseHash() → { spec?, op?, ver? }
 *   setSpec(name)        → updates hash to #spec=<name> (drops op)
 *   setSpecOp(name, op)  → updates hash to #spec=<name>&op=<op>
 *   tryExpandOp(opId)    → expands a Swagger UI operation row by id (idempotent)
 *
 * Behavior added at load:
 *   - MutationObserver on #swagger-ui auto-expands an `op=` target when Swagger
 *     UI finishes rendering.
 *   - Click delegate on `.opblock-summary` updates the hash to include the
 *     clicked op's operationId so users can copy a deep link.
 *
 * NOTE: viewer scripts must call __DeepLink.setSpec() instead of writing
 * window.location.hash directly so the op= param is preserved when present.
 */
(function () {
    'use strict';

    function parseHash() {
        var raw = (window.location.hash || '').replace(/^#/, '');
        if (!raw) return {};
        var out = {};
        var segs = raw.split('&');
        for (var i = 0; i < segs.length; i++) {
            var seg = segs[i];
            var eq = seg.indexOf('=');
            if (eq <= 0) continue;
            var k = seg.substring(0, eq);
            var v = seg.substring(eq + 1);
            try { v = decodeURIComponent(v); } catch (_) { /* keep raw */ }
            out[k] = v;
        }
        return out;
    }

    function buildHash(params) {
        var keys = ['ver', 'spec', 'op']; // stable order
        var parts = [];
        for (var i = 0; i < keys.length; i++) {
            var k = keys[i];
            var v = params[k];
            if (v == null || v === '') continue;
            parts.push(k + '=' + encodeURIComponent(v));
        }
        // any extra params not in the canonical list
        for (var k2 in params) {
            if (keys.indexOf(k2) !== -1) continue;
            if (!Object.prototype.hasOwnProperty.call(params, k2)) continue;
            var v2 = params[k2];
            if (v2 == null || v2 === '') continue;
            parts.push(k2 + '=' + encodeURIComponent(v2));
        }
        return parts.length ? '#' + parts.join('&') : '';
    }

    function writeHash(newHash) {
        if (window.location.hash === newHash) return;
        if (window.history && typeof window.history.replaceState === 'function') {
            // replaceState avoids triggering a hashchange event (which would
            // re-enter checkHash and reload the spec).
            window.history.replaceState(null, '', newHash || window.location.pathname + window.location.search);
        } else {
            window.location.hash = newHash;
        }
    }

    function setSpec(name) {
        if (!name) return;
        // Changing spec drops op (operations are spec-scoped).
        var cur = parseHash();
        var next = { spec: name };
        if (cur.ver) next.ver = cur.ver;
        writeHash(buildHash(next));
    }

    function setSpecOp(name, op) {
        if (!name) return;
        var cur = parseHash();
        var next = { spec: name, op: op || undefined };
        if (cur.ver) next.ver = cur.ver;
        writeHash(buildHash(next));
    }

    /** Find the Swagger UI .opblock element for the given operationId. */
    function findOpElement(opId) {
        if (!opId) return null;
        var ui = document.getElementById('swagger-ui');
        if (!ui) return null;
        // Swagger UI renders rows as id="operations-<tag>-<operationId>".
        // Tag may contain hyphens; match suffix robustly.
        var nodes = ui.querySelectorAll('div.opblock[id^="operations-"]');
        for (var i = 0; i < nodes.length; i++) {
            var n = nodes[i];
            // Strip leading "operations-" then look for the last "-<op>" segment.
            var rest = n.id.substring('operations-'.length);
            // Could be "<tag>-<op>" — exact suffix match (tag may have hyphens too,
            // so we check that rest ENDS with -opId or equals opId).
            if (rest === opId || rest.length > opId.length + 1
                && rest.substring(rest.length - opId.length - 1) === ('-' + opId)) {
                return n;
            }
        }
        return null;
    }

    function tryExpandOp(opId) {
        var el = findOpElement(opId);
        if (!el) return false;
        var summary = el.querySelector('.opblock-summary');
        var alreadyOpen = el.classList.contains('is-open');
        if (summary && !alreadyOpen && el.getAttribute('data-deeplink-expanded') !== '1') {
            el.setAttribute('data-deeplink-expanded', '1');
            try { summary.click(); } catch (_) { /* ignore */ }
        }
        try { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (_) { /* old browser */ }
        return true;
    }

    function extractOpIdFromBlock(opblock) {
        if (!opblock || !opblock.id) return null;
        var rest = opblock.id.indexOf('operations-') === 0
            ? opblock.id.substring('operations-'.length)
            : opblock.id;
        // tag-op — operationId is the segment after the tag. We don't know tag
        // boundaries, but Swagger UI always emits "<tag>-<operationId>" with
        // operationId being the last hyphen-delimited token only when ops have
        // simple ids. Most generated specs here do, so use the last segment.
        var idx = rest.lastIndexOf('-');
        if (idx === -1) return rest;
        return rest.substring(idx + 1);
    }

    function attachAutoExpand() {
        var ui = document.getElementById('swagger-ui');
        if (!ui) return;
        var pending = parseHash().op;
        if (!pending) return;
        // Try right away in case Swagger UI already rendered.
        if (tryExpandOp(pending)) return;
        // Otherwise observe DOM mutations until the row appears.
        var attempts = 0;
        var observer = new MutationObserver(function () {
            attempts++;
            if (tryExpandOp(pending)) {
                observer.disconnect();
            } else if (attempts > 2000) {
                observer.disconnect();
            }
        });
        observer.observe(ui, { childList: true, subtree: true });
    }

    function attachClickCapture() {
        // Capture-phase listeners fire before any inline onclick handlers and
        // before the browser's default <a href="#"> navigation.
        document.addEventListener('click', function (e) {
            var target = e.target;
            if (!target || !target.closest) return;

            // (1) Sidebar module links use href="#" with onclick that should
            // return false. In some environments (programmatic click, certain
            // event timings) the default action still fires and pushes "#"
            // into history, wiping our hash. Suppress that default here.
            var sidebar = target.closest('#moduleList a, .module-list a');
            if (sidebar && (sidebar.getAttribute('href') === '#' ||
                    sidebar.getAttribute('href') === '')) {
                e.preventDefault();
                // do NOT stopPropagation — onclick="loadSpec(...)" still runs
            }

            // (2) Update hash when user clicks an opblock summary so the URL
            // bar always reflects the currently-open operation.
            var summary = target.closest('.opblock-summary');
            if (!summary) return;
            var opblock = summary.closest('.opblock');
            var opId = extractOpIdFromBlock(opblock);
            if (!opId) return;
            var cur = parseHash();
            if (!cur.spec) return;
            // setSpecOp uses replaceState — does not trigger another reload.
            setSpecOp(cur.spec, opId);
        }, true); // capture phase so we run before Swagger UI's own handlers
    }

    // Re-run auto-expand whenever the hash changes (e.g. user pastes a new
    // deep link). Spec changes are still handled by the viewer's checkHash().
    window.addEventListener('hashchange', function () {
        attachAutoExpand();
    });

    // Defensive guard: if Swagger UI (or anything else) tries to push/replace
    // a hash that drops our spec= param, merge it back in.
    (function guardHistory() {
        function preserveSpec(url) {
            // url may be null/undefined (means "current URL") — leave alone.
            if (url == null) return url;
            try {
                var u = new URL(url, window.location.href);
                var cur = parseHash();
                if (!cur.spec) return url;
                // parse incoming hash
                var newRaw = (u.hash || '').replace(/^#/, '');
                var hasSpec = /(^|&)spec=/.test(newRaw);
                if (hasSpec) return url;
                // Re-attach our spec (and op if present) so it isn't lost.
                var keep = { spec: cur.spec };
                if (cur.op) keep.op = cur.op;
                if (cur.ver) keep.ver = cur.ver;
                // If the incoming hash is empty or just "#", just use ours.
                if (!newRaw) {
                    u.hash = buildHash(keep);
                    return u.pathname + u.search + u.hash;
                }
                // Otherwise prepend our params.
                u.hash = buildHash(keep) + '&' + newRaw;
                return u.pathname + u.search + u.hash;
            } catch (_) {
                return url;
            }
        }
        var origPush = history.pushState;
        var origRepl = history.replaceState;
        history.pushState = function (s, t, u) {
            return origPush.call(this, s, t, preserveSpec(u));
        };
        history.replaceState = function (s, t, u) {
            return origRepl.call(this, s, t, preserveSpec(u));
        };
    })();

    // Initial wiring after DOM ready.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            attachClickCapture();
            attachAutoExpand();
        });
    } else {
        attachClickCapture();
        attachAutoExpand();
    }

    window.__DeepLink = {
        parseHash: parseHash,
        buildHash: buildHash,
        setSpec: setSpec,
        setSpecOp: setSpecOp,
        tryExpandOp: tryExpandOp
    };
})();
