#!/usr/bin/env python3
"""
parse_mibs_md.py — Parse MIBS.md (workspace root) into a structured JSON file.

Extracts:
  * per-platform availability matrix (§3.5) → mib → list of platforms advertising it
  * functional categories (§2.1 — §2.25) → mib → category, role text
  * latest-release inventory (§1.5) → set of MIBs in latest release

Writes ``cisco-ios-xe-openapi-swagger/releases/<ver>/mib-platform-matrix.json`` for the
release passed via ``--version`` (or to a single shared file if ``--shared``).

Authoritative input: ../MIBS.md.
Companion to: enrich_mib_metadata.py.

Usage:
    python scripts/parse_mibs_md.py --version 26.1.1
    python scripts/parse_mibs_md.py --version 17.18.1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import PROJECT_ROOT  # type: ignore  # noqa: E402

WORKSPACE_ROOT = PROJECT_ROOT.parent
MIBS_MD = WORKSPACE_ROOT / "MIBS.md"

RE_FULL_MATRIX_HEADER = re.compile(r"^### 3\.5\b", re.MULTILINE)
RE_FUNCTIONAL_HEADER = re.compile(r"^### 2\.(\d+)\.\s+(.+?)\s*$", re.MULTILINE)
RE_NEXT_HEADING = re.compile(r"^#{1,3} ", re.MULTILINE)
RE_TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")


def parse_full_availability_matrix(text: str) -> tuple[list[str], dict[str, list[str]]]:
    """Return (platforms, mib → [platforms-advertising-it])."""
    m = RE_FULL_MATRIX_HEADER.search(text)
    if not m:
        return [], {}
    section = text[m.end():]
    end = RE_NEXT_HEADING.search(section)
    if end:
        section = section[: end.start()]
    lines = [ln for ln in section.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return [], {}
    header_cells = [c.strip() for c in lines[0].strip("|").split("|")]
    if not header_cells or header_cells[0].lower() != "mib":
        return [], {}
    platforms = header_cells[1:]
    matrix: dict[str, list[str]] = {}
    for ln in lines[2:]:  # skip separator line
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) < 2 or cells[0].startswith(":"):
            continue
        mib = cells[0].strip("`").strip()
        if not mib or "MIB" not in mib.upper() and not mib.endswith("-MIB") and "-TC" not in mib:
            # accept any token in column 1; the markdown may have bare strings
            pass
        marks = cells[1:1 + len(platforms)]
        present = [p for p, v in zip(platforms, marks) if v.strip().startswith("✓")]
        if mib:
            matrix[mib] = present
    return platforms, matrix


def parse_functional_categories(text: str) -> dict[str, dict[str, str]]:
    """Return mib → {category, role}. The role is the description column from the table."""
    headers = list(RE_FUNCTIONAL_HEADER.finditer(text))
    out: dict[str, dict[str, str]] = {}
    for i, m in enumerate(headers):
        cat_num = f"2.{m.group(1)}"
        cat_name = m.group(2).strip()
        body_start = m.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[body_start:body_end]
        next_h = re.search(r"^## ", body, re.MULTILINE)
        if next_h:
            body = body[: next_h.start()]
        for line in body.splitlines():
            row = RE_TABLE_ROW.match(line.strip())
            if not row:
                continue
            cells = [c.strip() for c in row.group(1).split("|")]
            if len(cells) < 2:
                continue
            first = cells[0]
            if first.lower() in ("mib", "---", ":--:"):
                continue
            # MIB names may include comma-separated multiples like `CISCO-CBP-TARGET-TC-MIB`, `CISCO-CBP-TC-MIB`
            for mib_token in re.findall(r"`([^`]+)`", first):
                mib = mib_token.strip()
                if not mib:
                    continue
                role = cells[1].strip() if len(cells) > 1 else ""
                # Don't overwrite an existing mapping with a less specific one
                out.setdefault(mib, {"category": f"{cat_num} {cat_name}", "role": role})
    return out


def parse_latest_inventory(text: str) -> list[str]:
    """Best-effort: collect every MIB-shaped backticked token under §1.5."""
    m = re.search(r"^### 1\.5\b", text, re.MULTILINE)
    if not m:
        return []
    section = text[m.end():]
    end = RE_NEXT_HEADING.search(section)
    if end:
        section = section[: end.start()]
    seen: list[str] = []
    seen_set: set[str] = set()
    for tok in re.findall(r"`([A-Z][A-Z0-9\-]+)`", section):
        if tok not in seen_set:
            seen.append(tok)
            seen_set.add(tok)
    return seen


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", required=True)
    args = p.parse_args()

    if not MIBS_MD.is_file():
        sys.stderr.write(f"[mibs] missing {MIBS_MD}\n")
        return 1
    text = MIBS_MD.read_text(encoding="utf-8")

    platforms, matrix = parse_full_availability_matrix(text)
    print(f"[mibs] platforms: {len(platforms)}; matrix rows: {len(matrix)}")
    categories = parse_functional_categories(text)
    print(f"[mibs] functional category mappings: {len(categories)}")
    inventory = parse_latest_inventory(text)
    print(f"[mibs] latest-release inventory tokens: {len(inventory)}")

    out_dir = PROJECT_ROOT / "releases" / args.version
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "mib-platform-matrix.json"
    out.write_text(json.dumps({
        "version": args.version,
        "source": "MIBS.md",
        "generated": datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
        "platforms": platforms,
        "platform_matrix": matrix,
        "functional_categories": categories,
        "latest_inventory": inventory,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"[mibs] wrote {out.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
