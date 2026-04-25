#!/usr/bin/env python3
"""Audit: find modules that have a YANG tree but no API spec."""
import json
import os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():

    # Load accountability
    with open(os.path.join(BASE, "yang_accountability.json"), encoding="utf-8") as f:
        data = json.load(f)

    # Also do a direct filesystem check
    tree_dir = os.path.join(BASE, "yang-trees")
    tree_files = set()
    if os.path.isdir(tree_dir):
        for fn in os.listdir(tree_dir):
            if fn.endswith(".html") and fn not in ("index.html", "mib-trees-index.html"):
                tree_files.add(fn.replace(".html", ""))

    # Check all spec folders directly
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

    all_spec_modules = set()
    spec_to_cats = {}
    for cat, folder in model_folders.items():
        for api_dir in ["api-v2", "api"]:
            p = os.path.join(BASE, folder, api_dir)
            if os.path.isdir(p):
                for fn in os.listdir(p):
                    if fn.endswith(".json") and fn != "manifest.json":
                        name = fn.replace(".json", "")
                        all_spec_modules.add(name)
                        spec_to_cats.setdefault(name, []).append(cat)

    # Also check YANG source
    yang_dir = os.path.join(BASE, "references", "17181-YANG-modules")
    yang_sources = set()
    if os.path.isdir(yang_dir):
        import re
        for fn in os.listdir(yang_dir):
            if fn.endswith(".yang"):
                name = re.sub(r"@\d{4}-\d{2}-\d{2}$", "", fn.replace(".yang", ""))
                yang_sources.add(name)

    # Find gaps
    tree_no_spec = sorted(tree_files - all_spec_modules)
    tree_and_spec = sorted(tree_files & all_spec_modules)

    print(f"=== TREE VS SPEC AUDIT ===")
    print(f"Total tree files:          {len(tree_files)}")
    print(f"Total spec modules:        {len(all_spec_modules)}")
    print(f"Trees WITH specs:          {len(tree_and_spec)}")
    print(f"Trees WITHOUT specs:       {len(tree_no_spec)}")
    print()

    # Classify the tree-no-spec modules
    cls_counts = Counter()
    has_yang = 0
    no_yang = 0

    print(f"{'Module':<55} {'Has YANG?':<10} {'Classification'}")
    print("-" * 90)
    for name in tree_no_spec:
        in_yang = name in yang_sources
        if in_yang:
            has_yang += 1
        else:
            no_yang += 1
    
        # Try to classify
        cls = "unknown"
        if name.startswith("Cisco-IOS-XE-") and "-oper" in name:
            cls = "oper"
        elif name.startswith("Cisco-IOS-XE-") and name.endswith("-rpc"):
            cls = "rpc"
        elif name.startswith("Cisco-IOS-XE-") and "-events" in name:
            cls = "events"
        elif name.startswith("Cisco-IOS-XE-") and name.endswith("-cfg"):
            cls = "cfg"
        elif name.startswith("Cisco-IOS-XE-") and ("-types" in name or name.endswith("-common")):
            cls = "types/common"
        elif name.startswith("Cisco-IOS-XE-") and "-deviation" in name.lower():
            cls = "deviation"
        elif name.startswith("Cisco-IOS-XE-"):
            # Read the .yang file to check for augment
            yang_path = os.path.join(yang_dir, name + ".yang")
            if os.path.isfile(yang_path):
                try:
                    with open(yang_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    if 'augment "/ios:' in content:
                        cls = "native-aug"
                    elif "rpc " in content:
                        cls = "rpc"
                    elif "notification " in content:
                        cls = "events"
                    else:
                        cls = "cfg/other"
                except OSError:
                    cls = "cfg/other"
            else:
                cls = "cisco-xe"
        elif name.startswith("openconfig-"):
            cls = "openconfig"
        elif name.startswith("ietf-") or name.startswith("iana-"):
            cls = "ietf"
        elif name.startswith("tailf-") or name.startswith("confd"):
            cls = "tailf"
        elif name.endswith("-MIB") or "-MIB-" in name or name.startswith("CISCO-"):
            cls = "mib"
    
        cls_counts[cls] += 1
        yang_str = "YES" if in_yang else "NO"
        print(f"  {name:<53} {yang_str:<10} {cls}")

    print()
    print(f"=== SUMMARY ===")
    print(f"  Has YANG source: {has_yang}")
    print(f"  No YANG source:  {no_yang}")
    print()
    print("By classification:")
    for c, n in cls_counts.most_common():
        print(f"  {c:<15} {n:4d}")

    # Which of these SHOULD have specs? (i.e., not types/deviations/augments)
    should_have = []
    for name in tree_no_spec:
        cls = "unknown"
        if name in yang_sources:
            yang_path = os.path.join(yang_dir, name + ".yang")
            try:
                with open(yang_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                content = ""
        else:
            content = ""
    
        # Skip types, deviations, common, native-aug
        if "-deviation" in name.lower() or name.endswith("-devs") or "-devs-" in name:
            continue
        if name.startswith("cisco-xe-") and "openconfig" in name.lower():
            continue
        if name.endswith("-types") or "-types-" in name:
            continue
        if name == "cisco-semver" or (name.endswith("-common") and not name.startswith("Cisco-IOS-XE-")):
            continue
        if name.startswith("Cisco-IOS-XE-") and (name.endswith("-common") or "-common-" in name):
            continue
        if name.startswith("Cisco-IOS-XE-") and 'augment "/ios:' in content:
            continue
        if name.startswith("tailf-") or "confd" in name.lower():
            continue
        if name.startswith("iana-"):
            continue
    
        should_have.append(name)

    print()
    print(f"=== MODULES THAT SHOULD HAVE SPECS ({len(should_have)}) ===")
    for name in should_have:
        in_yang = "HAS .yang" if name in yang_sources else "NO .yang"
        print(f"  {name:<55} {in_yang}")


if __name__ == '__main__':
    main()
