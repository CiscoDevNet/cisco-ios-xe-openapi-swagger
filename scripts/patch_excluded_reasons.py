#!/usr/bin/env python
"""patch_excluded_reasons.py

One-shot maintenance script: add `reason_excluded` strings to the small
remaining set of modules that surface on the accountability page as
"❌ No spec" without an explanation.

Each entry below was verified by inspecting the YANG source (no augments,
no top-level containers — only groupings / typedefs / identity catalogues).
Notification-only ("events") modules get the same reason the generator now
emits, and helper indexes such as `_paths_index` (not modules) are dropped
with the summary totals recomputed. Idempotent.
Touches all 6 accountability JSON files (root + 5 per-release copies).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_yang_accountability_v2 import EVENTS_REASON  # noqa: E402

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


def recompute_totals(data: dict) -> None:
    """Recompute summary fields with the same formulas as the generator."""
    modules = data["modules"]
    data["total_modules"] = len(modules)
    data["modules_with_specs"] = sum(1 for m in modules if m["has_spec"])
    data["modules_with_trees"] = sum(1 for m in modules if m["tree_url"])
    data["modules_multi_category"] = sum(1 for m in modules if len(m["categories"]) > 1)
    for classification, stats in data["categories"].items():
        members = [m for m in modules if m["classification"] == classification]
        stats["total"] = len(members)
        stats["with_specs"] = sum(1 for m in members if m["has_spec"])
        stats["coverage_pct"] = round(100 * stats["with_specs"] / len(members), 1) if members else 0.0


def main() -> int:
    total_patched = 0
    for path in ACCOUNTABILITY_FILES:
        if not path.is_file():
            print(f"  skip (missing): {path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        helper_entries = [m["name"] for m in data["modules"] if m["name"].startswith("_")]
        data["modules"] = [m for m in data["modules"] if not m["name"].startswith("_")]
        recompute_totals(data)
        patched = 0
        for mod in data.get("modules", []):
            name = mod.get("name")
            if mod.get("has_spec") or mod.get("reason_excluded"):
                continue
            if name in REASONS:
                mod["reason_excluded"] = REASONS[name]
                patched += 1
            elif mod.get("classification") == "events":
                mod["reason_excluded"] = EVENTS_REASON
                patched += 1
        # Same serialization as analyze_yang_accountability_v2.py.
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        total_patched += patched
        print(f"  {path.relative_to(ROOT)}: patched {patched}, dropped helper entries {helper_entries}")
    print(f"[patch_excluded_reasons] total entries patched: {total_patched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
