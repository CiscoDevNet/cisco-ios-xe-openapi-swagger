#!/usr/bin/env python3
"""Generate YANG-like tree HTML files from OpenAPI specs for modules missing trees.

Reads the Swagger spec paths and schemas to produce a pyang-style tree view,
then wraps it in the same styled HTML used by existing tree files.

Targets:
  - 17 openconfig specs without trees
  - 3 ietf specs without trees
  - 1 other spec without tree
  - 27 native-config specs without trees (total: 48)
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREE_DIR = os.path.join(ROOT, 'yang-trees')


def build_tree_from_paths(spec):
    """Build a tree structure from OpenAPI paths."""
    tree = {}
    module_prefix = None

    for path in sorted(spec.get('paths', {}).keys()):
        # Strip /data/ prefix
        clean = path.replace('/data/', '')

        # Extract module prefix from first segment
        segments = clean.split('/')
        if not segments:
            continue

        first = segments[0]
        if ':' in first and not module_prefix:
            module_prefix = first.split(':')[0]
            segments[0] = first.split(':', 1)[1]
        elif ':' in first:
            segments[0] = first.split(':', 1)[1]

        # Get methods for this path
        pv = spec['paths'][path]
        methods = []
        for m in ('get', 'post', 'put', 'patch', 'delete'):
            if m in pv:
                methods.append(m)

        # Determine if this is config (rw) or state (ro)
        is_state = any(s in ('state', 'oper') for s in segments)
        is_config = any(s == 'config' for s in segments)
        rw = 'ro' if is_state else 'rw'

        # Build nested dict
        node = tree
        for seg in segments:
            # Clean key parameters
            key_match = re.match(r'(.+?)=\{(.+?)\}', seg)
            if key_match:
                seg = key_match.group(1)
                keys = key_match.group(2).split('},{')
                keys = [k.strip('{}') for k in keys]
            else:
                keys = None

            if seg not in node:
                node[seg] = {'_children': {}, '_keys': None, '_rw': rw, '_methods': []}
            if keys:
                node[seg]['_keys'] = keys
            node[seg]['_methods'] = methods
            node[seg]['_rw'] = rw
            node = node[seg]['_children']

    return tree, module_prefix


def render_tree_text(tree, indent=0, is_last=True, prefix=''):
    """Render tree structure as pyang-style text."""
    lines = []
    items = list(tree.items())
    items = [(k, v) for k, v in items if not k.startswith('_')]

    for i, (name, node) in enumerate(items):
        last = (i == len(items) - 1)
        rw = node.get('_rw', 'rw')
        keys = node.get('_keys')
        children = {k: v for k, v in node.get('_children', {}).items() if not k.startswith('_')}

        # Build the connector
        if indent == 0:
            connector = ''
            child_prefix = '   '
        else:
            connector = prefix + ('+--' if last else '+--')
            child_prefix = prefix + ('   ' if last else '|  ')

        # Build the node label
        if keys:
            key_str = ' '.join('[%s]' % k for k in [','.join(keys)])
            label = '%s %s* %s' % (rw, name, key_str)
        elif children:
            label = '%s %s' % (rw, name)
        else:
            label = '%s %s?' % (rw, name)

        if indent == 0:
            lines.append('  %s%s' % (connector, label))
        else:
            lines.append('  %s%s' % (connector, label))

        # Recurse into children
        if children:
            child_lines = render_tree_text(
                children,
                indent=indent + 1,
                prefix=child_prefix
            )
            lines.extend(child_lines)

    return lines


def generate_tree_html(module_name, spec, tree_text):
    """Generate styled HTML for a tree view."""
    title = spec.get('info', {}).get('title', module_name)
    description = spec.get('info', {}).get('description', '')
    # Clean description for HTML
    description = description.replace('\n', ' ').strip()
    if len(description) > 200:
        description = description[:200] + '...'
    description = description.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')

    num_paths = len(spec.get('paths', {}))

    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%s - YANG Tree</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #f5f5f5;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #049fd9 0%%, #0070c9 100%%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 8px;
        }
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        .header a {
            color: white;
            text-decoration: underline;
            opacity: 0.9;
        }
        .header a:hover {
            opacity: 1;
        }
        .tree-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }
        pre {
            font-size: 13px;
            line-height: 1.4;
            white-space: pre;
            color: #333;
        }
        .footer {
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 8px;
            text-align: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 13px;
            color: #555;
        }
        .footer a {
            color: #049fd9;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .note {
            margin-top: 10px;
            padding: 10px 15px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 13px;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>%s</h1>
        <p>%s</p>
        <p style="margin-top: 8px;"><a href="index.html">&larr; Back to Tree Index</a></p>
    </div>
    <div class="note">
        This tree view was derived from the OpenAPI/Swagger specification (%d paths).
        It shows the RESTCONF resource hierarchy for this module.
    </div>
    <div class="tree-container" style="margin-top: 15px;">
        <pre>module: %s
%s</pre>
    </div>
    <div class="footer">
        Generated from OpenAPI spec &middot;
        <a href="../index.html">Home</a>
    </div>
</body>
</html>''' % (module_name, module_name, description, num_paths, module_name, tree_text)

    return html


def process_spec(folder, spec_name):
    """Generate tree HTML for a single spec."""
    filepath = os.path.join(ROOT, folder, 'api', spec_name + '.json')
    with open(filepath, encoding='utf-8') as f:
        spec = json.load(f)

    tree, module_prefix = build_tree_from_paths(spec)
    tree_lines = render_tree_text(tree)
    tree_text = '\n'.join(tree_lines)

    html = generate_tree_html(spec_name, spec, tree_text)

    out_path = os.path.join(TREE_DIR, spec_name + '.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return len(spec.get('paths', {}))


def main():
    # Load existing trees
    actual_trees = set(
        f.replace('.html', '')
        for f in os.listdir(TREE_DIR)
        if f.endswith('.html') and f != 'index.html' and f != 'mib-trees-index.html'
    )

    folders_to_check = [
        'swagger-openconfig-model',
        'swagger-ietf-model',
        'swagger-other-model',
        'swagger-native-config-model',
    ]

    total_created = 0
    all_new_names = []

    for folder in folders_to_check:
        api_dir = os.path.join(ROOT, folder, 'api')
        specs = [
            f.replace('.json', '')
            for f in sorted(os.listdir(api_dir))
            if f.endswith('.json') and f != 'manifest.json'
        ]

        missing = [s for s in specs if s not in actual_trees]
        if not missing:
            continue

        folder_count = 0
        for spec_name in missing:
            npaths = process_spec(folder, spec_name)
            folder_count += 1
            all_new_names.append(spec_name)

        print('  %s: created %d tree files' % (folder, folder_count))
        total_created += folder_count

    # Update tree-manifest.json
    if all_new_names:
        manifest_path = os.path.join(TREE_DIR, 'tree-manifest.json')
        raw = open(manifest_path, encoding='utf-8-sig').read()
        manifest = json.loads(raw)
        manifest_set = set(manifest)
        for name in all_new_names:
            if name not in manifest_set:
                manifest.append(name)
        manifest.sort()
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f)
            f.write('\n')
        print('\n  Updated tree-manifest.json: %d -> %d entries' % (len(manifest_set), len(manifest)))

    print('\nTotal: created %d tree HTML files' % total_created)


if __name__ == '__main__':
    main()
