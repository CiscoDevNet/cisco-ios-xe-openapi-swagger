#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specs from resolved YANG tree HTML files for operational modules.
Parses each Cisco-IOS-XE-*-oper.html tree to produce deep GET-only specs.

Unlike the native generator (one monolithic tree), oper has ~200 separate tree files,
one per YANG module. Each tree file produces one spec.
"""

import json
import re
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Tree parser (adapted from generate_native_from_tree.py)
# ---------------------------------------------------------------------------

class TreeNode:
    __slots__ = ('name', 'raw_name', 'rw', 'node_type', 'yang_type',
                 'is_key', 'children', 'depth')

    def __init__(self, name, rw='ro', node_type='container', yang_type='',
                 is_key=False, depth=0):
        self.name = name
        self.raw_name = name
        self.rw = rw
        self.node_type = node_type
        self.yang_type = yang_type
        self.is_key = is_key
        self.children: List['TreeNode'] = []
        self.depth = depth

    def find_child(self, name):
        for c in self.children:
            if c.name == name:
                return c
        return None

    def descendant_count(self):
        count = 0
        for c in self.children:
            count += 1 + c.descendant_count()
        return count


def parse_yang_tree_html(html_path: str) -> List[Tuple[str, TreeNode]]:
    """Parse a YANG tree HTML file and return list of (module_prefix, root_node) tuples.
    Oper trees may have multiple root containers (unlike native which has one 'native' root).
    Returns roots with their module prefix for RESTCONF path construction.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find tree <pre> blocks
    pre_matches = re.findall(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
    if not pre_matches:
        return []

    # The tree content is usually in the last (or second) <pre> block
    # Try to find one with actual tree markers
    tree_text = None
    for pre in reversed(pre_matches):
        cleaned = re.sub(r'<[^>]+>', '', pre)
        if re.search(r'[+o]-+(rw|ro|x)', cleaned):
            tree_text = cleaned
            break

    if not tree_text:
        return []

    tree_text = tree_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    lines = tree_text.split('\n')

    # Extract module name from the "module:" line
    module_name = None
    for line in lines:
        m = re.match(r'module:\s+(\S+)', line.strip())
        if m:
            module_name = m.group(1)
            break

    if not module_name:
        # Try to infer from filename
        fname = os.path.basename(html_path).replace('.html', '')
        module_name = fname

    # Find all root-level container/list nodes
    # These are nodes at the shallowest indentation level with +--rw or +--ro markers
    roots = []
    root_indices = []

    # First pass: find all tree node lines and their column positions
    node_lines = []
    for i, line in enumerate(lines):
        marker = re.search(r'[+o]-+(rw|ro|x)\s+(\S+)(.*)', line)
        if marker:
            node_lines.append((i, marker.start(), marker))

    if not node_lines:
        return []

    # The root level nodes are those at the minimum column position
    min_col = min(col for _, col, _ in node_lines)
    root_line_indices = [(i, col, m) for i, col, m in node_lines if col == min_col]

    for idx, (line_idx, col, marker) in enumerate(root_line_indices):
        rw = marker.group(1)
        raw_name = marker.group(2)
        rest = marker.group(3).strip()

        name = raw_name.rstrip('?').rstrip('!').rstrip('*')
        has_key = bool(re.search(r'\[(\S+)\]', rest))
        is_list = raw_name.rstrip('?').rstrip('!').endswith('*') and has_key

        if is_list:
            node_type = 'list'
        elif rest and not rest.startswith('[') and not rest.startswith('{'):
            yang_type = rest.split()[0] if rest.split() else 'string'
            node_type = 'leaf'
        else:
            node_type = 'container'

        root = TreeNode(name, rw, node_type, depth=0)
        root.raw_name = raw_name

        # Determine end of this root's children (next root line or end of file)
        if idx + 1 < len(root_line_indices):
            end_line = root_line_indices[idx + 1][0]
        else:
            end_line = len(lines)

        # Parse children
        node_stack: List[Tuple[int, TreeNode]] = [(col, root)]

        for i in range(line_idx + 1, end_line):
            line = lines[i]
            if not line.strip():
                continue

            case_match = re.search(r'[+o]--:\((\S+)\)', line)
            if case_match:
                c = case_match.start()
                cname = case_match.group(1)
                node = TreeNode(cname, 'ro', 'case', depth=0)
                while len(node_stack) > 1 and node_stack[-1][0] >= c:
                    node_stack.pop()
                parent_col, parent_node = node_stack[-1]
                parent_node.children.append(node)
                node.depth = parent_node.depth + 1
                node_stack.append((c, node))
                continue

            m = re.search(r'[+o]-+(rw|ro|x)\s+(\S+)(.*)', line)
            if not m:
                continue

            c = m.start()
            rw_child = m.group(1)
            raw = m.group(2)
            rest_child = m.group(3).strip()

            child_name = raw.rstrip('?').rstrip('!').rstrip('*')
            child_has_key = bool(re.search(r'\[(\S+)\]', rest_child))
            child_is_list = raw.rstrip('?').rstrip('!').endswith('*') and child_has_key

            if child_is_list:
                child_type = 'list'
                child_yang_type = ''
            elif raw.startswith('(') and (raw.endswith(')') or raw.endswith(')?')):
                child_type = 'choice'
                child_name = raw.strip('()?')
                child_yang_type = ''
            elif rest_child and not rest_child.startswith('[') and not rest_child.startswith('{'):
                child_yang_type = rest_child.split()[0] if rest_child.split() else 'string'
                if raw.rstrip('?').rstrip('!').endswith('*') and not child_has_key:
                    child_type = 'leaf-list'
                else:
                    child_type = 'leaf'
            else:
                child_type = 'container'
                child_yang_type = ''

            node = TreeNode(child_name, rw_child, child_type, child_yang_type, depth=0)
            node.raw_name = raw

            while len(node_stack) > 1 and node_stack[-1][0] >= c:
                node_stack.pop()

            parent_col, parent_node = node_stack[-1]
            parent_node.children.append(node)
            node.depth = parent_node.depth + 1
            node_stack.append((c, node))

        roots.append((module_name, root))

    return roots


# ---------------------------------------------------------------------------
# Example generator (operational-specific heuristics)
# ---------------------------------------------------------------------------

OPER_EXAMPLE_VALUES = {
    'name': 'GigabitEthernet1/0/1',
    'address': '10.10.10.1',
    'mask': '255.255.255.0',
    'mtu': 1500,
    'speed': '1000Mbps',
    'state': 'up',
    'admin-state': 'if-state-up',
    'oper-status': 'up',
    'interface-type': 'iana-iftype-ethernet-csmacd',
    'description': 'UPLINK_TO_CORE',
    'in-octets': 1234567890,
    'out-octets': 987654321,
    'in-errors': 0,
    'out-errors': 0,
    'in-discards': 0,
    'out-discards': 0,
    'uptime': 86400,
    'cpu-utilization': 12,
    'memory-usage': 45,
    'free-memory': 2048000,
    'used-memory': 1024000,
    'total-memory': 3072000,
    'hostname': 'DC1-CORE-SW01',
    'serial-number': 'FCW2345L0AB',
    'pid': 'C9300-48T',
    'version': '17.18.1',
    'uptime-seconds': 86400,
    'neighbors': 4,
    'routes': 150,
    'prefixes': 200,
    'sessions': 3,
    'count': 42,
    'index': 1,
    'id': 1,
    'vrf-name': 'default',
    'vlan-id': 100,
    'mac-address': '00:1A:2B:3C:4D:5E',
    'ip-address': '10.10.10.1',
}


def example_for_type(yang_type, name=''):
    name_lower = name.lower().replace('-', '').replace('_', '')
    for key, val in OPER_EXAMPLE_VALUES.items():
        if key.replace('-', '') in name_lower:
            return val

    try:
        from yang_value_index import lookup_example
        v = lookup_example(name)
        if v is not None:
            return v
    except Exception:
        pass

    base = yang_type.split(':')[-1] if ':' in yang_type else yang_type
    type_map = {
        'string': 'example', 'uint8': 1, 'uint16': 1, 'uint32': 1, 'uint64': 1,
        'int8': 1, 'int16': 1, 'int32': 1, 'int64': 1,
        'boolean': True, 'empty': None, 'enumeration': 'default',
        'union': 'auto', 'decimal64': 1.0, 'binary': 'QmFzZTY0', 'bits': '',
    }
    return type_map.get(base, 'example')


def generate_example(node, max_depth=3, depth=0):
    if depth > max_depth:
        return {}
    if node.node_type == 'leaf':
        return example_for_type(node.yang_type, node.name)
    if node.node_type == 'leaf-list':
        return [example_for_type(node.yang_type, node.name)]
    if node.node_type in ('choice', 'case'):
        if node.children:
            return generate_example(node.children[0], max_depth, depth)
        return {}
    obj = {}
    for child in node.children:
        if child.node_type in ('choice', 'case'):
            if child.children:
                first = child.children[0] if child.node_type == 'choice' else child
                for gc in first.children:
                    obj[gc.name] = generate_example(gc, max_depth, depth + 1)
        elif child.node_type == 'leaf':
            obj[child.name] = example_for_type(child.yang_type, child.name)
        elif child.node_type == 'leaf-list':
            obj[child.name] = [example_for_type(child.yang_type, child.name)]
        else:
            child_ex = generate_example(child, max_depth, depth + 1)
            if child.node_type == 'list':
                obj[child.name] = [child_ex] if isinstance(child_ex, dict) else child_ex
            else:
                obj[child.name] = child_ex
    return obj


# ---------------------------------------------------------------------------
# Schema builder
# ---------------------------------------------------------------------------

def yang_type_to_schema(yang_type, name=''):
    base = yang_type.split(':')[-1] if ':' in yang_type else yang_type
    mapping = {
        'string': {'type': 'string'},
        'uint8': {'type': 'integer', 'minimum': 0, 'maximum': 255},
        'uint16': {'type': 'integer', 'minimum': 0, 'maximum': 65535},
        'uint32': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
        'uint64': {'type': 'integer', 'minimum': 0},
        'int8': {'type': 'integer', 'minimum': -128, 'maximum': 127},
        'int16': {'type': 'integer', 'minimum': -32768, 'maximum': 32767},
        'int32': {'type': 'integer'}, 'int64': {'type': 'integer'},
        'boolean': {'type': 'boolean'},
        'empty': {'type': 'boolean', 'description': 'Presence flag'},
        'enumeration': {'type': 'string'}, 'union': {'type': 'string'},
        'decimal64': {'type': 'number'},
        'binary': {'type': 'string', 'format': 'byte'}, 'bits': {'type': 'string'},
    }
    return mapping.get(base, {'type': 'string'}).copy()


def build_schema(node, max_depth=6, depth=0):
    if depth > max_depth:
        return {'type': 'object'}
    if node.node_type == 'leaf':
        return yang_type_to_schema(node.yang_type, node.name)
    if node.node_type == 'leaf-list':
        return {'type': 'array', 'items': yang_type_to_schema(node.yang_type, node.name)}
    properties = {}
    required = []
    for child in node.children:
        if child.node_type in ('choice', 'case'):
            target = child.children[0] if child.node_type == 'choice' and child.children else child
            for gc in (target.children if target else []):
                properties[gc.name] = build_schema(gc, max_depth, depth + 1)
        else:
            properties[child.name] = build_schema(child, max_depth, depth + 1)
            if child.is_key:
                required.append(child.name)
    schema = {'type': 'object'}
    if properties:
        schema['properties'] = properties
    if required:
        schema['required'] = required
    if node.node_type == 'list':
        return {'type': 'array', 'items': schema}
    return schema


# ---------------------------------------------------------------------------
# Path collection
# ---------------------------------------------------------------------------

def collect_deep_paths(node, base_path, max_depth=8, depth=0):
    paths = [(base_path, node)]
    if depth >= max_depth:
        return paths
    for child in node.children:
        if child.node_type in ('choice', 'case'):
            target = child
            if child.node_type == 'choice' and child.children:
                target = child.children[0]
            for gc in target.children:
                cp = f"{base_path}/{gc.name}"
                if gc.node_type == 'list':
                    paths.append((cp, gc))
                    key_child = gc.find_child('name') or gc.find_child('id')
                    if key_child:
                        paths.append((f"{cp}={{{key_child.name}}}", gc))
                    paths.extend(collect_deep_paths(gc, cp, max_depth, depth + 1))
                elif gc.node_type == 'container':
                    paths.extend(collect_deep_paths(gc, cp, max_depth, depth + 1))
                else:
                    paths.append((cp, gc))
        elif child.node_type == 'list':
            cp = f"{base_path}/{child.name}"
            paths.append((cp, child))
            key_child = child.find_child('name') or child.find_child('id')
            if key_child:
                paths.append((f"{cp}={{{key_child.name}}}", child))
            paths.extend(collect_deep_paths(child, cp, max_depth, depth + 1))
        elif child.node_type == 'container':
            cp = f"{base_path}/{child.name}"
            paths.extend(collect_deep_paths(child, cp, max_depth, depth + 1))
        elif child.node_type in ('leaf', 'leaf-list'):
            paths.append((f"{base_path}/{child.name}", child))
    return paths


# ---------------------------------------------------------------------------
# OpenAPI spec builder (GET-only for operational data)
# ---------------------------------------------------------------------------

COMMON_COMPONENTS = {
    'securitySchemes': {
        'basicAuth': {'type': 'http', 'scheme': 'basic',
                      'description': 'RESTCONF basic authentication (RFC 8040)'}
    },
    'parameters': {
        'accept': {
            'name': 'Accept', 'in': 'header', 'required': False,
            'schema': {'type': 'string', 'default': 'application/yang-data+json'}
        },
        'depth': {
            'name': 'depth', 'in': 'query', 'required': False,
            'description': 'Limit response depth (RFC 8040)',
            'schema': {'type': 'string', 'default': 'unbounded'}
        }
    }
}


def make_get_operation(restconf_path, node, tag, module_prefix):
    schema = build_schema(node, max_depth=4)
    example = generate_example(node, max_depth=3)
    wrapper_key = f"{module_prefix}:{node.name}"
    wrapped = {wrapper_key: [example] if node.node_type == 'list' else example}
    schema = {'type': 'object', 'properties': {wrapper_key: schema}}
    op_id = restconf_path.replace('/data/', '').replace('/', '-').replace('=', '-').replace('{', '').replace('}', '')

    return {
        'get': {
            'summary': f"Get {node.name}",
            'operationId': f"get-{op_id}",
            'tags': [tag],
            'parameters': [
                {'$ref': '#/components/parameters/accept'},
                {'$ref': '#/components/parameters/depth'}
            ],
            'responses': {
                '200': {
                    'description': 'Successful response',
                    'content': {
                        'application/yang-data+json': {
                            'schema': schema,
                            'example': wrapped
                        }
                    }
                },
                '401': {'description': 'Unauthorized'},
                '404': {'description': 'Resource not found'}
            }
        }
    }


def create_spec(title, description, tag, paths, module_name, version='17.18.1'):
    return {
        'openapi': '3.0.0',
        'info': {
            'title': title,
            'description': description,
            'version': version,
            'contact': {'name': 'Cisco IOS-XE RESTCONF API', 'url': 'https://developer.cisco.com/iosxe/'},
            'x-yang-module': module_name,
            'x-model-type': 'operational'
        },
        'servers': [{
            'url': 'https://{device}:{port}/restconf',
            'description': 'IOS-XE Device RESTCONF API',
            'variables': {
                'device': {'default': 'devnetsandboxiosxec9k.cisco.com'},
                'port': {'default': '443'}
            }
        }],
        'paths': paths,
        'components': COMMON_COMPONENTS,
        'security': [{'basicAuth': []}]
    }


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def process_tree_file(html_path, output_dir, max_depth=8):
    """Process a single oper tree HTML file into one or more specs.
    Returns list of (filename, path_count) tuples."""
    results = []
    roots = parse_yang_tree_html(html_path)
    if not roots:
        return results

    # Group all roots by module name to avoid duplicates
    from collections import defaultdict
    module_roots = defaultdict(list)
    for module_name, root in roots:
        module_roots[module_name].append(root)

    for module_name, root_list in module_roots.items():
        # Merge paths from all roots with the same module name
        all_paths = {}
        total_descendants = 0
        root_names = []
        for root in root_list:
            base_path = f"/data/{module_name}:{root.name}"
            tag = root.name
            root_names.append(root.name)
            total_descendants += root.descendant_count()

            deep = collect_deep_paths(root, base_path, max_depth=max_depth)
            for rpath, rnode in deep:
                if rpath not in all_paths:
                    all_paths[rpath] = make_get_operation(rpath, rnode, tag, module_name)

        if not all_paths:
            continue

        title = f"Cisco IOS-XE Operational - {module_name}"
        desc = (f"Operational data from `{module_name}` module.\n\n"
                f"**Root containers:** {len(root_list)} ({', '.join(root_names[:5])}{'...' if len(root_names) > 5 else ''})\n"
                f"**Paths:** {len(all_paths)} | **Descendants:** {total_descendants}\n\n"
                f"All endpoints are read-only (GET).")

        # Use first root name as the primary tag
        primary_tag = root_list[0].name
        spec = create_spec(title, desc, primary_tag, all_paths, module_name)

        # Check size and limit depth if too large
        spec_json = json.dumps(spec, indent=2)
        size_kb = len(spec_json.encode('utf-8')) / 1024
        if size_kb > 2048 and max_depth > 3:
            return process_tree_file(html_path, output_dir, max_depth=max_depth - 1)

        fname = module_name
        out_path = output_dir / f"{fname}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(spec_json)

        results.append((fname, len(all_paths)))

    return results


def _resolve_paths(version: str):
    project_root = Path(__file__).resolve().parent.parent
    release_tree = project_root / 'releases' / version / 'yang-trees'
    if release_tree.is_dir():
        tree_dir = release_tree
        output_dir = (project_root / 'releases' / version
                      / 'swagger-oper-model' / 'api')
    elif version == '17.18.1':
        tree_dir = project_root / 'yang-trees'
        output_dir = project_root / 'swagger-oper-model' / 'api'
    else:
        tree_dir = project_root / 'releases' / version / 'yang-trees'
        output_dir = (project_root / 'releases' / version
                      / 'swagger-oper-model' / 'api')
    return tree_dir, output_dir


def generate_all(version: str = '17.18.1'):
    tree_dir, output_dir = _resolve_paths(version)

    # Clean previous output
    if output_dir.exists():
        for f in output_dir.glob('*.json'):
            f.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"Operational YANG Tree -> OpenAPI 3.0 Generator (v2)  [{version}]")
    print(f"  trees:  {tree_dir}")
    print(f"  output: {output_dir}")
    print(f"{'='*70}\n")

    # Find all oper tree files
    tree_files = sorted(tree_dir.glob('Cisco-IOS-XE-*-oper*.html'))
    print(f"Found {len(tree_files)} operational tree files\n")

    all_generated = []
    total_paths = 0
    errors = 0

    for tf in tree_files:
        try:
            results = process_tree_file(tf, output_dir)
            for fname, path_count in results:
                all_generated.append(fname)
                total_paths += path_count
                print(f"  {fname}: {path_count} paths")
        except Exception as e:
            errors += 1
            print(f"  ERROR {tf.name}: {e}")

    # Write manifest
    manifest = {
        'total_modules': len(all_generated),
        'total_paths': total_paths,
        'total_operations': total_paths,  # GET only
        'modules': sorted(all_generated),
        'generator': 'generate_oper_from_tree.py',
        'source': 'yang-trees/Cisco-IOS-XE-*-oper.html',
        'version': version,
    }
    with open(output_dir / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Done: {len(all_generated)} specs, {total_paths} paths, {errors} errors")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', default='17.18.1')
    args = ap.parse_args()
    generate_all(args.version)
