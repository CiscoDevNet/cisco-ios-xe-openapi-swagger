#!/usr/bin/env python3
"""One-shot rebrand pass:

  1. "IOS-XE"  -> "IOS XE"   (user-visible brand only — never touches
     YANG module ids like Cisco-IOS-XE-native, Postman filenames like
     IOS-XE-RESTCONF-v1, or the repo slug cisco-ios-xe-openapi-swagger).
  2. "OpenAPI / YANG Explorer" -> "OpenAPI Documentation Hub"
     (and stripped "YANG Explorer" branding of this app).

Scope: root-level .html / .js / .md / .py that drive the deployed site,
plus the two figure generators. Skips archive/, releases/, generators/,
references/, swagger-*-model/, yang-trees/, tools/, tests/, docs/,
.github/, .git/, and tmp/.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---- "IOS-XE" -> "IOS XE" only when it isn't part of a longer identifier.
#  - negative lookbehind  (?<!Cisco-)   -> skip "Cisco-IOS-XE..." YANG ids
#  - negative lookahead   (?!-)         -> skip "IOS-XE-RESTCONF-..." files
IOS_XE_RE = re.compile(r"(?<!Cisco-)IOS-XE(?!-)")

# ---- "OpenAPI / YANG Explorer" branding of THIS app.
EXPLORER_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"OpenAPI\s*/\s*YANG Explorer"), "OpenAPI Documentation Hub"),
    (re.compile(r"IOS XE OpenAPI Documentation Hub / YANG Documentation Hub"),
     "IOS XE OpenAPI Documentation Hub"),  # cleanup of any odd combo
]

SKIP_DIRS = {
    ".git", ".github", "archive", "releases", "generators",
    "references", "tests", "tools", "tmp", "yang-trees", "docs",
    "node_modules",
}
SKIP_FILES = {
    # don't touch this script
    "rebrand_ios_xe.py",
    # spec/audit/historical docs — leave for now
    "ASSURANCE_SPEC.md", "PROJECT_REQUIREMENTS.md",
    "DEVNET-1232-CISCO-LIVE-2026.md",
    "AGENTS.md",
}
# Skip every swagger-*-model directory (per-spec viewer roots use real
# Cisco-IOS-XE-foo module names inside their generated JSON — we don't
# touch generated data).
ALLOWED_EXTS = {".html", ".js", ".md", ".py"}


def should_process(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = set(rel.parts)
    if parts & SKIP_DIRS:
        return False
    if any(p.startswith("swagger-") and p.endswith("-model") for p in rel.parts):
        return False
    if path.name in SKIP_FILES:
        return False
    if path.suffix.lower() not in ALLOWED_EXTS:
        return False
    return True


def rewrite(text: str) -> tuple[str, int]:
    n = 0
    new_text, c = IOS_XE_RE.subn("IOS XE", text)
    n += c
    for pat, repl in EXPLORER_PATTERNS:
        new_text, c = pat.subn(repl, new_text)
        n += c
    return new_text, n


def main() -> int:
    changed: list[tuple[Path, int]] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # prune subdirectory descent in-place
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS
            and not (d.startswith("swagger-") and d.endswith("-model"))
        ]
        dpath = Path(dirpath)
        for fn in filenames:
            p = dpath / fn
            if p.name in SKIP_FILES:
                continue
            if p.suffix.lower() not in ALLOWED_EXTS:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            new_text, n = rewrite(text)
            if n and new_text != text:
                p.write_text(new_text, encoding="utf-8")
                changed.append((p.relative_to(ROOT), n))
    for rel, n in changed:
        print(f"  {n:4d}  {rel.as_posix()}")
    print(f"\nRewrote {len(changed)} files, {sum(n for _, n in changed)} replacements total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
