#!/usr/bin/env python3
"""Search for API paths in Native Config OpenAPI specs."""

import json
import sys
import os
from pathlib import Path

def search_path(search_term):
    """Search for a path in all native config specs."""
    api_dir = Path("swagger-native-config-model/api")
    results = []
    
    if not api_dir.exists():
        print(f"Error: {api_dir} not found")
        return
    
    # Get all JSON files
    json_files = sorted(api_dir.glob("native-*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                spec = json.load(f)
            
            # Search in paths
            if 'paths' in spec:
                for path, methods in spec['paths'].items():
                    if search_term.lower() in path.lower():
                        # Get the summary or description
                        summary = "N/A"
                        if 'get' in methods and 'summary' in methods['get']:
                            summary = methods['get']['summary']
                        elif 'put' in methods and 'summary' in methods['put']:
                            summary = methods['put']['summary']
                        
                        results.append({
                            'file': json_file.name,
                            'path': path,
                            'summary': summary
                        })
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_native_api.py <search_term>")
        print("Example: python search_native_api.py hostname")
        sys.exit(1)
    
    search_term = sys.argv[1]
    print(f"Searching for '{search_term}' in Native Config APIs...\n")
    
    results = search_path(search_term)
    
    if not results:
        print(f"No paths found containing '{search_term}'")
    else:
        print(f"Found {len(results)} matching path(s):\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. File: {result['file']}")
            print(f"   Path: {result['path']}")
            print(f"   Summary: {result['summary']}")
            print()
