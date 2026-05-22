/* tree-compare.js — Tree comparison page controller (extracted from inline script) */
(function () {
    'use strict';

    var searchIndex = null;
    var syncScrollEnabled = true;
    var highlightEnabled = false;
    var leftTreeData = null;
    var rightTreeData = null;

    // === URL / share-link helpers ===
    // Hash format: #left=<module>&right=<module>&ver=<release>
    //   - left/right auto-fill the dropdowns and trigger a compare on load
    //   - ver picks up the per-release search-index.json (matches
    //     viewer behaviour) so a shared link reproduces the exact pair
    //     the user was looking at in the exact release.
    function parseHash() {
        var raw = (window.location.hash || '').replace(/^#/, '');
        var out = {};
        raw.split('&').forEach(function (p) {
            if (!p) return;
            var i = p.indexOf('=');
            var k = (i < 0 ? p : p.slice(0, i)).toLowerCase();
            var v = i < 0 ? '' : decodeURIComponent(p.slice(i + 1));
            if (k) out[k] = v;
        });
        return out;
    }
    function activeVer() {
        try {
            var q = new URLSearchParams(window.location.search).get('ver');
            if (q) return q;
        } catch (_) {}
        var h = parseHash().ver;
        if (h) return h;
        try {
            var s = localStorage.getItem('iosxe-active-version');
            if (s) return s;
        } catch (_) {}
        return null;
    }
    function writeHash(left, right) {
        var ver = activeVer();
        var parts = [];
        if (ver) parts.push('ver=' + encodeURIComponent(ver));
        if (left) parts.push('left=' + encodeURIComponent(left));
        if (right) parts.push('right=' + encodeURIComponent(right));
        var next = '#' + parts.join('&');
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, '', window.location.pathname
                + window.location.search + next);
        } else {
            window.location.hash = next;
        }
    }

    // === Load search index ===
    // Prefer releases/<ver>/search-index.json when ?ver= / #ver= is set;
    // fall back to the root index if the per-release file is missing.
    async function loadSearchIndex() {
        var ver = activeVer();
        var opts = { cache: 'no-store' };
        try {
            if (ver) {
                var perRel = await fetch('releases/' + encodeURIComponent(ver)
                    + '/search-index.json', opts);
                if (perRel.ok) {
                    searchIndex = await perRel.json();
                    populateModuleSelects();
                    applyHashSelection();
                    return;
                }
            }
            var response = await fetch('search-index.json', opts);
            searchIndex = await response.json();
            populateModuleSelects();
            applyHashSelection();
        } catch (error) {
            console.error('Failed to load search index:', error);
            showNotice('Failed to load module list. Please refresh the page.', 'error');
        }
    }

    // If the URL hash carries left/right, populate the selects and run
    // compareModules() once the dropdowns are ready.
    function applyHashSelection() {
        var h = parseHash();
        if (!h.left && !h.right) return;
        var s1 = document.getElementById('module1');
        var s2 = document.getElementById('module2');
        if (s1 && h.left)  s1.value = h.left;
        if (s2 && h.right) s2.value = h.right;
        if (h.left && h.right) compareModules();
    }

    // === Populate module dropdowns ===

    function populateModuleSelects() {
        var select1 = document.getElementById('module1');
        var select2 = document.getElementById('module2');

        select1.innerHTML = '<option value="">-- Select a YANG module --</option>';
        select2.innerHTML = '<option value="">-- Select a YANG module --</option>';

        var categories = {};
        searchIndex.modules.forEach(function (module) {
            if (module.yangTreeUrl) {
                if (!categories[module.displayCategory]) {
                    categories[module.displayCategory] = [];
                }
                categories[module.displayCategory].push(module);
            }
        });

        Object.keys(categories).sort().forEach(function (category) {
            var optgroup1 = document.createElement('optgroup');
            var optgroup2 = document.createElement('optgroup');
            optgroup1.label = category;
            optgroup2.label = category;

            categories[category].sort(function (a, b) { return a.name.localeCompare(b.name); }).forEach(function (module) {
                var option1 = document.createElement('option');
                var option2 = document.createElement('option');
                option1.value = module.name;
                option2.value = module.name;
                option1.textContent = module.emoji + ' ' + module.name;
                option2.textContent = module.emoji + ' ' + module.name;
                optgroup1.appendChild(option1);
                optgroup2.appendChild(option2);
            });

            select1.appendChild(optgroup1);
            select2.appendChild(optgroup2);
        });
    }

    // === Quick compare presets ===

    function quickCompare(module1, module2) {
        document.getElementById('module1').value = module1;
        document.getElementById('module2').value = module2;
        compareModules();
    }

    // === Load tree content ===

    async function loadTreeContent(moduleName) {
        try {
            var module = searchIndex.modules.find(function (m) { return m.name === moduleName; });
            if (!module || !module.yangTreeUrl) {
                throw new Error('Tree not found');
            }

            var response = await fetch(module.yangTreeUrl);
            var html = await response.text();

            var parser = new DOMParser();
            var doc = parser.parseFromString(html, 'text/html');
            var preElement = doc.querySelector('.tree-container pre');

            if (!preElement) {
                throw new Error('Tree content not found in HTML');
            }

            return {
                content: preElement.textContent,
                module: module
            };
        } catch (error) {
            console.error('Failed to load tree:', error);
            throw error;
        }
    }

    // === Compare modules ===

    async function compareModules() {
        var module1 = document.getElementById('module1').value;
        var module2 = document.getElementById('module2').value;

        if (!module1 || !module2) {
            showNotice('Please select both modules to compare.', 'warning');
            return;
        }

        var container = document.getElementById('comparisonContainer');
        container.classList.add('active');
        document.getElementById('leftTree').innerHTML = '<div class="loading"><div class="loading-spinner"></div>Loading tree...</div>';
        document.getElementById('rightTree').innerHTML = '<div class="loading"><div class="loading-spinner"></div>Loading tree...</div>';

        try {
            var results = await Promise.all([
                loadTreeContent(module1),
                loadTreeContent(module2)
            ]);
            leftTreeData = results[0];
            rightTreeData = results[1];

            document.getElementById('leftModuleName').textContent = leftTreeData.module.name;
            document.getElementById('leftModuleType').textContent = leftTreeData.module.displayCategory;
            document.getElementById('rightModuleName').textContent = rightTreeData.module.name;
            document.getElementById('rightModuleType').textContent = rightTreeData.module.displayCategory;

            // Mirror the current pair into the URL so Copy Share Link
            // produces a permalink that reproduces this comparison.
            writeHash(module1, module2);

            renderComparison();
        } catch (error) {
            showNotice('Failed to load trees. Please try again.', 'error');
            container.classList.remove('active');
        }
    }

    // === Copy share link ===
    function copyShareLink(btn) {
        var url = window.location.href;
        var orig = btn ? btn.textContent : '';
        function flash(label) {
            if (!btn) return;
            btn.textContent = label;
            setTimeout(function () { btn.textContent = orig; }, 3000);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(
                function () { flash('Copied!'); },
                function () { flash('Copy failed'); }
            );
        } else {
            try {
                var ta = document.createElement('textarea');
                ta.value = url;
                ta.style.position = 'absolute';
                ta.style.left = '-9999px';
                document.body.appendChild(ta);
                ta.select();
                var ok = document.execCommand('copy');
                document.body.removeChild(ta);
                flash(ok ? 'Copied!' : 'Copy failed');
            } catch (_) { flash('Copy failed'); }
        }
    }
    // Expose so the page button (and tests) can invoke it directly.
    window.__TreeCompare = { copyShareLink: copyShareLink };

    // === Render comparison ===

    function renderComparison() {
        if (!leftTreeData || !rightTreeData) return;

        var leftLines = leftTreeData.content.split('\n');
        var rightLines = rightTreeData.content.split('\n');

        var leftFilter = document.getElementById('searchLeft').value.toLowerCase();
        var rightFilter = document.getElementById('searchRight').value.toLowerCase();

        var filteredLeft = leftLines.filter(function (line) {
            return !leftFilter || line.toLowerCase().includes(leftFilter);
        });
        var filteredRight = rightLines.filter(function (line) {
            return !rightFilter || line.toLowerCase().includes(rightFilter);
        });

        var stats = calculateDiff(leftLines, rightLines);
        updateStats(stats);

        document.getElementById('leftTree').innerHTML = filteredLeft
            .map(function (line) { return '<div class="line">' + escapeHtml(line) + '</div>'; })
            .join('');
        document.getElementById('rightTree').innerHTML = filteredRight
            .map(function (line) { return '<div class="line">' + escapeHtml(line) + '</div>'; })
            .join('');

        document.getElementById('leftLineCount').textContent = filteredLeft.length + ' lines';
        document.getElementById('rightLineCount').textContent = filteredRight.length + ' lines';
        document.getElementById('leftPanelTitle').textContent = leftTreeData.module.name;
        document.getElementById('rightPanelTitle').textContent = rightTreeData.module.name;

        setupScrollSync();
    }

    // === Calculate diff ===

    function calculateDiff(leftLines, rightLines) {
        var leftSet = new Set(leftLines.map(function (l) { return l.trim(); }).filter(function (l) { return l; }));
        var rightSet = new Set(rightLines.map(function (l) { return l.trim(); }).filter(function (l) { return l; }));

        var added = Array.from(rightSet).filter(function (l) { return !leftSet.has(l); }).length;
        var removed = Array.from(leftSet).filter(function (l) { return !rightSet.has(l); }).length;
        var matched = Array.from(leftSet).filter(function (l) { return rightSet.has(l); }).length;

        return {
            total: leftLines.length + rightLines.length,
            matched: matched,
            added: added,
            removed: removed,
            changed: 0
        };
    }

    function updateStats(stats) {
        document.getElementById('totalLines').textContent = stats.total;
        document.getElementById('matchedLines').textContent = stats.matched;
        document.getElementById('addedLines').textContent = stats.added;
        document.getElementById('removedLines').textContent = stats.removed;
        document.getElementById('changedLines').textContent = stats.changed;
    }

    // === Scroll synchronization ===

    function setupScrollSync() {
        var leftTree = document.getElementById('leftTree');
        var rightTree = document.getElementById('rightTree');

        leftTree.onscroll = function () {
            if (syncScrollEnabled) {
                rightTree.scrollTop = leftTree.scrollTop;
            }
        };

        rightTree.onscroll = function () {
            if (syncScrollEnabled) {
                leftTree.scrollTop = rightTree.scrollTop;
            }
        };
    }

    function toggleSyncScroll() {
        syncScrollEnabled = !syncScrollEnabled;
        document.getElementById('syncScrollBtn').classList.toggle('active');
    }

    function toggleHighlight() {
        highlightEnabled = !highlightEnabled;
        document.getElementById('highlightBtn').classList.toggle('active');
    }

    // === Export comparison ===

    function exportComparison() {
        if (!leftTreeData || !rightTreeData) return;

        var text = 'YANG Tree Comparison Report\n' +
            'Generated: ' + new Date().toLocaleString() + '\n\n' +
            'Left Module: ' + leftTreeData.module.name + '\n' +
            'Right Module: ' + rightTreeData.module.name + '\n\n' +
            '=== LEFT TREE ===\n' + leftTreeData.content + '\n\n' +
            '=== RIGHT TREE ===\n' + rightTreeData.content;

        var blob = new Blob([text], { type: 'text/plain' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'tree-comparison-' + leftTreeData.module.name + '-vs-' + rightTreeData.module.name + '.txt';
        a.click();
        URL.revokeObjectURL(url);
    }

    // === Dark mode ===

    function toggleDarkMode() {
        var currentTheme = document.documentElement.getAttribute('data-theme');
        var newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        var btn = document.querySelector('.dark-mode-toggle');
        btn.textContent = newTheme === 'dark' ? '\u2600\ufe0f' : '\ud83c\udf19';
    }

    // === Utility ===

    function escapeHtml(text) {
        if (text == null) return '';
        return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function showNotice(message, type) {
        var notice = document.getElementById('treeNotice');
        if (!notice) {
            notice = document.createElement('div');
            notice.id = 'treeNotice';
            notice.style.cssText = 'padding:12px 20px;border-radius:8px;margin:12px auto;max-width:600px;text-align:center;font-weight:500;';
            document.querySelector('.controls').appendChild(notice);
        }
        notice.style.display = 'block';
        notice.style.background = type === 'error' ? '#FFEBEE' : '#FFF3E0';
        notice.style.color = type === 'error' ? '#C62828' : '#E65100';
        notice.textContent = message;
        setTimeout(function () { notice.style.display = 'none'; }, 5000);
    }

    // === Initialization ===

    function init() {
        loadSearchIndex();

        // Load theme
        var savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        var btn = document.querySelector('.dark-mode-toggle');
        btn.textContent = savedTheme === 'dark' ? '\u2600\ufe0f' : '\ud83c\udf19';

        // Dark mode toggle
        var darkModeBtn = document.querySelector('.dark-mode-toggle');
        if (darkModeBtn) darkModeBtn.addEventListener('click', toggleDarkMode);

        // Compare button
        var compareBtn = document.getElementById('compareBtn');
        if (compareBtn) compareBtn.addEventListener('click', compareModules);

        // Quick compare presets (use data attributes)
        document.querySelectorAll('[data-quick-left]').forEach(function (el) {
            el.addEventListener('click', function () {
                quickCompare(this.dataset.quickLeft, this.dataset.quickRight);
            });
        });

        // Comparison options
        var syncBtn = document.getElementById('syncScrollBtn');
        if (syncBtn) syncBtn.addEventListener('click', toggleSyncScroll);

        var highlightBtn = document.getElementById('highlightBtn');
        if (highlightBtn) highlightBtn.addEventListener('click', toggleHighlight);

        var exportBtn = document.getElementById('exportBtn');
        if (exportBtn) exportBtn.addEventListener('click', exportComparison);

        var shareBtn = document.getElementById('shareBtn');
        if (shareBtn) shareBtn.addEventListener('click', function () {
            copyShareLink(shareBtn);
        });

        // Filter trees
        document.getElementById('searchLeft').addEventListener('input', renderComparison);
        document.getElementById('searchRight').addEventListener('input', renderComparison);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
