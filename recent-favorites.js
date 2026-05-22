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

// When recording a module visit we may be on the index page (no current
// op/spec context) OR inside a viewer that has both. Sniff both sources
// so a starred entry can later be reopened on the same operation in the
// same release. Stored fields are intentionally lightweight strings.
function _snapshotContext(module) {
    var ctx = { op: null, ver: null };
    try {
        // 1. operationId from the current viewer hash (set by deeplink.js).
        var raw = (window.location.hash || '').replace(/^#/, '');
        raw.split('&').forEach(function (s) {
            var i = s.indexOf('=');
            if (i <= 0) return;
            var k = s.substring(0, i);
            var v = s.substring(i + 1);
            try { v = decodeURIComponent(v); } catch (_) {}
            if (k === 'op' && !ctx.op) ctx.op = v;
            if (k === 'ver' && !ctx.ver) ctx.ver = v;
            // Only attribute the op to *this* module — protects against
            // starring module A while spec=B is loaded in another tab via
            // shared localStorage.
            if (k === 'spec' && module && v && v !== module.name) {
                ctx.op = null;
            }
        });
    } catch (_) {}
    try {
        if (!ctx.ver && window.__IOSXE_ACTIVE_VERSION__) ctx.ver = window.__IOSXE_ACTIVE_VERSION__;
        if (!ctx.ver) ctx.ver = localStorage.getItem('iosxe-active-version');
    } catch (_) {}
    return ctx;
}

// Compose the final href for a stored module entry. The base swaggerUrl
// is of the form "swagger-cfg-model/index.html#spec=<name>". We append
// the op= and ver= the user had when they saved the entry so the link
// jumps back to the exact same row in the exact same release.
function _composeDeepLink(entry) {
    var url = _sanitizeUrl(entry && entry.swaggerUrl);
    if (!url) return '';
    // Make sure there's a hash to extend; older entries (no #spec=) get a
    // synthesized one from .name.
    if (url.indexOf('#') === -1 && entry && entry.name) {
        url += '#spec=' + encodeURIComponent(entry.name);
    }
    if (entry && entry.op && url.indexOf('&op=') === -1 && url.indexOf('#op=') === -1) {
        url += '&op=' + encodeURIComponent(entry.op);
    }
    if (entry && entry.ver && url.indexOf('&ver=') === -1 && url.indexOf('#ver=') === -1) {
        // Use ?ver= so the viewer's __activeVer() picks it up even if a
        // collision exists with hash params from a previous deep link.
        var hashIdx = url.indexOf('#');
        var path = hashIdx >= 0 ? url.substring(0, hashIdx) : url;
        var hash = hashIdx >= 0 ? url.substring(hashIdx) : '';
        var sep = path.indexOf('?') >= 0 ? '&' : '?';
        url = path + sep + 'ver=' + encodeURIComponent(entry.ver) + hash;
    }
    return url;
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
        
        // Snapshot op/ver from current viewer hash so we can reconstruct
        // a deep link when the entry is clicked later.
        const ctx = _snapshotContext(module);
        
        // Add to beginning
        recent.unshift({
            name: module.name,
            type: module.type,
            displayCategory: module.displayCategory,
            emoji: module.emoji,
            swaggerUrl: module.swaggerUrl,
            yangTreeUrl: module.yangTreeUrl,
            op: ctx.op || null,
            ver: ctx.ver || null,
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
                showToast('Cannot save recent modules - storage is full', 'warning');
            } else {
                showToast('Cannot save recent modules (storage may be disabled)', 'warning');
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
            // Add to favorites — capture current op/ver so re-opening this
            // bookmark lands the user on the same operation in the same
            // release they were viewing when they starred it.
            const ctx = _snapshotContext(module);
            favorites.push({
                name: module.name,
                type: module.type,
                displayCategory: module.displayCategory,
                emoji: module.emoji,
                swaggerUrl: module.swaggerUrl,
                yangTreeUrl: module.yangTreeUrl,
                op: ctx.op || null,
                ver: ctx.ver || null,
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
                showToast('Cannot save favorites - storage is full', 'warning');
            } else {
                showToast('Cannot save favorites (storage may be disabled)', 'warning');
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
        container.innerHTML = '<div class="empty-state">'
            + '<span class="empty-state-icon" aria-hidden="true">&middot;&middot;&middot;</span>'
            + '<div class="empty-state-title">No recent modules yet</div>'
            + '<p class="empty-state-hint">Use the search box above or click a category card below to start browsing OpenAPI specs. The last 10 you visit will appear here.</p>'
            + '</div>';
        return;
    }
    
    const html = recent.map(module => {
        const isFav = isFavorite(module.name);
        const name = _escapeHtml(module.name);
        const emoji = _escapeHtml(module.emoji);
        const category = _escapeHtml(module.displayCategory);
        const swaggerUrl = _composeDeepLink(module);
        const yangTreeUrl = _sanitizeUrl(module.yangTreeUrl);
        const opBadge = module.op
            ? '<span class="recent-op-badge" title="Opens directly on this operation">→ ' + _escapeHtml(module.op) + '</span>'
            : '';
        const verBadge = module.ver
            ? '<span class="recent-ver-badge" title="Saved while viewing this release">' + _escapeHtml(module.ver) + '</span>'
            : '';
        return `
            <div class="recent-card">
                <div style="display: flex; align-items: start; justify-content: space-between; gap: 8px;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                            <span style="font-size: 0.75rem; color: var(--accent-color, #1565C0);">${emoji} ${category}</span>
                            ${verBadge}
                        </div>
                        <div style="font-weight: 500; color: var(--text-primary, #333); word-break: break-word;">${name}</div>
                        ${opBadge}
                    </div>
                    <button class="favorite-btn ${isFav ? 'active' : ''}" 
                            data-module="${name}"
                            onclick="toggleFavoriteUI(this.dataset.module, this)"
                            title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
                        ${isFav ? '★' : '☆'}
                    </button>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                    ${swaggerUrl ? `<a href="${_escapeHtml(swaggerUrl)}" class="quick-link" data-module="${name}" onclick="trackModuleClick(this.dataset.module)">${module.op ? 'Open Operation' : 'Open Spec'}</a>` : ''}
                    ${yangTreeUrl ? `<a href="${_escapeHtml(yangTreeUrl)}" class="quick-link" data-module="${name}" onclick="trackModuleClick(this.dataset.module)">YANG Tree</a>` : ''}
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
        container.innerHTML = '<div class="empty-state">'
            + '<span class="empty-state-icon" aria-hidden="true">☆</span>'
            + '<div class="empty-state-title">No favorites yet</div>'
            + '<p class="empty-state-hint">When viewing any module, click the <strong>☆ star</strong> in the search result card or recent list to bookmark it here — we’ll remember the exact operation and release.</p>'
            + '</div>';
        return;
    }
    
    const html = favorites.map(module => {
        const name = _escapeHtml(module.name);
        const emoji = _escapeHtml(module.emoji);
        const category = _escapeHtml(module.displayCategory);
        const swaggerUrl = _composeDeepLink(module);
        const yangTreeUrl = _sanitizeUrl(module.yangTreeUrl);
        const opBadge = module.op
            ? '<span class="recent-op-badge" title="Opens directly on this operation">→ ' + _escapeHtml(module.op) + '</span>'
            : '';
        const verBadge = module.ver
            ? '<span class="recent-ver-badge" title="Saved while viewing this release">' + _escapeHtml(module.ver) + '</span>'
            : '';
        return `
            <div class="recent-card">
                <div style="display: flex; align-items: start; justify-content: space-between; gap: 8px;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                            <span style="font-size: 0.75rem; color: var(--accent-color, #1565C0);">${emoji} ${category}</span>
                            ${verBadge}
                        </div>
                        <div style="font-weight: 500; color: var(--text-primary, #333); word-break: break-word;">${name}</div>
                        ${opBadge}
                    </div>
                    <button class="favorite-btn active" 
                            data-module="${name}"
                            onclick="toggleFavoriteUI(this.dataset.module, this)"
                            title="Remove from favorites">
                        ★
                    </button>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                    ${swaggerUrl ? `<a href="${_escapeHtml(swaggerUrl)}" class="quick-link" data-module="${name}" onclick="trackModuleClick(this.dataset.module)">${module.op ? 'Open Operation' : 'Open Spec'}</a>` : ''}
                    ${yangTreeUrl ? `<a href="${_escapeHtml(yangTreeUrl)}" class="quick-link" data-module="${name}" onclick="trackModuleClick(this.dataset.module)">YANG Tree</a>` : ''}
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
