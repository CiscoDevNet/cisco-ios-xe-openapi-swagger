#!/usr/bin/env python3
"""
Generate pyang tree visualizations for all MIB YANG modules.
Creates HTML files with formatted tree output for easy viewing.
"""

import subprocess
import os
from pathlib import Path
import html

def generate_tree_html(yang_file: Path, output_dir: Path) -> bool:
    """Generate pyang tree HTML for a single MIB YANG file"""
    module_name = yang_file.stem
    
    try:
        # Run pyang to get tree output
        result = subprocess.run(
            ['pyang', '-f', 'tree', str(yang_file)],
            capture_output=True,
            text=True,
            cwd=yang_file.parent,
            timeout=30
        )
        
        # Check if pyang succeeded
        if result.returncode != 0:
            print(f"  ⚠️  Error generating tree for {module_name}")
            return False
        
        tree_output = result.stdout
        
        # Skip if output is empty or trivial
        if not tree_output or len(tree_output.strip()) < 20:
            print(f"  ⚠️  Skipping {module_name} (empty or trivial output)")
            return False
        
        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{module_name} - YANG Tree</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
            border-bottom: 4px solid #5a67d8;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .nav-links {{
            background: #f7fafc;
            padding: 16px 40px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .nav-links a {{
            color: #5a67d8;
            text-decoration: none;
            font-size: 14px;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.2s;
            background: white;
            border: 1px solid #e2e8f0;
        }}
        .nav-links a:hover {{
            background: #5a67d8;
            color: white;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(90, 103, 216, 0.2);
        }}
        .tree-container {{
            padding: 40px;
            background: #1a202c;
        }}
        .tree-output {{
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 8px;
            padding: 24px;
            overflow-x: auto;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }}
        pre {{
            color: #e2e8f0;
            font-size: 13px;
            line-height: 1.6;
            margin: 0;
            white-space: pre;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        .tree-output pre {{
            color: #68d391;
        }}
        .info-box {{
            background: #edf2f7;
            padding: 20px 40px;
            border-top: 1px solid #e2e8f0;
        }}
        .info-box p {{
            color: #4a5568;
            font-size: 13px;
            line-height: 1.6;
        }}
        .info-box a {{
            color: #5a67d8;
            text-decoration: none;
            font-weight: 500;
        }}
        .info-box a:hover {{
            text-decoration: underline;
        }}
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .header {{ padding: 20px; }}
            .tree-container {{ padding: 20px; }}
            .tree-output {{ padding: 16px; }}
            pre {{ font-size: 11px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {module_name}</h1>
            <p>MIB YANG Tree Visualization - IOS-XE 17.18.1</p>
        </div>
        
        <div class="nav-links">
            <a href="../index.html">🏠 Home</a>
            <a href="index.html">🌳 Tree Browser</a>
            <a href="https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17181/MIBS/{module_name}.yang" target="_blank">📄 YANG Source</a>
            <a href="../swagger-mib-model/api/{module_name}.json" target="_blank">📚 Swagger API Spec</a>
        </div>
        
        <div class="tree-container">
            <div class="tree-output">
                <pre>{html.escape(tree_output)}</pre>
            </div>
        </div>
        
        <div class="info-box">
            <p>
                <strong>About this tree:</strong> This visualization shows the hierarchical structure of the {module_name} MIB YANG module.
                Generated using <code>pyang -f tree</code> command.
                • <strong>+--rw</strong> = read-write node
                • <strong>+--ro</strong> = read-only node
                • <strong>+--</strong> = configuration data
                • <strong>x--</strong> = deprecated node
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        # Write HTML file
        output_file = output_dir / f"{module_name}.html"
        output_file.write_text(html_content, encoding='utf-8')
        
        print(f"  ✓ Generated {module_name}.html")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Timeout generating tree for {module_name}")
        return False
    except Exception as e:
        print(f"  ⚠️  Error processing {module_name}: {e}")
        return False


def generate_mib_tree_index(output_dir: Path, generated_files: list):
    """Generate index.html for browsing MIB trees"""
    
    # Sort files alphabetically
    generated_files.sort()
    
    # Group by prefix for better organization
    groups = {}
    for filename in generated_files:
        prefix = filename.split('-')[0] if '-' in filename else filename[0].upper()
        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(filename)
    
    # Generate module list HTML
    modules_html = ""
    for prefix in sorted(groups.keys()):
        modules_html += f'<div class="group-header">{prefix}</div>\n'
        for module in groups[prefix]:
            display_name = module.replace('.html', '')
            modules_html += f'        <div class="tree-item" data-name="{display_name.lower()}">\n'
            modules_html += f'            <a href="{module}">{display_name}</a>\n'
            modules_html += f'        </div>\n'
    
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIB YANG Tree Browser - Cisco IOS-XE 17.18.1</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 36px;
            margin-bottom: 12px;
            font-weight: 600;
        }}
        .header p {{
            font-size: 16px;
            opacity: 0.95;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            margin-top: 20px;
            border-radius: 8px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 13px;
            opacity: 0.9;
            margin-top: 4px;
        }}
        .controls {{
            padding: 30px 40px;
            background: #f7fafc;
            border-bottom: 1px solid #e2e8f0;
        }}
        .search-box {{
            width: 100%;
            padding: 14px 20px;
            font-size: 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            transition: all 0.2s;
        }}
        .search-box:focus {{
            outline: none;
            border-color: #5a67d8;
            box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.1);
        }}
        .nav-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 16px;
            flex-wrap: wrap;
        }}
        .nav-buttons a {{
            padding: 10px 20px;
            background: white;
            color: #5a67d8;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            border: 1px solid #e2e8f0;
            transition: all 0.2s;
        }}
        .nav-buttons a:hover {{
            background: #5a67d8;
            color: white;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(90, 103, 216, 0.2);
        }}
        .tree-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1px;
            background: #e2e8f0;
            padding: 40px;
        }}
        .group-header {{
            grid-column: 1 / -1;
            background: #5a67d8;
            color: white;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 14px;
            margin-top: 20px;
        }}
        .group-header:first-child {{
            margin-top: 0;
        }}
        .tree-item {{
            background: white;
            transition: all 0.2s;
        }}
        .tree-item a {{
            display: block;
            padding: 16px 20px;
            color: #2d3748;
            text-decoration: none;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .tree-item:hover {{
            background: #f7fafc;
            transform: translateX(4px);
        }}
        .tree-item:hover a {{
            color: #5a67d8;
        }}
        .tree-item.hidden {{
            display: none;
        }}
        .no-results {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: #718096;
            font-size: 16px;
            display: none;
        }}
        @media (max-width: 768px) {{
            .tree-grid {{
                grid-template-columns: 1fr;
                padding: 20px;
            }}
            .stats {{
                flex-direction: column;
                gap: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌳 MIB YANG Tree Browser</h1>
            <p>Browse pyang tree visualizations for {len(generated_files)} MIB modules</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(generated_files)}</div>
                    <div class="stat-label">MIB Trees</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(groups)}</div>
                    <div class="stat-label">Groups</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <input type="text" 
                   class="search-box" 
                   id="searchBox" 
                   placeholder="🔍 Search MIB modules... (e.g., CISCO, BGP, SNMP)"
                   onkeyup="filterTrees()">
            <div class="nav-buttons">
                <a href="../index.html">🏠 Home</a>
                <a href="../yang-trees/index.html">🌳 Main YANG Trees</a>
                <a href="../swagger-mib-model/">📚 MIB Swagger Specs</a>
            </div>
        </div>
        
        <div class="tree-grid" id="treeGrid">
{modules_html}
            <div class="no-results" id="noResults">
                No MIB modules found matching your search.
            </div>
        </div>
    </div>

    <script>
        function filterTrees() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const items = document.querySelectorAll('.tree-item');
            const groups = document.querySelectorAll('.group-header');
            let visibleCount = 0;
            
            items.forEach(item => {{
                const name = item.getAttribute('data-name');
                if (name.includes(searchTerm)) {{
                    item.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    item.classList.add('hidden');
                }}
            }});
            
            // Hide/show group headers based on visibility of their items
            groups.forEach(group => {{
                let hasVisibleItems = false;
                let currentElement = group.nextElementSibling;
                
                while (currentElement && !currentElement.classList.contains('group-header')) {{
                    if (currentElement.classList.contains('tree-item') && !currentElement.classList.contains('hidden')) {{
                        hasVisibleItems = true;
                        break;
                    }}
                    currentElement = currentElement.nextElementSibling;
                }}
                
                group.style.display = hasVisibleItems ? 'block' : 'none';
            }});
            
            // Show/hide no results message
            document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
        }}
    </script>
</body>
</html>
"""
    
    index_file = output_dir / "mib-trees-index.html"
    index_file.write_text(index_html, encoding='utf-8')
    print(f"\n✓ Generated MIB tree index: {index_file}")


def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    yang_dir = script_dir.parent / 'references' / '17181-YANG-modules' / 'MIBS'
    output_dir = script_dir.parent / 'yang-trees'
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating pyang trees for MIB YANG modules...")
    print(f"Source: {yang_dir}")
    print(f"Output: {output_dir}\n")
    
    # Get all YANG files in MIBS directory
    yang_files = sorted(yang_dir.glob('*.yang'))
    total_files = len(yang_files)
    
    print(f"Found {total_files} MIB YANG files\n")
    
    generated_files = []
    skipped = 0
    
    for i, yang_file in enumerate(yang_files, 1):
        print(f"[{i}/{total_files}] Processing {yang_file.stem}...")
        
        if generate_tree_html(yang_file, output_dir):
            generated_files.append(f"{yang_file.stem}.html")
        else:
            skipped += 1
    
    # Generate index
    if generated_files:
        generate_mib_tree_index(output_dir, generated_files)
    
    print(f"\n{'='*60}")
    print(f"✓ MIB Tree Generation Complete!")
    print(f"{'='*60}")
    print(f"  Generated: {len(generated_files)} trees")
    print(f"  Skipped:   {skipped} files")
    print(f"  Output:    {output_dir}")
    print(f"\nView index at: {output_dir / 'mib-trees-index.html'}")


if __name__ == "__main__":
    main()
