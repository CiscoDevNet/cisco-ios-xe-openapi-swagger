#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specs from the resolved YANG tree HTML for Cisco-IOS-XE-native.
Parses the pre-rendered tree (which resolves all augmentations) to produce deep,
feature-level swagger specs with working RESTCONF paths and examples.

Strategy:
  - Parse indented tree text from the HTML into a structured tree
  - Generate one spec per top-level container (small/medium containers)
  - For mega containers (interface, ip, line): split by sub-features
  - Interface: feature-centric specs using GigabitEthernet as representative type
"""

import json
import re
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Tree parser: HTML -> structured tree nodes
# ---------------------------------------------------------------------------

class TreeNode:
    """Represents a node in the YANG tree."""
    __slots__ = ('name', 'raw_name', 'rw', 'node_type', 'yang_type',
                 'is_key', 'children', 'depth', 'description')

    def __init__(self, name: str, rw: str = 'rw', node_type: str = 'container',
                 yang_type: str = '', is_key: bool = False, depth: int = 0):
        self.name = name              # clean name (no ? ! *)
        self.raw_name = name          # as-is from tree
        self.rw = rw                  # rw | ro
        self.node_type = node_type    # container | list | leaf | leaf-list | choice | case
        self.yang_type = yang_type    # string, uint32, etc.
        self.is_key = is_key
        self.children: List['TreeNode'] = []
        self.depth = depth
        self.description = ''

    def find_child(self, name: str) -> Optional['TreeNode']:
        for c in self.children:
            if c.name == name:
                return c
        return None

    def descendant_count(self) -> int:
        count = 0
        for c in self.children:
            count += 1 + c.descendant_count()
        return count


def parse_yang_tree_html(html_path: str) -> TreeNode:
    """Parse the YANG tree HTML file and return the root 'native' node."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pre_matches = re.findall(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
    if len(pre_matches) < 2:
        raise ValueError("Could not find tree <pre> section in HTML")

    tree_text = pre_matches[1]
    tree_text = re.sub(r'<[^>]+>', '', tree_text)
    tree_text = tree_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

    lines = tree_text.split('\n')

    # Find the native container line
    native_idx = None
    for i, line in enumerate(lines):
        if re.match(r'\s+\+--rw native\s*$', line):
            native_idx = i
            break

    if native_idx is None:
        raise ValueError("Could not find 'native' container in tree")

    root = TreeNode('native', 'rw', 'container', depth=0)

    # Parse children using indentation-based depth tracking
    # native line indent tells us the base; children are indented further
    # We use a column-position approach: find the column of the '+--' or 'o--'
    # marker for each line to determine parent-child relationships.

    node_stack: List[Tuple[int, TreeNode]] = [(0, root)]  # (column, node)

    for i in range(native_idx + 1, len(lines)):
        line = lines[i]
        if not line.strip():
            continue

        # Handle case nodes: +--:(case-name)
        case_match = re.search(r'[+o]--:\((\S+)\)', line)
        if case_match:
            col = case_match.start()
            name = case_match.group(1)
            node = TreeNode(name, 'rw', 'case', depth=0)
            node.raw_name = f":({name})"
            while len(node_stack) > 1 and node_stack[-1][0] >= col:
                node_stack.pop()
            parent_col, parent_node = node_stack[-1]
            parent_node.children.append(node)
            node.depth = parent_node.depth + 1
            node_stack.append((col, node))
            continue

        # Find the [+o]-- marker position first, then extract rw/ro and name
        marker_match = re.search(r'[+o]-+(rw|ro|x)\s+(\S+)(.*)', line)
        if not marker_match:
            continue

        col = marker_match.start()
        rw = marker_match.group(1)
        raw_name = marker_match.group(2)
        rest = marker_match.group(3).strip()

        # If col <= native's children base column (5 for this tree), it's a child of native
        # Each depth level adds 3 columns (for '|  ' or '   ')

        # Clean up name
        name = raw_name.rstrip('?').rstrip('!').rstrip('*')
        has_key = bool(re.search(r'\[(\S+)\]', rest))
        is_list = raw_name.rstrip('?').rstrip('!').endswith('*') and has_key

        # Determine node type and yang type
        if is_list:
            node_type = 'list'
            yang_type = ''
        elif raw_name.startswith('(') and (raw_name.endswith(')') or raw_name.endswith(')?')):
            node_type = 'choice'
            name = raw_name.strip('()?')
            yang_type = ''
        elif rest and not rest.startswith('[') and not rest.startswith('{'):
            # Has a type annotation -> it's a leaf (or leaf-list if name ends with *)
            yang_type = rest.split()[0] if rest.split() else 'string'
            if raw_name.rstrip('?').rstrip('!').endswith('*') and not has_key:
                node_type = 'leaf-list'
            else:
                node_type = 'leaf'
        else:
            node_type = 'container'
            yang_type = ''

        node = TreeNode(name, rw, node_type, yang_type, depth=0)
        node.raw_name = raw_name

        # Find parent: pop stack until we find a node whose column is less than ours
        while len(node_stack) > 1 and node_stack[-1][0] >= col:
            node_stack.pop()

        parent_col, parent_node = node_stack[-1]
        parent_node.children.append(node)
        node.depth = parent_node.depth + 1

        # Push this node for potential children
        node_stack.append((col, node))

    return root


# ---------------------------------------------------------------------------
# Example data generator
# ---------------------------------------------------------------------------

EXAMPLE_VALUES = {
    'hostname': 'DC1-CORE-SW01',
    'name': 'GigabitEthernet1/0/1',
    'description': 'UPLINK_TO_CORE',
    'address': '10.10.10.1',
    'mask': '255.255.255.0',
    'mtu': 1500,
    'bandwidth': 1000000,
    'delay': 100,
    'cost': 10,
    'priority': 100,
    'vlan': 100,
    'community': 'RO_SNMP_v2c',
    'forwarding': 'PROD-VRF',
    'metric': 10,
    'weight': 100,
    'timeout': 300,
    'threshold': 80,
    'id': 1,
    'number': 1,
    'area': '0.0.0.0',
    'process-id': 1,
    'as-number': 65001,
}

def example_for_type(yang_type: str, name: str = '') -> Any:
    """Generate a reasonable example value from YANG type and node name."""
    name_lower = name.lower().replace('-', '').replace('_', '')

    # Check name-based overrides first (demo-polished values)
    for key, val in EXAMPLE_VALUES.items():
        if key.replace('-', '') in name_lower:
            return val

    # YANG-derived default or first enum value (covers ~5500 leaves)
    try:
        from yang_value_index import lookup_example
        v = lookup_example(name)
        if v is not None:
            return v
    except Exception:
        pass

    # Type-based defaults
    type_map = {
        'string': 'example',
        'uint8': 1, 'uint16': 1, 'uint32': 1, 'uint64': 1,
        'int8': 1, 'int16': 1, 'int32': 1, 'int64': 1,
        'boolean': True,
        'empty': None,  # presence
        'enumeration': 'default',
        'union': 'auto',
        'decimal64': 1.0,
        'binary': 'QmFzZTY0',
        'bits': '',
    }

    # Handle qualified types like ios-types:exp-acl-type
    base = yang_type.split(':')[-1] if ':' in yang_type else yang_type
    return type_map.get(base, 'example')


def generate_example(node: TreeNode, max_depth: int = 4, current_depth: int = 0) -> Any:
    """Recursively generate example JSON for a tree node."""
    if current_depth > max_depth:
        return {}

    if node.node_type == 'leaf':
        return example_for_type(node.yang_type, node.name)

    if node.node_type == 'leaf-list':
        val = example_for_type(node.yang_type, node.name)
        return [val]

    if node.node_type in ('choice', 'case'):
        # For choice: use first case's children
        if node.children:
            return generate_example(node.children[0], max_depth, current_depth)
        return {}

    # Container or list
    obj = {}
    for child in node.children:
        if child.node_type in ('choice', 'case'):
            # Flatten first case into parent
            if child.children:
                first_case = child.children[0] if child.node_type == 'choice' else child
                for gc in first_case.children:
                    obj[gc.name] = generate_example(gc, max_depth, current_depth + 1)
        elif child.node_type == 'leaf':
            obj[child.name] = example_for_type(child.yang_type, child.name)
        elif child.node_type == 'leaf-list':
            val = example_for_type(child.yang_type, child.name)
            obj[child.name] = [val]
        else:
            child_ex = generate_example(child, max_depth, current_depth + 1)
            if child.node_type == 'list':
                obj[child.name] = [child_ex] if isinstance(child_ex, dict) else child_ex
            else:
                obj[child.name] = child_ex

    return obj


# ---------------------------------------------------------------------------
# OpenAPI spec builder
# ---------------------------------------------------------------------------

def build_schema_from_node(node: TreeNode, max_depth: int = 6, depth: int = 0) -> Dict[str, Any]:
    """Build an OpenAPI schema object from a tree node."""
    if depth > max_depth:
        return {'type': 'object'}

    if node.node_type == 'leaf':
        return yang_type_to_schema(node.yang_type, node.name)

    if node.node_type == 'leaf-list':
        return {'type': 'array', 'items': yang_type_to_schema(node.yang_type, node.name)}

    # Container or list
    properties = {}
    required = []
    for child in node.children:
        if child.node_type in ('choice', 'case'):
            # Flatten first case
            target = child.children[0] if child.node_type == 'choice' and child.children else child
            for gc in (target.children if target else []):
                properties[gc.name] = build_schema_from_node(gc, max_depth, depth + 1)
        else:
            properties[child.name] = build_schema_from_node(child, max_depth, depth + 1)
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


def yang_type_to_schema(yang_type: str, name: str = '') -> Dict[str, Any]:
    """Convert a YANG type string to OpenAPI schema."""
    base = yang_type.split(':')[-1] if ':' in yang_type else yang_type

    mapping = {
        'string': {'type': 'string'},
        'uint8': {'type': 'integer', 'minimum': 0, 'maximum': 255},
        'uint16': {'type': 'integer', 'minimum': 0, 'maximum': 65535},
        'uint32': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
        'uint64': {'type': 'integer', 'minimum': 0},
        'int8': {'type': 'integer', 'minimum': -128, 'maximum': 127},
        'int16': {'type': 'integer', 'minimum': -32768, 'maximum': 32767},
        'int32': {'type': 'integer'},
        'int64': {'type': 'integer'},
        'boolean': {'type': 'boolean'},
        'empty': {'type': 'boolean', 'description': 'Presence flag'},
        'enumeration': {'type': 'string'},
        'union': {'type': 'string', 'description': 'Union type — accepts multiple formats'},
        'decimal64': {'type': 'number'},
        'binary': {'type': 'string', 'format': 'byte'},
        'bits': {'type': 'string'},
    }

    return mapping.get(base, {'type': 'string'}).copy()


# Standard components shared across all specs
COMMON_COMPONENTS = {
    'securitySchemes': {
        'basicAuth': {
            'type': 'http',
            'scheme': 'basic',
            'description': 'RESTCONF basic authentication (RFC 8040)'
        }
    },
    'schemas': {
        'restconf-error': {
            'type': 'object',
            'properties': {
                'errors': {
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'error-type': {'type': 'string'},
                                    'error-tag': {'type': 'string'},
                                    'error-message': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'parameters': {
        'content-type': {
            'name': 'Content-Type',
            'in': 'header',
            'schema': {
                'type': 'string',
                'default': 'application/yang-data+json',
                'enum': ['application/yang-data+json', 'application/yang-data+xml']
            }
        },
        'accept': {
            'name': 'Accept',
            'in': 'header',
            'required': False,
            'schema': {
                'type': 'string',
                'default': 'application/yang-data+json',
                'enum': ['application/yang-data+json', 'application/yang-data+xml']
            }
        },
        'depth': {
            'name': 'depth',
            'in': 'query',
            'required': False,
            'description': 'Limit response depth (RFC 8040 §4.8.2)',
            'schema': {'type': 'string', 'default': 'unbounded'}
        }
    }
}


def make_path_operations(restconf_path: str, node: TreeNode, tag: str,
                         module_prefix: str = 'Cisco-IOS-XE-native',
                         schema_depth: int = 4) -> Dict[str, Any]:
    """Create GET/PUT/PATCH/DELETE operations for a RESTCONF path."""
    inner_schema = build_schema_from_node(node, max_depth=schema_depth)
    example = generate_example(node, max_depth=min(schema_depth, 3))
    op_base = node.name.lower().replace(' ', '-')

    wrapper_key = f"{module_prefix}:{node.name}"
    wrapped_example = {wrapper_key: [example] if node.node_type == 'list' else example}
    # RESTCONF wire format wraps the resource in {"module:node": value}; the
    # schema must mirror that wrapping or Swagger UI's "Try it out" body
    # renders as an unusable bare scalar instead of a valid RESTCONF payload.
    schema = {'type': 'object', 'properties': {wrapper_key: inner_schema}}

    ops = {}

    # GET
    ops['get'] = {
        'summary': f"Get {node.name} configuration",
        'operationId': f"get-{op_base}",
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
                        'example': wrapped_example
                    }
                }
            },
            '401': {'description': 'Unauthorized'},
            '404': {'description': 'Resource not found'}
        }
    }

    if node.rw == 'rw':
        # PUT
        ops['put'] = {
            'summary': f"Replace {node.name} configuration",
            'operationId': f"put-{op_base}",
            'tags': [tag],
            'requestBody': {
                'required': True,
                'content': {
                    'application/yang-data+json': {
                        'schema': schema,
                        'example': wrapped_example
                    }
                }
            },
            'responses': {
                '201': {'description': 'Created'},
                '204': {'description': 'Updated successfully'},
                '400': {'description': 'Invalid input'}
            }
        }

        # PATCH
        ops['patch'] = {
            'summary': f"Update {node.name} configuration",
            'operationId': f"patch-{op_base}",
            'tags': [tag],
            'requestBody': {
                'required': True,
                'content': {
                    'application/yang-data+json': {
                        'schema': schema,
                        'example': wrapped_example
                    }
                }
            },
            'responses': {
                '204': {'description': 'Updated successfully'},
                '400': {'description': 'Invalid input'}
            }
        }

        # DELETE
        ops['delete'] = {
            'summary': f"Delete {node.name} configuration",
            'operationId': f"delete-{op_base}",
            'tags': [tag],
            'responses': {
                '204': {'description': 'Deleted successfully'},
                '404': {'description': 'Resource not found'}
            }
        }

    return ops


def create_spec(title: str, description: str, tag: str,
                paths: Dict[str, Any], version: str = '17.18.1') -> Dict[str, Any]:
    """Create a complete OpenAPI 3.0 spec."""
    return {
        'openapi': '3.0.0',
        'info': {
            'title': title,
            'description': description,
            'version': version,
            'contact': {
                'name': 'Cisco IOS-XE RESTCONF API',
                'url': 'https://developer.cisco.com/iosxe/'
            },
            'x-yang-module': 'Cisco-IOS-XE-native',
            'x-model-type': 'native'
        },
        'servers': [{
            'url': 'https://{device}:{port}/restconf',
            'description': 'IOS-XE Device RESTCONF API',
            'variables': {
                'device': {
                    'default': 'devnetsandboxiosxec9k.cisco.com',
                    'description': 'Device IP or hostname'
                },
                'port': {
                    'default': '443',
                    'description': 'HTTPS port'
                }
            }
        }],
        'paths': paths,
        'components': COMMON_COMPONENTS,
        'security': [{'basicAuth': []}]
    }


# ---------------------------------------------------------------------------
# Deep path generator: walks tree and emits RESTCONF paths at every level
# ---------------------------------------------------------------------------

def collect_deep_paths(node: TreeNode, base_restconf: str, max_depth: int = 5,
                       current_depth: int = 0) -> List[Tuple[str, TreeNode]]:
    """Collect RESTCONF paths for a node and its children up to max_depth."""
    paths = [(base_restconf, node)]

    if current_depth >= max_depth:
        return paths

    for child in node.children:
        if child.node_type in ('choice', 'case'):
            # Flatten: treat first case's children as direct children
            target = child
            if child.node_type == 'choice' and child.children:
                target = child.children[0]
            for gc in target.children:
                child_path = f"{base_restconf}/{gc.name}"
                if gc.node_type == 'list':
                    paths.append((child_path, gc))
                    # Also add keyed instance path
                    key_child = gc.find_child('name') or gc.find_child('id')
                    if key_child:
                        key_name = key_child.name
                        keyed_path = f"{child_path}={{{key_name}}}"
                        paths.append((keyed_path, gc))
                    paths.extend(collect_deep_paths(gc, child_path, max_depth, current_depth + 1))
                elif gc.node_type == 'container':
                    paths.extend(collect_deep_paths(gc, child_path, max_depth, current_depth + 1))
                else:
                    paths.append((child_path, gc))
        elif child.node_type == 'list':
            child_path = f"{base_restconf}/{child.name}"
            paths.append((child_path, child))
            key_child = child.find_child('name') or child.find_child('id')
            if key_child:
                keyed_path = f"{child_path}={{{key_child.name}}}"
                paths.append((keyed_path, child))
            paths.extend(collect_deep_paths(child, child_path, max_depth, current_depth + 1))
        elif child.node_type == 'container':
            child_path = f"{base_restconf}/{child.name}"
            paths.extend(collect_deep_paths(child, child_path, max_depth, current_depth + 1))
        elif child.node_type in ('leaf', 'leaf-list'):
            child_path = f"{base_restconf}/{child.name}"
            paths.append((child_path, child))

    return paths


# ---------------------------------------------------------------------------
# Interface mega-container handler: feature-centric specs
# ---------------------------------------------------------------------------

# Group interface features into functional bundles
INTERFACE_FEATURE_GROUPS = {
    'intf-ip-addressing': {
        'title': 'Interface — IP Addressing & VRF',
        'features': ['ip', 'ipv6', '(vrf-choice)'],
        'desc': 'IP/IPv6 addressing, VRF assignment, DHCP, helpers, and related L3 config per interface.'
    },
    'intf-switching': {
        'title': 'Interface — Switchport & L2',
        'features': ['switchport', 'switchport-conf', 'switchport-config', 'switchport-wrapper',
                     'storm-control', 'l2protocol-tunnel', 'l2protocol', 'encapsulation'],
        'desc': 'Layer 2 switchport mode, VLAN assignment, trunk config, storm control, and L2 protocol tunneling.'
    },
    'intf-routing': {
        'title': 'Interface — Routing Features',
        'features': ['isis', 'bfd', 'clns', 'mpls', 'standby'],
        'desc': 'Per-interface routing protocol settings: IS-IS, BFD, CLNS, MPLS, HSRP/VRRP standby.'
    },
    'intf-security': {
        'title': 'Interface — Security & Access Control',
        'features': ['access-session', 'trust', 'macsec-enable', 'macsec-option',
                     'dot1x', 'mab', 'identity'],
        'desc': 'Interface security: 802.1X, MAB, MACsec, trust boundaries, access sessions.'
    },
    'intf-qos': {
        'title': 'Interface — QoS & Queuing',
        'features': ['interface_qos', 'fair-queue', 'fair-queue-conf', 'priority-queue',
                     'rcv-queue', 'max-reserved-bandwidth'],
        'desc': 'Quality of Service: service-policy, queuing, bandwidth reservation per interface.'
    },
    'intf-physical': {
        'title': 'Interface — Physical & Basic',
        'features': ['name', 'description', 'shutdown', 'mtu', 'bandwidth', 'delay',
                     'mac-address', 'media-type', 'port-type', 'flowcontrol', 'mdix',
                     'dampening', 'load-interval', 'keepalive-config', 'if-state',
                     'stackwise-virtual', 'uplink', 'export-name'],
        'desc': 'Basic interface settings: shutdown, MTU, bandwidth, speed, duplex, description, MAC address.'
    },
    'intf-services': {
        'title': 'Interface — Network Services',
        'features': ['arp', 'logging', 'domain', 'mop', 'source', 'subscriber',
                     'backup', 'redundancy', 'service-insertion', 'peer', 'pm-path',
                     'srlg', 'punt-control', 'cemoudp', 'cws-tunnel', 'hold-queue',
                     'history'],
        'desc': 'Per-interface services: ARP, logging, domain, MOP, backup, redundancy.'
    },
}

# Interface types grouped by category for the compatibility matrix
INTERFACE_TYPE_GROUPS = {
    'Physical Ethernet': [
        'GigabitEthernet', 'TenGigabitEthernet', 'TwentyFiveGigE',
        'FortyGigabitEthernet', 'FiftyGigabitEthernet', 'HundredGigE',
        'TwoHundredGigE', 'FourHundredGigE', 'FiveGigabitEthernet',
        'TwoGigabitEthernet', 'AppGigabitEthernet', 'FastEthernet', 'Ethernet'
    ],
    'Virtual/Logical': [
        'Loopback', 'Tunnel', 'Virtual-Template', 'VirtualPortGroup',
        'Virtual-PPP', 'nve', 'Vif'
    ],
    'VLAN/Aggregation': ['Vlan', 'BDI', 'BD-VIF', 'Port-channel'],
    'WAN/Legacy': ['Serial', 'Dialer', 'Cellular', 'Multilink', 'MFR', 'Async'],
}


def generate_interface_specs(intf_node: TreeNode, output_dir: Path) -> List[str]:
    """Generate feature-centric specs for the interface mega container.
    Returns list of generated filenames (without .json)."""

    generated = []

    # Find GigabitEthernet as reference type
    gig_node = intf_node.find_child('GigabitEthernet')
    if not gig_node:
        print("  WARNING: GigabitEthernet not found in interface container")
        return generated

    # Build a lookup of all GigabitEthernet child features
    gig_features = {c.name: c for c in gig_node.children}

    # Also collect all interface type names for the compatibility notes
    all_intf_types = [c.name for c in intf_node.children if c.node_type == 'list']

    for group_key, group_info in INTERFACE_FEATURE_GROUPS.items():
        paths_dict = {}
        tag = group_key

        # Build description with type compatibility
        type_note = (
            f"\n\n**Representative type:** GigabitEthernet (paths work identically for "
            f"TenGigabitEthernet, HundredGigE, Loopback, Vlan, Tunnel, etc. — "
            f"just substitute the type name in the URL).\n\n"
            f"**All {len(all_intf_types)} interface types:** {', '.join(sorted(all_intf_types)[:20])}"
            f"{'...' if len(all_intf_types) > 20 else ''}"
        )

        desc = group_info['desc'] + type_note

        base_path = '/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={name}'

        for feat_name in group_info['features']:
            feat_node = gig_features.get(feat_name)
            if not feat_node:
                continue

            if feat_node.node_type == 'leaf':
                restconf = f"{base_path}/{feat_name}"
                paths_dict[restconf] = make_path_operations(restconf, feat_node, tag)
            elif feat_node.node_type in ('container', 'list'):
                # Collect deep paths within this feature
                deep = collect_deep_paths(feat_node, f"{base_path}/{feat_name}",
                                          max_depth=3, current_depth=0)
                for rpath, rnode in deep:
                    if rpath not in paths_dict:
                        paths_dict[rpath] = make_path_operations(rpath, rnode, tag)

        if not paths_dict:
            continue

        title = f"Cisco IOS-XE Native Config - {group_info['title']}"
        spec = create_spec(title, desc, tag, paths_dict)

        fname = f"native-{group_key}"
        out_path = output_dir / f"{fname}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)

        print(f"  {fname}: {len(paths_dict)} paths")
        generated.append(fname)

    # Also generate an interface-types overview spec (list endpoints for all types)
    paths_dict = {}
    tag = 'interface-types'
    for child in intf_node.children:
        if child.node_type != 'list':
            continue
        restconf = f"/data/Cisco-IOS-XE-native:native/interface/{child.name}"
        paths_dict[restconf] = make_path_operations(restconf, child, tag, schema_depth=0)

    if paths_dict:
        desc = (
            f"All {len(paths_dict)} interface types in the Cisco-IOS-XE-native model.\n\n"
            "Each type is a YANG list keyed by `name`. "
            "Features are nearly identical across types — see the feature-specific specs "
            "(IP Addressing, Switchport, QoS, etc.) for deep paths using GigabitEthernet as representative.\n\n"
            "**Type categories:**\n"
        )
        for cat, types in INTERFACE_TYPE_GROUPS.items():
            desc += f"- **{cat}:** {', '.join(types)}\n"

        title = "Cisco IOS-XE Native Config - Interface Types Overview"
        spec = create_spec(title, desc, tag, paths_dict)
        fname = "native-intf-types"
        out_path = output_dir / f"{fname}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)
        print(f"  {fname}: {len(paths_dict)} types")
        generated.append(fname)

    return generated


# ---------------------------------------------------------------------------
# IP mega-container handler
# ---------------------------------------------------------------------------

IP_FEATURE_GROUPS = {
    'ip-routing': {
        'title': 'IP — Routing & Forwarding',
        'features': ['route', 'routing', 'cef', 'forward-protocol', 'source-route',
                     'default-gateway', 'default-network'],
        'desc': 'Static routing, CEF, forwarding, default gateway.'
    },
    'ip-acl': {
        'title': 'IP — Access Lists',
        'features': ['access-list', 'prefix-list', 'community-list', 'extcommunity-list',
                     'as-path'],
        'desc': 'IP access control lists (standard, extended, named), prefix-lists, community-lists.'
    },
    'ip-services': {
        'title': 'IP — Services',
        'features': ['dhcp', 'dns', 'domain', 'host', 'http', 'ftp', 'tftp', 'ssh', 'scp',
                     'finger', 'rcmd', 'tcp', 'name-server', 'domain-name',
                     'domain-lookup', 'gratuitous-arps-conf', 'sla'],
        'desc': 'IP services: DHCP, DNS, HTTP server, SSH, SCP, TCP tuning, IP SLA.'
    },
    'ip-multicast': {
        'title': 'IP — Multicast',
        'features': ['multicast', 'igmp', 'pim', 'msdp', 'mroute'],
        'desc': 'IP multicast: PIM, IGMP, MSDP, static mroutes.'
    },
    'ip-nat': {
        'title': 'IP — NAT',
        'features': ['nat'],
        'desc': 'Network Address Translation: static, dynamic, PAT/overload, pools, access-list bindings.'
    },
}


def generate_ip_specs(ip_node: TreeNode, output_dir: Path) -> List[str]:
    """Generate feature-split specs for the ip mega container."""
    generated = []
    ip_children = {c.name: c for c in ip_node.children}
    assigned_features = set()

    for group_key, group_info in IP_FEATURE_GROUPS.items():
        paths_dict = {}
        tag = group_key

        for feat_name in group_info['features']:
            feat_node = ip_children.get(feat_name)
            if not feat_node:
                continue
            assigned_features.add(feat_name)

            base = f"/data/Cisco-IOS-XE-native:native/ip/{feat_name}"
            deep = collect_deep_paths(feat_node, base, max_depth=3, current_depth=0)
            for rpath, rnode in deep:
                if rpath not in paths_dict:
                    paths_dict[rpath] = make_path_operations(rpath, rnode, tag)

        if not paths_dict:
            continue

        title = f"Cisco IOS-XE Native Config - {group_info['title']}"
        spec = create_spec(title, group_info['desc'], tag, paths_dict)
        fname = f"native-{group_key}"
        out_path = output_dir / f"{fname}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)
        print(f"  {fname}: {len(paths_dict)} paths")
        generated.append(fname)

    # Remaining ip children go into ip-other
    remaining = {n: c for n, c in ip_children.items() if n not in assigned_features}
    if remaining:
        paths_dict = {}
        tag = 'ip-other'
        for feat_name, feat_node in remaining.items():
            base = f"/data/Cisco-IOS-XE-native:native/ip/{feat_name}"
            deep = collect_deep_paths(feat_node, base, max_depth=2, current_depth=0)
            for rpath, rnode in deep:
                if rpath not in paths_dict:
                    paths_dict[rpath] = make_path_operations(rpath, rnode, tag)

        if paths_dict:
            title = "Cisco IOS-XE Native Config - IP — Other Settings"
            desc = f"Remaining IP settings ({len(remaining)} features): {', '.join(sorted(remaining.keys()))}"
            spec = create_spec(title, desc, tag, paths_dict)
            fname = "native-ip-other"
            out_path = output_dir / f"{fname}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2)
            print(f"  {fname}: {len(paths_dict)} paths")
            generated.append(fname)

    return generated


# ---------------------------------------------------------------------------
# Standard container handler (medium/small containers)
# ---------------------------------------------------------------------------

def generate_container_spec(name: str, node: TreeNode, output_dir: Path,
                            max_depth: int = 4) -> Optional[str]:
    """Generate a single spec for a normal (non-mega) top-level container or leaf."""
    base = f"/data/Cisco-IOS-XE-native:native/{name}"
    tag = name

    if node.node_type == 'leaf':
        paths_dict = {base: make_path_operations(base, node, tag)}
    else:
        deep = collect_deep_paths(node, base, max_depth=max_depth, current_depth=0)
        paths_dict = {}
        for rpath, rnode in deep:
            if rpath not in paths_dict:
                paths_dict[rpath] = make_path_operations(rpath, rnode, tag)

    if not paths_dict:
        return None

    desc_count = node.descendant_count()
    title = f"Cisco IOS-XE Native Config - {name}"
    desc = (f"Configuration for `/native/{name}` container.\n\n"
            f"**Paths:** {len(paths_dict)} | **Descendants:** {desc_count}")

    spec = create_spec(title, desc, tag, paths_dict)
    fname = f"native-{name}"
    out_path = output_dir / f"{fname}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)

    return fname


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

# Containers that should be grouped together into a single spec (too small individually)
SMALL_CONTAINER_GROUPS = {
    'native-system-core': {
        'title': 'Cisco IOS-XE Native Config - System Core Settings',
        'desc': 'Core system settings: hostname, version, boot, config-register, and other fundamental device parameters.',
        'containers': [
            'version', 'hostname', 'config-register', 'boot-start-marker', 'boot-end-marker',
            'captive-portal-bypass', 'aqm-register-fnf', 'disable-eadi',
            'boot', 'clock', 'service', 'memory', 'memory-size', 'scheduler',
            'exception', 'process', 'setup', 'tod-clock', 'file'
        ]
    },
    'native-cli-mgmt': {
        'title': 'Cisco IOS-XE Native Config - CLI & Management',
        'desc': 'CLI management: banners, line config, parser, aliases, macros, templates, transport.',
        'containers': [
            'banner', 'line', 'parser', 'alias', 'macro', 'template', 'event',
            'transport', 'transport-map', 'wsma', 'archive'
        ]
    },
    'native-security': {
        'title': 'Cisco IOS-XE Native Config - Security & Authentication',
        'desc': 'Security: AAA, RADIUS, TACACS+, passwords, usernames, privileges, 802.1X, MAB.',
        'containers': [
            'aaa', 'radius', 'radius-server', 'tacacs', 'tacacs-server',
            'enable', 'password', 'username', 'user-name', 'privilege', 'login',
            'eap', 'dot1x', 'mab', 'identity', 'key'
        ]
    },
    'native-crypto': {
        'title': 'Cisco IOS-XE Native Config - Cryptography & PKI',
        'desc': 'Crypto: IKEv2, IPsec, PKI trustpoints, MACsec MKA, certificates.',
        'containers': ['crypto', 'mka']
    },
    'native-switching': {
        'title': 'Cisco IOS-XE Native Config - Switching & VLANs',
        'desc': 'Layer 2: VLANs, spanning-tree, VTP, LACP, port-channel, MAC table, errdisable.',
        'containers': [
            'vlan', 'spanning-tree', 'vtp', 'lacp', 'port-channel',
            'mac-address-table', 'mac', 'errdisable', 'l2', 'mvrp', 'avb',
            'ethernet', 'bridge-domain', 'xconnect', 'udld'
        ]
    },
    'native-routing-protocols': {
        'title': 'Cisco IOS-XE Native Config - Routing Protocols',
        'desc': 'Dynamic routing: OSPF, BGP, EIGRP, ISIS, RIP, static routes, route-maps, prefix-lists.',
        'containers': [
            'router', 'route-map', 'route-tag', 'table-map',
            'global-address-family', 'bfd', 'bfd-template', 'track'
        ]
    },
    'native-mpls-vpn': {
        'title': 'Cisco IOS-XE Native Config - MPLS, VPN & Segment Routing',
        'desc': 'MPLS, L2VPN, L3VPN, VXLAN, segment routing, performance measurement.',
        'containers': [
            'mpls', 'l2vpn', 'l2vpn-config', 'l3vpn', 'vxlan',
            'segment-routing', 'performance-measurement', 'otv',
            'pseudowire-class', 'l2tp-class', 'l2tp'
        ]
    },
    'native-monitoring': {
        'title': 'Cisco IOS-XE Native Config - Monitoring & Logging',
        'desc': 'Monitoring: syslog, SNMP, RMON, flow/NetFlow, sampler, performance.',
        'containers': [
            'logging', 'snmp', 'snmp-server', 'monitor', 'rmon', 'sampler',
            'flow', 'performance'
        ]
    },
    'native-platform': {
        'title': 'Cisco IOS-XE Native Config - Platform & Hardware',
        'desc': 'Platform: hardware modules, stacking, controllers, transceivers, diagnostics, licensing.',
        'containers': [
            'platform', 'hw-module', 'module', 'card', 'controller',
            'stack-power', 'stackwise-virtual', 'transceivers', 'license',
            'call-home', 'software', 'upgrade', 'iox'
        ]
    },
    'native-services': {
        'title': 'Cisco IOS-XE Native Config - Network Services',
        'desc': 'Services: NTP, DHCP, DNS/domain, CDP, NAT, QoS, LLDP, and other network services.',
        'containers': [
            'ntp', 'cdp', 'nat', 'domain', 'ptp',
            'avc', 'sdm', 'mls', 'object-group', 'parameter-map',
            'time-range', 'device-tracking', 'policy', 'qos'
        ]
    },
    'native-ha': {
        'title': 'Cisco IOS-XE Native Config - High Availability',
        'desc': 'HA: redundancy, FHRP (HSRP/VRRP/GLBP), standby, failover.',
        'containers': [
            'redundancy', 'fhrp', 'standby', 'redun-management'
        ]
    },
    'native-wan-misc': {
        'title': 'Cisco IOS-XE Native Config - WAN, VRF & Miscellaneous',
        'desc': 'WAN/misc: VRF, frame-relay, PPP, multilink, subscriber, fabric, and other features.',
        'containers': [
            'vrf', 'ipv6', 'frame-relay', 'ppp', 'multilink', 'subscriber-config',
            'fallback', 'fabric', 'location', 'epm', 'system',
            'cisp', 'clns', 'cts', 'cwmp', 'pfr', 'pfr-map',
            'network-clock', 'facility-alarm', 'default',
            'scada-gw', 'endpoint-tracker', 'ldap', 'zone', 'zone-pair',
            'alarm-contact', 'md-list', 'tftp-server-config', 'service-chain',
            'service-insertion', 'remote-management', 'virtual-service',
            'virtual-template', 'metadata', 'profile',
            'control-plane', 'control-plane-host', 'management',
            'redun-management'
        ]
    },
}


def generate_all(tree_html: str, output_dir: str):
    """Main entry point: parse tree, generate all specs."""
    output_path = Path(output_dir)
    # Clean previous output
    if output_path.exists():
        for f in output_path.glob('*.json'):
            f.unlink()
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("Native YANG Tree -> OpenAPI 3.0 Generator")
    print(f"{'='*70}\n")

    # Step 1: Parse the tree
    print("Parsing YANG tree HTML...")
    root = parse_yang_tree_html(tree_html)
    total_children = len(root.children)
    total_desc = root.descendant_count()
    print(f"  Parsed {total_children} top-level nodes, {total_desc} total descendants\n")

    # Build lookup of top-level children
    top_level = {c.name: c for c in root.children}

    all_generated = []

    # Step 2: Handle interface mega container
    print("--- Interface (mega container) ---")
    intf_node = top_level.get('interface')
    if intf_node:
        intf_specs = generate_interface_specs(intf_node, output_path)
        all_generated.extend(intf_specs)
    print()

    # Step 3: Handle IP mega container
    print("--- IP (mega container) ---")
    ip_node = top_level.get('ip')
    if ip_node:
        ip_specs = generate_ip_specs(ip_node, output_path)
        all_generated.extend(ip_specs)
    print()

    # Step 4: Handle grouped containers
    print("--- Grouped containers ---")
    assigned = set()
    # Collect all containers that are assigned to groups
    for group_key, group_info in SMALL_CONTAINER_GROUPS.items():
        assigned.update(group_info['containers'])

    # Also mark mega containers as assigned
    assigned.update(['interface', 'ip'])

    for group_key, group_info in SMALL_CONTAINER_GROUPS.items():
        paths_dict = {}
        tag = group_key

        for cname in group_info['containers']:
            cnode = top_level.get(cname)
            if not cnode:
                continue

            base = f"/data/Cisco-IOS-XE-native:native/{cname}"
            if cnode.node_type == 'leaf':
                paths_dict[base] = make_path_operations(base, cnode, tag)
            else:
                deep = collect_deep_paths(cnode, base, max_depth=3, current_depth=0)
                for rpath, rnode in deep:
                    if rpath not in paths_dict:
                        paths_dict[rpath] = make_path_operations(rpath, rnode, tag)

        if not paths_dict:
            continue

        spec = create_spec(group_info['title'], group_info['desc'], tag, paths_dict)
        spec_json = json.dumps(spec, indent=2)
        size_kb = len(spec_json.encode('utf-8')) / 1024
        MAX_SIZE_KB = 2048  # 2 MB

        if size_kb > MAX_SIZE_KB:
            # Split: emit one spec per container in this group
            print(f"  {group_key}: {len(paths_dict)} paths ({size_kb:.0f} KB) — splitting by container...")
            for cname in group_info['containers']:
                cnode = top_level.get(cname)
                if not cnode:
                    continue
                sub_paths = {}
                base = f"/data/Cisco-IOS-XE-native:native/{cname}"
                # Large individual containers: split further by sub-container
                desc_count = cnode.descendant_count()
                if desc_count > 500 and cnode.node_type != 'leaf':
                    # Split this container by its direct children
                    print(f"    {cname} ({desc_count} descendants) — splitting by sub-feature...")
                    # Root path
                    sub_paths[base] = make_path_operations(base, cnode, cname, schema_depth=1)
                    for sub_child in cnode.children:
                        sc_paths = {}
                        sc_base = f"{base}/{sub_child.name}"
                        if sub_child.node_type == 'leaf':
                            sc_paths[sc_base] = make_path_operations(sc_base, sub_child, sub_child.name)
                        else:
                            deep = collect_deep_paths(sub_child, sc_base, max_depth=3, current_depth=0)
                            for rpath, rnode in deep:
                                if rpath not in sc_paths:
                                    sc_paths[rpath] = make_path_operations(rpath, rnode, sub_child.name)
                        if not sc_paths:
                            continue
                        sc_title = f"Cisco IOS-XE Native Config - {cname}/{sub_child.name}"
                        sc_desc = f"Configuration for `/native/{cname}/{sub_child.name}`"
                        sc_spec = create_spec(sc_title, sc_desc, sub_child.name, sc_paths)
                        sc_fname = f"native-{cname}-{sub_child.name}"
                        sc_out = output_path / f"{sc_fname}.json"
                        with open(sc_out, 'w', encoding='utf-8') as f:
                            json.dump(sc_spec, f, indent=2)
                        sc_size = len(json.dumps(sc_spec, indent=2).encode('utf-8')) / 1024
                        print(f"      {sc_fname}: {len(sc_paths)} paths ({sc_size:.0f} KB)")
                        all_generated.append(sc_fname)
                else:
                    if cnode.node_type == 'leaf':
                        sub_paths[base] = make_path_operations(base, cnode, cname)
                    else:
                        deep = collect_deep_paths(cnode, base, max_depth=3, current_depth=0)
                        for rpath, rnode in deep:
                            if rpath not in sub_paths:
                                sub_paths[rpath] = make_path_operations(rpath, rnode, cname)
                    if not sub_paths:
                        continue
                    sub_title = f"Cisco IOS-XE Native Config - {cname}"
                    sub_desc = f"Configuration for `/native/{cname}` ({desc_count} descendants)"
                    sub_spec = create_spec(sub_title, sub_desc, cname, sub_paths)
                    sub_fname = f"native-{cname}"
                    sub_out = output_path / f"{sub_fname}.json"
                    with open(sub_out, 'w', encoding='utf-8') as f:
                        json.dump(sub_spec, f, indent=2)
                    sub_size = len(json.dumps(sub_spec, indent=2).encode('utf-8')) / 1024
                    print(f"    {sub_fname}: {len(sub_paths)} paths ({sub_size:.0f} KB)")
                    all_generated.append(sub_fname)
        else:
            fname = group_key
            out_path = output_path / f"{fname}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2)
            print(f"  {fname}: {len(paths_dict)} paths ({size_kb:.0f} KB)")
            all_generated.append(fname)

    print()

    # Step 5: Any unassigned containers -> native-uncategorized
    unassigned = {n: c for n, c in top_level.items() if n not in assigned}
    if unassigned:
        paths_dict = {}
        tag = 'uncategorized'
        for cname, cnode in unassigned.items():
            base = f"/data/Cisco-IOS-XE-native:native/{cname}"
            if cnode.node_type == 'leaf':
                paths_dict[base] = make_path_operations(base, cnode, tag)
            else:
                deep = collect_deep_paths(cnode, base, max_depth=2, current_depth=0)
                for rpath, rnode in deep:
                    if rpath not in paths_dict:
                        paths_dict[rpath] = make_path_operations(rpath, rnode, tag)

        if paths_dict:
            title = "Cisco IOS-XE Native Config - Uncategorized"
            desc = f"Remaining {len(unassigned)} containers: {', '.join(sorted(unassigned.keys()))}"
            spec = create_spec(title, desc, tag, paths_dict)
            fname = "native-uncategorized"
            out_path = output_path / f"{fname}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2)
            print(f"  {fname}: {len(paths_dict)} paths (unassigned containers)")
            all_generated.append(fname)

    # Step 6: Write manifest
    total_paths = 0
    for fname in all_generated:
        fpath = output_path / f"{fname}.json"
        if fpath.exists():
            with open(fpath) as f:
                spec = json.load(f)
            total_paths += len(spec.get('paths', {}))

    manifest = {
        'total_modules': len(all_generated),
        'total_paths': total_paths,
        'total_operations': total_paths * 4,  # GET/PUT/PATCH/DELETE
        'modules': sorted(all_generated),
        'generator': 'generate_native_from_tree.py',
        'source': 'Cisco-IOS-XE-native.html (resolved YANG tree)',
        'version': '17.18.1'
    }
    with open(output_path / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Done: {len(all_generated)} specs, {total_paths} total paths")
    print(f"{'='*70}\n")


def main():
    script_dir = Path(__file__).parent
    tree_html = str(script_dir.parent / 'yang-trees' / 'Cisco-IOS-XE-native.html')
    output_dir = str(script_dir.parent / 'swagger-native-config-model' / 'api')

    generate_all(tree_html, output_dir)


if __name__ == '__main__':
    main()
