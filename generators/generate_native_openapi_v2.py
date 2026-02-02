#!/usr/bin/env python3
"""
Convert Cisco-IOS-XE-native YANG module and submodules to OpenAPI 3.0 specifications.
Properly parses YANG structure instead of using hard-coded examples.
Splits into logical feature categories for better organization.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

class NativeToOpenAPI:
    """Convert Cisco-IOS-XE-native YANG to OpenAPI 3.0 with proper YANG parsing"""

    def __init__(self, yang_dir: str, output_dir: str):
        self.yang_dir = Path(yang_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.groupings_cache = {}
        self.typedefs_cache = {}
        self.processed_paths = []
        
        # Category mapping for organizing paths
        self.category_keywords = {
            'core': [],  # Will be matched explicitly in categorize_path for depth-0 leafs
            'interfaces': ['interface', 'GigabitEthernet', 'TenGigabitEthernet', 'Loopback', 
                          'Tunnel', 'Vlan', 'Port-channel', 'FastEthernet', 'Ethernet',
                          'BDI', 'Serial', 'Dialer', 'Virtual-Template', 'management-interface'],
            'routing': ['router', 'bgp', 'ospf', 'eigrp', 'rip', 'isis', 'ip route', 
                       'ipv6 route', 'route-map', 'prefix-list', 'rtr', 'track', 'bfd',
                       'global-address-family', 'table-map', 'route-tag'],
            'security': ['access-list', 'aaa', 'zone', 'class-map', 'policy-map', 
                        'acl', 'key chain', 'enable', 'username', 'user-name', 'password',
                        'login', 'privilege', 'dot1x', 'mab', 'eap', 'radius', 'tacacs',
                        'identity', 'object-group'],
            'crypto': ['crypto', 'ikev2', 'ipsec', 'isakmp', 'pki', 'key', 'certificate',
                      'keyring', 'trustpoint', 'mka', 'macsec'],
            'switching': ['vlan', 'spanning-tree', 'switchport', 'channel-group', 
                         'mac-address-table', 'errdisable', 'vtp', 'lacp', 'port-channel',
                         'l2', 'mvrp', 'avb', 'xconnect', 'pseudowire', 'l2tp'],
            'services': ['dhcp', 'nat', 'ntp', 'snmp', 'logging', 'cdp', 'lldp', 
                        'dns', 'domain', 'ip domain', 'archive', 'tftp-server',
                        'radius-server', 'ldap', 'http', 'telnet', 'ssh', 'service'],
            'qos': ['qos', 'service-policy', 'mls qos', 'class', 'policy', 'avc',
                   'parameter-map', 'sdm'],
            'mpls': ['mpls', 'ldp', 'traffic-eng', 'segment-routing'],
            'vpn': ['tunnel', 'gre', 'dmvpn'],
            'wireless': ['wireless', 'wlan', 'ap ', 'dot11'],
            'platform': ['hw-module', 'stack', 'switch', 'breakout', 'module', 'card',
                        'platform', 'stack-power', 'controller', 'cisp', 'redundancy',
                        'upgrade', 'software', 'boot', 'config-register', 'subslot', 
                        'transceiver'],
            'call-home': ['call-home'],
            'monitor': ['monitor', 'span', 'rspan', 'erspan', 'flow', 'sampler', 'rmon',
                       'netflow', 'session'],
            'voice': ['voice', 'dial-peer', 'voice-class', 'sip', 'scada-gw'],
            'switching': ['vlan', 'spanning-tree', 'switchport', 'channel-group', 
                         'mac-address-table', 'errdisable', 'vtp', 'lacp', 'port-channel',
                         'l2', 'mvrp', 'avb', 'xconnect', 'pseudowire', 'l2tp', 'mac'],
            'security': ['access-list', 'aaa', 'zone', 'class-map', 'policy-map', 
                        'acl', 'key chain', 'enable', 'username', 'user-name', 'password',
                        'login', 'privilege', 'dot1x', 'mab', 'eap', 'radius', 'tacacs',
                        'identity', 'object-group'],
            'services': ['dhcp', 'nat', 'ntp', 'snmp', 'logging', 'cdp', 'lldp', 
                        'dns', 'domain', 'ip domain', 'archive', 'tftp-server',
                        'radius-server', 'ldap', 'http', 'telnet', 'ssh', 'service'],
            'system': ['hostname', 'banner', 'clock', 'version', 'memory', 'scheduler', 
                      'process', 'license', 'line', 'parser', 'location', 'fabric',
                      'system', 'epm', 'ptp', 'multilink', 'ppp', 'macro', 'vrf',
                      'fallback', 'subscriber', 'frame-relay', 'aqm-register',
                      'control-plane', 'exception', 'transport', 'md-list', 'network-clock',
                      'protocol', 'type', 'default', 'border', 'master', 'secret', 'clns',
                      'cts', 'cwmp', 'pfr', 'facility-alarm', 'setup', 'profile', 'time-range',
                      'alias', 'group', 'tod-clock', 'transport-map']
        }

    def create_example_data(self, schema: Dict[str, Any], property_name: str = '') -> Any:
        """Generate context-aware example data based on schema and property name"""
        schema_type = schema.get('type', 'string')
        
        # Handle enumerations
        if 'enum' in schema and schema['enum']:
            return schema['enum'][0]
        
        # Context-aware examples based on property name
        name_lower = property_name.lower()
        
        # Hostname examples - realistic production names
        if 'hostname' in name_lower:
            return 'DC1-CORE-SW01'
        
        # Version examples
        if 'version' in name_lower and not any(x in name_lower for x in ['ip', 'software', 'protocol']):
            return '17.9'
        
        # Config register examples
        if 'config-register' in name_lower:
            return '0x2102'
        
        # Interface examples
        if 'interface' in name_lower or 'name' in name_lower:
            if 'loopback' in name_lower:
                return 'Loopback0'
            elif 'vlan' in name_lower:
                return 'Vlan100'
            elif 'tunnel' in name_lower:
                return 'Tunnel0'
            else:
                return 'GigabitEthernet1/0/1'
        
        # IP address examples
        if any(x in name_lower for x in ['ip-address', 'ipaddress', 'address']):
            if 'ipv6' in name_lower or 'v6' in name_lower:
                return '2001:db8::1'
            return '192.168.1.1'
        
        # Network mask examples
        if 'mask' in name_lower or 'netmask' in name_lower:
            return '255.255.255.0'
        
        # Prefix examples
        if 'prefix' in name_lower:
            if 'ipv6' in name_lower:
                return '2001:db8::/32'
            return '192.168.0.0/24'
        
        # MAC address examples
        if 'mac' in name_lower and 'address' in name_lower:
            return '00:11:22:33:44:55'
        
        # VLAN examples
        if 'vlan' in name_lower and 'id' in name_lower:
            return 100
        
        # VRF examples
        if 'vrf' in name_lower:
            return 'VRF-PROD'
        
        # AS number examples
        if 'as' in name_lower or 'asn' in name_lower:
            return 65001
        
        # Description examples
        if 'description' in name_lower or 'descr' in name_lower:
            return 'Configured via RESTCONF API'
        
        # Banner examples
        if 'banner' in name_lower:
            return 'Authorized Access Only'
        
        # Domain examples
        if 'domain' in name_lower:
            return 'example.com'
        
        # Username examples
        if 'username' in name_lower or 'user' in name_lower:
            return 'admin'
        
        # Password examples
        if 'password' in name_lower or 'secret' in name_lower:
            return '********'
        
        # Port examples
        if 'port' in name_lower:
            return 8443
        
        # Handle based on schema type
        if schema_type == 'array':
            items_schema = schema.get('items', {'type': 'string'})
            # Generate 3 example items with variations
            examples = []
            for i in range(3):
                item = self.create_example_data(items_schema, property_name)
                if isinstance(item, dict):
                    # Vary numeric and interface fields
                    if 'name' in item:
                        if isinstance(item['name'], str) and 'GigabitEthernet' in item['name']:
                            item['name'] = f'GigabitEthernet1/0/{i+1}'
                        elif isinstance(item['name'], str) and 'Vlan' in item['name']:
                            item['name'] = f'Vlan{100+i*10}'
                    if 'vlan' in item and 'id' in str(item.get('vlan', '')):
                        item['vlan'] = 100 + i * 10
                    if 'id' in item and isinstance(item['id'], int):
                        item['id'] = i + 1
                    if 'address' in item:
                        if isinstance(item['address'], str) and '192.168' in item['address']:
                            item['address'] = f'192.168.{i+1}.1'
                examples.append(item)
            return examples
        
        elif schema_type == 'object':
            properties = schema.get('properties', {})
            if not properties:
                return {}
            
            example_obj = {}
            for prop_name, prop_schema in properties.items():
                example_obj[prop_name] = self.create_example_data(prop_schema, prop_name)
            return example_obj
        
        elif schema_type == 'integer':
            minimum = schema.get('minimum', 0)
            maximum = schema.get('maximum', 100)
            
            # Context-specific integer values
            if 'mtu' in name_lower:
                return 1500
            elif 'bandwidth' in name_lower:
                return 1000000
            elif 'delay' in name_lower:
                return 100
            elif 'metric' in name_lower:
                return 10
            elif 'cost' in name_lower:
                return 1
            elif 'priority' in name_lower:
                return 100
            elif 'weight' in name_lower:
                return 1
            
            # Use minimum if it's reasonable, otherwise use a sensible default
            if minimum >= 0 and minimum <= 1000:
                return minimum + 1 if minimum < maximum else minimum
            return 1
        
        elif schema_type == 'boolean':
            return True
        
        elif schema_type == 'number':
            return 1.0
        
        else:  # string or unknown
            # Check format hints
            if schema.get('format') == 'ipv4':
                return '192.168.1.1'
            elif schema.get('format') == 'ipv6':
                return '2001:db8::1'
            elif schema.get('format') == 'byte':
                return 'QmFzZTY0RW5jb2RlZA=='
            
            # Generic string examples
            if 'name' in name_lower:
                return 'example-name'
            return 'example-string'

    def find_balanced_braces(self, text: str, start_pos: int) -> int:
        """Find the end position of balanced braces"""
        if start_pos >= len(text) or text[start_pos] != '{':
            return -1
        count = 0
        in_string = False
        for i in range(start_pos, len(text)):
            if text[i] == '"' and (i == 0 or text[i-1] != '\\'):
                in_string = not in_string
            if not in_string:
                if text[i] == '{':
                    count += 1
                elif text[i] == '}':
                    count -= 1
                    if count == 0:
                        return i
        return -1

    def read_yang_file(self, filepath: Path) -> str:
        """Read YANG file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"  Warning: Could not read {filepath}: {e}")
            return ""

    def extract_groupings(self, content: str):
        """Extract all groupings from YANG content"""
        pos = 0
        while True:
            grouping_match = re.search(r'\bgrouping\s+(\S+)\s*\{', content[pos:])
            if not grouping_match:
                break

            grouping_name = grouping_match.group(1)
            grouping_start = pos + grouping_match.end() - 1
            grouping_end = self.find_balanced_braces(content, grouping_start)

            if grouping_end == -1:
                pos += grouping_match.end()
                continue

            grouping_body = content[grouping_start + 1:grouping_end]
            self.groupings_cache[grouping_name] = grouping_body
            pos = grouping_end + 1

    def parse_leaf(self, leaf_content: str, leaf_name: str) -> Dict[str, Any]:
        """Parse a YANG leaf and return OpenAPI schema"""
        schema = {'type': 'string'}

        # Handle enumeration
        if 'type enumeration' in leaf_content:
            enum_start = leaf_content.find('type enumeration')
            if enum_start != -1:
                brace_start = leaf_content.find('{', enum_start)
                if brace_start != -1:
                    brace_end = self.find_balanced_braces(leaf_content, brace_start)
                    if brace_end != -1:
                        enum_body = leaf_content[brace_start + 1:brace_end]
                        enum_values = []
                        for enum_match in re.finditer(r'\benum\s+([^\s{;]+)', enum_body):
                            enum_val = enum_match.group(1).strip('"\'')
                            enum_values.append(enum_val)
                        if enum_values:
                            schema = {'type': 'string', 'enum': enum_values}

        if 'enum' not in schema:
            type_match = re.search(r'\btype\s+(\S+)(?:\s*\{([^}]*)\})?', leaf_content)
            if type_match:
                yang_type = type_match.group(1).split(':')[-1].rstrip(';')
                
                type_mapping = {
                    'string': {'type': 'string'},
                    'uint8': {'type': 'integer', 'minimum': 0, 'maximum': 255},
                    'uint16': {'type': 'integer', 'minimum': 0, 'maximum': 65535},
                    'uint32': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
                    'uint64': {'type': 'integer', 'minimum': 0},
                    'int8': {'type': 'integer', 'minimum': -128, 'maximum': 127},
                    'int16': {'type': 'integer', 'minimum': -32768, 'maximum': 32767},
                    'int32': {'type': 'integer', 'minimum': -2147483648, 'maximum': 2147483647},
                    'int64': {'type': 'integer'},
                    'boolean': {'type': 'boolean'},
                    'empty': {'type': 'boolean', 'description': 'Presence container marker'},
                    'binary': {'type': 'string', 'format': 'byte'},
                    'decimal64': {'type': 'number'},
                    'union': {'type': 'string', 'description': 'Union type'},
                    'ipv4-address': {'type': 'string', 'format': 'ipv4'},
                    'ipv6-address': {'type': 'string', 'format': 'ipv6'},
                    'ip-address': {'type': 'string', 'description': 'IPv4 or IPv6 address'},
                    'ipv4-prefix': {'type': 'string', 'pattern': r'^[\d.]+/\d+$'},
                    'ipv6-prefix': {'type': 'string', 'description': 'IPv6 prefix'},
                    'mac-address': {'type': 'string', 'pattern': r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'},
                }
                schema = type_mapping.get(yang_type, {'type': 'string'}).copy()

        # Extract description
        desc_match = re.search(r'\bdescription\s+"([^"]+)"', leaf_content)
        if desc_match:
            schema['description'] = desc_match.group(1).strip()[:500]

        return schema

    def parse_container_or_list(self, content: str, name: str, depth: int = 0) -> Dict[str, Any]:
        """Recursively parse container/list structure"""
        if depth > 15:
            return {'type': 'object', 'description': f'{name} (depth limit)'}

        properties = {}

        # Handle 'uses' statements
        for uses_match in re.finditer(r'\buses\s+(\S+);', content):
            grouping_ref = uses_match.group(1).split(':')[-1]
            if grouping_ref in self.groupings_cache:
                grouping_schema = self.parse_container_or_list(
                    self.groupings_cache[grouping_ref], grouping_ref, depth + 1
                )
                if 'properties' in grouping_schema:
                    properties.update(grouping_schema['properties'])

        # Parse leaves
        pos = 0
        while True:
            leaf_match = re.search(r'\bleaf\s+(\S+)\s*\{', content[pos:])
            if not leaf_match:
                break
            leaf_name = leaf_match.group(1)
            leaf_start = pos + leaf_match.end() - 1
            leaf_end = self.find_balanced_braces(content, leaf_start)
            if leaf_end == -1:
                pos += leaf_match.end()
                continue
            leaf_body = content[leaf_start + 1:leaf_end]
            properties[leaf_name] = self.parse_leaf(leaf_body, leaf_name)
            pos = leaf_end + 1

        # Parse leaf-lists
        pos = 0
        while True:
            ll_match = re.search(r'\bleaf-list\s+(\S+)\s*\{', content[pos:])
            if not ll_match:
                break
            ll_name = ll_match.group(1)
            ll_start = pos + ll_match.end() - 1
            ll_end = self.find_balanced_braces(content, ll_start)
            if ll_end == -1:
                pos += ll_match.end()
                continue
            ll_body = content[ll_start + 1:ll_end]
            item_schema = self.parse_leaf(ll_body, ll_name)
            properties[ll_name] = {'type': 'array', 'items': item_schema}
            pos = ll_end + 1

        # Parse nested containers
        pos = 0
        while True:
            cont_match = re.search(r'\bcontainer\s+(\S+)\s*\{', content[pos:])
            if not cont_match:
                break
            cont_name = cont_match.group(1)
            cont_start = pos + cont_match.end() - 1
            cont_end = self.find_balanced_braces(content, cont_start)
            if cont_end == -1:
                pos += cont_match.end()
                continue
            cont_body = content[cont_start + 1:cont_end]
            nested_schema = self.parse_container_or_list(cont_body, cont_name, depth + 1)
            properties[cont_name] = nested_schema
            pos = cont_end + 1

        # Parse nested lists
        pos = 0
        while True:
            list_match = re.search(r'\blist\s+(\S+)\s*\{', content[pos:])
            if not list_match:
                break
            list_name = list_match.group(1)
            list_start = pos + list_match.end() - 1
            list_end = self.find_balanced_braces(content, list_start)
            if list_end == -1:
                pos += list_match.end()
                continue
            list_body = content[list_start + 1:list_end]
            item_schema = self.parse_container_or_list(list_body, list_name, depth + 1)
            properties[list_name] = {'type': 'array', 'items': item_schema}
            pos = list_end + 1

        schema = {'type': 'object'}
        if properties:
            schema['properties'] = properties
        return schema

    def _remove_groupings_and_typedefs(self, content: str) -> str:
        """Remove grouping and typedef blocks"""
        result = content

        for pattern in [r'\bgrouping\s+\S+\s*\{', r'\btypedef\s+\S+\s*\{']:
            pos = 0
            while True:
                match = re.search(pattern, result[pos:])
                if not match:
                    break
                block_start = pos + match.start()
                brace_start = pos + match.end() - 1
                brace_end = self.find_balanced_braces(result, brace_start)
                if brace_end == -1:
                    pos += match.end()
                    continue
                result = result[:block_start] + ' ' * (brace_end + 1 - block_start) + result[brace_end + 1:]
                pos = block_start + 1

        return result

    def extract_nested_paths(self, content: str, parent_path: str, depth: int = 0, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Recursively extract all nested paths from YANG content"""
        paths = []
        
        if depth > max_depth:
            return paths
        
        # Extract nested containers
        pos = 0
        while True:
            cont_match = re.search(r'\bcontainer\s+(\S+)\s*\{', content[pos:])
            if not cont_match:
                break
                
            cont_name = cont_match.group(1)
            cont_start = pos + cont_match.end() - 1
            cont_end = self.find_balanced_braces(content, cont_start)
            
            if cont_end == -1:
                pos += cont_match.end()
                continue
                
            cont_body = content[cont_start + 1:cont_end]
            
            # Get description
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', cont_body)
            description = desc_match.group(1)[:200] if desc_match else f"{cont_name} configuration"
            
            # Parse schema
            schema = self.parse_container_or_list(cont_body, cont_name, 0)
            
            full_path = f"{parent_path}/{cont_name}"
            paths.append({
                'path': full_path,
                'name': cont_name,
                'description': description,
                'schema': schema,
                'is_list': False,
                'depth': depth
            })
            
            # Recursively extract nested paths
            nested_paths = self.extract_nested_paths(cont_body, full_path, depth + 1, max_depth)
            paths.extend(nested_paths)
            
            pos = cont_end + 1
        
        # Extract nested lists
        pos = 0
        while True:
            list_match = re.search(r'\blist\s+(\S+)\s*\{', content[pos:])
            if not list_match:
                break
                
            list_name = list_match.group(1)
            list_start = pos + list_match.end() - 1
            list_end = self.find_balanced_braces(content, list_start)
            
            if list_end == -1:
                pos += list_match.end()
                continue
                
            list_body = content[list_start + 1:list_end]
            
            # Get key
            key_match = re.search(r'\bkey\s+"([^"]+)"', list_body)
            key_name = key_match.group(1).split()[0] if key_match else "id"
            
            # Get description
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', list_body)
            description = desc_match.group(1)[:200] if desc_match else f"{list_name} list"
            
            # Parse schema
            schema = self.parse_container_or_list(list_body, list_name, 0)
            
            full_path_collection = f"{parent_path}/{list_name}"
            full_path_item = f"{parent_path}/{list_name}={{{key_name}}}"
            
            # Collection endpoint
            paths.append({
                'path': full_path_collection,
                'name': list_name,
                'description': f"{description} (collection)",
                'schema': {'type': 'array', 'items': schema},
                'is_list': True,
                'is_collection': True,
                'depth': depth
            })
            
            # Individual item endpoint
            paths.append({
                'path': full_path_item,
                'name': f"{list_name}-item",
                'description': description,
                'schema': schema,
                'is_list': True,
                'is_collection': False,
                'key': key_name,
                'depth': depth
            })
            
            # Recursively extract nested paths from list items
            nested_paths = self.extract_nested_paths(list_body, full_path_item, depth + 1, max_depth)
            paths.extend(nested_paths)
            
            pos = list_end + 1
        
        # Extract leaf nodes (only at depth 0 for top-level configs like hostname)
        if depth == 0:
            pos = 0
            while True:
                # Match leaf pattern: "leaf name { ... }"
                leaf_match = re.search(r'\bleaf\s+(\S+)\s*\{', content[pos:])
                if not leaf_match:
                    break
                    
                leaf_name = leaf_match.group(1)
                leaf_start = pos + leaf_match.end() - 1
                leaf_end = self.find_balanced_braces(content, leaf_start)
                
                if leaf_end == -1:
                    pos += leaf_match.end()
                    continue
                    
                leaf_body = content[leaf_start + 1:leaf_end]
                
                # Get type
                type_match = re.search(r'\btype\s+(\S+)', leaf_body)
                yang_type = type_match.group(1) if type_match else "string"
                
                # Map YANG type to JSON schema type
                if yang_type in ['string', 'inet:ipv4-address', 'inet:ipv6-address', 'inet:domain-name']:
                    json_type = 'string'
                elif yang_type in ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64']:
                    json_type = 'integer'
                elif yang_type == 'boolean':
                    json_type = 'boolean'
                elif yang_type == 'empty':
                    json_type = 'boolean'  # empty leaf becomes boolean
                else:
                    json_type = 'string'
                
                # Get description
                desc_match = re.search(r'\bdescription\s+"([^"]+)"', leaf_body)
                description = desc_match.group(1)[:200] if desc_match else f"{leaf_name} configuration"
                
                # Create schema
                schema = {'type': json_type}
                
                full_path = f"{parent_path}/{leaf_name}"
                paths.append({
                    'path': full_path,
                    'name': leaf_name,
                    'description': description,
                    'schema': schema,
                    'is_list': False,
                    'is_leaf': True,
                    'depth': depth
                })
                
                pos = leaf_end + 1
        
        return paths

    def extract_paths_from_native(self, content: str) -> List[Dict[str, Any]]:
        """Extract ALL paths from the native container recursively"""
        paths = []
        
        # Find the main 'native' container
        native_match = re.search(r'\bcontainer\s+native\s*\{', content)
        if not native_match:
            return paths
            
        native_start = native_match.end() - 1
        native_end = self.find_balanced_braces(content, native_start)
        if native_end == -1:
            return paths
            
        native_body = content[native_start + 1:native_end]
        
        # Remove groupings to get actual data nodes
        cleaned_content = self._remove_groupings_and_typedefs(native_body)
        
        # Extract all paths recursively
        paths = self.extract_nested_paths(cleaned_content, "native", depth=0, max_depth=10)
            
        return paths

    def categorize_path(self, path_name: str) -> str:
        """Determine category for a path - check specific categories first"""
        name_lower = path_name.lower()
        
        # Check if this is a top-level leaf (core settings)
        # These are paths like "native/hostname", "native/version", "native/config-register"
        core_leafs = ['native/version', 'native/hostname', 'native/config-register', 
                     'native/boot-start-marker', 'native/boot-end-marker', 
                     'native/captive-portal-bypass', 'native/aqm-register-fnf', 
                     'native/disable-eadi']
        if name_lower in core_leafs:
            return 'core'
        
        # Priority order: check specific categories before generic ones
        priority_categories = ['interfaces', 'crypto', 'platform', 'monitor', 'routing', 
                              'switching', 'security', 'services', 'qos', 'mpls', 'vpn', 
                              'wireless', 'call-home', 'voice', 'system']
        
        for category in priority_categories:
            keywords = self.category_keywords.get(category, [])
            for keyword in keywords:
                if keyword.lower() in name_lower:
                    return category
        
        return 'system'  # Default category

    def create_openapi_spec(self, category: str, paths: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create OpenAPI 3.0 spec for a category"""
        
        category_titles = {
            'core': 'Native - Core System Settings',
            'interfaces': 'Native - Interfaces',
            'routing': 'Native - Routing Protocols',
            'security': 'Native - Security & AAA',
            'crypto': 'Native - Cryptography & PKI',
            'switching': 'Native - Switching & VLANs',
            'services': 'Native - Network Services',
            'qos': 'Native - QoS & Policy',
            'mpls': 'Native - MPLS & TE',
            'vpn': 'Native - VPN & Tunnels',
            'wireless': 'Native - Wireless',
            'platform': 'Native - Platform & Hardware',
            'call-home': 'Native - Call Home & Licensing',
            'monitor': 'Native - Monitoring & Analytics',
            'voice': 'Native - Voice & Telephony',
            'system': 'Native - System & Management'
        }
        
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': category_titles.get(category, f'Native - {category.title()}'),
                'description': f"Cisco IOS-XE Native Configuration - {category.title()}\n\n"
                              f"Extracted from Cisco-IOS-XE-native YANG module.\n"
                              f"**Category:** {category.title()}\n"
                              f"**Paths:** {len(paths)}\n\n"
                              "**HTTP Methods:**\n"
                              "- GET: Retrieve configuration\n"
                              "- PUT: Replace configuration\n"
                              "- PATCH: Merge/update configuration\n"
                              "- DELETE: Remove configuration",
                'version': '17.18.1'
            },
            'servers': [{
                'url': 'https://{device}/restconf',
                'variables': {
                    'device': {
                        'default': 'router.example.com',
                        'description': 'Device IP or hostname'
                    }
                }
            }],
            'paths': {},
            'components': {
                'securitySchemes': {
                    'basicAuth': {'type': 'http', 'scheme': 'basic'}
                },
                'schemas': {}
            },
            'security': [{'basicAuth': []}],
            'tags': [{'name': category, 'description': category_titles.get(category, category)}]
        }
        
        for path_info in paths:
            restconf_path = f"/data/Cisco-IOS-XE-native:{path_info['path']}"
            schema_name = f"native-{path_info['name'].replace('/', '-')}"
            
            # Store schema
            spec['components']['schemas'][schema_name] = path_info['schema']
            
            # Create operations
            operations = {
                'get': {
                    'summary': f"Get {path_info['name']}",
                    'description': path_info['description'],
                    'operationId': f"get-{schema_name}",
                    'tags': [category],
                    'responses': {
                        '200': {
                            'description': 'Success',
                            'content': {
                                'application/yang-data+json': {
                                    'schema': path_info['schema'],
                                    'example': self.create_example_data(path_info['schema'], path_info['name'])
                                }
                            }
                        },
                        '401': {'description': 'Unauthorized'},
                        '404': {'description': 'Not found'}
                    }
                },
                'put': {
                    'summary': f"Replace {path_info['name']}",
                    'description': f"Replace entire {path_info['name']} configuration",
                    'operationId': f"put-{schema_name}",
                    'tags': [category],
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/yang-data+json': {
                                'schema': path_info['schema'],
                                'example': self.create_example_data(path_info['schema'], path_info['name'])
                            }
                        }
                    },
                    'responses': {
                        '201': {'description': 'Created'},
                        '204': {'description': 'Updated'},
                        '400': {'description': 'Bad request'},
                        '401': {'description': 'Unauthorized'}
                    }
                },
                'patch': {
                    'summary': f"Update {path_info['name']}",
                    'description': f"Merge updates to {path_info['name']} configuration",
                    'operationId': f"patch-{schema_name}",
                    'tags': [category],
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/yang-data+json': {
                                'schema': path_info['schema'],
                                'example': self.create_example_data(path_info['schema'], path_info['name'])
                            }
                        }
                    },
                    'responses': {
                        '204': {'description': 'Updated'},
                        '400': {'description': 'Bad request'},
                        '401': {'description': 'Unauthorized'}
                    }
                },
                'delete': {
                    'summary': f"Delete {path_info['name']}",
                    'description': f"Remove {path_info['name']} configuration",
                    'operationId': f"delete-{schema_name}",
                    'tags': [category],
                    'responses': {
                        '204': {'description': 'Deleted'},
                        '401': {'description': 'Unauthorized'},
                        '404': {'description': 'Not found'}
                    }
                }
            }
            
            spec['paths'][restconf_path] = operations
            
        return spec

    def load_all_yang_content(self) -> str:
        """Load and combine the native module and all its submodules"""
        combined_content = ""
        
        # Load main native module
        native_file = self.yang_dir / "Cisco-IOS-XE-native.yang"
        if native_file.exists():
            content = self.read_yang_file(native_file)
            combined_content += content
            
            # Extract included submodules
            for include_match in re.finditer(r'include\s+(\S+);', content):
                submodule_name = include_match.group(1)
                submodule_file = self.yang_dir / f"{submodule_name}.yang"
                if submodule_file.exists():
                    sub_content = self.read_yang_file(submodule_file)
                    combined_content += "\n" + sub_content
                    print(f"  Loaded submodule: {submodule_name}")
        
        return combined_content

    def generate_all(self):
        """Generate OpenAPI specs for all native categories"""
        print(f"\n{'='*70}")
        print("Native YANG to OpenAPI 3.0 Generator v2")
        print(f"{'='*70}\n")
        
        # Load all content
        print("Loading Cisco-IOS-XE-native module and submodules...")
        content = self.load_all_yang_content()
        
        if not content:
            print("ERROR: Could not load native YANG module")
            return
            
        print(f"Total content: {len(content)} characters")
        
        # Extract groupings first
        print("\nExtracting groupings...")
        self.extract_groupings(content)
        print(f"  Found {len(self.groupings_cache)} groupings")
        
        # Extract paths from native container
        print("\nExtracting paths from native container...")
        all_paths = self.extract_paths_from_native(content)
        print(f"  Found {len(all_paths)} total paths")
        
        # Categorize paths
        categorized_paths: Dict[str, List] = {cat: [] for cat in self.category_keywords.keys()}
        
        for path_info in all_paths:
            category = self.categorize_path(path_info['path'])  # Use 'path' not 'name' for categorization
            categorized_paths[category].append(path_info)
        
        # Generate specs per category
        print("\nGenerating OpenAPI specs by category:")
        total_specs = 0
        manifest_modules = []
        MAX_FILE_SIZE_MB = 5
        
        for category, paths in categorized_paths.items():
            if not paths:
                continue
            
            # Try generating the spec
            spec = self.create_openapi_spec(category, paths)
            spec_json = json.dumps(spec, indent=2)
            size_mb = len(spec_json.encode('utf-8')) / (1024 * 1024)
            
            # If file is too large, split it alphabetically
            if size_mb > MAX_FILE_SIZE_MB:
                print(f"  * {category}: {len(paths)} paths ({size_mb:.2f} MB) - SPLITTING...")
                
                # Sort paths alphabetically by name
                sorted_paths = sorted(paths, key=lambda p: p['name'].lower())
                
                # Calculate number of chunks needed (be conservative)
                num_chunks = int(size_mb / (MAX_FILE_SIZE_MB * 0.8)) + 1  # Target 80% of max to be safe
                chunk_size = len(sorted_paths) // num_chunks
                if chunk_size == 0:
                    chunk_size = 1
                
                chunk_num = 0
                for i in range(num_chunks):
                    start_idx = i * chunk_size
                    end_idx = (i + 1) * chunk_size if i < num_chunks - 1 else len(sorted_paths)
                    chunk_paths = sorted_paths[start_idx:end_idx]
                    
                    if not chunk_paths:
                        continue
                    
                    chunk_num += 1
                    chunk_spec = self.create_openapi_spec(f"{category} (Part {chunk_num})", chunk_paths)
                    # Update title to indicate split
                    chunk_spec['info']['title'] = chunk_spec['info']['title'].replace(f"Native - {category.title()}", 
                                                                                      f"Native - {category.title()} (Part {chunk_num})")
                    
                    output_file = self.output_dir / f"native-{category}-{chunk_num}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(chunk_spec, f, indent=2)
                    
                    chunk_size_mb = len(json.dumps(chunk_spec, indent=2).encode('utf-8')) / (1024 * 1024)
                    print(f"    Part {chunk_num}: {len(chunk_paths)} paths ({chunk_size_mb:.2f} MB) -> {output_file.name}")
                    total_specs += 1
                    manifest_modules.append(f"native-{category}-{chunk_num}")
            else:
                # File is small enough, write as single file
                # Use 00 prefix for core to ensure it appears first
                file_prefix = "native-00-core" if category == "core" else f"native-{category}"
                output_file = self.output_dir / f"{file_prefix}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(spec, f, indent=2)
                
                print(f"  * {category}: {len(paths)} paths ({size_mb:.2f} MB) -> {output_file.name}")
                total_specs += 1
                module_name = file_prefix.replace("native-", "").replace("-", "")
                manifest_modules.append(file_prefix.replace("native-", ""))
        
        
        # Generate manifest
        manifest = {
            'total_modules': total_specs,
            'total_paths': len(all_paths),
            'modules': sorted(manifest_modules),
            'generator': 'generate_native_openapi_v2.py',
            'source': 'Cisco-IOS-XE-native.yang',
            'version': '17.18.1'
        }
        
        manifest_file = self.output_dir / 'manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"Generation Complete: {total_specs} category specs, {len(all_paths)} total paths")
        print(f"{'='*70}\n")

def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    yang_dir = script_dir.parent / 'references' / '17181-YANG-modules'
    output_dir = script_dir.parent / 'swagger-native-config-model' / 'api'
    
    converter = NativeToOpenAPI(str(yang_dir), str(output_dir))
    converter.generate_all()

if __name__ == '__main__':
    main()
