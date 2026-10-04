"""Offline tests for the onboarding planner (no devices)."""
from __future__ import annotations

from scripts.harness.onboard import mask, plan

READY = """\
hostname LAB
service internal
aaa new-model
aaa authentication login default local
aaa authorization exec default local
username harness privilege 15 secret 9 $9$abc
crypto pki trustpoint TP-self-signed-123
ip http authentication local
ip http secure-server
restconf
netconf-yang
netconf-yang cisco-ia snmp-community-string ro-comm
snmp-server community ro-comm RO
snmp ifmib ifindex persist
gnxi
gnxi secure-trustpoint TP-self-signed-123
gnxi secure-server
"""

FRESH = """\
hostname NEW
line vty 0 4
 login local
"""


def by_name(steps):
    return {s.name: s for s in steps}


def test_ready_device_needs_nothing():
    steps = by_name(plan(READY, "harness", "pw", snmp_community="ro-comm"))
    assert {n: s.status for n, s in steps.items()} == {
        "aaa": "ok", "https": "ok", "restconf": "ok", "netconf": "ok", "gnmi": "ok", "snmp": "ok"}


def test_fresh_device_gets_full_plan_with_user_before_aaa():
    steps = by_name(plan(FRESH, "harness", "pw"))
    assert steps["aaa"].lines[0] == "username harness privilege 15 secret 0 pw"
    assert steps["aaa"].lines[1:] == ["aaa new-model", "aaa authentication login default local",
                                      "aaa authorization exec default local"]
    assert steps["https"].lines == ["ip http secure-server", "ip http authentication local"]
    assert steps["restconf"].lines == ["restconf"] and steps["netconf"].lines == ["netconf-yang"]
    assert "gnxi secure-trustpoint <TP-self-signed after https>" in steps["gnmi"].lines
    assert steps["snmp"].status == "skipped"


def test_existing_tacacs_aaa_is_never_modified():
    config = "aaa new-model\naaa authentication login default group tacacs+ local\n"
    steps = by_name(plan(config, "harness", "pw"))
    assert steps["aaa"].status == "manual" and not steps["aaa"].lines
    assert "aaa authorization exec default" in steps["aaa"].note
    assert steps["https"].lines == ["ip http secure-server", "ip http authentication aaa"]


def test_existing_complete_tacacs_aaa_uses_aaa_http_auth():
    config = ("aaa new-model\naaa authentication login default group tacacs+ local\n"
              "aaa authorization exec default group tacacs+ local\n")
    steps = by_name(plan(config, "harness", "pw"))
    assert steps["aaa"].status == "ok"
    assert "ip http authentication aaa" in steps["https"].lines
    assert "user" not in steps


def test_local_aaa_without_harness_user_is_flagged():
    config = "aaa new-model\naaa authentication login default local\naaa authorization exec default local\n"
    steps = by_name(plan(config, "harness", "pw"))
    assert steps["user"].status == "manual"


def test_existing_trustpoint_used_for_gnmi():
    config = READY.replace("gnxi secure-server\n", "")
    steps = by_name(plan(config, "harness", "pw"))
    assert "gnxi secure-trustpoint TP-self-signed-123" in steps["gnmi"].lines
    assert "service internal" not in steps["gnmi"].lines


def test_snmp_bridge_adds_only_missing_lines():
    config = READY.replace("snmp ifmib ifindex persist\n", "")
    steps = by_name(plan(config, "harness", "pw", snmp_community="ro-comm"))
    assert steps["snmp"].lines == ["snmp ifmib ifindex persist"]


def test_mask_hides_secrets():
    assert mask("username harness privilege 15 secret 0 pw") == "username harness privilege 15 secret 0 <masked>"
    assert mask("snmp-server community ro-comm RO") == "snmp-server community <masked> RO"
    assert mask("netconf-yang cisco-ia snmp-community-string ro-comm") == \
        "netconf-yang cisco-ia snmp-community-string <masked>"


class FakeConn:
    def __init__(self, config):
        self.config = config
        self.pushed = []
        self.saved = False

    def send_command(self, cmd, read_timeout=None):
        return self.config if cmd == "show running-config" else ""

    def send_config_set(self, lines, read_timeout=None):
        self.pushed.append(list(lines))
        if any(line.startswith("gnxi") for line in lines):
            self.config += "\n".join(lines) + "\n"
        return ""

    def save_config(self):
        self.saved = True

    def disconnect(self):
        pass


def _run(monkeypatch, tmp_path, config, login_ok=True, apply=True, save=False):
    from scripts.harness import inventory as inv
    from scripts.harness import onboard

    conn = FakeConn(config)
    monkeypatch.setattr(onboard, "_connect", lambda dev, auth: conn)
    monkeypatch.setattr(onboard, "_login_ok", lambda dev, auth: login_ok)
    monkeypatch.setattr(onboard, "_wait_ready", lambda dev, seconds=120: {"restconf:443": True})
    dev = inv.Device(name="lab", host="192.0.2.1")
    report = onboard.onboard_device(dev, ("harness", "pw"), apply, save, None, None, tmp_path)
    return conn, report


def test_dry_run_pushes_nothing(monkeypatch, tmp_path):
    conn, report = _run(monkeypatch, tmp_path, FRESH, apply=False)
    assert conn.pushed == [] and "backup" not in report
    assert any(s["name"] == "aaa" and s["status"] == "todo" for s in report["plan"])


def test_apply_backs_up_then_pushes_in_order(monkeypatch, tmp_path):
    conn, report = _run(monkeypatch, tmp_path, FRESH + "crypto pki trustpoint TP-self-signed-9\n", save=True)
    assert (tmp_path / report["backup"].split("/")[-1]).read_text() .startswith("hostname NEW")
    assert [p[0] for p in conn.pushed][:2] == ["username harness privilege 15 secret 0 pw", "ip http secure-server"]
    assert any("gnxi secure-trustpoint TP-self-signed-9" in p for p in conn.pushed)
    assert conn.saved and "pw" not in str(report["applied"])


def test_aaa_lockout_is_rolled_back(monkeypatch, tmp_path):
    import pytest
    with pytest.raises(RuntimeError, match="rolled back"):
        _run(monkeypatch, tmp_path, FRESH, login_ok=False)


def test_ready_device_apply_is_a_no_op(monkeypatch, tmp_path):
    conn, report = _run(monkeypatch, tmp_path, READY)
    assert conn.pushed == [] and "backup" not in report
