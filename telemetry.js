/* telemetry.js — "Telemetry & Notifications" page controller.
 *
 * Hosts two tabs:
 *   1. Telemetry XPaths — the MDT filter-xpath builder. Implements the
 *      formula documented in MDT_XPATH_SPEC.md:
 *        filter xpath = "/" + <prefix> + ":" + <path-without-leading-slash>
 *      Pick any release / category / module and we compute the MDT filter
 *      xpath for every operation in that spec, derived live. The xpath is
 *      always derived; there is no curated catalog.
 *   2. Event Notifications — the YANG notification catalog, rendered into
 *      #pane-notifications by notifications.js.
 *
 * This file owns tab switching (incl. ?tab= / #notifications deep-links) and
 * the xpath builder; the catalog is self-contained in notifications.js.
 */
(function () {
  'use strict';

  // --- Static configuration --------------------------------------------------

  // Categories rendered in the builder's category dropdown. "oper" is the
  // default because MDT subscriptions are overwhelmingly against
  // operational state. RPCs (actions, not subscribable) stay excluded. MIBs
  // ARE subscribable, but only via the SNMP -> MDT bridge: their xpath is
  // derived by a different, deterministic rule (/<MOD>:<MOD>/...) and they
  // need an SNMP community configured, so the page surfaces an extra
  // prerequisite block when a MIB module is selected.
  var CATEGORIES = [
    { id: 'oper',          label: 'Operational state (oper)' },
    { id: 'cfg',           label: 'Configuration (cfg)' },
    { id: 'native-config', label: 'Native config' },
    { id: 'openconfig',    label: 'OpenConfig' },
    { id: 'ietf',          label: 'IETF' },
    { id: 'mib',           label: 'MIB (via SNMP \u2192 MDT bridge)' },
    { id: 'other',         label: 'Other' }
  ];

  function isMibCat() { return state.cat === 'mib'; }

  // For 17.18.1 (legacy in-place layout) the prefix map sits at the repo
  // root; every other release gets a per-release file.
  function prefixMapUrl(ver) {
    if (ver === '17.18.1') return 'yang-prefix-map.json';
    return 'releases/' + encodeURIComponent(ver) + '/yang-prefix-map.json';
  }

  function specBaseUrl(ver, cat) {
    if (ver === '17.18.1') return 'swagger-' + cat + '-model/api/';
    return 'releases/' + encodeURIComponent(ver) + '/swagger-' + cat + '-model/api/';
  }

  // --- State -----------------------------------------------------------------

  var state = {
    ver: null,
    prefixes: {},   // { moduleName: prefix }
    cat: null,
    manifest: null,
    spec: null,
    specName: null,
    xport: 'grpc',  // selected subscription transport: grpc | netconf | gnmi
    lastXpath: null, // last xpath sent to the config box (for transport switching)
    versionStats: {} // per-release totals from version-stats.json (big numbers)
  };

  // --- DOM helpers -----------------------------------------------------------

  function $(id) { return document.getElementById(id); }
  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function clearChildren(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  // --- Boot ------------------------------------------------------------------

  initTabs();

  fetch('releases/index.json', { cache: 'no-store' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .catch(function () { return null; })
    .then(initReleases);

  // Precomputed per-release totals (spec/path/module counts) power the
  // headline metric cards so they show big, release-wide numbers without
  // having to fetch and parse every spec.
  fetch('version-stats.json', { cache: 'no-store' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .catch(function () { return null; })
    .then(function (vs) {
      state.versionStats = (vs && vs.totals) || {};
      renderStats();
    });

  // Two-tab layout: "Telemetry XPaths" (this builder) and "Event
  // Notifications" (the catalog rendered by notifications.js into
  // #pane-notifications). Switching is pure show/hide; both panes' scripts
  // initialise on load. ?tab=notifications (or #notifications) deep-links the
  // catalog tab — used by the per-module panel in the Swagger viewers.
  function selectTab(name) {
    var tabs = document.querySelectorAll('.tabs [data-tab]');
    for (var i = 0; i < tabs.length; i++) {
      var t = tabs[i];
      var on = t.getAttribute('data-tab') === name;
      t.classList.toggle('active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    }
    var panes = document.querySelectorAll('.pane[data-pane]');
    for (var j = 0; j < panes.length; j++) {
      var p = panes[j];
      p.classList.toggle('active', p.getAttribute('data-pane') === name);
    }
    try {
      if (typeof window.__iosxeTrack === 'function') {
        window.__iosxeTrack('telemetry_tab', { tab: name });
      }
    } catch (_) { /* noop */ }
  }

  function initTabs() {
    var tabs = document.querySelectorAll('.tabs [data-tab]');
    if (!tabs.length) return;
    for (var i = 0; i < tabs.length; i++) {
      (function (btn) {
        btn.addEventListener('click', function () {
          selectTab(btn.getAttribute('data-tab'));
        });
      })(tabs[i]);
    }
    // Initial tab from ?tab= or #<tab>.
    var want = 'telemetry';
    try {
      var qp = new URLSearchParams(location.search).get('tab');
      if (qp) want = qp;
      else if (/(^|#)notifications\b/.test(location.hash)) want = 'notifications';
    } catch (_) { /* noop */ }
    selectTab(want === 'notifications' ? 'notifications' : 'telemetry');
  }

  function initReleases(data) {
    var releases = (data && data.releases) || [{ ver: '26.1.1', label: '26.1.1' }];
    var hashVer = (location.hash.match(/(?:^|[#&])ver=([^&]+)/) || [])[1];
    var stored = null;
    try { stored = localStorage.getItem('iosxe-active-version'); } catch (_) {}
    var current = hashVer || stored || (data && data.default) || releases[0].ver;

    var rsel = $('release');
    releases.forEach(function (r) {
      var o = document.createElement('option');
      o.value = r.ver;
      o.textContent = (r.label || r.ver) + (r.status === 'planned' ? ' (planned)' : '');
      if (r.status === 'planned') o.disabled = true;
      if (r.ver === current) o.selected = true;
      rsel.appendChild(o);
    });
    rsel.addEventListener('change', function () { loadRelease(rsel.value); });

    var csel = $('b-cat');
    CATEGORIES.forEach(function (c) {
      var o = document.createElement('option');
      o.value = c.id;
      o.textContent = c.label;
      csel.appendChild(o);
    });
    csel.value = 'oper';
    csel.addEventListener('change', function () { loadCategory(csel.value); });
    $('b-mod').addEventListener('change', function () { loadModule($('b-mod').value); });
    $('b-filter').addEventListener('input', renderBuilderTable);
    $('b-copy-snippet').addEventListener('click', function () {
      var btn = $('b-copy-snippet');
      copyText($('b-snippet').textContent, btn);
    });
    var comm = $('b-comm');
    if (comm) comm.addEventListener('input', updateSnmpCli);
    var copySnmp = $('b-copy-snmp');
    if (copySnmp) copySnmp.addEventListener('click', function () {
      copyText($('b-snmp-cli').textContent, copySnmp);
    });
    Array.prototype.forEach.call(
      document.querySelectorAll('.xport-tabs [data-xport]'),
      function (btn) {
        btn.addEventListener('click', function () {
          selectXport(btn.getAttribute('data-xport'));
        });
      });
    var csvBtn = $('b-csv');
    if (csvBtn) csvBtn.addEventListener('click', function () { exportRowsCsv(csvBtn); });

    registerShortcuts();

    loadRelease(current);
  }

  // Page-specific keyboard shortcuts, surfaced in the '?' dialog via the
  // shared window.__SHORTCUTS array (consumed by site-chrome.js).
  function registerShortcuts() {
    var SH = window.__SHORTCUTS = window.__SHORTCUTS || [];
    SH.push({ keys: '/', label: 'Focus the path filter' });
    SH.push({ keys: 'E', label: 'Export the current rows as CSV' });
    SH.push({ keys: 'C', label: 'Copy the generated YANG-push snippet' });
    document.addEventListener('keydown', function (e) {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      var t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' ||
                t.tagName === 'SELECT' || t.isContentEditable)) return;
      var k = e.key;
      if (k === '/') {
        var f = $('b-filter'); if (f) { e.preventDefault(); f.focus(); f.select && f.select(); }
      } else if (k === 'e' || k === 'E') {
        var c = $('b-csv'); if (c) { e.preventDefault(); c.click(); }
      } else if (k === 'c' || k === 'C') {
        var s = $('b-copy-snippet'); if (s) { e.preventDefault(); s.click(); }
      }
    });
  }

  // --- Release-level loaders -------------------------------------------------

  function loadRelease(ver) {
    state.ver = ver;
    state.prefixes = {};
    state.spec = null;
    state.specName = null;

    fetch(prefixMapUrl(ver), { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; })
      .then(function (pm) {
        state.prefixes = (pm && pm.modules) || {};
        loadCategory($('b-cat').value);
      });
  }

  function loadCategory(cat) {
    state.cat = cat;
    state.manifest = null;
    state.spec = null;
    state.specName = null;
    var msel = $('b-mod');
    clearChildren(msel);
    var loading = document.createElement('option');
    loading.textContent = 'Loading…';
    loading.disabled = true;
    msel.appendChild(loading);

    fetch(specBaseUrl(state.ver, cat) + 'manifest.json', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; })
      .then(function (data) {
        state.manifest = data;
        clearChildren(msel);
        var modules = (data && data.modules) || [];
        if (!modules.length) {
          var none = document.createElement('option');
          none.textContent = '(no modules in this category for this release)';
          none.disabled = true;
          msel.appendChild(none);
          renderModuleInfo(null);
          renderBuilderTable();
          return;
        }
        var placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = '— choose a module (' + modules.length + ' available) —';
        msel.appendChild(placeholder);
        modules.slice().sort().forEach(function (name) {
          var o = document.createElement('option');
          o.value = name;
          o.textContent = name;
          msel.appendChild(o);
        });
        renderModuleInfo(null);
        renderBuilderTable();
      });
  }

  function loadModule(name) {
    if (!name) {
      state.spec = null;
      state.specName = null;
      renderModuleInfo(null);
      renderBuilderTable();
      return;
    }
    state.specName = name;
    fetch(specBaseUrl(state.ver, state.cat) + encodeURIComponent(name) + '.json',
          { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; })
      .then(function (spec) {
        state.spec = spec;
        renderModuleInfo(name);
        renderBuilderTable();
      });
  }

  // --- Formula ---------------------------------------------------------------

  // Convert an OpenAPI operation path like
  //    /data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization
  // into the MDT filter xpath
  //    /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization
  // per MDT_XPATH_SPEC.md §1.
  //
  // List keys (e.g. ``foo=KEY``) are dropped because MDT subscriptions take
  // an unkeyed root xpath. Returns ``null`` if the path can't be normalised
  // (no ``/data/`` prefix, no module qualifier, or unknown module prefix).
  //
  // MIB modules (``isMib``) derive by a different, prefix-map-free rule. A
  // MIB OpenAPI path
  //    /data/IF-MIB:ifTable/ifEntry
  // becomes the telemetry filter xpath
  //    /IF-MIB:IF-MIB/ifTable/ifEntry
  // i.e. the module name is BOTH the prefix and the repeated top container
  // (validated against a live device). Keyed entry rows collapse to their
  // keyless table/entry target (all rows stream; keys come back as tags).
  // The flattened bare-entry duplicate paths some generators emit (e.g.
  // /data/IF-MIB:ifEntry, with no parent table) are dropped — their derived
  // xpath would be invalid because the model nests the entry under its table.
  function deriveXpath(opPath, prefixes, isMib) {
    if (!opPath) return null;
    var p = opPath;
    if (p.indexOf('/data/') === 0) p = p.substring('/data/'.length);
    else if (p.indexOf('/restconf/data/') === 0) p = p.substring('/restconf/data/'.length);
    else if (p.charAt(0) === '/') p = p.substring(1);
    var firstSlash = p.indexOf('/');
    var first = firstSlash === -1 ? p : p.substring(0, firstSlash);
    var rest  = firstSlash === -1 ? '' : p.substring(firstSlash);
    var colon = first.indexOf(':');
    if (colon === -1) return null;
    var moduleName = first.substring(0, colon);
    var head = first.substring(colon + 1).replace(/=[^/]*$/, '');
    var tail = rest.replace(/=[^/]*(?=\/|$)/g, '');
    if (isMib) {
      // Drop flattened bare-entry duplicates (canonical entries live under
      // their *Table parent, where head is the table and tail is /...Entry).
      if (/Entry$/.test(head)) return null;
      return '/' + moduleName + ':' + moduleName + '/' + head + tail;
    }
    var prefix = prefixes[moduleName];
    if (!prefix) return null;
    return '/' + prefix + ':' + head + tail;
  }

  // --- Rendering -------------------------------------------------------------

  function renderModuleInfo(name) {
    var el = $('b-info');
    var mib = isMibCat();
    renderSnmpPrereq(mib && !!name);
    renderStats();
    if (!name) { el.hidden = true; el.innerHTML = ''; return; }
    var prefix = mib ? null : (state.prefixes[name] || null);
    var paths = (state.spec && state.spec.paths) ? Object.keys(state.spec.paths) : [];

    // Build a real worked example from the module's first derivable path,
    // so users see actual values instead of <container> placeholders. The
    // count reflects genuinely-derivable (subscribable) paths.
    var exampleApi = null, exampleXpath = null, derivable = 0;
    for (var i = 0; i < paths.length; i++) {
      var xp = deriveXpath(paths[i], state.prefixes, mib);
      if (xp) {
        derivable++;
        if (!exampleApi) { exampleApi = paths[i]; exampleXpath = xp; }
      }
    }

    var badge = mib
      ? ' <span class="mib-badge" title="Streams via the SNMP \u2192 MDT bridge; requires an SNMP community (see below)">via SNMP \u2192 MDT</span>'
      : '';

    var html =
      '<div><strong>' + escapeHtml(name) + '</strong>' + badge +
      (mib || prefix ? '' :
        ' &mdash; <span style="color:var(--hot);">no prefix entry in yang-prefix-map.json' +
        ' for this release</span>') +
      '</div>' +
      '<dl>' +
      (mib
        ? '<dt>MDT prefix</dt><dd>' + escapeHtml(name + ':' + name) + '</dd>'
        : '<dt>YANG prefix</dt><dd>' + escapeHtml(prefix || '(unknown)') + '</dd>') +
      '<dt>Subscribable paths</dt><dd>' + derivable + '</dd>' +
      '</dl>';

    if (exampleApi) {
      html +=
        '<div style="margin-top:6px;font-size:.82rem;color:var(--muted);">' +
        'Example &mdash; the RESTCONF path on the left becomes the telemetry ' +
        'filter xpath on the right:</div>' +
        '<div class="formula" style="margin-top:6px;">' +
        '<span style="color:var(--muted);">' + escapeHtml(exampleApi) + '</span>' +
        '<span style="margin:0 8px;">&rarr;</span>' +
        '<strong>' + escapeHtml(exampleXpath) + '</strong></div>';
    }

    el.innerHTML = html;
    el.hidden = false;
  }

  // Top-of-page metric cards, mirroring the Event Notifications tab. The
  // headline numbers are release-wide totals from version-stats.json (total
  // modules and the full RESTCONF/telemetry path surface); the last two cards
  // drill into the current category and selected module so the grid stays
  // responsive to the picker.
  function renderStats() {
    var el = $('b-stats');
    if (!el) return;
    var rel = (state.versionStats && state.versionStats[state.ver]) || null;
    var modules = (state.manifest && state.manifest.modules) || [];
    var sub = '\u2014';
    if (state.spec && state.spec.paths) {
      var mib = isMibCat();
      var d = 0;
      Object.keys(state.spec.paths).forEach(function (apiPath) {
        var methods = state.spec.paths[apiPath] || {};
        Object.keys(methods).forEach(function (m) {
          if (['get','post','put','patch','delete'].indexOf(m) === -1) return;
          var xp = deriveXpath(apiPath, state.prefixes, mib);
          if (mib && !xp) return;  // bare-entry duplicates are not real targets
          if (xp) d++;
        });
      });
      sub = d;
    }
    function fmt(n) {
      return (typeof n === 'number') ? n.toLocaleString('en-US') : n;
    }
    var cards = [
      { num: rel ? fmt(rel.modules_with_specs) : '\u2014', lbl: 'Modules in release' },
      { num: rel ? fmt(rel.paths) : '\u2014', lbl: 'RESTCONF data paths' },
      { num: rel ? fmt(rel.yang_modules) : '\u2014', lbl: 'YANG modules' },
      { num: modules.length || 0, lbl: 'Modules in category' },
      { num: fmt(sub), lbl: 'Subscribable xpaths (module)' }
    ];
    el.innerHTML = cards.map(function (c) {
      return '<div class="stat"><div class="num">' + c.num +
        '</div><div class="lbl">' + escapeHtml(c.lbl) + '</div></div>';
    }).join('');
    el.hidden = false;
  }

  // SNMP prerequisite block: only MIB telemetry needs it. MDT reads MIB data
  // through the SNMP subsystem, so the device needs an SNMP community that
  // the NETCONF/MDT internal agent is told to use — and the two community
  // strings MUST match. The community field is editable and live-fills both
  // CLI lines.
  function renderSnmpPrereq(show) {
    var box = $('b-snmp');
    if (!box) return;
    box.hidden = !show;
    if (show) updateSnmpCli();
  }

  function updateSnmpCli() {
    var pre = $('b-snmp-cli');
    if (!pre) return;
    var input = $('b-comm');
    var comm = (input && input.value.trim()) || 'mycommunity';
    pre.textContent = [
      'netconf-yang',
      'snmp-server community ' + comm + ' RO',
      'netconf-yang cisco-ia snmp-community-string ' + comm
    ].join('\n');
  }

  function _builderRows() {
    if (!state.spec || !state.spec.paths) return [];
    var q = ($('b-filter').value || '').trim().toLowerCase();
    var mib = isMibCat();
    var paths = state.spec.paths;
    var rows = [];
    Object.keys(paths).sort().forEach(function (apiPath) {
      var ops = paths[apiPath] || {};
      Object.keys(ops).forEach(function (method) {
        if (['get','post','put','patch','delete'].indexOf(method) === -1) return;
        var xpath = deriveXpath(apiPath, state.prefixes, mib);
        // For MIBs, the flattened bare-entry duplicates derive to null and are
        // not real subscribe targets, so drop them rather than show a wall of
        // "(not subscribable)" rows.
        if (mib && !xpath) return;
        rows.push({ method: method.toUpperCase(), api: apiPath, xpath: xpath });
      });
    });
    if (q) {
      rows = rows.filter(function (r) {
        var hay = (r.api + ' ' + (r.xpath || '')).toLowerCase();
        return hay.indexOf(q) !== -1;
      });
    }
    return rows;
  }

  function renderBuilderTable() {
    var tbody = document.querySelector('#b-tbl tbody');
    var empty = $('b-empty');
    clearChildren(tbody);

    if (!state.spec || !state.spec.paths) {
      empty.textContent = state.specName
        ? 'Spec ' + state.specName + ' has no paths or failed to load.'
        : 'Pick a category and module to see derived xpaths.';
      empty.style.display = 'block';
      return;
    }

    var rows = _builderRows();

    if (!rows.length) {
      empty.textContent = 'No paths match the current filter.';
      empty.style.display = 'block';
      return;
    }
    empty.style.display = 'none';

    rows.forEach(function (r) {
      var tr = document.createElement('tr');
      var xpathCell = r.xpath
        ? '<td class="xpath copyable" title="Click to copy this xpath" data-xp="' + escapeHtml(r.xpath) + '">' + escapeHtml(r.xpath) + '</td>'
        : '<td class="xpath" style="color:var(--muted);">(not subscribable)</td>';
      var copyCell = r.xpath
        ? '<td><button class="copy-btn" type="button" data-use="' + escapeHtml(r.xpath) + '">Use in config</button></td>'
        : '<td></td>';
      tr.innerHTML =
        '<td><span class="method ' + r.method + '">' + r.method + '</span></td>' +
        '<td class="api">' + escapeHtml(r.api) + '</td>' +
        xpathCell + copyCell;
      tbody.appendChild(tr);
    });

    // Click an xpath cell to copy just the xpath string.
    Array.prototype.forEach.call(tbody.querySelectorAll('td.copyable'),
      function (cell) {
        cell.addEventListener('click', function () {
          copyText(cell.getAttribute('data-xp'), null);
          var prev = cell.style.background;
          cell.style.background = 'rgba(56,142,60,.15)';
          setTimeout(function () { cell.style.background = prev; }, 600);
          track('telemetry_xpath_copied');
        });
      });

    // "Use in config" populates the subscription template at the top.
    Array.prototype.forEach.call(tbody.querySelectorAll('button[data-use]'),
      function (btn) {
        btn.addEventListener('click', function () {
          var xp = btn.getAttribute('data-use');
          state.lastXpath = xp;
          $('b-snippet').textContent = buildSubscriptionSnippet(xp, state.xport);
          btn.classList.add('ok');
          btn.textContent = 'Added \u2713';
          setTimeout(function () {
            btn.classList.remove('ok');
            btn.textContent = 'Use in config';
          }, 1200);
          // Flash the (sticky) config box so the user sees where it went.
          var box = document.querySelector('.snippet-box');
          if (box) {
            box.classList.remove('flash');
            void box.offsetWidth;  // restart the animation
            box.classList.add('flash');
          }
          track('telemetry_xpath_used');
        });
      });
  }

  function track(name) {
    try { if (typeof window.__iosxeTrack === 'function') window.__iosxeTrack(name, { release: state.ver }); }
    catch (_) { /* noop */ }
  }

  // === CSV export ====================================================
  // Dumps the currently-visible builder rows (Method, OpenAPI path, MDT
  // filter xpath) to a downloadable CSV that honors RFC 4180 quoting. Excel
  // auto-detects UTF-8 because we prefix a BOM.

  function _csvCell(value) {
    var s = value == null ? '' : String(value);
    if (/[",\r\n]/.test(s)) {
      s = '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  }

  function exportRowsCsv(btn) {
    var rows = _builderRows();
    if (!rows.length) {
      var orig = btn.textContent;
      btn.textContent = 'No rows';
      setTimeout(function () { btn.textContent = orig; }, 2000);
      return;
    }
    var lines = [['Method', 'OpenAPI Path', 'MDT Filter Xpath'].map(_csvCell).join(',')];
    rows.forEach(function (r) {
      lines.push([r.method, r.api, r.xpath || ''].map(_csvCell).join(','));
    });
    var csv = '\uFEFF' + lines.join('\r\n') + '\r\n';
    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    var ts = new Date().toISOString().slice(0, 10);
    var parts = ['telemetry-paths'];
    if (state.ver) parts.push(state.ver);
    if (state.specName) parts.push(String(state.specName).replace(/[^A-Za-z0-9._-]+/g, '_'));
    parts.push(ts);
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = parts.join('-') + '.csv';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
    var origLabel = btn.textContent;
    btn.textContent = 'Exported ' + rows.length;
    setTimeout(function () { btn.textContent = origLabel; }, 2500);
  }

  // The three subscription "proofs" share one derived xpath. gRPC dial-out is
  // the configured (model-driven telemetry) form; NETCONF is a dynamic
  // RFC 8641 yang-push <establish-subscription> RPC; gNMI is a gnmic sample
  // subscribe. Switching the selector rebuilds the box for the last xpath.
  function selectXport(x) {
    if (['grpc', 'netconf', 'gnmi'].indexOf(x) === -1) x = 'grpc';
    state.xport = x;
    Array.prototype.forEach.call(
      document.querySelectorAll('.xport-tabs [data-xport]'),
      function (b) {
        var on = b.getAttribute('data-xport') === x;
        b.classList.toggle('active', on);
        b.setAttribute('aria-selected', on ? 'true' : 'false');
      });
    var titles = {
      grpc: 'gRPC dial-out subscription config',
      netconf: 'NETCONF dynamic subscription RPC',
      gnmi: 'gNMI subscribe command'
    };
    var titleEl = $('b-snippet-title');
    if (titleEl) titleEl.textContent = titles[x];
    if (state.lastXpath) {
      $('b-snippet').textContent = buildSubscriptionSnippet(state.lastXpath, x);
    }
    track('telemetry_xport_' + x);
  }

  function buildSubscriptionSnippet(xpath, xport) {
    if (xport === 'netconf') {
      // RFC 8641 yang-push dynamic subscription, sent over the NETCONF
      // session (TCP 830). period is in centiseconds (3000 = 30s).
      return [
        '<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">',
        '  <establish-subscription',
        '      xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"',
        '      xmlns:yp="urn:ietf:params:xml:ns:yang:ietf-yang-push">',
        '    <stream>yp:yang-push</stream>',
        '    <yp:xpath-filter>' + xpath + '</yp:xpath-filter>',
        '    <yp:period>3000</yp:period>',
        '  </establish-subscription>',
        '</rpc>'
      ].join('\n');
    }
    if (xport === 'gnmi') {
      // gNMI streaming subscription (sample mode) via gnmic. gNMI listens on
      // TCP 57400 by default on IOS-XE.
      return [
        'gnmic -a <DEVICE-IP>:57400 -u <user> -p <pass> --insecure \\',
        '  subscribe --mode stream --stream-mode sample --sample-interval 30s \\',
        '  --path "' + xpath + '"'
      ].join('\n');
    }
    // Default: gRPC dial-out (configured model-driven telemetry).
    return [
      'telemetry ietf subscription 101',
      ' encoding encode-kvgpb',
      ' filter xpath ' + xpath,
      ' source-address <DEVICE-IP>',
      ' stream yang-push',
      ' update-policy periodic 3000',
      ' receiver ip address <COLLECTOR-IP> 57500 protocol grpc-tcp',
      '!'
    ].join('\n');
  }

  function copyText(text, btn) {
    var ok = function () {
      if (!btn) return;
      var prev = btn.textContent;
      btn.textContent = 'Copied';
      btn.classList.add('ok');
      setTimeout(function () { btn.textContent = prev; btn.classList.remove('ok'); }, 1200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok, function () { fallback(text); ok(); });
      return;
    }
    fallback(text); ok();
  }
  function fallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', '');
    ta.style.position = 'absolute'; ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (_) {}
    document.body.removeChild(ta);
  }
})();
