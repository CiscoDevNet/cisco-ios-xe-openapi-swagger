#!/usr/bin/env python3
"""Show sample captured records (keys + leaf values) per xpath from a Telegraf
capture file, so you can inspect the actual depth/keys of the streamed data.

  .venv-harness/bin/python extract_sample.py output/mdt-C9400.json --grep oc- --paths 6
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--grep", default="", help="Only paths containing this substring.")
    ap.add_argument("--paths", type=int, default=8, help="Max distinct paths to show.")
    ap.add_argument("--fields", type=int, default=14, help="Max fields per sample.")
    args = ap.parse_args()

    seen = {}
    counts = {}
    for line in Path(args.file).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        path = rec.get("tags", {}).get("path", rec.get("name", ""))
        if args.grep and args.grep.lower() not in path.lower():
            continue
        counts[path] = counts.get(path, 0) + 1
        if path not in seen:
            seen[path] = rec

    for path in list(seen)[:args.paths]:
        rec = seen[path]
        tags = {k: v for k, v in rec.get("tags", {}).items()
                if k not in ("path", "subscription", "source")}
        fields = rec.get("fields", {})
        print("\n" + "=" * 78)
        print(f"XPATH  {path}    ({counts[path]} records)")
        if tags:
            print("KEYS/dims: " + ", ".join(f"{k}={v}" for k, v in tags.items()))
        print("FIELDS (leaf = value):")
        for i, (k, v) in enumerate(fields.items()):
            if i >= args.fields:
                print(f"   … (+{len(fields) - args.fields} more leaves)")
                break
            print(f"   {k} = {v}")


if __name__ == "__main__":
    raise SystemExit(main())
