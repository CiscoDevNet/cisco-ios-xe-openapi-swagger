#!/usr/bin/env python3
"""Audit duplicate operationIds across all OpenAPI specs in the workspace.

Scans both the live viewer api/ directories and any per-release archives.
OpenAPI 3.0 mandates that operationIds are unique within a single document;
duplicates here break deep-link expansion in Swagger UI viewers because
findOpElement() falls back to the first matching id.
"""
from __future__ import annotations
import argparse, glob, json, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan_dir(api_dir: str) -> tuple[int, int, int, dict[str, tuple[int, int, int]]]:
    total_files = total_ops = surplus = 0
    dups_per_file: dict[str, tuple[int, int, int]] = {}
    for fp in sorted(glob.glob(os.path.join(api_dir, '*.json'))):
        if fp.endswith('manifest.json'):
            continue
        try:
            with open(fp, encoding='utf-8') as f:
                spec = json.load(f)
        except Exception:
            continue
        ids: list[str] = []
        for path, methods in (spec.get('paths') or {}).items():
            if not isinstance(methods, dict):
                continue
            for verb, op in methods.items():
                if isinstance(op, dict) and 'operationId' in op:
                    ids.append(op['operationId'])
        cnt = Counter(ids)
        dup_surplus = sum(v - 1 for v in cnt.values() if v > 1)
        total_files += 1
        total_ops += len(ids)
        if dup_surplus:
            dups_per_file[fp] = (len(ids), len(cnt), dup_surplus)
            surplus += dup_surplus
    return total_files, total_ops, surplus, dups_per_file


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=15, help='show this many worst offenders')
    args = ap.parse_args()

    # Live viewer api/ dirs.
    api_dirs = sorted(glob.glob(os.path.join(ROOT, 'swagger-*-model', 'api')))
    # Per-release archive copies (if any).
    api_dirs += sorted(glob.glob(os.path.join(ROOT, 'releases', '*', 'swagger-*-model', 'api')))

    grand_files = grand_ops = grand_surplus = 0
    grand_dups: dict[str, tuple[int, int, int]] = {}
    for d in api_dirs:
        f, o, s, dups = scan_dir(d)
        grand_files += f
        grand_ops += o
        grand_surplus += s
        grand_dups.update(dups)

    print(f'{grand_files} spec files | {grand_ops} ops | '
          f'{grand_surplus} duplicate-op surplus across {len(grand_dups)} files')
    print()
    worst = sorted(grand_dups.items(), key=lambda kv: -kv[1][2])[:args.top]
    for fp, (t, u, d) in worst:
        rel = os.path.relpath(fp, ROOT)
        print(f'  {d:5d} dup-surplus | {t:5d} ops | {u:5d} unique | {rel}')
    return 1 if grand_surplus else 0


if __name__ == '__main__':
    raise SystemExit(main())
