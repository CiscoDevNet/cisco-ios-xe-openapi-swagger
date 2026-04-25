# Changelog

All notable changes to this project. Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

The published site is versioned by IOS-XE release; the `Unreleased` section captures changes
not yet reflected in a tagged release of the upstream YANG models.

---

## [Unreleased]

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
