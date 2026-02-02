#!/usr/bin/env python3
"""
Find Missing Swagger Specs

Analyzes YANG modules that have pyang trees but NO swagger specs.
Categorizes them and reports which ones need swagger generation.

Usage: python find_missing_swaggers.py
"""

import json
from pathlib import Path
from collections import defaultdict

# Configuration
BASE_DIR = Path(__file__).parent.parent
YANG_DIR = BASE_DIR / "references" / "17181-YANG-modules"
TREES_DIR = BASE_DIR / "yang-trees"

# Swagger folders
SWAGGER_FOLDERS = {
    "oper": BASE_DIR / "swagger-oper-model" / "api",
    "rpc": BASE_DIR / "swagger-rpc-model" / "api",
    "cfg": BASE_DIR / "swagger-cfg-model" / "api",
    "events": BASE_DIR / "swagger-events-model" / "api",
    "ietf": BASE_DIR / "swagger-ietf-model" / "api",
    "openconfig": BASE_DIR / "swagger-openconfig-model" / "api",
    "other": BASE_DIR / "swagger-other-model" / "api",
}

def get_existing_specs():
    """Get list of all existing swagger spec module names."""
    all_specs = set()
    for folder_path in SWAGGER_FOLDERS.values():
        if folder_path.exists():
            for spec_file in folder_path.glob("*.json"):
                if spec_file.stem not in ["manifest", "all-oper", "all-rpc", "all-cfg"]:
                    # Extract module name from spec filename
                    all_specs.add(spec_file.stem)
    return all_specs

def get_tree_modules():
    """Get list of all modules that have pyang trees."""
    tree_modules = set()
    if TREES_DIR.exists():
        for tree_file in TREES_DIR.glob("*.html"):
            if tree_file.stem != "index":
                tree_modules.add(tree_file.stem)
    return tree_modules

def categorize_module(module_name):
    """Categorize a YANG module by name."""
    name = module_name
    
    # Cisco IOS-XE modules
    if name.startswith("Cisco-IOS-XE-"):
        if "-events" in name:
            return "events"
        if "-oper" in name:
            return "oper"
        if "-rpc" in name:
            return "rpc"
        if name.endswith("-cfg"):
            return "cfg"
        if "-mib" in name:
            return "mib"
        # Default Cisco modules to cfg
        return "cfg"
    
    # OpenConfig
    if name.startswith("openconfig-"):
        return "openconfig"
    
    # IETF
    if name.startswith("ietf-"):
        return "ietf"
    
    # Cisco extensions
    if name.startswith("cisco-xe-"):
        if "openconfig" in name:
            return "openconfig-ext"
        return "other"
    
    # Other cisco modules
    if name.startswith("cisco-"):
        return "other"
    
    # Tail-f modules
    if name.startswith("tailf-"):
        return "infrastructure"
    
    return "other"

def check_yang_file_exists(module_name):
    """Check if YANG file exists for this module."""
    yang_file = YANG_DIR / f"{module_name}.yang"
    return yang_file.exists()

def main():
    """Main entry point."""
    print("=" * 70)
    print("Finding YANG Modules with Trees but NO Swagger Specs")
    print("=" * 70)
    
    # Get existing specs
    print("\nScanning existing swagger specs...")
    existing_specs = get_existing_specs()
    print(f"Found {len(existing_specs)} existing swagger specs")
    
    # Get tree modules
    print("\nScanning pyang tree files...")
    tree_modules = get_tree_modules()
    print(f"Found {len(tree_modules)} modules with trees")
    
    # Find gaps
    missing = tree_modules - existing_specs
    print(f"\n{'='*70}")
    print(f"GAPS: {len(missing)} modules have trees but NO swagger specs")
    print(f"{'='*70}")
    
    # Categorize missing modules
    missing_by_category = defaultdict(list)
    for module in sorted(missing):
        category = categorize_module(module)
        yang_exists = check_yang_file_exists(module)
        missing_by_category[category].append({
            "module": module,
            "yang_exists": yang_exists
        })
    
    # Report by category
    print("\nMissing Swagger Specs by Category:")
    print("=" * 70)
    
    total_with_yang = 0
    for category in sorted(missing_by_category.keys()):
        modules = missing_by_category[category]
        with_yang = sum(1 for m in modules if m["yang_exists"])
        total_with_yang += with_yang
        
        print(f"\n{category.upper()} ({len(modules)} modules, {with_yang} with YANG files):")
        print("-" * 70)
        
        for m in modules:
            yang_status = "✅ YANG" if m["yang_exists"] else "❌ No YANG"
            print(f"  {yang_status}  {m['module']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total modules with trees but no swaggers: {len(missing)}")
    print(f"  - With YANG files: {total_with_yang} (can generate specs)")
    print(f"  - Without YANG files: {len(missing) - total_with_yang} (investigate)")
    
    # Actionable recommendations
    print("\n" + "=" * 70)
    print("ACTIONABLE ITEMS")
    print("=" * 70)
    
    # Priority categories that should have specs
    priority_cats = ["oper", "rpc", "cfg", "events", "ietf", "openconfig"]
    for cat in priority_cats:
        if cat in missing_by_category:
            with_yang = [m for m in missing_by_category[cat] if m["yang_exists"]]
            if with_yang:
                print(f"\n🎯 {cat.upper()}: {len(with_yang)} modules need swagger specs")
                for m in with_yang[:5]:  # Show first 5
                    print(f"   - {m['module']}")
                if len(with_yang) > 5:
                    print(f"   ... and {len(with_yang) - 5} more")
    
    # Save detailed report
    output_file = BASE_DIR / "missing_swagger_specs.json"
    report = {
        "total_tree_modules": len(tree_modules),
        "total_swagger_specs": len(existing_specs),
        "missing_count": len(missing),
        "missing_with_yang": total_with_yang,
        "missing_by_category": {
            cat: [m["module"] for m in modules if m["yang_exists"]]
            for cat, modules in missing_by_category.items()
        }
    }
    
    output_file.write_text(json.dumps(report, indent=2))
    print(f"\n📄 Detailed report saved: {output_file}")

if __name__ == "__main__":
    main()
