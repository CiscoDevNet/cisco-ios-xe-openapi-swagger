/* eslint-disable no-restricted-globals */
// Cisco IOS XE OpenAPI & YANG Docs — Service Worker
// ---------------------------------------------------------------------
// Goals:
//   * Make repeat visits feel instant (stale-while-revalidate on HTML/JS/CSS)
//   * Tolerate transient network failures (offline fallback to cached shell)
//   * NEVER cache the bulky per-release artifacts (releases/**) or
//     cross-origin requests (Swagger UI CDN etc.) — those would explode
//     the cache budget and stale by the next deploy.
//
// Kill-switch: bumping the CACHE_VERSION below forces a clean reinstall
// on every client. The Activate handler also drops any cache that does
// not match the current name.
// ---------------------------------------------------------------------

const CACHE_VERSION = 'v65-2026.06.19d';
const RUNTIME_CACHE = 'iosxe-runtime-' + CACHE_VERSION;
const PRECACHE      = 'iosxe-precache-' + CACHE_VERSION;

// Resolve scope-relative URLs once. The SW is registered at
// /cisco-ios-xe-openapi-swagger/service-worker.js, so registration scope
// is /cisco-ios-xe-openapi-swagger/.
const SCOPE = self.registration && self.registration.scope
  ? new URL(self.registration.scope)
  : new URL('./', self.location);

const PRECACHE_URLS = [
  '',                       // -> scope root (index.html)
  'index.html',
  '404.html',
  'about.html',
  'yang-accountability.html',
  'tree-compare.html',
  'code-generator.html',
  'exports.html',
  'app-map.html',
  'notifications.js',
  'assets/css/site.css',
  'assets/js/site-chrome.js',
  'assets/js/sw-register.js',
  'about-stats.js',
  'assets/icons/favicon.svg',
  'assets/icons/favicon.ico',
  'assets/icons/apple-touch-icon.png',
  // Vendored third-party libs (air-gap support). SRI-pinned in HTML.
  'assets/vendor/fuse.js',
  'assets/vendor/chart.umd.js',
  'assets/vendor/swagger-ui-5.31.0/swagger-ui.css',
  'assets/vendor/swagger-ui-5.31.0/swagger-ui-bundle.js',
  'assets/vendor/swagger-ui-5.31.0/swagger-ui-standalone-preset.js',
].map((p) => new URL(p, SCOPE).toString());

// Paths under scope that we explicitly bypass (network-only).
// Per-release JSON spec bundles are large and updated atomically on deploy,
// so caching them just bloats local storage with stale data.
const BYPASS_PREFIXES = [
  'releases/',
  'archive/',
  'tools/',
];

function isBypassed(url) {
  if (url.origin !== SCOPE.origin) return true; // cross-origin -> bypass
  // Same-origin: check path prefix against scope-relative paths.
  if (!url.pathname.startsWith(SCOPE.pathname)) return true; // out of scope
  const rel = url.pathname.slice(SCOPE.pathname.length);
  return BYPASS_PREFIXES.some((p) => rel.startsWith(p));
}

// ---------------------------------------------------------------------
// Install: precache the app shell. Use addAll with individual catch
// fallbacks so a single 404 (e.g. on a renamed asset) does not abort
// the whole install.
// ---------------------------------------------------------------------
self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(PRECACHE);
    await Promise.allSettled(
      PRECACHE_URLS.map((u) => cache.add(new Request(u, { cache: 'reload' })))
    );
    // Activate immediately on next reload — no waiting for old tabs to close.
    await self.skipWaiting();
  })());
});

// ---------------------------------------------------------------------
// Activate: drop stale caches from previous versions.
// ---------------------------------------------------------------------
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keep = new Set([PRECACHE, RUNTIME_CACHE]);
    const names = await caches.keys();
    await Promise.all(
      names
        .filter((n) => n.startsWith('iosxe-') && !keep.has(n))
        .map((n) => caches.delete(n))
    );
    await self.clients.claim();
  })());
});

// ---------------------------------------------------------------------
// Fetch: strategy router.
//   * Bypass list           -> network passthrough (no caching)
//   * Cross-origin          -> network passthrough
//   * Navigations (HTML)    -> network-first with offline cache fallback
//   * Same-origin GET       -> stale-while-revalidate
// ---------------------------------------------------------------------
self.addEventListener('fetch', (event) => {
  const req = event.request;

  if (req.method !== 'GET') return;                    // never cache POST/PUT
  let url;
  try { url = new URL(req.url); } catch (_) { return; }

  if (isBypassed(url)) return;                         // skip — let network do it

  // Navigation requests (HTML page loads)
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(networkFirstWithOfflineFallback(req));
    return;
  }

  // Static assets — JS, CSS, JSON, images
  event.respondWith(staleWhileRevalidate(req));
});

async function networkFirstWithOfflineFallback(req) {
  const cache = await caches.open(RUNTIME_CACHE);
  try {
    const fresh = await fetch(req);
    if (fresh && fresh.ok) cache.put(req, fresh.clone());
    return fresh;
  } catch (err) {
    const cached = await cache.match(req);
    if (cached) return cached;
    // Last-ditch fallback: cached shell.
    const shell = await caches.match(new URL('index.html', SCOPE).toString());
    if (shell) return shell;
    return new Response('Offline and no cached copy available.',
      { status: 503, statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
  }
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cached = await cache.match(req);
  const network = fetch(req).then((res) => {
    // Only cache successful, basic (same-origin) responses.
    if (res && res.ok && res.type === 'basic') {
      cache.put(req, res.clone()).catch(() => {});
    }
    return res;
  }).catch(() => cached);          // network failed -> at least return cached
  return cached || network;
}

// ---------------------------------------------------------------------
// Allow pages to trigger an immediate update via postMessage.
// ---------------------------------------------------------------------
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
