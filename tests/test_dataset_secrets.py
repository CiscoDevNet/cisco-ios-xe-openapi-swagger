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
    "restconf-live-data.json",
    "netconf-get-live-data.json",
    "netconf-getconfig-live-data.json",
    "netconf-sub-live-data.json",
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
