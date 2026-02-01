#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a combined OpenAPI specification containing ALL RPC operations from all modules.
This creates a single unified view of all operations.
"""

import json
from pathlib import Path
import sys

# Ensure proper console encoding
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def generate_combined_spec():
    """Combine all RPC operations from all modules into a single OpenAPI spec."""
    
    api_dir = Path("swagger-rpc-model/api")
    
    # Read manifest to get accurate count
    manifest_file = api_dir / "manifest.json"
    total_ops = 274  # Default
    if manifest_file.exists():
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            total_ops = manifest.get('total_operations', 274)
    
    # Base OpenAPI structure
    combined_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Cisco IOS-XE - ALL RPC Operations (Combined)",
            "version": "17.18.1",
            "description": f"**Complete collection of all {total_ops} RPC operations** from all IOS-XE YANG modules in a single unified view.\n\n"
                          "This consolidated specification includes operations from multiple modules:\n"
                          "- Core System Operations (Cisco-IOS-XE-rpc)\n"
                          "- Wireless Management\n"
                          "- Software & Configuration Management\n"
                          "- Security & Cryptography\n"
                          "- Licensing (cisco-smart-license)\n"
                          "- Bridge & L2 Operations (cisco-bridge-domain)\n"
                          "- Network Services & Protocols\n"
                          "- Cloud & SD-WAN\n"
                          "- Diagnostics & Troubleshooting\n"
                          "- Platform & Hardware\n"
                          "- CLI & Command Line\n\n"
                          "**Authentication**: All operations require HTTP Basic Authentication.\n\n"
                          "**Base URL**: `https://{device}/restconf`\n\n"
                          "**Content-Type**: `application/yang-data+json`",
            "contact": {
                "name": "Cisco IOS-XE RESTCONF API",
                "url": "https://developer.cisco.com/docs/ios-xe"
            }
        },
        "servers": [
            {
                "url": "https://{device}/restconf",
                "description": "IOS-XE Device RESTCONF Endpoint",
                "variables": {
                    "device": {
                        "default": "sandbox-iosxe-latest-1.cisco.com",
                        "description": "Device hostname or IP address"
                    }
                }
            }
        ],
        "paths": {},
        "components": {
            "securitySchemes": {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                    "description": "HTTP Basic Authentication using device credentials"
                }
            },
            "schemas": {}
        },
        "security": [
            {
                "basicAuth": []
            }
        ],
        "tags": []
    }
    
    # Track statistics
    total_operations = 0
    modules_processed = 0
    tags_added = set()
    
    # Process all JSON files
    json_files = sorted(api_dir.glob("*.json"))
    
    for json_file in json_files:
        if json_file.name == "manifest.json":
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                spec = json.load(f)
            
            module_name = json_file.stem
            modules_processed += 1
            
            # Extract module title for tag
            module_title = spec.get('info', {}).get('title', module_name)
            
            # Add tag if not already added
            if module_name not in tags_added:
                tag_description = spec.get('info', {}).get('description', f'Operations from {module_name}')
                combined_spec['tags'].append({
                    "name": module_name,
                    "description": tag_description
                })
                tags_added.add(module_name)
            
            # Merge paths (operations)
            if 'paths' in spec:
                for path, methods in spec['paths'].items():
                    # Check if path already exists
                    if path in combined_spec['paths']:
                        # Path exists, merge operations
                        for method, operation in methods.items():
                            if method not in combined_spec['paths'][path]:
                                # Add tag to operation
                                if 'tags' not in operation:
                                    operation['tags'] = []
                                if module_name not in operation['tags']:
                                    operation['tags'].append(module_name)
                                
                                combined_spec['paths'][path][method] = operation
                                total_operations += 1
                    else:
                        # New path, add it
                        for method, operation in methods.items():
                            # Add tag to operation
                            if 'tags' not in operation:
                                operation['tags'] = []
                            if module_name not in operation['tags']:
                                operation['tags'].append(module_name)
                            total_operations += 1
                        
                        combined_spec['paths'][path] = methods
            
            # Merge schemas
            if 'components' in spec and 'schemas' in spec['components']:
                for schema_name, schema_def in spec['components']['schemas'].items():
                    # Prefix schema name with module to avoid conflicts
                    prefixed_name = f"{module_name}_{schema_name}"
                    combined_spec['components']['schemas'][prefixed_name] = schema_def
                    
                    # Update references in the paths we just added
                    for path, methods in combined_spec['paths'].items():
                        for method, operation in methods.items():
                            if module_name in operation.get('tags', []):
                                # Update schema references in this operation
                                operation_str = json.dumps(operation)
                                operation_str = operation_str.replace(
                                    f'"#/components/schemas/{schema_name}"',
                                    f'"#/components/schemas/{prefixed_name}"'
                                )
                                combined_spec['paths'][path][method] = json.loads(operation_str)
        
        except Exception as e:
            print(f"Warning: Could not process {json_file.name}: {e}")
            continue
    
    # Sort tags alphabetically
    combined_spec['tags'] = sorted(combined_spec['tags'], key=lambda x: x['name'])
    
    # Write combined spec
    output_file = api_dir / "all-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_spec, f, indent=2)
    
    print(f"\n[SUCCESS] Successfully created combined OpenAPI specification!")
    print(f"   Output: {output_file}")
    print(f"   Modules processed: {modules_processed}")
    print(f"   Total operations: {total_operations}")
    print(f"   🏷️  Tags created: {len(combined_spec['tags'])}")
    print(f"   📋 Schemas merged: {len(combined_spec['components']['schemas'])}")
    
    return output_file

if __name__ == "__main__":
    generate_combined_spec()
