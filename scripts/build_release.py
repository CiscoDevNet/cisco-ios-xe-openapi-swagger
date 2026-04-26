#!/usr/bin/env python3
"""
build_release.py — Per-release orchestrator.

Runs the full pipeline for a single IOS-XE release: spec generators, post-processing,
pyang trees, manifests, accountability, search index, telemetry index, MIB metadata,
native capabilities, and Postman/Bruno exports. Idempotent — safe to re-run.

Authoritative spec: VERSIONING.md §8 (release runbook), §9 (CI gates).

Usage:
    python scripts/build_release.py --version 26.1.1
    python scripts/build_release.py --version 26.1.1 --skip-exports
    python scripts/build_release.py --version 26.1.1 --only trees,search
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

# Force UTF-8 for our own stdout/stderr so we can safely re-emit child output
# containing ✓ / ✗ characters on Windows cp1252 consoles.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = PROJECT_ROOT / "scripts"
GENERATORS = PROJECT_ROOT / "generators"

# Ordered pipeline. Each entry: (label, command-as-list-of-tokens).
# ``$VER`` is substituted with the release version at run time.
PIPELINE: list[tuple[str, list[str]]] = [
    # 1. Spec generation per model category
    ("oper-specs",          ["python", str(GENERATORS / "generate_oper_openapi_v2.py"),
                             "--version", "$VER"]),
    ("cfg-specs",           ["python", str(GENERATORS / "generate_cfg_openapi_v2.py"),
                             "--version", "$VER"]),
    ("native-specs",        ["python", str(GENERATORS / "generate_native_openapi_v2.py"),
                             "--version", "$VER"]),
    ("openconfig-specs",    ["python", str(GENERATORS / "generate_openconfig_openapi_v2.py"),
                             "--version", "$VER"]),
    ("ietf-specs",          ["python", str(GENERATORS / "generate_ietf_openapi_v2.py"),
                             "--version", "$VER"]),
    ("mib-specs",           ["python", str(GENERATORS / "generate_mib_openapi_v2.py"),
                             "--version", "$VER"]),
    ("rpc-specs",           ["python", str(GENERATORS / "generate_rpc_openapi_v2.py"),
                             "--version", "$VER"]),
    ("events-specs",        ["python", str(GENERATORS / "generate_events_openapi.py"),
                             "--version", "$VER"]),
    ("other-specs",         ["python", str(GENERATORS / "generate_other_openapi_v2.py"),
                             "--version", "$VER"]),
    # 2. Post-processing / enrichment
    ("enrich",              ["python", str(SCRIPTS / "enrich_v2_specs.py"),
                             "--version", "$VER"]),
    ("github-links",        ["python", str(SCRIPTS / "add_yang_github_links.py"),
                             "--version", "$VER"]),
    ("external-docs",       ["python", str(SCRIPTS / "add_external_docs.py"),
                             "--version", "$VER"]),
    # 3. Trees
    ("trees",               ["python", str(SCRIPTS / "generate_all_pyang_trees.py"),
                             "--version", "$VER"]),
    ("tree-links",          ["python", str(SCRIPTS / "add_tree_links.py"),
                             "--version", "$VER"]),
    # 4. MDT annotations (oper specs)
    ("mdt-annotate",        ["python", str(SCRIPTS / "annotate_mdt_xpaths.py"),
                             "--version", "$VER"]),
    # 5. MIB enrichment + native capabilities + native CLI/example overlays
    ("mibs-md-parse",       ["python", str(SCRIPTS / "parse_mibs_md.py"),
                             "--version", "$VER"]),
    ("mib-metadata",        ["python", str(SCRIPTS / "enrich_mib_metadata.py"),
                             "--version", "$VER"]),
    ("native-cli-mappings", ["python", str(SCRIPTS / "apply_cli_mappings.py"),
                             "--version", "$VER"]),
    ("native-example-overlay", ["python", str(SCRIPTS / "apply_example_overlay.py"),
                             "--version", "$VER"]),
    ("native-capabilities", ["python", str(SCRIPTS / "build_native_capabilities.py"),
                             "--version", "$VER"]),
    # 6. Manifests + accountability + search
    ("manifests",           ["python", str(SCRIPTS / "update_manifests.py"),
                             "--version", "$VER"]),
    ("stamp-spec-count",    ["python", str(SCRIPTS / "stamp_spec_count.py"),
                             "--version", "$VER"]),
    ("accountability",      ["python", str(SCRIPTS / "analyze_yang_accountability_v2.py"),
                             "--version", "$VER"]),
    ("search-index",        ["python", str(SCRIPTS / "generate_search_index.py"),
                             "--version", "$VER"]),
    # 7. Exports
    ("postman",             ["python", str(SCRIPTS / "generate_postman_v2_collection.py"),
                             "--version", "$VER", "--per-category", "--max-mb", "50"]),
    ("bruno",               ["python", str(SCRIPTS / "generate_bruno_collection.py"),
                             "--version", "$VER", "--per-category", "--max-mb", "50"]),
]


def run_step(label: str, cmd: list[str]) -> tuple[bool, float]:
    print(f"\n=== [{label}] {' '.join(cmd)}")
    t0 = time.time()
    # Force UTF-8 output from child Python processes so legacy generators that
    # emit ✓ / ✗ characters don't crash on Windows cp1252 consoles.
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    try:
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              env=env)
    except FileNotFoundError as e:
        print(f"[{label}] command not found: {e}")
        return False, time.time() - t0
    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    # Backward-compat shim: legacy generators have not yet been refactored to
    # accept --version. argparse exits 2 with "unrecognized arguments" or
    # "error: unrecognized arguments". Strip --version and retry once.
    if proc.returncode != 0 and "--version" in cmd and (
            "unrecognized arguments" in (proc.stderr or "")
            or "unrecognized arguments" in (proc.stdout or "")):
        stripped = []
        skip = False
        for tok in cmd:
            if skip:
                skip = False
                continue
            if tok == "--version":
                skip = True
                continue
            stripped.append(tok)
        print(f"[{label}] retrying without --version (legacy generator): "
              f"{' '.join(stripped)}")
        try:
            proc = subprocess.run(stripped, cwd=PROJECT_ROOT, env=env)
        except FileNotFoundError as e:
            print(f"[{label}] command not found: {e}")
            return False, time.time() - t0
        return proc.returncode == 0, time.time() - t0
    return proc.returncode == 0, time.time() - t0


def update_meta(version: str, results: list[dict]) -> None:
    meta_path = PROJECT_ROOT / "releases" / version / "meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict = {}
    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    existing["version"] = version
    existing["build_timestamp"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    existing["last_build"] = {"steps": results}
    meta_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--version", required=True, help="Release tag (e.g. 26.1.1)")
    parser.add_argument(
        "--only", default="",
        help="Comma-separated subset of step labels to run (others skipped)",
    )
    parser.add_argument(
        "--skip", default="",
        help="Comma-separated step labels to skip",
    )
    parser.add_argument(
        "--skip-exports", action="store_true",
        help="Shortcut for --skip postman,bruno",
    )
    parser.add_argument(
        "--continue-on-error", action="store_true",
        help="Run all steps even if some fail (default: stop on first failure)",
    )
    args = parser.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    if args.skip_exports:
        skip.update({"postman", "bruno"})

    print(f"\n[build_release] version={args.version} only={only or 'ALL'} skip={skip or '-'}")

    results: list[dict] = []
    failed = False
    for label, cmd in PIPELINE:
        if only and label not in only:
            results.append({"label": label, "status": "skipped-not-in-only"})
            continue
        if label in skip:
            results.append({"label": label, "status": "skipped"})
            continue
        cmd_resolved = [t.replace("$VER", args.version) for t in cmd]
        ok, elapsed = run_step(label, cmd_resolved)
        results.append({
            "label": label,
            "status": "ok" if ok else "failed",
            "seconds": round(elapsed, 2),
        })
        if not ok:
            failed = True
            if not args.continue_on_error:
                break

    update_meta(args.version, results)
    print("\n[build_release] step summary:")
    for r in results:
        print(f"  {r['label']:22} {r['status']:24} {r.get('seconds','')}")
    if failed:
        print("\n[build_release] FAILED — see step output above.")
        return 1
    print("\n[build_release] OK — next: python scripts/validate_release.py --version "
          f"{args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
