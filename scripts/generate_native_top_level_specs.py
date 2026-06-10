#!/usr/bin/env python
"""generate_native_top_level_specs.py

Materialise two index specs for the synthetic "native-00-*" trees that the
accountability report links to but the original generator never emitted:

    native-00-top-level-leafs       — direct leafs hanging off /native
    native-00-top-level-containers  — direct containers hanging off /native

The input is the pre-rendered tree HTML under yang-trees/. The output is a
minimal OpenAPI 3.0 spec per file: one GET path per top-level child, all
rooted at /data/Cisco-IOS-XE-native:native/<child>. These act as a catalogue
index for the hub — the real per-feature specs (native-banner, native-vlan,
...) carry the writable detail.

Idempotent: rewrites both spec files and patches the swagger-native-config-
model manifest. Safe to re-run after a tree regeneration.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API_DIR = ROOT / "swagger-native-config-model" / "api"
TREES_DIR = ROOT / "yang-trees"

_TREE_RE = re.compile(r"^\s+\+--rw\s+([A-Za-z0-9_.\-]+)\??", re.MULTILINE)


def _parse_children(html_path: Path) -> list[str]:
    text = html_path.read_text(encoding="utf-8", errors="replace")
    # The tree block is wrapped in <pre>...</pre>; the +--rw lines list the
    # direct children we want.
    return sorted(set(_TREE_RE.findall(text)))


def _server_block() -> dict:
    return {
        "url": "https://{device}:{port}/restconf",
        "description": "IOS XE Device RESTCONF API",
        "variables": {
            "device": {
                "default": "devnetsandboxiosxec9k.cisco.com",
                "description": "Device IP or hostname",
            },
            "port": {"default": "443", "description": "HTTPS port"},
        },
    }


def _path_entry(child: str, kind: str) -> dict:
    """One read-only catalogue entry per child.

    `kind` is 'leaf' or 'container' — informational only, surfaced in the
    operation summary so the catalogue view is self-describing.
    """
    return {
        "get": {
            "summary": f"Get top-level native {kind} '{child}'",
            "operationId": f"get-native-{child}",
            "tags": ["native-top-level"],
            "parameters": [{"$ref": "#/components/parameters/depth"}],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {"application/yang-data+json": {"schema": {"type": "object"}}},
                },
                "401": {"description": "Unauthorized"},
                "404": {"description": "Resource not found"},
            },
        }
    }


def _build_spec(title_suffix: str, kind: str, children: list[str]) -> dict:
    paths = {
        f"/data/Cisco-IOS-XE-native:native/{child}": _path_entry(child, kind)
        for child in children
    }
    return {
        "openapi": "3.0.0",
        "info": {
            "title": f"Cisco IOS XE Native Config - {title_suffix}",
            "description": (
                f"Index of {len(children)} top-level {kind}(s) directly under /native. "
                "Use the linked per-feature specs for the writable detail."
            ),
            "version": "17.18.1",
            "contact": {
                "name": "Cisco IOS XE RESTCONF API",
                "url": "https://developer.cisco.com/iosxe/",
            },
            "x-yang-module": "Cisco-IOS-XE-native",
            "x-model-type": "native",
            "x-synthetic-index": True,
        },
        "servers": [_server_block()],
        "paths": paths,
        "components": {
            "parameters": {
                "depth": {
                    "name": "depth",
                    "in": "query",
                    "description": "RESTCONF depth parameter",
                    "schema": {"type": "string", "default": "unbounded"},
                }
            }
        },
    }


def _patch_manifest() -> None:
    manifest_path = API_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    modules = set(manifest.get("modules", []))
    modules.update(["native-00-top-level-containers", "native-00-top-level-leafs"])
    manifest["modules"] = sorted(modules)
    # Recompute totals from disk so the viewer header math stays correct.
    total_paths = 0
    total_ops = 0
    for spec_file in sorted(API_DIR.glob("*.json")):
        if spec_file.name == "manifest.json" or spec_file.name.startswith("_"):
            continue
        try:
            spec = json.loads(spec_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        paths = spec.get("paths") or {}
        total_paths += len(paths)
        for ops in paths.values():
            total_ops += sum(1 for k in ops if k.lower() in {"get", "put", "post", "patch", "delete"})
    manifest["total_modules"] = len(manifest["modules"])
    manifest["spec_count"] = len(manifest["modules"])
    manifest["total_paths"] = total_paths
    manifest["total_operations"] = total_ops
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    containers_html = TREES_DIR / "native-00-top-level-containers.html"
    leafs_html = TREES_DIR / "native-00-top-level-leafs.html"
    for h in (containers_html, leafs_html):
        if not h.is_file():
            sys.stderr.write(f"[native-top-level] missing tree HTML: {h}\n")
            return 1

    containers = _parse_children(containers_html)
    leafs = _parse_children(leafs_html)
    print(f"[native-top-level] parsed {len(containers)} containers, {len(leafs)} leafs")

    containers_spec = _build_spec("top-level containers index", "container", containers)
    leafs_spec = _build_spec("top-level leafs index", "leaf", leafs)

    (API_DIR / "native-00-top-level-containers.json").write_text(
        json.dumps(containers_spec, indent=2) + "\n", encoding="utf-8"
    )
    (API_DIR / "native-00-top-level-leafs.json").write_text(
        json.dumps(leafs_spec, indent=2) + "\n", encoding="utf-8"
    )

    _patch_manifest()
    print("[native-top-level] wrote 2 specs + patched manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
