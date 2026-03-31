// Universal Search for Cisco IOS-XE YANG Documentation Hub
// Provides fuzzy search across all YANG modules with browse-all capability

// HTML Sanitization utility to prevent XSS
function escapeHtml(str) {
    if (str == null) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
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
            
            console.log(`✅ Loaded ${searchIndex.length} modules for search`);
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
    
    console.log(`✅ Built autocomplete index with ${autocompleteIndex.length} terms`);
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
        'configuration': '#00BCD4',
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
    
    const totalResults = results.length;
    const displayLimit = 60;
    const modeLabel = browseMode ? 'Browsing' : 'Found';
    const statsHtml = `<div class="search-stats">✨ ${modeLabel} ${totalResults} module${totalResults !== 1 ? 's' : ''}${totalResults > displayLimit ? ` — showing first ${displayLimit}` : ''}</div>`;
    
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
                <div class="search-result-links">${linksHtml}</div>
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
    });
    document.querySelector('[data-filter="all"]').classList.add('active');
    
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

// Perform search
function performSearch() {
    const query = document.getElementById('universalSearch').value.trim();
    
    if (!searchReady) return;
    
    // If no search text, check if we should browse by filter
    if (query.length === 0) {
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
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            } else {
                // Remove "All" filter if active
                if (activeFilters.has('all')) {
                    activeFilters.clear();
                    document.querySelector('[data-filter="all"]').classList.remove('active');
                }
                
                // Toggle this filter
                if (activeFilters.has(filterValue)) {
                    activeFilters.delete(filterValue);
                    btn.classList.remove('active');
                } else {
                    activeFilters.add(filterValue);
                    btn.classList.add('active');
                }
                
                // If no filters active, activate "All"
                if (activeFilters.size === 0) {
                    activeFilters.add('all');
                    document.querySelector('[data-filter="all"]').classList.add('active');
                }
            }
            
            // Re-run search with new filters
            performSearch();
        });
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSearchIndex();
    setupFilters();
    
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
    });
    
    console.log('✅ Search initialized. Press Ctrl+K to search!');
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
