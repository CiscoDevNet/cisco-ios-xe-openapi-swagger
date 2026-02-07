# Cisco IOS-XE 17.18.1 OpenAPI/Swagger Documentation

[![IOS-XE Version](https://img.shields.io/badge/IOS--XE-17.18.1-blue)](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe-17/tsd-products-support-series-home.html)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.0-green)](https://swagger.io/specification/)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)
[![Modules](https://img.shields.io/badge/Modules-641-brightgreen)](docs/PROJECT_SUMMARY.md)

Comprehensive OpenAPI 3.0 / Swagger documentation for Cisco IOS-XE 17.18.1 RESTCONF APIs. **Complete coverage with 641 modules, 53 categories, 717 YANG tree files, and interactive code generation** for developer productivity.

🌐 **[View Live Documentation](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)**  
🛠️ **[Code Generator Tool](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/code-generator.html)**  
📖 **[Getting Started Guide](docs/GETTING_STARTED.md)**

## ✨ What's New - Complete API Coverage

**All 9 model categories have been systematically documented:**

- ✅ **Native Config:** 18 categories, 172 paths (644 operations with examples)
- ✅ **Operational Data:** 199 modules across 16 categories (2,652 paths)
- ✅ **Events:** 117 modules (38 YANG + 79 MIB) (658 notification paths)
- ✅ **RPC Operations:** 60 modules (57 Cisco + 3 IETF/Tailf) (311 operations)
- ✅ **IETF Standards:** 21 modules (592 paths)
- ✅ **OpenConfig:** 41 modules (772 paths)
- ✅ **MIB Translations:** 147 modules (visualizations for SNMP data)
- ✅ **Configuration:** 39 modules (612 paths)
- ✅ **Other Models:** 10 modules

**Key Features:**
- 🔧 **Code Generator** - Auto-generate curl, Python, and Ansible code
- 📚 **Comprehensive Docs** - Getting started guide with 15+ examples
- 🎯 **53 Logical Categories** - Organized by network engineer workflows
- 📊 **100% Accountability** - Every YANG module mapped and documented
- 🌳 **717 Tree Files** - Searchable YANG tree visualizations

📊 **[Read Project Summary](docs/PROJECT_SUMMARY.md)** for full details on enhancements.

## 📊 Quick Stats

| Metric | Count | Description |
|--------|-------|-------------|
| **OpenAPI Specs** | 641 | Generated specifications |
| **API Paths** | 5,769 | RESTCONF endpoints (excl. MIB) |
| **Operations** | 10,000+ | Total API operations |
| **YANG Modules** | 848 | Source modules |
| **Tree Files** | 717 | YANG/MIB visualizations |
| **Model Types** | 9 | Categories |
| **Coverage** | 75.6% | YANG modules with specs (641/848) |
| **Accountability** | 100% | All modules mapped |

## 🗂️ Model Categories

### ⭐ Primary Models (Categorized & Organized)

#### 📊 Native Configuration (18 categories, 172 paths, 644 operations)
Full CLI-equivalent configuration organized by network domain.
- **Categories:** Top-level leafs, containers, IP, IPv6, Router, Crypto, AAA, Line, VRF, Platform & System, Protocols, Security & Access, Switching L2, QoS, Monitor, License, Service, Other
- **Operations:** GET, PUT, PATCH, DELETE with complete YANG examples
- [Browse Native Config APIs →](swagger-native-config-model/)

#### 📈 Operational Data (199 modules, 16 categories, 2,652 paths)
Real-time device state and statistics. Read-only GET operations.
- **Categories:** interfaces, routing, platform, memory, qos, wireless, vpn, security, switching, environment, processes, sdwan, mpls, services, other
- **Quick-Starts:** troubleshooting, performance, inventory
- [Browse Operational APIs →](swagger-oper-model/)

#### 🔔 Events (117 modules: 38 YANG + 79 MIB, 658 notification paths)
Event notification modules for YANG-Push telemetry and SNMP trap visualization.
- **YANG Events:** 38 Cisco-IOS-XE event modules
- **MIB Notifications:** 79 SNMP trap modules (view-only in Swagger)
- [Browse Events APIs →](swagger-events-model/)

#### ⚡ RPC Operations (60 modules, 311 operations)
Remote procedure calls for device actions and commands.
- **Cisco RPCs:** 57 modules for device operations
- **IETF/Tailf:** 3 modules (ietf-event-notifications, tailf-netconf-extensions, tailf-netconf-query)
- [Browse RPC APIs →](swagger-rpc-model/)

### 📚 Standard Models (Original Structure)

#### ⚙️ Configuration (39 modules, 612 paths)
Device configuration with full CRUD operations.
- MDT subscriptions, gNMI config, wireless settings
- [Browse Config APIs →](swagger-cfg-model/)

#### 🌍 OpenConfig (41 modules, 772 paths)
Vendor-neutral network configuration standards.
- Interfaces, BGP, OSPF, LLDP, MPLS, VLANs (no RPCs)
- [Browse OpenConfig APIs →](swagger-openconfig-model/)

#### 📜 IETF Standards (21 modules, 592 paths)
RFC-compliant IETF YANG models.
- ietf-interfaces, ietf-routing, ietf-netconf
- [Browse IETF APIs →](swagger-ietf-model/)

#### 📡 MIB Translations (147 modules)
SNMP MIB modules with YANG tree visualizations.
- IF-MIB, CISCO-PROCESS-MIB, OSPF-MIB, Entity MIBs
- [Browse MIB APIs →](swagger-mib-model/)

#### 📦 Other Models (10 modules)
Standalone and vendor-specific modules.
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
├── swagger-oper-model/                 # Operational (199 modules)
├── swagger-rpc-model/                  # RPC (53 modules)
├── swagger-cfg-model/                  # Config (39 modules)
├── swagger-openconfig-model/           # OpenConfig (41 modules)
├── swagger-ietf-model/                 # IETF (21 modules)
├── swagger-mib-model/                  # MIB (147 modules)
├── swagger-events-model/               # Events (38 modules)
├── swagger-native-config-model/        # Native (28 modules)
├── swagger-other-model/                # Other (8 modules)
├── swagger-ui-5.11.0/                  # Swagger UI framework
├── generators/                         # Python YANG parsers
├── scripts/                            # Validation/analysis tools
└── references/17181-YANG-modules/      # 848 YANG sources
```

## 📄 Documentation

- [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) - Full requirements
- [YANG_MODULE_ACCOUNTABILITY.md](YANG_MODULE_ACCOUNTABILITY.md) - Module coverage
- [GITHUB_PAGES_DEPLOY.md](GITHUB_PAGES_DEPLOY.md) - Deployment guide

## 🔗 Resources

- [Cisco IOS-XE RESTCONF Guide](https://developer.cisco.com/docs/ios-xe/#!restconf-api-overview)
- [YANG Models on GitHub](https://github.com/YangModels/yang)
- [OpenAPI Specification](https://swagger.io/specification/)

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger/issues)
- **DevNet**: [Cisco DevNet Community](https://community.cisco.com/t5/networking-developer-community/ct-p/5672j-dev-networking)
- **Author**: Jeremy Cohoe

---

**Last Updated**: February 2026 | **IOS-XE Version**: 17.18.1 | **OpenAPI**: 3.0.0