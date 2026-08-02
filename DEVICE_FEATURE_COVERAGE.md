# Device Feature Coverage — enabling features to collect more API data

**Purpose.** The RESTCONF GET harness captures every supported xpath, but on a
lab device most oper/config models return **404 = the feature isn't configured**
(see [DEVICE_DATA_COLLECTION.md §4.1](DEVICE_DATA_COLLECTION.md)). This runbook is
the living place to **discuss and document the device configuration** that lights
up more models, so a re-collection captures the most data for every API.

> Lab-only. These are illustrative enablements for a captive lab fleet
> (C9200/9300/9400/9500/9600 + C9800), IOS XE 26.1.1. Do **not** apply to
> production. One feature family at a time; `write memory`; then re-collect and
> measure (below).

## How to measure a coverage gain
1. Configure a feature family on the target device(s).
2. Re-collect + rebuild: `python scripts/refresh_live_data.py --version 26.1.1 --capture`.
3. Compare module coverage (captured / total per category) on the Live Data page,
   or via `releases/26.1.1/live-examples-index.json` → `categories[].captured_modules`.
4. Re-verify completeness: `python -X utf8 -m scripts.harness.depth_probe --device <PID> --discover --category oper`.

## Baseline: current state (26.1.1)
- **311 / 937 modules** have data; **626** return 404/empty = unconfigured or
  platform-inapplicable.
- Already enabled (verified): the **SNMP → RESTCONF MIB bridge**, which unlocked
  the `swagger-mib-model` data. Applied per device via netmiko:
  ```
  snmp-server community ***REDACTED*** RO
  snmp ifmib ifindex persist
  netconf-yang cisco-ia snmp-community-string ***REDACTED***
  ```

## Two buckets of uncaptured modules

### A. Enablable on Catalyst via config (worth doing)
A prioritized, **to-validate** checklist. Each family unlocks its `*-oper` (and
some `*-cfg`) modules once traffic/adjacencies exist. Counts are the uncaptured
oper modules observed on this fleet.

| Feature family | Example modules unlocked | Starter config (validate before trusting) |
|---|---|---|
| Unicast routing | `bgp`, `isis`, `ospf(v3)`, `eigrp`, `rip`, `rpl`/route-policy | `router bgp <asn>` + a neighbor; `router isis` + `net`; `router ospf 1` + a network; bring at least one adjacency **up** |
| MPLS / Segment Routing | `mpls-*` (3), `mpls-ldp`, `segment-routing` | `mpls ip`; `mpls label protocol ldp`; or `segment-routing mpls` + IGP SR |
| Multicast | `mvrp`, `igmp`/`pim`, `mfib` | `ip multicast-routing`; `ip pim` on SVIs; an IGMP joiner |
| MACsec / security | `macsec`, `cts`/trustsec, `matm` | `mka policy` + `macsec` on a link; `cts manual` |
| NetFlow / FnF | `flow-monitor`, `fnf`, `et-analytics` | `flow record`/`flow monitor` + apply to an interface |
| QoS | `diffserv`, `qos`, `policer` | `policy-map` + `service-policy` on an interface |
| DHCP / DNS / NAT | `dhcp`, `dns`, `nat`, `nbar` | `ip dhcp pool`; `ip nat inside/outside`; `ip nbar protocol-discovery` |
| L2 / bridging | `bridge-domain`, `cfm`, `dlr`, `mvrp`, `spanning-tree` extras | EVC/BD config; CFM domain; STP already on |
| Stacking / platform | `stackwise-virtual`, `stack`, `breakout`, `bbu` | SVL on 9500/9600 pair; `hw-module breakout` |
| Wireless (C9800) | `wireless-*` (14) — AP/client/RRM/mobility | Join **≥1 AP** and associate **≥1 client**; most wireless oper is empty until APs/clients exist |

> Tip: routing/MPLS/multicast oper models stay **empty until an adjacency or
> flow is actually up** — configuring the feature is necessary but not always
> sufficient; generate a little traffic/peering.

### B. Platform-inapplicable on Catalyst (will NOT populate — don't chase)
These belong to other platforms and will 404 on a C9K regardless of config:
`qfp-*` (QuantumFlow, ASR/CSR), `sdwan-*`, `appqoe`, `dre`, `umbrella`,
`aws-*` (cloud), `cable-*` (CMTS), `cellwan` (LTE/5G WAN modules). Track them as
**N/A for this fleet**, not as gaps.

## Iteration playbook (run this every cycle)
This is a **multi-pass** effort — we iterate until as much as possible is
configured and collected. Each cycle touches one feature family and is fully
measured before moving on.

1. **Pick** the next family from the Phased backlog (below), lowest phase first.
2. **Snapshot** current coverage: note `captured_modules` per category from
   `releases/26.1.1/live-examples-index.json` (or the Live Data coverage cards).
3. **Health check** the target device(s): reachable, RESTCONF up, no alarms.
4. **Back up** running-config (`show run`) before changing anything.
5. **Configure** the family on ONE device (or a device *pair* where an adjacency
   is needed), via netmiko. Keep changes minimal and reversible.
6. **Bring it up** — an oper model stays empty until the feature is *active*
   (adjacency established, flow/traffic present, client joined). Generate the
   minimum needed (peer, joiner, ping).
7. **`write memory`** once healthy.
8. **Re-collect**: `python scripts/refresh_live_data.py --version 26.1.1 --capture`
   (or targeted `python -m scripts.harness.collector --device <name> --module <mod>`).
9. **Measure** the delta: which `*-oper`/`*-cfg` modules moved from 404 → data;
   record the before→after `captured_modules`.
10. **Verify** no regression/crash: `python -m scripts.harness.depth_probe
    --device <PID> --discover --category <cat>`; confirm the device is healthy.
11. **Record** a row in the Iteration log; **commit** the regenerated data +
    the log update; roll the config to the remaining devices if it paid off.

## Prep / assumptions (do once, Phase 0.5)
- **Topology.** All 6 devices share the `10.85.134.0/24` management network.
  Confirm before Phase 1: (a) is mgmt in a VRF (`Mgmt-vrf`)?  (b) are there
  **data-plane links** between devices, or usable loopbacks, for L3 adjacencies?
  Routing/MPLS/multicast/MACsec need a peer or a link that is **not** the mgmt
  path. Document the actual lab cabling / SVIs / loopbacks here first.
- **Peering model.** Easiest is to peer the switches **to each other** (they are
  co-located) over a data VLAN/loopbacks — e.g. OSPF area 0 across a shared L2
  segment, iBGP between loopbacks. Where no data link exists, a single device +
  a loopback-only config still populates many oper models (process up) even
  without a neighbor.
- **Rollback.** Every cycle keeps a `show run` backup; changes are reversible
  (`no` forms). The capture harness stays GET-only.

### Discovered topology (2026-08-02, from `cdp-oper` + `interfaces-oper`)
The **C9300-24UX (10.85.134.70) is the lab aggregation hub** — 14 data ports up,
CDP neighbors include our C9600, C9800, plus external spines/TORs and a CW9166
AP. What connects to it, and whether the link is usable for data-plane routing:

| Device | Local port | → C9300 hub port | Link kind | Data-plane usable? |
|---|---|---|---|---|
| **C9800** | `Te0/0/0` (data) | `Te1/0/3` | data ↔ data, UP | **YES** — real adjacency, no recabling |
| C9600 | `Gig0/0` (**mgmt**) | `Te1/0/13` | mgmt ↔ data | No — C9600 side is the OOB Mgmt-vrf port |
| C9500 | `Gig0/0` (**mgmt**) | `Te1/0/10` | mgmt ↔ data | No — C9500 side is mgmt; already has `Loopback0 192.168.2.2` |
| C9200 | `Gi1/0/1` (data) | → external `C9300-TOR1` | data ↔ external | Peer not in our inventory |
| hub → spines | `Te1/0/9`,`Te1/0/10` | VNC2-SPINE1/2 (C9500s) | data ↔ external | Peer not ours (a running fabric) |
| hub → AP | `Te1/0/14` | CW9166I AP | data ↔ AP | Wireless (Phase 9) |

**C9600 free data ports:** `TenGigabitEthernet0/1` and `0/2` are **admin-up but
`lower-layer-down`** (enabled, nothing plugged in). **C9500** similarly has
`HundredGigE1/0/33-48` up-but-no-cable.

**Cabling answer — do NOT move `Gig0/0`.** On Catalyst, `Gig0/0` is the dedicated
out-of-band **Mgmt-vrf** port that carries our RESTCONF access (e.g. C9600 =
10.85.134.75); it cannot route data-plane traffic, and moving the cable would cut
data collection. Instead:
- **Zero-recabling wins now:** (a) **loopback-only** routing on all 6 (populates
  OSPF/ISIS/BGP process oper without a neighbor; C9500 already has a loopback);
  (b) a **real OSPF/BGP adjacency on the existing C9300↔C9800 data link**.
- **To give C9600/C9500 real neighbors:** add ONE data cable each — e.g. C9600
  `Te0/1` → a free hub port, C9500 `Hu1/0/33` → a free hub port — and **keep
  `Gig0/0` for management**. A routed p2p (`/31`) + OSPF then brings full oper.

## Phased backlog (priority order — iterate lowest-first)
Counts are the uncaptured **oper** modules this family should unlock on this
fleet. Mark each ✅ when validated in the Iteration log.

| Phase | Family | Unlocks (examples) | Minimal enable | Needs a peer/link? |
|---|---|---|---|---|
| 1 | **Unicast routing** | `ospf`, `isis`, `bgp`, `eigrp`, `rip`, `rpl`, `rib` | `router ospf 1` + net on a loopback/SVI; add ISIS/BGP/EIGRP | Peer for full oper; loopback alone still populates process state |
| 2 | **L2 / switching** | `bridge-domain`, `cfm`, `mvrp`, `dlr`, MST/VTP | EVC/BD; `ethernet cfm`; `spanning-tree mode mst` | Link between two devices |
| 3 | **Multicast** | `pim`, `igmp`, `mfib` | `ip multicast-routing`; `ip pim sparse-mode` on SVIs | Source + joiner |
| 4 | **MPLS / SR** | `mpls-*` (3), `mpls-ldp`, `segment-routing` | `mpls ip` + LDP, or `segment-routing mpls` | IGP up (Phase 1) |
| 5 | **Services** | `dhcp`, `dns`, `nat`, `nbar` | `ip dhcp pool`; `ip nat`; `ip nbar protocol-discovery` | No (local) |
| 6 | **Security** | `macsec`, `cts`/trustsec, `matm`, dot1x | `mka policy` + `macsec` on a link; `cts manual` | MACsec needs a link |
| 7 | **Telemetry / QoS** | `flow-monitor`/`fnf`, `et-analytics`, `diffserv`/`qos` | `flow monitor` on an intf; `policy-map` + `service-policy` | No (traffic helps) |
| 8 | **Platform / HA** | `stackwise-virtual`, `stack`, `breakout` | SVL on a 9500/9600 pair; `hw-module breakout` | Pair for SVL |
| 9 | **Wireless (C9800)** | `wireless-*` (14) — AP/client/RRM/mobility | Join ≥1 AP + associate ≥1 client | Physical AP(s) |

Phases 1–7 are software-only on the switches; Phase 8 needs a device pair;
Phase 9 needs AP hardware. Skip the **platform-inapplicable** families entirely
(bucket B above).

## Iteration log (fill one row per cycle)
| # | Date | Phase / family | Device(s) | Config summary | `captured_modules` before → after | New modules populated | Device healthy? | Commit |
|---|------|----------------|-----------|----------------|-----------------------------------|-----------------------|-----------------|--------|
| 0 | 2026-07 | 0 · SNMP→RESTCONF MIB bridge | all 6 | `snmp-server community`, `snmp ifmib ifindex persist`, `netconf-yang cisco-ia snmp-community-string` | mib 62 → 96 | MIB models | yes | shipped |
| 1 | _tbd_ | 1 · routing | _tbd_ | _tbd_ | _tbd_ | _tbd_ | _tbd_ | _tbd_ |

## Definition of done
"As much as possible configured and collected" = every family in bucket A is
either ✅ validated (modules populated + logged) or explicitly marked
**not-feasible-in-this-lab** (no hardware/peer), and bucket B is confirmed
platform-inapplicable. Re-run the full `depth_probe --discover` fleet sweep at
the end to reconfirm completeness.

## Safety
- **Never** enable in a way that requires the crash-unsafe modules to be walked
  (`Cisco-IOS-XE-lldp-oper`, `CISCO-RTTMON-MIB`, `CISCO-VOICE-DIAL-CONTROL-MIB`);
  they stay on the collector skip-list (DEVICE_DATA_COLLECTION §4/§9).
- One family at a time, on one device first; confirm the box is healthy; then
  `write memory` and roll to the rest.
- Re-run `depth_probe --discover` after enabling to confirm no new module hides
  data behind keyed lists.

## Where to discuss / track
This file is the **living runbook** — extend the tables as families are
validated (add the exact tested CLI + which modules it unlocked + which
device(s)). Open questions and decisions can go in the repo issue tracker;
link the relevant commit/PR back here when a family is validated.
