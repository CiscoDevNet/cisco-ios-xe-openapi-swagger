"""Offline unit tests for the Track B GET harness.

No devices, no live specs required. Run:
    python -X utf8 -m pytest scripts/harness/tests/ -v
or:
    python -X utf8 scripts/harness/tests/test_harness.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.harness import redact, secret_scan, spec_paths  # noqa: E402
from scripts.harness.build_capture_index import build_index, _flatten  # noqa: E402
from scripts.harness.find_value import coverage_matrix, search_keyword, search_value  # noqa: E402
from scripts.harness.request import (  # noqa: E402
    WriteAttemptError,
    assert_get_only,
    build_restconf_url,
    restconf_get,
)


# --- Safety core: GET-only guard --------------------------------------------

@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "", None, "GETX", "POST GET"])
def test_assert_get_only_refuses_non_get(method):
    with pytest.raises(WriteAttemptError):
        assert_get_only(method)


@pytest.mark.parametrize("method", ["GET", "get", "Get", "get ", " GET"])
def test_assert_get_only_allows_get(method):
    assert_get_only(method)  # whitespace is stripped; still GET, must not raise


def test_restconf_get_refuses_non_get_before_network():
    # _method other than GET must raise before any socket is opened.
    with pytest.raises(WriteAttemptError):
        restconf_get("10.0.0.1", 443, "/data/x", ("u", "p"), _method="POST")


def test_build_restconf_url():
    url = build_restconf_url("dev.example.com", 443, "/data/Cisco-IOS-XE-native:native/hostname")
    assert url == "https://dev.example.com:443/restconf/data/Cisco-IOS-XE-native:native/hostname"
    # spaces in list-key placeholders get encoded
    url2 = build_restconf_url("h", 830, "/data/x:y/location={fru slot bay}")
    assert " " not in url2


# --- Spec enumeration --------------------------------------------------------

def _write_spec(api_dir: Path, module: str, paths: dict) -> None:
    api_dir.mkdir(parents=True, exist_ok=True)
    (api_dir / f"{module}.json").write_text(
        json.dumps({"openapi": "3.0.0", "paths": paths}), encoding="utf-8"
    )


def test_enumerate_skips_keyed_and_non_get(tmp_path):
    api = tmp_path / "swagger-oper-model" / "api"
    _write_spec(
        api,
        "Cisco-IOS-XE-demo-oper",
        {
            "/data/Cisco-IOS-XE-demo-oper:demo": {"get": {}},
            "/data/Cisco-IOS-XE-demo-oper:demo/item={id}": {"get": {}},  # keyed -> skip
            "/data/Cisco-IOS-XE-demo-oper:demo/writeonly": {"post": {}},  # no get -> skip
        },
    )
    (api / "manifest.json").write_text(json.dumps(["Cisco-IOS-XE-demo-oper"]), encoding="utf-8")

    paths = spec_paths.enumerate_category(tmp_path, "oper")
    got = {p.path for p in paths}
    assert got == {"/data/Cisco-IOS-XE-demo-oper:demo"}


def test_enumerate_roots_only(tmp_path):
    api = tmp_path / "swagger-oper-model" / "api"
    _write_spec(
        api,
        "m",
        {
            "/data/m:root": {"get": {}},
            "/data/m:root/child/grandchild": {"get": {}},
        },
    )
    paths = spec_paths.enumerate_category(tmp_path, "oper", roots_only=True)
    assert [p.path for p in paths] == ["/data/m:root"]


def test_enumerate_mib_uses_module_name_path(tmp_path):
    # IOS XE serves MIBs at /data/<module-name>, not /data/<MIB>:<table>.
    api = tmp_path / "swagger-mib-model" / "api"
    _write_spec(api, "IF-MIB", {"/data/IF-MIB:ifTable": {"get": {}}})
    _write_spec(api, "ENTITY-MIB", {"/data/ENTITY-MIB:entPhysicalTable": {"get": {}}})
    (api / "manifest.json").write_text(json.dumps(["IF-MIB", "ENTITY-MIB"]), encoding="utf-8")
    got = {(p.module, p.path) for p in spec_paths.enumerate_category(tmp_path, "mib")}
    assert got == {("IF-MIB", "/data/IF-MIB"), ("ENTITY-MIB", "/data/ENTITY-MIB")}


# --- Redaction + secret scan -------------------------------------------------

def test_redaction_masks_secrets_keeps_lab_ids():
    payload = {
        "hostname": "sw1",
        "mgmt-ip": "10.1.1.1",
        "mac": "00:11:22:33:44:55",
        "password": "***REDACTED***",
        "snmp": {"community": "public"},
        "cert": "-----BEGIN CERTIFICATE-----abc-----END CERTIFICATE-----",
    }
    out = redact.redact(payload)
    assert out["hostname"] == "sw1"          # kept
    assert out["mgmt-ip"] == "10.1.1.1"      # kept
    assert out["mac"] == "00:11:22:33:44:55" # kept
    assert out["password"] == redact.REDACTED
    assert out["snmp"]["community"] == redact.REDACTED
    assert redact.REDACTED in out["cert"]


def test_secret_scan_flags_and_clears():
    dirty = json.dumps({"password": "hunter2"})
    assert secret_scan.find_secrets(dirty)
    clean = json.dumps(redact.redact({"password": "hunter2"}))
    assert not secret_scan.find_secrets(clean)


def test_no_secrets_in_committed_json_artifacts():
    # The guard's intent (DEVICE_DATA_COLLECTION.md §6) is to scan committed *data*
    # (scrubbed captures + example files), not the scanner/redactor source which
    # legitimately contains the secret regex literals. Scan only JSON artifacts
    # that could be committed; gitignored inventory.json/secrets are excluded.
    harness_dir = REPO_ROOT / "scripts" / "harness"
    for path in harness_dir.rglob("*.json"):
        rel = path.relative_to(harness_dir).as_posix()
        if rel.startswith("captures/") or rel == "inventory.json" or rel.startswith("secrets"):
            continue
        hits = secret_scan.scan_file(path)
        assert not hits, f"secret-like content in {rel}: {hits}"


# --- Index + find_value (canonical 633024 case) ------------------------------

def _fake_capture(tmp: Path, device: str, pid: str, response: dict) -> None:
    module = "Cisco-IOS-XE-switch-dp-punt-inject-oper"
    d = tmp / device / "oper"
    d.mkdir(parents=True, exist_ok=True)
    record = {
        "device": device, "pid": pid, "host": "10.0.0.9",
        "module": module, "category": "oper",
        "path": "/data/.../punt-inject-cpuq-brief-stats",
        "restconf_url": "https://h:443/restconf/data/...",
        "http_status": 200, "fetched_at": "2026-07-29T00:00:00Z",
        "os_version": "26.1.1", "error": None, "response": response,
    }
    (d / f"{module}__abc123.json").write_text(json.dumps(record), encoding="utf-8")


def test_flatten():
    rows = dict(_flatten({"a": {"b": [1, 2]}, "c": "x"}, ""))
    assert rows["a/b[0]"] == 1
    assert rows["a/b[1]"] == 2
    assert rows["c"] == "x"


def test_index_and_find_value_633024(tmp_path):
    resp = {
        "punt-inject-cpuq-brief-stats": [
            {"cpuq-id": 12, "cpu-punt-queue-name": "L2 Control", "policer-drop": "633024"},
            {"cpuq-id": 13, "cpu-punt-queue-name": "DOT1X Auth", "policer-drop": "0"},
        ]
    }
    _fake_capture(tmp_path, "sw1", "C9300-48T", resp)
    index = build_index(tmp_path)
    assert index["capture_files"] == 1
    assert index["row_count"] >= 6

    hits = search_value(index, "633024", exact=True)
    assert len(hits) == 1
    assert hits[0]["pid"] == "C9300-48T"
    assert "policer-drop" in hits[0]["leaf_xpath"]

    kw = search_keyword(index, "l2-control")
    assert not kw  # hyphen form not literally present
    kw2 = search_keyword(index, "cpu-punt-queue-name")
    assert any(r["value"] == "L2 Control" for r in kw2)

    matrix = coverage_matrix(index)
    assert "C9300-48T" in matrix["pids"]


# --- report.py (offline raw-capture browser) ---------------------------------

from scripts.harness import report as report_mod  # noqa: E402
from scripts.harness import build_observed_examples as overlay_mod  # noqa: E402
from scripts.harness.collector import CircuitBreaker  # noqa: E402


def test_circuit_breaker_trips_on_consecutive_errors():
    cb = CircuitBreaker(threshold=3)
    assert cb.register("error") is False
    assert cb.register("error") is False
    assert cb.register("error") is True   # 3rd consecutive -> trip
    assert cb.tripped is True


def test_circuit_breaker_resets_on_healthy_response():
    cb = CircuitBreaker(threshold=3)
    cb.register("error")
    cb.register("error")
    cb.register("404")                     # healthy (device answered) -> reset
    assert cb.consecutive == 0
    assert cb.register("error") is False
    assert cb.tripped is False


def test_circuit_breaker_disabled_when_threshold_zero():
    cb = CircuitBreaker(threshold=0)
    for _ in range(50):
        assert cb.register("error") is False
    assert cb.tripped is False


def test_circuit_breaker_trips_immediately_on_reset():
    cb = CircuitBreaker(threshold=8)
    # A single connection-reset (device crash signature) trips at once and names
    # the culprit path — no need for 8 consecutive errors.
    assert cb.register("200", reset=True, path="oper/Cisco-IOS-XE-lldp-oper  /data/x") is True
    assert cb.tripped is True
    assert "crash" in cb.reason
    assert cb.trip_path == "oper/Cisco-IOS-XE-lldp-oper  /data/x"


def test_device_log_sanitize_message():
    from scripts.harness.device_log import sanitize_message
    assert sanitize_message('a"b\nc  d') == "a b c d"
    assert len(sanitize_message("x" * 500)) <= 180
    assert "\n" not in sanitize_message("line1\r\nline2")


def test_filter_unsafe_skips_known_crasher_by_default():
    from scripts.harness.collector import filter_unsafe, KNOWN_UNSAFE_MODULES
    from scripts.harness.spec_paths import GetPath
    assert "Cisco-IOS-XE-lldp-oper" in KNOWN_UNSAFE_MODULES
    paths = [
        GetPath("oper", "Cisco-IOS-XE-lldp-oper", "/data/Cisco-IOS-XE-lldp-oper:lldp-entries"),
        GetPath("oper", "Cisco-IOS-XE-switchport-oper", "/data/x:switchport"),
    ]
    kept, skipped = filter_unsafe(paths)
    assert [p.module for p in kept] == ["Cisco-IOS-XE-switchport-oper"]
    assert skipped == ["Cisco-IOS-XE-lldp-oper"]
    # override restores it
    kept2, skipped2 = filter_unsafe(paths, include_unsafe=True)
    assert len(kept2) == 2 and skipped2 == []
    # extra user exclude
    kept3, skipped3 = filter_unsafe(paths, extra_exclude=["Cisco-IOS-XE-switchport-oper"], include_unsafe=True)
    assert [p.module for p in kept3] == ["Cisco-IOS-XE-lldp-oper"]
    assert skipped3 == ["Cisco-IOS-XE-switchport-oper"]


def _write_capture(
    captures: Path,
    device: str,
    category: str,
    module: str,
    path: str,
    status,
    response,
    pid: str = "C9300-48T",
    error=None,
) -> None:
    d = captures / device / category
    d.mkdir(parents=True, exist_ok=True)
    record = {
        "device": device, "pid": pid, "host": "10.0.0.9",
        "module": module, "category": category, "path": path,
        "restconf_url": f"https://h:443/restconf{path}",
        "http_status": status, "fetched_at": "2026-07-30T10:00:00Z",
        "os_version": "26.1.1", "error": error, "response": response,
    }
    safe = path.replace("/", "_")[:40]
    (d / f"{module}__{safe}__{status}.json").write_text(json.dumps(record), encoding="utf-8")


def test_report_status_class():
    assert report_mod._status_class(200) == "ok"
    assert report_mod._status_class(404) == "missing"
    assert report_mod._status_class(503) == "err"
    assert report_mod._status_class(None) == "other"


def test_report_counts_and_content(tmp_path):
    caps = tmp_path / "captures"
    _write_capture(caps, "sw1", "oper", "Cisco-IOS-XE-demo-oper",
                   "/data/demo/stats", 200, {"pkts": 633024})
    _write_capture(caps, "sw1", "oper", "Cisco-IOS-XE-demo-oper",
                   "/data/demo/missing", 404, None)
    html_str, counts, total = report_mod.build_report(caps, max_chars=None)
    assert total == 2
    assert counts["ok"] == 1 and counts["missing"] == 1
    assert "633024" in html_str
    assert "C9300-48T" in html_str          # provenance shown
    assert "/data/demo/stats" in html_str


def test_report_escapes_html(tmp_path):
    caps = tmp_path / "captures"
    _write_capture(caps, "sw1", "oper", "m", "/data/x", 200,
                   {"note": "<script>alert(1)</script>"})
    html_str, _counts, _total = report_mod.build_report(caps, max_chars=None)
    assert "<script>alert(1)</script>" not in html_str
    assert "&lt;script&gt;" in html_str


def test_report_truncates_large_body(tmp_path):
    caps = tmp_path / "captures"
    big = {"blob": "x" * 5000}
    _write_capture(caps, "sw1", "oper", "m", "/data/x", 200, big)
    html_str, _c, _t = report_mod.build_report(caps, max_chars=100)
    assert "truncated" in html_str


# --- build_observed_examples.py (real-data example overlay) -------------------

def _write_get_spec(specs_root: Path, category: str, module: str, path: str,
                    existing_example=None) -> Path:
    api = specs_root / f"swagger-{category}-model" / "api"
    api.mkdir(parents=True, exist_ok=True)
    media: dict = {}
    if existing_example is not None:
        media["example"] = existing_example
    spec = {"openapi": "3.0.0", "paths": {path: {"get": {"responses": {
        "200": {"description": "ok", "content": {"application/yang-data+json": media}}}}}}}
    spec_file = api / f"{module}.json"
    spec_file.write_text(json.dumps(spec), encoding="utf-8")
    return spec_file


def test_is_usable():
    assert overlay_mod._is_usable({"http_status": 200, "response": {"a": 1}})
    assert not overlay_mod._is_usable({"http_status": 200, "response": None})
    assert not overlay_mod._is_usable({"http_status": 200, "response": {}})
    assert not overlay_mod._is_usable({"http_status": 404, "response": {"a": 1}})
    assert not overlay_mod._is_usable({"http_status": 200, "response": {"a": 1}, "error": "boom"})


def test_overlay_dry_run_writes_nothing(tmp_path):
    caps = tmp_path / "captures"
    specs = tmp_path / "specs"
    _write_capture(caps, "sw1", "oper", "m", "/data/x", 200, {"pkts": 1})
    spec_file = _write_get_spec(specs, "oper", "m", "/data/x")
    before = spec_file.read_text(encoding="utf-8")
    stats = overlay_mod.apply_overlay(caps, specs, write=False)
    assert stats["operations_annotated"] == 1
    assert spec_file.read_text(encoding="utf-8") == before  # untouched


def test_overlay_injects_example_and_provenance(tmp_path):
    caps = tmp_path / "captures"
    specs = tmp_path / "specs"
    _write_capture(caps, "sw1", "oper", "m", "/data/x", 200,
                   {"pkts": 633024, "password": "hunter2"}, pid="C9300-48T")
    spec_file = _write_get_spec(specs, "oper", "m", "/data/x",
                                existing_example={"pkts": 0})
    overlay_mod.apply_overlay(caps, specs, write=True)
    spec = json.loads(spec_file.read_text(encoding="utf-8"))
    media = spec["paths"]["/data/x"]["get"]["responses"]["200"]["content"]["application/yang-data+json"]
    # singular example migrated, live example added
    assert "example" not in media
    assert media["examples"]["schema-default"]["value"] == {"pkts": 0}
    live = media["examples"]["live-C9300-48T"]
    assert live["value"]["pkts"] == 633024
    assert live["value"]["password"] == redact.REDACTED          # defensively redacted
    assert "Real device capture" in live["summary"]
    assert media["x-cisco-observed"]["live-C9300-48T"]["source"] == "live-device"
    assert media["x-cisco-observed"]["live-C9300-48T"]["pid"] == "C9300-48T"
    # Provenance must carry the OpenAPI path, never the device IP / restconf_url.
    obs = media["x-cisco-observed"]["live-C9300-48T"]
    assert obs["path"] == "/data/x"
    assert "restconf_url" not in obs
    assert not any("10.0.0" in str(v) for v in obs.values())


def test_overlay_skips_too_large_example(tmp_path):
    caps = tmp_path / "captures"
    specs = tmp_path / "specs"
    _write_capture(caps, "sw1", "oper", "m", "/data/x", 200, {"blob": "x" * 4000})
    spec_file = _write_get_spec(specs, "oper", "m", "/data/x")
    before = spec_file.read_text(encoding="utf-8")
    stats = overlay_mod.apply_overlay(caps, specs, write=True, max_bytes=100)
    assert stats["operations_annotated"] == 0
    assert stats["skipped_too_large"] == 1
    assert spec_file.read_text(encoding="utf-8") == before  # untouched


def test_overlay_skips_secret_bearing_example(tmp_path):
    caps = tmp_path / "captures"
    specs = tmp_path / "specs"
    # A cert-like value with no END block slips past light redaction but the
    # basic secret scanner still flags "BEGIN CERTIFICATE" -> must be skipped.
    _write_capture(caps, "sw1", "oper", "m", "/data/x", 200,
                   {"cert": "-----BEGIN CERTIFICATE-----abc"})
    spec_file = _write_get_spec(specs, "oper", "m", "/data/x")
    before = spec_file.read_text(encoding="utf-8")
    stats = overlay_mod.apply_overlay(caps, specs, write=True)
    assert stats["operations_annotated"] == 0
    assert stats["skipped_secret"] == 1
    assert spec_file.read_text(encoding="utf-8") == before  # untouched


def test_overlay_is_idempotent(tmp_path):
    caps = tmp_path / "captures"
    specs = tmp_path / "specs"
    _write_capture(caps, "sw1", "oper", "m", "/data/x", 200, {"pkts": 1})
    spec_file = _write_get_spec(specs, "oper", "m", "/data/x",
                                existing_example={"pkts": 0})
    overlay_mod.apply_overlay(caps, specs, write=True)
    first = spec_file.read_text(encoding="utf-8")
    overlay_mod.apply_overlay(caps, specs, write=True)
    assert spec_file.read_text(encoding="utf-8") == first


def test_overlay_multi_pid_adds_separate_examples(tmp_path):
    caps = tmp_path / "captures"
    specs = tmp_path / "specs"
    _write_capture(caps, "sw1", "oper", "m", "/data/x", 200, {"pkts": 1}, pid="C9200-48P")
    _write_capture(caps, "sw2", "oper", "m", "/data/x", 200, {"pkts": 2}, pid="C9300-48T")
    spec_file = _write_get_spec(specs, "oper", "m", "/data/x")
    overlay_mod.apply_overlay(caps, specs, write=True)
    spec = json.loads(spec_file.read_text(encoding="utf-8"))
    examples = spec["paths"]["/data/x"]["get"]["responses"]["200"]["content"]["application/yang-data+json"]["examples"]
    assert "live-C9200-48P" in examples and "live-C9300-48T" in examples


def test_overlay_skips_non200_and_missing_path(tmp_path):
    caps = tmp_path / "captures"
    specs = tmp_path / "specs"
    _write_capture(caps, "sw1", "oper", "m", "/data/present", 200, {"pkts": 1})
    _write_capture(caps, "sw1", "oper", "m", "/data/absent", 200, {"pkts": 1})
    _write_capture(caps, "sw1", "oper", "m", "/data/present", 404, None)
    _write_get_spec(specs, "oper", "m", "/data/present")  # only /data/present exists
    stats = overlay_mod.apply_overlay(caps, specs, write=True)
    assert stats["operations_annotated"] == 1
    assert stats["path_not_in_spec"] == 1
    assert stats["skipped_not200_or_empty"] == 1


def test_overlay_reports_missing_spec(tmp_path):
    caps = tmp_path / "captures"
    specs = tmp_path / "specs"
    (specs / "swagger-oper-model" / "api").mkdir(parents=True)
    _write_capture(caps, "sw1", "oper", "nonexistent-module", "/data/x", 200, {"a": 1})
    stats = overlay_mod.apply_overlay(caps, specs, write=True)
    assert stats["spec_missing"] == 1
    assert stats["operations_annotated"] == 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
