"""Redaction rules (scripts/mdt-telemetry/collector/redact_payload.py) for each gap behind
GitGuardian incident 3498322. All values are fake; real ones must never appear in tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "mdt-telemetry" / "collector"))

import redact_payload as rp  # noqa: E402

R = rp.REDACTED


def test_telemetry_path_joined_and_underscore_leaves():
    out = rp.redact_obj({
        "Cisco_IOS_XE_aaa:key/key": "FAKE7KEY1234", "Cisco_IOS_XE_aaa:key/encryption": "7",
        "pre_shared_key": "FAKEPSK", "key_string": "FAKEKS", "auth_key": "FAKEAK", "private_key": "FAKEPK",
        "ap_login_credentials/user_name": "fakeadmin", "username/name": "fakeuser",
        "cpu/user": 12, "key-id": 5, "public-key": "AAAA", "snmpInBadCommunityNames": "0",
    })
    assert all(out[k] == R for k in ("Cisco_IOS_XE_aaa:key/key", "pre_shared_key", "key_string", "auth_key",
                                      "private_key", "ap_login_credentials/user_name", "username/name"))
    assert out["Cisco_IOS_XE_aaa:key/encryption"] == "7"
    assert (out["cpu/user"], out["key-id"], out["public-key"], out["snmpInBadCommunityNames"]) == (12, 5, "AAAA", "0")


def test_nested_secret_objects_in_json_payloads_even_truncated():
    payload = ('{"neighbor":[{"id":"1.1.1.1","password":{"enctype":7,"text":"FAKETXT"}}],'
               '"ldp":{"password":{"clear":"FAKECLR","encrypted":"FAKEENC"}},'
               '"community":[{"name":"FAKECOMM","permission":"ro","view":"V1"}]}')
    out = rp.redact_payload(payload)
    assert not any(v in out for v in ("FAKETXT", "FAKECLR", "FAKEENC", "FAKECOMM"))
    assert '"enctype":7' in out and '"permission":"ro"' in out and '"view":"V1"' in out
    assert "FAKETXT" not in rp.redact_payload(payload[:75])


def test_xml_payload_secret_containers_and_usernames():
    xml = ("<user-mgmt><username>fakeadmin</username><password><enctype>7</enctype><text>FAKEX</text></password>"
           "</user-mgmt><description>key exchange</description><community-config><name>FAKEC</name></community-config>")
    out = rp.redact_payload(xml)
    assert not any(v in out for v in ("fakeadmin", "FAKEX", "FAKEC"))
    assert "<enctype>7</enctype>" in out and "key exchange" in out


def test_cli_forms():
    cli = "\n".join([
        "hostname FAKE-HOST",
        "username fakeuser privilege 15 secret 9 $9$FAKEfakeFAKEfake$FAKEhash",
        "enable secret 5 $1$FAKE$FAKEhash",
        " password 7 FAKE0822455D",
        "ntp authentication-key 1 md5 FAKENTP 7",
        "snmp-server user fakev3 GRP v3 auth sha FAKEAUTH priv aes 128 FAKEPRIV",
        "snmp-server host 10.1.1.1 vrf Mgmt version 2c FAKEHOSTCOMM",
        "snmp-server community FAKECOMM2 RO",
        " wpa psk set-key ascii 0 FAKEWPA",
        "key config-key password-encrypt FAKEMASTER",
        " pre-shared-key local 6 FAKEPSK6",
        " standby 1 authentication text FAKEHSRP",
        " mgmtuser username fakeap password 0 FAKEAPPW secret 0 FAKEAPSEC",
    ])
    out = rp.mask_cli(cli)
    for v in ("fakeuser", "$9$FAKE", "$1$FAKE", "FAKE0822", "FAKENTP", "fakev3", "FAKEAUTH", "FAKEPRIV",
              "FAKEHOSTCOMM", "FAKECOMM2", "FAKEWPA", "FAKEMASTER", "FAKEPSK6", "FAKEHSRP", "fakeap", "FAKEAPPW"):
        assert v not in out, v
    assert "hostname FAKE-HOST" in out and "secret 9 " + R in out and "auth sha" in out
    assert rp.mask_cli(out) == out


def test_mib_username_columns_json_and_xml():
    leaves = ("ccmHistoryEventTerminalUser", "ccmCTIDWhoChanged", "casnUserId", "cSipCfgAaaUsername", "admin-username")
    out = rp.redact_obj({leaf: "fakeadmin" for leaf in leaves} | {"casnUserIdCount": "3", "sysName": "FAKE-SW"})
    assert all(out[leaf] == R for leaf in leaves)
    assert (out["casnUserIdCount"], out["sysName"]) == ("3", "FAKE-SW")
    xml = ("<ccmHistoryEventEntry><ccmHistoryEventTerminalUser>fakeadmin</ccmHistoryEventTerminalUser>"
           "<ccmHistoryEventTerminalType>virtual</ccmHistoryEventTerminalType></ccmHistoryEventEntry>"
           "<casnActiveEntry><casnUserId>fakeadmin</casnUserId></casnActiveEntry>")
    masked = rp.redact_payload(xml)
    assert "fakeadmin" not in masked and "virtual" in masked
    mdt = ("<mdt-connections><conn-id><con-params><p-user>fakeproxy</p-user><p-pass>FAKEPP</p-pass>"
           "<p-pass-type>pw-encryption-clear</p-pass-type></con-params></conn-id><peer-id>fakeadmin</peer-id>"
           "</mdt-connections><bgp-neighbor><peer-id>10.0.0.1</peer-id></bgp-neighbor>")
    masked = rp.redact_payload(mdt)
    assert not any(v in masked for v in ("fakeproxy", "FAKEPP", "fakeadmin"))
    assert "pw-encryption-clear" in masked and "<peer-id>10.0.0.1</peer-id>" in masked


def test_telemetry_list_keys_judged_by_row_path():
    assert rp.redact_list_keys({"name": "fakeadmin"}, "Cisco-IOS-XE-native:native/username") == {"name": R}
    assert rp.redact_list_keys({"name": "Gi1/0/1"}, "openconfig-interfaces:interfaces/interface") == {"name": "Gi1/0/1"}
    # Identifiers of lists under password / credential containers stay visible.
    assert rp.redact_list_keys({"first": "0"}, "Cisco-IOS-XE-native:native/line/vty/password") == {"first": "0"}
    ap = "Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data/oper-data/ap-login-credentials"
    assert rp.redact_list_keys({"wtp_mac": "aa:bb:cc:00:11:22"}, ap) == {"wtp_mac": "aa:bb:cc:00:11:22"}
    dataset = {"paths": [
        {"path": path, "keys": {"name": "fakeadmin"}, "fields": {"privilege": 15},
         "samples": [{"keys": {"name": "fakeadmin"}, "fields": {}}]}
        for path in ("Cisco-IOS-XE-native:native/username", "Cisco-IOS-XE-native:native/username/secret",
                     "Cisco-IOS-XE-native:native/username/password", "ietf-netconf-acm:nacm/rule-list")
    ] + [{"path": "Cisco-IOS-XE-interfaces-oper:interfaces/interface", "keys": {"name": "Gi1/0/1"},
          "samples": [{"keys": {"name": "Gi1/0/1"}}]}]}
    out = rp.redact_obj(dataset)
    assert "fakeadmin" not in json.dumps(out)
    assert out["paths"][-1]["samples"][0]["keys"]["name"] == "Gi1/0/1"
    assert out["paths"][0]["fields"]["privilege"] == 15
    assert {label for label, _ in rp.scan_text(json.dumps(dataset))} == {"secret_leaf"}
    assert rp.scan_text(json.dumps(out)) == []


def test_gate_decodes_embedded_payloads_and_ignores_identifiers():
    doc = {"paths": [{"fields": {"Cisco_IOS_XE_aaa:key/key": "FAKE7KEY1234"},
                      "payload": "<secret>$9$FAKEfakeFAKE$FAKE</secret>"}],
           "methods": [{"key": "mdt"}, {"key": "netconf-get"}]}
    labels = {label for label, _ in rp.scan_text(json.dumps(doc))}
    assert labels == {"secret_leaf", "embedded_secret"}
    assert all("FAKE" not in loc for _, loc in rp.scan_text(json.dumps(doc)))
