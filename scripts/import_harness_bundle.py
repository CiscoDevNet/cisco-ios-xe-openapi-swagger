#!/usr/bin/env python3
"""
import_harness_bundle.py — verify a portable-harness bundle and import it into the webapp.

The bundle comes from the kit (`./harness bundle`, scripts/harness/kit.py). Every file
is checked before anything is touched: allowed path, sha256 + size against the
manifest, no unlisted files, JSON PID matches the file name, and no unmasked secret.
Default is a dry run that prints the plan. --apply copies the files into place
(anything replaced is moved to scripts/harness/import-archive/<UTC>/), then rebuilds
the Device Data datasets and protocol-matrix.json.

    .venv-harness/bin/python scripts/import_harness_bundle.py dist/harness-bundle-<UTC>.tar.gz
    .venv-harness/bin/python scripts/import_harness_bundle.py dist/harness-bundle-<UTC>.tar.gz --apply
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[1]
COLLECTOR = REPO / "scripts" / "mdt-telemetry" / "collector"
OUTPUT = COLLECTOR / "output"
ARCHIVE_ROOT = REPO / "scripts" / "harness" / "import-archive"
BUNDLE_FORMAT = "iosxe-harness-bundle/1"
ROOT = "harness-bundle/"
MAX_FILE_BYTES = 512 * 1024 * 1024

NAME = r"[A-Za-z0-9][A-Za-z0-9._-]*"
OUTPUT_RE = re.compile(rf"^scripts/mdt-telemetry/collector/output/"
                       rf"(?P<kind>config|restconf|netconf|netconf-sub|netconf-sub-config|gnmi|gnmi-sub|mdt|facts|coverage)"
                       rf"-(?P<pid>{NAME})\.json$")
ALLOWED = [
    OUTPUT_RE,
    re.compile(rf"^scripts/harness/captures/{NAME}/[a-z-]+/{NAME}\.json$"),
    re.compile(rf"^scripts/harness/onboard-output/{NAME}-onboard\.json$"),
]
LOG_RE = re.compile(rf"^logs/{NAME}\.log$")  # verified, kept in the bundle, never imported

sys.path.insert(0, str(COLLECTOR))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class BundleError(RuntimeError):
    pass


def output_kind(relative: str) -> tuple[str, str] | None:
    """(kind, pid) for a collector output file. The pid group is greedy, so
    netconf-sub-config-X / netconf-sub-X / gnmi-sub-X are disambiguated here."""
    match = OUTPUT_RE.match(relative)
    if not match:
        return None
    name = PurePosixPath(relative).stem
    for kind in ("netconf-sub-config", "netconf-sub", "gnmi-sub", "config", "restconf", "netconf", "gnmi", "mdt",
                 "facts", "coverage"):
        if name.startswith(kind + "-"):
            return kind, name[len(kind) + 1:]
    return None


def stage_bundle(bundle: Path, staging: Path) -> tuple[dict, dict]:
    """Extract regular files under harness-bundle/ into `staging`, hashing as we go."""
    digests: dict[str, dict] = {}
    with tarfile.open(bundle, "r:gz") as archive:
        for member in archive:
            if member.isdir():
                continue
            if not member.isfile():
                raise BundleError(f"not a regular file: {member.name}")
            parts = PurePosixPath(member.name).parts
            if not member.name.startswith(ROOT) or ".." in parts or member.name.startswith("/"):
                raise BundleError(f"unsafe path: {member.name}")
            if member.size > MAX_FILE_BYTES:
                raise BundleError(f"file too large: {member.name}")
            relative = member.name[len(ROOT):]
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with archive.extractfile(member) as source, open(target, "wb") as destination:
                for block in iter(lambda: source.read(1 << 20), b""):
                    digest.update(block)
                    destination.write(block)
            digests[relative] = {"sha256": digest.hexdigest(), "bytes": member.size}
    if "manifest.json" not in digests:
        raise BundleError("manifest.json missing")
    digests.pop("manifest.json")
    manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
    return manifest, digests


def verify(manifest: dict, digests: dict, staging: Path) -> list[str]:
    """Return a list of problems (empty = bundle is safe to import)."""
    from scripts.harness.kit import deep_scan

    problems = []
    if manifest.get("format") != BUNDLE_FORMAT:
        problems.append(f"unknown bundle format {manifest.get('format')!r}")
    listed = manifest.get("files") or {}
    for relative in sorted(set(digests) - set(listed)):
        problems.append(f"{relative}: not listed in manifest")
    for relative in sorted(set(listed) - set(digests)):
        problems.append(f"{relative}: listed in manifest but missing")
    for relative in sorted(set(digests) & set(listed)):
        if digests[relative] != {"sha256": listed[relative].get("sha256"), "bytes": listed[relative].get("bytes")}:
            problems.append(f"{relative}: checksum/size mismatch")
            continue
        if LOG_RE.match(relative):
            continue
        if not any(pattern.match(relative) for pattern in ALLOWED):
            problems.append(f"{relative}: path not allowed")
            continue
        text = (staging / relative).read_text(encoding="utf-8")
        for label, _ in deep_scan(text):
            problems.append(f"{relative}: unmasked secret ({label})")
        kind_pid = output_kind(relative)
        if kind_pid and kind_pid[0] != "mdt":
            try:
                pid = json.loads(text).get("pid")
            except json.JSONDecodeError:
                problems.append(f"{relative}: invalid JSON")
                continue
            if pid != kind_pid[1]:
                problems.append(f"{relative}: pid {pid!r} does not match file name")
    return problems


def inventory_pids() -> list[str]:
    inventory = REPO / "scripts" / "harness" / "inventory.json"
    try:
        return [d["pid"] for d in json.loads(inventory.read_text(encoding="utf-8"))]
    except (OSError, json.JSONDecodeError, KeyError):
        return []


def size_metric(relative: str, data: bytes):
    """Comparable amount of collected data in one file: MDT records, collector
    entries, or 1/0 for whether a walk capture returned HTTP 200."""
    kind_pid = output_kind(relative)
    if kind_pid and kind_pid[0] == "mdt":
        return sum(1 for line in data.splitlines() if line.strip())
    try:
        document = json.loads(data)
    except json.JSONDecodeError:
        return None
    if not isinstance(document, dict):
        return None
    if relative.startswith("scripts/harness/captures/"):
        return 1 if document.get("http_status") == 200 else 0
    if kind_pid and kind_pid[0] in ("facts", "coverage"):
        return None
    entries = document.get("entries")
    return len(entries) if isinstance(entries, list) else None


def plan_import(digests: dict, staging: Path) -> list[dict]:
    """One action per file: new | replace | same, plus `supersede` for older MDT
    files (e.g. legacy mdt-C9300.json) that resolve to the same device PID.
    A replace that would hold less data than the current file is flagged `shrinks`."""
    from build_live_dataset import pid_from_file

    known = inventory_pids()
    actions = []
    for relative in sorted(digests):
        if LOG_RE.match(relative):
            continue
        target = REPO / relative
        incoming = (staging / relative).read_bytes()
        item = {"action": "new", "path": relative}
        if target.exists():
            current = target.read_bytes()
            item["action"] = "same" if current == incoming else "replace"
            if item["action"] == "replace":
                before, after = size_metric(relative, current), size_metric(relative, incoming)
                if before is not None and after is not None and after < before:
                    item["shrinks"] = f"{before} -> {after}"
        actions.append(item)
        kind_pid = output_kind(relative)
        if kind_pid and kind_pid[0] == "mdt":
            for existing in sorted(OUTPUT.glob("mdt-*.json")):
                if existing.name in (PurePosixPath(relative).name, "mdt-live.json") or ".prev" in existing.name:
                    continue
                if pid_from_file(existing.name, known + [kind_pid[1]]) == kind_pid[1]:
                    actions.append({"action": "supersede", "path": existing.relative_to(REPO).as_posix()})
    return actions


def apply_import(actions: list[dict], staging: Path, stamp: str) -> Path:
    archive_dir = ARCHIVE_ROOT / stamp
    for item in actions:
        target = REPO / item["path"]
        if item["action"] in ("replace", "supersede"):
            saved = archive_dir / item["path"]
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), saved)
        if item["action"] in ("new", "replace"):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(staging / item["path"], target)
    return archive_dir


def rebuild_commands(actions: list[dict], release: str) -> list[tuple[list[str], Path]]:
    changed = [a["path"] for a in actions if a["action"] in ("new", "replace", "supersede")]
    kinds = {output_kind(p)[0] for p in changed if output_kind(p)}
    commands = []
    if kinds & {"netconf", "netconf-sub", "netconf-sub-config"}:
        commands.append(([sys.executable, "build_netconf_dataset.py"], COLLECTOR))
    if kinds & {"gnmi", "gnmi-sub"}:
        commands.append(([sys.executable, "build_gnmi_dataset.py"], COLLECTOR))
    if "mdt" in kinds:
        commands.append(([sys.executable, "build_live_dataset.py"], COLLECTOR))
    if any(p.startswith("scripts/harness/captures/") for p in changed):
        commands.append(([sys.executable, "scripts/refresh_live_data.py", "--version", release], REPO))
        commands.append(([sys.executable, "scripts/build_restconf_dataset.py"], REPO))
    if commands or kinds:
        commands.append(([sys.executable, "build_protocol_matrix.py"], COLLECTOR))
    return commands


def print_plan(manifest: dict, actions: list[dict]) -> None:
    print(f"bundle: release {manifest.get('release')}, created {manifest.get('created')}, "
          f"kit commit {(manifest.get('kit') or {}).get('commit', 'n/a')}")
    for device in manifest.get("devices", []):
        print(f"  device {device.get('pid')}: {device.get('name')} hostname={device.get('hostname')} "
              f"version={device.get('version')}")
    unknown = sorted({d.get("pid") for d in manifest.get("devices", [])} - set(inventory_pids()))
    if unknown:
        print(f"  note: not in scripts/harness/inventory.json (new to this repo): {', '.join(unknown)}")
    totals: dict[str, int] = {}
    for item in actions:
        totals[item["action"]] = totals.get(item["action"], 0) + 1
    print("  plan: " + ", ".join(f"{k}={v}" for k, v in sorted(totals.items())))
    for item in actions:
        if item["action"] != "same" and not item["path"].startswith("scripts/harness/captures/"):
            shrink = f"  SHRINKS {item['shrinks']}" if "shrinks" in item else ""
            print(f"    {item['action']:9} {item['path']}{shrink}")
    captures = sum(1 for a in actions if a["path"].startswith("scripts/harness/captures/") and a["action"] != "same")
    if captures:
        lost = sum(1 for a in actions if a["path"].startswith("scripts/harness/captures/") and "shrinks" in a)
        print(f"    {captures} RESTCONF walk capture file(s) new or changed"
              + (f", {lost} would lose HTTP 200 data" if lost else ""))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bundle")
    parser.add_argument("--apply", action="store_true", help="Import (default: verify and print the plan)")
    parser.add_argument("--no-build", action="store_true", help="Skip rebuilding the datasets after --apply")
    parser.add_argument("--allow-shrink", action="store_true",
                        help="Import even where a file would hold less data than today (e.g. a --limit smoke run)")
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="harness-bundle-") as temp:
        staging = Path(temp)
        try:
            manifest, digests = stage_bundle(Path(args.bundle), staging)
        except (BundleError, tarfile.TarError, json.JSONDecodeError, OSError) as exc:
            print(f"REJECTED: {exc}", file=sys.stderr)
            return 1
        problems = verify(manifest, digests, staging)
        if problems:
            print("REJECTED:\n  " + "\n  ".join(problems[:50]), file=sys.stderr)
            return 1
        print(f"verified: {len(digests)} files, checksums and secret scan ok")
        actions = plan_import(digests, staging)
        print_plan(manifest, actions)
        release = manifest.get("release", "")
        has_captures = any(a["path"].startswith("scripts/harness/captures/") for a in actions)
        if has_captures and not (REPO / "releases" / release).is_dir():
            print(f"REJECTED: release {release!r} not in releases/", file=sys.stderr)
            return 1
        if not args.apply:
            print("\nDry run. Re-run with --apply to import.")
            return 0
        shrinking = [a for a in actions if "shrinks" in a]
        if shrinking and not args.allow_shrink:
            print(f"REFUSED: {len(shrinking)} file(s) would hold less data than today; "
                  "re-collect fully or pass --allow-shrink", file=sys.stderr)
            return 1
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_dir = apply_import(actions, staging, stamp)
    print(f"imported; replaced files saved under {archive_dir.relative_to(REPO)}")
    if args.no_build:
        return 0
    for command, cwd in rebuild_commands(actions, release):
        print(f"\n$ {' '.join(Path(c).name if i == 0 else c for i, c in enumerate(command))}")
        if subprocess.run(command, cwd=cwd, check=False).returncode != 0:
            print("ERROR: rebuild step failed; fix and re-run it (the import itself is complete)", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
