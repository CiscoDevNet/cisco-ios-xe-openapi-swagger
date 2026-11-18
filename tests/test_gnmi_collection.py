"""gNMI collector + dataset rules that silently skewed the published data before."""
import sys
from pathlib import Path

import pytest

COLLECTOR = Path(__file__).resolve().parents[1] / "scripts" / "mdt-telemetry" / "collector"
sys.path.insert(0, str(COLLECTOR))


def _response(value):
    return {"notification": [{"update": [{"path": "interfaces/interface/aggregation", "val": value}]}]}


def test_empty_update_value_is_not_data():
    gnmi_get = pytest.importorskip("gnmi_get", reason="needs pygnmi")
    assert not gnmi_get.response_has_data(_response({}))
    assert not gnmi_get.response_has_data(_response({"state": {}, "config": []}))
    assert not gnmi_get.response_has_data({"notification": [{"update": []}]})
    assert gnmi_get.response_has_data(_response({"state": {"lag-type": "LACP"}}))
    assert gnmi_get.response_has_data(_response(0))


def test_unsafe_roots_are_never_sent():
    gnmi_get = pytest.importorskip("gnmi_get", reason="needs pygnmi")
    assert "/notif-bis:streams" in gnmi_get.UNSAFE_PATHS


@pytest.mark.parametrize("body, expected", [
    ('<a xmlns="x"><b></b></a>', False),
    ('<a xmlns="x">\n  <b>\n  </b>\n</a>', False),
    ('<a xmlns="x"><b>7</b></a>', True),
    ('<a xmlns="x"><shutdown/></a>', True),
])
def test_netconf_empty_skeleton_is_not_data(body, expected):
    netconf_get = pytest.importorskip("netconf_get", reason="needs ncclient")
    assert netconf_get.xml_has_data(f"<rpc-reply><data>{body}</data></rpc-reply>") is expected


def test_data_rows_reference_one_file_per_path_across_devices(tmp_path, monkeypatch):
    import build_gnmi_dataset as builder

    monkeypatch.setattr(builder, "REPO_ROOT", tmp_path)
    files = builder.PayloadFiles("26.1.1")
    entry = {"xpath": "/oc-if:interfaces/interface/state/counters", "category": "openconfig",
             "module": "openconfig-interfaces", "gnmi_path": "openconfig:/interfaces/interface/state/counters",
             "depth": 4, "payload": '{"notification": [{"update": [{"val": {"in-octets": 1}}]}]}'}
    first = builder._index_entry({"pid": "C9500", "host": "h1"}, entry, "data", files, "get")
    second = builder._index_entry({"pid": "C9600", "host": "h2"}, entry, "data", files, "get")
    empty = builder._index_entry({"pid": "C9200", "host": "h3"}, {**entry, "payload": ""}, "empty", files, "get")
    files.write()

    assert first["file"] == second["file"] and first["file"].startswith("releases/26.1.1/gnmi-data/get/")
    assert "payload" not in first and empty["payload"] == "" and "file" not in empty
    doc = (tmp_path / first["file"]).read_text(encoding="utf-8")
    assert '"C9500"' in doc and '"C9600"' in doc and '"C9200"' not in doc


def test_state_equal_to_get_shares_the_get_file(tmp_path, monkeypatch):
    import build_gnmi_dataset as builder

    monkeypatch.setattr(builder, "REPO_ROOT", tmp_path)
    files = builder.PayloadFiles("26.1.1")
    base = {"xpath": "/oc-sys:system/state", "category": "openconfig", "module": "openconfig-system"}
    body = '{{"notification": [{{"timestamp": {ts}, "update": [{{"val": {{"hostname": "{host}"}}}}]}}]}}'
    device = {"pid": "C9500", "host": "h1"}
    get = builder._index_entry(device, {**base, "payload": body.format(ts=1, host="a")}, "data", files, "get")
    same = builder._index_entry(device, {**base, "payload": body.format(ts=2, host="a")}, "data", files, "state")
    drift = builder._index_entry(device, {**base, "payload": body.format(ts=3, host="b")}, "data", files, "getconfig")

    assert same["file"] == get["file"] and same["same_as"] == "gnmi-get"
    assert drift["file"] != get["file"] and "same_as" not in drift
