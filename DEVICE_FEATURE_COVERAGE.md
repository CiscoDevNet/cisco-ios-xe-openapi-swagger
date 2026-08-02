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
