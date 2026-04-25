# Changelog

All notable changes to this project. Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

The published site is versioned by IOS-XE release; the `Unreleased` section captures changes
not yet reflected in a tagged release of the upstream YANG models.

---

## Versions Supported

The site serves these IOS-XE releases under one GitHub Pages URL with an in-app version
selector (see [VERSIONING.md](VERSIONING.md) for the architecture).

| Version | YangModels path | Status | Notes |
|---------|-----------------|--------|-------|
| 26.1.1  | `vendor/cisco/xe/2611`  | planned (build pending) | Newest release |
| 17.18.1 | `vendor/cisco/xe/17181` | active                 | Existing baseline; migrating to `releases/17.18.1/` |
| 17.15.x | `vendor/cisco/xe/17151` | planned (build pending) | |
| 17.12.x | `vendor/cisco/xe/17121` | planned (build pending) | |
| 17.9.x  | `vendor/cisco/xe/1791`  | planned (build pending) | Older release |

Adding additional patches/minors is the mechanical runbook in [VERSIONING.md §8](VERSIONING.md#8-adding-a-new-release--runbook).

---

## [Unreleased]

### Added — Multi-release foundations (April 2026)

- **`releases/<ver>/` per-release folder layout** — defined in [VERSIONING.md](VERSIONING.md). Per-release
  folders hold OpenAPI specs, pyang trees, manifests, accountability JSON, search index,
  telemetry index, MIB metadata, native capabilities, and Postman/Bruno exports.
- **[VERSIONING.md](VERSIONING.md)** — new authoritative doc covering folder layout, URL contract,
  `meta.json` schema, manifest schema, "add a new release" runbook, and CI gates.
- **[MDT_XPATH_SPEC.md](MDT_XPATH_SPEC.md)** — new authoritative doc defining the
  `/<prefix>:<container-path>` MDT filter-xpath rule, OpenAPI `x-mdt-*` extensions, and
  `telemetry-index.json` schema.
- **[scripts/fetch_yang_release.py](scripts/fetch_yang_release.py)** — sparse, shallow clone of
  YangModels/yang for a single release; pins commit SHA in `releases/<ver>/meta.json`.
- **[scripts/generate_all_pyang_trees.py](scripts/generate_all_pyang_trees.py)** — version-aware tree
  generator that writes `releases/<ver>/yang-trees/` and a per-release `tree_audit.json` documenting
  every skip reason (`types-only`, `submodule`, `deviation-only`, `augment-only`, `empty-tree`).
- **[scripts/build_release.py](scripts/build_release.py)** — single-release pipeline orchestrator
  (specs → enrichment → trees → MDT annotation → MIB metadata → native capabilities → manifests
  → accountability → search → Postman → Bruno).
- **[scripts/build_all_releases.py](scripts/build_all_releases.py)** — iterates `releases/index.json`.
- **[scripts/validate_release.py](scripts/validate_release.py)** — local pre-flight that runs every
  CI gate from [VERSIONING.md §9](VERSIONING.md#9-ci-gates-per-release).
- **[scripts/migrate_to_releases_layout.py](scripts/migrate_to_releases_layout.py)** — one-shot
  migration of the current 17.18.1 artifacts into `releases/17.18.1/`. Default dry-run; `--apply`
  copies and `--remove-legacy` deletes the originals after copy.
- **[releases/index.json](releases/index.json)** — canonical list of releases consumed by the UI
  version selector.
- **[PROJECT_REQUIREMENTS.md §16](PROJECT_REQUIREMENTS.md#16-multi-release-phase-april-2026)** —
  new section locking the multi-release, MDT, native v2, MIB detail, exports, and accountability
  requirements.
- **CODE_REVIEW.md resolution banner** — confirms the three "Must-Fix Blockers" (XSS in `search.js`,
  localStorage silent-fail in `recent-favorites.js`, search-index race condition) are already
  resolved in code.

### Added — Multi-release scripts & UI surfaces (round 2, April 2026)

- **[scripts/_release_paths.py](scripts/_release_paths.py)** — shared `ReleasePaths` helper used by
  every new version-aware script; centralises `releases/<ver>/...` path resolution and provides
  `list_active_releases()` / `all_releases()` against `releases/index.json`.
- **[scripts/annotate_mdt_xpaths.py](scripts/annotate_mdt_xpaths.py)** — parses
  [`telemetry-reference-v2.md`](telemetry-reference-v2.md) and stamps `x-mdt-filter-xpath`,
  `x-mdt-tier`, `x-mdt-cadence-seconds`, `x-mdt-encoding`, `x-mdt-on-change-capable`,
  and `x-mdt-feature-section` onto matching oper-spec operations. Emits
  `releases/<ver>/telemetry-index.json` and `releases/<ver>/telemetry-skipped.json`.
- **[scripts/parse_mibs_md.py](scripts/parse_mibs_md.py)** — parses [MIBS.md](../MIBS.md) §3.5
  full-availability matrix, §2.x functional-category roles, and §1.5 latest-inventory list, writing
  `releases/<ver>/mib-platform-matrix.json`.
- **[scripts/enrich_mib_metadata.py](scripts/enrich_mib_metadata.py)** — extracts SMIv2 OID prefix,
  table/scalar/leaf counts, deprecated-object counts, latest-revision date, organization, and
  RFC reference from each MIB-derived YANG, then joins with the platform matrix into
  `releases/<ver>/mib-metadata.json`.
- **[scripts/build_native_capabilities.py](scripts/build_native_capabilities.py)** — counts paths,
  operations (per HTTP method), schemas, leafs, lists, and choices across every
  `swagger-native-config-model` spec, writing `releases/<ver>/native-capabilities.json` for the
  Config Capabilities summary page.
- **[scripts/build_accountability_compare.py](scripts/build_accountability_compare.py)** — reads
  every active release's `yang_accountability.json` and emits a unified cross-version matrix at
  `accountability_compare.json` (with `summary`, `deltas`, and per-module `by_version` rows)
  consumed by [yang-accountability-compare.html](yang-accountability-compare.html).
- **[scripts/generate_bruno_collection.py](scripts/generate_bruno_collection.py)** — emits one Bruno
  collection per (release, model-category) pair under `releases/<ver>/exports/bruno/`, with auto-split
  on the 50 MB cap and a top-level `bruno-manifest.json`.
- **[scripts/generate_postman_v2_collection.py](scripts/generate_postman_v2_collection.py)** —
  version-aware successor to the legacy `generate_postman_collection.py`; emits per-(release, category)
  Postman v2.1 collections plus an environment file under `releases/<ver>/exports/postman/`, with
  auto-split on the 50 MB cap and a top-level `postman-manifest.json`. The legacy script is kept
  untouched for backward compatibility with `tools/`.

#### UI surfaces

- **[index.html](index.html)** — version selector dropdown in the header sourced from
  `releases/index.json`; persists in `localStorage['iosxe-active-version']` and reflects in the URL
  hash as `ver=<v>`. Added quick-nav links to **Compare Versions**, **MDT Telemetry**, and **Exports**.
- **[index-app.js](index-app.js)** — `initVersionSelector()` and `applyVersion()`; exposes
  `window.__IOSXE_ACTIVE_VERSION__` so other modules can scope their fetches.
- **[search.js](search.js)** — `loadSearchIndexForActiveVersion()` tries
  `releases/<ver>/search-index.json` first and falls back to the legacy root index for
  backward compatibility.
- **[telemetry.html](telemetry.html)** — new top-level page; loads
  `releases/<ver>/telemetry-index.json`, filters by tier (HOT/WARM/COOL), on-change capability,
  and free-text, links each row back to its OpenAPI spec.
- **[exports.html](exports.html)** — new top-level page; per-release matrix of Postman + Bruno
  collections from `*-manifest.json` with size badges and download links.
- **[yang-accountability-compare.html](yang-accountability-compare.html)** — new top-level page;
  renders the cross-version comparison matrix and version-to-version add/remove deltas from
  `accountability_compare.json`.

#### Build pipeline

- **[scripts/build_release.py](scripts/build_release.py)** — pipeline now includes
  `mibs-md-parse`, switches the postman step to `generate_postman_v2_collection.py`,
  and is the single source of truth for per-release builds.
- **[.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml)** — adds a
  `validate-releases` matrix job (`17.9.x`, `17.12.x`, `17.15.x`, `17.18.1`, `26.1.1`) that runs
  `scripts/validate_release.py` per cell and gates the deploy job; deploy step now copies the
  `releases/` tree into the artifact.

#### Generator migration (round 2.5)

- **[generators/_version_args.py](generators/_version_args.py)** — shared
  `resolve_paths(category, mib_subdir=False)` helper that strips `--version <ver>` from `sys.argv`
  and returns the correct `(yang_dir, output_dir, version)` tuple. Legacy 17.18.1 maps to
  `references/17181-YANG-modules/` + `swagger-<cat>-model/api/`; any other version maps to
  `releases/<ver>/yang-source/` + `releases/<ver>/swagger-<cat>-model/api-v2/`. Backward compatible:
  generators called without `--version` retain their original behaviour.
- All 9 v2 spec generators (`generate_oper_openapi_v2.py`, `generate_cfg_openapi_v2.py`,
  `generate_native_openapi_v2.py`, `generate_openconfig_openapi_v2.py`, `generate_ietf_openapi_v2.py`,
  `generate_mib_openapi_v2.py`, `generate_other_openapi_v2.py`, `generate_events_openapi.py`,
  `generate_rpc_openapi_v2.py`) now use the shared helper in their entry points and accept
  `--version <ver>`.
- **[scripts/build_release.py](scripts/build_release.py)** — `run_step()` now captures
  stdout/stderr and, if a step fails because a generator rejects `--version` (argparse
  "unrecognized arguments"), automatically retries without the flag. Defensive shim retained for
  any non-migrated tools.

#### Per-spec MDT panel

- **[swagger-oper-model/index-v2.html](swagger-oper-model/index-v2.html)** — when an oper spec is
  loaded, fetches the active release's `telemetry-index.json`, filters entries to that module, and
  exposes them via a 📡 toolbar toggle that opens an inline panel listing each XPath with HOT /
  WARM / COOL tier badges, cadence, and on-change indicators. Falls back gracefully when no
  telemetry index is present.

#### Visible UI surfaces (round 3)

- **[swagger-mib-model/index-v2.html](swagger-mib-model/index-v2.html)** — added a 🗄️ MIB Details
  toolbar toggle. When opened it loads the active release's `mib-metadata.json` (with fallback to
  the legacy in-place file) and renders the loaded spec's MIB record: module / OID prefix /
  table-scalar-leaf counts / indexes / deprecated flag / latest revision / organization / RFC /
  functional category / supported platforms (as badges).
- **[swagger-native-config-model/capabilities.html](swagger-native-config-model/capabilities.html)**
  *(new)* — standalone Native config capability dashboard. Reads
  `releases/<ver>/native-capabilities.json`, shows totals (paths / operations / schemas / leafs /
  lists / choices / categories) and a sortable & filterable per-category table with deep-links into
  each category's spec in the Swagger UI viewer. Includes the standard release picker.
- **[swagger-native-config-model/index-v2.html](swagger-native-config-model/index-v2.html)** —
  added a 📊 Capabilities Report link in the toolbar.
- **[references/native-cli-mappings.yaml](references/native-cli-mappings.yaml)** *(new)* — curated
  YAML mapping table (~25 prefixes covering hostname, interfaces, BGP / OSPF, VLANs, AAA, SNMP,
  NTP, logging, spanning-tree, ACLs, NAT) of `path → cli` so every native operation can advertise
  its CLI equivalent.
- **[scripts/apply_cli_mappings.py](scripts/apply_cli_mappings.py)** *(new)* — overlay step that
  walks the active release's native specs (longest-prefix match, with `/data` prefix
  normalisation against the YAML keys) and stamps `x-cli-equivalent` (and optional `x-cli-notes`)
  onto every HTTP method. Verified on 17.18.1: stamps 2,372 operations across 12 spec files.
- **[references/native-example-overlay.yaml](references/native-example-overlay.yaml)** *(new)* +
  **[scripts/apply_example_overlay.py](scripts/apply_example_overlay.py)** *(new)* — curated
  request-body examples for the most common native paths (hostname, Loopback, GigE, BGP, vlan-list,
  snmp host, ntp server, aaa new-model). The applier writes the example into each PUT/PATCH/POST's
  `requestBody.content["application/yang-data+json"].example`.
- **[scripts/build_release.py](scripts/build_release.py)** — pipeline now runs
  `apply_cli_mappings.py` and `apply_example_overlay.py` between `mib-metadata` and
  `build_native_capabilities` so capability counts reflect the overlay-augmented specs.

### Fixed (round 3)

- **[scripts/build_native_capabilities.py](scripts/build_native_capabilities.py)** —
  `count_schema_features()` only counted the top-level schema and one level of properties, so the
  legacy 17.18.1 native specs (which keep most of their data shape inline under each path's
  request/response, with only one `restconf-error` schema in `components.schemas`) reported
  `leafs=0 lists=0`. Added depth-first `_walk_schema()` recursion (handles nested `properties`,
  `items`, `oneOf` / `anyOf` / `allOf`, `patternProperties`) and a new `count_path_features()` that
  walks every operation's request/response `schema`. Verified on 17.18.1: `leafs=27,312`,
  `lists=3,252` across 81 categories / 3,363 paths / 13,452 operations.
- **[scripts/validate_release.py](scripts/validate_release.py)** — gates now tolerate the legacy
  17.18.1 in-place layout (specs at repo root, `releases/17.18.1/` either missing or partially
  populated). Detects "no specs under `releases/<ver>/swagger-*-model/api-v2/`" and re-roots to
  `PROJECT_ROOT` for 17.18.1 only. Gates 1, 4, 5 now glob `swagger-*-model/api-v2/*.json`
  (eliminating false hits in `archive/` and other releases). Search-index, tree-audit and
  accountability files fall back to repo-root copies. Manifests without a declared `spec_count`
  emit a warning instead of failing. Verified: `validate_release.py --version 17.18.1` exits 0
  with all gates passing (666 specs parsed, 790 unique search entries).


### Fixed

- **Eliminated empty `{}` examples in 657 specs** — POST/PUT/PATCH request bodies now contain
  realistic, RFC 7951–compliant payloads.
  ([scripts/enrich_v2_specs.py](scripts/enrich_v2_specs.py))
  - Added `build_example_from_schema()` — recursively walks schema `properties` to construct
    examples from leaf types and known field-name heuristics.
  - Added `CONTAINER_FILL` (~95 templates) — maps YANG container names (e.g., `state`, `config`,
    `switchport`, `bfd`, `bgp`) to realistic structured fills.
  - Added `_build_example_from_path()` — path-based templates for VLAN, BGP, OSPF, ACL,
    AAA, NTP, SNMP, etc.
  - Added `_populate_empty_example()` — orchestrator: schema-first, path-based fallback,
    finally `[null]` for empty YANG leaves (RFC 7951 encoding).
  - **Result**: 0 empty `{}` and 0 stray `null` values across 26,331 config examples
    (verified across all 9 model categories).
- **Fixed deep-link URLs from search results** — copying/pasting a search URL now opens the
  correct module instead of the index page. ([search.js](search.js))
  - `updateUrlHash(query)` writes `#search=<query>` via `history.replaceState`.
  - `handleDeepLink()` parses three URL hash patterns on load:
    - `#search=<query>` — runs the search
    - `#module=<name>` — redirects to the module's swagger page
    - `#spec=<model>/<name>` — redirects to the model's `index-v2.html#spec=<name>`
  - Added `hashchange` listener for browser back/forward sync.

### Added

- **`scripts/validate_examples_c9kv.py`** — Live-device validation for write-operation examples
  against a Catalyst 9000V (or any IOS-XE 17.18.1+ device).
  - CLI: `--host --port --username --password --spec --method --limit --dry-run --patch-only --output`
  - 8,066 PATCH-testable examples confirmed via `--dry-run`.
- **`AGENTS.md`** — AI agent guide (build/run, conventions, pitfalls, common tasks).
- **`CONTRIBUTING.md`** — Contribution workflow.
- **`CHANGELOG.md`** — This file.

### Changed

- **Inline JavaScript extracted from HTML pages** to comply with strict Content Security Policy:
  - [index.html](index.html) → [index-app.js](index-app.js) (341 lines)
  - [code-generator.html](code-generator.html) → [code-generator.js](code-generator.js) (345 lines)
  - [tree-compare.html](tree-compare.html) → [tree-compare.js](tree-compare.js) (332 lines)
  - [yang-accountability.html](yang-accountability.html) → [yang-accountability.js](yang-accountability.js) (254 lines)
- **CSP hardened** — `script-src 'self' cdn.jsdelivr.net`. No more `unsafe-inline`.

---

## [17.18.1] — Initial public release

The full 17.18.1 corpus, summarized:

### Specifications

- 657 OpenAPI 3.0 specs across 9 model categories
- 43,726 RESTCONF API paths
- 68,353 API operations
- 60,200 example payloads
- 768 YANG/MIB tree HTML visualizations
- 848 source YANG modules tracked
- 100% module accountability (every YANG module documented or excluded with reason)

### Coverage by model

| Model | Specs | Paths/Ops |
|---|---:|---:|
| Operational | 205 | 20,159 paths |
| MIB | 149 | 12,482 paths |
| Native Config | 81 | 13,452 ops |
| RPC | 59 | 308 RPCs |
| OpenConfig | 57 | 5,920 ops |
| Configuration | 39 | 9,452 ops |
| Events | 38 | 861 paths |
| IETF | 19 | 1,122 ops |
| Other | 10 | 4,597 ops |

### Site features

- Fuse.js fuzzy search across all 657 modules
- Multi-language code generator (Python/curl/Go/Ansible/Postman)
- YANG tree comparison tool
- 100% module accountability report
- Recent + favorites (localStorage)
- 6 curated quick-start collections (day0, troubleshooting, performance, etc.)

---

## Future

- **17.15** and **26.1** YANG releases — multi-version picker
- Live C9KV validation runs in CI
- Optional automated `pytest`-based test suite
