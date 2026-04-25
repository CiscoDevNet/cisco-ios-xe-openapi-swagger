// Recent & Favorites functionality for Cisco IOS-XE YANG Documentation
// Tracks user's recently viewed modules and allows bookmarking favorites

const STORAGE_KEYS = {
    RECENT: 'iosxe-recent-modules',
    FAVORITES: 'iosxe-favorite-modules'
};

const MAX_RECENT = 10;

// HTML sanitization to prevent XSS from localStorage data
function _escapeHtml(str) {
    if (str == null) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// Validate URLs to prevent javascript: protocol injection
function _sanitizeUrl(url) {
    if (!url) return '';
    const str = String(url).trim();
    if (/^https?:\/\//i.test(str) || str.startsWith('/') || str.startsWith('./') || str.startsWith('../')) return str;
    return '';
}

// Get recent modules from localStorage
function getRecentModules() {
    try {
        const recent = localStorage.getItem(STORAGE_KEYS.RECENT);
        return recent ? JSON.parse(recent) : [];
    } catch (error) {
        console.error('Error reading recent modules:', error);
        return [];
    }
}

// Add module to recent list
function addToRecent(module) {
    try {
        let recent = getRecentModules();
        
        // Remove if already exists
        recent = recent.filter(m => m.name !== module.name);
        
        // Add to beginning
        recent.unshift({
            name: module.name,
            type: module.type,
            displayCategory: module.displayCategory,
            emoji: module.emoji,
            swaggerUrl: module.swaggerUrl,
            yangTreeUrl: module.yangTreeUrl,
            timestamp: new Date().toISOString()
        });
        
        // Keep only MAX_RECENT items
        recent = recent.slice(0, MAX_RECENT);
        
        localStorage.setItem(STORAGE_KEYS.RECENT, JSON.stringify(recent));
        
        // Update display if on index page
        if (document.getElementById('recentModules')) {
            renderRecentModules();
        }
        return { success: true };
    } catch (error) {
        console.error('Error adding to recent:', error);
        if (typeof showToast !== 'undefined') {
            if (error.name === 'QuotaExceededError') {
                showToast('⚠️ Cannot save recent modules - storage is full', 'warning');
            } else {
                showToast('⚠️ Cannot save recent modules (storage may be disabled)', 'warning');
            }
        }
        return { success: false, error: error.message };
    }
}

// Get favorite modules from localStorage
function getFavoriteModules() {
    try {
        const favorites = localStorage.getItem(STORAGE_KEYS.FAVORITES);
        return favorites ? JSON.parse(favorites) : [];
    } catch (error) {
        console.error('Error reading favorites:', error);
        return [];
    }
}

// Toggle favorite status
function toggleFavorite(module) {
    try {
        let favorites = getFavoriteModules();
        const index = favorites.findIndex(f => f.name === module.name);
        
        if (index >= 0) {
            // Remove from favorites
            favorites.splice(index, 1);
        } else {
            // Add to favorites
            favorites.push({
                name: module.name,
                type: module.type,
                displayCategory: module.displayCategory,
                emoji: module.emoji,
                swaggerUrl: module.swaggerUrl,
                yangTreeUrl: module.yangTreeUrl,
                timestamp: new Date().toISOString()
            });
        }
        
        localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(favorites));
        
        // Update display if on index page
        if (document.getElementById('favoriteModules')) {
            renderFavoriteModules();
        }
        
        return index < 0; // Return true if added, false if removed
    } catch (error) {
        console.error('Error toggling favorite:', error);
        if (typeof showToast !== 'undefined') {
            if (error.name === 'QuotaExceededError') {
                showToast('⚠️ Cannot save favorites - storage is full', 'warning');
            } else {
                showToast('⚠️ Cannot save favorites (storage may be disabled)', 'warning');
            }
        }
        return false;
    }
}

// Check if module is favorited
function isFavorite(moduleName) {
    const favorites = getFavoriteModules();
    return favorites.some(f => f.name === moduleName);
}

// Copy text to clipboard
function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(() => {
        // Visual feedback
        const originalText = buttonElement.textContent;
        buttonElement.textContent = '✓ Copied!';
        buttonElement.style.background = '#4CAF50';
        
        setTimeout(() => {
            buttonElement.textContent = originalText;
            buttonElement.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

// Render recent modules section
function renderRecentModules() {
    const container = document.getElementById('recentModules');
    if (!container) return;
    
    const recent = getRecentModules();
    
    if (recent.length === 0) {
        container.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">No recent modules yet. Browse some modules to see them here!</p>';
        return;
    }
    
    const html = recent.map(module => {
        const isFav = isFavorite(module.name);
        const name = _escapeHtml(module.name);
        const emoji = _escapeHtml(module.emoji);
        const category = _escapeHtml(module.displayCategory);
        const swaggerUrl = _sanitizeUrl(module.swaggerUrl);
        const yangTreeUrl = _sanitizeUrl(module.yangTreeUrl);
        return `
            <div class="recent-card">
                <div style="display: flex; align-items: start; justify-content: space-between; gap: 8px;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span style="font-size: 0.75rem; color: #1565C0;">${emoji} ${category}</span>
                        </div>
                        <div style="font-weight: 500; color: #333; word-break: break-word;">${name}</div>
                    </div>
                    <button class="favorite-btn ${isFav ? 'active' : ''}" 
                            data-module="${name}"
                            onclick="toggleFavoriteUI(this.dataset.module, this)"
                            title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
                        ${isFav ? '★' : '☆'}
                    </button>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                    ${swaggerUrl ? `<a href="${_escapeHtml(swaggerUrl)}" class="quick-link" data-module="${name}" onclick="trackModuleClick(this.dataset.module)">📖 API Spec</a>` : ''}
                    ${yangTreeUrl ? `<a href="${_escapeHtml(yangTreeUrl)}" class="quick-link" data-module="${name}" onclick="trackModuleClick(this.dataset.module)">🌳 YANG Tree</a>` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// Render favorite modules section
function renderFavoriteModules() {
    const container = document.getElementById('favoriteModules');
    if (!container) return;
    
    const favorites = getFavoriteModules();
    
    if (favorites.length === 0) {
        container.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">No favorites yet. Click the star (☆) icon to bookmark modules!</p>';
        return;
    }
    
    const html = favorites.map(module => {
        const name = _escapeHtml(module.name);
        const emoji = _escapeHtml(module.emoji);
        const category = _escapeHtml(module.displayCategory);
        const swaggerUrl = _sanitizeUrl(module.swaggerUrl);
        const yangTreeUrl = _sanitizeUrl(module.yangTreeUrl);
        return `
            <div class="recent-card">
                <div style="display: flex; align-items: start; justify-content: space-between; gap: 8px;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span style="font-size: 0.75rem; color: #1565C0;">${emoji} ${category}</span>
                        </div>
                        <div style="font-weight: 500; color: #333; word-break: break-word;">${name}</div>
                    </div>
                    <button class="favorite-btn active" 
                            data-module="${name}"
                            onclick="toggleFavoriteUI(this.dataset.module, this)"
                            title="Remove from favorites">
                        ★
                    </button>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                    ${swaggerUrl ? `<a href="${_escapeHtml(swaggerUrl)}" class="quick-link" data-module="${name}" onclick="trackModuleClick(this.dataset.module)">📖 API Spec</a>` : ''}
                    ${yangTreeUrl ? `<a href="${_escapeHtml(yangTreeUrl)}" class="quick-link" data-module="${name}" onclick="trackModuleClick(this.dataset.module)">🌳 YANG Tree</a>` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// Toggle favorite from UI
function toggleFavoriteUI(moduleName, buttonElement) {
    // Find module in search index
    const module = searchIndex.find(m => m.name === moduleName);
    if (!module) return;
    
    const isNowFavorite = toggleFavorite(module);
    
    // Update button
    buttonElement.textContent = isNowFavorite ? '★' : '☆';
    buttonElement.classList.toggle('active', isNowFavorite);
    buttonElement.title = isNowFavorite ? 'Remove from favorites' : 'Add to favorites';
    
    // Re-render both sections
    renderRecentModules();
    renderFavoriteModules();
}

// Track when user clicks a module link (for recent tracking)
function trackModuleClick(moduleName) {
    const module = searchIndex.find(m => m.name === moduleName);
    if (module) {
        addToRecent(module);
    }
}

// Initialize recent & favorites on page load
document.addEventListener('DOMContentLoaded', () => {
    renderRecentModules();
    renderFavoriteModules();
});
