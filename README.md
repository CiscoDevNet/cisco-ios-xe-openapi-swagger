# Cisco IOS-XE 17.18.1 OpenAPI/Swagger Documentation

[![IOS-XE Version](https://img.shields.io/badge/IOS--XE-17.18.1-blue)](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe-17/tsd-products-support-series-home.html)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.0-green)](https://swagger.io/specification/)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)
[![Enhanced](https://img.shields.io/badge/Enhanced-4%20Models-brightgreen)](docs/PROJECT_SUMMARY.md)

Comprehensive OpenAPI 3.0 / Swagger documentation for Cisco IOS-XE 17.18.1 RESTCONF APIs. **Enhanced with 53 categories, 6 quick-starts, and interactive code generation** for developer productivity.

🌐 **[View Live Documentation](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/)**  
🛠️ **[Code Generator Tool](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/code-generator.html)**  
📖 **[Getting Started Guide](docs/GETTING_STARTED.md)**

## ✨ What's New - Enhanced Models

**4 models have been reorganized and enhanced for better usability:**

- ✅ **Native Config:** 28 files across 18 categories + 3 quick-starts (5,267 paths)
- ✅ **Operational Data:** 20 files across 16 categories + 3 quick-starts (2,634 paths)
- ✅ **Events:** 11 files across 10 categories (76 notifications)
- ✅ **RPC Operations:** 10 files across 9 categories (284 actions)

**New Features:**
- 🚀 **6 Quick-Start Collections** - Curated endpoints for common workflows
- 🛠️ **Code Generator** - Auto-generate curl, Python, and Ansible code
- 📚 **Comprehensive Docs** - Getting started guide with 15+ examples
- 🎯 **53 Logical Categories** - Organized by network engineer workflows

📊 **[Read Project Summary](docs/PROJECT_SUMMARY.md)** for full details on enhancements.

## 📊 Quick Stats

| Metric | Count | Description |
|--------|-------|-------------|
| **OpenAPI Specs** | 543 | Generated specifications |
| **API Paths** | 9,659 | RESTCONF endpoints |
| **Operations** | 15,342 | Total API operations |
| **YANG Modules** | 848 | Source modules |
| **Model Types** | 9 | Categories |
| **Coverage** | 45.5% | YANG modules with specs |

## 🗂️ Model Categories

### ⭐ Enhanced Models (Reorganized & Categorized)

#### 📊 Native Configuration - ENHANCED (28 files, 18 categories, 5,267 paths)
Full CLI-equivalent configuration organized by network domain.
- **Categories:** interfaces, routing, security, system, qos, vpn, wireless, switching, multicast, mpls, sdwan, services, platform, nat, voice, aaa, other
- **Quick-Starts:** day0, interface-basics, routing-basics
- [Browse Native Config APIs →](swagger-native-config-model/)

#### 📈 Operational Data - ENHANCED (20 files, 16 categories, 2,634 paths)
Real-time device state and statistics. Read-only GET operations.
- **Categories:** interfaces, routing, platform, memory, qos, wireless, vpn, security, switching, environment, processes, sdwan, mpls, services, other
- **Quick-Starts:** troubleshooting, performance, inventory
- [Browse Operational APIs →](swagger-oper-model/)

#### 🔔 Events - ENHANCED (11 files, 10 categories, 76 notifications)
Event notification modules for YANG-Push telemetry.
- **Categories:** interfaces, routing, security, platform, wireless, vpn, sdwan, services, qos, other
- [Browse Events APIs →](swagger-events-model/)

#### ⚡ RPC Operations - ENHANCED (10 files, 9 categories, 284 actions)
Remote procedure calls for device actions and commands.
- **Categories:** network-ops, wireless-ops, system-ops, security-ops, config-ops, debug-ops, platform-ops, cloud-ops, other
- [Browse RPC APIs →](swagger-rpc-model/)

### 📚 Standard Models (Original Structure)

#### ⚙️ Configuration (39 modules, 612 paths)
Device configuration with full CRUD operations.
- MDT subscriptions, gNMI config, wireless settings
- [Browse Config APIs →](swagger-cfg-model/)

#### 🌍 OpenConfig (42 modules, 772 paths)
Vendor-neutral network configuration standards.
- Interfaces, BGP, OSPF, LLDP, MPLS, VLANs
- [Browse OpenConfig APIs →](swagger-openconfig-model/)

#### 📜 IETF Standards (22 modules, 505 paths)
RFC-compliant IETF YANG models.
- ietf-interfaces, ietf-routing, ietf-netconf
- [Browse IETF APIs →](swagger-ietf-model/)

#### 📡 MIB Translations (148 modules, 4,272 paths)
SNMP MIB modules translated to YANG.
- IF-MIB, CISCO-PROCESS-MIB, OSPF-MIB
- [Browse MIB APIs →](swagger-mib-model/)

#### ⚙️ CFG Model (40 modules, 612 paths)
Device configuration with full CRUD operations.
- MDT subscriptions, gNMI config, wireless settings
- [Browse Config APIs →](swagger-cfg-model/)
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
├── swagger-oper-model/                 # Operational (197 specs)
├── swagger-rpc-model/                  # RPC (53 specs)
├── swagger-cfg-model/                  # Config (39 specs)
├── swagger-openconfig-model/           # OpenConfig (41 specs)
├── swagger-ietf-model/                 # IETF (21 specs)
├── swagger-mib-model/                  # MIB (147 specs)
├── swagger-events-model/               # Events (32 specs)
├── swagger-native-config-model/        # Native (9 specs)
├── swagger-other-model/                # Other (4 specs)
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