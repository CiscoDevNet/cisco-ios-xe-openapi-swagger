"""Query the capture index by value or keyword (DEVICE_DATA_COLLECTION.md §5).

Given scripts/harness/capture-index.json, search for:
  - a value (exact or substring), e.g. 633024
  - a keyword against leaf names / values, e.g. policer, dot1x, forus, l2-control,
    cpu-punt-queue-name

and print the matching (device, pid, module, path, leaf, value) rows. Also emits
a per-PID coverage matrix (module/path x PID -> has-data / 404 / empty).

Run:
  python -X utf8 -m scripts.harness.find_value --value 633024
  python -X utf8 -m scripts.harness.find_value --keyword policer
  python -X utf8 -m scripts.harness.find_value --coverage
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

HARNESS_DIR = Path(__file__).resolve().parent
INDEX_PATH = HARNESS_DIR / "capture-index.json"


def load_index(path: Path = INDEX_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Index not found: {path}. Run build_capture_index.py first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def search_value(index: dict, needle: str, exact: bool) -> list[dict]:
    """Match against the row VALUE (stringified)."""
    out = []
    needle_l = needle.lower()
    for row in index.get("rows", []):
        sval = str(row.get("value"))
        if (sval == needle) if exact else (needle_l in sval.lower()):
            out.append(row)
    return out


def search_keyword(index: dict, keyword: str) -> list[dict]:
    """Match against the leaf name (last xpath segment), full xpath, or value."""
    out = []
    kw = keyword.lower()
    for row in index.get("rows", []):
        leaf = str(row.get("leaf_xpath", ""))
        leaf_name = leaf.rsplit("/", 1)[-1].split("[", 1)[0]
        if kw in leaf_name.lower() or kw in leaf.lower() or kw in str(row.get("value")).lower():
            out.append(row)
    return out


def print_rows(rows: list[dict], limit: int) -> None:
    if not rows:
        print("  (no matches)")
        return
    for row in rows[:limit]:
        print(
            f"  {row.get('device')} [{row.get('pid')}] "
            f"{row.get('module')}\n"
            f"    path: {row.get('path')}\n"
            f"    leaf: {row.get('leaf_xpath')} = {row.get('value')!r}"
        )
    if len(rows) > limit:
        print(f"  ... and {len(rows) - limit} more (raise --limit)")


def coverage_matrix(index: dict) -> dict:
    """Per (module,path) x PID -> status, derived from indexed rows.

    A (module, path) with any indexed row for a PID => 'data'. The index only
    contains rows for responses that had a body, so 404/empty are inferred as
    absence. For authoritative 404/empty status, cross-reference the raw
    capture http_status; here we report data vs no-data per PID.
    """
    pids: set[str] = set()
    cells: dict[tuple[str, str], dict[str, str]] = {}
    for row in index.get("rows", []):
        pid = str(row.get("pid"))
        pids.add(pid)
        key = (str(row.get("module")), str(row.get("path")))
        cells.setdefault(key, {})[pid] = "data"
    return {
        "pids": sorted(pids),
        "cells": {f"{m}||{p}": statuses for (m, p), statuses in sorted(cells.items())},
    }


def print_coverage(index: dict) -> None:
    matrix = coverage_matrix(index)
    pids = matrix["pids"]
    print("Per-PID coverage (module/path -> data present):")
    print("PID columns:", ", ".join(pids))
    for key, statuses in matrix["cells"].items():
        module, path = key.split("||", 1)
        marks = " ".join("Y" if statuses.get(pid) == "data" else "-" for pid in pids)
        print(f"  [{marks}] {module}  {path}")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", help="Index path (default scripts/harness/capture-index.json)")
    ap.add_argument("--value", help="Search by value (substring unless --exact)")
    ap.add_argument("--exact", action="store_true", help="Exact value match")
    ap.add_argument("--keyword", help="Search leaf names/values by keyword")
    ap.add_argument("--coverage", action="store_true", help="Print per-PID coverage matrix")
    ap.add_argument("--limit", type=int, default=50, help="Max rows to print")
    args = ap.parse_args(argv)

    if not any([args.value, args.keyword, args.coverage]):
        ap.error("provide --value, --keyword, and/or --coverage")

    try:
        index = load_index(Path(args.index) if args.index else INDEX_PATH)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.value:
        print(f"== value search: {args.value!r} ({'exact' if args.exact else 'substring'}) ==")
        print_rows(search_value(index, args.value, args.exact), args.limit)
    if args.keyword:
        print(f"== keyword search: {args.keyword!r} ==")
        print_rows(search_keyword(index, args.keyword), args.limit)
    if args.coverage:
        print_coverage(index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
