// Universal Search for Cisco IOS-XE YANG Documentation Hub
// Provides fuzzy search across all YANG modules with browse-all capability

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

// Load search index
async function loadSearchIndex() {
    if (searchReadyPromise) return searchReadyPromise;
    
    searchReadyPromise = (async () => {
        try {
            const searchInput = document.getElementById('universalSearch');
            if (searchInput) {
                searchInput.placeholder = '⏳ Loading search index...';
                searchInput.disabled = true;
            }
            
            const response = await fetch('search-index.json');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            searchIndex = data.modules;
            
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
                threshold: 0.35,
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
                searchInput.placeholder = `Search ${searchIndex.length} modules — type a name, keyword, or feature... (Ctrl+K)`;
                searchInput.disabled = false;
            }
            
            // Search index loaded successfully
        } catch (error) {
            console.error('❌ Error loading search index:', error);
            const searchInput = document.getElementById('universalSearch');
            if (searchInput) {
                searchInput.placeholder = '⚠️ Search unavailable — please refresh the page';
                searchInput.disabled = false;
            }
            showToast('⚠️ Search unavailable. Please refresh the page.', 'error');
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
    return related.slice(0, 5);
}

// Render search results
function renderResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    
    if (!results || results.length === 0) {
        const noResultMsg = browseMode 
            ? '🔍 No modules match the selected filters.'
            : '🔍 No modules found. Try different keywords or broaden your filters.';
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
    const displayLimit = 60;
    const modeLabel = browseMode ? 'Browsing' : 'Found';
    const sortBtnStyle = (s) => `cursor:pointer; padding:3px 8px; border:1px solid ${currentSort===s ? '#1565C0' : 'var(--border-color,#ddd)'}; border-radius:4px; background:${currentSort===s ? '#1565C0' : 'var(--bg-card,#fff)'}; color:${currentSort===s ? '#fff' : 'var(--text-secondary,#666)'}; font-size:0.78rem;`;
    const sortBtn = (key, label) => `<button style="${sortBtnStyle(key)}" aria-pressed="${currentSort===key}" onclick="changeSort('${key}')">${label}</button>`;
    const sortHtml = `<span style="display:inline-flex;gap:4px;margin-left:12px;align-items:center;" role="group" aria-label="Sort results"><span style="font-size:0.78rem;color:var(--text-secondary,#666);">Sort:</span>${sortBtn('relevance','Relevance')}${sortBtn('name','Name')}${sortBtn('paths','Paths \u2193')}${sortBtn('type','Type')}</span>`;
    const statsHtml = `<div class="search-stats" style="display:flex;align-items:center;flex-wrap:wrap;">✨ ${modeLabel} ${totalResults} module${totalResults !== 1 ? 's' : ''}${totalResults > displayLimit ? ` — showing first ${displayLimit}` : ''}${sortHtml}</div>`;
    
    const cardsHtml = results.slice(0, displayLimit).map(result => {
        const module = result.item || result;
        const badgeClass = getBadgeClass(module.type);
        const borderColor = getBorderColor(module.type);
        const isFav = typeof isFavorite !== 'undefined' ? isFavorite(module.name) : false;
        const description = truncateDescription(module.description, 160);
        const escapedName = escapeHtml(module.name);
        const escapedDesc = escapeHtml(description);
        const pathLabel = module.type === 'rpc' ? 'operations' : 'paths';
        
        let linksHtml = '';
        if (module.swaggerUrl) {
            linksHtml += `<a href="${escapeHtml(module.swaggerUrl)}" class="search-result-link" data-module="${escapedName}">📖 View API Spec</a>`;
        }
        if (module.yangTreeUrl) {
            linksHtml += `<a href="${escapeHtml(module.yangTreeUrl)}" class="search-result-link" data-module="${escapedName}">🌳 View YANG Tree</a>`;
        }
        
        // Related modules in other categories
        const related = getRelatedModules(module);
        let relatedHtml = '';
        if (related.length > 0) {
            const relLinks = related.map(r => {
                const url = r.swaggerUrl ? escapeHtml(r.swaggerUrl) : '#';
                const badge = escapeHtml(r.displayCategory);
                const rName = escapeHtml(r.name);
                return `<a href="${url}" title="${rName}" class="related-link" data-related-search="${rName}">${escapeHtml(r.emoji)} ${badge}</a>`;
            }).join(' ');
            relatedHtml = `<div style="margin-top:6px;display:flex;align-items:center;gap:6px;flex-wrap:wrap;"><span style="font-size:0.75rem;color:var(--text-secondary,#888);">Also in:</span>${relLinks}</div>`;
        }
        
        return `
            <div class="search-result-card" style="border-left-color: ${borderColor}">
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
    
    if (totalResults > displayLimit) {
        resultsContainer.innerHTML += `<div class="search-stats" style="text-align: center; margin-top: 16px;">📌 Refine your search or filters to see more specific results.</div>`;
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
    if (!query || query.length < 2) {
        hideAutocomplete();
        return;
    }
    
    const lowerQuery = query.toLowerCase();
    const suggestions = autocompleteIndex
        .filter(entry => entry.name.toLowerCase().includes(lowerQuery))
        .slice(0, 8);
    
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
    
    if (query.length < 2) {
        document.getElementById('searchResults').innerHTML = '<div class="search-stats">⌨️ Type at least 2 characters to search...</div>';
        document.getElementById('searchResults').classList.add('active');
        return;
    }
    
    // Perform fuzzy search
    let results = fuse.search(query);
    
    // Apply filters
    results = filterResults(results);
    
    // Update URL hash for deep-linking
    updateUrlHash(query);
    
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
            window.location.href = modelDir + '/index-v2.html#spec=' + specName;
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
        
        // Debounced search (fast 200ms)
        searchTimeout = setTimeout(performSearch, 200);
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
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}
