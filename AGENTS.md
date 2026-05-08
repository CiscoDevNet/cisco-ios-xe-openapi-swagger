# AGENTS.md — AI Agent Guide

> Guidance for AI coding agents (GitHub Copilot, Claude, Cursor, etc.) working in this repository.
> Follows the [agents.md](https://agents.md) convention.

This file describes **how to work in this codebase safely and productively**. Read it before making changes.

---

## 0. Source-of-truth docs (read these first)

When making non-trivial changes, the following documents are authoritative. Update them when behavior changes; do not duplicate their content elsewhere.

| Doc | Authoritative for |
|-----|-------------------|
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
| `swagger-native-config-model/` | native | 81 | Full CLI-equivalent config (full CRUD) |
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

---

## 9. Testing Approach

There is **no automated test suite** yet (this is a static doc site). Verification is manual:

- **Lint**: `python -c "import ast; ast.parse(open('scripts/foo.py').read())"` for syntax
- **Spec validation**: `python scripts/validate_quality.py` audits all specs
- **Audit reports**: `python scripts/audit_examples.py`, `audit_quality.py`, etc.
- **Live device**: `python scripts/validate_examples_c9kv.py` sends real RESTCONF requests
- **Visual**: `python -m http.server 8000` and click through the UI

Adding `pytest` or similar is welcome but not required.

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

*Last updated: 2026-04-25 — Reflects the post-enrichment (zero-empty-examples) and deep-linking fixes.*
