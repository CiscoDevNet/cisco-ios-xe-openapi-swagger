#!/usr/bin/env python3
"""check_native_coverage.py

Build-time guard: enumerate every top-level data child of /native in
references/<ver>/Cisco-IOS-XE-native.yang and assert each one appears in
at least one path of the split swagger-native-config-model specs.

Exit codes:
    0  all top-level children covered
    1  missing children — gap report printed to stderr
    2  input files missing

Run standalone:
    python scripts/check_native_coverage.py --version 26.1.1
    python scripts/check_native_coverage.py --all

Wired into scripts/build_release.py after native-specs so a regression
in the v2 generator (or its successor) fails the build.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASES = ["17.9.x", "17.12.x", "17.15.x", "17.18.1", "26.1.1"]

_DATA_KIND_RE = re.compile(
    r"(container|list|leaf|leaf-list|choice|anyxml)\s+([A-Za-z0-9_\-:]+)"
)
_USES_RE = re.compile(r"uses\s+([A-Za-z0-9_\-:]+)")
_NATIVE_RE = re.compile(r"container\s+native\s*\{")
_PATH_TOP_RE = re.compile(r"^/data/Cisco-IOS-XE-native:native/([^/?=]+)")


def _balanced_body(src: str, brace_open_pos: int) -> tuple[str, int]:
    depth = 1
    i = brace_open_pos + 1
    while i < len(src) and depth > 0:
        c = src[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return src[brace_open_pos + 1 : i], i
        i += 1
    return "", -1


def _depth_zero_statements(body: str) -> list[str]:
    d = 0
    cur = ""
    out: list[str] = []
    for ch in body:
        if ch == "{":
            if d == 0:
                out.append(cur.strip())
                cur = ""
            d += 1
        elif ch == "}":
            d -= 1
            if d == 0:
                cur = ""
        elif d == 0:
            if ch == ";":
                out.append(cur.strip())
                cur = ""
            else:
                cur += ch
    return out


def yang_top_level_data_children(yang_path: Path) -> set[str]:
    """Top-level data children of `container native` (containers, lists, leafs,
    leaf-lists) — including those resolved from inline `uses <grouping>` at
    the top level. Empty `container foo;` declarations (no body) DO count as
    children: they exist in the data tree even when populated only by augments
    from sibling modules.
    """
    src = yang_path.read_text(encoding="utf-8", errors="replace")
    m = _NATIVE_RE.search(src)
    if not m:
        return set()
    body, _ = _balanced_body(src, m.end() - 1)
    if not body:
        return set()

    grouping_bodies: dict[str, str] = {}
    for gm in re.finditer(r"grouping\s+([A-Za-z0-9_\-:]+)\s*\{", src):
        gbody, _ = _balanced_body(src, gm.end() - 1)
        if gbody:
            grouping_bodies[gm.group(1)] = gbody

    def resolve(stmts: list[str], seen: set[str]) -> set[str]:
        out: set[str] = set()
        for s in stmts:
            s2 = " ".join(s.split())
            mm = _DATA_KIND_RE.match(s2)
            if mm:
                out.add(mm.group(2))
                continue
            um = _USES_RE.match(s2)
            if um:
                g = um.group(1).split(":")[-1]
                if g in grouping_bodies and g not in seen:
                    out |= resolve(_depth_zero_statements(grouping_bodies[g]), seen | {g})
        return out

    return resolve(_depth_zero_statements(body), set())


def covered_top_segments(api_dir: Path) -> set[str]:
    covered: set[str] = set()
    for fp in sorted(glob.glob(str(api_dir / "native-*.json"))):
        try:
            spec = json.loads(Path(fp).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for p in spec.get("paths", {}).keys():
            mm = _PATH_TOP_RE.match(p)
            if mm:
                covered.add(mm.group(1))
    return covered


_REF_DIR_OVERRIDES = {"17.18.1": "17181-YANG-modules"}


def _ref_dir(version: str) -> Path:
    sub = _REF_DIR_OVERRIDES.get(version, version)
    return ROOT / "references" / sub


def check_release(version: str) -> tuple[int, list[str], int]:
    yang_path = _ref_dir(version) / "Cisco-IOS-XE-native.yang"
    api_dir = ROOT / "releases" / version / "swagger-native-config-model" / "api"
    if not yang_path.is_file():
        sys.stderr.write(f"[{version}] missing YANG source: {yang_path}\n")
        return 2, [], 0
    if not api_dir.is_dir():
        sys.stderr.write(f"[{version}] missing api dir: {api_dir}\n")
        return 2, [], 0
    yang_top = yang_top_level_data_children(yang_path)
    covered = covered_top_segments(api_dir)
    missing = sorted(yang_top - covered)
    return (1 if missing else 0), missing, len(yang_top)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", help="release version to check (e.g. 26.1.1)")
    ap.add_argument("--all", action="store_true", help="check all known releases")
    ap.add_argument(
        "--warn-only",
        action="store_true",
        help="report gaps to stderr but exit 0 (use in CI until generator is fixed)",
    )
    args = ap.parse_args()

    if not args.version and not args.all:
        ap.error("specify --version <ver> or --all")

    versions = RELEASES if args.all else [args.version]
    overall_rc = 0
    for v in versions:
        rc, missing, total = check_release(v)
        if rc == 2:
            overall_rc = max(overall_rc, 2)
            continue
        if missing:
            overall_rc = max(overall_rc, 1)
            sys.stderr.write(
                f"[{v}] FAIL: {len(missing)}/{total} top-level /native children "
                f"not covered by any split spec:\n"
            )
            for m in missing:
                sys.stderr.write(f"  - {m}\n")
        else:
            print(f"[{v}] OK: all {total} top-level /native children covered")
    if args.warn_only and overall_rc == 1:
        sys.stderr.write("[check_native_coverage] --warn-only: gaps present but exit 0\n")
        return 0
    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())
