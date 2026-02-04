#!/usr/bin/env python3
"""
Enhance YANG tree HTML files with metadata
Adds: namespace, prefix, related modules, example usage
"""

import os
import json
import re
from pathlib import Path

# Load search index for module metadata
with open('search-index.json', 'r', encoding='utf-8') as f:
    search_index = json.load(f)

# Create module lookup
modules_dict = {m['name']: m for m in search_index['modules']}

# Common YANG namespaces and prefixes (based on typical Cisco IOS-XE modules)
NAMESPACE_MAP = {
    'Cisco-IOS-XE': 'http://cisco.com/ns/yang/',
    'ietf': 'urn:ietf:params:xml:ns:yang:',
    'openconfig': 'http://openconfig.net/yang/',
    'tailf': 'http://tail-f.com/ns/',
}

def extract_module_metadata(module_name):
    """Extract metadata for a module"""
    metadata = {
        'namespace': '',
        'prefix': '',
        'related_modules': [],
        'imports': [],
        'example_usage': ''
    }
    
    # Determine namespace based on module name
    if module_name.startswith('Cisco-IOS-XE'):
        metadata['namespace'] = f"{NAMESPACE_MAP['Cisco-IOS-XE']}{module_name}"
        metadata['prefix'] = module_name.replace('Cisco-IOS-XE-', '').replace('-', '_')[:15]
    elif module_name.startswith('ietf-'):
        metadata['namespace'] = f"{NAMESPACE_MAP['ietf']}{module_name}"
        metadata['prefix'] = module_name.replace('ietf-', '')[:10]
    elif module_name.startswith('openconfig-'):
        metadata['namespace'] = f"{NAMESPACE_MAP['openconfig']}{module_name}"
        metadata['prefix'] = 'oc-' + module_name.replace('openconfig-', '')[:10]
    elif module_name.startswith('tailf-'):
        metadata['namespace'] = f"{NAMESPACE_MAP['tailf']}{module_name}"
        metadata['prefix'] = module_name.replace('tailf-', '')[:10]
    else:
        # MIBs and others
        metadata['namespace'] = f"http://cisco.com/ns/yang/{module_name}"
        metadata['prefix'] = module_name.lower().replace('-mib', '')[:15]
    
    # Find related modules (same category or similar name)
    module_info = modules_dict.get(module_name)
    if module_info:
        category = module_info.get('category', '')
        base_name = module_name.replace('-oper', '').replace('-cfg', '').replace('-rpc', '').replace('-events', '')
        
        for mod_name, mod_data in modules_dict.items():
            if mod_name == module_name:
                continue
            
            # Related if: same base name, same category (limit to 5)
            if base_name in mod_name or mod_data.get('category') == category:
                metadata['related_modules'].append({
                    'name': mod_name,
                    'type': mod_data.get('type', 'unknown'),
                    'category': mod_data.get('displayCategory', ''),
                    'url': mod_data.get('yangTreeUrl', '')
                })
                if len(metadata['related_modules']) >= 5:
                    break
    
    # Generate example usage based on module type
    if module_info:
        mod_type = module_info.get('type', '')
        if 'oper' in mod_type or 'operational' in module_name.lower():
            metadata['example_usage'] = f"""# GET operational data
curl -X GET \\
  -H "Accept: application/yang-data+json" \\
  -u admin:password \\
  --insecure \\
  https://device-ip/restconf/data/{module_name}"""
        elif 'config' in mod_type or 'cfg' in module_name.lower():
            metadata['example_usage'] = f"""# PUT configuration
curl -X PUT \\
  -H "Content-Type: application/yang-data+json" \\
  -u admin:password \\
  --insecure \\
  https://device-ip/restconf/data/{module_name} \\
  -d @config.json"""
        elif 'rpc' in module_name.lower():
            metadata['example_usage'] = f"""# POST RPC operation
curl -X POST \\
  -H "Content-Type: application/yang-data+json" \\
  -u admin:password \\
  --insecure \\
  https://device-ip/restconf/operations/{module_name}:rpc-name \\
  -d '{{"input": {{}}}}'"""
        else:
            metadata['example_usage'] = f"""# GET module data
curl -X GET \\
  -H "Accept: application/yang-data+json" \\
  -u admin:password \\
  --insecure \\
  https://device-ip/restconf/data/{module_name}"""
    
    return metadata

def create_metadata_section(module_name, metadata):
    """Create HTML metadata section"""
    related_html = ''
    if metadata['related_modules']:
        related_items = []
        for rel in metadata['related_modules'][:5]:
            if rel['url']:
                related_items.append(f'<a href="{rel["url"]}" style="color: #0070c9; text-decoration: none; padding: 4px 8px; background: #f0f0f0; border-radius: 4px; font-size: 12px; display: inline-block; margin: 2px;">{rel["name"]}</a>')
        if related_items:
            related_html = '<br>'.join(related_items)
    
    # Generate documentation links based on module type
    doc_links = []
    
    # GitHub source link (all modules)
    github_path = f"https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17181/{module_name}.yang"
    doc_links.append(f'<a href="{github_path}" target="_blank" style="color: #0070c9; text-decoration: none; padding: 6px 12px; background: white; border-radius: 4px; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; border: 1px solid #e0e0e0; margin: 4px;">💻 YANG Source</a>')
    
    # YANG Catalog link
    yang_catalog = f"https://yangcatalog.org/yang-search/module_details/{module_name}"
    doc_links.append(f'<a href="{yang_catalog}" target="_blank" style="color: #0070c9; text-decoration: none; padding: 6px 12px; background: white; border-radius: 4px; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; border: 1px solid #e0e0e0; margin: 4px;">📖 YANG Catalog</a>')
    
    # IETF-specific links
    if module_name.startswith('ietf-'):
        # Try to find RFC number (simplified - would need actual mapping)
        doc_links.append(f'<a href="https://www.rfc-editor.org/search/rfc_search_detail.php?title={module_name}" target="_blank" style="color: #0070c9; text-decoration: none; padding: 6px 12px; background: white; border-radius: 4px; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; border: 1px solid #e0e0e0; margin: 4px;">📋 Search IETF RFC</a>')
    
    # OpenConfig-specific links
    if module_name.startswith('openconfig-'):
        oc_name = module_name.replace('openconfig-', '')
        doc_links.append(f'<a href="https://openconfig.net/projects/models/" target="_blank" style="color: #0070c9; text-decoration: none; padding: 6px 12px; background: white; border-radius: 4px; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; border: 1px solid #e0e0e0; margin: 4px;">🌍 OpenConfig Docs</a>')
    
    # Cisco DevNet link for Cisco modules
    if module_name.startswith('Cisco-IOS-XE-'):
        doc_links.append(f'<a href="https://developer.cisco.com/docs/ios-xe/#!yang-models" target="_blank" style="color: #0070c9; text-decoration: none; padding: 6px 12px; background: white; border-radius: 4px; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; border: 1px solid #e0e0e0; margin: 4px;">🌐 DevNet Guide</a>')
    
    doc_links_html = ''.join(doc_links)
    
    html = f'''
    <div style="background: #fff9e6; border-left: 4px solid #FFA726; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
        <p style="color: #E65100; font-size: 14px; margin-bottom: 10px;"><strong>📋 Module Metadata</strong></p>
        <div style="font-size: 13px; color: #333;">
            <p style="margin: 8px 0;"><strong>Namespace:</strong> <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-size: 12px;">{metadata['namespace']}</code></p>
            <p style="margin: 8px 0;"><strong>Prefix:</strong> <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-size: 12px;">{metadata['prefix']}</code></p>
            {f'<p style="margin: 8px 0;"><strong>Related Modules:</strong><br>{related_html}</p>' if related_html else ''}
        </div>
    </div>
    
    <div style="background: #e3f2fd; border-left: 4px solid #2196F3; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
        <p style="color: #01579b; font-size: 14px; margin-bottom: 10px;"><strong>📚 External Documentation</strong></p>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            {doc_links_html}
        </div>
    </div>
    
    <div style="background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
        <p style="color: #2E7D32; font-size: 14px; margin-bottom: 10px;"><strong>💡 Example Usage</strong></p>
        <pre style="background: #263238; color: #aed581; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 12px; line-height: 1.6;">{metadata['example_usage']}</pre>
    </div>
    '''
    
    return html

def enhance_tree_file(filepath):
    """Enhance a single tree HTML file"""
    print(f"Enhancing {filepath.name}...")
    
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract module name from filename
    module_name = filepath.stem
    
    # Get metadata
    metadata = extract_module_metadata(module_name)
    
    # Create metadata HTML
    metadata_html = create_metadata_section(module_name, metadata)
    
    # Insert metadata section before tree container
    # Find the insertion point (before <div class="tree-container">)
    tree_container_pattern = r'(<div class="tree-container">)'
    
    if re.search(tree_container_pattern, content):
        enhanced_content = re.sub(
            tree_container_pattern,
            metadata_html + r'\n    \1',
            content,
            count=1
        )
        
        # Write enhanced content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        return True
    else:
        print(f"  ⚠️  Could not find insertion point in {filepath.name}")
        return False

def main():
    """Enhance all YANG tree HTML files"""
    trees_dir = Path('yang-trees')
    
    if not trees_dir.exists():
        print("Error: yang-trees directory not found")
        return
    
    # Get all HTML files (exclude index)
    tree_files = [f for f in trees_dir.glob('*.html') if f.name not in ['index.html', 'mib-trees-index.html']]
    
    print(f"Found {len(tree_files)} tree files to enhance\n")
    
    enhanced_count = 0
    failed_count = 0
    
    for tree_file in tree_files:
        if enhance_tree_file(tree_file):
            enhanced_count += 1
        else:
            failed_count += 1
    
    print(f"\nEnhanced {enhanced_count} files successfully!")
    if failed_count > 0:
        print(f"Failed to enhance {failed_count} files")

if __name__ == '__main__':
    main()
