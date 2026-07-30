"""Verify capture completeness and attribute device crashes (Track B).

Two jobs, both answering the questions from the crash post-mortem:

  1. "Ensure none were missed" (--gaps): enumerate every harness GET path per
     category and reconcile against the captures on disk. Reports, per category,
     how many are OK, how many ERRORED (a capture exists but failed), and how
     many are MISSING (never captured). Errored + missing = the re-run set, which
     it writes to scripts/harness/gaps.txt (one path per line, ``--category``
     prefixed) so the collector's resume (which now re-runs errored paths) closes
     them.

  2. "Which module crashed the device" (--crashes): read the per-GET trace
     (scripts/harness/trace.jsonl) and surface the crash signatures — GETs where
     the device reset the connection (reset=true) and stalls (multiple attempts /
     very long elapsed). Grouped by module so the culprit is obvious even when the
     capture data was masked by retries.

Run:
  python -X utf8 -m scripts.harness.verify              # both
  python -X utf8 -m scripts.harness.verify --gaps
  python -X utf8 -m scripts.harness.verify --crashes
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.harness import spec_paths
else:  # pragma: no cover
    from . import spec_paths

HARNESS_DIR = Path(__file__).resolve().parent
CAPTURES_DIR = HARNESS_DIR / "captures"
TRACE_PATH = HARNESS_DIR / "trace.jsonl"
GAPS_PATH = HARNESS_DIR / "gaps.txt"

STALL_MS = 15000  # a single GET taking this long is a stall/near-crash


def _captured(device_dir: Path) -> dict:
    """path -> {'category', 'error'} for every capture of a device."""
    out = {}
    for cap in device_dir.glob("*/*.json"):
        try:
            r = json.loads(cap.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        out[r.get("path")] = {"category": r.get("category"), "error": r.get("error")}
    return out


def check_gaps(specs_root: Path, device_dir: Path) -> tuple[dict, list]:
    """Reconcile enumerated GET paths vs captures. Returns (per_cat, rerun_list)."""
    captured = _captured(device_dir)
    per_cat = {}
    rerun = []
    for cat in spec_paths.GET_CATEGORIES:
        universe = {gp.path for gp in spec_paths.enumerate_get_paths(specs_root, categories=[cat])}
        ok = errored = 0
        for p in universe:
            c = captured.get(p)
            if c is None:
                rerun.append((cat, p))
            elif c.get("error"):
                errored += 1; rerun.append((cat, p))
            else:
                ok += 1
        missing = len(universe) - ok - errored
        per_cat[cat] = {"enumerated": len(universe), "ok": ok, "errored": errored, "missing": missing}
    return per_cat, rerun


def analyze_trace(trace_path: Path) -> dict:
    """Summarize crash signatures from the trace: resets + stalls per module."""
    resets = []          # definitive: device dropped the connection on this GET
    stalls = []          # attempts>1 or elapsed >= STALL_MS
    by_module = Counter()
    lines = 0
    if not trace_path.exists():
        return {"present": False}
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        lines += 1
        key = f"{e.get('category')}/{e.get('module')}"
        if e.get("reset"):
            resets.append(e); by_module[key] += 1
        elif e.get("attempts", 1) > 1 or e.get("elapsed_ms", 0) >= STALL_MS:
            stalls.append(e)
    return {"present": True, "lines": lines, "resets": resets, "stalls": stalls,
            "by_module": by_module}


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--specs-root", help="Specs root (default releases/26.1.1)")
    ap.add_argument("--device", default="sw-pilot", help="Device name under captures/ (default sw-pilot)")
    ap.add_argument("--gaps", action="store_true", help="Only run the completeness reconciliation")
    ap.add_argument("--crashes", action="store_true", help="Only run the crash attribution")
    args = ap.parse_args(argv)
    do_all = not (args.gaps or args.crashes)

    device_dir = CAPTURES_DIR / args.device
    if not device_dir.is_dir():
        print(f"No captures for device {args.device!r} at {device_dir}", file=sys.stderr)
        return 2

    if args.gaps or do_all:
        specs_root = spec_paths.resolve_specs_root(args.specs_root)
        per_cat, rerun = check_gaps(specs_root, device_dir)
        print("== COMPLETENESS (enumerated GET paths vs captured) ==")
        print(f"{'category':16}{'enumerated':>11}{'ok':>9}{'errored':>9}{'missing':>9}")
        tot = Counter()
        for cat, d in per_cat.items():
            print(f"{cat:16}{d['enumerated']:>11,}{d['ok']:>9,}{d['errored']:>9,}{d['missing']:>9,}")
            for k, v in d.items():
                tot[k] += v
        print("-" * 54)
        print(f"{'TOTAL':16}{tot['enumerated']:>11,}{tot['ok']:>9,}{tot['errored']:>9,}{tot['missing']:>9,}")
        if rerun:
            GAPS_PATH.write_text("".join(f"{cat}\t{p}\n" for cat, p in rerun), encoding="utf-8")
            print(f"\n{len(rerun):,} path(s) still to close (errored+missing) -> {GAPS_PATH}")
            print("Re-run: collector resume now re-fetches errored paths automatically.")
        else:
            print("\nAll enumerated GET paths captured cleanly. Nothing missed.")

    if args.crashes or do_all:
        t = analyze_trace(TRACE_PATH)
        print("\n== CRASH ATTRIBUTION (from trace.jsonl) ==")
        if not t.get("present"):
            print(f"No trace at {TRACE_PATH} (run the collector to generate one).")
        else:
            print(f"trace entries: {t['lines']:,}  |  resets: {len(t['resets'])}  |  stalls: {len(t['stalls'])}")
            if t["by_module"]:
                print("\nModules with CONNECTION RESETS (device crash signature):")
                for mod, n in t["by_module"].most_common():
                    print(f"  {n:3} x reset   {mod}")
                print("\nReset events (path that dropped the connection):")
                for e in t["resets"][:20]:
                    print(f"  {e.get('t')}  {e.get('category')}/{e.get('module')}  {e.get('path')}")
            if t["stalls"]:
                print(f"\nStalls (attempts>1 or >= {STALL_MS//1000}s) \u2014 top by elapsed:")
                for e in sorted(t["stalls"], key=lambda e: -e.get("elapsed_ms", 0))[:15]:
                    print(f"  {e.get('elapsed_ms'):>7} ms  x{e.get('attempts')}  "
                          f"{e.get('category')}/{e.get('module')}  {e.get('path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
