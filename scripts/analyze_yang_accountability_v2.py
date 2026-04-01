#!/usr/bin/env python3
"""
YANG Module Accountability Analyzer v2

Comprehensive accountability for every YANG module:
- Which swagger categories each module appears in (some appear in multiple)
- Direct links to OpenAPI spec pages
- Direct links to pyang tree HTML files
- Classification: types, deviation, native-aug, common, etc.

Usage: python analyze_yang_accountability_v2.py
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
YANG_DIR = BASE_DIR / "references" / "17181-YANG-modules"
TREE_DIR = BASE_DIR / "yang-trees"
OUTPUT_MD = BASE_DIR / "YANG_MODULE_ACCOUNTABILITY.md"
OUTPUT_JSON = BASE_DIR / "yang_accountability.json"

# GitHub Pages base URL
GH_PAGES = "https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger"

# All swagger model folders
MODEL_FOLDERS = {
    "swagger-oper-model": {"label": "Operational", "emoji": "🔵"},
    "swagger-cfg-model": {"label": "Configuration", "emoji": "⚙️"},
    "swagger-native-config-model": {"label": "Native Config", "emoji": "🏠"},
    "swagger-openconfig-model": {"label": "OpenConfig", "emoji": "🌍"},
    "swagger-ietf-model": {"label": "IETF", "emoji": "📜"},
    "swagger-mib-model": {"label": "MIB", "emoji": "📡"},
    "swagger-rpc-model": {"label": "RPC", "emoji": "⚡"},
    "swagger-events-model": {"label": "Events", "emoji": "🔔"},
    "swagger-other-model": {"label": "Other", "emoji": "📦"},
}


def scan_all_specs():
    """Scan api/ and api-v2/ folders to find every spec file and which modules they contain."""
    # Returns: dict[module_name] -> list of {folder, api_version, spec_name}
    module_specs = defaultdict(list)

    for folder_name in MODEL_FOLDERS:
        folder_path = BASE_DIR / folder_name
        for api_dir_name in ["api-v2", "api"]:
            api_path = folder_path / api_dir_name
            if not api_path.exists():
                continue
            for json_file in sorted(api_path.glob("*.json")):
                if json_file.stem == "manifest" or json_file.stem.startswith("all-"):
                    continue
                spec_name = json_file.stem
                module_specs[spec_name].append({
                    "folder": folder_name,
                    "api_dir": api_dir_name,
                    "spec_name": spec_name,
                })

    return module_specs


def scan_tree_files():
    """Scan yang-trees/ for HTML tree files."""
    trees = {}
    if TREE_DIR.exists():
        for f in TREE_DIR.glob("*.html"):
            trees[f.stem] = f"yang-trees/{f.name}"
    return trees


def classify_yang_module(filename, content=""):
    """Classify a YANG module into its primary type.
    Returns (classification, reason_if_excluded)"""
    name = filename.replace(".yang", "")

    # Deviation modules
    if "-deviation" in name.lower() or name.endswith("-devs") or "-devs-" in name:
        return "deviation", "Deviation module - modifies other modules"
    # OpenConfig deviations
    if name.startswith("cisco-xe-") and "openconfig" in name.lower():
        return "deviation", "OpenConfig deviation module"

    # Type definition modules
    if name.endswith("-types") or "-types-" in name:
        return "types", "Type definitions only"
    if name.startswith("openconfig-") and "-types" in name:
        return "types", "OpenConfig type definitions only"
    if name.startswith("ietf-") and "-types" in name:
        return "types", "IETF type definitions only"
    if name.startswith("iana-") and "-types" in name:
        return "types", "IANA type definitions only"

    # Common/shared modules
    if name == "cisco-semver":
        return "common", "Semantic versioning module"
    if "common" in name.lower() and not name.startswith("Cisco-IOS-XE-"):
        return "common", "Common/shared protocol module"
    if name.startswith("Cisco-IOS-XE-") and (name.endswith("-common") or "-common-" in name):
        return "common", "Common type definitions and groupings"

    # Native augmentations
    if name.startswith("Cisco-IOS-XE-") and name != "Cisco-IOS-XE-native":
        if content and re.search(r'augment\s+"/ios:', content):
            return "native-aug", "Augments native module - included in native specs"

    # RPC augmentations (augment Cisco-IOS-XE-rpc, not standalone RPCs)
    if name.startswith("Cisco-IOS-XE-") and name.endswith("-rpc") and name != "Cisco-IOS-XE-rpc":
        if content and re.search(r'augment\s+"/ios-xe-rpc:', content):
            return "rpc-aug", "Augments Cisco-IOS-XE-rpc - included in main RPC spec"

    # Native module itself
    if name == "Cisco-IOS-XE-native":
        return "native", "Main native module - split into multiple specs"

    # Cisco IOS-XE events (check before oper)
    if name.startswith("Cisco-IOS-XE-") and "-events" in name:
        return "events", ""
    # Cisco IOS-XE oper
    if name.startswith("Cisco-IOS-XE-") and "-oper" in name:
        return "oper", ""
    # Cisco IOS-XE RPC
    if name.startswith("Cisco-IOS-XE-") and name.endswith("-rpc"):
        return "rpc", ""
    if name == "Cisco-IOS-XE-rpc":
        return "rpc", ""
    # Cisco IOS-XE MIB
    if name.startswith("Cisco-IOS-XE-") and ("-mib" in name.lower()):
        return "mib", ""
    # Cisco IOS-XE CFG
    if name.startswith("Cisco-IOS-XE-") and name.endswith("-cfg"):
        return "cfg", ""
    # Remaining Cisco IOS-XE (probably cfg)
    if name.startswith("Cisco-IOS-XE-"):
        if content and re.search(r'^\s*rpc\s+\w+\s*{', content, re.MULTILINE):
            return "rpc", ""
        if content and re.search(r'^\s*notification\s+', content, re.MULTILINE):
            return "events", ""
        return "cfg", ""

    # OpenConfig
    if name.startswith("openconfig-"):
        return "openconfig", ""

    # IETF/IANA
    if name.startswith("ietf-") or name.startswith("iana-"):
        return "ietf", ""

    # MIB modules
    if name.endswith("-MIB") or "-MIB-" in name:
        return "mib", ""
    if name.startswith("CISCO-") and "MIB" in name:
        return "mib", ""

    # Tailf/ConfD
    if name.startswith("tailf-") or name.startswith("Tailf-"):
        return "other", "Tail-f infrastructure module"
    if "confd" in name.lower():
        return "other", "ConfD infrastructure module"

    # Content-based detection
    if content:
        if re.search(r'^\s*rpc\s+\w+\s*{', content, re.MULTILINE):
            return "rpc", ""
        if re.search(r'^\s*notification\s+', content, re.MULTILINE):
            return "events", ""
        if re.search(r'^\s*typedef\s+', content, re.MULTILINE) and \
           not re.search(r'^\s*container\s+', content, re.MULTILINE):
            return "types", "Contains only type definitions"

    return "other", ""


def classify_spec_only_module(name, specs):
    """Classify a module that has a spec but no .yang source file."""
    # Determine category from spec folder locations
    folders = set(s["folder"] for s in specs) if specs else set()

    # MIB modules
    if "swagger-mib-model" in folders or name.endswith("-MIB") or "-MIB-" in name:
        return "mib", None
    if name.startswith("CISCO-") or name.startswith("SNMP") or name.startswith("RFC"):
        return "mib", None
    # Well-known MIB naming patterns
    mib_patterns = ["IF-MIB", "IP-MIB", "TCP-MIB", "UDP-MIB", "ENTITY-", "BRIDGE-",
                    "RMON", "SONET-", "DS1-", "DS3-", "TUNNEL-", "OSPF-", "BGP4-",
                    "PIM-", "IGMP-", "NHRP-", "LLDP-", "MPLS-", "POWER-", "ETHER",
                    "FRAME-RELAY", "DRAFT-", "DIFFSERV", "DISMAN-", "INT-SERV",
                    "INTEGRATED-", "EXPRESSION-", "NOTIFICATION-LOG", "TOKENRING",
                    "TOKEN-RING", "ATM-", "DIAL-CONTROL", "P-BRIDGE", "Q-BRIDGE"]
    for pat in mib_patterns:
        if name.startswith(pat) or name == pat.rstrip("-"):
            return "mib", None

    # Native split specs
    if "swagger-native-config-model" in folders or name.startswith("native-"):
        return "native", None

    # Events
    if "swagger-events-model" in folders:
        return "events", None

    # RPC
    if "swagger-rpc-model" in folders:
        return "rpc", None

    # Operational
    if "swagger-oper-model" in folders:
        return "oper", None

    # Configuration
    if "swagger-cfg-model" in folders:
        return "cfg", None

    # OpenConfig
    if "swagger-openconfig-model" in folders or name.startswith("openconfig-"):
        return "openconfig", None

    # IETF
    if "swagger-ietf-model" in folders or name.startswith("ietf-"):
        return "ietf", None

    # Other
    if "swagger-other-model" in folders:
        return "other", None

    return "other", None


def build_spec_url(folder, api_dir, spec_name):
    """Build the URL to view this spec in the Swagger UI."""
    # index-v2.html handles both api-v2/ and api/ specs (with fallback)
    return f"{folder}/index-v2.html#spec={spec_name}"


def main():
    print("=" * 60)
    print("YANG Module Accountability Analyzer v2")
    print("=" * 60)

    # 1. Scan all specs in all api/ and api-v2/ folders
    print("\nScanning all OpenAPI spec files...")
    module_specs = scan_all_specs()
    print(f"  Found {len(module_specs)} unique spec names across all folders")

    # 2. Scan tree files
    print("Scanning YANG tree files...")
    tree_files = scan_tree_files()
    print(f"  Found {len(tree_files)} tree files")

    # 3. Analyze all YANG source modules
    yang_files = sorted(YANG_DIR.glob("*.yang"))
    print(f"\nAnalyzing {len(yang_files)} YANG source modules...")

    modules = []
    classifications = defaultdict(list)

    for yang_file in yang_files:
        name = yang_file.stem
        try:
            content = yang_file.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            content = ""

        # Classify
        classification, reason = classify_yang_module(yang_file.name, content)

        # Find all specs this module appears in (by name match)
        specs_found = module_specs.get(name, [])

        # Determine which swagger categories have this module
        # Prefer api-v2 (deep-path) over api (legacy)
        categories = []
        seen_folders = set()
        for spec in specs_found:
            folder = spec["folder"]
            if folder not in seen_folders:
                seen_folders.add(folder)
                # Pick the best api_dir for this folder
                api_dirs = [s["api_dir"] for s in specs_found if s["folder"] == folder]
                best_api = "api-v2" if "api-v2" in api_dirs else "api"
                url = build_spec_url(folder, best_api, name)
                categories.append({
                    "folder": folder,
                    "label": MODEL_FOLDERS[folder]["label"],
                    "api_dir": best_api,
                    "spec_url": url,
                })

        # Tree file
        tree_url = tree_files.get(name)

        has_spec = len(categories) > 0

        module_info = {
            "name": name,
            "classification": classification,
            "has_spec": has_spec,
            "categories": categories,
            "tree_url": tree_url,
            "reason_excluded": reason if not has_spec and reason else None,
        }
        modules.append(module_info)
        classifications[classification].append(module_info)

    # 4. Add modules that have specs but no .yang source file
    #    (e.g., MIB specs, native split specs, etc.)
    yang_names = set(m["name"] for m in modules)
    spec_only_count = 0
    for spec_name, specs in module_specs.items():
        if spec_name in yang_names:
            continue  # Already tracked from YANG source

        # Classify based on spec location and name
        classification, reason = classify_spec_only_module(spec_name, specs)

        # Build categories
        categories = []
        seen_folders = set()
        for spec in specs:
            folder = spec["folder"]
            if folder not in seen_folders:
                seen_folders.add(folder)
                api_dirs = [s["api_dir"] for s in specs if s["folder"] == folder]
                best_api = "api-v2" if "api-v2" in api_dirs else "api"
                url = build_spec_url(folder, best_api, spec_name)
                categories.append({
                    "folder": folder,
                    "label": MODEL_FOLDERS[folder]["label"],
                    "api_dir": best_api,
                    "spec_url": url,
                })

        tree_url = tree_files.get(spec_name)

        module_info = {
            "name": spec_name,
            "classification": classification,
            "has_spec": True,
            "categories": categories,
            "tree_url": tree_url,
            "reason_excluded": None,
        }
        modules.append(module_info)
        classifications[classification].append(module_info)
        spec_only_count += 1

    print(f"  Added {spec_only_count} spec-only modules (no .yang source file)")

    # 5. Add tree-only modules (have tree but no spec and no .yang source)
    all_names = set(m["name"] for m in modules)
    tree_only_count = 0
    for tree_name, tree_url_val in tree_files.items():
        if tree_name in all_names:
            continue
        if tree_name in ("index", "mib-trees-index"):
            continue  # Skip index pages

        classification, reason = classify_spec_only_module(tree_name, [])
        module_info = {
            "name": tree_name,
            "classification": classification,
            "has_spec": False,
            "categories": [],
            "tree_url": tree_url_val,
            "reason_excluded": reason or "Has tree but no spec",
        }
        modules.append(module_info)
        classifications[classification].append(module_info)
        tree_only_count += 1

    if tree_only_count:
        print(f"  Added {tree_only_count} tree-only modules (tree but no spec or .yang source)")

    # 6. Sort modules by name
    modules.sort(key=lambda m: m["name"].lower())

    # 7. Print summary
    total = len(modules)
    with_spec = sum(1 for m in modules if m["has_spec"])
    with_tree = sum(1 for m in modules if m["tree_url"])
    multi_cat = sum(1 for m in modules if len(m["categories"]) > 1)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total YANG modules:        {total}")
    print(f"Modules with specs:        {with_spec} ({100*with_spec/total:.1f}%)")
    print(f"Modules with tree files:   {with_tree}")
    print(f"Modules in multiple cats:  {multi_cat}")

    print("\nBy Classification:")
    class_order = ["oper", "rpc", "cfg", "openconfig", "ietf", "mib", "events",
                   "native", "other", "types", "deviation", "common", "native-aug", "rpc-aug"]
    for cls in class_order:
        mods = classifications.get(cls, [])
        if not mods:
            continue
        ct = len(mods)
        ws = sum(1 for m in mods if m["has_spec"])
        pct = 100 * ws / ct if ct > 0 else 0
        print(f"  {cls:15s} {ct:4d} modules, {ws:4d} with specs ({pct:.0f}%)")

    # 8. Generate reports
    generate_json(modules, classifications, total, with_spec, with_tree, multi_cat)
    generate_markdown(modules, classifications, total, with_spec, with_tree, multi_cat)

    print(f"\nReports generated:")
    print(f"  - {OUTPUT_JSON}")
    print(f"  - {OUTPUT_MD}")


def generate_json(modules, classifications, total, with_spec, with_tree, multi_cat):
    """Generate the JSON data file for the HTML viewer."""
    class_order = ["oper", "rpc", "cfg", "openconfig", "ietf", "mib", "events",
                   "native", "other", "types", "deviation", "common", "native-aug", "rpc-aug"]

    cat_stats = {}
    for cls in class_order:
        mods = classifications.get(cls, [])
        if not mods:
            continue
        cat_stats[cls] = {
            "total": len(mods),
            "with_specs": sum(1 for m in mods if m["has_spec"]),
            "coverage_pct": round(100 * sum(1 for m in mods if m["has_spec"]) / len(mods), 1)
        }

    report = {
        "generated": datetime.now().isoformat(),
        "ios_xe_version": "17.18.1",
        "total_modules": total,
        "modules_with_specs": with_spec,
        "modules_with_trees": with_tree,
        "modules_multi_category": multi_cat,
        "categories": cat_stats,
        "modules": modules,
    }

    OUTPUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def generate_markdown(modules, classifications, total, with_spec, with_tree, multi_cat):
    """Generate the markdown accountability report with links."""
    now = datetime.now()

    L = []
    L.append("# YANG Module Accountability Report")
    L.append("")
    L.append(f"**Date:** {now.strftime('%B %d, %Y')}")
    L.append(f"**IOS-XE Version:** 17.18.1")
    L.append(f"**Total YANG Modules:** {total}")
    L.append(f"**Modules with OpenAPI Specs:** {with_spec} ({100*with_spec/total:.1f}%)")
    L.append(f"**Modules with YANG Trees:** {with_tree}")
    L.append(f"**Modules in Multiple Categories:** {multi_cat}")
    L.append("")
    L.append("> **Interactive Report:** [View the HTML accountability report](yang-accountability.html) with search, filtering, and clickable links.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Executive Summary")
    L.append("")
    L.append("This report provides **100% accountability** for every YANG module in the")
    L.append("`references/17181-YANG-modules/` folder. Each module is either:")
    L.append("")
    L.append("1. **Documented** with one or more OpenAPI specs (some modules appear in multiple categories)")
    L.append("2. **Excluded** with documented reason (types, deviations, augments, etc.)")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Category Summary")
    L.append("")
    L.append("| Classification | Total | With Specs | Coverage | Notes |")
    L.append("|----------------|-------|------------|----------|-------|")

    class_order = ["oper", "rpc", "cfg", "openconfig", "ietf", "mib", "events",
                   "native", "other", "types", "deviation", "common", "native-aug", "rpc-aug"]
    excluded_classes = {"types", "deviation", "common", "native-aug", "rpc-aug"}

    for cls in class_order:
        mods = classifications.get(cls, [])
        if not mods:
            continue
        ct = len(mods)
        ws = sum(1 for m in mods if m["has_spec"])
        if cls in excluded_classes:
            coverage = "N/A"
            notes = "Excluded by design"
        else:
            coverage = f"{100*ws/ct:.0f}%"
            notes = ""
        L.append(f"| **{cls}** | {ct} | {ws} | {coverage} | {notes} |")

    L.append("")
    L.append("---")
    L.append("")
    L.append("## Detailed Module List")
    L.append("")

    for cls in class_order:
        mods = classifications.get(cls, [])
        if not mods:
            continue
        ct = len(mods)
        ws = sum(1 for m in mods if m["has_spec"])

        L.append(f"### {cls.upper()} ({ct} modules)")
        L.append("")

        if cls in excluded_classes:
            reason = mods[0]["reason_excluded"] if mods and mods[0].get("reason_excluded") else "Excluded by design"
            L.append(f"*{reason}*")
            L.append("")
            L.append("<details>")
            L.append(f"<summary>Click to expand {ct} {cls} modules</summary>")
            L.append("")
            L.append("| Module | Tree |")
            L.append("|--------|------|")
            for m in sorted(mods, key=lambda x: x["name"]):
                tree_link = f"[🌳]({m['tree_url']})" if m["tree_url"] else "-"
                L.append(f"| {m['name']} | {tree_link} |")
            L.append("")
            L.append("</details>")
        else:
            L.append(f"| Module | Categories | Spec Links | Tree |")
            L.append(f"|--------|------------|------------|------|")
            for m in sorted(mods, key=lambda x: x["name"]):
                cats = ", ".join(c["label"] for c in m["categories"]) if m["categories"] else "-"
                if m["categories"]:
                    spec_links = " ".join(
                        f"[{c['label']}]({c['spec_url']})" for c in m["categories"]
                    )
                else:
                    spec_links = "❌ No spec"
                tree_link = f"[🌳]({m['tree_url']})" if m["tree_url"] else "-"
                L.append(f"| {m['name']} | {cats} | {spec_links} | {tree_link} |")

        L.append("")

    # Multi-category modules section
    multi = [m for m in modules if len(m["categories"]) > 1]
    if multi:
        L.append("---")
        L.append("")
        L.append(f"## Modules in Multiple Categories ({len(multi)})")
        L.append("")
        L.append("These modules appear in more than one swagger category:")
        L.append("")
        L.append("| Module | Categories |")
        L.append("|--------|------------|")
        for m in sorted(multi, key=lambda x: x["name"]):
            cats = ", ".join(c["label"] for c in m["categories"])
            L.append(f"| {m['name']} | {cats} |")
        L.append("")

    # Footer
    L.append("---")
    L.append("")
    L.append("## Exclusion Categories Explained")
    L.append("")
    L.append("| Classification | Reason |")
    L.append("|----------------|--------|")
    L.append("| **types** | Contains only `typedef` and `grouping` statements — no API operations |")
    L.append("| **deviation** | Modifies other modules' behavior — no standalone API |")
    L.append("| **common** | Infrastructure modules (tailf-*, cisco-semver) — shared types only |")
    L.append("| **native-aug** | Augments Cisco-IOS-XE-native — content is included in Native Config specs |")
    L.append("| **rpc-aug** | Augments Cisco-IOS-XE-rpc — content is included in the main RPC spec |")
    L.append("")
    L.append(f"*Report generated: {now.isoformat()}*")

    OUTPUT_MD.write_text("\n".join(L), encoding='utf-8')


if __name__ == "__main__":
    main()
