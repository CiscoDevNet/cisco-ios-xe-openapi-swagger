/* notifications.js — Event & Notification capability catalog.
 *
 * Loads the cross-model notification index (releases/<ver>/notifications.json,
 * produced by generators/generate_notifications_index.py) and renders a
 * browsable, filterable catalog of every YANG notification across all models.
 *
 * Version-aware: honours ?ver= / #ver= / localStorage, falling back to the
 * default release from releases/index.json. CSP-safe (external file, no eval).
 */
(function () {
    'use strict';

    var statusEl = document.getElementById('status');
    var catalogEl = document.getElementById('catalog');
    var summaryEl = document.getElementById('summaryGrid');
    var releaseSel = document.getElementById('releaseSel');
    var filterEl = document.getElementById('filter');
    var transportSel = document.getElementById('transportSel');
    var catSel = document.getElementById('catSel');
    var modSel = document.getElementById('modSel');
    var modFilter = document.getElementById('modFilter');
    var consumableOnly = document.getElementById('consumableOnly');
    var exportBtn = document.getElementById('exportBtn');
    var copyLinkBtn = document.getElementById('nCopyLinkBtn');

    var current = null;      // loaded index document
    var defaultVer = null;
    var _pending = null;     // deep-link category/module to apply once loaded

    // --- Deep-link hash (shareable URLs) ---------------------------------------
    // This pane owns the hash keys q, ntransport, ncat, nmod (+ shared ver/tab);
    // the Telemetry XPaths pane owns cat/mod/xpath/xport. _writeHash preserves
    // keys it does not own so the two panes never clobber each other.
    function _readHash() {
        var out = {};
        var h = (location.hash || '').replace(/^#/, '');
        h.split('&').forEach(function (kv) {
            if (!kv) return;
            var i = kv.indexOf('=');
            var k = i < 0 ? kv : kv.slice(0, i);
            var v = i < 0 ? '' : kv.slice(i + 1);
            if (k) { try { out[k] = decodeURIComponent(v); } catch (_) { out[k] = v; } }
        });
        return out;
    }
    function _writeHash(updates) {
        try {
            var cur = _readHash();
            Object.keys(updates).forEach(function (k) {
                var v = updates[k];
                if (v == null || v === '') delete cur[k];
                else cur[k] = v;
            });
            var s = Object.keys(cur).map(function (k) {
                return k + '=' + encodeURIComponent(cur[k]);
            }).join('&');
            history.replaceState(null, '', location.pathname + location.search + (s ? '#' + s : ''));
        } catch (_) { /* noop */ }
    }

    function setStatus(msg, err) {
        statusEl.textContent = msg || '';
        statusEl.className = err ? 'error' : '';
        statusEl.style.display = msg ? 'block' : 'none';
    }

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // ---- version resolution: ?ver / #ver / localStorage / default ----------
    function detectVer() {
        try {
            var q = new URLSearchParams(location.search).get('ver');
            if (q) return q;
            var m = (location.hash || '').match(/[#&]ver=([^&]+)/);
            if (m) return decodeURIComponent(m[1]);
            var s = localStorage.getItem('iosxe-active-version');
            if (s) return s;
        } catch (_) { /* noop */ }
        return defaultVer;
    }

    function notifUrl(ver) {
        return 'releases/' + encodeURIComponent(ver) + '/notifications.json';
    }

    function loadRelease(ver) {
        setStatus('Loading notifications for ' + ver + '…');
        catalogEl.innerHTML = '';
        return fetch(notifUrl(ver), { cache: 'default' })
            .then(function (r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function (doc) {
                current = doc;
                try { localStorage.setItem('iosxe-active-version', ver); } catch (_) {}
                populateCategoryFilter(doc);
                populateModuleSelect('');
                // Deep-link restore: category + module options now exist.
                if (_pending) {
                    if (_pending.ncat) catSel.value = _pending.ncat;
                    if (_pending.nmod && modSel) {
                        var ok = Array.prototype.some.call(modSel.options, function (o) { return o.value === _pending.nmod; });
                        if (ok) modSel.value = _pending.nmod;
                    }
                    _pending = null;
                }
                renderSummary(doc);
                render();
                setStatus('');
                track('notifications_release_loaded', { release: ver });
            })
            .catch(function (e) {
                setStatus('Failed to load notifications for ' + ver + ': ' + e.message, true);
            });
    }

    function populateCategoryFilter(doc) {
        var cats = {};
        doc.modules.forEach(function (m) { cats[m.display_category] = m.category; });
        // Keep current selection if still valid.
        var prev = catSel.value;
        catSel.innerHTML = '<option value="">(all)</option>';
        Object.keys(cats).sort().forEach(function (label) {
            var opt = document.createElement('option');
            opt.value = cats[label];
            opt.textContent = label;
            catSel.appendChild(opt);
        });
        if (prev) catSel.value = prev;
    }

    // Module picker, mirroring the Telemetry XPaths tab: type in modFilter to
    // live-narrow the dropdown, or choose a module to focus the catalog on it.
    function populateModuleSelect(filter) {
        if (!modSel) return;
        var prev = modSel.value;
        var names = {};
        ((current && current.modules) || []).forEach(function (m) { names[m.module] = 1; });
        var all = Object.keys(names).sort();
        var q = (filter || '').trim().toLowerCase();
        var shown = q
            ? all.filter(function (n) { return n.toLowerCase().indexOf(q) !== -1; })
            : all;
        modSel.innerHTML = '';
        var ph = document.createElement('option');
        ph.value = '';
        ph.textContent = q
            ? '(' + shown.length + ' of ' + all.length + ' modules)'
            : '(all modules)';
        modSel.appendChild(ph);
        shown.forEach(function (n) {
            var o = document.createElement('option');
            o.value = n; o.textContent = n;
            modSel.appendChild(o);
        });
        // Preserve the focused module when it still matches the filter.
        if (prev && shown.indexOf(prev) !== -1) modSel.value = prev;
    }

    function renderSummary(doc) {
        var t = doc.totals || {};
        var bt = t.by_transport || {};
        var cards = [
            { num: t.modules_with_notifications || 0, lbl: 'Modules' },
            { num: t.total_notifications || 0, lbl: 'Notifications' },
            { num: bt['yang-push'] || 0, lbl: 'YANG-Push' },
            { num: bt['snmp-trap'] || 0, lbl: 'SNMP traps' },
            { num: bt['netconf-stream'] || 0, lbl: 'NETCONF streams' }
        ];
        summaryEl.innerHTML = cards.map(function (c) {
            return '<div class="summary-card"><div class="num">' + c.num +
                '</div><div class="lbl">' + esc(c.lbl) + '</div></div>';
        }).join('');
    }

    function moduleMatches(mod, q, transport, cat, consume) {
        if (transport && mod.transport !== transport) return false;
        if (cat && mod.category !== cat) return false;
        if (consume && !mod.restconf_consumable) return false;
        if (!q) return true;
        if (mod.module.toLowerCase().indexOf(q) >= 0) return true;
        // Match against any notification name too.
        return mod.notifications.some(function (n) {
            return n.name.toLowerCase().indexOf(q) >= 0;
        });
    }

    function filteredModules() {
        if (!current) return [];
        var q = (filterEl.value || '').trim().toLowerCase();
        var transport = transportSel.value || '';
        var cat = catSel.value || '';
        var selMod = (modSel && modSel.value) || '';
        var consume = !!consumableOnly.checked;
        return current.modules.filter(function (m) {
            if (selMod && m.module !== selMod) return false;
            return moduleMatches(m, q, transport, cat, consume);
        });
    }

    function objHtml(obj) {
        var s = '<span class="objn">' + esc(obj.name) + '</span>';
        if (obj.target) {
            s += ' <span class="tgt">\u2192 ' + esc(obj.target) + '</span>';
        } else if (obj.type) {
            s += ' <span class="objt">' + esc(obj.type) + '</span>';
        }
        return s;
    }

    function notifHtml(n, q) {
        var objs = (n.objects || []);
        var objList = objs.length
            ? '<ul class="obj-list">' + objs.map(function (o) {
                  return '<li>' + objHtml(o) + '</li>';
              }).join('') + '</ul>'
            : '<div class="obj-list" style="padding-left:0;font-style:italic;">no carried objects</div>';
        var example = '';
        if (n.example) {
            var pretty = JSON.stringify(n.example, null, 2);
            example = '<div class="notif-example">'
                + '<div class="ex-head">Example payload (RFC 7951 JSON)'
                + '<button type="button" class="ex-copy" data-copy="' + esc(pretty) + '">Copy</button>'
                + '</div><pre>' + esc(pretty) + '</pre></div>';
        }
        return '<li><span class="notif-name">' + esc(n.name) + '</span>'
            + objList + example + '</li>';
    }

    // Individual YANG tree pages live under releases/<ver>/yang-trees/, but the
    // notifications index stores them as bare "yang-trees/<mod>.html" (which
    // 404s from the site root). Prefix the release the loaded catalog belongs
    // to (current.version) so the Tree links resolve.
    function resolveTreeUrl(url) {
        if (!url || !/^yang-trees\//.test(url)) return url;
        var ver = current && current.version;
        return ver ? 'releases/' + encodeURIComponent(ver) + '/' + url : url;
    }

    function moduleHtml(mod, q) {
        var consumeBadge = mod.restconf_consumable
            ? '<span class="badge consume-yes" title="Subscribable via NETCONF / gRPC dial-out">RESTCONF \u2715 · NETCONF \u2713</span>'
            : '<span class="badge consume-no" title="Not RESTCONF-subscribable">RESTCONF \u2715</span>';
        var links = '';
        if (mod.spec_url) links += '<a href="' + esc(mod.spec_url) + '">Spec</a>';
        var treeUrl = resolveTreeUrl(mod.tree_url);
        if (treeUrl) links += '<a class="tree" href="' + esc(treeUrl) + '" target="_blank" rel="noopener noreferrer">Tree</a>';
        var head = '<div class="mod-head">'
            + '<span class="mod-name">' + esc(mod.module) + '</span>'
            + '<span class="badge cat">' + esc(mod.display_category) + '</span>'
            + '<span class="badge transport-' + esc(mod.transport) + '">' + esc(mod.transport) + '</span>'
            + consumeBadge
            + '<span class="count">' + mod.notification_count + ' notification'
            + (mod.notification_count === 1 ? '' : 's') + '</span>'
            + '<span class="links">' + links + '</span>'
            + '</div>';
        var consume = mod.consumption
            ? '<div class="mod-consume"><strong>How to consume:</strong> ' + esc(mod.consumption) + '</div>'
            : '';
        var body = '<ul class="notif-list">'
            + mod.notifications.map(function (n) { return notifHtml(n, q); }).join('')
            + '</ul>';
        return '<div class="mod-card">' + head + consume + body + '</div>';
    }

    function render() {
        var mods = filteredModules();
        if (!mods.length) {
            catalogEl.innerHTML = '<div class="empty">No modules match the current filters.</div>';
            return;
        }
        var q = (filterEl.value || '').trim().toLowerCase();
        catalogEl.innerHTML = mods.map(function (m) { return moduleHtml(m, q); }).join('');
        // Wire copy buttons (CSP-safe: no inline handlers).
        var btns = catalogEl.querySelectorAll('.ex-copy');
        for (var i = 0; i < btns.length; i++) {
            btns[i].addEventListener('click', onCopyExample);
        }
    }

    function onCopyExample(ev) {
        var btn = ev.currentTarget;
        var text = btn.getAttribute('data-copy') || '';
        var done = function () {
            var orig = btn.textContent;
            btn.textContent = 'Copied \u2713';
            setTimeout(function () { btn.textContent = orig; }, 1500);
        };
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(done, function () {});
            }
        } catch (_) { /* noop */ }
        track('notification_example_copied', { release: current && current.version });
    }

    function exportCsv() {
        if (!current) return;
        var rows = [['module', 'category', 'transport', 'restconf_consumable',
                     'notification', 'object', 'object_type', 'leafref_target']];
        filteredModules().forEach(function (m) {
            m.notifications.forEach(function (n) {
                if (!n.objects || !n.objects.length) {
                    rows.push([m.module, m.category, m.transport, m.restconf_consumable,
                               n.name, '', '', '']);
                    return;
                }
                n.objects.forEach(function (o) {
                    rows.push([m.module, m.category, m.transport, m.restconf_consumable,
                               n.name, o.name, o.type || '', o.target || '']);
                });
            });
        });
        var csv = rows.map(function (r) {
            return r.map(function (c) {
                var s = String(c == null ? '' : c);
                return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
            }).join(',');
        }).join('\n');
        var blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'notifications-' + (current.version || 'release') + '.csv';
        document.body.appendChild(a); a.click();
        setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 100);
        track('notifications_csv_exported', { release: current.version });
        try {
            if (window.analytics) window.analytics.trackExportResults({
                export_type: 'notifications_csv', release: current.version,
                result: 'success', page_or_section: 'notifications'
            });
        } catch (_) { /* noop */ }
    }

    function track(name, data) {
        try { if (typeof window.__iosxeTrack === 'function') window.__iosxeTrack(name, data); }
        catch (_) { /* noop */ }
    }

    // Pre-fill the text filter from ?q= / #q= so other pages (e.g. the Swagger
    // viewers' per-module notifications panel) can deep-link straight to a
    // module's notifications.
    function initialFilter() {
        try {
            var q = new URLSearchParams(location.search).get('q');
            if (q) return q;
            var m = (location.hash || '').match(/[#&]q=([^&]+)/);
            if (m) return decodeURIComponent(m[1]);
        } catch (_) { /* noop */ }
        return '';
    }

    function init() {
        fetch('releases/index.json', { cache: 'no-store' })
            .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(function (idx) {
                defaultVer = idx.default;
                var want = detectVer();
                var versions = (idx.releases || []).map(function (r) { return r.ver; });
                if (versions.indexOf(want) < 0) want = defaultVer;
                versions.forEach(function (v) {
                    var opt = document.createElement('option');
                    opt.value = v; opt.textContent = v;
                    if (v === want) opt.selected = true;
                    releaseSel.appendChild(opt);
                });
                var pre = initialFilter();
                if (pre) filterEl.value = pre;
                // Deep-link restore: transport (static options) now; category /
                // module are staged for after the release doc loads.
                var hp = _readHash();
                if (hp.ntransport && transportSel) {
                    var tok = Array.prototype.some.call(transportSel.options, function (o) { return o.value === hp.ntransport; });
                    if (tok) transportSel.value = hp.ntransport;
                }
                if (hp.ncat || hp.nmod) _pending = { ncat: hp.ncat || null, nmod: hp.nmod || null };
                releaseSel.addEventListener('change', function () {
                    _writeHash({ ver: releaseSel.value, ncat: null, nmod: null });
                    loadRelease(releaseSel.value);
                });
                filterEl.addEventListener('input', function () { _writeHash({ q: filterEl.value }); render(); });
                transportSel.addEventListener('change', function () { _writeHash({ ntransport: transportSel.value }); render(); });
                catSel.addEventListener('change', function () { _writeHash({ ncat: catSel.value, nmod: null }); render(); });
                if (modFilter) modFilter.addEventListener('input', function () { populateModuleSelect(modFilter.value); });
                if (modSel) modSel.addEventListener('change', function () {
                    _writeHash({ nmod: modSel.value });
                    render();
                    try {
                        if (window.analytics && modSel.value) window.analytics.trackDataModelSelected({
                            yang_model: modSel.value, release: current && current.version,
                            page_or_section: 'notifications'
                        });
                    } catch (_) { /* noop */ }
                });
                consumableOnly.addEventListener('change', render);
                exportBtn.addEventListener('click', exportCsv);
                if (copyLinkBtn) copyLinkBtn.addEventListener('click', function () {
                    var prevTxt = copyLinkBtn.textContent;
                    function done() { copyLinkBtn.textContent = 'Copied!'; setTimeout(function () { copyLinkBtn.textContent = prevTxt; }, 1200); }
                    try {
                        if (navigator.clipboard && navigator.clipboard.writeText) {
                            navigator.clipboard.writeText(location.href).then(done, done);
                        } else { done(); }
                    } catch (_) { done(); }
                    track('notifications_link_copied', {
                        release: current && current.version,
                        transport: transportSel && transportSel.value,
                        yang_model: modSel && modSel.value
                    });
                });
                loadRelease(want);
            })
            .catch(function (e) {
                setStatus('Failed to load release index: ' + e.message, true);
            });
    }

    init();
})();
