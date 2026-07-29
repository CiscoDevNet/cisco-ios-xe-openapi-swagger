#!/usr/bin/env python3
"""Estimate active development time from git commit timestamps (git-hours style).

Commit timestamps are the only signal git records, so this is an *estimate*:
consecutive commits closer together than ``--max-gap`` minutes are treated as
one working session; a session's time is (last - first) commit span plus a
fixed ``--first-commit`` allotment for the ramp-up before the first commit.

Usage:
    python -X utf8 scripts/estimate_dev_hours.py               # whole history
    python -X utf8 scripts/estimate_dev_hours.py --by day      # per-day table
    python -X utf8 scripts/estimate_dev_hours.py --max-gap 120 --first-commit 30
"""
from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta


def _git_timestamps() -> list[datetime]:
    out = subprocess.run(
        ["git", "log", "--format=%cI"],
        capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    # %cI is strict ISO-8601; oldest last -> reverse to chronological
    stamps = [datetime.fromisoformat(s) for s in out if s]
    stamps.reverse()
    return stamps


def estimate(stamps: list[datetime], max_gap_min: int, first_commit_min: int):
    if not stamps:
        return 0.0, []
    gap = timedelta(minutes=max_gap_min)
    first = timedelta(minutes=first_commit_min)
    sessions: list[tuple[datetime, datetime, int]] = []
    s_start = stamps[0]
    s_prev = stamps[0]
    s_count = 1
    for t in stamps[1:]:
        if t - s_prev <= gap:
            s_prev = t
            s_count += 1
        else:
            sessions.append((s_start, s_prev, s_count))
            s_start = s_prev = t
            s_count = 1
    sessions.append((s_start, s_prev, s_count))
    total = 0.0
    for start, end, _ in sessions:
        total += first.total_seconds() + (end - start).total_seconds()
    return total / 3600.0, sessions


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-gap", type=int, default=120,
                    help="minutes between commits that still count as one session")
    ap.add_argument("--first-commit", type=int, default=30,
                    help="minutes credited for the ramp-up before each session's first commit")
    ap.add_argument("--by", choices=["total", "day", "month"], default="total")
    args = ap.parse_args()

    stamps = _git_timestamps()
    if not stamps:
        print("no commits")
        return 0

    total_hours, sessions = estimate(stamps, args.max_gap, args.first_commit)
    span_days = (stamps[-1] - stamps[0]).days + 1
    print(f"Commits: {len(stamps)}   Span: {stamps[0].date()} -> {stamps[-1].date()} "
          f"({span_days} days)")
    print(f"Sessions: {len(sessions)}   Est. active time: {total_hours:.1f} h "
          f"(~{total_hours / span_days:.2f} h/day over the span)")
    print(f"(model: max-gap={args.max_gap}m, first-commit credit={args.first_commit}m)")

    if args.by in ("day", "month"):
        buckets: dict[str, list[datetime]] = defaultdict(list)
        for t in stamps:
            key = t.strftime("%Y-%m-%d") if args.by == "day" else t.strftime("%Y-%m")
            buckets[key].append(t)
        print(f"\n{'Date':<12}{'Commits':>9}{'Est. hours':>12}")
        print("-" * 33)
        for key in sorted(buckets):
            h, _ = estimate(buckets[key], args.max_gap, args.first_commit)
            print(f"{key:<12}{len(buckets[key]):>9}{h:>11.1f}h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
