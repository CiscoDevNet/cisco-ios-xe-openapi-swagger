#!/usr/bin/env python3
"""
apply_example_overlay.py — Stamp curated request-body examples onto native specs.

Reads ``references/native-example-overlay.yaml`` and overlays each entry's
``value`` onto matching write operations (PUT/PATCH/POST by default). The
overlay is the canonical source for human-curated payloads; auto-generated
examples remain as fallback.

Per PROJECT_REQUIREMENTS.md §16.5 item 4.

Usage:
    python scripts/apply_example_overlay.py --version 26.1.1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import PROJECT_ROOT, ReleasePaths  # type: ignore  # noqa: E402

WRITE_METHODS = ("put", "patch", "post")
DEFAULT_OVERLAY = PROJECT_ROOT / "references" / "native-example-overlay.yaml"


def load_yaml(path: Path) -> dict:
    """Use PyYAML if present, else a minimal subset reader."""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        sys.stderr.write(
            "[ex-overlay] PyYAML not installed; install with `pip install pyyaml` "
            "for full overlay support. Skipping.\n"
        )
        return {}


def apply_to_operation(op: dict, value) -> bool:
    """Set/overwrite the JSON example on the operation's request body."""
    rb = op.get("requestBody")
    if not isinstance(rb, dict):
        rb = {"required": True, "content": {}}
        op["requestBody"] = rb
    content = rb.setdefault("content", {})
    media = content.setdefault("application/yang-data+json", {})
    media["example"] = value
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", required=True)
    p.add_argument("--overlay", default=str(DEFAULT_OVERLAY))
    args = p.parse_args()

    overlay_path = Path(args.overlay)
    if not overlay_path.is_file():
        sys.stderr.write(f"[ex-overlay] overlay not found: {overlay_path}\n")
        return 1
    overlay = load_yaml(overlay_path)
    examples = overlay.get("examples") or []
    if not examples:
        print("[ex-overlay] no entries; nothing to do.")
        return 0
    examples.sort(key=lambda e: len(e.get("path", "")), reverse=True)

    # OpenAPI native paths are prefixed with the RESTCONF data root
    # (``/data/Cisco-IOS-XE-native:native/...``); the overlay omits ``/data``.
    def normalise(p: str) -> str:
        return p.replace("/data/", "/", 1) if p.startswith("/data/") else p

    rp = ReleasePaths(version=args.version, legacy=True)
    spec_dir = rp.spec_dir("swagger-native-config-model")
    if not spec_dir.is_dir():
        sys.stderr.write(f"[ex-overlay] missing native spec dir: {spec_dir}\n")
        return 1

    files_changed = 0
    ops_stamped = 0
    for spec_path in sorted(spec_dir.glob("*.json")):
        if spec_path.name == "manifest.json":
            continue
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except Exception as e:
            sys.stderr.write(f"[ex-overlay] cannot parse {spec_path.name}: {e}\n")
            continue
        paths = spec.get("paths") or {}
        if not isinstance(paths, dict):
            continue
        changed = False
        for opath, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            n_opath = normalise(opath)
            entry = next((e for e in examples if n_opath.startswith(e["path"])), None)
            if not entry:
                continue
            allowed = entry.get("method")
            allowed_set = {allowed} if allowed else set(WRITE_METHODS)
            for method in WRITE_METHODS:
                if method not in allowed_set:
                    continue
                op = methods.get(method)
                if not isinstance(op, dict):
                    continue
                if apply_to_operation(op, entry.get("value")):
                    ops_stamped += 1
                    changed = True
        if changed:
            spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
            files_changed += 1
    print(f"[ex-overlay] stamped {ops_stamped} write operation(s) across "
          f"{files_changed} spec file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
