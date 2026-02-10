"""
Enhance event notification Swagger specs with YANG-derived schemas and examples.

Parses YANG tree HTML files to extract notification definitions,
generates OpenAPI schemas with typed properties and realistic examples,
and updates each event spec in swagger-events-model/api/.

Usage:
    python scripts/enhance_events.py              # dry-run
    python scripts/enhance_events.py --apply      # apply changes
"""
import json
import os
import re
import sys
import copy
from collections import OrderedDict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS_DIR = os.path.join(BASE, 'swagger-events-model', 'api')
TREES_DIR = os.path.join(BASE, 'yang-trees')
TODO_PATH = os.path.join(BASE, 'TODO_EVENTS.md')

DRY_RUN = '--apply' not in sys.argv

# ──────────────────────────────────────────────────────────────
# YANG type → JSON Schema type mapping
# ──────────────────────────────────────────────────────────────
YANG_TYPE_MAP = {
    'string': {'type': 'string'},
    'binary': {'type': 'string', 'format': 'binary'},
    'boolean': {'type': 'boolean'},
    'empty': {'type': 'boolean'},
    'int8': {'type': 'integer', 'format': 'int32'},
    'int16': {'type': 'integer', 'format': 'int32'},
    'int32': {'type': 'integer', 'format': 'int32'},
    'int64': {'type': 'integer', 'format': 'int64'},
    'uint8': {'type': 'integer', 'format': 'int32'},
    'uint16': {'type': 'integer', 'format': 'int32'},
    'uint32': {'type': 'integer', 'format': 'int32'},
    'uint64': {'type': 'integer', 'format': 'int64'},
    'decimal64': {'type': 'number', 'format': 'double'},
    'counter32': {'type': 'integer', 'format': 'int32'},
    'counter64': {'type': 'integer', 'format': 'int64'},
    'gauge32': {'type': 'integer', 'format': 'int32'},
    'gauge64': {'type': 'integer', 'format': 'int64'},
}

# Pattern-based type detection for qualified types
TYPE_PATTERNS = [
    (r'inet:ip-address', {'type': 'string', 'format': 'ipv4'}, '10.1.1.1'),
    (r'inet:ipv4-address', {'type': 'string', 'format': 'ipv4'}, '10.1.1.1'),
    (r'inet:ipv6-address', {'type': 'string', 'format': 'ipv6'}, '2001:db8::1'),
    (r'inet:host', {'type': 'string'}, '10.1.1.1'),
    (r'inet:port-number', {'type': 'integer', 'format': 'int32'}, 830),
    (r'inet:uri', {'type': 'string', 'format': 'uri'}, 'https://example.com'),
    (r'yang:mac-address', {'type': 'string'}, '00:1a:2b:3c:4d:5e'),
    (r'yang:date-and-time', {'type': 'string', 'format': 'date-time'}, '2026-02-10T10:30:00Z'),
    (r'yang:counter32', {'type': 'integer', 'format': 'int32'}, 12345),
    (r'yang:counter64', {'type': 'integer', 'format': 'int64'}, 123456789),
    (r'yang:gauge32', {'type': 'integer', 'format': 'int32'}, 50),
    (r'yang:gauge64', {'type': 'integer', 'format': 'int64'}, 50),
    (r'yang:timeticks', {'type': 'integer', 'format': 'int64'}, 36000),
    (r'yang:timestamp', {'type': 'integer', 'format': 'int64'}, 1707500000),
    (r'yang:phys-address', {'type': 'string'}, '00:1a:2b:3c:4d:5e'),
    (r'enumeration', {'type': 'string'}, 'value-1'),
    (r'bits', {'type': 'string'}, 'bit0'),
    (r'union', {'type': 'string'}, 'value'),
]

# Example values by YANG type
EXAMPLE_VALUES = {
    'string': 'example-string',
    'boolean': True,
    'empty': True,
    'int8': 1,
    'int16': 100,
    'int32': 1000,
    'int64': 100000,
    'uint8': 1,
    'uint16': 100,
    'uint32': 1000,
    'uint64': 100000,
    'decimal64': 3.14,
    'counter32': 12345,
    'counter64': 123456789,
    'gauge32': 50,
    'gauge64': 50,
}

# Context-aware example values based on leaf name patterns
NAME_EXAMPLES = {
    'severity': 'major',
    'severity-level': 'major',
    'host-name': 'Router1',
    'hostname': 'Router1',
    'system-ip': '10.1.1.1',
    'vrf-name': 'default',
    'vrf': 'default',
    'if-name': 'GigabitEthernet1',
    'interface': 'GigabitEthernet1',
    'if-index': 1,
    'ifindex': 1,
    'router-id': '1.1.1.1',
    'process-id': 1,
    'address': '10.1.1.1',
    'mask': '255.255.255.0',
    'ip-address': '10.1.1.1',
    'ipv4-address': '10.1.1.1',
    'ipv6-address': '2001:db8::1',
    'mac-address': '00:1a:2b:3c:4d:5e',
    'client-mac': '00:1a:2b:3c:4d:5e',
    'wtp-mac': 'aa:bb:cc:dd:ee:ff',
    'ssid': 'Corporate-WiFi',
    'vlan-id': 100,
    'username': 'admin',
    'session-id': 12345,
    'subscription-id': 2147483650,
    'state': 'active',
    'status': 'up',
    'reason': 'configuration-change',
    'message': 'Operation completed successfully',
    'uuid': '550e8400-e29b-41d4-a716-446655440000',
    'timestamp': '2026-02-10T10:30:00Z',
    'name': 'example-name',
    'description': 'Event notification description',
    'index': 1,
    'count': 5,
    'id': 12345,
    'type': 'event-type',
    'mode': 'active',
    'version': '17.18.1',
    'from-version': '17.17.1',
    'to-version': '17.18.1',
    'percentage': 85,
    'percentage-completed': 85,
    'percentage-predownloaded': 100,
    'channel': 36,
    'rssi': -65,
    'snr': 30,
    'band-id': 1,
    'slot-id': 0,
    'seconds-left': 86400,
    'expire-time': '2026-12-31T23:59:59Z',
    'start-time': '2026-02-10T10:00:00Z',
    'end-time': '2026-02-10T11:00:00Z',
    'expected-end-time': '2026-02-10T11:00:00Z',
    'total-num-of-aps': 100,
    'num-of-aps-predownloaded': 100,
    'num-of-aps-upgraded': 95,
    'aps-selected-for-upgd': 100,
    'num-of-iterations': 3,
    'current-iteration': 2,
    'serial-iter-num': 1,
    'entry-count': 10,
    'configured-threshold': 80,
    'threshold-reached-clear': False,
    'is-fabric-client': False,
    'is-dot1x': True,
    'is-beacon-ds': False,
    'is-client': True,
    'audit-session-id': 'AC1001640000002B',
    'auth-result': 'success',
    'event-type': 'state-change',
    'upgrade-state': 'in-progress',
}

# ──────────────────────────────────────────────────────────────
# YANG Tree Parser
# ──────────────────────────────────────────────────────────────

class YangNotification:
    """Represents a single YANG notification definition."""
    def __init__(self, name):
        self.name = name
        self.leaves = []  # list of (name, yang_type, is_list, children)
        self.is_deprecated = False


class NotifLeaf:
    """A leaf/container within a notification."""
    def __init__(self, name, yang_type=None, is_list=False, is_container=False):
        self.name = name
        self.yang_type = yang_type
        self.is_list = is_list
        self.is_container = is_container
        self.children = []


def find_yang_tree(html_content):
    """Find the YANG tree <pre> block in HTML."""
    pres = re.findall(r'<pre>(.*?)</pre>', html_content, re.DOTALL)
    for p in pres:
        if 'module:' in p[:50] or '+--' in p[:200]:
            return p
    return None


def decode_html(text):
    """Decode HTML entities."""
    return text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')


def parse_notifications(tree_text):
    """Parse all notification definitions from a YANG tree text."""
    tree_text = decode_html(tree_text)
    lines = tree_text.split('\n')
    
    notifications = []
    current_notif = None
    notif_indent = 0
    
    # Stack for tracking nested containers/lists within a notification
    # Each entry: (indent, NotifLeaf)
    container_stack = []
    
    in_notifications_section = False
    
    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue
        
        # Check if we've entered the notifications section
        if 'notifications:' in stripped:
            in_notifications_section = True
            continue
        
        if not in_notifications_section:
            continue
        
        # Calculate indent level (rough, based on leading whitespace)
        indent = len(line) - len(line.lstrip())
        
        # Check for new notification: +---n name
        notif_match = re.search(r'\+---n\s+(\S+)', stripped)
        if notif_match:
            notif_name = notif_match.group(1)
            current_notif = YangNotification(notif_name)
            notifications.append(current_notif)
            notif_indent = indent
            container_stack = []
            
            # Check if deprecated (x---n)
            if 'x---n' in stripped:
                current_notif.is_deprecated = True
            continue
        
        # Also catch x---n (deprecated notifications) as they still show in tree
        dep_match = re.search(r'x---n\s+(\S+)', stripped)
        if dep_match:
            notif_name = dep_match.group(1)
            current_notif = YangNotification(notif_name)
            current_notif.is_deprecated = True
            notifications.append(current_notif)
            notif_indent = indent
            container_stack = []
            continue
        
        if current_notif is None:
            continue
        
        # If we hit another top-level section (rpcs, etc), stop
        if indent <= notif_indent and ('+--rw' in stripped or '+--ro' in stripped or 'rpcs:' in stripped):
            # Might be a different section
            if not any(c in stripped for c in ['+--ro object-', '+--ro ']):
                if indent < notif_indent:
                    current_notif = None
                    container_stack = []
                    continue
        
        # Parse leaf/container lines within a notification
        # Patterns:
        #   +--ro name?   type               (leaf)
        #   +--ro name*   type               (leaf-list)
        #   +--ro name* [keys]               (list)
        #   +--ro name                       (container - no type)
        #   +--ro object-N                   (MIB trap object grouping)
        
        leaf_match = re.search(r'\+--ro\s+(\S+?)(\*|\?)?\s+(.*)', stripped)
        if leaf_match:
            name = leaf_match.group(1)
            modifier = leaf_match.group(2) or ''
            rest = leaf_match.group(3).strip()
            
            is_list = '*' in modifier or ('*' in stripped.split(name)[0][-2:] if name in stripped else False)
            
            # Check if it's a reference (MIB style: -> /MIB/table/entry/col)
            if rest.startswith('->') or rest.startswith('-&gt;'):
                # MIB object reference - extract the referenced column name
                ref_path = rest.replace('->', '').replace('-&gt;', '').strip()
                ref_col = ref_path.split('/')[-1] if '/' in ref_path else name
                leaf = NotifLeaf(ref_col, yang_type='string')
                _add_leaf_to_parent(current_notif, container_stack, leaf, indent)
                continue
            
            # Check for list with keys: [key1] or []
            if rest.startswith('['):
                # It's a list container
                leaf = NotifLeaf(name, is_list=True, is_container=True)
                _add_leaf_to_parent(current_notif, container_stack, leaf, indent)
                container_stack = [(i, l) for i, l in container_stack if i < indent]
                container_stack.append((indent, leaf))
                continue
            
            # If rest is empty, it's a container
            if not rest:
                leaf = NotifLeaf(name, is_container=True)
                _add_leaf_to_parent(current_notif, container_stack, leaf, indent)
                container_stack = [(i, l) for i, l in container_stack if i < indent]
                container_stack.append((indent, leaf))
                continue
            
            # It's a leaf with a type
            yang_type = rest.strip()
            leaf = NotifLeaf(name, yang_type=yang_type, is_list=is_list)
            _add_leaf_to_parent(current_notif, container_stack, leaf, indent)
            continue
        
        # Catch the simpler form: +--ro name (no ? or *)
        simple_match = re.search(r'\+--ro\s+(\S+)\s*$', stripped)
        if simple_match:
            name = simple_match.group(1)
            leaf = NotifLeaf(name, is_container=True)
            _add_leaf_to_parent(current_notif, container_stack, leaf, indent)
            container_stack = [(i, l) for i, l in container_stack if i < indent]
            container_stack.append((indent, leaf))
    
    return notifications


def _add_leaf_to_parent(notif, container_stack, leaf, indent):
    """Add a leaf to the appropriate parent based on indent level."""
    # Pop containers that are at same or deeper indent
    while container_stack and container_stack[-1][0] >= indent:
        container_stack.pop()
    
    if container_stack:
        container_stack[-1][1].children.append(leaf)
    else:
        notif.leaves.append(leaf)


# ──────────────────────────────────────────────────────────────
# Schema and Example Generation
# ──────────────────────────────────────────────────────────────

def yang_type_to_schema(yang_type):
    """Convert a YANG type string to JSON Schema type dict."""
    if not yang_type:
        return {'type': 'string'}
    
    # Check pattern-based types first
    for pattern, schema, _ in TYPE_PATTERNS:
        if pattern in yang_type:
            return dict(schema)
    
    # Check basic type map
    base = yang_type.split(':')[-1] if ':' in yang_type else yang_type
    if base in YANG_TYPE_MAP:
        return dict(YANG_TYPE_MAP[base])
    
    # Qualified types that look like enums (module:type-name)
    if ':' in yang_type:
        return {'type': 'string'}
    
    return {'type': 'string'}


def get_example_value(leaf_name, yang_type):
    """Generate a realistic example value for a leaf."""
    # Try name-based examples first
    name_lower = leaf_name.lower().replace('_', '-')
    if name_lower in NAME_EXAMPLES:
        return NAME_EXAMPLES[name_lower]
    
    # Partial name matches
    for key, val in NAME_EXAMPLES.items():
        if key in name_lower:
            return val
    
    # Pattern-based type examples
    if yang_type:
        for pattern, _, example in TYPE_PATTERNS:
            if pattern in yang_type:
                return example
        
        base = yang_type.split(':')[-1] if ':' in yang_type else yang_type
        if base in EXAMPLE_VALUES:
            return EXAMPLE_VALUES[base]
        
        # If it's a qualified enum type
        if ':' in yang_type:
            # Generate a reasonable enum value from type name
            parts = yang_type.split(':')[-1].replace('-', ' ').split()
            return '-'.join(parts[:2]) if parts else 'value'
    
    return 'example-value'


def leaf_to_schema_property(leaf):
    """Convert a NotifLeaf to a JSON Schema property dict."""
    if leaf.is_container and leaf.children:
        props = {}
        for child in leaf.children:
            props[child.name] = leaf_to_schema_property(child)
        schema = {'type': 'object', 'properties': props}
        if leaf.is_list:
            return {'type': 'array', 'items': schema}
        return schema
    
    if leaf.is_list and leaf.yang_type:
        item_schema = yang_type_to_schema(leaf.yang_type)
        return {'type': 'array', 'items': item_schema}
    
    schema = yang_type_to_schema(leaf.yang_type)
    return schema


def leaf_to_example(leaf):
    """Generate example value for a leaf."""
    if leaf.is_container and leaf.children:
        example = {}
        for child in leaf.children:
            example[child.name] = leaf_to_example(child)
        if leaf.is_list:
            return [example]
        return example
    
    if leaf.is_list and leaf.yang_type:
        return [get_example_value(leaf.name, leaf.yang_type)]
    
    return get_example_value(leaf.name, leaf.yang_type)


def build_notification_schema(module_name, notif):
    """Build a complete OpenAPI schema for a notification."""
    # Build inner properties from notification leaves
    inner_props = {}
    inner_example = {}
    
    for leaf in notif.leaves:
        prop_schema = leaf_to_schema_property(leaf)
        inner_props[leaf.name] = prop_schema
        inner_example[leaf.name] = leaf_to_example(leaf)
    
    # Determine the notification namespace prefix
    prefix = module_name
    
    # Build the full notification wrapper
    schema = {
        'type': 'object',
        'description': f'Notification payload for {notif.name}',
        'properties': {
            'notification': {
                'type': 'object',
                'properties': {
                    'eventTime': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'Timestamp when the event occurred'
                    },
                    f'{prefix}:{notif.name}': {
                        'type': 'object',
                        'properties': inner_props
                    }
                }
            }
        },
        'example': {
            'notification': {
                'eventTime': '2026-02-10T10:30:00Z',
                f'{prefix}:{notif.name}': inner_example
            }
        }
    }
    
    return schema


def build_mib_notification_schema(mib_name, notif):
    """Build schema for MIB-style SNMP trap notifications.
    
    MIB notifications have object-1, object-2, etc. groupings
    with reference leaves. We flatten them into varbind properties.
    """
    varbind_props = {}
    varbind_example = {}
    
    for leaf in notif.leaves:
        if leaf.is_container and leaf.name.startswith('object-'):
            # MIB object grouping - extract the reference column leaves
            for child in leaf.children:
                if not child.name.startswith(('clog', 'ccm', 'cpm', 'cisco', 'if', 'ent',
                    'snmp', 'ip', 'mpls', 'bgp', 'ospf', 'rsvp', 'pim', 'rmon',
                    'dot', 'ds', 'frame', 'power', 'lldp', 'atm', 'dial')):
                    # Skip index refs that are children
                    pass
                # Include the actual value leaf (not the index)
                prop_schema = yang_type_to_schema(child.yang_type)
                varbind_props[child.name] = prop_schema
                varbind_example[child.name] = get_example_value(child.name, child.yang_type)
        else:
            # Direct leaves
            prop_schema = leaf_to_schema_property(leaf)
            varbind_props[leaf.name] = prop_schema
            varbind_example[leaf.name] = leaf_to_example(leaf)
    
    # If no properties extracted, create minimal schema
    if not varbind_props:
        varbind_props = {
            'event-time': {'type': 'string', 'format': 'date-time'}
        }
        varbind_example = {'event-time': '2026-02-10T10:30:00Z'}
    
    schema = {
        'type': 'object',
        'description': f'SNMP trap notification payload for {notif.name}',
        'properties': {
            'notification': {
                'type': 'object',
                'properties': {
                    'eventTime': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'Timestamp when the trap was generated'
                    },
                    f'{mib_name}:{notif.name}': {
                        'type': 'object',
                        'description': f'Varbind objects for {notif.name} trap',
                        'properties': varbind_props
                    }
                }
            }
        },
        'example': {
            'notification': {
                'eventTime': '2026-02-10T10:30:00Z',
                f'{mib_name}:{notif.name}': varbind_example
            }
        }
    }
    
    return schema


# ──────────────────────────────────────────────────────────────
# Spec Enhancement
# ──────────────────────────────────────────────────────────────

def enhance_spec(spec_path, tree_path):
    """Enhance a single event spec with YANG-derived schemas and examples."""
    with open(spec_path, encoding='utf-8-sig') as f:
        spec = json.load(f)
    
    basename = os.path.basename(spec_path).replace('.json', '')
    
    with open(tree_path, encoding='utf-8') as f:
        html = f.read()
    
    tree_text = find_yang_tree(html)
    if not tree_text:
        return None, 'No YANG tree found'
    
    notifications = parse_notifications(tree_text)
    if not notifications:
        return None, 'No notifications in tree'
    
    is_mib = '-MIB' in basename and basename[0].isupper()
    
    # Build schemas for all notifications
    new_schemas = {}
    for notif in notifications:
        if is_mib:
            schema = build_mib_notification_schema(basename, notif)
        else:
            schema = build_notification_schema(basename, notif)
        new_schemas[notif.name] = schema
    
    # Ensure components.schemas exists
    if 'components' not in spec:
        spec['components'] = {}
    if 'schemas' not in spec['components']:
        spec['components']['schemas'] = {}
    
    # Add/update schemas
    added_schemas = 0
    for name, schema in new_schemas.items():
        if name not in spec['components']['schemas']:
            spec['components']['schemas'][name] = schema
            added_schemas += 1
        else:
            # Update existing schema if it lacks examples
            existing = spec['components']['schemas'][name]
            if 'example' not in existing:
                existing['example'] = schema['example']
                added_schemas += 1
            # Ensure nested properties are present
            if 'properties' in schema and 'properties' in existing:
                notif_prop = schema.get('properties', {}).get('notification', {})
                existing_notif = existing.get('properties', {}).get('notification', {})
                if notif_prop and existing_notif:
                    # Merge missing properties
                    for key, val in notif_prop.get('properties', {}).items():
                        if key not in existing_notif.get('properties', {}):
                            if 'properties' not in existing_notif:
                                existing_notif['properties'] = {}
                            existing_notif['properties'][key] = val
    
    # Now update paths to reference schemas and add examples
    paths_updated = 0
    for path_key, path_obj in spec.get('paths', {}).items():
        for method_key, op in path_obj.items():
            if not isinstance(op, dict):
                continue
            
            # Determine which notification this path is for
            notif_name = _find_notif_for_path(path_key, notifications, basename)
            
            if not notif_name or notif_name not in new_schemas:
                continue
            
            schema_ref = f'#/components/schemas/{notif_name}'
            notif_schema = new_schemas[notif_name]
            
            # Update response content
            for status_code, response in op.get('responses', {}).items():
                if not isinstance(response, dict):
                    continue
                
                # Skip $ref responses - replace them with inline
                if '$ref' in response:
                    # Replace the $ref with a proper inline response
                    op['responses'][status_code] = {
                        'description': response.get('description', f'{notif_name} notification data'),
                        'content': {
                            'application/yang-data+json': {
                                'schema': {'$ref': schema_ref},
                                'example': notif_schema.get('example', {})
                            }
                        }
                    }
                    paths_updated += 1
                    continue
                
                if status_code in ('200', '101'):
                    content = response.get('content', {})
                    if 'application/yang-data+json' not in content:
                        # Add content type
                        if 'content' not in response:
                            response['content'] = {}
                        response['content']['application/yang-data+json'] = {
                            'schema': {'$ref': schema_ref},
                            'example': notif_schema.get('example', {})
                        }
                        paths_updated += 1
                    else:
                        yd = content['application/yang-data+json']
                        updated_this = False
                        # Add schema ref if missing
                        if 'schema' not in yd:
                            yd['schema'] = {'$ref': schema_ref}
                            updated_this = True
                        elif '$ref' not in yd.get('schema', {}):
                            yd['schema'] = {'$ref': schema_ref}
                            updated_this = True
                        # Add/update example with YANG-derived one
                        new_ex = notif_schema.get('example', {})
                        if 'example' not in yd:
                            yd['example'] = new_ex
                            updated_this = True
                        else:
                            # Always replace with YANG-derived example
                            yd['example'] = new_ex
                            updated_this = True
                        if updated_this:
                            paths_updated += 1
            
            # Update requestBody examples (for subscription POST)
            if 'requestBody' in op:
                rb = op['requestBody']
                if isinstance(rb, dict) and 'content' in rb:
                    for ct, ct_val in rb['content'].items():
                        if isinstance(ct_val, dict) and 'example' not in ct_val:
                            ct_val['example'] = {
                                'input': {
                                    'stream': f'{basename}:{notif_name}',
                                    'encoding': 'encode-json',
                                    'update-trigger': 'on-change'
                                }
                            }
    
    return spec, f'+{added_schemas} schemas, {paths_updated} path updates, {len(notifications)} notifications'


def _find_notif_for_path(path_key, notifications, module_name):
    """Match a path to a notification name."""
    # Patterns to check:
    # /ws/event-streams/module/notif-name
    # /data/module:events (match first notification)
    # /data/ietf-subscribed-notifications:.../MIB:notifName
    
    for notif in notifications:
        # Check direct name in path
        if notif.name in path_key:
            return notif.name
    
    # For generic event paths like /data/module:events, use first notification
    if f'{module_name}:events' in path_key or f'{module_name}:event' in path_key:
        if notifications:
            return notifications[0].name
    
    # For subscription paths
    if 'establish-subscription' in path_key:
        if notifications:
            return notifications[0].name
    
    return None


def _is_generic_example(example):
    """Check if an example is generic/placeholder rather than YANG-derived."""
    if not isinstance(example, dict):
        return False
    
    # Check for the generic pattern used in current events
    for key, val in example.items():
        if isinstance(val, dict):
            inner = val
            # Generic examples typically have simple/wrong field names
            for inner_key, inner_val in inner.items():
                if isinstance(inner_val, dict):
                    fields = set(inner_val.keys())
                    # If it has generic fields like 'event-type', 'username', etc.
                    # that aren't actually in the YANG model
                    if 'event-type' in fields and 'username' in fields:
                        return True
    
    return False


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    mode = 'DRY-RUN' if DRY_RUN else 'APPLYING'
    print(f'=== Event Notification Enhancement ({mode}) ===\n')
    
    files = sorted([f for f in os.listdir(EVENTS_DIR) if f.endswith('.json') and f != 'manifest.json'])
    
    total = 0
    enhanced = 0
    skipped = 0
    errors = 0
    total_schemas = 0
    todo_updates = {}
    
    for fn in files:
        spec_path = os.path.join(EVENTS_DIR, fn)
        base = fn.replace('.json', '')
        tree_path = os.path.join(TREES_DIR, f'{base}.html')
        
        total += 1
        
        if not os.path.exists(tree_path):
            print(f'  SKIP {fn} - no YANG tree')
            skipped += 1
            todo_updates[fn] = 'SKIP (no tree)'
            continue
        
        try:
            result, msg = enhance_spec(spec_path, tree_path)
            
            if result is None:
                print(f'  SKIP {fn} - {msg}')
                skipped += 1
                todo_updates[fn] = f'SKIP ({msg})'
                continue
            
            # Count schemas in result
            schema_count = len(result.get('components', {}).get('schemas', {}))
            total_schemas += schema_count
            
            print(f'  OK   {fn} - {msg}')
            enhanced += 1
            todo_updates[fn] = f'DONE ({msg})'
            
            if not DRY_RUN:
                with open(spec_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                    f.write('\n')
        
        except Exception as e:
            print(f'  ERR  {fn} - {e}')
            errors += 1
            todo_updates[fn] = f'ERROR ({e})'
    
    print(f'\n=== Summary ===')
    print(f'Total specs:    {total}')
    print(f'Enhanced:       {enhanced}')
    print(f'Skipped:        {skipped}')
    print(f'Errors:         {errors}')
    print(f'Total schemas:  {total_schemas}')
    
    # Update TODO_EVENTS.md
    if not DRY_RUN and os.path.exists(TODO_PATH):
        with open(TODO_PATH, encoding='utf-8') as f:
            content = f.read()
        
        for fn, status in todo_updates.items():
            if status.startswith('DONE'):
                content = content.replace(f'| {fn} |', f'| {fn} |').replace(
                    f'{fn} |', f'{fn} |'
                )
                # Replace [ ] with [x] for this file's row
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if fn in line and '| [ ] |' in line:
                        lines[i] = line.replace('| [ ] |', '| [x] |')
                content = '\n'.join(lines)
        
        with open(TODO_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'\nUpdated TODO_EVENTS.md')


if __name__ == '__main__':
    main()
