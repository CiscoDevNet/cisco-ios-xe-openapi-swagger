#!/usr/bin/env python3
"""
apply_cisco_live_examples_overlay.py — Stamp real per-PID device responses onto
GET operations as the ``x-cisco-live-examples`` vendor extension.

Reads a committed sidecar (default ``references/live-examples-<version>.json``,
produced by ``scripts/harness/build_observed_examples.py --sidecar``) and, for
each entry, adds the per-PID captured response under
``responses.200.content.<media>.x-cisco-live-examples`` on the matching GET
operation. The synthetic ``example`` is left UNTOUCHED (agreed Phase 4 decision,
DEVICE_DATA_COLLECTION.md §11.0); the web app's viewer-enhancements.js renders a
"Live device sample - <PID>" panel beside it.

This runs in build_release.py AFTER the specs + synthetic examples are generated,
so the injection survives spec regeneration. It is additive metadata (a vendor
extension) and does NOT change path/operation/module counts (G-6 safe). Idempotent.

Usage:
    python scripts/apply_cisco_live_examples_overlay.py --version 26.1.1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def spec_api_dir(version: str, model_dir: str) -> Path:
    """releases/<version>/<swagger-*-model>/api (the committed release layout)."""
    return PROJECT_ROOT / "releases" / version / model_dir / "api"

# harness category name -> swagger model dir name
CATEGORY_MODEL = {
    "oper": "swagger-oper-model",
    "mib": "swagger-mib-model",
    "cfg": "swagger-cfg-model",
    "native-config": "swagger-native-config-model",
    "openconfig": "swagger-openconfig-model",
    "ietf": "swagger-ietf-model",
    "other": "swagger-other-model",
}
PREFERRED_MEDIA = "application/yang-data+json"


def _get_op(spec: dict, path: str):
    item = (spec.get("paths") or {}).get(path)
    if isinstance(item, dict):
        for k, op in item.items():
            if k.lower() == "get" and isinstance(op, dict):
                return op
    return None


def _shortest_get_path(spec: dict):
    """Fallback for MIB: the whole-MIB response has no /data/<MIB>:<table> path;
    stamp it on the shortest GET path of the module (a representative location)."""
    candidates = []
    for p, item in (spec.get("paths") or {}).items():
        if isinstance(item, dict) and any(k.lower() == "get" for k in item):
            candidates.append(p)
    return min(candidates, key=len) if candidates else None


def _media_200(op: dict):
    responses = op.get("responses") or {}
    resp = responses.get("200") or responses.get("default")
    if not isinstance(resp, dict):
        resp = {"description": "Successful RESTCONF GET."}
        op.setdefault("responses", {})["200"] = resp
    content = resp.get("content")
    if not isinstance(content, dict) or not content:
        content = {PREFERRED_MEDIA: {}}
        resp["content"] = content
    media = content.get(PREFERRED_MEDIA)
    if isinstance(media, dict):
        return media
    for m in content.values():
        if isinstance(m, dict):
            return m
    content[PREFERRED_MEDIA] = {}
    return content[PREFERRED_MEDIA]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--sidecar", help="Sidecar path (default references/live-examples-<version>.json)")
    args = ap.parse_args()

    sidecar_path = Path(args.sidecar) if args.sidecar else (
        PROJECT_ROOT / "references" / f"live-examples-{args.version}.json"
    )
    if not sidecar_path.is_file():
        print(f"[live-ex] no sidecar at {sidecar_path}; nothing to do.")
        return 0
    try:
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"[live-ex] sidecar not valid JSON: {exc}\n")
        return 1

    entries = sidecar.get("entries") or []

    # Group entries by (category, module) so each spec file is read/written once.
    by_spec: dict[tuple[str, str], list[dict]] = {}
    for e in entries:
        by_spec.setdefault((e.get("category"), e.get("module")), []).append(e)

    ops_stamped = 0
    files_changed = 0
    missing = 0
    for (category, module), es in sorted(by_spec.items()):
        model_dir = CATEGORY_MODEL.get(category)
        if not model_dir:
            continue
        spec_file = spec_api_dir(args.version, model_dir) / f"{module}.json"
        if not spec_file.is_file():
            missing += len(es)
            continue
        try:
            spec = json.loads(spec_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        changed = False
        for e in es:
            op = _get_op(spec, e.get("path"))
            if op is None and category == "mib":
                fallback = _shortest_get_path(spec)
                op = _get_op(spec, fallback) if fallback else None
            if op is None:
                missing += 1
                continue
            media = _media_200(op)
            media["x-cisco-live-examples"] = e.get("pids") or {}
            ops_stamped += 1
            changed = True
        if changed:
            spec_file.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
            files_changed += 1

    print(f"[live-ex] stamped x-cisco-live-examples on {ops_stamped} GET operation(s) "
          f"across {files_changed} spec file(s) (os {sidecar.get('os_version')}); "
          f"{missing} entr(y/ies) had no matching spec path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
