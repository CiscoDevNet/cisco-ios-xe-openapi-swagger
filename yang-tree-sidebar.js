/* yang-tree-sidebar.js — shared recursive YANG container tree sidebar.
 *
 * Each path /data/<module>:<root>/<container>/<container>/.../<leaf>
 * (or /streams/..., /operations/...) is broken into:
 *   prefix    = "data" | "streams" | "operations"      (NOT shown)
 *   root      = "<module>:<root>"                       (top-level node)
 *   segs[]    = the YANG container/list chain under root
 * RESTCONF list keys (e.g. `interface={name}`) are stripped so the tree
 * mirrors the YANG schema rather than the URL form.
 *
 * Public API:
 *   window.YangTreeSidebar.build(allModules)
 *     → containerTree root node { name:'', children:Map, ... }
 *     allModules: [{ fname, pathList:[string], pathOps:{[path]:opId} }]
 *
 *   window.YangTreeSidebar.render(containerTree, hostEl, opts)
 *     opts = {
 *       filter: 'substring',         // case-insensitive
 *       currentModule: 'fname',      // for .selected highlight
 *       onLoad: (fname, el, opId) => void,   // click handler
 *       collapseAllByDefault: true,  // recommended for multi-root viewers
 *       storageKey: 'yang-tree-cfg', // when set, expansion state persists
 *                                    // in localStorage across reloads
 *     }
 *     → { visibleTops, matched }     // for the "x of y" label
 *
 *   window.YangTreeSidebar.toggle(rowEl, evt)  — invoked from inline onclick
 */
(function () {
    'use strict';

    function _escape(s) {
        return String(s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function _emptyNode(name) {
        return { name: name, children: new Map(), ownPathSpec: null, ownPathOpId: null, totalPaths: 0 };
    }

    function _splitPath(p) {
        // Returns { prefix, root, segs } or null when the path is unrecognised.
        if (!p || p[0] !== '/') return null;
        var raw = p.slice(1);
        if (!raw) return null;
        var parts = raw.split('/');
        var prefix = parts[0]; // data | streams | operations
        if (prefix !== 'data' && prefix !== 'streams' && prefix !== 'operations') return null;
        if (parts.length < 2) return null;
        var root = parts[1].replace(/=.*/, '');
        var segs = parts.slice(2).map(function (s) { return s.replace(/=.*/, ''); }).filter(Boolean);
        return { prefix: prefix, root: root, segs: segs };
    }

    function build(allModules) {
        var root = _emptyNode('');
        // Sort specs by name so the *first* spec to claim a node wins
        // deterministically across reloads.
        var sorted = allModules.slice().sort(function (a, b) { return a.fname.localeCompare(b.fname); });
        for (var i = 0; i < sorted.length; i++) {
            var m = sorted[i];
            var paths = m.pathList || [];
            for (var j = 0; j < paths.length; j++) {
                var p = paths[j];
                var s = _splitPath(p);
                if (!s) continue;
                root.totalPaths++;
                // Top level: the root container (e.g. wlan-cfg-data, native, etc.)
                if (!root.children.has(s.root)) {
                    root.children.set(s.root, _emptyNode(s.root));
                }
                var node = root.children.get(s.root);
                node.totalPaths++;
                if (s.segs.length === 0) {
                    // The path *is* the root itself.
                    if (!node.ownPathSpec) {
                        node.ownPathSpec = m.fname;
                        node.ownPathOpId = (m.pathOps || {})[p] || null;
                    }
                    continue;
                }
                for (var k = 0; k < s.segs.length; k++) {
                    var seg = s.segs[k];
                    if (!node.children.has(seg)) {
                        node.children.set(seg, _emptyNode(seg));
                    }
                    node = node.children.get(seg);
                    node.totalPaths++;
                }
                if (!node.ownPathSpec) {
                    node.ownPathSpec = m.fname;
                    node.ownPathOpId = (m.pathOps || {})[p] || null;
                }
            }
        }
        _groupSiblingsByModule(root);
        return root;
    }

    // Some modules (notably YANG `notifications` modules like
    // Cisco-IOS-XE-ios-events-oper) produce dozens of sibling top-level paths
    // shaped `/data/<module>:<leaf>` with no shared parent container. The
    // builder above keys each top-level entry by `<module>:<leaf>`, so they
    // would otherwise appear as a long flat list of unrelated siblings.
    //
    // Walk the tree and, at each level, find sibling nodes whose names share
    // a `<module>:` prefix. When 2+ siblings share that prefix, wrap them in
    // a synthetic node named `<module>` so the sidebar groups them under a
    // single disclosure.
    function _groupSiblingsByModule(node) {
        if (!node.children || !node.children.size) return;
        // Recurse first so deeper levels are also grouped.
        node.children.forEach(function (child) { _groupSiblingsByModule(child); });
        // Bucket children by `<module>:` prefix (only the leading qualifier
        // before the first `:`). Children that don't have a `:` go into a
        // null bucket and are left alone.
        var buckets = new Map();
        node.children.forEach(function (child, key) {
            var idx = key.indexOf(':');
            if (idx <= 0) return;
            var mod = key.substring(0, idx);
            if (!buckets.has(mod)) buckets.set(mod, []);
            buckets.get(mod).push(key);
        });
        buckets.forEach(function (keys, mod) {
            if (keys.length < 2) return;
            // Build a synthetic group node containing the bucketed children.
            var group = _emptyNode(mod);
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i];
                var child = node.children.get(key);
                // Strip the `<module>:` prefix from the child's display name
                // so the grouped row reads cleanly (e.g. `severity-level`
                // instead of `Cisco-IOS-XE-ios-events-oper:severity-level`).
                child.name = key.substring(mod.length + 1) || key;
                group.children.set(child.name, child);
                group.totalPaths += child.totalPaths;
                // Promote the first child's owning spec onto the synthetic
                // group so clicking the module-name row loads that spec's
                // page. Children of a `<module>:` bucket all come from the
                // same OpenAPI spec, so any child's ownPathSpec works.
                if (!group.ownPathSpec && child.ownPathSpec) {
                    group.ownPathSpec = child.ownPathSpec;
                    group.ownPathOpId = null; // group row → no specific op
                }
                node.children.delete(key);
            }
            node.children.set(mod, group);
        });
    }

    function _renderNode(node, depth, pathSoFar, filterRe, expandAll, currentModule) {
        var fullPath = pathSoFar ? pathSoFar + '/' + node.name : node.name;
        var selfMatch = !filterRe || filterRe.test(fullPath);
        var childrenHtml = '';
        var descendantMatch = false;
        if (node.children.size) {
            var sortedChildren = [];
            node.children.forEach(function (v) { sortedChildren.push(v); });
            sortedChildren.sort(function (a, b) { return a.name.localeCompare(b.name); });
            for (var i = 0; i < sortedChildren.length; i++) {
                var r = _renderNode(sortedChildren[i], depth + 1, fullPath, filterRe, expandAll, currentModule);
                if (r) {
                    childrenHtml += r.html;
                    if (r.matched) descendantMatch = true;
                }
            }
        }
        if (filterRe && !selfMatch && !descendantMatch) return null;
        var hasKids = node.children.size > 0;
        var fname = node.ownPathSpec;
        var opId = node.ownPathOpId;
        // Auto-expand when filtering and a descendant matched, or when caller
        // forces expandAll. Never auto-expand the top container in multi-root
        // viewers — caller passes expandAll=false.
        var expanded = (filterRe && descendantMatch) || expandAll;
        var collapsedClass = hasKids ? (expanded ? '' : ' collapsed') : '';
        var arrow = hasKids
            ? '<span class="tree-arrow">&#9660;</span>'
            : '<span class="tree-arrow tree-arrow-empty"></span>';
        var toggleAttr = hasKids ? 'onclick="YangTreeSidebar.toggle(this, event)"' : '';
        var selected = (fname && currentModule === fname) ? ' selected' : '';
        var opArg = opId ? "'" + _escape(opId) + "'" : 'null';
        var loadAttr = fname
            ? 'data-module="' + _escape(fname) + '" onclick="event.stopPropagation(); YangTreeSidebar._click(\'' + _escape(fname) + '\', this, ' + opArg + '); return false;"'
            : 'onclick="event.stopPropagation(); return false;"';
        var labelAttr = fname ? loadAttr : '';
        var indent = depth * 12;
        var pathBadge = node.totalPaths > 1 ? '<span class="path-count">' + node.totalPaths + '</span>' : '';
        var fnameBadge = fname ? '<span class="leaf-spec">' + _escape(fname) + '</span>' : '';
        var pathAttr = hasKids ? ' data-tree-path="' + _escape(fullPath) + '"' : '';
        var html =
            '<div class="tree-row' + collapsedClass + selected + '" data-depth="' + depth + '"' + pathAttr + ' style="padding-left:' + indent + 'px" ' + toggleAttr + '>' +
                arrow +
                '<span class="tree-label" ' + labelAttr + '><code>' + _escape(node.name) + '</code>' + fnameBadge + '</span>' +
                pathBadge +
            '</div>' +
            '<div class="tree-children' + collapsedClass + '">' + childrenHtml + '</div>';
        return { html: html, matched: selfMatch || descendantMatch };
    }

    function render(containerTree, hostEl, opts) {
        opts = opts || {};
        var filter = (opts.filter || '').trim();
        var filterRe = null;
        if (filter) {
            var safe = filter.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            filterRe = new RegExp(safe, 'i');
        }
        // Click handler — stash on the namespace so the inline onclick can find it.
        window.YangTreeSidebar._currentOnLoad = opts.onLoad || function () {};
        // Persist storageKey on the host so toggle() can find it later.
        if (opts.storageKey) {
            hostEl.setAttribute('data-tree-storage-key', opts.storageKey);
        } else {
            hostEl.removeAttribute('data-tree-storage-key');
        }
        var html = '';
        var visibleTops = 0;
        var tops = [];
        containerTree.children.forEach(function (v) { tops.push(v); });
        tops.sort(function (a, b) { return a.name.localeCompare(b.name); });
        // expandAll: when filtering OR when caller didn't ask to collapse. For
        // single-root viewers (native), top is auto-expanded. For multi-root,
        // pass collapseAllByDefault=true.
        var expandAllTop = !!filterRe || !opts.collapseAllByDefault;
        for (var i = 0; i < tops.length; i++) {
            var r = _renderNode(tops[i], 0, '', filterRe, expandAllTop, opts.currentModule);
            if (r) { html += r.html; visibleTops++; }
        }
        hostEl.innerHTML = html;
        // Apply persisted expand/collapse state. We only honor it when there is
        // no active filter — a filter forces an open view of matching subtrees.
        if (opts.storageKey && !filterRe) {
            var saved = _readState(opts.storageKey);
            if (saved) {
                var rows = hostEl.querySelectorAll('.tree-row[data-tree-path]');
                for (var j = 0; j < rows.length; j++) {
                    var row = rows[j];
                    var path = row.getAttribute('data-tree-path');
                    if (!(path in saved)) continue;
                    var wantCollapsed = !!saved[path];
                    var isCollapsed = row.classList.contains('collapsed');
                    if (wantCollapsed !== isCollapsed) {
                        row.classList.toggle('collapsed');
                        var kids = row.nextElementSibling;
                        if (kids && kids.classList.contains('tree-children')) {
                            kids.classList.toggle('collapsed');
                        }
                    }
                }
            }
        }
        var matched = hostEl.querySelectorAll('.tree-row').length;
        return { visibleTops: visibleTops, matched: matched };
    }

    function _readState(key) {
        try {
            var raw = window.localStorage.getItem('YangTreeSidebar:' + key);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            return (parsed && typeof parsed === 'object') ? parsed : null;
        } catch (_) { return null; }
    }

    function _writeState(key, state) {
        try {
            window.localStorage.setItem('YangTreeSidebar:' + key, JSON.stringify(state));
        } catch (_) { /* quota / disabled — ignore */ }
    }

    function toggle(rowEl, evt) {
        if (evt) evt.stopPropagation();
        rowEl.classList.toggle('collapsed');
        var kids = rowEl.nextElementSibling;
        if (kids && kids.classList.contains('tree-children')) kids.classList.toggle('collapsed');
        // Persist the new state if the host opted in.
        var host = rowEl.parentElement;
        while (host && !host.hasAttribute('data-tree-storage-key')) host = host.parentElement;
        if (!host) return;
        var key = host.getAttribute('data-tree-storage-key');
        var path = rowEl.getAttribute('data-tree-path');
        if (!key || !path) return;
        var state = _readState(key) || {};
        state[path] = rowEl.classList.contains('collapsed');
        _writeState(key, state);
    }

    function _click(fname, el, opId) {
        var fn = window.YangTreeSidebar._currentOnLoad;
        if (typeof fn === 'function') fn(fname, el, opId);
    }

    window.YangTreeSidebar = {
        build: build,
        render: render,
        toggle: toggle,
        _click: _click,
        _currentOnLoad: null,
    };
})();
