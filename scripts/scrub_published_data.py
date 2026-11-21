#!/usr/bin/env python3
"""scrub_published_data.py — apply the shared redaction rules to every published device-data file.

Publish-time safety net on top of the per-builder redaction: re-scrubs the repo-root
Device Data datasets, protocol-matrix.json, releases/<ver>/live-data/** and gnmi-data/**, plus the
live-examples index and live-modules files, with
scripts/mdt-telemetry/collector/redact_payload.py. Idempotent; keeps each file's JSON
formatting. Secrets and credential usernames become ``***REDACTED***``.

Usage:
    python scripts/scrub_published_data.py            # rewrite files that change
    python scripts/scrub_published_data.py --check    # exit 1 if anything would change
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "mdt-telemetry" / "collector"))

from redact_payload import redact_obj  # noqa: E402

PATTERNS = [
    "*-live-data.json",
    "protocol-matrix.json",
    "releases/*/live-data/**/*.json",
    "releases/*/gnmi-data/**/*.json",
    "releases/*/live-examples-index.json",
    "releases/*/live-modules.json",
]
STYLES = [
    {"separators": (",", ":")},
    {"indent": 2},
    {"indent": 1},
    {},
]


def published_files() -> list[Path]:
    seen: dict[Path, None] = {}
    for pattern in PATTERNS:
        for f in sorted(REPO.glob(pattern)):
            seen[f] = None
    return list(seen)


def _dump(obj, text: str) -> str:
    """Serialise in the style the file already uses (the builders' style when unknown)."""
    original = json.loads(text)
    body = text.rstrip("\n")
    for style in STYLES:
        for ascii_flag in (False, True):
            if json.dumps(original, ensure_ascii=ascii_flag, **style) == body:
                return json.dumps(obj, ensure_ascii=ascii_flag, **style) + text[len(body):]
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"


def scrub(path: Path, check: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    doc = json.loads(text)
    red = redact_obj(doc)
    if red == doc:
        return False
    if not check:
        path.write_text(_dump(red, text), encoding="utf-8", newline="\n")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report files that would change; do not write")
    args = ap.parse_args()
    files = published_files()
    changed = [f for f in files if scrub(f, args.check)]
    verb = "would change" if args.check else "scrubbed"
    print(f"{len(files)} published files checked; {len(changed)} {verb}")
    for f in changed[:50]:
        print("  " + f.relative_to(REPO).as_posix())
    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
