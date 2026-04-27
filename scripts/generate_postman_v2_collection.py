#!/usr/bin/env python3
"""
generate_postman_v2_collection.py — Per-(version, model-category) Postman v2.1 collections.

Companion to ``generate_bruno_collection.py``. Emits one Postman collection per
(release, model-category) pair under ``releases/<ver>/exports/postman/``,
plus a per-version environment file. Hard 50 MB cap per collection (per
VERSIONING.md §9 gate 7); auto-splits with ``-part-N`` suffix and records the
split in ``releases/<ver>/exports/postman-manifest.json``.

This is the version-aware successor to the legacy ``generate_postman_collection.py``,
which writes a single non-versioned set of collections to ``tools/``. The legacy
script is kept untouched for backward compatibility but is no longer the primary
export pipeline.

Usage:
    python scripts/generate_postman_v2_collection.py --version 26.1.1 --per-category --max-mb 50
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import (PROJECT_ROOT, MODEL_CATEGORIES, ReleasePaths)  # type: ignore  # noqa: E402

METHODS = ("get", "put", "patch", "post", "delete", "head", "options")
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._\-\s]+")


def safe_name(s: str) -> str:
    return SAFE_NAME_RE.sub(" ", s).strip()[:200] or "request"


def url_to_postman(url_str: str) -> dict:
    """Convert a literal URL into a Postman v2.1 url object with host/path/variable."""
    if "://" in url_str:
        scheme, rest = url_str.split("://", 1)
    else:
        scheme, rest = "https", url_str
    if "/" in rest:
        host_part, path_part = rest.split("/", 1)
    else:
        host_part, path_part = rest, ""
    host = host_part.split(":")[0]
    port = host_part.split(":")[1] if ":" in host_part else None
    path_segments = [seg for seg in path_part.split("/") if seg]
    variables: list[dict] = []
    for i, seg in enumerate(path_segments):
        m = re.match(r"^\{([^}]+)\}$", seg)
        if m:
            variables.append({"key": m.group(1), "value": "", "description": ""})
            path_segments[i] = ":" + m.group(1)
    out = {
        "raw": url_str,
        "protocol": scheme,
        "host": [host],
        "path": path_segments,
    }
    if port:
        out["port"] = port
    if variables:
        out["variable"] = variables
    return out


def build_request_item(spec_module: str, path: str, method: str, op: dict,
                       servers: list[dict]) -> dict:
    base = ""
    if servers and isinstance(servers[0], dict):
        base = servers[0].get("url", "") or ""
    if not base:
        base = "https://{{host}}:{{port}}/restconf/data"
    base = base.replace("{host}", "{{host}}").replace("{port}", "{{port}}")
    full_url = base.rstrip("/") + path

    headers = [
        {"key": "Accept", "value": "application/yang-data+json"},
    ]

    body_obj = None
    rb = op.get("requestBody")
    if isinstance(rb, dict):
        content = rb.get("content") or {}
        for _, cdef in content.items():
            if not isinstance(cdef, dict):
                continue
            if "example" in cdef:
                body_obj = cdef["example"]
                break
            examples = cdef.get("examples") or {}
            if examples:
                first = next(iter(examples.values()))
                if isinstance(first, dict) and "value" in first:
                    body_obj = first["value"]
                    break
        headers.append({"key": "Content-Type", "value": "application/yang-data+json"})

    item = {
        "name": safe_name(op.get("summary") or op.get("operationId")
                          or f"{method.upper()} {path}"),
        "request": {
            "method": method.upper(),
            "header": headers,
            "url": url_to_postman(full_url),
            "description": (op.get("description") or op.get("summary") or "")[:2000],
        },
    }
    if body_obj is not None and method.lower() in ("put", "patch", "post"):
        try:
            raw = json.dumps(body_obj, indent=2)
        except Exception:
            raw = "{}"
        item["request"]["body"] = {"mode": "raw", "raw": raw,
                                    "options": {"raw": {"language": "json"}}}
    # Preserve MDT extensions for downstream tooling that supports x-* fields.
    for key in ("x-mdt-filter-xpath", "x-mdt-tier", "x-mdt-cadence-seconds",
                "x-mdt-encoding", "x-mdt-on-change-capable",
                "x-mdt-feature-section"):
        if key in op:
            item.setdefault("description", "")
            # Embed in description so it's at least visible; keep separate too.
            item["x-mdt"] = item.get("x-mdt", {})
            item["x-mdt"][key.replace("x-mdt-", "")] = op[key]
    return item


def items_for_spec(spec_path: Path) -> list[dict]:
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    servers = spec.get("servers") or []
    out: list[dict] = []
    for path, methods in (spec.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        for method in METHODS:
            op = methods.get(method)
            if not isinstance(op, dict):
                continue
            out.append(build_request_item(spec_path.stem, path, method, op, servers))
    return out


def write_collection(target_dir: Path, version: str, category: str,
                     specs: list[Path], max_bytes: int) -> list[dict]:
    """Write one Postman collection JSON, auto-splitting on size."""
    target_dir.mkdir(parents=True, exist_ok=True)
    parts: list[dict] = []
    part = 1

    def make_collection() -> dict:
        return {
            "info": {
                "_postman_id": str(uuid.uuid4()),
                "name": f"IOS-XE {version} — {category}"
                        + (f" (part {part})" if part > 1 else ""),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                "description": f"Generated {datetime.now(timezone.utc).isoformat()}\n"
                               f"Source: cisco-ios-xe-openapi-swagger / "
                               f"releases/{version}/swagger-{category}-model/api/",
                "version": "1.0.0",
            },
            "item": [],
        }

    coll = make_collection()
    coll_size = len(json.dumps(coll, indent=2).encode("utf-8"))

    for spec in specs:
        if spec.name == "manifest.json":
            continue
        spec_items = items_for_spec(spec)
        if not spec_items:
            continue
        folder = {"name": spec.stem, "item": spec_items}
        folder_size = len(json.dumps(folder).encode("utf-8"))
        if coll_size + folder_size > max_bytes and len(coll["item"]) > 0:
            # Flush current part
            out_path = target_dir / (
                f"IOS-XE-{version}-{category}.postman_collection.json"
                if part == 1 else
                f"IOS-XE-{version}-{category}-part-{part}.postman_collection.json"
            )
            out_path.write_text(json.dumps(coll, indent=2) + "\n", encoding="utf-8")
            parts.append({
                "name": coll["info"]["name"],
                "path": str(out_path.relative_to(PROJECT_ROOT)),
                "request_count": sum(len(f.get("item") or []) for f in coll["item"]),
                "size_bytes": out_path.stat().st_size,
            })
            part += 1
            coll = make_collection()
            coll_size = len(json.dumps(coll, indent=2).encode("utf-8"))
        coll["item"].append(folder)
        coll_size += folder_size

    if coll["item"]:
        out_path = target_dir / (
            f"IOS-XE-{version}-{category}.postman_collection.json"
            if part == 1 else
            f"IOS-XE-{version}-{category}-part-{part}.postman_collection.json"
        )
        out_path.write_text(json.dumps(coll, indent=2) + "\n", encoding="utf-8")
        parts.append({
            "name": coll["info"]["name"],
            "path": str(out_path.relative_to(PROJECT_ROOT)),
            "request_count": sum(len(f.get("item") or []) for f in coll["item"]),
            "size_bytes": out_path.stat().st_size,
        })
    return parts


def write_environment(rp: ReleasePaths, version: str) -> Path:
    env = {
        "id": str(uuid.uuid4()),
        "name": f"IOS-XE {version} (RESTCONF)",
        "values": [
            {"key": "host", "value": "10.0.0.1", "enabled": True},
            {"key": "port", "value": "443", "enabled": True},
            {"key": "username", "value": "admin", "enabled": True},
            {"key": "password", "value": "", "type": "secret", "enabled": True},
        ],
        "_postman_variable_scope": "environment",
    }
    out_dir = rp.exports_dir("postman")
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"IOS-XE-{version}.postman_environment.json"
    p.write_text(json.dumps(env, indent=2) + "\n", encoding="utf-8")
    return p


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", required=True)
    p.add_argument("--per-category", action="store_true")
    p.add_argument("--max-mb", type=int, default=50)
    args = p.parse_args()

    rp = ReleasePaths(version=args.version, legacy=True)
    max_bytes = args.max_mb * 1024 * 1024
    target_dir = rp.exports_dir("postman")

    manifest: list[dict] = []
    if args.per_category:
        for cat in MODEL_CATEGORIES:
            specs = sorted(rp.spec_dir(cat).glob("*.json"))
            if not specs:
                continue
            cat_short = cat.replace("swagger-", "").replace("-model", "")
            parts = write_collection(target_dir, args.version, cat_short, specs, max_bytes)
            manifest.extend(parts)
    else:
        specs = []
        for cat in MODEL_CATEGORIES:
            specs.extend(sorted(rp.spec_dir(cat).glob("*.json")))
        parts = write_collection(target_dir, args.version, "all", specs, max_bytes)
        manifest.extend(parts)

    env_path = write_environment(rp, args.version)
    manifest_path = rp.exports_dir() / "postman-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({
        "version": args.version,
        "generated": datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
        "max_bytes": max_bytes,
        "environment": str(env_path.relative_to(PROJECT_ROOT)),
        "collections": manifest,
    }, indent=2) + "\n", encoding="utf-8")

    total = sum(c["request_count"] for c in manifest)
    print(f"[postman] wrote {len(manifest)} collection file(s), {total} request(s) → "
          f"{target_dir.relative_to(PROJECT_ROOT)}")
    print(f"[postman] environment: {env_path.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
