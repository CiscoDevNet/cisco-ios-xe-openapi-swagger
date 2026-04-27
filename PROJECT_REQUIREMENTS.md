# Cisco IOS-XE YANG Documentation Hub
## Project Requirements, Architecture & Decisions

**Version:** 3.0
**Date:** April 25, 2026
**IOS-XE Versions Supported:** 17.9.x, 17.12.x, 17.15.x, 17.18.1, 26.1.1
**Author:** Jeremy Cohoe (jcohoe@cisco.com)
**Repository:** [github.com/jeremycohoe/cisco-ios-xe-openapi-swagger](https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger)
**Live Site:** [jeremycohoe.github.io/cisco-ios-xe-openapi-swagger](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)

> **Companion documents (binding):**
> - [VERSIONING.md](VERSIONING.md) — multi-release folder layout, URL contract, CI gates, release-add runbook.
> - [MDT_XPATH_SPEC.md](MDT_XPATH_SPEC.md) — MDT/gRPC dial-out filter xpath rule and OpenAPI extensions.
> - [../MIBS.md](../MIBS.md) — MIB coverage and platform applicability.
> - [../telemetry-reference.md](../telemetry-reference.md) — per-feature telemetry subscription metadata.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Design Decisions](#2-architecture--design-decisions)
3. [Module Categories & Classification](#3-module-categories--classification)
4. [Native Config Model Design](#4-native-config-model-design)
5. [Events Model Design](#5-events-model-design)
6. [OpenAPI Spec Structure](#6-openapi-spec-structure)
7. [Project File Structure](#7-project-file-structure)
8. [YANG Tree Visualizations](#8-yang-tree-visualizations)
9. [Quality Enhancements](#9-quality-enhancements)
10. [External Resources & Links](#10-external-resources--links)
11. [Scripts & Generators](#11-scripts--generators)
12. [Deployment](#12-deployment)
13. [Statistics & Metrics](#13-statistics--metrics)
14. [Changelog & Git History](#14-changelog--git-history)
15. [Known Gaps & Future Work](#15-known-gaps--future-work)

---

## 1. Project Overview

### Purpose

Generate comprehensive OpenAPI 3.0 specifications from Cisco IOS-XE 17.18.1 YANG models to provide interactive Swagger UI documentation for RESTCONF API operations. The project serves as a one-stop documentation hub for all IOS-XE programmability interfaces.

### Goals

1. Create OpenAPI specs for **all applicable YANG modules** (672 total)
2. Provide interactive **Swagger UI** for API exploration and testing
3. Maintain **100% accountability** for every YANG module (documented or excluded with reason)
4. Organize specs into **9 model categories** aligned with network engineer workflows
5. Support both local development and **GitHub Pages** deployment
6. Provide **YANG tree visualizations** for every module with specs (767 tree files)

### Source Materials

| Source | Location | Count |
|--------|----------|-------|
| YANG Modules | [YangModels/yang - vendor/cisco/xe/17181](https://github.com/YangModels/yang/tree/main/vendor/cisco/xe/17181) | 848 files |
| MIB YANG Modules | Subset of above | 147 files |
| Swagger UI Framework | [swagger-api/swagger-ui](https://github.com/swagger-api/swagger-ui/releases) v5.11.0 (CDN) | - |

---

## 2. Architecture & Design Decisions

### Decision: Static GitHub Pages Site

**Rationale:** No server-side processing needed. All specs are pre-generated JSON files served via CDN. This ensures:
- Zero hosting costs
- Global CDN distribution
- No authentication or backend dependencies
- Version-controlled documentation via Git

### Decision: Per-Module OpenAPI Specs (Not Monolithic)

**Rationale:** Each YANG module gets its own `.json` spec file rather than combining everything into one massive file. This ensures:
- Fast loading times in Swagger UI (individual specs are 5KB–50KB instead of 100MB+)
- Granular module-level browsing
- Easy diffing and version control

### Decision: 9 Model Categories

**Rationale:** YANG modules naturally group by their suffix and purpose:

| Category | Selection Criteria | HTTP Methods |
|----------|--------------------|-------------|
| Operational (`*-oper`) | Suffix `-oper.yang`, read-only state | GET only |
| Configuration (`*-cfg`) | Suffix `-cfg.yang`, writable config | GET, PUT, PATCH, DELETE |
| RPC (`*-rpc`) | Suffix `-rpc.yang` or contains `rpc` statements | POST only |
| Events (`*-events`) | Suffix `-events.yang` or notification modules | Schema-only (no HTTP ops) |
| Native Config | `Cisco-IOS-XE-native.yang` augments | GET, PUT, PATCH, DELETE |
| OpenConfig (`openconfig-*`) | Prefix `openconfig-` | GET, PUT, PATCH, DELETE |
| IETF (`ietf-*`, `iana-*`) | Prefix `ietf-` or `iana-` | Varies by module |
| MIB (`*-MIB`, `*-mib`) | SNMP MIB translations to YANG | GET only |
| Other | Doesn't fit above patterns | Varies |

### Decision: Manifest-Based Index Pages

Each model folder has an `api/manifest.json` that drives the sub-model `index.html` page:

```json
{
  "total_modules": 200,
  "total_paths": 4222,
  "total_operations": 4222,
  "modules": ["Cisco-IOS-XE-aaa-oper", "Cisco-IOS-XE-acl-oper", ...]
}
```

The `modules` array contains **plain strings** (module names). The JavaScript in each `index.html` reads `manifest.total_paths` and `manifest.total_operations` directly — it does **not** try to reduce/sum from the modules array.

### Decision: CDN Swagger UI (Not Local)

**Rationale:** Using `unpkg.com/swagger-ui-dist@5.11.0` CDN instead of hosting a local copy of the Swagger UI JavaScript. The `swagger-ui-5.11.0/` folder exists for reference but is not used at runtime. This reduces repo size and ensures the latest patches.

### Decision: Standardized Server URLs

All specs use a parameterized server URL pointing to the Cisco DevNet Always-On Sandbox:

```json
"servers": [{
  "url": "https://{device}/restconf",
  "variables": {
    "device": {
      "default": "devnetsandboxiosxec9k.cisco.com",
      "description": "Device IP or hostname"
    }
  }
}]
```

**Decision:** Use `devnetsandboxiosxec9k.cisco.com` as the default — it's the publicly accessible Always-On IOS-XE sandbox that requires no reservation.

### Decision: All External Links Point to `developer.cisco.com/iosxe`

The old URL `developer.cisco.com/docs/ios-xe` is a redirect. All 474 occurrences across the project were updated to `developer.cisco.com/iosxe` (commit `868f13f`).

### Decision: RESTCONF Guide URL

The correct RESTCONF programmability guide URL is:
```
https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/m_1718_prog_restconf.html
```

This is the official Cisco.com documentation for RESTCONF on IOS-XE 17.18.

---

## 3. Module Categories & Classification

### Swagger-ized Categories (672 modules with specs)

| Category | Swagger Folder | Specs | Paths | Operations | Description |
|----------|----------------|-------|-------|------------|-------------|
| **Operational** | `swagger-oper-model/` | 200 | 4,222 | 4,222 | Real-time state data (GET only) |
| **MIB** | `swagger-mib-model/` | 147 | 4,272 | 4,272 | SNMP MIB translations to YANG |
| **Events** | `swagger-events-model/` | 128 | 455 | 455 | Notification schemas (40 YANG + 88 MIB) |
| **RPC** | `swagger-rpc-model/` | 58 | 290 | 290 | Remote procedure calls (POST) |
| **OpenConfig** | `swagger-openconfig-model/` | 42 | 2,063 | 7,482 | Vendor-neutral models (CRUD) |
| **Configuration** | `swagger-cfg-model/` | 39 | 815 | 2,722 | Config data (CRUD) |
| **Native Config** | `swagger-native-config-model/` | 27 | 328 | 1,307 | Native IOS-XE config hierarchy |
| **IETF** | `swagger-ietf-model/` | 21 | 553 | 1,836 | RFC standard models |
| **Other** | `swagger-other-model/` | 10 | 842 | 2,148 | Miscellaneous models |
| **TOTAL** | | **672** | **13,840** | **24,734** | |

### Excluded Categories (176 modules — no specs generated)

| Category | Count | Reason |
|----------|-------|--------|
| **Types** (`*-types.yang`) | ~80 | Type definitions only — no data nodes or operations |
| **Deviation** (`*-deviation*.yang`, `*-devs.yang`) | ~98 | Modify other modules' constraints — no standalone endpoints |
| **Common** (`*-common*.yang`) | ~17 | Shared groupings/typedefs, no endpoints |
| **Infrastructure** (`tailf-*.yang`, `cisco-semver.yang`) | ~8 | Build/version infrastructure |
| **Deprecated** | ~5 | Marked obsolete in YANG |

**Total YANG Modules:** 848  
**With Specs:** 672 (79.2% of total, 100% of data-bearing modules)  
**Excluded:** 176 (all non-data-bearing)

### Module Accountability

Every single YANG module is tracked in `yang-accountability.json` (6,006 lines) with:
- Module name, category, assigned swagger folder
- Whether it has a spec (`has_spec: true/false`)
- Exclusion reason if applicable

The interactive accountability report is viewable at `yang-accountability.html`.

---

## 4. Native Config Model Design

### The Problem

`Cisco-IOS-XE-native.yang` is a monolithic model with 163+ augment sub-modules. Unlike other categories where each module maps 1:1 to a spec, the native model must be decomposed into logical categories.

### The Solution: 27 Category Specs

The native config model is split into 27 OpenAPI specs based on functional groupings:

| Spec File | Description |
|-----------|-------------|
| `native-00-top-level-containers.json` | Top-level containers (hostname, version, etc.) |
| `native-00-top-level-leafs.json` | Top-level leaf nodes |
| `native-aaa.json` | Authentication, Authorization, Accounting |
| `native-app-services.json` | Application services (NBAR, IP SLA, etc.) |
| `native-crypto.json` | Cryptographic configuration |
| `native-industrial-iot.json` | Industrial IoT protocols |
| `native-intf-ethernet.json` | Ethernet interfaces |
| `native-intf-service.json` | Service instances |
| `native-intf-virtual.json` | Virtual interfaces (Loopback, Tunnel, BDI, etc.) |
| `native-intf-wan.json` | WAN interfaces (Serial, Cellular, etc.) |
| `native-ip.json` | IP configuration (addressing, routing, NAT) |
| `native-l2-discovery.json` | L2 discovery protocols (CDP, LLDP) |
| `native-line.json` | Line (console, VTY) configuration |
| `native-misc-ext.json` | Miscellaneous extensions |
| `native-other.json` | Remaining native containers (~82 containers) |
| `native-platform-diag.json` | Platform diagnostics |
| `native-platform-system.json` | Platform and system configuration |
| `native-policy.json` | Policy maps and class maps |
| `native-protocols.json` | Routing protocols (OSPF, BGP, EIGRP, etc.) |
| `native-qos-policy.json` | QoS and queuing |
| `native-router.json` | Router-level configuration |
| `native-routing-multicast.json` | Multicast routing |
| `native-security-access.json` | Security and access control |
| `native-security-services.json` | Security services (UTD, Umbrella, etc.) |
| `native-switching-l2.json` | Layer 2 switching |
| `native-vrf.json` | VRF configuration |
| `native-wan-legacy.json` | Legacy WAN technologies |

**Totals:** 328 paths, 1,307 operations (each path supports GET/PUT/PATCH/DELETE)

### Known Gap: `kron` Module

`Cisco-IOS-XE-kron.yang` (job/event scheduling) is the only significant native augment not covered. It was identified during audit but not included in the original Swagger generation batch. Related but different modules (`event` = EEM, `scheduler` = CPU allocation) are documented.

### Native Augment Coverage

- **Documented:** 162/163 augment modules (99.4%)
- **Missing:** `kron` (1 module)
- **Operational-only (no config YANG):** `lldp`, `macsec`, `trustsec` — these have oper specs instead

---

## 5. Events Model Design

### The Problem

Event/notification modules don't have traditional RESTCONF operations. They define notification schemas for model-driven telemetry subscriptions.

### The Solution

128 event specs document the notification schemas with:
- **40 YANG notification modules** (Cisco-IOS-XE-*-events, ietf-*-notifications, etc.)
- **88 MIB trap modules** (CISCO-*-MIB trap definitions translated to YANG)

Each spec includes the notification schema definitions derived from the YANG model paths, with `total_paths` and `total_operations` both set to the notification count (455 total).

### Events Manifest

The events manifest uses the same format as other models:
```json
{
  "total_modules": 128,
  "total_paths": 455,
  "total_operations": 455,
  "modules": ["BGP4-MIB", "BRIDGE-MIB", ...]
}
```

**Important:** The JavaScript reads `manifest.total_paths` and `manifest.total_operations` (not `manifest.total_notifications` which does not exist).

---

## 6. OpenAPI Spec Structure

### Standard Spec Format

Every spec follows this structure:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Module-Name",
    "description": "YANG description + category + path count + YANG GitHub link + tree link",
    "version": "17.18.1"
  },
  "servers": [{ "url": "https://{device}/restconf", "variables": {...} }],
  "externalDocs": {
    "description": "Cisco IOS-XE Programmability Guide",
    "url": "https://developer.cisco.com/iosxe/"
  },
  "security": [{ "basicAuth": [] }],
  "paths": {
    "/data/Module-Name:container": {
      "get": {
        "summary": "Get container",
        "description": "Description of the endpoint",
        "operationId": "get-container-0",
        "tags": ["Module-Name"],
        "responses": {
          "200": { "description": "Success", "content": {...} },
          "401": { "description": "Unauthorized" },
          "404": { "description": "Resource not found" }
        }
      }
    }
  },
  "components": {
    "schemas": { ... },
    "securitySchemes": {
      "basicAuth": { "type": "http", "scheme": "basic" }
    }
  }
}
```

### Completeness Requirements (100% achieved)

Every operation in every spec has:
- `operationId` — unique identifier (24,734 total)
- `tags` — at least one tag per operation
- `description` — meaningful description
- `summary` — concise summary
- `responses` — proper response schemas for GET operations

Every spec has:
- `externalDocs` — link to Cisco DevNet
- `security` — basicAuth scheme defined
- `servers` — parameterized RESTCONF URL

### YANG List Key Parameters

For YANG list nodes, the OpenAPI path includes key parameters:

```json
"/data/Module:container/list={key1},{key2}": {
  "get": {
    "parameters": [
      { "name": "key1", "in": "path", "required": true, "schema": { "type": "string" } },
      { "name": "key2", "in": "path", "required": true, "schema": { "type": "string" } }
    ]
  }
}
```

**8,466 key parameters** were added across 5,434 keyed paths in 264 specs (commit `2df4c78`).

---

## 7. Project File Structure

```
cisco-ios-xe-openapi-swagger/
├── index.html                          # Main landing page (917 lines)
├── tree-compare.html                   # YANG tree comparison tool
├── yang-accountability.html            # Module accountability report
├── code-generator.html                 # Code snippet generator (legacy, de-linked)
├── 404.html                            # Custom error page
├── .nojekyll                           # GitHub Pages config
├── README.md                           # Project README
├── PROJECT_REQUIREMENTS.md             # This document
├── QUICK_REFERENCE.md                  # Quick reference card
│
├── swagger-oper-model/                 # 200 operational specs
│   ├── index.html                      # Swagger UI browser for this category
│   └── api/
│       ├── manifest.json               # Module registry (200 modules)
│       └── *.json                      # 200 spec files
│
├── swagger-cfg-model/                  # 39 configuration specs
│   ├── index.html
│   └── api/
│       ├── manifest.json
│       └── *.json                      # 39 spec files
│
├── swagger-rpc-model/                  # 58 RPC specs
│   ├── index.html
│   └── api/
│       ├── manifest.json
│       └── *.json                      # 58 spec files
│
├── swagger-events-model/               # 128 event notification specs
│   ├── index.html
│   └── api/
│       ├── manifest.json
│       └── *.json                      # 128 spec files
│
├── swagger-native-config-model/        # 27 native config category specs
│   ├── index.html
│   └── api/
│       ├── manifest.json
│       └── *.json                      # 27 spec files
│
├── swagger-openconfig-model/           # 42 OpenConfig specs
│   ├── index.html
│   └── api/
│       ├── manifest.json
│       └── *.json                      # 42 spec files
│
├── swagger-ietf-model/                 # 21 IETF/IANA specs
│   ├── index.html
│   └── api/
│       ├── manifest.json
│       └── *.json                      # 21 spec files
│
├── swagger-mib-model/                  # 147 MIB specs
│   ├── index.html
│   └── api/
│       ├── manifest.json
│       └── *.json                      # 147 spec files
│
├── swagger-other-model/                # 10 miscellaneous specs
│   ├── index.html
│   └── api/
│       ├── manifest.json
│       └── *.json                      # 10 spec files
│
├── yang-trees/                         # YANG tree visualizations
│   ├── tree-manifest.json              # Array of 767 module names
│   └── *.html                          # 767 tree HTML files
│
├── generators/                         # OpenAPI generators (Python)
│   ├── generate_oper_openapi_v2.py     # Operational model generator
│   ├── generate_cfg_openapi_v2.py      # Configuration model generator
│   ├── generate_rpc_openapi_v2.py      # RPC model generator
│   ├── generate_events_openapi.py      # Events model generator
│   ├── generate_native_openapi_v2.py   # Native config generator
│   ├── generate_openconfig_openapi_v2.py
│   ├── generate_ietf_openapi_v2.py
│   ├── generate_mib_openapi_v2.py
│   ├── generate_other_openapi_v2.py
│   ├── generate_combined_*.py          # Combined view generators (6 files)
│   └── generate_examples.py            # Example value generator
│
├── scripts/                            # 46 utility/enhancement scripts
│   ├── add_operation_ids.py            # Added 5,939 operationIds
│   ├── add_top_tags.py                 # Added tags to 149 specs
│   ├── add_descriptions.py            # Added 982 descriptions
│   ├── add_external_docs.py            # Added externalDocs to 672 specs
│   ├── add_key_params.py              # Added 8,466 list key parameters
│   ├── fix_server_urls.py             # Standardized 252 server URLs
│   ├── fix_broken_refs.py             # Fixed 122 broken $ref schemas
│   ├── fix_get_responses.py           # Fixed 5 GET response schemas
│   ├── fix_devnet_urls.py             # Replaced 474 old DevNet URLs
│   ├── fix_examples.py               # Fixed 2,048 placeholder values
│   ├── generate_missing_trees.py      # Generated 48 tree HTML files
│   ├── generate_pyang_trees.py        # pyang-based tree generation
│   ├── audit_quality.py              # Quality audit tool
│   ├── validate_quality.py           # Validation tool
│   └── ... (32 more utility scripts)
│
├── docs/                               # Documentation
│   ├── GETTING_STARTED.md              # Getting started guide (744 lines)
│   ├── PROJECT_SUMMARY.md             # Project summary (548 lines)
│   └── ...
│
├── references/                         # Source YANG modules
│   └── 17181-YANG-modules/            # 848 YANG files
│
├── .github/
│   └── workflows/
│       └── deploy-pages.yml           # GitHub Pages CI/CD
│
├── archive/                            # Archived/superseded files
│
└── swagger-ui-5.11.0/                 # Swagger UI (reference, CDN used)
    └── dist/
```

---

## 8. YANG Tree Visualizations

### Overview

Every module with an OpenAPI spec also has a YANG tree visualization — an HTML page showing the hierarchical structure of the YANG model's data nodes.

### Statistics

- **767 tree HTML files** in `yang-trees/`
- **tree-manifest.json** — flat JSON array of module names that have trees
- **100% coverage** — all 672 spec modules have tree files (plus extras for sub-modules)

### Tree Generation

- **717 trees** generated using `pyang -f tree` from original YANG source files
- **48 trees** synthetically generated from API spec paths (for modules where pyang wasn't run: 17 OpenConfig name mismatches, 3 IETF gaps, 1 Other, 27 Native Config)
- **2 additional trees** from MIB-specific generation

### Tree HTML Format

Each tree HTML file includes:
- Styled tree output with expandable sections
- Links to: YANG source on GitHub, YANG Catalog, DevNet Guide
- Module name, description, and revision date
- Responsive design matching the main site theme

### Tree Links in Specs

Every spec's `info.description` field includes a link to its tree visualization:
```
YANG Tree: View Module-Name structure
(link to: https://jeremycohoe.github.io/.../yang-trees/Module-Name.html)
```

Specs where no tree file exists have the tree link hidden (21 broken links were fixed in commit `9daa75d`).

---

## 9. Quality Enhancements

### Enhancement Timeline (Commits)

| Commit | Date | Enhancement | Impact |
|--------|------|-------------|--------|
| `cce6350` | Feb 2026 | Replace 2,048 placeholder values with realistic data | All specs |
| `2df4c78` | Feb 2026 | Add 8,466 YANG list key parameters to 5,434 paths | 264 specs |
| `2958d2d` | Feb 2026 | Add YANG-derived schemas to 128 event specs | 128 specs |
| `0a51587` | Feb 2026 | Enhance 83 specs with +6,777 YANG-aligned paths | 83 specs |
| `4386177` | Feb 2026 | 100% completeness: operationIds, tags, descriptions, externalDocs | All 672 specs |
| `495ce62` | Feb 2026 | Server URLs, broken $refs, tree links, navigation | 252+ specs |
| `9b1bcbd` | Feb 2026 | Generate 48 missing YANG tree files | 48 files |
| `868f13f` | Feb 2026 | Update all DevNet URLs (474 occurrences) | 473 files |
| `cb22832` | Feb 2026 | Add YANG Suite links, fix RESTCONF guide URL | 5 files |

### Quality Scorecard (All 100%)

| Metric | Count | Coverage |
|--------|-------|----------|
| Specs with `operationId` | 24,734 / 24,734 | 100% |
| Specs with `tags` | 24,734 / 24,734 | 100% |
| Specs with `description` | 24,734 / 24,734 | 100% |
| Specs with `summary` | 24,734 / 24,734 | 100% |
| Specs with `externalDocs` | 672 / 672 | 100% |
| Specs with `security` | 672 / 672 | 100% |
| GET responses with schemas | 13,512 / 13,512 | 100% |
| Tree file coverage | 672 / 672 | 100% |
| Module accountability | 848 / 848 | 100% |

### Broken $ref Fixes

122 broken schema `$ref` pointers were identified and fixed (commit `495ce62`). These were cross-module references that pointed to non-existent schema definitions.

### Placeholder Value Fixes

2,048 placeholder/incorrect example values (e.g., `"string"`, `0`, `true`) were replaced with YANG-aligned realistic values such as actual IP addresses, interface names, and protocol-appropriate defaults (commit `cce6350`).

---

## 10. External Resources & Links

### Links Used Across the Project

| Resource | URL | Used In |
|----------|-----|---------|
| Cisco DevNet IOS-XE | `https://developer.cisco.com/iosxe/` | All 672 specs (`externalDocs`), index.html |
| IOS-XE RESTCONF Guide | `https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/m_1718_prog_restconf.html` | index.html, README, QUICK_REFERENCE |
| Cisco YANG Suite | `https://developer.cisco.com/yangsuite/` | index.html, README, QUICK_REFERENCE, GETTING_STARTED |
| YANG Suite GitHub | `https://github.com/CiscoDevNet/yangsuite/` | index.html, README, QUICK_REFERENCE |
| YANG Catalog | `https://yangcatalog.org/yang-search/` | index.html, tree HTML files |
| YANG Source Files | `https://github.com/YangModels/yang/tree/main/vendor/cisco/xe/17181` | index.html, spec descriptions |
| OpenConfig | `https://www.openconfig.net/` | index.html |
| IETF RFCs | `https://www.rfc-editor.org/` | index.html |
| DevNet Sandbox | `devnetsandboxiosxec9k.cisco.com` | All 672 specs (server URL default) |

### Deprecated Links (Removed)

| Old URL | Status | Replaced With |
|---------|--------|---------------|
| `developer.cisco.com/docs/ios-xe/` | Redirect | `developer.cisco.com/iosxe/` |
| `developer.cisco.com/docs/ios-xe/#!restconf-api-overview` | Redirect | Cisco.com RESTCONF guide |
| `developer.cisco.com/docs/ios-xe/#!working-with-restconf` | Redirect | Cisco.com RESTCONF guide |
| `developer.cisco.com/docs/ios-xe/#!yang-models` | Redirect | `developer.cisco.com/iosxe/` |
| Code Generator (`code-generator.html`) | Removed from navigation | Still exists as file but de-linked |

---

## 11. Scripts & Generators

### Generators (`generators/` — 17 files)

Per-category OpenAPI generators that parse YANG files and produce spec JSON:

| Generator | Output | Description |
|-----------|--------|-------------|
| `generate_oper_openapi_v2.py` | 200 specs | Operational data modules |
| `generate_cfg_openapi_v2.py` | 39 specs | Configuration modules |
| `generate_rpc_openapi_v2.py` | 58 specs | RPC/action modules |
| `generate_events_openapi.py` | 128 specs | Event notification modules |
| `generate_native_openapi_v2.py` | 27 specs | Native config categories |
| `generate_openconfig_openapi_v2.py` | 42 specs | OpenConfig modules |
| `generate_ietf_openapi_v2.py` | 21 specs | IETF/IANA modules |
| `generate_mib_openapi_v2.py` | 147 specs | MIB translation modules |
| `generate_other_openapi_v2.py` | 10 specs | Miscellaneous modules |
| `generate_combined_*.py` (6 files) | Combined views | Multi-module combined specs |
| `generate_examples.py` | Examples | Realistic example values |

### Enhancement Scripts (`scripts/` — 46 files)

Scripts that enhance, fix, and validate specs post-generation:

**Adding content:**
- `add_operation_ids.py` — Added 5,939 operationIds to 204 specs
- `add_top_tags.py` — Added tags to 149 specs
- `add_descriptions.py` — Added 982 descriptions to 14 specs
- `add_external_docs.py` — Added `externalDocs` to all 672 specs
- `add_key_params.py` — Added 8,466 YANG list key parameters
- `add_yang_tree_links.py` — Added tree visualization links to spec descriptions
- `add_yang_github_links.py` — Added YANG source links

**Fixing issues:**
- `fix_server_urls.py` — Standardized 252 server URLs
- `fix_broken_refs.py` — Fixed 122 broken `$ref` schemas
- `fix_get_responses.py` — Fixed 5 GET response schemas
- `fix_devnet_urls.py` — Replaced 474 old DevNet URLs
- `fix_examples.py` — Replaced 2,048 placeholder values
- `fix_quality.py` — General quality fixes

**Auditing/analysis:**
- `audit_quality.py` — Comprehensive quality audit
- `audit_refs.py` / `audit_refs_detail.py` — Schema reference auditing
- `audit_examples.py` — Example value auditing
- `audit_keys.py` — YANG list key parameter auditing
- `audit_swagger_vs_tree.py` — Verify tree coverage matches specs
- `analyze_yang_accountability.py` — Module accountability analysis
- `validate_quality.py` — Final validation
- `count_totals.py` — Count all paths/operations across specs

**Tree generation:**
- `generate_pyang_trees.py` — pyang-based tree generation (717 trees)
- `generate_mib_pyang_trees.py` — MIB-specific tree generation
- `generate_missing_trees.py` — Synthetic tree generation from API paths (48 trees)

---

## 12. Deployment

### GitHub Pages (Production)

The site is deployed via GitHub Pages from the `main` branch:

**CI/CD:** `.github/workflows/deploy-pages.yml` handles automatic deployment on push to `main`.

**URL:** `https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/`

**Requirements:**
- `.nojekyll` file in root (disables Jekyll processing)
- All paths are relative (no absolute filesystem paths)
- All resources loaded via CDN or relative URLs

### Local Development

```bash
# Clone the repository
git clone https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger.git
cd cisco-ios-xe-openapi-swagger

# Serve locally (any static HTTP server works)
python -m http.server 8000
# Access: http://localhost:8000
```

### Regenerating Specs

```bash
# Prerequisites: Python 3.x, YANG source files in references/17181-YANG-modules/

# Generate specs for each category
cd generators
python generate_oper_openapi_v2.py
python generate_rpc_openapi_v2.py
python generate_cfg_openapi_v2.py
python generate_openconfig_openapi_v2.py
python generate_ietf_openapi_v2.py
python generate_mib_openapi_v2.py
python generate_events_openapi.py
python generate_native_openapi_v2.py
python generate_other_openapi_v2.py

# Run quality enhancements
cd ../scripts
python add_operation_ids.py
python add_top_tags.py
python add_descriptions.py
python add_external_docs.py
python add_key_params.py
python fix_server_urls.py
python fix_broken_refs.py
```

---

## 13. Statistics & Metrics

### Final Project Numbers

| Metric | Value |
|--------|-------|
| **OpenAPI Specs** | 672 |
| **API Paths** | 13,840 |
| **API Operations** | 24,734 |
| **YANG Modules (Total)** | 848 |
| **YANG Modules (With Specs)** | 672 (79.2%) |
| **YANG Modules (Excluded)** | 176 (non-data-bearing) |
| **Module Accountability** | 100% (848/848) |
| **YANG Tree Files** | 767 |
| **Model Categories** | 9 |
| **OperationIds** | 24,734 (100% coverage) |
| **List Key Parameters** | 8,466 across 5,434 paths |
| **Enhancement Scripts** | 46 Python files |
| **Generators** | 17 Python files |
| **Git Commits** | 30+ |

### Per-Model Breakdown

| Model | Modules | Paths | Operations | Avg Paths/Module |
|-------|---------|-------|------------|-----------------|
| Operational | 200 | 4,222 | 4,222 | 21.1 |
| MIB | 147 | 4,272 | 4,272 | 29.1 |
| Events | 128 | 455 | 455 | 3.6 |
| RPC | 58 | 290 | 290 | 5.0 |
| OpenConfig | 42 | 2,063 | 7,482 | 49.1 |
| Configuration | 39 | 815 | 2,722 | 20.9 |
| Native Config | 27 | 328 | 1,307 | 12.1 |
| IETF | 21 | 553 | 1,836 | 26.3 |
| Other | 10 | 842 | 2,148 | 84.2 |

### Operations by HTTP Method (Approximate)

| Method | Usage | Categories |
|--------|-------|-----------|
| **GET** | ~13,840 | All categories (read operations) |
| **PUT** | ~4,500 | cfg, openconfig, ietf, native, other |
| **PATCH** | ~4,500 | cfg, openconfig, ietf, native, other |
| **DELETE** | ~1,600 | cfg, openconfig, ietf, native, other |
| **POST** | ~290 | RPC only |

---

## 14. Changelog & Git History

| Version | Commit | Date | Changes |
|---------|--------|------|---------|
| 2.0 | `cb22832` | Feb 11, 2026 | Add YANG Suite links, fix RESTCONF guide URL, remove Code Generator navigation |
| 1.9 | `868f13f` | Feb 11, 2026 | Update all 474 DevNet URLs from `/docs/ios-xe` to `/iosxe` across 473 files |
| 1.8 | `fe60e35` | Feb 10, 2026 | Fix Events page stats (was reading non-existent `total_notifications`) |
| 1.7 | `6c7e041` | Feb 10, 2026 | Fix stats display in Other, MIB, and Native Config index pages (JS bugs) |
| 1.6 | `9b1bcbd` | Feb 2026 | Generate 48 missing YANG tree files for 100% coverage (765→767 entries) |
| 1.5 | `4386177` | Feb 2026 | 100% spec completeness: operationIds, tags, descriptions, externalDocs, response schemas |
| 1.4 | `495ce62` | Feb 2026 | Server URL standardization (252 specs), broken $ref fixes (122), tree link fixes (21), stale docs |
| 1.3 | `9daa75d` | Feb 2026 | Fix 21 broken YANG tree links (hide link when no tree exists) |
| 1.2 | `2df4c78` | Feb 2026 | Add 8,466 YANG list key parameters to 5,434 keyed paths in 264 specs |
| 1.1 | `cce6350` | Feb 2026 | Replace 2,048 placeholder values with realistic YANG-aligned data |
| 1.0 | Various | Jan–Feb 2026 | Initial generation of all 672 specs, landing page, documentation |

---

## 15. Known Gaps & Future Work

### Known Gaps

1. **`kron` module** — `Cisco-IOS-XE-kron.yang` (job/event scheduling) is the only significant native augment without a Swagger spec (1 of 163 augments)
2. **`code-generator.html`** — File still exists in repo but is no longer linked from navigation (removed in `cb22832`)
3. **`yang-accountability.json` counts** — Shows 403 modules with specs (outdated from when it was generated); actual count is 672

### Potential Future Enhancements

| Phase | Enhancement | Description |
|-------|-------------|-------------|
| Phase 8 | Model consolidation | Consolidate cfg/ietf/openconfig/mib into category-based views |
| Phase 9 | Postman collections | Auto-generate Postman collections from OpenAPI specs |
| Phase 10 | CI/CD testing | Automated endpoint testing against DevNet sandbox |
| Phase 11 | Version tracking | Support multiple IOS-XE versions with diff capability |

---

## 16. Multi-Release Phase (April 2026)

This section captures the requirements added in the April 2026 expansion. The detailed contracts live in companion documents; this section is an index and binding requirement set.

### 16.1 Versions

The site simultaneously serves five IOS-XE releases under the same GitHub Pages URL: **17.9.x, 17.12.x, 17.15.x, 17.18.1, 26.1.1**. The version selector at the top of every page switches all per-release data (specs, trees, search, accountability, exports). Folder layout, URL contract, and the runbook for adding additional releases are defined in [VERSIONING.md](VERSIONING.md).

**Requirement:** Adding a new IOS-XE release must be a mechanical operation (fetch → build → register → push), not a code change.

### 16.2 Pyang tree completeness

Every OpenAPI spec on every release must either link to a pyang tree HTML file or have a documented exclusion reason in that release's accountability JSON. A consolidated generator (`scripts/generate_all_pyang_trees.py`) produces trees for all modules of a release in one pass; CI fails the build on any uncovered spec. The spec→tree link is stored as `info.x-yang-tree-url` and rendered in every model viewer.

### 16.3 Accountability across releases

Each release ships its own machine-readable `releases/<ver>/yang_accountability.json` and a re-rendered `YANG_MODULE_ACCOUNTABILITY.md` section. A new comparison page (`yang-accountability-compare.html`) renders a per-module 5-version matrix sourced from `accountability_compare.json`. CI fails on regressions in `with_specs` count vs the prior release unless an entry is added to `releases/<ver>/known_removals.json`.

### 16.4 MDT / gRPC dial-out filter xpaths

Operational-model specs annotate operations with `x-mdt-filter-xpath`, `x-mdt-tier`, `x-mdt-cadence-seconds`, `x-mdt-encoding`, `x-mdt-on-change-capable`, and `x-mdt-feature-section`. The xpath construction rule is `/<module-prefix>:<container-path>` (see [MDT_XPATH_SPEC.md](MDT_XPATH_SPEC.md)). Three UI surfaces consume this data: per-operation Swagger UI badge, per-viewer MDT panel, and a global `telemetry.html` browser. The annotation source of truth is `telemetry-reference.md` joined with the active release's pyang trees.

### 16.5 Cisco-IOS-XE-native v2 enhancements

The native config model (the largest and most complex YANG module in the source set) ships these enhancements in addition to the existing 28 category specs:

1. **Tier-1 discovery spec** (`native-00-top-level-complete.json`) — ~100 top-level containers/leafs with `x-related-spec` cross-links to category specs. Loads in <1s.
2. **Depth-3 representative paths** for high-value categories (interfaces by type, BGP per address family, OSPF per process, ISIS, ACL types).
3. **`x-cli-equivalent` extension** on top operations, sourced from `references/native-cli-mappings.yaml`. Initial coverage ~200 mappings; extends iteratively.
4. **Canonical example payloads** generated from YANG defaults plus a curated overlay (`references/native-example-overlay.yaml`); replaces residual empty `{}` examples.
5. **Config Capabilities summary page** (`swagger-native-config-model/capabilities.html`) — leaf/list/choice counts per category; configurable-surface map; sourced from `releases/<ver>/native-capabilities.json`.

### 16.6 MIB YANG detail surfacing

Each MIB YANG module ships enriched metadata in `releases/<ver>/mib-metadata.json` (OID prefix, table/scalar counts, indexes, deprecated objects, RFC/Cisco source, platform applicability joined from [../MIBS.md](../MIBS.md)). The MIB viewer renders this in a side card alongside the active spec and links to the matching pyang tree. Platform applicability comes from the structured parse of `MIBS.md` (no manual duplication).

### 16.7 Postman + Bruno exports

Exports are emitted **per (version, model-category)**, with a hard 50 MB cap per file. Both Postman (`*.postman_collection.json`) and Bruno (`*.bru` directory tree) formats are produced for every release. A new `exports.html` page renders the version × category × format download matrix. CI fails on any single file exceeding 50 MB without an auto-split manifest entry.

### 16.8 Source-of-truth doc set (locked)

The following documents form the binding contract for this and future releases. Code changes that affect their subjects must update them first.

- [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) (this file)
- [VERSIONING.md](VERSIONING.md)
- [MDT_XPATH_SPEC.md](MDT_XPATH_SPEC.md)
- [AGENTS.md](AGENTS.md)
- [../MIBS.md](../MIBS.md)
- [../telemetry-reference.md](../telemetry-reference.md)
- [CHANGELOG.md](CHANGELOG.md)

### 16.9 Resolved review blockers

The three "Must-Fix Blockers" from [../CODE_REVIEW.md](../CODE_REVIEW.md) (XSS in `search.js`, localStorage silent-fail in `recent-favorites.js`, search-index race condition) are resolved as of this version. See the Resolution Status banner in CODE_REVIEW.md.

---

## Reference Standards

| Standard | URL |
|----------|-----|
| RESTCONF (RFC 8040) | https://datatracker.ietf.org/doc/html/rfc8040 |
| YANG (RFC 7950) | https://datatracker.ietf.org/doc/html/rfc7950 |
| YANG NACM (RFC 8341) | https://datatracker.ietf.org/doc/html/rfc8341 |
| OpenAPI 3.0 Specification | https://spec.openapis.org/oas/v3.0.0 |

## Tools

| Tool | URL | Usage |
|------|-----|-------|
| pyang | https://github.com/mbj4668/pyang | YANG parsing, tree generation |
| Swagger UI | https://swagger.io/tools/swagger-ui/ | Interactive API documentation |
| Cisco YANG Suite | https://developer.cisco.com/yangsuite/ | YANG model exploration and testing |
| YANG Suite GitHub | https://github.com/CiscoDevNet/yangsuite/ | Source and Docker setup |
