#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specs from resolved YANG tree HTML files for config (cfg) modules.
Produces deep specs with GET/PUT/PATCH/DELETE for rw nodes, GET-only for ro nodes.
"""

import json
import re
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Tree parser (shared logic with oper generator)
# ---------------------------------------------------------------------------

class TreeNode:
    __slots__ = ('name', 'raw_name', 'rw', 'node_type', 'yang_type',
                 'is_key', 'children', 'depth')

    def __init__(self, name, rw='rw', node_type='container', yang_type='',
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
    """Parse a YANG tree HTML and return list of (module_prefix, root_node)."""
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
        module_name = os.path.basename(html_path).replace('.html', '')

    node_lines = []
    for i, line in enumerate(lines):
        marker = re.search(r'[+o]-+(rw|ro|x)\s+(\S+)(.*)', line)
        if marker:
            node_lines.append((i, marker.start(), marker))

    if not node_lines:
        return []

    min_col = min(col for _, col, _ in node_lines)
    root_line_indices = [(i, col, m) for i, col, m in node_lines if col == min_col]

    roots = []
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
            end_line = len(lines)

        node_stack: List[Tuple[int, TreeNode]] = [(col, root)]

        for i in range(line_idx + 1, end_line):
            line = lines[i]
            if not line.strip():
                continue

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

    return roots


# ---------------------------------------------------------------------------
# Example + Schema (shared)
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
# Path collection & operations
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


COMMON_COMPONENTS = {
    'securitySchemes': {
        'basicAuth': {'type': 'http', 'scheme': 'basic',
                      'description': 'RESTCONF basic authentication (RFC 8040)'}
    },
    'parameters': {
        'content-type': {
            'name': 'Content-Type', 'in': 'header',
            'schema': {'type': 'string', 'default': 'application/yang-data+json'}
        },
        'accept': {
            'name': 'Accept', 'in': 'header', 'required': False,
            'schema': {'type': 'string', 'default': 'application/yang-data+json'}
        },
        'depth': {
            'name': 'depth', 'in': 'query', 'required': False,
            'description': 'Limit response depth',
            'schema': {'type': 'string', 'default': 'unbounded'}
        }
    }
}


def make_path_operations(restconf_path, node, tag, module_prefix):
    """Create GET + write operations (PUT/PATCH/DELETE for rw nodes)."""
    inner_schema = build_schema(node, max_depth=4)
    example = generate_example(node, max_depth=3)
    wrapper_key = f"{module_prefix}:{node.name}"
    wrapped = {wrapper_key: [example] if node.node_type == 'list' else example}
    # Wrap schema to match RESTCONF wire format so Swagger UI's Try-It body matches.
    schema = {'type': 'object', 'properties': {wrapper_key: inner_schema}}
    op_id = restconf_path.replace('/data/', '').replace('/', '-').replace('=', '-').replace('{', '').replace('}', '')

    ops = {}

    # GET (always)
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
            'x-yang-module': module_name, 'x-model-type': 'configuration'
        },
        'servers': [{
            'url': 'https://{device}:{port}/restconf',
            'description': 'IOS-XE Device RESTCONF API',
            'variables': {'device': {'default': 'devnetsandboxiosxec9k.cisco.com'}, 'port': {'default': '443'}}
        }],
        'paths': paths,
        'components': COMMON_COMPONENTS,
        'security': [{'basicAuth': []}]
    }


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def process_tree_file(html_path, output_dir, max_depth=8):
    results = []
    roots = parse_yang_tree_html(html_path)
    if not roots:
        return results

    # Group roots by module name so multiple top-level containers from the
    # same YANG module produce a single spec file (avoids fname collisions
    # where last-write-wins; mirrors generate_oper_from_tree.py logic).
    from collections import defaultdict
    module_roots: dict[str, list] = defaultdict(list)
    for module_name, root in roots:
        module_roots[module_name].append(root)

    for module_name, root_list in module_roots.items():
        paths_dict = {}
        total_descendants = 0
        root_names = []
        for root in root_list:
            base_path = f"/data/{module_name}:{root.name}"
            tag = root.name
            root_names.append(root.name)
            total_descendants += root.descendant_count()
            deep = collect_deep_paths(root, base_path, max_depth=max_depth)
            for rpath, rnode in deep:
                if rpath not in paths_dict:
                    paths_dict[rpath] = make_path_operations(rpath, rnode, tag, module_name)

        if not paths_dict:
            continue

        # Count operations (rw gets 4 ops, ro gets 1)
        total_ops = sum(len(ops) for ops in paths_dict.values())

        title = f"Cisco IOS-XE Configuration - {module_name}"
        desc = (f"Configuration data from `{module_name}` module.\n\n"
                f"**Root containers:** {len(root_list)} ({', '.join(root_names[:5])}{'...' if len(root_names) > 5 else ''})\n"
                f"**Paths:** {len(paths_dict)} | **Operations:** {total_ops} | "
                f"**Descendants:** {total_descendants}\n\n"
                f"Supports GET/PUT/PATCH/DELETE for read-write nodes.")

        primary_tag = root_list[0].name
        spec = create_spec(title, desc, primary_tag, paths_dict, module_name)

        spec_json = json.dumps(spec, indent=2)
        size_kb = len(spec_json.encode('utf-8')) / 1024
        if size_kb > 2048 and max_depth > 3:
            return process_tree_file(html_path, output_dir, max_depth=max_depth - 1)

        fname = module_name
        out_path = output_dir / f"{fname}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(spec_json)
        results.append((fname, len(paths_dict), total_ops))

    return results


def _resolve_paths(version: str):
    """Locate tree input dir + spec output dir for the given release.

    For 17.18.1, prefer the per-release layout when releases/17.18.1/yang-trees
    exists (the dataset has been migrated). Fall back to the legacy top-level
    layout otherwise.
    """
    project_root = Path(__file__).resolve().parent.parent
    release_tree = project_root / 'releases' / version / 'yang-trees'
    if release_tree.is_dir():
        tree_dir = release_tree
        output_dir = (project_root / 'releases' / version
                      / 'swagger-cfg-model' / 'api')
    elif version == '17.18.1':
        tree_dir = project_root / 'yang-trees'
        output_dir = project_root / 'swagger-cfg-model' / 'api'
    else:
        tree_dir = project_root / 'releases' / version / 'yang-trees'
        output_dir = (project_root / 'releases' / version
                      / 'swagger-cfg-model' / 'api')
    return tree_dir, output_dir


def generate_all(version: str = '17.18.1'):
    tree_dir, output_dir = _resolve_paths(version)

    if output_dir.exists():
        for f in output_dir.glob('*.json'):
            f.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"Configuration YANG Tree -> OpenAPI 3.0 Generator (v2)  [{version}]")
    print(f"  trees:  {tree_dir}")
    print(f"  output: {output_dir}")
    print(f"{'='*70}\n")

    tree_files = sorted(tree_dir.glob('Cisco-IOS-XE-*-cfg*.html'))
    print(f"Found {len(tree_files)} configuration tree files\n")

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
        'generator': 'generate_cfg_from_tree.py',
        'source': 'yang-trees/Cisco-IOS-XE-*-cfg.html',
        'version': version,
    }
    with open(output_dir / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Done: {len(all_generated)} specs, {total_paths} paths, {total_ops} ops, {errors} errors")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', default='17.18.1')
    args = ap.parse_args()
    generate_all(args.version)
