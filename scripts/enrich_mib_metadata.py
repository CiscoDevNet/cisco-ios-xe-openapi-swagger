#!/usr/bin/env python3
"""
enrich_mib_metadata.py — Per-MIB metadata enrichment.

For every MIB YANG module in the active release, derives lightweight metadata
(OID prefix, table/scalar counts, indexes, deprecated counts, RFC/Cisco source)
and joins it with the platform applicability + functional category data parsed
from MIBS.md by parse_mibs_md.py.

Output: ``releases/<ver>/mib-metadata.json`` consumed by the MIB viewer side card.

Authoritative input: PROJECT_ROOT/references/<ver>/*.yang (MIB YANG conversions).
Authoritative companion: parse_mibs_md.py output (mib-platform-matrix.json).

Usage:
    python scripts/enrich_mib_metadata.py --version 26.1.1
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

# Heuristic: a "MIB YANG" module is one whose source file ends in -MIB.yang or
# matches typical SMIv2-converted naming.
RE_OID_PREFIX = re.compile(r"smiv2:oid\s+\"([0-9.]+)\"")
RE_TABLE = re.compile(r"^\s*list\s+", re.MULTILINE)
RE_LEAF = re.compile(r"^\s*leaf\s+([A-Za-z][A-Za-z0-9_\-]*)", re.MULTILINE)
RE_KEY = re.compile(r"^\s*key\s+\"([^\"]+)\"", re.MULTILINE)
RE_DEPRECATED = re.compile(r"status\s+(deprecated|obsolete)", re.IGNORECASE)
RE_REVISION = re.compile(r"revision\s+\"([\d\-]+)\"", re.IGNORECASE)
RE_ORGANIZATION = re.compile(r"organization\s+\"([^\"]+)\"", re.IGNORECASE)


def is_mib_yang(name: str) -> bool:
    upper = name.upper()
    return upper.endswith("-MIB") or upper.endswith("-TC") or upper.endswith("-TC-MIB") or "MIB" in upper.split("-")


def extract_metadata(yang_path: Path) -> dict:
    text = yang_path.read_text(encoding="utf-8", errors="replace")
    name = yang_path.stem
    oid = ""
    m = RE_OID_PREFIX.search(text)
    if m:
        oid = m.group(1)
    tables = len(RE_TABLE.findall(text))
    leaves = len(RE_LEAF.findall(text))
    keys: set[str] = set()
    for k in RE_KEY.finditer(text):
        for tok in k.group(1).split():
            keys.add(tok.strip())
    deprecated_count = len(RE_DEPRECATED.findall(text))
    rev = RE_REVISION.search(text)
    org = RE_ORGANIZATION.search(text)
    rfc_match = re.search(r"\bRFC\s*\d{3,5}\b", text)
    return {
        "name": name,
        "oid_prefix": oid,
        "table_count": tables,
        "leaf_count": leaves,
        "scalar_count": max(0, leaves - tables),
        "indexes": sorted(keys),
        "deprecated_object_count": deprecated_count,
        "latest_revision": rev.group(1) if rev else "",
        "organization": (org.group(1) if org else "").strip().splitlines()[0] if org else "",
        "rfc_reference": rfc_match.group(0) if rfc_match else "",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", required=True)
    args = p.parse_args()

    rp = ReleasePaths(version=args.version, legacy=True)
    yang_dir = rp.yang_source_dir()
    if not yang_dir.is_dir():
        sys.stderr.write(f"[mib-meta] no YANG sources for {args.version}: {yang_dir}\n")
        return 1

    matrix_path = PROJECT_ROOT / "releases" / args.version / "mib-platform-matrix.json"
    matrix_data = {}
    if matrix_path.is_file():
        matrix_data = json.loads(matrix_path.read_text(encoding="utf-8"))
    else:
        print(f"[mib-meta] note: {matrix_path.name} not found; "
              "platform applicability will be empty (run parse_mibs_md.py first).")

    platform_matrix: dict[str, list[str]] = matrix_data.get("platform_matrix", {})
    categories: dict[str, dict] = matrix_data.get("functional_categories", {})
    platforms: list[str] = matrix_data.get("platforms", [])

    # Find MIB YANG files. Prefer references/<ver>/MIBS/*.yang (upstream
    # YangModels/yang publishes SMIv2-derived modules under that subdir);
    # fall back to top-level *-MIB.yang style for legacy layouts.
    mib_subdir = yang_dir / "MIBS"
    if mib_subdir.is_dir():
        candidates = sorted(mib_subdir.rglob("*.yang"))
    else:
        candidates = [f for f in yang_dir.glob("*.yang") if is_mib_yang(f.stem)]
    print(f"[mib-meta] {args.version}: found {len(candidates)} MIB YANG candidates")

    entries: list[dict] = []
    for f in sorted(candidates):
        meta = extract_metadata(f)
        # Some MIB YANG modules use lowercase names; the matrix uses the SMIv2 MIB name.
        # Try the bare stem first, then upper-case variants.
        stem = meta["name"]
        plat_key = None
        for key in (stem, stem.upper(), stem.replace("_", "-")):
            if key in platform_matrix:
                plat_key = key
                break
        meta["platforms"] = platform_matrix.get(plat_key or stem, [])
        cat = categories.get(plat_key or stem) or categories.get(stem.upper(), {})
        meta["functional_category"] = cat.get("category", "")
        meta["role"] = cat.get("role", "")
        entries.append(meta)

    out = rp.mib_metadata()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "version": args.version,
        "generated": datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
        "platforms": platforms,
        "mib_count": len(entries),
        "mibs": entries,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"[mib-meta] wrote {out.relative_to(PROJECT_ROOT)} ({len(entries)} MIBs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
