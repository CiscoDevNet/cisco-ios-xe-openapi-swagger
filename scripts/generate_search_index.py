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

        # Top-level path map: { <yang-container-name-lowercased>: <operationId> }
        # for paths exactly one level under the YANG root (e.g.
        # /data/Cisco-IOS-XE-native:native/iox).  Used by search.js to
        # deep-link a keyword hit straight to that container's operation
        # instead of just opening the spec at the top of the page.
        #
        # We also collect depth-2 entries (e.g. "Loopback", "GigabitEthernet",
        # "bgp", "vlan") into the same map so a search for a common YANG
        # leaf-container name lands on its specific operation, not just the
        # parent module root.  First writer wins, so depth-1 hits always
        # take precedence (intentional: a top-level container is a better
        # landing page than a deeply nested keyword collision).
        top_paths: dict[str, str] = {}
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            segs = [s for s in path.split('/') if s]
            # Drop /data/ or /operations/ prefix.
            if segs and segs[0] in ('data', 'operations'):
                segs = segs[1:]
            if segs and segs[0] in ('restconf',):
                segs = segs[1:]
                if segs and segs[0] in ('data', 'operations'):
                    segs = segs[1:]
            # Drop the YANG namespace prefix on the root segment.
            if segs and ':' in segs[0]:
                segs = segs[1:]
            # Strip RESTCONF list-keys from any remaining segment so we
            # match the YANG container name, not the keyed instance.
            segs = [s.split('=', 1)[0] for s in segs]
            if not segs:
                continue

            op_id = None
            for verb in ('get', 'put', 'patch', 'post', 'delete'):
                op = methods.get(verb)
                if isinstance(op, dict) and op.get('operationId'):
                    op_id = op['operationId']
                    break
            if not op_id:
                continue

            # depth-1 (root child) — high-quality landing target.
            if len(segs) == 1 and segs[0]:
                k1 = segs[0].lower()
                if k1 not in top_paths:
                    top_paths[k1] = op_id
            # depth-2 — used to deep-link Loopback / GigabitEthernet / bgp / vlan.
            elif len(segs) == 2 and segs[1]:
                k2 = segs[1].lower()
                if k2 not in top_paths:
                    top_paths[k2] = op_id

        # NOTE: displayCategory, emoji, and swaggerUrl are intentionally
        # omitted here — search.js hydrates them from the top-level
        # `categories` lookup map at load time. This cuts ~150 KB off the
        # uncompressed payload across 1.3k+ modules.
        module_entry = {
            'name': module_name,
            'type': type_name,
            'category': dir_name,
            'description': desc,
            'keywords': sorted(list(keywords))[:50],
            'pathCount': len(paths),
            'version': version,
        }
        if top_paths:
            module_entry['topPaths'] = top_paths
        modules.append(module_entry)

    return count, endpoints


def build_index_for_root(root_dir):
    """Scan ``<root_dir>/swagger-*-model/api/*.json`` and return a full
    index dict ready to be JSON-dumped. Mutates module-level state, so
    callers must reset ``modules``, ``by_category`` and ``total_endpoints``
    before calling. Returns ``None`` when no api dirs are found under root.
    """
    global modules, total_endpoints, by_category
    modules = []
    total_endpoints = 0
    by_category = {}
    found_any = False
    for dir_name, (type_name, display_cat, emoji) in MODEL_DIRS.items():
        api_dir = os.path.join(root_dir, dir_name, 'api')
        if not os.path.isdir(api_dir):
            continue
        found_any = True
        count, eps = index_api_dir(api_dir, dir_name, type_name, display_cat, emoji, 'v2')
        total_endpoints += eps
        by_category[dir_name] = count
    if not found_any:
        return None
    categories = {
        dir_name: {'displayCategory': display_cat, 'emoji': emoji}
        for dir_name, (_t, display_cat, emoji) in MODEL_DIRS.items()
    }
    return {
        'version': '3.1',
        'generated': datetime.date.today().isoformat(),
        'stats': {
            'total_modules': len(modules),
            'total_endpoints': total_endpoints,
            'by_category': by_category,
        },
        'categories': categories,
        'modules': list(modules),
    }


def main():
    # The top-level swagger-*-model/api/ directories have been removed -- the
    # viewers always fetch from releases/<ver>/swagger-*-model/api/ now (no
    # default-version shortcut). The root search-index.json is therefore built
    # from releases/<default_version>/ so the unversioned page (which is what
    # the landing page links to) still has a hydrated search index.
    releases_root = os.path.join(BASE, 'releases')
    default_ver = None
    releases_idx = os.path.join(releases_root, 'index.json')
    if os.path.isfile(releases_idx):
        try:
            default_ver = json.load(open(releases_idx, encoding='utf-8')).get('default')
        except Exception:
            default_ver = None
    if not default_ver:
        raise SystemExit('cannot determine default version from releases/index.json')

    default_dir = os.path.join(releases_root, default_ver)
    index = build_index_for_root(default_dir)
    if index is None:
        raise SystemExit(f'no swagger-*-model/api directories found under releases/{default_ver}/')
    out_path = os.path.join(BASE, 'search-index.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"search-index.json (from releases/{default_ver}): {index['stats']['total_modules']} modules, "
          f"{index['stats']['total_endpoints']} endpoints  -> {out_path}")

    # 2. Per-release indexes -- search.js fetches releases/<ver>/search-index.json
    #    first, falling back to the root file. Without this, switching
    #    release in the version dropdown still searched the default release.
    if os.path.isdir(releases_root):
        for ver in sorted(os.listdir(releases_root)):
            rel_dir = os.path.join(releases_root, ver)
            if not os.path.isdir(rel_dir):
                continue
            rel_index = build_index_for_root(rel_dir)
            if rel_index is None:
                continue
            rel_out = os.path.join(rel_dir, 'search-index.json')
            with open(rel_out, 'w', encoding='utf-8') as f:
                json.dump(rel_index, f, indent=2, ensure_ascii=False)
                f.write('\n')
            print(f"  release {ver}: {rel_index['stats']['total_modules']} modules  -> {rel_out}")


if __name__ == '__main__':
    main()
