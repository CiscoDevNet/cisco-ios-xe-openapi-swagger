# Self-hosting the Cisco IOS XE OpenAPI Documentation Hub

Run the full site from a `git clone` on a laptop, behind a corporate proxy, on
an internal web server, or inside a fully **air-gapped / high-security**
network. The repository is self-contained: there are no runtime build steps,
no required services, no analytics, no telemetry, and (since v33) **no
external CDN or web-font requests**.

---

## TL;DR

```powershell
git clone https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger.git
cd cisco-ios-xe-openapi-swagger
python -m http.server 8000
# open http://localhost:8000
```

That is the entire deployment for a single user. For multi-user use behind a
real web server, see [Hosting behind nginx / IIS / Apache](#hosting-behind-a-real-web-server).

---

## What runs locally without internet

The site is 100% static HTML / CSS / JS / JSON. Every dependency required to
render any page is in the repository:

| Component | Where |
|-----------|-------|
| OpenAPI 2.0 spec bundles | `swagger-*-model/*.json` and `releases/<ver>/...` |
| Swagger UI 5.31.0 | `assets/vendor/swagger-ui-5.31.0/` (SRI-verified) |
| Fuse.js 7.0.0 (search) | `assets/vendor/fuse.js` (SRI-verified) |
| Chart.js 4.4.0 (hub charts) | `assets/vendor/chart.umd.js` (SRI-verified) |
| Postman / Bruno collections | `tools/` and `releases/<ver>/exports/` |
| YANG tree HTML | `yang-trees/` and `releases/<ver>/yang-trees/` |
| Per-release search & accountability indices | `releases/<ver>/*.json` |
| Fonts | System sans-serif fallback (`Roboto, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif`). Google Fonts is **not** loaded. |

A strict `Content-Security-Policy` declared in every HTML `<head>` enforces
`default-src 'self'` with no external hosts. You can verify by opening DevTools
→ Network and confirming every request resolves to your own host.

---

## Prerequisites

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| Disk space | ~1 GB | Repository is large because of `releases/` snapshots. Use shallow clone (`--depth 1`) to halve it. |
| Python | 3.9+ | Only needed if you use `python -m http.server`; the site itself has no Python runtime. |
| Browser | Any modern Chromium / Firefox / Edge / Safari from the last 2 years | The site is PWA-capable but does not require service workers to function. |
| Network egress from server | **None.** | Only the initial `git clone` needs internet (or transfer the repo by USB / artifact server). |

### Shallow clone (recommended for transfer)

If you only need the current release and want a smaller payload to move into
the air-gapped network:

```powershell
git clone --depth 1 https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger.git
```

Then bundle and transfer:

```powershell
Compress-Archive -Path cisco-ios-xe-openapi-swagger -DestinationPath xe-docs.zip
```

On the destination machine extract and serve. No further fetch is required.

---

## Quick start: single-user laptop

```powershell
cd cisco-ios-xe-openapi-swagger
python -m http.server 8000
```

Open `http://localhost:8000` in any modern browser. Every page (Universal
Search, every `swagger-*-model/` viewer, Tree Compare, Code Generator,
Telemetry, Platform Coverage, YANG Accountability, App Map) will function with
no further configuration.

### Optional: skip the service worker

If you do not want the PWA install prompt or offline caching, just ignore it.
The site works identically without registering the worker. To fully disable
it, delete `assets/js/sw-register.js` references — but there is no need.

---

## Hosting behind a real web server

The site is just a directory of static files. Point any web server at the
repository root.

### nginx

```nginx
server {
  listen 443 ssl;
  server_name xe-docs.internal.example.com;

  ssl_certificate     /etc/nginx/certs/xe-docs.crt;
  ssl_certificate_key /etc/nginx/certs/xe-docs.key;

  root /srv/cisco-ios-xe-openapi-swagger;
  index index.html;

  # YANG files are text; some browsers will offer to download them
  # without this hint.
  types {
    text/plain  yang;
    application/json  json;
  }

  # Cache the immutable vendored libs for a year.
  location /assets/vendor/ {
    add_header Cache-Control "public, max-age=31536000, immutable";
  }

  # Service worker should never be cached at the edge.
  location = /service-worker.js {
    add_header Cache-Control "no-cache, no-store, must-revalidate";
  }

  # SPA-style 404 -> the bundled 404.html (smart-suggest viewer).
  error_page 404 /404.html;
}
```

### IIS

The repo ships a `web.config` is **not** required. Default static-file
serving works. To suggest a `.yang` MIME mapping, add via IIS Manager →
MIME Types: `.yang` → `text/plain`.

### Apache (`httpd.conf` snippet)

```apache
<Directory "/srv/cisco-ios-xe-openapi-swagger">
  AddType text/plain .yang
  AddType application/json .json
  Options -Indexes
  AllowOverride None
  Require all granted
  ErrorDocument 404 /404.html
</Directory>

<LocationMatch "^/assets/vendor/">
  Header set Cache-Control "public, max-age=31536000, immutable"
</LocationMatch>

<Location "/service-worker.js">
  Header set Cache-Control "no-cache, no-store, must-revalidate"
</Location>
```

### Python (production)

For very small deployments (a few users, intranet) `python -m http.server` is
fine. For anything larger, prefer nginx — `http.server` is single-threaded and
not hardened for production.

---

## Security posture

What ships:

- **Strict CSP.** Every top-level page declares
  `default-src 'self'`. Viewer pages additionally allow
  `'unsafe-inline' 'unsafe-eval'` in `script-src` only because Swagger UI's
  bundle requires it; no external hosts are allowed under any directive.
- **Subresource Integrity (SRI).** Every `<script>` and `<link>` to a vendored
  third-party file carries a `integrity="sha384-..."` attribute. Tampering with
  any of the files under `assets/vendor/` is detected by the browser and the
  resource is rejected.
- **`X-Content-Type-Options: nosniff`** is set via `<meta>` on the home page.
- **No analytics, no telemetry, no third-party tracking.** Confirmed by
  `grep -r 'gtag\|analytics\|telemetry\|sentry\|datadog'` returning zero
  matches in user-facing code (the word "telemetry" only appears in YANG model
  context).
- **No outbound network calls** from any page in a fresh, freshly-served
  install. Verify with browser DevTools → Network: every request should be
  same-origin.

Recommended for high-security deployments:

1. Serve over HTTPS (with your internal CA).
2. Add HSTS at the web server (`Strict-Transport-Security: max-age=63072000; includeSubDomains`).
3. Add `X-Frame-Options: DENY` and `Referrer-Policy: no-referrer` at the
   server.
4. Audit `assets/vendor/README.md` against the upstream package SHA-384 hashes
   if your compliance regime requires reproducible-build attestation.
5. The repo includes an `_run_trees.ps1` helper and various scripts under
   `scripts/`. These are **build-time** developer tooling and never executed
   by the site itself; you do not need to copy them to your production
   deployment.

### Minimum file set for a production deployment

If you want to ship the smallest possible bundle, copy these and skip the
rest:

```
*.html
*.js
*.json
site.webmanifest
robots.txt
sitemap.xml
assets/
swagger-*-model/
yang-trees/
releases/        # only the version(s) you want to expose
tools/           # optional: Postman / Bruno collections
docs/            # optional: in-repo documentation
```

You can safely omit `archive/`, `generators/`, `references/`, `scripts/`,
`tests/`, `tmp/`, and the top-level `*.md` files (other than this guide if
you want it in-app).

---

## Updating vendored libraries

`assets/vendor/README.md` documents the upstream source, version, SHA-384
hash, and license for every vendored file. To refresh:

```powershell
# Edit assets/vendor/README.md with the new version + hashes.
# Then re-download (verifies SHA-384 against README on next run).
python -X utf8 scripts/vendor_offline_patch.py   # rewrites HTML refs
# Bump the SRI hashes inline in every consumer HTML file.
# Bump CACHE_VERSION in service-worker.js so clients pick up new vendor files.
```

The `scripts/vendor_offline_patch.py` script is **idempotent** — safe to run
any number of times. It strips Google Fonts links, rewrites jsdelivr URLs to
local `assets/vendor/` paths, and updates CSP `<meta>` tags.

---

## Troubleshooting

### "Swagger UI didn't load — blank page in `swagger-*-model/`"

Open DevTools → Console. The most common cause is that
`assets/vendor/swagger-ui-5.31.0/` is missing from your deployment (the
directory was excluded during file copy / archive). Re-deploy with the full
`assets/vendor/` tree.

### "All my YANG files download as `.yang` instead of opening"

Add the MIME hint shown in the nginx / IIS / Apache examples above so
`.yang` is served as `text/plain`.

### "Service worker is serving stale content after I redeployed"

Bump `CACHE_VERSION` in [service-worker.js](../service-worker.js#L16) before
deploying. Users will get the new build on the next page load. To force-clear
immediately, hard-reload (Ctrl + F5) or unregister the worker via DevTools →
Application → Service Workers → **Unregister**.

### "I see a `localhost:8000` URL in code-generator output"

By design — the Code Generator page produces example code targeting an
arbitrary RESTCONF device. Replace the placeholder host with your real device
IP/FQDN. No code is executed by the site; you copy/paste the snippet into
your own runtime.

### "Universal search returns nothing"

Fuse.js failed to load. Confirm `assets/vendor/fuse.js` is present and that
the SRI hash in [index.html](../index.html#L911) matches the file. If you
replaced the file, regenerate the SRI hash:

```powershell
$bytes = [System.IO.File]::ReadAllBytes('assets/vendor/fuse.js')
$sha   = [System.Security.Cryptography.SHA384]::Create().ComputeHash($bytes)
"sha384-$([Convert]::ToBase64String($sha))"
```

---

## What is not supported in air-gapped mode

- **External documentation links** (the "Related Tools" cards on the home
  page link to developer.cisco.com, yangcatalog.org, github.com/YangModels,
  rfc-editor.org, openconfig.net, developer.cisco.com/yangsuite, etc.) These
  open in a new tab and will fail to load if the user has no internet. They
  do not block any in-site functionality.
- **GitHub Issues / Discussions** links on the About page open github.com.
- **Live-device validation** (`scripts/validate_examples_c9kv.py`) is a
  developer tool that needs RESTCONF connectivity to a Cisco device — it is
  not a runtime dependency of the site.

---

## Feedback

File an issue at
<https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger/issues> describing
your deployment scenario. Pull requests improving this guide are welcome.
