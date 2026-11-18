/* deprecations.js — "Deprecated & obsolete YANG elements" page.
 * Data (built by scripts/build_deprecations.py):
 *   releases/index.json                               release list
 *   releases/<ver>/deprecations/index.json            totals, categories, modules, validation
 *   releases/<ver>/deprecations/modules/<module>.json on demand: nodes + statements of one module
 *   releases/<ver>/deprecations/changes.json          on demand: changes since the previous release
 * DOM is built with textContent only. */
(function () {
    'use strict';

    var SAFE_NAME = /^[A-Za-z0-9._-]+$/;
    var SPEC_URL = /^(swagger-[a-z-]+-model)\/index\.html#spec=([A-Za-z0-9._-]+)$/;
    var PAGE = 300;
    var FLAGGED = ['deprecated', 'obsolete'];
    var CATEGORY_LABELS = {
        native: 'Native config (Cisco-IOS-XE-native)', 'native-aug': 'Native config augments',
        oper: 'Operational', cfg: 'Config (-cfg)', rpc: 'RPC', 'rpc-aug': 'RPC augments',
        mib: 'MIB', ietf: 'IETF / IANA', openconfig: 'OpenConfig', events: 'Events',
        types: 'Types', common: 'Common', deviation: 'Deviation', submodule: 'Submodule', other: 'Other'
    };
    var CHANGE_LABELS = {
        'newly-deprecated': 'Newly deprecated', 'newly-obsolete': 'Newly obsolete',
        'added-deprecated': 'Added as deprecated', 'added-obsolete': 'Added as obsolete',
        escalated: 'Deprecated → obsolete', relaxed: 'Obsolete → deprecated',
        'now-current': 'Now current', removed: 'Removed'
    };
    var BUCKET_LABELS = {
        'schema-node': 'Schema node',
        definition: 'Definition (not a schema node)',
        instantiation: 'uses / augment — inherited by the nodes it adds',
        extension: 'SMIv2 alias (no YANG data node)',
        unreached: 'Not in the schema tree',
        unexplained: 'Unexplained'
    };

    var state = {
        releases: [], ver: null, index: null, shards: {}, changes: null, changesVer: null,
        expanded: null, changeLimit: PAGE, pendingModule: null
    };

    // ------------------------------------------------------------------ helpers

    function el(tag, attrs, text) {
        var node = document.createElement(tag);
        if (attrs) {
            Object.keys(attrs).forEach(function (key) {
                if (key === 'className') node.className = attrs[key];
                else node.setAttribute(key, attrs[key]);
            });
        }
        if (text !== undefined && text !== null) node.textContent = String(text);
        return node;
    }

    function fmt(n) { return Number(n || 0).toLocaleString(); }
    function $(id) { return document.getElementById(id); }
    function categoryLabel(c) { return CATEGORY_LABELS[c] || c || '—'; }
    function changeLabel(t) { return CHANGE_LABELS[t] || t; }
    function base(ver) { return 'releases/' + encodeURIComponent(ver) + '/deprecations/'; }
    function sum(obj) { return Object.keys(obj || {}).reduce(function (a, k) { return a + (obj[k] || 0); }, 0); }

    function fetchJson(url) {
        return fetch(url).then(function (r) {
            if (!r.ok) throw new Error(url + ' → HTTP ' + r.status);
            return r.json();
        });
    }

    function readHash() {
        var out = {};
        (location.hash || '').replace(/^#/, '').split('&').forEach(function (part) {
            var i = part.indexOf('=');
            if (i > 0) {
                try { out[decodeURIComponent(part.slice(0, i))] = decodeURIComponent(part.slice(i + 1)); }
                catch (_) { /* ignore malformed */ }
            }
        });
        return out;
    }

    function writeHash() {
        var params = { ver: state.ver };
        var extra = {
            status: $('statusFilter').value, category: $('categoryFilter').value,
            q: $('searchBox').value.trim(), changed: $('changedOnly').checked ? '1' : '',
            module: state.expanded || '', view: $('changeView').value === 'node' ? 'node' : '',
            change: $('changeType').value, instances: $('hideInstances').checked ? '' : 'show'
        };
        Object.keys(extra).forEach(function (k) { if (extra[k]) params[k] = extra[k]; });
        history.replaceState(null, '', '#' + Object.keys(params).map(function (k) {
            return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]);
        }).join('&'));
    }

    function badge(cls, text) { return el('span', { className: 'badge ' + cls }, text); }

    // Same-named siblings (e.g. two augments of one MIB table) carry an ordinal.
    function statementLabel(s) {
        return s.keyword + ' ' + (s.name || '') + (s.ordinal ? ' (#' + (s.ordinal + 1) + ')' : '');
    }

    function moreButton(host, shown, total, onMore) {
        host.replaceChildren();
        if (shown >= total) return;
        var btn = el('button', { type: 'button', className: 'more' },
            'Show ' + fmt(Math.min(PAGE, total - shown)) + ' more (' + fmt(total - shown) + ' remaining)');
        btn.addEventListener('click', onMore);
        host.appendChild(btn);
    }

    // ---------------------------------------------------------- summary views

    function renderSource() {
        var idx = state.index, src = idx.source || {}, v = idx.validation || {};
        var line = $('sourceLine');
        line.replaceChildren();
        var parts = ['Source: '];
        if (src.yangmodels_path) parts.push('YangModels ' + src.yangmodels_path + ' ');
        if (src.yangmodels_commit_sha) parts.push('@' + String(src.yangmodels_commit_sha).slice(0, 8) + ' ');
        parts.push('· ' + fmt(src.yang_files) + ' YANG files (content sha256 ' + String(src.content_sha256 || '').slice(0, 12) + ')');
        parts.push(' · ' + fmt(src.deviation_files_not_applied) + ' deviation modules not applied');
        parts.push(' · pyang ' + (src.pyang_version || '?') + ' · generated ' + String(idx.generated || '').slice(0, 10) + ' · ');
        line.appendChild(document.createTextNode(parts.join('')));
        var unexplained = (v.unexplained || []).length;
        var mismatches = (v.lexical_vs_parsed_mismatches || []).length;
        var check = fmt(v.flagged_statements) + ' status statements found by tokenizer and parser (' +
            fmt(mismatches) + ' disagreements), ' + fmt(unexplained) + ' unexplained';
        if (v.tree_check) {
            check += '; pyang tree markers x=' + fmt(v.tree_check.tree_deprecated) + ' o=' +
                fmt(v.tree_check.tree_obsolete) + ', ' + fmt(Object.keys(v.tree_check.mismatched_modules || {}).length) +
                ' modules differ';
        }
        line.appendChild(el('span', { className: v.passed ? 'ok' : 'fail' },
            (v.passed ? 'Checks passed: ' : 'Checks FAILED: ') + check));
    }

    function scope() {
        var cat = $('categoryFilter').value;
        return cat && state.index.by_category[cat] ? state.index.by_category[cat] : state.index.totals;
    }

    function changeScope() {
        var ch = state.index.changes;
        if (!ch || !ch.summary) return null;
        var cat = $('categoryFilter').value;
        if (!cat) return ch.summary;
        return (ch.by_category || {})[cat] || { statements: {}, nodes: {}, nodes_new_instance: 0 };
    }

    function renderCards() {
        var s = scope(), host = $('cards'), status = $('statusFilter').value;
        host.replaceChildren();
        var cards = [];
        FLAGGED.forEach(function (st) {
            if (status && status !== st) return;
            var t = s[st] || {};
            cards.push([st, fmt(t.statements), st + ' statements']);
            cards.push([st, fmt(t.top_most_nodes), 'top-most ' + st + ' nodes']);
            cards.push([st, fmt(t.effective_nodes), 'all ' + st + ' nodes (' + fmt(t.effective_leafs) + ' leafs)']);
        });
        cards.push(['', fmt(s.modules), 'modules with findings']);
        var ch = changeScope();
        if (ch) {
            var st = ch.statements || {}, from = state.index.changes.from;
            cards.push(['deprecated', fmt((st['newly-deprecated'] || 0) + (st['added-deprecated'] || 0)),
                'statements newly deprecated since ' + from]);
            cards.push(['obsolete', fmt((st['newly-obsolete'] || 0) + (st['added-obsolete'] || 0) + (st.escalated || 0)),
                'statements newly obsolete since ' + from + ' (' + fmt(st.escalated) + ' were deprecated)']);
        }
        cards.forEach(function (c) {
            var card = el('div', { className: 'stat ' + c[0] });
            card.appendChild(el('div', { className: 'num' }, c[1]));
            card.appendChild(el('div', { className: 'lbl' }, c[2]));
            host.appendChild(card);
        });
    }

    function populateCategories(keep) {
        var select = $('categoryFilter');
        select.replaceChildren(el('option', { value: '' }, 'All'));
        Object.keys(state.index.by_category).sort().forEach(function (c) {
            select.appendChild(el('option', { value: c }, categoryLabel(c)));
        });
        select.value = state.index.by_category[keep] ? keep : '';
    }

    function renderCategories() {
        var tbody = $('categoryRows'), selected = $('categoryFilter').value;
        tbody.replaceChildren();
        var cats = state.index.by_category;
        var names = Object.keys(cats).filter(function (c) {
            return FLAGGED.some(function (st) { return cats[c][st].statements || cats[c][st].effective_nodes; });
        }).sort(function (a, b) {
            return (cats[b].deprecated.effective_nodes + cats[b].obsolete.effective_nodes) -
                (cats[a].deprecated.effective_nodes + cats[a].obsolete.effective_nodes) ||
                (cats[b].deprecated.statements + cats[b].obsolete.statements) -
                (cats[a].deprecated.statements + cats[a].obsolete.statements);
        });
        names.concat(['__total']).forEach(function (c) {
            var e = c === '__total' ? state.index.totals : cats[c];
            var tr = el('tr', c === '__total' ? null : { className: 'clickable' + (c === selected ? ' selected' : ''), tabindex: '0' });
            var name = el('td');
            if (c === '__total') name.appendChild(el('strong', null, 'Total'));
            else {
                name.appendChild(document.createTextNode(categoryLabel(c) + ' '));
                name.appendChild(el('code', { className: 'muted' }, c));
            }
            tr.appendChild(name);
            tr.appendChild(el('td', { className: 'num' }, fmt(e.modules)));
            FLAGGED.forEach(function (st) {
                ['statements', 'top_most_nodes', 'effective_nodes'].forEach(function (k) {
                    tr.appendChild(el('td', { className: 'num ' + (st === 'deprecated' ? 'dep' : 'obs') }, fmt(e[st][k])));
                });
            });
            if (c !== '__total') {
                var pick = function () {
                    $('categoryFilter').value = selected === c ? '' : c;
                    onFilterChange();
                };
                tr.addEventListener('click', pick);
                tr.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); pick(); } });
            }
            tbody.appendChild(tr);
        });
    }

    // ----------------------------------------------------------------- modules

    function moduleTotals(m, status) {
        var sts = status ? [status] : FLAGGED;
        return sts.reduce(function (acc, st) {
            var t = m[st] || {};
            acc.statements += t.statements || 0;
            acc.top += t.top_most_nodes || 0;
            acc.nodes += t.effective_nodes || 0;
            return acc;
        }, { statements: 0, top: 0, nodes: 0 });
    }

    function changeCount(m) {
        return m.changes ? sum(m.changes.statements) + sum(m.changes.nodes) : 0;
    }

    function filteredModules() {
        var status = $('statusFilter').value, cat = $('categoryFilter').value;
        var q = $('searchBox').value.trim().toLowerCase(), changed = $('changedOnly').checked;
        var mods = state.index.by_module;
        var names = Object.keys(mods).filter(function (name) {
            var m = mods[name], t = moduleTotals(m, status);
            if (cat && m.category !== cat) return false;
            if (q && name.toLowerCase().indexOf(q) < 0) return false;
            if (changed) return changeCount(m) > 0;
            return t.statements + t.nodes > 0;
        });
        var sort = $('sortSelect').value;
        var key = {
            nodes: function (n) { return moduleTotals(mods[n], status).nodes; },
            top: function (n) { return moduleTotals(mods[n], status).top; },
            statements: function (n) { return moduleTotals(mods[n], status).statements; },
            changes: function (n) { return changeCount(mods[n]); }
        }[sort];
        names.sort(function (a, b) { return (key ? key(b) - key(a) : 0) || a.localeCompare(b); });
        return names;
    }

    function moduleLinks(name, m) {
        var links = el('div', { className: 'links' });
        var match = SPEC_URL.exec(m.spec_url || '');
        if (match) {
            links.appendChild(el('a', { href: match[1] + '/index.html#ver=' + encodeURIComponent(state.ver) + '&spec=' + match[2] }, 'Spec'));
        }
        if (m.has_tree && SAFE_NAME.test(name)) {
            links.appendChild(el('a', { href: 'releases/' + encodeURIComponent(state.ver) + '/yang-trees/' + name + '.html' }, 'Tree'));
        }
        if (SAFE_NAME.test(name)) links.appendChild(el('a', { href: 'release-compare.html#module=' + encodeURIComponent(name) }, 'History'));
        return links;
    }

    function triple(m, st) {
        var t = m[st] || {};
        return fmt(t.statements) + ' / ' + fmt(t.top_most_nodes) + ' / ' + fmt(t.effective_nodes);
    }

    function changesText(m) {
        if (!m.changes) return '—';
        var parts = [];
        var s = m.changes.statements || {}, n = m.changes.nodes || {};
        Object.keys(s).forEach(function (k) { parts.push(fmt(s[k]) + ' ' + changeLabel(k).toLowerCase()); });
        var nodes = sum(n);
        if (nodes) parts.push(fmt(nodes) + ' node changes');
        return parts.join(', ');
    }

    function renderModules() {
        var tbody = $('moduleRows');
        tbody.replaceChildren();
        var names = filteredModules(), mods = state.index.by_module;
        $('moduleCount').textContent = fmt(names.length) + ' modules';
        if (!names.length) {
            var empty = el('tr');
            empty.appendChild(el('td', { colspan: '6', className: 'empty' }, 'No modules match these filters.'));
            tbody.appendChild(empty);
            return;
        }
        names.forEach(function (name) {
            var m = mods[name];
            var tr = el('tr', { 'data-module': name });
            var toggleCell = el('td');
            var toggle = el('button', { type: 'button', className: 'expand', 'aria-expanded': 'false',
                'aria-label': 'Show details for ' + name }, '+');
            toggle.addEventListener('click', function () { toggleDetail(tr, toggle, name); });
            toggleCell.appendChild(toggle);
            tr.appendChild(toggleCell);
            var nameCell = el('td');
            nameCell.appendChild(el('code', null, name));
            nameCell.appendChild(moduleLinks(name, m));
            tr.appendChild(nameCell);
            tr.appendChild(el('td', null, categoryLabel(m.category)));
            tr.appendChild(el('td', { className: 'num dep' }, triple(m, 'deprecated')));
            tr.appendChild(el('td', { className: 'num obs' }, triple(m, 'obsolete')));
            tr.appendChild(el('td', { className: 'desc' }, changesText(m)));
            tbody.appendChild(tr);
            if (state.expanded === name) toggleDetail(tr, toggle, name, true);
        });
    }

    function toggleDetail(tr, toggle, name, forceOpen) {
        var next = tr.nextElementSibling;
        var open = next && next.classList.contains('detail');
        if (open && !forceOpen) {
            next.remove();
            toggle.textContent = '+';
            toggle.setAttribute('aria-expanded', 'false');
            if (state.expanded === name) state.expanded = null;
            writeHash();
            return;
        }
        if (open) return;
        document.querySelectorAll('#moduleRows tr.detail').forEach(function (row) {
            var owner = row.previousElementSibling;
            row.remove();
            var btn = owner && owner.querySelector('button.expand');
            if (btn) { btn.textContent = '+'; btn.setAttribute('aria-expanded', 'false'); }
        });
        state.expanded = name;
        writeHash();
        toggle.textContent = '−';
        toggle.setAttribute('aria-expanded', 'true');
        var detail = el('tr', { className: 'detail' });
        var cell = el('td', { colspan: '6' });
        cell.appendChild(el('p', { className: 'muted' }, 'Loading ' + name + '…'));
        detail.appendChild(cell);
        tr.after(detail);
        loadShard(name).then(function (shard) {
            renderDetail(cell, shard);
        }).catch(function (err) {
            cell.replaceChildren(el('p', { className: 'empty' }, 'Could not load details: ' + err.message));
        });
    }

    function loadShard(name) {
        if (!SAFE_NAME.test(name)) return Promise.reject(new Error('invalid module name'));
        var key = state.ver + '/' + name;
        if (!state.shards[key]) {
            state.shards[key] = fetchJson(base(state.ver) + 'modules/' + name + '.json');
        }
        return state.shards[key];
    }

    function renderDetail(cell, shard) {
        cell.replaceChildren();
        var cols = {};
        (shard.node_columns || []).forEach(function (c, i) { cols[c] = i; });

        cell.appendChild(el('h3', null, 'Schema nodes'));
        var controls = el('div', { className: 'controls' });
        var nestedLabel = el('label');
        var nested = el('input', { type: 'checkbox' });
        nestedLabel.appendChild(nested);
        nestedLabel.appendChild(document.createTextNode(' Include nodes inside an already-flagged subtree'));
        var filter = el('input', { type: 'search', placeholder: 'Filter paths…', 'aria-label': 'Filter node paths' });
        controls.appendChild(nestedLabel);
        controls.appendChild(filter);
        var count = el('span', { className: 'note' });
        controls.appendChild(count);
        cell.appendChild(controls);
        var wrap = el('div', { className: 'table-wrap' });
        var table = el('table');
        var head = el('tr');
        ['Status', 'Schema path', 'Node', 'Data nodes below', 'Status comes from', 'Description'].forEach(function (h, i) {
            head.appendChild(el('th', { scope: 'col', className: i === 3 ? 'num' : '' }, h));
        });
        table.appendChild(el('thead')).appendChild(head);
        var body = el('tbody');
        table.appendChild(body);
        wrap.appendChild(table);
        cell.appendChild(wrap);
        var more = el('div');
        cell.appendChild(more);

        var limit = PAGE;
        function nodeRows() {
            var status = $('statusFilter').value, q = filter.value.trim().toLowerCase();
            return shard.nodes.filter(function (r) {
                var top = r[cols.top_most];
                if (!top && !nested.checked) return false;
                var st = top ? r[cols.effective] : r[cols.status];
                if (status && st !== status) return false;
                if (q && String(r[cols.path]).toLowerCase().indexOf(q) < 0) return false;
                return true;
            });
        }
        function draw() {
            var rows = nodeRows();
            body.replaceChildren();
            count.textContent = fmt(rows.length) + ' nodes';
            if (!rows.length) {
                var empty = el('tr');
                empty.appendChild(el('td', { colspan: '6', className: 'empty' }, 'No flagged schema nodes match.'));
                body.appendChild(empty);
            }
            rows.slice(0, limit).forEach(function (r) {
                var top = r[cols.top_most];
                var st = top ? r[cols.effective] : r[cols.status];
                var tr = el('tr');
                var stCell = el('td');
                stCell.appendChild(badge(st, st));
                if (!top) stCell.appendChild(el('div', { className: 'desc' }, 'inside ' + r[cols.effective] + ' subtree'));
                tr.appendChild(stCell);
                var p = el('td', { className: 'path' });
                p.appendChild(el('code', null, r[cols.path]));
                tr.appendChild(p);
                tr.appendChild(el('td', null, r[cols.keyword] + ' · ' + r[cols.kind]));
                tr.appendChild(el('td', { className: 'num' }, fmt(r[cols.descendants])));
                var from = el('td');
                from.appendChild(document.createTextNode(r[cols.via] || 'own status'));
                if (r[cols.file]) from.appendChild(el('div', { className: 'desc mono' }, r[cols.file] + ':' + r[cols.line]));
                tr.appendChild(from);
                tr.appendChild(el('td', { className: 'desc' }, r[cols.description] || ''));
                body.appendChild(tr);
            });
            moreButton(more, Math.min(limit, rows.length), rows.length, function () { limit += PAGE; draw(); });
        }
        nested.addEventListener('change', function () { limit = PAGE; draw(); });
        filter.addEventListener('input', function () { limit = PAGE; draw(); });
        draw();

        var items = shard.items || [];
        cell.appendChild(el('h3', null, 'Status statements in this module (' + fmt(items.length) + ')'));
        if (!items.length) {
            cell.appendChild(el('p', { className: 'note' },
                'None — the flagged nodes above come from groupings or augments defined in other modules.'));
            return;
        }
        var bucketSel = el('select', { 'aria-label': 'Statement kind' });
        bucketSel.appendChild(el('option', { value: '' }, 'All statements'));
        var buckets = {};
        items.forEach(function (it) { buckets[it.bucket] = (buckets[it.bucket] || 0) + 1; });
        Object.keys(buckets).sort().forEach(function (b) {
            bucketSel.appendChild(el('option', { value: b }, (BUCKET_LABELS[b] || b) + ' (' + fmt(buckets[b]) + ')'));
        });
        var ic = el('div', { className: 'controls' });
        ic.appendChild(bucketSel);
        cell.appendChild(ic);
        var iwrap = el('div', { className: 'table-wrap' });
        var itable = el('table');
        var ihead = el('tr');
        ['Status', 'Statement', 'Context', 'Kind', 'Where', 'Description'].forEach(function (h) {
            ihead.appendChild(el('th', { scope: 'col' }, h));
        });
        itable.appendChild(el('thead')).appendChild(ihead);
        var ibody = el('tbody');
        itable.appendChild(ibody);
        iwrap.appendChild(itable);
        cell.appendChild(iwrap);
        var imore = el('div');
        cell.appendChild(imore);
        var ilimit = PAGE;
        function drawItems() {
            var status = $('statusFilter').value, b = bucketSel.value;
            var rows = items.filter(function (it) {
                return (!status || it.status === status) && (!b || it.bucket === b);
            });
            ibody.replaceChildren();
            rows.slice(0, ilimit).forEach(function (it) {
                var tr = el('tr');
                var s = el('td');
                s.appendChild(badge(it.status, it.status));
                tr.appendChild(s);
                var stmt = el('td');
                stmt.appendChild(el('code', null, statementLabel(it)));
                tr.appendChild(stmt);
                tr.appendChild(el('td', { className: 'path desc mono' }, it.context || '—'));
                var kind = BUCKET_LABELS[it.bucket] || it.bucket;
                if (it.bucket === 'schema-node') {
                    kind += ' — ' + fmt(it.instances) + ' instance' + (it.instances === 1 ? '' : 's') +
                        (it.top_most_instances !== it.instances ? ', ' + fmt(it.top_most_instances) + ' top-most' : '');
                }
                if (it.reason) kind += ': ' + it.reason;
                tr.appendChild(el('td', { className: 'desc' }, kind));
                tr.appendChild(el('td', { className: 'desc mono' }, it.file + ':' + it.line));
                tr.appendChild(el('td', { className: 'desc' }, it.description || ''));
                ibody.appendChild(tr);
            });
            moreButton(imore, Math.min(ilimit, rows.length), rows.length, function () { ilimit += PAGE; drawItems(); });
        }
        bucketSel.addEventListener('change', function () { ilimit = PAGE; drawItems(); });
        drawItems();
    }

    // ----------------------------------------------------------------- changes

    function renderChangesIntro() {
        var ch = state.index.changes, note = $('changesNote');
        var available = !!(ch && ch.summary);
        $('changesControls').hidden = !available;
        $('changeHead').replaceChildren();
        $('changeRows').replaceChildren();
        $('changeMore').replaceChildren();
        if (!ch) {
            note.textContent = state.ver + ' is the oldest release tracked, so there is nothing to compare it with.';
            return;
        }
        if (!available) {
            note.textContent = 'The census for ' + ch.from + ' is not available, so changes cannot be computed.';
            return;
        }
        var s = ch.summary;
        note.textContent = 'Compared with ' + ch.from + ': ' + fmt(sum(s.statements)) + ' status statements changed and ' +
            fmt(sum(s.nodes)) + ' top-most schema nodes changed effective status (' + fmt(s.nodes_new_instance) +
            ' of them are new instances of definitions that were already flagged).' +
            (ch.previous_sources_parsed ? '' : ' The previous release\'s sources were not available, so "added" cannot be told apart from "newly".');
        populateChangeTypes();
        loadChanges();
    }

    function populateChangeTypes() {
        var ch = state.index.changes, view = $('changeView').value === 'node' ? 'nodes' : 'statements';
        var select = $('changeType'), keep = select.value;
        select.replaceChildren(el('option', { value: '' }, 'All'));
        Object.keys(ch.summary[view] || {}).sort().forEach(function (t) {
            select.appendChild(el('option', { value: t }, changeLabel(t) + ' (' + fmt(ch.summary[view][t]) + ')'));
        });
        select.value = (ch.summary[view] || {})[keep] ? keep : '';
        $('hideInstances').parentNode.hidden = view !== 'nodes';
    }

    function loadChanges() {
        if (state.changes && state.changesVer === state.ver) { renderChanges(); return; }
        var ver = state.ver;
        $('changeRows').replaceChildren(rowMessage(7, 'Loading changes…'));
        fetchJson(base(ver) + 'changes.json').then(function (data) {
            if (state.ver !== ver) return;
            state.changes = data;
            state.changesVer = ver;
            renderChanges();
        }).catch(function (err) {
            $('changeRows').replaceChildren(rowMessage(7, 'Could not load changes: ' + err.message));
        });
    }

    function rowMessage(span, text) {
        var tr = el('tr');
        tr.appendChild(el('td', { colspan: String(span), className: 'empty' }, text));
        return tr;
    }

    function renderChanges() {
        if (!state.changes) return;
        var view = $('changeView').value === 'node' ? 'node' : 'statement';
        var type = $('changeType').value, status = $('statusFilter').value, cat = $('categoryFilter').value;
        var q = $('searchBox').value.trim().toLowerCase(), hide = $('hideInstances').checked;
        var rows = state.changes.entries.filter(function (e) {
            if (e.element !== view) return false;
            if (type && e.type !== type) return false;
            if (cat && e.category !== cat) return false;
            if (q && e.module.toLowerCase().indexOf(q) < 0) return false;
            if (status && e.from !== status && e.to !== status) return false;
            if (view === 'node' && hide && e.cause === 'new-instance') return false;
            return true;
        });
        var head = el('tr');
        var cols = view === 'node'
            ? ['Change', 'Module', 'Schema path', 'Node', 'Status', 'Data nodes below', 'Cause']
            : ['Change', 'Module', 'Statement', 'Context', 'Status'];
        cols.forEach(function (h, i) { head.appendChild(el('th', { scope: 'col', className: h === 'Data nodes below' ? 'num' : '' }, h)); });
        $('changeHead').replaceChildren(head);
        var body = $('changeRows');
        body.replaceChildren();
        if (!rows.length) body.appendChild(rowMessage(cols.length, 'No changes match these filters.'));
        rows.slice(0, state.changeLimit).forEach(function (e) {
            var tr = el('tr');
            var c = el('td');
            c.appendChild(badge(e.type === 'removed' || e.type === 'now-current' || e.type === 'relaxed' ? e.type : 'change',
                changeLabel(e.type)));
            tr.appendChild(c);
            var m = el('td');
            var btn = el('button', { type: 'button', className: 'link' }, e.module);
            btn.addEventListener('click', function () { openModule(e.module); });
            m.appendChild(btn);
            tr.appendChild(m);
            var statusCell = el('td');
            statusCell.appendChild(badge(e.from || 'current', e.from || 'current'));
            statusCell.appendChild(document.createTextNode(' → '));
            statusCell.appendChild(e.to ? badge(e.to, e.to) : el('span', { className: 'muted' }, 'gone'));
            if (view === 'node') {
                var p = el('td', { className: 'path' });
                p.appendChild(el('code', null, e.path));
                tr.appendChild(p);
                tr.appendChild(el('td', null, e.keyword + ' · ' + e.kind));
                tr.appendChild(statusCell);
                tr.appendChild(el('td', { className: 'num' }, fmt(e.descendants)));
                tr.appendChild(el('td', { className: 'desc' }, e.cause === 'new-instance'
                    ? 'New instance of an already-flagged definition' : (e.cause ? 'Status statement changed' : '')));
            } else {
                var s = el('td');
                s.appendChild(el('code', null, statementLabel(e)));
                tr.appendChild(s);
                tr.appendChild(el('td', { className: 'path desc mono' }, e.context || '—'));
                tr.appendChild(statusCell);
            }
            body.appendChild(tr);
        });
        moreButton($('changeMore'), Math.min(state.changeLimit, rows.length), rows.length, function () {
            state.changeLimit += PAGE;
            renderChanges();
        });
    }

    function openModule(name) {
        $('changedOnly').checked = false;
        $('searchBox').value = name;
        state.expanded = name;
        onFilterChange();
        var row = document.querySelector('#moduleRows tr[data-module="' + (window.CSS && CSS.escape ? CSS.escape(name) : name) + '"]');
        if (row) row.scrollIntoView({ block: 'start' });
    }

    // -------------------------------------------------------------------- flow

    function renderAll() {
        renderSource();
        renderCards();
        renderCategories();
        renderModules();
        renderChangesIntro();
        var csv = $('csvLink');
        csv.href = base(state.ver) + 'deprecations.csv';
        csv.setAttribute('download', 'iosxe-' + state.ver + '-deprecations.csv');
    }

    function onFilterChange() {
        state.changeLimit = PAGE;
        renderCards();
        renderCategories();
        renderModules();
        renderChanges();
        writeHash();
    }

    function loadRelease(ver, hash) {
        state.ver = ver;
        state.index = null;
        state.changes = null;
        $('moduleRows').replaceChildren(rowMessage(6, 'Loading ' + ver + '…'));
        return fetchJson(base(ver) + 'index.json').then(function (idx) {
            if (state.ver !== ver) return;
            state.index = idx;
            populateCategories(hash ? hash.category : $('categoryFilter').value);
            renderAll();
            writeHash();
        });
    }

    function showError(message) {
        $('moduleRows').replaceChildren(rowMessage(6, message));
        $('sourceLine').textContent = '';
    }

    function init() {
        var hash = readHash();
        if (hash.status && FLAGGED.indexOf(hash.status) >= 0) $('statusFilter').value = hash.status;
        if (hash.q) $('searchBox').value = hash.q;
        if (hash.changed === '1') $('changedOnly').checked = true;
        if (hash.view === 'node') $('changeView').value = 'node';
        if (hash.instances === 'show') $('hideInstances').checked = false;
        if (hash.module && SAFE_NAME.test(hash.module)) state.expanded = hash.module;

        ['statusFilter', 'categoryFilter', 'changedOnly', 'sortSelect'].forEach(function (id) {
            $(id).addEventListener('change', onFilterChange);
        });
        $('searchBox').addEventListener('input', onFilterChange);
        $('changeView').addEventListener('change', function () {
            state.changeLimit = PAGE;
            populateChangeTypes();
            renderChanges();
            writeHash();
        });
        ['changeType', 'hideInstances'].forEach(function (id) {
            $(id).addEventListener('change', function () { state.changeLimit = PAGE; renderChanges(); writeHash(); });
        });
        $('releaseSelect').addEventListener('change', function (e) {
            state.expanded = null;
            loadRelease(e.target.value).catch(function (err) { showError(err.message); });
        });

        fetchJson('releases/index.json').then(function (index) {
            state.releases = (index.releases || []).filter(function (r) { return SAFE_NAME.test(r.ver); });
            if (!state.releases.length) throw new Error('No releases listed.');
            var select = $('releaseSelect');
            state.releases.forEach(function (r) {
                select.appendChild(el('option', { value: r.ver }, r.label || r.ver));
            });
            var wanted = state.releases.some(function (r) { return r.ver === hash.ver; }) ? hash.ver
                : (index['default'] || state.releases[0].ver);
            select.value = wanted;
            return loadRelease(wanted, hash);
        }).then(function () {
            if (hash.change && state.index && state.index.changes && state.index.changes.summary) {
                $('changeType').value = hash.change;
                renderChanges();
                writeHash();
            }
            if (state.expanded) {
                var row = document.querySelector('#moduleRows tr[data-module="' + state.expanded + '"]');
                if (row) row.scrollIntoView({ block: 'start' });
            }
        }).catch(function (err) { showError(err.message); });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
    // Our own updates use replaceState (no event); this catches edited URLs and in-page links.
    window.addEventListener('hashchange', function () { location.reload(); });
})();
