# Cisco IOS-XE YANG Model Documentation Hub
## Project Requirements & Fresh Start Guide

**Version:** 1.0  
**Date:** February 1, 2026  
**IOS-XE Version:** 17.18.1

---

## 1. Project Overview

### Purpose
Generate comprehensive OpenAPI 3.0 specifications from Cisco IOS-XE YANG models to provide interactive Swagger UI documentation for RESTCONF API operations.

### Goals
1. Create OpenAPI specs for ALL applicable YANG modules
2. Provide interactive Swagger UI for API exploration and testing
3. Maintain 100% accountability for every YANG module (documented or excluded with reason)
4. Support both local development and GitHub Pages deployment

---

## 2. Source Materials Required

### YANG Modules Directory
```
references/17181-YANG-modules/
├── *.yang                 # 848 YANG files (main)
└── MIBS/                  # MIB translation modules (optional subfolder)
```

### Required Files
- All IOS-XE 17.18.1 YANG modules from Cisco GitHub:
  https://github.com/YangModels/yang/tree/main/vendor/cisco/xe/17181

### Swagger UI Framework
- Swagger UI 5.11.0 (or latest)
- Download from: https://github.com/swagger-api/swagger-ui/releases

---

## 3. Module Categories & Classification

### Swagger-ized Categories (Generate OpenAPI specs)

| Category | Pattern | Swagger Folder | Description |
|----------|---------|----------------|-------------|
| **oper** | `*-oper.yang` | swagger-oper-model/ | Operational state data (GET only) |
| **rpc** | `*-rpc.yang`, has `rpc` statements | swagger-rpc-model/ | Remote procedure calls (POST) |
| **cfg** | `*-cfg.yang`, config containers | swagger-cfg-model/ | Configuration data (CRUD) |
| **openconfig** | `openconfig-*.yang` | swagger-openconfig-model/ | Vendor-neutral standards |
| **ietf** | `ietf-*.yang`, `iana-*.yang` | swagger-ietf-model/ | IETF RFC standards |
| **mib** | `*-mib.yang`, `CISCO-*-MIB.yang` | swagger-mib-model/ | SNMP MIB translations |
| **events** | `*-events*.yang` | swagger-events-model/ | Event notifications |
| **native** | `Cisco-IOS-XE-native.yang` | swagger-native-config-model/ | Monolithic native config |
| **other** | Miscellaneous | swagger-other-model/ | Uncategorized modules |

### Excluded Categories (Do NOT generate specs)

| Category | Pattern | Reason |
|----------|---------|--------|
| **types** | `*-types.yang` | Type definitions only, no operations |
| **deviation** | `*-deviation*.yang`, `*-devs.yang` | Modifies other modules |
| **common** | `tailf-*.yang`, `cisco-semver.yang` | Infrastructure, no user operations |
| **deprecated** | Marked obsolete in YANG | No longer supported |

---

## 4. Output Structure

```
project-root/
├── index.html                      # Main landing page
├── all-models.html                 # Combined view
├── README.md                       # Project documentation
├── .nojekyll                       # GitHub Pages config
├── 404.html                        # Error page
│
├── swagger-oper-model/
│   ├── index.html                  # Category index
│   ├── all-operations.html         # Combined view
│   └── api/
│       ├── manifest.json           # Module registry
│       ├── all-operations.json     # Combined spec
│       └── *.json                  # Individual specs
│
├── swagger-rpc-model/
├── swagger-cfg-model/
├── swagger-openconfig-model/
├── swagger-ietf-model/
├── swagger-mib-model/
├── swagger-events-model/
├── swagger-native-config-model/
├── swagger-other-model/
│
├── generators/                     # Python generators
│   ├── generate_*_openapi_v2.py   # Per-category generators
│   └── generate_combined_*.py     # Combined view generators
│
├── scripts/                        # Utility scripts
│   ├── validate_quality.py        # Quality validation
│   ├── prepare_github_pages.py    # Deployment prep
│   └── analyze_yang_modules.py    # Module analysis
│
├── docs/                           # User documentation
├── references/                     # Source YANG modules
│   └── 17181-YANG-modules/
│
└── swagger-ui-5.11.0/             # UI framework
    └── dist/
```

---

## 5. Generator Requirements

### Core Functionality
Each generator MUST:
1. **Parse YANG structure** using balanced brace matching (not regex hacks)
2. **Extract all data nodes** - containers, lists, leaves, leaf-lists
3. **Generate proper paths** following RESTCONF RFC 8040
4. **Create schemas** from actual YANG types
5. **Handle groupings** by resolving `uses` statements
6. **Support augmentations** where applicable

### Key Methods Required
```python
def find_balanced_braces(text: str, start_pos: int) -> int
def parse_leaf(leaf_content: str, leaf_name: str) -> Dict
def parse_container_or_grouping(content: str, name: str, depth: int) -> Dict
def extract_paths(content: str, module_name: str) -> List[Dict]
def generate_openapi_spec(module_path: str) -> Dict
```

### Output Format
- OpenAPI 3.0.0 specification
- JSON format
- Includes: info, servers, paths, components/schemas
- RESTCONF-compliant paths: `/data/{module-name}:{path}`

---

## 6. Quality Requirements

### Per-Spec Validation
- [ ] Valid JSON syntax
- [ ] OpenAPI 3.0 schema compliance
- [ ] At least 1 path per spec (except type modules)
- [ ] Proper HTTP methods (GET for oper, POST for RPC, CRUD for config)
- [ ] Schema definitions for request/response bodies

### Project-Level Validation
- [ ] 100% YANG module accountability (see Module Accountability Report)
- [ ] All internal links working (zero 404s)
- [ ] Consistent theming across all pages
- [ ] GitHub Pages deployment ready

---

## 7. Module Accountability Requirement

### Every YANG module MUST be:
1. **Documented** with an OpenAPI spec in the appropriate swagger folder, OR
2. **Excluded** with documented reason in the accountability report

### Accountability Report Format
| Module Name | Category | Swagger Folder | Has Spec | Reason if Excluded |
|-------------|----------|----------------|----------|-------------------|
| Cisco-IOS-XE-aaa-oper | oper | swagger-oper-model | ✅ | - |
| Cisco-IOS-XE-types | types | - | ❌ | Type definitions only |

---

## 8. Deployment Options

### Option A: GitHub Pages (Recommended)
```bash
# Prepare for deployment
python scripts/prepare_github_pages.py

# Push to GitHub, enable Pages in settings
# Access: https://username.github.io/repo-name/
```

### Option B: Local HTTP Server
```bash
python -m http.server 8000
# Access: http://localhost:8000
```

### Option C: Production Web Server
```bash
# Nginx, Apache, or any static file server
# No server-side processing required
```

---

## 9. Development Workflow

### Initial Setup
```bash
# 1. Clone/create project directory
mkdir yang-swagger-docs
cd yang-swagger-docs

# 2. Copy YANG modules to references/
cp -r /path/to/17181-YANG-modules references/

# 3. Download Swagger UI
# Extract to swagger-ui-5.11.0/

# 4. Create directory structure
mkdir -p swagger-{oper,rpc,cfg,openconfig,ietf,mib,events,native-config,other}-model/api
mkdir -p generators scripts docs
```

### Generation Workflow
```bash
# 1. Analyze all YANG modules
python scripts/analyze_yang_modules.py

# 2. Generate specs for each category
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

# 3. Generate combined views
python generate_combined_oper.py
python generate_combined_rpc.py
# ... etc

# 4. Validate quality
cd ../scripts
python validate_quality.py

# 5. Prepare for deployment
python prepare_github_pages.py
```

---

## 10. Success Criteria

### Minimum Requirements
- [ ] All 9 model type folders created with specs
- [ ] index.html landing page functional
- [ ] 100% YANG module accountability documented
- [ ] Zero broken internal links
- [ ] GitHub Pages deployment working

### Quality Targets
| Metric | Target |
|--------|--------|
| Total OpenAPI Specs | 550+ |
| Total API Paths | 10,000+ |
| Total API Operations | 15,000+ |
| Module Accountability | 100% |
| Link Validation | 0 errors |

---

## 11. Reference Documentation

### Standards
- [RESTCONF RFC 8040](https://datatracker.ietf.org/doc/html/rfc8040)
- [YANG RFC 7950](https://datatracker.ietf.org/doc/html/rfc7950)
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.0)

### Cisco Resources
- [Cisco IOS-XE YANG Models](https://github.com/YangModels/yang/tree/main/vendor/cisco/xe)
- [Cisco IOS-XE Programmability Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/guide.html)

### Tools
- [pyang](https://github.com/mbj4668/pyang) - YANG parser and validator
- [Swagger UI](https://swagger.io/tools/swagger-ui/) - API documentation UI

---

## 12. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 1, 2026 | Initial requirements document |

