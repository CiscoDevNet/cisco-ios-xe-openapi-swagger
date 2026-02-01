#!/usr/bin/env python3
"""
YANG Module Accountability Analyzer

Analyzes all YANG modules in the reference folder and generates
a comprehensive accountability report showing:
- Which Swagger set each module is available in
- Why modules are not swagger-ized (types, deviations, etc.)

Usage: python analyze_yang_accountability.py
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Configuration
BASE_DIR = Path(__file__).parent.parent
YANG_DIR = BASE_DIR / "references" / "17181-YANG-modules"
OUTPUT_FILE = BASE_DIR / "YANG_MODULE_ACCOUNTABILITY.md"
JSON_OUTPUT = BASE_DIR / "yang_accountability.json"

# Swagger folder mappings
SWAGGER_FOLDERS = {
    "oper": BASE_DIR / "swagger-oper-model" / "api",
    "rpc": BASE_DIR / "swagger-rpc-model" / "api",
    "cfg": BASE_DIR / "swagger-cfg-model" / "api",
    "openconfig": BASE_DIR / "swagger-openconfig-model" / "api",
    "ietf": BASE_DIR / "swagger-ietf-model" / "api",
    "mib": BASE_DIR / "swagger-mib-model" / "api",
    "events": BASE_DIR / "swagger-events-model" / "api",
    "native": BASE_DIR / "swagger-native-config-model" / "api",
    "other": BASE_DIR / "swagger-other-model" / "api",
}

def get_existing_specs() -> Dict[str, List[str]]:
    """Get list of existing OpenAPI specs in each swagger folder."""
    specs = {}
    for category, folder in SWAGGER_FOLDERS.items():
        if folder.exists():
            json_files = [f.stem for f in folder.glob("*.json") 
                         if not f.stem.startswith("manifest") and not f.stem.startswith("all-")]
            specs[category] = json_files
        else:
            specs[category] = []
    return specs

def categorize_yang_module(filename: str, content: str = "") -> Tuple[str, str]:
    """
    Categorize a YANG module and provide reason if excluded.
    
    Returns: (category, reason_if_excluded)
    """
    name = filename.replace(".yang", "")
    
    # Check for deviation modules first (highest priority exclusion)
    if "-deviation" in name.lower() or name.endswith("-devs") or "-devs-" in name:
        return "deviation", "Deviation module - modifies other modules, no standalone API"
    
    # Type definition modules
    if name.endswith("-types") or "-types-" in name:
        return "types", "Type definitions only - no API operations"
    
    # Common/infrastructure modules
    if name.startswith("tailf-"):
        return "common", "Tail-f/Cisco infrastructure module - internal use"
    if name == "cisco-semver":
        return "common", "Semantic versioning module - metadata only"
    if name.startswith("cisco-xe-") and "openconfig" in name.lower():
        return "deviation", "OpenConfig deviation module"
    
    # OpenConfig modules
    if name.startswith("openconfig-"):
        if "-types" in name:
            return "types", "OpenConfig type definitions only"
        return "openconfig", ""
    
    # IETF/IANA modules
    if name.startswith("ietf-") or name.startswith("iana-"):
        if "-types" in name:
            return "types", "IETF type definitions only"
        return "ietf", ""
    
    # Cisco IOS-XE modules
    if name.startswith("Cisco-IOS-XE-"):
        # Operational
        if name.endswith("-oper"):
            return "oper", ""
        # RPC
        if name.endswith("-rpc"):
            return "rpc", ""
        # Events
        if "-events" in name:
            return "events", ""
        # MIB
        if name.endswith("-mib") or "-mib-" in name:
            return "mib", ""
        # Types
        if name.endswith("-types") or "-types-" in name:
            return "types", "Type definitions only - no API operations"
        # Config (cfg suffix or config-related)
        if name.endswith("-cfg"):
            return "cfg", ""
        # Native module and augmentations
        if name == "Cisco-IOS-XE-native":
            return "native", ""
        # Check content for augments native
        if "augment" in content and "native" in content:
            return "native-aug", "Augments native module - included in native specs"
        # Default to cfg for remaining Cisco modules
        return "cfg", ""
    
    # MIB modules (CISCO-*-MIB pattern)
    if name.startswith("CISCO-") and "-MIB" in name:
        return "mib", ""
    if name.endswith("-MIB") or "-MIB-" in name:
        return "mib", ""
    
    # PIM, OSPF, etc. (protocol modules)
    if name in ["pim", "ospf", "bgp", "isis"]:
        return "other", "Protocol definition module"
    
    # Deprecated/obsolete
    if "deprecated" in name.lower() or "obsolete" in name.lower():
        return "deprecated", "Deprecated module - no longer supported"
    
    # Check content for more hints
    if content:
        # Has RPC definitions
        if re.search(r'^\s*rpc\s+\w+\s*{', content, re.MULTILINE):
            return "rpc", ""
        # Only typedefs
        if re.search(r'^\s*typedef\s+', content, re.MULTILINE) and not re.search(r'^\s*container\s+', content, re.MULTILINE):
            return "types", "Contains only type definitions"
        # Has notifications (events)
        if re.search(r'^\s*notification\s+', content, re.MULTILINE):
            return "events", ""
    
    return "other", ""

def find_spec_for_module(module_name: str, existing_specs: Dict[str, List[str]], category: str) -> Tuple[Optional[str], bool]:
    """
    Find which swagger folder has a spec for this module.
    
    Returns: (swagger_folder_name, has_spec)
    """
    # Direct match in expected category
    expected_folder = {
        "oper": "oper",
        "rpc": "rpc",
        "cfg": "cfg",
        "openconfig": "openconfig",
        "ietf": "ietf",
        "mib": "mib",
        "events": "events",
        "native": "native",
        "other": "other",
    }.get(category)
    
    if expected_folder and module_name in existing_specs.get(expected_folder, []):
        return f"swagger-{expected_folder}-model", True
    
    # Check all folders for the spec
    for folder_cat, specs in existing_specs.items():
        if module_name in specs:
            return f"swagger-{folder_cat}-model", True
    
    return None, False

def analyze_all_modules():
    """Analyze all YANG modules and generate accountability report."""
    
    print("=" * 60)
    print("YANG Module Accountability Analyzer")
    print("=" * 60)
    
    # Get existing specs
    print("\nScanning existing OpenAPI specs...")
    existing_specs = get_existing_specs()
    for cat, specs in existing_specs.items():
        print(f"  {cat}: {len(specs)} specs")
    
    # Get all YANG files
    yang_files = list(YANG_DIR.glob("*.yang"))
    print(f"\nFound {len(yang_files)} YANG modules")
    
    # Analyze each module
    modules = []
    categories = defaultdict(lambda: {"total": 0, "with_spec": 0, "modules": []})
    
    for yang_file in sorted(yang_files):
        module_name = yang_file.stem
        
        # Read content for better categorization
        try:
            content = yang_file.read_text(encoding='utf-8', errors='ignore')
        except:
            content = ""
        
        # Categorize
        category, reason = categorize_yang_module(yang_file.name, content)
        
        # Find spec
        swagger_folder, has_spec = find_spec_for_module(module_name, existing_specs, category)
        
        # If no spec but should have one, explain why
        if not has_spec and not reason:
            if category in ["types", "deviation", "common", "deprecated", "native-aug"]:
                pass  # Already has reason
            else:
                reason = "Spec not yet generated or module excluded"
        
        module_info = {
            "name": module_name,
            "category": category,
            "swagger_folder": swagger_folder,
            "has_spec": has_spec,
            "reason_if_excluded": reason if not has_spec else None
        }
        modules.append(module_info)
        
        # Update category stats
        categories[category]["total"] += 1
        if has_spec:
            categories[category]["with_spec"] += 1
        categories[category]["modules"].append(module_info)
    
    # Generate reports
    generate_markdown_report(modules, categories)
    generate_json_report(modules, categories)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_yang = len(modules)
    total_with_spec = sum(1 for m in modules if m["has_spec"])
    
    print(f"\nTotal YANG modules: {total_yang}")
    print(f"Modules with specs: {total_with_spec} ({100*total_with_spec/total_yang:.1f}%)")
    print(f"Modules excluded:   {total_yang - total_with_spec}")
    
    print("\nBy Category:")
    for cat in sorted(categories.keys()):
        info = categories[cat]
        pct = 100 * info["with_spec"] / info["total"] if info["total"] > 0 else 0
        status = "✅" if pct > 80 else "⚠️" if pct > 50 else "❌" if info["total"] > 10 else "📝"
        print(f"  {status} {cat:15} {info['total']:4} modules, {info['with_spec']:4} with specs ({pct:.0f}%)")
    
    print(f"\nReports generated:")
    print(f"  - {OUTPUT_FILE}")
    print(f"  - {JSON_OUTPUT}")

def generate_markdown_report(modules: List[dict], categories: dict):
    """Generate the markdown accountability report."""
    
    total = len(modules)
    with_spec = sum(1 for m in modules if m["has_spec"])
    
    lines = [
        "# YANG Module Accountability Report",
        "",
        f"**Date:** {__import__('datetime').datetime.now().strftime('%B %d, %Y')}",
        f"**IOS-XE Version:** 17.18.1",
        f"**Total YANG Modules:** {total}",
        f"**Modules with OpenAPI Specs:** {with_spec} ({100*with_spec/total:.1f}%)",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "This report provides **100% accountability** for every YANG module in the",
        "`references/17181-YANG-modules/` folder. Each module is either:",
        "",
        "1. **Documented** with an OpenAPI spec in a swagger-* folder, OR",
        "2. **Excluded** with documented reason (types, deviations, etc.)",
        "",
        "---",
        "",
        "## Category Summary",
        "",
        "| Category | Total | With Specs | Coverage | Notes |",
        "|----------|-------|------------|----------|-------|",
    ]
    
    # Category summary table
    cat_order = ["oper", "rpc", "cfg", "openconfig", "ietf", "mib", "events", "native", "other",
                 "types", "deviation", "common", "native-aug", "deprecated"]
    
    for cat in cat_order:
        if cat in categories:
            info = categories[cat]
            pct = 100 * info["with_spec"] / info["total"] if info["total"] > 0 else 0
            if cat in ["types", "deviation", "common", "native-aug", "deprecated"]:
                notes = "Excluded by design"
                coverage = "N/A"
            else:
                notes = ""
                coverage = f"{pct:.0f}%"
            lines.append(f"| **{cat}** | {info['total']} | {info['with_spec']} | {coverage} | {notes} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## Detailed Module List",
        "",
    ])
    
    # Group by category
    for cat in cat_order:
        if cat not in categories:
            continue
        
        info = categories[cat]
        lines.extend([
            f"### {cat.upper()} ({info['total']} modules)",
            "",
        ])
        
        if cat in ["types", "deviation", "common", "native-aug", "deprecated"]:
            lines.append(f"*These modules are excluded by design: {info['modules'][0]['reason_if_excluded'] if info['modules'] else 'N/A'}*")
            lines.append("")
            lines.append("<details>")
            lines.append(f"<summary>Click to expand list of {info['total']} {cat} modules</summary>")
            lines.append("")
            lines.append("| Module Name | Reason |")
            lines.append("|-------------|--------|")
            for m in sorted(info["modules"], key=lambda x: x["name"]):
                lines.append(f"| {m['name']} | {m['reason_if_excluded'] or '-'} |")
            lines.append("")
            lines.append("</details>")
        else:
            lines.append("| Module Name | Swagger Folder | Has Spec |")
            lines.append("|-------------|----------------|----------|")
            for m in sorted(info["modules"], key=lambda x: x["name"]):
                spec_status = "✅" if m["has_spec"] else "❌"
                folder = m["swagger_folder"] or "-"
                lines.append(f"| {m['name']} | {folder} | {spec_status} |")
        
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## Generation Notes",
        "",
        "### Excluded Categories Explained",
        "",
        "| Category | Reason for Exclusion |",
        "|----------|---------------------|",
        "| **types** | Contains only `typedef` and `grouping` statements - no API operations |",
        "| **deviation** | Modifies other modules' behavior - no standalone API |",
        "| **common** | Infrastructure modules (tailf-*, cisco-semver) - internal use |",
        "| **native-aug** | Augments Cisco-IOS-XE-native - included in native category specs |",
        "| **deprecated** | Obsolete modules - no longer supported |",
        "",
        "### Native Module Handling",
        "",
        "The `Cisco-IOS-XE-native.yang` module (200,000+ lines) is too large for a single spec.",
        "It's broken into categorical specs in `swagger-native-config-model/`:",
        "",
        "- native-routing.json",
        "- native-interfaces.json",
        "- native-security.json",
        "- etc.",
        "",
        "Modules that augment native are included in these categorical specs.",
        "",
        "---",
        "",
        f"*Report generated: {__import__('datetime').datetime.now().isoformat()}*",
    ])
    
    OUTPUT_FILE.write_text("\n".join(lines), encoding='utf-8')

def generate_json_report(modules: List[dict], categories: dict):
    """Generate JSON version of the report."""
    
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "ios_xe_version": "17.18.1",
        "total_modules": len(modules),
        "modules_with_specs": sum(1 for m in modules if m["has_spec"]),
        "categories": {
            cat: {
                "total": info["total"],
                "with_specs": info["with_spec"],
                "coverage_pct": round(100 * info["with_spec"] / info["total"], 1) if info["total"] > 0 else 0
            }
            for cat, info in categories.items()
        },
        "modules": modules
    }
    
    JSON_OUTPUT.write_text(json.dumps(report, indent=2), encoding='utf-8')

if __name__ == "__main__":
    analyze_all_modules()
