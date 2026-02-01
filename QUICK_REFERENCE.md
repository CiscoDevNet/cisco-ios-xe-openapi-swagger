# Quick Reference Guide

## Fixed Issues

### 1. ✅ Other Model - Fixed [object object] Display
**Issue:** Other/Misc tab showed `[object object]` instead of module names  
**Fix:** Updated JavaScript to properly handle module objects from manifest  
**Status:** Fixed and deployed

### 2. ✅ Native Config - Added Search for hostname
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

### 3. ⚠️ MIB Model - Errors Expected
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
All 848 YANG modules are in:
```
references/17181-YANG-modules/
```

**Browse on GitHub:**  
https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger/tree/main/references/17181-YANG-modules

## API Categories Summary

| Category | Count | Use Case | Quality |
|----------|-------|----------|---------|
| **Operational** | 197 modules, 7,239 ops | Monitoring, state data | ⭐⭐⭐⭐⭐ Production Ready |
| **RPC** | 53 modules, 284 ops | Actions, commands | ⭐⭐⭐⭐⭐ Production Ready |
| **Config** | 39 modules, 905 ops | Feature config | ⭐⭐⭐⭐⭐ Production Ready |
| **Native** | 9 categories, 606 ops | Full device config | ⭐⭐⭐⭐⭐ Production Ready |
| **OpenConfig** | 41 modules, 364 ops | Vendor-neutral config | ⭐⭐⭐⭐ Stable |
| **IETF** | 21 modules, 117 ops | Standards-based | ⭐⭐⭐⭐ Stable |
| **Events** | 32 modules, 89 ops | Notifications | ⭐⭐⭐⭐ Stable |
| **MIB** | 147 modules, 65 ops | SNMP MIB reference | ⚠️ Reference Only |
| **Other** | 4 modules, 287 ops | Misc/vendor-specific | ⭐⭐⭐ Variable |

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
- **RESTCONF Guide:** [Cisco DevNet RESTCONF](https://developer.cisco.com/docs/ios-xe/#!working-with-restconf)
- **OpenAPI Specs:** All available at https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/
