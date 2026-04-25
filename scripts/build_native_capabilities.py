#!/usr/bin/env python3
"""
build_native_capabilities.py — Summarize the Cisco-IOS-XE-native config surface.

Walks every spec under ``releases/<ver>/swagger-native-config-model/api-v2/`` and
counts paths/operations/leafs/lists/choices per category file. Emits
``releases/<ver>/native-capabilities.json`` consumed by the Config Capabilities
summary page.

This deliberately uses a heuristic over the OpenAPI spec rather than re-parsing
YANG: it stays accurate as the spec generator evolves and does not require
pyang. Per VERSIONING.md / PROJECT_REQUIREMENTS.md §16.5.

Usage:
    python scripts/build_native_capabilities.py --version 26.1.1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import PROJECT_ROOT, ReleasePaths  # type: ignore  # noqa: E402

METHODS = ("get", "put", "patch", "post", "delete", "head", "options")


def _walk_schema(node, counts: dict, depth: int = 0) -> None:
    """Recursively walk a schema (or any nested dict) accumulating leaf/list/choice counts."""
    if depth > 30 or node is None:
        return
    if isinstance(node, list):
        for item in node:
            _walk_schema(item, counts, depth + 1)
        return
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "array":
        counts["lists"] += 1
        items = node.get("items")
        if items:
            _walk_schema(items, counts, depth + 1)
    elif t in {"string", "integer", "boolean", "number"}:
        counts["leafs"] += 1
    if "oneOf" in node or "anyOf" in node:
        counts["choices"] += 1
    for key in ("properties", "patternProperties"):
        props = node.get(key)
        if isinstance(props, dict):
            for _, child in props.items():
                _walk_schema(child, counts, depth + 1)
    for key in ("oneOf", "anyOf", "allOf"):
        for child in (node.get(key) or []):
            _walk_schema(child, counts, depth + 1)
    if "items" in node and t != "array":
        _walk_schema(node["items"], counts, depth + 1)


def count_schema_features(schemas: dict) -> tuple[int, int, int]:
    """Return (leaf_count, list_count, choice_count) over the components/schemas dict."""
    counts = {"leafs": 0, "lists": 0, "choices": 0}
    if isinstance(schemas, dict):
        for _, schema in schemas.items():
            _walk_schema(schema, counts)
    return counts["leafs"], counts["lists"], counts["choices"]


def count_path_features(paths: dict) -> tuple[int, int, int]:
    """Walk every operation's request/response inline schemas — the native specs
    keep most of their data shape there rather than in components.schemas."""
    counts = {"leafs": 0, "lists": 0, "choices": 0}
    for _, methods in (paths or {}).items():
        if not isinstance(methods, dict):
            continue
        for _, op in methods.items():
            if not isinstance(op, dict):
                continue
            rb = op.get("requestBody")
            if isinstance(rb, dict):
                for _, cdef in (rb.get("content") or {}).items():
                    if isinstance(cdef, dict):
                        _walk_schema(cdef.get("schema"), counts)
            for _, resp in (op.get("responses") or {}).items():
                if not isinstance(resp, dict):
                    continue
                for _, cdef in (resp.get("content") or {}).items():
                    if isinstance(cdef, dict):
                        _walk_schema(cdef.get("schema"), counts)
    return counts["leafs"], counts["lists"], counts["choices"]


def summarize_spec(spec_path: Path) -> dict:
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    paths = spec.get("paths") or {}
    op_count = 0
    method_counts: dict[str, int] = {m: 0 for m in METHODS}
    for _, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for m in METHODS:
            if m in methods:
                op_count += 1
                method_counts[m] += 1
    schemas = (spec.get("components") or {}).get("schemas") or {}
    s_leafs, s_lists, s_choices = count_schema_features(schemas)
    p_leafs, p_lists, p_choices = count_path_features(paths)
    leafs = s_leafs + p_leafs
    lists = s_lists + p_lists
    choices = s_choices + p_choices
    title = (spec.get("info") or {}).get("title", "")
    return {
        "file": spec_path.name,
        "title": title,
        "path_count": len(paths),
        "operation_count": op_count,
        "method_counts": method_counts,
        "leaf_count": leafs,
        "list_count": lists,
        "choice_count": choices,
        "schema_count": len(schemas),
    }


def derive_category(filename: str) -> str:
    m = re.match(r"^native-(?:\d+-)?(.+?)\.json$", filename)
    return m.group(1) if m else filename.removesuffix(".json")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", required=True)
    args = p.parse_args()

    rp = ReleasePaths(version=args.version, legacy=True)
    spec_dir = rp.spec_dir("swagger-native-config-model")
    if not spec_dir.is_dir():
        sys.stderr.write(f"[native-cap] missing native spec dir: {spec_dir}\n")
        return 1

    categories: list[dict] = []
    totals = {
        "path_count": 0, "operation_count": 0,
        "leaf_count": 0, "list_count": 0, "choice_count": 0, "schema_count": 0,
    }
    for spec in sorted(spec_dir.glob("*.json")):
        if spec.name == "manifest.json":
            continue
        s = summarize_spec(spec)
        if not s:
            continue
        s["category"] = derive_category(spec.name)
        categories.append(s)
        for k in totals:
            totals[k] += s.get(k, 0)

    out = rp.native_capabilities()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "version": args.version,
        "generated": datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
        "totals": totals,
        "categories": categories,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"[native-cap] wrote {out.relative_to(PROJECT_ROOT)} "
          f"(categories={len(categories)}, paths={totals['path_count']}, "
          f"leafs={totals['leaf_count']}, lists={totals['list_count']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
