/* release-compare.js — "What changed between releases" page.
 * Data: releases/compare/index.json, releases/compare/<old>__<new>.json and
 * on-demand releases/compare/<old>__<new>/<module>.json (built by
 * scripts/build_release_compare.py). DOM is built with textContent only. */
(function () {
    'use strict';

    var SAFE_NAME = /^[A-Za-z0-9._-]+$/;
    var state = { pairs: [], data: null, pair: null, detailCache: {}, pairCache: {}, history: null, presence: null };

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

    function readHash() {
        var out = {};
        (location.hash || '').replace(/^#/, '').split('&').forEach(function (part) {
            var i = part.indexOf('=');
            if (i > 0) out[decodeURIComponent(part.slice(0, i))] = decodeURIComponent(part.slice(i + 1));
        });
        return out;
    }

    function writeHash() {
        var params = { pair: state.pair };
        var status = document.getElementById('statusFilter').value;
        var category = document.getElementById('categoryFilter').value;
        var query = document.getElementById('searchBox').value.trim();
        if (status) params.status = status;
        if (category) params.category = category;
        if (query) params.q = query;
        if (state.history) params.module = state.history;
        var hash = Object.keys(params).map(function (k) {
            return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]);
        }).join('&');
        history.replaceState(null, '', '#' + hash);
    }

    function fetchJson(url) {
        return fetch(url).then(function (r) {
            if (!r.ok) throw new Error(url + ' → HTTP ' + r.status);
            return r.json();
        });
    }

    function releaseFor(module) {
        return module.status === 'removed' ? state.data.old : state.data.new;
    }

    function specLink(spec, ver) {
        // spec.url looks like "swagger-oper-model/index.html#spec=<module>".
        var match = /^(swagger-[a-z-]+-model)\/index\.html#spec=([A-Za-z0-9._-]+)$/.exec(spec.url || '');
        if (!match) return null;
        return el('a', { href: match[1] + '/index.html#ver=' + encodeURIComponent(ver) + '&spec=' + match[2] }, spec.label);
    }

    function renderCards() {
        var s = state.data.summary;
        var host = document.getElementById('cards');
        host.replaceChildren();
        [
            ['', s.modules_before + ' → ' + s.modules_after, 'YANG modules'],
            ['added', '+' + s.added, 'modules added'],
            ['removed', '−' + s.removed, 'modules removed'],
            ['changed', s.changed, 'module files changed'],
            ['changed', s.changed_with_schema_delta, 'with schema changes'],
            ['added', '+' + s.nodes_added.toLocaleString(), 'schema nodes added'],
            ['removed', '−' + s.nodes_removed.toLocaleString(), 'schema nodes removed'],
            ['changed', s.nodes_changed.toLocaleString(), 'nodes changed (type, status…)']
        ].forEach(function (c) {
            var card = el('div', { className: 'stat ' + c[0] });
            card.appendChild(el('div', { className: 'num' }, c[1]));
            card.appendChild(el('div', { className: 'lbl' }, c[2]));
            host.appendChild(card);
        });

        var line = document.getElementById('sourceLine');
        line.replaceChildren();
        var sources = state.data.sources || {};
        [state.data.old, state.data.new].forEach(function (ver, i) {
            var src = sources[ver] || {};
            line.appendChild(document.createTextNode((i ? ' · ' : 'Source: ') + ver + ' = YangModels '
                + (src.yangmodels_path || '?') + (src.commit ? ' @' + String(src.commit).slice(0, 8) : '')));
        });
        if (state.data.overview_doc && /^https:\/\/github\.com\//.test(state.data.overview_doc)) {
            line.appendChild(document.createTextNode(' · '));
            line.appendChild(el('a', { href: state.data.overview_doc, target: '_blank', rel: 'noopener noreferrer' },
                'Source-level release overview (augments, groupings, deviations)'));
        }
    }

    function populateCategories() {
        var select = document.getElementById('categoryFilter');
        var keep = select.value;
        var cats = {};
        state.data.modules.forEach(function (m) { if (m.category) cats[m.category] = true; });
        select.replaceChildren(el('option', { value: '' }, 'All'));
        Object.keys(cats).sort().forEach(function (c) { select.appendChild(el('option', { value: c }, c)); });
        select.value = cats[keep] ? keep : '';
    }

    function filteredModules() {
        var status = document.getElementById('statusFilter').value;
        var category = document.getElementById('categoryFilter').value;
        var query = document.getElementById('searchBox').value.trim().toLowerCase();
        return state.data.modules.filter(function (m) {
            if (status === 'schema' && !m.schema_counts) return false;
            if (status && status !== 'schema' && m.status !== status) return false;
            if (category && m.category !== category) return false;
            if (query && m.name.toLowerCase().indexOf(query) < 0) return false;
            return true;
        });
    }

    function schemaCell(m) {
        var td = el('td', { className: 'num' });
        if (!m.schema_counts) {
            td.appendChild(el('span', { className: 'muted' }, m.status === 'changed' ? 'no node change' : '—'));
            return td;
        }
        var c = m.schema_counts;
        if (c.added) td.appendChild(el('span', { className: 'plus' }, '+' + c.added + ' '));
        if (c.removed) td.appendChild(el('span', { className: 'minus' }, '−' + c.removed + ' '));
        if (c.changed) td.appendChild(el('span', { className: 'tilde' }, '~' + c.changed));
        return td;
    }

    function renderModules() {
        var tbody = document.getElementById('moduleRows');
        tbody.replaceChildren();
        var rows = filteredModules();
        if (!rows.length) {
            var empty = el('tr');
            empty.appendChild(el('td', { colspan: '6', className: 'empty' }, 'No modules match these filters.'));
            tbody.appendChild(empty);
            return;
        }
        rows.forEach(function (m) {
            var tr = el('tr');
            var toggleCell = el('td');
            var toggle = el('button', { type: 'button', className: 'expand', 'aria-expanded': 'false',
                'aria-label': 'Show details for ' + m.name }, '+');
            toggle.addEventListener('click', function () { toggleDetail(tr, toggle, m); });
            toggleCell.appendChild(toggle);
            tr.appendChild(toggleCell);

            var nameCell = el('td');
            nameCell.appendChild(el('code', null, m.name));
            var links = el('div', { className: 'links' });
            var ver = releaseFor(m);
            (m.specs || []).forEach(function (spec) {
                var a = specLink(spec, ver);
                if (a) links.appendChild(a);
            });
            if (m.has_tree && SAFE_NAME.test(m.name)) {
                links.appendChild(el('a', { href: 'releases/' + encodeURIComponent(ver) + '/yang-trees/' + m.name + '.html' }, 'Tree'));
            }
            if (SAFE_NAME.test(m.name)) {
                var hist = el('button', { type: 'button', className: 'link' }, 'History');
                hist.addEventListener('click', function () { showHistory(m.name); });
                links.appendChild(hist);
            }
            if (links.childNodes.length) nameCell.appendChild(links);
            tr.appendChild(nameCell);

            var statusCell = el('td');
            statusCell.appendChild(el('span', { className: 'badge ' + m.status }, m.status));
            tr.appendChild(statusCell);
            tr.appendChild(el('td', null, m.category || '—'));
            tr.appendChild(el('td', { className: 'mono' },
                (m.revision_before || '—') + ' → ' + (m.revision_after || '—')));
            tr.appendChild(schemaCell(m));
            tbody.appendChild(tr);
        });
    }

    function nodeList(title, items, render) {
        var frag = document.createDocumentFragment();
        if (!items || !items.length) return frag;
        frag.appendChild(el('h3', null, title + ' (' + items.length + ')'));
        var ul = el('ul');
        items.slice(0, 300).forEach(function (item) { ul.appendChild(render(item)); });
        if (items.length > 300) ul.appendChild(el('li', { className: 'muted' }, '… ' + (items.length - 300) + ' more'));
        frag.appendChild(ul);
        return frag;
    }

    function subtreeItem(item) {
        var li = el('li');
        li.appendChild(el('code', null, item.path));
        var meta = [item.kind, item.type, item.status !== 'current' ? item.status : '']
            .filter(Boolean).join(', ');
        li.appendChild(el('span', { className: 'muted' }, ' ' + meta
            + (item.descendants ? ' · +' + item.descendants + ' nodes below' : '')));
        return li;
    }

    function changedItem(item) {
        var li = el('li');
        li.appendChild(el('code', null, item.path));
        Object.keys(item.changes).forEach(function (key) {
            var pair = item.changes[key];
            li.appendChild(el('span', { className: 'muted' }, ' · ' + key + ': ' + (pair[0] || '∅') + ' → ' + (pair[1] || '∅')));
        });
        return li;
    }

    function getDetail(pairId, name) {
        var key = pairId + '/' + name;
        if (state.detailCache[key]) return Promise.resolve(state.detailCache[key]);
        return fetchJson('releases/compare/' + encodeURIComponent(pairId) + '/' + name + '.json').then(function (detail) {
            state.detailCache[key] = detail;
            return detail;
        });
    }

    function fillDetail(cell, m, pairId) {
        cell.replaceChildren();
        (m.revision_notes || []).forEach(function (r) {
            var p = el('p');
            p.appendChild(el('strong', null, r.date + ': '));
            p.appendChild(document.createTextNode(r.note || '(no description)'));
            cell.appendChild(p);
        });
        if (!m.schema_counts) {
            if (!(m.revision_notes || []).length) cell.appendChild(el('p', { className: 'muted' }, 'No schema-node or revision change detected (file differs in descriptions or formatting).'));
            return;
        }
        if (!SAFE_NAME.test(m.name)) return;
        var loading = el('p', { className: 'muted' }, 'Loading schema changes…');
        cell.appendChild(loading);
        getDetail(pairId || state.pair, m.name).then(function (detail) {
            loading.remove();
            cell.appendChild(nodeList('Added', detail.added, subtreeItem));
            cell.appendChild(nodeList('Removed', detail.removed, subtreeItem));
            cell.appendChild(nodeList('Changed', detail.changed, changedItem));
        }).catch(function (err) {
            loading.textContent = 'Could not load details: ' + err.message;
        });
    }

    function toggleDetail(tr, button, m, pairId, colspan) {
        var next = tr.nextElementSibling;
        if (next && next.classList.contains('detail')) {
            next.remove();
            button.textContent = '+';
            button.setAttribute('aria-expanded', 'false');
            return;
        }
        var detailRow = el('tr', { className: 'detail' });
        var cell = el('td', { colspan: String(colspan || 6), className: 'detail' });
        detailRow.appendChild(cell);
        tr.after(detailRow);
        button.textContent = '−';
        button.setAttribute('aria-expanded', 'true');
        fillDetail(cell, m, pairId);
    }

    function moduleListDetails(names, label) {
        var td = el('td');
        if (!names.length) { td.appendChild(el('span', { className: 'muted' }, '—')); return td; }
        var details = el('details', { className: 'plat' });
        details.appendChild(el('summary', null, label + names.length));
        details.appendChild(el('div', { className: 'mono' }, names.join(', ')));
        td.appendChild(details);
        return td;
    }

    function renderPlatforms() {
        var tbody = document.getElementById('platformRows');
        tbody.replaceChildren();
        (state.data.platforms || []).forEach(function (p) {
            var tr = el('tr');
            var name = el('td');
            name.appendChild(el('strong', null, p.label));
            name.appendChild(el('span', { className: 'muted' }, ' (' + p.id + ')'));
            tr.appendChild(name);
            tr.appendChild(el('td', { className: 'num' }, p.before + ' → ' + p.after));
            tr.appendChild(moduleListDetails(p.added, '+'));
            tr.appendChild(moduleListDetails(p.removed, '−'));
            tbody.appendChild(tr);
        });
        if (!tbody.childNodes.length) {
            var empty = el('tr');
            empty.appendChild(el('td', { colspan: '4', className: 'empty' }, 'No platform data for this pair.'));
            tbody.appendChild(empty);
        }
    }

    function getPair(entry) {
        var id = entry.old + '__' + entry.new;
        if (state.pairCache[id]) return Promise.resolve(state.pairCache[id]);
        return fetchJson('releases/compare/' + encodeURIComponent(entry.file)).then(function (data) {
            state.pairCache[id] = data;
            return data;
        });
    }

    function loadPair(pairId) {
        var entry = state.pairs.filter(function (p) { return p.old + '__' + p.new === pairId; })[0] || state.pairs[0];
        state.pair = entry.old + '__' + entry.new;
        document.getElementById('pairSelect').value = state.pair;
        return getPair(entry).then(function (data) {
            state.data = data;
            populateCategories();
            renderCards();
            renderModules();
            renderPlatforms();
            writeHash();
        });
    }

    // ---------- Module history: one module across every release pair ----------

    function chronologicalPairs() {
        return state.pairs.slice().reverse();
    }

    function loadPresence() {
        if (state.presence) return Promise.resolve(state.presence);
        return fetchJson('accountability_compare.json').then(function (doc) {
            var map = {};
            (doc.matrix || []).forEach(function (row) { map[row.module] = row.by_version || {}; });
            state.presence = map;
            var list = document.getElementById('historyModules');
            var frag = document.createDocumentFragment();
            Object.keys(map).sort().forEach(function (name) { frag.appendChild(el('option', { value: name })); });
            list.replaceChildren(frag);
            return map;
        });
    }

    function buildTimeline(name, pairData) {
        var pairs = chronologicalPairs();
        var presence = (state.presence || {})[name] || null;
        var present = function (ver) { return presence && presence[ver] ? !!presence[ver].present : null; };
        var rows = [];
        var first = pairs[0].old;
        rows.push({ ver: first, pairId: null, entry: null, present: present(first) });
        pairs.forEach(function (p, i) {
            var entry = (pairData[i].modules || []).filter(function (m) { return m.name === name; })[0] || null;
            rows.push({ ver: p.new, pairId: p.old + '__' + p.new, entry: entry, present: present(p.new) });
        });
        // Fill gaps the presence matrix doesn't cover from the change events themselves.
        rows.forEach(function (r, i) {
            if (r.present !== null) return;
            var next = rows[i + 1] && rows[i + 1].entry;
            if (r.entry) r.present = r.entry.status !== 'removed';
            else if (next) r.present = next.status !== 'added';
            else r.present = i > 0 ? rows[i - 1].present : false;
        });
        // Node counts are only recorded on changes; carry them across unchanged releases.
        var nodes = rows.map(function (r, i) {
            if (r.entry && r.entry.nodes_after !== undefined && r.entry.status !== 'removed') return r.entry.nodes_after;
            var next = rows[i + 1] && rows[i + 1].entry;
            if (next && next.nodes_before !== undefined && next.status !== 'added') return next.nodes_before;
            return null;
        });
        for (var i = 1; i < rows.length; i++) if (nodes[i] === null && rows[i].present && !rows[i].entry) nodes[i] = nodes[i - 1];
        for (var j = rows.length - 2; j >= 0; j--) if (nodes[j] === null && rows[j].present && !(rows[j + 1].entry)) nodes[j] = nodes[j + 1];
        rows.forEach(function (r, k) {
            r.nodes = r.present ? nodes[k] : null;
            var next = rows[k + 1] && rows[k + 1].entry;
            if (!r.present) r.revision = null;
            else if (r.entry) r.revision = r.entry.revision_after || r.entry.revision_before || null;
            else if (next && next.status !== 'added') r.revision = next.revision_before || null;
            else r.revision = k > 0 ? rows[k - 1].revision : null;
            if (k === 0) r.status = r.present ? 'baseline' : 'absent';
            else if (r.entry) r.status = r.entry.status;
            else r.status = r.present ? (rows[k - 1].present ? 'unchanged' : 'added') : 'absent';
        });
        return rows;
    }

    function historyCards(name, rows) {
        var host = document.getElementById('historyCards');
        host.replaceChildren();
        var latest = rows[rows.length - 1];
        var firstSeen = rows.filter(function (r) { return r.present; })[0];
        var added = 0, removed = 0, changed = 0, revisions = 0;
        rows.forEach(function (r) {
            if (!r.entry) return;
            var c = r.entry.schema_counts || {};
            added += c.added || 0; removed += c.removed || 0; changed += c.changed || 0;
            revisions += (r.entry.revision_notes || []).length;
        });
        var nodeVals = rows.filter(function (r) { return r.nodes !== null && r.nodes !== undefined; });
        var lastStep = latest.entry
            ? latest.entry.status + (latest.entry.schema_counts ? ' (+' + (latest.entry.schema_counts.added || 0) + ' / −' + (latest.entry.schema_counts.removed || 0) + ')' : '')
            : latest.status;
        [
            ['changed', lastStep, 'since ' + rows[rows.length - 2].ver],
            ['', firstSeen ? firstSeen.ver : '—', firstSeen && firstSeen === rows[0] ? 'present since (oldest tracked)' : 'first release'],
            ['', nodeVals.length ? nodeVals[0].nodes + ' → ' + nodeVals[nodeVals.length - 1].nodes : '—', 'schema nodes (first → latest)'],
            ['added', '+' + added, 'node changes added, all time'],
            ['removed', '−' + removed, 'node changes removed, all time'],
            ['changed', revisions, 'YANG revisions recorded']
        ].forEach(function (c) {
            var card = el('div', { className: 'stat ' + c[0] });
            card.appendChild(el('div', { className: 'num' }, c[1]));
            card.appendChild(el('div', { className: 'lbl' }, c[2]));
            host.appendChild(card);
        });
    }

    function historyRows(name, rows) {
        var tbody = document.getElementById('historyRows');
        tbody.replaceChildren();
        rows.slice().reverse().forEach(function (r) {
            var tr = el('tr', r.status === 'absent' ? { className: 'absent' } : null);
            var toggleCell = el('td');
            if (r.entry && (r.entry.schema_counts || (r.entry.revision_notes || []).length)) {
                var toggle = el('button', { type: 'button', className: 'expand', 'aria-expanded': 'false',
                    'aria-label': 'Show changes in ' + r.ver }, '+');
                toggle.addEventListener('click', function () { toggleDetail(tr, toggle, r.entry, r.pairId, 6); });
                toggleCell.appendChild(toggle);
            }
            tr.appendChild(toggleCell);
            var verCell = el('td');
            verCell.appendChild(el('strong', null, r.ver));
            if (r.present && SAFE_NAME.test(name) && SAFE_NAME.test(r.ver) && (!r.entry || r.entry.has_tree !== false)) {
                var links = el('div', { className: 'links' });
                links.appendChild(el('a', { href: 'releases/' + encodeURIComponent(r.ver) + '/yang-trees/' + name + '.html' }, 'Tree'));
                (r.entry && r.entry.specs || []).forEach(function (spec) {
                    var a = specLink(spec, r.ver);
                    if (a) links.appendChild(a);
                });
                verCell.appendChild(links);
            }
            tr.appendChild(verCell);
            var statusCell = el('td');
            var labels = { baseline: 'present', absent: 'not present' };
            statusCell.appendChild(el('span', { className: 'badge ' + r.status }, labels[r.status] || r.status));
            tr.appendChild(statusCell);
            tr.appendChild(el('td', { className: 'mono' }, r.revision || '—'));
            tr.appendChild(el('td', { className: 'num' }, r.nodes === null || r.nodes === undefined ? '—' : r.nodes.toLocaleString()));
            tr.appendChild(r.entry ? schemaCell(r.entry) : el('td', { className: 'num muted' }, '—'));
            tbody.appendChild(tr);
        });
    }

    function netChange(name, rows) {
        var host = document.getElementById('historyNet');
        host.replaceChildren(el('p', { className: 'muted' }, 'Loading every release step…'));
        var steps = rows.filter(function (r) { return r.entry && r.entry.schema_counts; });
        if (!steps.length) {
            host.replaceChildren(el('p', { className: 'muted' }, 'No schema-node changes recorded for this module in any release.'));
            return;
        }
        Promise.all(steps.map(function (r) { return getDetail(r.pairId, name); })).then(function (details) {
            var added = new Map(), removed = new Map(), changed = new Map();
            details.forEach(function (d) {
                (d.added || []).forEach(function (a) {
                    if (removed.has(a.path)) removed.delete(a.path); else added.set(a.path, a);
                });
                (d.removed || []).forEach(function (x) {
                    if (added.has(x.path)) added.delete(x.path); else removed.set(x.path, x);
                });
                (d.changed || []).forEach(function (c) {
                    if (added.has(c.path)) return;
                    var prev = changed.get(c.path);
                    var merged = { path: c.path, changes: {} };
                    var keys = Object.keys(c.changes).concat(prev ? Object.keys(prev.changes) : []);
                    keys.forEach(function (k) {
                        var before = prev && prev.changes[k] ? prev.changes[k][0] : (c.changes[k] || [])[0];
                        var after = c.changes[k] ? c.changes[k][1] : prev.changes[k][1];
                        if (before !== after) merged.changes[k] = [before, after];
                    });
                    if (Object.keys(merged.changes).length) changed.set(c.path, merged); else changed.delete(c.path);
                });
            });
            host.replaceChildren();
            var span = rows.filter(function (r) { return r.present; });
            host.appendChild(el('p', { className: 'muted' }, span.length
                ? span[0].ver + ' → ' + span[span.length - 1].ver + ' across ' + details.length + ' release step(s) with schema changes.'
                : ''));
            host.appendChild(nodeList('Added', Array.from(added.values()), subtreeItem));
            host.appendChild(nodeList('Removed', Array.from(removed.values()), subtreeItem));
            host.appendChild(nodeList('Changed', Array.from(changed.values()), changedItem));
            if (!added.size && !removed.size && !changed.size) host.appendChild(el('p', { className: 'muted' }, 'Changes cancel out: no net schema difference.'));
        }).catch(function (err) {
            host.replaceChildren(el('p', { className: 'muted' }, 'Could not load details: ' + err.message));
        });
    }

    function showHistory(name) {
        name = String(name || '').trim();
        if (!SAFE_NAME.test(name) || !state.pairs.length) return;
        var section = document.getElementById('historySection');
        document.getElementById('historyInput').value = name;
        document.getElementById('historyHeading').textContent = 'Module history: ' + name;
        document.getElementById('historyMeta').textContent = 'Loading…';
        document.getElementById('historyCards').replaceChildren();
        document.getElementById('historyRows').replaceChildren();
        var netHost = document.getElementById('historyNet');
        var netBtn = el('button', { type: 'button', className: 'action' }, 'Compute net change');
        netHost.replaceChildren(netBtn);
        section.hidden = false;
        state.history = name;
        writeHash();
        var pairs = chronologicalPairs();
        Promise.all([Promise.all(pairs.map(getPair)), loadPresence().catch(function () { return null; })])
            .then(function (res) {
                if (state.history !== name) return;
                var rows = buildTimeline(name, res[0]);
                if (!rows.some(function (r) { return r.present || r.entry; })) {
                    netHost.replaceChildren();
                    document.getElementById('historyMeta').textContent = 'No module named ' + name
                        + ' in any release ' + pairs[0].old + ' → ' + pairs[pairs.length - 1].new + '.';
                    return;
                }
                document.getElementById('historyMeta').textContent = 'Releases ' + pairs[0].old + ' → '
                    + pairs[pairs.length - 1].new + ' (newest first). Expand a release to see what changed in it.';
                historyCards(name, rows);
                historyRows(name, rows);
                netBtn.addEventListener('click', function () { netChange(name, rows); });
                section.scrollIntoView({ block: 'start' });
            })
            .catch(function (err) { document.getElementById('historyMeta').textContent = 'Could not load history: ' + err.message; });
    }

    function closeHistory() {
        state.history = null;
        document.getElementById('historySection').hidden = true;
        writeHash();
    }

    function showError(message) {
        var tbody = document.getElementById('moduleRows');
        var tr = el('tr');
        tr.appendChild(el('td', { colspan: '6', className: 'empty' }, message));
        tbody.replaceChildren(tr);
    }

    function init() {
        var hash = readHash();
        ['statusFilter', 'categoryFilter'].forEach(function (id) {
            document.getElementById(id).addEventListener('change', function () { renderModules(); writeHash(); });
        });
        document.getElementById('searchBox').addEventListener('input', function () { renderModules(); writeHash(); });
        document.getElementById('pairSelect').addEventListener('change', function (e) {
            loadPair(e.target.value).catch(function (err) { showError(err.message); });
        });
        if (hash.status) document.getElementById('statusFilter').value = hash.status;
        if (hash.q) document.getElementById('searchBox').value = hash.q;
        document.getElementById('historyForm').addEventListener('submit', function (e) {
            e.preventDefault();
            showHistory(document.getElementById('historyInput').value);
        });
        document.getElementById('historyInput').addEventListener('focus', function () {
            loadPresence().catch(function () { /* datalist is optional */ });
        }, { once: true });
        document.getElementById('historyClose').addEventListener('click', closeHistory);

        fetchJson('releases/compare/index.json').then(function (index) {
            state.pairs = (index.pairs || []).filter(function (p) {
                return SAFE_NAME.test(p.old) && SAFE_NAME.test(p.new) && /^[A-Za-z0-9._-]+\.json$/.test(p.file);
            });
            if (!state.pairs.length) throw new Error('No release comparisons available.');
            var select = document.getElementById('pairSelect');
            state.pairs.forEach(function (p) {
                select.appendChild(el('option', { value: p.old + '__' + p.new }, p.old + ' → ' + p.new));
            });
            return loadPair(hash.pair);
        }).then(function () {
            if (hash.category) {
                document.getElementById('categoryFilter').value = hash.category;
                renderModules();
            }
            if (hash.module) showHistory(hash.module);
        }).catch(function (err) { showError(err.message); });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
