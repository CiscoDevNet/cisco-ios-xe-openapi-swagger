#!/usr/bin/env python3
"""
apply_cli_mappings.py — Stamp `x-cli-equivalent` on native config operations.

Reads ``references/native-cli-mappings.yaml`` and walks every spec under the
release's native-config api-v2 directory. When a mapping ``path`` is a prefix
of an OpenAPI ``paths`` key, every operation under that path gets the mapping's
``cli`` string attached as ``x-cli-equivalent`` (and optionally ``x-cli-notes``).

Per PROJECT_REQUIREMENTS.md §16.5 item 3.

Usage:
    python scripts/apply_cli_mappings.py --version 26.1.1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import PROJECT_ROOT, ReleasePaths  # type: ignore  # noqa: E402

METHODS = ("get", "put", "patch", "post", "delete", "head", "options")
DEFAULT_OVERLAY = PROJECT_ROOT / "references" / "native-cli-mappings.yaml"


def load_yaml_simple(path: Path) -> dict:
    """Tiny YAML reader that supports the subset used by native-cli-mappings.yaml.

    Avoids a hard PyYAML dependency. Handles:
      mappings:
        - path: ...
          cli: "..."
          notes: "..."
    """
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        pass

    out: dict = {"mappings": []}
    cur: dict | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("- "):
            if cur:
                out["mappings"].append(cur)
            cur = {}
            stripped = stripped[2:]
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if cur is None or indent == 0:
                continue
            cur[key] = val
    if cur:
        out["mappings"].append(cur)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", required=True)
    p.add_argument("--overlay", default=str(DEFAULT_OVERLAY),
                   help="Path to YAML mapping overlay (default: references/native-cli-mappings.yaml)")
    args = p.parse_args()

    overlay_path = Path(args.overlay)
    if not overlay_path.is_file():
        sys.stderr.write(f"[cli-map] overlay not found: {overlay_path}\n")
        return 1
    overlay = load_yaml_simple(overlay_path)
    mappings = overlay.get("mappings") or []
    if not mappings:
        sys.stderr.write("[cli-map] no mappings found in overlay; nothing to do.\n")
        return 0
    # Sort longest-prefix-first so /a/b beats /a when both match.
    mappings.sort(key=lambda m: len(m.get("path", "")), reverse=True)

    # The OpenAPI specs prefix every native path with the RESTCONF data root,
    # e.g. ``/data/Cisco-IOS-XE-native:native/...``. The mapping YAML omits the
    # ``/data`` prefix for readability. Normalise both sides so prefix-match
    # works either way.
    def normalise(p: str) -> str:
        return p.replace("/data/", "/", 1) if p.startswith("/data/") else p

    rp = ReleasePaths(version=args.version, legacy=True)
    spec_dir = rp.spec_dir("swagger-native-config-model")
    if not spec_dir.is_dir():
        sys.stderr.write(f"[cli-map] missing native spec dir: {spec_dir}\n")
        return 1

    total_files = 0
    total_ops_stamped = 0
    for spec_path in sorted(spec_dir.glob("*.json")):
        if spec_path.name == "manifest.json":
            continue
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except Exception as e:
            sys.stderr.write(f"[cli-map] cannot parse {spec_path.name}: {e}\n")
            continue
        paths = spec.get("paths") or {}
        if not isinstance(paths, dict):
            continue
        changed = False
        per_file_ops = 0
        for opath, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            n_opath = normalise(opath)
            match = next((m for m in mappings if n_opath.startswith(m["path"])), None)
            if not match:
                continue
            for method in METHODS:
                op = methods.get(method)
                if not isinstance(op, dict):
                    continue
                op["x-cli-equivalent"] = match.get("cli", "")
                if match.get("notes"):
                    op["x-cli-notes"] = match["notes"]
                per_file_ops += 1
                changed = True
        if changed:
            spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
            total_files += 1
            total_ops_stamped += per_file_ops
    print(f"[cli-map] stamped {total_ops_stamped} operation(s) across {total_files} "
          f"spec file(s) (overlay: {overlay_path.name}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
