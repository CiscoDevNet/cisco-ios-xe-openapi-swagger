#!/usr/bin/env python3
"""
Swagger Spec Enhancement Script
================================
Reads YANG tree HTML files and corresponding Swagger JSON specs,
identifies missing RESTCONF paths, and generates the missing paths
with proper schemas to fill the gaps.

Processes all specs scored MEDIUM or above (gap_score >= 30) from audit_results.json.
Skips events and MIB folders (different paradigm).

Usage:
  python scripts/enhance_swagger.py              # enhance all focus specs
  python scripts/enhance_swagger.py --dry-run    # show what would change
  python scripts/enhance_swagger.py --spec NAME  # enhance a single spec
"""

import json
import os
import re
import sys
import copy
from pathlib import Path
from collections import OrderedDict

ROOT = Path(__file__).resolve().parent.parent
YANG_TREES_DIR = ROOT / "yang-trees"
AUDIT_FILE = ROOT / "scripts" / "audit_results.json"

# Folders to enhance (skip events/MIB — different paradigm)
FOCUS_FOLDERS = {
    "swagger-oper-model",
    "swagger-cfg-model",
    "swagger-openconfig-model",
    "swagger-ietf-model",
    "swagger-rpc-model",
    "swagger-other-model",
}

# Min gap score to enhance
MIN_SCORE = 30

# YANG type -> JSON Schema type mapping
YANG_TYPE_MAP = {
    "string": {"type": "string"},
    "boolean": {"type": "boolean"},
    "empty": {"type": "string"},
    "binary": {"type": "string", "format": "binary"},
    "bits": {"type": "string"},
    "decimal64": {"type": "number"},
    "int8": {"type": "integer", "minimum": -128, "maximum": 127},
    "int16": {"type": "integer", "minimum": -32768, "maximum": 32767},
    "int32": {"type": "integer", "minimum": -2147483648, "maximum": 2147483647},
    "int64": {"type": "integer"},
    "uint8": {"type": "integer", "minimum": 0, "maximum": 255},
    "uint16": {"type": "integer", "minimum": 0, "maximum": 65535},
    "uint32": {"type": "integer", "minimum": 0, "maximum": 4294967295},
    "uint64": {"type": "integer", "minimum": 0},
    "enumeration": {"type": "string"},
    "identityref": {"type": "string"},
    "leafref": {"type": "string"},
    "union": {"type": "string"},
    "instance-identifier": {"type": "string"},
}


class YangNode:
    """Represents a node in the YANG tree hierarchy."""
    def __init__(self, name, depth, access, is_list=False, is_leaf=False,
                 yang_type=None, keys=None, description=""):
        self.name = name
        self.depth = depth
        self.access = access  # 'w' or 'o'
        self.is_list = is_list
        self.is_leaf = is_leaf
        self.yang_type = yang_type
        self.keys = keys  # list of key names for lists
        self.description = description
        self.children = []
        self.parent = None

    def is_container(self):
        return not self.is_list and not self.is_leaf

    def is_addressable(self):
        """Containers and lists are RESTCONF-addressable."""
        return self.is_container() or self.is_list

    def full_path(self, module_name):
        """Build the full RESTCONF path for this node."""
        parts = []
        node = self
        while node:
            if node.is_addressable():
                if node.is_list and node.keys:
                    key_params = ",".join(f"{{{k}}}" for k in node.keys)
                    parts.insert(0, f"{node.name}={key_params}")
                else:
                    parts.insert(0, node.name)
            node = node.parent

        if not parts:
            return None

        # First segment has module prefix
        parts[0] = f"{module_name}:{parts[0]}"
        return "/data/" + "/".join(parts)

    def collection_path(self, module_name):
        """For list nodes, return the collection path (without keys)."""
        if not self.is_list:
            return None
        parts = []
        node = self
        while node:
            if node.is_addressable():
                parts.insert(0, node.name)
            node = node.parent

        if not parts:
            return None

        parts[0] = f"{module_name}:{parts[0]}"
        return "/data/" + "/".join(parts)


def parse_yang_tree_hierarchical(html_path):
    """
    Parse YANG tree HTML and build a hierarchical node tree.
    Returns (module_name, root_nodes_list).
    """
    try:
        with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return None, []

    # Find the right <pre> block
    pre_matches = list(re.finditer(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL))
    tree_text = None
    for m in pre_matches:
        block = m.group(1)
        if 'module:' in block[:50] or '+--r' in block[:200]:
            tree_text = block
            break
    if not tree_text:
        return None, []

    tree_text = re.sub(r'<[^>]+>', '', tree_text)
    tree_text = tree_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

    lines = tree_text.split('\n')

    # Extract module name
    module_name = None
    for line in lines:
        m = re.match(r'\s*module:\s*(\S+)', line)
        if m:
            module_name = m.group(1)
            break

    if not module_name:
        return None, []

    all_nodes = []
    # Stack to track parent at each depth: {depth: node}
    depth_stack = {}

    for line in lines:
        if not re.search(r'\+--', line):
            continue

        # Calculate depth
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        depth = indent // 3

        # Get access type
        rw_match = re.search(r'\+--r([wo])\s+', line)
        if not rw_match:
            continue
        access = rw_match.group(1)

        # Get node part
        node_part = re.sub(r'.*\+--r[wo]\s+', '', line).strip()

        # Detect list
        is_list = False
        keys = None
        if '*' in node_part:
            is_list = True
            key_match = re.search(r'\[([^\]]+)\]', node_part)
            if key_match:
                keys = [k.strip() for k in key_match.group(1).split()]
            node_part = re.sub(r'\*.*', '', node_part).strip()

        # Get name
        parts = node_part.split()
        name = parts[0].rstrip('?!') if parts else ''
        if not name or name.startswith('(') or name.startswith('|'):
            continue

        # Detect leaf vs container
        is_leaf = False
        yang_type = None
        if len(parts) >= 2:
            remaining = parts[1].rstrip('?')
            if remaining and not remaining.startswith('+') and not remaining.startswith('|') and not remaining.startswith('('):
                is_leaf = True
                yang_type = remaining

        # Handle choice/case nodes - skip them (they're structural, not RESTCONF addressable)
        if name.startswith('(') or '(' in node_part.split()[0] if node_part.split() else False:
            continue

        node = YangNode(
            name=name,
            depth=depth,
            access=access,
            is_list=is_list,
            is_leaf=is_leaf,
            yang_type=yang_type,
            keys=keys,
        )

        # Find parent
        for d in range(depth - 1, -1, -1):
            if d in depth_stack:
                parent = depth_stack[d]
                node.parent = parent
                parent.children.append(node)
                break

        # Update depth stack
        depth_stack[depth] = node
        # Clear deeper entries
        for d in list(depth_stack.keys()):
            if d > depth:
                del depth_stack[d]

        all_nodes.append(node)

    # Root nodes are those with no parent
    root_nodes = [n for n in all_nodes if n.parent is None]
    return module_name, root_nodes


def collect_all_restconf_paths(module_name, root_nodes, max_depth=None):
    """
    Walk the tree and collect all RESTCONF-addressable paths.

    Returns list of dicts:
      {path, name, is_list, keys, access, children_leaves, node}
    """
    paths = []

    def walk(node, current_depth=0):
        if max_depth is not None and current_depth > max_depth:
            return

        if node.is_addressable():
            path = node.full_path(module_name)
            if path:
                # Collect direct leaf children for schema
                child_leaves = [
                    c for c in node.children if c.is_leaf
                ]
                child_containers = [
                    c for c in node.children if c.is_container()
                ]
                child_lists = [
                    c for c in node.children if c.is_list
                ]

                paths.append({
                    'path': path,
                    'name': node.name,
                    'is_list': node.is_list,
                    'keys': node.keys,
                    'access': node.access,
                    'child_leaves': child_leaves,
                    'child_containers': child_containers,
                    'child_lists': child_lists,
                    'node': node,
                })

                # For lists, also add collection path
                if node.is_list:
                    coll_path = node.collection_path(module_name)
                    if coll_path and coll_path != path:
                        paths.append({
                            'path': coll_path,
                            'name': node.name,
                            'is_list': False,  # collection is like a container
                            'is_collection': True,
                            'keys': None,
                            'access': node.access,
                            'child_leaves': child_leaves,
                            'child_containers': child_containers,
                            'child_lists': child_lists,
                            'node': node,
                        })

        for child in node.children:
            walk(child, current_depth + 1)

    for root in root_nodes:
        walk(root)

    return paths


def yang_type_to_json_schema(yang_type):
    """Convert a YANG type string to a JSON Schema property definition."""
    if not yang_type:
        return {"type": "string"}

    # Strip module prefix: inet:ip-address -> ip-address, yang:counter64 -> counter64
    base = yang_type.split(':')[-1] if ':' in yang_type else yang_type

    # Check direct map
    if base in YANG_TYPE_MAP:
        return copy.deepcopy(YANG_TYPE_MAP[base])

    # Common patterns
    if 'counter' in base.lower() or 'gauge' in base.lower():
        return {"type": "string"}  # Large counters stored as strings
    if 'address' in base.lower() or 'prefix' in base.lower():
        return {"type": "string"}
    if 'date-and-time' in base.lower() or 'timestamp' in base.lower():
        return {"type": "string"}

    # Default to string
    return {"type": "string"}


def build_schema_for_node(module_name, node):
    """
    Build a flattened JSON Schema for a YANG node.
    Collects all leaf descendants into a flat properties dict.
    Nested containers become nested objects.
    """
    properties = OrderedDict()

    def collect_leaves(n, target_props):
        for child in n.children:
            if child.is_leaf:
                prop = yang_type_to_json_schema(child.yang_type)
                prop["description"] = child.name.replace('-', ' ').title()
                target_props[child.name] = prop
            elif child.is_container():
                # Nested container becomes nested object
                nested_props = OrderedDict()
                collect_leaves(child, nested_props)
                container_schema = {"type": "object", "description": child.name.replace('-', ' ').title()}
                if nested_props:
                    container_schema["properties"] = dict(nested_props)
                target_props[child.name] = container_schema
            elif child.is_list:
                # Lists at this level become object stubs
                target_props[child.name] = {
                    "type": "object",
                    "description": child.name.replace('-', ' ').title()
                }

    collect_leaves(node, properties)
    return dict(properties)


def make_oper_get(schema_ref, name, description, op_index, tag):
    """Create a GET operation for an oper (read-only) path."""
    return {
        "get": {
            "summary": f"Get {name}",
            "description": description,
            "operationId": f"get-{name}-{op_index}",
            "tags": [tag],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/yang-data+json": {
                            "schema": {"$ref": f"#/components/schemas/{schema_ref}"}
                        }
                    }
                },
                "404": {"description": "Resource not found"},
                "401": {"description": "Unauthorized"}
            }
        }
    }


def make_cfg_crud(schema_ref, name, description, op_index, tag):
    """Create GET/PUT/PATCH/DELETE operations for a config path."""
    return {
        "get": {
            "summary": f"Get {name}",
            "description": description,
            "operationId": f"get-{name}-{op_index}",
            "tags": [tag],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/yang-data+json": {
                            "schema": {"$ref": f"#/components/schemas/{schema_ref}"}
                        }
                    }
                },
                "404": {"description": "Resource not found"}
            }
        },
        "put": {
            "summary": f"Create or replace {name}",
            "description": f"Create or replace {description}",
            "operationId": f"put-{name}-{op_index}",
            "tags": [tag],
            "requestBody": {
                "required": True,
                "content": {
                    "application/yang-data+json": {
                        "schema": {"$ref": f"#/components/schemas/{schema_ref}"}
                    }
                }
            },
            "responses": {
                "201": {"description": "Created"},
                "204": {"description": "Updated"},
                "400": {"description": "Bad request"}
            }
        },
        "patch": {
            "summary": f"Modify {name}",
            "description": f"Partially modify {description}",
            "operationId": f"patch-{name}-{op_index}",
            "tags": [tag],
            "requestBody": {
                "required": True,
                "content": {
                    "application/yang-data+json": {
                        "schema": {"$ref": f"#/components/schemas/{schema_ref}"}
                    }
                }
            },
            "responses": {
                "204": {"description": "Updated"},
                "400": {"description": "Bad request"}
            }
        },
        "delete": {
            "summary": f"Delete {name}",
            "description": f"Delete {description}",
            "operationId": f"delete-{name}-{op_index}",
            "tags": [tag],
            "responses": {
                "204": {"description": "Deleted"},
                "404": {"description": "Not found"}
            }
        }
    }


def make_cfg_collection(schema_ref, name, description, op_index, tag):
    """Create GET + POST operations for a config list collection path."""
    return {
        "get": {
            "summary": f"Get {name}",
            "description": description,
            "operationId": f"get-{name}-{op_index}",
            "tags": [tag],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/yang-data+json": {
                            "schema": {"$ref": f"#/components/schemas/{schema_ref}"}
                        }
                    }
                },
                "404": {"description": "Resource not found"}
            }
        },
        "post": {
            "summary": f"Create {name}",
            "description": f"Create new entry in {description}",
            "operationId": f"post-{name}-{op_index}",
            "tags": [tag],
            "requestBody": {
                "required": True,
                "content": {
                    "application/yang-data+json": {
                        "schema": {"$ref": f"#/components/schemas/{schema_ref}"}
                    }
                }
            },
            "responses": {
                "201": {"description": "Created"},
                "400": {"description": "Bad request"},
                "409": {"description": "Conflict - resource already exists"}
            }
        }
    }


def determine_model_type(folder, module_name, existing_spec):
    """
    Determine if a spec is oper (read-only), config (read-write), or mixed.
    Returns 'oper', 'cfg', or 'mixed'.
    """
    if "oper" in folder or "-oper" in module_name:
        return "oper"
    if "cfg" in folder or "-cfg" in module_name:
        return "cfg"
    if "rpc" in folder or "-rpc" in module_name:
        return "rpc"

    # Check existing spec for method signatures
    methods = set()
    for path, ops in existing_spec.get('paths', {}).items():
        for m in ['get', 'put', 'patch', 'delete', 'post']:
            if m in ops:
                methods.add(m)

    if methods <= {'get'}:
        return "oper"
    if 'put' in methods or 'patch' in methods:
        return "cfg"
    return "cfg"  # Default to cfg for openconfig/ietf/other


def enhance_spec(spec_path, tree_path, folder, dry_run=False):
    """
    Enhance a single Swagger spec by adding missing paths from the YANG tree.

    Returns (added_paths, added_ops, added_schemas) counts, or None on error.
    """
    spec_name = Path(spec_path).stem

    # Load existing spec
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    except Exception as e:
        print(f"    ERROR: Cannot read spec {spec_name}: {e}")
        return None

    # Parse tree
    module_name, root_nodes = parse_yang_tree_hierarchical(tree_path)
    if not module_name or not root_nodes:
        print(f"    ERROR: Cannot parse tree for {spec_name}")
        return None

    # Determine model type
    model_type = determine_model_type(folder, module_name, spec)

    # Collect all possible RESTCONF paths from tree
    tree_paths = collect_all_restconf_paths(module_name, root_nodes)

    # Get existing paths
    existing_paths = set(spec.get('paths', {}).keys())

    # Find missing paths
    missing = [p for p in tree_paths if p['path'] not in existing_paths]

    if not missing:
        return (0, 0, 0)

    # Determine starting operation index
    existing_ops = spec.get('paths', {})
    max_index = -1
    for path_key, ops in existing_ops.items():
        for method in ['get', 'put', 'patch', 'delete', 'post']:
            if method in ops:
                op_id = ops[method].get('operationId', '')
                idx_match = re.search(r'-(\d+)$', op_id)
                if idx_match:
                    max_index = max(max_index, int(idx_match.group(1)))
    next_index = max_index + 1

    tag = spec.get('tags', [{}])[0].get('name', spec_name)

    added_paths = 0
    added_ops = 0
    added_schemas = 0

    for p in missing:
        path = p['path']
        name = p['name']
        node = p['node']
        is_collection = p.get('is_collection', False)

        # Build schema
        schema_name_suffix = name
        if p['is_list'] and not is_collection:
            schema_name_suffix = f"{name}-item"

        schema_ref = f"{module_name}-{schema_name_suffix}"
        description = name.replace('-', ' ').title()

        # Build operations based on model type and node type
        if model_type == "oper":
            ops = make_oper_get(schema_ref, name if not is_collection else name,
                               description, next_index, tag)
        elif model_type == "rpc":
            # RPCs only have POST at the action endpoint; skip adding non-RPC paths
            continue
        else:
            # cfg / openconfig / ietf / other
            if is_collection:
                # List collection: GET + POST
                ops = make_cfg_collection(schema_ref, name, description, next_index, tag)
            elif p['is_list']:
                # List instance with keys: GET + PUT + PATCH + DELETE
                ops = make_cfg_crud(schema_ref, f"{name}-item", description, next_index, tag)
            else:
                # Container: GET + PUT + PATCH + DELETE
                ops = make_cfg_crud(schema_ref, name, description, next_index, tag)

        # Add the path
        spec['paths'][path] = ops
        added_paths += 1
        added_ops += len(ops)
        next_index += 1

        # Add schema if not already present
        schemas = spec.setdefault('components', {}).setdefault('schemas', {})
        if schema_ref not in schemas:
            props = build_schema_for_node(module_name, node)
            schemas[schema_ref] = {
                "type": "object",
                "properties": props
            } if props else {"type": "object"}
            added_schemas += 1

    # Update path count in description
    info_desc = spec.get('info', {}).get('description', '')
    total_paths = len(spec.get('paths', {}))
    # Replace the **Paths:** N pattern
    info_desc = re.sub(r'\*\*Paths:\*\*\s*\d+', f'**Paths:** {total_paths}', info_desc)
    spec['info']['description'] = info_desc

    if not dry_run:
        # Write updated spec
        with open(spec_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return (added_paths, added_ops, added_schemas)


def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    single_spec = None

    for i, arg in enumerate(args):
        if arg == '--spec' and i + 1 < len(args):
            single_spec = args[i + 1]

    # Load audit results
    if not AUDIT_FILE.exists():
        print("ERROR: Run audit_swagger_vs_tree.py first to generate audit_results.json")
        sys.exit(1)

    with open(AUDIT_FILE, 'r') as f:
        audit = json.load(f)

    results = audit.get('results', [])

    # Filter to focus specs
    focus = [
        r for r in results
        if r['folder'] in FOCUS_FOLDERS
        and (r.get('gap_score') or 0) >= MIN_SCORE
    ]

    # Sort worst first
    focus.sort(key=lambda x: -(x.get('gap_score') or 0))

    if single_spec:
        focus = [r for r in focus if single_spec.lower() in r['name'].lower()]
        if not focus:
            print(f"No matching spec found for '{single_spec}'")
            sys.exit(1)

    print("=" * 72)
    print(f"  Swagger Enhancement {'(DRY RUN)' if dry_run else ''}")
    print(f"  Specs to enhance: {len(focus)}")
    print("=" * 72)

    total_added_paths = 0
    total_added_ops = 0
    total_added_schemas = 0
    enhanced_count = 0
    failed_count = 0

    for r in focus:
        name = r['name']
        folder = r['folder']
        score = r.get('gap_score', 0)
        tree_file = r.get('tree_file', f"{name}.html")

        spec_path = ROOT / folder / "api" / f"{name}.json"
        tree_path = YANG_TREES_DIR / tree_file

        if not spec_path.exists():
            print(f"  SKIP: {name} — spec not found at {spec_path}")
            failed_count += 1
            continue
        if not tree_path.exists():
            print(f"  SKIP: {name} — tree not found at {tree_path}")
            failed_count += 1
            continue

        result = enhance_spec(spec_path, tree_path, folder, dry_run=dry_run)

        if result is None:
            failed_count += 1
            continue

        added_p, added_o, added_s = result

        if added_p > 0:
            print(f"  OK {name}: +{added_p} paths, +{added_o} ops, +{added_s} schemas (was score {score})")
            total_added_paths += added_p
            total_added_ops += added_o
            total_added_schemas += added_s
            enhanced_count += 1
        else:
            print(f"  -- {name}: no missing paths found (score {score})")

    print("\n" + "=" * 72)
    print(f"  ENHANCEMENT COMPLETE {'(DRY RUN)' if dry_run else ''}")
    print("=" * 72)
    print(f"  Specs enhanced:     {enhanced_count}")
    print(f"  Specs skipped:      {len(focus) - enhanced_count - failed_count}")
    print(f"  Specs failed:       {failed_count}")
    print(f"  Total paths added:  {total_added_paths}")
    print(f"  Total ops added:    {total_added_ops}")
    print(f"  Total schemas added: {total_added_schemas}")

    if dry_run:
        print("\n  NOTE: DRY RUN - no files were modified")


if __name__ == "__main__":
    main()
