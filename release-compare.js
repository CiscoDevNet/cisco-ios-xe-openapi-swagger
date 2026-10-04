/* release-compare.js — "What changed between releases" page.
 * Data: releases/compare/index.json, releases/compare/<old>__<new>.json and
 * on-demand releases/compare/<old>__<new>/<module>.json (built by
 * scripts/build_release_compare.py). DOM is built with textContent only. */
(function () {
    'use strict';

    var SAFE_NAME = /^[A-Za-z0-9._-]+$/;
    var state = { pairs: [], data: null, pair: null, detailCache: {} };

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

    function fillDetail(cell, m) {
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
        var key = state.pair + '/' + m.name;
        var loading = el('p', { className: 'muted' }, 'Loading schema changes…');
        cell.appendChild(loading);
        var cached = state.detailCache[key];
        var promise = cached ? Promise.resolve(cached)
            : fetchJson('releases/compare/' + encodeURIComponent(state.pair) + '/' + m.name + '.json');
        promise.then(function (detail) {
            state.detailCache[key] = detail;
            loading.remove();
            cell.appendChild(nodeList('Added', detail.added, subtreeItem));
            cell.appendChild(nodeList('Removed', detail.removed, subtreeItem));
            cell.appendChild(nodeList('Changed', detail.changed, changedItem));
        }).catch(function (err) {
            loading.textContent = 'Could not load details: ' + err.message;
        });
    }

    function toggleDetail(tr, button, m) {
        var next = tr.nextElementSibling;
        if (next && next.classList.contains('detail')) {
            next.remove();
            button.textContent = '+';
            button.setAttribute('aria-expanded', 'false');
            return;
        }
        var detailRow = el('tr', { className: 'detail' });
        var cell = el('td', { colspan: '6', className: 'detail' });
        detailRow.appendChild(cell);
        tr.after(detailRow);
        button.textContent = '−';
        button.setAttribute('aria-expanded', 'true');
        fillDetail(cell, m);
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

    function loadPair(pairId) {
        var entry = state.pairs.filter(function (p) { return p.old + '__' + p.new === pairId; })[0] || state.pairs[0];
        state.pair = entry.old + '__' + entry.new;
        document.getElementById('pairSelect').value = state.pair;
        return fetchJson('releases/compare/' + encodeURIComponent(entry.file)).then(function (data) {
            state.data = data;
            populateCategories();
            renderCards();
            renderModules();
            renderPlatforms();
            writeHash();
        });
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
        }).catch(function (err) { showError(err.message); });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
