#!/usr/bin/env python3
"""
fix_quality.py - Fix all remaining quality issues in event notification examples.

Addresses 578+ bad values across 5 categories:
1. "event-type" placeholders in enum/type fields (355)
2. Self-referential values where value == leaf name (162)
3. Wrong-domain values (e.g., "link-flap-detected" in license context) (18)
4. IP addresses in MAC address fields (29)
5. OperStatus="up" in Down traps (14)

Usage:
  python scripts/fix_quality.py          # dry-run
  python scripts/fix_quality.py --apply  # apply changes
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(BASE, "swagger-events-model", "api")
APPLY = "--apply" in sys.argv

# ============================================================
# MASTER LEAF → REALISTIC VALUE MAPPING
# Based on YANG tree research for each leaf name
# ============================================================

# --- MIB "Type" / enum fields that were set to "event-type" ---
LEAF_FIXES = {
    # OSPF-TRAP-MIB / CISCO-OSPF-TRAP-MIB
    "ospfConfigErrorType": "authTypeMismatch",
    "ospfPacketType": "hello",
    "ospfLsdbType": "routerLink",
    "cospfConfigErrorType": "authTypeMismatch",
    "cospfPacketType": "hello",
    "cospfLsdbType": "routerLink",
    "cospfShamLinkNbrIpAddrType": "ipv4",
    "cospfShamLinksLocalIpAddrType": "ipv4",
    "cospfShamLinksRemoteIpAddrType": "ipv4",

    # IF-MIB
    "ifType": "ethernetCsmacd",

    # DIAL-CONTROL-MIB
    "callHistoryInfoType": "speech",
    "callActiveInfoType": "speech",

    # RMON-MIB
    "alarmSampleType": "absoluteValue",

    # MPLS-LDP-STD-MIB (counter32, not enum)
    "mplsLdpSessionStatsUnknownMesTypeErrors": 0,

    # CISCO-BGP4-MIB / BGP4-MIB
    "cbgpPeer2Type": "ipv4",

    # CISCO-EIGRP-MIB
    "cEigrpDestNetType": "ipv4",
    "cEigrpPeerAddrType": "ipv4",

    # CISCO-PIM-MIB / PIM-MIB
    "cpimLastErrorGroupType": "ipv4",
    "cpimLastErrorOriginType": "ipv4",
    "cpimLastErrorRPType": "ipv4",
    "cpimRPMappingChangeType": "newMapping",

    # CISCO-IPSEC-FLOW-MONITOR-MIB / CISCO-IPSEC-MIB
    "cikePeerLocalType": "ipAddrPeer",
    "cikePeerRemoteType": "ipAddrPeer",
    "cipsStaticCryptomapType": "ipsec-manual",

    # CISCO-ATM-PVCTRAP-EXTN-MIB
    "catmIntfTypeOfOAMFailure": "aisRDI",
    "catmIntfTypeOfOAMRecover": "aisRDI",
    "CISCO-ATM-PVCTRAP-EXTN-MIB:catmIntfTypeOfOAMFailure": "aisRDI",
    "CISCO-ATM-PVCTRAP-EXTN-MIB:catmIntfTypeOfOAMRecover": "aisRDI",

    # CISCO-CONFIG-MAN-MIB
    "ccmHistoryEventTerminalType": "virtual",

    # CISCO-DOT3-OAM-MIB
    "cdot3OamEventLogType": "errSymPeriodEvent",

    # CISCO-ENTITY-ALARM-MIB
    "ceAlarmHistAlarmType": "environmentalAlarm",

    # CISCO-EMBEDDED-EVENT-MGR-MIB
    "ceemHistoryEventType1": 1,
    "ceemHistoryEventType2": 2,
    "ceemHistoryEventType3": 3,
    "ceemHistoryEventType4": 4,

    # CISCO-ENHANCED-MEMPOOL-MIB / CISCO-ENTITY-QFP-MIB
    "ceqfpMemoryResType": "dram",

    # CISCO-IMAGE-LICENSE-MGMT-MIB
    "clmgmtLicenseType": "demo",

    # CISCO-NETSYNC-MIB
    "cnsInpSrcIntfType": "netsyncIfTypeEthernet",
    "cnsSelInpSrcIntfType": "netsyncIfTypeEthernet",
    "cnsT4ClkSrcIntfType": "netsyncIfTypeEthernet",

    # CISCO-SUBSCRIBER-SESSION-MIB
    "csubAggStatsPointType": "interface",
    "csubAggStatsSessionType": "pppSubscriber",

    # CISCO-UNIFIED-FIREWALL-MIB
    "cufwUrlfServerAddrType": "ipv4",

    # CISCO-VOICE-DIAL-CONTROL-MIB
    "cvCommonDcCallHistoryCoderTypeRate": "g729r8000",

    # CISCO-VPDN-MGMT-MIB
    "cvpdnSystemTunnelType": "l2f",

    # CISCO-ISIS-MIB
    "ciiErrorTLVType": 1,

    # ENTITY-MIB
    "entPhysicalVendorType": "1.3.6.1.4.1.9.12.3",

    # CISCO-STP-EXTENSIONS-MIB
    "stpxSpanningTreeType": "rapidPvstPlus",

    # CISCO-RTTMON-MIB
    "probe-type": "icmp-echo",
    "react-type": "rtt",
    "y1731-sub-type": "delay-measurement",

    # CISCO-NBAR-PROTOCOL-DISCOVERY-MIB
    "threshold-type": "percent",

    # DS1/DS3 MIB
    "hw-sensor-type": "temperature",

    # CISCO-IP-LOCAL-POOL-MIB
    "addr-type": "ipv4",

    # ietf-ospf
    "link-type": "point-to-point-link",
    "packet-type": "hello",

    # Cisco-IOS-XE specific
    "comp-type": "chassis",
    "sensor-type": "temperature",
    "coa-req-type": "coa-req-reauth",
    "guard-type": "root-guard",
    "err-type": "hash-mismatch",
    "nat-event-type": "create",
    "nat-type": "static",
    "dca-change-type": "added",
    "action-type": "permit",
    "network-type": "broadcast",
    "ni-type": "vrf",
    "oper-type": "add",
    "route-type": "connected",
    "ev-type": "link-up",
    "af": "address-family-ipv4",
    "event-type-string": "interface-state-change",
    "file-type": "image",
    "type": "security",

    # Cisco-IOS-XE-platform-events-oper (complex containers become simple strings when treated as leaf)
    "(event-type-choice)?": "rogue-potential-honeypot-detected",
    "(filter-type)?": "by-reference",
    "(mac-type-choice)?": "00:1a:2b:3c:4d:5e",
    "(vlan-type-choice)?": 100,
    "(instance-type-choice)?": 1,
}

# --- Self-referential leaf fixes (value == leaf name) ---
SELF_REF_FIXES = {
    # ietf-ospf
    "routing-instance": "default",
    "sham-link": "10.1.1.1",

    # Cisco-IOS-XE-platform-events-oper
    "location": "R0",
    "sensor-val": "42.5",
    "alarm-data": "temperature-critical",

    # Cisco-IOS-XE-sm-events-oper
    "coa-params": "session-reauth",

    # Cisco-IOS-XE-stack-mgr-events-oper
    "member-stats": "active",
    "mbr-port": "StackPort1/1",
    "stats": "15000 packets",
    "svl-port": "FortyGigabitEthernet1/1/1",
    "local-port": "StackPort1/1",
    "remote-port": "StackPort2/1",
    "port-stats": "50000 frames tx",
    "mbr-keepalive": "12000 sent",
    "dad-port": "StackPort1/2",

    # Cisco-IOS-XE-wireless-events-oper
    "reporting-ap": "AP-Floor3-West",

    # Cisco-IOS-XE-qfp-resource-events
    "warning-string": "QFP memory utilization exceeded 90% threshold",

    # Cisco-IOS-XE-verify-events
    "computed-hash": "a3f2b8c1d9e0f47856234ab1cd789ef0",
    "file-hash": "e5d7a1b2c3f4096785ab23cd01ef9876",

    # Cisco-IOS-XE-xcopy-events
    "errstr": "Connection to remote server timed out",

    # Cisco-IOS-XE-udld-events
    "neighbor-port": "GigabitEthernet1/0/2",

    # ietf-event-notifications
    "stream": "NETCONF",
    "encoding": "encode-xml",
    "filter": "/ietf-interfaces:interfaces",
    "filter-ref": "1",

    # ietf-netconf-notifications
    "changed-by": "admin",
    "datastore": "running",
    "edit": "merge",
    "target": "/ietf-interfaces:interfaces/interface[name='GigabitEthernet1']",
    "confirm-event": "start",

    # Cisco-IOS-XE misc
    "module": "Cisco-IOS-XE-native",
    "headline": "System configuration changed",
    "name-server": "8.8.8.8",
    "trust-point": "CISCO_IDEVID_SUDI",
    "sha": "SHA-256",
    "url": "https://10.1.1.1/firmware.bin",
    "warning": "Approaching resource limit",
    "ed-string": "Interface GigabitEthernet1 link-up",
    "registration-entity": "smart-agent",
    "remote-host": "10.0.0.100",
    "react-data": "5ms",
    "part-no": "C9300-24T",
    "filesystem": "bootflash:",
    "db-file": "vlan.dat",
    "vpn": "Corp-VPN",
    "xofy": "1-of-5",
}

# --- Context-specific: "link-flap-detected" in license contexts ---
LICENSE_REASON_FIX = "comm-failure"

# --- IP-in-MAC fields fix ---
MAC_FIX = "de:ad:be:ef:00:01"

# ============================================================
# Operational status fixes for Down traps
# ============================================================
OPER_DOWN_FIELDS = {
    "ifOperStatus": "down",
    "mplsXCOperStatus": "down",
    "mplsTunnelOperStatus": "down",
    "mplsXCAdminStatus": "down",
    "mplsTunnelAdminStatus": "down",
    "cpwVcOperStatus": "down",
    "cieIfOperStatusCause": "down",
}


def fix_example(obj, path="", schema_name="", file_name="", fixes_log=None):
    """Recursively walk and fix example values."""
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            new_obj[k] = fix_example(v, new_path, schema_name, file_name, fixes_log)
        return new_obj
    elif isinstance(obj, list):
        return [fix_example(v, f"{path}[{i}]", schema_name, file_name, fixes_log) for i, v in enumerate(obj)]
    elif isinstance(obj, str):
        leaf = path.rsplit(".", 1)[-1] if "." in path else path
        leaf = re.sub(r"\[\d+\]$", "", leaf)
        original = obj

        # Fix 1: "event-type" placeholder → correct value
        if obj == "event-type" or obj == "ospfv3-address":
            if leaf in LEAF_FIXES:
                new_val = LEAF_FIXES[leaf]
                if fixes_log is not None:
                    fixes_log.append(("event-type", file_name, schema_name, leaf, original, new_val))
                return new_val
            # Fallback: try without module prefix
            bare_leaf = leaf.split(":")[-1] if ":" in leaf else leaf
            if bare_leaf in LEAF_FIXES:
                new_val = LEAF_FIXES[bare_leaf]
                if fixes_log is not None:
                    fixes_log.append(("event-type", file_name, schema_name, leaf, original, new_val))
                return new_val

        # Fix 2: Self-referential (value == leaf name)
        if obj == leaf or obj == leaf.replace("-", "_"):
            if leaf in SELF_REF_FIXES:
                new_val = SELF_REF_FIXES[leaf]
                if fixes_log is not None:
                    fixes_log.append(("self-ref", file_name, schema_name, leaf, original, new_val))
                return new_val

        # Fix 3: Wrong-domain (link-flap-detected in license context)
        if obj == "link-flap-detected" and ("license" in file_name.lower() or "license" in schema_name.lower()):
            if fixes_log is not None:
                fixes_log.append(("wrong-domain", file_name, schema_name, leaf, original, LICENSE_REASON_FIX))
            return LICENSE_REASON_FIX

        # Fix 4: IP address in MAC field
        if "mac" in leaf.lower() and re.match(r"^\d+\.\d+\.\d+\.\d+$", obj):
            if fixes_log is not None:
                fixes_log.append(("IP-in-MAC", file_name, schema_name, leaf, original, MAC_FIX))
            return MAC_FIX

        # Fix 5: OperStatus="up" in Down trap
        is_down_context = "down" in schema_name.lower()
        if is_down_context and leaf in OPER_DOWN_FIELDS and obj == "up":
            new_val = OPER_DOWN_FIELDS[leaf]
            if fixes_log is not None:
                fixes_log.append(("oper-down", file_name, schema_name, leaf, original, new_val))
            return new_val

    return obj


def process_file(fpath, fname, fixes_log):
    """Process one JSON spec file, returning modified data or None if no changes."""
    with open(fpath, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    changed = False
    before_count = len(fixes_log)

    # Fix component schemas examples
    schemas = data.get("components", {}).get("schemas", {})
    for sname in list(schemas.keys()):
        if "example" in schemas[sname]:
            new_ex = fix_example(
                schemas[sname]["example"], "", sname, fname, fixes_log
            )
            if new_ex != schemas[sname]["example"]:
                schemas[sname]["example"] = new_ex
                changed = True

    # Fix path-level examples
    for p, pv in data.get("paths", {}).items():
        for method, mv in pv.items():
            if not isinstance(mv, dict):
                continue
            for code, rv in mv.get("responses", {}).items():
                content = rv.get("content", {})
                for ct in list(content.keys()):
                    if "example" in content[ct]:
                        # Determine schema name from path
                        sname = p.rsplit(":", 1)[-1] if ":" in p else p.rsplit("/", 1)[-1]
                        new_ex = fix_example(
                            content[ct]["example"], "", sname, fname, fixes_log
                        )
                        if new_ex != content[ct]["example"]:
                            content[ct]["example"] = new_ex
                            changed = True

    after_count = len(fixes_log)
    return data if changed else None, after_count - before_count


def main():
    fs = sorted(
        f
        for f in os.listdir(API_DIR)
        if f.endswith(".json") and f != "manifest.json"
    )

    fixes_log = []
    files_fixed = 0

    for fname in fs:
        fpath = os.path.join(API_DIR, fname)
        new_data, fix_count = process_file(fpath, fname, fixes_log)
        if new_data is not None:
            files_fixed += 1
            if APPLY:
                with open(fpath, "w", encoding="utf-8") as fh:
                    json.dump(new_data, fh, indent=2, ensure_ascii=False)
                    fh.write("\n")

    # Summary
    mode = "APPLIED" if APPLY else "DRY-RUN"
    print(f"\n{'='*60}")
    print(f"  {mode} Summary")
    print(f"{'='*60}")
    print(f"  Files checked:  {len(fs)}")
    print(f"  Files fixed:    {files_fixed}/{len(fs)}")
    print(f"  Values fixed:   {len(fixes_log)}")

    # Breakdown by category
    cats = {}
    for fix in fixes_log:
        cats[fix[0]] = cats.get(fix[0], 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"    {cat}: {count}")

    # Show unfixed "event-type" values
    remaining_et = 0
    remaining_sr = 0
    for fname in fs:
        fpath = os.path.join(API_DIR if APPLY else API_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as fh:
            text = fh.read()
            data = json.loads(text)

        def count_remaining(obj, path="", sname=""):
            nonlocal remaining_et, remaining_sr
            if isinstance(obj, dict):
                for k, v in obj.items():
                    count_remaining(v, f"{path}.{k}" if path else k, sname)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    count_remaining(v, f"{path}[{i}]", sname)
            elif isinstance(obj, str):
                leaf = path.rsplit(".", 1)[-1] if "." in path else path
                leaf = re.sub(r"\[\d+\]$", "", leaf)
                if obj == "event-type" or obj == "ospfv3-address":
                    remaining_et += 1
                    if remaining_et <= 20:
                        print(f"    UNFIXED event-type: {fname} -> {sname} -> {leaf}")
                if obj == leaf or obj == leaf.replace("-", "_"):
                    remaining_sr += 1
                    if remaining_sr <= 20:
                        print(f"    UNFIXED self-ref: {fname} -> {sname} -> {leaf}={obj}")

        schemas = data.get("components", {}).get("schemas", {})
        for sname, sval in schemas.items():
            count_remaining(sval.get("example", {}), sname=sname)
        for p, pv in data.get("paths", {}).items():
            for method, mv in pv.items():
                if not isinstance(mv, dict):
                    continue
                for code, rv in mv.get("responses", {}).items():
                    for ct, cv in rv.get("content", {}).items():
                        sname = p.rsplit(":", 1)[-1] if ":" in p else p.rsplit("/", 1)[-1]
                        count_remaining(cv.get("example", {}), sname=sname)

    print(f"\n  Remaining 'event-type': {remaining_et}")
    print(f"  Remaining self-ref:     {remaining_sr}")
    print(f"{'='*60}")

    if not APPLY:
        print("\n  Run with --apply to write changes to disk.")


if __name__ == "__main__":
    main()
