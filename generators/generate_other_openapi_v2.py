#!/usr/bin/env python3
"""
Convert misc/other YANG modules to OpenAPI 3.0 specifications.
Handles standalone Cisco and vendor-specific modules not in other categories.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List

class OtherToOpenAPI:
    """Convert misc/other YANG modules to OpenAPI 3.0 with proper YANG parsing"""

    def __init__(self, yang_dir: str, output_dir: str, module_list: List[str]):
        self.yang_dir = Path(yang_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.module_list = module_list
        self.groupings_cache = {}
        self.processed_modules = []

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
        return "Cisco IOS-XE YANG data model"

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

        # Extract description
        desc_match = re.search(r'description\s+"([^"]+)"', content[:500])
        if desc_match:
            schema["description"] = desc_match.group(1).strip()

        # Parse nested elements
        properties_target = schema["items"]["properties"] if is_list else schema["properties"]

        # Find all leaves
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

        # Find nested containers (limit depth)
        pos = 0
        depth_limit = 3
        while True:
            container_match = re.search(r'\n\s+container\s+(\S+)\s*\{', content[pos:])
            if not container_match or depth_limit <= 0:
                break

            cont_name = container_match.group(1)
            cont_start = pos + container_match.end() - 1
            cont_end = self.find_balanced_braces(content, cont_start)

            if cont_end != -1:
                cont_content = content[cont_start + 1:cont_end]
                properties_target[cont_name] = self.parse_container_or_grouping(cont_content, cont_name, False)

            pos = cont_end + 1 if cont_end != -1 else pos + container_match.end()

        return schema

    def extract_paths(self, content: str, module_name: str) -> Dict[str, Any]:
        """Extract RESTCONF paths from YANG module"""
        paths = {}

        # Extract groupings first
        self.extract_groupings(content)

        # Remove groupings and typedefs to avoid extracting containers from them
        # We only want top-level data containers, not structure definitions
        cleaned_content = self._remove_groupings_and_typedefs(content)

        # Find top-level containers and lists
        self._extract_paths_recursive(cleaned_content, module_name, "", paths, max_depth=8)

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
                paths[container_path] = {
                    "get": {
                        "summary": f"Get {container_name} data",
                        "description": f"Retrieve {container_name} configuration/operational data",
                        "tags": [module_name],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/yang-data+json": {
                                        "schema": {
                                            "$ref": f"#/components/schemas/{module_name}_{container_name}"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                # Add PUT/PATCH/DELETE for config containers
                if is_config:
                    paths[container_path]["put"] = {
                        "summary": f"Update {container_name}",
                        "description": f"Update or create {container_name} configuration",
                        "tags": [module_name],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/yang-data+json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{module_name}_{container_name}"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "Created"},
                            "204": {"description": "Updated"}
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
            is_config = 'config false' not in list_content[:200]

            # Extract key
            key_match = re.search(r'key\s+"([^"]+)"', list_content)
            key_params = key_match.group(1).strip() if key_match else "id"

            # Build paths
            if parent_path:
                list_path = f"{parent_path}/{list_name}"
            else:
                list_path = f"/data/{module_name}:{list_name}"

            # Collection path
            if list_path not in paths:
                operations = {
                    "get": {
                        "summary": f"Get {list_name} list",
                        "description": f"Retrieve list of {list_name} entries",
                        "tags": [module_name],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/yang-data+json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "$ref": f"#/components/schemas/{module_name}_{list_name}"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                if is_config:
                    operations["post"] = {
                        "summary": f"Create {list_name} entry",
                        "description": f"Create new {list_name} entry",
                        "tags": [module_name],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/yang-data+json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{module_name}_{list_name}"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "Created"}
                        }
                    }

                paths[list_path] = operations

            # Individual item path
            item_path = f"{list_path}={{{key_params}}}"
            if item_path not in paths:
                item_operations = {
                    "get": {
                        "summary": f"Get {list_name} entry",
                        "description": f"Retrieve specific {list_name} entry by key",
                        "tags": [module_name],
                        "parameters": [
                            {
                                "name": key_params,
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/yang-data+json": {
                                        "schema": {
                                            "$ref": f"#/components/schemas/{module_name}_{list_name}"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                if is_config:
                    item_operations["put"] = {
                        "summary": f"Update {list_name} entry",
                        "tags": [module_name],
                        "parameters": [{"name": key_params, "in": "path", "required": True, "schema": {"type": "string"}}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/yang-data+json": {
                                    "schema": {"$ref": f"#/components/schemas/{module_name}_{list_name}"}
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created"}, "204": {"description": "Updated"}}
                    }
                    item_operations["delete"] = {
                        "summary": f"Delete {list_name} entry",
                        "tags": [module_name],
                        "parameters": [{"name": key_params, "in": "path", "required": True, "schema": {"type": "string"}}],
                        "responses": {"204": {"description": "Deleted"}}
                    }

                paths[item_path] = item_operations

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
            print(f"  Skipping {module_name} (no data structures)")
            return None

        description = self.extract_description(content)
        paths = self.extract_paths(content, module_name)
        schemas = self.extract_schemas(content, module_name)

        if not paths:
            print(f"  Skipping {module_name} (no paths extracted)")
            return None

        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{module_name} API",
                "version": "1.0.0",
                "description": description,
                "contact": {
                    "name": "Cisco DevNet",
                    "url": "https://developer.cisco.com"
                }
            },
            "servers": [
                {
                    "url": "https://{device}:{port}/restconf",
                    "variables": {
                        "device": {
                            "default": "ios-xe-device",
                            "description": "IOS-XE Device IP or Hostname"
                        },
                        "port": {
                            "default": "443",
                            "description": "RESTCONF Port"
                        }
                    }
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
                    "description": f"Operations for {module_name}"
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

    def process_modules(self):
        """Process specified YANG modules"""
        print(f"\n{'='*70}")
        print(f"Processing {len(self.module_list)} misc/other YANG modules")
        print(f"{'='*70}\n")

        processed_count = 0
        skipped_count = 0

        for module_name in self.module_list:
            yang_file = self.yang_dir / f"{module_name}.yang"

            if not yang_file.exists():
                print(f"Warning: {yang_file.name} not found, skipping...")
                skipped_count += 1
                continue

            print(f"Processing: {yang_file.name}...")

            openapi_spec = self.convert_to_openapi(yang_file)

            if openapi_spec:
                output_file = self.output_dir / f"{module_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(openapi_spec, f, indent=2)
                print(f"  ✓ Generated: {output_file.name} ({len(openapi_spec['paths'])} paths)")
                processed_count += 1
            else:
                skipped_count += 1

        print(f"\n{'='*70}")
        print(f"Other Modules Generation Complete!")
        print(f"{'='*70}")
        print(f"Processed: {processed_count} files")
        print(f"Skipped:   {skipped_count} files")
        print(f"Total:     {len(self.module_list)} files")
        print(f"{'='*70}\n")

        # Save manifest
        manifest = {
            "total_files": len(self.module_list),
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
    script_dir = Path(__file__).parent
    yang_dir = script_dir.parent / 'references' / '17181-YANG-modules'
    output_dir = script_dir.parent / 'swagger-other-model' / 'api'

    # List of standalone misc/other modules
    modules = [
        'cisco-evpn-service',
        'cisco-self-mgmt',
        'cisco-smart-license',
        'cisco-storm-control',
        'nvo',
        'confd_dyncfg'
    ]

    converter = OtherToOpenAPI(str(yang_dir), str(output_dir), modules)
    processed = converter.process_modules()

    print(f"\n✓ Successfully generated {len(processed)} misc/other OpenAPI specifications")
    print(f"  Output directory: {output_dir}")


if __name__ == "__main__":
    main()
