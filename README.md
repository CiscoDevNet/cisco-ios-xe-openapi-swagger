# Cisco IOS XE OpenAPI/Swagger Documentation

[![IOS XE Version](https://img.shields.io/badge/IOS--XE-26.2.1-blue)](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe-17/tsd-products-support-series-home.html)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.0-green)](https://swagger.io/specification/)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/)
[![Modules](https://img.shields.io/badge/Modules-1469-brightgreen)](docs/PROJECT_SUMMARY.md)

Comprehensive OpenAPI 3.0 / Swagger documentation for Cisco IOS XE RESTCONF APIs across multiple releases (17.9.x, 17.12.x, 17.15.x, 17.18.1, 26.1.1, 26.2.1). The site defaults to the newest release, 26.2.1, with **953 OpenAPI specs, 81,560 paths, and 758 tree files**. See the [API growth across releases](yang-accountability-compare.html) view for per-release counts.

**[View Live Documentation](https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/)**
 **[Getting Started Guide](docs/GETTING_STARTED.md)**

## Deep-Path Specifications

**Tree-based generators** produce full-depth RESTCONF paths from resolved YANG trees. All model types covered (counts shown for the default 26.2.1 release):

- **Operational:** 220 specs, 22,508 paths (GET-only read endpoints)
- **Configuration:** 44 specs, 2,449 paths, 9,622 ops (full CRUD)
- **Native Config:** 411 specs, 49,862 paths, 199,448 ops (full depth CRUD)
- **OpenConfig:** 43 specs, 1,062 paths, 3,930 ops (vendor-neutral)
- **IETF:** 20 specs, 419 paths, 1,392 ops (mixed CRUD + RPC)
- **MIB:** 147 specs, 4,272 paths (GET-only deep paths)
- **RPC:** 60 specs, 318 RPCs (POST to /operations/)
- **Notifications:** 133 modules, 506 notifications (Telemetry & Notifications catalog)
- **Other:** 8 specs, 670 paths, 1,534 ops (full CRUD)

**Key Features:**
-  **Comprehensive Docs** - Getting started guide with 15+ examples
- **53 Logical Categories** - Organized by network engineer workflows
- **100% Accountability** - Every YANG module mapped and documented
- **758 Tree Files** - Searchable YANG tree visualizations

**[Read Project Summary](docs/PROJECT_SUMMARY.md)** for full details on enhancements.

## Quick Stats (default release: 26.2.1)

| Metric | Count | Description |
|--------|-------|-------------|
| **OpenAPI Specs** | 953 | Deep-path specs across the 8 OpenAPI model types |
| **API Paths** | 81,560 | RESTCONF endpoints from resolved YANG trees |
| **Operations** | 243,024 | Total API operations |
| **Tracked Modules** | 1,469 | All tracked units (YANG + MIB + native config bundles) |
| **Modules with specs** | 949 | 64.6% coverage |
| **Tree Files** | 758 | YANG/MIB visualizations |
| **Model Types** | 8 + notifications | OpenAPI categories plus the notification catalog |
| **Releases covered** | 6 | 17.9.x → 26.2.1 |

For the per-release growth curve (specs/paths/operations across all 6 releases), see [yang-accountability-compare.html](yang-accountability-compare.html) on the live site or `version-stats.json` in this repo.

## Model Categories

### Primary Models (Categorized & Organized)

#### Native Configuration (411 specs, 49,862 paths, 199,448 operations)
Full CLI-equivalent configuration organized by network domain.
- **Categories:** Top-level leafs, containers, IP, IPv6, Router, Crypto, AAA, Line, VRF, Platform & System, Protocols, Security & Access, Switching L2, QoS, Monitor, License, Service, Other, App & Services, L2 Discovery, Routing & Multicast, Security Services, Platform & Diagnostics, WAN & Legacy, Industrial & IoT, Misc Extensions
- **Operations:** GET, PUT, PATCH, DELETE with complete YANG examples
- [Browse Native Config APIs →](swagger-native-config-model/)

#### Operational Data (220 specs, 22,508 paths)
Real-time device state and statistics. Read-only GET operations.
- **Categories:** interfaces, routing, platform, memory, qos, wireless, vpn, security, switching, environment, processes, sdwan, mpls, services, other
- [Browse Operational APIs →](swagger-oper-model/)

#### Event Notifications (Notification Catalog)
YANG-Push event notifications and SNMP traps, with realistic payloads and consumption guidance.
The former Events Swagger viewer was retired (its `/streams` endpoints are not callable on a device).
- [Browse the Notification Catalog →](telemetry.html#notifications)

#### RPC Operations (60 specs, 318 RPCs)
Remote procedure calls for device actions and commands.
- **Cisco RPCs** for device operations (including the 26.2.1 config-management RPCs)
- **IETF/Tailf** modules (ietf-event-notifications, tailf-netconf-extensions, tailf-netconf-query, and others)
- [Browse RPC APIs →](swagger-rpc-model/)

### Standard Models (Original Structure)

#### Configuration (44 specs, 2,449 paths)
Device configuration with full CRUD operations.
- MDT subscriptions, gNMI config, wireless settings
- [Browse Config APIs →](swagger-cfg-model/)

#### OpenConfig (43 specs, 1,062 paths)
Vendor-neutral network configuration standards.
- Interfaces, BGP, OSPF, LLDP, MPLS, VLANs (no RPCs)
- [Browse OpenConfig APIs →](swagger-openconfig-model/)

#### IETF Standards (20 specs, 419 paths)
RFC-compliant IETF YANG models.
- ietf-interfaces, ietf-routing, ietf-netconf
- [Browse IETF APIs →](swagger-ietf-model/)

#### MIB Translations (147 specs, 4,272 paths)
SNMP MIB modules with YANG tree visualizations.
- IF-MIB, CISCO-PROCESS-MIB, OSPF-MIB, Entity MIBs
- [Browse MIB APIs →](swagger-mib-model/)

#### Other Models (8 specs, 670 paths)
Standalone and vendor-specific modules.
- [Browse Other APIs →](swagger-other-model/)

## Recent Improvements

- **Dark mode everywhere, WCAG AA contrast** — every page, including the ~4,200 YANG tree pages, follows the dark/light toggle; text and white-on-colour buttons meet 4.5:1 in both themes (tokens in [assets/css/site.css](assets/css/site.css)).
- **Link integrity** — tree pages, the 404 page and generated docs were fixed; [tests/test_internal_links.py](tests/test_internal_links.py) checks every static link in every published page, and release validation gate 5 checks every viewer and accountability tree link.
- **26.2.1 is the default release** — the site always opens on the newest release; device data comes from the release the lab runs (`device_data` in [releases/index.json](releases/index.json), 26.1.1 today). See [VERSIONING.md §8.1–8.2](VERSIONING.md).
- **What Changed Between Releases** — [release-compare.html](release-compare.html) (hub → More → What Changed) lists, for each adjacent release pair, the YANG modules added, removed and changed, with a per-module tree diff. Built from the pyang trees by [scripts/build_release_compare.py](scripts/build_release_compare.py).
- **Portable data-collection harness** — [scripts/build_kit.py](scripts/build_kit.py) packages an offline kit (collectors, Telegraf, Python wheels) that onboards devices, collects RESTCONF / NETCONF / gNMI / MDT, reports coverage per device and returns a secret-scanned bundle; [scripts/import_harness_bundle.py](scripts/import_harness_bundle.py) imports it here. See [DEVICE_DATA_COLLECTION.md §14](DEVICE_DATA_COLLECTION.md).
- **Device Data browser** — [device-data.html](device-data.html) shows *real* data collected from 7 lab platforms (Catalyst 9200/9300/9400/9500/9600, a 9300 8-member stack and a 9800 WLC) over every transport, chosen with a selector: **Model-Driven Telemetry** (push · gRPC), **RESTCONF** (GET), **NETCONF** (get, get-config, subscribe) and **gNMI** (Get, Subscribe). Secrets (keys, passwords, SNMP communities) are masked before publishing. One UI for all of them — per device (PID), model flavor, and path, with the actual streamed keys/values and GET payloads, plus summary charts and copy-to-clipboard. To keep the OpenAPI specs lean, response bodies are **not** injected into the specs; they are served on demand as per-path data files (`releases/<ver>/live-data/<category>/<module>/<hash>.json`), while each spec keeps only its synthetic schema example. An in-viewer banner links to the browser. See [scripts/build_restconf_dataset.py](scripts/build_restconf_dataset.py), [scripts/build_live_examples_index.py](scripts/build_live_examples_index.py), and the [CHANGELOG](CHANGELOG.md).
- **Realistic write-operation examples** — Every POST/PUT/PATCH body across the spec set ships with a complete, RFC 7951–compliant payload. No more empty `{}` placeholders. See [scripts/enrich_v2_specs.py](scripts/enrich_v2_specs.py) and the [CHANGELOG](CHANGELOG.md).
- **Deep-link URLs** — Sharing a search result, module, or spec URL now opens the right view. Hash patterns: `#search=<q>`, `#module=<name>`, `#spec=<model>/<name>`.
- **CSP-hardened frontend** — All inline JS extracted to external files; `script-src 'self' cdn.jsdelivr.net`.
- **Live-device validation script** — [scripts/validate_examples_c9kv.py](scripts/validate_examples_c9kv.py) verifies examples against a real Catalyst 9000V (or any IOS XE 17.18.1+ device).

## Quick Start

### View Online
Visit [https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/](https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/)

### Test Locally
```bash
# Clone repository
git clone https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger.git
cd cisco-ios-xe-openapi-swagger

# Start local server
python -m http.server 8000

# Open browser to http://localhost:8000
```

### Use the OpenAPI Specs
```bash
# Download a specific spec (replace 26.2.1 with the release you want)
curl -O https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/releases/26.2.1/swagger-oper-model/api/Cisco-IOS-XE-interfaces-oper.json

# Generate Python client
openapi-generator-cli generate -i Cisco-IOS-XE-interfaces-oper.json -g python -o ./python-client
```

## API Examples

### Python RESTCONF Example
```python
import requests
from requests.auth import HTTPBasicAuth

base_url = "https://sandbox-iosxe-latest-1.cisco.com/restconf"
auth = HTTPBasicAuth('developer', 'C1sco12345')

# Get interface statistics
response = requests.get(
    f"{base_url}/data/Cisco-IOS-XE-interfaces-oper:interfaces",
    headers={"Accept": "application/yang-data+json"},
    auth=auth,
    verify=False
)
print(response.json())
```

## Development

### Prerequisites
- Python 3.12 with pyang 2.7 (the repo uses `.venv-harness/`)
- YANG sources for the release under `references/<ver>/` (see [VERSIONING.md §8](VERSIONING.md))

### Regenerate a Release
```bash
# Trees, all spec categories, notifications, prefix map, enrichment, search,
# accountability and exports for one release
python scripts/build_release.py --version 26.2.1

# Resume or re-run selected steps
python scripts/build_release.py --version 26.2.1 --only trees,prefix-map

# Release gates (JSON, manifests, search index, tree coverage + links, MDT xpaths, export sizes)
python scripts/validate_release.py --version 26.2.1

# Tests (CI runs the same)
python -m pytest tests scripts/harness/tests
```

## Project Structure

```
cisco-ios-xe-openapi-swagger/
├── index.html, *.html                  # Hub and tool pages (Device Data, Telemetry, What Changed, ...)
├── swagger-<category>-model/           # 8 Swagger UI viewers (specs are read from releases/<ver>/)
├── releases/
│   ├── index.json                      # Releases, default (26.2.1) and device_data (26.1.1)
│   ├── <ver>/swagger-*-model/api/      # OpenAPI specs per release
│   ├── <ver>/yang-trees/               # pyang tree pages per release
│   ├── <ver>/live-data/                # Captured device responses (device_data release)
│   └── compare/                        # Release-to-release differences
├── assets/                             # Shared CSS (site, viewer, tree-page themes), JS, vendored Swagger UI
├── generators/                         # Spec generators (YANG trees → OpenAPI)
├── scripts/                            # Release pipeline, validation, device-data builders
├── scripts/harness/                    # Device data collection harness and portable kit
├── tests/                              # pytest suite (links, secrets, release data, generators)
└── references/<ver>/                   # YANG sources per release (not published)
```

## Documentation

- [AGENTS.md](AGENTS.md) — AI agent guide (build/run, conventions, pitfalls, common tasks)
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution workflow
- [CHANGELOG.md](CHANGELOG.md) — Release history
- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) — RESTCONF API consumer guide (curl, Python, JS)
- [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) — Completion summary by phase
- [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) — Architecture decisions, full requirements
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) — Known fixes, common APIs, support links
- [YANG_MODULE_ACCOUNTABILITY.md](YANG_MODULE_ACCOUNTABILITY.md) — Module-by-module coverage
- [DEVICE_DATA_COLLECTION.md](DEVICE_DATA_COLLECTION.md) — Device data collection harness and portable kit
- [VERSIONING.md](VERSIONING.md) — Multi-release architecture and the add-a-release runbook
- [GITHUB_PAGES_DEPLOY.md](GITHUB_PAGES_DEPLOY.md) — Deployment workflow details

## Resources

- [Cisco IOS XE RESTCONF Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/m_1718_prog_restconf.html)
- [Cisco YANG Suite](https://developer.cisco.com/yangsuite/)
- [YANG Suite on GitHub](https://github.com/CiscoDevNet/yangsuite/)
- [YANG Models on GitHub](https://github.com/YangModels/yang)
- [OpenAPI Specification](https://swagger.io/specification/)

## Contact

- **Issues**: [GitHub Issues](https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger/issues)
- **DevNet**: [Cisco DevNet](https://developer.cisco.com/)
- **Author**: Jeremy Cohoe

---

**Last Updated**: October 2026 | **Default IOS XE release**: 26.2.1 (6 releases, 17.9.x to 26.2.1) | **OpenAPI**: 3.0.0
