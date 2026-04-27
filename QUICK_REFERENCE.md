# Quick Reference Guide

## Fixed Issues

### 4. Empty `{}` and `null` Examples — Fixed
**Issue:** POST/PUT/PATCH request bodies showed `{}` or stray `null` values, making the examples unusable for real RESTCONF calls.
**Fix:** [scripts/enrich_v2_specs.py](scripts/enrich_v2_specs.py) now schema-walks, then path-matches, then falls back to `[null]` (RFC 7951 empty-leaf encoding). 48,541 enrichments applied across 657 specs. Verified: 0 empty `{}` and 0 `null` values across all 26,331 config examples.
**Status:** Fixed and deployed. See [CHANGELOG](CHANGELOG.md) for details.

### 5. Deep-Link URLs — Fixed
**Issue:** Copying a search-result URL brought users back to the index page instead of the right module.
**Fix:** [search.js](search.js) now reads/writes URL hashes:
- `#search=<query>` — runs the search on load
- `#module=<name>` — opens the module's swagger page
- `#spec=<model>/<name>` — opens the spec inside the right model's `index.html`
**Status:** Fixed and deployed.

### 1. Other Model - Fixed [object object] Display
**Issue:** Other/Misc tab showed `[object object]` instead of module names  
**Fix:** Updated JavaScript to properly handle module objects from manifest  
**Status:** Fixed and deployed

### 2. Native Config - Added Search for hostname
**Issue:** Too many APIs, couldn't find `hostname` easily  
**Fix:** 
- Added search box at top of sidebar
- Type "hostname" to filter categories
- hostname API is in **System** category
- Also enabled Swagger UI's built-in filter (search box in operations)

**How to find hostname API:**
1. Go to [Native Config](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-native-config-model/)
2. Click **System - hostname, banner, etc** in sidebar
3. Search for "hostname" in the operations filter
4. Look for `/data/Cisco-IOS-XE-native:native/hostname`

### 3. MIB Model - Errors Expected
**Issue:** "Lots of lots of errors"  
**Explanation:** MIB-to-YANG conversions often have validation issues:
- 147 MIB modules converted from SNMP MIBs
- Some MIBs have complex structures that don't map perfectly to YANG/OpenAPI
- These are reference specs - not all MIBs are fully supported via RESTCONF
- **This is normal** - focus on Operational, RPC, and Config models for production use

**Recommendation:** Use MIB model as reference only. For production:
- Use **Operational** model for state/monitoring
- Use **Config** or **Native** model for configuration
- Use **RPC** model for actions

## YANG Module Locations

### Cisco-IOS-XE-ios-events-oper.yang
**GitHub Link:** https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger/blob/main/references/17181-YANG-modules/Cisco-IOS-XE-ios-events-oper.yang

**Local Path:** 
```
references/17181-YANG-modules/Cisco-IOS-XE-ios-events-oper.yang
```

**OpenAPI Spec:**
- **Category:** Events Model
- **URL:** https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-events-model/
- **Select Module:** Cisco-IOS-XE-ios-events-oper
- **API Endpoint:** `/data/ios-events-ios-xe-oper:ios-events`

### All YANG Modules
All 848 YANG source modules are in:
```
references/17181-YANG-modules/
```
The accountability report tracks 1,103 total modules (848 YANG + 255 spec-only MIB/Native).

**Browse on GitHub:**  
https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger/tree/main/references/17181-YANG-modules

## API Categories Summary

All 9 model types have deep-path specs generated from resolved YANG trees, providing full-depth RESTCONF paths with production-realistic examples.

| Category | Specs | Paths/Ops | Use Case | Quality |
|----------|-------|-----------|----------|---------|
| **Operational** | 205 specs | 20,159 paths | Monitoring, state data | Production Ready |
| **Native Config** | 81 specs | 13,452 ops | Full device config | Production Ready |
| **Configuration** | 39 specs | 9,452 ops | Feature config | Production Ready |
| **RPC** | 59 specs | 232 RPCs | Actions, commands | Production Ready |
| **OpenConfig** | 57 specs | 5,920 ops | Vendor-neutral config | Stable |
| **IETF** | 19 specs | 1,122 ops | Standards-based | Stable |
| **Events** | 38 specs | 861 paths | Notifications | Stable |
| **MIB** | 149 specs | 12,482 paths | SNMP MIB reference | Reference Only |
| **Other** | 9 specs | 4,593 ops | Misc/vendor-specific | Variable |

### Quick Links

| Model | Link |
|-------|------|
| Operational | [Browse Oper](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-oper-model/index.html) |
| Native Config | [Browse Native](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-native-config-model/index.html) |
| Configuration | [Browse Config](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-cfg-model/index.html) |
| OpenConfig | [Browse OpenConfig](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-openconfig-model/index.html) |
| IETF | [Browse IETF](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-ietf-model/index.html) |
| MIB | [Browse MIB](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-mib-model/index.html) |
| RPC | [Browse RPC](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-rpc-model/index.html) |
| Events | [Browse Events](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-events-model/index.html) |
| Other | [Browse Other](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-other-model/index.html) |

## Tips & Tricks

### Finding Specific APIs
1. **Use Category Search:** Each model page has search functionality
2. **Use Browser Find:** Ctrl+F in the sidebar to find modules
3. **Native Config:** Use the search box for keywords like "hostname", "interface", "routing"
4. **Swagger Filter:** Once a spec is loaded, use the filter box at the top of operations

### Common APIs Quick Links

**Hostname Configuration:**
- [Native > System](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-native-config-model/) > Select "System"
- Endpoint: `/data/Cisco-IOS-XE-native:native/hostname`

**Interface State:**
- [Operational](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-oper-model/) > Select "Cisco-IOS-XE-interfaces-oper"
- Endpoint: `/data/interfaces-ios-xe-oper:interfaces`

**Save Config (RPC):**
- [RPC](https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-rpc-model/) > Select "Cisco-IOS-XE-rpc"
- Endpoint: `/operations/cisco-ia:save-config`

## Known Limitations

1. **MIB Model Errors:** Expected - these are auto-converted from SNMP MIBs
2. **Local Swagger UI:** Removed - using CDN version for reliability
3. **Some specs may be large:** Native and Operational specs can be 1MB+ (normal for comprehensive device models)

## Support & Resources

- **YANG Models:** [Cisco IOS-XE YANG GitHub](https://github.com/YangModels/yang/tree/main/vendor/cisco/xe)
- **RESTCONF Guide:** [IOS-XE 17.18 RESTCONF Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/m_1718_prog_restconf.html)
- **YANG Suite:** [Cisco YANG Suite](https://developer.cisco.com/yangsuite/) | [GitHub](https://github.com/CiscoDevNet/yangsuite/)
- **OpenAPI Specs:** All available at https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/
