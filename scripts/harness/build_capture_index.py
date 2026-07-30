"""Build the value-discovery index from captured responses (DEVICE_DATA_COLLECTION.md §5).

Walks every capture under scripts/harness/captures/, recursively flattens each
JSON response into (device, pid, module, category, path, leaf_xpath, value)
rows, and writes scripts/harness/capture-index.json. Mirrors the build/consume
pattern of scripts/build_paths_index.py.

Run:  python -X utf8 -m scripts.harness.build_capture_index
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator, Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

HARNESS_DIR = Path(__file__).resolve().parent
CAPTURES_DIR = HARNESS_DIR / "captures"
INDEX_PATH = HARNESS_DIR / "capture-index.json"


def _flatten(value: Any, prefix: str) -> Iterator[tuple[str, Any]]:
    """Yield (leaf_xpath, scalar_value) for every scalar under ``value``."""
    if isinstance(value, dict):
        for k, v in value.items():
            child = f"{prefix}/{k}" if prefix else str(k)
            yield from _flatten(v, child)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            child = f"{prefix}[{i}]"
            yield from _flatten(item, child)
    else:
        yield prefix, value


def iter_capture_files(captures_dir: Path) -> Iterator[Path]:
    yield from sorted(captures_dir.glob("*/*/*.json"))


def build_index(captures_dir: Path = CAPTURES_DIR) -> dict:
    """Return the index dict: metadata + flattened rows."""
    rows: list[dict] = []
    files = 0
    for cap in iter_capture_files(captures_dir):
        try:
            record = json.loads(cap.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        files += 1
        response = record.get("response")
        base = {
            "device": record.get("device"),
            "pid": record.get("pid"),
            "category": record.get("category"),
            "module": record.get("module"),
            "path": record.get("path"),
            "http_status": record.get("http_status"),
        }
        if response is None:
            continue
        for leaf_xpath, val in _flatten(response, ""):
            if isinstance(val, (dict, list)):
                continue
            rows.append({**base, "leaf_xpath": leaf_xpath, "value": val})
    return {
        "generated_at": None,  # set by caller if desired; kept deterministic here
        "capture_files": files,
        "row_count": len(rows),
        "rows": rows,
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--captures", help="Captures dir (default scripts/harness/captures)")
    ap.add_argument("--out", help="Output index path (default scripts/harness/capture-index.json)")
    args = ap.parse_args(argv)

    captures_dir = Path(args.captures) if args.captures else CAPTURES_DIR
    out_path = Path(args.out) if args.out else INDEX_PATH
    if not captures_dir.is_dir():
        print(f"No captures dir yet: {captures_dir}. Run the collector first.", file=sys.stderr)
        return 2

    index = build_index(captures_dir)
    out_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Indexed {index['capture_files']} capture file(s) -> "
          f"{index['row_count']} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
