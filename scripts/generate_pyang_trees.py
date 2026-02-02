#!/usr/bin/env python3
"""
Generate pyang tree outputs for all YANG modules
Creates HTML files with formatted tree output for web viewing
"""

import subprocess
from pathlib import Path
import re

def get_swagger_category(module_name: str) -> tuple:
    """Determine which swagger category a module belongs to"""
    # Check for specific patterns
    if module_name.endswith('-oper'):
        return ('swagger-oper-model', 'Operational State APIs')
    elif module_name.endswith('-rpc'):
        return ('swagger-rpc-model', 'RPC APIs')
    elif module_name.endswith('-events'):
        return ('swagger-events-model', 'Event/Telemetry APIs')
    elif module_name.endswith('-cfg'):
        return ('swagger-cfg-model', 'Configuration APIs')
    elif module_name.startswith('ietf-'):
        return ('swagger-ietf-model', 'IETF Standard APIs')
    elif module_name.startswith('openconfig-'):
        return ('swagger-openconfig-model', 'OpenConfig APIs')
    elif module_name == 'Cisco-IOS-XE-native':
        return ('swagger-native-config-model', 'Native Config APIs')
    elif module_name.startswith('cisco-') and not module_name.startswith('Cisco-IOS-XE-'):
        return ('swagger-other-model', 'Other/Vendor APIs')
    elif module_name in ['nvo', 'confd_dyncfg', 'common-mpls-static']:
        return ('swagger-other-model', 'Other/Vendor APIs')
    else:
        # Default - likely in native config or other
        return ('swagger-native-config-model', 'Native Config APIs')

def generate_pyang_tree(yang_file: Path, output_dir: Path) -> bool:
    """Generate pyang tree for a single YANG module"""
    try:
        module_name = yang_file.stem
        
        # Get swagger category for this module
        swagger_dir, swagger_label = get_swagger_category(module_name)
        
        # Run pyang tree command
        result = subprocess.run(
            ['pyang', '-f', 'tree', str(yang_file)],
            cwd=yang_file.parent,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Check if tree output is empty (types-only modules)
        tree_output = result.stdout.strip()
        if not tree_output or len(tree_output) < 50:
            print(f"  ⏭️  Skipping {module_name} (no tree structure)")
            return False
        
        # Create HTML file with formatted tree
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{module_name} - YANG Tree</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Courier New', monospace;
            background: #f5f5f5;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #049fd9 0%, #0070c9 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 24px;
            margin-bottom: 8px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .header a {{
            color: white;
            text-decoration: underline;
            opacity: 0.9;
        }}
        .header a:hover {{
            opacity: 1;
        }}
        .tree-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        pre {{
            font-size: 13px;
            line-height: 1.4;
            white-space: pre;
            color: #333;
        }}
        .footer {{
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 8px;
            text-align: center;
            font-size: 13px;
        }}
        .footer a {{
            color: #0070c9;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{module_name}</h1>
        <p>YANG Data Model Tree Structure</p>
        <p style="margin-top: 8px;">
            <a href="https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17181/{module_name}.yang" target="_blank">View YANG Source on GitHub →</a>
        </p>
    </div>
    
    <div style="background: #e3f2fd; padding: 15px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid #0070c9;">
        <p style="color: #01579b; font-size: 14px; margin-bottom: 10px;"><strong>📚 API Documentation & Navigation</strong></p>
        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
            <a href="../{swagger_dir}/?url=api/{module_name}.json" style="color: white; background: #0070c9; text-decoration: none; font-size: 13px; padding: 6px 12px; border-radius: 4px; font-weight: 500;">📄 Swagger API Spec</a>
            <a href="../{swagger_dir}/" style="color: #0070c9; text-decoration: none; font-size: 13px; padding: 6px 12px; background: white; border-radius: 4px; border: 1px solid #e0e0e0;">📂 Browse {swagger_label}</a>
            <a href="index.html" style="color: #666; text-decoration: none; font-size: 13px; padding: 6px 12px; background: white; border-radius: 4px; border: 1px solid #e0e0e0;">🌳 All Trees</a>
        </div>
    </div>
    
    <div class="tree-container">
        <pre>{tree_output}</pre>
    </div>
    
    <div class="footer">
        Generated with pyang | 
        <a href="../index.html">← Back to Main Page</a> | 
        <a href="https://github.com/mbj4668/pyang" target="_blank">About pyang</a>
    </div>
</body>
</html>
"""
        
        # Write HTML file
        output_file = output_dir / f"{module_name}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✅ Generated tree for {module_name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {yang_file.name}: {e}")
        return False

def generate_index_page(output_dir: Path, modules: list):
    """Generate index page for all tree files"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YANG Tree Browser - IOS-XE 17.18.1</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #049fd9 0%, #0070c9 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 16px;
        }
        .search-box {
            width: 100%;
            max-width: 600px;
            padding: 12px 20px;
            font-size: 16px;
            border: none;
            border-radius: 4px;
            margin-top: 20px;
        }
        .module-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .module-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .module-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .module-card a {
            color: #0070c9;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
        }
        .module-card a:hover {
            text-decoration: underline;
        }
        .stats {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stats h2 {
            color: #333;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 YANG Tree Browser</h1>
        <p>Visual data structure for all IOS-XE 17.18.1 YANG modules</p>
        <input type="text" class="search-box" id="searchBox" placeholder="Search modules..." onkeyup="filterModules()">
    </div>
    
    <div class="stats">
        <h2>""" + str(len(modules)) + """ Modules with Tree Structure</h2>
        <p style="color: #666; margin-top: 5px;">Data-bearing modules only (types-only modules excluded)</p>
    </div>
    
    <div class="module-grid" id="moduleGrid">
"""
    
    for module in sorted(modules):
        html_content += f'        <div class="module-card"><a href="{module}.html">{module}</a></div>\n'
    
    html_content += """    </div>
    
    <script>
        function filterModules() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const cards = document.querySelectorAll('.module-card');
            
            cards.forEach(card => {
                const moduleName = card.textContent.toLowerCase();
                if (moduleName.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""
    
    index_file = output_dir / 'index.html'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Generated index page: {index_file}")

def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    yang_dir = project_root / 'references' / '17181-YANG-modules'
    output_dir = project_root / 'yang-trees'
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("Generate pyang Tree Outputs for All YANG Modules")
    print("="*70)
    
    # Find all YANG files
    yang_files = sorted(yang_dir.glob('*.yang'))
    
    if not yang_files:
        print(f"No YANG files found in {yang_dir}")
        return
    
    print(f"\nFound {len(yang_files)} YANG modules")
    print(f"Output directory: {output_dir}\n")
    
    generated_modules = []
    for yang_file in yang_files:
        if generate_pyang_tree(yang_file, output_dir):
            generated_modules.append(yang_file.stem)
    
    # Generate index page
    if generated_modules:
        generate_index_page(output_dir, generated_modules)
    
    print(f"\n{'='*70}")
    print(f"COMPLETE: Generated {len(generated_modules)}/{len(yang_files)} tree files")
    print(f"{'='*70}")
    print(f"\nView index: file:///{output_dir / 'index.html'}")
    print(f"GitHub Pages: https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/yang-trees/\n")

if __name__ == '__main__':
    main()
