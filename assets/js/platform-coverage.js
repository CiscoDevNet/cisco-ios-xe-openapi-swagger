(function () {
    var INDEX_URL = 'platform-support-index.json';
    var sel = document.getElementById('releaseSel');
    var platSel = document.getElementById('platSel');
    var filter = document.getElementById('filter');
    var status = document.getElementById('status');
    var matrixWrap = document.getElementById('matrixWrap');
    var matrix = document.getElementById('matrix');
    var summary = document.getElementById('summary');
    var countsPanel = document.getElementById('countsPanel');
    var countsTable = document.getElementById('countsTable');
    var current = null;
    var counts = null;

    function setStatus(msg, err) {
        status.textContent = msg;
        status.className = err ? 'error' : '';
        status.style.display = msg ? 'block' : 'none';
        matrixWrap.style.display = msg ? 'none' : 'block';
    }

    function loadRelease(ver) {
        setStatus('Loading platform-support.json for ' + ver + '…');
        loadCounts(ver);
        return fetch('releases/' + encodeURIComponent(ver) + '/platform-support.json',
                     { cache: 'default' })
            .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(function (doc) {
                current = doc;
                populatePlatformFilter(doc);
                render();
                setStatus('');
            })
            .catch(function (e) {
                setStatus('Failed to load platform-support.json for ' + ver + ': ' + e.message, true);
            });
    }

    function loadCounts(ver) {
        counts = null;
        countsPanel.hidden = true;
        fetch('releases/' + encodeURIComponent(ver) + '/platform-api-counts.json', { cache: 'no-cache' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (doc) {
                if (!doc || doc.release !== sel.value) return;
                counts = doc;
                renderCounts();
            })
            .catch(function () { /* optional panel */ });
    }

    function cell(tag, text, className) {
        var c = document.createElement(tag);
        if (className) c.className = className;
        c.textContent = text;
        return c;
    }

    function renderCounts() {
        if (!counts) return;
        var all = counts.all;
        var cats = Object.keys(all.by_category).sort();
        var picked = platSel.value || '';
        var thead = document.createElement('thead');
        var hr = document.createElement('tr');
        ['Platform', 'Family', 'YANG modules', 'Paths', 'Operations'].concat(cats).forEach(function (h) {
            hr.appendChild(cell('th', h));
        });
        thead.appendChild(hr);
        var tbody = document.createElement('tbody');

        function numCell(n, total) {
            var td = cell('td', n.toLocaleString());
            if (total) td.appendChild(cell('span', Math.round(100 * n / total) + '%', 'pct'));
            return td;
        }
        function addRow(label, family, modules, row, className) {
            var tr = document.createElement('tr');
            if (className) tr.className = className;
            tr.appendChild(cell('td', label));
            tr.appendChild(cell('td', family));
            tr.appendChild(cell('td', modules === null ? '—' : modules.toLocaleString()));
            tr.appendChild(numCell(row.paths, row === all ? 0 : all.paths));
            tr.appendChild(numCell(row.operations, row === all ? 0 : all.operations));
            cats.forEach(function (c) {
                tr.appendChild(cell('td', ((row.by_category[c] || {}).paths || 0).toLocaleString()));
            });
            tbody.appendChild(tr);
        }

        addRow('All IOS XE', '', null, all, 'all');
        counts.platforms.forEach(function (p) {
            addRow(p.id + ' — ' + p.label, p.family, p.modules, p, p.id === picked ? 'picked' : '');
        });
        countsTable.replaceChildren(thead, tbody);
        var un = counts.unmapped || { specs: [] };
        document.getElementById('countsNote').textContent =
            'Unique RESTCONF paths and operations (release ' + counts.release + ') whose YANG module is in each ' +
            'platform\'s published yang-set. Native config paths also require the module that augments them. ' +
            'Per-category columns are paths. Deviations are not applied.' +
            (un.specs.length ? ' Not in any yang-set, so not counted per platform: ' + un.specs.join(', ') + '.' : '');
        countsPanel.hidden = false;
    }

    function populatePlatformFilter(doc) {
        platSel.innerHTML = '<option value="">(any)</option>';
        doc.platforms.forEach(function (p) {
            var opt = document.createElement('option');
            opt.value = p.id; opt.textContent = p.id + ' — ' + p.label;
            platSel.appendChild(opt);
        });
    }

    function moduleRowMatches(modName, info, q, platFilter) {
        if (platFilter && info.platforms.indexOf(platFilter) < 0) return false;
        if (!q) return true;
        return modName.toLowerCase().indexOf(q) >= 0;
    }

    function render() {
        if (!current) return;
        var q = (filter.value || '').trim().toLowerCase();
        var platFilter = platSel.value || '';
        var plats = current.platforms;
        var mods = current.modules;
        var modNames = Object.keys(mods).sort();
        var head = '<thead><tr><th class="module-col">YANG module</th>';
        plats.forEach(function (p) {
            head += '<th><span class="plat-head" data-family="' + p.family +
                    '" title="' + p.label + '">' + p.id + '</span></th>';
        });
        head += '</tr></thead>';
        var body = '<tbody>';
        var shown = 0;
        for (var i = 0; i < modNames.length; i++) {
            var name = modNames[i];
            var info = mods[name];
            if (!moduleRowMatches(name, info, q, platFilter)) continue;
            shown++;
            var rev = info.revision ? '<span class="revision">' + info.revision + '</span>' : '';
            body += '<tr><td class="module-col"><span class="module-name">' + name +
                    '</span>' + rev + '</td>';
            var supported = {};
            info.platforms.forEach(function (pid) { supported[pid] = 1; });
            plats.forEach(function (p) {
                body += '<td>' + (supported[p.id]
                    ? '<span class="yes" title="' + p.id + ' supports ' + name + '">&#10003;</span>'
                    : '<span class="no" title="' + p.id + ' does NOT support ' + name + '">·</span>')
                    + '</td>';
            });
            body += '</tr>';
        }
        body += '</tbody>';
        matrix.innerHTML = head + body;
        summary.textContent = shown + ' of ' + modNames.length + ' modules · ' +
                              plats.length + ' platforms · release ' + current.release;
    }

    function exportCsv() {
        if (!current) return;
        var plats = current.platforms.map(function (p) { return p.id; });
        var lines = ['module,revision,' + plats.join(',')];
        var q = (filter.value || '').trim().toLowerCase();
        var platFilter = platSel.value || '';
        var modNames = Object.keys(current.modules).sort();
        modNames.forEach(function (name) {
            var info = current.modules[name];
            if (!moduleRowMatches(name, info, q, platFilter)) return;
            var sup = {};
            info.platforms.forEach(function (pid) { sup[pid] = 1; });
            var row = [name, info.revision || ''].concat(
                plats.map(function (pid) { return sup[pid] ? '1' : ''; })
            );
            lines.push(row.map(function (c) {
                return /[,"\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c;
            }).join(','));
        });
        var blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'platform-coverage-' + current.release + '.csv';
        document.body.appendChild(a); a.click();
        setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 100);
    }

    function init() {
        fetch(INDEX_URL, { cache: 'no-store' })
            .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(function (idx) {
                idx.releases.forEach(function (v) {
                    var opt = document.createElement('option');
                    opt.value = v; opt.textContent = v;
                    if (v === idx.default) opt.selected = true;
                    sel.appendChild(opt);
                });
                sel.addEventListener('change', function () { loadRelease(sel.value); });
                filter.addEventListener('input', render);
                platSel.addEventListener('change', render);
                platSel.addEventListener('change', renderCounts);
                document.getElementById('exportBtn').addEventListener('click', exportCsv);
                loadRelease(sel.value);
            })
            .catch(function (e) {
                setStatus('Failed to load ' + INDEX_URL + ': ' + e.message, true);
            });
    }
    init();
})();
