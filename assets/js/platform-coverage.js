(function () {
    var INDEX_URL = 'platform-support-index.json';
    var sel = document.getElementById('releaseSel');
    var platSel = document.getElementById('platSel');
    var filter = document.getElementById('filter');
    var status = document.getElementById('status');
    var matrixWrap = document.getElementById('matrixWrap');
    var matrix = document.getElementById('matrix');
    var summary = document.getElementById('summary');
    var current = null;

    function setStatus(msg, err) {
        status.textContent = msg;
        status.className = err ? 'error' : '';
        status.style.display = msg ? 'block' : 'none';
        matrixWrap.style.display = msg ? 'none' : 'block';
    }

    function loadRelease(ver) {
        setStatus('Loading platform-support.json for ' + ver + '…');
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
                document.getElementById('exportBtn').addEventListener('click', exportCsv);
                loadRelease(sel.value);
            })
            .catch(function (e) {
                setStatus('Failed to load ' + INDEX_URL + ': ' + e.message, true);
            });
    }
    init();
})();
