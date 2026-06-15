#!/usr/bin/env python3
"""
Convert IETF YANG modules to OpenAPI 3.0 specifications.
Properly parses YANG structure using tree walking.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yang_parse import (
    find_balanced_braces as _shared_find_balanced_braces,
    iter_top_level_blocks as _shared_iter_top_level_blocks,
    iter_top_level_uses as _shared_iter_top_level_uses,
    resolve_includes as _shared_resolve_includes,
    is_submodule as _shared_is_submodule,
)


class IETFToOpenAPI:
    """Convert IETF YANG modules to OpenAPI 3.0 with proper YANG parsing"""

    def __init__(self, yang_dir: str, output_dir: str):
        self.yang_dir = Path(yang_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.groupings_cache = {}
        self.processed_modules = []
        self.total_paths = 0

    def create_example_data(self, schema: Dict[str, Any], property_name: str = "") -> Any:
        """Generate realistic example data based on schema and property name"""
        if not schema:
            return "example-value"
        
        schema_type = schema.get('type', 'string')
        
        # Handle arrays - generate 3 items for better examples
        if schema_type == 'array':
            items_schema = schema.get('items', {})
            example_items = []
            for i in range(3):
                item = self.create_example_data(items_schema, property_name)
                # Vary data for each entry
                if isinstance(item, dict):
                    # Update index fields
                    for key in list(item.keys()):
                        if 'index' in key.lower() or 'id' in key.lower():
                            if isinstance(item[key], str):
                                item[key] = str(i + 1)
                            elif isinstance(item[key], int):
                                item[key] = i + 1
                    # Update interface-specific fields
                    if 'name' in item and 'interface' in property_name.lower():
                        item['name'] = f"GigabitEthernet0/0/{i}"
                    if 'address' in item and 'ip' in str(item.keys()).lower():
                        item['address'] = f"192.168.{i+1}.1"
                example_items.append(item)
            return example_items
        
        # Handle objects
        if schema_type == 'object':
            example_obj = {}
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                example_obj[prop_name] = self.create_example_data(prop_schema, prop_name)
            return example_obj
        
        # Context-aware examples based on property name
        name_lower = property_name.lower()
        
        if schema_type == 'boolean':
            return True
        
        if schema_type == 'integer' or schema_type == 'number':
            if 'port' in name_lower:
                return 830
            if 'timeout' in name_lower:
                return 30
            if 'mtu' in name_lower:
                return 1500
            if 'id' in name_lower or 'index' in name_lower:
                return 1
            return schema.get('minimum', 0)
        
        # String type with context awareness
        if 'ip' in name_lower or 'addr' in name_lower:
            if 'ipv6' in name_lower:
                return "2001:db8::1"
            return "192.168.1.1"
        if 'interface' in name_lower or 'name' in name_lower:
            return "GigabitEthernet0/0/0"
        if 'hostname' in name_lower or 'host' in name_lower:
            return "devnetsandboxiosxec9k"
        if 'username' in name_lower or 'user' in name_lower:
            return "admin"
        if 'password' in name_lower:
            return "********"
        if 'description' in name_lower or 'descr' in name_lower:
            return "Example configuration"
        if 'type' in name_lower:
            return "ethernet"
        if 'status' in name_lower or 'state' in name_lower:
            return "up"
        
        return "example-string"

    def find_balanced_braces(self, text: str, start_pos: int) -> int:
        return _shared_find_balanced_braces(text, start_pos)

    def extract_groupings(self, content: str):
        """Cache all top-level groupings (RFC 7950 §7.12). Nested groupings
        inside other groupings are intentionally ignored — `uses` looks them
        up by simple name and only one definition can win."""
        for name, body in _shared_iter_top_level_blocks(content, 'grouping'):
            self.groupings_cache[name] = body

    def read_yang_file(self, filepath: Path) -> str:
        """Read YANG file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            return ""

    def extract_module_name(self, content: str) -> str:
        """Extract module name from YANG content"""
        match = re.search(r'^\s*module\s+([^\s{]+)', content, re.MULTILINE)
        return match.group(1) if match else ""

    def extract_description(self, content: str) -> str:
        """Extract module description"""
        module_match = re.search(r'^\s*module\s+', content, re.MULTILINE)
        if module_match:
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', content[module_match.end():module_match.end() + 2000])
            if desc_match:
                return desc_match.group(1).strip()
        return "IETF standard YANG data model"

    def parse_leaf(self, leaf_content: str, leaf_name: str) -> Dict[str, Any]:
        """Parse a YANG leaf and return OpenAPI schema"""
        schema = {'type': 'string'}  # Default

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
                            schema = {
                                'type': 'string',
                                'enum': enum_values
                            }

        if 'enum' not in schema:
            # Extract type
            type_match = re.search(r'\btype\s+(\S+)(?:\s*\{([^}]*)\})?', leaf_content)
            if type_match:
                yang_type = type_match.group(1).split(':')[-1].rstrip(';')
                type_constraints = type_match.group(2) if type_match.group(2) else ""

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
                    'empty': {'type': 'object', 'description': 'Empty object or [null] for presence'},
                    'binary': {'type': 'string', 'format': 'byte'},
                    'decimal64': {'type': 'number'},
                    'union': {'type': 'string', 'description': 'Union type - accepts multiple formats'},
                    'ipv4-address': {'type': 'string', 'pattern': '^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$'},
                    'ipv6-address': {'type': 'string', 'format': 'ipv6'},
                    'ip-address': {'type': 'string', 'description': 'IPv4 or IPv6 address'},
                    'ipv4-prefix': {'type': 'string', 'pattern': '^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$'},
                    'ipv6-prefix': {'type': 'string', 'description': 'IPv6 prefix'},
                    'ip-prefix': {'type': 'string', 'description': 'IPv4 or IPv6 prefix'},
                    'mac-address': {'type': 'string', 'pattern': '^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$'},
                    'date-and-time': {'type': 'string', 'format': 'date-time'},
                    'phys-address': {'type': 'string', 'pattern': '^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$'},
                }

                schema = type_mapping.get(yang_type, {'type': 'string'}).copy()

                # Handle range constraints
                if type_constraints:
                    range_match = re.search(r'\brange\s+"([^"]+)"', type_constraints)
                    if range_match:
                        range_val = range_match.group(1)
                        if '..' in range_val:
                            parts = range_val.split('|')[0].strip()
                            if '..' in parts:
                                min_val, max_val = parts.split('..', 1)
                                try:
                                    schema['minimum'] = int(min_val.strip())
                                    if max_val.strip() and max_val.strip() != 'max':
                                        schema['maximum'] = int(max_val.strip())
                                except ValueError:
                                    pass

        # Extract description
        desc_match = re.search(r'\bdescription\s+"([^"]+)"', leaf_content)
        if desc_match:
            schema['description'] = desc_match.group(1).strip()

        # Check if mandatory
        if re.search(r'\bmandatory\s+true\b', leaf_content):
            schema['x-mandatory'] = True

        return schema

    def parse_container_or_grouping(self, content: str, name: str, depth: int = 0,
                                    _seen_groupings: set = None) -> Dict[str, Any]:
        """Recursively parse container/grouping"""
        # Bound recursion to avoid pathological inline-schema blow-up. Some IETF
        # models (notably ietf-ospf) nest lists-within-lists very deeply and, since
        # every nested node also becomes its own RESTCONF path carrying a full inline
        # copy of its subtree, an unbounded expansion is O(N^2) in document size
        # (ietf-ospf reached 70 MB and broke the browser). Real config rarely needs
        # more than ~8 levels; deeper nodes are reachable via their own dedicated paths.
        if depth > 8:
            return {'type': 'object', 'description': f'{name} (truncated; use the dedicated sub-path)'}

        if _seen_groupings is None:
            _seen_groupings = frozenset()

        properties = {}
        required = []

        # Resolve 'uses' statements (RFC 7950 §7.13) — top-level only.
        # Guard against recursive grouping expansion: a grouping that is already
        # being expanded on the current path is skipped to avoid combinatorial /
        # cyclic blow-up (e.g. ietf-ospf groupings reference each other heavily).
        for grouping_name in _shared_iter_top_level_uses(content):
            if grouping_name in _seen_groupings:
                continue
            grouping_content = self.groupings_cache.get(grouping_name)
            if grouping_content is None:
                continue
            grouping_schema = self.parse_container_or_grouping(
                grouping_content, grouping_name, depth + 1,
                _seen_groupings | {grouping_name})
            if 'properties' in grouping_schema and grouping_schema['properties']:
                properties.update(grouping_schema['properties'])
            if 'required' in grouping_schema:
                required.extend(grouping_schema['required'])

        # Parse leaves (RFC 7950 §7.6) — top-level only.
        for leaf_name, leaf_body in _shared_iter_top_level_blocks(content, 'leaf'):
            leaf_schema = self.parse_leaf(leaf_body, leaf_name)
            if leaf_schema.pop('x-mandatory', False):
                required.append(leaf_name)
            properties[leaf_name] = leaf_schema

        # Parse leaf-lists (RFC 7950 §7.7) — top-level only.
        for ll_name, ll_body in _shared_iter_top_level_blocks(content, 'leaf-list'):
            item_schema = self.parse_leaf(ll_body, ll_name)
            item_schema.pop('x-mandatory', None)
            properties[ll_name] = {
                'type': 'array',
                'items': item_schema
            }

        # Parse nested containers (RFC 7950 §7.5) — top-level only.
        for cont_name, cont_body in _shared_iter_top_level_blocks(content, 'container'):
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', cont_body)
            description = desc_match.group(1) if desc_match else None
            nested_schema = self.parse_container_or_grouping(cont_body, cont_name, depth + 1, _seen_groupings)
            if description:
                nested_schema['description'] = description
            properties[cont_name] = nested_schema

        # Parse nested lists (RFC 7950 §7.8) — top-level only.
        for list_name, list_body in _shared_iter_top_level_blocks(content, 'list'):
            item_schema = self.parse_container_or_grouping(list_body, list_name, depth + 1, _seen_groupings)
            properties[list_name] = {'type': 'array', 'items': item_schema}

        # Parse choices (RFC 7950 §7.9) — top-level only.
        for _choice_name, choice_body in _shared_iter_top_level_blocks(content, 'choice'):
            for case_name, case_body in _shared_iter_top_level_blocks(choice_body, 'case'):
                case_schema = self.parse_container_or_grouping(case_body, f"case-{case_name}", depth + 1, _seen_groupings)
                if 'properties' in case_schema and case_schema['properties']:
                    properties.update(case_schema['properties'])

        schema = {'type': 'object'}
        if properties:
            schema['properties'] = properties
        if required:
            schema['required'] = required

        return schema

    def extract_paths(self, content: str, module_name: str) -> List[Dict[str, Any]]:
        """Extract all top-level containers and lists to create RESTCONF paths"""
        paths = []

        # Find the module's main container
        module_match = re.search(r'^\s*module\s+' + re.escape(module_name), content, re.MULTILINE)
        if not module_match:
            return paths

        # Start searching after module declaration
        search_start = module_match.end()

        # Remove groupings and typedefs to avoid extracting containers from them
        # We only want top-level data containers, not structure definitions
        cleaned_content = self._remove_groupings_and_typedefs(content[search_start:])

        # Extract paths recursively
        self._extract_paths_recursive(cleaned_content, module_name, [], paths, depth=0)

        return paths

    def _remove_groupings_and_typedefs(self, content: str) -> str:
        """Remove grouping and typedef blocks to avoid extracting their internal containers"""
        result = content

        # Remove all grouping blocks
        pos = 0
        while True:
            grouping_match = re.search(r'\bgrouping\s+\S+\s*\{', result[pos:])
            if not grouping_match:
                break

            grouping_start = pos + grouping_match.start()
            brace_start = pos + grouping_match.end() - 1
            brace_end = self.find_balanced_braces(result, brace_start)

            if brace_end == -1:
                pos += grouping_match.end()
                continue

            # Replace the entire grouping block with whitespace to preserve line positions
            result = result[:grouping_start] + ' ' * (brace_end + 1 - grouping_start) + result[brace_end + 1:]
            pos = grouping_start + 1

        # Remove all typedef blocks
        pos = 0
        while True:
            typedef_match = re.search(r'\btypedef\s+\S+\s*\{', result[pos:])
            if not typedef_match:
                break

            typedef_start = pos + typedef_match.start()
            brace_start = pos + typedef_match.end() - 1
            brace_end = self.find_balanced_braces(result, brace_start)

            if brace_end == -1:
                pos += typedef_match.end()
                continue

            # Replace the entire typedef block with whitespace
            result = result[:typedef_start] + ' ' * (brace_end + 1 - typedef_start) + result[brace_end + 1:]
            pos = typedef_start + 1

        return result

    def _extract_paths_recursive(self, content: str, module_name: str, path_parts: List[str],
                                 paths: List[Dict[str, Any]], depth: int = 0, max_depth: int = 8):
        """Recursively extract paths from YANG structure"""
        if depth > max_depth:
            return

        # Parse containers
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

            # Extract description
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', cont_body)
            description = desc_match.group(1) if desc_match else f"{cont_name} container"

            # Create path for this container
            current_path = path_parts + [cont_name]
            path_str = '/'.join(current_path)

            # Parse the container schema
            schema = self.parse_container_or_grouping(cont_body, cont_name, depth)

            paths.append({
                'path': path_str,
                'name': cont_name,
                'description': description,
                'schema': schema,
                'is_list': False
            })

            # Recursively process this container's children
            self._extract_paths_recursive(cont_body, module_name, current_path, paths, depth + 1, max_depth)

            pos = cont_end + 1

        # Parse lists
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

            # Extract description
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', list_body)
            description = desc_match.group(1) if desc_match else f"{list_name} list"

            # Extract key
            key_match = re.search(r'\bkey\s+"([^"]+)"', list_body)
            key_name = key_match.group(1) if key_match else "id"

            # Create path for this list
            current_path = path_parts + [list_name]
            path_str = '/'.join(current_path)

            # Parse the list schema
            schema = self.parse_container_or_grouping(list_body, list_name, depth)

            # Add collection path (without key)
            paths.append({
                'path': path_str,
                'name': list_name,
                'description': f"{description} (collection)",
                'schema': {
                    'type': 'array',
                    'items': schema
                },
                'is_list': True,
                'is_collection': True
            })

            # Add individual item path (with key)
            paths.append({
                'path': f"{path_str}={{{key_name}}}",
                'name': f"{list_name}-item",
                'description': description,
                'schema': schema,
                'is_list': True,
                'is_collection': False,
                'key': key_name
            })

            # Recursively process this list's children
            self._extract_paths_recursive(list_body, module_name, current_path, paths, depth + 1, max_depth)

            pos = list_end + 1

    def create_openapi_spec(self, module_name: str, description: str, paths: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create OpenAPI 3.0 spec"""

        openapi_spec = {
            'openapi': '3.0.0',
            'info': {
                'title': module_name,
                'description': f"{description}\n\n**IETF Standard YANG Model**\n**Module:** `{module_name}`\n**Paths:** {len(paths)}",
                'version': '17.18.1'
            },
            'servers': [{
                'url': 'https://{device}/restconf',
                'variables': {'device': {'default': 'devnetsandboxiosxec9k.cisco.com', 'description': 'Device IP or hostname'}}
            }],
            'paths': {},
            'components': {
                'securitySchemes': {
                    'basicAuth': {'type': 'http', 'scheme': 'basic'}
                },
                'schemas': {}
            },
            'security': [{'basicAuth': []}],
            'tags': [{'name': module_name, 'description': description}]
        }

        # Create OpenAPI paths
        for path_info in paths:
            path = f"/data/{module_name}:{path_info['path']}"
            schema_name = f"{module_name}-{path_info['name']}"

            # Store schema in components
            openapi_spec['components']['schemas'][schema_name] = path_info['schema']

            # Create operations
            operations = {}

            # GET operation (always available)
            operations['get'] = {
                'summary': f"Get {path_info['name']}",
                'description': path_info['description'],
                'operationId': f"get-{path_info['name']}-{len(openapi_spec['paths'])}",
                'tags': [module_name],
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
                    '404': {'description': 'Resource not found'}
                }
            }

            # PUT/PATCH/DELETE for non-collection paths
            if not path_info.get('is_collection', False):
                # PUT - Replace/Create
                operations['put'] = {
                    'summary': f"Create or replace {path_info['name']}",
                    'description': f"Create or replace {path_info['description']}",
                    'operationId': f"put-{path_info['name']}-{len(openapi_spec['paths'])}",
                    'tags': [module_name],
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
                        '400': {'description': 'Bad request'}
                    }
                }

                # PATCH - Modify
                operations['patch'] = {
                    'summary': f"Modify {path_info['name']}",
                    'description': f"Partially modify {path_info['description']}",
                    'operationId': f"patch-{path_info['name']}-{len(openapi_spec['paths'])}",
                    'tags': [module_name],
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
                        '400': {'description': 'Bad request'}
                    }
                }

                # DELETE
                operations['delete'] = {
                    'summary': f"Delete {path_info['name']}",
                    'description': f"Delete {path_info['description']}",
                    'operationId': f"delete-{path_info['name']}-{len(openapi_spec['paths'])}",
                    'tags': [module_name],
                    'responses': {
                        '204': {'description': 'Deleted'},
                        '404': {'description': 'Not found'}
                    }
                }

            # POST for collections (create list entry)
            if path_info.get('is_collection', False):
                # Get the item schema from the array schema
                item_schema = path_info['schema'].get('items', {})
                operations['post'] = {
                    'summary': f"Add {path_info['name']} entry",
                    'description': f"Add a new entry to {path_info['description']}",
                    'operationId': f"post-{path_info['name']}-{len(openapi_spec['paths'])}",
                    'tags': [module_name],
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/yang-data+json': {
                                'schema': item_schema,
                                'example': self.create_example_data(item_schema, path_info['name'])
                            }
                        }
                    },
                    'responses': {
                        '201': {'description': 'Created'},
                        '400': {'description': 'Bad request'}
                    }
                }

            openapi_spec['paths'][path] = operations

        return openapi_spec

    def process_module(self, yang_file: Path) -> bool:
        """Process a single IETF YANG module"""
        try:
            content = self.read_yang_file(yang_file)
            if not content:
                return False

            # Submodules contribute via the parent module's `include` \u2014
            # don't emit a standalone spec for them.
            if _shared_is_submodule(content):
                return False

            # Inline `include <submodule>;` bodies so groupings/containers
            # defined in submodules become visible.
            content = _shared_resolve_includes(yang_file, content)

            module_name = self.extract_module_name(content)
            if not module_name or not module_name.startswith('ietf-'):
                return False

            print(f"Processing {module_name}...")

            # Extract groupings first
            self.extract_groupings(content)

            # Extract description
            description = self.extract_description(content)

            # Extract all paths from the YANG structure
            paths = self.extract_paths(content, module_name)

            if not paths:
                print(f"  ⚠️  No paths found for {module_name}")
                return False

            print(f"  ✓ Found {len(paths)} paths")

            # Create OpenAPI spec
            openapi_spec = self.create_openapi_spec(module_name, description, paths)

            # Write to file
            output_file = self.output_dir / f"{module_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(openapi_spec, f, indent=2)

            print(f"  ✓ Generated {output_file}")
            self.processed_modules.append(module_name)
            self.total_paths += len(paths)
            return True

        except Exception as e:
            print(f"  ✗ Error processing {yang_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_all(self):
        """Process all IETF modules"""
        print(f"\n{'='*70}")
        print("IETF YANG to OpenAPI 3.0 Generator v2")
        print(f"{'='*70}\n")

        # Find all ietf-*.yang files
        yang_files = sorted(self.yang_dir.glob('ietf-*.yang'))

        if not yang_files:
            print(f"No IETF YANG files found in {self.yang_dir}")
            return

        print(f"Found {len(yang_files)} IETF modules\n")

        success_count = 0
        for yang_file in yang_files:
            if self.process_module(yang_file):
                success_count += 1

        print(f"\n{'='*70}")
        print(f"Generation Complete: {success_count}/{len(yang_files)} modules")
        print(f"{'='*70}\n")

        # Create manifest
        manifest = {
            'total_modules': len(self.processed_modules),
            'total_paths': self.total_paths,
            'modules': sorted(self.processed_modules),
            'generator': 'generate_ietf_openapi_v2.py',
            'timestamp': '2026-01-30'
        }

        manifest_file = self.output_dir / 'manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        print(f"Manifest: {manifest_file}")

def main():
    """Main entry point"""
    import sys
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from _version_args import resolve_paths
    yang_dir, output_dir, _ver = resolve_paths('ietf')

    converter = IETFToOpenAPI(str(yang_dir), str(output_dir))
    converter.generate_all()

if __name__ == '__main__':
    main()
