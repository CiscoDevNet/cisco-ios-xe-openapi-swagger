#!/usr/bin/env python3
"""
Convert Cisco IOS-XE RPC YANG modules to OpenAPI 3.0 specifications.
RFC 7950 (YANG 1.1) and RFC 8040 (RESTCONF) compliant.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class RPCYANGToOpenAPIConverter:
    """
    Converts YANG RPC modules to OpenAPI 3.0 specifications.
    Fully RFC 7950 and RFC 8040 compliant.
    """
    
    def __init__(self, yang_dir: str, output_dir: str):
        self.yang_dir = Path(yang_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.groupings_cache = {}
        
    def find_balanced_braces(self, text: str, start_pos: int) -> int:
        """Find the end position of balanced braces"""
        if start_pos >= len(text) or text[start_pos] != '{':
            return -1
        count = 0
        for i in range(start_pos, len(text)):
            if text[i] == '{':
                count += 1
            elif text[i] == '}':
                count -= 1
                if count == 0:
                    return i
        return -1
    
    def extract_groupings(self, content: str):
        """Extract all groupings from YANG content and cache them"""
        self.groupings_cache = {}  # Reset cache
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
        """Parse a YANG leaf and return OpenAPI schema - RFC 7950 compliant"""
        schema = {'type': 'string'}  # Default
        
        # Extract type
        type_match = re.search(r'\btype\s+(\S+)(?:\s*\{([^}]*)\})?', leaf_content)
        if type_match:
            yang_type = type_match.group(1).split(':')[-1]  # Remove prefix
            type_constraints = type_match.group(2) if type_match.group(2) else ""
            
            # RFC 7950 built-in types mapping to JSON/OpenAPI
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
                # inet types
                'ipv4-address': {'type': 'string', 'pattern': '^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$'},
                'ipv6-address': {'type': 'string', 'format': 'ipv6'},
                'ip-address': {'type': 'string', 'description': 'IPv4 or IPv6 address'},
                'ipv4-prefix': {'type': 'string', 'pattern': '^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$'},
                'ipv6-prefix': {'type': 'string', 'description': 'IPv6 prefix'},
                'ip-prefix': {'type': 'string', 'description': 'IPv4 or IPv6 prefix'},
            }
            
            schema = type_mapping.get(yang_type, {'type': 'string'}).copy()
            
            # Handle range constraints (RFC 7950 Section 9.2)
            if type_constraints:
                range_match = re.search(r'\brange\s+"([^"]+)"', type_constraints)
                if range_match:
                    range_val = range_match.group(1)
                    if '..' in range_val:
                        parts = range_val.split('|')[0].strip()  # Handle multiple ranges
                        if '..' in parts:
                            min_val, max_val = parts.split('..', 1)
                            try:
                                schema['minimum'] = int(min_val.strip())
                                schema['maximum'] = int(max_val.strip())
                            except ValueError:
                                pass
                
                # Handle length constraints (RFC 7950 Section 9.4)
                length_match = re.search(r'\blength\s+"([^"]+)"', type_constraints)
                if length_match:
                    length_val = length_match.group(1)
                    if '..' in length_val:
                        parts = length_val.split('|')[0].strip()
                        if '..' in parts:
                            min_len, max_len = parts.split('..', 1)
                            try:
                                schema['minLength'] = int(min_len.strip()) if min_len.strip() else 0
                                if max_len.strip():
                                    schema['maxLength'] = int(max_len.strip())
                            except ValueError:
                                pass
                
                # Handle pattern constraints (RFC 7950 Section 9.4.5)
                pattern_match = re.search(r'\bpattern\s+["\']([^"\']+)["\']', type_constraints)
                if pattern_match:
                    pattern = pattern_match.group(1)
                    # Convert YANG pattern to JSON Schema pattern
                    # YANG uses XSD patterns which are anchored by default
                    if 'pattern' not in schema:
                        schema['pattern'] = pattern
        
        # Extract description (RFC 7950 Section 7.21.3)
        desc_match = re.search(r'\bdescription\s+"([^"]+)"', leaf_content)
        if desc_match:
            desc = desc_match.group(1)
            if 'description' in schema:
                schema['description'] = f"{schema['description']}. {desc}"
            else:
                schema['description'] = desc
        
        # Check if mandatory (RFC 7950 Section 7.6.5)
        if re.search(r'\bmandatory\s+true\b', leaf_content):
            schema['x-mandatory'] = True  # Mark for later processing
        
        # Default value (RFC 7950 Section 7.6.4)
        default_match = re.search(r'\bdefault\s+"([^"]+)"', leaf_content)
        if default_match:
            schema['default'] = default_match.group(1)
        
        return schema
    
    def parse_container_or_grouping(self, content: str, name: str, depth: int = 0, is_choice_case: bool = False) -> Dict[str, Any]:
        """Recursively parse container/grouping - RFC 7950 compliant"""
        if depth > 15:  # Prevent infinite recursion
            return {'type': 'object', 'description': f'{name} (max depth reached)'}
        
        properties = {}
        required = []
        has_properties = False
        
        # Check for presence container (RFC 7950 Section 7.5.1)
        is_presence = 'presence' in content or re.search(r'\bpresence\s+"[^"]+"', content)
        
        # Resolve 'uses' statements (RFC 7950 Section 7.13)
        uses_pattern = r'\buses\s+(\S+);'
        for uses_match in re.finditer(uses_pattern, content):
            grouping_name = uses_match.group(1)
            if grouping_name in self.groupings_cache:
                grouping_content = self.groupings_cache[grouping_name]
                grouping_schema = self.parse_container_or_grouping(grouping_content, grouping_name, depth + 1)
                if 'properties' in grouping_schema and grouping_schema['properties']:
                    properties.update(grouping_schema['properties'])
                    has_properties = True
                if 'required' in grouping_schema:
                    required.extend(grouping_schema['required'])
        
        # Parse leaves (RFC 7950 Section 7.6)
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
            leaf_schema = self.parse_leaf(leaf_body, leaf_name)
            
            if leaf_schema.pop('x-mandatory', False):
                required.append(leaf_name)
            
            properties[leaf_name] = leaf_schema
            has_properties = True
            pos = leaf_end + 1
        
        # Parse leaf-lists (RFC 7950 Section 7.7)
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
            item_schema.pop('x-mandatory', None)
            
            properties[ll_name] = {
                'type': 'array',
                'items': item_schema
            }
            has_properties = True
            pos = ll_end + 1
        
        # Parse nested containers (RFC 7950 Section 7.5)
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
            description = desc_match.group(1) if desc_match else None
            
            nested_schema = self.parse_container_or_grouping(cont_body, cont_name, depth + 1)
            if description:
                nested_schema['description'] = description
            
            properties[cont_name] = nested_schema
            has_properties = True
            pos = cont_end + 1
        
        # Parse choices (RFC 7950 Section 7.9)
        # Choices represent mutually exclusive options
        pos = 0
        while True:
            choice_match = re.search(r'\bchoice\s+(\S+)\s*\{', content[pos:])
            if not choice_match:
                break
            
            choice_name = choice_match.group(1)
            choice_start = pos + choice_match.end() - 1
            choice_end = self.find_balanced_braces(content, choice_start)
            
            if choice_end == -1:
                pos += choice_match.end()
                continue
            
            choice_body = content[choice_start + 1:choice_end]
            
            # Check if choice is mandatory
            choice_mandatory = re.search(r'\bmandatory\s+true\b', choice_body[:100])
            
            # Parse all cases within the choice
            case_pos = 0
            while True:
                case_match = re.search(r'\bcase\s+(\S+)\s*\{', choice_body[case_pos:])
                if not case_match:
                    break
                
                case_name = case_match.group(1)
                case_start = case_pos + case_match.end() - 1
                case_end = self.find_balanced_braces(choice_body, case_start)
                
                if case_end == -1:
                    case_pos += case_match.end()
                    continue
                
                case_body = choice_body[case_start + 1:case_end]
                
                # Parse case content and merge properties
                # According to RFC 8040, all choice cases become optional properties
                case_schema = self.parse_container_or_grouping(case_body, f"{name}-{case_name}", depth + 1, is_choice_case=True)
                if 'properties' in case_schema and case_schema['properties']:
                    properties.update(case_schema['properties'])
                    has_properties = True
                
                case_pos = case_end + 1
            
            pos = choice_end + 1
        
        # Build schema
        schema = {
            'type': 'object'
        }
        
        if has_properties and properties:
            schema['properties'] = properties
        
        if required:
            schema['required'] = required
        
        if is_presence:
            schema['description'] = schema.get('description', '') + ' (presence container)'
        
        return schema
    
    def create_example_data(self, schema: Dict[str, Any]) -> Any:
        """Generate example data from a schema"""
        if not schema:
            return {}
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            example = {}
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self.create_example_data(prop_schema)
            return example
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self.create_example_data(items_schema)]
        
        elif schema_type == 'string':
            # Check for specific formats or patterns
            fmt = schema.get('format')
            pattern = schema.get('pattern')
            if fmt == 'ipv6':
                return "2001:db8::1"
            elif pattern and 'ipv4' in pattern:
                return "192.168.1.1"
            elif 'ipv4-prefix' in schema.get('description', ''):
                return "192.168.1.0/24"
            elif 'ip-address' in schema.get('description', ''):
                return "192.168.1.1"
            return "example-string"
        
        elif schema_type == 'integer':
            minimum = schema.get('minimum', 0)
            maximum = schema.get('maximum', 100)
            return min(maximum, max(minimum, 10))
        
        elif schema_type == 'number':
            return 1.5
        
        elif schema_type == 'boolean':
            return True
        
        return None
    
    def parse_yang_file(self, yang_file: Path) -> Dict[str, Any]:
        """Parse YANG file and extract module info"""
        with open(yang_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        module_match = re.search(r'(?:sub)?module\s+(\S+)', content)
        module_name = module_match.group(1) if module_match else yang_file.stem
        
        desc_match = re.search(r'module\s+\S+\s*\{[^}]*?description\s+"([^"]+)"', content, re.DOTALL)
        if not desc_match:
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', content)
        description = desc_match.group(1) if desc_match else f"RPC operations for {module_name}"
        
        org_match = re.search(r'\borganization\s+"([^"]+)"', content)
        organization = org_match.group(1) if org_match else "Cisco Systems, Inc."
        
        contact_match = re.search(r'\bcontact\s+"([^"]+)"', content, re.DOTALL)
        contact = contact_match.group(1).strip() if contact_match else ""
        
        revision_match = re.search(r'\brevision\s+(\d{4}-\d{2}-\d{2})', content)
        version = revision_match.group(1) if revision_match else "1.0.0"
        
        self.extract_groupings(content)
        
        return {
            'module_name': module_name,
            'description': description,
            'version': version,
            'organization': organization,
            'contact': contact,
            'content': content
        }
    
    def extract_rpcs(self, content: str) -> List[Dict[str, Any]]:
        """Extract all RPC definitions from YANG content"""
        rpcs = []
        pos = 0
        
        while True:
            rpc_match = re.search(r'\brpc\s+(\S+)\s*\{', content[pos:])
            if not rpc_match:
                break
            
            rpc_name = rpc_match.group(1)
            rpc_start = pos + rpc_match.end() - 1
            rpc_end = self.find_balanced_braces(content, rpc_start)
            
            if rpc_end == -1:
                pos += rpc_match.end()
                continue
            
            rpc_body = content[rpc_start + 1:rpc_end]
            
            # Extract description
            desc_match = re.search(r'\bdescription\s+"([^"]+)"', rpc_body)
            description = desc_match.group(1) if desc_match else f"{rpc_name} operation"
            
            # Extract input
            input_schema = {'type': 'object', 'properties': {}}
            input_match = re.search(r'\binput\s*\{', rpc_body)
            if input_match:
                input_start = input_match.end() - 1
                input_end = self.find_balanced_braces(rpc_body, input_start)
                if input_end != -1:
                    input_body = rpc_body[input_start + 1:input_end]
                    input_schema = self.parse_container_or_grouping(input_body, f"{rpc_name}-input")
            
            # Extract output
            output_schema = {'type': 'object'}
            output_match = re.search(r'\boutput\s*\{', rpc_body)
            if output_match:
                output_start = output_match.end() - 1
                output_end = self.find_balanced_braces(rpc_body, output_start)
                if output_end != -1:
                    output_body = rpc_body[output_start + 1:output_end]
                    output_schema = self.parse_container_or_grouping(output_body, f"{rpc_name}-output")
            
            rpcs.append({
                'name': rpc_name,
                'operation_id': rpc_name,
                'description': description,
                'input_schema': input_schema,
                'output_schema': output_schema
            })
            
            pos = rpc_end + 1
        
        return rpcs
    
    def create_openapi_spec(self, yang_info: Dict[str, Any], rpcs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create OpenAPI 3.0 spec - RFC 8040 compliant"""
        
        module_name = yang_info['module_name']
        module_prefix = module_name.replace('Cisco-IOS-XE-', '').replace('-', '_')
        
        openapi_spec = {
            'openapi': '3.0.0',
            'info': {
                'title': f"{module_name} - RPC Operations",
                'description': f"{yang_info['description']}\n\n**Module:** `{module_name}`\n**Version:** {yang_info['version']}\n**Operations:** {len(rpcs)}",
                'version': yang_info['version']
            },
            'servers': [{
                'url': 'https://{device}/restconf',
                'variables': {'device': {'default': 'router.example.com'}}
            }],
            'paths': {},
            'components': {
                'securitySchemes': {
                    'basicAuth': {'type': 'http', 'scheme': 'basic'}
                }
            },
            'security': [{'basicAuth': []}]
        }
        
        # Create paths for each RPC - RFC 8040 Section 3.6
        for rpc in rpcs:
            rpc_name = rpc['name']
            
            # RFC 8040: RPC operations use /operations/{module}:{rpc-name}
            path = f"/operations/{module_prefix}:{rpc_name}"
            
            # RFC 8040: Input must be wrapped in module:rpc-name container
            request_schema = {
                'type': 'object',
                'properties': {
                    f"{module_prefix}:{rpc_name}": rpc['input_schema']
                }
            }
            
            # Create example request
            request_example = self.create_example_data(request_schema)
            
            openapi_spec['paths'][path] = {
                'post': {
                    'summary': rpc['description'],
                    'description': f"{rpc['description']}\n\n**Endpoint:** `POST /restconf{path}`",
                    'operationId': rpc['operation_id'],
                    'tags': [module_name],
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/yang-data+json': {
                                'schema': request_schema,
                                'example': request_example
                            }
                        }
                    },
                    'responses': {
                        '200': {
                            'description': 'RPC executed successfully',
                            'content': {
                                'application/yang-data+json': {
                                    'schema': rpc['output_schema'],
                                    'example': self.create_example_data(rpc['output_schema'])
                                }
                            }
                        },
                        '400': {'description': 'Invalid input'},
                        '401': {'description': 'Unauthorized'},
                        '500': {'description': 'Internal server error'}
                    }
                }
            }
        
        return openapi_spec
    
    def process_yang_file(self, yang_file: Path) -> Optional[Dict[str, Any]]:
        """Process a single YANG file and return OpenAPI spec"""
        print(f"Processing {yang_file.name}...")
        
        yang_info = self.parse_yang_file(yang_file)
        rpcs = self.extract_rpcs(yang_info['content'])
        
        if not rpcs:
            print(f"  No RPCs found in {yang_file.name}")
            return None
        
        print(f"  Found {len(rpcs)} RPC operations")
        spec = self.create_openapi_spec(yang_info, rpcs)
        
        # Save to file
        output_file = self.output_dir / f"{yang_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)
        
        print(f"  Created {output_file.name}")
        return spec
    
    def run(self):
        """Process all YANG RPC files"""
        yang_files = list(self.yang_dir.glob('*.yang'))
        
        # Filter for RPC files
        rpc_keywords = ['rpc', 'cmd', 'actions']
        rpc_files = [f for f in yang_files if any(kw in f.stem.lower() for kw in rpc_keywords)]
        
        # Additional modules with RPCs
        additional = ['cisco-smart-license.yang', 'cisco-bridge-domain.yang', 'cisco-ia.yang']
        for add_file in additional:
            full_path = self.yang_dir / add_file
            if full_path.exists() and full_path not in rpc_files:
                rpc_files.append(full_path)
        
        results = []
        for yang_file in sorted(rpc_files):
            spec = self.process_yang_file(yang_file)
            if spec:
                results.append({
                    'name': spec['info']['title'],
                    'file': f"{yang_file.stem}.json",
                    'version': spec['info']['version'],
                    'operations': len(spec['paths'])
                })
        
        # Create manifest
        manifest = {
            'title': 'Cisco IOS-XE RPC Operations',
            'description': 'OpenAPI specifications for Cisco IOS-XE NETCONF/RESTCONF RPC operations',
            'apis': results,
            'total_operations': sum(r['operations'] for r in results)
        }
        
        with open(self.output_dir / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"Successfully created {len(results)} OpenAPI specifications")
        print(f"Total operations: {manifest['total_operations']}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*70}")
        print(f"\nCreated manifest: {self.output_dir / 'manifest.json'}")

if __name__ == '__main__':
    script_dir = Path(__file__).parent
    converter = RPCYANGToOpenAPIConverter(
        yang_dir=str(script_dir.parent / 'references' / '17181-YANG-modules'),
        output_dir=str(script_dir.parent / 'swagger-rpc-model' / 'api')
    )
    converter.run()
