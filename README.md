# Cisco IOS-XE 17.18.1 OpenAPI/Swagger Documentation

[![IOS-XE Version](https://img.shields.io/badge/IOS--XE-17.18.1-blue)](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe-17/tsd-products-support-series-home.html)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.0-green)](https://swagger.io/specification/)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)
[![Modules](https://img.shields.io/badge/Modules-1317-brightgreen)](docs/PROJECT_SUMMARY.md)

Comprehensive OpenAPI 3.0 / Swagger documentation for Cisco IOS-XE 17.18.1 RESTCONF APIs. **Complete coverage with 1,317 specs (v1+v2), 43,649 paths, and 768 YANG tree files** for developer productivity.

🌐 **[View Live Documentation](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)**  
 **[Getting Started Guide](docs/GETTING_STARTED.md)**

## ✨ What's New - v2 Deep-Path Specifications

**Tree-based v2 generators** produce full-depth RESTCONF paths from resolved YANG trees. All 9 model types now have v2:

- 🆕 **Operational v2:** 205 specs, 20,159 paths (GET-only, up from 200 v1 specs)
- 🆕 **Config (CFG) v2:** 39 specs, 2,363 paths, 9,452 ops (3x depth vs v1)
- 🆕 **Native Config v2:** 81 specs, 3,363 paths, 13,452 ops (from 27 v1 specs)
- 🆕 **OpenConfig v2:** 57 specs, 2,377 paths, 5,920 ops (from 42 v1 specs)
- 🆕 **IETF v2:** 19 specs, 438 paths, 1,122 ops (mixed CRUD + RPC)
- 🆕 **MIB v2:** 149 specs, 12,482 paths (GET-only deep paths)
- 🆕 **RPC v2:** 48 specs, 232 RPCs (POST to /operations/)
- 🆕 **Events v2:** 38 specs, 861 paths (notifications + data endpoints)
- 🆕 **Other v2:** 9 specs, 1,374 paths, 4,593 ops (full CRUD)

**All 9 model categories documented (v1):**

- ✅ **Native Config:** 27 categories, 328 paths (1,307 operations with examples)
- ✅ **Operational Data:** 200 modules across 16 categories (4,196 paths)
- ✅ **Events:** 128 modules (40 YANG + 88 MIB) (455 notification paths)
- ✅ **RPC Operations:** 59 modules (51 Cisco + 7 IETF/Tailf) (311 operations)
- ✅ **IETF Standards:** 21 modules (552 paths)
- ✅ **OpenConfig:** 42 modules (2,063 paths)
- ✅ **MIB Translations:** 147 modules (visualizations for SNMP data)
- ✅ **Configuration:** 39 modules (815 paths)
- ✅ **Other Models:** 10 modules

**Key Features:**
-  **Comprehensive Docs** - Getting started guide with 15+ examples
- 🎯 **53 Logical Categories** - Organized by network engineer workflows
- 📊 **100% Accountability** - Every YANG module mapped and documented
- 🌳 **768 Tree Files** - Searchable YANG tree visualizations

📊 **[Read Project Summary](docs/PROJECT_SUMMARY.md)** for full details on enhancements.

## 📊 Quick Stats

| Metric | Count | Description |
|--------|-------|-------------|
| **OpenAPI Specs** | 1,317 | v1 (672) + v2 deep-path (645 specs across all 9 models) |
| **API Paths** | 43,649 | RESTCONF endpoints (v2 where available) |
| **Operations** | 68,273 | Total API operations |
| **YANG Modules** | 848 | Source modules |
| **Tree Files** | 768 | YANG/MIB visualizations |
| **Model Types** | 9 | Categories |
| **Coverage** | 79.2% | YANG modules with specs (672/848) |
| **Accountability** | 100% | All modules mapped |

## 🗂️ Model Categories

### ⭐ Primary Models (Categorized & Organized)

#### 📊 Native Configuration (27 categories, 328 paths, 1,307 operations)
Full CLI-equivalent configuration organized by network domain.
- **Categories:** Top-level leafs, containers, IP, IPv6, Router, Crypto, AAA, Line, VRF, Platform & System, Protocols, Security & Access, Switching L2, QoS, Monitor, License, Service, Other, App & Services, L2 Discovery, Routing & Multicast, Security Services, Platform & Diagnostics, WAN & Legacy, Industrial & IoT, Misc Extensions
- **Operations:** GET, PUT, PATCH, DELETE with complete YANG examples
- [Browse Native Config APIs →](swagger-native-config-model/)

#### 📈 Operational Data (200 modules, 16 categories, 4,196 paths)
Real-time device state and statistics. Read-only GET operations.
- **Categories:** interfaces, routing, platform, memory, qos, wireless, vpn, security, switching, environment, processes, sdwan, mpls, services, other
- [Browse Operational APIs →](swagger-oper-model/)

#### 🔔 Events (128 v1 modules, 38 v2 specs, 861 paths)
Event notification modules for YANG-Push telemetry and SNMP trap visualization.
- **YANG Events:** 40 Cisco-IOS-XE event modules
- **MIB Notifications:** 88 SNMP trap modules (view-only in Swagger)
- [Browse Events v2 APIs →](swagger-events-model/index-v2.html) | [v1 →](swagger-events-model/)

#### ⚡ RPC Operations (59 v1 modules, 48 v2 specs, 232 RPCs)
Remote procedure calls for device actions and commands.
- **Cisco RPCs:** 51 modules for device operations
- **IETF/Tailf:** 7 modules (ietf-event-notifications, tailf-netconf-extensions, tailf-netconf-query, and others)
- [Browse RPC v2 APIs →](swagger-rpc-model/index-v2.html) | [v1 →](swagger-rpc-model/)

### 📚 Standard Models (Original Structure)

#### ⚙️ Configuration (39 v1 + 39 v2 specs, 2,363 paths)
Device configuration with full CRUD operations.
- MDT subscriptions, gNMI config, wireless settings
- [Browse Config v2 APIs →](swagger-cfg-model/index-v2.html) | [v1 →](swagger-cfg-model/)

#### 🌍 OpenConfig (42 v1 + 57 v2 specs, 2,377 paths)
Vendor-neutral network configuration standards.
- Interfaces, BGP, OSPF, LLDP, MPLS, VLANs (no RPCs)
- [Browse OpenConfig v2 APIs →](swagger-openconfig-model/index-v2.html) | [v1 →](swagger-openconfig-model/)

#### 📜 IETF Standards (21 v1 + 19 v2 specs, 438 paths)
RFC-compliant IETF YANG models.
- ietf-interfaces, ietf-routing, ietf-netconf
- [Browse IETF v2 APIs →](swagger-ietf-model/index-v2.html) | [v1 →](swagger-ietf-model/)

#### 📡 MIB Translations (147 v1 + 149 v2 specs, 12,482 paths)
SNMP MIB modules with YANG tree visualizations.
- IF-MIB, CISCO-PROCESS-MIB, OSPF-MIB, Entity MIBs
- [Browse MIB v2 APIs →](swagger-mib-model/index-v2.html) | [v1 →](swagger-mib-model/)

#### 📦 Other Models (10 v1 + 9 v2 specs, 1,374 paths)
Standalone and vendor-specific modules.
- [Browse Other v2 APIs →](swagger-other-model/index-v2.html) | [v1 →](swagger-other-model/)
- [Browse Other APIs →](swagger-other-model/)

## 🚀 Quick Start

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

## 📚 API Examples

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

## 🔧 Development

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

## 📋 Project Structure

```
iosxe-1718-yang-swagger/
├── index.html                          # Main landing page
├── swagger-oper-model/                 # Operational (200 v1 + 205 v2 specs)
├── swagger-rpc-model/                  # RPC (59 v1 + 48 v2 specs)
├── swagger-cfg-model/                  # Config (39 v1 + 39 v2 specs)
├── swagger-openconfig-model/           # OpenConfig (42 v1 + 57 v2 specs)
├── swagger-ietf-model/                 # IETF (21 v1 + 19 v2 specs)
├── swagger-mib-model/                  # MIB (147 v1 + 149 v2 specs)
├── swagger-events-model/               # Events (128 v1 + 38 v2 specs)
├── swagger-native-config-model/        # Native (27 v1 + 81 v2 specs)
├── swagger-other-model/                # Other (10 v1 + 9 v2 specs)
├── generators/                         # Python YANG parsers
├── scripts/                            # Validation/analysis tools
└── references/17181-YANG-modules/      # 848 YANG sources
```

## 📄 Documentation

- [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) - Full requirements
- [YANG_MODULE_ACCOUNTABILITY.md](YANG_MODULE_ACCOUNTABILITY.md) - Module coverage
- [GITHUB_PAGES_DEPLOY.md](GITHUB_PAGES_DEPLOY.md) - Deployment guide

## 🔗 Resources

- [Cisco IOS-XE RESTCONF Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/m_1718_prog_restconf.html)
- [Cisco YANG Suite](https://developer.cisco.com/yangsuite/)
- [YANG Suite on GitHub](https://github.com/CiscoDevNet/yangsuite/)
- [YANG Models on GitHub](https://github.com/YangModels/yang)
- [OpenAPI Specification](https://swagger.io/specification/)

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger/issues)
- **DevNet**: [Cisco DevNet Community](https://community.cisco.com/t5/networking-developer-community/ct-p/5672j-dev-networking)
- **Author**: Jeremy Cohoe

---

**Last Updated**: March 2026 | **IOS-XE Version**: 17.18.1 | **OpenAPI**: 3.0.0