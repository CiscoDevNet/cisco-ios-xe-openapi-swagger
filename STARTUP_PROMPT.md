# Cisco IOS-XE YANG-to-Swagger Documentation Project
## AI Assistant Startup Prompt

Copy and paste this prompt to start a fresh session with an AI assistant:

---

## PROMPT START

```
I have a project to generate OpenAPI/Swagger documentation from Cisco IOS-XE 17.18.1 YANG models.

## Project Location
c:\Users\jcohoe\OneDrive - Cisco\Documents\VSCODE-OD\Swagger2\Swagger\iosxe-1718-yang-swagger

## What's Already Set Up
- 848 YANG modules in references/17181-YANG-modules/
- v2 generators in generators/ (YANG-parsing based)
- Swagger UI 5.11.0 in swagger-ui-5.11.0/
- Empty swagger-*-model/api/ folders ready for specs
- Scripts in scripts/ for validation and deployment

## Project Goal
Generate OpenAPI 3.0 specifications for ALL Cisco IOS-XE RESTCONF APIs, organized by model type:
- swagger-oper-model/ - Operational state (read-only)
- swagger-rpc-model/ - RPC operations  
- swagger-cfg-model/ - Configuration (CRUD)
- swagger-openconfig-model/ - OpenConfig standards
- swagger-ietf-model/ - IETF standards
- swagger-mib-model/ - SNMP MIB translations
- swagger-events-model/ - Event notifications
- swagger-native-config-model/ - Cisco native config
- swagger-other-model/ - Miscellaneous

## Key Requirements
1. 100% YANG module accountability - every module documented or excluded with reason
2. YANG-parsing generators (not hardcoded examples)
3. Interactive Swagger UI for each model type
4. GitHub Pages deployment ready
5. See PROJECT_REQUIREMENTS.md for full details

## Generators Available
- generate_oper_openapi_v2.py - Operational models
- generate_rpc_openapi_v2.py - RPC operations
- generate_cfg_openapi_v2.py - Config models
- generate_openconfig_openapi_v2.py - OpenConfig
- generate_ietf_openapi_v2.py - IETF standards
- generate_mib_openapi_v2.py - MIB translations
- generate_events_openapi.py - Events
- generate_native_openapi_v2.py - Native config
- generate_other_openapi_v2.py - Other models
- generate_combined_*.py - Combined views

## First Tasks
1. Run the generators to create OpenAPI specs
2. Create index.html pages for each swagger folder
3. Validate quality with scripts/validate_quality.py
4. Generate accountability report with scripts/analyze_yang_accountability.py

Please help me generate all the OpenAPI specifications and set up the Swagger UI interfaces.
```

---

## PROMPT END

---

## Quick Reference Commands

### Run All Generators
```powershell
cd iosxe-1718-yang-swagger/generators

# Individual model types
python generate_oper_openapi_v2.py
python generate_rpc_openapi_v2.py
python generate_cfg_openapi_v2.py
python generate_openconfig_openapi_v2.py
python generate_ietf_openapi_v2.py
python generate_mib_openapi_v2.py
python generate_events_openapi.py
python generate_native_openapi_v2.py
python generate_other_openapi_v2.py

# Combined views
python generate_combined_oper.py
python generate_combined_rpc.py
python generate_combined_ietf.py
python generate_combined_events.py
python generate_combined_mib.py
python generate_combined_native.py
```

### Validate Quality
```powershell
cd iosxe-1718-yang-swagger
python scripts/validate_quality.py
```

### Generate Accountability Report
```powershell
python scripts/analyze_yang_accountability.py
```

### Test Locally
```powershell
cd iosxe-1718-yang-swagger
python -m http.server 8000
# Open http://localhost:8000
```

### Prepare for GitHub Pages
```powershell
python scripts/prepare_github_pages.py
```

---

## Expected Output

| Model Type | Expected Specs | Description |
|------------|---------------|-------------|
| Operational | ~209 | Real-time state data |
| RPC | ~53 | Remote procedure calls |
| Config | ~42 | Configuration CRUD |
| OpenConfig | ~65 | Vendor-neutral standards |
| IETF | ~30 | RFC standards |
| MIB | ~148 | SNMP translations |
| Events | ~32 | Notifications |
| Native | ~10 | Cisco native categories |
| Other | ~6 | Miscellaneous |
| **Total** | **~595** | |

---

## File Structure After Generation

```
iosxe-1718-yang-swagger/
├── index.html                 # Main landing page
├── swagger-oper-model/
│   ├── index.html            # Model type index
│   ├── all-operations.html   # Combined view
│   └── api/
│       ├── manifest.json     # Module registry
│       ├── all-operations.json
│       └── *.json            # Individual specs
├── swagger-rpc-model/
│   └── ...
├── [other swagger folders]
├── generators/               # Python generators
├── scripts/                  # Utility scripts
├── references/
│   └── 17181-YANG-modules/   # 848 YANG files
└── swagger-ui-5.11.0/        # UI framework
```

---

## Troubleshooting

### Generator fails with import error
```powershell
pip install pyang
```

### Missing Swagger UI assets
Ensure swagger-ui-5.11.0/dist/ contains swagger-ui-bundle.js and swagger-ui.css

### Specs not showing in UI
Check that api/ folders contain JSON files and manifest.json exists

---

**Created:** February 1, 2026
**IOS-XE Version:** 17.18.1
