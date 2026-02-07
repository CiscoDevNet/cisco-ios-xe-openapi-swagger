#!/usr/bin/env python3
"""
Rebuild Events Model Manifest with Accurate Notification Path Counts
Scans all Event spec files and counts WebSocket notification paths
"""

import json
import os
from pathlib import Path

def count_notification_paths(spec_file):
    """Count all notification paths in a spec file"""
    try:
        # Try utf-8-sig first to handle BOM, then fall back to utf-8
        with open(spec_file, 'r', encoding='utf-8-sig') as f:
            spec = json.load(f)
        
        # Count ALL paths - this includes:
        # - WebSocket paths: /ws/event-streams/...
        # - SNMP trap paths: /data/ietf-subscribed-notifications:...
        # - NETCONF notification paths: various patterns
        paths = spec.get('paths', {})
        return len(paths)
    except Exception as e:
        print(f"Error reading {spec_file}: {e}")
        return 0

def rebuild_events_manifest():
    """Rebuild the Events manifest with accurate counts"""
    
    api_dir = Path('swagger-events-model/api')
    
    if not api_dir.exists():
        print(f"Error: Directory {api_dir} not found")
        return
    
    # Get all JSON files except manifest files
    exclude_files = {'manifest.json', 'events-manifest.json', 'events-modules.txt'}
    spec_files = [f for f in api_dir.glob('*.json') if f.name not in exclude_files]
    
    print(f"\n🔍 Scanning {len(spec_files)} Event spec files...")
    
    modules = []
    total_paths = 0
    
    for spec_file in sorted(spec_files):
        module_name = spec_file.stem  # filename without .json extension
        path_count = count_notification_paths(spec_file)
        total_paths += path_count
        
        modules.append({
            "name": module_name,
            "file": spec_file.name,
            "notification_paths": path_count
        })
        
        if path_count > 0:
            print(f"  ✓ {module_name}: {path_count} notification paths")
    
    # Build the manifest
    manifest = {
        "title": "Cisco IOS-XE Event Notifications",
        "description": "Event notification modules for model-driven telemetry and streaming telemetry using YANG-push, NETCONF notifications, and SNMP traps",
        "version": "1.0.0",
        "generated": "2026-02-07",
        "total_modules": len(modules),
        "total_notifications": total_paths,
        "modules": modules
    }
    
    # Write manifest
    manifest_path = api_dir / 'manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 EVENTS MANIFEST REBUILD COMPLETE")
    print(f"{'='*60}")
    print(f"Total Modules: {len(modules)}")
    print(f"Total Notification Paths: {total_paths}")
    print(f"\nManifest saved to: {manifest_path}")
    print(f"{'='*60}\n")
    
    # Validation
    print("🔍 Validating JSON...")
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print("✅ manifest.json is valid JSON\n")
    except Exception as e:
        print(f"❌ Validation error: {e}\n")
    
    return manifest

if __name__ == '__main__':
    rebuild_events_manifest()
