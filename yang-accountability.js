/* yang-accountability.js — YANG accountability page controller (extracted from inline script) */
(function () {
    'use strict';

    var allModules = [];
    var reportData = {};
    var currentFilter = { category: 'all', status: 'all' };

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

    async function loadModuleData() {
        try {
            var response = await fetch('yang_accountability.json');
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
        } catch (error) {
            console.error('Error loading module data:', error);
            document.getElementById('moduleTableBody').innerHTML =
                '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #F44336;">Error loading data. Please refresh.</td></tr>';
        }
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
            renderTable();
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

    function renderTable() {
        var tbody = document.getElementById('moduleTableBody');
        var searchTerm = document.getElementById('searchBox').value.toLowerCase();

        var filtered = allModules.filter(function (module) {
            if (currentFilter.category !== 'all' && module.classification !== currentFilter.category) return false;
            if (currentFilter.status === 'documented' && !module.has_spec) return false;
            if (currentFilter.status === 'missing' && module.has_spec) return false;
            if (currentFilter.status === 'has-tree' && !module.tree_url) return false;
            if (currentFilter.status === 'multi-cat' && module.categories.length <= 1) return false;
            if (searchTerm && !module.name.toLowerCase().includes(searchTerm)) return false;
            return true;
        });

        document.getElementById('tableStats').textContent = 'Showing: ' + filtered.length + ' of ' + allModules.length + ' modules';

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #666;">No modules match your filters</td></tr>';
            return;
        }

        tbody.innerHTML = filtered.map(function (module, index) {
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
    }

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
        renderTable();
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

    function init() {
        loadModuleData();

        // Search box
        document.getElementById('searchBox').addEventListener('keyup', renderTable);

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
