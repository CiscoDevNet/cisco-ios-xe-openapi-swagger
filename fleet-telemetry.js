/* fleet-telemetry.js — browse REAL live MDT captured from the fleet.
 *
 * Loads telemetry-live-data.json (built by build_live_dataset.py from the
 * per-device Telegraf capture files) and renders it as device (PID) tabs, a
 * model-flavor filter, a streamed-path list, and a per-path detail showing the
 * list keys and leaf values that streamed.
 *
 * CSP note: strict CSP (no inline scripts); every node is built with
 * createElement / textContent — never innerHTML.
 */
(function () {
    'use strict';

    var DATA_URL = 'telemetry-live-data.json';
    var CAT_LABEL = {
        oper: 'Oper', openconfig: 'OpenConfig', 'native-config': 'Native',
        cfg: 'Config', ietf: 'IETF', other: 'Other', mib: 'MIB', wireless: 'Wireless'
    };
    var CAT_COLOR = {
        oper: '#2196F3', openconfig: '#009688', 'native-config': '#4CAF50',
        cfg: '#00BCD4', ietf: '#FF5722', other: '#757575', mib: '#9C27B0', wireless: '#E91E63'
    };

    var state = { data: null, pid: '', cat: 'all', q: '', sel: null };
    var charts = {};

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
    function catClass(c) { return 'cat-' + c; }

    // ---------- filtering ----------
    function devicePaths(pid) {
        return (state.data.paths || []).filter(function (p) { return p.pid === pid; });
    }
    function matches(p) {
        if (state.cat !== 'all' && p.category !== state.cat) return false;
        if (state.q && p.path.toLowerCase().indexOf(state.q) === -1) return false;
        return true;
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
        var rows = devicePaths(state.pid).filter(matches)
            .sort(function (a, b) { return a.category.localeCompare(b.category) || a.path.localeCompare(b.path); });
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
                el('span', { className: 'rc', text: fmt(p.records) + ' rec' })
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

        var head = el('div', { className: 'dhead' }, [
            el('div', { className: 'dpath', text: p.path }),
            el('div', { className: 'dmeta', text: (CAT_LABEL[p.category] || p.category) + ' · ' + p.pid + ' · ' + fmt(p.records) + ' records' })
        ]);
        panel.appendChild(head);

        var body = el('div', { className: 'body' });
        var table = el('table', { className: 'ftable' });
        var tbody = el('tbody');
        var keys = p.keys || {};
        Object.keys(keys).forEach(function (k) {
            tbody.appendChild(el('tr', {}, [
                el('td', { className: 'k' }, [document.createTextNode(k), el('span', { className: 'keybadge', text: 'key' })]),
                el('td', { className: 'v', text: String(keys[k]) })
            ]));
        });
        var fields = p.fields || {};
        Object.keys(fields).forEach(function (f) {
            tbody.appendChild(el('tr', {}, [
                el('td', { className: 'k', text: f }),
                el('td', { className: 'v', text: String(fields[f]) })
            ]));
        });
        if (!tbody.firstChild) tbody.appendChild(el('tr', {}, [el('td', { className: 'k', text: '(no sampled fields)' })]));
        table.appendChild(tbody);
        body.appendChild(table);
        panel.appendChild(body);
    }

    function updateSummary() {
        var shown = devicePaths(state.pid).filter(matches).length;
        $('summary').textContent = shown + ' paths · ' + fmt((state.data.totals || {}).records) + ' records total';
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
        host.appendChild(tile(fmt(t.paths), 'Streamed paths'));
        host.appendChild(tile(fmt(t.records), 'Records'));
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
        var devRecs = devs.map(function (d) { return d.records; });
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
            data: { labels: devLabels, datasets: [{ data: devRecs, backgroundColor: '#00838F' }] },
            options: Object.assign({}, base, { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } })
        });
    }

    function render() {
        renderDeviceTabs();
        renderCatChips();
        renderList();
        renderDetail();
        updateSummary();
    }

    function init() {
        var search = $('searchBox');
        search.addEventListener('input', function () {
            state.q = search.value.trim().toLowerCase();
            renderList();
            updateSummary();
        });
        fetch(DATA_URL)
            .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(function (data) {
                state.data = data;
                var d = (data.devices || [])[0];
                state.pid = d ? d.pid : '';
                var prov = data.platform || 'IOS XE';
                $('prov').textContent = (data.totals ? fmt(data.totals.devices) + ' devices · ' + fmt(data.totals.paths) + ' paths · ' + fmt(data.totals.records) + ' records' : '') + '  ·  ' + (data.transport || '');
                renderSummary();
                render();
            })
            .catch(function () {
                $('browser').textContent = '';
                $('emptyState').hidden = false;
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
