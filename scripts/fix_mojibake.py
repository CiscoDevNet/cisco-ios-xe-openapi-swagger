"""Repair mojibake using ftfy. Skips archive/, references/, node_modules/, .git/."""
from __future__ import annotations
import pathlib
import ftfy

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"archive", "references", "node_modules", ".git"}

def included(p: pathlib.Path) -> bool:
    parts = p.relative_to(ROOT).parts
    return not any(part in SKIP for part in parts)

changed = 0
scanned = 0
for ext in ("*.html", "*.js", "*.css", "*.md"):
    for path in ROOT.rglob(ext):
        if not included(path):
            continue
        try:
            txt = path.read_text(encoding="utf-8")
        except Exception:
            continue
        scanned += 1
        new = ftfy.fix_text(txt)
        if new != txt:
            path.write_text(new, encoding="utf-8", newline="")
            changed += 1
            print(f"fixed: {path.relative_to(ROOT)}")

print(f"\nscanned={scanned} changed={changed}")
