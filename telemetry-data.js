/* telemetry-data.js — interactive browser for REAL Model-Driven Telemetry (MDT)
 * streamed from physical Cisco Catalyst switches.
 *
 * Loads the committed dataset (telemetry-data.json, produced by
 * scripts/build_telemetry_dataset.py) and renders it as: coverage stat cards,
 * polling-tier tabs (HOT/WARM/COOL), a filterable subscription list, and a
 * per-subscription detail panel showing the exact metrics and sample values
 * that XPath produced.
 *
 * CSP note: this page ships a strict CSP (no 'unsafe-inline' for scripts), so
 * every DOM node is built with createElement / textContent — never innerHTML —
 * so no dataset- or URL-controlled string can reach a markup sink.
 */
(function () {
    'use strict';

    var DATA_URL = 'telemetry-data.json';
    var TIER_ORDER = ['hot', 'warm', 'cool'];
    var TIER_LABEL = { hot: 'HOT', warm: 'WARM', cool: 'COOL' };

    var state = {
        data: null,
        tier: 'all',        // all | hot | warm | cool
        status: 'all',      // all | produced | silent
        q: '',
        sel: null           // selected subscription id
    };

    // ---------- tiny DOM helpers (no innerHTML) ----------
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

    // ---------- hash (shareable deep links) ----------
    function readHash() {
        try {
            var params = new URLSearchParams(location.hash.replace(/^#/, ''));
            if (params.get('tier')) state.tier = params.get('tier');
            if (params.get('status')) state.status = params.get('status');
            if (params.get('sub')) state.sel = params.get('sub');
        } catch (e) { /* ignore malformed hash */ }
    }
    function writeHash() {
        var parts = [];
        if (state.tier !== 'all') parts.push('tier=' + encodeURIComponent(state.tier));
        if (state.status !== 'all') parts.push('status=' + encodeURIComponent(state.status));
        if (state.sel) parts.push('sub=' + encodeURIComponent(state.sel));
        var next = parts.length ? '#' + parts.join('&') : location.pathname;
        history.replaceState(null, '', next);
    }

    // ---------- filtering ----------
    function subscriptions() { return (state.data && state.data.subscriptions) || []; }

    function matches(sub) {
        if (state.tier !== 'all' && sub.tier !== state.tier) return false;
        if (state.status === 'produced' && !sub.produced) return false;
        if (state.status === 'silent' && sub.produced) return false;
        if (state.q) {
            var hay = (sub.name + ' ' + sub.yang_module + ' ' + sub.xpath + ' ' + sub.id).toLowerCase();
            if (hay.indexOf(state.q) === -1) return false;
        }
        return true;
    }

    // ---------- stat cards ----------
    function renderStatCards() {
        var wrap = $('statCards');
        clear(wrap);
        var t = state.data.totals || {};
        var pct = t.subscriptions ? Math.round((t.produced / t.subscriptions) * 100) : 0;
        var cards = [
            { lbl: 'Subscriptions', big: fmt(t.subscriptions), sub: 'defined' },
            { lbl: 'Streaming', big: fmt(t.produced), sub: pct + '% produced data', bar: pct },
            { lbl: 'Silent', big: fmt(t.silent), sub: 'feature not configured' },
            { lbl: 'Metrics', big: fmt(t.metrics), sub: 'distinct sampled' },
            { lbl: 'Data points', big: fmt(t.data_points), sub: 'in capture window' }
        ];
        cards.forEach(function (c) {
            var kids = [
                el('div', { className: 'lbl', text: c.lbl }),
                el('div', { className: 'big', text: c.big }),
                el('div', { className: 'sub', text: c.sub })
            ];
            if (c.bar != null) {
                kids.push(el('div', { className: 'bar' }, [
                    el('span', { attrs: { style: 'width:' + c.bar + '%' } })
                ]));
            }
            wrap.appendChild(el('div', { className: 'cvcard' }, kids));
        });
    }

    // ---------- tier tabs ----------
    function tierCount(tier) {
        return subscriptions().filter(function (s) { return tier === 'all' || s.tier === tier; }).length;
    }
    function renderTierTabs() {
        var wrap = $('tierTabs');
        clear(wrap);
        var tabs = [{ id: 'all', label: 'All tiers' }].concat(
            TIER_ORDER.map(function (tier) {
                var interval = (state.data.tiers[tier] || {}).interval_sec;
                return { id: tier, label: TIER_LABEL[tier] + (interval ? ' · ' + interval + 's' : '') };
            })
        );
        tabs.forEach(function (tab) {
            var btn = el('button', {
                className: 'tier-tab' + (state.tier === tab.id ? ' active' : ''),
                attrs: { role: 'tab', 'aria-selected': String(state.tier === tab.id) },
                onclick: function () { state.tier = tab.id; state.sel = null; refresh(); }
            }, [
                document.createTextNode(tab.label + ' '),
                el('span', { className: 'n', text: '(' + tierCount(tab.id) + ')' })
            ]);
            wrap.appendChild(btn);
        });
    }

    // ---------- status filter chips ----------
    function renderStatusFilter() {
        var wrap = $('statusFilter');
        clear(wrap);
        [
            { id: 'all', label: 'All' },
            { id: 'produced', label: 'Streaming' },
            { id: 'silent', label: 'Silent' }
        ].forEach(function (opt) {
            wrap.appendChild(el('button', {
                className: state.status === opt.id ? 'active' : '',
                text: opt.label,
                onclick: function () { state.status = opt.id; refresh(); }
            }));
        });
    }

    // ---------- subscription list ----------
    function renderList() {
        var wrap = $('browser');
        clear(wrap);
        var rows = subscriptions().filter(matches);
        $('browserCount').textContent = rows.length + ' of ' + subscriptions().length;
        if (!rows.length) {
            wrap.appendChild(el('div', { className: 'placeholder', text: 'No subscriptions match the current filters.' }));
            return;
        }
        rows.forEach(function (sub) {
            var pill = sub.produced
                ? el('span', { className: 'pill ' + sub.tier, text: TIER_LABEL[sub.tier] || sub.tier })
                : el('span', { className: 'pill silent', text: 'SILENT' });
            var right = sub.produced
                ? el('span', { className: 'pts', text: fmt(sub.data_points) + ' pts' })
                : el('span', { className: 'pts', text: '' });
            var row = el('div', {
                className: 'subrow' + (sub.produced ? '' : ' silent') + (state.sel === sub.id ? ' sel' : ''),
                onclick: function () { state.sel = sub.id; refresh(); }
            }, [
                el('span', { className: 'tierdot ' + sub.tier }),
                el('span', { className: 'id', text: '#' + sub.id }),
                el('span', { className: 'meta' }, [
                    el('div', { className: 'nm', text: sub.name }),
                    el('div', { className: 'mod', text: sub.yang_module })
                ]),
                pill,
                right
            ]);
            wrap.appendChild(row);
        });
    }

    // ---------- detail panel ----------
    function defRow(dl, label, value) {
        if (value == null || value === '') return;
        dl.appendChild(el('dt', { text: label }));
        dl.appendChild(el('dd', { text: value }));
    }

    function renderDetail() {
        var panel = $('detail');
        clear(panel);
        if (!state.sel) {
            panel.appendChild(el('div', { className: 'placeholder', text: 'Select a subscription on the left to view its streamed metrics.' }));
            return;
        }
        var sub = subscriptions().filter(function (s) { return s.id === state.sel; })[0];
        if (!sub) {
            panel.appendChild(el('div', { className: 'placeholder', text: 'Subscription not found.' }));
            return;
        }

        var title = el('div', { className: 'dtitle' }, [
            el('span', { className: 'tierdot ' + sub.tier }),
            document.createTextNode(sub.name),
            sub.produced
                ? el('span', { className: 'pill ' + sub.tier, text: TIER_LABEL[sub.tier] || sub.tier })
                : el('span', { className: 'pill silent', text: 'SILENT' })
        ]);

        var dl = el('dl');
        defRow(dl, 'Subscription', '#' + sub.id);
        defRow(dl, 'YANG module', sub.yang_module);
        defRow(dl, 'Polling tier', (TIER_LABEL[sub.tier] || sub.tier) + (sub.interval_sec ? ' · every ' + sub.interval_sec + 's' : ''));
        if (sub.produced) {
            defRow(dl, 'Data points', fmt(sub.data_points));
            defRow(dl, 'Telemetry messages', fmt(sub.telemetry_messages));
        } else {
            defRow(dl, 'Silent reason', sub.silent_reason || 'Feature not configured on the reference switches');
        }
        if (sub.expected_keys && sub.expected_keys.length) defRow(dl, 'Keys', sub.expected_keys.join(', '));
        if (sub.expected_dimensions && sub.expected_dimensions.length) defRow(dl, 'Dimensions', sub.expected_dimensions.join(', '));

        var head = el('div', { className: 'dhead' }, [
            title,
            el('div', { className: 'dpath', text: sub.xpath }),
            dl
        ]);
        panel.appendChild(head);

        var body = el('div', { className: 'body' });
        if (!sub.produced) {
            body.appendChild(el('div', {
                className: 'silentbox',
                text: 'This subscription streamed no data during the capture window because the underlying feature is not configured on the reference switches (' + (sub.silent_reason || 'feature not configured') + ').'
            }));
        } else if (!sub.metrics || !sub.metrics.length) {
            body.appendChild(el('div', { className: 'silentbox', text: 'No sampled metrics recorded for this subscription.' }));
        } else {
            body.appendChild(buildMetricsTable(sub.metrics));
        }
        panel.appendChild(body);
    }

    function buildMetricsTable(metrics) {
        var thead = el('thead', {}, [
            el('tr', {}, [
                el('th', { text: 'Metric' }),
                el('th', { text: 'Type' }),
                el('th', { text: 'Cardinality' }),
                el('th', { text: 'Sample values' })
            ])
        ]);
        var tbody = el('tbody');
        metrics.forEach(function (m) {
            var samples = el('div', { className: 'samp' });
            (m.samples || []).forEach(function (s) {
                var row = el('div', {}, [
                    el('span', { className: 'v', text: s.value }),
                    document.createTextNode('  '),
                    el('span', { className: 'l', text: s.label })
                ]);
                samples.appendChild(row);
            });
            tbody.appendChild(el('tr', { className: 'mclass-' + (m['class'] || 'content') }, [
                el('td', { className: 'leaf', text: m.leaf || m.name, title: m.name }),
                el('td', { text: m.type }),
                el('td', { className: 'card', text: fmt(m.cardinality) }),
                el('td', {}, [samples])
            ]));
        });
        return el('table', { className: 'mtable' }, [thead, tbody]);
    }

    // ---------- provenance line ----------
    function renderProvenance() {
        var d = state.data;
        var devices = (d.devices || []).length;
        var txt = d.platform + ' · IOS XE ' + d.os_version + ' · ' +
            devices + ' device' + (devices === 1 ? '' : 's') + ' · ' + d.transport;
        $('prov').textContent = txt;
    }

    // ---------- orchestration ----------
    function refresh() {
        renderTierTabs();
        renderStatusFilter();
        renderList();
        renderDetail();
        updateSummary();
        writeHash();
    }
    function updateSummary() {
        var shown = subscriptions().filter(matches).length;
        $('summary').textContent = shown + ' shown';
    }

    function init() {
        var search = $('searchBox');
        search.addEventListener('input', function () {
            state.q = search.value.trim().toLowerCase();
            renderList();
            updateSummary();
        });
        window.addEventListener('hashchange', function () {
            readHash();
            if (search) search.value = state.q;
            refresh();
        });

        fetch(DATA_URL)
            .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(function (data) {
                state.data = data;
                readHash();
                renderProvenance();
                renderStatCards();
                refresh();
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
