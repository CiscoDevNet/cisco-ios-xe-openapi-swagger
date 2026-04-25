/* index-app.js — Main page controller (extracted from inline script) */
(function () {
    'use strict';

    // === Dark Mode ===

    function toggleDarkMode() {
        var html = document.documentElement;
        var currentTheme = html.getAttribute('data-theme');
        var newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        var lightIcon = document.querySelector('.light-icon');
        var darkIcon = document.querySelector('.dark-icon');
        if (lightIcon && darkIcon) {
            if (newTheme === 'dark') {
                lightIcon.style.display = 'none';
                darkIcon.style.display = 'block';
            } else {
                lightIcon.style.display = 'block';
                darkIcon.style.display = 'none';
            }
        }

        // Redraw chart with new theme
        if (window.moduleChart) {
            drawChart();
        }
    }

    // Load saved theme immediately (before DOMContentLoaded)
    (function () {
        var savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark') {
            var lightIcon = document.querySelector('.light-icon');
            var darkIcon = document.querySelector('.dark-icon');
            if (lightIcon && darkIcon) {
                lightIcon.style.display = 'none';
                darkIcon.style.display = 'block';
            }
        }
    })();

    // === Statistics Chart ===

    var chartRetries = 0;

    function drawChart() {
        var ctx = document.getElementById('moduleChart');
        if (!ctx) {
            console.error('Canvas element not found');
            return;
        }

        if (typeof Chart === 'undefined') {
            chartRetries++;
            if (chartRetries > 30) {
                console.warn('Chart.js failed to load after 30 retries');
                var container = ctx.closest('.chart-section, .dashboard-chart, div');
                if (container) container.style.display = 'none';
                return;
            }
            setTimeout(drawChart, 100);
            return;
        }

        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        var textColor = isDark ? '#e0e0e0' : '#333';

        var data = {
            labels: ['Operational', 'Configuration', 'MIB', 'RPC', 'Native Config', 'OpenConfig', 'Events', 'IETF', 'Other'],
            datasets: [{
                data: [20159, 9452, 12482, 308, 13452, 5920, 861, 1122, 4597],
                backgroundColor: [
                    '#2196F3',
                    '#00BCD4',
                    '#9C27B0',
                    '#FFC107',
                    '#4CAF50',
                    '#009688',
                    '#FF9800',
                    '#FF5722',
                    '#757575'
                ],
                borderWidth: 3,
                borderColor: isDark ? '#1a1a1a' : '#fff'
            }]
        };

        var config = {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: isDark ? '#2d2d2d' : '#fff',
                        titleColor: textColor,
                        bodyColor: textColor,
                        borderColor: isDark ? '#444' : '#ddd',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function (context) {
                                var label = context.label || '';
                                var value = context.parsed || 0;
                                var total = context.dataset.data.reduce(function (a, b) { return a + b; }, 0);
                                var percentage = ((value / total) * 100).toFixed(1);
                                return label + ': ' + value.toLocaleString() + ' operations (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        };

        // Destroy existing chart if it exists and has destroy method
        if (window.moduleChart && typeof window.moduleChart.destroy === 'function') {
            window.moduleChart.destroy();
        }

        try {
            window.moduleChart = new Chart(ctx, config);
            console.log('Chart initialized successfully');
        } catch (error) {
            console.error('Error creating chart:', error);
        }
    }

    // === Code Snippet Generator Modal ===

    var currentCodeTab = 'curl';
    var generatedSnippets = {};

    function openCodeGenerator(e) {
        if (e) e.preventDefault();
        document.getElementById('codeGenModal').classList.add('active');
    }

    function closeCodeGenerator() {
        document.getElementById('codeGenModal').classList.remove('active');
    }

    function switchCodeTab(tab, btn) {
        currentCodeTab = tab;
        document.querySelectorAll('#codeGenModal .code-tab').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');

        if (generatedSnippets[tab]) {
            document.getElementById('generatedCode').textContent = generatedSnippets[tab];
        }
    }

    function generateCode(e) {
        e.preventDefault();

        var deviceIp = document.getElementById('deviceIp').value.trim();
        var username = document.getElementById('username').value.trim();
        var yangModule = document.getElementById('yangModule').value.trim();
        var operation = document.getElementById('operation').value;

        // Validate inputs to prevent injection
        var hostPattern = /^[a-zA-Z0-9][a-zA-Z0-9.\-]{0,253}[a-zA-Z0-9]$/;
        if (!hostPattern.test(deviceIp)) {
            if (typeof showToast !== 'undefined') showToast('Invalid hostname/IP format', 'error');
            return;
        }
        if (!username || /[\s'"`;$]/.test(username)) {
            if (typeof showToast !== 'undefined') showToast('Invalid username format', 'error');
            return;
        }

        var baseUrl = 'https://' + deviceIp + '/restconf/data/' + yangModule;

        // Generate cURL
        generatedSnippets.curl = '# ' + operation + ' request to ' + yangModule + '\ncurl -X ' + operation + ' \\\n  -H "Content-Type: application/yang-data+json" \\\n  -H "Accept: application/yang-data+json" \\\n  -u ' + username + ':YOUR_PASSWORD \\\n  --insecure \\\n  ' + baseUrl + (operation !== 'GET' ? ' \\\n  -d @payload.json' : '');

        // Generate Python
        generatedSnippets.python = '# ' + operation + ' request using Python requests library\nimport requests\nfrom requests.auth import HTTPBasicAuth\nimport json\nimport urllib3\nurllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)\n\n# Configuration\ndevice_ip = "' + deviceIp + '"\nusername = "' + username + '"\npassword = "YOUR_PASSWORD"\nyang_module = "' + yangModule + '"\n\n# RESTCONF endpoint\nurl = f"https://{device_ip}/restconf/data/{yang_module}"\n\n# Headers\nheaders = {\n    "Content-Type": "application/yang-data+json",\n    "Accept": "application/yang-data+json"\n}\n\n# Make request\nresponse = requests.' + operation.toLowerCase() + '(\n    url,\n    auth=HTTPBasicAuth(username, password),\n    headers=headers,' + (operation !== 'GET' ? '\n    json=payload,  # Define your payload here' : '') + '\n    verify=False\n)\n\nprint(f"Status: {response.status_code}")\nprint(f"Response: {response.json()}")';

        // Generate Ansible
        generatedSnippets.ansible = '# ' + operation + ' request using Ansible uri module\n---\n- name: ' + operation + ' ' + yangModule + '\n  hosts: localhost\n  gather_facts: no\n  vars:\n    device_ip: "' + deviceIp + '"\n    username: "' + username + '"\n    password: "YOUR_PASSWORD"\n    yang_module: "' + yangModule + '"\n  \n  tasks:\n    - name: ' + operation + ' RESTCONF request\n      uri:\n        url: "https://{{ device_ip }}/restconf/data/{{ yang_module }}"\n        method: ' + operation + '\n        user: "{{ username }}"\n        password: "{{ password }}"\n        force_basic_auth: yes\n        headers:\n          Content-Type: "application/yang-data+json"\n          Accept: "application/yang-data+json"' + (operation !== 'GET' ? '\n        body: "{{ payload | to_json }}"  # Define payload variable' : '') + '\n        validate_certs: no\n        status_code: [200, 201, 204]\n      register: response\n    \n    - name: Display response\n      debug:\n        var: response.json';

        // Generate JavaScript
        generatedSnippets.javascript = '// ' + operation + ' request using JavaScript fetch API\nconst deviceIp = \'' + deviceIp + '\';\nconst username = \'' + username + '\';\nconst password = \'YOUR_PASSWORD\';\nconst yangModule = \'' + yangModule + '\';\n\nconst url = `https://${deviceIp}/restconf/data/${yangModule}`;\n\nconst headers = {\n  \'Content-Type\': \'application/yang-data+json\',\n  \'Accept\': \'application/yang-data+json\',\n  \'Authorization\': \'Basic \' + btoa(username + \':\' + password)\n};\n\nconst options = {\n  method: \'' + operation + '\',\n  headers: headers,' + (operation !== 'GET' ? '\n  body: JSON.stringify(payload)  // Define your payload' : '') + '\n};\n\nfetch(url, options)\n  .then(response => {\n    if (!response.ok) throw new Error(`HTTP ${response.status}`);\n    return response.json();\n  })\n  .then(data => console.log(\'Success:\', data))\n  .catch(error => console.error(\'Error:\', error));';

        // Display the code
        document.getElementById('codeOutput').style.display = 'block';
        document.getElementById('generatedCode').textContent = generatedSnippets[currentCodeTab];
    }

    function copyCode() {
        var code = document.getElementById('generatedCode').textContent;
        navigator.clipboard.writeText(code).then(function () {
            var btn = document.querySelector('.copy-code-btn');
            var originalText = btn.textContent;
            btn.textContent = '\u2705 Copied!';
            btn.classList.add('copied');
            setTimeout(function () {
                btn.textContent = originalText;
                btn.classList.remove('copied');
            }, 2000);
        }).catch(function () {
            if (typeof showToast !== 'undefined') showToast('Failed to copy to clipboard', 'warning');
        });
    }

    // === Nav Bar Auto-Hide ===

    function initNavBarScroll() {
        var nav = document.getElementById('quickNav');
        var header = document.querySelector('.header');
        if (!nav || !header) return;
        var firstCheck = true;
        var observer = new IntersectionObserver(function (entries) {
            var e = entries[0];
            if (firstCheck) {
                firstCheck = false;
                if (!e.isIntersecting) {
                    nav.style.transition = 'none';
                    nav.style.maxHeight = '0';
                    nav.style.opacity = '0';
                    nav.style.padding = '0 20px';
                    nav.style.borderBottom = 'none';
                    requestAnimationFrame(function () { nav.style.transition = ''; });
                    return;
                }
            }
            if (e.isIntersecting) {
                nav.style.maxHeight = '200px';
                nav.style.opacity = '1';
                nav.style.padding = '10px 20px 8px';
                nav.style.borderBottom = '1px solid var(--border-color)';
            } else {
                nav.style.maxHeight = '0';
                nav.style.opacity = '0';
                nav.style.padding = '0 20px';
                nav.style.borderBottom = 'none';
            }
        }, { threshold: 0 });
        observer.observe(header);
    }

    // === Initialization ===

    function init() {
        // Chart
        drawChart();

        // Dark mode toggle
        var darkModeBtn = document.getElementById('darkModeToggle');
        if (darkModeBtn) darkModeBtn.addEventListener('click', toggleDarkMode);

        // Skip link focus/blur
        var skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('focus', function () { this.style.top = '0'; });
            skipLink.addEventListener('blur', function () { this.style.top = '-40px'; });
        }

        // Quick nav search focus link
        var navSearchLink = document.getElementById('navSearchLink');
        if (navSearchLink) {
            navSearchLink.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector('.search-box').focus();
            });
        }

        // Browse All / Advanced Filters / Reset (functions from search.js)
        var browseAllBtn = document.getElementById('browseAllBtn');
        if (browseAllBtn) browseAllBtn.addEventListener('click', function () { if (typeof browseAll === 'function') browseAll(); });

        var advFiltersBtn = document.getElementById('advancedFiltersBtn');
        if (advFiltersBtn) advFiltersBtn.addEventListener('click', function () { if (typeof toggleAdvancedFilters === 'function') toggleAdvancedFilters(); });

        var resetBtn = document.getElementById('resetFiltersBtn');
        if (resetBtn) resetBtn.addEventListener('click', function () { if (typeof resetFilters === 'function') resetFilters(); });

        // Advanced filter buttons (delegate via data attributes)
        document.querySelectorAll('[data-advanced-filter]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                if (typeof applyAdvancedFilter === 'function') {
                    applyAdvancedFilter(this.dataset.advancedFilter, this.dataset.value);
                }
            });
        });

        // Quick Snippet link
        var quickSnippetLink = document.getElementById('quickSnippetLink');
        if (quickSnippetLink) quickSnippetLink.addEventListener('click', openCodeGenerator);

        // Code generator modal — close button
        var modalClose = document.querySelector('#codeGenModal .modal-close');
        if (modalClose) modalClose.addEventListener('click', closeCodeGenerator);

        // Code generator form submit
        var codeGenForm = document.querySelector('#codeGenModal .code-gen-form');
        if (codeGenForm) codeGenForm.addEventListener('submit', generateCode);

        // Code tabs (use data-tab attribute)
        document.querySelectorAll('#codeGenModal .code-tab').forEach(function (tab) {
            tab.addEventListener('click', function () {
                switchCodeTab(this.dataset.tab, this);
            });
        });

        // Copy code button
        var copyBtn = document.querySelector('#codeGenModal .copy-code-btn');
        if (copyBtn) copyBtn.addEventListener('click', copyCode);

        // Escape to close modal
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeCodeGenerator();
        });

        // Click outside modal to close
        var modal = document.getElementById('codeGenModal');
        if (modal) {
            modal.addEventListener('click', function (e) {
                if (e.target.id === 'codeGenModal') closeCodeGenerator();
            });
        }

        // Nav bar auto-hide
        initNavBarScroll();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
