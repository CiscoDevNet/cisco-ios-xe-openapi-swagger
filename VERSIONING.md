# Versioning & Multi-Release Architecture

**Status:** Active (Phase 0 of multi-version rollout)
**Owner:** Project maintainers
**Scope:** This document is the single source of truth for how IOS XE releases are added, stored, built, validated, and exposed in the UI. It supersedes any prior single-release assumptions in [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md).

---

## 1. Goals

1. Host **multiple IOS XE releases** (currently: 17.9.x, 17.12.x, 17.15.x, 17.18.1, 26.1.1, 26.2.1) under the **same GitHub Pages URL** with no domain change.
2. Make adding a new release a **mechanical, scripted operation** — no ad-hoc edits across dozens of files.
3. Preserve **deep-link backward compatibility** for existing URLs while introducing a new version-aware URL contract.
4. Enforce **per-release CI gates** so a broken or incomplete release cannot ship.

## 2. Releases in scope

| Release Tag | YangModels Path | Patch Pin | Notes |
|-------------|-----------------|-----------|-------|
| `17.9.x`    | `vendor/cisco/xe/1791/`  | latest in branch | Older release; some modules may emit pyang warnings |
| `17.12.x`   | `vendor/cisco/xe/17121/` | latest in branch | |
| `17.15.x`   | `vendor/cisco/xe/17151/` | latest in branch | |
| `17.18.1`   | `vendor/cisco/xe/17181/` | exact            | Existing baseline release |
| `26.1.1`    | `vendor/cisco/xe/2611/`  | exact            | Default release |
| `26.2.1`    | `vendor/cisco/xe/2621/`  | exact            | Newest release |

The exact upstream commit SHA used to build each release is pinned in `releases/<ver>/meta.json` (see §5).

## 3. Folder layout

All per-release artifacts live under a new top-level `releases/` directory:

```
cisco-ios-xe-openapi-swagger/
├── releases/
│   ├── index.json                              # list of releases consumed by UI
│   ├── 17.9.x/
│   │   ├── meta.json                           # release metadata (see §5)
│   │   ├── manifests/                          # per-model manifest.json + accountability.json
│   │   ├── swagger-cfg-model/api/*.json     # OpenAPI specs
│   │   ├── swagger-native-config-model/api/*.json
│   │   ├── swagger-oper-model/api/*.json
│   │   ├── swagger-rpc-model/api/*.json
│   │   ├── swagger-ietf-model/api/*.json
│   │   ├── swagger-openconfig-model/api/*.json
│   │   ├── swagger-mib-model/api/*.json
│   │   ├── swagger-other-model/api/*.json
│   │   ├── yang-trees/*.html                   # pyang tree HTML, one per module (themed: site.css + yang-tree.css)
│   │   ├── tree_audit.json                     # per-module tree result (generated / skip reason)
│   │   ├── search-index.json                   # Fuse.js index for this release
│   │   ├── yang_accountability.json            # accountability report (machine-readable)
│   │   ├── telemetry-index.json                # MDT xpath index (oper specs only)
│   │   ├── mib-metadata.json                   # MIB enrichment data
│   │   ├── native-capabilities.json            # native config-surface summary
│   │   ├── yang-prefix-map.json                # module -> xpath prefix (telemetry XPath builder)
│   │   ├── notifications.json                  # notification catalog
│   │   └── exports/
│   │       ├── postman/IOS-XE-17.9.x-<category>.postman_collection.json.zip   # built at deploy
│   │       ├── postman/IOS-XE-17.9.x.postman_environment.json                 # built at deploy
│   │       ├── bruno/IOS-XE-17.9.x-<category>.tar.gz                          # built at deploy
│   │       └── {postman,bruno}-manifest.json                                  # tracked
│   ├── 17.12.x/  (same shape)
│   ├── 17.15.x/  (same shape)
│   ├── 17.18.1/  (same shape; this is the migration target for current artifacts)
│   ├── 26.1.1/   (same shape + live-data/, live-examples-index.json, live-modules.json: device data)
│   ├── 26.2.1/   (same shape)
│   └── compare/  # release-to-release differences (build_release_compare.py)
├── references/
│   ├── 17.9.x/   # raw YANG modules (excluded from deploy/)
│   ├── 17.12.x/
│   ├── 17.15.x/
│   ├── 17.18.1/
│   ├── 26.1.1/
│   └── 26.2.1/
└── (shared UI: index.html, *.js, swagger-*-model/index.html, etc.)
```

The `swagger-*-model/index.html` viewers, `index.html` landing page, accountability viewer, telemetry browser, exports page, and all JavaScript are **shared across releases**. They load per-release data based on the active version.

## 4. `releases/index.json` schema

```json
{
  "default": "26.2.1",
  "device_data": "26.1.1",
  "releases": [
    { "ver": "26.2.1",  "label": "26.2.1 (newest)", "date": "2026-10-02", "default": true },
    { "ver": "26.1.1",  "label": "26.1.1",          "date": "2026-04-01" },
    { "ver": "17.18.1", "label": "17.18.1",         "date": "2026-02-01" },
    { "ver": "17.15.x", "label": "17.15.x",         "date": "2025-09-01" },
    { "ver": "17.12.x", "label": "17.12.x",         "date": "2024-11-01" },
    { "ver": "17.9.x",  "label": "17.9.x",          "date": "2023-08-01" }
  ]
}
```

Order is the order presented in the UI version selector. `default` is the version loaded when no `#ver=` hash is present; it is always the **newest active release** (`tests/test_release_counts.py` enforces this).

`device_data` is the release the lab devices run. Real device data (the Device Data page, the viewers' "Live device data" panel, MDT and harness captures) belongs to that release, independent of `default`. Every device-data tool reads it through `scripts/_release_paths.py:device_data_release()`. A viewer opened on a release without captures shows the `device_data` release's captures, labelled with the release they came from.

## 5. `releases/<ver>/meta.json` schema

```json
{
  "version": "26.1.1",
  "label": "26.1.1",
  "yangmodels_repo": "https://github.com/YangModels/yang",
  "yangmodels_path": "vendor/cisco/xe/2611",
  "yangmodels_commit_sha": "<40-char SHA>",
  "yangmodels_fetch_date": "2026-04-25T00:00:00Z",
  "pyang_version": "2.6.1",
  "build_timestamp": "2026-04-25T12:00:00Z",
  "module_counts": {
    "total_yang": 0,
    "with_specs": 0,
    "with_trees": 0
  }
}
```

`yangmodels_commit_sha` is **mandatory** and pins the exact source. Builds are not reproducible without it.

## 6. URL contract

The UI uses URL hash fragments for client-side routing.

| Pattern | Meaning |
|---------|---------|
| `#ver=<v>`                       | Switch active release; load that release's data |
| `#ver=<v>&spec=<model>/<name>`   | Open spec `<name>` in `<model>` viewer at version `<v>` |
| `#ver=<v>&module=<name>`         | Open module by name (auto-resolves model) |
| `#spec=<model>/<name>`           | Backward-compatible: opens at default release |
| `#module=<name>`                 | Backward-compatible: opens at default release |

Implementations:
- [cisco-ios-xe-openapi-swagger/index-app.js](index-app.js) — landing page version selector + initial load.
- [cisco-ios-xe-openapi-swagger/search.js](search.js) — version-aware index loading.
- All `swagger-*-model/index.html` — read `ver` from hash, load `releases/<ver>/...` paths.

When a user changes version in the selector, the `ver` query param is updated and dependent state (search index, sidebar, currently-displayed spec if applicable) is reloaded; recent/favorites keys are namespaced as `iosxe-<ver>-recent-modules` and `iosxe-<ver>-favorite-modules`.

## 7. Manifest contract (per model, per release)

Every `releases/<ver>/swagger-<type>-model/api/manifest.json`:

```json
{
  "version": "26.1.1",
  "model": "swagger-oper-model",
  "generated": "2026-04-25T12:00:00Z",
  "spec_count": 199,
  "specs": [
    {
      "file": "Cisco-IOS-XE-bgp-oper.json",
      "module": "Cisco-IOS-XE-bgp-oper",
      "tree_url": "../../yang-trees/Cisco-IOS-XE-bgp-oper.html",
      "path_count": 412,
      "operation_count": 412,
      "has_mdt_xpaths": true
    }
  ]
}
```

CI (§9) verifies that `spec_count` matches the number of `*.json` spec files in the same folder and that every `tree_url` resolves to a file unless an exclusion is documented in `releases/<ver>/yang_accountability.json`.

## 8. Adding a new release — runbook

For maintainers adding the next IOS XE release (e.g. `26.2.1`):

1. **Fetch source YANG**:
   ```
   python scripts/fetch_yang_release.py --version 26.2.1 --yangmodels-path vendor/cisco/xe/2621
   ```
   Writes `references/26.2.1/` and an initial `releases/26.2.1/meta.json` with the pinned commit SHA.
2. **Build the release** (from a venv with `pyang` installed: the tree step runs `python -m pyang` and aborts if it is missing):
   ```
   python scripts/build_release.py --version 26.2.1 --skip-exports
   ```
   Generates all OpenAPI specs, pyang trees, manifests, accountability JSON, search index, telemetry index, MIB metadata, native capabilities and the XPath prefix map. Postman/Bruno archives are built at deploy time; run both export generators once locally to create the tracked `exports/{postman,bruno}-manifest.json`.
3. **Register in UI**: prepend the release entry to `releases/index.json`, add it to the `validate-releases` matrix in `deploy-pages.yml`, then run `python scripts/patch_viewers_version_aware.py` (refreshes the viewers' version allow-list), `python scripts/generate_platform_support.py` (needs the release's `yang-set-*.xml` under `references/yang/vendor/cisco/xe/<id>/`) and rebuild `release_counts.json` (`--write`), `version-stats.json`, `accountability_compare.json` and the release comparisons (`python scripts/build_release_compare.py`). If it should become the new default, set `default` and flip `default: true` on the entry.
4. **Verify locally**: `python scripts/audit_swagger_vs_tree.py --version 26.2.1` and `python scripts/validate_release.py --version 26.2.1` (the validator wraps all CI gates from §9 for local pre-flight).
5. **Update [CHANGELOG.md](CHANGELOG.md)**: add a row under "Versions Supported".
6. **Commit and push**: GitHub Actions runs the matrix build for every registered release; deployment is gated on all passing.

No edits to per-model HTML or shared JS are required to add a release. If a step fails, fix the underlying generator or skip-list — never bypass CI gates.

### 8.1 Make the new release the default (always: newest = default)

1. In `releases/index.json` set `default` to the new release and move `"default": true` to its entry. Leave `device_data` alone.
2. Regenerate the root copies of the default release: `python scripts/generate_search_index.py`, `python -X utf8 generators/generate_notifications_index.py --version <new>`, copy `releases/<new>/yang_accountability.json` to the root, then `python scripts/build_version_stats.py`, `python scripts/generate_platform_support.py` and `python scripts/patch_viewers_version_aware.py`.
3. Update the static fallbacks that show the default: `index.html` (`activeVersionLabel`, YANG source card, `version_label` stat), the `index-app.js` fallback option, the `about.html` stat fallbacks and release table, `yang-accountability.html` header version, and the README badge and stats.
4. Run the tests; `test_default_is_newest_release` fails until the default is the newest active release.

### 8.2 After upgrading the lab devices to a new release (device data)

Device data stays on the release the devices ran until it is re-collected:

1. Upgrade the devices, then `scripts/harness/kit.py onboard --all` (dry run) to confirm the APIs are still enabled.
2. Set `device_data` in `releases/index.json` to the new release. Every device-data tool follows it: specs walked, MDT xpaths, MIB catalog, live-data index, harness kit default.
3. Regenerate the catalogs for that release: `count_subscribable.py --dump output/subscribable-nodes.json` and `mib_catalog.py` (collector folder).
4. Collect everything: `kit.py telegraf start`, `kit.py collect` (all methods, all devices; add `--timeout 90 --window 35` for WAN devices), `kit.py coverage` until every device is COMPLETE. Or build a kit with `build_kit.py` and collect where the devices are.
5. Rebuild: `refresh_live_data.py` (writes `releases/<new>/live-examples-index.json`, `live-modules.json`, `live-data/`), `build_restconf_augment.py --from-ref HEAD`, `build_restconf_dataset.py`, then in the collector folder `build_live_dataset.py`, `build_netconf_dataset.py`, `build_gnmi_dataset.py`, `build_protocol_matrix.py`.
6. The previous release keeps its `releases/<old>/live-data/` and live examples, so its viewers keep showing what was captured on it.

## 9. CI gates (per release)

[.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml) runs the matrix `[17.9.x, 17.12.x, 17.15.x, 17.18.1, 26.1.1, 26.2.1]` and enforces:

1. **JSON validity** — every spec parses.
2. **Manifest accuracy** — `spec_count` equals `len(specs)` and matches actual file count on disk.
3. **Search-index integrity** — no duplicate module entries within a release.
4. **Tree coverage** — every spec has either a `tree_url` resolving to a real file or an entry in the release's accountability `excluded_modules` list with a reason (`types-only`, `deviation`, `augment`, `submodule`, `rpc-augment`, `framework`).
5. **Spec→tree linkage** — every spec whose tree was generated (`tree_audit.json`) has its `yang-trees/<module>.html` page (the viewers' "View YANG Tree" link), and every accountability `tree_url` resolves.
6. **MDT xpath sanity** (oper model only) — every operation marked `x-mdt-filter-xpath` matches the `^/[a-z0-9-]+:[A-Za-z0-9/_\-\[\]'=]+$` shape from [MDT_XPATH_SPEC.md](MDT_XPATH_SPEC.md).
7. **Export size cap** — every Postman/Bruno collection ≤ 50 MB; auto-split parts must be referenced from an exports manifest.
8. **Accountability regression guard** — total `with_specs` for the new release must be ≥ 95% of the prior release's count, unless the maintainer adds an entry to `releases/<ver>/known_removals.json` justifying the drop (e.g. upstream module retirement).

A failure in any gate fails the deploy. Bypass requires editing `known_removals.json` or the relevant skip-list with a justification — never disable the gate.

## 10. Out-of-scope (this phase)

- Pre-17.9 releases.
- Synthesizing intermediate patch levels per-version (we pin one patch per minor train).
- Cross-release "diff" UX beyond the 5-version matrix in the accountability comparison page.
- Backend services for live device probing.
