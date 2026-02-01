#!/usr/bin/env python3
"""
Generate combined MIB OpenAPI specification.
Merges all 147 SNMP MIB (SMIv2-to-YANG) module specifications into a single unified spec.
"""

import json
from pathlib import Path

def generate_combined_mib():
    """Generate all-mibs.json combining all MIB module specs."""

    base_path = Path("/home/tme/Swagger/swagger-mib-model/api")

    # Base combined spec
    combined = {
        "openapi": "3.0.0",
        "info": {
            "title": "SNMP MIB Models - All Modules (SMIv2-to-YANG)",
            "description": """Complete SNMP MIB collection for IOS-XE 17.18.1.

This unified specification combines all 147 SNMP MIB modules (translated from SMIv2 to YANG) supported by Cisco IOS-XE.

⚠️ **CRITICAL - MIB DATA ACCESS LIMITATION**:

These YANG models exist for SMIv2-to-YANG translation purposes, but **MIB data on IOS-XE devices is primarily accessed via SNMP protocol, not RESTCONF**.

**RESTCONF Limitation**: Most MIB paths will return **404 errors** via RESTCONF `/data` endpoints because IOS-XE exposes MIB data through SNMP, not the YANG datastore.

**Recommended Access Methods**:
1. **SNMP (Primary)**: Use SNMP v2c/v3 to query MIB data directly - this is the standard and supported method
2. **NETCONF**: Use NETCONF `<get>` operations for devices supporting YANG-modeled MIB access
3. **Device Check**: Verify your specific IOS-XE version/platform for RESTCONF MIB support

**YANG Model Purpose**: These models define SNMP MIB structure in YANG format for:
- Tooling compatibility and code generation
- Documentation and schema validation
- NETCONF/YANG-based management systems
- **NOT for production RESTCONF data access on most IOS-XE platforms**

---

**MIB Categories:**
- **Standard MIBs**: BGP4-MIB, OSPF-MIB, IF-MIB, IP-MIB, TCP-MIB, UDP-MIB
- **Cisco Enterprise MIBs**: CISCO-BGP4-MIB, CISCO-OSPF-MIB, CISCO-IF-EXTENSION-MIB
- **IETF MIBs**: ENTITY-MIB, BRIDGE-MIB, RMON-MIB, RMON2-MIB
- **ATM/SONET**: ATM-MIB, SONET-MIB, DS1-MIB, DS3-MIB
- **Monitoring**: NOTIFICATION-LOG-MIB, DISMAN-EVENT-MIB, HC-RMON-MIB

**Total Modules:** 147 SNMP MIB modules
**RESTCONF Base URL:** https://10.85.134.65/restconf/data (⚠️ likely unavailable for MIBs)
**SNMP Access:** Use SNMP client with community string or SNMPv3 credentials
""",
            "version": "17.18.1",
            "contact": {
                "name": "IOS-XE MIB Models",
                "url": "https://github.com/YangModels/yang/tree/main/vendor/cisco/xe"
            }
        },
        "servers": [
            {
                "url": "https://10.85.134.65/restconf",
                "description": "IOS-XE Device (C9300)"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "BasicAuth": {
                    "type": "http",
                    "scheme": "basic"
                }
            }
        },
        "security": [{"BasicAuth": []}],
        "tags": []
    }

    # Track statistics
    stats = {
        "total_paths": 0,
        "total_schemas": 0,
        "modules_merged": 0,
        "modules": []
    }

    # Get all JSON files (exclude manifest, combined, and stats)
    json_files = sorted([f for f in base_path.glob("*.json")
                        if f.name not in ["manifest.json", "all-mibs.json", "merge_stats.json"]])

    print(f"\n{'='*70}")
    print(f"Merging {len(json_files)} MIB module specifications")
    print(f"{'='*70}\n")

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                spec = json.load(f)

            module_name = json_file.stem
            paths_count = len(spec.get("paths", {}))
            schemas_count = len(spec.get("components", {}).get("schemas", {}))

            # Merge paths
            for path, path_obj in spec.get("paths", {}).items():
                if path not in combined["paths"]:
                    combined["paths"][path] = path_obj
                    stats["total_paths"] += 1

            # Merge schemas
            for schema_name, schema_obj in spec.get("components", {}).get("schemas", {}).items():
                if schema_name not in combined["components"]["schemas"]:
                    combined["components"]["schemas"][schema_name] = schema_obj
                    stats["total_schemas"] += 1

            # Add tag
            if spec.get("tags"):
                for tag in spec["tags"]:
                    if tag not in combined["tags"]:
                        combined["tags"].append(tag)

            stats["modules_merged"] += 1
            stats["modules"].append({
                "name": module_name,
                "file": json_file.name,
                "paths": paths_count,
                "schemas": schemas_count
            })

            print(f"  ✓ Merged: {module_name:30s} ({paths_count:4d} paths, {schemas_count:4d} schemas)")

        except Exception as e:
            print(f"  ✗ Error merging {json_file.name}: {e}")
            continue

    # Write combined spec
    output_file = base_path / "all-mibs.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Combined MIB Specification Generated!")
    print(f"{'='*70}")
    print(f"Output: {output_file}")
    print(f"Total paths: {stats['total_paths']}")
    print(f"Total schemas: {stats['total_schemas']}")
    print(f"Modules merged: {stats['modules_merged']}/{len(json_files)}")
    print(f"{'='*70}\n")

    # Save merge statistics
    stats_file = base_path / "merge_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

    print(f"Merge statistics saved: {stats_file}")

    return stats

if __name__ == "__main__":
    generate_combined_mib()
