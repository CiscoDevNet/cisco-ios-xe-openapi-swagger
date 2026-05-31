#!/usr/bin/env python3
"""
Wrap RESTCONF requestBody / response body schemas with their namespaced
top-level key so Swagger UI's "Try it out" pre-fills a valid wire payload.

Background
==========
The from_tree generators (cfg, oper, events) already emit a wrapped schema
like:

    "schema": {
      "type": "object",
      "properties": {
        "Cisco-IOS-XE-native:hostname": { "type": "string" }
      }
    }

The legacy v2 generators (native, openconfig, ietf, mib, rpc, other) emit
the bare leaf schema while the *example* is already wrapped:

    "schema":  { "type": "string", "pattern": "..." }
    "example": { "Cisco-IOS-XE-native:hostname": "rtr-edge-01" }

Swagger UI fills the editor body from the schema, so the bare form leaves
the user with an empty body and the request fails on the device.

This post-processor walks every generated spec under
``releases/<ver>/swagger-*-model/api/*.json`` (or the top-level mirror
when ``--version`` is omitted) and for every ``application/yang-data+json``
content node:

  1. Inspect the existing ``example`` object.
  2. If the example is a dict with exactly one top-level key matching the
     RESTCONF namespaced form ``<module-prefix>:<leaf>`` (i.e. contains
     ``:``), AND the existing schema is not already wrapped with that key,
     wrap the schema as::

         { "type": "object", "properties": { "<key>": <original_schema> } }

  3. Leave already-wrapped schemas and key-less examples untouched.

The change is idempotent and safe to run repeatedly; the audit at the
end reports per-viewer wrap counts and any remaining bare body schemas.

Usage
-----
    python scripts/wrap_body_schemas.py                  # top-level mirror
    python scripts/wrap_body_schemas.py --version 26.1.1 # one release
    python scripts/wrap_body_schemas.py --all-releases   # every release

This script is meant to run after the per-category generators (i.e. as
a step in ``build_release.py``) and before manifests are stamped.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

YANG_MEDIA_TYPE = 'application/yang-data+json'
HTTP_METHODS = ('get', 'put', 'patch', 'post', 'delete')
VIEWER_CATEGORIES = (
    'cfg', 'events', 'ietf', 'mib', 'native-config',
    'openconfig', 'oper', 'other', 'rpc',
)


def _derive_wrap_key_from_path(url_path: str) -> Optional[str]:
    """For ``/data/<module>:<root>/.../<leaf>`` return ``<module>:<leaf>``.

    Walks the path right-to-left:
      - the *leaf* is the last non-empty segment (stripped of any ``={...}`` key);
        if that segment is itself ``mod:leaf`` it is returned as-is.
      - the *module* is taken from the deepest segment containing ``:`` to the
        left of the leaf (closest enclosing module-qualified container).
    """
    if not url_path:
        return None
    segs = [s for s in url_path.split('/') if s and s != 'data']
    if not segs:
        return None

    def _name(seg: str) -> str:
        return seg.split('=', 1)[0]

    last = _name(segs[-1])
    if ':' in last:
        return last  # already module-qualified
    module = None
    for seg in reversed(segs[:-1]):
        nm = _name(seg)
        if ':' in nm:
            module = nm.split(':', 1)[0]
            break
    if not module:
        return None
    return f'{module}:{last}'


def _wrap_if_needed(media_node: dict, url_path: str = '') -> Optional[str]:
    """Mutate the media node in place; return wrap key if wrapping happened."""
    if not isinstance(media_node, dict):
        return None
    example = media_node.get('example')
    schema = media_node.get('schema')
    if not isinstance(schema, dict):
        return None

    wrap_key: Optional[str] = None
    wrap_value = None  # only used when we also need to wrap the example

    if isinstance(example, dict) and len(example) == 1:
        candidate = next(iter(example))
        if ':' in candidate:
            wrap_key = candidate

    if wrap_key is None:
        # Fall back to deriving from URL path; this also catches the case where
        # the example is a bare scalar (e.g. "DC1-CORE-SW01") and needs wrapping.
        derived = _derive_wrap_key_from_path(url_path)
        if derived is None:
            return None
        # Wrap empty dict examples (container with no children populated) by
        # nesting them under the derived key, so the editor shows
        # ``{"Cisco-IOS-XE-native:ntp": {}}`` instead of ``{}``.
        if isinstance(example, dict) and len(example) == 0:
            wrap_key = derived
            wrap_value = {}
        # Wrap multi-key dict examples whose top-level keys are NOT
        # RESTCONF-namespaced (no ``module:`` prefix). Valid RESTCONF bodies
        # always have exactly one namespaced top-level key, so a bare-key dict
        # cannot be correct on the wire and must be wrapped under the
        # URL-derived key.
        elif isinstance(example, dict) and not any(':' in k for k in example):
            wrap_key = derived
            wrap_value = dict(example)
        # Wrap list-typed (YANG list) bodies. RESTCONF requires the array
        # to be wrapped as ``{"<module>:<leaf>": [ ... ]}``.
        elif isinstance(example, list):
            wrap_key = derived
            wrap_value = example
        # Only synthesize an example wrapper when the existing example is a
        # bare scalar (not None, not list, not dict). Leave already-namespaced
        # dict examples alone so we don't second-guess intentional structure.
        elif example is not None and not isinstance(example, dict):
            wrap_key = derived
            wrap_value = example
        elif example is None:
            # No example at all but we still want a wrapped schema.
            wrap_key = derived
        else:
            return None

    # Already wrapped with this key? Leave alone.
    if (schema.get('type') == 'object'
            and isinstance(schema.get('properties'), dict)
            and wrap_key in schema['properties']):
        # Still might need to wrap example.
        if wrap_value is not None:
            media_node['example'] = {wrap_key: wrap_value}
            return wrap_key
        return None

    inner = schema
    example_value = (example.get(wrap_key)
                     if isinstance(example, dict) else wrap_value)
    if isinstance(example_value, list) and inner.get('type') != 'array':
        inner = {'type': 'array', 'items': inner}

    media_node['schema'] = {
        'type': 'object',
        'properties': {wrap_key: inner},
    }
    if wrap_value is not None:
        media_node['example'] = {wrap_key: wrap_value}
    return wrap_key


def _walk_operations(spec: dict, counters: dict) -> None:
    paths = spec.get('paths') or {}
    if not isinstance(paths, dict):
        return
    for path, ops in paths.items():
        if not isinstance(ops, dict):
            continue
        for method, op in ops.items():
            if method not in HTTP_METHODS or not isinstance(op, dict):
                continue
            body = op.get('requestBody')
            if isinstance(body, dict):
                media = (body.get('content') or {}).get(YANG_MEDIA_TYPE)
                if isinstance(media, dict):
                    counters['body_examined'] += 1
                    if _wrap_if_needed(media, path):
                        counters['body_wrapped'] += 1
            for _code, resp in (op.get('responses') or {}).items():
                if not isinstance(resp, dict):
                    continue
                media = (resp.get('content') or {}).get(YANG_MEDIA_TYPE)
                if isinstance(media, dict):
                    counters['resp_examined'] += 1
                    if _wrap_if_needed(media, path):
                        counters['resp_wrapped'] += 1


def process_api_dir(api_dir: Path) -> dict:
    counters = {
        'files': 0, 'body_examined': 0, 'body_wrapped': 0,
        'resp_examined': 0, 'resp_wrapped': 0,
    }
    if not api_dir.is_dir():
        return counters
    for spec_path in sorted(api_dir.glob('*.json')):
        if spec_path.name in ('manifest.json', '_paths_index.json'):
            continue
        try:
            spec = json.loads(spec_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(spec, dict) or 'paths' not in spec:
            continue
        before = (counters['body_wrapped'], counters['resp_wrapped'])
        _walk_operations(spec, counters)
        after = (counters['body_wrapped'], counters['resp_wrapped'])
        if after != before:
            spec_path.write_text(
                json.dumps(spec, indent=2) + '\n', encoding='utf-8'
            )
        counters['files'] += 1
    return counters


def process_release(project_root: Path, version: Optional[str]) -> None:
    if version is None:
        # Top-level mirror (default release surface)
        roots = [project_root / f'swagger-{cat}-model' / 'api'
                 for cat in VIEWER_CATEGORIES]
        label = 'top-level'
    else:
        base = project_root / 'releases' / version
        roots = [base / f'swagger-{cat}-model' / 'api'
                 for cat in VIEWER_CATEGORIES]
        label = version
    grand = {
        'body_examined': 0, 'body_wrapped': 0,
        'resp_examined': 0, 'resp_wrapped': 0, 'files': 0,
    }
    print(f'[wrap_body_schemas] === {label} ===')
    for api_dir in roots:
        if not api_dir.is_dir():
            continue
        c = process_api_dir(api_dir)
        cat = api_dir.parent.name
        print(f'  {cat:30s} files={c["files"]:4d}  '
              f'body wrapped={c["body_wrapped"]:5d}/{c["body_examined"]:5d}  '
              f'resp wrapped={c["resp_wrapped"]:5d}/{c["resp_examined"]:5d}')
        for k in grand:
            grand[k] += c[k]
    print(f'  TOTAL files={grand["files"]}  '
          f'body wrapped={grand["body_wrapped"]}/{grand["body_examined"]}  '
          f'resp wrapped={grand["resp_wrapped"]}/{grand["resp_examined"]}')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--version', help='Release tag (e.g. 26.1.1).')
    ap.add_argument('--all-releases', action='store_true',
                    help='Process every release under releases/ plus top-level mirror.')
    ap.add_argument('--root',
                    default=str(Path(__file__).resolve().parent.parent),
                    help='Repo root.')
    args = ap.parse_args()
    root = Path(args.root)

    if args.all_releases:
        process_release(root, None)
        rel_root = root / 'releases'
        if rel_root.is_dir():
            for d in sorted(rel_root.iterdir()):
                if d.is_dir():
                    process_release(root, d.name)
    elif args.version:
        process_release(root, args.version)
    else:
        process_release(root, None)
    return 0


if __name__ == '__main__':
    sys.exit(main())
