# AGENTS.md — AI Agent Guide

> Guidance for AI coding agents (GitHub Copilot, Claude, Cursor, etc.) working in this repository.
> Follows the [agents.md](https://agents.md) convention.

This file describes **how to work in this codebase safely and productively**. Read it before making changes.

---

## 0. Source-of-truth docs (read these first)

When making non-trivial changes, the following documents are authoritative. Update them when behavior changes; do not duplicate their content elsewhere.

| Doc | Authoritative for |
|-----|-------------------|
| [ASSURANCE_SPEC.md](ASSURANCE_SPEC.md) | **Required post-change validation.** Run the gates / smoke / data / security checks defined there and append the final assurance report to your reply **before declaring work complete**. |
| [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) | High-level scope, model categories, accountability rules |
| [VERSIONING.md](VERSIONING.md) | Multi-release folder layout, URL contract, CI gates, "add a new release" runbook |
| [MDT_XPATH_SPEC.md](MDT_XPATH_SPEC.md) | MDT/gRPC dial-out filter xpath rule + OpenAPI extensions |
| [../MIBS.md](../MIBS.md) | MIB coverage and platform applicability matrix |
| [../telemetry-reference.md](../telemetry-reference.md) | Per-feature telemetry subscription metadata (feature → xpath, tier, cadence) |
| [CHANGELOG.md](CHANGELOG.md) | Versions Supported table; release-by-release deltas |

If a request conflicts with these docs, prefer updating the doc first (with rationale) and then code.

---

## 1. Project Overview

**What this is:** A static documentation site for **Cisco IOS-XE RESTCONF APIs across multiple releases (17.9.x, 17.12.x, 17.15.x, 17.18.1, 26.1.1)**, generated from upstream YANG modules. Hosted on GitHub Pages — no backend, no build step at runtime. Per-release artifacts live under `releases/<ver>/`; shared UI lives at the repo root and reads the active release based on the `#ver=` URL hash. See [VERSIONING.md](VERSIONING.md) for the full layout.

**What ships:**

- 608 OpenAPI 3.0 specs in the default 26.1.1 release (`releases/26.1.1/swagger-*-model/api/*.json`); 506\u2013608 across the five tracked releases. See [version-stats.json](version-stats.json) for per-release counts.
- 765 YANG tree HTML visualizations per release (`releases/<ver>/yang-trees/`)
- 6 vanilla-JS pages (index, code generator, tree compare, accountability, plus 9 model index pages)
- A per-release search index (`releases/<ver>/search-index.json`) consumed by Fuse.js fuzzy search

**What this is NOT:**

- A SaaS app (no users, no auth, no DB, no API)
- A library or package (nothing is `npm install`-able)
- Real-time (specs are pre-generated; the live site is read-only)

---

## 2. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Hosting | GitHub Pages | `.github/workflows/deploy-pages.yml` |
| Frontend | Vanilla HTML/CSS/JS (no framework) | All inline scripts have been extracted to external `.js` for CSP |
| Search | [Fuse.js 7.0.0](https://www.fusejs.io/) | Fuzzy search via CDN |
| Charts | [Chart.js 4.4.0](https://www.chartjs.org/) | CDN |
| API viewer | [Swagger UI 5.31.0](https://github.com/swagger-api/swagger-ui) | CDN |
| Generators | Python 3.8+ with [pyang](https://github.com/mbj4668/pyang) | YANG → OpenAPI |
| YANG sources | [YangModels/yang vendor/cisco/xe/17181](https://github.com/YangModels/yang) | 848 files in `references/17181-YANG-modules/` |

---

## 3. Repository Layout

```text
cisco-ios-xe-openapi-swagger/
├── index.html                  # Main landing / search
├── code-generator.html         # Snippet generator (Python/curl/Go/etc.)
├── tree-compare.html           # YANG tree diff tool
├── yang-accountability.html    # Module coverage report
├── 404.html                    # GitHub Pages 404 fallback
│
├── index-app.js                # Main page controller
├── search.js                   # Fuse.js search + deep-linking
├── code-generator.js           # Snippet generation logic
├── tree-compare.js             # Tree comparison logic
├── yang-accountability.js      # Accountability report renderer
├── recent-favorites.js         # localStorage-backed favorites
│
├── search-index.json           # Fuse.js search source (~780 modules)
├── yang_accountability.json    # Module-by-module coverage data
│
├── swagger-{type}-model/       # 9 model categories (see §4)
│   ├── index.html           # Model browser with deep-linking
│   ├── api/*.json           # OpenAPI specs (deep paths)
│   └── api/*.json              # Legacy v1 specs (kept as fallback)
│
├── yang-trees/                 # 768 generated YANG/MIB tree HTML files
├── references/17181-YANG-modules/  # 848 source YANG files (excluded from Pages deploy)
│
├── generators/                 # 27 Python YANG → OpenAPI generators
│   ├── generate_{type}_from_tree.py     # Tree-based deep-path generators
│   ├── generate_{type}_openapi_v2.py    # Wrappers / orchestrators
│   └── generate_combined_{type}.py      # Per-category combined specs
│
├── scripts/                    # 67 Python post-processing/audit tools
│   ├── enrich_v2_specs.py              # Realistic example values + descriptions
│   ├── validate_examples_c9kv.py       # Live device validation (C9KV)
│   ├── generate_search_index.py        # Build search-index.json
│   ├── generate_pyang_trees.py         # Build yang-trees/*.html
│   ├── prepare_github_pages.py         # Stage deploy directory
│   └── audit_*.py / analyze_*.py       # Coverage/quality auditors
│
├── tools/                      # Postman collection + environment
├── docs/                       # GETTING_STARTED.md, PROJECT_SUMMARY.md
└── archive/                    # Completed phase docs (read-only)
```

---

## 4. The 9 Model Categories

| Directory | Type | Specs | Purpose |
|---|---|---|---|
| `swagger-oper-model/` | operational | 205 | Read-only state/statistics (GET) |
| `swagger-cfg-model/` | configuration | 39 | Feature config (full CRUD) |
| `swagger-native-config-model/` | native | 159 | Full CLI-equivalent config (full CRUD). Composed of one spec per top-level functional area plus 8 augment-resolved router protocol buckets (bgp/eigrp/isis/lisp/lisp-list/nhrp/ospf/rip), augment-resolved placeholder specs, root-augment specs for sibling-module additions (kron, maintenance-template, voice/switch/aaa subtrees, …), and a completeness-sweep safety net — see [§6 Native YANG augments & placeholders](#native-yang-augments--placeholders-critical). |
| `swagger-openconfig-model/` | openconfig | 57 | Vendor-neutral standards |
| `swagger-ietf-model/` | ietf | 19 | RFC-compliant IETF models |
| `swagger-mib-model/` | mib | 149 | SNMP MIB → YANG translations (GET) |
| `swagger-rpc-model/` | rpc | 59 | RPC/action endpoints (POST `/operations/`) |
| `swagger-events-model/` | events | 38 | YANG-Push notifications + SNMP traps |
| `swagger-other-model/` | other | 10 | Standalone / vendor-specific |

Each directory ships an `index.html` with hash-based deep-linking (`#spec=<module-name>`).

---

## 5. Build & Run

### Run locally (preview the site)

```powershell
cd cisco-ios-xe-openapi-swagger
python -m http.server 8000
# Open http://localhost:8000
```

### Regenerate everything (full pipeline)

The supported pipeline is **per-release** and orchestrated by `scripts/build_release.py`. Do not invoke individual generators ad-hoc unless you are iterating on the generator itself — the orchestrator runs them in dependency order and writes manifests, search index, telemetry index, MIB metadata, native capabilities, and Postman/Bruno exports atomically.

```powershell
# Build a single release (all model categories + trees + manifests + exports)
python scripts/build_release.py --version 26.1.1

# Build all registered releases (matrix)
python scripts/build_all_releases.py
```

To add a new IOS-XE release, follow the runbook in [VERSIONING.md §8](VERSIONING.md#8-adding-a-new-release--runbook). Do not hand-edit per-release artifacts.

If you must invoke a single generator directly (debugging only), pass `--version <ver>` so it writes into `releases/<ver>/`:

```powershell
cd generators
python generate_oper_openapi_v2.py --version 26.1.1
python generate_native_openapi_v2.py --version 26.1.1
# etc.
```

Post-processing scripts (`scripts/enrich_v2_specs.py`, `scripts/add_yang_github_links.py`, `scripts/annotate_mdt_xpaths.py`, `scripts/enrich_mib_metadata.py`, `scripts/build_native_capabilities.py`, `scripts/generate_search_index.py`, `scripts/generate_all_pyang_trees.py`, `scripts/generate_postman_collection.py`, `scripts/generate_bruno_collection.py`) all take `--version` and are run by `build_release.py`. Run them individually only when iterating on that step.

### Site-wide post-build steps

After adding a new release or rebuilding manifests/viewers, run:

```powershell
# Normalize all manifest.json files (default + per-release) to the schema viewers expect.
python scripts/normalize_manifests.py

# Re-patch all 9 swagger-*-model/index.html viewers with version-aware helpers
# (reads default + active-versions allow-list from releases/index.json).
python scripts/patch_viewers_version_aware.py

# Build the YANG module -> prefix map per release. Required by the
# Module XPath Builder in telemetry.html. Re-run whenever YANG sources
# change for any release.
python scripts/build_yang_prefix_map.py

# Local schema unit tests (also runs in CI via .github/workflows/tests.yml).
python -X utf8 -m pytest tests/ -v

# Headless smoke test against the live deployment.
python scripts/smoke_live.py
# Or against a staging URL:
python scripts/smoke_live.py --base-url https://example.com/staging
```

### Validate examples against a live device

```powershell
python scripts/validate_examples_c9kv.py --host 10.1.1.1 --username admin --password Cisco123 --patch-only --dry-run
```

---

## 6. Conventions & Rules

### Python (generators + scripts)

- **Python 3.8+**, standard library only where possible (pyang is the only required external)
- Files use 4-space indentation, `snake_case` names
- Each top-level script accepts `--help` and uses `argparse` when it has options
- Generators write JSON with `indent=2` and a trailing newline
- **Do not edit generated specs by hand.** Modify the relevant generator in `generators/` or post-processor in `scripts/` and re-run

### RESTCONF request/response body schemas (CRITICAL)

All `requestBody` and `responses['200'].content['application/yang-data+json']` payloads MUST be wrapped objects matching RESTCONF wire format — never bare scalars or arrays. For a leaf `hostname` in `Cisco-IOS-XE-native`, the schema and example are both:

```json
{ "type": "object",
  "properties": { "Cisco-IOS-XE-native:hostname": { "type": "string" } } }
```

Swagger UI's "Try it out" pre-fills the body from the **schema**, not the media-type-level `example`, so a bare `{"type":"string"}` leaves the editor blank and the request fails on the device. The 8 `generate_*_from_tree.py` generators (cfg, events, ietf, mib, native, openconfig, oper, other) wrap the schema with `wrapper_key = "<module>:<node>"` immediately after computing the inner schema, and `scripts/wrap_body_schemas.py` (invoked from `build_release.py` after `apply_example_overlay`) enforces the invariant across the legacy v2 generators (`generate_*_openapi_v2.py`) and every release by deriving the wrap key from the URL path when no namespaced example is present. The live invariant is "0 PUT/PATCH/POST bodies whose schema is not `{type:object, properties:{<module>:<leaf>: ...}}`" across all 5 releases and all 9 viewers (currently 0 / 97,208).

### Native YANG augments & placeholders (CRITICAL)

`Cisco-IOS-XE-native.yang` is **not** a self-contained module. Several of its top-level containers are declared as bodyless placeholders, e.g.

```yang
container router;
container xconnect;
container route-tag;
container l2vpn-config;
```

Their real schema lives in **augment statements inside sibling modules** that import native and write into these placeholders:

| Placeholder | Augmenting modules (26.1.1 example) | Generated specs |
|---|---|---|
| `/native/router` | `Cisco-IOS-XE-bgp`, `-ospf`, `-eigrp`, `-isis`, `-lisp`, `-nhrp`, `-rip` (29 augments, 9 modules) | `native-router-bgp.json`, `native-router-ospf.json`, `native-router-eigrp.json`, `native-router-isis.json`, `native-router-lisp.json`, `native-router-lisp-list.json`, `native-router-nhrp.json`, `native-router-rip.json` + slim `native-router.json` index |
| `/native/xconnect` | `Cisco-IOS-XE-l2vpn` | `native-xconnect.json` |
| `/native/route-tag` | `Cisco-IOS-XE-eigrp` | `native-route-tag.json` |
| `/native/l2vpn-config` | `Cisco-IOS-XE-l2vpn` | `native-l2vpn-config.json` |

Augment bodies typically reference `uses <grouping-name>;` instead of inlining the schema, so resolution requires a **cross-module grouping index** built from every `.yang` file in the release.

**Historical bug:** [generators/generate_native_openapi_v2.py](generators/generate_native_openapi_v2.py) only parses `Cisco-IOS-XE-native.yang` and uses a regex that requires `container <name> {` (body) — silently dropping `container router;` (bodyless placeholder). For multiple releases this hid the entire BGP/OSPF/EIGRP/ISIS/LISP/NHRP/RIP/xconnect config tree from the viewer.

**Fixed in the pipeline:**

1. [scripts/generate_native_augment_specs.py](scripts/generate_native_augment_specs.py) runs immediately after `native-specs`. It scans every YANG module for `augment "/<pref>:native/<pref>:<placeholder>"`, builds a cross-module grouping index, walks each augment body (recursively expanding `uses` intra- and cross-module), and emits one OpenAPI 3.0 spec per placeholder. The `/native/router` subtree is split into per-protocol buckets via the `_ROUTER_BUCKETS` map to stay under the legacy ~6 MB per-spec ceiling.
2. [scripts/check_native_coverage.py](scripts/check_native_coverage.py) is a **fatal** build-time guard. It enumerates every top-level container/list/leaf declared in `container native { ... }` of the YANG source (resolving `uses` inside the native module) and verifies every name appears in some `/data/Cisco-IOS-XE-native:native/<name>` path across the split specs. Failure stops `scripts/build_release.py`.

**Known remaining edge case — native-root augments (RESOLVED):** Modules can also augment the `/native` root directly (`augment "/ios:native" { uses some-grouping; }`) to add brand-new top-level children. This affects 67 sibling modules across 113 distinct top-level children (kron, maintenance-template, voice, switch, security/login/password, scada-gw, zone, zone-pair, etc.). The augment-spec generator now handles this class too: it discovers root augments via `find_native_root_augments`, walks their bodies (expanding `uses` cross-module and tolerating `uses NAME { refinement }` blocks), and emits a `native-<child>.json` per added child — including stub specs for leaf-only additions like `pae`. The coverage guard's `root_augment_added_children` mirrors this discovery so any new sibling-module augment will be enforced.

**Completeness sweep:** A final pass in `generate_native_augment_specs.py` (`_parse_native_top_children` + `_covered_top_names`) emits a `native-<child>.json` for any top-level container declared in `Cisco-IOS-XE-native.yang` itself that the v2 generator silently dropped (historical examples: `dot1x`, `identity`, `login`, `object-group`, `password`, `scada-gw`, `zone`, `zone-pair`). This is the safety net that makes the coverage guard achievable for every release.

**Coverage today (post-fix, all 5 releases):**

| Release | Top-level /native children | Native spec files | Total paths | Operations |
|---|---:|---:|---:|---:|
| 17.9.x  | 233 / 233 ✅ | 129 | 9,059  | 36,236 |
| 17.12.x | 237 / 237 ✅ | 133 | 9,169  | 36,676 |
| 17.15.x | 256 / 256 ✅ | 152 | 9,635  | 38,540 |
| 17.18.1 | 258 / 258 ✅ | 153 | 9,871  | 39,484 |
| 26.1.1  | 264 / 264 ✅ | 159 | 10,417 | 41,668 |

**Rules when touching the native pipeline:**

- Do **not** assume native = one module. Always think in terms of (native YANG + augmenting sibling YANG + groupings).
- Do **not** rely on the v2 native generator for anything inside the 4 placeholders — its output is empty there by design. The augment-resolver owns those subtrees.
- Do **not** delete `native-router.json` even though it only contains the placeholder root path; it is the index that lets the guard map the router subtree back to a single covered name.
- When adding a new placeholder-style container to `Cisco-IOS-XE-native.yang`, add its name to `PLACEHOLDERS` in `generate_native_augment_specs.py` and (if router-sized) extend `_ROUTER_BUCKETS`.
- When adding a new module that augments `/native` root, extend the generator to handle root augments and add to `_ROUTER_BUCKETS` / a new bucket map. Document it in this section.

### Canonical demo target: DevNet Always-On C9K sandbox

Every spec MUST point Swagger UI's "Execute" at the public Cisco DevNet Always-On Catalyst 9000v sandbox so the demo can actually be tried without a private device. Canonical values, enforced by `scripts/wrap_body_schemas.py`:

| Setting | Value | Notes |
|---|---|---|
| `servers[*].variables.device.default` | `devnetsandboxiosxec9k.cisco.com` | Public hostname (RESTCONF 443, NETCONF 830, gNMI 9339, SSH 22). Catalog: https://devnetsandbox.cisco.com/DevNet/catalog/Cat9k-Always-On_cat9k-always-on |
| `Cisco-IOS-XE-native:hostname` example body value | `devnetsandboxiosxec9k` | Short form (no domain) — matches the device's own `hostname` config. |
| `index.html` + `code-generator.html` device-IP inputs | `devnetsandboxiosxec9k.cisco.com` | Default + placeholder so copy/paste-able snippets target the sandbox. |

Never introduce `router.example.com`, `sandbox-iosxe-latest-1.cisco.com`, `192.168.1.1`, `10.0.0.1`, `DC1-CORE-SW01`, `rtr-edge-01`, or any other placeholder for these fields — the post-processor will rewrite them but the source-of-truth in `generators/` and `scripts/` must already be correct.

### Example data generation (realistic Try-It-Out bodies)

Example values for generated specs come from a layered lookup in `example_for_type(yang_type, name)`:

1. **Demo-polish overrides** — only `generate_native_from_tree.py` and `generate_oper_from_tree.py` carry name-keyed dicts (`EXAMPLE_VALUES` / `OPER_EXAMPLE_VALUES`) for common leaves: `hostname → "devnetsandboxiosxec9k"`, `address → "10.10.10.1"`, `vlan → 100`, `community → "RO_SNMP_v2c"`, `area → "0.0.0.0"`, `as-number → 65001`, etc. Add new overrides here when a particular demo path needs a more meaningful value than the YANG default.
2. **YANG-derived defaults / enums** — all 9 `generate_*_from_tree.py` generators call `yang_value_index.lookup_example(name)` (built once per process from `references/17181-YANG-modules/*.yang`). The index scans every `leaf` and `typedef`, records `default "X";` statements and `enum X;` lists, and **only returns a value when every YANG leaf with that name agrees** (unanimous default or unanimous first enum). Conflicting same-name leaves return `None` so we never substitute a wrong default into an unrelated path.
3. **Type-based fallback** — `string → "example"`, `boolean → true`, `uint* → 1`, `enumeration → "default"`, `union → "auto"`, `empty → null` (presence). Used when neither override nor YANG index resolves the name.

The current state of generated example bodies after this pipeline, **per release surface** (request + response examples across all 8 viewers; the same counts apply to each of the 5 tracked releases once that release is re-built):

| Viewer | Example bodies | Generic `"example"` placeholder |
|--------|---------------:|--------------------------------:|
| cfg            |  6,965 | 31.3% |
| events         |    861 | 64.7% |
| ietf           |    928 | 51.5% |
| mib            | 12,482 | 74.5% |
| native-config  | 10,089 | 16.3% |
| openconfig     |  4,739 | 54.9% |
| oper           | 21,507 | 20.7% |
| other          |  3,520 | 39.5% |
| **Total**      | **61,091** | **37.0%** |

> Scope caveat: example-data realism counts above are for the **top-level (default 26.1.1) viewer surface**. The four other tracked releases (`releases/17.9.x/`, `releases/17.12.x/`, `releases/17.15.x/`, `releases/17.18.1/`) carry roughly comparable example-body volumes per release. Of the 9 from-tree generators, 7 (`native`, `ietf`, `mib`, `openconfig`, `events`, `other`, `rpc`) hardcode the top-level `yang-trees/` input path and only re-emit examples for the default surface; only `cfg` and `oper` accept `--version` and re-emit per-release. To roll the same example-data layering across all 5 releases, re-run `scripts/build_release.py --version <ver>` for each release rather than the individual generators.
>
> **Wire-correctness (schema wrap) is enforced across all 5 releases**, however: the `scripts/wrap_body_schemas.py` post-processor runs as part of every `build_release.py` invocation (and can be run ad-hoc with `--all-releases`). It walks every `application/yang-data+json` requestBody and response, and wraps any unwrapped schema (and synthesises a wrapper for bare-scalar / list / empty-dict / multi-key-non-namespaced examples) under the RESTCONF-namespaced key derived from the URL path. After the post-processor: **0 / 97,208 PUT/PATCH/POST bodies remain unwrapped across all 5 releases and all 9 viewers** (audit: any body where `schema.type != "object"` or no `properties` key contains `":"`).

When improving coverage:
- **Prefer extending the YANG index** (it benefits all 9 generators at once) over per-generator overrides.
- **For ambiguous names** (e.g. `mode`, `type`, `name`), do NOT add to overrides — pick the right value via the YANG index by passing path context, or accept the placeholder. A wrong realistic-looking value is worse than an obvious placeholder.
- After changing the index or overrides, regenerate the affected viewers and re-run the audit one-liner in `tmp/` to verify the realistic-value percentage didn't regress.

### Frontend JS

- **Vanilla ES6** — no bundler, no transpiler, no `npm install`
- **No inline scripts or `onclick=` handlers** in HTML (CSP requires external `.js` files)
- Wrap files in IIFE (`(function () { ... })();`) where possible
- Always escape user-influenced strings before `innerHTML` — see `escapeHtml()` in [search.js](search.js)
- Use `localStorage` defensively (private mode and quota errors throw — wrap in `try/catch` and surface via `showToast()`)
- Hash-based deep-linking is the convention (`#spec=...`, `#search=...`, `#module=...`)

### HTML

- Strict CSP is enforced (`script-src 'self' cdn.jsdelivr.net`)
- Adding new third-party scripts requires updating the CSP `meta` tag
- All pages must work without JS for basic content (progressive enhancement)

### No emoji in UI or docs

This is a developer-facing technical reference, not a marketing site. Decorative
emoji (e.g. globes, rockets, stars-of-wonder, charts, clipboards, fire, etc.)
look like AI slop and frequently render as mojibake on consoles or older
browsers. Do **not** add emoji to:

- HTML files (landing page, viewers, code generator, accountability pages)
- JS files (toast messages, placeholder text, badges, search results)
- Markdown docs at the repo root (`README.md`, `AGENTS.md`, `CHANGELOG.md`,
  `QUICK_REFERENCE.md`, `PROJECT_REQUIREMENTS.md`, etc.)

**Banned ranges:** `U+1F000-1FAFF`, `U+2600-27BF`, `U+2300-23FF`, `U+2B00-2BFF`
(plus `U+FE0F` variation selector when attached to those code points).

**Exempt (functional monochrome glyphs the UI needs):**

- `U+2605` BLACK STAR / `U+2606` WHITE STAR — favorites toggle
- `U+2713` CHECK MARK — copy-to-clipboard confirmation
- `U+2715` MULTIPLICATION X — close button

If you find decorative emoji creeping back in, run
`python -X utf8 scripts/strip_emoji.py .` from the repo root to remove them.

### Git & deploy

**Two remotes — dev (default) and prod (manual promotion):**

| Remote | URL | Role |
|--------|-----|------|
| `dev`  | `https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger` | Default working remote. Local `main` tracks `dev/main`. Push here freely. |
| `prod` | `https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger` | Public/official Cisco DevNet copy. Push here only on deliberate promotion (releases, milestones). |

Day-to-day workflow:

```bash
git push                # pushes to dev (tracked upstream)
# ...iterate freely on dev...
git push prod main      # promote to CiscoDevNet when ready
```

- Push to `main` on **either** remote → that remote's GitHub Actions deploys to its own Pages site
- Generated artifacts (specs, trees, search index) **are committed** — keeps the deploy reproducible without running Python in CI
- Don't commit large debugging/exploration files; use `archive/` for completed-phase docs
- Never `git push --force prod` without explicit user confirmation; prefer `--force-with-lease` and verify the remote SHA you're overwriting

---

## 7. Common Tasks

### "Add a realistic example for field X"

Edit [scripts/enrich_v2_specs.py](scripts/enrich_v2_specs.py):

- Add to `get_example_for_field()` if it's a leaf-level field name → value mapping
- Add to `CONTAINER_FILL` if it's a YANG container that should produce a structured example
- Add to `_build_example_from_path()` if it's a path-based heuristic (e.g., VLAN, BGP, OSPF templates)
- Re-run: `python scripts/enrich_v2_specs.py`
- Verify: `python -m http.server 8000` and load the spec in Swagger UI

### "Add support for a new YANG module"

1. Place the `.yang` file in `references/17181-YANG-modules/`
2. Re-run the matching generator (e.g., `generators/generate_native_from_tree.py`)
3. Re-run `scripts/enrich_v2_specs.py` and `scripts/generate_search_index.py`

### "Update the search index"

```powershell
python scripts/generate_search_index.py
```

This rebuilds `search-index.json` from the `swagger-*-model/api/manifest.json` files.

### "Fix a broken deep-link"

The main `index.html` reads `#search=`, `#module=`, `#spec=` from the URL hash via `handleDeepLink()` in [search.js](search.js). Module pages read `#spec=<name>` via `checkHash()` in their `index.html`.

### "Validate write-operation examples against C9KV"

```powershell
python scripts/validate_examples_c9kv.py --host <ip> --username <u> --password <p> --spec native-switching.json --patch-only
```

---

## 8. Pitfalls — Read Before Editing

### Specs and Search Index Drift

`search-index.json` is generated from spec manifests. **If you edit specs directly without regenerating the search index, the site will look stale.** Always re-run `scripts/generate_search_index.py` after spec changes.

### Spec Files Are Generated

Direct edits to `swagger-*-model/api/*.json` will be **overwritten** the next time generators or `enrich_v2_specs.py` run. Make changes in the relevant Python file instead.

### CSP Will Block New CDN Scripts

The CSP `meta` tag in each HTML page restricts script sources. Adding a new external library (e.g., `unpkg.com`) requires updating CSP in **every** HTML file that uses it. Prefer `cdn.jsdelivr.net` (already allowlisted).

### Inline Scripts Have Been Extracted

Don't reintroduce inline `<script>` blocks or `onclick="..."` attributes — they violate CSP. The 4 main pages were refactored to externalize all JS. See [index-app.js](index-app.js), [code-generator.js](code-generator.js), [tree-compare.js](tree-compare.js), [yang-accountability.js](yang-accountability.js).

### MIB Specs Have Validation Issues

149 MIB specs are auto-converted from SNMP MIBs. Some don't validate cleanly — this is **expected and documented**. Don't try to "fix" them by hand-editing JSON. They're reference-only; production code should use Operational/Native/Config/RPC models.

### YANG Empty Leaves & Presence Containers

In RFC 7951 RESTCONF JSON, an empty YANG leaf is `[null]` (an array containing null), **not** `null` or `{}`. The enrichment script uses `[null]` for YANG presence containers it can't otherwise fill. Don't replace these with `{}` — devices will reject the request.

### "Empty" Examples Used to Be a Real Bug

Earlier versions had `{"Cisco-IOS-XE-native:vlan": {}}` examples that broke device updates. The fix lives in `scripts/enrich_v2_specs.py` (`build_example_from_schema()`, `_build_example_from_path()`, `_populate_empty_example()`). If you see `{}` come back in examples, the fix has regressed.

### Shared YANG parser — all v2 generators (fixed 2026-06-15, expanded 2026-06-16)

All active v2 generators — `generate_native_openapi_v2.py`, `generate_openconfig_openapi_v2.py`, `generate_ietf_openapi_v2.py`, `generate_mib_openapi_v2.py`, `generate_other_openapi_v2.py`, `generate_rpc_openapi_v2.py` — import the shared helper module [generators/_yang_parse.py](generators/_yang_parse.py). Never re-implement these primitives inline.

Public API exposed by `_yang_parse.py`:

- `find_balanced_braces(content, brace_start)` — matched-brace scanner that respects YANG string literals and `//` / `/* */` comments.
- `iter_top_level_blocks(content, keyword)` — yields `(name, body)` for every `<keyword> <name> { ... }` at brace-depth 0. Works for `grouping`, `container`, `list`, `leaf`, `leaf-list`, `choice`, `case`, etc.
- `iter_top_level_uses(content)` — yields each `uses <grouping-name>;` at depth 0.
- `resolve_includes(yang_file, content)` — recursively follows YANG `include <submodule>;` statements and **injects each submodule body inside the parent module's `{ ... }` wrapper** so the inlined groupings sit at the same brace depth as the parent's own definitions. Tracks `seen` to break circular includes.
- `is_submodule(content)` — `True` when the file starts with `submodule X { ... }`. Generators must early-return on this so submodules are not emitted as standalone specs (`analyze_yang_accountability_v2.py` records `reason_excluded="Submodule of <parent> - included in parent spec"`).

Both `iter_top_level_blocks` and `iter_top_level_uses` automatically call `_unwrap_module(content)` first, so callers may pass whole-file YANG content **or** an already-extracted block body and get the same result.

Three rules future edits must preserve:

1. **`include <submodule>;` must be resolved before parsing.** Without `resolve_includes()` inlining the submodule body, `extract_groupings()` returns nothing and the request schema collapses to `{}`. This silently affected `rpc:crypto` (pki import/export/enroll/authenticate/benchmark/crl/certificate/server), `rpc:clear` (aaa/arp/bgp/dhcp/ospf/platform) and `rpc:debug` (platform/crypto) for years, and analogously affected openconfig, native, ietf groupings.
2. **All keyword scanners (`leaf` / `leaf-list` / `container` / `list` / `choice` / `case` / `uses`) must respect brace depth.** A naive `re.search(r'\bleaf\s+(\S+)\s*\{')` will match leaves nested arbitrarily deep and hoist them into the parent schema. Use `iter_top_level_blocks` / `iter_top_level_uses`.
3. **`parse_container_or_grouping` must enumerate `list` blocks**, not just `container` blocks. A container whose only child is a YANG `list` (very common in IETF modules — `container interfaces { list interface { ... } }`) will produce an empty PUT body if you forget the list scanner.

After the 2026-06-16 rollout, post-fix empty-body counts (POST/PUT/PATCH whose body is just `{"<module>:<name>": {"type":"object"}}`): rpc 261→43 (26.1.1), openconfig 86→20, ietf 200→216 (now correct — the old "non-empty" bodies had leaves falsely hoisted from nested lists), native percentage 58.1%→52.6%, total 43.6%→39.8% on 26.1.1.

If a customer reports "I can find X in the YANG tree but not in the OpenAPI", check all three rules before touching anything else.

### `scripts/update_manifests.py` is dead code

The `manifests` step in `scripts/build_release.py` calls `update_manifests.py`, which ignores `--version` and tries to write top-level `swagger-*-model/api/manifest.json` paths that no longer exist (everything moved under `releases/<v>/`). Per-release manifests are already created by each generator. Run `build_release.py` with `--only` lists that exclude `manifests`. Do not "fix" by writing top-level dirs.

---

## 9. Testing Approach

**Follow [ASSURANCE_SPEC.md](ASSURANCE_SPEC.md) after every change** — it lists every required gate, smoke test, data check, and security check, and defines the final assurance report you must append to your reply.

Current automated coverage (run as part of G-1):

- `tests/test_no_emoji.py` — enforces no decorative emoji or UTF-8 mojibake in source
- `tests/test_security_regressions.py` — catches CSP / XSS / open-redirect regressions on hub pages
- `tests/test_manifest_schema.py` — informational; 6 pre-existing failures are tracked as baseline
- `tests/test_assurance_spec_complete.py` — fails if `ASSURANCE_SPEC.md` references a file/script that no longer exists (spec-rot guard)
- `tests/test_release_counts.py` — fails on **silent regression in API count, operation count, or module count** vs the checked-in `release_counts.json` baseline. Refresh the baseline only on intentional drops: `python -X utf8 scripts/release_counts.py --write`

Local smoke runner:

- `python -X utf8 scripts/smoke_assurance.py` — hits the live deployed site and runs S-1..S-6 from the assurance spec using only the Python stdlib (no browser, no Playwright). Pass `--base http://localhost:8000` to test a local `python -m http.server` instance, or `--only S-1,S-4` to scope. Exit codes: `0` = all PASS, `1` = at least one FAIL, `2` = no FAILs but SKIP.
- `python -X utf8 scripts/smoke_live.py` — deeper, Playwright-based variant retained for browser-only assertions. Requires `pip install playwright; playwright install chromium`.

Deeper, slower validation:

- `python scripts/validate_release.py --version <v>` (per-release artifact parity — G-2)
- `python scripts/validate_quality.py` (spec quality audit)
- `python scripts/validate_examples_c9kv.py` (real RESTCONF requests against a live C9kv — not in CI)
- `python -m http.server 8000` and click through the UI

---

## 10. Operational Safety

When making changes that affect generated artifacts:

**Safe** — edit, re-run generator/enrichment locally, commit both source and outputs
**Safe** — add new generators or scripts, document them here
**Safe** — frontend changes (must validate CSP compliance)

**Confirm with user first**:

- Deleting any `swagger-*-model/` directory or its contents
- Removing scripts in `scripts/` or `generators/` (some are referenced by the deploy workflow)
- Modifying `.github/workflows/*.yml`
- Force-pushing to `main`
- Bumping the IOS-XE source version (currently `17181`) — affects 100+ files

---

## 11. Where to Read More

- [README.md](README.md) — high-level project overview
- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) — RESTCONF API consumer guide (curl, Python, JS examples)
- [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) — completion summary by phase
- [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) — architecture decisions, full requirements
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) — known fixes, common APIs, support links
- [GITHUB_PAGES_DEPLOY.md](GITHUB_PAGES_DEPLOY.md) — deployment workflow details
- [YANG_MODULE_ACCOUNTABILITY.md](YANG_MODULE_ACCOUNTABILITY.md) — module-by-module coverage
- [CHANGELOG.md](CHANGELOG.md) — release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution workflow

---

*Last updated: 2026-06-01 — Closes the native-root-augment gap (kron/mmode + 111 other sibling-module children) and adds a completeness sweep for any top-level native container the v2 generator silently drops. Coverage guard now verifies 233–264 children per release across all 5 releases.*
