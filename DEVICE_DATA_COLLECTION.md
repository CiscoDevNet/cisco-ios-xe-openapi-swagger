# Device Data Collection — Catalyst 9000 RESTCONF (Track B)

Self-contained context for continuing on the VM that can reach the 6 Catalyst
9000 switches. Keep this file at the repo root. This is the sole context carrier
— the web-app session's chat memory does not travel with the SCP.

## 0. Current status (2026-07-30)
The GET-phase harness is BUILT and lives under `scripts/harness/`. This section
supersedes any "to build" wording later in the doc — those sections describe the
design intent; the modules below already implement it.

| Component | File | State |
|---|---|---|
| GET-only client (safety core) | `scripts/harness/request.py` | Built — `restconf_get` + `assert_get_only` raise on any non-GET |
| Path enumeration from specs | `scripts/harness/spec_paths.py` | Built — reads category manifests, emits GET paths |
| Inventory + credential loading | `scripts/harness/inventory.py` | Built — loads `inventory.json`, env creds |
| Collector (capture engine) | `scripts/harness/collector.py` | Built — preflight/pilot/full/roots-only/dry-run, resume-safe |
| Light redaction | `scripts/harness/redact.py` | Built — strips secrets before disk |
| Value-discovery index | `scripts/harness/build_capture_index.py` | Built — flattens captures to rows |
| Value/keyword search + coverage | `scripts/harness/find_value.py` | Built — `--value` / `--keyword` / `--coverage` |
| Offline raw-capture browser | `scripts/harness/report.py` | Built — emits `capture-report.html` (gitignored) |
| Real-data example overlay | `scripts/harness/build_observed_examples.py` | Built — emits the `x-cisco-live-examples` sidecar; see §11.0 (SHIPPED) |
| Secret-scan guard | `scripts/harness/secret_scan.py` | Built |
| Tests | `scripts/harness/tests/` | Built (pytest) |
| Inventory template | `scripts/harness/inventory.example.json` | Committed (6 placeholder devices) |

**Remaining / to verify on arrival:**
- Fill `inventory.json` with the 6 real devices and set `IOSXE_USER`/`IOSXE_PASS`.
- Run `--preflight`, then `--pilot`, then scale (see §9 run guide).
- Confirm no real capture has been committed (all under gitignored `captures/`).
- Phase 4 (web-app injection) is **SHIPPED** (see §11.0); Phase 5 (CRUD) is still design-only.

## 1. What we're building
A dev-only Python harness (Track B) that connects to 6 real Catalyst 9000
switches (C9200/9300/9400/9500/9600, IOS XE 26.1.1) over RESTCONF and:
1. GET phase (first, strictly READ-ONLY): comprehensive GETs across oper + mib +
   cfg + native models per device; store raw responses locally.
2. Value-discovery: index the captures so we can search a value (e.g. 633024) or
   keyword (policer/dot1x/forus/l2-control) and get back the exact
   pid/module/path/leaf that returned it (CLI-output -> YANG-path mapping).
3. CRUD phase (LATER, separately gated): controlled config changes with backup,
   dry-run, confirmation, and rollback.

Two parallel tracks: Track A = the static web app (other session/workspace);
Track B = this harness (this VM). Web-app injection of captured data is DEFERRED
until we have multi-PID captures.

## 2. Canonical use case
Prove the CLI-output -> YANG-path mapping end to end on one module before scaling.
The pilot target is the oper module `Cisco-IOS-XE-switch-dp-punt-inject-oper`
(wired as `PILOT_CATEGORY`/`PILOT_MODULE` in `collector.py`):
1. GET the punt/inject oper subtree on ONE device.
2. Confirm `punt-inject-cpuq-brief-stats` returns queue names + counters.
3. Search the index for a known value (e.g. `633024`) and get back the exact
   device/pid/module/path/leaf that produced it.
Once that round-trips, the same pipeline scales to all oper/mib/cfg/native
modules across all 6 PIDs, and the per-PID coverage matrix falls out for free.

## 3. Repo facts the harness needs
- Specs are OpenAPI 3.0 JSON under releases/26.1.1/swagger-<cat>-model/api/*.json.
  servers.url = https://{device}:{port}/restconf ; paths like /data/Cisco-IOS-XE-...:...
  RESTCONF URL = "https://<host>:<port>/restconf" + <openapi path>.
- GET-only categories: oper (~22,144 paths) + mib (~4,272). cfg/native are CRUD
  but can be GET too (read running config). rpc = POST /operations (skip in GET phase).
- Path source per category manifest: releases/26.1.1/swagger-<cat>-model/api/manifest.json ("modules": [...]).
- Existing code to REUSE:
  - scripts/validate_examples_c9kv.py -> restconf_request(method, host, path, payload,
    username, password, port=443): requests + HTTP Basic + verify=False + timeout=30,
    HEADERS = application/yang-data+json. Also has extract_write_examples() for PUT/PATCH/POST
    (useful for the later CRUD phase). Reuse the request pattern; add a GET-only wrapper.
    NOTE: this file is gitignored (local scratch) but travels with an SCP of the folder.
  - scripts/build_paths_index.py -> pattern for building/consuming a JSON search index.
  - scripts/apply_example_overlay.py + references/native-example-overlay.yaml -> overlay injection (Phase 4).
  - scripts/add_oper_examples.py -> domain-aware example injection (Phase 4 alt).
- Run env: `python -X utf8 ...`; `pip install requests`. Confirm Python 3 + requests on the VM first.
- Tests live in tests/ (pytest). Add harness tests + a secret-scan guard for any committed scrubbed capture.

## 4. Harness design (GET phase)
Directory: scripts/harness/ (dev-only; NOT wired into build_release.py, CI, or the Pages deploy).
- request.py: single restconf_get(host, port, path, auth, timeout) that HARD-REFUSES any
  non-GET method (raise). This guard is the safety core for the whole GET phase.
- inventory: scripts/harness/inventory.json (GITIGNORED) =
  [{ "name": "sw1", "pid": "C9300-48T", "host": "10.x.x.x", "port": 443,
     "os_version": "26.1.1", "writable": false }]
  A committed scripts/harness/inventory.example.json ships with placeholders.
- creds: env vars IOSXE_USER / IOSXE_PASS (or per-host in a gitignored secrets file).
  Never write creds into captures or logs.
- path enumeration: read the 4 category manifests -> load each module spec -> collect every
  GET path. Exhaustive per-path GET is the chosen mode; also provide a --roots-only fast mode
  (GET each module root container once; the subtree contains child data).
- capture format: scripts/harness/captures/<device-name>/<category>/<module>__<path-hash>.json =
  { device, pid, host, module, category, path, restconf_url, http_status, fetched_at,
    os_version, response }  (raw response verbatim). captures/ is GITIGNORED.
- robustness: concurrency cap (4-8), per-request timeout, retry/backoff on 5xx/timeouts,
  resume (skip already-captured), rate-limit, per-module summary (200/404/empty/error).
  Handle 204/empty bodies and non-JSON gracefully.
- pilot first: capture ONE device, just the switch-dp-punt-inject-oper path, to prove the
  pipeline end-to-end, then scale to all modules and all 6 devices.

## 5. Value-discovery index
scripts/harness/build_capture_index.py (mirror scripts/build_paths_index.py):
- Walk every captured response; recursively flatten to rows (device, pid, module, path,
  leaf_xpath, value). Emit scripts/harness/capture-index.json (or SQLite for speed).
scripts/harness/find_value.py:
- Query by value (exact/substring, e.g. 633024) OR keyword (policer, dot1x, forus, l2-control,
  cpu-punt-queue-name) -> list of (device, pid, module, path, leaf, value).
- Emit a per-PID coverage matrix (module/path x PID -> has-data / 404 / empty).
Optional: a small offline HTML/JSON report to browse results.

## 6. Sanitization / safety (repo is PUBLIC - CiscoDevNet)
- Raw captures stay LOCAL and GITIGNORED. Nothing device-real is committed until scrubbed + reviewed.
- Redaction level chosen: LIGHT (strip obvious secrets/keys - passwords, community strings,
  certs, private keys, tokens). IPs/serials/MACs/hostnames kept (lab data) UNLESS the data
  classification says otherwise (confirm before committing anything).
- Add a tests/ secret-scan guard over any committed scrubbed capture (regex for
  BEGIN PRIVATE KEY, password/secret fields, SNMP community, etc.).
- Creds only from env/gitignored files; never in outputs.
- GET-only guard enforced in code for this phase.

## 7. Phase 5 - CRUD (LATER; do NOT start until GET capture is solid)
Separate opt-in write mode on top of the default GET-only guard:
- Lab-writable allowlist: refuse writes unless inventory host has "writable": true.
- Backup-before/after: GET the target subtree + running-config before any change; snapshot pre/post.
- Dry-run default: print exact method + URL + body; require --apply and per-change confirmation.
- Reversible/idempotent changes only to start (e.g. a benign interface description or loopback).
- Rollback: keep the pre-change payload; restore and verify.
- Reuse validate_examples_c9kv.py extract_write_examples() to source PUT/PATCH/POST bodies,
  but never fire without the guardrails above.
- Purpose: prove documented write examples work per PID; capture real before/after pairs.

## 8. .gitignore additions (already applied in this repo)
```
scripts/harness/captures/
scripts/harness/inventory.json
scripts/harness/secrets*
scripts/harness/capture-index.*
!scripts/harness/inventory.example.json
```

## 9. Run guide (the harness is already built)
All commands run from the repo root. Use `python -X utf8` and the `-m` module form
so package imports resolve. A venv is recommended: `python -m venv .venv-harness &&
source .venv-harness/bin/activate && pip install requests`.

**1. One-time setup**
```bash
cp scripts/harness/inventory.example.json scripts/harness/inventory.json   # then edit: real 6 devices
export IOSXE_USER=<user>            # never written to captures/logs
export IOSXE_PASS=<pass>
# VERIFY THE BASE URL FIRST (biggest pilot risk): this must return HTTP 200 with
# a JSON body, NOT 404. If it 404s, the restconf root/path composition is wrong
# and every GET will fail — fix before scaling.
curl -k -u "$IOSXE_USER" https://<host>/restconf/data/Cisco-IOS-XE-native:native/hostname \
     -H "Accept: application/yang-data+json" -i
```

**2. Preflight (no device I/O)** \u2014 verifies specs, inventory, and creds:
```bash
python -X utf8 -m scripts.harness.collector --preflight
python -X utf8 -m scripts.harness.collector --dry-run          # print the GET plan only
```

**3. Pilot** \u2014 one device, the punt/inject oper module (\u00a72):
```bash
python -X utf8 -m scripts.harness.collector --pilot
python -X utf8 -m scripts.harness.build_capture_index
python -X utf8 -m scripts.harness.find_value --value 633024
python -X utf8 -m scripts.harness.report --open           # eyeball the raw captures
```
Confirm `punt-inject-cpuq-brief-stats` shows queue names/counters before scaling.

**4. Scale** \u2014 all categories, all devices (resume-safe; re-run to continue):
```bash
python -X utf8 -m scripts.harness.collector                    # all 6 devices, oper+mib+cfg+native
python -X utf8 -m scripts.harness.collector --roots-only       # faster: root container per module
# scope helpers: --device sw2 --category oper --module Cisco-IOS-XE-... --concurrency 6
```

**5. Index + discover** \u2014 build the CLI->YANG mapping and per-PID coverage:
```bash
python -X utf8 -m scripts.harness.build_capture_index
python -X utf8 -m scripts.harness.find_value --keyword policer
python -X utf8 -m scripts.harness.find_value --coverage        # per-PID data/no-data matrix
```

**6. Safety gate before committing anything** \u2014 raw captures stay local/gitignored:
```bash
python -X utf8 -m scripts.harness.secret_scan scripts/harness/captures
python -X utf8 -m pytest scripts/harness/tests -q
```

**7. Report back**, then plan Phase 4 (web-app injection, \u00a711) and Phase 5 (CRUD, \u00a77).

## 10. Open prereqs to confirm on arrival
- Python/requests present on the VM; direct HTTPS/443 to devices or via jump host?
- The 6 devices' mgmt IPs + exact PIDs + whether lab (affects redaction depth).
- Data classification: is keeping serials/MACs/IPs acceptable for the PUBLIC repo?

## 11. Phase 4 - web-app representation of captured data (SHIPPED)

### 11.0.1 SHIPPED (2026-07-31)
Phase 4 is built and deployed. End-to-end pipeline, multi-device (aggregates per PID):

1. **Collect** (per device, resume-safe; crashers auto-excluded):
   `python -X utf8 -m scripts.harness.collector --device <name> [--device ...]`
2. **Build the committable sidecar** from ALL device captures:
   `python -X utf8 -m scripts.harness.build_observed_examples --sidecar references/live-examples-26.1.1.json`
3. **Emit the served artifacts** (index + tiny module summary + per-path body files):
   `python scripts/build_live_examples_index.py --version 26.1.1`

Step 3 is wired into `scripts/build_release.py` (after `manifests`). The OpenAPI
specs are **never modified** — they keep only their synthetic example, so the
Swagger viewers stay lean. The real bodies live in
`releases/<ver>/live-data/<category>/<module>/<hash>.json` and are fetched by the
Live Data page on demand.

**Surfaces:**
- Interactive page `live-data.html` (+ `live-data.js`): device tabs (per PID),
  per-category coverage cards + summary charts, module/path browser, real-response
  drill-down (fetches one small per-path data file).
- Lightweight in-viewer "Live device data" banner in
  `assets/js/viewer-enhancements.js` (reads the ~32 KB `live-modules.json`) that
  deep-links into the page.

**Committed vs local:** `releases/<ver>/live-examples-index.json`,
`releases/<ver>/live-modules.json`, and `releases/<ver>/live-data/**` are
committed/served; raw captures, `inventory.json`, `.env`, and
`references/live-examples-*.json` stay local (gitignored).

### 11.0 AGREED DECISION (user-confirmed 2026-07-30; from webapp main §5a) — SUPERSEDES 11.A.2
How the collected real data shows up in the web app (built AFTER captures exist):
- Keep the existing synthetic `example` UNTOUCHED (YANG-aligned baseline; always renders in Swagger UI).
- ADD real captures as an OpenAPI vendor EXTENSION field next to it (NOT an HTTP header):
  ```jsonc
  "content": { "application/yang-data+json": {
      "schema": {...}, "example": {...synthetic...},
      "x-cisco-live-examples": { "C9300-24UX": {...real...}, "C9500-40X": {...}, ... }  // per PID
  }}
  ```
  Matches the repo's existing `x-` convention (specs already carry `x-yang-module`, `x-model-type`).
- Swagger UI IGNORES unknown `x-` fields, so a viewer hook is required to display them: add to
  `assets/js/viewer-enhancements.js` a "Live device sample - <PID>" panel that reads
  `x-cisco-live-examples` and renders per-PID real data beside the synthetic example.
- Non-destructive: user sees BOTH the synthetic example and the real per-PID device data.
- Wire the injection into `build_release.py` (an overlay/merge step, `apply_example_overlay`-style)
  so it survives regeneration.
- **TODO:** re-align `scripts/harness/build_observed_examples.py` to emit `x-cisco-live-examples`
  (currently emits `examples["live-<pid>"]` + `x-cisco-observed`; §11.A.2 below is the older design,
  kept for reference but superseded by this decision).

> Deferred until we have scrubbed captures. **We start with ONE device.** So the
> plan is staged: 11.A is the single-device goal (review raw data easily + show
> real captured bodies inline in the OpenAPI examples, clearly labelled as real);
> 11.B is the later multi-PID scale-up (a switcher + coverage matrix). Design
> intent, not yet built.

### 11.A Single device first (the immediate goal)

**Goal:** (1) review the raw captured data with ease, (2) see that same real data
inside the OpenAPI `example`, (3) make it unmistakable that it came from a real
device (device / PID / os_version / timestamp), not a synthetic schema default.

#### 11.A.1 Reviewing raw data with ease
The collector already writes one self-describing JSON per path under
`scripts/harness/captures/<device>/<category>/<module>__<hash>.json`, each with
full provenance + the verbatim `response`. Three ways to review, cheapest first:
- **Direct:** open the capture file (or `jq .` it) — device, pid, http_status,
  fetched_at, path, and response are all right there.
- **Search:** `python -X utf8 -m scripts.harness.build_capture_index` then
  `find_value.py --value 633024` / `--keyword policer` to jump to the exact
  path+leaf that produced a value.
- **Browse (built):** `python -X utf8 -m scripts.harness.report` renders every
  capture into a single offline `scripts/harness/capture-report.html` (device ->
  category -> module -> path, status badge + collapsible response, live text
  filter). Local-only + gitignored; `--open` launches it in a browser.

#### 11.A.2 Showing it in the OpenAPI example, marked as REAL
Overlay the captured (redacted) GET response into each path's `200` response
example in the release specs, using OpenAPI 3.0's plural `examples` map so the
provenance is visible natively in Swagger UI (it renders the `summary` in a
dropdown — no custom JS needed to prove it's real):

```jsonc
// responses.200.content."application/yang-data+json"
"examples": {
  "live-C9300-48T": {        // keyed per PID; a 2nd device adds another entry
    "summary": "Real device capture - C9300-48T - IOS XE 26.1.1 - 2026-07-30",
    "description": "Verbatim RESTCONF GET response from a real Catalyst 9300, lightly redacted (secrets only). Not a synthetic schema default.",
    "value": { /* the captured response body */ }
  }
}
"x-cisco-observed": {          // machine-readable provenance next to the example
  "live-C9300-48T": {
    "source": "live-device",
    "device": "sw2", "pid": "C9300-48T",
    "os_version": "26.1.1", "http_status": 200,
    "fetched_at": "2026-07-30T...Z",
    "path": "/data/Cisco-IOS-XE-..."   // OpenAPI path only; NEVER the device IP
  }
}
```

- **What `x-cisco-observed` is:** an OpenAPI vendor extension (any `x-` field is
  allowed and ignored by tools that don't read it). It is a provenance stamp
  proving the sibling example is real captured data and giving an audit trail
  (which device/model/OS/date produced it). Keyed per PID to match the examples.
  It records the OpenAPI `path`, **never** `restconf_url`/`host` — those carry the
  device management IP and must not reach the public repo.
- **"Clearly real" in the UI:** the `summary`/`description` strings do the work in
  stock Swagger UI. Optionally add a tiny green "LIVE" badge via the existing
  viewer JS keyed off `x-cisco-observed` for a stronger visual (CSP-safe, reads
  local spec JSON only).
- **Where it goes:** GET `responses.200` example (today's injectors only fill
  POST/PUT/PATCH *request* bodies). This is additive to existing example content.
- **Guards in the overlay:** (1) a huge-default `--max-example-bytes` safety valve
  (default 5 MB, `0` = no cap) skips only a pathological runaway subtree; (2) a
  basic secret gate re-scans each redacted example with `secret_scan` and refuses
  (skips) any that still looks secret-bearing. Both are reported in the summary.
- **Counts stay safe:** injecting example content does NOT change path / operation
  / module counts, so the G-6 baseline (`release_counts.json`) does not trip.
  Bump `service-worker.js` `CACHE_VERSION` since a cached spec changed.
- **Build path:** `capture-index.json` (local) -> a new
  `scripts/harness/build_observed_examples.py` (BUILT) that overlays scrubbed
  bodies onto the release specs' GET 200 responses (mirrors the existing
  `scripts/apply_example_overlay.py` pattern in §3). Dry-run by default; `--write`
  applies in place. Re-runnable, idempotent, and keyed per PID so a second device
  just adds another `live-<pid>` example (the §11.B switcher, for free).
- **Run order:** run the overlay AFTER `scripts/build_release.py` — a spec rebuild
  regenerates the files and wipes injected examples. Re-run the overlay as a
  post-build step (see §12.4).
- **Safety:** only scrubbed, reviewed captures are ever committed; the overlay's
  secret gate is a backstop, not a substitute for the §6 secret-scan test over any
  committed spec carrying an `x-cisco-observed` example.

### 11.B Later: multiple PIDs (scale-up)
Once a second PID is captured (e.g. C9200 alongside C9300), the same path returns
DIFFERENT values per device, which a single inline example can't hold. At that
point move the per-PID values into an additive sidecar and add a switcher.

#### 11.B.1 Sidecar dataset (per release)
Keep the OpenAPI specs unchanged. Emit ONE additive, gitignored-until-scrubbed
JSON per release, derived from `capture-index.json`, keyed for O(1) browser lookup:

```
releases/26.1.1/device-observations.json
{
  "os_version": "26.1.1",
  "generated_at": "...",
  "pids": ["C9200-48P", "C9300-48T", "C9400", "C9500", "C9600", "C9300X-48HX"],
  "families": { "9200": ["C9200-48P"], "9300": ["C9300-48T", "C9300X-48HX"], ... },
  "paths": {
    "Cisco-IOS-XE-switch-dp-punt-inject-oper::/data/Cisco-IOS-XE-...:.../punt-inject-cpuq-brief-stats": {
      "category": "oper",
      "status_by_pid": { "C9200-48P": "200", "C9300-48T": "200", "C9400": "404" },
      "leaves": {
        ".../cpu-punt-queue-name": { "C9200-48P": "forus", "C9300-48T": "forus" },
        ".../pkts": { "C9200-48P": 633024, "C9300-48T": 41 }
      }
    }
  }
}
```

Why a sidecar (not inline `x-cisco-examples` in the spec):
- Specs stay byte-stable -> G-6 path/op/module count guard never trips.
- One fetch per release, lazy-loaded only on pages that need it (CSP-friendly,
  no inline data, service-worker `CACHE_VERSION` bump when it changes).
- Raw stays local; only the scrubbed, reviewed sidecar is ever committed.

### 11.B.2 How it surfaces in the UI (three additive touchpoints)
1. **PID value switcher on the Swagger viewer.** When an open operation's path has
   an entry in `device-observations.json`, add a small "Observed on: [9200][9300]
   [9400]..." control (built from `pids`/`families`). Selecting a PID swaps the
   *displayed* example body to that PID's captured values, with a "lab-captured,
   not schema default" badge. Default view = schema example (unchanged) so nothing
   regresses for paths we have no data for.
2. **Per-PID coverage matrix.** Extend platform-coverage.html (today: module x
   platform from NETCONF capabilities) with a second lens: module/path x PID ->
   `data` / `404` / `empty`, fed straight from `find_value.py --coverage`. This is
   the "which switches actually return this data" view.
3. **PID diff view.** For a chosen path, a compact table of leaf -> value-per-PID
   with differences highlighted (e.g. `pkts` differs across PIDs, queue-name set
   differs 9200 vs 9300). Reuses the existing tree-compare diff styling.

### 11.B.3 Aggregation rules across devices
- **Key on exact PID** in the data (`C9300-48T` vs `C9300X-48HX`), because models
  within a family genuinely differ; **group by family** ("9300") in the UI for
  browsing, drill down to exact model on demand.
- **Presence vs value:** a path is "covered" for a PID if any indexed row exists
  (200 with body). `404`/`empty` come from the raw capture `http_status`
  (`find_value.py` notes the index alone can't distinguish 404 from empty).
- **Collapse identical values:** if all PIDs share a value, show it once with an
  "all PIDs" tag; only split out where they diverge (keeps the diff signal clean).
- **Never merge across releases:** observations are per `os_version`; the release
  dropdown selects the matching sidecar.

### 11.B.4 Build path (when multi-PID starts)
`capture-index.json` (harness, local) -> a new `scripts/build_device_observations.py`
that scrubs + reshapes into `releases/<ver>/device-observations.json` -> new JS
(`assets/js/device-observations.js`) that the Swagger viewer + platform-coverage
page lazy-load. Gate additions: extend G-6 baseline only for the new sidecar (its
own count), keep spec counts untouched; add a secret-scan test over the committed
sidecar (mirrors §6).

## 12. How collection works (design decisions)
The exact, code-grounded behaviour of the GET phase. These are the decisions to
carry into any write-up.

### 12.1 Collection order (deterministic)
The plan is built by `spec_paths.enumerate_get_paths` and is fully deterministic:
1. **Category order (fixed):** `oper` -> `mib` -> `cfg` -> `native-config`
   (`GET_CATEGORIES`). rpc is POST-only and excluded.
2. **Module order:** within a category, follows that category's
   `api/manifest.json` order; falls back to sorted filenames if no manifest
   (`_module_names`).
3. **Path order:** within a module, the spec JSON's own `paths` key order,
   filtered by `_is_capturable`.

So the plan is: every oper module (manifest order) -> each of its paths (spec
order) -> then mib -> cfg -> native-config.

**Wire order caveat:** per device, `collector.capture_device` submits that plan to
a thread pool (default `--concurrency 6`) and drains via `as_completed`, so
requests *start* in plan order but *complete* out of order. Devices are processed
strictly one at a time (finish a device before starting the next). This affects
only interleaving, never which paths are collected.

### 12.2 Redundancy: exhaustive vs roots-only (the main lever)
RESTCONF GETs are issued with **no `depth`/`fields`/`content` query params**
(`request.build_restconf_url` appends the path verbatim), so every GET returns
the **entire subtree** below the target.

- **Exhaustive (default):** GET every non-keyed path at every depth. Because a
  parent-container GET already contains all descendant data, and we then GET each
  descendant again, the same leaf value is returned by the module root, by each
  intermediate container, and by its own leaf path -> **heavy, intentional
  redundancy**. Cost ~= `~22,144 oper + ~4,272 mib (+ cfg/native)` GETs *per
  device* x 6 devices. The index does NOT dedupe, so one value yields multiple
  rows. Value of this mode: authoritative **per-path** 200/404/empty status.
- **Roots-only (`--roots-only`):** keep only the shortest keyless path per module
  (`min(capturable, key=len)`) -> one GET per module root; the whole subtree comes
  back in that one response. **Near-zero redundancy**, far fewer requests. Cost of
  this mode: you lose per-path status (you only asked the root).

**Decision / guidance:** roots-only for the broad sweep (speed, minimal dupes);
exhaustive only where per-path coverage matters (e.g. the per-PID coverage
matrix). For the pilot: exhaustive on the single pilot module to prove behaviour,
then roots-only to scale.

### 12.3 YANG lists and keyed-lists (completeness)
- **Keyed element paths are skipped.** `_is_capturable` returns `False` for any
  path containing `={` (a list-key placeholder like `interface={name}`), because
  we hold no concrete key values to substitute.
- **List data is still captured completely** via the keyless ancestor. A GET on
  the containing container/list (e.g. `/data/...:interfaces`) returns **every list
  entry with all keys and full sub-trees** (no depth limit). So we get all entries
  from the parent GET rather than N per-key GETs.
- **Edge case:** if a module exposes *only* keyed paths (no keyless ancestor), it
  yields zero capturable paths and is silently skipped. Rare (the module root
  container is normally keyless) but worth a pilot spot-check.

**Net:** every list entry is collected completely, keyed or not, provided a
keyless ancestor path exists; the harness never enumerates keys itself.

### 12.4 Other collection semantics
- **Empty / non-JSON / 204:** returned as `empty=True` (not an error); still
  written so absence is recorded.
- **Retries:** transient 5xx and timeouts retry with exponential backoff
  (`retries=2`); other statuses are recorded as-is.
- **Resume:** existing capture files are skipped unless `--no-resume`, so a run is
  interruptible and re-runnable.
- **Redaction on write:** every response is light-redacted (`redact.redact`)
  before it touches disk; raw stays local + gitignored.
- **Overlay runs AFTER build:** `build_observed_examples.py` edits the generated
  release specs, so a later `scripts/build_release.py` run wipes injected
  examples. Always run the overlay as a post-build step (build -> overlay ->
  bump `CACHE_VERSION`), and re-run it after any spec regeneration.
- **Provenance excludes the IP:** the overlay records the OpenAPI `path` in
  `x-cisco-observed`, never `restconf_url`/`host`. Captures on disk still contain
  `host`/`restconf_url` (local only); only the scrubbed example reaches a commit.

## 13. Web-app documentation copy (what to publish)
Ready-to-adapt text for the site's own docs (about.html / changelog.html /
APP_MAP) explaining the real-device-data feature to end users. Keep it factual;
do not imply live querying — the site stays static.

### 13.1 Short blurb (about / feature card)
> **Real device data in examples.** Selected RESTCONF operations now show a
> response captured verbatim from a real Catalyst 9000 switch running IOS XE
> 26.1.1 — not a synthetic schema default. These examples are labelled "Real
> device capture" with the device model (PID), OS version, and capture date, and
> carry machine-readable `x-cisco-observed` provenance in the spec. Secrets are
> redacted; the data is read-only and captured offline (the site itself never
> contacts a device).

### 13.2 How it was produced (methodology note)
> Data was collected by a read-only harness that issues RESTCONF **GET requests
> only** (writes are structurally impossible in this phase). It enumerates GET
> paths from the published OpenAPI specs across the oper, mib, cfg, and
> native-config categories, captures each device's raw response locally, and
> overlays the successful (HTTP 200) responses into the corresponding operation's
> example. Multiple device models produce multiple labelled examples
> (`live-<PID>`) on the same path, selectable from Swagger UI's examples dropdown.

### 13.3 Coverage / caveats to state plainly
- Examples reflect **one lab capture** per model at a point in time; counters and
  operational values are snapshots, not live.
- A path may have data on some models and return 404/empty on others; the
  per-model coverage view (planned) shows which models return each path.
- Keyed-list entries appear inside their parent container's captured response;
  the site does not fabricate list keys.
- Provenance for every real example is in the spec under `x-cisco-observed`
  (source, device, pid, os_version, http_status, fetched_at, path). The device
  management IP / restconf_url is deliberately excluded.

### 13.4 Where each decision is documented
- Collection order, redundancy modes, list/keyed-list handling: this file, §12.
- Example-injection representation + provenance shape: §11.A.2.
- Multi-PID representation (switcher / coverage / diff): §11.B.
- Safety / redaction / secret-scan: §6.

### 13.5 Assurance touchpoints when this ships to the site (per ASSURANCE_SPEC.md)
- Injecting example content does **not** change path/operation/module counts ->
  the **G-6** baseline (`release_counts.json`) is unaffected.
- Bump `service-worker.js` `CACHE_VERSION` (cached spec content changed).
- Keep hub-page CSP strict; the real-data example content is spec JSON, not
  inline script.
- Add a secret-scan test over any committed spec carrying an `x-cisco-observed`
  example (mirrors §6).
