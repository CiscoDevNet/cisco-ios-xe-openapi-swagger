#!/usr/bin/env python
"""patch_excluded_reasons.py

One-shot maintenance script: add `reason_excluded` strings to the small
remaining set of modules that surface on the accountability page as
"❌ No spec" without an explanation.

Each entry below was verified by inspecting the YANG source (no augments,
no top-level containers — only groupings / typedefs / identity catalogues).
Touches all 6 accountability JSON files (root + 5 per-release copies).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REASONS = {
    # Identity / feature catalogues — no data nodes
    "Cisco-IOS-XE-features": "Feature catalogue (identity statements only); no data nodes to expose",
    "iana-if-type": "IANA interface type identity registry; no data nodes",
    "openconfig-extensions": "OpenConfig extension keyword definitions; no data nodes",
    "ietf-yang-patch-ann": "YANG annotation definitions; no data nodes",
    "ietf-netconf-otlp-context-traceparent-version-1.0": "OTLP trace-context annotation module; no data nodes",
    "ietf-netconf-otlp-context-tracestate-version-1.0": "OTLP trace-context annotation module; no data nodes",
    # Typedef libraries — imported only
    "ietf-datastores": "Typedef/identity library (NMDA datastores); consumed via import",
    "iana-crypt-hash": "Typedef library (crypt-hash); consumed via import",
    "ietf-yang-smiv2": "SMIv2 annotation typedef library; consumed via import",
    # Groupings-only — building blocks for other modules
    "Cisco-IOS-XE-sisf": "Groupings-only module (6 reusable groupings); no instantiated data nodes",
    "ietf-restconf": "Groupings-only protocol module; consumed via import",
    "ietf-yang-patch": "Groupings-only protocol module; consumed via import",
    "openconfig-network-instance-l3": "Groupings-only module; consumed via import by openconfig-network-instance",
    # Augment + groupings — modify other modules, no standalone tree
    "openconfig-mpls-ldp": "Augments other openconfig-mpls modules; no standalone tree",
    "openconfig-mpls-rsvp": "Augments other openconfig-mpls modules; no standalone tree",
    "openconfig-mpls-sr": "Augments other openconfig-mpls modules; no standalone tree",
    "ietf-netconf-with-defaults": "Augments ietf-netconf protocol module; no standalone data nodes",
    # 'other' category — extension / identity / shared modules
    "cisco-extensions": "YANG extension keyword definitions; no data nodes",
    "cisco-semver-internal": "Internal semver extension definition; no data nodes",
    "cisco-routing-ext": "Routing identity registry; no data nodes",
    "cisco-storm-control": "Identity + groupings module; consumed via import",
    "cisco-policy": "Augments other policy modules; no standalone tree",
    "cisco-policy-target": "Augments other policy modules; no standalone tree",
    "cisco-xe-ietf-routing-ext": "Augments ietf-routing; no standalone tree",
    "cisco-xe-ietf-yang-push-ext": "Augments ietf-yang-push; no standalone tree",
    "cisco-ospf": "Groupings + typedefs + augments only; consumed via import by ospf modules",
    "policy-attr": "Groupings-only module (32 reusable groupings); consumed via import",
    # Per-release additional gaps (augment / groupings modules without a standalone tree)
    "cisco-evpn-service": "Groupings-only module (5 reusable groupings); consumed via import",
    "ietf-interfaces-ext": "Augments ietf-interfaces; no standalone tree",
    "ietf-yang-push": "Augments NETCONF subscription protocol; data exposed via ietf-subscribed-notifications",
    "openconfig-aft-network-instance": "Augments openconfig-network-instance; no standalone tree",
    "openconfig-bgp-policy": "Augments openconfig-routing-policy + groupings only; no standalone tree",
    "openconfig-if-aggregate": "Augments openconfig-interfaces; no standalone tree",
    "openconfig-if-ip": "Augments openconfig-interfaces; no standalone tree",
    "openconfig-if-ip-ext": "Augments openconfig-if-ip; no standalone tree",
    "openconfig-if-poe": "Augments openconfig-interfaces; no standalone tree",
    "openconfig-isis-policy": "Augments openconfig-routing-policy; no standalone tree",
    "openconfig-network-instance-policy": "Augments openconfig-network-instance; no standalone tree",
    "openconfig-openflow": "Augments openconfig-network-instance + groupings only; no standalone tree",
    "openconfig-ospf-policy": "Augments openconfig-routing-policy; no standalone tree",
    "openconfig-pf-srte": "Augments openconfig-network-instance; no standalone tree",
    "openconfig-platform-cpu": "Augments openconfig-platform; no standalone tree",
    "openconfig-platform-fan": "Augments openconfig-platform; no standalone tree",
    "openconfig-platform-linecard": "Augments openconfig-platform; no standalone tree",
    "openconfig-platform-port": "Augments openconfig-platform; no standalone tree",
    "openconfig-platform-psu": "Augments openconfig-platform; no standalone tree",
    "openconfig-programming-errors": "Augments openconfig-network-instance; no standalone tree",
    "openconfig-rib-bgp-ext": "Augments openconfig-rib-bgp; no standalone tree",
    "openconfig-route-summary": "Augments openconfig-network-instance; no standalone tree",
    "openconfig-system-grpc": "Augments openconfig-system + identity registry; no standalone tree",
    # Read-only stats module without -oper suffix (data accessible via paired -oper spec)
    "Cisco-IOS-XE-qfp-stats": "Read-only counters; data exposed via Cisco-IOS-XE-qfp-stats-oper spec",
    # 17.9.x-only modules
    "ietf-restconf-monitoring-ann": "RESTCONF monitoring annotation module; no data nodes",
    "openconfig-rib-bgp": "Augments openconfig-network-instance + groupings only; no standalone tree",
}

ACCOUNTABILITY_FILES = [
    ROOT / "yang_accountability.json",
    ROOT / "releases" / "17.9.x" / "yang_accountability.json",
    ROOT / "releases" / "17.12.x" / "yang_accountability.json",
    ROOT / "releases" / "17.15.x" / "yang_accountability.json",
    ROOT / "releases" / "17.18.1" / "yang_accountability.json",
    ROOT / "releases" / "26.1.1" / "yang_accountability.json",
]


def main() -> int:
    total_patched = 0
    for path in ACCOUNTABILITY_FILES:
        if not path.is_file():
            print(f"  skip (missing): {path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        patched = 0
        for mod in data.get("modules", []):
            name = mod.get("name")
            if name in REASONS and not mod.get("has_spec") and not mod.get("reason_excluded"):
                mod["reason_excluded"] = REASONS[name]
                patched += 1
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        total_patched += patched
        print(f"  {path.relative_to(ROOT)}: patched {patched}")
    print(f"[patch_excluded_reasons] total entries patched: {total_patched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
