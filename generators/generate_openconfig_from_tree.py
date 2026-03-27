#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specs from resolved YANG tree HTML files for OpenConfig modules.
GET/PUT/PATCH/DELETE for rw (config) nodes, GET-only for ro (state) nodes.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple


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
        return sum(1 + c.descendant_count() for c in self.children)


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

        node_type = 'list' if is_list else ('leaf' if rest and not rest.startswith('[') and not rest.startswith('{') else 'container')
        root = TreeNode(name, rw, node_type, depth=0)
        root.raw_name = raw_name

        end_line = root_line_indices[idx + 1][0] if idx + 1 < len(root_line_indices) else len(lines)
        node_stack = [(col, root)]

        for i in range(line_idx + 1, end_line):
            line = lines[i]
            if not line.strip():
                continue

            case_match = re.search(r'[+o]--:\((\S+)\)', line)
            if case_match:
                c = case_match.start()
                node = TreeNode(case_match.group(1), 'rw', 'case', depth=0)
                while len(node_stack) > 1 and node_stack[-1][0] >= c:
                    node_stack.pop()
                p = node_stack[-1][1]
                p.children.append(node)
                node.depth = p.depth + 1
                node_stack.append((c, node))
                continue

            m = re.search(r'[+o]-+(rw|ro|x)\s+(\S+)(.*)', line)
            if not m:
                continue

            c = m.start()
            rw_c = m.group(1)
            raw = m.group(2)
            rest_c = m.group(3).strip()
            cn = raw.rstrip('?').rstrip('!').rstrip('*')
            ck = bool(re.search(r'\[(\S+)\]', rest_c))
            cl = raw.rstrip('?').rstrip('!').endswith('*') and ck

            if cl:
                ct, cyt = 'list', ''
            elif raw.startswith('(') and (raw.endswith(')') or raw.endswith(')?')):
                ct, cn, cyt = 'choice', raw.strip('()?'), ''
            elif rest_c and not rest_c.startswith('[') and not rest_c.startswith('{'):
                cyt = rest_c.split()[0] if rest_c.split() else 'string'
                ct = 'leaf-list' if (raw.rstrip('?').rstrip('!').endswith('*') and not ck) else 'leaf'
            else:
                ct, cyt = 'container', ''

            node = TreeNode(cn, rw_c, ct, cyt, depth=0)
            node.raw_name = raw
            while len(node_stack) > 1 and node_stack[-1][0] >= c:
                node_stack.pop()
            p = node_stack[-1][1]
            p.children.append(node)
            node.depth = p.depth + 1
            node_stack.append((c, node))

        roots.append((module_name, root))
    return roots


# --- Example + Schema ---

def example_for_type(yang_type, name=''):
    base = yang_type.split(':')[-1] if ':' in yang_type else yang_type
    type_map = {
        'string': 'example', 'uint8': 1, 'uint16': 1, 'uint32': 1, 'uint64': 1,
        'int8': 1, 'int16': 1, 'int32': 1, 'int64': 1,
        'boolean': True, 'empty': None, 'enumeration': 'default',
        'union': 'auto', 'decimal64': 1.0, 'identityref': 'IDENTITY',
        'leafref': 'ref-value', 'binary': 'QmFzZTY0', 'bits': '',
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
        return generate_example(node.children[0], max_depth, depth) if node.children else {}
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
            ce = generate_example(child, max_depth, depth + 1)
            obj[child.name] = [ce] if child.node_type == 'list' and isinstance(ce, dict) else ce
    return obj


def yang_type_to_schema(yang_type, name=''):
    base = yang_type.split(':')[-1] if ':' in yang_type else yang_type
    mapping = {
        'string': {'type': 'string'}, 'uint8': {'type': 'integer'},
        'uint16': {'type': 'integer'}, 'uint32': {'type': 'integer'},
        'uint64': {'type': 'integer'}, 'int8': {'type': 'integer'},
        'int16': {'type': 'integer'}, 'int32': {'type': 'integer'},
        'int64': {'type': 'integer'}, 'boolean': {'type': 'boolean'},
        'empty': {'type': 'boolean'}, 'enumeration': {'type': 'string'},
        'union': {'type': 'string'}, 'decimal64': {'type': 'number'},
        'identityref': {'type': 'string'}, 'leafref': {'type': 'string'},
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
    props, req = {}, []
    for child in node.children:
        if child.node_type in ('choice', 'case'):
            target = child.children[0] if child.node_type == 'choice' and child.children else child
            for gc in (target.children if target else []):
                props[gc.name] = build_schema(gc, max_depth, depth + 1)
        else:
            props[child.name] = build_schema(child, max_depth, depth + 1)
            if child.is_key:
                req.append(child.name)
    schema = {'type': 'object'}
    if props:
        schema['properties'] = props
    if req:
        schema['required'] = req
    return {'type': 'array', 'items': schema} if node.node_type == 'list' else schema


# --- Paths ---

def collect_deep_paths(node, base, max_depth=5, depth=0):
    paths = [(base, node)]
    if depth >= max_depth:
        return paths
    for child in node.children:
        if child.node_type in ('choice', 'case'):
            target = child if child.node_type != 'choice' else (child.children[0] if child.children else child)
            for gc in target.children:
                cp = f"{base}/{gc.name}"
                if gc.node_type == 'list':
                    paths.append((cp, gc))
                    kc = gc.find_child('name') or gc.find_child('id')
                    if kc:
                        paths.append((f"{cp}={{{kc.name}}}", gc))
                    paths.extend(collect_deep_paths(gc, cp, max_depth, depth + 1))
                elif gc.node_type == 'container':
                    paths.extend(collect_deep_paths(gc, cp, max_depth, depth + 1))
                else:
                    paths.append((cp, gc))
        elif child.node_type == 'list':
            cp = f"{base}/{child.name}"
            paths.append((cp, child))
            kc = child.find_child('name') or child.find_child('id')
            if kc:
                paths.append((f"{cp}={{{kc.name}}}", child))
            paths.extend(collect_deep_paths(child, cp, max_depth, depth + 1))
        elif child.node_type == 'container':
            cp = f"{base}/{child.name}"
            paths.extend(collect_deep_paths(child, cp, max_depth, depth + 1))
        elif child.node_type in ('leaf', 'leaf-list'):
            paths.append((f"{base}/{child.name}", child))
    return paths


COMMON_COMPONENTS = {
    'securitySchemes': {
        'basicAuth': {'type': 'http', 'scheme': 'basic',
                      'description': 'RESTCONF basic authentication (RFC 8040)'}
    },
    'parameters': {
        'content-type': {'name': 'Content-Type', 'in': 'header',
                         'schema': {'type': 'string', 'default': 'application/yang-data+json'}},
        'accept': {'name': 'Accept', 'in': 'header', 'required': False,
                   'schema': {'type': 'string', 'default': 'application/yang-data+json'}},
        'depth': {'name': 'depth', 'in': 'query', 'required': False,
                  'schema': {'type': 'string', 'default': 'unbounded'}}
    }
}


def make_path_ops(restconf_path, node, tag, module_prefix):
    schema = build_schema(node, max_depth=4)
    example = generate_example(node, max_depth=3)
    wrapper = f"{module_prefix}:{node.name}"
    wrapped = {wrapper: [example] if node.node_type == 'list' else example}
    op_id = restconf_path.replace('/data/', '').replace('/', '-').replace('=', '-').replace('{', '').replace('}', '')

    ops = {}
    ops['get'] = {
        'summary': f"Get {node.name}",
        'operationId': f"get-{op_id}",
        'tags': [tag],
        'parameters': [{'$ref': '#/components/parameters/accept'}, {'$ref': '#/components/parameters/depth'}],
        'responses': {
            '200': {'description': 'OK', 'content': {'application/yang-data+json': {'schema': schema, 'example': wrapped}}},
            '401': {'description': 'Unauthorized'}, '404': {'description': 'Not found'}
        }
    }

    if node.rw == 'rw':
        body = {'required': True, 'content': {'application/yang-data+json': {'schema': schema, 'example': wrapped}}}
        ops['put'] = {'summary': f"Replace {node.name}", 'operationId': f"put-{op_id}", 'tags': [tag],
                      'requestBody': body, 'responses': {'201': {'description': 'Created'}, '204': {'description': 'Updated'}, '400': {'description': 'Bad request'}}}
        ops['patch'] = {'summary': f"Update {node.name}", 'operationId': f"patch-{op_id}", 'tags': [tag],
                        'requestBody': body, 'responses': {'204': {'description': 'Updated'}, '400': {'description': 'Bad request'}}}
        ops['delete'] = {'summary': f"Delete {node.name}", 'operationId': f"delete-{op_id}", 'tags': [tag],
                         'responses': {'204': {'description': 'Deleted'}, '404': {'description': 'Not found'}}}
    return ops


def create_spec(title, desc, tag, paths, module_name):
    return {
        'openapi': '3.0.0',
        'info': {'title': title, 'description': desc, 'version': '17.18.1',
                 'contact': {'name': 'Cisco IOS-XE RESTCONF API', 'url': 'https://developer.cisco.com/iosxe/'},
                 'x-yang-module': module_name, 'x-model-type': 'openconfig'},
        'servers': [{'url': 'https://{device}:{port}/restconf', 'description': 'IOS-XE Device',
                     'variables': {'device': {'default': 'devnetsandboxiosxec9k.cisco.com'}, 'port': {'default': '443'}}}],
        'paths': paths, 'components': COMMON_COMPONENTS, 'security': [{'basicAuth': []}]
    }


# --- Main ---

def process_tree_file(html_path, output_dir, max_depth=5):
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
        root_names = []
        for root in root_list:
            base = f"/data/{module_name}:{root.name}"
            root_names.append(root.name)
            deep = collect_deep_paths(root, base, max_depth=max_depth)
            for rp, rn in deep:
                if rp not in all_paths:
                    all_paths[rp] = make_path_ops(rp, rn, root.name, module_name)
        if not all_paths:
            continue

        total_ops = sum(len(o) for o in all_paths.values())
        title = f"OpenConfig - {module_name}"
        desc = (f"OpenConfig `{module_name}` module.\n\n"
                f"**Root containers:** {len(root_list)} ({', '.join(root_names[:5])}{'...' if len(root_names) > 5 else ''})\n"
                f"**Paths:** {len(all_paths)} | **Ops:** {total_ops}\n\n"
                f"`config` subtrees: GET/PUT/PATCH/DELETE | `state` subtrees: GET only.")

        primary_tag = root_list[0].name
        spec = create_spec(title, desc, primary_tag, all_paths, module_name)
        spec_json = json.dumps(spec, indent=2)
        if len(spec_json.encode('utf-8')) / 1024 > 2048 and max_depth > 3:
            return process_tree_file(html_path, output_dir, max_depth - 1)

        out = output_dir / f"{module_name}.json"
        with open(out, 'w', encoding='utf-8') as f:
            f.write(spec_json)
        results.append((module_name, len(all_paths), total_ops))
    return results


def generate_all():
    script_dir = Path(__file__).parent
    tree_dir = script_dir.parent / 'yang-trees'
    output_dir = script_dir.parent / 'swagger-openconfig-model' / 'api-v2'

    if output_dir.exists():
        for f in output_dir.glob('*.json'):
            f.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("OpenConfig YANG Tree -> OpenAPI 3.0 Generator (v2)")
    print(f"{'='*70}\n")

    tree_files = sorted(tree_dir.glob('openconfig-*.html'))
    print(f"Found {len(tree_files)} OpenConfig tree files\n")

    all_generated = []
    total_paths = 0
    total_ops = 0
    skipped = 0

    for tf in tree_files:
        try:
            results = process_tree_file(tf, output_dir)
            if not results:
                skipped += 1
                continue
            for fname, pc, oc in results:
                all_generated.append(fname)
                total_paths += pc
                total_ops += oc
                print(f"  {fname}: {pc} paths, {oc} ops")
        except Exception as e:
            skipped += 1
            print(f"  SKIP {tf.name}: {e}")

    manifest = {
        'total_modules': len(all_generated),
        'total_paths': total_paths,
        'total_operations': total_ops,
        'modules': sorted(all_generated),
        'generator': 'generate_openconfig_from_tree.py',
        'source': 'yang-trees/openconfig-*.html',
        'version': '17.18.1'
    }
    with open(output_dir / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Done: {len(all_generated)} specs, {total_paths} paths, {total_ops} ops, {skipped} skipped")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    generate_all()
