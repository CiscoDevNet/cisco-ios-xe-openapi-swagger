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
  snmp-server community <community> RO
  snmp ifmib ifindex persist
  netconf-yang cisco-ia snmp-community-string <community>
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

### Rack roster + what is safe to touch (from the VNC2 Lab Matrix, 2026-08-02)
The rack has **many** devices on `10.85.134.0/24`; only 6 are ours to collect and
configure (matrix rows highlighted "XESWAGGER-L"). Trust the matrix's **RU**
column; other columns (roles/versions) may be stale.

**Our 6 (free-standing, safe to configure — pending the C9500 check below):**
`.70` C9300-24UX (hub, "R1 TOR-2 Rear") · `.71` C9400 · `.72` C9200L · `.75`
C9600 · `.83` C9840 WLC · `.95` C9500-32QC.

**NOT ours — shared rack/TOR, do NOT reconfigure (many Meraki-managed):**
- **VNC2 EVPN/Meraki/DT fabric:** `.99/.98/.97/.96` vnc2-leaf1–4, `.94/.92`
  vnc2-border2 / border1-acr, `.84` vnc2-spine1 (C9500-24Q). A **live** fabric.
- **Meraki-mode:** `.74` c9350, `.202` c9350-lux, an MX.
- **Infra:** `.65` TOR (C9300-24), `.79`/`.199` console servers, `.89` ASR1001,
  `.77` C9300L (needs password recovery), `.78` C9300-X, `.80` C9300LM.

> **⚠ Two hard constraints for Phase ≥1:**
> 1. **Never CLI-configure a Meraki-managed / live-fabric device** — the dashboard
>    owns it and will fight/lose the change. Touch only our 6.
> 2. **Our hub cables to the live EVPN spines** (hub `Te1/0/9`→vnc2-spine1,
>    `Te1/0/10`→our `.95`/vnc2-spine2). Do **not** push routing/VLAN changes onto
>    the hub's fabric-facing or mgmt-bridging ports — keep feature config on
>    **loopbacks and leaf devices**, away from `Te1/0/9`,`Te1/0/10`,`Te1/0/13`,
>    `Te1/0/24` and the mgmt VLAN.

> **✅ Resolved (2026-08-02):** `.95` (C9500) is **no longer in the VNC2 EVPN
> fabric** — it is free-standing and safe to reconfigure. All 6 XESWAGGER-L
> devices are in the config set. (Its hub-facing link is now just a lab link, not
> a live-fabric uplink — but still avoid disturbing the hub's mgmt-bridging role.)

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

## Phase 1 — implementation proposal (DRAFT — review before applying)
> **Status: NOT APPLIED. Next agent: review this whole section before writing
> anything to a device.** This is the first *write* to the fleet in this project;
> everything before it was read-only.

> ### ⚠ Risk findings (2026-08-02, verified read-only) — THESE REVISE THE PLAN
> - **C9800 mgmt is IN-BAND on `Vlan311` (10.85.134.83), not the `Gig0` OOB
>   port.** Its management therefore rides a **data** path (the `Te0/0/0`→hub
>   `Te1/0/3` link). **Converting that link to a routed `/31` would cut RESTCONF/
>   SSH to the C9800.**
> - **3 APs are joined** to the C9800 (incl. the CW9166 on hub `Te1/0/14`); their
>   CAPWAP rides the same data path — converting the link would **drop the APs**.
> - The C9300 hub also **bridges mgmt** for C9500/C9600 (their `Gig0/0` land on
>   hub ports). Touching the hub's mgmt VLAN/ports cuts those devices too.
>
> **Conclusion:** there is **no spare inter-device data link** among our 6 (the
> only ones are load-bearing for mgmt/CAPWAP; C9600/C9500 data ports are
> uncabled). So **Phase 1 = loopback-only OSPF on all 6, NO port conversions, NO
> adjacency, NO BGP.** This is additive/control-plane only and carries ~zero
> connectivity risk. Real neighbor/BGP oper (the config blocks below) becomes
> **Phase 1b — deferred until a dedicated spare cable is added** (e.g. C9600
> `Te0/1`→a free hub port), so no production/mgmt/CAPWAP link is disturbed.
>
> **Before ANY write:** confirm out-of-band **console** access (jcohoe-console
> `C1100T` / CONSOLE2) so a device is recoverable if it drops.
>
> ### Recovery model / OOB (know this before writing)
> - **Console lines** (matrix "Serial Port" col): C9400 `2010`, C9300-2 `2017`,
>   C9200 `2018`, C9840 WLC `2019`, C9500 `2024`, C9600 `2027`. Telnet the
>   console server → line → the device serial, independent of the device's
>   *network* mgmt.
> - **APs re-join automatically** once the WLC path is restored — no manual step.
> - **Do not `write memory` until confirmed healthy** — an unsaved bad change is
>   undone by a reload (and APs rejoin).
> - **The `/24` is sacred.** The TOR (`.65`) and BOTH console servers (`.79`,
>   `.199`) live on `10.85.134.0/24`. Breaking the `/24` upstream = losing the
>   TOR **and** console = no remote recovery. Only touching the hub's
>   mgmt-bridging ports or the mgmt VLAN can do this — both are forbidden.
> - Breaking a **single device's own** in-band mgmt (e.g. C9800 `Vlan311`) is
>   recoverable via that device's console line; the `/24` stays up for everyone
>   else. **Phase 1a (loopback-only) touches no port/VLAN/SVI, so it cannot break
>   the `/24` or any device's mgmt.**

**Goal.** Populate the routing oper models (`ospf`, `bgp`, `rib`, `rpl`, and —
where a process comes up — `isis`/`eigrp`) with zero recabling, on our 6
free-standing devices, without disturbing management or the neighboring live
EVPN fabric.

**Phase 1a (SAFE, apply now once reviewed): loopback-only OSPF on all 6.** A
dedicated loopback in OSPF area 0 brings up the OSPF process + interface/area
oper on every device even with no neighbor. **No physical port is touched.**

**Phase 1b (DEFERRED — needs a dedicated spare cable): real adjacency + iBGP.**
The routed-`/31` + iBGP blocks below stay as the reference design for when a
spare link exists. **Do NOT convert `Te1/0/3` / `Te0/0/0`** — they carry C9800
mgmt (Vlan311) + CAPWAP.

**Addressing (proposed — change if it collides with lab allocations).**
| Device | Mgmt IP | New Loopback100 | OSPF router-id |
|---|---|---|---|
| C9300-24UX (hub) | .70 | 10.255.0.70/32 | 10.255.0.70 |
| C9400 | .71 | 10.255.0.71/32 | 10.255.0.71 |
| C9200 | .72 | 10.255.0.72/32 | 10.255.0.72 |
| C9600 | .75 | 10.255.0.75/32 | 10.255.0.75 |
| C9840 WLC | .83 | 10.255.0.83/32 | 10.255.0.83 |
| C9500 | .95 | 10.255.0.95/32 | 10.255.0.95 (keep existing `Loopback0 192.168.2.2`) |

Point-to-point link: **`10.254.0.0/31`** — C9300 = `.0`, C9800 = `.1`.
OSPF process **1**, area **0**. BGP AS **65000**.

**Phase 1a — final per-device CLI (verified against current state 2026-08-02).**
Pre-checks: `Loopback100` free on all 6; no OSPF anywhere **except C9500**, which
already has `router ospf 1` (`network 0.0.0.0 255.255.255.255 area 0`) + `Loopback0
192.168.2.2` — leave that process untouched.
```
! C9300-24UX  (10.85.134.70)
router ospf 1
 router-id 10.255.0.70
interface Loopback100
 ip address 10.255.0.70 255.255.255.255
 ip ospf 1 area 0
```
```
! C9400  (10.85.134.71)
router ospf 1
 router-id 10.255.0.71
interface Loopback100
 ip address 10.255.0.71 255.255.255.255
 ip ospf 1 area 0
```
```
! C9200  (10.85.134.72)
router ospf 1
 router-id 10.255.0.72
interface Loopback100
 ip address 10.255.0.72 255.255.255.255
 ip ospf 1 area 0
```
```
! C9600  (10.85.134.75)
router ospf 1
 router-id 10.255.0.75
interface Loopback100
 ip address 10.255.0.75 255.255.255.255
 ip ospf 1 area 0
```
```
! C9840 WLC  (10.85.134.83)
router ospf 1
 router-id 10.255.0.83
interface Loopback100
 ip address 10.255.0.83 255.255.255.255
 ip ospf 1 area 0
```
```
! C9500  (10.85.134.95) — special: do NOT modify its existing "router ospf 1".
! Its match-all network statement auto-includes this loopback in area 0.
interface Loopback100
 ip address 10.255.0.95 255.255.255.255
```
Rollback (control-plane only): `no interface Loopback100` on all 6; plus
`no router ospf 1` on the five (NOT C9500 — leave its existing OSPF).

### Phase 1 — APPLIED & SAVED (2026-08-02): routing protocols + platform limits
OSPF (Phase 1a) applied+saved on the 5 routing-capable devices. A follow-up pass
added **ISIS + EIGRP + BGP** (loopback/control-plane only) — applied+saved on the
**4 switches**; `bgp-oper` populates on C9500 via a real (idle) neighbor. Exact
CLI added per switch (octet = last IP digit):
```
router isis
 net 49.0001.0000.0000.00<oct>.00
 is-type level-2-only
interface Loopback100
 ip router isis
router eigrp 1
 network 10.255.0.<oct> 0.0.0.0
router bgp 65000
 bgp router-id 10.255.0.<oct>
 neighbor 10.255.0.254 remote-as 65000        ! dummy -> populates bgp-oper, never establishes
 address-family ipv4 unicast
  neighbor 10.255.0.254 activate
```
Rollback: `no router isis` / `no router eigrp 1` / `no router bgp 65000` + `no ip router isis` on Loopback100.

**Platform capability matrix (verified on the devices):**
| Device | OSPF | ISIS | EIGRP | BGP | Notes |
|---|---|---|---|---|---|
| C9300 / C9400 / C9500 / C9600 | ✅ | ✅ | ✅ | ✅ | full routing |
| **C9840 WLC (.83)** | ✅ | ❌ | ❌ | ❌ | **wireless controller — OSPF only**; `router isis/eigrp/bgp` = *Invalid input* |
| **C9200L (.72)** | ❌ | ❌ | ❌ | ❌ | **C9200L has no routing / no Loopback** interfaces at all |

**Result (oper modules now returning data):** `ospf-oper` 5/5; `isis-oper` 4/5;
`eigrp-oper` 4/5; `bgp-oper` on C9500 (idle neighbor). An *established* BGP
session (richer bgp-oper) needs two BGP-capable, same-VRF, mutually-reachable
peers — deferred to Phase 1b (a spare link).

### Phase 1b reference config (DEFERRED — do NOT apply without a spare cable)
The routed-`/31` + iBGP blocks below are kept only as the design for when a
dedicated spare link exists. **Never convert `Te1/0/3`/`Te0/0/0`** (C9800 mgmt
Vlan311 + CAPWAP ride them).
```
! --- C9300-24UX (.70) ONLY: routed p2p toward C9800 on Te1/0/3 ---
! PRE-CHECK: confirm Te1/0/3 is a plain data link to C9800 Te0/0/0 and is NOT in
! the management VLAN and NOT trunking the mgmt subnet (it bridges no mgmt).
interface TenGigabitEthernet1/0/3
 no switchport
 ip address 10.254.0.0 255.255.255.254
 ip ospf network point-to-point
 ip ospf 1 area 0
!
router bgp 65000
 bgp router-id 10.255.0.70
 neighbor 10.255.0.83 remote-as 65000
 neighbor 10.255.0.83 update-source Loopback100
 address-family ipv4 unicast
  neighbor 10.255.0.83 activate
```
```
! --- C9840 WLC (.83) ONLY: routed p2p toward C9300 on Te0/0/0 ---
! PRE-CHECK: confirm C9800 management (10.85.134.83) is via GigabitEthernet0
! (OOB / Mgmt-vrf) and does NOT traverse Te0/0/0. If mgmt rides Te0/0/0, DO NOT
! convert it — do loopback-only for C9800 and skip the adjacency.
interface TenGigabitEthernet0/0/0
 no switchport
 ip address 10.254.0.1 255.255.255.254
 ip ospf network point-to-point
 ip ospf 1 area 0
!
router bgp 65000
 bgp router-id 10.255.0.83
 neighbor 10.255.0.70 remote-as 65000
 neighbor 10.255.0.70 update-source Loopback100
 address-family ipv4 unicast
  neighbor 10.255.0.70 activate
```

**Pre-flight gates (must all pass before applying Phase 1a).**
- [ ] Confirm out-of-band **console** access to all 6 (recovery path if a box drops).
- [ ] Back up `show running-config` from each device to a gitignored file (exact
      config, so rollback restores the original — not just `default`).
- [ ] Confirm `Loopback100` is unused on all 6; confirm `10.255.0.0/24` doesn't
      collide with lab/fabric ranges.
- [ ] Use interface-level `ip ospf 1 area 0` on the **loopback only** — no
      `network` statements, so no data/fabric/mgmt interface is pulled into OSPF.
- [ ] Do NOT touch any port, VLAN, or SVI (esp. `Vlan311`, the hub mgmt ports
      `Te1/0/9/10/13/24`, or any Meraki/fabric device).

**Phase 1b gates (DEFERRED — only after a dedicated spare cable exists).**
- [ ] A NEW physical link between two of our devices that carries **no** mgmt/
      CAPWAP/fabric traffic (e.g. C9600 `Te0/1` → a free hub data port).
- [ ] Never convert `Te1/0/3` / `Te0/0/0` (C9800 mgmt Vlan311 + CAPWAP ride them).

**Apply / verify / rollback (Phase 1a).**
- Apply via netmiko `send_config_set`, **one device at a time**; re-verify RESTCONF
  (mgmt) reachability after EACH device before continuing.
- Verify: RESTCONF GET `Cisco-IOS-XE-ospf-oper:ospf-oper-data` returns the process
  + `Loopback100` in area 0 (`show ip ospf interface brief`).
- Rollback: `no router ospf 1`, `no interface Loopback100` (control-plane only;
  nothing else changed).
- `write memory` only after health + reachability confirmed on all 6.

**Expected coverage delta.** `oper`: `+ospf`, `+bgp` (and `rib`/`rpl` may
populate); confirm with `depth_probe --discover --category oper` + the
`captured_modules` before/after. Record in the Iteration log.

## Iteration log (fill one row per cycle)
| # | Date | Phase / family | Device(s) | Config summary | `captured_modules` before → after | New modules populated | Device healthy? | Commit |
|---|------|----------------|-----------|----------------|-----------------------------------|-----------------------|-----------------|--------|
| 0 | 2026-07 | 0 · SNMP→RESTCONF MIB bridge | all 6 | `snmp-server community`, `snmp ifmib ifindex persist`, `netconf-yang cisco-ia snmp-community-string` | mib 62 → 96 | MIB models | yes | shipped |
| 1 | 2026-08-02 | 1a · OSPF (loopback) | C9300/C9400/C9600/C9840/C9500 | `router ospf 1` + `Loopback100` in area 0 (C9500 uses existing OSPF) | ospf-oper 0→5 devices | `ospf-oper` | yes, no outage | saved (not yet collected) |
| 2 | 2026-08-02 | 1 · ISIS+EIGRP+BGP (loopback) | C9300/C9400/C9600/C9500 (switches) | `router isis`/`eigrp 1`/`bgp 65000` on loopback | isis/eigrp 0→4, bgp-oper 0→1 (C9500, idle) | `isis-oper`,`eigrp-oper`,`bgp-oper` | yes, no outage | saved (not yet collected) |

> **Not yet re-collected** (per decision 2026-08-02): the config is applied+saved
> on-device, but the published live-data has NOT been refreshed to capture these
> new oper modules. Run `scripts/refresh_live_data.py --version 26.1.1 --capture`
> when ready to bank the coverage.
>
> **Platform limits found:** C9200L has no routing/loopback; C9840 WLC is
> OSPF-only. Those routing modules will never populate there.
>
> **Wireless:** 22/36 wireless oper modules are ALREADY captured (3 APs joined).
> The 14 remaining need lab hardware/active state and are **not** a config win:
> `wireless-client-oper` needs an associated client (0 now); `rfid`/`ble-mgmt`/
> `location` need tags/BLE; `mesh-oper` needs a mesh AP; the rest are niche
> features. Mark these **not-feasible-in-this-lab** unless hardware is added.

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
