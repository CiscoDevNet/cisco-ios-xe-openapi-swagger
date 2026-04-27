#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specs from resolved YANG tree HTML files for RPC modules.
RPC operations use POST on /operations/{module}:{rpc-name} with input/output schemas.
Parses each Cisco-IOS-XE-*-rpc.html tree to produce deep specs.
"""

import json
import re
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict


# ---------------------------------------------------------------------------
# Tree parser
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
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pre_matches = re.findall(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
    if not pre_matches:
        return []

    tree_text = None
    for pre in reversed(pre_matches):
        cleaned = re.sub(r'<[^>]+>', '', pre)
        if re.search(r'[+o]-+(rw|ro|x|w|n)', cleaned):
            tree_text = cleaned
            break

    if not tree_text:
        return []

    tree_text = tree_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    lines = tree_text.split('\n')

    module_name = None
    for line in lines:
        m = re.match(r'module:\s+(\S+)', line.strip())
        if m:
            module_name = m.group(1)
            break

    if not module_name:
        fname = os.path.basename(html_path).replace('.html', '')
        module_name = fname

    # RPC trees have "rpcs:" section header
    # Find all RPC-level nodes (marked with +---x)
    node_lines = []
    in_rpcs = False
    for i, line in enumerate(lines):
        if line.strip() == 'rpcs:':
            in_rpcs = True
            continue
        if in_rpcs:
            marker = re.search(r'[+o]-+(rw|ro|x|w)\s+(\S+)(.*)', line)
            if marker:
                node_lines.append((i, marker.start(), marker))

    # If no rpcs: section found, try parsing all x-marked nodes
    if not node_lines:
        for i, line in enumerate(lines):
            marker = re.search(r'[+o]-+(x)\s+(\S+)(.*)', line)
            if marker:
                node_lines.append((i, marker.start(), marker))

    if not node_lines:
        # Also try rw/ro nodes (some RPC trees don't use x marker)
        for i, line in enumerate(lines):
            marker = re.search(r'[+o]-+(rw|ro|x)\s+(\S+)(.*)', line)
            if marker:
                node_lines.append((i, marker.start(), marker))

    if not node_lines:
        return []

    # Find the top-level RPC nodes (those with x marker at minimum column)
    x_nodes = [(i, col, m) for i, col, m in node_lines if m.group(1) == 'x']
    if x_nodes:
        min_col = min(col for _, col, _ in x_nodes)
        rpc_root_indices = [(i, col, m) for i, col, m in x_nodes if col == min_col]
    else:
        min_col = min(col for _, col, _ in node_lines)
        rpc_root_indices = [(i, col, m) for i, col, m in node_lines if col == min_col]

    roots = []

    for idx, (line_idx, col, marker) in enumerate(rpc_root_indices):
        raw_name = marker.group(2)
        rest = marker.group(3).strip()
        name = raw_name.rstrip('?').rstrip('!').rstrip('*')

        rpc_root = TreeNode(name, 'x', 'rpc', depth=0)
        rpc_root.raw_name = raw_name

        if idx + 1 < len(rpc_root_indices):
            end_line = rpc_root_indices[idx + 1][0]
        else:
            end_line = len(lines)

        node_stack: List[Tuple[int, TreeNode]] = [(col, rpc_root)]

        for i in range(line_idx + 1, end_line):
            line = lines[i]
            if not line.strip():
                continue

            m = re.search(r'[+o]-+(rw|ro|x|w)\s+(\S+)(.*)', line)
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
            elif child_name in ('input', 'output'):
                child_type = 'container'
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

        roots.append((module_name, rpc_root))

    return roots


# ---------------------------------------------------------------------------
# Example + Schema
# ---------------------------------------------------------------------------

def example_for_type(yang_type, name=''):
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
# RPC operation builder (POST only)
# ---------------------------------------------------------------------------

COMMON_COMPONENTS = {
    'securitySchemes': {
        'basicAuth': {'type': 'http', 'scheme': 'basic',
                      'description': 'RESTCONF basic authentication (RFC 8040)'}
    },
    'parameters': {
        'content-type': {
            'name': 'Content-Type', 'in': 'header', 'required': False,
            'schema': {'type': 'string', 'default': 'application/yang-data+json'}
        }
    }
}


def make_rpc_operation(restconf_path, rpc_node, tag, module_prefix):
    input_node = rpc_node.find_child('input')
    output_node = rpc_node.find_child('output')

    input_schema = build_schema(input_node, max_depth=4) if input_node else {'type': 'object'}
    input_example = generate_example(input_node, max_depth=3) if input_node else {}
    output_schema = build_schema(output_node, max_depth=4) if output_node else {'type': 'object'}
    output_example = generate_example(output_node, max_depth=3) if output_node else {}

    op_id = restconf_path.replace('/operations/', '').replace('/', '-').replace(':', '-')

    op = {
        'summary': f"Execute {rpc_node.name}",
        'operationId': f"post-{op_id}",
        'tags': [tag],
        'responses': {
            '204': {'description': 'Success (no output)'},
            '401': {'description': 'Unauthorized'},
            '404': {'description': 'Not found'},
        }
    }

    if output_node and output_node.children:
        op['responses']['200'] = {
            'description': 'Successful response',
            'content': {
                'application/yang-data+json': {
                    'schema': output_schema,
                    'example': {f"{module_prefix}:output": output_example}
                }
            }
        }

    if input_node and input_node.children:
        op['requestBody'] = {
            'required': True,
            'content': {
                'application/yang-data+json': {
                    'schema': input_schema,
                    'example': {f"{module_prefix}:input": input_example}
                }
            }
        }

    return {'post': op}


def create_spec(title, description, tag, paths, module_name, version='17.18.1'):
    return {
        'openapi': '3.0.0',
        'info': {
            'title': title, 'description': description, 'version': version,
            'contact': {'name': 'Cisco IOS-XE RESTCONF API', 'url': 'https://developer.cisco.com/iosxe/'},
            'x-yang-module': module_name, 'x-model-type': 'rpc'
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

def process_tree_file(html_path, output_dir, max_depth=5):
    results = []
    roots = parse_yang_tree_html(html_path)
    if not roots:
        return results

    module_roots = defaultdict(list)
    for module_name, root in roots:
        module_roots[module_name].append(root)

    for module_name, root_list in module_roots.items():
        all_paths = {}
        rpc_names = []
        for root in root_list:
            rpc_path = f"/operations/{module_name}:{root.name}"
            rpc_names.append(root.name)
            if rpc_path not in all_paths:
                all_paths[rpc_path] = make_rpc_operation(rpc_path, root, module_name, module_name)

        if not all_paths:
            continue

        title = f"Cisco IOS-XE RPC - {module_name}"
        desc = (f"RPC operations from `{module_name}` module.\n\n"
                f"**RPCs:** {len(rpc_names)} ({', '.join(rpc_names[:5])}{'...' if len(rpc_names) > 5 else ''})\n\n"
                f"All endpoints use POST on `/operations/`.")

        spec = create_spec(title, desc, module_name, all_paths, module_name)

        spec_json = json.dumps(spec, indent=2)
        fname = module_name
        out_path = output_dir / f"{fname}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(spec_json)

        results.append((fname, len(all_paths)))

    return results


def generate_all():
    script_dir = Path(__file__).parent
    tree_dir = script_dir.parent / 'yang-trees'
    output_dir = script_dir.parent / 'swagger-rpc-model' / 'api'

    if output_dir.exists():
        for f in output_dir.glob('*.json'):
            f.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("RPC YANG Tree -> OpenAPI 3.0 Generator (v2)")
    print(f"{'='*70}\n")

    tree_files = sorted(tree_dir.glob('Cisco-IOS-XE-*-rpc.html'))
    # Also include Cisco-IOS-XE-rpc.html (no dash before "rpc") and
    # non-Cisco modules that contain RPC operations
    extra_rpc_trees = [
        'Cisco-IOS-XE-rpc.html',
        'cisco-bridge-domain.html',
        'cisco-ia.html',
        'cisco-smart-license.html',
        'ietf-event-notifications.html',
        'ietf-netconf-monitoring.html',
        'ietf-netconf.html',
        'ietf-routing.html',
        'tailf-netconf-extensions.html',
        'tailf-netconf-query.html',
        'tailf-netconf-transactions.html',
    ]
    existing_names = {f.name for f in tree_files}
    for extra in extra_rpc_trees:
        p = tree_dir / extra
        if p.exists() and extra not in existing_names:
            tree_files.append(p)
    tree_files = sorted(tree_files, key=lambda f: f.name)
    print(f"Found {len(tree_files)} RPC tree files\n")

    all_generated = []
    total_paths = 0
    errors = 0

    for tf in tree_files:
        try:
            results = process_tree_file(tf, output_dir)
            for fname, path_count in results:
                all_generated.append(fname)
                total_paths += path_count
                print(f"  {fname}: {path_count} RPCs")
        except Exception as e:
            errors += 1
            print(f"  ERROR {tf.name}: {e}")

    manifest = {
        'total_modules': len(all_generated),
        'total_paths': total_paths,
        'total_operations': total_paths,  # 1 POST per RPC
        'modules': sorted(all_generated),
        'generator': 'generate_rpc_from_tree.py',
        'source': 'yang-trees/Cisco-IOS-XE-*-rpc.html',
        'version': '17.18.1'
    }
    with open(output_dir / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Done: {len(all_generated)} specs, {total_paths} RPCs, {errors} errors")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    generate_all()
