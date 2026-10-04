#!/usr/bin/env python3
"""
build_kit.py — package the portable IOS XE data-collection harness.

Produces dist/iosxe-harness-kit-<release>/ (+ .tar.gz): the harness and collector
code with the repo's relative layout, slim release specs (paths + methods only),
the root catalogs, an offline wheelhouse, and a checksum-verified Telegraf binary.
On the isolated host: ./setup.sh, then ./harness doctor | onboard | collect | bundle.
Bring the bundle back and run scripts/import_harness_bundle.py.

    .venv-harness/bin/python scripts/build_kit.py --release 26.1.1
    .venv-harness/bin/python scripts/build_kit.py --release 26.1.1 --telegraf-tarball /tmp/telegraf.tgz \\
        --python-version 3.11            # wheels for a different target interpreter
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARNESS = REPO / "scripts" / "harness"
COLLECTOR = REPO / "scripts" / "mdt-telemetry" / "collector"
CATALOG_FILES = ("subscribable-nodes.json", "mib-nodes.json")

REQUIREMENTS = ["requests==2.34.2", "ncclient==0.7.1", "netmiko==4.7.0", "pygnmi==0.8.15", "PyYAML==6.0.3"]
TELEGRAF_VERSION = "1.40.1"
TELEGRAF_URL = f"https://dl.influxdata.com/telegraf/releases/telegraf-{TELEGRAF_VERSION}_linux_amd64.tar.gz"
TELEGRAF_SHA256 = "3a6cfa0ab1b08a31687d80b3813304706280dba789348b5dad539bdbe0a72d52"
TELEGRAF_MEMBER = f"telegraf-{TELEGRAF_VERSION}/usr/bin/telegraf"
HTTP_METHODS = {"get", "put", "post", "patch", "delete"}

SETUP_SH = """#!/bin/sh
# Create the harness virtualenv from the bundled wheels (no internet needed).
set -eu
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
"$PYTHON" -m venv .venv
.venv/bin/pip install --no-index --find-links wheels -r requirements.txt -c constraints.txt
echo "Ready. Next: create scripts/harness/inventory.json and scripts/harness/.env, then ./harness doctor"
"""

LAUNCHER = """#!/bin/sh
HERE="$(cd "$(dirname "$0")" && pwd)"
exec "$HERE/.venv/bin/python" "$HERE/scripts/harness/kit.py" "$@"
"""

README = """# IOS XE data-collection harness kit (release {release})

Collects RESTCONF, NETCONF (get, get-config, subscribe), gNMI (Get, Subscribe), MDT
(Telegraf dial-out), and the RESTCONF spec walk from Cisco IOS XE devices, then packs
the results into a bundle for the webapp's `scripts/import_harness_bundle.py`.

Built {built} from commit {commit}. Wheels target Python {python}; Telegraf {telegraf} (linux amd64).

## 1. Verify and install (offline)

    sha256sum -c SHA256SUMS
    ./setup.sh                       # PYTHON=python3.12 ./setup.sh to pick the interpreter

## 2. Describe the devices

    cp scripts/harness/inventory.example.json scripts/harness/inventory.json   # name, host, pid
    printf 'IOSXE_USER=...\\nIOSXE_PASS=...\\n' > scripts/harness/.env && chmod 600 scripts/harness/.env

`pid` names the device's files (for example C9300-48P). The account needs privilege 15.

## 3. Prepare the devices

    ./harness doctor
    ./harness onboard --all                          # plan only: shows what is missing
    ./harness onboard --all --apply                  # enable AAA (only if none), HTTPS, RESTCONF, NETCONF, gNMI
    ./harness onboard --all --apply --snmp-community <ro-community>   # also the SNMP MIB bridge

Onboarding backs up the running-config first (scripts/harness/onboard-output/, keep private),
never touches existing AAA, verifies a fresh login after enabling AAA, and does not
`write memory` unless you add `--save`.

## 4. Collect

    ./harness telegraf start                         # MDT receiver on :57500 (devices must reach this host)
    ./harness collect --device <name> --limit 5      # smoke test first
    ./harness collect                                # everything, all devices
    ./harness coverage                               # COMPLETE / INCOMPLETE per device
    ./harness telegraf stop

MDT subscriptions are added in small CPU-gated batches and removed after each batch.
Re-run `collect --device X --methods <method>` to fill any gap coverage reports.

## 5. Bundle and bring back

    ./harness bundle                                 # dist/harness-bundle-<UTC>.tar.gz

The bundle masks secret values, refuses to build if any secret remains, and lists a
sha256 for every file. Copy it to the webapp repo and run:

    python scripts/import_harness_bundle.py <bundle>            # verify + show the plan
    python scripts/import_harness_bundle.py <bundle> --apply    # import + rebuild datasets
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def slim_spec(document: dict) -> dict:
    """Keep only what the collectors read: each path and its HTTP method names."""
    paths = {}
    for path, operations in (document.get("paths") or {}).items():
        methods = operations if isinstance(operations, dict) else {}
        paths[path] = {method: {} for method in methods if method.lower() in HTTP_METHODS}
    return {"openapi": document.get("openapi"), "info": document.get("info", {}), "paths": paths}


def copy_code(kit: Path) -> None:
    for source_dir, patterns in ((HARNESS, ("*.py", "inventory.example.json")), (COLLECTOR, ("*.py",))):
        target_dir = kit / source_dir.relative_to(REPO)
        target_dir.mkdir(parents=True, exist_ok=True)
        for pattern in patterns:
            for source in sorted(source_dir.glob(pattern)):
                shutil.copy2(source, target_dir / source.name)
    shutil.copy2(REPO / "scripts" / "_release_paths.py", kit / "scripts" / "_release_paths.py")


def write_release_index(kit: Path, release: str) -> None:
    """A one-release index so the shared release helpers resolve to the kit's release."""
    index = {"default": release, "device_data": release, "releases": [{"ver": release, "status": "active"}]}
    (kit / "releases" / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")


def copy_catalogs(kit: Path, release: str) -> None:
    target = kit / COLLECTOR.relative_to(REPO) / "output"
    target.mkdir(parents=True, exist_ok=True)
    for name in CATALOG_FILES:
        source = COLLECTOR / "output" / name
        version = json.loads(source.read_text(encoding="utf-8")).get("version")
        if version != release:
            raise SystemExit(f"{source.name} is for {version}, not {release}; regenerate it first "
                             f"(count_subscribable.py --version {release} --dump / mib_catalog.py)")
        shutil.copy2(source, target / name)
    shutil.copy2(REPO / "yang-prefix-map.json", kit / "yang-prefix-map.json")


def copy_specs(kit: Path, release: str) -> int:
    source_root = REPO / "releases" / release
    if not source_root.is_dir():
        raise SystemExit(f"release not found: {source_root}")
    count = 0
    for api_dir in sorted(source_root.glob("swagger-*-model/api")):
        target_dir = kit / api_dir.relative_to(REPO)
        target_dir.mkdir(parents=True, exist_ok=True)
        for spec in sorted(api_dir.glob("*.json")):
            if spec.name.startswith("_"):
                continue  # webapp search index; collectors never read it
            if spec.name == "manifest.json":
                shutil.copy2(spec, target_dir / spec.name)
                continue
            document = json.loads(spec.read_text(encoding="utf-8"))
            (target_dir / spec.name).write_text(json.dumps(slim_spec(document), separators=(",", ":")),
                                                encoding="utf-8")
            count += 1
    release_prefix_map = source_root / "yang-prefix-map.json"
    if release_prefix_map.exists():
        shutil.copy2(release_prefix_map, kit / release_prefix_map.relative_to(REPO))
    return count


def download_wheels(kit: Path, python_version: str | None, platform: str | None) -> None:
    """Pin the whole dependency closure to this (tested) environment's versions."""
    wheels = kit / "wheels"
    frozen = subprocess.run([sys.executable, "-m", "pip", "freeze", "--exclude-editable"], capture_output=True,
                            text=True, check=True).stdout
    constraints = kit / "constraints.txt"
    constraints.write_text("".join(line + "\n" for line in frozen.splitlines() if "==" in line), encoding="utf-8")
    command = [sys.executable, "-m", "pip", "download", "--dest", str(wheels), "-c", str(constraints),
               *REQUIREMENTS]
    if python_version or platform:
        command += ["--only-binary=:all:"]
        command += ["--python-version", python_version] if python_version else []
        command += ["--platform", platform] if platform else []
    subprocess.run(command, check=True)


def install_telegraf(kit: Path, tarball: Path | None) -> None:
    if tarball is None:
        tarball = kit.parent / f"telegraf-{TELEGRAF_VERSION}.tar.gz"
        if not tarball.exists():
            print(f"downloading {TELEGRAF_URL}")
            urllib.request.urlretrieve(TELEGRAF_URL, tarball)  # noqa: S310 - fixed https URL, checksum below
    actual = sha256_file(tarball)
    if actual != TELEGRAF_SHA256:
        raise SystemExit(f"Telegraf checksum mismatch: {actual} != {TELEGRAF_SHA256}")
    target = kit / "bin" / "telegraf"
    target.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tarball, "r:gz") as archive:
        member = archive.getmember(TELEGRAF_MEMBER)
        with archive.extractfile(member) as source, open(target, "wb") as destination:
            shutil.copyfileobj(source, destination)
    target.chmod(0o755)


def git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True,
                            check=False)
    return result.stdout.strip() or "unknown"


def write_launchers(kit: Path, info: dict) -> None:
    (kit / "requirements.txt").write_text("\n".join(REQUIREMENTS) + "\n", encoding="utf-8")
    for name, content in (("setup.sh", SETUP_SH), ("harness", LAUNCHER)):
        (kit / name).write_text(content, encoding="utf-8")
        (kit / name).chmod(0o755)
    (kit / "README.md").write_text(README.format(**info), encoding="utf-8")
    (kit / "KIT.json").write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")


def write_checksums(kit: Path) -> None:
    lines = [f"{sha256_file(path)}  {path.relative_to(kit).as_posix()}"
             for path in sorted(kit.rglob("*")) if path.is_file() and path.name != "SHA256SUMS"]
    (kit / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(args) -> Path:
    kit = Path(args.out).resolve() / f"iosxe-harness-kit-{args.release}"
    if kit.exists():
        shutil.rmtree(kit)
    kit.mkdir(parents=True)
    copy_code(kit)
    copy_catalogs(kit, args.release)
    spec_count = copy_specs(kit, args.release)
    write_release_index(kit, args.release)
    print(f"specs: {spec_count} slim spec files")
    if not args.no_wheels:
        download_wheels(kit, args.python_version, args.platform)
    if not args.no_telegraf:
        install_telegraf(kit, Path(args.telegraf_tarball) if args.telegraf_tarball else None)
    info = {
        "release": args.release, "built": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": git_commit(), "python": args.python_version or f"{sys.version_info.major}.{sys.version_info.minor}",
        "telegraf": TELEGRAF_VERSION if not args.no_telegraf else "not bundled",
    }
    write_launchers(kit, info)
    write_checksums(kit)
    return kit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--release", help="Release the devices run (default: releases/index.json device_data)")
    parser.add_argument("--out", default=str(REPO / "dist"))
    parser.add_argument("--telegraf-tarball", help=f"Local telegraf-{TELEGRAF_VERSION}_linux_amd64.tar.gz")
    parser.add_argument("--python-version", help="Target interpreter for wheels, e.g. 3.11 (default: this one)")
    parser.add_argument("--platform", help="Target wheel platform, e.g. manylinux2014_x86_64")
    parser.add_argument("--no-wheels", action="store_true")
    parser.add_argument("--no-telegraf", action="store_true")
    parser.add_argument("--no-archive", action="store_true")
    args = parser.parse_args()
    if not args.release:
        sys.path.insert(0, str(REPO / "scripts"))
        from _release_paths import device_data_release

        args.release = device_data_release()

    kit = build(args)
    size = sum(p.stat().st_size for p in kit.rglob("*") if p.is_file())
    print(f"kit: {kit} ({size / 1e6:.1f} MB)")
    if not args.no_archive:
        archive = kit.with_name(kit.name + ".tar.gz")
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(kit, arcname=kit.name)
        print(f"archive: {archive} ({archive.stat().st_size / 1e6:.1f} MB) sha256 {sha256_file(archive)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
