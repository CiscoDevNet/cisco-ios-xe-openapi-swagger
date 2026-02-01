#!/usr/bin/env python3
"""
Generate example payloads for OpenAPI specs from YANG models.
This script extracts YANG structures and creates proper request body examples.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class YANGToExampleGenerator:
    def __init__(self, yang_dir: str, openapi_dir: str):
        self.yang_dir = Path(yang_dir)
        self.openapi_dir = Path(openapi_dir)
        self.yang_cache = {}
        
    def parse_yang_container(self, yang_content: str, container_name: str) -> Dict[str, Any]:
        """Extract structure from a YANG container"""
        examples = {}
        
        # Find the container definition
        container_pattern = rf'container {re.escape(container_name)} \{{(.*?)\n  \}}'
        match = re.search(container_pattern, yang_content, re.DOTALL)
        
        if not match:
            return {}
        
        container_body = match.group(1)
        
        # Extract leaf definitions
        leaf_pattern = r'leaf\s+(\S+)\s*\{([^}]*)\}'
        for leaf_match in re.finditer(leaf_pattern, container_body):
            leaf_name = leaf_match.group(1)
            leaf_body = leaf_match.group(2)
            
            # Get type
            type_match = re.search(r'type\s+(\S+)', leaf_body)
            if type_match:
                yang_type = type_match.group(1)
                examples[leaf_name] = self._get_example_value(yang_type, leaf_body)
        
        # Extract leaf-list definitions
        leaflist_pattern = r'leaf-list\s+(\S+)\s*\{([^}]*)\}'
        for ll_match in re.finditer(leaflist_pattern, container_body):
            ll_name = ll_match.group(1)
            ll_body = ll_match.group(2)
            
            type_match = re.search(r'type\s+(\S+)', ll_body)
            if type_match:
                yang_type = type_match.group(1)
                examples[ll_name] = [self._get_example_value(yang_type, ll_body)]
        
        # Extract nested containers
        nested_container_pattern = r'container\s+(\S+)\s*\{'
        for nc_match in re.finditer(nested_container_pattern, container_body):
            nc_name = nc_match.group(1)
            examples[nc_name] = self.parse_yang_container(container_body, nc_name)
        
        # Extract lists
        list_pattern = r'list\s+(\S+)\s*\{([^}]*key\s+"([^"]+)"[^}]*)\}'
        for list_match in re.finditer(list_pattern, container_body):
            list_name = list_match.group(1)
            key_name = list_match.group(3)
            examples[list_name] = [{key_name: f"example-{key_name}"}]
        
        return examples
    
    def _get_example_value(self, yang_type: str, context: str) -> Any:
        """Generate example value based on YANG type"""
        
        # Check for range
        range_match = re.search(r'range\s+"([^"]+)"', context)
        if range_match:
            range_str = range_match.group(1)
            # Get first value in range
            if '..' in range_str:
                min_val = range_str.split('..')[0]
                return int(min_val) if min_val.isdigit() else 1
        
        # Check for enumeration
        if 'enumeration' in context:
            enum_match = re.search(r'enum\s+"?(\S+?)"?;', context)
            if enum_match:
                return enum_match.group(1)
        
        # Map YANG types to example values
        type_examples = {
            'string': 'example-string',
            'inet:ipv4-address': '192.168.1.1',
            'inet:ipv6-address': '2001:db8::1',
            'boolean': True,
            'empty': True,
            'uint8': 10,
            'uint16': 100,
            'uint32': 1000,
            'uint64': 10000,
            'int8': 10,
            'int16': 100,
            'int32': 1000,
            'int64': 10000,
        }
        
        # Handle qualified types (e.g., ios-types:...)
        base_type = yang_type.split(':')[-1]
        
        return type_examples.get(yang_type, type_examples.get(base_type, 'example-value'))
    
    def load_yang_file(self, yang_file: str) -> str:
        """Load YANG file content"""
        yang_path = self.yang_dir / yang_file
        if yang_path.exists():
            with open(yang_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def generate_example_for_xpath(self, xpath: str) -> Optional[Dict[str, Any]]:
        """Generate example payload from XPath"""
        
        # Parse xpath to understand structure
        # Example: native/crypto/ikev2/policy
        parts = xpath.split('/')
        
        if not parts:
            return None
        
        # Determine which YANG file to use
        yang_file = None
        if 'crypto' in parts:
            yang_file = 'Cisco-IOS-XE-crypto.yang'
        elif 'interface' in parts:
            # Check interface type
            if 'Loopback' in parts:
                yang_file = 'Cisco-IOS-XE-native.yang'
        
        if not yang_file:
            yang_file = 'Cisco-IOS-XE-native.yang'
        
        yang_content = self.load_yang_file(yang_file)
        if not yang_content:
            return None
        
        # Build example recursively
        example = {}
        for part in reversed(parts):
            if not example:
                example = self.parse_yang_container(yang_content, part)
            else:
                example = {part: example}
        
        return example
    
    def update_openapi_file(self, openapi_file: str, dry_run: bool = True):
        """Update OpenAPI file with generated examples"""
        
        file_path = self.openapi_dir / openapi_file
        if not file_path.exists():
            print(f"❌ File not found: {openapi_file}")
            return
        
        print(f"\n📄 Processing: {openapi_file}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        updates = 0
        
        # Iterate through paths
        for path, path_obj in spec.get('paths', {}).items():
            for method, operation in path_obj.items():
                if method not in ['post', 'put', 'patch']:
                    continue
                
                # Check if has requestBody
                request_body = operation.get('requestBody')
                if not request_body:
                    continue
                
                # Get description to extract XPath
                description = operation.get('description', '')
                xpath_match = re.search(r'XPath:\s*(.+?)(?:\.|$)', description)
                
                if xpath_match:
                    xpath = xpath_match.group(1).strip()
                    
                    # Generate example
                    example = self.generate_example_for_xpath(xpath)
                    
                    if example:
                        # Update the schema with example
                        content = request_body.get('content', {})
                        for content_type in ['application/yang-data+json', 'application/yang-data+xml']:
                            if content_type in content:
                                schema = content[content_type].get('schema', {})
                                
                                # Add example to schema
                                if 'example' not in schema:
                                    schema['example'] = example
                                    updates += 1
                                    print(f"  ✅ Added example for {method.upper()} {path}")
        
        print(f"\n📊 Total updates: {updates}")
        
        if not dry_run and updates > 0:
            # Save updated spec
            backup_path = file_path.with_suffix('.json.backup')
            file_path.rename(backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2)
            
            print(f"💾 Saved updated file (backup: {backup_path.name})")
        elif dry_run:
            print("🔍 DRY RUN - No files modified")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate YANG-based examples for OpenAPI specs')
    parser.add_argument('--yang-dir', default='../references/17181-YANG-modules',
                        help='Directory containing YANG files')
    parser.add_argument('--api-dir', default='api',
                        help='Directory containing OpenAPI JSON files')
    parser.add_argument('--file', help='Specific OpenAPI file to process')
    parser.add_argument('--apply', action='store_true',
                        help='Actually update files (default is dry-run)')
    
    args = parser.parse_args()
    
    generator = YANGToExampleGenerator(args.yang_dir, args.api_dir)
    
    if args.file:
        generator.update_openapi_file(args.file, dry_run=not args.apply)
    else:
        # Process all JSON files
        api_path = Path(args.api_dir)
        for json_file in api_path.glob('*.json'):
            if json_file.name != 'manifest.json':
                generator.update_openapi_file(json_file.name, dry_run=not args.apply)


if __name__ == '__main__':
    main()
