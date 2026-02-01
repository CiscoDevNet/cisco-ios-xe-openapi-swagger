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
            'interfaces': ['interface', 'GigabitEthernet', 'TenGigabitEthernet', 'Loopback', 
                          'Tunnel', 'Vlan', 'Port-channel', 'FastEthernet', 'Ethernet',
                          'BDI', 'Serial', 'Dialer', 'Virtual-Template'],
            'routing': ['router', 'bgp', 'ospf', 'eigrp', 'rip', 'isis', 'ip route', 
                       'ipv6 route', 'route-map', 'prefix-list'],
            'security': ['access-list', 'aaa', 'crypto', 'zone', 'parameter-map', 
                        'class-map', 'policy-map', 'acl', 'key chain', 'enable', 'username'],
            'switching': ['vlan', 'spanning-tree', 'switchport', 'channel-group', 
                         'mac-address-table', 'errdisable'],
            'services': ['dhcp', 'nat', 'ntp', 'snmp', 'logging', 'cdp', 'lldp', 
                        'dns', 'domain', 'ip domain', 'archive'],
            'qos': ['qos', 'service-policy', 'mls qos', 'class', 'policy'],
            'mpls': ['mpls', 'ldp', 'traffic-eng', 'segment-routing'],
            'vpn': ['tunnel', 'ipsec', 'isakmp', 'ikev2', 'l2tp', 'gre', 'dmvpn'],
            'wireless': ['wireless', 'wlan', 'ap ', 'dot11'],
            'system': ['hostname', 'banner', 'boot', 'clock', 'version', 'service', 
                      'memory', 'scheduler', 'process', 'platform', 'license', 'line']
        }

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

    def extract_paths_from_native(self, content: str) -> List[Dict[str, Any]]:
        """Extract paths from the native container"""
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
        
        # Extract top-level containers within native
        pos = 0
        while True:
            cont_match = re.search(r'\bcontainer\s+(\S+)\s*\{', cleaned_content[pos:])
            if not cont_match:
                break
                
            cont_name = cont_match.group(1)
            cont_start = pos + cont_match.end() - 1
            cont_end = self.find_balanced_braces(cleaned_content, cont_start)
            
            if cont_end == -1:
                pos += cont_match.end()
                continue
                
            cont_body = cleaned_content[cont_start + 1:cont_end]
            
            # Get description
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', cont_body)
            description = desc_match.group(1)[:200] if desc_match else f"{cont_name} configuration"
            
            # Parse schema
            schema = self.parse_container_or_list(cont_body, cont_name, 0)
            
            paths.append({
                'path': f"native/{cont_name}",
                'name': cont_name,
                'description': description,
                'schema': schema,
                'is_list': False
            })
            
            pos = cont_end + 1
        
        # Extract top-level lists within native
        pos = 0
        while True:
            list_match = re.search(r'\blist\s+(\S+)\s*\{', cleaned_content[pos:])
            if not list_match:
                break
                
            list_name = list_match.group(1)
            list_start = pos + list_match.end() - 1
            list_end = self.find_balanced_braces(cleaned_content, list_start)
            
            if list_end == -1:
                pos += list_match.end()
                continue
                
            list_body = cleaned_content[list_start + 1:list_end]
            
            # Get key
            key_match = re.search(r'\bkey\s+"([^"]+)"', list_body)
            key_name = key_match.group(1).split()[0] if key_match else "id"
            
            # Get description
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', list_body)
            description = desc_match.group(1)[:200] if desc_match else f"{list_name} list"
            
            # Parse schema
            schema = self.parse_container_or_list(list_body, list_name, 0)
            
            # Collection endpoint
            paths.append({
                'path': f"native/{list_name}",
                'name': list_name,
                'description': f"{description} (collection)",
                'schema': {'type': 'array', 'items': schema},
                'is_list': True,
                'is_collection': True
            })
            
            # Individual item endpoint
            paths.append({
                'path': f"native/{list_name}={{{key_name}}}",
                'name': f"{list_name}-item",
                'description': description,
                'schema': schema,
                'is_list': True,
                'is_collection': False,
                'key': key_name
            })
            
            pos = list_end + 1
            
        return paths

    def categorize_path(self, path_name: str) -> str:
        """Determine category for a path"""
        name_lower = path_name.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in name_lower:
                    return category
        
        return 'system'  # Default category

    def create_openapi_spec(self, category: str, paths: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create OpenAPI 3.0 spec for a category"""
        
        category_titles = {
            'interfaces': 'Native - Interfaces',
            'routing': 'Native - Routing Protocols',
            'security': 'Native - Security & AAA',
            'switching': 'Native - Switching & VLANs',
            'services': 'Native - Network Services',
            'qos': 'Native - QoS & Policy',
            'mpls': 'Native - MPLS & TE',
            'vpn': 'Native - VPN & Tunnels',
            'wireless': 'Native - Wireless',
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
                                    'schema': {'$ref': f"#/components/schemas/{schema_name}"}
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
                                'schema': {'$ref': f"#/components/schemas/{schema_name}"}
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
                                'schema': {'$ref': f"#/components/schemas/{schema_name}"}
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
            category = self.categorize_path(path_info['name'])
            categorized_paths[category].append(path_info)
        
        # Generate specs per category
        print("\nGenerating OpenAPI specs by category:")
        total_specs = 0
        manifest_modules = []
        
        for category, paths in categorized_paths.items():
            if not paths:
                continue
                
            spec = self.create_openapi_spec(category, paths)
            
            output_file = self.output_dir / f"native-{category}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2)
            
            print(f"  ✓ {category}: {len(paths)} paths -> {output_file.name}")
            total_specs += 1
            manifest_modules.append(f"native-{category}")
        
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
