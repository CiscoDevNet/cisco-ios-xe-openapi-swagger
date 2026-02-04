// Universal Search for Cisco IOS-XE YANG Documentation Hub
// Provides fuzzy search across all 768+ YANG modules

let searchIndex = [];
let fuse = null;
let activeFilters = new Set(['all']);
let advancedFilters = {
    prefix: 'all',
    hasTree: 'all',
    hasSpec: 'all'
};
let autocompleteIndex = [];
let selectedSuggestionIndex = -1;

// Load search index
async function loadSearchIndex() {
    try {
        const response = await fetch('search-index.json');
        const data = await response.json();
        searchIndex = data.modules;
        
        // Build autocomplete index
        buildAutocompleteIndex();
        
        // Initialize Fuse.js
        fuse = new Fuse(searchIndex, {
            keys: ['name', 'keywords', 'description', 'displayCategory'],
            threshold: 0.3,
            includeScore: true,
            minMatchCharLength: 2
        });
        
        console.log(`✅ Loaded ${searchIndex.length} modules for search`);
    } catch (error) {
        console.error('❌ Error loading search index:', error);
    }
}

// Build autocomplete suggestions index
function buildAutocompleteIndex() {
    const suggestions = new Set();
    
    // Add module names
    searchIndex.forEach(module => {
        suggestions.add(module.name);
        
        // Add keywords
        if (module.keywords) {
            module.keywords.forEach(keyword => suggestions.add(keyword));
        }
    });
    
    autocompleteIndex = Array.from(suggestions).sort();
    console.log(`✅ Built autocomplete index with ${autocompleteIndex.length} terms`);
}

// Get badge class for module type
function getBadgeClass(type) {
    const badgeMap = {
        'operational': 'badge-operational',
        'config': 'badge-config',
        'rpc': 'badge-rpc',
        'events': 'badge-events',
        'mib': 'badge-mib',
        'ietf': 'badge-ietf',
        'openconfig': 'badge-openconfig',
        'configuration': 'badge-configuration',
        'other': 'badge-other',
        'yang-tree': 'badge-yang-tree',
        'mib-tree': 'badge-mib-tree'
    };
    return badgeMap[type] || 'badge-other';
}

// Render search results
function renderResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">🔍 No modules found. Try different keywords or filters.</div>';
        resultsContainer.classList.add('active');
        return;
    }
    
    const statsHtml = `<div class="search-stats">✨ Found ${results.length} module${results.length !== 1 ? 's' : ''}</div>`;
    
    const cardsHtml = results.slice(0, 50).map(result => {
        const module = result.item || result;
        const badgeClass = getBadgeClass(module.type);
                const isFav = typeof isFavorite !== 'undefined' ? isFavorite(module.name) : false;
                
                let linksHtml = '';
                if (module.swaggerUrl) {
                    linksHtml += `<a href="${module.swaggerUrl}" class="search-result-link" onclick="trackModuleClick('${module.name}')">📖 View API Spec</a>`;
                }
                if (module.yangTreeUrl) {
                    linksHtml += `<a href="${module.yangTreeUrl}" class="search-result-link" onclick="trackModuleClick('${module.name}')">🌳 View YANG Tree</a>`;
                }
                
                return `
                    <div class="search-result-card">
                        <div class="search-result-header">
                            <span class="search-result-badge ${badgeClass}">${module.emoji} ${module.displayCategory}</span>
                            <span class="search-result-title">${module.name}</span>
                            <button class="favorite-btn ${isFav ? 'active' : ''}" 
                                    onclick="toggleFavoriteUI('${module.name.replace(/'/g, "\\'")}', this)"
                                    title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
                                ${isFav ? '★' : '☆'}
                            </button>
                    ${linksHtml}
                </div>
            </div>
        `;
    }).join('');
    
    resultsContainer.innerHTML = statsHtml + cardsHtml;
    resultsContainer.classList.add('active');
    
    if (results.length > 50) {
        resultsContainer.innerHTML += `<div class="search-stats" style="text-align: center; margin-top: 16px;">📌 Showing first 50 results. Refine your search to see more.</div>`;
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
        .filter(term => term.toLowerCase().includes(lowerQuery))
        .slice(0, 8);
    
    if (suggestions.length === 0) {
        hideAutocomplete();
        return;
    }
    
    const autocompleteDiv = document.getElementById('autocomplete');
    autocompleteDiv.innerHTML = suggestions.map((term, index) => {
        const highlightedTerm = term.replace(
            new RegExp(query, 'gi'),
            match => `<strong>${match}</strong>`
        );
        return `<div class="autocomplete-item ${index === selectedSuggestionIndex ? 'selected' : ''}" 
                     onclick="selectSuggestion('${term.replace(/'/g, "\\'")}')">${highlightedTerm}</div>`;
    }).join('');
    
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
    
    performSearch();
}

// Perform search
function performSearch() {
    const query = document.getElementById('universalSearch').value.trim();
    
    if (!fuse || query.length === 0) {
        document.getElementById('searchResults').classList.remove('active');
        return;
    }
    
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
        
        // Debounced search
        searchTimeout = setTimeout(performSearch, 300);
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
    
    console.log('✅ Search initialized. Press Ctrl+K to search!');
});
