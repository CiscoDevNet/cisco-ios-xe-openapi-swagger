#!/usr/bin/env python3
"""
Generate missing OpenAPI specs for dual-role YANG modules.

These modules have both config/data AND notifications/RPCs but are missing
specs for their config data portion (and in one case, a missing events spec).

This generator:
1. Parses YANG files for container/list/leaf nodes (config data)
2. Generates OpenAPI 3.0 specs with RESTCONF paths
3. Places them in the appropriate swagger model folder
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
YANG_DIR = BASE / "references" / "17181-YANG-modules"
GH_PAGES = "https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger"

# Modules missing config specs and where to put them
MISSING_CONFIG_SPECS = {
    # RPC modules with config data -> swagger-other-model
    "Cisco-IOS-XE-cellular-rpc": "swagger-other-model",
    "Cisco-IOS-XE-cli-preview-rpc": "swagger-other-model",
    "Cisco-IOS-XE-cli-rpc": "swagger-other-model",
    "Cisco-IOS-XE-cts-rpc": "swagger-other-model",
    "Cisco-IOS-XE-install-rpc": "swagger-other-model",
    "Cisco-IOS-XE-livetools-actions-rpc": "swagger-other-model",
    "Cisco-IOS-XE-nwpi-rpc": "swagger-other-model",
    "Cisco-IOS-XE-omp-rpc": "swagger-other-model",
    "Cisco-IOS-XE-port-security-rpc": "swagger-other-model",
    "Cisco-IOS-XE-power-supply-rpc": "swagger-other-model",
    "Cisco-IOS-XE-rpc": "swagger-other-model",
    "Cisco-IOS-XE-switch-rpc": "swagger-other-model",
    "Cisco-IOS-XE-trace-rpc": "swagger-other-model",
    "Cisco-IOS-XE-ucse-rpc": "swagger-other-model",
    "Cisco-IOS-XE-utd-rpc": "swagger-other-model",
    "Cisco-IOS-XE-wireless-access-point-cmd-rpc": "swagger-other-model",
    "cisco-ia": "swagger-other-model",
    "tailf-netconf-query": "swagger-other-model",
    "tailf-netconf-transactions": "swagger-other-model",
    # Events modules with config data -> swagger-other-model
    "Cisco-IOS-XE-controller-shdsl-events": "swagger-other-model",
    "Cisco-IOS-XE-ip-sla-events": "swagger-other-model",
    "Cisco-IOS-XE-line-events": "swagger-other-model",
    "Cisco-IOS-XE-platform-software-events": "swagger-other-model",
    "tailf-kicker": "swagger-other-model",
    # Missing both config + events
    "Cisco-IOS-XE-l2vpn": "swagger-other-model",
}

# Module missing events spec
MISSING_EVENTS_SPECS = {
    "Cisco-IOS-XE-wpan-oper": "swagger-events-model",
    "Cisco-IOS-XE-l2vpn": "swagger-events-model",
}


def parse_yang_type(yang_type):
    """Convert YANG type to JSON Schema type."""
    type_map = {
        "string": ("string", None),
        "boolean": ("boolean", None),
        "empty": ("boolean", None),
        "int8": ("integer", "int32"),
        "int16": ("integer", "int32"),
        "int32": ("integer", "int32"),
        "int64": ("integer", "int64"),
        "uint8": ("integer", "int32"),
        "uint16": ("integer", "int32"),
        "uint32": ("integer", "int64"),
        "uint64": ("integer", "int64"),
        "decimal64": ("number", "double"),
        "binary": ("string", "byte"),
        "enumeration": ("string", None),
        "union": ("string", None),
        "leafref": ("string", None),
        "identityref": ("string", None),
        "instance-identifier": ("string", None),
        "inet:ip-address": ("string", None),
        "inet:ipv4-address": ("string", None),
        "inet:ipv6-address": ("string", None),
        "inet:host": ("string", None),
        "inet:port-number": ("integer", "int32"),
        "inet:uri": ("string", "uri"),
        "yang:counter32": ("integer", "int64"),
        "yang:counter64": ("integer", "int64"),
        "yang:gauge32": ("integer", "int64"),
        "yang:gauge64": ("integer", "int64"),
        "yang:date-and-time": ("string", "date-time"),
        "yang:timeticks": ("integer", "int64"),
    }
    # Strip module prefix
    clean = yang_type.strip()
    if ":" in clean:
        clean = clean.split(":")[-1]
    t, fmt = type_map.get(clean, ("string", None))
    result = {"type": t}
    if fmt:
        result["format"] = fmt
    return result


def get_example_value(name, json_type):
    """Generate a reasonable example value for a leaf."""
    if json_type == "boolean":
        return True
    if json_type == "integer":
        return 1
    if json_type == "number":
        return 1.0
    # Common name-based examples
    name_lower = name.lower()
    if "address" in name_lower or "ip" in name_lower:
        return "10.1.1.1"
    if "name" in name_lower:
        return "example"
    if "id" in name_lower:
        return "1"
    if "port" in name_lower:
        return 443
    if "description" in name_lower or "desc" in name_lower:
        return "Description"
    if "time" in name_lower or "date" in name_lower:
        return "2026-01-01T00:00:00Z"
    if "path" in name_lower:
        return "/path"
    if "url" in name_lower or "uri" in name_lower:
        return "https://example.com"
    return "value"


def find_block_end(content, start):
    """Find the matching closing brace for an opening brace at start."""
    depth = 0
    i = start
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(content) - 1


def extract_top_level_nodes(yang_content, module_name):
    """Extract top-level containers and lists from a YANG module.
    Skip groupings, RPCs, notifications, and augments."""
    nodes = []

    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', yang_content, flags=re.DOTALL)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

    # Find the module body
    module_match = re.search(r'module\s+\S+\s*\{', content)
    if not module_match:
        return nodes

    module_start = module_match.end()

    # Find top-level containers and lists (not inside grouping/rpc/notification/augment)
    # We need to track brace depth to only get top-level nodes
    depth = 1  # We're inside the module block
    i = module_start
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                break

        # Only look at depth 1 (direct children of module)
        if depth == 1:
            # Check for container/list at this position
            for node_type in ['container', 'list']:
                pattern = rf'{node_type}\s+(\S+)\s*\{{'
                m = re.match(pattern, content[i:])
                if m:
                    node_name = m.group(1)
                    block_start = i + m.start()
                    brace_pos = i + m.end() - 1
                    block_end = find_block_end(content, brace_pos)
                    block_content = content[brace_pos:block_end + 1]

                    # Check if config false
                    config_false = bool(re.search(r'config\s+false\s*;', block_content[:500]))

                    # Extract key for lists
                    key = None
                    if node_type == 'list':
                        key_match = re.search(r'key\s+"([^"]+)"', block_content)
                        if not key_match:
                            key_match = re.search(r"key\s+'([^']+)'", block_content)
                        if key_match:
                            key = key_match.group(1)

                    # Extract leaves
                    leaves = extract_leaves(block_content)

                    # Extract description
                    desc_match = re.search(r'description\s+"([^"]*(?:""[^"]*)*)"', block_content[:1000])
                    description = desc_match.group(1).replace('""', '"')[:200] if desc_match else ""

                    nodes.append({
                        "type": node_type,
                        "name": node_name,
                        "config_false": config_false,
                        "key": key,
                        "description": description,
                        "leaves": leaves,
                        "block": block_content,
                    })

                    # Skip past this block
                    i = block_end + 1
                    continue

            # Skip grouping, rpc, notification, augment blocks at top level
            for skip_type in ['grouping', 'rpc', 'notification', 'augment', 'typedef', 'identity']:
                skip_pattern = rf'{skip_type}\s+'
                if re.match(skip_pattern, content[i:]):
                    # Find the opening brace and skip to closing
                    brace_match = re.search(r'\{', content[i:])
                    if brace_match:
                        brace_pos = i + brace_match.start()
                        block_end = find_block_end(content, brace_pos)
                        i = block_end + 1
                        continue

        i += 1

    return nodes


def extract_leaves(block_content):
    """Extract leaf and leaf-list definitions from a block."""
    leaves = []
    # Find leaf and leaf-list definitions
    for m in re.finditer(r'(leaf(?:-list)?)\s+(\S+)\s*\{([^}]*)\}', block_content):
        leaf_type = m.group(1)
        leaf_name = m.group(2)
        leaf_body = m.group(3)

        # Get type
        type_match = re.search(r'type\s+(\S+?)(?:\s*\{|\s*;)', leaf_body)
        yang_type = type_match.group(1) if type_match else "string"

        schema = parse_yang_type(yang_type)

        # Get description
        desc_match = re.search(r'description\s+"([^"]*)"', leaf_body)
        desc = desc_match.group(1)[:150] if desc_match else None

        leaf_info = {
            "name": leaf_name,
            "is_list": leaf_type == "leaf-list",
            "schema": schema,
            "description": desc,
        }
        leaves.append(leaf_info)

    return leaves[:20]  # Limit to avoid huge schemas


def extract_notifications(yang_content, module_name):
    """Extract notification definitions from a YANG module."""
    notifications = []
    content = re.sub(r'/\*.*?\*/', '', yang_content, flags=re.DOTALL)

    for m in re.finditer(r'notification\s+(\S+)\s*\{', content):
        notif_name = m.group(1)
        brace_pos = m.end() - 1
        block_end = find_block_end(content, brace_pos)
        block = content[brace_pos:block_end + 1]

        desc_match = re.search(r'description\s+"([^"]*(?:""[^"]*)*)"', block[:1000])
        desc = desc_match.group(1).replace('""', '"')[:200] if desc_match else f"Notification: {notif_name}"

        leaves = extract_leaves(block)

        notifications.append({
            "name": notif_name,
            "description": desc,
            "leaves": leaves,
        })

    return notifications


def build_leaf_schema(leaves):
    """Build a JSON Schema object from a list of leaves."""
    properties = {}
    for leaf in leaves:
        prop = dict(leaf["schema"])
        if leaf.get("description"):
            prop["description"] = leaf["description"]
        prop["example"] = get_example_value(leaf["name"], prop["type"])
        if leaf["is_list"]:
            prop = {"type": "array", "items": prop}
        properties[leaf["name"]] = prop
    return {"type": "object", "properties": properties} if properties else {"type": "object"}


def generate_config_spec(module_name, nodes, target_folder):
    """Generate an OpenAPI spec for the config data nodes of a module."""
    paths = {}
    schemas = {}
    tags_set = set()
    path_count = 0
    op_count = 0

    prefix = module_name

    for node in nodes:
        node_name = node["name"]
        tag = node_name
        tags_set.add(tag)
        schema_key = f"{module_name}_{node_name}".replace("-", "_")
        schema = build_leaf_schema(node["leaves"])
        schemas[schema_key] = schema

        base_path = f"/data/{prefix}:{node_name}"

        if node["config_false"]:
            # Read-only: GET only
            paths[base_path] = {
                "get": {
                    "summary": f"Get {node_name} (read-only)",
                    "operationId": f"get-{prefix}:{node_name}",
                    "tags": [tag],
                    "parameters": [
                        {"$ref": "#/components/parameters/accept"},
                        {"$ref": "#/components/parameters/depth"},
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/yang-data+json": {
                                    "schema": {"$ref": f"#/components/schemas/{schema_key}"}
                                }
                            }
                        }
                    }
                }
            }
            path_count += 1
            op_count += 1
        else:
            # Read-write: GET + PUT + PATCH + DELETE for containers
            path_ops = {}

            # GET
            path_ops["get"] = {
                "summary": f"Get {node_name}",
                "operationId": f"get-{prefix}:{node_name}",
                "tags": [tag],
                "parameters": [
                    {"$ref": "#/components/parameters/accept"},
                    {"$ref": "#/components/parameters/depth"},
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/yang-data+json": {
                                "schema": {"$ref": f"#/components/schemas/{schema_key}"}
                            }
                        }
                    }
                }
            }
            op_count += 1

            # PUT
            path_ops["put"] = {
                "summary": f"Create or replace {node_name}",
                "operationId": f"put-{prefix}:{node_name}",
                "tags": [tag],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/yang-data+json": {
                            "schema": {"$ref": f"#/components/schemas/{schema_key}"}
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Created"},
                    "204": {"description": "Updated (no content)"},
                }
            }
            op_count += 1

            # PATCH
            path_ops["patch"] = {
                "summary": f"Update {node_name}",
                "operationId": f"patch-{prefix}:{node_name}",
                "tags": [tag],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/yang-data+json": {
                            "schema": {"$ref": f"#/components/schemas/{schema_key}"}
                        }
                    }
                },
                "responses": {
                    "204": {"description": "Updated (no content)"},
                }
            }
            op_count += 1

            # DELETE
            path_ops["delete"] = {
                "summary": f"Delete {node_name}",
                "operationId": f"delete-{prefix}:{node_name}",
                "tags": [tag],
                "responses": {
                    "204": {"description": "Deleted (no content)"},
                }
            }
            op_count += 1

            paths[base_path] = path_ops
            path_count += 1

            # For lists, add item-level path with key
            if node["type"] == "list" and node.get("key"):
                keys = node["key"].split()
                key_params = "=" + ",".join(f"{{{k}}}" for k in keys)
                item_path = f"{base_path}{key_params}"

                key_parameters = []
                for k in keys:
                    key_parameters.append({
                        "name": k,
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    })

                item_ops = {}
                item_ops["get"] = {
                    "summary": f"Get {node_name} by key",
                    "operationId": f"get-{prefix}:{node_name}-item",
                    "tags": [tag],
                    "parameters": key_parameters + [
                        {"$ref": "#/components/parameters/accept"},
                        {"$ref": "#/components/parameters/depth"},
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/yang-data+json": {
                                    "schema": {"$ref": f"#/components/schemas/{schema_key}"}
                                }
                            }
                        }
                    }
                }
                item_ops["put"] = {
                    "summary": f"Create or replace {node_name} item",
                    "operationId": f"put-{prefix}:{node_name}-item",
                    "tags": [tag],
                    "parameters": key_parameters,
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/yang-data+json": {
                                "schema": {"$ref": f"#/components/schemas/{schema_key}"}
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Created"},
                        "204": {"description": "Updated (no content)"},
                    }
                }
                item_ops["delete"] = {
                    "summary": f"Delete {node_name} item",
                    "operationId": f"delete-{prefix}:{node_name}-item",
                    "tags": [tag],
                    "parameters": key_parameters,
                    "responses": {
                        "204": {"description": "Deleted (no content)"},
                    }
                }

                paths[item_path] = item_ops
                path_count += 1
                op_count += 3

    if not paths:
        return None

    # Get module description from YANG
    yang_file = YANG_DIR / f"{module_name}.yang"
    module_desc = ""
    if yang_file.exists():
        try:
            content = yang_file.read_text(encoding='utf-8', errors='ignore')
            desc_match = re.search(r'description\s+"([^"]*(?:""[^"]*)*)"', content[:3000])
            if desc_match:
                module_desc = desc_match.group(1).replace('""', '"')[:300]
        except (OSError, UnicodeDecodeError):
            pass

    tree_url = f"{GH_PAGES}/yang-trees/{module_name}.html"
    yang_url = f"https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17181/{module_name}.yang"

    tags = [{"name": t, "description": f"{t} operations"} for t in sorted(tags_set)]

    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": f"Cisco IOS-XE - {module_name}",
            "description": f"Configuration data from `{module_name}` module.\n\n"
                          f"**Note:** This module also contains {'RPCs' if '-rpc' in module_name else 'notifications'} "
                          f"documented in the {'RPC' if '-rpc' in module_name else 'Events'} model.\n\n"
                          f"**Paths:** {path_count} | **Operations:** {op_count}\n\n"
                          f"**YANG Source:** [{module_name}.yang]({yang_url})\n\n"
                          f"**YANG Tree:** [View tree structure]({tree_url})",
            "version": "17.18.1",
            "contact": {
                "name": "Cisco IOS-XE RESTCONF API",
                "url": "https://developer.cisco.com/iosxe/"
            },
            "x-yang-module": module_name,
            "x-model-type": "other",
        },
        "servers": [
            {
                "url": "https://{device}:{port}/restconf",
                "description": "IOS-XE Device RESTCONF API",
                "variables": {
                    "device": {"default": "devnetsandboxiosxec9k.cisco.com"},
                    "port": {"default": "443"},
                }
            }
        ],
        "paths": paths,
        "components": {
            "schemas": schemas,
            "securitySchemes": {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                    "description": "HTTP Basic Authentication"
                }
            },
            "parameters": {
                "accept": {
                    "name": "Accept",
                    "in": "header",
                    "schema": {"type": "string", "default": "application/yang-data+json"},
                },
                "depth": {
                    "name": "depth",
                    "in": "query",
                    "schema": {"type": "integer", "default": 65535},
                    "description": "Limit subtree depth in response",
                }
            }
        },
        "security": [{"basicAuth": []}],
        "tags": tags,
    }

    return spec, path_count, op_count


def generate_events_spec(module_name, notifications):
    """Generate an OpenAPI events spec for notifications."""
    paths = {}
    schemas = {}
    tags_set = set()

    yang_url = f"https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17181/{module_name}.yang"
    tree_url = f"{GH_PAGES}/yang-trees/{module_name}.html"

    for notif in notifications:
        tag = f"{notif['name']}-events"
        tags_set.add(tag)
        schema_key = notif["name"].replace("-", "_")

        # Build notification schema
        props = {}
        for leaf in notif["leaves"]:
            prop = dict(leaf["schema"])
            if leaf.get("description"):
                prop["description"] = leaf["description"]
            prop["example"] = get_example_value(leaf["name"], prop["type"])
            if leaf["is_list"]:
                prop = {"type": "array", "items": prop}
            props[leaf["name"]] = prop

        schemas[notif["name"]] = {
            "type": "object",
            "description": notif["description"],
            "properties": props if props else {"event-data": {"type": "object"}},
        }

        # Error schema (reuse)
        schemas["restconf-error"] = {
            "type": "object",
            "properties": {
                "errors": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "error-type": {"type": "string"},
                                    "error-tag": {"type": "string"},
                                    "error-message": {"type": "string"},
                                }
                            }
                        }
                    }
                }
            }
        }

        event_path = f"/ws/event-streams/{module_name}/{notif['name']}"
        paths[event_path] = {
            "get": {
                "summary": f"Subscribe to {notif['name']} events",
                "description": notif["description"],
                "tags": [tag],
                "responses": {
                    "101": {
                        "description": "Switching Protocols - WebSocket connection established",
                        "content": {
                            "application/yang-data+json": {
                                "schema": {"$ref": f"#/components/schemas/{notif['name']}"},
                                "example": {
                                    "notification": {
                                        "eventTime": "2026-01-01T00:00:00Z",
                                        f"{module_name}:{notif['name']}": {
                                            leaf["name"]: get_example_value(leaf["name"], leaf["schema"]["type"])
                                            for leaf in notif["leaves"][:5]
                                        } if notif["leaves"] else {"event-data": "value"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/yang-data+json": {
                                "schema": {"$ref": "#/components/schemas/restconf-error"}
                            }
                        }
                    }
                }
            }
        }

    if not paths:
        return None

    tags = [{"name": t, "description": f"Event notification subscriptions"} for t in sorted(tags_set)]

    spec = {
        "openapi": "3.0.1",
        "info": {
            "title": f"{module_name} Event Notifications",
            "version": "17.18.1",
            "description": f"Event notifications from `{module_name}` module.\n\n"
                          f"**Event Notifications Module** - Used for model-driven telemetry.\n\n"
                          f"**Protocol**: RFC 8639 (Subscription to YANG Notifications)\n\n"
                          f"**YANG Model:** [{module_name}.yang]({yang_url})\n\n"
                          f"**YANG Tree:** [View {module_name} structure]({tree_url})",
            "x-yang-module": module_name,
            "x-model-type": "events",
        },
        "servers": [
            {
                "url": "https://{device}/restconf",
                "variables": {
                    "device": {"default": "devnetsandboxiosxec9k.cisco.com"}
                }
            }
        ],
        "paths": paths,
        "components": {
            "schemas": schemas,
            "securitySchemes": {
                "basicAuth": {"type": "http", "scheme": "basic"}
            }
        },
        "security": [{"basicAuth": []}],
        "tags": tags,
    }

    return spec, len(paths), len(paths)


def update_manifest(folder_path, api_dir="api"):
    """Regenerate manifest.json for a swagger model folder."""
    api_path = folder_path / api_dir
    if not api_path.exists():
        return

    specs = sorted(f.stem for f in api_path.glob("*.json") if f.stem != "manifest")
    total_paths = 0
    total_ops = 0

    for spec_name in specs:
        spec_file = api_path / f"{spec_name}.json"
        try:
            data = json.loads(spec_file.read_text(encoding='utf-8'))
            paths = data.get("paths", {})
            total_paths += len(paths)
            for path_ops in paths.values():
                total_ops += len([k for k in path_ops if k in ('get', 'put', 'post', 'patch', 'delete')])
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            pass

    manifest = {
        "total_modules": len(specs),
        "total_paths": total_paths,
        "total_operations": total_ops,
        "modules": specs,
    }

    manifest_file = api_path / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f"  Updated manifest: {api_dir}/ -> {len(specs)} modules, {total_paths} paths, {total_ops} ops")


def main():
    print("=" * 60)
    print("Dual-Role Config Spec Generator")
    print("=" * 60)

    config_generated = 0
    events_generated = 0
    config_skipped = 0
    events_skipped = 0
    affected_folders = set()

    # 1. Generate missing config specs
    print(f"\n--- Generating {len(MISSING_CONFIG_SPECS)} config specs ---")
    for module_name, target_folder in sorted(MISSING_CONFIG_SPECS.items()):
        yang_file = YANG_DIR / f"{module_name}.yang"
        if not yang_file.exists():
            print(f"  SKIP {module_name}: no .yang file")
            config_skipped += 1
            continue

        content = yang_file.read_text(encoding='utf-8', errors='ignore')
        nodes = extract_top_level_nodes(content, module_name)

        if not nodes:
            print(f"  SKIP {module_name}: no top-level containers/lists found")
            config_skipped += 1
            continue

        result = generate_config_spec(module_name, nodes, target_folder)
        if result is None:
            print(f"  SKIP {module_name}: no RESTCONF paths generated")
            config_skipped += 1
            continue

        spec, path_count, op_count = result

        # Write to api/
        output_dir = BASE / target_folder / "api"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{module_name}.json"
        output_file.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding='utf-8')
        affected_folders.add(target_folder)
        config_generated += 1
        print(f"  Generated {target_folder}/api/{module_name}.json ({path_count} paths, {op_count} ops, {len(nodes)} nodes)")

    # 2. Generate missing events specs
    print(f"\n--- Generating {len(MISSING_EVENTS_SPECS)} events specs ---")
    for module_name, target_folder in sorted(MISSING_EVENTS_SPECS.items()):
        yang_file = YANG_DIR / f"{module_name}.yang"
        if not yang_file.exists():
            print(f"  SKIP {module_name}: no .yang file")
            events_skipped += 1
            continue

        # Check if events spec already exists
        existing_v2 = BASE / target_folder / "api" / f"{module_name}.json"
        existing_v1 = BASE / target_folder / "api" / f"{module_name}.json"
        if existing_v2.exists() or existing_v1.exists():
            print(f"  SKIP {module_name}: events spec already exists")
            events_skipped += 1
            continue

        content = yang_file.read_text(encoding='utf-8', errors='ignore')
        notifications = extract_notifications(content, module_name)

        if not notifications:
            print(f"  SKIP {module_name}: no notifications found")
            events_skipped += 1
            continue

        result = generate_events_spec(module_name, notifications)
        if result is None:
            print(f"  SKIP {module_name}: no event paths generated")
            events_skipped += 1
            continue

        spec, path_count, op_count = result

        # Write to api/ (v1, matching existing events pattern)
        output_dir = BASE / target_folder / "api"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{module_name}.json"
        output_file.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding='utf-8')
        affected_folders.add(target_folder)
        events_generated += 1
        print(f"  Generated {target_folder}/api/{module_name}.json ({path_count} events, {len(notifications)} notifications)")

    # 3. Update manifests for affected folders
    print(f"\n--- Updating manifests ---")
    for folder in sorted(affected_folders):
        folder_path = BASE / folder
        if (folder_path / "api").exists():
            update_manifest(folder_path, "api")

    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"  Config specs generated: {config_generated}")
    print(f"  Config specs skipped:   {config_skipped}")
    print(f"  Events specs generated: {events_generated}")
    print(f"  Events specs skipped:   {events_skipped}")
    print(f"  Folders updated:        {sorted(affected_folders)}")


if __name__ == "__main__":
    main()
