#!/usr/bin/env python3
"""Build a YANG module -> filter-xpath prefix map for a release.

Scans every ``*.yang`` file under the release's YANG source directory and
extracts each module's ``prefix`` statement. The output is consumed by the
``telemetry.html`` Module XPath Builder so it can derive MDT filter xpaths
on the fly for any module/path the user selects, using the formula:

    filter xpath = "/" + <prefix> + ":" + <path-without-leading-slash>

Output schema (``releases/<ver>/yang-prefix-map.json``)::

    {
      "version": "26.1.1",
      "module_count": 848,
      "modules": {
        "Cisco-IOS-XE-process-cpu-oper": "process-cpu-ios-xe-oper",
        "Cisco-IOS-XE-memory-oper": "memory-ios-xe-oper",
        ...
      }
    }

Source-directory resolution:

* ``17.18.1`` (legacy in-place layout) → ``references/17181-YANG-modules/``
* otherwise → first existing of:
  * ``releases/<ver>/yang-source/``
  * ``references/<ver>/``

If neither directory exists the script exits 0 without writing (so it is safe
to wire into ``build_release.py`` for releases that haven't fetched YANG yet).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX_RE = re.compile(r'^\s*prefix\s+["\']?([\w-]+)', re.MULTILINE)
LEGACY_VERSION = "17.18.1"


def resolve_yang_dir(version: str) -> Path | None:
    candidates: list[Path] = []
    if version == LEGACY_VERSION:
        candidates.append(ROOT / "references" / "17181-YANG-modules")
    candidates.append(ROOT / "releases" / version / "yang-source")
    candidates.append(ROOT / "references" / version)
    for c in candidates:
        if c.is_dir() and any(c.glob("*.yang")):
            return c
    return None


def extract_prefixes(yang_dir: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for f in sorted(yang_dir.glob("*.yang")):
        # Read enough of the header to find the prefix line. YANG headers
        # are conventionally short; 8KB covers every module we have today
        # while keeping I/O modest.
        try:
            head = f.read_text(encoding="utf-8", errors="replace")[:8192]
        except OSError as e:
            print(f"WARN: cannot read {f.name}: {e}", file=sys.stderr)
            continue
        m = PREFIX_RE.search(head)
        if not m:
            continue
        # Module name = filename minus extension. We deliberately ignore
        # submodules without their own prefix line.
        out[f.stem] = m.group(1)
    return out


def write_map(version: str, yang_dir: Path, modules: dict[str, str]) -> Path:
    if version == LEGACY_VERSION:
        # Stamp the legacy default at repo root so the static viewer can
        # find it without a release prefix.
        target = ROOT / "yang-prefix-map.json"
    else:
        target = ROOT / "releases" / version / "yang-prefix-map.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": version,
        "yang_source": str(yang_dir.relative_to(ROOT)).replace("\\", "/"),
        "module_count": len(modules),
        "modules": modules,
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def build_one(version: str) -> int:
    yang_dir = resolve_yang_dir(version)
    if yang_dir is None:
        print(f"[prefix-map] {version}: no YANG source dir found, skipping")
        return 0
    modules = extract_prefixes(yang_dir)
    if not modules:
        print(f"[prefix-map] {version}: no modules with prefix in {yang_dir}")
        return 0
    target = write_map(version, yang_dir, modules)
    print(f"[prefix-map] {version}: wrote {target.relative_to(ROOT)} "
          f"({len(modules)} modules, source={yang_dir.relative_to(ROOT)})")
    return 0


def all_active_versions() -> list[str]:
    cfg = json.loads((ROOT / "releases" / "index.json").read_text(encoding="utf-8"))
    return [r["ver"] for r in cfg.get("releases", []) if r.get("status") == "active"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--version",
                    help="Release to build (default: every active release).")
    args = ap.parse_args()
    versions = [args.version] if args.version else all_active_versions()
    rc = 0
    for v in versions:
        rc |= build_one(v)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
