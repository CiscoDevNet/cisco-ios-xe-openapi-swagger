#!/usr/bin/env python3
"""drop_v2_naming.py — One-shot refactor: drop project-naming "v2".

At top-level (``swagger-<cat>-model/``): both ``api/`` (legacy v1, flat specs)
and ``api-v2/`` (deep specs) are tracked with different content. We DROP v1
and promote v2 to ``api/``. Same for ``index.html`` (legacy redirect/v1
viewer) vs ``index-v2.html`` (real viewer): drop v1, promote v2, leave a
small redirect stub at ``index-v2.html`` for back-compat.

At per-release level (``releases/<ver>/swagger-<cat>-model/``): only
``api-v2/`` exists, so a simple rename to ``api/``.

Bulk text-replace tokens across source files: ``api-v2`` -> ``api``,
``index-v2.html`` -> ``index.html``, ``telemetry-reference.md`` ->
``telemetry-reference.md``.

Real protocol/standard names (e.g. ``Cisco-IOS-XE-mdt-oper-v2.yang``,
``openconfig-ospfv2.yang``, ``SNMPv2-MIB.yang``, ``ietf-yang-smiv2.yang``)
are NOT touched — they are real YANG module names.

Filesystem-level deletes/moves only — `git add -A` at commit time records
all changes. This avoids the interactive "Should I try again? (y/n)" prompt
that ``git rm -rf`` triggers on Windows OneDrive paths with read-only flags.
"""
from __future__ import annotations
import os
import shutil
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent

SKIP_DIR_PARTS = {".git", "__pycache__", "archive", "node_modules"}
TEXT_EXTS = {".html", ".js", ".py", ".md", ".json", ".yml", ".yaml", ".txt", ".css"}

REDIRECT_STUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url=index.html">
<title>Redirecting</title>
<script>
  var t = 'index.html';
  if (location.hash) t += location.hash;
  if (location.search) t += location.search;
  location.replace(t);
</script>
<link rel="canonical" href="index.html">
</head>
<body>
<p>This page has moved to <a href="index.html">index.html</a>.</p>
</body>
</html>
"""

REPLACEMENTS = [
    ("telemetry-reference.md", "telemetry-reference.md"),
    ("index-v2.html",             "index.html"),
    ("api-v2",                    "api"),
]


def _force_rmtree(path: Path) -> None:
    """Remove a directory tree, clearing read-only attributes as we go."""
    def _onerror(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
        except OSError:
            pass
        try:
            func(p)
        except OSError:
            pass
    if path.exists():
        shutil.rmtree(str(path), onerror=_onerror)


def _walk(root):
    for d, dirnames, filenames in os.walk(root):
        dirnames[:] = [n for n in dirnames if n not in SKIP_DIR_PARTS]
        yield Path(d), dirnames, filenames


def phase1a_toplevel_promote():
    api_n = idx_n = 0
    for d in sorted(ROOT.glob("swagger-*-model")):
        v1_api, v2_api = d / "api", d / "api-v2"
        if v2_api.is_dir():
            _force_rmtree(v1_api)
            shutil.move(str(v2_api), str(v1_api))
            api_n += 1
            print(f"  api    {d.name}: dropped v1, promoted v2")
        v1_idx, v2_idx = d / "index.html", d / "index-v2.html"
        if v2_idx.is_file():
            if v1_idx.is_file():
                try:
                    os.chmod(v1_idx, stat.S_IWRITE)
                except OSError:
                    pass
                try:
                    v1_idx.unlink()
                except OSError:
                    pass
            shutil.move(str(v2_idx), str(v1_idx))
            v2_idx.write_text(REDIRECT_STUB, encoding="utf-8", newline="\n")
            idx_n += 1
            print(f"  index  {d.name}: promoted v2, stub at index-v2.html")
    return api_n, idx_n


def phase1b_release_renames():
    n = 0
    for v2_api in sorted(ROOT.glob("releases/*/swagger-*-model/api-v2")):
        api = v2_api.parent / "api"
        if api.exists():
            continue
        shutil.move(str(v2_api), str(api))
        n += 1
    print(f"  {n} per-release api-v2/ dirs renamed")
    return n


def _should_replace(path):
    if path.suffix.lower() not in TEXT_EXTS:
        return False
    if path.name == "drop_v2_naming.py":
        return False
    parts = set(path.parts)
    if parts & SKIP_DIR_PARTS:
        return False
    p = str(path).replace("\\", "/")
    if "/swagger-" in p and "/api/" in p and path.suffix == ".json":
        return path.name == "manifest.json"
    return True


def phase2_bulk_replace():
    files_changed = 0
    total_subs = 0
    candidates = []
    for d, _, filenames in _walk(ROOT):
        for fn in filenames:
            p = d / fn
            if _should_replace(p):
                candidates.append(p)
    if WORKSPACE.exists():
        for p in WORKSPACE.iterdir():
            if p.is_file() and _should_replace(p):
                candidates.append(p)
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new = text
        for old_tok, new_tok in REPLACEMENTS:
            if old_tok in new:
                new = new.replace(old_tok, new_tok)
        if new != text:
            before = sum(text.count(o) for o, _ in REPLACEMENTS)
            after = sum(new.count(o) for o, _ in REPLACEMENTS)
            try:
                os.chmod(path, stat.S_IWRITE)
            except OSError:
                pass
            path.write_text(new, encoding="utf-8", newline="\n")
            files_changed += 1
            total_subs += (before - after)
    return files_changed, total_subs


def phase3_telemetry():
    src = WORKSPACE / "telemetry-reference.md"
    dst = WORKSPACE / "telemetry-reference.md"
    if not src.is_file() or dst.exists():
        return False
    shutil.move(str(src), str(dst))
    print(f"  mv {src.name} -> {dst.name}")
    return True


def main():
    print("=== Phase 1a: top-level promote (drop v1, v2 -> canonical) ===")
    a, i = phase1a_toplevel_promote()
    print(f"  {a} api dirs, {i} index pages promoted")
    print("\n=== Phase 1b: per-release api-v2/ -> api/ ===")
    phase1b_release_renames()
    print("\n=== Phase 2: bulk text replace ===")
    f, s = phase2_bulk_replace()
    print(f"  {f} files rewritten, {s} substitutions")
    print("\n=== Phase 3: telemetry-reference rename ===")
    phase3_telemetry()
    print("\nDone. Use `git add -A` to stage all changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
