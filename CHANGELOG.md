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
| 26.1.1  | `vendor/cisco/xe/2611`  | active **(default)** | Newest release; site default |
| 17.18.1 | `vendor/cisco/xe/17181` | active | Baseline for legacy in-place artifacts |
| 17.15.x | `vendor/cisco/xe/17151` | active | |
| 17.12.x | `vendor/cisco/xe/17121` | active | |
| 17.9.x  | `vendor/cisco/xe/1791`  | active | Oldest supported release |

Tree-module counts are monotonic across versions: 620 / 637 / 683 / 715 / 742 (17.9.x → 26.1.1).

Adding additional patches/minors is the mechanical runbook in [VERSIONING.md §8](VERSIONING.md#8-adding-a-new-release--runbook).

---

## What's New in 26.1.1

Highlights for users coming from 17.x. This is a curated summary; see the
release-tagged sections below for full per-round detail.

- **+27 net new YANG modules** vs 17.18.1 (742 vs 715 tree modules); +122 modules vs 17.9.x (620).
- **Per-release artefacts** under [releases/26.1.1/](releases/26.1.1/) —
  search index, YANG accountability report, Postman collections, Bruno collections,
  prefix map, and viewer manifests, all version-pinned. The hub's version selector
  resolves these at runtime.
- **Deeper cfg + oper specs** — `generate_cfg_from_tree.py` and `generate_oper_from_tree.py`
  now emit depth-8 trees, producing ~4× more cfg paths, ~7.8× more oper paths and
  ~10.8× more native paths over the legacy depth-4 cap.
- **MDT telemetry builder** — `telemetry.html` derives a paste-ready
  `telemetry ietf subscription` snippet from any operational xpath, with curated
  tier / cadence / on-change annotations folded in when matched.
- **Site quality bar** — Lighthouse strict mode + axe-core gates every deploy;
  PWA service worker enables offline browsing of the shell.
- **Tooling parity across releases** — all five active releases (17.9.x, 17.12.x,
  17.15.x, 17.18.1, 26.1.1) pass the same strict pyang validation and ship the
  same set of artefacts.

For a hands-on walkthrough of common tasks, see [CONTRIBUTING.md](CONTRIBUTING.md#walkthrough-add-a-missing-operational-spec).

---

## [Unreleased]

### Added — UX polish, deep-links, CSV export (round 10, 2026)

- **Keyboard shortcut help dialog** — press `?` on any page to open a focused,
  Esc-dismissable modal listing global shortcuts (`/`, `Ctrl+K`, `Esc`, `Tab`,
  `Shift+Tab`, `Enter`). Implemented in [assets/js/site-chrome.js](assets/js/site-chrome.js)
  with proper focus management (returns focus on close, `aria-modal`,
  `aria-labelledby`). Pages may extend via `window.__SHORTCUTS`. A discoverable
  "? Shortcuts" button sits next to the hub search bar.
- **`yang-accountability.html` Export CSV** — downloads the currently-filtered rows
  as a UTF-8 BOM, RFC 4180-quoted `.csv` named
  `yang-accountability-<ver>-<date>.csv`. Columns: Module Name, Classification,
  Categories, Has Spec, Has Tree, Spec URLs, Tree URL, Reason Excluded.
- **`telemetry.html` Export CSV** — downloads visible Method / OpenAPI path / MDT
  filter xpath rows as
  `telemetry-paths-<ver>-<spec>-<date>.csv` honoring the active path filter.
- **`yang-accountability.html` deep-links + Copy Share Link** — URL hash now
  preserves `ver`, `q`, `cat`, `status`; filter buttons sync to URL on every
  change. A new Copy Share Link button reproduces the exact filter state.
- **`code-generator.html` deep-links + Copy Share Link + version-aware picker** —
  `ver=&category=&spec=&path=&method=` hash schema; per-release search-index
  fallback; never persists credentials.
- **`exports.html` filter bar** — release dropdown + Postman / Bruno / All
  toggle with hash sync (`#ver=&format=`), live totals (requests + bytes), and
  basename-only Path display with full path in tooltip.
- **Postman split-by-category** — each release ships 9 per-category Postman v2.1
  collections to stay under GitHub's 50 MB recommended limit. Max shard 22.7 MB
  (native-config 26.1.1).
- **Sitemap refresh + sitemap generator** — `python scripts/generate_sitemap.py`
  refreshes `lastmod` on all 16 entries to today.
- **Accessibility** — `aria-label` on filter inputs across code-generator,
  yang-accountability, yang-accountability-compare, tree-compare, telemetry;
  keyboard-activatable native-config search-clear span; close-button
  `aria-label` on the code-snippet modal.
- **Generator output paths** — Postman + Bruno manifests now write POSIX paths
  (forward slashes) regardless of host OS, so download links on the live site
  work correctly when generators run on Windows.
- **Terminology** — "Has Swagger Spec:" → "Has OpenAPI Spec:" on the hub.
- **Service worker** — `CACHE_VERSION` bumped to `v3-2026.05.22` to ensure
  returning visitors pick up this round's changes.

### Added — Site quality, PWA, and per-release exports (round 9, 2026)

- **Lighthouse strict + axe-core CI** — site quality gates (Tier 3) added to the deploy
  workflow, blocking regressions in performance, accessibility, best-practices, and SEO.
- **JSON minify + htmlhint** (Tier 4) — deploy step now minifies JSON data files and runs
  htmlhint over every shipped HTML page.
- **search-index v3.1 slim-down** (Tier 5 + 8) —
  [scripts/generate_search_index.py](scripts/generate_search_index.py) now drops empty
  fields and truncates module descriptions at a 160-char word boundary (down from 250).
  Combined effect: `search-index.json` shipped size 1,124,074 → 1,096,810 B (−2.4%
  pretty, larger savings post-CI minify); `max-desc-len` capped at 162.
- **PWA service worker + manifest** (Tier 6) — [service-worker.js](service-worker.js)
  pre-caches the app shell and serves it offline. [site.webmanifest](site.webmanifest)
  registered on all 17 top-level pages by [scripts/inject_pwa.py](scripts/inject_pwa.py).
- **Deep-link scroll-position memory** (Tier 7) — [deeplink.js](deeplink.js) now stores
  the last `op=` location under `iosxe-scroll-<spec>` and restores it after spec load,
  so refreshing or returning to a deep-link lands on the same operation row instead of
  the top of the page.
- **Update-available toast** (Tier 9) — when a new service worker reaches `installed`
  while an existing controller is in charge, all pages surface a small bottom-right
  card with a Reload button. Reload posts `{type:'SKIP_WAITING'}`; the
  `controllerchange` listener then refreshes the page exactly once.
  `CACHE_VERSION` bumped to `v2-2026.05.20`. Inline registration is CSP-safe
  (`role=status`, `aria-live=polite`, dismiss button, fail-silent).
- **Per-release Postman + Bruno exports for all 5 releases** — `releases/<ver>/exports/`
  now exists for 17.9.x, 17.12.x, 17.15.x, 17.18.1 and 26.1.1, each with 9 per-category
  Postman v2.1 collections, a Postman environment, a `postman-manifest.json`, and a
  `bruno-manifest.json`. Bruno collection content remains git-ignored and is
  regenerated locally via
  [scripts/generate_bruno_collection.py](scripts/generate_bruno_collection.py).
  Per-release request totals: 17.9.x=52,170 / 17.12.x=54,164 / 17.15.x=58,874 /
  17.18.1=68,353 / 26.1.1=63,541.
- **`Cisco-IOS-XE-bgp-route-oper` exclusion reason** — `yang_accountability.json` (root
  + all 5 per-release files) and [YANG_MODULE_ACCOUNTABILITY.md](YANG_MODULE_ACCOUNTABILITY.md)
  updated to record `"Source YANG not bundled with model package"` instead of `null`.
- **[FAQ.md](FAQ.md)** — new top-level FAQ covering offline use, Catalyst 9k API
  discovery, on-device validation, MDT subscription, and Postman/Bruno consumption.

### Added — Hub-level cross-category operation search & d8 spec depth (round 8, 2026)

- **[hub-search-ops.js](hub-search-ops.js)** — augments the universal search box on the
  landing page (`#universalSearch`) with a new "Operations matching" section that surfaces
  individual API operations across all 9 viewer categories. Lazy-loads each category's
  `_paths_index.json` (built by [scripts/build_paths_index.py](scripts/build_paths_index.py))
  on the first user query and caches in memory. Each hit renders HTTP-method badges
  (GET/POST/PUT/PATCH/DELETE colour-coded) and clicks deep-link to
  `swagger-<cat>-model/index.html#spec=<module>&op=<operationId>`, handled by
  [deeplink.js](deeplink.js) in each viewer (auto-loads spec, expands the operation row).
  CSP-strict (same-origin script, no `eval`, no inline handlers).
- **Depth-d8 cfg / oper specs (26.1.1)** — `generate_cfg_from_tree.py` and
  `generate_oper_from_tree.py` `max_depth` raised from 6 → 8 in both `collect_deep_paths()`
  and `process_tree_file()`. 26.1.1 now publishes:
  - cfg : 2559 paths, 10083 operations, 40 specs (+25 paths at d7 + d8)
  - oper: 22144 paths, 215 specs (+566 paths at d7 + d8)
- **Audit floor tightened** — [scripts/audit_path_depth.py](scripts/audit_path_depth.py)
  `MIN_MAX_DEPTH` raised cfg / oper 6 → 7. Strict mode now blocks any future regression
  below d7 for those two categories.
- **17.x backport (shipped)** — the from-tree generators were rolled out to 17.9.x, 17.12.x
  and 17.15.x via `_resolve_paths(version)` (`releases/<ver>/yang-trees/`). Followed by
  `enrich`, `github-links`, `external-docs`, `tree-links`, `mdt-annotate`, `manifests`,
  `stamp-spec-count`, `search-index` and `path-depth-audit`. Depth gains:
  - 17.9.x : cfg 643→2519 (d2→d8), oper 1907→17136 (d3→d8), events 52→699 (d1→d2)
  - 17.12.x: cfg 601→2512 (d2→d8), oper 2226→19042 (d3→d8), events 54→710 (d1→d2)
  - 17.15.x: cfg 579→2546 (d2→d8), oper 2426→20465 (d3→d8), events 70→799 (d1→d2)
  All four active releases (17.9.x, 17.12.x, 17.15.x, 26.1.1) now PASS the strict
  path-depth audit floor. 17.18.1 still uses the legacy top-level `api/` layout and was
  intentionally left untouched.

### Added — Path-depth audit, tree-based generators & cross-chunk operation search (rounds 6–7, 2026)

- **Tree-based generators for cfg / oper / events** —
  [generators/generate_cfg_from_tree.py](generators/generate_cfg_from_tree.py),
  [generators/generate_oper_from_tree.py](generators/generate_oper_from_tree.py) and
  [generators/generate_events_from_tree.py](generators/generate_events_from_tree.py)
  replace the older regex-based generators in [scripts/build_release.py](scripts/build_release.py)'s
  `cfg-specs`, `oper-specs` and `events-specs` steps. Tree parsers walk the pyang HTML
  output and emit one operation per node up to the configured `max_depth`, mirroring the
  same approach already used by the `native_from_tree` and `openconfig_from_tree`
  generators. On 26.1.1 this produced ~4× more cfg paths, ~7.8× more oper paths and ~10.8×
  more events paths versus the previous regex passes.
- **[scripts/audit_path_depth.py](scripts/audit_path_depth.py)** — new build step that
  walks every `releases/<ver>/swagger-<cat>-model/api/*.json`, computes a per-category
  depth distribution + `max-depth`, writes `releases/<ver>/path_depth_audit.json` and (in
  `--strict` mode, used by `build_release.py`) fails the build if any category is below its
  `MIN_MAX_DEPTH` floor. Floors at end of round 7: cfg=6, oper=6, native-config=6, ietf=3,
  openconfig=3, other=3, events=2, mib=2, rpc=1.
- **Cross-chunk operation search in all 9 viewers** — `paths-search.js` (canonical copy in
  [swagger-native-config-model/paths-search.js](swagger-native-config-model/paths-search.js))
  is wired into every viewer (`cfg`, `events`, `ietf`, `mib`, `native-config`, `openconfig`,
  `oper`, `other`, `rpc`). The IIFE hooks the viewer's `#searchBox` and queries the
  category-scoped `_paths_index.json`, so a path/op search resolves across **all** spec
  chunks in the category, not just the one currently rendered. 80 ms input debounce,
  `MIN_QUERY=2`, `MAX_HITS=60`. The hook self-skips on releases other than 26.1.1.
- **Spec-count manifest fixes** — both [scripts/stamp_spec_count.py](scripts/stamp_spec_count.py)
  and [scripts/update_manifests.py](scripts/update_manifests.py) now exclude `manifest.json`
  and `_paths_index.json` when counting specs, so the published counts stay correct after
  the paths-index file landed in `api/`.
- **Multi-root merge in `generate_cfg_from_tree.py`** — earlier the cfg generator emitted
  separate spec files per `data` root, causing 40 files vs 90 modules. The from-tree port
  now merges roots per module name (matching the oper generator), restoring 1-spec-per-module
  parity.

### Added — Module-driven Telemetry XPath Builder (round 5, April 2026)

- **[telemetry.html](telemetry.html) rewrite** — formerly a static dump of the 61 curated
  `telemetry-index.json` entries; now a two-tab tool. The default tab, **Module XPath Builder**,
  lets the user pick any release / category / module and renders the MDT
  `filter xpath` for **every** operation in that spec, derived live with the formula from
  [MDT_XPATH_SPEC.md](MDT_XPATH_SPEC.md) (`/<prefix>:<path-without-leading-slash>`). Each row
  has a "Use" button that drops the xpath into a ready-to-paste `telemetry ietf subscription`
  config snippet. Curated tier / cadence / on-change annotations from `telemetry-index.json`
  are folded in as enrichment when the derived xpath matches a catalogued entry. The original
  filterable curated table is preserved as the **Curated Catalog** tab.
- **[scripts/build_yang_prefix_map.py](scripts/build_yang_prefix_map.py)** — new build step that
  scans every `*.yang` file under each release's source directory, extracts the `prefix`
  statement, and emits `releases/<ver>/yang-prefix-map.json` (and a top-level
  `yang-prefix-map.json` for the legacy 17.18.1 in-place layout). Output schema:
  `{version, yang_source, module_count, modules: {moduleName: prefix}}`. Built today for all
  five active releases: 26.1.1 (887), 17.18.1 (848), 17.15.x (799), 17.12.x (719), 17.9.x (701).
- **Formula verified** against the existing curated 17.18.1 catalog: 60/61 entries match
  exactly; the single "mismatch" is a curator-chosen deeper xpath
  (`/interfaces-ios-xe-oper:interfaces/interface`) rooted on the same operation, not a
  formula bug.
- **[telemetry.js](telemetry.js)** — new external script (CSP `script-src 'self'` compliant);
  no inline JS in `telemetry.html`.

### Added — Site-wide version awareness & quality hardening (round 4, April 2026)

- **Version-aware viewers** — all 9 `swagger-*-model/index.html` viewers now resolve the active
  release at runtime via `__activeVer()` / `__apiBase()` / `__treeBase()` helpers injected by
  [scripts/patch_viewers_version_aware.py](scripts/patch_viewers_version_aware.py). The patcher
  reads `releases/index.json` once and bakes the default version + active-versions allow-list into
  each viewer as `__IOSXE_DEFAULT_VER__` / `__IOSXE_ALLOWED_VERS__`. Unknown `?ver=` values are
  rejected (no more 404 storms on bad URLs). Helper block is regex-replaceable for true idempotency,
  and the dead `getSpecFolder()` function was removed from all viewers.
- **[scripts/normalize_manifests.py](scripts/normalize_manifests.py)** — normalises every
  `manifest.json` (default + 4 release dirs × 9 categories = 45 manifests) to the viewer-expected
  schema: integer `total_modules` / `total_paths` / `total_operations` / `spec_count` summed from
  the sibling spec files, and `modules` as a flat list of string basenames. Fixes the viewer crash
  `Cannot read properties of undefined (reading 'toLocaleString')`.
- **[scripts/smoke_live.py](scripts/smoke_live.py)** *(new, replaces `_debug_viewer.py`)* —
  headless Playwright smoke test of the live deployment. Loads version list from
  `releases/index.json`, walks every active release through the viewer, and exits non-zero on real
  failures (transient 503s ignored). `--base-url` flag for staging.
- **[tests/test_manifest_schema.py](tests/test_manifest_schema.py)** *(new)* — 46 parametrized
  pytest cases (45 manifests + 1 sanity) asserting required integer keys, `modules` as `list[str]`,
  count agreement, and that every listed module resolves to a sibling `.json` spec.
- **[.github/workflows/tests.yml](.github/workflows/tests.yml)** *(new)* — runs the manifest-schema
  test suite on push/PR touching `swagger-*-model/`, `releases/`, `tests/`, the manifest
  normaliser, the viewer patcher, or itself.
- **[index-app.js](index-app.js)** — `applyVersion()` now rewrites all
  `a[href*="swagger-"][href*="-model/index.html"]` hrefs to carry `?ver=<v>` so category-card
  navigation preserves the active release.

### Fixed (round 4)

- **Manifest schema mismatch** across release directories — old-schema manifests (missing
  `total_paths` / `total_operations`, `modules` as objects rather than strings) caused the viewer
  to crash on load. All 45 manifests rewritten via `normalize_manifests.py`.
- **404 storms on malformed URLs** — `?ver=garbage` previously triggered ~150 spec 404s. Now
  validated against the allow-list baked into the viewer; falls back silently to the default.
- **Mojibake repaired in 7 viewers** — `â€"` → `—`, `ðŸŒ³` → ``, `ðŸ—„` → ``, etc., via `ftfy`.
  CSP meta tags verified present on all 9 viewers.
- **Patcher fragility** — anchor strings differed across viewers; idempotency previously relied on
  a substring sentinel. Replaced with a regex-replaceable helper block and a dead-code strip pass.

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
  [`telemetry-reference.md`](telemetry-reference.md) and stamps `x-mdt-filter-xpath`,
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
  `releases/<ver>/yang-source/` + `releases/<ver>/swagger-<cat>-model/api/`. Backward compatible:
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

- **[swagger-oper-model/index.html](swagger-oper-model/index.html)** — when an oper spec is
  loaded, fetches the active release's `telemetry-index.json`, filters entries to that module, and
  exposes them via a toolbar toggle that opens an inline panel listing each XPath with HOT /
  WARM / COOL tier badges, cadence, and on-change indicators. Falls back gracefully when no
  telemetry index is present.

#### Visible UI surfaces (round 3)

- **[swagger-mib-model/index.html](swagger-mib-model/index.html)** — added a MIB Details
  toolbar toggle. When opened it loads the active release's `mib-metadata.json` (with fallback to
  the legacy in-place file) and renders the loaded spec's MIB record: module / OID prefix /
  table-scalar-leaf counts / indexes / deprecated flag / latest revision / organization / RFC /
  functional category / supported platforms (as badges).
- **[swagger-native-config-model/capabilities.html](swagger-native-config-model/capabilities.html)**
  *(new)* — standalone Native config capability dashboard. Reads
  `releases/<ver>/native-capabilities.json`, shows totals (paths / operations / schemas / leafs /
  lists / choices / categories) and a sortable & filterable per-category table with deep-links into
  each category's spec in the Swagger UI viewer. Includes the standard release picker.
- **[swagger-native-config-model/index.html](swagger-native-config-model/index.html)** —
  added a Capabilities Report link in the toolbar.
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
  populated). Detects "no specs under `releases/<ver>/swagger-*-model/api/`" and re-roots to
  `PROJECT_ROOT` for 17.18.1 only. Gates 1, 4, 5 now glob `swagger-*-model/api/*.json`
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
    - `#spec=<model>/<name>` — redirects to the model's `index.html#spec=<name>`
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

- Live C9KV validation runs in CI
- Scheduled `smoke_live.py` cron job (GitHub Actions) for daily deployment regression detection
- Optional `viewer-bootstrap.js` extraction to retire the 9 inline helper blocks and the patcher script
