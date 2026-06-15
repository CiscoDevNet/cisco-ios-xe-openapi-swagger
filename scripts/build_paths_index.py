#!/usr/bin/env python3
"""Build per-category _paths_index.json files for the cross-chunk operation
search feature in the Swagger viewers.

Runs for every active release. Each viewer's paths-search.js IIFE is gated
on __IOSXE_ACTIVE_VERSION__ so users see the wider search surface on the
release they are currently browsing.

Output schema (one file per category, written next to the v2 specs).
Entries are deduplicated to one row per (spec, path); HTTP methods and the
operationId for each method are kept as parallel arrays. Short keys are
used to keep the JSON small enough to fetch on viewer load.

    {
      "v": "26.1.1",
      "c": "native-config",
      "n": 4900,
      "ops": [
        {"s": "native-interfaces",
         "p": "/data/Cisco-IOS-XE-native:native/vlan",
         "t": "vlan",
         "sm": "Get vlan",
         "ms": ["get","put","patch","delete"],
         "ids": ["get-native-vlan","put-native-vlan",
                 "patch-native-vlan","delete-native-vlan"]},
        ...
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CATEGORIES = (
    "cfg",
    "events",
    "ietf",
    "mib",
    "native-config",
    "openconfig",
    "oper",
    "other",
    "rpc",
)
HTTP_METHODS = ("get", "put", "post", "patch", "delete", "head", "options")

# Per-operation keyword budget. Request-body schemas (especially native-config)
# can be enormous, so the searchable keyword blob extracted from nested property
# names + descriptions is capped to keep _paths_index.json small enough to fetch
# on viewer load. RPC bodies are tiny, so this fully covers cases like the
# hw-module "beacon" (Blue Beacon LED) leaf that is buried in the request body
# and was previously invisible to operation search.
_KW_MAX_CHARS = 600
_KW_MAX_DEPTH = 16
_KW_STOPWORDS = {
    "the", "and", "for", "this", "that", "with", "from", "type", "value",
    "object", "string", "which", "when", "will", "have", "been", "into",
    "system", "data", "name", "list", "config", "configuration",
}


def _resolve_ref(ref: str, root: dict) -> dict | None:
    """Resolve a same-document JSON pointer ($ref) to its schema object."""
    if not ref.startswith("#/"):
        return None
    node: object = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, dict) else None


def _collect_kw(schema, root, names, words, depth=0, seen=None):
    """Walk a request-body schema collecting property names + description words.

    Names are the highest-value tokens (e.g. ``beacon``). Descriptions add
    natural-language coverage (e.g. ``Control Blue Beacon LED``). Same-document
    ``$ref``s are resolved with a cycle guard. Bounded by depth and the caller's
    overall character budget.
    """
    if depth > _KW_MAX_DEPTH or not isinstance(schema, dict):
        return
    if "$ref" in schema:
        ref = schema["$ref"]
        if seen is None:
            seen = set()
        if ref in seen:
            return
        seen = seen | {ref}
        resolved = _resolve_ref(ref, root)
        if resolved is not None:
            _collect_kw(resolved, root, names, words, depth + 1, seen)
        return
    desc = schema.get("description")
    if isinstance(desc, str) and desc:
        for w in desc.replace("-", " ").split():
            w = "".join(c for c in w.lower() if c.isalnum())
            if len(w) >= 3 and w not in _KW_STOPWORDS:
                words.add(w)
    props = schema.get("properties")
    if isinstance(props, dict):
        for k, v in props.items():
            kl = str(k).lower()
            if len(kl) >= 2:
                names.add(kl)
            _collect_kw(v, root, names, words, depth + 1, seen)
    items = schema.get("items")
    if isinstance(items, dict):
        _collect_kw(items, root, names, words, depth + 1, seen)
    for comb in ("allOf", "oneOf", "anyOf"):
        arr = schema.get(comb)
        if isinstance(arr, list):
            for s in arr:
                _collect_kw(s, root, names, words, depth + 1, seen)


def _build_kw(methods: dict, root: dict) -> str:
    """Build the capped, deduplicated keyword blob for one (spec,path) row."""
    names: set[str] = set()
    words: set[str] = set()
    for method, op in methods.items():
        if method.lower() not in HTTP_METHODS or not isinstance(op, dict):
            continue
        body = op.get("requestBody")
        if not isinstance(body, dict):
            continue
        for media in (body.get("content") or {}).values():
            if isinstance(media, dict) and isinstance(media.get("schema"), dict):
                _collect_kw(media["schema"], root, names, words)
    if not names and not words:
        return ""
    # Property names first (most precise), then description words. Sorted for
    # determinism, joined and truncated to the per-op budget.
    ordered = sorted(names) + sorted(words - names)
    blob = " ".join(ordered)
    if len(blob) > _KW_MAX_CHARS:
        blob = blob[:_KW_MAX_CHARS].rsplit(" ", 1)[0]
    return blob



def build_one(api_dir: Path, version: str, category: str) -> int:
    rows: list[dict] = []
    for spec_path in sorted(api_dir.glob("*.json")):
        if spec_path.name in ("manifest.json", "_paths_index.json"):
            continue
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"  ! skip {spec_path.name}: {exc}", file=sys.stderr)
            continue
        spec_name = spec_path.stem
        paths = spec.get("paths") or {}
        for raw_path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            ms: list[str] = []
            ids: list[str] = []
            tag = ""
            summary = ""
            for method, op in methods.items():
                m = method.lower()
                if m not in HTTP_METHODS or not isinstance(op, dict):
                    continue
                ms.append(m)
                ids.append(op.get("operationId") or "")
                if not tag:
                    tags = op.get("tags") or []
                    if tags and isinstance(tags, list):
                        tag = str(tags[0])
                if not summary:
                    summary = op.get("summary") or ""
            if not ms:
                continue
            row = {
                "s": spec_name,
                "p": raw_path,
                "t": tag,
                "sm": summary,
                "ms": ms,
                "ids": ids,
            }
            kw = _build_kw(methods, spec)
            if kw:
                row["kw"] = kw
            rows.append(row)

    out = {
        "v": version,
        "c": category,
        "n": len(rows),
        "ops": rows,
    }
    out_path = api_dir / "_paths_index.json"
    out_path.write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", default="26.1.1",
                    help="Release version to index.")
    ap.add_argument("--root", default=".",
                    help="Repo root containing the releases/ directory.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    base = root / "releases" / args.version
    if not base.is_dir():
        print(f"[build_paths_index] ERROR: {base} not found", file=sys.stderr)
        return 1

    print(f"[build_paths_index] {args.version}")
    grand_total = 0
    for cat in CATEGORIES:
        api_dir = base / f"swagger-{cat}-model" / "api"
        if not api_dir.is_dir():
            print(f"  - {cat:14s}  MISSING ({api_dir.relative_to(root)})")
            continue
        n = build_one(api_dir, args.version, cat)
        grand_total += n
        print(f"  + {cat:14s}  {n:>6d} paths        -> {api_dir.relative_to(root)}/_paths_index.json")
    print(f"[build_paths_index] DONE  total paths indexed: {grand_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
