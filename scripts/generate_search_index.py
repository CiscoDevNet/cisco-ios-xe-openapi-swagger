#!/usr/bin/env python3
"""Regenerate search-index.json from all OpenAPI specs (v1 + v2)."""
import json, os, re, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIRS = {
    'swagger-oper-model': ('operational', 'Operational Data', '🔵'),
    'swagger-cfg-model': ('configuration', 'Configuration', '🔧'),
    'swagger-native-config-model': ('native', 'Native Configuration', '🏠'),
    'swagger-openconfig-model': ('openconfig', 'OpenConfig', '🌍'),
    'swagger-ietf-model': ('ietf', 'IETF Standards', '📜'),
    'swagger-mib-model': ('mib', 'MIB Translations', '📡'),
    'swagger-rpc-model': ('rpc', 'RPC Operations', '⚡'),
    'swagger-events-model': ('events', 'Event Notifications', '🔔'),
    'swagger-other-model': ('other', 'Other Models', '📦'),
}

# NOTE: There is no longer a separate v1/v2 directory split — every viewer
# serves a single `api/` directory containing the tree-derived (v2) specs.
# The legacy V2_DIRS pass has been removed because it scanned the SAME
# directories as MODEL_DIRS, producing duplicate entries (every module
# appeared twice — once tagged v1, once tagged v2). See `version` field
# below: kept as 'v2' for historical/consumer compatibility.

modules = []
total_endpoints = 0
by_category = {}


def index_api_dir(api_dir, dir_name, type_name, display_cat, emoji, version):
    """Index all specs in an api directory. Returns (count, endpoints)."""
    count = 0
    endpoints = 0
    for fn in sorted(os.listdir(api_dir)):
        if not fn.endswith('.json') or fn == 'manifest.json':
            continue

        fp = os.path.join(api_dir, fn)
        with open(fp, 'r', encoding='utf-8') as f:
            spec = json.load(f)

        module_name = fn.replace('.json', '')
        count += 1

        # Extract description (truncate at word boundary for smaller index)
        desc = spec.get('info', {}).get('description', '')
        if len(desc) > 160:
            cut = desc[:160]
            sp = cut.rfind(' ')
            if sp > 120:
                cut = cut[:sp]
            desc = cut + '...'

        # Extract keywords from paths and tags
        keywords = set()
        paths = spec.get('paths', {})
        endpoints += len(paths)

        for path in paths:
            segments = path.split('/')
            for seg in segments:
                if ':' in seg:
                    clean = seg.split(':')[-1].split('=')[0]
                    keywords.add(clean)
                elif seg and seg != 'data' and seg != 'operations' and not seg.startswith('{'):
                    keywords.add(seg)

            for method in ['get', 'put', 'patch', 'delete', 'post']:
                op = paths[path].get(method, {})
                if isinstance(op, dict):
                    summary = op.get('summary', '')
                    if summary:
                        for word in summary.lower().split():
                            if len(word) > 3:
                                keywords.add(word.strip('.,()'))

        for tag in spec.get('tags', []):
            tag_name = tag.get('name', '')
            if tag_name:
                keywords.add(tag_name.lower())

        # NOTE: displayCategory, emoji, and swaggerUrl are intentionally
        # omitted here — search.js hydrates them from the top-level
        # `categories` lookup map at load time. This cuts ~150 KB off the
        # uncompressed payload across 1.3k+ modules.
        modules.append({
            'name': module_name,
            'type': type_name,
            'category': dir_name,
            'description': desc,
            'keywords': sorted(list(keywords))[:50],
            'pathCount': len(paths),
            'version': version,
        })

    return count, endpoints


def main():
    global total_endpoints
    # Single indexing pass — every viewer has exactly one `api/` directory.
    for dir_name, (type_name, display_cat, emoji) in MODEL_DIRS.items():
        api_dir = os.path.join(BASE, dir_name, 'api')
        if not os.path.isdir(api_dir):
            continue
        count, eps = index_api_dir(api_dir, dir_name, type_name, display_cat, emoji, 'v2')
        total_endpoints += eps
        by_category[dir_name] = count

    # Build a categories lookup: search.js (and downstream consumers via
    # hydration there) read displayCategory + emoji from this map instead
    # of every per-module record carrying duplicates.
    categories = {}
    for dir_name, (_t, display_cat, emoji) in MODEL_DIRS.items():
        categories[dir_name] = {'displayCategory': display_cat, 'emoji': emoji}
    # V2 entries share the same dir_name as v1; values already populated.

    index = {
        'version': '3.1',
        'generated': datetime.date.today().isoformat(),
        'stats': {
            'total_modules': len(modules),
            'total_endpoints': total_endpoints,
            'by_category': by_category,
        },
        'categories': categories,
        'modules': modules,
    }

    out_path = os.path.join(BASE, 'search-index.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"search-index.json regenerated: {len(modules)} modules, {total_endpoints} endpoints")
    print(f"  v1: {sum(1 for m in modules if m['version'] == 'v1')} modules")
    print(f"  v2: {sum(1 for m in modules if m['version'] == 'v2')} modules")
    print(f"File: {out_path}")

if __name__ == '__main__':
    main()
