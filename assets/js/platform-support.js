/* platform-support.js
 * Loads releases/<ver>/platform-support.json once per release and renders
 * a row of platform chips for the currently-loaded spec.
 *
 * Exposes window.__PlatformSupport:
 *   loadForVersion(ver)        -> Promise<doc | null>
 *   getModulePlatforms(fname)  -> [{id,label,family}, ...]
 *   renderBadges(host, fname)  -> populates host with chip row or fallback message
 *   currentDoc()               -> last successfully loaded doc
 */
(function () {
    'use strict';

    var FAMILY_COLOR = {
        switching: '#1976D2',
        routing:   '#2E7D32',
        iot:       '#EF6C00',
        wireless:  '#6A1B9A',
        other:     '#546E7A'
    };

    var docs = {};       // ver -> doc | null (null = loaded, not available)
    var inflight = {};   // ver -> Promise
    var lastDoc = null;

    function activeVer() {
        if (typeof window.__activeVer === 'function') {
            try { return window.__activeVer(); } catch (_) {}
        }
        return window.__IOSXE_ACTIVE_VERSION__ || null;
    }

    function baseHref() {
        // Each viewer lives at /swagger-XYZ-model/index.html, so platform JSON
        // is one level up at /releases/<ver>/platform-support.json. The hub
        // pages live at root, so try without the '..' prefix too.
        var m = location.pathname.match(/\/(swagger-[^/]+-model|tools|generators)\//);
        return m ? '../' : '';
    }

    function loadForVersion(ver) {
        if (!ver) return Promise.resolve(null);
        if (ver in docs) return Promise.resolve(docs[ver]);
        if (inflight[ver]) return inflight[ver];
        var url = baseHref() + 'releases/' + encodeURIComponent(ver) + '/platform-support.json';
        inflight[ver] = fetch(url, { cache: 'default' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (doc) {
                docs[ver] = doc;
                if (doc) lastDoc = doc;
                delete inflight[ver];
                return doc;
            })
            .catch(function () {
                docs[ver] = null;
                delete inflight[ver];
                return null;
            });
        return inflight[ver];
    }

    function resolveModuleName(fname) {
        if (!lastDoc || !lastDoc.modules || !fname) return fname;
        if (lastDoc.modules[fname]) return fname;
        // Native viewer splits Cisco-IOS-XE-native into sub-specs
        // (native-aaa, native-bgp, native-00-core, ...). All resolve to
        // the single underlying YANG module.
        if (/^native(-|$)/i.test(fname) && lastDoc.modules['Cisco-IOS-XE-native']) {
            return 'Cisco-IOS-XE-native';
        }
        return fname;
    }

    function getModulePlatforms(fname) {
        if (!lastDoc || !lastDoc.modules || !fname) return [];
        var entry = lastDoc.modules[resolveModuleName(fname)];
        if (!entry || !entry.platforms) return [];
        var byId = {};
        (lastDoc.platforms || []).forEach(function (p) { byId[p.id] = p; });
        var out = [];
        entry.platforms.forEach(function (pid) {
            if (byId[pid]) out.push(byId[pid]);
            else out.push({ id: pid, label: pid, family: 'other' });
        });
        return out;
    }

    function getModuleRevision(fname) {
        if (!lastDoc || !lastDoc.modules || !fname) return null;
        var entry = lastDoc.modules[resolveModuleName(fname)];
        return entry ? (entry.revision || null) : null;
    }

    function chip(p, rev) {
        var color = FAMILY_COLOR[p.family] || FAMILY_COLOR.other;
        var tip = p.label + ' (' + p.id + ')';
        if (rev) tip += ' — module revision ' + rev;
        return '<span class="platform-chip" data-pid="' + p.id + '" data-family="' + p.family +
               '" title="' + tip.replace(/"/g, '&quot;') + '" ' +
               'style="display:inline-block;padding:2px 8px;margin:2px 4px 2px 0;border-radius:10px;' +
               'background:' + color + ';color:#fff;font-size:11px;font-weight:500;line-height:1.4;' +
               'white-space:nowrap;cursor:help;">' + p.id + '</span>';
    }

    function renderBadges(host, fname) {
        if (!host) return;
        var ver = activeVer();
        host.style.display = 'block';
        host.innerHTML = '<span style="color:#888;font-size:12px;">Loading platform support…</span>';
        loadForVersion(ver).then(function (doc) {
            if (!doc) {
                host.innerHTML = '<span style="color:#888;font-size:12px;font-style:italic;">' +
                    'Platform support data not available for release ' + (ver || '?') + '.</span>';
                return;
            }
            var plats = getModulePlatforms(fname);
            if (!plats.length) {
                host.innerHTML = '<span style="color:#888;font-size:12px;font-style:italic;">' +
                    'No NETCONF capability entry for <code>' + fname +
                    '</code> in release ' + ver + ' (module may be Swagger-only, augment, ' +
                    'or named differently in capability files).</span>';
                return;
            }
            var rev = getModuleRevision(fname);
            var label = '<span style="color:#444;font-size:12px;font-weight:600;margin-right:6px;">' +
                'Supported on:</span>';
            host.innerHTML = label + plats.map(function (p) { return chip(p, rev); }).join('');
        });
    }

    window.__PlatformSupport = {
        loadForVersion: loadForVersion,
        getModulePlatforms: getModulePlatforms,
        getModuleRevision: getModuleRevision,
        renderBadges: renderBadges,
        currentDoc: function () { return lastDoc; }
    };
})();
