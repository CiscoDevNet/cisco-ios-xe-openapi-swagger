#!/usr/bin/env python3
"""Update nav bars in existing v2 index pages to include all 9 model types."""

import re

nav_links = [
    ('Home', '../index.html'),
    ('Oper (v2)', '../swagger-oper-model/index-v2.html'),
    ('Config (v2)', '../swagger-cfg-model/index-v2.html'),
    ('Native (v2)', '../swagger-native-config-model/index-v2.html'),
    ('OpenConfig (v2)', '../swagger-openconfig-model/index-v2.html'),
    ('RPC (v2)', '../swagger-rpc-model/index-v2.html'),
    ('IETF (v2)', '../swagger-ietf-model/index-v2.html'),
    ('MIB (v2)', '../swagger-mib-model/index-v2.html'),
    ('Events (v2)', '../swagger-events-model/index-v2.html'),
    ('Other (v2)', '../swagger-other-model/index-v2.html'),
]

pages = {
    'swagger-oper-model/index-v2.html': 'Oper (v2)',
    'swagger-cfg-model/index-v2.html': 'Config (v2)',
    'swagger-native-config-model/index-v2.html': 'Native (v2)',
    'swagger-openconfig-model/index-v2.html': 'OpenConfig (v2)',
}

def main():
    for page, active_label in pages.items():
        with open(page, encoding='utf-8') as f:
            content = f.read()
        
        # Build nav HTML
        nav_parts = []
        for label, href in nav_links:
            cls = ' class="active"' if label == active_label else ''
            nav_parts.append(f'        <a href="{href}"{cls}>{label}</a>')
        nav_html = '\n'.join(nav_parts)
        
        # Replace everything between <nav class="nav-bar"> and the tree browser link
        pattern = r'(<nav class="nav-bar">)\s*\n(.*?)(\s*<a href="../yang-trees/)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            new_content = content[:match.end(1)] + '\n' + nav_html + '\n' + content[match.start(3):]
            with open(page, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'{page}: nav updated')
        else:
            print(f'{page}: nav NOT FOUND')

    # Also update v1 index.html pages to add v2 link button
    v1_pages = [
        'swagger-mib-model/index.html',
        'swagger-rpc-model/index.html', 
        'swagger-ietf-model/index.html',
        'swagger-events-model/index.html',
        'swagger-other-model/index.html',
    ]

    for page in v1_pages:
        try:
            with open(page, encoding='utf-8') as f:
                content = f.read()
            
            # Check if v2 link already exists
            if 'index-v2.html' in content:
                print(f'{page}: v2 link already exists')
                continue
            
            # Try to add v2 button to nav bar
            # Look for closing </nav> or Tree Browser link
            tree_pattern = r'(<a[^>]*yang-trees[^>]*>.*?</a>)'
            tree_match = re.search(tree_pattern, content)
            if tree_match:
                v2_button = '<a href="index-v2.html" style="background: #1565C0; color: white; padding: 6px 14px; border-radius: 4px; font-size: 13px; text-decoration: none;">v2 ↗</a>\n        '
                new_content = content[:tree_match.start()] + v2_button + content[tree_match.start():]
                with open(page, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'{page}: v2 link added')
            else:
                print(f'{page}: no tree link found to insert before')
        except FileNotFoundError:
            print(f'{page}: NOT FOUND')

    print('\nDone!')

if __name__ == '__main__':
    main()
