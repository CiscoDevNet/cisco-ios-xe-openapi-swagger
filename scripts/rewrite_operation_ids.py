#!/usr/bin/env python3
"""Rewrite all operationIds in OpenAPI specs to be path-derived and unique.

OpenAPI 3.0 mandates that operationIds are unique within a single document.
Many of our generators historically produced ids from just the last path
segment (e.g. ``get-switch``), which collides whenever the same YANG leaf
name appears under two different containers (e.g. ``/iox/switch`` and
``/hw-module/switch``). That breaks deep-link expansion in the viewers
because the lookup hits the first matching id and expands the wrong row.

This script reads every spec under

  - ``swagger-*-model/api/*.json``                       (live viewer copies)
  - ``releases/<ver>/swagger-*-model/api/*.json``        (per-release archives)

and rewrites every operationId to ``<verb>-<slug>``, where slug is derived
from the URL path:

  /data/Cisco-IOS-XE-native:native/iox/switch        GET  -> get-iox-switch
  /data/Cisco-IOS-XE-native:native/hw-module/switch  GET  -> get-hw-module-switch
  /data/.../interface/GigabitEthernet={name}         GET  -> get-interface-gigabitethernet-by-name
  /operations/Cisco-IOS-XE-rpc:default                POST -> post-rpc-default

Algorithm
---------
1. Strip a leading ``/data/`` or ``/operations/``.
2. Strip the namespace prefix on the first segment (``Cisco-IOS-XE-native:``).
3. Drop the root container name (it's the same for every path in the file).
4. For each remaining segment:
   - if it's a list-key marker ``foo={name}`` → ``foo-by-name``
   - else → segment as-is (lowercased)
5. Hyphen-join all remaining parts and prefix with the HTTP verb.
6. If the resulting id still collides within the same file (rare, but can
   happen for two paths that differ only in a stripped list-key), append a
   numeric suffix ``-2``, ``-3``, … in path-sort order.

The script also rewrites ``operationRef`` strings that point at these ids
if any exist (none in the current corpus, but the logic is here for
defensive correctness).
"""
from __future__ import annotations
import argparse, glob, json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERBS = ('get', 'put', 'patch', 'post', 'delete', 'head', 'options', 'trace')

# Lowercase a-z0-9-, collapse runs of separators, strip leading/trailing.
_SLUG_BAD = re.compile(r'[^a-z0-9]+')


def _norm(part: str) -> str:
    s = _SLUG_BAD.sub('-', part.lower()).strip('-')
    return s


def _segment_slug(seg: str) -> str:
    # foo={key}   -> foo-by-key
    # foo={a},{b} -> foo-by-a-b
    m = re.match(r'^([^=]+)=(.+)$', seg)
    if m:
        head = _norm(m.group(1))
        # extract placeholder names from {a},{b} etc.
        keys = re.findall(r'\{([^}]+)\}', m.group(2))
        if keys:
            tail = '-by-' + '-'.join(_norm(k) for k in keys)
        else:
            tail = '-by-' + _norm(m.group(2))
        return head + tail
    return _norm(seg)


def path_to_slug(path: str) -> str:
    """Return the dash-joined slug for a single URL path (no verb prefix)."""
    p = path.lstrip('/')
    # Strip /data/ or /operations/ prefix (the only top-level RESTCONF roots).
    for prefix in ('data/', 'operations/', 'restconf/data/', 'restconf/operations/'):
        if p.startswith(prefix):
            p = p[len(prefix):]
            break
    if not p:
        return 'root'
    segs = [s for s in p.split('/') if s]
    # The first segment usually carries a YANG namespace prefix
    # (Cisco-IOS-XE-native:native). Strip it and drop the root container name
    # since every path in this file shares that root anyway.
    if segs and ':' in segs[0]:
        segs = segs[1:]
    parts = [_segment_slug(s) for s in segs]
    parts = [p for p in parts if p]
    return '-'.join(parts) if parts else 'root'


def unique_op_id(verb: str, path: str, seen: dict[str, int]) -> str:
    base = f'{verb.lower()}-{path_to_slug(path)}'
    if base not in seen:
        seen[base] = 1
        return base
    seen[base] += 1
    return f'{base}-{seen[base]}'


def rewrite_spec(spec: dict, *, dry: bool) -> tuple[int, int]:
    """Rewrite operationIds in-place. Returns (changed, total)."""
    paths = spec.get('paths') or {}
    if not isinstance(paths, dict):
        return 0, 0

    # Pass 1: in stable path-sort order, build new ids.
    seen: dict[str, int] = {}
    new_ids: dict[tuple[str, str], str] = {}  # (path, verb) -> new id
    old_to_new: dict[str, str] = {}            # old id -> new id (best-effort,
                                               # used for operationRef rewrites)

    for path in sorted(paths.keys()):
        methods = paths.get(path) or {}
        if not isinstance(methods, dict):
            continue
        for verb, op in methods.items():
            if verb not in VERBS or not isinstance(op, dict):
                continue
            new_id = unique_op_id(verb, path, seen)
            new_ids[(path, verb)] = new_id

    # Pass 2: write the new ids.
    changed = total = 0
    for (path, verb), new_id in new_ids.items():
        op = paths[path][verb]
        old = op.get('operationId')
        total += 1
        if old == new_id:
            continue
        if old:
            old_to_new[old] = new_id
        if not dry:
            op['operationId'] = new_id
        changed += 1

    # Defensive: rewrite any string-typed `operationRef` that still points at
    # an old id. The current corpus has none, but it's cheap insurance.
    def walk(node):
        if isinstance(node, dict):
            ref = node.get('operationRef')
            if isinstance(ref, str):
                # operationRef is typically a JSON-ref-ish string; we only
                # patch the trailing identifier when it matches an old id.
                tail = ref.rsplit('/', 1)[-1]
                if tail in old_to_new and not dry:
                    node['operationRef'] = ref[: -len(tail)] + old_to_new[tail]
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(spec)
    return changed, total


def find_spec_dirs(version: str | None = None) -> list[str]:
    # When invoked from build_release.py with --version, scope the scan to
    # that release's spec tree so the pipeline cost stays bounded. Without
    # --version we touch every release (used by ad-hoc audits and the
    # one-shot global cleanup).
    if version:
        rel = os.path.join(ROOT, 'releases', version, 'swagger-*-model', 'api')
        live = os.path.join(ROOT, 'swagger-*-model', 'api')
        return sorted(glob.glob(rel)) + sorted(glob.glob(live))
    dirs = sorted(glob.glob(os.path.join(ROOT, 'swagger-*-model', 'api')))
    dirs += sorted(glob.glob(os.path.join(ROOT, 'releases', '*', 'swagger-*-model', 'api')))
    return dirs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='do not write files')
    ap.add_argument('--only', help='glob to limit which spec files are touched')
    ap.add_argument('--version', help='only rewrite specs for this release version')
    args = ap.parse_args()

    grand_changed = grand_total = grand_files = 0
    file_changes: list[tuple[str, int, int]] = []

    for api_dir in find_spec_dirs(args.version):
        for fp in sorted(glob.glob(os.path.join(api_dir, '*.json'))):
            if fp.endswith('manifest.json'):
                continue
            if args.only and args.only not in fp:
                continue
            try:
                with open(fp, encoding='utf-8') as f:
                    spec = json.load(f)
            except Exception as e:
                print(f'  ! skip {fp}: {e}', file=sys.stderr)
                continue
            changed, total = rewrite_spec(spec, dry=args.dry_run)
            grand_changed += changed
            grand_total += total
            grand_files += 1
            if changed:
                file_changes.append((fp, changed, total))
                if not args.dry_run:
                    with open(fp, 'w', encoding='utf-8') as f:
                        json.dump(spec, f, indent=2, ensure_ascii=False)
                        f.write('\n')

    action = 'WOULD change' if args.dry_run else 'changed'
    print(f'{grand_files} spec files scanned | {grand_total} operations | '
          f'{action} {grand_changed} operationIds across {len(file_changes)} files')

    # Re-audit duplicates after rewrite (sanity check, in-memory).
    if not args.dry_run:
        from collections import Counter as _C
        leftover_dups = 0
        leftover_files = 0
        for api_dir in find_spec_dirs(args.version):
            for fp in sorted(glob.glob(os.path.join(api_dir, '*.json'))):
                if fp.endswith('manifest.json'):
                    continue
                try:
                    spec = json.load(open(fp, encoding='utf-8'))
                except Exception:
                    continue
                ids = []
                for p, ms in (spec.get('paths') or {}).items():
                    if not isinstance(ms, dict):
                        continue
                    for v, op in ms.items():
                        if isinstance(op, dict) and 'operationId' in op:
                            ids.append(op['operationId'])
                d = sum(c - 1 for c in _C(ids).values() if c > 1)
                if d:
                    leftover_dups += d
                    leftover_files += 1
        print(f'post-rewrite duplicate surplus: {leftover_dups} '
              f'across {leftover_files} files')
        return 1 if leftover_dups else 0
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
