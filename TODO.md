# Phase 3 — Native Model Completion: Gaps, Policy & Interfaces

> **Interactive tracking document for completing ALL remaining native augment coverage.**
> Prior phases delivered 22 spec files covering 128 / 139 native augment modules.
> Phase 3 closes the remaining 11 gaps and adds per-interface-type + policy endpoints.

---

## Summary

| Section | Items | New Spec Files | Est. Paths |
|---------|-------|---------------|------------|
| A — Top-level Gaps | 7 modules | 0 (add to existing) | 7 |
| B — Policy | 1 module (massive) | 1 `native-policy.json` | 5 |
| C — Interface Types | 63 types | 4 new files | 63 |
| D — Interface-only Augments | 3 modules (nam, serial, tunnel) | 0 (covered by C) | 0 extra |
| **Total** | **~74 new endpoints** | **5 new files** | **~75** |

---

## A — Top-level Gap Endpoints (7 modules)

These modules augment `/ios:native` with top-level containers that are missing from the
existing 22 spec files. Each will be added to the most appropriate existing file.

| # | Module | RESTCONF Path | Target File | Status |
|---|--------|--------------|-------------|--------|
| A1 | Cisco-IOS-XE-cef | `/native/cef` | `native-ip.json` | ✅ |
| A2 | Cisco-IOS-XE-device-sensor | `/native/device-sensor` | `native-security-access.json` | ✅ |
| A3 | Cisco-IOS-XE-eta | `/native/et-analytics` | `native-security-services.json` | ✅ |
| A4 | Cisco-IOS-XE-nd | `/native/ipv6/nd` | `native-routing-multicast.json` | ✅ |
| A5 | Cisco-IOS-XE-power | `/native/power` | `native-platform-system.json` | ✅ |
| A6 | Cisco-IOS-XE-sla | `/native/ip/sla` | `native-ip.json` | ✅ |
| A7 | Cisco-IOS-XE-utd | `/native/utd` | `native-security-services.json` | ✅ |

### Placement rationale
- **cef** → `native-ip.json` — augments `/native/ip/cef` and `/native/ipv6/cef` (IP forwarding plane)
- **device-sensor** → `native-security-access.json` — profiling/identity, sits next to device-tracking
- **eta** (Encrypted Traffic Analytics) → `native-security-services.json` — security analytics
- **nd** (Neighbor Discovery) → `native-routing-multicast.json` — augments `/native/ipv6/nd`, next to mld
- **power** (PoE) → `native-platform-system.json` — hardware/platform, next to platform settings
- **sla** (IP SLA) → `native-ip.json` — augments `/native/ip/sla`, IP services
- **utd** (Unified Threat Defense) → `native-security-services.json` — security feature

### YANG tree details
```
cef:            /native/cef → table, output-chain, consistency-check
device-sensor:  /native/device-sensor → accounting, notify, filter-list, filter-spec
eta:            /native/et-analytics → ip/flow-export, ipv6/flow-export, inactive-timeout, whitelist
nd:             /native/ipv6/nd → cache, reachable-time, ra, nud, raguard, inspection
power:          /native/power → inline (consumption/logging), redundancy-mode, supply
sla:            /native/ip/sla → entry (icmp-echo/udp-jitter/http/dns/etc), responder, schedule, logging
utd:            /native/utd → engine, redirect, web-filter; utd-st, utd-mt, utd-unified-policy
```

---

## B — Policy Module

`Cisco-IOS-XE-policy` is the largest single augment module (424 KB YANG tree, 6000+ lines).
It augments 36 unique paths across native, policy, parameter-map, control-plane, and 32 interface types.

**New file: `native-policy.json`**

| # | RESTCONF Path | Description | Status |
|---|--------------|-------------|--------|
| B1 | `/native/service-group` | Service groups with input/output policy bindings | ✅ |
| B2 | `/native/policy/class-map` | QoS / security class-map definitions (match criteria) | ✅ |
| B3 | `/native/policy/policy-map` | QoS / security policy-map definitions (actions) | ✅ |
| B4 | `/native/parameter-map/type` | Parameter map types (inspect, regex, webauth, etc.) | ✅ |
| B5 | `/native/control-plane/service-policy` | Control-plane policy binding (CoPP) | ✅ |

> **Note:** Per-interface `service-policy` bindings are part of each interface type definition
> and will be covered automatically by the interface specs in Section C.

### Policy module scope
```
augment /ios:native:              → service-group* [group-id]
augment /ios:native/ios:policy:   → class-map* [name], policy-map* [name]
augment /ios:native/ios:parameter-map/ios:type: → inspect, regex, webauth, ...
augment /ios:native/ios:control-plane:          → service-policy (input/output)
augment /ios:native/ios:interface/ios:{32 types}: → service-policy per interface
```

---

## C — Interface Type Endpoints (63 types)

The native YANG model defines 63 interface types under `/native/interface`.
Currently only the top-level `/native/interface` container overview exists (in `native-misc-ext.json`).
Each type needs its own CRUD endpoint: GET list, GET by name, PUT, PATCH, DELETE.

**Split into 4 files by function:**

### C1 — `native-intf-ethernet.json` — Physical Ethernet Family (13 types)

| # | Interface Type | RESTCONF Path | Status |
|---|---------------|--------------|--------|
| C1.01 | Ethernet | `/native/interface/Ethernet` | ✅ |
| C1.02 | FastEthernet | `/native/interface/FastEthernet` | ✅ |
| C1.03 | GigabitEthernet | `/native/interface/GigabitEthernet` | ✅ |
| C1.04 | TwoGigabitEthernet | `/native/interface/TwoGigabitEthernet` | ✅ |
| C1.05 | FiveGigabitEthernet | `/native/interface/FiveGigabitEthernet` | ✅ |
| C1.06 | AppGigabitEthernet | `/native/interface/AppGigabitEthernet` | ✅ |
| C1.07 | TenGigabitEthernet | `/native/interface/TenGigabitEthernet` | ✅ |
| C1.08 | TwentyFiveGigE | `/native/interface/TwentyFiveGigE` | ✅ |
| C1.09 | FortyGigabitEthernet | `/native/interface/FortyGigabitEthernet` | ✅ |
| C1.10 | FiftyGigabitEthernet | `/native/interface/FiftyGigabitEthernet` | ✅ |
| C1.11 | HundredGigE | `/native/interface/HundredGigE` | ✅ |
| C1.12 | TwoHundredGigE | `/native/interface/TwoHundredGigE` | ✅ |
| C1.13 | FourHundredGigE | `/native/interface/FourHundredGigE` | ✅ |

### C2 — `native-intf-virtual.json` — Virtual, Overlay & Switching (18 types)

| # | Interface Type | RESTCONF Path | Status |
|---|---------------|--------------|--------|
| C2.01 | Loopback | `/native/interface/Loopback` | ✅ |
| C2.02 | Tunnel | `/native/interface/Tunnel` | ✅ |
| C2.03 | Virtual-Template | `/native/interface/Virtual-Template` | ✅ |
| C2.04 | Virtual-PPP | `/native/interface/Virtual-PPP` | ✅ |
| C2.05 | VirtualPortGroup | `/native/interface/VirtualPortGroup` | ✅ |
| C2.06 | vasileft | `/native/interface/vasileft` | ✅ |
| C2.07 | vasiright | `/native/interface/vasiright` | ✅ |
| C2.08 | Vif | `/native/interface/Vif` | ✅ |
| C2.09 | Vlan | `/native/interface/Vlan` | ✅ |
| C2.10 | BDI | `/native/interface/BDI` | ✅ |
| C2.11 | BD-VIF | `/native/interface/BD-VIF` | ✅ |
| C2.12 | LISP | `/native/interface/LISP` | ✅ |
| C2.13 | LISP-subinterface | `/native/interface/LISP-subinterface` | ✅ |
| C2.14 | L2LISP | `/native/interface/L2LISP` | ✅ |
| C2.15 | L2LISP-subinterface | `/native/interface/L2LISP-subinterface` | ✅ |
| C2.16 | nve | `/native/interface/nve` | ✅ |
| C2.17 | overlay | `/native/interface/overlay` | ✅ |
| C2.18 | pseudowire | `/native/interface/pseudowire` | ✅ |

### C3 — `native-intf-wan.json` — WAN, Serial & Aggregation (17 types)

| # | Interface Type | RESTCONF Path | Status |
|---|---------------|--------------|--------|
| C3.01 | Serial | `/native/interface/Serial` | ✅ |
| C3.02 | Serial-subinterface | `/native/interface/Serial-subinterface` | ✅ |
| C3.03 | ATM | `/native/interface/ATM` | ✅ |
| C3.04 | ATM-subinterface | `/native/interface/ATM-subinterface` | ✅ |
| C3.05 | ATM-ACR | `/native/interface/ATM-ACR` | ✅ |
| C3.06 | ATM-ACRsubinterface | `/native/interface/ATM-ACRsubinterface` | ✅ |
| C3.07 | CEM | `/native/interface/CEM` | ✅ |
| C3.08 | CEM-ACR | `/native/interface/CEM-ACR` | ✅ |
| C3.09 | Dialer | `/native/interface/Dialer` | ✅ |
| C3.10 | Cellular | `/native/interface/Cellular` | ✅ |
| C3.11 | Multilink | `/native/interface/Multilink` | ✅ |
| C3.12 | Group-Async | `/native/interface/Group-Async` | ✅ |
| C3.13 | Async | `/native/interface/Async` | ✅ |
| C3.14 | MFR | `/native/interface/MFR` | ✅ |
| C3.15 | MFR-subinterface | `/native/interface/MFR-subinterface` | ✅ |
| C3.16 | Port-channel | `/native/interface/Port-channel` | ✅ |
| C3.17 | Port-channel-subinterface | `/native/interface/Port-channel-subinterface` | ✅ |

### C4 — `native-intf-service.json` — Service, IoT & Specialty (15 types)

| # | Interface Type | RESTCONF Path | Status |
|---|---------------|--------------|--------|
| C4.01 | AppNav-Compress | `/native/interface/AppNav-Compress` | ✅ |
| C4.02 | AppNav-UnCompress | `/native/interface/AppNav-UnCompress` | ✅ |
| C4.03 | Embedded-Service-Engine | `/native/interface/Embedded-Service-Engine` | ✅ |
| C4.04 | Service-Engine | `/native/interface/Service-Engine` | ✅ |
| C4.05 | ucse | `/native/interface/ucse` | ✅ |
| C4.06 | Ethernet-Internal | `/native/interface/Ethernet-Internal` | ✅ |
| C4.07 | Wlan-GigabitEthernet | `/native/interface/Wlan-GigabitEthernet` | ✅ |
| C4.08 | SM | `/native/interface/SM` | ✅ |
| C4.09 | GMPLS | `/native/interface/GMPLS` | ✅ |
| C4.10 | PRP-channel | `/native/interface/PRP-channel` | ✅ |
| C4.11 | Bundle | `/native/interface/Bundle` | ✅ |
| C4.12 | LORAWAN | `/native/interface/LORAWAN` | ✅ |
| C4.13 | WPAN | `/native/interface/WPAN` | ✅ |
| C4.14 | Virtual-WPAN | `/native/interface/Virtual-WPAN` | ✅ |
| C4.15 | vmi | `/native/interface/vmi` | ✅ |

---

## D — Interface-only Augment Modules (covered by C)

These three modules only augment interface containers (no top-level `/native` container).
Their coverage is automatically satisfied when interface types are added in Section C.

| Module | What It Augments | Covered By |
|--------|-----------------|------------|
| Cisco-IOS-XE-nam | 12+ interface types (analysis-module, monitoring) + `/native/ppp` | C1, C2, C3 |
| Cisco-IOS-XE-serial | `/native/interface/Serial` + encapsulation augment | C3.01 |
| Cisco-IOS-XE-tunnel | `/native/interface/Tunnel` + Virtual-Template | C2.02, C2.03 |

---

## Execution Plan

### Step 1 — Gap Endpoints (A1–A7) — Quick Wins
Add 7 endpoints to existing spec files. ~30 min.
- Add RESTCONF path with GET/PUT/PATCH/DELETE operations
- Update `info.description` and YANG module lists in each target file
- Update manifest.json path counts
- **Files touched:** native-ip.json (+2), native-security-access.json (+1), native-security-services.json (+2), native-routing-multicast.json (+1), native-platform-system.json (+1)

### Step 2 — Policy (B1–B5)
Create `native-policy.json` with 5 top-level policy endpoints. ~30 min.
- Does NOT include per-interface `service-policy` bindings (part of each interface type)

### Step 3 — Interface Types (C1–C4)
Create 4 interface spec files covering 63 types. Largest batch, ~2 hrs.
- `native-intf-ethernet.json` — 13 physical Ethernet speed variants
- `native-intf-virtual.json` — 18 virtual/overlay/switching types
- `native-intf-wan.json` — 17 WAN/serial/aggregation types
- `native-intf-service.json` — 15 service/IoT/specialty types

### Step 4 — Finalization
- Update `manifest.json` with 5 new modules + revised path counts for 4 existing
- Update `search-index.json` with new endpoints
- Update both `index.html` files with sidebar entries + stats
- Final audit: confirm 139/139 native augment coverage + 63 interface types
- Git commit & push

---

## Progress Tracker

```
Phase 3 Progress: 75 / 75 endpoints   [████████████████████] 100%  ✅ COMPLETE

Section A (Gaps):       7 / 7    ███████  ✅
Section B (Policy):     5 / 5    █████    ✅
Section C (Interfaces): 63 / 63  ███████████████████████████████  ✅
```

---

## Reference: Final 27 Spec Files (Phase 3 Complete)

| File | Paths | Tags |
|------|-------|------|
| native-00-top-level-containers.json | 5 | management, services, switching |
| native-00-top-level-leafs.json | 8 | boot, leafs, network-features, platform, qos, system-basics |
| native-aaa.json | 4 | aaa-root, accounting, authentication, authorization |
| native-app-services.json | 7 | app-hosting, kron, mdns-gateway, nbar, pnp, service-discovery, service-routing |
| native-crypto.json | 5 | crypto-root, keys, pki, vpn |
| native-industrial-iot.json | 11 | cellular, coap, dapr, digitalio, dlr, irig, lorawan, lte450, mrp, prp, rawsocket |
| native-intf-ethernet.json | 13 | **NEW** — 13 physical Ethernet speed variants |
| native-intf-service.json | 15 | **NEW** — 15 service/IoT/specialty interface types |
| native-intf-virtual.json | 18 | **NEW** — 18 virtual/overlay/switching interface types |
| native-intf-wan.json | 17 | **NEW** — 17 WAN/serial/aggregation interface types |
| native-ip.json | 10 | ip-root, routing, security, services, **+cef, +sla** |
| native-l2-discovery.json | 5 | arp, icmp, lldp, loop-detect, uplink-autoconfig |
| native-line.json | 4 | aux, console, line-root, vty |
| native-misc-ext.json | 10 | ezpm, interfaces, iwanfabric, pathmgr, perf-measure, site-manager, voice-port, vservice, vstack, wccp |
| native-other.json | 82 | other |
| native-platform-diag.json | 13 | alarm-profile, buffers, diagnostics, dying-gasp, ethinternal-subslot, geo, gnss, ida, mmode, qfp-stats, rmi-dad, synce, ucse |
| native-platform-system.json | 16 | platform, **+power** |
| native-policy.json | 5 | **NEW** — class-map, policy-map, parameter-map, service-group, control-plane |
| native-protocols.json | 17 | protocols |
| native-qos-policy.json | 2 | qos |
| native-router.json | 7 | bgp, eigrp, isis, lisp, ospf, rip, router-root |
| native-routing-multicast.json | 8 | igmp, mld, mobileip, multicast, nhrp, ospfv3, rsvp, **+nd** |
| native-security-access.json | 16 | security, **+device-sensor** |
| native-security-services.json | 7 | fqdn, group-policy, pae, sanet, umbrella, **+eta, +utd** |
| native-switching-l2.json | 9 | switching |
| native-vrf.json | 2 | vrf-config, vrf-root |
| native-wan-legacy.json | 12 | adsl, atm, bba-group, dialer, ipc, ipmux, isdn, isg, l2nat, l3nat-iox, pppoe, vpdn |
| **TOTAL** | **328** | **27 categories, 1,307 operations** |
