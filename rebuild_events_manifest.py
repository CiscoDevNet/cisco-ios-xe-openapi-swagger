#!/usr/bin/env python3
"""
Rebuild the Events model manifest.json file.
Scans all Event notification spec files and creates an updated manifest.
"""

import json
import os
from pathlib import Path

def main():
    # Define the directory
    base_dir = Path(r"c:\Users\jcohoe\OneDrive - Cisco\Documents\VSCODE-OD\Swagger2\monday-Swagger\cisco-ios-xe-openapi-swagger")
    api_dir = base_dir / "swagger-events-model" / "api"
    
    print("\n" + "="*70)
    print("  EVENT NOTIFICATION MANIFEST BUILDER")
    print("="*70 + "\n")
    
    # Get all JSON files except manifest.json and events-manifest.json
    json_files = sorted([f for f in api_dir.glob("*.json") 
                        if f.name not in ['manifest.json', 'events-manifest.json']])
    
    print(f"📁 Directory: {api_dir}")
    print(f"📄 Found {len(json_files)} event notification spec files\n")
    
    modules = []
    total_paths = 0
    
    # Process each file
    for json_file in json_files:
        module_name = json_file.stem
        
        try:
            # Try utf-8-sig first to handle BOM, fallback to utf-8
            try:
                with open(json_file, 'r', encoding='utf-8-sig') as f:
                    spec = json.load(f)
            except:
                with open(json_file, 'r', encoding='utf-8') as f:
                    spec = json.load(f)
            
            # Count paths that start with /ws/event-streams/
            path_count = 0
            if 'paths' in spec:
                for path in spec['paths'].keys():
                    if path.startswith('/ws/event-streams/'):
                        path_count += 1
            
            total_paths += path_count
            
            # Get description if available
            description = spec.get('info', {}).get('description', '')
            
            modules.append({
                "name": module_name,
                "file": json_file.name,
                "notification_count": path_count
            })
            
            print(f"✓ {module_name:60s} ({path_count} notifications)")
            
        except Exception as e:
            print(f"✗ {module_name:60s} ERROR: {e}")
    
    # Create manifest structure
    manifest = {
        "title": "Cisco IOS-XE Event Notifications",
        "description": "Event notification modules for model-driven telemetry and streaming telemetry using YANG-push, NETCONF notifications, and SNMP traps",
        "version": "1.0.0",
        "generated": "2026-02-07",
        "total_modules": len(modules),
        "total_notifications": total_paths,
        "modules": sorted([{"name": m["name"], "file": m["file"]} for m in modules], 
                         key=lambda x: x["name"])
    }
    
    # Save manifest
    manifest_path = api_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("  MANIFEST GENERATION COMPLETE")
    print("="*70)
    print(f"\n📊 STATISTICS:")
    print(f"   Total Modules: {manifest['total_modules']}")
    print(f"   Total Notifications: {manifest['total_notifications']}")
    print(f"   Output File: manifest.json")
    
    # Validate JSON
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"\n✓ manifest.json validated successfully")
    except Exception as e:
        print(f"\n✗ Validation error: {e}")
    
    print(f"\n✅ Manifest saved to: {manifest_path}\n")
    
    # Show top modules by notification count
    top_modules = sorted(modules, key=lambda x: x['notification_count'], reverse=True)[:10]
    print("📈 TOP 10 MODULES BY NOTIFICATION COUNT:")
    for i, mod in enumerate(top_modules, 1):
        print(f"   {i:2d}. {mod['name']:55s} {mod['notification_count']:3d} notifications")
    print()

if __name__ == "__main__":
    main()
