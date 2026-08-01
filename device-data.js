/* device-data.js — browse REAL collected device data across two transports.
 *
 * Loads two datasets in the same shape and lets the user toggle between them:
 *   - Model-Driven Telemetry (push): telemetry-live-data.json, built by
 *     build_live_dataset.py from the per-device Telegraf capture files.
 *   - RESTCONF (pull): restconf-live-data.json, built by
 *     build_restconf_dataset.py from the release's live-examples index; the
 *     actual GET payloads are fetched lazily per path on selection.
 *
 * Renders device (PID) tabs, a model-flavor filter, a path list, summary
 * tiles + charts, and a per-path detail (streamed keys/values for MDT, the
 * GET response payload for RESTCONF).
 *
 * CSP note: strict CSP (no inline scripts); every node is built with
 * createElement / textContent — never innerHTML.
 */
(function () {
    'use strict';

    var MDT_URL = 'telemetry-live-data.json';
    var RESTCONF_URL = 'restconf-live-data.json';
    var CAT_LABEL = {
        oper: 'Oper', openconfig: 'OpenConfig', 'native-config': 'Native',
        cfg: 'Config', ietf: 'IETF', other: 'Other', mib: 'MIB', wireless: 'Wireless', rpc: 'RPC'
    };
    var CAT_COLOR = {
        oper: '#2196F3', openconfig: '#009688', 'native-config': '#4CAF50',
        cfg: '#00BCD4', ietf: '#FF5722', other: '#757575', mib: '#9C27B0', wireless: '#E91E63', rpc: '#795548'
    };

    var state = { transport: 'mdt', datasets: {}, data: null, pid: '', cat: 'all', q: '', sel: null, sort: 'cat' };
    var charts = {};
    var payloadCache = {};

    function el(tag, opts, kids) {
        var n = document.createElement(tag);
        opts = opts || {};
        if (opts.className) n.className = opts.className;
        if (opts.text != null) n.textContent = opts.text;
        if (opts.title) n.title = opts.title;
        if (opts.attrs) { Object.keys(opts.attrs).forEach(function (k) { n.setAttribute(k, opts.attrs[k]); }); }
        if (opts.onclick) n.addEventListener('click', opts.onclick);
        (kids || []).forEach(function (k) { if (k) n.appendChild(k); });
        return n;
    }
    function clear(n) { while (n && n.firstChild) n.removeChild(n.firstChild); }
    function $(id) { return document.getElementById(id); }
    function fmt(n) { return (n == null) ? '' : Number(n).toLocaleString('en-US'); }
    function fmtBytes(n) {
        n = n || 0;
        if (n < 1024) return n + ' B';
        if (n < 1048576) return (n / 1024).toFixed(1) + ' KB';
        return (n / 1048576).toFixed(1) + ' MB';
    }
    function catClass(c) { return 'cat-' + c; }

    // Size proxy per transport: RESTCONF = response bytes; MDT = records captured.
    function sizeOf(p) { return state.transport === 'restconf' ? (p.bytes || 0) : (p.records || 0); }
    function shortLabel(path) { var parts = path.split('/'); return parts.slice(-2).join('/'); }
    function sortComparator(a, b) {
        if (state.sort === 'size') return sizeOf(b) - sizeOf(a) || a.path.localeCompare(b.path);
        if (state.sort === 'path') return a.path.localeCompare(b.path);
        return a.category.localeCompare(b.category) || a.path.localeCompare(b.path);
    }

    // ---------- filtering ----------
    function devicePaths(pid) {
        return (state.data.paths || []).filter(function (p) { return p.pid === pid; });
    }
    function matches(p) {
        if (state.cat !== 'all' && p.category !== state.cat) return false;
        if (state.q && haystack(p).indexOf(state.q) === -1) return false;
        return true;
    }
    // Lazily build a lowercase search string per path covering the xpath plus
    // every captured instance's keys and leaf values (cached on the path).
    function haystack(p) {
        if (p._hay != null) return p._hay;
        var parts = [p.path];
        (p.samples || []).forEach(function (s) {
            var keys = s.keys || {};
            Object.keys(keys).forEach(function (k) { parts.push(k, String(keys[k])); });
            var f = s.fields || {};
            Object.keys(f).forEach(function (k) { parts.push(k, String(f[k])); });
        });
        p._hay = parts.join(' ').toLowerCase();
        return p._hay;
    }

    // ---------- device tabs ----------
    function renderDeviceTabs() {
        var wrap = $('deviceTabs');
        clear(wrap);
        (state.data.devices || []).forEach(function (d) {
            var btn = el('button', {
                className: 'device-tab' + (state.pid === d.pid ? ' active' : ''),
                attrs: { role: 'tab', 'aria-selected': String(state.pid === d.pid) },
                onclick: function () { state.pid = d.pid; state.cat = 'all'; state.sel = null; render(); }
            }, [
                document.createTextNode(d.pid + ' '),
                el('span', { className: 'n', text: '(' + fmt(d.paths) + ')' })
            ]);
            wrap.appendChild(btn);
        });
    }

    // ---------- category chips ----------
    function renderCatChips() {
        var wrap = $('catChips');
        clear(wrap);
        var dev = (state.data.devices || []).filter(function (d) { return d.pid === state.pid; })[0];
        var byCat = (dev && dev.by_category) || {};
        var total = devicePaths(state.pid).length;
        wrap.appendChild(chip('all', 'All', total));
        Object.keys(byCat).sort().forEach(function (c) {
            wrap.appendChild(chip(c, CAT_LABEL[c] || c, byCat[c]));
        });
    }
    function chip(cat, label, n) {
        var active = state.cat === cat;
        var kids = [];
        if (cat !== 'all') kids.push(el('span', { className: 'catdot ' + catClass(cat) }));
        kids.push(document.createTextNode(label + ' '));
        kids.push(el('span', { className: 'n', text: '(' + fmt(n) + ')' }));
        return el('button', {
            className: 'chip' + (active ? ' active ' + catClass(cat) : ''),
            onclick: function () { state.cat = cat; state.sel = null; render(); }
        }, kids);
    }

    // ---------- path list ----------
    function renderList() {
        var wrap = $('browser');
        clear(wrap);
        var rows = devicePaths(state.pid).filter(matches);
        rows.sort(sortComparator);
        $('browserCount').textContent = rows.length;
        if (!rows.length) {
            wrap.appendChild(el('div', { className: 'placeholder', text: 'No streamed paths match.' }));
            return;
        }
        rows.forEach(function (p) {
            var key = p.pid + '|' + p.path;
            var row = el('div', {
                className: 'prow' + (state.sel === key ? ' sel' : ''),
                onclick: function () { state.sel = key; renderList(); renderDetail(); }
            }, [
                el('span', { className: 'catdot ' + catClass(p.category), title: p.category }),
                el('span', { className: 'p', text: p.path }),
                el('span', { className: 'rc', text: state.transport === 'restconf' ? fmtBytes(p.bytes) : fmt(p.records) + ' rec' })
            ]);
            wrap.appendChild(row);
        });
    }

    // ---------- detail ----------
    function renderDetail() {
        var panel = $('detail');
        clear(panel);
        if (!state.sel) {
            panel.appendChild(el('div', { className: 'placeholder', text: 'Select a path to view its streamed keys and values.' }));
            return;
        }
        var p = (state.data.paths || []).filter(function (x) { return x.pid + '|' + x.path === state.sel; })[0];
        if (!p) { panel.appendChild(el('div', { className: 'placeholder', text: 'Not found.' })); return; }

        if (state.transport === 'restconf') { renderRestconfDetail(panel, p); return; }

        var samples = p.samples || [];
        var instances = p.instances || samples.length || 1;
        var metaBits = (CAT_LABEL[p.category] || p.category) + ' · ' + p.pid + ' · ' + fmt(p.records) + ' records';
        if (instances > 1) metaBits += ' · ' + fmt(instances) + ' instances';
        var head = el('div', { className: 'dhead' }, [
            el('div', { className: 'dpath', text: p.path }),
            el('div', { className: 'dmeta', text: metaBits }),
            el('div', { className: 'dbtns' }, [
                copyBtn('Copy payload', function () { return JSON.stringify(payloadOf(p), null, 2); }),
                copyBtn('Copy path', function () { return p.path; })
            ])
        ]);
        panel.appendChild(head);

        var body = el('div', { className: 'body' });
        if (samples.length) {
            samples.forEach(function (s, i) {
                body.appendChild(renderInstance(s, samples.length > 1 ? instanceLabel(s, i) : null));
            });
            if (instances > samples.length) {
                body.appendChild(el('div', { className: 'instmore',
                    text: 'Showing ' + samples.length + ' of ' + fmt(instances) + ' instances. The full set streams live from the device — rebuild the dataset to refresh.' }));
            }
        } else {
            body.appendChild(renderInstance({ keys: p.keys || {}, fields: p.fields || {} }, null));
        }
        panel.appendChild(body);
    }

    function instanceLabel(s, i) {
        var keys = s.keys || {};
        var vals = Object.keys(keys).map(function (k) { return keys[k]; });
        return vals.length ? vals.join(' · ') : 'Instance ' + (i + 1);
    }

    // Full payload for the selected path (all captured instances) as clipboard JSON.
    function payloadOf(p) {
        return {
            pid: p.pid, source: p.source, category: p.category, path: p.path,
            records: p.records, instances: p.instances,
            samples: p.samples && p.samples.length ? p.samples : [{ keys: p.keys || {}, fields: p.fields || {} }]
        };
    }
    function copyBtn(label, getText) {
        return el('button', {
            className: 'cbtn', text: label,
            onclick: function (e) { copyText(getText(), e.currentTarget, label); }
        });
    }
    function copyText(text, btn, label) {
        function flash(ok) {
            btn.textContent = ok ? 'Copied!' : 'Copy failed';
            setTimeout(function () { btn.textContent = label; }, 1200);
        }
        function legacyCopy() {
            try {
                var ta = document.createElement('textarea');
                ta.value = text; ta.setAttribute('readonly', '');
                ta.style.position = 'absolute'; ta.style.left = '-9999px';
                document.body.appendChild(ta); ta.select();
                var ok = document.execCommand('copy');
                document.body.removeChild(ta);
                return ok;
            } catch (_) { return false; }
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(
                function () { flash(true); },
                function () { flash(legacyCopy()); }  // fall back if the async API is blocked
            );
            return;
        }
        flash(legacyCopy());
    }

    // ---------- RESTCONF detail (lazy payload fetch) ----------
    function renderRestconfDetail(panel, p) {
        var metaBits = (CAT_LABEL[p.category] || p.category) + ' · ' + p.pid
            + ' · HTTP ' + (p.status == null ? '?' : p.status) + ' · ' + fmtBytes(p.bytes);
        var head = el('div', { className: 'dhead' }, [
            el('div', { className: 'dpath', text: p.path }),
            el('div', { className: 'dmeta', text: metaBits }),
            el('div', { className: 'dbtns' }, [copyBtn('Copy path', function () { return p.path; })])
        ]);
        panel.appendChild(head);
        var body = el('div', { className: 'body' });
        var pre = el('pre', { className: 'jsonbox', text: 'Loading payload…' });
        body.appendChild(pre);
        panel.appendChild(body);
        var btns = head.querySelector('.dbtns');
        fetchRestconfPayload(p).then(function (value) {
            var text = JSON.stringify(value, null, 2);
            pre.textContent = text;
            btns.insertBefore(copyBtn('Copy payload', function () { return text; }), btns.firstChild);
        }, function (err) {
            pre.textContent = 'Could not load payload: ' + ((err && err.message) || err);
        });
    }
    function fetchRestconfPayload(p) {
        var cacheKey = p.file + '#' + p.pid;
        if (payloadCache[cacheKey]) return Promise.resolve(payloadCache[cacheKey]);
        return fetch(p.file)
            .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(function (doc) {
                var pids = doc.pids || {};
                var entry = pids[p.pid] || {};
                var value = (entry.value != null) ? entry.value
                    : (doc.value != null ? doc.value : doc);
                payloadCache[cacheKey] = value;
                return value;
            });
    }

    function renderInstance(s, label) {
        var wrap = el('div', { className: 'inst' });
        if (label != null) wrap.appendChild(el('div', { className: 'insthead', text: label }));
        var table = el('table', { className: 'ftable' });
        var tbody = el('tbody');
        var keys = s.keys || {};
        Object.keys(keys).forEach(function (k) {
            tbody.appendChild(el('tr', {}, [
                el('td', { className: 'k' }, [document.createTextNode(k), el('span', { className: 'keybadge', text: 'key' })]),
                el('td', { className: 'v', text: String(keys[k]) })
            ]));
        });
        var fields = s.fields || {};
        Object.keys(fields).forEach(function (f) {
            tbody.appendChild(el('tr', {}, [
                el('td', { className: 'k', text: f }),
                el('td', { className: 'v', text: String(fields[f]) })
            ]));
        });
        if (!tbody.firstChild) tbody.appendChild(el('tr', {}, [el('td', { className: 'k', text: '(no sampled fields)' })]));
        table.appendChild(tbody);
        wrap.appendChild(table);
        return wrap;
    }

    function updateSummary() {
        var all = devicePaths(state.pid).length;
        var shown = devicePaths(state.pid).filter(matches).length;
        $('summary').textContent = shown + (shown === all ? '' : ' / ' + all) + ' paths';
    }

    // ---------- fleet summary (tiles + charts) ----------
    function tile(big, lbl) {
        return el('div', { className: 'mtile' }, [
            el('div', { className: 'big', text: big }),
            el('div', { className: 'lbl', text: lbl })
        ]);
    }
    function renderSummary() {
        var t = state.data.totals || {};
        var cats = state.data.categories || [];
        var host = $('mtiles');
        clear(host);
        host.appendChild(tile(fmt(t.devices), 'Devices'));
        host.appendChild(tile(fmt(t.paths), 'Captured paths'));
        if (state.transport === 'restconf') {
            var totBytes = (state.data.devices || []).reduce(function (s, d) { return s + (d.bytes || 0); }, 0);
            host.appendChild(tile(fmtBytes(totBytes), 'Response payload'));
        } else {
            host.appendChild(tile(fmt(t.records), 'Records'));
        }
        host.appendChild(tile(fmt(cats.length), 'Model flavors'));
        renderCharts();
    }
    function destroyChart(k) {
        if (charts[k]) { try { charts[k].destroy(); } catch (_) { /* noop */ } charts[k] = null; }
    }
    function renderCharts() {
        if (typeof window.Chart === 'undefined') return;  // vendored chart.js unavailable
        var cats = state.data.categories || [];
        var catLabels = cats.map(function (c) { return CAT_LABEL[c.category] || c.category; });
        var catColors = cats.map(function (c) { return CAT_COLOR[c.category] || '#607D8B'; });
        var catPaths = cats.map(function (c) { return c.paths; });
        var devs = state.data.devices || [];
        var devLabels = devs.map(function (d) { return d.pid; });
        var devPaths = devs.map(function (d) { return d.paths; });
        var restconf = state.transport === 'restconf';
        var thirdData = restconf ? devs.map(function (d) { return d.bytes || 0; }) : devs.map(function (d) { return d.records; });
        var thirdTitle = restconf ? 'Response bytes per device' : 'Records captured per device';
        var titleEl = $('chartRecTitle'); if (titleEl) titleEl.textContent = thirdTitle;
        var base = { animation: false, responsive: true, maintainAspectRatio: false };

        destroyChart('cat');
        charts.cat = new window.Chart($('chartCat'), {
            type: 'doughnut',
            data: { labels: catLabels, datasets: [{ data: catPaths, backgroundColor: catColors, borderWidth: 0 }] },
            options: Object.assign({}, base, { plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } } } })
        });
        destroyChart('dev');
        charts.dev = new window.Chart($('chartDev'), {
            type: 'bar',
            data: { labels: devLabels, datasets: [{ data: devPaths, backgroundColor: '#1565c0' }] },
            options: Object.assign({}, base, { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } })
        });
        destroyChart('rec');
        charts.rec = new window.Chart($('chartRec'), {
            type: 'bar',
            data: { labels: devLabels, datasets: [{ data: thirdData, backgroundColor: '#00838F' }] },
            options: Object.assign({}, base, { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } })
        });
    }

    function render() {
        renderDeviceTabs();
        renderCatChips();
        renderList();
        renderDetail();
        updateSummary();
        renderTopChart();
    }

    // ---------- largest-paths chart (active device + flavor filter) ----------
    function renderTopChart() {
        if (typeof window.Chart === 'undefined') return;
        var restconf = state.transport === 'restconf';
        var rows = devicePaths(state.pid).filter(matches).slice()
            .sort(function (a, b) { return sizeOf(b) - sizeOf(a); }).slice(0, 12);
        var labels = rows.map(function (p) { return shortLabel(p.path); });
        var vals = rows.map(sizeOf);
        var colors = rows.map(function (p) { return CAT_COLOR[p.category] || '#607D8B'; });
        var metric = restconf ? 'bytes' : 'records';
        var scope = state.cat === 'all' ? 'all flavors' : (CAT_LABEL[state.cat] || state.cat);
        var titleEl = $('chartTopTitle');
        if (titleEl) titleEl.textContent = 'Largest paths — ' + state.pid + ' · ' + scope + ' (' + metric + ')';
        destroyChart('top');
        if (!rows.length) return;
        charts.top = new window.Chart($('chartTop'), {
            type: 'bar',
            data: { labels: labels, datasets: [{ data: vals, backgroundColor: colors }] },
            options: {
                animation: false, responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { title: function (items) { return rows[items[0].dataIndex].path; } } }
                },
                scales: { x: { beginAtZero: true }, y: { ticks: { font: { size: 9 } } } }
            }
        });
    }

    function init() {
        var search = $('searchBox');
        search.addEventListener('input', function () {
            state.q = search.value.trim().toLowerCase();
            renderList();
            updateSummary();
            renderTopChart();
        });
        var sortSel = $('sortBy');
        if (sortSel) sortSel.addEventListener('change', function () {
            state.sort = sortSel.value;
            renderList();
        });
        var mdtBtn = $('tMdt'), rcBtn = $('tRestconf');
        if (mdtBtn) mdtBtn.addEventListener('click', function () { setTransport('mdt'); });
        if (rcBtn) rcBtn.addEventListener('click', function () { setTransport('restconf'); });

        Promise.all([
            fetchJson(MDT_URL).catch(function () { return null; }),
            fetchJson(RESTCONF_URL).catch(function () { return null; })
        ]).then(function (res) {
            state.datasets.mdt = res[0];
            state.datasets.restconf = res[1];
            if (!res[0] && !res[1]) { $('browser').textContent = ''; $('emptyState').hidden = false; return; }
            if (!res[1] && rcBtn) { rcBtn.disabled = true; }
            if (!res[0] && mdtBtn) { mdtBtn.disabled = true; }
            setTransport(res[0] ? 'mdt' : 'restconf');
        });
    }

    function fetchJson(url) {
        return fetch(url).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); });
    }
    function setTransport(t) {
        if (!state.datasets[t]) return;
        state.transport = t;
        state.data = state.datasets[t];
        state.cat = 'all'; state.q = ''; state.sel = null;
        var sb = $('searchBox'); if (sb) sb.value = '';
        var d = (state.data.devices || [])[0];
        state.pid = d ? d.pid : '';
        var mdtBtn = $('tMdt'), rcBtn = $('tRestconf');
        if (mdtBtn) mdtBtn.classList.toggle('active', t === 'mdt');
        if (rcBtn) rcBtn.classList.toggle('active', t === 'restconf');
        updateProv();
        renderSummary();
        render();
    }
    function updateProv() {
        var data = state.data || {};
        var totals = data.totals || {};
        $('prov').textContent = (totals.paths != null
            ? fmt(totals.devices) + ' devices · ' + fmt(totals.paths) + ' paths' : '')
            + '  ·  ' + (data.transport || '');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
