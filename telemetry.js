/* telemetry.js — Module-Driven Telemetry XPath Builder.
 *
 * Implements the formula documented in MDT_XPATH_SPEC.md:
 *   filter xpath = "/" + <prefix> + ":" + <path-without-leading-slash>
 *
 * Pick any release / category / module and we compute the MDT
 * filter xpath for every operation in that spec, derived live from the
 * formula. The xpath is always derived; there is no curated catalog.
 */
(function () {
  'use strict';

  // --- Static configuration --------------------------------------------------

  // Categories rendered in the builder's category dropdown. "oper" is the
  // default because MDT subscriptions are overwhelmingly against
  // operational state.
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

    loadRelease(current);
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
  function deriveXpath(opPath, prefixes) {
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
    var head = first.substring(colon + 1);
    var prefix = prefixes[moduleName];
    if (!prefix) return null;
    head = head.replace(/=[^/]*$/, '');
    var tail = rest.replace(/=[^/]*(?=\/|$)/g, '');
    return '/' + prefix + ':' + head + tail;
  }

  // --- Rendering -------------------------------------------------------------

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
        rows.push({ method: method.toUpperCase(), api: apiPath, xpath: xpath });
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
      var copyCell = r.xpath
        ? '<td><button class="copy-btn" type="button" data-xp="' + escapeHtml(r.xpath) + '">Use</button></td>'
        : '<td></td>';
      tr.innerHTML =
        '<td><span class="method ' + r.method + '">' + r.method + '</span></td>' +
        '<td class="api">' + escapeHtml(r.api) + '</td>' +
        xpathCell + copyCell;
      tbody.appendChild(tr);
    });

    Array.prototype.forEach.call(tbody.querySelectorAll('button[data-xp]'),
      function (btn) {
        btn.addEventListener('click', function () {
          var xp = btn.getAttribute('data-xp');
          $('b-snippet').textContent = buildSubscriptionSnippet(xp);
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
})();
