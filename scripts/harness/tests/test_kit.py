"""Offline tests for the portable harness kit, its builder, and the bundle importer."""
from __future__ import annotations

import io
import json
import sys
import tarfile
from pathlib import Path

import pytest

from scripts import build_kit, import_harness_bundle as importer
from scripts.harness import kit
from scripts.harness.inventory import Device

DEVICE = Device(name="LAB-SW1", host="192.0.2.10", pid="C9300-48P")
SECRET_VALUE = "Hunter2-Lab-Pass"


# ---------------------------------------------------------------- kit helpers

def test_telegraf_config_points_at_absolute_output(tmp_path):
    config = kit.telegraf_config(57501, tmp_path / "mdt-live.json")
    assert 'service_address = ":57501"' in config
    assert json.dumps(str(tmp_path / "mdt-live.json")) in config
    assert "cisco_telemetry_mdt" in config


def test_split_mdt_routes_by_hostname_and_skips_unknown(tmp_path, monkeypatch):
    monkeypatch.setattr(kit.inv, "load_inventory", lambda: [DEVICE])
    live = tmp_path / "mdt-live.json"
    records = [{"tags": {"source": "lab-sw1-host", "path": "a:b", "subscription": "900001"}, "fields": {}},
               {"tags": {"source": "lab-sw1-host", "path": "a:c", "subscription": "900002"}, "fields": {}},
               {"tags": {"source": "lab-sw1-host", "path": "a:d", "subscription": "30002"}, "fields": {}},
               {"tags": {"source": "stranger", "path": "a:b", "subscription": "900001"}, "fields": {}}]
    live.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    counts = kit.split_mdt(live, tmp_path, facts={"C9300-48P": {"hostname": "lab-sw1-host"}})
    assert counts == {"C9300-48P": 2}
    assert len((tmp_path / "mdt-C9300-48P.json").read_text().splitlines()) == 2
    assert not list(tmp_path.glob("mdt-stranger*"))


def test_fleet_idle_counter_ignores_standing_subscriptions(tmp_path):
    from collect_fleet import count_lines

    live = tmp_path / "mdt-live.json"
    live.write_text('{"tags":{"subscription":"900004"}}\n{"tags":{"subscription":"30002"}}\n')
    assert count_lines(live) == 1


def test_score_module_prefers_best_state():
    assert kit.score_module({"a": "no", "b": "ok"}) == "empty"
    assert kit.score_module({"a": "no", "b": "data"}) == "data"
    assert kit.score_module({"a": "no"}) == "unsupported"
    assert kit.score_module({}) == "not-attempted"


def test_coverage_checklist_and_completeness(monkeypatch, tmp_path):
    monkeypatch.setattr(kit, "OUTPUT", tmp_path)
    for kind in kit.RAW_KINDS:
        (tmp_path / f"{kind}-{DEVICE.pid}.json").write_text("{}")
    facts = {"hostname": "h", "modules": ["mod-a", "mod-b", "mod-types"]}
    catalog = {"mod-a": "oper", "mod-b": "oper", "mod-unadvertised": "oper"}
    report = kit.coverage_for(DEVICE, facts, catalog, {"mod-a": {"restconf": "data"}}, {"mod-b": "ok"})
    assert report["checklist_modules"] == 2
    assert report["excluded_no_data_nodes"] == ["mod-types"]
    assert report["counts"] == {"data": 1, "empty": 1}
    assert report["complete"] is True

    partial = kit.coverage_for(DEVICE, facts, catalog, {"mod-a": {"restconf": "data"}}, {})
    assert partial["counts"]["not-attempted"] == 1
    assert partial["missing_methods"] == ["restconf-walk"]
    assert partial["complete"] is False


def test_redact_document_masks_payloads_and_mdt_fields():
    netconf = json.dumps({"pid": "X", "entries": [{"payload": "<user><password>abc</password></user>"}]})
    masked = kit.redact_document("scripts/mdt-telemetry/collector/output/netconf-X.json", netconf)
    assert "abc" not in masked and "***REDACTED***" in masked

    mdt = json.dumps({"tags": {"source": "h"}, "fields": {"secret": "abc", "name": "ok"}}) + "\n"
    masked = kit.redact_document("scripts/mdt-telemetry/collector/output/mdt-X.json", mdt)
    assert json.loads(masked)["fields"] == {"secret": "***REDACTED***", "name": "ok"}


# ---------------------------------------------------------------- bundle round trip

@pytest.fixture
def kit_tree(tmp_path, monkeypatch):
    """A fake kit layout with one device's results."""
    root = tmp_path / "kit"
    output = root / "scripts/mdt-telemetry/collector/output"
    captures = root / "scripts/harness/captures"
    output.mkdir(parents=True)
    (captures / DEVICE.name / "oper").mkdir(parents=True)
    for name, value in (("REPO", root), ("OUTPUT", output), ("CAPTURES", captures),
                        ("ONBOARD_OUT", root / "scripts/harness/onboard-output"), ("LOG_DIR", root / "logs"),
                        ("KIT_INFO", root / "KIT.json")):
        monkeypatch.setattr(kit, name, value)
    monkeypatch.setattr(kit, "literal_secrets", lambda: [SECRET_VALUE])
    (root / "KIT.json").write_text(json.dumps({"release": "26.1.1", "commit": "abc"}))
    (output / f"netconf-{DEVICE.pid}.json").write_text(json.dumps(
        {"pid": DEVICE.pid, "entries": [{"xpath": "/m:c", "status": "data", "payload": "<c>1</c>"}]}))
    (output / f"facts-{DEVICE.pid}.json").write_text(json.dumps(
        {"pid": DEVICE.pid, "hostname": "lab-sw1-host", "modules": []}))
    (output / f"mdt-{DEVICE.pid}.json").write_text(json.dumps(
        {"tags": {"source": "lab-sw1-host", "path": "m:c"}, "fields": {"x": 1}}) + "\n")
    (captures / DEVICE.name / "oper" / "m__0123.json").write_text(json.dumps(
        {"device": DEVICE.name, "pid": DEVICE.pid, "http_status": 200, "response": {"m:c": {"x": 1}}}))
    return root


def test_bundle_round_trip_verifies(kit_tree, tmp_path):
    bundle = tmp_path / "bundle.tar.gz"
    manifest = kit.build_bundle([DEVICE], bundle)
    assert manifest["release"] == "26.1.1"
    assert manifest["devices"][0]["hostname"] == "lab-sw1-host"
    staging = tmp_path / "staging"
    staging.mkdir()
    manifest, digests = importer.stage_bundle(bundle, staging)
    assert set(digests) == set(manifest["files"])
    assert importer.verify(manifest, digests, staging) == []


def test_bundle_refuses_literal_secret_and_leaves_nothing(kit_tree, tmp_path):
    log_dir = kit_tree / "logs"
    log_dir.mkdir()
    (log_dir / "netconf-X.log").write_text(f"connecting with {SECRET_VALUE}\n")
    bundle = tmp_path / "bundle.tar.gz"
    with pytest.raises(RuntimeError, match="secret scan failed"):
        kit.build_bundle([DEVICE], bundle)
    assert not bundle.exists()
    assert not list(tmp_path.glob("*.partial"))


def _write_bundle(path: Path, files: dict[str, bytes], manifest_files: dict | None = None) -> None:
    listed = manifest_files if manifest_files is not None else {
        name: {"sha256": kit.sha256_bytes(data), "bytes": len(data)} for name, data in files.items()}
    manifest = {"format": kit.BUNDLE_FORMAT, "release": "26.1.1", "devices": [], "files": listed}
    with tarfile.open(path, "w:gz") as archive:
        for name, data in list(files.items()) + [("manifest.json", json.dumps(manifest).encode())]:
            info = tarfile.TarInfo("harness-bundle/" + name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))


def _verify(tmp_path, files, manifest_files=None):
    bundle = tmp_path / "b.tar.gz"
    _write_bundle(bundle, files, manifest_files)
    staging = tmp_path / "staging"
    staging.mkdir(exist_ok=True)
    manifest, digests = importer.stage_bundle(bundle, staging)
    return importer.verify(manifest, digests, staging)


GOOD = "scripts/mdt-telemetry/collector/output/netconf-C9300-48P.json"


def test_verify_rejects_tampering_and_bad_paths(tmp_path):
    data = json.dumps({"pid": "C9300-48P", "entries": []}).encode()
    listed = {GOOD: {"sha256": "0" * 64, "bytes": len(data)}}
    assert any("checksum" in p for p in _verify(tmp_path, {GOOD: data}, listed))
    assert any("not allowed" in p for p in _verify(tmp_path, {"index.html": b"<html>"}))
    assert any("does not match" in p for p in _verify(tmp_path, {GOOD: json.dumps({"pid": "OTHER"}).encode()}))
    leaked = json.dumps({"pid": "C9300-48P", "entries": [{"payload": '{"password": "abc"}'}]}).encode()
    assert any("secret" in p for p in _verify(tmp_path, {GOOD: leaked}))


def test_stage_rejects_path_traversal(tmp_path):
    bundle = tmp_path / "evil.tar.gz"
    with tarfile.open(bundle, "w:gz") as archive:
        info = tarfile.TarInfo("harness-bundle/../../etc/passwd")
        info.size = 1
        archive.addfile(info, io.BytesIO(b"x"))
    with pytest.raises(importer.BundleError, match="unsafe path"):
        importer.stage_bundle(bundle, tmp_path / "staging")


def test_output_kind_disambiguates_sub_files():
    base = "scripts/mdt-telemetry/collector/output/"
    assert importer.output_kind(base + "netconf-sub-config-C9500.json") == ("netconf-sub-config", "C9500")
    assert importer.output_kind(base + "netconf-sub-C9500.json") == ("netconf-sub", "C9500")
    assert importer.output_kind(base + "gnmi-sub-C9300-24UX.json") == ("gnmi-sub", "C9300-24UX")
    assert importer.output_kind(base + "netconf-C9500.json") == ("netconf", "C9500")


@pytest.fixture
def fake_repo(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    output = repo / "scripts/mdt-telemetry/collector/output"
    output.mkdir(parents=True)
    monkeypatch.setattr(importer, "REPO", repo)
    monkeypatch.setattr(importer, "OUTPUT", output)
    monkeypatch.setattr(importer, "ARCHIVE_ROOT", repo / "scripts/harness/import-archive")
    monkeypatch.setattr(importer, "inventory_pids", lambda: ["C9300-48P"])
    return repo


def test_plan_flags_shrink_and_supersedes_legacy_mdt(fake_repo, tmp_path):
    output = fake_repo / "scripts/mdt-telemetry/collector/output"
    (output / "netconf-C9300-48P.json").write_text(json.dumps({"pid": "C9300-48P", "entries": [1, 2, 3]}))
    (output / "mdt-C9300.json").write_text("{}\n{}\n")
    staging = tmp_path / "staging"
    incoming = {GOOD: json.dumps({"pid": "C9300-48P", "entries": [1]}),
                "scripts/mdt-telemetry/collector/output/mdt-C9300-48P.json": "{}\n"}
    for name, text in incoming.items():
        (staging / name).parent.mkdir(parents=True, exist_ok=True)
        (staging / name).write_text(text)
    actions = importer.plan_import({name: {} for name in incoming}, staging)
    by_path = {a["path"]: a for a in actions}
    assert by_path[GOOD]["shrinks"] == "3 -> 1"
    assert by_path["scripts/mdt-telemetry/collector/output/mdt-C9300.json"]["action"] == "supersede"

    archive_dir = importer.apply_import(actions, staging, "T")
    assert (archive_dir / GOOD).exists() and (archive_dir / "scripts/mdt-telemetry/collector/output/mdt-C9300.json").exists()
    assert json.loads((fake_repo / GOOD).read_text())["entries"] == [1]
    assert not (output / "mdt-C9300.json").exists()


def test_rebuild_commands_follow_changed_kinds():
    actions = [{"action": "new", "path": "scripts/mdt-telemetry/collector/output/gnmi-sub-X.json"},
               {"action": "same", "path": "scripts/mdt-telemetry/collector/output/netconf-X.json"}]
    scripts = [Path(cmd[1]).name for cmd, _ in importer.rebuild_commands(actions, "26.1.1")]
    assert scripts == ["build_gnmi_dataset.py", "build_protocol_matrix.py"]


# ---------------------------------------------------------------- kit builder

def test_slim_spec_keeps_paths_and_methods_only():
    spec = {"openapi": "3.0.0", "info": {"title": "t"}, "components": {"schemas": {"big": {}}},
            "paths": {"/data/m:c": {"get": {"responses": {}}, "parameters": [], "put": {}}}}
    slim = build_kit.slim_spec(spec)
    assert slim == {"openapi": "3.0.0", "info": {"title": "t"}, "paths": {"/data/m:c": {"get": {}, "put": {}}}}


def test_copy_code_excludes_private_files(tmp_path):
    build_kit.copy_code(tmp_path)
    harness = tmp_path / "scripts/harness"
    assert (harness / "kit.py").exists() and (harness / "inventory.example.json").exists()
    assert (tmp_path / "scripts/mdt-telemetry/collector/collect_fleet.py").exists()
    for private in ("inventory.json", ".env", "secrets.json", "captures", "tests", "onboard-output"):
        assert not (harness / private).exists()


def test_install_telegraf_rejects_bad_checksum(tmp_path):
    tarball = tmp_path / "telegraf.tar.gz"
    tarball.write_bytes(b"not telegraf")
    with pytest.raises(SystemExit, match="checksum mismatch"):
        build_kit.install_telegraf(tmp_path / "kit", tarball)


def test_kit_main_routes_onboard_flags(monkeypatch):
    seen = {}
    from scripts.harness import onboard

    monkeypatch.setattr(onboard, "main", lambda argv: seen.setdefault("argv", argv) and 0)
    kit.main(["onboard", "--device", "C9500", "--apply"])
    assert seen["argv"] == ["--device", "C9500", "--apply"]


def test_collect_commands_use_device_name(monkeypatch):
    import argparse

    args = argparse.Namespace(limit=3, release="26.1.1", receiver_port=57500, walk_roots_only=True)
    sub_config = kit.method_command("netconf-sub-config", DEVICE, args, "198.51.100.1")
    assert sub_config[1].endswith("netconf_subscribe.py")
    assert sub_config[2:] == ["--device", DEVICE.name, "--config-roots", "--both", "--limit", "3"]
    mdt = kit.method_command("mdt", DEVICE, args, "198.51.100.1")
    assert "--apply" in mdt and mdt[mdt.index("--receiver-ip") + 1] == "198.51.100.1"
    assert mdt[mdt.index("--per-cat-cap") + 1] == "3"
    walk = kit.method_command("restconf-walk", DEVICE, args, None)
    assert walk[0] == sys.executable and "--roots-only" in walk
