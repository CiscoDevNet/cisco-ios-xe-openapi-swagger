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

    var TRANSPORTS = [
        { key: 'mdt', url: 'telemetry-live-data.json', label: 'MDT', sub: 'push · gRPC' },
        { key: 'restconf', url: 'restconf-live-data.json', label: 'RESTCONF', sub: 'GET · HTTPS' },
        { key: 'netconf-get', url: 'netconf-get-live-data.json', label: 'NETCONF get', sub: 'SSH · 830' },
        { key: 'netconf-getconfig', url: 'netconf-getconfig-live-data.json', label: 'NETCONF', sub: 'get-config' },
        { key: 'netconf-sub', url: 'netconf-sub-live-data.json', label: 'NETCONF', sub: 'subscribe' },
        { key: 'gnmi-get', url: 'gnmi-get-live-data.json', label: 'gNMI Get', sub: 'all · 9339' },
        { key: 'gnmi-getconfig', url: 'gnmi-getconfig-live-data.json', label: 'gNMI Get', sub: 'config' },
        { key: 'gnmi-state', url: 'gnmi-state-live-data.json', label: 'gNMI Get', sub: 'state · oper' },
        { key: 'gnmi-sub', url: 'gnmi-sub-live-data.json', label: 'gNMI Sub', sub: 'once/sample/change' }
    ];
    var MATRIX_URL = 'protocol-matrix.json';
    var CAT_LABEL = {
        oper: 'Oper', openconfig: 'OpenConfig', 'native-config': 'Native',
        cfg: 'Config', ietf: 'IETF', other: 'Other', mib: 'MIB', wireless: 'Wireless', rpc: 'RPC'
    };
    var CAT_COLOR = {
        oper: '#2196F3', openconfig: '#009688', 'native-config': '#4CAF50',
        cfg: '#00BCD4', ietf: '#FF5722', other: '#757575', mib: '#9C27B0', wireless: '#E91E63', rpc: '#795548'
    };

    var state = { transport: 'mdt', datasets: {}, data: null, pid: '', cat: 'all', q: '', sel: null, sort: 'cat', matrix: false, dataFilter: 'all', matrixGaps: false, matrixCat: 'all', jump: null,
        matrixPivot: 'methods', matrixMethod: null, matrixInconsistent: false, matrixIndex: null, matrixClass: null };
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
    function fmtAge(iso) {
        var t = iso ? Date.parse(iso) : NaN;
        if (isNaN(t)) return '';
        var s = Math.max(0, (Date.now() - t) / 1000);
        if (s < 90) return 'just now';
        if (s < 5400) return Math.round(s / 60) + ' min ago';
        if (s < 129600) return Math.round(s / 3600) + ' h ago';
        return Math.round(s / 86400) + ' days ago';
    }
    function catClass(c) { return 'cat-' + c; }

    // Size proxy: MDT reports records; the other methods report response bytes.
    function sizeOf(p) { return (p.records != null ? p.records : p.bytes) || 0; }
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
        if (state.dataFilter === 'data' && isNoData(p)) return false;
        if (state.dataFilter === 'nodata' && !isNoData(p)) return false;
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
                onclick: function () { state.pid = d.pid; state.cat = 'all'; state.sel = null; if (state.matrix) { renderMatrix(); } else { render(); } }
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
        var withData = [], without = [];
        rows.forEach(function (p) { (isNoData(p) ? without : withData).push(p); });
        withData.forEach(function (p) { wrap.appendChild(pathRow(p, false)); });
        if (without.length) {
            wrap.appendChild(el('div', { className: 'nodhead',
                text: 'No data \u00b7 ' + without.length + ' path' + (without.length > 1 ? 's' : '') }));
            without.forEach(function (p) { wrap.appendChild(pathRow(p, true)); });
        }
    }
    function pathRow(p, dim) {
        var key = p.pid + '|' + p.path;
        return el('div', {
            className: 'prow' + (state.sel === key ? ' sel' : '') + (dim ? ' nodata' : ''),
            onclick: function () { state.sel = key; renderList(); renderDetail(); }
        }, [
            el('span', { className: 'catdot ' + catClass(p.category), title: p.category }),
            el('span', { className: 'p', text: p.path }),
            el('span', { className: 'rc', text: dim ? 'no data'
                : (p.records != null ? fmt(p.records) + ' rec' : fmtBytes(p.bytes)) })
        ]);
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

        if (state.transport === 'restconf' && p.file) { renderRestconfDetail(panel, p); return; }
        if (typeof p.payload === 'string') { renderInlineDetail(panel, p); return; }

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

    // ---------- payload formatting & syntax highlighting ----------
    // Empty NETCONF replies are just an <rpc-reply><data/></rpc-reply> envelope;
    // treat those (and blank subscribe payloads) as "no data" rather than showing
    // an empty box. MDT/RESTCONF paths have no inline payload string, so skip them.
    function isNoData(p) {
        if (typeof p.payload !== 'string') return false;
        if (p.status === 'empty' || p.status === 'accepted-nodata') return true;
        return p.payload.replace(/\s+/g, '') === '';
    }
    function detectLang(text) {
        var t = (text || '').replace(/^\uFEFF/, '').trim();
        if (t.charAt(0) === '<') return 'xml';
        if (t.charAt(0) === '{' || t.charAt(0) === '[') return 'json';
        return 'text';
    }
    function formatJson(text) {
        try { return JSON.stringify(JSON.parse(text), null, 2); } catch (e) { return null; }
    }
    // Lightweight, dependency-free XML re-indenter.
    function formatXml(xml) {
        var PAD = '  ', pad = 0, out = '';
        xml = (xml || '').replace(/<\?xml[^>]*\?>/g, '').trim().replace(/>\s+</g, '><');
        xml = xml.replace(/(>)(<)(\/*)/g, '$1\n$2$3');
        xml.split('\n').forEach(function (node) {
            node = node.trim(); if (!node) return;
            var delta = 0;
            if (/^<\/\w/.test(node)) { pad = Math.max(pad - 1, 0); }
            else if (/^<\w[^>]*[^\/]>$/.test(node) && node.indexOf('</') === -1) { delta = 1; }
            out += PAD.repeat(pad) + node + '\n';
            pad += delta;
        });
        return out.trim();
    }
    function formatPayload(text, lang) {
        if (lang === 'json') { var j = formatJson(text); if (j != null) return j; }
        if (lang === 'xml') return formatXml(text);
        return text || '';
    }
    function span(cls, txt) { return el('span', { className: cls, text: txt }); }
    function highlightInto(pre, text, lang) {
        clear(pre);
        if (lang === 'json') { highlightJson(pre, text); return; }
        if (lang === 'xml') { highlightXml(pre, text); return; }
        pre.appendChild(document.createTextNode(text));
    }
    function highlightJson(pre, text) {
        var re = /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([{}\[\],])/g;
        var last = 0, m;
        while ((m = re.exec(text))) {
            if (m.index > last) pre.appendChild(document.createTextNode(text.slice(last, m.index)));
            if (m[1] != null && m[2] != null) { pre.appendChild(span('t-key', m[1])); pre.appendChild(span('t-punct', m[2])); }
            else if (m[1] != null) { pre.appendChild(span('t-str', m[1])); }
            else if (m[3] != null) { pre.appendChild(span('t-lit', m[3])); }
            else if (m[4] != null) { pre.appendChild(span('t-num', m[4])); }
            else if (m[5] != null) { pre.appendChild(span('t-punct', m[5])); }
            last = re.lastIndex;
        }
        if (last < text.length) pre.appendChild(document.createTextNode(text.slice(last)));
    }
    function highlightXml(pre, text) {
        var re = /(<\/?)([\w:.-]+)((?:\s+[\w:.-]+="[^"]*")*)(\s*\/?>)|([^<]+)/g;
        var last = 0, m;
        while ((m = re.exec(text))) {
            if (m.index > last) pre.appendChild(document.createTextNode(text.slice(last, m.index)));
            if (m[5] != null) {
                pre.appendChild(m[5].trim() ? span('t-text', m[5]) : document.createTextNode(m[5]));
            } else {
                pre.appendChild(span('t-punct', m[1]));
                pre.appendChild(span('t-name', m[2]));
                if (m[3]) appendXmlAttrs(pre, m[3]);
                pre.appendChild(span('t-punct', m[4]));
            }
            last = re.lastIndex;
        }
        if (last < text.length) pre.appendChild(document.createTextNode(text.slice(last)));
    }
    function appendXmlAttrs(pre, str) {
        var re = /([\w:.-]+)(=)("[^"]*")/g, last = 0, m;
        while ((m = re.exec(str))) {
            if (m.index > last) pre.appendChild(document.createTextNode(str.slice(last, m.index)));
            pre.appendChild(span('t-attr', m[1]));
            pre.appendChild(span('t-punct', m[2]));
            pre.appendChild(span('t-str', m[3]));
            last = re.lastIndex;
        }
        if (last < str.length) pre.appendChild(document.createTextNode(str.slice(last)));
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
        var pre = el('pre', { className: 'codebox', text: 'Loading payload…' });
        body.appendChild(pre);
        panel.appendChild(body);
        var btns = head.querySelector('.dbtns');
        fetchRestconfPayload(p).then(function (value) {
            var text = JSON.stringify(value, null, 2);
            highlightInto(pre, text, 'json');
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

    function renderInlineDetail(panel, p) {
        var noData = isNoData(p);
        var lang = noData ? 'text' : detectLang(p.payload);
        var pretty = noData ? '' : formatPayload(p.payload, lang);
        var meta = (CAT_LABEL[p.category] || p.category) + ' · ' + p.pid
            + (p.status ? ' · ' + p.status : '') + (p.bytes ? ' · ' + fmtBytes(p.bytes) : '');
        var head = el('div', { className: 'dhead' }, [
            el('div', { className: 'dpath', text: p.path }),
            el('div', { className: 'dmeta' }, [
                document.createTextNode(meta),
                (!noData && lang !== 'text') ? el('span', { className: 'langbadge', text: lang.toUpperCase() }) : document.createTextNode('')
            ]),
            el('div', { className: 'dbtns' }, noData
                ? [copyBtn('Copy path', function () { return p.path; })]
                : [copyBtn('Copy payload', function () { return pretty; }),
                   copyBtn('Copy path', function () { return p.path; })])
        ]);
        panel.appendChild(head);
        if (p.once != null || p.sample != null || p.onchange != null) {
            panel.appendChild(subscribeModes(p));
        }
        var body = el('div', { className: 'body' });
        if (noData) {
            body.appendChild(el('div', { className: 'nodatanote',
                text: 'No data returned' + (p.status ? ' (status: ' + p.status + ')' : '')
                    + '. The path is supported but the datastore had nothing to return.' }));
        } else {
            var pre = el('pre', { className: 'codebox' });
            highlightInto(pre, pretty, lang);
            body.appendChild(pre);
        }
        panel.appendChild(body);
    }
    function subscribeModes(p) {
        function badge(name, st) {
            var cls = st === 'streamed' ? 'ok' : (st === 'accepted-nodata' ? 'warn' : 'no');
            return el('span', { className: 'modebadge mb-' + cls, text: name + ': ' + (st || 'n/a') });
        }
        return el('div', { className: 'submodes' }, [
            badge('ONCE', p.once), badge('SAMPLE', p.sample), badge('ON_CHANGE', p.onchange)
        ]);
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
        if (state.transport !== 'mdt') {
            var totBytes = (state.data.devices || []).reduce(function (s, d) { return s + (d.bytes || 0); }, 0);
            host.appendChild(tile(fmtBytes(totBytes), 'Response payload'));
        } else {
            host.appendChild(tile(fmt(t.records), 'Records'));
        }
        host.appendChild(tile(fmt(cats.length), 'Model flavors'));
        var ti = $('transportInfo');
        if (ti) {
            var gen = state.data.generated;
            ti.textContent = gen ? 'Captured ' + fmtAge(gen) : '';
            if (gen) { ti.title = 'Dataset generated ' + gen; } else { ti.removeAttribute('title'); }
        }
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
        var restconf = state.transport !== 'mdt';
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
        var restconf = state.transport !== 'mdt';
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
        var dfSel = $('dataFilter');
        if (dfSel) dfSel.addEventListener('change', function () {
            state.dataFilter = dfSel.value;
            renderList();
            updateSummary();
            renderTopChart();
        });
        var mg = $('matrixGaps');
        if (mg) mg.addEventListener('change', function () {
            state.matrixGaps = mg.checked;
            renderMatrix();
        });
        var mi = $('matrixInconsistent');
        if (mi) mi.addEventListener('change', function () {
            state.matrixInconsistent = mi.checked;
            renderMatrix();
        });
        var pmBtn = $('pivotMethods'); if (pmBtn) pmBtn.addEventListener('click', function () { setPivot('methods'); });
        var pdBtn = $('pivotDevices'); if (pdBtn) pdBtn.addEventListener('click', function () { setPivot('devices'); });
        var mmSel = $('matrixMethod');
        if (mmSel) mmSel.addEventListener('change', function () {
            state.matrixMethod = mmSel.value;
            renderMatrix();
        });
        buildTransportBar();
        var mt = $('matrixToggle');
        if (mt) mt.addEventListener('click', toggleMatrix);
        loadTransport(TRANSPORTS[0].key, true);
    }

    function fetchJson(url) {
        return fetch(url).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); });
    }
    function buildTransportBar() {
        var bar = $('transportBar'); clear(bar);
        TRANSPORTS.forEach(function (t) {
            bar.appendChild(el('button', {
                className: 'tbtn', attrs: { role: 'tab', 'data-key': t.key },
                onclick: function () { loadTransport(t.key, false); }
            }, [document.createTextNode(t.label + ' '), el('span', { className: 'tsub', text: t.sub })]));
        });
    }
    function transportDef(key) { return TRANSPORTS.filter(function (t) { return t.key === key; })[0]; }
    function setActiveBtn(key) {
        Array.prototype.forEach.call($('transportBar').querySelectorAll('.tbtn'), function (b) {
            b.classList.toggle('active', b.getAttribute('data-key') === key);
        });
    }
    function loadTransport(key, isInitial) {
        if (state.matrix) setMatrix(false);
        if (state.datasets[key]) { activateTransport(key); return; }
        var def = transportDef(key);
        clear($('browser'));
        $('browser').appendChild(el('div', { className: 'placeholder', text: 'Loading ' + def.label + '\u2026' }));
        fetchJson(def.url).then(function (data) {
            state.datasets[key] = data;
            activateTransport(key);
        }, function () {
            var btn = $('transportBar').querySelector('[data-key="' + key + '"]');
            if (btn) { btn.disabled = true; btn.title = 'No data captured for this method yet'; }
            if (isInitial) {
                var next = TRANSPORTS.filter(function (t) { return t.key !== key; })[0];
                if (next) { loadTransport(next.key, true); } else { clear($('browser')); $('emptyState').hidden = false; }
            } else {
                clear($('browser'));
                $('browser').appendChild(el('div', { className: 'placeholder', text: 'No data captured for ' + def.label + ' yet.' }));
            }
        });
    }
    function activateTransport(key) {
        state.transport = key;
        state.data = state.datasets[key];
        state.cat = 'all'; state.q = ''; state.sel = null;
        var sb = $('searchBox'); if (sb) sb.value = '';
        var jump = state.jump; state.jump = null;
        var d0 = (state.data.devices || [])[0];
        state.pid = (jump && jump.pid && (state.data.devices || []).some(function (x) { return x.pid === jump.pid; }))
            ? jump.pid : (d0 ? d0.pid : '');
        setActiveBtn(key);
        updateProv();
        renderSummary();
        render();
        if (jump) applyJump(jump);
    }
    // Open the example payload for a module behind a matrix cell.
    function jumpToPayload(methodKey, xpath, pid) {
        if (!transportDef(methodKey)) return;
        state.jump = { pid: pid, xpath: xpath };
        loadTransport(methodKey, false);
    }
    function applyJump(jump) {
        var term = jump.xpath || '';
        var container = term.split('/').pop().split(':').pop();
        var paths = devicePaths(state.pid);
        var match = paths.filter(function (p) { return p.path === term; })[0]
            || paths.filter(function (p) { return container && p.path.indexOf(container) !== -1; })[0];
        if (match) {
            state.sel = match.pid + '|' + match.path;
            state.dataFilter = 'all';
            var df = $('dataFilter'); if (df) df.value = 'all';
            renderList(); renderDetail();
            var selRow = $('browser').querySelector('.prow.sel');
            if (selRow && selRow.scrollIntoView) selRow.scrollIntoView({ block: 'center' });
        } else if (container) {
            state.q = container.toLowerCase();
            var sb = $('searchBox'); if (sb) sb.value = container;
            renderList(); updateSummary();
        }
    }

    // ---------- comparison / coverage view ----------
    // Precompute per loaded matrix: which (method,category) the fleet ever
    // returns data for (method "serves" that flavor), and which categories each
    // device has rows for (model present). Drives expected-vs-real gap calls.
    function matrixClass() {
        if (state.matrixClass) return state.matrixClass;
        var m = state.matrixData || {}, serves = {}, devCat = {};
        (m.rows || []).forEach(function (r) {
            (devCat[r.pid] || (devCat[r.pid] = {}))[r.category] = true;
            var cells = r.cells || {};
            Object.keys(cells).forEach(function (mk) {
                if (cells[mk] === 'data') (serves[mk] || (serves[mk] = {}))[r.category] = true;
            });
        });
        state.matrixClass = { serves: serves, devCat: devCat };
        return state.matrixClass;
    }
    // Glyph + tooltip for one cell, separating real (peer-relative) gaps from
    // expected blanks (method doesn't serve the flavor, or model absent).
    function cellInfo(row, methodKey, category) {
        var v = row && row.cells ? row.cells[methodKey] : null;
        var cls = matrixClass();
        var served = !!(cls.serves[methodKey] && cls.serves[methodKey][category]);
        if (v === 'data') return { cls: 'y', txt: '\u25cf', tip: 'returned data \u2014 click to open payload', data: true };
        if (v === 'ok') return { cls: 'ok', txt: '\u25d1', tip: 'supported \u00b7 returned no data (feature likely not configured on this device)' };
        if (v === 'no') return served
            ? { cls: 'no', txt: '\u2715', tip: 'tried \u00b7 rejected by this device \u2014 peers return data here (likely a real gap)', real: true }
            : { cls: 'no', txt: '\u2715', tip: 'tried \u00b7 not supported (this method does not serve this flavor)' };
        if (!row) return { cls: 'na', txt: '\u00b7', tip: 'model not present on this device (expected)' };
        if (served) return { cls: 'na', txt: '\u00b7', tip: 'not collected via this method \u2014 peers return data here (likely a real gap)', real: true };
        return { cls: 'na', txt: '\u00b7', tip: 'this method does not serve this flavor (expected)' };
    }
    function setMatrix(on) {
        state.matrix = on;
        var mv = $('matrixView'); if (mv) mv.hidden = !on;
        ['.charts', '.layout', '#mtiles', '#filterToolbar'].forEach(function (sel) {
            var n = document.querySelector(sel); if (n) n.style.display = on ? 'none' : '';
        });
        var mt = $('matrixToggle'); if (mt) mt.classList.toggle('active', on);
        if (on) { renderMatrix(); }
        else { var db = $('deviceBar'); if (db) db.style.display = ''; }
    }
    function toggleMatrix() { setMatrix(!state.matrix); }

    // (pid|module) -> row, for O(1) cell lookups across both pivots.
    function matrixIndex() {
        if (state.matrixIndex) return state.matrixIndex;
        var idx = {};
        ((state.matrixData || {}).rows || []).forEach(function (r) { idx[r.pid + '|' + r.module] = r; });
        state.matrixIndex = idx;
        return idx;
    }
    function methodDef(key) {
        return ((state.matrixData || {}).methods || []).filter(function (mm) { return mm.key === key; })[0];
    }
    function ensureMatrixMethod() {
        var methods = (state.matrixData || {}).methods || [];
        if (!methods.length) return;
        if (!state.matrixMethod || !methodDef(state.matrixMethod)) {
            state.matrixMethod = methodDef(state.transport) ? state.transport : methods[0].key;
        }
    }

    function renderMatrix() {
        var host = $('matrixWrap'); clear(host);
        if (!state.matrixData) {
            host.appendChild(el('div', { className: 'placeholder', text: 'Loading comparison matrix\u2026' }));
            fetchJson(MATRIX_URL).then(function (m) { state.matrixData = m; state.matrixIndex = null; state.matrixClass = null; renderMatrix(); },
                function () { clear(host); host.appendChild(el('div', { className: 'placeholder', text: 'protocol-matrix.json not available yet.' })); });
            return;
        }
        ensureMatrixMethod();
        renderMethodPicker();
        renderFleetOverview();
        renderFreshness();
        renderGapSummary();
        syncMatrixControls();
        if (state.matrixPivot === 'devices') { renderMatrixDevices(host); }
        else { renderMatrixMethods(host); }
    }

    // Show/hide the pivot-specific controls and the device tab bar.
    function syncMatrixControls() {
        var dev = state.matrixPivot === 'devices';
        var pm = $('pivotMethods'), pd = $('pivotDevices');
        if (pm) pm.classList.toggle('active', !dev);
        if (pd) pd.classList.toggle('active', dev);
        var mp = $('methodPickWrap'); if (mp) mp.hidden = !dev;
        var gw = $('gapsWrap'); if (gw) gw.hidden = dev;
        var iw = $('inconWrap'); if (iw) iw.hidden = !dev;
        var db = $('deviceBar'); if (db) db.style.display = dev ? 'none' : '';
    }
    function setPivot(p) {
        if (state.matrixPivot === p) return;
        state.matrixPivot = p;
        state.matrixCat = 'all';
        renderMatrix();
    }
    function renderMethodPicker() {
        var sel = $('matrixMethod'); if (!sel) return;
        var methods = (state.matrixData || {}).methods || [];
        if (sel.options.length !== methods.length) {
            clear(sel);
            methods.forEach(function (mm) { sel.appendChild(el('option', { text: mm.label, attrs: { value: mm.key } })); });
        }
        sel.value = state.matrixMethod;
    }
    function renderLegend(dev) {
        var host = $('mxlegend'); if (!host) return; clear(host);
        function item(cls, glyph, label) {
            return el('span', {}, [el('b', { className: 'lg lg-' + cls, text: glyph }), document.createTextNode(' ' + label)]);
        }
        host.appendChild(item('y', '\u25cf', 'returned data'));
        host.appendChild(item('ok', '\u25d1', 'supported \u00b7 no data (empty)'));
        host.appendChild(item('no', '\u2715', 'tried \u00b7 rejected / not supported'));
        host.appendChild(item('na', '\u00b7', 'not applicable (absent / not run)'));
        if (dev) {
            host.appendChild(el('span', {}, [
                el('span', { className: 'mxconsist warn', text: 'inconsistent' }),
                document.createTextNode(' devices that have this model disagree')
            ]));
        }
        host.appendChild(el('span', { className: 'mxhint', text: 'Tip: click a data cell to open its example payload.' }));
    }

    // ---- fleet overview: device x method heat-grid (# modules with data) ----
    function renderFleetOverview() {
        var host = $('fleetOverview'); if (!host) return; clear(host);
        var m = state.matrixData;
        var methods = m.methods || [], devices = m.devices || [];
        var counts = {};
        devices.forEach(function (d) { counts[d] = {}; methods.forEach(function (mm) { counts[d][mm.key] = { data: 0, ok: 0, no: 0 }; }); });
        (m.rows || []).forEach(function (r) {
            var c = counts[r.pid]; if (!c) return;
            methods.forEach(function (mm) {
                var v = (r.cells || {})[mm.key];
                if (v && c[mm.key][v] != null) c[mm.key][v] += 1;
            });
        });
        var maxData = 1;
        devices.forEach(function (d) { methods.forEach(function (mm) { maxData = Math.max(maxData, counts[d][mm.key].data); }); });
        var table = el('table', { className: 'fleet' });
        var hr = el('tr', {}, [el('th', { className: 'l', text: 'Device' })]);
        methods.forEach(function (mm) {
            var th = el('th', {}, [document.createTextNode(mm.label)]);
            if (mm.key === 'mdt') th.appendChild(el('span', { className: 'mdtmark', text: '\u2020', attrs: { title: 'MDT reflects each device\u2019s active subscription set, not its capability \u2014 counts are not directly comparable across devices.' } }));
            hr.appendChild(th);
        });
        table.appendChild(el('thead', {}, [hr]));
        var tb = el('tbody');
        devices.forEach(function (d) {
            var tr = el('tr', {}, [el('td', { className: 'l', text: d })]);
            methods.forEach(function (mm) {
                var cell = counts[d][mm.key];
                var td = el('td', {
                    className: 'heat' + (cell.data ? '' : ' zero'),
                    text: String(cell.data),
                    attrs: { title: d + ' \u00b7 ' + mm.label + ' \u2014 ' + cell.data + ' data \u00b7 ' + cell.ok + ' empty \u00b7 ' + cell.no + ' rejected (click to compare devices)' },
                    onclick: function () { state.matrixMethod = mm.key; setPivot('devices'); }
                });
                if (cell.data) { td.style.background = 'rgba(46,125,50,' + (0.10 + 0.55 * (cell.data / maxData)).toFixed(3) + ')'; }
                tr.appendChild(td);
            });
            tb.appendChild(tr);
        });
        table.appendChild(tb);
        host.appendChild(table);
        host.appendChild(el('div', { className: 'mdtnote', text: '\u2020 MDT = active subscription set, not capability; counts are not directly comparable across devices.' }));
    }

    // ---- data freshness per method (capture time; flags stale transports) ----
    function renderFreshness() {
        var host = $('freshLine'); if (!host) return; clear(host);
        var m = state.matrixData || {};
        var src = m.sources || {}, methods = m.methods || [];
        var times = [];
        methods.forEach(function (mm) { if (src[mm.key]) { var t = Date.parse(src[mm.key].generated); if (!isNaN(t)) times.push(t); } });
        if (!times.length) return;
        var newest = Math.max.apply(null, times);
        host.appendChild(el('span', { className: 'freshlbl', text: 'Captured:' }));
        methods.forEach(function (mm) {
            var s = src[mm.key]; if (!s) return;
            var t = Date.parse(s.generated); if (isNaN(t)) return;
            var olderH = (newest - t) / 3.6e6;
            var chip = el('span', {
                className: 'freshchip' + (olderH >= 6 ? ' warn' : (olderH >= 2 ? ' old' : '')),
                title: s.file + ' \u00b7 generated ' + s.generated + (olderH >= 1 ? ' (' + olderH.toFixed(0) + ' h older than the freshest transport)' : ' (freshest)')
            }, [document.createTextNode(mm.label + ' ')]);
            chip.appendChild(el('span', { className: 'fresha', text: fmtAge(s.generated) }));
            if (olderH >= 2) chip.appendChild(el('span', { className: 'freshd', text: '\u00b7 ' + olderH.toFixed(0) + ' h older' }));
            host.appendChild(chip);
        });
        host.appendChild(el('span', { className: 'freshnote', text: 'Older transports may under-report vs the freshest \u2014 re-capture for a fair comparison.' }));
    }

    // ---- gap summary: real (peer-relative) gaps vs expected blanks ----
    function renderGapSummary() {
        var host = $('gapSummary'); if (!host) return; clear(host);
        var m = state.matrixData; if (!m) return;
        var methods = m.methods || [], devices = m.devices || [], cls = matrixClass();
        var serves = cls.serves, devCat = cls.devCat;
        var dataCnt = {};
        devices.forEach(function (d) { dataCnt[d] = {}; methods.forEach(function (mm) { dataCnt[d][mm.key] = {}; }); });
        (m.rows || []).forEach(function (r) {
            var byM = dataCnt[r.pid]; if (!byM) return;
            var cells = r.cells || {};
            methods.forEach(function (mm) {
                if (cells[mm.key] === 'data') byM[mm.key][r.category] = (byM[mm.key][r.category] || 0) + 1;
            });
        });
        var gapRows = [];
        devices.forEach(function (d) {
            methods.forEach(function (mm) {
                var missing = [], total = 0;
                Object.keys(dataCnt[d][mm.key]).forEach(function (c) { total += dataCnt[d][mm.key][c]; });
                Object.keys(serves[mm.key] || {}).forEach(function (cat) {
                    if (!(devCat[d] && devCat[d][cat])) return;
                    if ((dataCnt[d][mm.key][cat] || 0) === 0) missing.push(cat);
                });
                if (missing.length) { missing.sort(); gapRows.push({ device: d, method: mm, missing: missing, full: total === 0 }); }
            });
        });
        gapRows.sort(function (a, b) { return (b.full ? 1 : 0) - (a.full ? 1 : 0) || b.missing.length - a.missing.length || a.device.localeCompare(b.device); });
        host.appendChild(el('h3', { className: 'gaph', text: 'Coverage gaps \u2014 what\u2019s missing, and why' }));
        if (!gapRows.length) {
            host.appendChild(el('div', { className: 'gapnote', text: 'No real gaps \u2014 every device returns data for every flavor its peers collect. Remaining blank cells are structural (see legend).' }));
            return;
        }
        host.appendChild(el('div', { className: 'gapnote', text: gapRows.length + ' device\u00d7method combinations return no data for a model flavor their peers do collect. Every other blank cell is expected (structural).' }));
        var table = el('table', { className: 'gaptbl' });
        table.appendChild(el('thead', {}, [el('tr', {}, [
            el('th', { text: 'Device' }), el('th', { text: 'Method' }), el('th', { text: 'Missing flavors (n = peers that do collect it)' })
        ])]));
        var tb = el('tbody');
        gapRows.forEach(function (g) {
            var chips = el('td', {});
            if (g.full) chips.appendChild(el('span', { className: 'gapfull', text: 'no data at all' }));
            g.missing.forEach(function (cat) {
                var peers = 0;
                devices.forEach(function (d) { if (d !== g.device && (dataCnt[d][g.method.key][cat] || 0) > 0) peers += 1; });
                chips.appendChild(el('span', {
                    className: 'gapchip',
                    title: peers + ' of ' + (devices.length - 1) + ' peer devices return ' + (CAT_LABEL[cat] || cat) + ' data via ' + g.method.label
                }, [
                    el('span', { className: 'catdot ' + catClass(cat) }),
                    document.createTextNode(' ' + (CAT_LABEL[cat] || cat) + ' '),
                    el('span', { className: 'gapn', text: String(peers) })
                ]));
            });
            tb.appendChild(el('tr', {}, [
                el('td', {}, [el('button', {
                    className: 'gaplink', text: g.device,
                    title: 'Open ' + g.method.label + ' across all devices',
                    onclick: function () { state.matrixMethod = g.method.key; if (state.matrixPivot === 'devices') renderMatrix(); else setPivot('devices'); }
                })]),
                el('td', { text: g.method.label }),
                chips
            ]));
        });
        table.appendChild(tb);
        host.appendChild(el('div', { className: 'gapwrap' }, [table]));
        host.appendChild(el('div', { className: 'gaphint', text: 'Expected blanks (not listed): the method doesn\u2019t serve that flavor (e.g. MIB isn\u2019t served over gNMI; get-config returns only config models), or the model isn\u2019t present on the device (e.g. wireless only on C9800). MDT reflects each device\u2019s active subscription set, not its capability.' }));
    }

    function moduleLabelCell(row, meta) {
        var kids = [el('span', { className: 'catdot ' + catClass(row.category) }), document.createTextNode(' ' + row.module)];
        if (meta) {
            kids.push(el('span', { className: 'mxcount', text: meta.dataN + '/' + ((state.matrixData || {}).devices || []).length }));
            if (meta.inconsistent) kids.push(el('span', { className: 'mxconsist warn', text: 'inconsistent' }));
        }
        return el('td', { className: 'l', title: row.category }, kids);
    }
    function dataCell(row, methodKey, pid, category) {
        var info = cellInfo(row, methodKey, category);
        if (info.data && row && row.xpath && transportDef(methodKey)) {
            return el('td', {
                className: info.cls + ' link', text: info.txt,
                attrs: { title: info.tip },
                onclick: function () { jumpToPayload(methodKey, row.xpath, pid); }
            });
        }
        return el('td', { className: info.cls + (info.real ? ' gap' : ''), text: info.txt, attrs: { title: info.tip } });
    }

    // ---- pivot A: modules x methods for one device ----
    function renderMatrixMethods(host) {
        renderLegend(false);
        var m = state.matrixData, methods = m.methods || [];
        var allRows = (m.rows || []).filter(function (r) { return r.pid === state.pid; });
        renderMatrixChips(allRows);
        var rows = allRows.filter(function (r) { return state.matrixCat === 'all' || r.category === state.matrixCat; });
        if (state.matrixGaps) {
            rows = rows.filter(function (r) { return !methods.some(function (mm) { return (r.cells || {})[mm.key] === 'data'; }); });
        }
        rows.sort(function (a, b) { return (a.category || '').localeCompare(b.category || '') || a.module.localeCompare(b.module); });
        var info = $('matrixInfo');
        if (info) info.textContent = state.pid + ' \u00b7 ' + rows.length + ' modules \u00d7 ' + methods.length + ' methods'
            + (state.matrixGaps ? ' \u00b7 only models with NO data from any method' : '');
        var table = el('table', { className: 'mx' });
        var hr = el('tr', {}, [el('th', { className: 'l', text: 'YANG module' })]);
        methods.forEach(function (mm) { hr.appendChild(el('th', { text: mm.label })); });
        table.appendChild(el('thead', {}, [hr]));
        var tbody = el('tbody');
        rows.forEach(function (r) {
            var tr = el('tr', {}, [moduleLabelCell(r)]);
            methods.forEach(function (mm) { tr.appendChild(dataCell(r, mm.key, r.pid, r.category)); });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        host.appendChild(table);
    }

    // ---- pivot B: modules x devices for one method (cross-device coverage) ----
    function renderMatrixDevices(host) {
        renderLegend(true);
        var m = state.matrixData, devices = m.devices || [], method = state.matrixMethod, idx = matrixIndex();
        var modMeta = {};
        (m.rows || []).forEach(function (r) {
            if (!(r.cells || {}).hasOwnProperty(method)) return;
            var meta = modMeta[r.module] || (modMeta[r.module] = { module: r.module, category: r.category });
            if ((!meta.category || meta.category === 'other') && r.category) meta.category = r.category;
        });
        var modules = Object.keys(modMeta).map(function (k) { return modMeta[k]; });
        renderMatrixChips(modules);
        if (state.matrixCat !== 'all') modules = modules.filter(function (x) { return x.category === state.matrixCat; });
        modules.forEach(function (x) {
            var statuses = [], dataN = 0;
            devices.forEach(function (d) {
                var row = idx[d + '|' + x.module];
                var v = row && row.cells ? row.cells[method] : null;
                if (v) { statuses.push(v); if (v === 'data') dataN += 1; }
            });
            x.dataN = dataN;
            var distinct = {}; statuses.forEach(function (s) { distinct[s] = 1; });
            x.inconsistent = Object.keys(distinct).length >= 2;
        });
        if (state.matrixInconsistent) modules = modules.filter(function (x) { return x.inconsistent; });
        modules.sort(function (a, b) {
            return (b.inconsistent ? 1 : 0) - (a.inconsistent ? 1 : 0)
                || (a.category || '').localeCompare(b.category || '')
                || a.module.localeCompare(b.module);
        });
        var inconN = modules.filter(function (x) { return x.inconsistent; }).length;
        var info = $('matrixInfo');
        if (info) info.textContent = ((methodDef(method) || {}).label || method) + ' \u00b7 ' + modules.length
            + ' modules \u00d7 ' + devices.length + ' devices \u00b7 ' + inconN + ' inconsistent'
            + (state.matrixInconsistent ? ' (showing inconsistent only)' : '');
        var table = el('table', { className: 'mx' });
        var hr = el('tr', {}, [el('th', { className: 'l', text: 'YANG module' })]);
        devices.forEach(function (d) { hr.appendChild(el('th', { text: d })); });
        table.appendChild(el('thead', {}, [hr]));
        var tbody = el('tbody');
        modules.forEach(function (x) {
            var tr = el('tr', x.inconsistent ? { className: 'incon' } : {}, [moduleLabelCell(x, x)]);
            devices.forEach(function (d) { tr.appendChild(dataCell(idx[d + '|' + x.module], method, d, x.category)); });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        host.appendChild(table);
    }

    function renderMatrixChips(items) {
        var wrap = $('matrixChips'); if (!wrap) return; clear(wrap);
        var counts = {};
        items.forEach(function (r) { counts[r.category] = (counts[r.category] || 0) + 1; });
        wrap.appendChild(matrixChip('all', 'All flavors', items.length));
        Object.keys(counts).sort().forEach(function (c) {
            wrap.appendChild(matrixChip(c, CAT_LABEL[c] || c, counts[c]));
        });
    }
    function matrixChip(cat, label, n) {
        var active = state.matrixCat === cat;
        var kids = [];
        if (cat !== 'all') kids.push(el('span', { className: 'catdot ' + catClass(cat) }));
        kids.push(document.createTextNode(label + ' '));
        kids.push(el('span', { className: 'n', text: '(' + fmt(n) + ')' }));
        return el('button', {
            className: 'chip' + (active ? ' active ' + catClass(cat) : ''),
            onclick: function () { state.matrixCat = cat; renderMatrix(); }
        }, kids);
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
