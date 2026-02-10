#!/usr/bin/env python3
"""
Swagger vs YANG Tree Completeness Audit
========================================
Compares every OpenAPI/Swagger spec against its corresponding pyang tree
to identify under-modeled specs where the Swagger has far fewer paths
than the YANG tree has addressable container/list nodes.

Output: audit_results.json + audit_report.md (sorted by gap severity)
"""

import json
import os
import re
import glob
from pathlib import Path
from collections import defaultdict

# Project root
ROOT = Path(__file__).resolve().parent.parent

# Swagger folders and their spec patterns
SWAGGER_FOLDERS = {
    "swagger-oper-model": "Cisco-IOS-XE-*.json",
    "swagger-rpc-model": "Cisco-IOS-XE-*.json",
    "swagger-cfg-model": "Cisco-IOS-XE-*.json",
    "swagger-openconfig-model": "openconfig-*.json",
    "swagger-ietf-model": "*.json",
    "swagger-mib-model": "*.json",
    "swagger-events-model": "*.json",
    "swagger-native-config-model": "native-*.json",
    "swagger-other-model": "*.json",
}

EXCLUDE_FILES = {
    "manifest.json", "all-operations.json", "all-rpc-operations.json",
    "all-config.json", "all-ietf.json", "all-openconfig.json",
    "all-mib.json", "all-events.json", "all-other.json"
}

YANG_TREES_DIR = ROOT / "yang-trees"


def parse_yang_tree(html_path):
    """
    Parse a pyang tree HTML file and extract structural info.
    
    Returns dict with:
      - total_nodes: all data nodes (containers + lists + leaves + leaf-lists)
      - containers: container nodes (no type, no list key)
      - lists: list nodes (has * [keys])
      - leaves: leaf nodes (has type)
      - leaf_lists: leaf-list nodes (has type + *)
      - top_level_paths: container/list names at depth 1-2 (RESTCONF addressable)
      - depth: max nesting depth
    """
    try:
        with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return None

    # Extract the pyang tree <pre> block (the one starting with "module:" or containing +--r)
    # There may be multiple <pre> blocks (e.g., curl examples), so find the right one
    pre_matches = list(re.finditer(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL))
    tree_text = None
    for m in pre_matches:
        block = m.group(1)
        if 'module:' in block[:50] or '+--r' in block[:200]:
            tree_text = block
            break
    if not tree_text:
        return None
    # Remove HTML tags
    tree_text = re.sub(r'<[^>]+>', '', tree_text)
    # Decode HTML entities
    tree_text = tree_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

    lines = tree_text.split('\n')

    containers = []
    lists = []
    leaves = []
    leaf_lists = []
    top_level_containers = []
    top_level_lists = []
    max_depth = 0
    
    # Track all container/list paths for RESTCONF path comparison
    restconf_addressable = []  # (depth, name, is_list, key_names)

    for line in lines:
        # Skip module/augment declaration lines
        if not re.search(r'\+--', line):
            continue

        # Determine depth by leading whitespace/tree chars
        # Each level is typically 3 chars of indent (|  or +-- etc.)
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        # Rough depth calculation
        depth = indent // 3

        max_depth = max(max_depth, depth)

        # Determine read-write vs read-only
        rw_match = re.search(r'\+--r([wo])\s+', line)
        if not rw_match:
            continue

        access = rw_match.group(1)  # 'w' or 'o'

        # Get the node part after +--rw or +--ro
        node_part = re.sub(r'.*\+--r[wo]\s+', '', line).strip()

        # Check if it's a list (has * [keys] or just *)
        is_list = False
        list_keys = None
        if '*' in node_part:
            is_list = True
            key_match = re.search(r'\[([^\]]+)\]', node_part)
            if key_match:
                list_keys = key_match.group(1).strip()
            node_part = re.sub(r'\*.*', '', node_part).strip()

        # Get node name
        node_name = node_part.split()[0].rstrip('?') if node_part.split() else ''
        if not node_name:
            continue

        # Determine if leaf vs container
        # Leaves have a type after the name: "name?   string" or "name   identityref"
        # Containers just have a name (possibly followed by nothing or by uses/augment info)
        parts = node_part.split()
        
        # After removing name, if there's a type keyword, it's a leaf
        has_type = False
        if len(parts) >= 2:
            remaining = parts[1].rstrip('?')
            # Types are things like: string, uint32, boolean, enumeration, identityref,
            # inet:ip-address, yang:date-and-time, oc-types:xxx, etc.
            # NOT types: (these indicate containers)
            if remaining and not remaining.startswith('+') and not remaining.startswith('|'):
                has_type = True

        if is_list:
            lists.append({'name': node_name, 'depth': depth, 'keys': list_keys, 'access': access})
            if depth <= 2:
                top_level_lists.append(node_name)
            restconf_addressable.append({
                'name': node_name, 'depth': depth, 'type': 'list',
                'keys': list_keys, 'access': access
            })
        elif has_type:
            if '*' in line and '[' not in line:
                leaf_lists.append({'name': node_name, 'depth': depth, 'access': access})
            else:
                leaves.append({'name': node_name, 'depth': depth, 'access': access})
        else:
            containers.append({'name': node_name, 'depth': depth, 'access': access})
            if depth <= 2:
                top_level_containers.append(node_name)
            restconf_addressable.append({
                'name': node_name, 'depth': depth, 'type': 'container',
                'access': access
            })

    return {
        'total_nodes': len(containers) + len(lists) + len(leaves) + len(leaf_lists),
        'containers': len(containers),
        'lists': len(lists),
        'leaves': len(leaves),
        'leaf_lists': len(leaf_lists),
        'restconf_addressable': len(restconf_addressable),
        'top_level_containers': top_level_containers,
        'top_level_lists': top_level_lists,
        'max_depth': max_depth,
        'container_names': [c['name'] for c in containers],
        'list_names': [l['name'] for l in lists],
    }


def parse_swagger_spec(json_path):
    """
    Parse a Swagger/OpenAPI JSON spec and extract path/schema info.
    
    Returns dict with:
      - path_count: number of RESTCONF paths
      - operation_count: total HTTP operations
      - paths: list of path strings
      - schema_count: number of schemas in components
      - schema_properties: total properties across all schemas
      - has_examples: whether any path has examples
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    except Exception as e:
        return None

    paths = spec.get('paths', {})
    path_list = list(paths.keys())
    
    op_count = 0
    has_examples = False
    methods_used = set()
    
    for path, methods in paths.items():
        for method in ['get', 'put', 'patch', 'delete', 'post']:
            if method in methods:
                op_count += 1
                methods_used.add(method)
                # Check for examples
                op = methods[method]
                if 'requestBody' in op:
                    rb = op['requestBody']
                    if 'content' in rb:
                        for ct in rb['content'].values():
                            if 'example' in ct or 'examples' in ct:
                                has_examples = True
                if 'responses' in op:
                    for resp in op['responses'].values():
                        if isinstance(resp, dict) and 'content' in resp:
                            for ct in resp['content'].values():
                                if 'example' in ct or 'examples' in ct:
                                    has_examples = True

    # Count schemas
    schemas = spec.get('components', {}).get('schemas', {})
    schema_count = len(schemas)
    total_props = 0
    for schema_name, schema_def in schemas.items():
        if isinstance(schema_def, dict):
            props = schema_def.get('properties', {})
            total_props += len(props)
            # Check nested items for array types
            if 'items' in schema_def:
                items = schema_def['items']
                if isinstance(items, dict) and 'properties' in items:
                    total_props += len(items['properties'])

    return {
        'path_count': len(path_list),
        'operation_count': op_count,
        'paths': path_list,
        'schema_count': schema_count,
        'schema_properties': total_props,
        'has_examples': has_examples,
        'methods': list(methods_used),
    }


def find_tree_for_spec(spec_name, category):
    """
    Find the corresponding YANG tree HTML for a given spec.
    
    Mapping rules:
    - oper/rpc/cfg/events specs: direct name match (Cisco-IOS-XE-xxx.html)
    - openconfig: openconfig-xxx.html
    - ietf: ietf-xxx.html or iana-xxx.html
    - mib: MIB-NAME.html (uppercase)
    - native: complex - these are categorical groupings
    """
    if category == "swagger-native-config-model":
        # Native specs are categorical (native-routing.json etc.)
        # They don't map 1:1 to a single tree - skip or handle specially
        return None

    # Try direct match
    tree_name = spec_name + ".html"
    tree_path = YANG_TREES_DIR / tree_name
    if tree_path.exists():
        return tree_path

    # Try without -oper, -cfg, -rpc suffixes for alternate naming
    # e.g., spec might be Cisco-IOS-XE-aaa-oper but tree is Cisco-IOS-XE-aaa-oper
    # Usually direct match works

    # For MIBs, try uppercase
    upper_name = spec_name.upper() + ".html"
    upper_path = YANG_TREES_DIR / upper_name
    if upper_path.exists():
        return upper_path

    return None


def compute_gap_score(tree_info, spec_info):
    """
    Compute a gap score indicating how under-modeled the spec is.
    
    Higher score = worse gap.
    
    Key metric: tree has N containers+lists (RESTCONF-addressable nodes)
    but spec only has M paths. Gap = (N - M) / N
    
    Also considers schema completeness vs leaf count.
    """
    if not tree_info or not spec_info:
        return None

    tree_addressable = tree_info['restconf_addressable']
    spec_paths = spec_info['path_count']

    if tree_addressable == 0:
        return {
            'score': 0,
            'tree_addressable': 0,
            'spec_paths': spec_paths,
            'missing_paths': 0,
            'coverage_pct': 100.0,
            'tree_leaves': tree_info['leaves'],
            'schema_props': spec_info['schema_properties'],
            'leaf_coverage_pct': 100.0,
        }

    missing = max(0, tree_addressable - spec_paths)
    coverage = min(100.0, (spec_paths / tree_addressable) * 100)

    # Leaf coverage: tree leaves vs schema properties
    tree_leaves = tree_info['leaves']
    schema_props = spec_info['schema_properties']
    leaf_coverage = min(100.0, (schema_props / tree_leaves * 100)) if tree_leaves > 0 else 100.0

    # Combined score (0-100, higher = worse)
    # Weight path coverage more heavily (70%) vs schema coverage (30%)
    path_gap = 100 - coverage
    leaf_gap = 100 - leaf_coverage
    score = (path_gap * 0.7) + (leaf_gap * 0.3)

    return {
        'score': round(score, 1),
        'tree_addressable': tree_addressable,
        'spec_paths': spec_paths,
        'missing_paths': missing,
        'coverage_pct': round(coverage, 1),
        'tree_leaves': tree_leaves,
        'schema_props': schema_props,
        'leaf_coverage_pct': round(leaf_coverage, 1),
    }


def main():
    print("=" * 70)
    print("  Swagger vs YANG Tree Completeness Audit")
    print("=" * 70)

    results = []
    no_tree = []
    errors = []
    
    # Process each swagger folder
    for folder, pattern in SWAGGER_FOLDERS.items():
        api_dir = ROOT / folder / "api"
        if not api_dir.exists():
            print(f"  SKIP: {folder} (no api/ directory)")
            continue

        spec_files = list(api_dir.glob(pattern))
        spec_files = [f for f in spec_files if f.name not in EXCLUDE_FILES]
        
        print(f"\n  Processing {folder}: {len(spec_files)} specs")

        for spec_file in sorted(spec_files):
            spec_name = spec_file.stem  # filename without .json

            # Parse swagger
            spec_info = parse_swagger_spec(spec_file)
            if not spec_info:
                errors.append({'name': spec_name, 'folder': folder, 'error': 'Failed to parse spec'})
                continue

            # Find corresponding tree
            tree_path = find_tree_for_spec(spec_name, folder)
            
            if not tree_path:
                no_tree.append({
                    'name': spec_name,
                    'folder': folder,
                    'spec_paths': spec_info['path_count'],
                    'spec_ops': spec_info['operation_count'],
                    'schema_props': spec_info['schema_properties'],
                })
                continue

            # Parse tree
            tree_info = parse_yang_tree(tree_path)
            if not tree_info:
                errors.append({'name': spec_name, 'folder': folder, 'error': 'Failed to parse tree'})
                continue

            # Compute gap
            gap = compute_gap_score(tree_info, spec_info)

            results.append({
                'name': spec_name,
                'folder': folder,
                'tree_file': tree_path.name,
                'spec_paths': spec_info['path_count'],
                'spec_ops': spec_info['operation_count'],
                'spec_schemas': spec_info['schema_count'],
                'spec_schema_props': spec_info['schema_properties'],
                'has_examples': spec_info['has_examples'],
                'tree_total_nodes': tree_info['total_nodes'],
                'tree_containers': tree_info['containers'],
                'tree_lists': tree_info['lists'],
                'tree_leaves': tree_info['leaves'],
                'tree_addressable': tree_info['restconf_addressable'],
                'tree_max_depth': tree_info['max_depth'],
                'gap_score': gap['score'] if gap else None,
                'path_coverage_pct': gap['coverage_pct'] if gap else None,
                'leaf_coverage_pct': gap['leaf_coverage_pct'] if gap else None,
                'missing_paths': gap['missing_paths'] if gap else None,
            })

    # Sort by gap score (worst first)
    results.sort(key=lambda x: -(x['gap_score'] or 0))

    # Save full results JSON
    output_json = ROOT / "scripts" / "audit_results.json"
    with open(output_json, 'w') as f:
        json.dump({
            'generated': '2026-02-10',
            'total_audited': len(results),
            'no_tree_count': len(no_tree),
            'error_count': len(errors),
            'results': results,
            'no_tree': no_tree,
            'errors': errors,
        }, f, indent=2)
    print(f"\n  Saved: {output_json}")

    # Generate markdown report
    generate_report(results, no_tree, errors)

    # Print summary
    print("\n" + "=" * 70)
    print("  AUDIT SUMMARY")
    print("=" * 70)
    print(f"  Total specs with trees: {len(results)}")
    print(f"  Specs without trees:    {len(no_tree)}")
    print(f"  Errors:                 {len(errors)}")
    
    # Severity buckets
    critical = [r for r in results if (r['gap_score'] or 0) >= 70]
    high = [r for r in results if 50 <= (r['gap_score'] or 0) < 70]
    medium = [r for r in results if 30 <= (r['gap_score'] or 0) < 50]
    low = [r for r in results if 10 <= (r['gap_score'] or 0) < 30]
    good = [r for r in results if (r['gap_score'] or 0) < 10]

    print(f"\n  🔴 CRITICAL (score >= 70): {len(critical)} specs")
    print(f"  🟠 HIGH     (score 50-69): {len(high)} specs")
    print(f"  🟡 MEDIUM   (score 30-49): {len(medium)} specs")
    print(f"  🔵 LOW      (score 10-29): {len(low)} specs")
    print(f"  🟢 GOOD     (score < 10):  {len(good)} specs")

    if critical:
        print(f"\n  Top 20 worst gaps:")
        for r in critical[:20]:
            print(f"    {r['name']}: score={r['gap_score']}, "
                  f"paths={r['spec_paths']}/{r['tree_addressable']}, "
                  f"leaves={r['spec_schema_props']}/{r['tree_leaves']}")


def generate_report(results, no_tree, errors):
    """Generate a detailed markdown report."""
    report = ROOT / "scripts" / "audit_report.md"

    with open(report, 'w', encoding='utf-8') as f:
        f.write("# 📊 Swagger vs YANG Tree Completeness Audit Report\n\n")
        f.write(f"**Generated:** February 10, 2026\n")
        f.write(f"**Total Specs Audited:** {len(results)}\n")
        f.write(f"**Specs Without Trees:** {len(no_tree)}\n\n")

        # Severity summary
        critical = [r for r in results if (r['gap_score'] or 0) >= 70]
        high = [r for r in results if 50 <= (r['gap_score'] or 0) < 70]
        medium = [r for r in results if 30 <= (r['gap_score'] or 0) < 50]
        low = [r for r in results if 10 <= (r['gap_score'] or 0) < 30]
        good = [r for r in results if (r['gap_score'] or 0) < 10]

        f.write("## Summary\n\n")
        f.write("| Severity | Count | Description |\n")
        f.write("|----------|-------|-------------|\n")
        f.write(f"| 🔴 CRITICAL | {len(critical)} | Gap score ≥ 70 — Swagger has very few paths vs YANG tree |\n")
        f.write(f"| 🟠 HIGH | {len(high)} | Gap score 50-69 — Significant modeling gaps |\n")
        f.write(f"| 🟡 MEDIUM | {len(medium)} | Gap score 30-49 — Moderate gaps, many containers missing |\n")
        f.write(f"| 🔵 LOW | {len(low)} | Gap score 10-29 — Minor gaps, mostly complete |\n")
        f.write(f"| 🟢 GOOD | {len(good)} | Gap score < 10 — Well modeled |\n\n")

        # Critical details
        if critical:
            f.write("## 🔴 CRITICAL — Severely Under-Modeled Specs\n\n")
            f.write("These specs have the largest gap between YANG tree nodes and Swagger paths.\n\n")
            f.write("| # | Module | Folder | Swagger Paths | Tree Containers+Lists | Path Coverage | Schema Props | Tree Leaves | Leaf Coverage | Gap Score |\n")
            f.write("|---|--------|--------|---------------|----------------------|---------------|-------------|-------------|---------------|-----------|\n")
            for i, r in enumerate(critical, 1):
                f.write(f"| {i} | {r['name']} | {r['folder']} | {r['spec_paths']} | {r['tree_addressable']} | {r['path_coverage_pct']}% | {r['spec_schema_props']} | {r['tree_leaves']} | {r['leaf_coverage_pct']}% | {r['gap_score']} |\n")
            f.write("\n")

        # High details
        if high:
            f.write("## 🟠 HIGH — Significant Gaps\n\n")
            f.write("| # | Module | Folder | Swagger Paths | Tree C+L | Path Coverage | Gap Score |\n")
            f.write("|---|--------|--------|---------------|----------|---------------|-----------|\n")
            for i, r in enumerate(high, 1):
                f.write(f"| {i} | {r['name']} | {r['folder']} | {r['spec_paths']} | {r['tree_addressable']} | {r['path_coverage_pct']}% | {r['gap_score']} |\n")
            f.write("\n")

        # Medium
        if medium:
            f.write("## 🟡 MEDIUM — Moderate Gaps\n\n")
            f.write("| # | Module | Folder | Swagger Paths | Tree C+L | Path Coverage | Gap Score |\n")
            f.write("|---|--------|--------|---------------|----------|---------------|-----------|\n")
            for i, r in enumerate(medium, 1):
                f.write(f"| {i} | {r['name']} | {r['folder']} | {r['spec_paths']} | {r['tree_addressable']} | {r['path_coverage_pct']}% | {r['gap_score']} |\n")
            f.write("\n")

        # Low (just count)
        if low:
            f.write(f"## 🔵 LOW — {len(low)} specs with minor gaps (score 10-29)\n\n")
            f.write("<details><summary>Click to expand</summary>\n\n")
            f.write("| Module | Paths | Tree C+L | Coverage | Score |\n")
            f.write("|--------|-------|----------|----------|-------|\n")
            for r in low:
                f.write(f"| {r['name']} | {r['spec_paths']} | {r['tree_addressable']} | {r['path_coverage_pct']}% | {r['gap_score']} |\n")
            f.write("\n</details>\n\n")

        # Good
        f.write(f"## 🟢 GOOD — {len(good)} specs well-modeled (score < 10)\n\n")
        f.write(f"These {len(good)} specs have adequate path and schema coverage.\n\n")

        # No-tree specs
        if no_tree:
            f.write(f"## ℹ️ Specs Without YANG Trees ({len(no_tree)})\n\n")
            f.write("These specs have no corresponding YANG tree file and could not be audited.\n\n")
            f.write("| Module | Folder | Paths | Ops |\n")
            f.write("|--------|--------|-------|-----|\n")
            for r in no_tree:
                f.write(f"| {r['name']} | {r['folder']} | {r['spec_paths']} | {r['spec_ops']} |\n")
            f.write("\n")

    print(f"  Saved: {report}")


if __name__ == "__main__":
    main()
