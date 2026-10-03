"""Offline safety tests for the gated CRUD write path (scripts/harness/crud.py).

No devices are contacted: every RESTCONF/SSH call is replaced by a fake.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.harness import crud  # noqa: E402
from scripts.harness.inventory import Device  # noqa: E402

SECRET_USER = "lab-user-xyz"
SECRET_PASS = "s3cr3t-Pa55-never-print"
AUTH = (SECRET_USER, SECRET_PASS)


def _get_result(status: int = 200, body=None):
    return SimpleNamespace(
        ok=200 <= status < 300, http_status=status, body=body,
        is_json=body is not None, error=None,
    )


@pytest.fixture
def lab(monkeypatch, tmp_path):
    """Fake device + recorder for every network-facing call crud.py can make."""
    calls: list[tuple] = []

    def fake_get(dev, path, auth, session):
        calls.append(("GET", path))
        if path == crud.GNMI_CONFIG_PATH:
            return _get_result(200, {"Cisco-IOS-XE-gnmi-cfg:config": {"enable": False}})
        return _get_result(200, {"stub": path})

    def fake_write(method, host, port, path, payload, auth, session, timeout=30):
        calls.append((method, path))
        return crud.WriteResult(ok=True, http_status=204, body=None, error=None,
                                elapsed_ms=1, url=path, method=method)

    def forbidden_ssh(*args, **kwargs):
        raise AssertionError("SSH must not be used in this test")

    monkeypatch.setattr(crud, "_get_json", fake_get)
    monkeypatch.setattr(crud, "restconf_write", fake_write)
    monkeypatch.setattr(crud, "tcp_open", lambda *a, **k: True)
    monkeypatch.setattr(crud, "gnmi_capabilities", lambda *a, **k: {"ok": True, "models": 1})
    # USE_CASES holds a direct reference captured at import time.
    monkeypatch.setitem(crud.USE_CASES["gnmi-enable"], "post_apply", lambda dev, auth: {"ok": True})
    monkeypatch.setattr(crud, "cli_send_config", forbidden_ssh)
    monkeypatch.setattr(crud, "cli_show", forbidden_ssh)
    monkeypatch.setattr(crud, "BACKUPS_DIR", tmp_path / "captures")
    monkeypatch.setattr(crud.time, "sleep", lambda *a, **k: None)
    device = Device(name="LAB1", host="192.0.2.10", writable=True)
    return SimpleNamespace(calls=calls, device=device, backups=tmp_path / "captures")


def _writes(calls):
    return [c for c in calls if c[0] != "GET"]


def test_restconf_write_rejects_get():
    with pytest.raises(ValueError):
        crud.restconf_write("GET", "192.0.2.10", 443, "/data/x", None, AUTH, session=None)


def test_dry_run_sends_no_writes_and_saves_backup(lab):
    assert crud.run_use_case(lab.device, AUTH, "gnmi-enable", apply=False) == 0
    assert _writes(lab.calls) == []
    backup_files = list(lab.backups.glob("LAB1/crud-backups/*/*.json"))
    assert any(f.name == "_manifest.json" for f in backup_files)


def test_apply_backs_up_before_writing(lab):
    crud.run_use_case(lab.device, AUTH, "gnmi-enable", apply=True)
    first_write = next(i for i, c in enumerate(lab.calls) if c[0] != "GET")
    backed_up = [c[1] for c in lab.calls[:first_write]]
    assert crud.GNMI_CONFIG_PATH in backed_up
    assert crud.NATIVE_ROOT_PATH in backed_up
    assert _writes(lab.calls) == [("PATCH", crud.GNMI_CONFIG_PATH)]


def test_credentials_never_printed(lab, capsys):
    crud.run_use_case(lab.device, AUTH, "gnmi-enable", apply=True)
    output = capsys.readouterr()
    for secret in AUTH:
        assert secret not in output.out
        assert secret not in output.err


def test_main_refuses_non_writable_device(monkeypatch, capsys):
    readonly = Device(name="RO1", host="192.0.2.11", writable=False)
    monkeypatch.setattr(crud.inv, "load_inventory", lambda path=None: [readonly])
    monkeypatch.setattr(crud.inv, "load_credentials", lambda: AUTH)

    def must_not_run(*args, **kwargs):
        raise AssertionError("no use case may run against a read-only device")

    monkeypatch.setattr(crud, "run_use_case", must_not_run)
    monkeypatch.setattr(crud, "run_mdt_enable", must_not_run)
    monkeypatch.setattr(crud, "run_rollback", must_not_run)
    assert crud.main(["--device", "RO1", "--use-case", "gnmi-enable", "--apply"]) == 3
    assert "REFUSED" in capsys.readouterr().err


def test_mdt_cli_rollback_removes_exactly_what_was_added():
    add, remove = crud.build_mdt_cli("192.0.2.200", 57500, crud.MDT_TEST_SUBS, source_vrf="Mgmt-vrf")
    added_ids = [line.split()[-1] for line in add if line.startswith("telemetry ietf subscription")]
    assert remove == [f"no telemetry ietf subscription {sid}" for sid in added_ids]
    assert add.count(" source-vrf Mgmt-vrf") == len(added_ids)


@pytest.mark.parametrize("body, expected_method", [(None, "DELETE"), ({"a": 1}, "PUT")])
def test_rollback_restores_or_removes(lab, tmp_path, body, expected_method):
    backup = tmp_path / "backup.json"
    backup.write_text(json.dumps({"path": crud.GNMI_CONFIG_PATH, "http_status": 200, "body": body}))
    assert crud.run_rollback(lab.device, AUTH, backup) == 0
    assert _writes(lab.calls) == [(expected_method, crud.GNMI_CONFIG_PATH)]
