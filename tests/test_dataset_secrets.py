"""Guard: repo-root Device Data datasets must not embed unmasked secrets.

The harness secret gate scans releases/*/live-data, but the collector-built
repo-root *-live-data.json datasets — which embed device payloads inline
(NETCONF XML, gNMI json_ietf) — plus protocol-matrix.json were previously
unguarded. A rebuild that skipped redaction could re-leak a community string /
password / PSK there. This test closes that gap using the same payload-aware
scanner the builders redact with (redact_payload.scan_text).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "mdt-telemetry" / "collector"))

from redact_payload import scan_text  # noqa: E402

DATASETS = [
    "telemetry-live-data.json",
    "restconf-live-data.json",
    "netconf-get-live-data.json",
    "netconf-getconfig-live-data.json",
    "netconf-sub-live-data.json",
    "netconf-sub-config-live-data.json",
    "gnmi-get-live-data.json",
    "gnmi-getconfig-live-data.json",
    "gnmi-state-live-data.json",
    "gnmi-sub-live-data.json",
    "protocol-matrix.json",
]


def test_repo_root_datasets_have_no_unmasked_secrets():
    problems = []
    for name in DATASETS:
        f = REPO / name
        if not f.exists():
            continue
        hits = scan_text(f.read_text(encoding="utf-8"))
        if hits:
            problems.append((name, hits[:5]))
    assert not problems, f"unmasked secrets found in repo-root datasets: {problems}"


def test_release_live_data_has_no_unmasked_secrets():
    """Per-path device bodies under releases/*/live-data, including SNMP communities in CLI text."""
    problems = []
    for f in sorted(REPO.glob("releases/*/live-data/*/*/*.json")):
        hits = scan_text(f.read_text(encoding="utf-8"))
        if hits:
            problems.append((f.relative_to(REPO).as_posix(), hits[:2]))
    assert not problems, f"{len(problems)} live-data file(s) with unmasked secrets: {problems[:5]}"


def test_release_gnmi_data_has_no_unmasked_secrets():
    """Full gNMI response bodies under releases/*/gnmi-data (build_gnmi_dataset.py)."""
    problems = []
    for f in sorted(REPO.glob("releases/*/gnmi-data/*/*.json")):
        hits = scan_text(f.read_text(encoding="utf-8"))
        if hits:
            problems.append((f.relative_to(REPO).as_posix(), hits[:2]))
    assert not problems, f"{len(problems)} gnmi-data file(s) with unmasked secrets: {problems[:5]}"


def test_gnmi_dataset_file_refs_exist():
    """Every gNMI dataset row with data points at a published payload file."""
    import json

    missing = []
    for name in ("gnmi-get-live-data.json", "gnmi-getconfig-live-data.json",
                 "gnmi-state-live-data.json", "gnmi-sub-live-data.json"):
        f = REPO / name
        if not f.exists():
            continue
        for row in json.loads(f.read_text(encoding="utf-8")).get("paths", []):
            if row.get("status") == "data" and not (REPO / row.get("file", "")).is_file():
                missing.append((name, row.get("pid"), row.get("path")))
    assert not missing, f"{len(missing)} gNMI rows without a payload file: {missing[:5]}"


def test_published_device_data_is_fully_scrubbed():
    """Every file scripts/scrub_published_data.py covers is already scrubbed (it would change nothing)."""
    sys.path.insert(0, str(REPO / "scripts"))
    import scrub_published_data as scrub  # noqa: E402

    dirty = [f.relative_to(REPO).as_posix() for f in scrub.published_files() if scrub.scrub(f, check=True)]
    assert not dirty, f"run python scripts/scrub_published_data.py: {dirty[:10]}"
