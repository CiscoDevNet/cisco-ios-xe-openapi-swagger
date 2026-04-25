#!/usr/bin/env python3
"""
Comprehensive audit of the YANG accountability report.
Cross-checks: YANG source files, spec files (api/api-v2), search-index.json,
yang_accountability.json, manifest.json files, and YANG tree files.
"""

import json
import os
import glob
import re
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():

    # ─── 1. Scan YANG source files ───
    yang_dir = os.path.join(BASE, "references", "17181-YANG-modules")
    yang_source_files = set()
    if os.path.isdir(yang_dir):
        for f in os.listdir(yang_dir):
            if f.endswith(".yang"):
                name = f.replace(".yang", "")
                # Strip revision suffix like @2024-03-01
                name = re.sub(r"@\d{4}-\d{2}-\d{2}$", "", name)
                yang_source_files.add(name)
    print(f"=== YANG SOURCE FILES: {len(yang_source_files)} ===")

    # ─── 2. Scan all spec files (api and api-v2) ───
    model_folders = {
        "Operational": "swagger-oper-model",
        "Configuration": "swagger-cfg-model",
        "Native": "swagger-native-config-model",
        "OpenConfig": "swagger-openconfig-model",
        "IETF": "swagger-ietf-model",
        "MIB": "swagger-mib-model",
        "RPC": "swagger-rpc-model",
        "Events": "swagger-events-model",
        "Other": "swagger-other-model",
    }

    spec_modules_v2 = {}  # module_name -> list of categories (from api-v2)
    spec_modules_v1 = {}  # module_name -> list of categories (from api only, no api-v2)
    all_spec_modules = {}  # module_name -> list of categories (union)

    for cat, folder in model_folders.items():
        # api-v2
        api_v2_dir = os.path.join(BASE, folder, "api-v2")
        if os.path.isdir(api_v2_dir):
            for f in os.listdir(api_v2_dir):
                if f.endswith(".json") and f != "manifest.json":
                    name = f.replace(".json", "")
                    spec_modules_v2.setdefault(name, []).append(cat)
                    all_spec_modules.setdefault(name, []).append(cat)

        # api (v1)
        api_dir = os.path.join(BASE, folder, "api")
        if os.path.isdir(api_dir):
            for f in os.listdir(api_dir):
                if f.endswith(".json") and f != "manifest.json":
                    name = f.replace(".json", "")
                    spec_modules_v1.setdefault(name, []).append(cat)
                    if name not in all_spec_modules:
                        all_spec_modules[name] = [cat]

    print(f"\n=== SPEC FILES ===")
    print(f"  api-v2 specs: {len(spec_modules_v2)}")
    print(f"  api-only (v1, no v2): {len([k for k in spec_modules_v1 if k not in spec_modules_v2])}")
    print(f"  Total unique specs: {len(all_spec_modules)}")

    # ─── 3. Scan YANG tree files ───
    tree_dir = os.path.join(BASE, "yang-trees")
    tree_modules = set()
    if os.path.isdir(tree_dir):
        for f in os.listdir(tree_dir):
            if f.endswith(".html"):
                name = f.replace(".html", "")
                tree_modules.add(name)
    print(f"\n=== YANG TREE FILES: {len(tree_modules)} ===")

    # ─── 4. Load search-index.json ───
    search_index_path = os.path.join(BASE, "search-index.json")
    search_modules = {}
    with open(search_index_path, encoding="utf-8") as f:
        search_data = json.load(f)
    search_entries = search_data.get("modules", search_data) if isinstance(search_data, dict) else search_data
    if isinstance(search_entries, list):
        for entry in search_entries:
            mod_name = entry.get("module") or entry.get("name")
            if mod_name:
                search_modules[mod_name] = entry
    elif isinstance(search_entries, dict):
        for mod_name, entry in search_entries.items():
            if isinstance(entry, dict):
                entry["module"] = mod_name
                search_modules[mod_name] = entry
    print(f"\n=== SEARCH INDEX ENTRIES: {len(search_modules)} ===")

    # ─── 5. Load yang_accountability.json ───
    acct_path = os.path.join(BASE, "yang_accountability.json")
    with open(acct_path) as f:
        acct_data = json.load(f)
    acct_modules = {}
    for m in acct_data["modules"]:
        acct_modules[m["name"]] = m
    print(f"\n=== ACCOUNTABILITY REPORT MODULES: {len(acct_modules)} ===")

    # ─── 6. Load manifests ───
    manifest_counts = {}
    for cat, folder in model_folders.items():
        mf_path = os.path.join(BASE, folder, "api-v2", "manifest.json")
        if os.path.isfile(mf_path):
            with open(mf_path) as f:
                mf = json.load(f)
            manifest_counts[cat] = {
                "total_modules": mf.get("total_modules", 0),
                "modules_list": len(mf.get("modules", [])),
                "total_paths": mf.get("total_paths", 0),
                "total_operations": mf.get("total_operations", 0),
            }
            # Verify manifest module count matches actual api-v2 files
            api_v2_dir = os.path.join(BASE, folder, "api-v2")
            actual_files = len([f for f in os.listdir(api_v2_dir) if f.endswith(".json") and f != "manifest.json"])
            if actual_files != mf["total_modules"]:
                print(f"  WARNING: {cat} manifest says {mf['total_modules']} but has {actual_files} actual spec files!")
            if actual_files != len(mf.get("modules", [])):
                print(f"  WARNING: {cat} manifest modules list has {len(mf['modules'])} but {actual_files} actual files!")

    print(f"\n=== MANIFEST COUNTS (api-v2) ===")
    total_v2_specs = 0
    for cat in sorted(manifest_counts):
        mc = manifest_counts[cat]
        print(f"  {cat}: {mc['total_modules']} specs, {mc['total_paths']} paths, {mc['total_operations']} ops")
        total_v2_specs += mc["total_modules"]
    print(f"  TOTAL: {total_v2_specs} specs")

    # ─── 7. CROSS-CHECK: YANG sources in accountability report ───
    print(f"\n{'='*60}")
    print(f"=== CROSS-CHECK 1: YANG sources vs Accountability Report ===")
    missing_from_acct = yang_source_files - set(acct_modules.keys())
    extra_in_acct = set(acct_modules.keys()) - yang_source_files
    if missing_from_acct:
        print(f"\n  MISSING from accountability ({len(missing_from_acct)} modules):")
        for m in sorted(missing_from_acct)[:30]:
            has_spec = "HAS SPEC" if m in all_spec_modules else "no spec"
            has_tree = "HAS TREE" if m in tree_modules else "no tree"
            print(f"    - {m} ({has_spec}, {has_tree})")
        if len(missing_from_acct) > 30:
            print(f"    ... and {len(missing_from_acct)-30} more")
    else:
        print("  OK: All YANG source modules are in the accountability report")

    if extra_in_acct:
        print(f"\n  EXTRA in accountability ({len(extra_in_acct)} modules not in YANG sources):")
        for m in sorted(extra_in_acct)[:20]:
            print(f"    - {m}")
    else:
        print("  OK: No extra modules in accountability report")

    # ─── 8. CROSS-CHECK: Specs vs Accountability ───
    print(f"\n{'='*60}")
    print(f"=== CROSS-CHECK 2: Spec files vs Accountability Report ===")
    specs_missing_from_acct = set()
    specs_wrong_has_spec = set()
    for mod in all_spec_modules:
        if mod not in acct_modules:
            specs_missing_from_acct.add(mod)
        elif not acct_modules[mod].get("has_spec"):
            specs_wrong_has_spec.add(mod)

    if specs_missing_from_acct:
        print(f"\n  Modules WITH specs but MISSING from accountability ({len(specs_missing_from_acct)}):")
        for m in sorted(specs_missing_from_acct):
            print(f"    - {m} (categories: {all_spec_modules[m]})")
    else:
        print("  OK: All modules with specs are in accountability report")

    if specs_wrong_has_spec:
        print(f"\n  Modules WITH specs but has_spec=False in report ({len(specs_wrong_has_spec)}):")
        for m in sorted(specs_wrong_has_spec):
            print(f"    - {m} (actual categories: {all_spec_modules[m]})")
    else:
        print("  OK: All spec modules have has_spec=True in report")

    # Check reverse: accountability says has_spec but no actual spec file
    acct_says_has_spec = {m for m, d in acct_modules.items() if d.get("has_spec")}
    phantom_specs = acct_says_has_spec - set(all_spec_modules.keys())
    if phantom_specs:
        print(f"\n  Modules marked has_spec=True but NO spec file found ({len(phantom_specs)}):")
        for m in sorted(phantom_specs):
            print(f"    - {m}")
    else:
        print("  OK: No phantom specs (all has_spec=True modules have actual files)")

    # ─── 9. CROSS-CHECK: Trees vs Accountability ───
    print(f"\n{'='*60}")
    print(f"=== CROSS-CHECK 3: Tree files vs Accountability Report ===")
    # Exclude known index pages from tree check
    tree_index_pages = {"index", "mib-trees-index"}
    trees_missing_from_acct = tree_modules - set(acct_modules.keys()) - tree_index_pages
    if trees_missing_from_acct:
        print(f"\n  Modules WITH trees but MISSING from accountability ({len(trees_missing_from_acct)}):")
        for m in sorted(trees_missing_from_acct)[:20]:
            print(f"    - {m}")
    else:
        print("  OK: All tree modules are in accountability report")

    # Check tree_url accuracy
    trees_wrong = []
    for mod, d in acct_modules.items():
        tree_url = d.get("tree_url", "")
        has_tree_file = mod in tree_modules
        if has_tree_file and not tree_url:
            trees_wrong.append((mod, "has tree file but no tree_url"))
        elif not has_tree_file and tree_url:
            trees_wrong.append((mod, "has tree_url but no tree file"))
    if trees_wrong:
        print(f"\n  Tree URL mismatches ({len(trees_wrong)}):")
        for m, reason in sorted(trees_wrong)[:20]:
            print(f"    - {m}: {reason}")
    else:
        print("  OK: Tree URLs match actual tree files")

    # ─── 10. CROSS-CHECK: Search index vs Specs ───
    print(f"\n{'='*60}")
    print(f"=== CROSS-CHECK 4: Search Index vs Spec Files ===")
    specs_not_in_search = set(all_spec_modules.keys()) - set(search_modules.keys())
    if specs_not_in_search:
        print(f"\n  Spec modules NOT in search index ({len(specs_not_in_search)}):")
        for m in sorted(specs_not_in_search):
            print(f"    - {m} (categories: {all_spec_modules[m]})")
    else:
        print("  OK: All spec modules are in search index")

    search_no_spec = set()
    for mod, entry in search_modules.items():
        if mod not in all_spec_modules:
            search_no_spec.add(mod)
    if search_no_spec:
        print(f"\n  Search entries with NO spec file ({len(search_no_spec)}):")
        for m in sorted(search_no_spec)[:20]:
            print(f"    - {m} (type: {search_modules[m].get('type', 'unknown')})")
        if len(search_no_spec) > 20:
            print(f"    ... and {len(search_no_spec)-20} more")
    else:
        print("  OK: All search entries have spec files")

    # ─── 11. CROSS-CHECK: Accountability categories vs actual spec locations ───
    print(f"\n{'='*60}")
    print(f"=== CROSS-CHECK 5: Category Assignments ===")
    cat_mismatches = []
    for mod, d in acct_modules.items():
        cat_entries = d.get("categories", [])
        acct_cats = set()
        for c in cat_entries:
            if isinstance(c, dict):
                lbl = c.get("label", "").lower()
                # Normalize "native config" -> "native"
                lbl = lbl.replace(" config", "")
                acct_cats.add(lbl)
            else:
                acct_cats.add(str(c).lower())
        actual_cats_raw = set(all_spec_modules.get(mod, []))
        actual_cats = set(c.lower() for c in actual_cats_raw)
    
        # Only compare if module has specs
        if actual_cats and acct_cats:
            missing_cats = actual_cats - acct_cats
            if missing_cats:
                cat_mismatches.append((mod, f"missing categories: {missing_cats}, has: {acct_cats}"))

    if cat_mismatches:
        print(f"\n  Category mismatches ({len(cat_mismatches)}):")
        for m, reason in sorted(cat_mismatches)[:20]:
            print(f"    - {m}: {reason}")
    else:
        print("  OK: All category assignments match actual spec locations")

    # ─── 12. CROSS-CHECK: Manifest vs index.html stats ───
    print(f"\n{'='*60}")
    print(f"=== CROSS-CHECK 6: Manifest consistency ===")
    for cat, folder in model_folders.items():
        api_v2_dir = os.path.join(BASE, folder, "api-v2")
        mf_path = os.path.join(api_v2_dir, "manifest.json")
        if not os.path.isfile(mf_path):
            print(f"  WARNING: No manifest.json for {cat}")
            continue
        with open(mf_path) as f:
            mf = json.load(f)
    
        # Count actual spec files
        actual_specs = [f for f in os.listdir(api_v2_dir) if f.endswith(".json") and f != "manifest.json"]
    
        # Verify modules list matches files
        manifest_modules = set(mf.get("modules", []))
        actual_module_names = set(f.replace(".json", "") for f in actual_specs)
    
        missing_in_manifest = actual_module_names - manifest_modules
        extra_in_manifest = manifest_modules - actual_module_names
    
        if missing_in_manifest:
            print(f"  {cat}: {len(missing_in_manifest)} spec files NOT listed in manifest:")
            for m in sorted(missing_in_manifest):
                print(f"    - {m}")
        if extra_in_manifest:
            print(f"  {cat}: {len(extra_in_manifest)} manifest entries with NO spec file:")
            for m in sorted(extra_in_manifest):
                print(f"    - {m}")
        if not missing_in_manifest and not extra_in_manifest:
            print(f"  {cat}: OK ({len(actual_specs)} specs match manifest)")

    # ─── FINAL SUMMARY ───
    print(f"\n{'='*60}")
    print(f"=== FINAL AUDIT SUMMARY ===")
    print(f"  YANG source files:       {len(yang_source_files)}")
    print(f"  Accountability modules:  {len(acct_modules)}")
    print(f"  Total unique specs:      {len(all_spec_modules)} (api-v2: {len(spec_modules_v2)}, v1-only: {len([k for k in spec_modules_v1 if k not in spec_modules_v2])})")
    print(f"  YANG tree files:         {len(tree_modules)}")
    print(f"  Search index entries:    {len(search_modules)}")
    print(f"  Multi-category modules:  {acct_data.get('modules_multi_category', 'N/A')}")

    issues = []
    if missing_from_acct: issues.append(f"{len(missing_from_acct)} YANG modules missing from accountability")
    if specs_missing_from_acct: issues.append(f"{len(specs_missing_from_acct)} spec modules missing from accountability")
    if specs_wrong_has_spec: issues.append(f"{len(specs_wrong_has_spec)} modules with wrong has_spec flag")
    if phantom_specs: issues.append(f"{len(phantom_specs)} phantom specs in accountability")
    if trees_wrong: issues.append(f"{len(trees_wrong)} tree URL mismatches")
    if specs_not_in_search: issues.append(f"{len(specs_not_in_search)} specs not in search index")
    if cat_mismatches: issues.append(f"{len(cat_mismatches)} category mismatches")

    if issues:
        print(f"\n  ISSUES FOUND ({len(issues)}):")
        for i in issues:
            print(f"    - {i}")
    else:
        print(f"\n  ALL CHECKS PASSED!")

if __name__ == '__main__':
    main()
