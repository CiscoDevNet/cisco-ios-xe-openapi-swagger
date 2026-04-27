# Cisco IOS-XE OpenAPI/Swagger Documentation

[![IOS-XE Version](https://img.shields.io/badge/IOS--XE-26.1.1-blue)](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe-17/tsd-products-support-series-home.html)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.0-green)](https://swagger.io/specification/)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)
[![Modules](https://img.shields.io/badge/Modules-608-brightgreen)](docs/PROJECT_SUMMARY.md)

Comprehensive OpenAPI 3.0 / Swagger documentation for Cisco IOS-XE RESTCONF APIs across multiple releases (17.9.x, 17.12.x, 17.15.x, 17.18.1, 26.1.1). The site defaults to the newest release (26.1.1) with **608 OpenAPI specs, 37,072 paths, and 765 YANG tree files**. See the [API growth across releases](yang-accountability-compare.html) view for per-release counts.

**[View Live Documentation](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)**
 **[Getting Started Guide](docs/GETTING_STARTED.md)**

## Deep-Path Specifications

**Tree-based generators** produce full-depth RESTCONF paths from resolved YANG trees. All 9 model types covered (counts shown for the default 26.1.1 release):

- **Operational:** 216 specs, 22,144 paths (GET-only read endpoints)
- **Configuration:** 41 specs, 2,559 paths, 10,083 ops (full CRUD)
- **Native Config:** 29 specs, 4,932 paths, 19,728 ops (full depth CRUD)
- **OpenConfig:** 43 specs, 778 paths, 2,904 ops (vendor-neutral)
- **IETF:** 22 specs, 505 paths, 1,664 ops (mixed CRUD + RPC)
- **MIB:** 148 specs, 4,272 paths (GET-only deep paths)
- **RPC:** 57 specs, 302 RPCs (POST to /operations/)
- **Events:** 43 specs, 910 paths (notifications + data endpoints)
- **Other:** 9 specs, 670 paths, 1,534 ops (full CRUD)

**Key Features:**
-  **Comprehensive Docs** - Getting started guide with 15+ examples
- **53 Logical Categories** - Organized by network engineer workflows
- **100% Accountability** - Every YANG module mapped and documented
- **767 Tree Files** - Searchable YANG tree visualizations

**[Read Project Summary](docs/PROJECT_SUMMARY.md)** for full details on enhancements.

## Quick Stats (default release: 26.1.1)

| Metric | Count | Description |
|--------|-------|-------------|
| **OpenAPI Specs** | 608 | Deep-path specs across all 9 models |
| **API Paths** | 37,072 | RESTCONF endpoints from resolved YANG trees |
| **Operations** | 63,541 | Total API operations |
| **YANG Modules (tracked)** | 1,125 | All modules (YANG + spec-only) |
| **Modules with specs** | 702 | 62.4% coverage |
| **Tree Files** | 765 | YANG/MIB visualizations |
| **Model Types** | 9 | Categories |
| **Releases covered** | 5 | 17.9.x → 26.1.1 |

For the per-release growth curve (specs/paths/operations across all 5 releases), see [yang-accountability-compare.html](yang-accountability-compare.html) on the live site or `version-stats.json` in this repo.

## Model Categories

### Primary Models (Categorized & Organized)

#### Native Configuration (81 specs, 3,363 paths, 13,452 operations)
Full CLI-equivalent configuration organized by network domain.
- **Categories:** Top-level leafs, containers, IP, IPv6, Router, Crypto, AAA, Line, VRF, Platform & System, Protocols, Security & Access, Switching L2, QoS, Monitor, License, Service, Other, App & Services, L2 Discovery, Routing & Multicast, Security Services, Platform & Diagnostics, WAN & Legacy, Industrial & IoT, Misc Extensions
- **Operations:** GET, PUT, PATCH, DELETE with complete YANG examples
- [Browse Native Config APIs →](swagger-native-config-model/)

#### Operational Data (205 modules, 20,159 paths)
Real-time device state and statistics. Read-only GET operations.
- **Categories:** interfaces, routing, platform, memory, qos, wireless, vpn, security, switching, environment, processes, sdwan, mpls, services, other
- [Browse Operational APIs →](swagger-oper-model/)

#### Events (38 specs, 861 paths)
Event notification modules for YANG-Push telemetry and SNMP trap visualization.
- **YANG Events:** 40 Cisco-IOS-XE event modules
- **MIB Notifications:** 88 SNMP trap modules (view-only in Swagger)
- [Browse Events APIs →](swagger-events-model/)

#### RPC Operations (59 specs, 232 RPCs)
Remote procedure calls for device actions and commands.
- **Cisco RPCs:** 51 modules for device operations
- **IETF/Tailf:** 7 modules (ietf-event-notifications, tailf-netconf-extensions, tailf-netconf-query, and others)
- [Browse RPC APIs →](swagger-rpc-model/)

### Standard Models (Original Structure)

#### Configuration (39 specs, 2,363 paths)
Device configuration with full CRUD operations.
- MDT subscriptions, gNMI config, wireless settings
- [Browse Config APIs →](swagger-cfg-model/)

#### OpenConfig (57 specs, 2,377 paths)
Vendor-neutral network configuration standards.
- Interfaces, BGP, OSPF, LLDP, MPLS, VLANs (no RPCs)
- [Browse OpenConfig APIs →](swagger-openconfig-model/)

#### IETF Standards (19 specs, 438 paths)
RFC-compliant IETF YANG models.
- ietf-interfaces, ietf-routing, ietf-netconf
- [Browse IETF APIs →](swagger-ietf-model/)

#### MIB Translations (149 specs, 12,482 paths)
SNMP MIB modules with YANG tree visualizations.
- IF-MIB, CISCO-PROCESS-MIB, OSPF-MIB, Entity MIBs
- [Browse MIB APIs →](swagger-mib-model/)

#### Other Models (9 specs, 1,374 paths)
Standalone and vendor-specific modules.
- [Browse Other APIs →](swagger-other-model/)

## Recent Improvements

- **Realistic write-operation examples** — Every POST/PUT/PATCH body across the spec set ships with a complete, RFC 7951–compliant payload. No more empty `{}` placeholders. See [scripts/enrich_v2_specs.py](scripts/enrich_v2_specs.py) and the [CHANGELOG](CHANGELOG.md).
- **Deep-link URLs** — Sharing a search result, module, or spec URL now opens the right view. Hash patterns: `#search=<q>`, `#module=<name>`, `#spec=<model>/<name>`.
- **CSP-hardened frontend** — All inline JS extracted to external files; `script-src 'self' cdn.jsdelivr.net`.
- **Live-device validation script** — [scripts/validate_examples_c9kv.py](scripts/validate_examples_c9kv.py) verifies examples against a real Catalyst 9000V (or any IOS-XE 17.18.1+ device).

## Quick Start

### View Online
Visit [https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)

### Test Locally
```bash
# Clone repository
git clone https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger.git
cd cisco-ios-xe-openapi-swagger

# Start local server
python -m http.server 8000

# Open browser to http://localhost:8000
```

### Use the OpenAPI Specs
```bash
# Download a specific spec
curl -O https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-oper-model/api/Cisco-IOS-XE-interfaces-oper.json

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
- Python 3.8+
- pyang (`pip install pyang`)

### Regenerate Specifications
```bash
cd generators

# Run all generators
python generate_oper_openapi_v2.py
python generate_rpc_openapi_v2.py
python generate_cfg_openapi_v2.py
python generate_openconfig_openapi_v2.py
python generate_ietf_openapi_v2.py
python generate_mib_openapi_v2.py
python generate_events_openapi.py
python generate_native_openapi_v2.py
python generate_other_openapi_v2.py

# Validate quality
cd ..
python scripts/validate_quality.py

# Generate accountability report
python scripts/analyze_yang_accountability.py
```

## Project Structure

```
iosxe-1718-yang-swagger/
├── index.html                          # Main landing page
├── swagger-oper-model/                 # Operational (205 specs)
├── swagger-rpc-model/                  # RPC (59 specs)
├── swagger-cfg-model/                  # Config (39 specs)
├── swagger-openconfig-model/           # OpenConfig (57 specs)
├── swagger-ietf-model/                 # IETF (19 specs)
├── swagger-mib-model/                  # MIB (149 specs)
├── swagger-events-model/               # Events (38 specs)
├── swagger-native-config-model/        # Native (81 specs)
├── swagger-other-model/                # Other (9 specs)
├── generators/                         # Python YANG parsers
├── scripts/                            # Validation/analysis tools
└── references/17181-YANG-modules/      # 848 YANG sources
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
- [GITHUB_PAGES_DEPLOY.md](GITHUB_PAGES_DEPLOY.md) — Deployment workflow details

## Resources

- [Cisco IOS-XE RESTCONF Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/m_1718_prog_restconf.html)
- [Cisco YANG Suite](https://developer.cisco.com/yangsuite/)
- [YANG Suite on GitHub](https://github.com/CiscoDevNet/yangsuite/)
- [YANG Models on GitHub](https://github.com/YangModels/yang)
- [OpenAPI Specification](https://swagger.io/specification/)

## Contact

- **Issues**: [GitHub Issues](https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger/issues)
- **DevNet**: [Cisco DevNet Community](https://community.cisco.com/t5/networking-developer-community/ct-p/5672j-dev-networking)
- **Author**: Jeremy Cohoe

---

**Last Updated**: March 2026 | **IOS-XE Version**: 17.18.1 | **OpenAPI**: 3.0.0