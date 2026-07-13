/* code-generator.js — Code generator page controller (extracted from inline script) */
(function () {
    'use strict';

    var loadedSpec = null;
    var allSpecModules = [];
    var allPaths = [];

    // === Active release ==================================================
    // Honour ?ver=… / #ver=… / localStorage so the spec picker pulls from
    // releases/<ver>/search-index.json when the user came in from a release.

    function _activeVersion() {
        try {
            var qs = new URLSearchParams(location.search).get('ver');
            if (qs) return qs;
            var m = (location.hash || '').match(/[#&]ver=([^&]+)/);
            if (m) return decodeURIComponent(m[1]);
        } catch (_) { /* noop */ }
        if (window.__IOSXE_ACTIVE_VERSION__) return window.__IOSXE_ACTIVE_VERSION__;
        try {
            var ls = localStorage.getItem('iosxe-active-version');
            if (ls) return ls;
        } catch (_) { /* noop */ }
        return null;
    }

    function _searchIndexUrl() {
        var ver = _activeVersion();
        if (ver) return 'releases/' + encodeURIComponent(ver) + '/search-index.json';
        return 'search-index.json';
    }

    function _specBaseUrl(category, name) {
        // The release dirs mirror the live tree (swagger-*-model/api/<name>.json),
        // so just rebase on releases/<ver>/ when a release is active.
        var ver = _activeVersion();
        var prefix = ver ? 'releases/' + encodeURIComponent(ver) + '/' : '';
        return prefix + category + '/api/' + name + '.json';
    }

    // === Hash deep-link ==================================================
    // Hash shape:
    //   #ver=<release>&category=<cat>&spec=<name>&path=<encoded>&method=<verb>
    // Lets users share / bookmark a fully-populated form (everything but the
    // password, which we never persist).

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
            var picker = document.getElementById('specPicker');
            if (picker && picker.value) {
                var opt = picker.selectedOptions[0];
                if (opt) {
                    if (opt.dataset.category) parts.push('category=' + encodeURIComponent(opt.dataset.category));
                    if (opt.dataset.name) parts.push('spec=' + encodeURIComponent(opt.dataset.name));
                }
            }
            var pathPicker = document.getElementById('pathPicker');
            if (pathPicker && pathPicker.value) {
                parts.push('path=' + encodeURIComponent(pathPicker.value));
            }
            var method = document.getElementById('method');
            if (method && method.value && method.value !== 'GET') {
                parts.push('method=' + encodeURIComponent(method.value));
            }
            var next = parts.length ? '#' + parts.join('&') : ' ';
            if (location.hash !== next) {
                history.replaceState(null, '', location.pathname + location.search + next);
            }
        } catch (_) { /* noop */ }
    }

    function _bindShareBtn() {
        var btn = document.getElementById('cgShareBtn');
        if (!btn || btn.__bound) return;
        btn.__bound = true;
        btn.addEventListener('click', function () {
            _writeHash();
            if (window.__DeepLink && typeof window.__DeepLink.copyShareLink === 'function') {
                try { window.__DeepLink.copyShareLink(btn); return; } catch (_) { /* fall through */ }
            }
            var url = location.href;
            var orig = btn.textContent;
            var done = function () {
                btn.textContent = 'Copied!';
                setTimeout(function () { btn.textContent = orig; }, 3000);
            };
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url).then(done, function () { window.prompt('Copy this URL:', url); });
            } else {
                window.prompt('Copy this URL:', url);
            }
        });
    }

    // === Show/hide body input based on method ===

    function initMethodToggle() {
        document.getElementById('method').addEventListener('change', function () {
            var bodyGroup = document.getElementById('bodyGroup');
            var method = this.value;
            bodyGroup.style.display = ['POST', 'PUT', 'PATCH'].includes(method) ? 'block' : 'none';
            _writeHash();
        });
    }

    // === Code Generation ===

    function generateCode() {
        var host = document.getElementById('host').value;
        var method = document.getElementById('method').value;
        var path = document.getElementById('path').value;
        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;
        var body = document.getElementById('body').value;

        var url = 'https://' + host + path;

        // Generate curl code
        var curlCode = 'curl -k -X ' + method + ' \\\n';
        curlCode += '  "' + url + '" \\\n';
        curlCode += '  -H "Accept: application/yang-data+json" \\\n';
        if (['POST', 'PUT', 'PATCH'].includes(method)) {
            curlCode += '  -H "Content-Type: application/yang-data+json" \\\n';
        }
        curlCode += '  -u "' + username + ':' + password + '"';
        if (['POST', 'PUT', 'PATCH'].includes(method) && body) {
            curlCode += ' \\\n  -d \'' + body + '\'';
        }

        // Generate Python code
        var pythonCode = '#!/usr/bin/env python3\n' +
            '"""\nCisco IOS XE RESTCONF API Example\nGenerated: ' + new Date().toISOString() + '\n"""\n\n' +
            'import requests\nimport json\nfrom urllib3.exceptions import InsecureRequestWarning\n\n' +
            '# Disable SSL warnings (not recommended for production)\n' +
            'requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)\n\n' +
            '# Device credentials\nhost = "' + host + '"\nusername = "' + username + '"\npassword = "' + password + '"\n\n' +
            '# API endpoint\nurl = f"https://{host}' + path + '"\n\n' +
            '# Headers\nheaders = {\n    "Accept": "application/yang-data+json",\n    "Content-Type": "application/yang-data+json"\n}\n';

        if (['POST', 'PUT', 'PATCH'].includes(method) && body) {
            pythonCode += '\n# Request body\npayload = ' + body + '\n\n' +
                '# Make request\nresponse = requests.' + method.toLowerCase() + '(\n' +
                '    url,\n    headers=headers,\n    auth=(username, password),\n    json=payload,\n    verify=False\n)\n';
        } else {
            pythonCode += '\n# Make request\nresponse = requests.' + method.toLowerCase() + '(\n' +
                '    url,\n    headers=headers,\n    auth=(username, password),\n    verify=False\n)\n';
        }

        pythonCode += '\n# Check response\nprint(f"Status Code: {response.status_code}")\n' +
            'if response.status_code in [200, 201, 204]:\n    print("Success!")\n' +
            '    if response.text:\n        print(json.dumps(response.json(), indent=2))\nelse:\n' +
            '    print(f"Error: {response.text}")';

        // Generate Ansible code
        var ansibleCode = '---\n# Cisco IOS XE RESTCONF API Playbook\n' +
            '# Generated: ' + new Date().toISOString() + '\n\n' +
            '- name: Cisco IOS XE RESTCONF Example\n  hosts: localhost\n  gather_facts: no\n  \n  vars:\n' +
            '    iosxe_host: "' + host + '"\n    iosxe_user: "' + username + '"\n' +
            '    iosxe_pass: "' + password + '"\n    api_path: "' + path + '"\n  \n  tasks:\n' +
            '    - name: ' + method + ' request to IOS XE RESTCONF\n      uri:\n' +
            '        url: "https://{{ iosxe_host }}{{ api_path }}"\n        method: ' + method + '\n' +
            '        user: "{{ iosxe_user }}"\n        password: "{{ iosxe_pass }}"\n' +
            '        force_basic_auth: yes\n        validate_certs: no\n        headers:\n' +
            '          Accept: "application/yang-data+json"\n          Content-Type: "application/yang-data+json"';

        if (['POST', 'PUT', 'PATCH'].includes(method) && body) {
            ansibleCode += '\n        body: |\n          ' + body + '\n        body_format: json';
        }

        ansibleCode += '\n        status_code:\n          - 200\n          - 201\n          - 204\n' +
            '      register: api_response\n    \n    - name: Display response\n      debug:\n' +
            '        var: api_response.json\n      when: api_response.json is defined';

        // Generate JavaScript (fetch) code
        var jsCode = '// Cisco IOS XE RESTCONF API Example\n' +
            '// Generated: ' + new Date().toISOString() + '\n\n' +
            'const host = "' + host + '";\nconst username = "' + username + '";\n' +
            'const password = "' + password + '";\n\n' +
            'const url = `https://${host}' + path + '`;\n\n' +
            'const headers = {\n  "Accept": "application/yang-data+json",\n' +
            '  "Content-Type": "application/yang-data+json",\n' +
            '  "Authorization": "Basic " + btoa(`${username}:${password}`)\n};\n\n' +
            'const options = {\n  method: "' + method + '",\n  headers: headers,';

        if (['POST', 'PUT', 'PATCH'].includes(method) && body) {
            jsCode += '\n  body: JSON.stringify(' + body + '),';
        }

        jsCode += '\n};\n\nfetch(url, options)\n  .then(response => {\n' +
            '    console.log(`Status: ${response.status}`);\n' +
            '    if (!response.ok) throw new Error(`HTTP ${response.status}`);\n' +
            '    return response.json();\n  })\n' +
            '  .then(data => console.log(JSON.stringify(data, null, 2)))\n' +
            '  .catch(error => console.error("Error:", error));';

        // Update code blocks
        document.getElementById('curlCode').textContent = curlCode;
        document.getElementById('pythonCode').textContent = pythonCode;
        document.getElementById('ansibleCode').textContent = ansibleCode;
        document.getElementById('javascriptCode').textContent = jsCode;

        // Show output section
        document.getElementById('outputSection').style.display = 'block';
        document.getElementById('outputSection').scrollIntoView({ behavior: 'smooth' });

        // Analytics: highest-intent action on the site — someone produced a
        // ready-to-run snippet. Tag by method + selected spec + RESTCONF path
        // only (never the host, username, or password field values).
        try {
            if (typeof window.__iosxeTrack === 'function') {
                var _picker = document.getElementById('specPicker');
                var _spec = (_picker && _picker.selectedOptions && _picker.selectedOptions[0]
                    && _picker.selectedOptions[0].dataset.name) || '';
                window.__iosxeTrack('code_generated', { http_method: (method || '').toUpperCase(), spec: _spec, op_path: path || '' });
                if (window.analytics) window.analytics.trackWorkflowCompleted({
                    workflow: 'code_generated',
                    api_operation: ((method || '').toUpperCase() + ' ' + (path || '')).trim(),
                    yang_model: _spec, http_method: (method || '').toUpperCase(),
                    page_or_section: 'code-generator'
                });
            }
        } catch (e) { /* noop */ }
    }

    function switchTab(tab, btn) {
        document.querySelectorAll('.tab-content').forEach(function (t) { t.classList.remove('active'); });
        document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
        document.getElementById(tab + 'Tab').classList.add('active');
        btn.classList.add('active');
    }

    function copyCode(elementId) {
        var code = document.getElementById(elementId).textContent;
        navigator.clipboard.writeText(code).then(function () {
            var btn = document.querySelector('[data-copy-target="' + elementId + '"]');
            if (!btn) return;
            var originalText = btn.textContent;
            btn.textContent = '\u2705 Copied!';
            setTimeout(function () { btn.textContent = originalText; }, 2000);
        }).catch(function () {
            // Fallback: select text for manual copy
        });
        // Analytics: which language snippet people actually take away.
        try {
            if (typeof window.__iosxeTrack === 'function') {
                var lang = String(elementId || '').replace(/Code$/, '');
                window.__iosxeTrack('snippet_copied', { snippet_language: lang });
            }
        } catch (e) { /* noop */ }
    }

    function clearForm() {
        document.getElementById('host').value = '10.0.0.1';
        document.getElementById('method').value = 'GET';
        document.getElementById('path').value = '/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces';
        document.getElementById('username').value = 'admin';
        document.getElementById('password').value = 'cisco123';
        document.getElementById('body').value = '';
        document.getElementById('bodyGroup').style.display = 'none';
        document.getElementById('outputSection').style.display = 'none';
        document.getElementById('specPicker').value = '';
        document.getElementById('specSearch').value = '';
        document.getElementById('pathSearch').value = '';
        document.getElementById('pathPickerGroup').style.display = 'none';
        filterSpecPicker();
    }

    // === Spec Picker ===

    function filterSpecPicker() {
        var query = document.getElementById('specSearch').value.toLowerCase().trim();
        var picker = document.getElementById('specPicker');
        picker.innerHTML = '<option value="">— Manual path entry —</option>';

        var filtered = query
            ? allSpecModules.filter(function (m) {
                return m.name.toLowerCase().includes(query) ||
                    (m.keywords || []).some(function (k) { return k.toLowerCase().includes(query); });
            })
            : allSpecModules;

        // Group by category
        var groups = {};
        filtered.forEach(function (m) {
            var label = m.displayCategory;
            if (!groups[label]) groups[label] = [];
            groups[label].push(m);
        });

        Object.entries(groups).sort().forEach(function (entry) {
            var groupLabel = entry[0];
            var mods = entry[1];
            var optgroup = document.createElement('optgroup');
            optgroup.label = groupLabel;
            mods.sort(function (a, b) { return a.name.localeCompare(b.name); }).forEach(function (m) {
                var opt = document.createElement('option');
                opt.value = m.swaggerUrl || '';
                opt.dataset.category = m.category;
                opt.dataset.version = m.version || '';
                opt.dataset.name = m.name;
                opt.textContent = m.name + ' (' + (m.pathCount || 0) + ' paths)';
                optgroup.appendChild(opt);
            });
            picker.appendChild(optgroup);
        });

        document.getElementById('specCount').textContent = filtered.length + ' of ' + allSpecModules.length + ' modules';
    }

    function filterPathPicker() {
        var query = document.getElementById('pathSearch').value.toLowerCase().trim();
        var picker = document.getElementById('pathPicker');
        picker.innerHTML = '<option value="">— Select a path —</option>';

        var filtered = query ? allPaths.filter(function (p) { return p.path.toLowerCase().includes(query); }) : allPaths;
        filtered.forEach(function (p) {
            var opt = document.createElement('option');
            opt.value = p.path;
            opt.textContent = p.path + '  [' + p.methods + ']';
            picker.appendChild(opt);
        });
    }

    async function loadSpecPicker() {
        try {
            var url = _searchIndexUrl();
            var resp = await fetch(url, { cache: 'no-store' });
            if (!resp.ok && url !== 'search-index.json') {
                // Per-release index missing — fall back to the root one.
                resp = await fetch('search-index.json', { cache: 'no-store' });
            }
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            var data = await resp.json();
            allSpecModules = data.modules;
            filterSpecPicker();
            _restoreFromHash();
        } catch (e) {
            console.error('Failed to load search index for spec picker:', e);
            var picker = document.getElementById('specPicker');
            if (picker) {
                var opt = document.createElement('option');
                opt.textContent = '\u26a0\ufe0f Failed to load modules \u2014 please refresh';
                opt.disabled = true;
                picker.innerHTML = '';
                picker.appendChild(opt);
            }
        }
    }

    async function onSpecSelected() {
        var picker = document.getElementById('specPicker');
        var pathPickerGroup = document.getElementById('pathPickerGroup');

        if (!picker.value) {
            pathPickerGroup.style.display = 'none';
            loadedSpec = null;
            allPaths = [];
            return;
        }

        var opt = picker.selectedOptions[0];
        var category = opt.dataset.category;
        var name = opt.dataset.name;
        var specUrl = _specBaseUrl(category, name);

        try {
            var resp = await fetch(specUrl, { cache: 'no-store' });
            loadedSpec = await resp.json();
            allPaths = Object.keys(loadedSpec.paths).sort().map(function (p) {
                var methods = Object.keys(loadedSpec.paths[p])
                    .filter(function (m) { return ['get', 'put', 'patch', 'delete', 'post'].includes(m); })
                    .map(function (m) { return m.toUpperCase(); }).join(', ');
                return { path: p, methods: methods };
            });
            document.getElementById('pathSearch').value = '';
            filterPathPicker();
            pathPickerGroup.style.display = 'block';
            _writeHash();
        } catch (e) {
            console.error('Failed to load spec:', e);
            pathPickerGroup.style.display = 'none';
            allPaths = [];
        }
    }

    function onPathSelected() {
        var pathPicker = document.getElementById('pathPicker');
        if (pathPicker.value) {
            var fullPath = pathPicker.value;
            if (!fullPath.startsWith('/restconf')) {
                fullPath = '/restconf' + fullPath;
            }
            document.getElementById('path').value = fullPath;
            if (loadedSpec && loadedSpec.paths[pathPicker.value]) {
                var ops = loadedSpec.paths[pathPicker.value];
                var methods = Object.keys(ops).filter(function (m) { return ['get', 'put', 'patch', 'delete', 'post'].includes(m); });
                if (methods.length > 0) {
                    document.getElementById('method').value = methods[0].toUpperCase();
                    document.getElementById('method').dispatchEvent(new Event('change'));
                }
                var writeMethod = methods.find(function (m) { return ['put', 'patch', 'post'].includes(m); });
                if (writeMethod && ops[writeMethod]) {
                    var rb = ops[writeMethod].requestBody;
                    if (rb && rb.content) {
                        var jsonContent = rb.content['application/yang-data+json'] || rb.content['application/json'];
                        if (jsonContent) {
                            var example = jsonContent.example || (jsonContent.schema && jsonContent.schema.example);
                            if (example) {
                                document.getElementById('body').value = JSON.stringify(example, null, 2);
                            }
                        }
                    }
                }
            }
        }
        _writeHash();
    }

    // Restore picker state from #spec=<name>&category=<cat>&path=<p>&method=<m>.
    // Called from loadSpecPicker() once allSpecModules is populated.
    async function _restoreFromHash() {
        var h = _parseHash();
        if (!h.spec || !h.category) return;
        var picker = document.getElementById('specPicker');
        if (!picker) return;
        // Find the matching option (search-index may have re-filtered the list,
        // so re-run filter clear before picking).
        document.getElementById('specSearch').value = '';
        filterSpecPicker();
        var match = Array.prototype.find.call(picker.options, function (o) {
            return o.dataset && o.dataset.name === h.spec && o.dataset.category === h.category;
        });
        if (!match) return;
        picker.value = match.value;
        await onSpecSelected();
        if (h.path) {
            var pp = document.getElementById('pathPicker');
            var pmatch = Array.prototype.find.call(pp.options, function (o) { return o.value === h.path; });
            if (pmatch) {
                pp.value = h.path;
                onPathSelected();
            }
        }
        if (h.method) {
            var sel = document.getElementById('method');
            if (sel) {
                sel.value = h.method.toUpperCase();
                sel.dispatchEvent(new Event('change'));
            }
        }
    }

    // === Initialization ===

    function init() {
        initMethodToggle();
        _bindShareBtn();

        // Generate button
        var generateBtn = document.getElementById('generateBtn');
        if (generateBtn) generateBtn.addEventListener('click', generateCode);

        // Clear button
        var clearBtn = document.getElementById('clearBtn');
        if (clearBtn) clearBtn.addEventListener('click', clearForm);

        // Tab buttons (use data-tab attribute)
        document.querySelectorAll('.tab-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                switchTab(this.dataset.tab, this);
            });
        });

        // Copy buttons (use data-copy-target attribute)
        document.querySelectorAll('.copy-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                copyCode(this.dataset.copyTarget);
            });
        });

        // Spec picker
        document.getElementById('specSearch').addEventListener('input', filterSpecPicker);
        document.getElementById('specPicker').addEventListener('change', onSpecSelected);

        // Path picker
        document.getElementById('pathSearch').addEventListener('input', filterPathPicker);
        document.getElementById('pathPicker').addEventListener('change', onPathSelected);

        // Load spec picker
        loadSpecPicker();

        // === Page-specific keyboard shortcuts ===
        // Registered with the shared help dialog (site-chrome.js) and wired
        // to a single keydown listener that ignores typing targets.
        window.__SHORTCUTS = (window.__SHORTCUTS || []).concat([
            { keys: 'g', desc: 'Generate code for the current spec + path' },
            { keys: 'l', desc: 'Copy Share Link for current selection' },
            { keys: 'x', desc: 'Clear the form' }
        ]);
        document.addEventListener('keydown', function (e) {
            if (e.ctrlKey || e.metaKey || e.altKey) return;
            var t = e.target;
            var tag = t && t.tagName;
            if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (t && t.isContentEditable)) return;
            var k = (e.key || '').toLowerCase();
            if (k === 'g') {
                e.preventDefault();
                var b = document.getElementById('generateBtn'); if (b) b.click();
            } else if (k === 'l') {
                e.preventDefault();
                var b2 = document.getElementById('cgShareBtn'); if (b2) b2.click();
            } else if (k === 'x') {
                e.preventDefault();
                var b3 = document.getElementById('clearBtn'); if (b3) b3.click();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
