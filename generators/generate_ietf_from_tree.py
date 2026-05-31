#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specs from resolved YANG tree HTML files for IETF modules.
IETF modules have mixed rw/ro nodes — GET for read-only, full CRUD for read-write.
Parses each ietf-*.html tree to produce deep specs.
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
        if re.search(r'[+o]-+(rw|ro|x)', cleaned):
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

    # Also detect rpcs: and notifications: sections
    section = 'data'
    section_lines = {}  # track which lines belong to which section
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == 'rpcs:':
            section = 'rpcs'
        elif stripped == 'notifications:':
            section = 'notifications'
        section_lines[i] = section

    node_lines = []
    for i, line in enumerate(lines):
        marker = re.search(r'[+o]-+(rw|ro|x|n)\s+(\S+)(.*)', line)
        if marker:
            node_lines.append((i, marker.start(), marker, section_lines.get(i, 'data')))

    if not node_lines:
        return []

    # Only process data section nodes for RESTCONF /data/ paths
    data_nodes = [(i, col, m) for i, col, m, sec in node_lines if sec == 'data']
    rpc_nodes = [(i, col, m) for i, col, m, sec in node_lines if sec == 'rpcs']
    notif_nodes = [(i, col, m) for i, col, m, sec in node_lines if sec == 'notifications']

    roots = []

    # Process data nodes
    if data_nodes:
        min_col = min(col for _, col, _ in data_nodes)
        root_line_indices = [(i, col, m) for i, col, m in data_nodes if col == min_col]

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
                node_type = 'leaf'
            else:
                node_type = 'container'

            root = TreeNode(name, rw, node_type, depth=0)
            root.raw_name = raw_name

            if idx + 1 < len(root_line_indices):
                end_line = root_line_indices[idx + 1][0]
            else:
                # End at rpcs/notifications section or end of data nodes
                end_line = len(lines)
                for li in range(line_idx + 1, len(lines)):
                    if lines[li].strip() in ('rpcs:', 'notifications:'):
                        end_line = li
                        break

            node_stack: List[Tuple[int, TreeNode]] = [(col, root)]

            for i in range(line_idx + 1, end_line):
                line = lines[i]
                if not line.strip():
                    continue
                if line.strip() in ('rpcs:', 'notifications:'):
                    break

                case_match = re.search(r'[+o]--:\((\S+)\)', line)
                if case_match:
                    c = case_match.start()
                    cname = case_match.group(1)
                    node = TreeNode(cname, 'rw', 'case', depth=0)
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

    # Process RPC nodes as action endpoints
    if rpc_nodes:
        min_col = min(col for _, col, _ in rpc_nodes)
        rpc_root_indices = [(i, col, m) for i, col, m in rpc_nodes if col == min_col]

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
                for li in range(line_idx + 1, len(lines)):
                    if lines[li].strip() == 'notifications:':
                        end_line = li
                        break

            node_stack = [(col, rpc_root)]
            for i in range(line_idx + 1, end_line):
                line = lines[i]
                if not line.strip():
                    continue
                if line.strip() == 'notifications:':
                    break

                m = re.search(r'[+o]-+(rw|ro|x|w)\s+(\S+)(.*)', line)
                if not m:
                    continue

                c = m.start()
                rw_child = m.group(1)
                raw = m.group(2)
                rest_child = m.group(3).strip()
                child_name = raw.rstrip('?').rstrip('!').rstrip('*')

                if rest_child and not rest_child.startswith('[') and not rest_child.startswith('{'):
                    child_yang_type = rest_child.split()[0] if rest_child.split() else 'string'
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
# Path collection & operations (CRUD for rw, GET for ro)
# ---------------------------------------------------------------------------

def collect_deep_paths(node, base_path, max_depth=5, depth=0):
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


def make_path_operations(restconf_path, node, tag, module_prefix):
    schema = build_schema(node, max_depth=4)
    example = generate_example(node, max_depth=3)
    wrapper_key = f"{module_prefix}:{node.name}"
    wrapped = {wrapper_key: [example] if node.node_type == 'list' else example}
    schema = {'type': 'object', 'properties': {wrapper_key: schema}}
    op_id = restconf_path.replace('/data/', '').replace('/operations/', '').replace('/', '-').replace('=', '-').replace('{', '').replace('}', '')

    ops = {}

    # RPC nodes get POST on /operations/
    if node.node_type == 'rpc':
        input_node = node.find_child('input')
        output_node = node.find_child('output')
        input_schema = build_schema(input_node, max_depth=4) if input_node else {'type': 'object'}
        input_example = generate_example(input_node, max_depth=3) if input_node else {}
        output_schema = build_schema(output_node, max_depth=4) if output_node else {'type': 'object'}
        output_example = generate_example(output_node, max_depth=3) if output_node else {}

        op = {
            'summary': f"Execute {node.name}",
            'operationId': f"post-{op_id}",
            'tags': [tag],
            'responses': {
                '200': {'description': 'Successful response',
                        'content': {'application/yang-data+json': {'schema': output_schema, 'example': output_example}}},
                '204': {'description': 'No content'},
                '401': {'description': 'Unauthorized'},
            }
        }
        if input_node and input_node.children:
            op['requestBody'] = {
                'required': True,
                'content': {'application/yang-data+json': {
                    'schema': input_schema,
                    'example': {f"{module_prefix}:input": input_example}
                }}
            }
        ops['post'] = op
        return ops

    # GET (always for data nodes)
    ops['get'] = {
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
                'content': {'application/yang-data+json': {'schema': schema, 'example': wrapped}}
            },
            '401': {'description': 'Unauthorized'},
            '404': {'description': 'Resource not found'}
        }
    }

    if node.rw == 'rw':
        body_content = {
            'required': True,
            'content': {'application/yang-data+json': {'schema': schema, 'example': wrapped}}
        }
        ops['put'] = {
            'summary': f"Replace {node.name}",
            'operationId': f"put-{op_id}",
            'tags': [tag],
            'requestBody': body_content,
            'responses': {'201': {'description': 'Created'}, '204': {'description': 'Updated'}, '400': {'description': 'Invalid input'}}
        }
        ops['patch'] = {
            'summary': f"Update {node.name}",
            'operationId': f"patch-{op_id}",
            'tags': [tag],
            'requestBody': body_content,
            'responses': {'204': {'description': 'Updated'}, '400': {'description': 'Invalid input'}}
        }
        ops['delete'] = {
            'summary': f"Delete {node.name}",
            'operationId': f"delete-{op_id}",
            'tags': [tag],
            'responses': {'204': {'description': 'Deleted'}, '404': {'description': 'Not found'}}
        }

    return ops


def create_spec(title, description, tag, paths, module_name, version='17.18.1'):
    return {
        'openapi': '3.0.0',
        'info': {
            'title': title, 'description': description, 'version': version,
            'contact': {'name': 'Cisco IOS-XE RESTCONF API', 'url': 'https://developer.cisco.com/iosxe/'},
            'x-yang-module': module_name, 'x-model-type': 'ietf'
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
        total_descendants = 0
        root_names = []
        has_rpc = False
        for root in root_list:
            root_names.append(root.name)
            total_descendants += root.descendant_count()

            if root.node_type == 'rpc':
                has_rpc = True
                rpc_path = f"/operations/{module_name}:{root.name}"
                if rpc_path not in all_paths:
                    all_paths[rpc_path] = make_path_operations(rpc_path, root, root.name, module_name)
            else:
                base_path = f"/data/{module_name}:{root.name}"
                tag = root.name
                deep = collect_deep_paths(root, base_path, max_depth=max_depth)
                for rpath, rnode in deep:
                    if rpath not in all_paths:
                        all_paths[rpath] = make_path_operations(rpath, rnode, tag, module_name)

        if not all_paths:
            continue

        total_ops = sum(len(ops) for ops in all_paths.values())

        title = f"Cisco IOS-XE IETF - {module_name}"
        desc = (f"IETF standard data from `{module_name}` module.\n\n"
                f"**Root containers:** {len(root_list)} ({', '.join(root_names[:5])}{'...' if len(root_names) > 5 else ''})\n"
                f"**Paths:** {len(all_paths)} | **Operations:** {total_ops}\n\n"
                f"Supports CRUD for read-write nodes, GET for read-only nodes.")

        primary_tag = root_list[0].name
        spec = create_spec(title, desc, primary_tag, all_paths, module_name)

        spec_json = json.dumps(spec, indent=2)
        size_kb = len(spec_json.encode('utf-8')) / 1024
        if size_kb > 2048 and max_depth > 3:
            return process_tree_file(html_path, output_dir, max_depth=max_depth - 1)

        fname = module_name
        out_path = output_dir / f"{fname}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(spec_json)

        results.append((fname, len(all_paths), total_ops))

    return results


def generate_all():
    script_dir = Path(__file__).parent
    tree_dir = script_dir.parent / 'yang-trees'
    output_dir = script_dir.parent / 'swagger-ietf-model' / 'api'

    if output_dir.exists():
        for f in output_dir.glob('*.json'):
            f.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("IETF YANG Tree -> OpenAPI 3.0 Generator (v2)")
    print(f"{'='*70}\n")

    tree_files = sorted(tree_dir.glob('ietf-*.html'))
    print(f"Found {len(tree_files)} IETF tree files\n")

    all_generated = []
    total_paths = 0
    total_ops = 0
    errors = 0

    for tf in tree_files:
        try:
            results = process_tree_file(tf, output_dir)
            for fname, path_count, op_count in results:
                all_generated.append(fname)
                total_paths += path_count
                total_ops += op_count
                print(f"  {fname}: {path_count} paths, {op_count} ops")
        except Exception as e:
            errors += 1
            print(f"  ERROR {tf.name}: {e}")

    manifest = {
        'total_modules': len(all_generated),
        'total_paths': total_paths,
        'total_operations': total_ops,
        'modules': sorted(all_generated),
        'generator': 'generate_ietf_from_tree.py',
        'source': 'yang-trees/ietf-*.html',
        'version': '17.18.1'
    }
    with open(output_dir / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Done: {len(all_generated)} specs, {total_paths} paths, {total_ops} ops, {errors} errors")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    generate_all()
