// Universal Search for Cisco IOS-XE YANG Documentation Hub
// Provides fuzzy search across all 768+ YANG modules

let searchIndex = [];
let fuse = null;
let activeFilters = new Set(['all']);

// Load search index
async function loadSearchIndex() {
    try {
        const response = await fetch('search-index.json');
        const data = await response.json();
        searchIndex = data.modules;
        
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
    if (activeFilters.has('all')) {
        return results;
    }
    
    return results.filter(result => {
        const module = result.item || result;
        return activeFilters.has(module.type);
    });
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
    
    // Setup search input with debounce
    let searchTimeout;
    document.getElementById('universalSearch').addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(performSearch, 300);
    });
});
