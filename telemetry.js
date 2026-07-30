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
    modules: [],    // sorted module names in the current category
    spec: null,
    specName: null,
    xport: 'grpc',  // selected subscription transport: grpc | netconf | gnmi
    lastXpath: null, // last xpath sent to the config box (for transport switching)
    versionStats: {}, // per-release totals from version-stats.json (big numbers)
    pendingRestore: null // deep-link state to reapply once async loads finish
  };

  // --- DOM helpers -----------------------------------------------------------

  function $(id) { return document.getElementById(id); }
  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function clearChildren(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  // --- Deep-link hash (shareable URLs) ---------------------------------------
  // The URL hash carries the full selection so a link reopens the same view.
  // This tab owns the keys: tab, ver, cat, mod, xpath, xport. The notifications
  // pane owns q, ntransport, ncat, nmod. _writeHash preserves any key it does
  // not own, so the two panes never clobber each other. replaceState is used so
  // updates don't spam history or fire a hashchange loop.
  function _readHash() {
    var out = {};
    var h = (location.hash || '').replace(/^#/, '');
    h.split('&').forEach(function (kv) {
      if (!kv) return;
      var i = kv.indexOf('=');
      var k = i < 0 ? kv : kv.slice(0, i);
      var v = i < 0 ? '' : kv.slice(i + 1);
      if (k) { try { out[k] = decodeURIComponent(v); } catch (_) { out[k] = v; } }
    });
    return out;
  }
  function _writeHash(updates) {
    try {
      var cur = _readHash();
      Object.keys(updates).forEach(function (k) {
        var v = updates[k];
        if (v == null || v === '') delete cur[k];
        else cur[k] = v;
      });
      var s = Object.keys(cur).map(function (k) {
        return k + '=' + encodeURIComponent(cur[k]);
      }).join('&');
      history.replaceState(null, '', location.pathname + location.search + (s ? '#' + s : ''));
    } catch (_) { /* noop */ }
  }

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
    _writeHash({ tab: name });
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
    // CSP-safe cross-tab links (e.g. "See Event Notifications") that switch
    // panes in place and scroll back to the top.
    var jumps = document.querySelectorAll('[data-goto-tab]');
    for (var g = 0; g < jumps.length; g++) {
      (function (link) {
        link.addEventListener('click', function (e) {
          e.preventDefault();
          selectTab(link.getAttribute('data-goto-tab'));
          try { window.scrollTo({ top: 0, behavior: 'smooth' }); }
          catch (_) { window.scrollTo(0, 0); }
        });
      })(jumps[g]);
    }
    // Initial tab from #tab= (deep-link), then ?tab= / #<tab>.
    var want = 'telemetry';
    try {
      var hp = _readHash();
      if (hp.tab) want = hp.tab;
      else {
        var qp = new URLSearchParams(location.search).get('tab');
        if (qp) want = qp;
        else if (/(^|#|&)notifications\b/.test(location.hash)) want = 'notifications';
      }
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
    rsel.addEventListener('change', function () {
      loadRelease(rsel.value);
      _writeHash({ ver: rsel.value, mod: null, xpath: null, xport: null });
    });

    var csel = $('b-cat');
    CATEGORIES.forEach(function (c) {
      var o = document.createElement('option');
      o.value = c.id;
      o.textContent = c.label;
      csel.appendChild(o);
    });
    // Restore category + stage module/xpath/transport from a shared link.
    var hp0 = _readHash();
    if (hp0.cat && CATEGORIES.some(function (c) { return c.id === hp0.cat; })) csel.value = hp0.cat;
    else csel.value = 'oper';
    if (hp0.mod) {
      state.pendingRestore = { mod: hp0.mod, xpath: hp0.xpath || null, xport: hp0.xport || null };
    }
    csel.addEventListener('change', function () {
      loadCategory(csel.value);
      _writeHash({ cat: csel.value, mod: null, xpath: null, xport: null });
    });
    $('b-mod').addEventListener('change', function () {
      var v = $('b-mod').value;
      loadModule(v);
      _writeHash({ mod: v, xpath: null, xport: null });
    });
    var modFilter = $('b-mod-filter');
    if (modFilter) modFilter.addEventListener('input', function () {
      populateModuleSelect(modFilter.value);
    });
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
          var x = btn.getAttribute('data-xport');
          selectXport(x);
          if (state.lastXpath) _writeHash({ xport: x });
        });
      });
    var csvBtn = $('b-csv');
    if (csvBtn) csvBtn.addEventListener('click', function () { exportRowsCsv(csvBtn); });
    var copyLinkBtn = $('b-copylink');
    if (copyLinkBtn) copyLinkBtn.addEventListener('click', function () {
      copyText(location.href, copyLinkBtn);
      track('telemetry_link_copied', {
        yang_model: state.specName, model_category: state.cat, xpath: state.lastXpath
      });
    });

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
    state.modules = [];
    state.spec = null;
    state.specName = null;
    var filt = $('b-mod-filter');
    if (filt) filt.value = '';
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
        state.modules = ((data && data.modules) || []).slice().sort();
        populateModuleSelect('');
        renderModuleInfo(null);
        renderBuilderTable();
        // Deep-link restore: auto-select the module named in the shared URL.
        if (state.pendingRestore && state.pendingRestore.mod &&
            state.modules.indexOf(state.pendingRestore.mod) !== -1) {
          var msel2 = $('b-mod');
          if (msel2) msel2.value = state.pendingRestore.mod;
          loadModule(state.pendingRestore.mod);
        } else if (state.pendingRestore && !state.pendingRestore.xpath) {
          state.pendingRestore = null;  // module missing and nothing else to restore
        }
      });
  }

  // Display label for a module option. Native-config specs are split into
  // generator chunks named native-<container> (with native-NN-* foundational
  // bundles), which reads as "by category". Strip the native- and numeric
  // ordering prefixes so the dropdown lists clean container names (router-bgp,
  // aaa, interface…) alphabetically, like the Swagger API. The option *value*
  // stays the real module name so the right spec still loads.
  function moduleLabel(name) {
    if (state.cat === 'native-config') {
      return name.replace(/^native-/, '').replace(/^\d+-/, '');
    }
    return name;
  }

  // Populate the module dropdown, optionally narrowed by a filter string.
  // Large categories (native-config has 400+ modules) are unusable as a flat
  // dropdown, so the filter input live-narrows the options.
  function populateModuleSelect(filter) {
    var msel = $('b-mod');
    if (!msel) return;
    clearChildren(msel);
    var mods = (state.modules || []).slice().sort(function (a, b) {
      var la = moduleLabel(a).toLowerCase(), lb = moduleLabel(b).toLowerCase();
      return la < lb ? -1 : (la > lb ? 1 : 0);
    });
    if (!mods.length) {
      var none = document.createElement('option');
      none.value = '';
      none.textContent = '(no modules in this category for this release)';
      none.disabled = true;
      msel.appendChild(none);
      return;
    }
    var q = (filter || '').trim().toLowerCase();
    var shown = q
      ? mods.filter(function (m) {
          return m.toLowerCase().indexOf(q) !== -1 ||
                 moduleLabel(m).toLowerCase().indexOf(q) !== -1;
        })
      : mods;
    var placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = q
      ? '— ' + shown.length + ' of ' + mods.length + ' modules match —'
      : '— choose a module (' + mods.length + ' available) —';
    msel.appendChild(placeholder);
    shown.forEach(function (name) {
      var o = document.createElement('option');
      o.value = name;
      o.textContent = moduleLabel(name);
      msel.appendChild(o);
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
        try {
          if (window.analytics) window.analytics.trackDataModelSelected({
            yang_model: name, model_category: state.cat,
            release: state.ver, page_or_section: 'telemetry'
          });
        } catch (e) { /* noop */ }
        // Open a subscription-build workflow on module load; closed on "Use in config".
        try {
          if (window.analytics && window.analytics.startWorkflow) {
            window.__iosxeWf = window.__iosxeWf || {};
            window.__iosxeWf.telemetry = window.analytics.startWorkflow('telemetry_subscription_built', {
              yang_model: name, model_category: state.cat, release: state.ver, page_or_section: 'telemetry'
            });
          }
        } catch (e) { /* noop */ }
        // Deep-link restore: rebuild the subscription for the shared xpath.
        if (state.pendingRestore && state.pendingRestore.xpath) {
          var pr = state.pendingRestore; state.pendingRestore = null;
          state.lastXpath = pr.xpath;
          selectXport(pr.xport || state.xport);  // builds the snippet from lastXpath
        } else {
          state.pendingRestore = null;
        }
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
        'Example &mdash; the OpenAPI path on the left becomes the telemetry ' +
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
  // modules and the full YANG data-path / telemetry surface); the last two
  // cards drill into the current category and selected module so the grid
  // stays responsive to the picker.
  function renderStats() {
    var el = $('b-stats');
    if (!el) return;
    var rel = (state.versionStats && state.versionStats[state.ver]) || null;
    var modules = (state.manifest && state.manifest.modules) || [];
    var sub = '\u2014';
    if (state.spec && state.spec.paths) {
      var mib = isMibCat();
      // Count *unique* derived xpaths (the subscribable filter targets), not
      // operations — a path with GET/PUT/PATCH/DELETE still maps to one xpath.
      var seen = {};
      var d = 0;
      Object.keys(state.spec.paths).forEach(function (apiPath) {
        var xp = deriveXpath(apiPath, state.prefixes, mib);
        if (!xp) return;  // underivable / MIB bare-entry duplicates
        if (!seen[xp]) { seen[xp] = 1; d++; }
      });
      sub = d;
    }
    function fmt(n) {
      return (typeof n === 'number') ? n.toLocaleString('en-US') : n;
    }
    var relXpaths = rel
      ? (rel.telemetry_xpaths != null ? rel.telemetry_xpaths : rel.paths)
      : null;
    var cards = [
      { num: rel ? fmt(rel.modules_with_specs) : '\u2014', lbl: 'Modules in release' },
      { num: relXpaths != null ? fmt(relXpaths) : '\u2014', lbl: 'Telemetry xpaths' },
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
          track('telemetry_xpath_copied', {
            yang_model: state.specName, model_category: state.cat,
            xpath: cell.getAttribute('data-xp')
          });
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
          track('telemetry_xpath_used', {
            yang_model: state.specName, model_category: state.cat,
            xpath: xp, transport: state.xport
          });
          _writeHash({ xpath: xp, xport: state.xport });
          try {
            if (window.analytics && window.analytics.completeWorkflow) {
              window.__iosxeWf = window.__iosxeWf || {};
              var _twf = window.__iosxeWf.telemetry
                || (window.analytics.startWorkflow && window.analytics.startWorkflow('telemetry_subscription_built', { yang_model: state.specName, model_category: state.cat, release: state.ver, page_or_section: 'telemetry' }));
              window.analytics.completeWorkflow(_twf, {
                workflow: 'telemetry_subscription_built', status: 'success',
                yang_model: state.specName, model_category: state.cat,
                transport: state.xport, release: state.ver,
                page_or_section: 'telemetry'
              });
              window.__iosxeWf.telemetry = null;
            }
          } catch (e) { /* noop */ }
        });
      });
  }

  function track(name, props) {
    try {
      var data = { release: state.ver };
      if (props) Object.keys(props).forEach(function (k) { if (props[k] != null) data[k] = props[k]; });
      if (typeof window.__iosxeTrack === 'function') window.__iosxeTrack(name, data);
    } catch (_) { /* noop */ }
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
    try {
      if (window.analytics) window.analytics.trackExportResults({
        export_type: 'telemetry_csv', row_count: rows.length,
        yang_model: state.specName, model_category: state.cat,
        release: state.ver, result: 'success', page_or_section: 'telemetry'
      });
    } catch (e) { /* noop */ }
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
      netconf: 'NETCONF dynamic subscription (ncc + raw RPC)',
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
      // RFC 8641 yang-push dynamic subscription. Two equivalent forms: a
      // quick one-liner using the ncc validation tool (so the subscription
      // can be confirmed end-to-end), and the raw RPC sent over the NETCONF
      // session (TCP 830). period is in centiseconds (3000 = 30s).
      return [
        '# Quick validation with the ncc tool (github.com/CiscoDevNet/ncc):',
        './ncc-establish-subscription.py --host <DEVICE-IP> --port 830 \\',
        '    -u <user> -p <pass> \\',
        '    --xpath ' + xpath + ' \\',
        '    --period 3000',
        '',
        '# --- equivalent raw RFC 8641 yang-push RPC over the NETCONF session: ---',
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
