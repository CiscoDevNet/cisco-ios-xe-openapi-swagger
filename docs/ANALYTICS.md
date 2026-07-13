# Analytics (Microsoft Clarity + PostHog)

This site runs **two** complementary analytics tools behind **one** wrapper:

| Tool | Purpose | Where it lives |
|------|---------|----------------|
| **Microsoft Clarity** | Heatmaps, session recordings, debugging. Custom tags (release, model, page, spec, operation). | Bootstrapped in `assets/js/sw-register.js` (`window.clarity`). |
| **PostHog** | Aggregate reporting, charts, dashboards, exports. Structured events + properties. | Loaded by `assets/js/analytics.js` (`window.posthog`). |

Application code **never** calls `window.clarity` or `window.posthog` directly.
It calls the wrapper: **`window.analytics`** (or the legacy `window.__iosxeTrack`
shim, which now routes through the wrapper too).

---

## Where analytics is initialized

Loaded on every interactive page in this fixed order (all external scripts; the
strict-CSP pages forbid inline executable script). The block is injected by
`scripts/inject_pwa.py`:

1. `assets/js/analytics-config.js` *(sync)* — sets `window.__ANALYTICS_CONFIG__`
   (PostHog key/host, `appVersion`, `environment`).
2. `assets/js/sw-register.js` *(defer)* — service worker + **Clarity** bootstrap
   and Clarity page tags.
3. `assets/js/analytics.js` *(defer)* — the **wrapper**. Creates
   `window.analytics`, loads **PostHog**, and re-points `window.__iosxeTrack` so
   existing call sites also reach PostHog.

CSP: `scripts/inject_pwa.py` allowlists `https://*.clarity.ms`,
`https://*.posthog.com`, and `https://*.i.posthog.com` in `script-src` and
`connect-src` on every page that has a CSP meta.

### Configuration (no hardcoded secrets)

`assets/js/analytics-config.js`:

```js
window.__ANALYTICS_CONFIG__ = {
  posthog: { apiKey: 'PLACEHOLDER_POSTHOG_KEY', host: 'https://us.i.posthog.com' },
  appVersion: 'v72-2026.07.13a',
  environment: ''            // auto-detected from hostname when blank
};
```

- A PostHog **project API key** (`phc_...`) is a **public, client-side write
  key** — like the Clarity project id. It is safe to ship to the browser. Do
  **not** put a PostHog *personal* key (`phx_...`) or any real secret here.
- Provide the value either by editing the placeholder, or at deploy time via CI,
  e.g. `sed -i "s/PLACEHOLDER_POSTHOG_KEY/$POSTHOG_KEY/" assets/js/analytics-config.js`
  reading `$POSTHOG_KEY` from a CI variable.
- If the key is empty or still the placeholder, **PostHog stays disabled** and
  Clarity keeps working (fail-open).
- `environment` auto-detects: `localhost` → `development`,
  `ciscodevnet.github.io` → `production`, `jeremycohoe.github.io` → `staging`.

In the **PostHog project settings**, also enable **"Discard client IP data"** so
the server-side IP is not retained (see Privacy below).

---

## Event names and properties

Every event automatically carries `app_version`, `environment`, and
`page_or_section` (added by the wrapper if the caller does not supply them).

| Event | Fired when | Key properties |
|-------|-----------|----------------|
| `app_loaded` | Each page view (wrapper, on ready). | — |
| `data_model_selected` | A YANG model/module is chosen (telemetry, notifications, viewer tree). | `yang_model`, `model_category`, `release` |
| `api_operation_selected` | An operation is expanded in a viewer (or code generated). | `api_operation`, `yang_model`, `http_method` |
| `api_request` | A Swagger UI **Try it out** call completes. | `api_operation`, `yang_model`, `http_code`, `result` |
| `api_error` | A Try-it-out call fails (network/timeout). | `api_operation`, `yang_model`, `result`, `error_type` |
| `export_results` | A CSV/export download runs. | `export_type`, `row_count`, `result` |
| `workflow_completed` | A multi-step task finishes (subscription built, code generated). | `workflow`, `api_operation`, `yang_model` |

`result` is one of `success | error | timeout`.

The headline call (matches the agreed shape exactly):

```js
analytics.trackApiRequest({
  api_operation: selectedOperation,   // e.g. "GET /data/Cisco-IOS-XE-bgp-oper:bgp-state-data"
  yang_model: selectedYangModel,      // e.g. "Cisco-IOS-XE-bgp-oper"
  http_code: response.status,
  result: response.ok ? 'success' : 'error',
  page_or_section: currentPage,       // optional; auto-filled if omitted
});
```

Wrapper API (`window.analytics`):

- `track(name, props)` — generic; sends to **both** PostHog and Clarity.
- `trackApiRequest(props)`
- `trackAppLoaded(props)`
- `trackDataModelSelected(props)`
- `trackApiOperationSelected(props)`
- `trackApiError(props)`
- `trackExportResults(props)`
- `trackWorkflowCompleted(props)`

Each call fans out to:
- **PostHog** → `posthog.capture(name, properties)` (dashboards/exports).
- **Clarity** → `clarity('event', name)` + `clarity('set', key, value)` for each
  property (recordings can be sliced by the same dimensions).

---

## How to add a new event

1. Pick a stable, lowercase, snake_case name (reuse an existing one if it fits).
2. Call the wrapper at the interaction point, guarded and fail-silent:

   ```js
   try {
     if (window.analytics) window.analytics.track('my_new_event', {
       yang_model: modelName,
       some_dimension: value,          // normalized, non-sensitive only
     });
   } catch (e) { /* noop */ }
   ```

   Or add a named helper to `assets/js/analytics.js` if it is part of the
   standard set.
3. Only pass **normalized, non-sensitive** properties (see Privacy). Keep values
   short; the wrapper truncates to 160 chars and drops objects.
4. If the page is new, make sure it is in `scripts/inject_pwa.py` so the
   analytics scripts + CSP hosts are injected, then re-run it.
5. Document the event in the table above.

---

## Privacy rules

The wrapper enforces these; do not bypass them.

**Never send** usernames, emails, IP addresses, device IDs, customer names,
hostnames, serial numbers, MAC addresses, tokens/secrets, cookies, session ids,
raw URLs, request/response payloads, or raw search/filter text.

How it is enforced in `assets/js/analytics.js`:

- **Key denylist** (`DENY_KEYS`) drops properties named `email`, `user`,
  `hostname`, `serial`, `token`, `url`, `payload`, `query`, `search`, `ip`, … on
  an exact (lower-cased) key match.
- **Value redaction** drops any value that looks like an email or an IPv4
  address, and never sends objects/arrays.
- **Truncation** caps string values at 160 chars.
- **PostHog auto-properties** are additionally sanitized (`sanitize_properties`):
  `$current_url`/`$initial_current_url` are reduced to a path (no query/hash/
  origin), and `$referrer`/`$referring_domain`/`$ip` are removed.
- PostHog is initialized with `autocapture: false`, `capture_pageview: false`,
  `disable_session_recording: true`, `person_profiles: 'identified_only'` — no
  DOM text capture, no anonymous person profiles.
- **Do-Not-Track**: when the browser sends a DNT signal, the wrapper sends
  **nothing** (to PostHog *or* Clarity) and PostHog is not even loaded; Clarity
  bootstrap in `sw-register.js` is likewise skipped. Controlled by
  `respectDoNotTrack` in `analytics-config.js` (default `true`).
- Enable **"Discard client IP data"** in the PostHog project settings to drop the
  server-observed IP.

**Clarity field masking:** Clarity masks input values by default. For any
sensitive UI field (e.g. the code-generator host/username/password inputs), add
`data-clarity-mask="true"` to the element so its contents never appear in
recordings. Never pass such field values to `analytics.*`.

---

## Building PostHog reports

All the required dashboards are breakdowns of the `api_request` event (plus
`app_loaded` for usage). In PostHog:

1. **API requests over time** — Insight → *Trends* → series = event `api_request`
   → *Total count* → time interval Day/Week.
2. **Top API operations** — `api_request` → **Break down by** property
   `api_operation` → bar chart, sort desc.
3. **Top selected YANG models** — event `data_model_selected` (or `api_request`)
   → **Break down by** `yang_model`.
4. **HTTP status distribution** — `api_request` → **Break down by** `http_code`
   → pie/bar.
5. **Error rate by API operation** — Insight → *Trends* → two series on
   `api_request`: (a) total, (b) filtered `result = error` → set display to
   **"% of total"**, then **Break down by** `api_operation`. (Include `timeout`
   in the error series if desired.)
6. **Usage by app version / section** — event `app_loaded` → **Break down by**
   `app_version` (or `page_or_section`).

Add each insight to a **Dashboard** ("IOS-XE Docs — API Usage"). Use the global
`environment` filter to separate production from staging/development. Exports:
each insight has **Export → CSV**.

---

## Files

| File | Role |
|------|------|
| `assets/js/analytics-config.js` | Public config: PostHog key/host, app version, environment. |
| `assets/js/analytics.js` | The wrapper: `window.analytics`, PostHog loader, Clarity mirror, sanitizer, `app_loaded`. |
| `assets/js/sw-register.js` | Service worker + Microsoft Clarity bootstrap + Clarity page tags. |
| `scripts/inject_pwa.py` | Injects the analytics scripts and allowlists Clarity + PostHog in each page CSP. |
| `tests/test_js_syntax.py` | Bracket-balance guard (covers the analytics JS). |
