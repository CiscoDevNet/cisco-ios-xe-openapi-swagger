// Universal Search for Cisco IOS XE YANG Documentation Hub
// Provides fuzzy search across all YANG modules with browse-all capability

// Tunable constants. Centralised so behaviour can be adjusted in one place
// instead of hunting through magic numbers scattered across this file.
const SEARCH_CONFIG = Object.freeze({
    debounceMs: 200,            // Input → performSearch debounce window
    minQueryChars: 2,           // Below this we show a hint instead of searching
    autocompleteLimit: 8,       // Max suggestions shown in the dropdown
    displayLimit: 60,           // Max search-result cards rendered per query
    relatedLimit: 5,            // Max "related modules" shown per card
    descTruncate: 160,          // Max chars for description preview (word-boundary)
    fuseThreshold: 0.35,        // Fuse.js fuzziness (0=exact, 1=match anything)
    toastShowMs: 10,            // Delay before adding .show class to toast
    toastDismissMs: 5000,       // How long a toast stays visible
    toastRemoveMs: 300          // Fade-out window before DOM removal
});
// Back-compat alias for any external callers / future modules.
if (typeof window !== 'undefined') window.SEARCH_CONFIG = SEARCH_CONFIG;

// HTML Sanitization utility to prevent XSS
function escapeHtml(str) {
    if (str == null) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

let searchIndex = [];
let fuse = null;
let searchReady = false;
let searchReadyPromise = null;
let activeFilters = new Set(['all']);
let advancedFilters = {
    prefix: 'all',
    hasTree: 'all',
    hasSpec: 'all'
};
let autocompleteIndex = [];
let selectedSuggestionIndex = -1;
let browseMode = false;
let currentSort = 'relevance';
let lastResults = [];
// Lowercased copy of the current query — referenced by renderResults() to
// decide whether to upgrade a result's link from "open the spec at the top"
// to "deep-link to the matching top-level YANG container" (see topPaths in
// search-index.json).
let activeQueryLower = '';

// Multi-release: try the active-release search index first, then fall back to
// the root index for backward compatibility with the legacy single-release
// layout. window.__IOSXE_ACTIVE_VERSION__ is set by index-app.js once the
// version selector resolves.
//
// `cache: 'no-store'` bypasses the browser cache entirely. We previously
// used 'no-cache' which only forces revalidation — on a revalidation
// network hiccup the browser can still serve the stale copy, which is
// exactly the bug we were trying to avoid (GitHub Pages default
// max-age=600 pinning a pre-rewrite index for up to 10 minutes after
// deploy). Every other index/manifest fetch in the site uses 'no-store'
// (yang-accountability.js, index-app.js, telemetry.js) — match them.
async function loadSearchIndexForActiveVersion() {
    var opts = { cache: 'no-store' };
    var ver = (typeof window !== 'undefined') ? window.__IOSXE_ACTIVE_VERSION__ : null;
    if (ver) {
        try {
            var resp = await fetch('releases/' + encodeURIComponent(ver) + '/search-index.json', opts);
            if (resp.ok) return resp;
        } catch (_) { /* fall through to root */ }
    }
    return fetch('search-index.json', opts);
}

// Load search index
async function loadSearchIndex() {
    if (searchReadyPromise) return searchReadyPromise;
    
    searchReadyPromise = (async () => {
        try {
            const searchInput = document.getElementById('universalSearch');
            if (searchInput) {
                searchInput.placeholder = 'Loading search index...';
                searchInput.disabled = true;
            }
            
            const response = await loadSearchIndexForActiveVersion();
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            searchIndex = data.modules;

            // Hydrate per-module records from the top-level categories map
            // (search-index.json v3.1+). Older indexes already carry these
            // fields per-module, so we only fill in the gaps. This keeps
            // consumers like recent-favorites.js and code-generator.js
            // unaware of the wire format change.
            const categories = (data && data.categories) || {};
            for (const m of searchIndex) {
                const cat = m.category && categories[m.category];
                if (cat) {
                    if (!m.displayCategory) m.displayCategory = cat.displayCategory;
                    if (!m.emoji) m.emoji = cat.emoji;
                }
                if (!m.swaggerUrl && m.category && m.name) {
                    m.swaggerUrl = m.category + '/index.html#spec=' + m.name;
                }
            }

            // Build autocomplete index
            buildAutocompleteIndex();
            
            // Initialize Fuse.js with weighted keys
            fuse = new Fuse(searchIndex, {
                keys: [
                    { name: 'name', weight: 0.4 },
                    { name: 'keywords', weight: 0.3 },
                    { name: 'description', weight: 0.2 },
                    { name: 'displayCategory', weight: 0.1 }
                ],
                threshold: SEARCH_CONFIG.fuseThreshold,
                includeScore: true,
                includeMatches: true,
                minMatchCharLength: 2,
                ignoreLocation: true
            });
            
            searchReady = true;
            
            // Update filter buttons with counts
            updateFilterCounts();
            
            // Update search input
            if (searchInput) {
                searchInput.placeholder = `Search ${searchIndex.length} modules — type a name, keyword, or feature... (press / or Ctrl+K)`;
                searchInput.disabled = false;
            }
            
            // Search index loaded successfully
        } catch (error) {
            console.error('Error loading search index:', error);
            const searchInput = document.getElementById('universalSearch');
            if (searchInput) {
                searchInput.placeholder = 'Search unavailable — click here to retry';
                searchInput.disabled = false;
                // Wire a one-shot click handler so users can retry without
                // a full page reload (also helps on flaky cell networks).
                searchInput.addEventListener('click', function retry() {
                    searchInput.removeEventListener('click', retry);
                    searchReadyPromise = null;
                    loadSearchIndex();
                }, { once: true });
            }
            if (typeof showToast === 'function') {
                showToast('Search index failed to load (' + (error && error.message || 'network error') + '). Click the search box to retry.', 'error');
            }
        }
    })();
    
    return searchReadyPromise;
}

// Update filter buttons with module counts
function updateFilterCounts() {
    const typeCounts = {};
    searchIndex.forEach(m => {
        typeCounts[m.type] = (typeCounts[m.type] || 0) + 1;
    });
    
    document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
        const filterType = btn.dataset.filter;
        if (filterType === 'all') {
            const currentText = btn.textContent.replace(/\s*\(\d+\)$/, '');
            btn.textContent = `${currentText} (${searchIndex.length})`;
        } else if (typeCounts[filterType] !== undefined) {
            const currentText = btn.textContent.replace(/\s*\(\d+\)$/, '');
            btn.textContent = `${currentText} (${typeCounts[filterType]})`;
        }
    });
}

// Build autocomplete suggestions index (module names only for clarity)
function buildAutocompleteIndex() {
    autocompleteIndex = searchIndex.map(module => ({
        name: module.name,
        category: module.displayCategory,
        emoji: module.emoji,
        type: module.type
    })).sort((a, b) => a.name.localeCompare(b.name));
    
    // Autocomplete index built
}

// Get badge class for module type
function getBadgeClass(type) {
    const badgeMap = {
        'operational': 'badge-operational',
        'config': 'badge-config',
        'configuration': 'badge-configuration',
        'rpc': 'badge-rpc',
        'events': 'badge-events',
        'mib': 'badge-mib',
        'ietf': 'badge-ietf',
        'openconfig': 'badge-openconfig',
        'native': 'badge-native',
        'other': 'badge-other',
        'yang-tree': 'badge-yang-tree',
        'mib-tree': 'badge-mib-tree'
    };
    return badgeMap[type] || 'badge-other';
}

// Get border color for module type
function getBorderColor(type) {
    const colorMap = {
        'operational': '#2196F3',
        'config': '#00BCD4',
        'native': '#4CAF50',
        'rpc': '#FFC107',
        'events': '#FF9800',
        'mib': '#9C27B0',
        'ietf': '#FF5722',
        'openconfig': '#009688',
        'other': '#757575'
    };
    return colorMap[type] || '#1565C0';
}

// Truncate description for display
function truncateDescription(desc, maxLen) {
    if (!desc) return '';
    // Strip markdown bold markers and normalize whitespace
    let clean = desc.replace(/\*\*[^*]+\*\*/g, '').replace(/\\n/g, ' ').replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();
    if (clean.length > maxLen) {
        return clean.substring(0, maxLen).replace(/\s+\S*$/, '') + '…';
    }
    return clean;
}

// Extract core technology keyword from a module name
function extractCoreKeyword(name) {
    const lower = name.toLowerCase();
    // Cisco-IOS-XE-xxx-oper / -events / -rpc / -cfg
    let m = lower.match(/^cisco-ios-xe-(.+?)-(oper|events|rpc|cfg|common|types|actions-rpc)$/);
    if (m) return m[1];
    // Cisco-IOS-XE-xxx (no suffix)
    m = lower.match(/^cisco-ios-xe-(.+)$/);
    if (m && m[1].length > 2) return m[1];
    // openconfig-xxx
    m = lower.match(/^openconfig-(.+?)(-types)?$/);
    if (m) return m[1];
    // ietf-xxx
    m = lower.match(/^ietf-(.+)$/);
    if (m) return m[1];
    // CISCO-XXX-MIB or XXX-MIB or XXX-TRAP-MIB
    m = lower.match(/^(?:cisco-)?(.+?)(?:-trap)?-mib$/);
    if (m && m[1].length > 2) return m[1];
    return null;
}

// Keyword-to-modules lookup map (built once at load time)
let relatedModulesMap = null;

function buildRelatedModulesMap() {
    relatedModulesMap = {};
    for (const m of searchIndex) {
        const kw = extractCoreKeyword(m.name);
        if (kw) {
            if (!relatedModulesMap[kw]) relatedModulesMap[kw] = [];
            relatedModulesMap[kw].push(m);
        }
    }
}

// Find related modules in other categories (O(1) lookup)
function getRelatedModules(module) {
    if (!relatedModulesMap) buildRelatedModulesMap();
    const keyword = extractCoreKeyword(module.name);
    if (!keyword || !relatedModulesMap[keyword]) return [];
    const related = [];
    const myCategory = module.category;
    const seen = new Set();
    for (const m of relatedModulesMap[keyword]) {
        if (m.name === module.name || m.category === myCategory) continue;
        if (!seen.has(m.category)) {
            seen.add(m.category);
            related.push(m);
        }
    }
    return related.slice(0, SEARCH_CONFIG.relatedLimit);
}

// Returns the URL we should send the user to when they click "View API Spec"
// on a search result. If the active query exactly matches one of the
// module's top-level YANG containers (e.g. user typed "iox" and the module
// has /native/iox → operationId "get-iox"), append &op=<id> to the spec
// hash so Swagger UI lands directly on that operation row instead of just
// opening the spec at the top.
function pickDeepLink(module) {
    if (!module || !module.swaggerUrl) return module && module.swaggerUrl;
    const q = activeQueryLower;
    if (!q || !module.topPaths) return module.swaggerUrl;
    const opId = module.topPaths[q];
    if (!opId) return module.swaggerUrl;
    if (module.swaggerUrl.indexOf('&op=') !== -1) return module.swaggerUrl;
    return module.swaggerUrl + '&op=' + encodeURIComponent(opId);
}

// Render search results
function renderResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    
    if (!results || results.length === 0) {
        const noResultMsg = browseMode 
            ? 'No modules match the selected filters.'
            : 'No modules found. Try different keywords or broaden your filters.';
        resultsContainer.innerHTML = `<div class="no-results">${noResultMsg}</div>`;
        resultsContainer.classList.add('active');
        return;
    }

    // Apply sorting — save original order, sort a copy
    lastResults = results;
    results = [...results];
    if (currentSort === 'name') {
        results.sort((a, b) => ((a.item || a).name || '').localeCompare((b.item || b).name || ''));
    } else if (currentSort === 'paths') {
        results.sort((a, b) => ((b.item || b).pathCount || 0) - ((a.item || a).pathCount || 0));
    } else if (currentSort === 'type') {
        results.sort((a, b) => ((a.item || a).type || '').localeCompare((b.item || b).type || '') || ((a.item || a).name || '').localeCompare((b.item || b).name || ''));
    }
    // 'relevance' = default Fuse.js order, no re-sort needed
    
    const totalResults = results.length;
    const displayLimit = SEARCH_CONFIG.displayLimit;
    const modeLabel = browseMode ? 'Browsing' : 'Found';
    const sortBtnStyle = (s) => `cursor:pointer; padding:3px 8px; border:1px solid ${currentSort===s ? '#1565C0' : 'var(--border-color,#ddd)'}; border-radius:4px; background:${currentSort===s ? '#1565C0' : 'var(--bg-card,#fff)'}; color:${currentSort===s ? '#fff' : 'var(--text-secondary,#666)'}; font-size:0.78rem;`;
    const sortBtn = (key, label) => `<button style="${sortBtnStyle(key)}" aria-pressed="${currentSort===key}" onclick="changeSort('${key}')">${label}</button>`;
    const sortHtml = `<span style="display:inline-flex;gap:4px;margin-left:12px;align-items:center;" role="group" aria-label="Sort results"><span style="font-size:0.78rem;color:var(--text-secondary,#666);">Sort:</span>${sortBtn('relevance','Relevance')}${sortBtn('name','Name')}${sortBtn('paths','Paths \u2193')}${sortBtn('type','Type')}</span>`;
    const statsHtml = `<div class="search-stats" style="display:flex;align-items:center;flex-wrap:wrap;">${modeLabel} ${totalResults} module${totalResults !== 1 ? 's' : ''}${totalResults >displayLimit ? ` — showing first ${displayLimit}` : ''}${sortHtml}</div>`;
    
    const cardsHtml = results.slice(0, displayLimit).map(result => {
        const module = result.item || result;
        const badgeClass = getBadgeClass(module.type);
        const borderColor = getBorderColor(module.type);
        const isFav = typeof isFavorite !== 'undefined' ? isFavorite(module.name) : false;
        const description = truncateDescription(module.description, SEARCH_CONFIG.descTruncate);
        const escapedName = escapeHtml(module.name);
        const escapedDesc = escapeHtml(description);
        const pathLabel = module.type === 'rpc' ? 'operations' : 'paths';

        // If the current query exactly matches a top-level YANG container in
        // this module (e.g. user searched "iox" and native-platform has a
        // /native/iox container), build a deep link straight to that
        // operation row instead of just dropping the user at the spec top.
        // module.topPaths is { <container-lowercased>: <operationId> }.
        const specUrl = pickDeepLink(module);
        const opHint = (typeof activeQueryLower === 'string' && activeQueryLower &&
            module.topPaths && Object.prototype.hasOwnProperty.call(module.topPaths, activeQueryLower))
            ? activeQueryLower
            : null;

        let linksHtml = '';
        if (specUrl) {
            const label = opHint ? `View ${escapeHtml(opHint)} API` : 'View API Spec';
            linksHtml += `<a href="${escapeHtml(specUrl)}" class="search-result-link" data-module="${escapedName}">${label}</a>`;
        }
        if (module.yangTreeUrl) {
            linksHtml += `<a href="${escapeHtml(module.yangTreeUrl)}" class="search-result-link" data-module="${escapedName}">View YANG Tree</a>`;
        }
        
        // Related modules in other categories
        const related = getRelatedModules(module);
        let relatedHtml = '';
        if (related.length > 0) {
            const relLinks = related.map(r => {
                const rUrl = pickDeepLink(r);
                const url = rUrl ? escapeHtml(rUrl) : '#';
                const badge = escapeHtml(r.displayCategory);
                const rName = escapeHtml(r.name);
                return `<a href="${url}" title="${rName}" class="related-link" data-related-search="${rName}">${escapeHtml(r.emoji)} ${badge}</a>`;
            }).join(' ');
            relatedHtml = `<div style="margin-top:6px;display:flex;align-items:center;gap:6px;flex-wrap:wrap;"><span style="font-size:0.75rem;color:var(--text-secondary,#888);">Also in:</span>${relLinks}</div>`;
        }
        
        return `
            <div class="search-result-card" style="border-left-color: ${borderColor}; ${specUrl ? 'cursor:pointer;' : ''}" ${specUrl ? `data-href="${escapeHtml(specUrl)}" tabindex="0" role="link" aria-label="Open ${escapedName}${opHint ? ' — ' + escapeHtml(opHint) : ''}"` : ''}>
                <div class="search-result-header">
                    <span class="search-result-badge ${badgeClass}">${escapeHtml(module.emoji)} ${escapeHtml(module.displayCategory)}</span>
                    <span class="search-result-title">${escapedName}</span>
                    ${module.pathCount ? `<span class="search-result-paths">${module.pathCount} ${pathLabel}</span>` : ''}
                    <button class="favorite-btn ${isFav ? 'active' : ''}" 
                            data-module="${escapedName}"
                            title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
                        ${isFav ? '★' : '☆'}
                    </button>
                </div>
                ${escapedDesc ? `<div class="search-result-desc">${escapedDesc}</div>` : ''}
                <div class="search-result-links">${linksHtml}</div>${relatedHtml}
            </div>
        `;
    }).join('');
    
    resultsContainer.innerHTML = statsHtml + cardsHtml;
    resultsContainer.classList.add('active');

    // Make the whole card act as a link: clicking anywhere on the card
    // (outside of inner buttons / links / the favorite star) navigates to
    // its data-href. Inner <a>/<button> elements keep their own behavior.
    if (!resultsContainer._cardClickWired) {
        resultsContainer._cardClickWired = true;
        resultsContainer.addEventListener('click', function (e) {
            var card = e.target.closest && e.target.closest('.search-result-card');
            if (!card) return;
            var href = card.getAttribute('data-href');
            if (!href) return;
            // Don't hijack clicks on inner interactive elements.
            if (e.target.closest('a, button, input, select, textarea, [role="button"]')) return;
            window.location.href = href;
        });
        resultsContainer.addEventListener('keydown', function (e) {
            if (e.key !== 'Enter' && e.key !== ' ') return;
            var card = e.target.closest && e.target.closest('.search-result-card[data-href]');
            if (!card || card !== e.target) return;
            e.preventDefault();
            window.location.href = card.getAttribute('data-href');
        });
    }
    
    if (totalResults > displayLimit) {
        resultsContainer.innerHTML += `<div class="search-stats" style="text-align: center; margin-top: 16px;">Refine your search or filters to see more specific results.</div>`;
    }
}

// Filter results by type
function filterResults(results) {
    if (activeFilters.has('all') && advancedFilters.prefix === 'all' && 
        advancedFilters.hasTree === 'all' && advancedFilters.hasSpec === 'all') {
        return results;
    }
    
    return results.filter(result => {
        const module = result.item || result;
        
        // Type filter
        if (!activeFilters.has('all') && !activeFilters.has(module.type)) {
            return false;
        }
        
        // Prefix filter
        if (advancedFilters.prefix !== 'all') {
            const name = module.name.toLowerCase();
            if (advancedFilters.prefix === 'cisco' && !name.startsWith('cisco-ios-xe-')) {
                return false;
            }
            if (advancedFilters.prefix === 'ietf' && !name.startsWith('ietf-')) {
                return false;
            }
            if (advancedFilters.prefix === 'openconfig' && !name.startsWith('openconfig-')) {
                return false;
            }
            if (advancedFilters.prefix === 'mib' && module.category !== 'swagger-mib-model') {
                return false;
            }
        }
        
        // Has Tree filter
        if (advancedFilters.hasTree === 'yes' && !module.yangTreeUrl) {
            return false;
        }
        if (advancedFilters.hasTree === 'no' && module.yangTreeUrl) {
            return false;
        }
        
        // Has Spec filter
        if (advancedFilters.hasSpec === 'yes' && !module.swaggerUrl) {
            return false;
        }
        if (advancedFilters.hasSpec === 'no' && module.swaggerUrl) {
            return false;
        }
        
        return true;
    });
}

// Show autocomplete suggestions
function showAutocomplete(query) {
    if (!query || query.length < SEARCH_CONFIG.minQueryChars) {
        hideAutocomplete();
        return;
    }
    
    const lowerQuery = query.toLowerCase();
    const suggestions = autocompleteIndex
        .filter(entry => entry.name.toLowerCase().includes(lowerQuery))
        .slice(0, SEARCH_CONFIG.autocompleteLimit);
    
    if (suggestions.length === 0) {
        hideAutocomplete();
        return;
    }
    
    const autocompleteDiv = document.getElementById('autocomplete');
    autocompleteDiv.innerHTML = suggestions.map((entry, index) => {
        const highlightedTerm = escapeHtml(entry.name).replace(
            new RegExp(escapeHtml(query).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'),
            match => `<strong>${match}</strong>`
        );
        return `<div class="autocomplete-item ${index === selectedSuggestionIndex ? 'selected' : ''}" 
                     data-term="${escapeHtml(entry.name)}">
                    <span>${highlightedTerm}</span>
                    <span class="autocomplete-category">${entry.emoji} ${escapeHtml(entry.category)}</span>
                 </div>`;
    }).join('');
    
    // Use event delegation for clicks
    autocompleteDiv.onclick = function(e) {
        const item = e.target.closest('.autocomplete-item');
        if (item) {
            selectSuggestion(item.dataset.term);
        }
    };
    
    autocompleteDiv.classList.add('active');
}

// Hide autocomplete
function hideAutocomplete() {
    const autocompleteDiv = document.getElementById('autocomplete');
    if (autocompleteDiv) {
        autocompleteDiv.classList.remove('active');
        autocompleteDiv.innerHTML = '';
    }
    selectedSuggestionIndex = -1;
}

// Select suggestion
function selectSuggestion(term) {
    document.getElementById('universalSearch').value = term;
    hideAutocomplete();
    performSearch();
}

// Handle keyboard navigation in autocomplete
function handleAutocompleteKeyboard(e) {
    const autocompleteDiv = document.getElementById('autocomplete');
    if (!autocompleteDiv || !autocompleteDiv.classList.contains('active')) {
        return;
    }
    
    const items = autocompleteDiv.querySelectorAll('.autocomplete-item');
    
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, items.length - 1);
        updateAutocompleteSelection(items);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
        updateAutocompleteSelection(items);
    } else if (e.key === 'Enter' && selectedSuggestionIndex >= 0) {
        e.preventDefault();
        items[selectedSuggestionIndex].click();
    } else if (e.key === 'Escape') {
        hideAutocomplete();
    }
}

// Update autocomplete selection
function updateAutocompleteSelection(items) {
    items.forEach((item, index) => {
        if (index === selectedSuggestionIndex) {
            item.classList.add('selected');
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.classList.remove('selected');
        }
    });
}

// Toggle advanced filters
function toggleAdvancedFilters() {
    const panel = document.getElementById('advancedFilters');
    panel.classList.toggle('active');
}

// Apply advanced filter
function applyAdvancedFilter(filterType, value) {
    advancedFilters[filterType] = value;
    
    // Update button states
    document.querySelectorAll(`[data-advanced-filter="${filterType}"]`).forEach(btn => {
        if (btn.dataset.value === value) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    performSearch();
}

// Reset all filters
function resetFilters() {
    // Reset type filters
    activeFilters.clear();
    activeFilters.add('all');
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
    });
    document.querySelector('[data-filter="all"]').classList.add('active');
    document.querySelector('[data-filter="all"]').setAttribute('aria-pressed', 'true');
    
    // Reset advanced filters
    advancedFilters = {
        prefix: 'all',
        hasTree: 'all',
        hasSpec: 'all'
    };
    document.querySelectorAll('[data-advanced-filter]').forEach(btn => {
        if (btn.dataset.value === 'all') {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Clear search and hide results
    document.getElementById('universalSearch').value = '';
    document.getElementById('searchResults').classList.remove('active');
    browseMode = false;
}

// Browse all modules (filtered, no search text required)
function browseAll() {
    if (!searchReady) return;
    
    browseMode = true;
    
    // Wrap all modules as results for filtering
    let results = searchIndex.map(m => ({ item: m }));
    
    // Apply filters
    results = filterResults(results);
    
    // Sort by category then name
    results.sort((a, b) => {
        const catA = (a.item || a).displayCategory || '';
        const catB = (b.item || b).displayCategory || '';
        if (catA !== catB) return catA.localeCompare(catB);
        return ((a.item || a).name || '').localeCompare((b.item || b).name || '');
    });
    
    renderResults(results);
}

// Change sort order and re-render
function changeSort(sort) {
    currentSort = sort;
    if (lastResults.length > 0) {
        renderResults(lastResults);
    }
}

// Perform search
function performSearch() {
    const query = document.getElementById('universalSearch').value.trim();
    activeQueryLower = query.toLowerCase();

    if (!searchReady) return;
    
    // If no search text, check if we should browse by filter
    if (query.length === 0) {
        updateUrlHash('');
        if (!activeFilters.has('all') || advancedFilters.prefix !== 'all' || 
            advancedFilters.hasTree !== 'all' || advancedFilters.hasSpec !== 'all') {
            browseAll();
            return;
        }
        browseMode = false;
        document.getElementById('searchResults').classList.remove('active');
        return;
    }
    
    browseMode = false;
    
    if (query.length < SEARCH_CONFIG.minQueryChars) {
        document.getElementById('searchResults').innerHTML = '<div class="search-stats">Type at least ' + SEARCH_CONFIG.minQueryChars + ' characters to search...</div>';
        document.getElementById('searchResults').classList.add('active');
        return;
    }
    
    // Perform fuzzy search
    let results = fuse.search(query);
    
    // Apply filters
    results = filterResults(results);
    
    // Update URL hash for deep-linking
    updateUrlHash(query);
    
    // Analytics: a zero-result search is a direct signal of a module/spec a
    // user wanted but we don't surface — track the query so the gaps are
    // visible in the dashboard. (Only fired for real searches, not browse.)
    try {
        if ((!results || results.length === 0) && typeof window.__iosxeTrack === 'function') {
            window.__iosxeTrack('search_no_results', { search_query: query });
        }
    } catch (e) { /* noop */ }
    
    // Render results
    renderResults(results);
}

// Handle filter button clicks
function setupFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const filterValue = btn.dataset.filter;
            
            if (filterValue === 'all') {
                // Clear all filters and activate "All"
                activeFilters.clear();
                activeFilters.add('all');
                filterButtons.forEach(b => { b.classList.remove('active'); b.setAttribute('aria-pressed', 'false'); });
                btn.classList.add('active');
                btn.setAttribute('aria-pressed', 'true');
            } else {
                // Remove "All" filter if active
                if (activeFilters.has('all')) {
                    activeFilters.clear();
                    const allBtn = document.querySelector('[data-filter="all"]');
                    allBtn.classList.remove('active');
                    allBtn.setAttribute('aria-pressed', 'false');
                }
                
                // Toggle this filter
                if (activeFilters.has(filterValue)) {
                    activeFilters.delete(filterValue);
                    btn.classList.remove('active');
                    btn.setAttribute('aria-pressed', 'false');
                } else {
                    activeFilters.add(filterValue);
                    btn.classList.add('active');
                    btn.setAttribute('aria-pressed', 'true');
                }
                
                // If no filters active, activate "All"
                if (activeFilters.size === 0) {
                    activeFilters.add('all');
                    const allBtn = document.querySelector('[data-filter="all"]');
                    allBtn.classList.add('active');
                    allBtn.setAttribute('aria-pressed', 'true');
                }
            }
            
            // Re-run search with new filters
            performSearch();
        });
    });
}

// ── Deep-linking: preserve search state in URL hash ─────────────────────────

function updateUrlHash(query) {
    if (query && query.length >= 2) {
        history.replaceState(null, '', '#search=' + encodeURIComponent(query));
    } else if (window.location.hash) {
        history.replaceState(null, '', window.location.pathname);
    }
}

function handleDeepLink() {
    var hash = decodeURIComponent(window.location.hash);

    // ?q=query — bridge Google's SearchAction sitelinks search box to our
    // hash-based deep-link format. Normalises the URL to use #search=
    // so subsequent navigation matches the rest of the codebase.
    try {
        var sp = new URLSearchParams(window.location.search);
        var qParam = sp.get('q');
        if (qParam && qParam.length >= 2 && !hash) {
            history.replaceState(null, '', window.location.pathname + '#search=' + encodeURIComponent(qParam));
            hash = '#search=' + qParam;
        }
    } catch (_) { /* URLSearchParams unsupported \u2192 skip */ }

    // #search=query — restore a search
    if (hash.startsWith('#search=')) {
        var query = hash.replace('#search=', '');
        if (query && query.length >= 2) {
            var searchInput = document.getElementById('universalSearch');
            if (searchInput) {
                searchInput.value = query;
                // Wait for search index to load, then auto-search
                var checkReady = setInterval(function () {
                    if (searchReady) {
                        clearInterval(checkReady);
                        performSearch();
                        searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, 100);
                // Safety timeout — stop waiting after 10s
                setTimeout(function () { clearInterval(checkReady); }, 10000);
            }
        }
        return;
    }

    // #module=name — redirect to the module's Swagger UI page
    if (hash.startsWith('#module=')) {
        var moduleName = hash.replace('#module=', '');
        if (moduleName) {
            var checkReady2 = setInterval(function () {
                if (searchReady && searchIndex) {
                    clearInterval(checkReady2);
                    var found = searchIndex.find(function (m) {
                        return m.name === moduleName;
                    });
                    if (found && found.swaggerUrl) {
                        window.location.href = found.swaggerUrl;
                    }
                }
            }, 100);
            setTimeout(function () { clearInterval(checkReady2); }, 10000);
        }
        return;
    }

    // #spec=model/name — redirect to module page (cross-page deep link)
    if (hash.startsWith('#spec=')) {
        var specParts = hash.replace('#spec=', '').split('/');
        if (specParts.length === 2) {
            var modelDir = specParts[0];
            var specName = specParts[1];
            // SECURITY: only redirect when modelDir matches a known viewer
            // category directory. Without this guard an attacker can craft
            // a URL like `#spec=javascript:alert(1)/x` and have it executed
            // because `window.location.href = "javascript:..."` runs the
            // payload. Whitelist short-circuits that path.
            var ALLOWED_MODEL_DIRS = [
                'swagger-cfg-model', 'swagger-ietf-model',
                'swagger-mib-model', 'swagger-native-config-model', 'swagger-oper-model',
                'swagger-openconfig-model', 'swagger-other-model', 'swagger-rpc-model'
            ];
            if (ALLOWED_MODEL_DIRS.indexOf(modelDir) === -1) return;
            window.location.href = modelDir + '/index.html#spec=' + encodeURIComponent(specName);
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSearchIndex();
    setupFilters();
    handleDeepLink();
    
    // Setup search input with debounce and autocomplete
    let searchTimeout;
    const searchInput = document.getElementById('universalSearch');
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        // Show autocomplete
        showAutocomplete(query);
        
        // Debounced search (SEARCH_CONFIG.debounceMs)
        searchTimeout = setTimeout(performSearch, SEARCH_CONFIG.debounceMs);
    });
    
    // Keyboard shortcuts
    searchInput.addEventListener('keydown', handleAutocompleteKeyboard);
    
    // Global keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
            searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // "/" focuses search too (GitHub convention). Skip when already
        // typing into a form field so we don't hijack the user's input.
        if (e.key === '/' && document.activeElement !== searchInput) {
            const t = e.target;
            if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA'
                    || t.tagName === 'SELECT' || t.isContentEditable)) return;
            e.preventDefault();
            searchInput.focus();
            try { searchInput.select(); } catch (_) {}
            searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // Escape to clear search and hide results
        if (e.key === 'Escape' && document.activeElement === searchInput) {
            searchInput.value = '';
            document.getElementById('searchResults').classList.remove('active');
            hideAutocomplete();
        }
    });
    
    // Click outside to close autocomplete
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            hideAutocomplete();
        }
    });
    
    // Event delegation for search result links and favorites
    document.getElementById('searchResults').addEventListener('click', (e) => {
        const link = e.target.closest('.search-result-link');
        if (link) {
            const moduleName = link.dataset.module;
            if (moduleName && typeof trackModuleClick !== 'undefined') {
                trackModuleClick(moduleName);
            }
        }
        
        // Handle favorite button clicks with event delegation
        const favBtn = e.target.closest('.favorite-btn');
        if (favBtn) {
            const moduleName = favBtn.dataset.module;
            if (moduleName && typeof toggleFavoriteUI !== 'undefined') {
                toggleFavoriteUI(moduleName, favBtn);
            }
        }
        
        // Handle related module link clicks with event delegation
        const relatedLink = e.target.closest('.related-link[data-related-search]');
        if (relatedLink) {
            e.preventDefault();
            const searchTerm = relatedLink.dataset.relatedSearch;
            if (searchTerm) {
                document.getElementById('universalSearch').value = searchTerm;
                performSearch();
            }
        }
    });
    
    // Search initialized
    
    // Handle browser back/forward for deep-linked searches
    window.addEventListener('hashchange', function () {
        var hash = decodeURIComponent(window.location.hash);
        if (hash.startsWith('#search=')) {
            var q = hash.replace('#search=', '');
            var si = document.getElementById('universalSearch');
            if (si && q !== si.value.trim()) {
                si.value = q;
                performSearch();
            }
        }
    });
});

// Toast notification system for user-visible errors
function showToast(message, type = 'info') {
    // Remove existing toast if present
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = message;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), SEARCH_CONFIG.toastShowMs);
    
    // Auto-remove after the configured display window
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), SEARCH_CONFIG.toastRemoveMs);
    }, SEARCH_CONFIG.toastDismissMs);
}
