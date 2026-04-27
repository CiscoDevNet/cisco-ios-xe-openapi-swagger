/* telemetry.js — Module-Driven Telemetry XPath Builder.
 *
 * Implements the formula documented in MDT_XPATH_SPEC.md:
 *   filter xpath = "/" + <prefix> + ":" + <path-without-leading-slash>
 *
 * Two modes:
 *  (1) "Module XPath Builder" — pick ANY release / category / module and we
 *      compute the MDT filter xpath for every operation_path in that spec
 *      using the per-release yang-prefix-map.json. Curated tier / cadence
 *      annotations from telemetry-index.json (when present) are folded in
 *      as enrichment, but the xpath itself is always derived live from the
 *      formula — there is no requirement that the entry exist in any
 *      curated catalog.
 *  (2) "Curated Catalog" — preserves the original telemetry-index.json
 *      table for the legacy 61 annotated subscriptions on 17.18.1.
 */
(function () {
  'use strict';

  // --- Static configuration --------------------------------------------------

  // Categories rendered in the builder's category dropdown. Order is the
  // order shown to the user; "oper" is the default because MDT subscriptions
  // are overwhelmingly against operational state.
  var CATEGORIES = [
    { id: 'oper',          label: 'Operational state (oper)' },
    { id: 'cfg',           label: 'Configuration (cfg)' },
    { id: 'native-config', label: 'Native config' },
    { id: 'openconfig',    label: 'OpenConfig' },
    { id: 'ietf',          label: 'IETF' },
    { id: 'mib',           label: 'MIB-aligned' },
    { id: 'events',        label: 'Events / notifications' },
    { id: 'rpc',           label: 'RPCs' },
    { id: 'other',         label: 'Other' }
  ];

  // For 17.18.1 (legacy in-place layout) the prefix map sits at the repo
  // root; every other release gets a per-release file. Returning ``null``
  // for unsupported releases lets the builder render a friendly notice
  // instead of a broken table.
  function prefixMapUrl(ver) {
    if (ver === '17.18.1') return 'yang-prefix-map.json';
    return 'releases/' + encodeURIComponent(ver) + '/yang-prefix-map.json';
  }

  function specBaseUrl(ver, cat) {
    if (ver === '17.18.1') return 'swagger-' + cat + '-model/api-v2/';
    return 'releases/' + encodeURIComponent(ver) + '/swagger-' + cat + '-model/api-v2/';
  }

  function telemetryIndexUrl(ver) {
    if (ver === '17.18.1') return 'releases/17.18.1/telemetry-index.json';
    return 'releases/' + encodeURIComponent(ver) + '/telemetry-index.json';
  }

  // --- State -----------------------------------------------------------------

  var state = {
    ver: null,
    prefixes: {},        // { moduleName: prefix }
    catalog: null,       // telemetry-index.json (curated)
    catalogByXpath: {},  // xpath -> entry, for builder enrichment
    cat: null,
    manifest: null,
    spec: null,
    specName: null
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

  fetch('releases/index.json', { cache: 'no-store' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .catch(function () { return null; })
    .then(initReleases);

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

    // Tab wiring
    var tabs = document.querySelectorAll('.tabs button');
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        tabs.forEach(function (x) { x.classList.remove('active'); });
        t.classList.add('active');
        document.querySelectorAll('.pane').forEach(function (p) { p.classList.remove('active'); });
        $(t.getAttribute('data-pane')).classList.add('active');
      });
    });

    // Category dropdown — populated once; module dropdown is repopulated per
    // category load.
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

    // Catalog pane filter handlers
    ['c-filter', 'c-tier', 'c-onchange'].forEach(function (id) {
      $(id).addEventListener('input', renderCatalog);
    });

    loadRelease(current);
  }

  // --- Release-level loaders -------------------------------------------------

  function loadRelease(ver) {
    state.ver = ver;
    state.prefixes = {};
    state.catalog = null;
    state.catalogByXpath = {};
    state.spec = null;
    state.specName = null;

    var pPrefixes = fetch(prefixMapUrl(ver), { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });

    var pCatalog = fetch(telemetryIndexUrl(ver), { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });

    Promise.all([pPrefixes, pCatalog]).then(function (results) {
      var pm = results[0];
      var cat = results[1];
      state.prefixes = (pm && pm.modules) || {};
      state.catalog = cat;
      state.catalogByXpath = {};
      var entries = (cat && cat.entries) || [];
      entries.forEach(function (e) {
        if (e && e.filter_xpath) state.catalogByXpath[e.filter_xpath] = e;
      });
      // Kick off the default category for the builder, and refresh catalog pane.
      loadCategory($('b-cat').value);
      renderCatalogStats();
      renderCatalog();
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
  // List keys on the FIRST segment (e.g. ``foo=KEY``) are dropped because MDT
  // subscriptions take an unkeyed root xpath. Subsequent ``=...`` selectors
  // are likewise stripped to keep the result a structural xpath. Returns
  // ``null`` if the path can't be normalised (no ``/data/`` prefix, no
  // module qualifier, or unknown module prefix).
  function deriveXpath(opPath, prefixes) {
    if (!opPath) return null;
    var p = opPath;
    // Strip the RESTCONF data root.
    if (p.indexOf('/data/') === 0) p = p.substring('/data/'.length);
    else if (p.indexOf('/restconf/data/') === 0) p = p.substring('/restconf/data/'.length);
    else if (p.charAt(0) === '/') p = p.substring(1);
    // First segment must carry the module qualifier ``Module:container``.
    var firstSlash = p.indexOf('/');
    var first = firstSlash === -1 ? p : p.substring(0, firstSlash);
    var rest  = firstSlash === -1 ? '' : p.substring(firstSlash); // keeps leading "/"
    var colon = first.indexOf(':');
    if (colon === -1) return null;
    var moduleName = first.substring(0, colon);
    var head = first.substring(colon + 1);
    var prefix = prefixes[moduleName];
    if (!prefix) return null;
    // Drop list keys: ``container=KEY,KEY2`` -> ``container``.
    head = head.replace(/=[^/]*$/, '');
    var tail = rest.replace(/=[^/]*(?=\/|$)/g, '');
    return '/' + prefix + ':' + head + tail;
  }

  // --- Rendering: builder ----------------------------------------------------

  function renderModuleInfo(name) {
    var el = $('b-info');
    if (!name) { el.hidden = true; el.innerHTML = ''; return; }
    var prefix = state.prefixes[name] || null;
    var pathCount = state.spec && state.spec.paths
      ? Object.keys(state.spec.paths).length
      : 0;
    var sample = '/data/' + name + ':<container>';
    var derived = prefix
      ? '/' + prefix + ':<container>'
      : '<unknown — no prefix mapped>';
    var html =
      '<div><strong>' + escapeHtml(name) + '</strong>' +
      (prefix ? '' :
        ' &mdash; <span style="color:var(--hot);">no prefix entry in yang-prefix-map.json' +
        ' for this release</span>') +
      '</div>' +
      '<dl>' +
      '<dt>YANG prefix</dt><dd>' + escapeHtml(prefix || '(unknown)') + '</dd>' +
      '<dt>OpenAPI paths</dt><dd>' + pathCount + '</dd>' +
      '<dt>Sample input</dt><dd>' + escapeHtml(sample) + '</dd>' +
      '<dt>Derived xpath</dt><dd>' + escapeHtml(derived) + '</dd>' +
      '</dl>' +
      '<div class="formula">filter xpath /' +
        escapeHtml(prefix || '&lt;prefix&gt;') +
        ':&lt;path-without-leading-slash&gt;</div>';
    el.innerHTML = html;
    el.hidden = false;
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

    var q = $('b-filter').value.trim().toLowerCase();
    var paths = state.spec.paths;
    var rows = [];
    Object.keys(paths).sort().forEach(function (apiPath) {
      var ops = paths[apiPath] || {};
      Object.keys(ops).forEach(function (method) {
        if (['get','post','put','patch','delete'].indexOf(method) === -1) return;
        var xpath = deriveXpath(apiPath, state.prefixes);
        var enriched = (xpath && state.catalogByXpath[xpath]) || null;
        rows.push({
          method: method.toUpperCase(),
          api: apiPath,
          xpath: xpath,
          tier: enriched && enriched.tier,
          cadence: enriched && enriched.cadence_seconds,
          onChange: enriched && enriched.on_change_capable
        });
      });
    });

    if (q) {
      rows = rows.filter(function (r) {
        var hay = (r.api + ' ' + (r.xpath || '')).toLowerCase();
        return hay.indexOf(q) !== -1;
      });
    }

    if (!rows.length) {
      empty.textContent = 'No paths match the current filter.';
      empty.style.display = 'block';
      return;
    }
    empty.style.display = 'none';

    rows.forEach(function (r) {
      var tr = document.createElement('tr');
      var xpathCell = r.xpath
        ? '<td class="xpath">' + escapeHtml(r.xpath) + '</td>'
        : '<td class="xpath" style="color:var(--muted);">(can\'t derive — unknown module prefix)</td>';
      var tierCell = r.tier
        ? '<td><span class="tier ' + escapeHtml(String(r.tier).toUpperCase()) + '">'
            + escapeHtml(r.tier) + '</span></td>'
        : '<td></td>';
      var cadenceCell = r.cadence ? '<td>' + escapeHtml(r.cadence + 's') + '</td>' : '<td></td>';
      var onChangeCell = '<td>' + (r.onChange ? '\u2713' : '') + '</td>';
      var copyCell = r.xpath
        ? '<td><button class="copy-btn" type="button" data-xp="' + escapeHtml(r.xpath) + '">Use</button></td>'
        : '<td></td>';
      tr.innerHTML =
        '<td><span class="method ' + r.method + '">' + r.method + '</span></td>' +
        '<td class="api">' + escapeHtml(r.api) + '</td>' +
        xpathCell + tierCell + cadenceCell + onChangeCell + copyCell;
      tbody.appendChild(tr);
    });

    // Wire "Use" buttons to populate the subscription template.
    Array.prototype.forEach.call(tbody.querySelectorAll('button[data-xp]'),
      function (btn) {
        btn.addEventListener('click', function () {
          var xp = btn.getAttribute('data-xp');
          $('b-snippet').textContent = buildSubscriptionSnippet(xp);
          // Visual confirmation; reset after a moment.
          btn.classList.add('ok');
          btn.textContent = 'Used';
          setTimeout(function () {
            btn.classList.remove('ok');
            btn.textContent = 'Use';
          }, 1200);
        });
      });
  }

  function buildSubscriptionSnippet(xpath) {
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

  // --- Rendering: curated catalog (legacy view) ------------------------------

  function renderCatalogStats() {
    var s = $('c-stats');
    var entries = (state.catalog && state.catalog.entries) || [];
    if (!entries.length) {
      s.innerHTML = '<div class="stat"><div class="num">&mdash;</div>' +
        '<div class="lbl">No telemetry-index.json for ' + escapeHtml(state.ver) + '</div></div>';
      return;
    }
    var byTier = { HOT: 0, WARM: 0, COOL: 0, OTHER: 0 };
    var onChange = 0, modules = {};
    entries.forEach(function (e) {
      var t = (e.tier || '').toUpperCase();
      if (byTier[t] !== undefined) byTier[t]++; else byTier.OTHER++;
      if (e.on_change_capable) onChange++;
      if (e.module) modules[e.module] = true;
    });
    s.innerHTML =
      stat(entries.length, 'XPaths annotated') +
      stat(byTier.HOT,  'HOT') +
      stat(byTier.WARM, 'WARM') +
      stat(byTier.COOL, 'COOL') +
      stat(onChange,    'on-change') +
      stat(Object.keys(modules).length, 'modules');
  }
  function stat(n, l) {
    return '<div class="stat"><div class="num">' + n +
           '</div><div class="lbl">' + escapeHtml(l) + '</div></div>';
  }

  function renderCatalog() {
    var tb = document.querySelector('#c-tbl tbody');
    var emp = $('c-empty');
    clearChildren(tb);
    var entries = (state.catalog && state.catalog.entries) || [];
    var q = $('c-filter').value.trim().toLowerCase();
    var tier = $('c-tier').value;
    var oc = $('c-onchange').value;
    var shown = 0;
    entries.forEach(function (e) {
      if (tier && (e.tier || '').toUpperCase() !== tier) return;
      if (oc === 'true' && !e.on_change_capable) return;
      if (oc === 'false' && e.on_change_capable) return;
      var xp = e.filter_xpath || e.xpath || '';
      if (q) {
        var hay = (xp + ' ' + (e.module || '') + ' ' + (e.feature_title || '')
                 + ' ' + (e.feature_section || '')).toLowerCase();
        if (hay.indexOf(q) === -1) return;
      }
      shown++;
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td class="xpath">' + escapeHtml(xp) + '</td>' +
        '<td>' + escapeHtml(e.module || '') + '</td>' +
        '<td>' + (e.tier ? '<span class="tier ' + escapeHtml((e.tier || '').toUpperCase()) +
                         '">' + escapeHtml(e.tier) + '</span>' : '') + '</td>' +
        '<td>' + (e.cadence_seconds ? escapeHtml(e.cadence_seconds + 's') : '') + '</td>' +
        '<td><span class="badge">' + escapeHtml(e.encoding || 'kvGPB') + '</span></td>' +
        '<td>' + (e.on_change_capable ? '\u2713' : '') + '</td>' +
        '<td>' + (e.feature_section
          ? '<a class="spec-link" href="' + escapeHtml(e.feature_section) + '">view</a>'
          : '') + '</td>';
      tb.appendChild(tr);
    });
    emp.style.display = shown ? 'none' : 'block';
    if (!shown && !entries.length) {
      emp.textContent = 'No curated telemetry-index.json is published for this release yet. '
        + 'Use the Module XPath Builder tab to derive xpaths on the fly.';
    } else if (!shown) {
      emp.textContent = 'No telemetry XPaths match the current filters.';
    }
  }
})();
