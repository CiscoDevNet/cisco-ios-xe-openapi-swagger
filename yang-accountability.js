/* yang-accountability.js — YANG accountability page controller (extracted from inline script) */
(function () {
    'use strict';

    var allModules = [];
    var reportData = {};
    var currentFilter = { category: 'all', status: 'all' };

    // Pagination: render rows in chunks so the initial paint stays cheap on
    // releases with 1300+ modules. "Show more" appends another page; "Show
    // all" disables paging for the rest of the session.
    var PAGE_SIZE = 200;
    var visibleRows = PAGE_SIZE;

    var CAT_ORDER = ['oper', 'rpc', 'cfg', 'openconfig', 'ietf', 'mib', 'events', 'native', 'other', 'types', 'deviation', 'common', 'native-aug', 'rpc-aug', 'submodule'];
    var EXCLUDED = new Set(['types', 'deviation', 'common', 'native-aug', 'rpc-aug', 'submodule']);
    var CAT_NOTES = {
        oper: 'Operational state data', rpc: 'Remote procedure calls', cfg: 'Configuration modules',
        openconfig: 'OpenConfig standard modules', ietf: 'IETF standard modules', mib: 'SNMP MIB translations',
        events: 'Event notifications', native: 'Main native module - split into specs', other: 'Miscellaneous modules',
        types: 'Type definitions only', deviation: 'Modifies other modules', common: 'Infrastructure modules',
        'native-aug': 'Augments native module',
        'rpc-aug': 'Augments main RPC module',
        submodule: 'Submodule included in parent module spec'
    };

    // === Load data ===

    function _activeVersion() {
        // Honor ?ver=… or #ver=… on this page, then fall back to the parent
        // hub's __IOSXE_ACTIVE_VERSION__ when navigated to from index.html.
        try {
            var qs = new URLSearchParams(location.search).get('ver');
            if (qs) return qs;
            var m = (location.hash || '').match(/[#&]ver=([^&]+)/);
            if (m) return decodeURIComponent(m[1]);
        } catch (_) { /* noop */ }
        if (window.__IOSXE_ACTIVE_VERSION__) return window.__IOSXE_ACTIVE_VERSION__;
        return null;
    }

    function _accountabilityUrl() {
        var ver = _activeVersion();
        if (ver) return 'releases/' + encodeURIComponent(ver) + '/yang_accountability.json';
        return 'yang_accountability.json';
    }

    // === Hash deep-link (search + filters + version) ===
    // URL hash shape:
    //   #ver=<release>&q=<search>&cat=<classification>&status=<status>
    // Lets users share / bookmark an exact filter view.

    function _parseHash() {
        var out = {};
        var h = (location.hash || '').replace(/^#/, '');
        if (!h) return out;
        h.split('&').forEach(function (kv) {
            if (!kv) return;
            var i = kv.indexOf('=');
            var k = i >= 0 ? kv.slice(0, i) : kv;
            var v = i >= 0 ? decodeURIComponent(kv.slice(i + 1)) : '';
            if (k) out[k] = v;
        });
        return out;
    }

    function _writeHash() {
        try {
            var parts = [];
            var ver = _activeVersion();
            if (ver) parts.push('ver=' + encodeURIComponent(ver));
            var q = (document.getElementById('searchBox') || {}).value || '';
            if (q) parts.push('q=' + encodeURIComponent(q));
            if (currentFilter.category && currentFilter.category !== 'all') {
                parts.push('cat=' + encodeURIComponent(currentFilter.category));
            }
            if (currentFilter.status && currentFilter.status !== 'all') {
                parts.push('status=' + encodeURIComponent(currentFilter.status));
            }
            var next = parts.length ? '#' + parts.join('&') : ' ';
            if (location.hash !== next) {
                history.replaceState(null, '', location.pathname + location.search + next);
            }
        } catch (_) { /* noop */ }
    }

    function _applyHashOnLoad() {
        var h = _parseHash();
        if (h.q) {
            var sb = document.getElementById('searchBox');
            if (sb) sb.value = h.q;
        }
        if (h.cat) currentFilter.category = h.cat;
        if (h.status) currentFilter.status = h.status;
    }

    function _syncFilterButtons() {
        // After data load, reflect currentFilter state in the button highlights.
        var catBtns = document.querySelectorAll('#categoryFilterButtons .filter-btn');
        catBtns.forEach(function (b) {
            b.classList.toggle('active', b.dataset.category === currentFilter.category);
        });
        var statusBtns = document.querySelectorAll('#statusFilterButtons .filter-btn');
        statusBtns.forEach(function (b) {
            b.classList.toggle('active', b.dataset.status === currentFilter.status);
        });
    }

    function _bindShareBtn() {
        var btn = document.getElementById('yaShareBtn');
        if (!btn || btn.__bound) return;
        btn.__bound = true;
        btn.addEventListener('click', function () {
            _writeHash();
            var original = btn.textContent;
            var url = location.href;
            var done = function () {
                btn.textContent = 'Copied!';
                setTimeout(function () { btn.textContent = original; }, 3000);
            };
            // Prefer the shared DeepLink helper for consistent UX (3s flash + toast)
            if (window.__DeepLink && typeof window.__DeepLink.copyShareLink === 'function') {
                try { window.__DeepLink.copyShareLink(btn); return; } catch (_) { /* fall through */ }
            }
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url).then(done, function () {
                    window.prompt('Copy this URL:', url);
                });
            } else {
                window.prompt('Copy this URL:', url);
            }
        });
    }

    // === CSV export ====================================================
    // Dumps the currently-filtered table rows to a downloadable CSV. Columns
    // mirror the on-screen table plus a few useful flags. Honors RFC 4180:
    // values containing comma/quote/newline are wrapped in double quotes and
    // embedded quotes are doubled. Uses UTF-8 BOM so Excel opens it cleanly.

    function _csvCell(value) {
        var s = value == null ? '' : String(value);
        if (/[",\r\n]/.test(s)) {
            s = '"' + s.replace(/"/g, '""') + '"';
        }
        return s;
    }

    function _csvRow(values) {
        return values.map(_csvCell).join(',');
    }

    function _buildCsv(modules) {
        var headers = [
            'Module Name', 'Classification', 'Categories',
            'Has Spec', 'Has Tree', 'Spec URLs', 'Tree URL', 'Reason Excluded'
        ];
        var lines = [_csvRow(headers)];
        modules.forEach(function (m) {
            var cats = (m.categories || []).map(function (c) { return c.label || c.key || ''; }).join('; ');
            var specUrls = (m.categories || []).map(function (c) { return c.spec_url || ''; }).filter(Boolean).join('; ');
            lines.push(_csvRow([
                m.name || '',
                m.classification || '',
                cats,
                m.has_spec ? 'yes' : 'no',
                m.tree_url ? 'yes' : 'no',
                specUrls,
                m.tree_url || '',
                m.reason_excluded || ''
            ]));
        });
        return lines.join('\r\n') + '\r\n';
    }

    function _bindCsvBtn() {
        var btn = document.getElementById('yaCsvBtn');
        if (!btn || btn.__bound) return;
        btn.__bound = true;
        btn.addEventListener('click', function () {
            var rows = _filteredModules();
            if (!rows.length) {
                btn.textContent = 'No rows match filter';
                setTimeout(function () { btn.textContent = 'Export CSV'; }, 2500);
                return;
            }
            var csv = _buildCsv(rows);
            // UTF-8 BOM so Excel auto-detects encoding
            var blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' });
            var ver = (typeof _activeVersion === 'function') ? _activeVersion() : '';
            var ts = new Date().toISOString().slice(0, 10);
            var name = 'yang-accountability' + (ver ? '-' + ver : '') + '-' + ts + '.csv';
            var a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = name;
            document.body.appendChild(a);
            a.click();
            setTimeout(function () {
                URL.revokeObjectURL(a.href);
                a.remove();
            }, 0);
            var orig = btn.textContent;
            btn.textContent = 'Exported ' + rows.length + ' rows';
            setTimeout(function () { btn.textContent = orig; }, 3000);
        });
    }

    // === Copy-as-text export ===========================================
    // Renders the currently-filtered modules as a plain-text report you can
    // paste into chat, email, or a code review comment. Two-column fixed-
    // width header + name-aligned rows. Truncates after 200 rows with a
    // "+N more" footer so big copies don't explode the clipboard.

    function _buildTextReport(modules) {
        var ver = (typeof _activeVersion === 'function') ? _activeVersion() : '';
        var ts = new Date().toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
        var lines = [];
        lines.push('YANG Module Accountability' + (ver ? ' \u2014 ' + ver : ''));
        lines.push('Generated ' + ts);
        if (reportData) {
            lines.push('Total: ' + reportData.total_modules +
                       '  |  With spec: ' + reportData.modules_with_specs +
                       '  |  Coverage: ' + (100 * reportData.modules_with_specs / reportData.total_modules).toFixed(1) + '%');
        }
        lines.push('Filter: category=' + currentFilter.category + ', status=' + currentFilter.status +
                   (document.getElementById('searchBox') && document.getElementById('searchBox').value ?
                    ', search="' + document.getElementById('searchBox').value + '"' : ''));
        lines.push('Rows: ' + modules.length);
        lines.push('');
        var MAX = 200;
        var shown = modules.slice(0, MAX);
        var nameWidth = Math.min(60, shown.reduce(function (n, m) { return Math.max(n, (m.name || '').length); }, 4));
        function pad(s, w) { s = s || ''; return s.length >= w ? s : s + new Array(w - s.length + 1).join(' '); }
        lines.push(pad('Name', nameWidth) + '  Spec  Tree  Categories');
        lines.push(new Array(nameWidth + 1).join('-') + '  ----  ----  ----------');
        shown.forEach(function (m) {
            var cats = (m.categories || []).map(function (c) { return c.label || c.key || ''; }).join(', ');
            lines.push(pad(m.name || '', nameWidth) + '  ' +
                       (m.has_spec ? ' yes' : '  no') + '  ' +
                       (m.tree_url ? ' yes' : '  no') + '  ' + cats);
        });
        if (modules.length > MAX) {
            lines.push('');
            lines.push('+' + (modules.length - MAX) + ' more rows not shown (use Export CSV for the full set).');
        }
        return lines.join('\n');
    }

    function _bindCopyTextBtn() {
        var btn = document.getElementById('yaCopyTextBtn');
        if (!btn || btn.__bound) return;
        btn.__bound = true;
        btn.addEventListener('click', function () {
            var rows = _filteredModules();
            if (!rows.length) {
                btn.textContent = 'No rows match filter';
                setTimeout(function () { btn.textContent = 'Copy as Text'; }, 2500);
                return;
            }
            var text = _buildTextReport(rows);
            var orig = btn.textContent;
            var done = function () {
                btn.textContent = 'Copied ' + Math.min(rows.length, 200) + ' rows';
                setTimeout(function () { btn.textContent = orig; }, 3000);
            };
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(done, _fallbackCopy);
            } else {
                _fallbackCopy();
            }
            function _fallbackCopy() {
                // execCommand path for older browsers / insecure contexts.
                var ta = document.createElement('textarea');
                ta.value = text;
                ta.setAttribute('readonly', '');
                ta.style.position = 'absolute';
                ta.style.left = '-9999px';
                document.body.appendChild(ta);
                ta.select();
                try { document.execCommand('copy'); done(); }
                catch (_) { window.prompt('Copy report:', text); }
                document.body.removeChild(ta);
            }
        });
    }

    async function loadModuleData() {
        // Render a short skeleton table while the JSON fetch is in flight.
        // Keeps the layout stable and signals "loading" without a spinner.
        _renderLoadingSkeleton();
        try {
            var url = _accountabilityUrl();
            var response = await fetch(url, { cache: 'no-store' });
            if (!response.ok && url !== 'yang_accountability.json') {
                // Per-release JSON missing — fall back to root snapshot.
                response = await fetch('yang_accountability.json', { cache: 'no-store' });
            }
            reportData = await response.json();
            allModules = reportData.modules;

            document.getElementById('statTotal').textContent = reportData.total_modules;
            document.getElementById('statWithSpec').textContent = reportData.modules_with_specs;
            document.getElementById('statCoverage').textContent = (100 * reportData.modules_with_specs / reportData.total_modules).toFixed(1) + '%';
            document.getElementById('statWithTree').textContent = reportData.modules_with_trees;
            document.getElementById('statMultiCat').textContent = reportData.modules_multi_category;
            document.getElementById('statExcluded').textContent = reportData.total_modules - reportData.modules_with_specs;

            buildCategoryButtons();
            renderCategorySummary();
            renderTable();
            _syncFilterButtons();
        } catch (error) {
            console.error('Error loading module data:', error);
            document.getElementById('moduleTableBody').innerHTML =
                '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #F44336;">Error loading data. Please refresh.</td></tr>';
        }
    }

    // Render skeleton rows + stat-card placeholders before the real fetch
    // resolves. Uses six columns to match renderTable()'s structure.
    function _renderLoadingSkeleton() {
        var tbody = document.getElementById('moduleTableBody');
        if (tbody) {
            var rows = '';
            for (var i = 0; i < 8; i++) {
                rows +=
                    '<tr class="skeleton-row" aria-hidden="true">' +
                        '<td><span class="skeleton-bar sk-sm"></span></td>' +
                        '<td><span class="skeleton-bar sk-lg"></span></td>' +
                        '<td><span class="skeleton-bar sk-sm"></span></td>' +
                        '<td><span class="skeleton-bar sk-md"></span></td>' +
                        '<td><span class="skeleton-bar sk-md"></span></td>' +
                        '<td><span class="skeleton-bar sk-sm"></span></td>' +
                    '</tr>';
            }
            tbody.innerHTML = rows;
        }
        // Stat-card placeholders.
        ['statTotal', 'statWithSpec', 'statCoverage', 'statWithTree',
         'statMultiCat', 'statExcluded'].forEach(function (id) {
            var el = document.getElementById(id);
            if (el && !el.textContent.trim()) el.innerHTML = '<span class="skeleton-bar sk-sm" aria-hidden="true"></span>';
        });
        var stats = document.getElementById('tableStats');
        if (stats) stats.textContent = 'Loading modules\u2026';
    }

    // === Category buttons ===

    function buildCategoryButtons() {
        var container = document.getElementById('categoryFilterButtons');
        var html = '<button class="filter-btn active" data-category="all">All (' + allModules.length + ')</button>';
        CAT_ORDER.forEach(function (cls) {
            var cat = reportData.categories[cls];
            if (cat) {
                html += '<button class="filter-btn" data-category="' + cls + '">' + cls.toUpperCase() + ' (' + cat.total + ')</button>';
            }
        });
        container.innerHTML = html;

        // Bind click events via delegation
        container.addEventListener('click', function (e) {
            var btn = e.target.closest('.filter-btn');
            if (!btn || !btn.dataset.category) return;
            currentFilter.category = btn.dataset.category;
            container.querySelectorAll('.filter-btn').forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            visibleRows = PAGE_SIZE;
            renderTable();
            _writeHash();
        });
    }

    // === Category summary ===

    function renderCategorySummary() {
        var tbody = document.getElementById('categorySummaryBody');
        var html = '';
        CAT_ORDER.forEach(function (cls) {
            var cat = reportData.categories[cls];
            if (!cat) return;
            var isExcluded = EXCLUDED.has(cls);
            var badgeHtml = '';
            var coverageClass = 'coverage-na';
            var coverage = 'N/A';

            if (!isExcluded) {
                var pct = cat.coverage_pct;
                if (pct >= 90) { badgeHtml = '<span class="badge badge-success">READY</span>'; coverageClass = 'coverage-high'; }
                else if (pct >= 50) { badgeHtml = '<span class="badge badge-warning">PARTIAL</span>'; coverageClass = 'coverage-med'; }
                else { coverageClass = 'coverage-low'; }
                coverage = pct.toFixed(1) + '%';
            } else {
                badgeHtml = '<span class="badge badge-info">EXCLUDED</span>';
            }

            html += '<tr>' +
                '<td><strong>' + cls + '</strong> ' + badgeHtml + '</td>' +
                '<td>' + cat.total + '</td>' +
                '<td>' + cat.with_specs + '</td>' +
                '<td class="' + coverageClass + '">' + coverage + '</td>' +
                '<td>' + (CAT_NOTES[cls] || '') + '</td>' +
                '</tr>';
        });
        tbody.innerHTML = html;
    }

    // === Main table ===

    function _filteredModules() {
        var searchTerm = (document.getElementById('searchBox').value || '').toLowerCase();
        return allModules.filter(function (module) {
            if (currentFilter.category !== 'all' && module.classification !== currentFilter.category) return false;
            if (currentFilter.status === 'documented' && !module.has_spec) return false;
            if (currentFilter.status === 'missing' && module.has_spec) return false;
            if (currentFilter.status === 'has-tree' && !module.tree_url) return false;
            if (currentFilter.status === 'multi-cat' && module.categories.length <= 1) return false;
            if (searchTerm && !module.name.toLowerCase().includes(searchTerm)) return false;
            return true;
        });
    }

    function renderTable() {
        var tbody = document.getElementById('moduleTableBody');
        var filtered = _filteredModules();

        document.getElementById('tableStats').textContent = 'Showing: ' + Math.min(filtered.length, visibleRows) + ' of ' + filtered.length + ' modules' + (filtered.length !== allModules.length ? ' (filtered from ' + allModules.length + ')' : '');

        if (filtered.length === 0) {
            // Determine which filters are active to decide whether to offer
            // a "Clear filters" CTA in the empty state.
            var hasSearch = !!((document.getElementById('searchBox') || {}).value || '').trim();
            var hasCat = currentFilter.category && currentFilter.category !== 'all';
            var hasStatus = currentFilter.status && currentFilter.status !== 'all';
            var anyActive = hasSearch || hasCat || hasStatus;
            var cta = anyActive
                ? '<div style="margin-top:12px;"><button type="button" id="emptyClearFiltersBtn" class="copy-btn">Clear filters</button></div>'
                : '';
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #666;">'
                + '<div style="font-size:1.1rem;margin-bottom:6px;">No modules match your filters</div>'
                + '<div style="font-size:0.9rem;color:#888;">Try a broader search, or clear filters to see all modules.</div>'
                + cta
                + '</td></tr>';
            var clearBtn = document.getElementById('emptyClearFiltersBtn');
            if (clearBtn) clearBtn.addEventListener('click', _clearAllFilters);
            _renderPagerControls(0, 0);
            return;
        }

        var slice = filtered.slice(0, visibleRows);

        tbody.innerHTML = slice.map(function (module, index) {
            var classBadge = getCategoryBadge(module.classification);

            var catsHtml;
            if (module.categories.length === 0) {
                if (module.reason_excluded) {
                    catsHtml = '<span style="color:#999;font-size:0.85rem;">' + escapeHtml(module.reason_excluded) + '</span>';
                } else {
                    catsHtml = '<span style="color:#999;">\u2014</span>';
                }
            } else {
                catsHtml = module.categories.map(function (c) {
                    return '<span class="cat-tag">' + escapeHtml(c.label) + '</span>';
                }).join(' ');
            }

            var specHtml;
            if (module.categories.length === 0) {
                specHtml = '<span style="color:#ccc;">\u2014</span>';
            } else {
                specHtml = module.categories.map(function (c) {
                    return '<a href="' + escapeHtml(c.spec_url) + '" class="spec-link" title="View in ' + escapeHtml(c.label) + '">' + escapeHtml(c.label) + '</a>';
                }).join(' ');
            }

            var treeHtml = module.tree_url
                ? '<a href="' + escapeHtml(module.tree_url) + '" class="tree-link" title="View YANG Tree">\ud83c\udf33 Tree</a>'
                : '<span style="color:#ccc;">\u2014</span>';

            return '<tr>' +
                '<td style="color: #999;">' + (index + 1) + '</td>' +
                '<td><strong>' + escapeHtml(module.name) + '</strong></td>' +
                '<td>' + classBadge + '</td>' +
                '<td>' + catsHtml + '</td>' +
                '<td>' + specHtml + '</td>' +
                '<td>' + treeHtml + '</td>' +
                '</tr>';
        }).join('');

        _renderPagerControls(slice.length, filtered.length);
    }

    function _renderPagerControls(shown, total) {
        var pager = document.getElementById('tablePager');
        if (!pager) return;
        if (total === 0 || shown >= total) {
            pager.innerHTML = '';
            return;
        }
        var remaining = total - shown;
        var nextChunk = Math.min(PAGE_SIZE, remaining);
        pager.innerHTML =
            '<button type="button" id="pagerMore" class="filter-btn" aria-label="Show next ' + nextChunk + ' rows">Show next ' + nextChunk + '</button>' +
            ' <button type="button" id="pagerAll" class="filter-btn" aria-label="Show all ' + total + ' rows">Show all (' + total + ')</button>';
        document.getElementById('pagerMore').onclick = function () { visibleRows += PAGE_SIZE; renderTable(); };
        document.getElementById('pagerAll').onclick = function () { visibleRows = Number.MAX_SAFE_INTEGER; renderTable(); };

    // === Utilities ===

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function getCategoryBadge(category) {
        var badges = {
            'oper': '<span class="badge badge-success">OPER</span>',
            'rpc': '<span class="badge badge-warning">RPC</span>',
            'events': '<span class="badge badge-success">EVENTS</span>',
            'cfg': '<span class="badge badge-warning">CFG</span>',
            'ietf': '<span class="badge badge-info">IETF</span>',
            'mib': '<span class="badge badge-info">MIB</span>',
            'openconfig': '<span class="badge badge-info">OPENCONFIG</span>',
            'native': '<span class="badge">NATIVE</span>',
            'types': '<span class="badge badge-info">TYPES</span>',
            'deviation': '<span class="badge badge-info">DEVIATION</span>',
            'native-aug': '<span class="badge badge-info">NATIVE-AUG</span>',
            'rpc-aug': '<span class="badge badge-info">RPC-AUG</span>',
            'common': '<span class="badge badge-info">COMMON</span>',
            'submodule': '<span class="badge badge-info">SUBMODULE</span>',
            'other': '<span class="badge">OTHER</span>'
        };
        return badges[category] || '<span class="badge">' + (category || '').toUpperCase() + '</span>';
    }

    // === Filters ===

    function filterByStatus(status, btn) {
        currentFilter.status = status;
        btn.parentElement.querySelectorAll('button').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        visibleRows = PAGE_SIZE;
        renderTable();
        _writeHash();
    }

    // Reset all visible filters (search box, category buttons, status buttons)
    // and re-render. Invoked from the "Clear filters" CTA in the empty state.
    function _clearAllFilters() {
        var sb = document.getElementById('searchBox');
        if (sb) sb.value = '';
        currentFilter.category = 'all';
        currentFilter.status = 'all';
        document.querySelectorAll('[data-category]').forEach(function (b) {
            b.classList.toggle('active', b.dataset.category === 'all');
        });
        document.querySelectorAll('[data-status]').forEach(function (b) {
            b.classList.toggle('active', b.dataset.status === 'all');
        });
        visibleRows = PAGE_SIZE;
        renderTable();
        _writeHash();
        if (sb) sb.focus();
    }

    // === Sort ===

    var sortDirection = 1;

    function sortTable(columnIndex) {
        var keys = ['index', 'name', 'classification'];
        var key = keys[columnIndex];
        if (!key) return;

        if (key === 'index') {
            sortDirection *= -1;
            allModules.reverse();
        } else {
            sortDirection *= -1;
            allModules.sort(function (a, b) { return sortDirection * (a[key] || '').localeCompare(b[key] || ''); });
        }
        renderTable();
    }

    // === Initialization ===

    function _registerShortcuts() {
        // Page-specific keyboard shortcuts. Surfaced in the '?' dialog by
        // pushing entries into the shared window.__SHORTCUTS array.
        var SH = window.__SHORTCUTS = window.__SHORTCUTS || [];
        SH.push({ keys: 'E', label: 'Export CSV (filtered rows)' });
        SH.push({ keys: 'T', label: 'Copy filtered table as text' });
        SH.push({ keys: 'L', label: 'Copy Share Link (filter state)' });
        SH.push({ keys: '/', label: 'Focus the module search box' });

        document.addEventListener('keydown', function (e) {
            if (e.ctrlKey || e.metaKey || e.altKey) return;
            var t = e.target;
            if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' ||
                      t.tagName === 'SELECT' || t.isContentEditable)) return;
            var k = e.key;
            if (k === 'e' || k === 'E') { var b = document.getElementById('yaCsvBtn'); if (b) { e.preventDefault(); b.click(); } }
            else if (k === 't' || k === 'T') { var b2 = document.getElementById('yaCopyTextBtn'); if (b2) { e.preventDefault(); b2.click(); } }
            else if (k === 'l' || k === 'L') { var b3 = document.getElementById('yaShareBtn'); if (b3) { e.preventDefault(); b3.click(); } }
            else if (k === '/') { var s = document.getElementById('searchBox'); if (s) { e.preventDefault(); s.focus(); s.select && s.select(); } }
        });
    }

    function init() {
        _applyHashOnLoad();
        _bindShareBtn();
        _bindCsvBtn();
        _bindCopyTextBtn();
        _registerShortcuts();
        loadModuleData();

        // Search box
        document.getElementById('searchBox').addEventListener('keyup', function () { visibleRows = PAGE_SIZE; renderTable(); _writeHash(); });

        // Status filter buttons (event delegation)
        var statusFilterContainer = document.getElementById('statusFilterButtons');
        if (statusFilterContainer) {
            statusFilterContainer.addEventListener('click', function (e) {
                var btn = e.target.closest('.filter-btn');
                if (!btn || !btn.dataset.status) return;
                filterByStatus(btn.dataset.status, btn);
            });
        }

        // Sort headers (event delegation)
        document.querySelectorAll('[data-sort-col]').forEach(function (th) {
            th.addEventListener('click', function () {
                sortTable(parseInt(this.dataset.sortCol, 10));
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
