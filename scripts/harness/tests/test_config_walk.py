"""Offline tests for the config-driven MDT walk: running-config capture, CLI masking, pruning, match."""
from __future__ import annotations

import json

from scripts import import_harness_bundle as importer
from scripts.harness import kit

import config_get  # noqa: E402  (collector dir is on sys.path via kit)
import prune_walk_catalog as prune  # noqa: E402
from redact_payload import REDACTED, mask_cli, scan_text  # noqa: E402

FAKE = "Hunter2-Lab-Pass"
SHOW_RUN = f"""Building configuration...
hostname lab-sw1
enable secret 9 $9${FAKE}
username admin privilege 15 password 0 {FAKE}
snmp-server community {FAKE} RO
netconf-yang cisco-ia snmp-community-string {FAKE}
key chain K1
 key 1
  key-string 7 {FAKE}
interface GigabitEthernet1/0/1
 ip ospf message-digest-key 1 md5 {FAKE}
-----BEGIN CERTIFICATE-----
{FAKE}
-----END CERTIFICATE-----
end
"""
RESTCONF_JSON = "show running-config | format restconf-json\n" + json.dumps({"data": {
    "Cisco-IOS-XE-native:native": {"hostname": "lab-sw1", "enable": {"secret": {"secret": FAKE}},
                                   "interface": {"GigabitEthernet": [{"name": "1/0/1"}]}},
    "Cisco-IOS-XE-wireless-wlan-cfg:wlan-cfg-data": {"wlan-cfg-entries": {"wlan-cfg-entry": [{"profile-name": "x"}]}},
}})


def test_mask_cli_masks_every_secret_form_and_keeps_structure():
    masked = mask_cli(SHOW_RUN)
    assert FAKE not in masked
    assert "hostname lab-sw1" in masked
    assert f"snmp-server community {REDACTED} RO" in masked
    assert len(masked.splitlines()) == len(SHOW_RUN.splitlines()) - 2  # PEM block collapses to one line


def test_build_record_has_no_secrets():
    record = config_get.build_record({"pid": "C9300-48P", "name": "LAB-SW1"}, SHOW_RUN, RESTCONF_JSON)
    text = json.dumps(record)
    assert FAKE not in text and not scan_text(text)
    assert record["models"] == ["Cisco-IOS-XE-native:native", "Cisco-IOS-XE-wireless-wlan-cfg:wlan-cfg-data"]
    assert "hostname lab-sw1" in record["sections"] and "interface GigabitEthernet1/0/1" in record["sections"]
    assert "key 1" not in record["sections"]  # indented lines are not top-level sections


def test_configured_matches_every_segment_ignoring_prefixes():
    tree = {"native": {"interface": {"GigabitEthernet": [{"name": "1/0/1", "ip": {"address": {}}}]}}}
    assert prune.configured(tree, "/ios:native/interface/GigabitEthernet")
    assert prune.configured(tree, "/ios:native/interface/GigabitEthernet/ios:ip/address")
    assert not prune.configured(tree, "/ios:native/router/bgp")
    assert not prune.configured(tree, "/ios:native/interface/Vlan")


def test_keep_prefers_configured_then_fleet_streamed(tmp_path, monkeypatch):
    monkeypatch.setattr(prune, "OUT", tmp_path)
    (tmp_path / "config-WLC.json").write_text(json.dumps({"restconf_json": {
        "Cisco-IOS-XE-wireless-wlan-cfg:wlan-cfg-data": {"wlan-cfg-entries": {}}}}))
    (tmp_path / "walk-SW1-cfg.json").write_text(json.dumps({"results": {
        "/wlan:wlan-cfg-data/wlan-cfg-entries": {"status": "invalid"},  # switch lacks the model
        "/x:other-cfg-data": {"status": "streamed"},
        "/y:dead-cfg-data": {"status": "invalid"}}}))
    nodes = [{"xpath": x, "module": "m", "category": "cfg"}
             for x in ("/wlan:wlan-cfg-data/wlan-cfg-entries", "/x:other-cfg-data", "/y:dead-cfg-data")]
    kept = [n["xpath"] for n in prune.keep("cfg", "WLC", nodes, set())]
    assert kept == ["/wlan:wlan-cfg-data/wlan-cfg-entries", "/x:other-cfg-data"]


def test_fleet_history_is_compact_and_read_back(tmp_path, monkeypatch):
    monkeypatch.setattr(prune, "OUT", tmp_path)
    (tmp_path / "walk-SW1-oper.json").write_text(json.dumps({"results": {
        "/a:a": {"status": "streamed", "records": 3, "ts": "t"}, "/b:b": {"status": "silent"}}}))
    history = prune.fleet_history("oper")
    assert history["devices"] == {"SW1": {"/a:a": {"status": "streamed"}}}
    (tmp_path / "walk-SW1-oper.json").unlink()
    (tmp_path / "fleet-walk-oper.json").write_text(json.dumps(history))
    assert prune.fleet_results("oper", set()) == [{"/a:a": {"status": "streamed"}}]
    assert prune.fleet_results("oper", {"SW1"}) == []


def test_config_match_counts_invalid_as_resolved_and_retry_wins():
    configured = ["/a", "/b", "/c", "/d", "/e"]
    results = {"/a": {"status": "streamed"}, "/b": {"status": "invalid"}, "/c": {"status": "silent"},
               "/d": {"status": "silent"}}
    match = kit.config_match(configured, results, {"/c": {"status": "streamed"}})
    assert match["streamed"] == ["/a", "/c"] and match["invalid"] == ["/b"]
    assert match["silent"] == ["/d"] and match["unresolved"] == ["/e"]
    assert (match["resolved"], match["matched_pct"]) == (3, 60.0)


def test_redact_document_masks_config_capture():
    document = json.dumps({"pid": "X", "show_run": f"enable secret 9 {FAKE}\n",
                           "restconf_json": {"native": {"enable": {"password": FAKE}}}})
    masked = kit.redact_document("scripts/mdt-telemetry/collector/output/config-X.json", document)
    assert FAKE not in masked


def test_importer_accepts_config_files():
    assert importer.output_kind("scripts/mdt-telemetry/collector/output/config-C9300-48P.json") == (
        "config", "C9300-48P")
    assert "config" in kit.METHODS and kit.METHODS[0] == "config"


def test_split_mdt_merges_without_losing_earlier_records(tmp_path, monkeypatch):
    monkeypatch.setattr(kit.inv, "load_inventory", lambda: [])
    earlier = json.dumps({"tags": {"source": "sw1", "path": "deep:walk", "subscription": "900001"}})
    target = tmp_path / "mdt-PID1.json"
    target.write_text(earlier + "\n", encoding="utf-8")
    fresh = json.dumps({"tags": {"source": "sw1", "path": "a:b", "subscription": "900002"}})
    live = tmp_path / "mdt-live.json"
    live.write_text(f"{fresh}\n{fresh}\n", encoding="utf-8")
    for _ in range(2):
        kit.split_mdt(live, tmp_path, facts={"PID1": {"hostname": "sw1"}})
    assert target.read_text(encoding="utf-8").splitlines() == [earlier, fresh]
