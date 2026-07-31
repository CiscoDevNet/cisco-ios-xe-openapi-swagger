/* live-data.js — interactive browser for real captured device responses.
 *
 * Loads the lightweight per-release index
 * (releases/<ver>/live-examples-index.json) for coverage + navigation, then
 * fetches a single per-module spec on demand to show the actual captured
 * response body. Device platforms (PIDs) are shown as tabs so the same path
 * can be compared across a C9300 / C9400 / C9500 / C9600, etc.
 *
 * CSP note: this page ships a strict CSP (no 'unsafe-inline' for scripts), so
 * all logic lives here and every DOM node is built with textContent /
 * createElement — never innerHTML — so no URL-controlled data can reach a
 * markup sink.
 */
(function () {
    'use strict';

    var MODEL_DIR = {
        oper: 'swagger-oper-model',
        cfg: 'swagger-cfg-model',
        'native-config': 'swagger-native-config-model',
        openconfig: 'swagger-openconfig-model',
        ietf: 'swagger-ietf-model',
        mib: 'swagger-mib-model',
        other: 'swagger-other-model',
        rpc: 'swagger-rpc-model'
    };
    var CAT_COLOR = {
        oper: '#2196F3', cfg: '#00BCD4', 'native-config': '#4CAF50',
        openconfig: '#009688', ietf: '#FF5722', mib: '#9C27B0',
        other: '#757575', rpc: '#FFC107'
    };
    var CAT_LABEL = {
        oper: 'Oper', cfg: 'Config', 'native-config': 'Native',
        openconfig: 'OpenConfig', ietf: 'IETF', mib: 'MIB',
        other: 'Other', rpc: 'RPC'
    };
    var LIVE_KEY = 'x-cisco-live-examples';

    var state = {
        ver: '', index: null, pid: '', cat: 'all', q: '',
        specCache: {}, sel: null, /* {cat, module, path} */
        charts: {}
    };

    // ---------- tiny DOM helper (no innerHTML) ----------
    function el(tag, opts, kids) {
        var n = document.createElement(tag);
        opts = opts || {};
        if (opts.className) n.className = opts.className;
        if (opts.text != null) n.textContent = opts.text;
        if (opts.title) n.title = opts.title;
        if (opts.href) n.setAttribute('href', opts.href);
        if (opts.style) n.style.cssText = opts.style;
        if (opts.attrs) { Object.keys(opts.attrs).forEach(function (k) { n.setAttribute(k, opts.attrs[k]); }); }
        if (opts.onclick) n.addEventListener('click', opts.onclick);
        (kids || []).forEach(function (k) { if (k) n.appendChild(k); });
        return n;
    }
    function clear(n) { while (n && n.firstChild) n.removeChild(n.firstChild); }
    function fmtBytes(b) {
        if (b == null) return '';
        if (b < 1024) return b + ' B';
        if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
        return (b / 1048576).toFixed(1) + ' MB';
    }

    // ---------- hash / query (parse only — never fed to a markup sink) ----------
    function readParams() {
        var out = {};
        try {
            var q = new URLSearchParams(location.search);
            if (q.get('ver')) out.ver = q.get('ver');
        } catch (_) { /* noop */ }
        var raw = (location.hash || '').replace(/^#/, '');
        raw.split('&').forEach(function (kv) {
            var i = kv.indexOf('=');
            if (i < 0) return;
            var k = kv.slice(0, i), v = kv.slice(i + 1);
            try { v = decodeURIComponent(v); } catch (_) { /* noop */ }
            if (k) out[k] = v;
        });
        return out;
    }
    function writeHash() {
        var parts = [];
        if (state.ver) parts.push('ver=' + encodeURIComponent(state.ver));
        if (state.pid) parts.push('pid=' + encodeURIComponent(state.pid));
        if (state.sel) {
            parts.push('module=' + encodeURIComponent(state.sel.module));
            parts.push('path=' + encodeURIComponent(state.sel.path));
        }
        // location.hash assignment is not a markup sink; safe under CSP.
        var h = '#' + parts.join('&');
        if (('#' + (location.hash || '').replace(/^#/, '')) !== h) {
            if (window.history && window.history.replaceState) {
                window.history.replaceState(null, '', location.pathname + location.search + h);
            } else {
                location.hash = h;
            }
        }
    }

    // ---------- boot ----------
    function boot() {
        var p = readParams();
        loadReleases(p.ver).then(function () {
            var initial = p.ver || state.ver;
            return loadIndex(initial, p);
        });
        document.getElementById('verSelect').addEventListener('change', function (e) {
            state.sel = null;
            loadIndex(e.target.value, {});
        });
        document.getElementById('searchBox').addEventListener('input', function (e) {
            state.q = (e.target.value || '').toLowerCase().trim();
            renderBrowser();
        });
    }

    function loadReleases(preferred) {
        return fetch('releases/index.json', { cache: 'default' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (doc) {
                var sel = document.getElementById('verSelect');
                clear(sel);
                var vers = [];
                if (doc && Array.isArray(doc.releases)) {
                    doc.releases.forEach(function (rel) { if (rel && rel.ver) vers.push(rel.ver); });
                }
                if (!vers.length) vers = ['26.1.1'];
                var def = preferred || (doc && doc.default) || vers[0];
                vers.forEach(function (v) {
                    var o = el('option', { text: v });
                    o.value = v;
                    if (v === def) o.selected = true;
                    sel.appendChild(o);
                });
                state.ver = def;
            })
            .catch(function () {
                var sel = document.getElementById('verSelect');
                clear(sel);
                var o = el('option', { text: '26.1.1' }); o.value = '26.1.1'; o.selected = true;
                sel.appendChild(o);
                state.ver = '26.1.1';
            });
    }

    function loadIndex(ver, params) {
        state.ver = ver;
        document.getElementById('verSelect').value = ver;
        var browser = document.getElementById('browser');
        clear(browser); browser.appendChild(el('div', { className: 'placeholder', text: 'Loading…' }));
        return fetch('releases/' + encodeURIComponent(ver) + '/live-examples-index.json', { cache: 'default' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (idx) {
                state.index = idx;
                state.specCache = {};
                if (!idx || !idx.modules || !idx.modules.length) {
                    document.querySelector('.layout').style.display = 'none';
                    document.getElementById('coverageCards').style.display = 'none';
                    document.getElementById('overview').style.display = 'none';
                    document.getElementById('emptyState').hidden = false;
                    document.getElementById('summary').textContent = '';
                    return;
                }
                document.querySelector('.layout').style.display = '';
                document.getElementById('coverageCards').style.display = '';
                document.getElementById('overview').style.display = '';
                document.getElementById('emptyState').hidden = true;

                // choose active device
                var pids = (idx.devices || []).map(function (d) { return d.pid; });
                state.pid = (params && params.pid && pids.indexOf(params.pid) >= 0)
                    ? params.pid : (pids[0] || '');
                state.cat = 'all';

                renderDeviceTabs();
                renderCatFilter();
                renderCoverage();
                renderOverview();
                renderSummary();
                renderBrowser();

                // deep-link selection
                if (params && params.module && params.path) {
                    selectPath(params.module, params.path, { scroll: true });
                }
                writeHash();
            })
            .catch(function () {
                var b = document.getElementById('browser');
                clear(b); b.appendChild(el('div', { className: 'placeholder', text: 'Failed to load live data index.' }));
            });
    }

    // ---------- device tabs ----------
    function renderDeviceTabs() {
        var host = document.getElementById('deviceTabs');
        clear(host);
        (state.index.devices || []).forEach(function (d) {
            var tab = el('button', {
                className: 'device-tab' + (d.pid === state.pid ? ' active' : ''),
                attrs: { role: 'tab', 'aria-selected': d.pid === state.pid ? 'true' : 'false' },
                onclick: function () {
                    if (state.pid === d.pid) return;
                    state.pid = d.pid;
                    renderDeviceTabs(); renderCoverage(); renderOverview(); renderSummary(); renderBrowser();
                    if (state.sel) selectPath(state.sel.module, state.sel.path, {});
                    writeHash();
                }
            }, [
                el('span', { text: d.pid }),
                el('span', { className: 'os', text: 'IOS XE ' + (d.os_version || '') })
            ]);
            host.appendChild(tab);
        });
    }

    // ---------- coverage cards (computed for the active device) ----------
    function deviceCoverage(pid) {
        var byCat = {};
        (state.index.modules || []).forEach(function (m) {
            var hit = 0;
            m.paths.forEach(function (p) { if (p.pids && p.pids[pid]) hit++; });
            if (!hit) return;
            var c = byCat[m.category] || (byCat[m.category] = { paths: 0, modules: 0 });
            c.paths += hit; c.modules += 1;
        });
        return byCat;
    }

    function renderCoverage() {
        var host = document.getElementById('coverageCards');
        clear(host);
        var cov = deviceCoverage(state.pid);
        (state.index.categories || []).forEach(function (c) {
            var got = cov[c.category] || { paths: 0, modules: 0 };
            if (!c.total_paths && !got.paths) return;
            var pct = c.total_paths ? Math.min(100, (got.paths / c.total_paths) * 100) : 0;
            var color = CAT_COLOR[c.category] || '#607D8B';
            var card = el('div', { className: 'cvcard' }, [
                el('span', { className: 'cat', text: CAT_LABEL[c.category] || c.category, style: 'background:' + color }),
                el('div', { className: 'big', text: got.paths.toLocaleString() }),
                el('div', { className: 'sub', text: 'of ' + c.total_paths.toLocaleString() + ' paths · ' + got.modules + ' modules' }),
                el('div', { className: 'bar' }, [el('span', { style: 'width:' + pct.toFixed(1) + '%;background:' + color })])
            ]);
            host.appendChild(card);
        });
    }

    // ---------- summary: stat tiles + charts + largest payloads ----------
    function computeStats(pid) {
        var byCat = {};   // category -> {paths, bytes, mods:{}}
        var byDev = {};   // pid -> {paths, bytes}
        var top = [];
        var totalPaths = 0, totalBytes = 0;
        (state.index.modules || []).forEach(function (m) {
            m.paths.forEach(function (p) {
                var pids = p.pids || {};
                Object.keys(pids).forEach(function (dp) {
                    var b = (pids[dp] && pids[dp].bytes) || 0;
                    var dv = byDev[dp] || (byDev[dp] = { paths: 0, bytes: 0 });
                    dv.paths += 1; dv.bytes += b;
                });
                var info = pids[pid];
                if (info) {
                    var c = byCat[m.category] || (byCat[m.category] = { paths: 0, bytes: 0, mods: {} });
                    c.paths += 1; c.bytes += info.bytes || 0; c.mods[m.module] = 1;
                    totalPaths += 1; totalBytes += info.bytes || 0;
                    top.push({ path: p.path, module: m.module, bytes: info.bytes || 0 });
                }
            });
        });
        top.sort(function (a, b) { return b.bytes - a.bytes; });
        return { byCat: byCat, byDev: byDev, top: top.slice(0, 12), totalPaths: totalPaths, totalBytes: totalBytes };
    }

    function renderOverview() {
        var stats = computeStats(state.pid);
        renderStatTiles(stats);
        renderTopPayloads(stats);
        renderCharts(stats);
        var note = document.getElementById('chartsNote');
        if (note) note.textContent = 'Charts and the largest-response list reflect the selected device: ' + state.pid + '. Coverage cards below show captured vs total paths per category.';
    }

    function renderStatTiles(stats) {
        var host = document.getElementById('statTiles');
        if (!host) return;
        clear(host);
        var t = state.index.totals || {};
        var allBytes = 0;
        Object.keys(stats.byDev).forEach(function (d) { allBytes += stats.byDev[d].bytes; });
        var tiles = [
            [String((state.index.devices || []).length), 'Devices'],
            [(t.modules_with_data || 0).toLocaleString(), 'Modules with data'],
            [(t.captured_paths || 0).toLocaleString(), 'Captured paths'],
            [fmtBytes(allBytes), 'Total payload'],
            [stats.totalPaths.toLocaleString(), state.pid + ' paths'],
            [fmtBytes(stats.totalBytes), state.pid + ' payload']
        ];
        tiles.forEach(function (tt) {
            host.appendChild(el('div', { className: 'stat-tile' }, [
                el('div', { className: 'num', text: tt[0] }),
                el('div', { className: 'lbl', text: tt[1] })
            ]));
        });
    }

    function renderTopPayloads(stats) {
        var host = document.getElementById('topPayloads');
        var dev = document.getElementById('topDev');
        if (dev) dev.textContent = 'on ' + state.pid;
        if (!host) return;
        clear(host);
        if (!stats.top.length) { host.appendChild(el('li', { className: 'placeholder', text: 'No data for this device.' })); return; }
        stats.top.forEach(function (row) {
            host.appendChild(el('li', {
                title: 'Open ' + row.module,
                onclick: function () { selectPath(row.module, row.path, { scroll: true }); }
            }, [
                el('span', { className: 'p', text: row.path }),
                el('span', { className: 'b', text: fmtBytes(row.bytes) })
            ]));
        });
    }

    function _destroyChart(key) {
        if (state.charts[key]) { try { state.charts[key].destroy(); } catch (_) { /* noop */ } state.charts[key] = null; }
    }

    function renderCharts(stats) {
        if (typeof window.Chart === 'undefined') return;  // vendored chart.js unavailable
        var cats = (state.index.categories || [])
            .map(function (c) { return c.category; })
            .filter(function (c) { return stats.byCat[c] && stats.byCat[c].paths; });
        var catLabels = cats.map(function (c) { return CAT_LABEL[c] || c; });
        var catColors = cats.map(function (c) { return CAT_COLOR[c] || '#607D8B'; });
        var catPaths = cats.map(function (c) { return stats.byCat[c].paths; });
        var catKB = cats.map(function (c) { return Math.round(stats.byCat[c].bytes / 1024); });

        var devs = (state.index.devices || []).map(function (d) { return d.pid; });
        var devPaths = devs.map(function (d) { return (stats.byDev[d] || {}).paths || 0; });
        var devColors = devs.map(function (d) { return d === state.pid ? '#1565c0' : '#9fb3c8'; });

        var base = { animation: false, responsive: true, maintainAspectRatio: false };

        _destroyChart('cat');
        state.charts.cat = new window.Chart(document.getElementById('chartCat'), {
            type: 'doughnut',
            data: { labels: catLabels, datasets: [{ data: catPaths, backgroundColor: catColors, borderWidth: 0 }] },
            options: Object.assign({}, base, { plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } } } })
        });

        _destroyChart('dev');
        state.charts.dev = new window.Chart(document.getElementById('chartDev'), {
            type: 'bar',
            data: { labels: devs, datasets: [{ data: devPaths, backgroundColor: devColors }] },
            options: Object.assign({}, base, { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } })
        });

        _destroyChart('bytes');
        state.charts.bytes = new window.Chart(document.getElementById('chartBytes'), {
            type: 'bar',
            data: { labels: catLabels, datasets: [{ label: 'KB', data: catKB, backgroundColor: catColors }] },
            options: Object.assign({}, base, { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'KB' } } } })
        });
    }

    // ---------- category filter chips ----------
    function renderCatFilter() {
        var host = document.getElementById('catFilter');
        clear(host);
        var cats = {};
        (state.index.modules || []).forEach(function (m) { cats[m.category] = true; });
        var order = Object.keys(cats).sort();
        function chip(catKey, label) {
            var active = state.cat === catKey;
            var color = catKey === 'all' ? '#455A64' : (CAT_COLOR[catKey] || '#607D8B');
            var b = el('button', {
                className: active ? 'active' : '', text: label,
                style: active ? 'background:' + color : '',
                onclick: function () { state.cat = catKey; renderCatFilter(); renderBrowser(); }
            });
            return b;
        }
        host.appendChild(chip('all', 'All'));
        order.forEach(function (c) { host.appendChild(chip(c, CAT_LABEL[c] || c)); });
    }

    function renderSummary() {
        var d = (state.index.devices || []).filter(function (x) { return x.pid === state.pid; })[0];
        var total = state.index.totals || {};
        var txt = (d ? d.paths.toLocaleString() + ' paths on ' + d.pid : '')
            + ' · ' + (total.modules_with_data || 0) + ' modules · '
            + (state.index.devices || []).length + ' device(s)';
        document.getElementById('summary').textContent = txt;
    }

    // ---------- module / path browser ----------
    function visibleModules() {
        var out = [];
        (state.index.modules || []).forEach(function (m) {
            if (state.cat !== 'all' && m.category !== state.cat) return;
            var paths = m.paths.filter(function (p) { return p.pids && p.pids[state.pid]; });
            if (!paths.length) return;
            if (state.q) {
                var modHit = m.module.toLowerCase().indexOf(state.q) >= 0;
                if (!modHit) {
                    paths = paths.filter(function (p) { return p.path.toLowerCase().indexOf(state.q) >= 0; });
                    if (!paths.length) return;
                }
            }
            out.push({ category: m.category, module: m.module, paths: paths });
        });
        return out;
    }

    function renderBrowser() {
        var host = document.getElementById('browser');
        clear(host);
        var mods = visibleModules();
        var totalPaths = mods.reduce(function (a, m) { return a + m.paths.length; }, 0);
        document.getElementById('browserCount').textContent =
            mods.length + ' modules · ' + totalPaths + ' paths';
        if (!mods.length) {
            host.appendChild(el('div', { className: 'placeholder', text: 'No matches for this device / filter.' }));
            return;
        }
        mods.forEach(function (m) {
            var color = CAT_COLOR[m.category] || '#607D8B';
            var openThis = state.sel && state.sel.module === m.module;
            var det = el('details', { className: 'modrow' });
            if (openThis) det.open = true;
            var sum = el('summary', {}, [
                el('span', { className: 'caret', text: '\u203A' }),
                el('span', { className: 'catdot', style: 'background:' + color }),
                el('span', { className: 'mod', text: m.module }),
                el('span', { className: 'n', text: m.paths.length + '' })
            ]);
            det.appendChild(sum);
            m.paths.forEach(function (p) {
                var info = p.pids[state.pid] || {};
                var selected = state.sel && state.sel.module === m.module && state.sel.path === p.path;
                var row = el('div', {
                    className: 'pathrow' + (selected ? ' sel' : ''),
                    onclick: function () { selectPath(m.module, p.path, {}); }
                }, [
                    el('span', { className: 'st', text: (info.status || '') + (info.bytes != null ? ' · ' + fmtBytes(info.bytes) : '') }),
                    el('span', { text: p.path })
                ]);
                det.appendChild(row);
            });
            host.appendChild(det);
        });
    }

    // ---------- detail pane ----------
    function findIndexEntry(module, path) {
        var found = null;
        (state.index.modules || []).some(function (m) {
            if (m.module !== module) return false;
            return m.paths.some(function (p) {
                if (p.path === path) { found = { category: m.category, module: module, path: path, pids: p.pids }; return true; }
                return false;
            });
        });
        return found;
    }

    function selectPath(module, path, opts) {
        var entry = findIndexEntry(module, path);
        if (!entry) return;
        state.sel = { cat: entry.category, module: module, path: path };
        // active device for the detail: keep global pid if it has this path, else first that does
        var pidForDetail = (entry.pids && entry.pids[state.pid]) ? state.pid : Object.keys(entry.pids || {})[0];
        renderBrowser();
        renderDetail(entry, pidForDetail);
        writeHash();
        if (opts && opts.scroll) {
            var d = document.getElementById('detail');
            if (d && d.scrollIntoView) d.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function renderDetail(entry, pid) {
        var host = document.getElementById('detail');
        clear(host);
        var pids = Object.keys(entry.pids || {});
        var info = entry.pids[pid] || {};

        var head = el('div', { className: 'dhead' }, [
            el('div', { className: 'dpath', text: 'GET ' + entry.path }),
            el('div', {
                className: 'dmeta',
                text: (CAT_LABEL[entry.category] || entry.category) + ' · ' + entry.module
                    + ' · ' + pid + ' · HTTP ' + (info.status || '?')
                    + (info.bytes != null ? ' · ' + fmtBytes(info.bytes) : '')
            })
        ]);
        if (pids.length > 1) {
            var subtabs = el('div', { className: 'dsub-tabs' });
            pids.forEach(function (pp) {
                subtabs.appendChild(el('button', {
                    className: 'dsub-tab' + (pp === pid ? ' active' : ''), text: pp,
                    onclick: function () { renderDetail(entry, pp); }
                }));
            });
            head.appendChild(subtabs);
        }
        host.appendChild(head);

        var pre = el('pre', { className: 'resp', text: 'Loading captured response…' });
        host.appendChild(pre);

        getResponseValue(entry.category, entry.module, entry.path, pid).then(function (rec) {
            if (rec == null) { pre.textContent = '(no captured body found in spec)'; return; }
            var body = rec.value;
            var txt;
            try { txt = JSON.stringify(body, null, 2); } catch (_) { txt = String(body); }
            pre.textContent = txt;
        }).catch(function () {
            pre.textContent = 'Failed to load the module spec for this path.';
        });
    }

    function getResponseValue(cat, module, path, pid) {
        var key = cat + '/' + module;
        var cached = state.specCache[key];
        var specPromise = cached
            ? Promise.resolve(cached)
            : fetch('releases/' + encodeURIComponent(state.ver) + '/' + MODEL_DIR[cat] + '/api/'
                + encodeURIComponent(module) + '.json', { cache: 'default' })
                .then(function (r) { if (!r.ok) throw new Error('http'); return r.json(); })
                .then(function (spec) { state.specCache[key] = spec; return spec; });
        return specPromise.then(function (spec) {
            var item = (spec.paths || {})[path];
            if (!item || !item.get) return null;
            var responses = item.get.responses || {};
            var resp = responses['200'] || responses['default'];
            var content = resp && resp.content;
            if (!content) return null;
            var keys = Object.keys(content);
            for (var i = 0; i < keys.length; i++) {
                var media = content[keys[i]];
                if (media && media[LIVE_KEY] && media[LIVE_KEY][pid]) return media[LIVE_KEY][pid];
            }
            return null;
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
