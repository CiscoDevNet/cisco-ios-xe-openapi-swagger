#!/usr/bin/env python3
"""
Convert MIB YANG modules to OpenAPI 3.0 specifications.
Processes SMIv2-to-YANG translated MIB files.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List

class MIBToOpenAPI:
    """Convert MIB YANG modules to OpenAPI 3.0 with proper YANG parsing"""

    def __init__(self, yang_dir: str, output_dir: str):
        self.yang_dir = Path(yang_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.groupings_cache = {}
        self.processed_modules = []

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
                        if 'Index' in key or 'index' in key:
                            item[key] = str(i + 1) if isinstance(item[key], str) else i + 1
                    # Update interface-specific fields
                    if 'ifDescr' in item:
                        item['ifDescr'] = f"GigabitEthernet1/0/{i + 1}"
                    if 'ifPhysAddress' in item:
                        item['ifPhysAddress'] = f"00:11:22:33:44:{i+1:02x}"
                    if 'ifInOctets' in item:
                        item['ifInOctets'] = 1234567890 + (i * 1000000)
                    if 'ifOutOctets' in item:
                        item['ifOutOctets'] = 1234567890 + (i * 1000000)
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
            # Check for specific MIB counter/gauge types
            if 'counter' in name_lower or 'octets' in name_lower or 'packets' in name_lower:
                return 1234567890
            if 'mtu' in name_lower:
                return 1500
            if 'speed' in name_lower:
                return 1000000000  # 1 Gbps in bits/sec
            if 'index' in name_lower or 'ifindex' in name_lower:
                return 1
            if 'admin' in name_lower or 'oper' in name_lower:
                return 1  # up(1)
            return schema.get('minimum', 0)
        
        # String type with context awareness
        if 'mac' in name_lower or 'phys' in name_lower and 'address' in name_lower:
            return "00:11:22:33:44:55"
        if 'ip' in name_lower or 'addr' in name_lower:
            if 'ipv6' in name_lower:
                return "2001:db8::1"
            return "192.168.1.1"
        if 'interface' in name_lower or 'ifname' in name_lower or 'descr' in name_lower:
            return "GigabitEthernet1/0/1"
        if 'type' in name_lower:
            return "ethernetCsmacd(6)"
        if 'status' in name_lower or 'state' in name_lower:
            return "up(1)"
        if 'name' in name_lower:
            return "interface-1"
        if 'oid' in name_lower:
            return "1.3.6.1.2.1.1"
        
        return "example-string"

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

    def read_yang_file(self, filepath: Path) -> str:
        """Read YANG file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
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
        return "SNMP MIB translated to YANG data model"

    def parse_leaf(self, leaf_content: str, leaf_name: str) -> Dict[str, Any]:
        """Parse a YANG leaf and return OpenAPI schema"""
        schema = {
            "type": "string",
            "description": leaf_name
        }

        # Extract description
        desc_match = re.search(r'description\s+"([^"]+)"', leaf_content)
        if desc_match:
            schema["description"] = desc_match.group(1).strip()

        # Extract type
        type_match = re.search(r'type\s+([^;\s{]+)', leaf_content)
        if type_match:
            yang_type = type_match.group(1).strip()
            schema.update(self.yang_type_to_json_schema(yang_type))

        # Handle mandatory
        if re.search(r'\bmandatory\s+true', leaf_content):
            schema["x-mandatory"] = True

        return schema

    def yang_type_to_json_schema(self, yang_type: str) -> Dict[str, Any]:
        """Convert YANG type to JSON Schema type"""
        type_mapping = {
            'uint8': {'type': 'integer', 'minimum': 0, 'maximum': 255},
            'uint16': {'type': 'integer', 'minimum': 0, 'maximum': 65535},
            'uint32': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
            'uint64': {'type': 'integer', 'minimum': 0},
            'int8': {'type': 'integer', 'minimum': -128, 'maximum': 127},
            'int16': {'type': 'integer', 'minimum': -32768, 'maximum': 32767},
            'int32': {'type': 'integer', 'minimum': -2147483648, 'maximum': 2147483647},
            'int64': {'type': 'integer'},
            'boolean': {'type': 'boolean'},
            'string': {'type': 'string'},
            'binary': {'type': 'string', 'format': 'binary'},
            'bits': {'type': 'string'},
            'enumeration': {'type': 'string'},
            'decimal64': {'type': 'number'},
            'empty': {'type': 'boolean'},
            'yang:counter32': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
            'yang:counter64': {'type': 'integer', 'minimum': 0},
            'yang:gauge32': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
            'yang:gauge64': {'type': 'integer', 'minimum': 0},
        }

        if yang_type in type_mapping:
            return type_mapping[yang_type]
        elif yang_type.startswith('inet:'):
            return {'type': 'string', 'format': yang_type}
        elif yang_type.startswith('yang:'):
            return {'type': 'string', 'x-yang-type': yang_type}
        else:
            return {'type': 'string', 'x-yang-type': yang_type}

    def parse_container_or_grouping(self, content: str, name: str, is_list: bool = False) -> Dict[str, Any]:
        """Parse a container or grouping and return its schema"""
        schema = {
            "type": "object",
            "description": name,
            "properties": {}
        }

        if is_list:
            schema["type"] = "array"
            schema["items"] = {"type": "object", "properties": {}}
            # Remove properties field from array type
            del schema["properties"]

        # Extract description
        desc_match = re.search(r'description\s+"([^"]+)"', content[:500])
        if desc_match:
            schema["description"] = desc_match.group(1).strip()

        # Parse nested elements
        properties_target = schema["items"]["properties"] if is_list else schema["properties"]
        
        # First, check if this container has nested lists or containers
        # If it does, we should only add those as properties, not the leaves
        has_nested_structures = bool(re.search(r'\n\s+(list|container)\s+\S+\s*\{', content))
        
        # First, check if this container has nested lists or containers
        # If it does, we should only add those as properties, not the leaves
        has_nested_structures = bool(re.search(r'\n\s+(list|container)\s+\S+\s*\{', content))

        # Find nested lists first (they should be properties of the container)
        pos = 0
        while True:
            list_match = re.search(r'\n\s+list\s+(\S+)\s*\{', content[pos:])
            if not list_match:
                break

            list_name = list_match.group(1)
            list_start = pos + list_match.end() - 1
            list_end = self.find_balanced_braces(content, list_start)

            if list_end != -1:
                list_content = content[list_start + 1:list_end]
                # Parse as list and add to properties
                properties_target[list_name] = self.parse_container_or_grouping(list_content, list_name, True)

            pos = list_end + 1 if list_end != -1 else pos + list_match.end()

        # Find nested containers
        pos = 0
        while True:
            container_match = re.search(r'\n\s+container\s+(\S+)\s*\{', content[pos:])
            if not container_match:
                break

            cont_name = container_match.group(1)
            cont_start = pos + container_match.end() - 1
            cont_end = self.find_balanced_braces(content, cont_start)

            if cont_end != -1:
                cont_content = content[cont_start + 1:cont_end]
                properties_target[cont_name] = self.parse_container_or_grouping(cont_content, cont_name, False)

            pos = cont_end + 1 if cont_end != -1 else pos + container_match.end()
        
        # Only parse direct leaves if there are no nested lists
        # This prevents duplication when a container only exists to hold a list
        if not has_nested_structures or is_list:
            pos = 0
            while True:
                leaf_match = re.search(r'\n\s+(leaf|leaf-list)\s+(\S+)\s*\{', content[pos:])
                if not leaf_match:
                    break

                leaf_name = leaf_match.group(2)
                leaf_start = pos + leaf_match.end() - 1
                leaf_end = self.find_balanced_braces(content, leaf_start)

                if leaf_end != -1:
                    leaf_content = content[leaf_start + 1:leaf_end]
                    properties_target[leaf_name] = self.parse_leaf(leaf_content, leaf_name)

                pos = leaf_end + 1 if leaf_end != -1 else pos + leaf_match.end()

        return schema

    def extract_paths(self, content: str, module_name: str) -> Dict[str, Any]:
        """Extract RESTCONF paths from YANG module"""
        paths = {}

        # Extract groupings first
        self.extract_groupings(content)

        # MIB modules typically have a top-level container with the same name as the module
        # We need to skip this container and process its children directly
        top_level_container = None
        container_match = re.search(rf'\n\s*container\s+{re.escape(module_name)}\s*\{{', content)

        if container_match:
            # Found top-level container matching module name, process its contents
            container_start = container_match.end() - 1
            container_end = self.find_balanced_braces(content, container_start)

            if container_end != -1:
                # Process the contents of the top-level container instead of the module content
                top_level_content = content[container_start + 1:container_end]
                self._extract_paths_recursive(top_level_content, module_name, "", paths, max_depth=8)
                return paths

        # Fallback: no top-level container matching module name, process normally
        self._extract_paths_recursive(content, module_name, "", paths, max_depth=8)

        return paths

    def _extract_paths_recursive(self, content: str, module_name: str, parent_path: str, paths: Dict, depth: int = 0, max_depth: int = 8):
        """Recursively extract paths from YANG content"""
        if depth > max_depth:
            return

        # Find containers
        pos = 0
        while True:
            container_match = re.search(r'\n\s*container\s+(\S+)\s*\{', content[pos:])
            if not container_match:
                break

            container_name = container_match.group(1)
            container_start = pos + container_match.end() - 1
            container_end = self.find_balanced_braces(content, container_start)

            if container_end == -1:
                pos += container_match.end()
                continue

            container_content = content[container_start + 1:container_end]

            # Check if config false (read-only)
            is_config = 'config false' not in container_content[:200]

            # Build path
            if parent_path:
                container_path = f"{parent_path}/{container_name}"
            else:
                container_path = f"/data/{module_name}:{container_name}"

            # Add GET operation for this container
            if container_path not in paths:
                # Generate example from schema
                container_schema = self.parse_container_or_grouping(container_content, container_name, False)
                example_data = self.create_example_data(container_schema, container_name)
                
                paths[container_path] = {
                    "get": {
                        "summary": f"Get {container_name} data",
                        "description": f"Retrieve {container_name} operational data from MIB",
                        "tags": [module_name],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/yang-data+json": {
                                        "schema": container_schema,
                                        "example": {
                                            f"{module_name}:{container_name}": example_data
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

            # Recurse into container
            self._extract_paths_recursive(container_content, module_name, container_path, paths, depth + 1, max_depth)

            pos = container_end + 1

        # Find lists
        pos = 0
        while True:
            list_match = re.search(r'\n\s*list\s+(\S+)\s*\{', content[pos:])
            if not list_match:
                break

            list_name = list_match.group(1)
            list_start = pos + list_match.end() - 1
            list_end = self.find_balanced_braces(content, list_start)

            if list_end == -1:
                pos += list_match.end()
                continue

            list_content = content[list_start + 1:list_end]

            # Extract key
            key_match = re.search(r'key\s+"([^"]+)"', list_content)
            key_params = key_match.group(1).strip() if key_match else "id"

            # Build paths
            if parent_path:
                list_path = f"{parent_path}/{list_name}"
            else:
                list_path = f"/data/{module_name}:{list_name}"

            # Collection path (GET)
            if list_path not in paths:
                # Generate example from schema
                list_schema = self.parse_container_or_grouping(list_content, list_name, True)
                example_item = self.create_example_data(list_schema.get('items', {}), list_name)
                
                paths[list_path] = {
                    "get": {
                        "summary": f"Get {list_name} list",
                        "description": f"Retrieve list of {list_name} entries from MIB",
                        "tags": [module_name],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/yang-data+json": {
                                        "schema": list_schema,
                                        "example": {
                                            f"{module_name}:{list_name}": [example_item]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

            # Individual item path (GET)
            item_path = f"{list_path}={{{key_params}}}"
            if item_path not in paths:
                # Generate example from schema (reuse from above)
                list_schema = self.parse_container_or_grouping(list_content, list_name, True)
                example_item = self.create_example_data(list_schema.get('items', {}), list_name)
                item_schema = list_schema.get('items', {"type": "object"})
                
                paths[item_path] = {
                    "get": {
                        "summary": f"Get {list_name} entry",
                        "description": f"Retrieve specific {list_name} entry by key from MIB",
                        "tags": [module_name],
                        "parameters": [
                            {
                                "name": key_params,
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "example": "1"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/yang-data+json": {
                                        "schema": item_schema,
                                        "example": {
                                            f"{module_name}:{list_name}": example_item
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

            # Recurse into list
            self._extract_paths_recursive(list_content, module_name, item_path.replace(f"={{{key_params}}}", ""), paths, depth + 1, max_depth)

            pos = list_end + 1

    def extract_schemas(self, content: str, module_name: str) -> Dict[str, Any]:
        """Extract schema definitions from YANG module"""
        schemas = {}

        # Find all containers
        pos = 0
        while True:
            container_match = re.search(r'\bcontainer\s+(\S+)\s*\{', content[pos:])
            if not container_match:
                break

            container_name = container_match.group(1)
            container_start = pos + container_match.end() - 1
            container_end = self.find_balanced_braces(content, container_start)

            if container_end != -1:
                container_content = content[container_start + 1:container_end]
                schema_name = f"{module_name}_{container_name}"
                schemas[schema_name] = self.parse_container_or_grouping(container_content, container_name, False)

            pos = container_end + 1 if container_end != -1 else pos + container_match.end()

        # Find all lists
        pos = 0
        while True:
            list_match = re.search(r'\blist\s+(\S+)\s*\{', content[pos:])
            if not list_match:
                break

            list_name = list_match.group(1)
            list_start = pos + list_match.end() - 1
            list_end = self.find_balanced_braces(content, list_start)

            if list_end != -1:
                list_content = content[list_start + 1:list_end]
                schema_name = f"{module_name}_{list_name}"
                schemas[schema_name] = self.parse_container_or_grouping(list_content, list_name, True)

            pos = list_end + 1 if list_end != -1 else pos + list_match.end()

        return schemas

    def convert_to_openapi(self, yang_file: Path) -> Dict[str, Any]:
        """Convert a YANG file to OpenAPI 3.0 specification"""
        content = self.read_yang_file(yang_file)
        if not content:
            return None

        module_name = self.extract_module_name(content)
        if not module_name:
            return None

        # Check if module has actual data structures
        has_container = 'container ' in content
        has_list = 'list ' in content

        if not has_container and not has_list:
            print(f"  Skipping {module_name} (no data structures - type/typedef only)")
            return None

        description = self.extract_description(content)
        paths = self.extract_paths(content, module_name)
        schemas = self.extract_schemas(content, module_name)

        if not paths:
            print(f"  Skipping {module_name} (no paths extracted)")
            return None

        # Add MIB-specific warning to description
        mib_warning = """

⚠️ **IMPORTANT - MIB DATA ACCESS**:
This YANG model exists for SMIv2-to-YANG translation purposes, but MIB data on IOS-XE devices is primarily accessed via **SNMP protocol**, not RESTCONF.

**RESTCONF Limitation**: Many MIB paths may return 404 errors via RESTCONF `/data` endpoints because the device exposes MIB data through SNMP, not the YANG datastore.

**Recommended Access Methods**:
- Use SNMP (v2c/v3) to query MIB data directly
- Use NETCONF `<get>` operations for devices supporting YANG-modeled MIB access
- Check device capabilities: some newer IOS-XE versions may support limited RESTCONF access to specific MIBs

**YANG Model Purpose**: These YANG models define the structure of SNMP MIBs in YANG format for tooling compatibility, but do not guarantee RESTCONF data availability.
"""

        full_description = (description + mib_warning) if description else mib_warning.strip()

        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{module_name} MIB API",
                "version": "1.0.0",
                "description": full_description,
                "contact": {
                    "name": "Cisco DevNet",
                    "url": "https://developer.cisco.com"
                }
            },
            "servers": [
                {
                    "url": "https://10.85.134.65/restconf",
                    "description": "IOS-XE Device (C9300)"
                }
            ],
            "paths": paths,
            "components": {
                "schemas": schemas,
                "securitySchemes": {
                    "basicAuth": {
                        "type": "http",
                        "scheme": "basic"
                    }
                }
            },
            "security": [
                {
                    "basicAuth": []
                }
            ],
            "tags": [
                {
                    "name": module_name,
                    "description": f"MIB operations for {module_name}"
                }
            ]
        }

        self.processed_modules.append({
            "name": module_name,
            "file": yang_file.name,
            "paths": len(paths),
            "schemas": len(schemas)
        })

        return openapi_spec

    def process_all_mibs(self):
        """Process all MIB YANG files"""
        mib_files = sorted(self.yang_dir.glob('*.yang'))

        print(f"\n{'='*70}")
        print(f"Processing {len(mib_files)} MIB YANG files from MIBS directory")
        print(f"{'='*70}\n")

        processed_count = 0
        skipped_count = 0

        for mib_file in mib_files:
            print(f"Processing: {mib_file.name}...")

            openapi_spec = self.convert_to_openapi(mib_file)

            if openapi_spec:
                output_file = self.output_dir / f"{mib_file.stem}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(openapi_spec, f, indent=2)
                print(f"  + Generated: {output_file.name} ({len(openapi_spec['paths'])} paths)")
                processed_count += 1
            else:
                skipped_count += 1

        print(f"\n{'='*70}")
        print(f"MIB Generation Complete!")
        print(f"{'='*70}")
        print(f"Processed: {processed_count} files")
        print(f"Skipped:   {skipped_count} files (type-only modules)")
        print(f"Total:     {len(mib_files)} files")
        print(f"{'='*70}\n")

        # Save manifest
        manifest = {
            "total_files": len(mib_files),
            "processed": processed_count,
            "skipped": skipped_count,
            "modules": self.processed_modules
        }

        manifest_file = self.output_dir / "manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        print(f"Manifest saved: {manifest_file}")

        return self.processed_modules


def main():
    """Main entry point"""
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    script_dir = Path(__file__).parent
    yang_dir = script_dir.parent / 'references' / '17181-YANG-modules' / 'MIBS'
    output_dir = script_dir.parent / 'swagger-mib-model' / 'api'

    converter = MIBToOpenAPI(str(yang_dir), str(output_dir))
    modules = converter.process_all_mibs()

    print(f"\n+ Successfully generated {len(modules)} MIB OpenAPI specifications")
    print(f"  Output directory: {output_dir}")


if __name__ == "__main__":
    main()
