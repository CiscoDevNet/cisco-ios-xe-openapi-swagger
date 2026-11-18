# 0004 — OpenConfig specs from the pyang-resolved schema (21 data modules, augments included)

- Status: accepted
- Date: 2026-11-18
- Component: versioning
- Commit/PR: (this change)

## Context
The regex-based `generate_openconfig_openapi_v2.py` never followed `uses` or `augment` when
building paths, so specs were thin (openconfig-interfaces 12 paths vs 142 schema containers;
openconfig-system 3 vs 111) and missed every augment (ethernet, subinterfaces, ipv4, AAA,
logging). It also emitted a spec for every `openconfig-*.yang` file: 22 of the 43 were for
grouping/augment-only modules (openconfig-bgp, -isis, -aaa, -if-ethernet, ...) whose paths,
such as `/data/openconfig-bgp:bgp`, do not exist on a device. 19 of 43 failed OpenAPI
validation (path templates without parameters). Found while expanding OpenConfig over gNMI.

## Decision
- `generators/generate_openconfig_from_yang.py` replaces it: pyang loads the release's
  OpenConfig YANG with the generic Cisco `cisco-xe-openconfig-*` ext/deviation modules
  (`generators/_openconfig_schema.py`, shared with the gNMI node catalog).
- One spec per module with top-level data (21 on 26.2.1, 20 on 26.1.1, 19 on 17.18.1). Every
  container and list is a path; lists get a collection path and an item path with **all**
  keys as declared path parameters; augmented segments are RFC 8040 module-qualified
  (`.../interface={name}/openconfig-if-ethernet:ethernet`); body members follow RFC 7951.
  Config nodes get GET/PUT/PATCH/DELETE, `config false` nodes GET only. Output follows the
  cfg/oper tree-generator format (wrapped body schemas, examples).
- Spec-less OpenConfig modules are explained, not left as gaps: the generator writes
  `augment_only_modules` (module -> specs carrying its nodes, following grouping origins) into
  the manifest and the accountability analyzer uses it as `reason_excluded`. MPLS and segment
  routing are removed by Cisco deviations (hand reasons in `patch_excluded_reasons.REASONS`).

## Alternatives rejected
- Patch the regex generator to follow augments: it cannot resolve groupings across modules or
  apply deviations without re-implementing pyang.
- Keep the 22 grouping-module specs as reference stubs: their paths are invalid on a device
  (user chose the clean replacement).
- Inline schemas without a depth cap: openconfig-network-instance grows past 12 MB; schema depth
  4 / example depth 3 (same as cfg) keeps it at 11.5 MB, with an automatic step-down above 12 MB.

## Consequences
- Spec counts per release drop by 22–24 (OpenConfig 43 -> 19–21) while paths rise
  (26.2.1: 1,892 paths); `release_counts.json` was rebaselined.
- Rebuilding one category: the per-spec post-processors (enrich, github-links, wrap-body-schemas,
  ...) are **not idempotent** on already-processed specs (they duplicate examples and re-encode
  text). Run them, restore every other category's spec folder from git, then rebuild the
  aggregates (accountability, search-index, paths-index, platform-api-counts, path-depth-audit,
  exports). `paths-index` also rewrites other categories' `_paths_index.json` (older indexer
  drift); restore those too.
- The deprecations census links specs through accountability: re-running `build_deprecations.py`
  on this VM changes `content_sha256` / `yangmodels_path` (different YANG checkout), so only the
  changed `spec_url` values were applied.
