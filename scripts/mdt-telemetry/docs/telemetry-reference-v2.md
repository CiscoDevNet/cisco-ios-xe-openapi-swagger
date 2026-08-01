# Catalyst 9300 MDT Telemetry Reference

Unified reference for the Catalyst 9300 MDT telemetry pipeline: 65 YANG operational models (48 validated core + 9 native IOS XE expansion + 8 validated platform expansion) streamed via gRPC dial-out through an OpenTelemetry Collector into a Splunk Metrics Index.

This document merges the engineering feature plan, dashboard product requirements, and feature enablement guide into a single per-feature reference.

**Platform:** Catalyst 9000 family (C9200, C9300, C9400, C9500, C9600; IOS XE 17.18+)
**Pipeline:** gRPC kvGPB dial-out → `cisco_mdt` OTel receiver → Splunk HEC → Metrics Index `cisco_mdt`
**Subscriptions:** 66 total — 4 HOT (30s) · 29 WARM (60s) · 33 COOL (300s)

---

## Table of Contents

- [Part I: Feature Enablement Model](#part-i-feature-enablement-model)
  - [1.1 Five-State Model](#11-five-state-model)
  - [1.2 Deployment Profiles](#12-deployment-profiles)
    - [Profile A: Baseline Pack](#profile-a-baseline-pack)
    - [Profile B: Feature-Activated Pack](#profile-b-feature-activated-pack)
  - [1.3 Feature Dependency and Risk Classes](#13-feature-dependency-and-risk-classes)
    - [Feature Dependency Classes](#feature-dependency-classes)
    - [Automation Risk Classes](#automation-risk-classes)
- [Part II: Dashboard Design](#part-ii-dashboard-design)
  - [2.1 Overview Dashboard](#21-overview-dashboard)
  - [2.2 Domain Map](#22-domain-map)
  - [2.3 Global Requirements](#23-global-requirements)
    - [Multi-Device Support](#multi-device-support)
    - [Naming and Traceability](#naming-and-traceability)
    - [Metric Tiering](#metric-tiering)
    - [Visualization Guidance](#visualization-guidance)
- [Part III: Feature Reference](#part-iii-feature-reference)
  - [§1. CPU Utilization](#§1-cpu-utilization)
  - [§2. Memory Statistics](#§2-memory-statistics)
  - [§3. Process Memory](#§3-process-memory)
  - [§4. System DRAM (Platform Software)](#§4-system-dram-platform-software)
  - [§5. Environment Sensors (Temperature, Fan, Power Supply)](#§5-environment-sensors-temperature-fan-power-supply)
  - [§6. Power over Ethernet (PoE)](#§6-power-over-ethernet-poe)
  - [§7. Interface Statistics](#§7-interface-statistics)
  - [§8. Spanning Tree Protocol (STP)](#§8-spanning-tree-protocol-stp)
  - [§9. Stack Health](#§9-stack-health)
  - [§10. VLANs](#§10-vlans)
  - [§11. MAC Address Table (MATM)](#§11-mac-address-table-matm)
  - [§12. ARP Table](#§12-arp-table)
  - [§13. LLDP Neighbors](#§13-lldp-neighbors)
  - [§14. CDP Neighbors](#§14-cdp-neighbors)
  - [§15. Platform Components](#§15-platform-components)
  - [§16. Device Hardware (Uptime, SW Version, Boot Time)](#§16-device-hardware-uptime-sw-version-boot-time)
  - [§17. Switchport](#§17-switchport)
  - [§18. Transceiver / Optics](#§18-transceiver-optics)
  - [§19. UDLD](#§19-udld)
  - [§20. 802.1X / Identity Sessions](#§20-8021x-identity-sessions)
  - [§21. TCAM Utilization](#§21-tcam-utilization)
  - [§22. MDT Subscription Health](#§22-mdt-subscription-health)
  - [§23. Software Install](#§23-software-install)
  - [§24. BGP State](#§24-bgp-state)
  - [§25. OSPF State](#§25-ospf-state)
  - [§26. IETF Routing Table (RIB)](#§26-ietf-routing-table-rib)
  - [§27. DHCP Pool Stats](#§27-dhcp-pool-stats)
  - [§28. High Availability State](#§28-high-availability-state)
  - [§29. Linecard Status](#§29-linecard-status)
  - [§30. TrustSec (SGT/SXP)](#§30-trustsec-sgtsxp)
  - [§31. LACP / Port-Channel (via interfaces-oper)](#§31-lacp-port-channel-via-interfaces-oper)
  - [§32. ACL Hit Counters](#§32-acl-hit-counters)
  - [§33. NTP Synchronization](#§33-ntp-synchronization)
  - [§34. BFD Sessions](#§34-bfd-sessions)
  - [§35. HSRP State](#§35-hsrp-state)
  - [§36. VRRP State](#§36-vrrp-state)
  - [§37. Flexible NetFlow / Flow Monitor](#§37-flexible-netflow-flow-monitor)
  - [§38. IP SLA Probes](#§38-ip-sla-probes)
  - [§39. AAA / RADIUS / TACACS Statistics](#§39-aaa-radius-tacacs-statistics)
  - [§40. Port Security](#§40-port-security)
  - [§41. MACsec / MKA Encryption](#§41-macsec-mka-encryption)
  - [§42. VRF Operational State](#§42-vrf-operational-state)
  - [§43. Data Plane Resources (TCAM/EM per Feature)](#§43-data-plane-resources-tcamem-per-feature)
  - [§44. CPU Punt/Inject Counters](#§44-cpu-puntinject-counters)
  - [§45. PoE Health (Detailed Port-Level)](#§45-poe-health-detailed-port-level)
  - [§46. CEF / FIB State](#§46-cef-fib-state)
  - [§47. EIGRP Routing (if applicable)](#§47-eigrp-routing-if-applicable)
  - [§48. IS-IS Routing (if applicable)](#§48-is-is-routing-if-applicable)
  - [§49. BGP Neighbor Detail](#§49-bgp-neighbor-detail)
  - [§50. BGP RIB Detail](#§50-bgp-rib-detail)
  - [§51. High-Scale ARP](#§51-high-scale-arp)
  - [§52. IPv6 Neighbor Discovery](#§52-ipv6-neighbor-discovery)
  - [§53. IS-IS Interface Detail](#§53-is-is-interface-detail)
  - [§54. Multicast Routing State](#§54-multicast-routing-state)
  - [§55. Stack Member / Stackwise Virtual Detail](#§55-stack-member-stackwise-virtual-detail)
  - [§56. Tunnel Interface State](#§56-tunnel-interface-state)
  - [§57. YANG Management Plane Interfaces](#§57-yang-management-plane-interfaces)
  - [§59. PIM Multicast State](#§59-pim-multicast-state)
  - [§60. MPLS LDP Operational State](#§60-mpls-ldp-operational-state)
  - [§61. MPLS Forwarding (LFIB)](#§61-mpls-forwarding-lfib)
  - [§62. LISP Operational State](#§62-lisp-operational-state)
  - [§63. VXLAN NVE Tunnel Endpoints](#§63-vxlan-nve-tunnel-endpoints)
  - [§64. EVPN Operational State](#§64-evpn-operational-state)
  - [§65. PTP / SyncE Timing](#§65-ptp-synce-timing)
  - [§67. IETF Interfaces Operational State](#§67-ietf-interfaces-operational-state)
- [Part IV: IOS XE Subscription Configuration](#part-iv-ios-xe-subscription-configuration)
  - [Subscription Summary Table](#subscription-summary-table)
  - [Recommended Polling Intervals](#recommended-polling-intervals)
  - [On-Change Capable Features](#on-change-capable-features)
  - [Reference Links](#reference-links)
- [Part V: Domain Requirements](#part-v-domain-requirements)
  - [1. System Health](#1-system-health)
  - [2. Environment and Power](#2-environment-and-power)
  - [3. Interfaces](#3-interfaces)
  - [4. L2 Topology](#4-l2-topology)
  - [5. L3 Routing](#5-l3-routing)
  - [6. Security and Identity](#6-security-and-identity)
  - [7. Network Services](#7-network-services)
  - [8. Platform and Resources](#8-platform-and-resources)
  - [9. Operations](#9-operations)
- [Part VI: Lab Topology and Activation Runbook](#part-vi-lab-topology-and-activation-runbook)
  - [Lab Topology Assumptions](#lab-topology-assumptions-for-this-project)
  - [Recommended Lab VLAN and Address Plan](#recommended-lab-vlan-and-address-plan)
  - [Recommended Per-Device Configuration Model](#recommended-per-device-configuration-model)
  - [Recommended Minimum Lab CLI Patterns](#recommended-minimum-lab-cli-patterns)
  - [Ordered Lab Activation Runbook](#ordered-lab-activation-runbook)
  - [Feature-Specific Reality Notes](#feature-specific-reality-notes-for-this-lab)
  - [YANG Structure to Splunk Field Mapping Guide](#yang-structure-to-splunk-field-mapping-guide)
- [Appendix A: LLM Execution Contract](#appendix-a-llm-execution-contract)
  - [Recommended Interpretation Rules for Empty Data](#recommended-interpretation-rules-for-empty-data)
- [Appendix B: Repo Example Coverage Audit](#appendix-b-repo-example-coverage-audit)
  - [Subscription Matrix](#subscription-matrix)


## Part I: Feature Enablement Model

### 1.1 Five-State Model

| State | Meaning | LLM Interpretation |
|---|---|---|
| Available | The model exists on the platform and release. | Feature is technically supported. |
| Subscribed | The telemetry subscription is configured and valid. | Transport path is ready. |
| Enabled | The switch feature has been configured locally. | The switch is prepared to generate state. |
| Active | The feature has live operational context such as a peer, endpoint, service, or traffic. | Telemetry should now become non-empty or materially richer. |
| Validated | CLI and telemetry both confirm the feature is producing useful data. | Safe to recommend charts, panels, and verification logic. |

`Subscribed` is not enough. `Enabled` is not always enough. The desired state for most feature-dependent telemetry is `Validated`.

### 1.2 Deployment Profiles

### Profile A: Baseline Pack

Profile A is the subscription and dashboard set that should work on most Catalyst 9300 devices without deliberate feature-specific configuration.

This is the default pack that should be enabled first in any new lab or new device onboarding workflow.

#### Baseline Feature Set

| § | Feature | Reason |
|---|---|---|
| 1 | CPU Utilization | Always present on a running switch. |
| 2 | Memory Statistics | Always present on a running switch. |
| 3 | Process Memory | Always present on a running switch. |
| 4 | System DRAM | Always present on a running switch. |
| 5 | Environment Sensors | Normally available without extra feature configuration. |
| 7 | Interface Statistics | Normally available without extra feature configuration. |
| 15 | Platform Components | Normally available without extra feature configuration. |
| 16 | Device Hardware | Normally available without extra feature configuration. |
| 21 | TCAM Utilization | Typically available without explicit feature activation. |
| 22 | MDT Subscription Health | Required to validate telemetry itself. |
| 43 | Data Plane Resources | Typically available without explicit feature activation. |
| 44 | CPU Punt/Inject Counters | Typically available without explicit feature activation. |

#### Extended Baseline Feature Set

These features are usually available in a normal campus-switch lab, but not universally useful on every device.

| § | Feature | Why It Is Extended Instead of Core Baseline |
|---|---|---|
| 6 | PoE | Requires PoE-capable hardware and usually powered endpoints. |
| 8 | STP | Often useful, but topology dependent. |
| 10 | VLANs | Usually present, but low-value in very small labs. |
| 11 | MAC Address Table | Needs active L2 endpoints and traffic. |
| 12 | ARP Table | Needs active L3 interfaces and neighboring hosts. |
| 14 | CDP Neighbors | Depends on live Cisco neighbors. |
| 17 | Switchport | Depends on L2 access-port usage. |
| 18 | Transceiver / Optics | Depends on pluggables and active links. |
| 46 | CEF / FIB State | Usually present, but more meaningful in a routed environment. |

### Profile B: Feature-Activated Pack

Profile B includes features whose telemetry should be expected to remain empty or low-value until the underlying function is configured and active.

This profile should be enabled selectively.

It is the right model for:

- protocol-specific demonstrations
- focused validation for a feature such as BGP or MACsec
- labs where an LLM is asked to activate a feature and then prove telemetry changed meaningfully

### 1.3 Feature Dependency and Risk Classes

## Feature Dependency Classes

Each feature should be assigned one primary dependency class.

| Class | Meaning | Typical Trigger |
|---|---|---|
| Baseline | No extra config beyond normal operation | Device boots and telemetry is enabled |
| Hardware-Conditional | Depends on hardware role, module, or platform form factor | PoE-capable switch, stack member, modular platform |
| Peer-Dependent | Requires a live peer, adjacency, second switch, or remote endpoint | BGP, OSPF, HSRP, VRRP, LACP, MACsec |
| Service-Dependent | Requires reachable external infrastructure | NTP, RADIUS, TACACS+, identity services |
| Traffic-Dependent | Counters are only meaningful when traffic or endpoints exist | ACL hits, Flow Monitor, Port Security |
| Feature-Only | Can be enabled locally on a single switch without external infrastructure, though a consumer may improve realism | DHCP pool, IP SLA, VRF |

## Automation Risk Classes

Not every feature should be handled the same way by automation.

| Risk Class | Meaning | Examples |
|---|---|---|
| Low | Safe to enable in a lab with limited blast radius | NTP, DHCP pool in a lab VLAN, IP SLA, VRF, ACL counters |
| Medium | Requires peer awareness or topology awareness | BGP, OSPF, HSRP, VRRP, LACP, UDLD, BFD |
| High | Can affect access control, trust, encryption, or identity | AAA, 802.1X, TrustSec, MACsec |
| Discover-Only | Should usually be detected rather than force-enabled | PoE health, stack, linecard, HA |

---

## Part II: Dashboard Design

### 2.1 Overview Dashboard

The overview dashboard should answer: is the device healthy, is telemetry working, and where should the operator drill next?

The overview should contain only Must-Have signals and summary panels.

Required overview content:

- Device identity and platform banner from Device Hardware and Platform Components
- CPU summary from §1
- Memory and DRAM summary from §2 and §4
- Environment summary from §5
- PoE summary from §6 where relevant
- Interface health summary from §7
- Stack or platform readiness summary from §9 and §28 where applicable
- Routing summary from §24, §25, and §26 when present
- MDT subscription health from §22
- High-level security or access-session summary from §20 and §41 when present

Overview panel types should favor:

- single-value cards
- gauges
- compact trend charts
- summary tables
- status indicators

The overview is not the place for large inventory tables or deep troubleshooting views.

### 2.2 Domain Map

### Drill-Down Dashboard Domains

The requirements should be organized into these drill-down domains:

| Domain | Features Included |
|---|---|
| System Health | §1 CPU, §2 Memory, §3 Process Memory, §4 DRAM |
| Environment and Power | §5 Environment, §6 PoE, §45 PoE Health |
| Interfaces | §7 Interfaces, §17 Switchport, §18 Transceiver, §19 UDLD, §31 Port-Channel, §56 Tunnel |
| L2 Topology | §8 STP, §10 VLANs, §11 MAC, §12 ARP, §13 LLDP, §14 CDP, §51 High-Scale ARP, §52 IPv6 ND |
| L3 Routing | §24 BGP, §25 OSPF, §26 RIB, §42 VRF, §46 CEF, §47 EIGRP, §48 IS-IS, §49 BGP Neighbor Detail, §50 BGP RIB Detail, §53 IS-IS Interface Detail, §54 Multicast |
| Security and Identity | §20 802.1X, §30 TrustSec, §32 ACL, §39 AAA, §40 Port Security, §41 MACsec/MKA |
| Network Services | §27 DHCP, §33 NTP, §34 BFD, §35 HSRP, §36 VRRP, §37 Flow Monitor, §38 IP SLA |
| Platform and Resources | §9 Stack, §15 Components, §16 Device Hardware, §21 TCAM, §28 HA, §29 Linecard, §43 DP Resources, §44 Punt/Inject, §55 Stack Member/SVL |
| Operations | §22 MDT Health, §23 Software Install, §57 YANG Management Interfaces |

### 2.3 Global Requirements

## Global Requirements

### Multi-Device Support

All dashboards should be designed for multi-device operation.

Required capabilities:

- device selector dropdown
- filtering by hostname, management IP, or telemetry source identity
- ability to compare one device versus many devices depending on panel type
- panel queries that preserve feature identity and device identity at the same time

### Naming and Traceability

Each major panel or grouped requirement should preserve traceability back to the telemetry source.

Recommended naming pattern:

- include the feature reference number such as `§7`
- use clear operational naming such as `Interface Errors and Discards`
- keep the YANG model visible in the requirements, even if not shown in final panel titles

### Metric Tiering

Each metric should be classified into one of three tiers:

| Tier | Meaning |
|---|---|
| Must-Have | Core operational signal; should appear in the overview or top drill-down panels |
| Nice-to-Have | Useful supporting data; belongs in drill-down dashboards |
| Optional | Deep troubleshooting or inventory detail; may be hidden or deferred |

### Visualization Guidance

Visualization guidance should be specified at requirements time, but treated as directional rather than absolute.

Preferred mapping rules:

- gauges and single values for instantaneous health signals
- time charts for trends, counters, and rates
- tables for inventory, adjacency, neighbors, and membership data
- status indicators for stateful protocols and operational flags
- bar charts for utilization and top-N comparisons

Threshold logic, alerting behavior, and color semantics are not finalized in this phase.

---

## Part III: Feature Reference

Each section contains: metadata, KPI table, Splunk panel description, typed-leaf requirements, and activation guidance where applicable.

### §1. CPU Utilization

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-process-cpu-oper.yang` |
| **XPath** | `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization` |
| **Sub ID** | 30001 |
| **Tier** | HOT (30s) |
| **Domain** | System Health |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| CPU 5-second average | `five-seconds` | gauge (%) | Time chart, single value gauge |
| CPU 1-minute average | `one-minute` | gauge (%) | Time chart overlay |
| CPU 5-minute average | `five-minutes` | gauge (%) | Time chart overlay |

**Splunk Panel:** Time chart showing all three CPU averages over time, per switch. Single-value gauge for current 5-second reading. Alert threshold at >80%.

#### Typed-Leaf Requirements

Root XPath: `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `five-seconds` | percent | Primary current CPU health signal for overview and alerting. |
| `one-minute` | percent | Short smoothing signal for drill-down trend context. |
| `five-minutes` | percent | Long smoothing signal for sustained load context. |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §2. Memory Statistics

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-memory-oper.yang` |
| **XPath** | `/memory-ios-xe-oper:memory-statistics/memory-statistic` |
| **Sub ID** | 60001 |
| **Tier** | WARM (60s) |
| **Domain** | System Health |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Total memory (bytes) | `total-memory` | gauge | Single value (converted to GB) |
| Used memory (bytes) | `used-memory` | gauge | Bar gauge (% of total) |
| Free memory (bytes) | `free-memory` | gauge | Bar gauge |
| Lowest usage ever | `lowest-usage` | gauge | Reference line |
| Memory pool name | `name` (key) | string | Filter/group-by (Processor, lsmpi_io, reserve Processor) |

**Splunk Panel:** Stacked area chart showing used vs free over time for "Processor" pool. Percent utilization gauge. Group by memory pool name.

#### Typed-Leaf Requirements

Root XPath: `/memory-ios-xe-oper:memory-statistics/memory-statistic`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `total-memory` | bytes | Memory pool capacity baseline. |
| `used-memory` | bytes | Current consumed memory in the pool. |
| `free-memory` | bytes | Current available memory in the pool. |
| `lowest-usage` | bytes | Historical low-water reference for capacity analysis. |
| `name` | string | Pool identity, especially Processor versus reserve pools. |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §3. Process Memory

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-process-memory-oper.yang` |
| **XPath** | `/process-memory-ios-xe-oper:memory-usage-processes` |
| **Sub ID** | 30002 |
| **Tier** | HOT (30s) |
| **Domain** | System Health |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Process name | `name` (key) | string | Table column / group-by |
| PID | `pid` (key) | int | Table column |
| Allocated memory | `allocated-memory` | counter | Top-N bar chart |
| Freed memory | `freed-memory` | counter | Comparison chart |
| Holding memory | `holding-memory` | gauge | Top-N bar chart |
| Get buffers | `get-buffers` | counter | Table column |
| Ret buffers | `ret-buffers` | counter | Table column |

**Splunk Panel:** Top 10 processes by `holding-memory`. Allocated vs freed comparison chart. Table of all processes sortable by memory.

#### Typed-Leaf Requirements

Root XPath: `/process-memory-ios-xe-oper:memory-usage-processes`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `name` | string | Process identity for top-N views. |
| `pid` | count | Unique process key for table correlation. |
| `allocated-memory` | counter | Total allocation activity; useful as churn signal. |
| `freed-memory` | counter | Paired with allocated memory to detect churn patterns. |
| `holding-memory` | bytes | Current held memory; primary ranking field for top consumers. |
| `get-buffers` | counter | Buffer request activity for deep troubleshooting. |
| `ret-buffers` | counter | Buffer return activity for deep troubleshooting. |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §4. System DRAM (Platform Software)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-platform-software-oper.yang` |
| **XPath** | `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes` |
| **Sub ID** | 60002 |
| **Tier** | WARM (60s) |
| **Domain** | System Health |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Total DRAM (bytes) | control process memory fields | gauge | Single value (GB) |
| Used DRAM | used memory fields | gauge | Percent gauge |
| Free DRAM | free memory fields | gauge | Time chart |

**Splunk Panel:** System DRAM total/used/free in GB with percentage gauge per switch.

#### Typed-Leaf Requirements

Root XPath: `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `control-process/fru` | string | Control-process location identity (key). |
| `control-process/slot` | count | Slot identity (key). |
| `control-process/bay` | count | Bay identity (key). |
| `control-process/chassis` | count | Chassis identity (key); differentiates stack members. |
| `control-process/memory-stats/memory-status` | string | Memory health state for status panels. |
| `control-process/memory-stats/total` | bytes | Total platform DRAM baseline. |
| `control-process/memory-stats/used-number` | bytes | Used DRAM for platform-level health summary. |
| `control-process/memory-stats/used-percent` | percent | Used DRAM percentage; primary health gauge signal. |
| `control-process/memory-stats/free-number` | bytes | Free DRAM for platform-level health summary. |
| `control-process/memory-stats/free-percent` | percent | Free DRAM percentage. |
| `control-process/memory-stats/committed-number` | bytes | Committed memory for overcommit analysis. |
| `control-process/memory-stats/committed-percent` | percent | Committed memory percentage; alert when >100%. |
| `control-process/control-process-status` | enum | Online/offline status for platform health. |
| `control-process/high-availability-state` | enum | HA role context for multi-chassis views. |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §5. Environment Sensors (Temperature, Fan, Power Supply)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-environment-oper.yang` |
| **XPath** | `/environment-ios-xe-oper:environment-sensors` |
| **Sub ID** | 60003 |
| **Tier** | WARM (60s) |
| **Domain** | Environment and Power |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Sensor name | `name` (key) | string | Table column / filter |
| Sensor location | `location` | string | Group-by (Switch 1, Switch 2...) |
| Current reading | `current-reading` | gauge | Gauge, time chart |
| Sensor units | `sensor-units` | string | Label (celsius, watts, rpm, mV) |
| State | `state` | enum | Status indicator (GREEN/Normal/NotExist) |
| Sensor type name | `sensor-name` | string | Filter (temperature, power, fan) |
| Low critical threshold | `low-critical-threshold` | int | Reference line |
| High critical threshold | `high-critical-threshold` | int | Reference line |
| Low normal threshold | `low-normal-threshold` | int | Reference line |
| High normal threshold | `high-normal-threshold` | int | Reference line |

**Specific sensor names on C9300:**
- **Inlet Temp Sens** — inlet air temperature (Celsius), GREEN/YELLOW/RED
- **Outlet Temp Sen** — exhaust air temperature (Celsius)
- **HotSpot Temp Se** — ASIC hotspot temperature (Celsius)
- **Power Supply A** — PSU A watts, state=Normal/NotExist
- **Power Supply B** — PSU B watts, state=Normal/NotExist
- **FAN - T1 1/2/3** — fan tray temperatures (Celsius)

**Splunk Panel:** Temperature time chart (Inlet/Outlet/HotSpot), PSU wattage gauge with Normal/NotExist status indicator, fan status table. Alert when state != GREEN/Normal.

#### Typed-Leaf Requirements

Root XPath: `/environment-ios-xe-oper:environment-sensors`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `name` | string | Sensor instance identity. |
| `location` | string | Physical context such as member or chassis location. |
| `current-reading` | count | Raw sensor value; interpretation depends on `sensor-units`. |
| `sensor-units` | string | Required unit discriminator such as Celsius, watts, rpm, or mV. |
| `state` | enum | Normal, warning, critical, or missing state for status panels. |
| `sensor-name` | string | Sensor class used to split temperature, fan, or PSU views. |
| `low-critical-threshold` | count | Critical lower bound reference. |
| `high-critical-threshold` | count | Critical upper bound reference. |
| `low-normal-threshold` | count | Normal lower range reference. |
| `high-normal-threshold` | count | Normal upper range reference. |

Requirement note: when `sensor-units` is `celsius`, `current-reading` should be treated as temperature; when it is `watts`, it should be treated as power; when it is `rpm`, it should be treated as fan speed.

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §6. Power over Ethernet (PoE)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-poe-oper.yang` |
| **XPath** | `/poe-ios-xe-oper:poe-oper-data` |
| **Sub ID** | 60004 |
| **Tier** | WARM (60s) |
| **Domain** | Environment and Power |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |
| **Platforms** | C9200/C9300/C9400 PoE-capable models; C9500/C9600 with PoE line cards |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | `poe-port-detail/intf-name` (key) | string | Table column |
| Operational power (mW) | `poe-port-detail/oper-power` | gauge | Bar chart per port |
| Operational state | `poe-port-detail/oper-state` | enum | Status indicator |
| PD class | `poe-port-detail/pd-class` | string | Table column |
| Power used (mW) | `poe-port-detail/power-used` | gauge | Stacked bar chart |
| LLDP power requested | `poe-port-detail/lldp-mdi-rx/power-requested` | gauge | Comparison |
| LLDP power allocated | `poe-port-detail/lldp-mdi-rx/power-allocated` | gauge | Comparison |
| Power priority | `poe-port-detail/lldp-mdi-rx/power-priority` | string | Table column |
| Power source | `poe-port-detail/lldp-mdi-rx/power-source` | string | Table column |
| Power type | `poe-port-detail/lldp-mdi-rx/power-type` | string | Table column |
| PSE max available power | `poe-port-detail/lldp-mdi-rx/pse-max-available-power` | gauge | Reference line |
| Dual-sig power class A/B | `poe-port-detail/lldp-mdi-rx/dual-sig-pwr-class-mode-a/b` | string | Detail table |

**Splunk Panel:** Per-port power consumption bar chart, total switch PoE budget gauge (sum vs max), PoE status table with PD class/priority, power requested vs allocated comparison.
**Reference:** https://grafana.com/grafana/dashboards/17238-catalyst-poe-dashboard/, https://github.com/jeremycohoe/cisco-mdt-poe

#### Typed-Leaf Requirements

Root XPath: `/poe-ios-xe-oper:poe-oper-data`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `poe-port-detail/intf-name` | string | Port identity for per-port PoE panels. |
| `poe-port-detail/oper-power` | milliwatts | Current delivered power. |
| `poe-port-detail/oper-state` | enum | Port power state for health and exception panels. |
| `poe-port-detail/pd-class` | string | Powered-device classification detail. |
| `poe-port-detail/power-used` | milliwatts | Actual consumed power. |
| `poe-port-detail/lldp-mdi-rx/power-requested` | milliwatts | Requested power from LLDP negotiation. |
| `poe-port-detail/lldp-mdi-rx/power-allocated` | milliwatts | Allocated power from LLDP negotiation. |
| `poe-port-detail/lldp-mdi-rx/power-priority` | string | Priority label for oversubscription analysis. |
| `poe-port-detail/lldp-mdi-rx/power-source` | string | Source context for negotiated power. |
| `poe-port-detail/lldp-mdi-rx/power-type` | string | Device or PSE capability descriptor. |
| `poe-port-detail/lldp-mdi-rx/pse-max-available-power` | milliwatts | Maximum power capacity reference for the link. |
| `poe-port-detail/lldp-mdi-rx/dual-sig-pwr-class-mode-a/b` | string | Dual-signature class detail for advanced PoE troubleshooting. |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §7. Interface Statistics

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-interfaces-oper.yang` |
| **XPath** | `/interfaces-ios-xe-oper:interfaces/interface` |
| **Sub ID** | 30003 |
| **Tier** | HOT (30s) |
| **Domain** | Interfaces |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | `name` (key) | string | Filter / group-by |
| Admin status | `admin-status` | enum | Status indicator |
| Oper status | `oper-status` | enum | Status indicator (up/down) |
| Speed (bps) | `speed` | gauge | Table column |
| IP address | `ipv4` | string | Table column |
| Physical address | `phys-address` | string | Table column |
| **RX rate (Kbps)** | `statistics/rx-kbps` | gauge | **Time chart** |
| **TX rate (Kbps)** | `statistics/tx-kbps` | gauge | **Time chart** |
| **RX rate (pps)** | `statistics/rx-pps` | gauge | Time chart |
| **TX rate (pps)** | `statistics/tx-pps` | gauge | Time chart |
| In octets | `statistics/in-octets` | counter | Derivative for bps |
| Out octets | `statistics/out-octets` | counter | Derivative for bps |
| In unicast pkts | `statistics/in-unicast-pkts` | counter | Table |
| In broadcast pkts | `statistics/in-broadcast-pkts` | counter | Table |
| In multicast pkts | `statistics/in-multicast-pkts` | counter | Table |
| Out unicast/broadcast/multicast | `statistics/out-*-pkts` | counter | Table |
| **In errors** | `statistics/in-errors` | counter | **Alert panel** |
| **In CRC errors** | `statistics/in-crc-errors` | counter | **Alert panel** |
| **In discards** | `statistics/in-discards` | counter | **Alert panel** |
| Out errors | `statistics/out-errors` | counter | Alert panel |
| Out discards | `statistics/out-discards` | counter | Alert panel |
| **Num flaps** | `statistics/num-flaps` | counter | **Single value / alert** |
| Interface type | `interface-type` | enum | Filter |
| **Ether state** (17.14+) | `ether-state/negotiated-duplex-mode`, `negotiated-port-speed`, `media-type`, `auto-negotiate`, `enable-flow-control` | various | Detail table |
| **Ether stats** (17.14+) | `ether-stats/in-mac-pause-frames`, `in-8021q-frames`, `in-jabber-frames`, `in-oversize-frames`, `in-fragment-frames` | counter | Detail table |
| **Dot3 error counters** (17.14+) | `dot3-error-counters-v2/dot3-fcs-errors`, `dot3-alignment-errors`, `dot3-late-collisions`, `dot3-symbol-errors`, etc. | counter | Error detail table |

**Splunk Panel:** RX/TX Kbps time chart per interface, RX/TX pps time chart, error/discard counters with alert thresholds, interface status table (up/down/flaps), top-N by traffic volume.

#### Typed-Leaf Requirements

Root XPath: `/interfaces-ios-xe-oper:interfaces/interface`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `name` | string | Primary interface key. |
| `admin-status` | enum | Administrative intent state. |
| `oper-status` | enum | Actual link state. |
| `speed` | count | Interface speed in bps. |
| `ipv4` | string | L3 identity context where present. |
| `phys-address` | string | MAC address inventory field. |
| `statistics/rx-kbps` | count | Current inbound throughput. |
| `statistics/tx-kbps` | count | Current outbound throughput. |
| `statistics/rx-pps` | count | Current inbound packet rate. |
| `statistics/tx-pps` | count | Current outbound packet rate. |
| `statistics/in-octets` | counter | Source counter for rate calculation and long-term volume. |
| `statistics/out-octets` | counter | Source counter for rate calculation and long-term volume. |
| `statistics/in-errors` | counter | Primary inbound health exception metric. |
| `statistics/in-crc-errors` | counter | Physical-layer error indicator. |
| `statistics/in-discards` | counter | Congestion or policy-drop indicator. |
| `statistics/out-errors` | counter | Outbound error indicator. |
| `statistics/out-discards` | counter | Outbound congestion or policy-drop indicator. |
| `statistics/num-flaps` | counter | Link stability indicator. |
| `interface-type` | enum | Media or interface family filter. |
| `ether-state/...` | enum and count | Negotiation, duplex, and media details for deep drill-down. |
| `ether-stats/...` | counter | Additional Ethernet framing and pause counters. |
| `dot3-error-counters-v2/...` | counter | IEEE 802.3 physical error detail. |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §8. Spanning Tree Protocol (STP)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-spanning-tree-oper.yang` |
| **XPath** | `/stp-ios-xe-oper:stp-details` |
| **Sub ID** | 60005 |
| **Tier** | WARM (60s) |
| **Domain** | L2 Topology |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| STP instance | `stp-detail/instance` (key) | int | Group-by |
| Designated root address | `stp-detail/designated-root-address` | string | Table |
| Designated root priority | `stp-detail/designated-root-priority` | int | Table |
| Root cost | `stp-detail/root-cost` | int | Table |
| Root port | `stp-detail/root-port` | string | Table |
| **Interface name** | `stp-detail/interfaces/interface/name` (key) | string | Table row |
| **Port role** | `stp-detail/interfaces/interface/role` | enum | **Status indicator** (root/designated/alternate/backup) |
| **Port state** | `stp-detail/interfaces/interface/state` | enum | **Status indicator** (forwarding/blocking/listening/learning) |
| Port cost | `stp-detail/interfaces/interface/cost` | int | Table |
| Port priority | `stp-detail/interfaces/interface/port-priority` | int | Table |
| **BPDU sent** | `stp-detail/interfaces/interface/bpdu-sent` | counter | Time chart |
| **BPDU received** | `stp-detail/interfaces/interface/bpdu-received` | counter | Time chart |
| BPDU guard | `stp-detail/interfaces/interface/bpdu-guard` | enum | Status indicator |
| BPDU filter | `stp-detail/interfaces/interface/bpdu-filter` | enum | Table |
| Forward transitions | `stp-detail/interfaces/interface/forward-transitions` | counter | **Alert** (topology change) |
| Guard type | `stp-detail/interfaces/interface/guard` | enum | Table |
| Designated bridge address/priority | `stp-detail/interfaces/interface/designated-bridge-*` | various | Table |

**Splunk Panel:** STP instance overview table (root bridge, root port), per-port state/role status grid (color-coded: forwarding=green, blocking=orange), BPDU counters time chart, alert on forward-transitions increment (topology change detected).

#### Typed-Leaf Requirements

Root XPath: `/stp-ios-xe-oper:stp-details`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `stp-detail/instance` (key) | int | STP instance |
| `stp-detail/designated-root-address` | string | Designated root address |
| `stp-detail/designated-root-priority` | int | Designated root priority |
| `stp-detail/root-cost` | int | Root cost |
| `stp-detail/root-port` | string | Root port |
| `stp-detail/interfaces/interface/name` (key) | string | **Interface name** |
| `stp-detail/interfaces/interface/role` | enum | **Port role** |
| `stp-detail/interfaces/interface/state` | enum | **Port state** |
| `stp-detail/interfaces/interface/cost` | int | Port cost |
| `stp-detail/interfaces/interface/port-priority` | int | Port priority |
| `stp-detail/interfaces/interface/bpdu-sent` | counter | **BPDU sent** |
| `stp-detail/interfaces/interface/bpdu-received` | counter | **BPDU received** |
| `stp-detail/interfaces/interface/bpdu-guard` | enum | BPDU guard |
| `stp-detail/interfaces/interface/bpdu-filter` | enum | BPDU filter |
| `stp-detail/interfaces/interface/forward-transitions` | counter | Forward transitions |
| `stp-detail/interfaces/interface/guard` | enum | Guard type |
| `stp-detail/interfaces/interface/designated-bridge-*` | various | Designated bridge address/priority |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §9. Stack Health

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-stack-oper.yang` |
| **XPath** | `/stack-ios-xe-oper:stack-oper-data` |
| **Sub ID** | 60006 |
| **Tier** | WARM (60s) |
| **Domain** | Platform and Resources |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |
| **Platforms** | C9200/C9300 stackable models only; C9400/C9500/C9600 do not stack |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Chassis number | `stack-node/chassis-number` (key) | int | Table row |
| **Role** | `stack-node/role` | enum | **Status indicator** (Active/Standby/Member) |
| **Node state** | `stack-node/node-state` | enum | **Status indicator** (Ready/NotReady) |
| Priority | `stack-node/priority` | int (1-15) | Table |
| Serial number | `stack-node/serial-number` | string | Table (asset tracking) |
| MAC address | `stack-node/mac-address` | string | Table |
| Reload reason | `stack-node/reload-reason` | string | Table |
| SSO ready flag | `stack-node/sso-ready-flag` | bool | Status indicator |
| Stack mode | `stack-node/stack-mode` | enum | Table |
| Interface MTU | `stack-node/interface-mtu` | int | Table |
| Latency | `stack-node/latency` | int | Time chart |
| **Stack port number** | `stack-node/stack-ports/port-num` | int | Table |
| **Stack port state** | `stack-node/stack-ports/port-state` | enum | Status indicator |
| Stack port neighbor switch | `stack-node/stack-ports/switch-nbr-port` | string | Table |
| **KA sent** | `stack-node/keepalive-counters/sent` | counter | Time chart |
| **KA received** | `stack-node/keepalive-counters/received` | counter | Time chart |
| KA sent failure | `stack-node/keepalive-counters/sent-failure` | counter | Alert |
| KA receive failure | `stack-node/keepalive-counters/receive-failure` | counter | Alert |
| KA consecutive losses | `stack-node/keepalive-counters/consecutive-losses` | counter | **Alert** |
| **Stack port stats** | `stack-node/stack-ports/sp-stats/rac-data-crc-err`, `rac-invalid-ringword-err`, `rac-pcs-codeword-err`, `rac-rwcrc-err` | counter | Error alert panel |

**Splunk Panel:** Stack member overview table (chassis, role, state, priority, serial), stack port status grid, keepalive counters time chart, alert on consecutive-losses > 0 or port-state != Up.

#### Typed-Leaf Requirements

Root XPath: `/stack-ios-xe-oper:stack-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `stack-node/chassis-number` (key) | int | Chassis number |
| `stack-node/role` | enum | **Role** |
| `stack-node/node-state` | enum | **Node state** |
| `stack-node/priority` | int (1-15) | Priority |
| `stack-node/serial-number` | string | Serial number |
| `stack-node/mac-address` | string | MAC address |
| `stack-node/reload-reason` | string | Reload reason |
| `stack-node/sso-ready-flag` | bool | SSO ready flag |
| `stack-node/stack-mode` | enum | Stack mode |
| `stack-node/interface-mtu` | int | Interface MTU |
| `stack-node/latency` | int | Latency |
| `stack-node/stack-ports/port-num` | int | **Stack port number** |
| `stack-node/stack-ports/port-state` | enum | **Stack port state** |
| `stack-node/stack-ports/switch-nbr-port` | string | Stack port neighbor switch |
| `stack-node/keepalive-counters/sent` | counter | **KA sent** |
| `stack-node/keepalive-counters/received` | counter | **KA received** |
| `stack-node/keepalive-counters/sent-failure` | counter | KA sent failure |
| `stack-node/keepalive-counters/receive-failure` | counter | KA receive failure |
| `stack-node/keepalive-counters/consecutive-losses` | counter | KA consecutive losses |
| `stack-node/stack-ports/sp-stats/rac-data-crc-err`, `rac-invalid-ringword-err`, `rac-pcs-codeword-err`, `rac-rwcrc-err` | counter | **Stack port stats** |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §10. VLANs

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-vlan-oper.yang` |
| **XPath** | `/vlan-ios-xe-oper:vlans` |
| **Sub ID** | 50001 |
| **Tier** | COOL (300s) |
| **Domain** | L2 Topology |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VLAN ID | `vlan/id` (key) | int | Table row |
| VLAN name | `vlan/name` | string | Table column |
| VLAN status | `vlan/status` | enum (active/suspended) | Status indicator |
| Member interfaces | `vlan/vlan-interfaces/interface` | list | Table column (comma-separated) |

**Splunk Panel:** VLAN inventory table with member port count, active/suspended status indicators per switch.

#### Typed-Leaf Requirements

Root XPath: `/vlan-ios-xe-oper:vlans`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `vlan/id` (key) | int | VLAN ID |
| `vlan/name` | string | VLAN name |
| `vlan/status` | enum (active/suspended) | VLAN status |
| `vlan/vlan-interfaces/interface` | list | Member interfaces |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §11. MAC Address Table (MATM)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-matm-oper.yang` |
| **XPath** | `/matm-ios-xe-oper:matm-oper-data` |
| **Sub ID** | 50002 |
| **Tier** | COOL (300s) |
| **Domain** | L2 Topology |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VLAN ID | `matm-table/vlan-id-number` (key) | int | Group-by |
| Table type | `matm-table/table-type` | string | Filter |
| Aging time | `matm-table/aging-time` | int | Table column |
| MAC address | `matm-table/matm-mac-entry/mac` (key) | string | Table row |
| Entry type | `matm-table/matm-mac-entry/mat-addr-type` | enum (static/dynamic) | Table column |
| Port | `matm-table/matm-mac-entry/port` | string | Table column |

**Splunk Panel:** MAC table entry count per VLAN (bar chart), MAC table total size (single value), table of MAC entries (filterable by VLAN).

#### Typed-Leaf Requirements

Root XPath: `/matm-ios-xe-oper:matm-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `matm-table/vlan-id-number` (key) | int | VLAN ID |
| `matm-table/table-type` | string | Table type |
| `matm-table/aging-time` | int | Aging time |
| `matm-table/matm-mac-entry/mac` (key) | string | MAC address |
| `matm-table/matm-mac-entry/mat-addr-type` | enum (static/dynamic) | Entry type |
| `matm-table/matm-mac-entry/port` | string | Port |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §12. ARP Table

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-arp-oper.yang` |
| **XPath** | `/arp-ios-xe-oper:arp-data` |
| **Sub ID** | 50003 |
| **Tier** | COOL (300s) |
| **Domain** | L2 Topology |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VRF name | `arp-vrf/vrf` (key) | string | Filter |
| IP address | `arp-vrf/arp-entry/address` (key) | string | Table row |
| MAC address | `arp-vrf/arp-entry/hardware` | string | Table column |
| Interface | `arp-vrf/arp-entry/interface` | string | Table column |
| Entry type | `arp-vrf/arp-entry/mode` | enum (dynamic/static) | Table column |
| Entry time | `arp-vrf/arp-entry/time` | string | Table column |

**Splunk Panel:** ARP entry count per VRF (single value), ARP table browser with search.

#### Typed-Leaf Requirements

Root XPath: `/arp-ios-xe-oper:arp-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `arp-vrf/vrf` (key) | string | VRF name |
| `arp-vrf/arp-entry/address` (key) | string | IP address |
| `arp-vrf/arp-entry/hardware` | string | MAC address |
| `arp-vrf/arp-entry/interface` | string | Interface |
| `arp-vrf/arp-entry/mode` | enum (dynamic/static) | Entry type |
| `arp-vrf/arp-entry/time` | string | Entry time |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §13. LLDP Neighbors

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-lldp-oper.yang` |
| **XPath** | `/lldp-ios-xe-oper:lldp-entries` |
| **Sub ID** | 50004 |
| **Tier** | COOL (300s) |
| **Domain** | L2 Topology |
| **Dependency** | Peer-Dependent |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Local interface | `lldp-intf-details/if-name` (key) | string | Table |
| Neighbor device ID | `lldp-intf-details/lldp-neighbor-details/identifier` | string | Table |
| Neighbor port ID | `lldp-intf-details/lldp-neighbor-details/port-id` | string | Table |
| Neighbor system name | `lldp-intf-details/lldp-neighbor-details/system-name` | string | Table |
| Capabilities | `lldp-intf-details/lldp-neighbor-details/system-capabilities` | string | Table |
| Management address | `lldp-intf-details/lldp-neighbor-details/mgmt-addrs` | string | Table |

**Splunk Panel:** LLDP neighbor topology table per switch, neighbor count single value, device discovery table.

#### Typed-Leaf Requirements

Root XPath: `/lldp-ios-xe-oper:lldp-entries`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `lldp-intf-details/if-name` (key) | string | Local interface |
| `lldp-intf-details/lldp-neighbor-details/identifier` | string | Neighbor device ID |
| `lldp-intf-details/lldp-neighbor-details/port-id` | string | Neighbor port ID |
| `lldp-intf-details/lldp-neighbor-details/system-name` | string | Neighbor system name |
| `lldp-intf-details/lldp-neighbor-details/system-capabilities` | string | Capabilities |
| `lldp-intf-details/lldp-neighbor-details/mgmt-addrs` | string | Management address |

#### Activation Guidance

**Minimum Enablement Objective:** Ensure LLDP is enabled and a live neighbor is present.

**Telemetry Success Condition:** Neighbor entries appear with interface and system identity.

**Verification CLI:** `show lldp neighbors detail`

**Reference Guide:** Interface and Hardware Components Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/int_hw/b_1718_int_and_hw_9300_cg.html

---

### §14. CDP Neighbors

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-cdp-oper.yang` |
| **XPath** | `/cdp-ios-xe-oper:cdp-neighbor-details` |
| **Sub ID** | 50005 |
| **Tier** | COOL (300s) |
| **Domain** | L2 Topology |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Local interface | `cdp-neighbor-detail/local-intf-name` | string | Table |
| Device name | `cdp-neighbor-detail/device-name` | string | Table |
| Platform | `cdp-neighbor-detail/platform-name` | string | Table |
| Remote port | `cdp-neighbor-detail/port-id` | string | Table |
| Capabilities | `cdp-neighbor-detail/capability` | string | Table |
| IP address | `cdp-neighbor-detail/ip-address` | string | Table |
| Software version | `cdp-neighbor-detail/version` | string | Detail table |

**Splunk Panel:** CDP neighbor discovery table, neighbor count by platform type (pie chart).

#### Typed-Leaf Requirements

Root XPath: `/cdp-ios-xe-oper:cdp-neighbor-details`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `cdp-neighbor-detail/local-intf-name` | string | Local interface |
| `cdp-neighbor-detail/device-name` | string | Device name |
| `cdp-neighbor-detail/platform-name` | string | Platform |
| `cdp-neighbor-detail/port-id` | string | Remote port |
| `cdp-neighbor-detail/capability` | string | Capabilities |
| `cdp-neighbor-detail/ip-address` | string | IP address |
| `cdp-neighbor-detail/version` | string | Software version |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §15. Platform Components

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-platform-oper.yang` |
| **XPath** | `/platform-ios-xe-oper:components` |
| **Sub ID** | 60007 |
| **Tier** | WARM (60s) |
| **Domain** | Platform and Resources |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Component name | `component/cname` (key) | string | Table row |
| Type | `component/state/type` | string | Table column |
| Description | `component/state/description` | string | Table |
| Part number | `component/state/part-no` | string | Table |
| Serial number | `component/state/serial-no` | string | Table (asset tracking) |
| Status | `component/state/status` | string | Status indicator |
| Status description | `component/state/status-desc` | string | Table |
| Version | `component/state/version` | string | Table |
| Empty slot | `component/state/empty` | bool | Status indicator |
| Parent | `component/state/parent` | string | Hierarchy |

**Splunk Panel:** Hardware inventory table (component name, type, serial, status), status indicators for PSU/fan/module health, filterable by component type.

#### Typed-Leaf Requirements

Root XPath: `/platform-ios-xe-oper:components`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `component/cname` (key) | string | Component name |
| `component/state/type` | string | Type |
| `component/state/description` | string | Description |
| `component/state/part-no` | string | Part number |
| `component/state/serial-no` | string | Serial number |
| `component/state/status` | string | Status |
| `component/state/status-desc` | string | Status description |
| `component/state/version` | string | Version |
| `component/state/empty` | bool | Empty slot |
| `component/state/parent` | string | Parent |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §16. Device Hardware (Uptime, SW Version, Boot Time)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-device-hardware-oper.yang` |
| **XPath** | `/device-hardware-xe-oper:device-hardware-data/device-hardware` |
| **Sub ID** | 50006 |
| **Tier** | COOL (300s) |
| **Domain** | Platform and Resources |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| **Software version** | `device-system-data/software-version` | string | **Single value per switch** |
| **Boot time** | `device-system-data/boot-time` | datetime | **Single value** (uptime calc) |
| Reboot reason | `device-system-data/last-reboot-reason` | string | Table column |
| Hardware model | `device-inventory/hw-type` | string | Table |
| Serial number | `device-inventory/serial-number` | string | Table |

**Splunk Panel:** Device overview banner — hostname, software version, boot time (calculated uptime), reboot reason, serial number. One row per switch.

#### Typed-Leaf Requirements

Root XPath: `/device-hardware-xe-oper:device-hardware-data/device-hardware`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `device-system-data/software-version` | string | **Software version** |
| `device-system-data/boot-time` | datetime | **Boot time** |
| `device-system-data/last-reboot-reason` | string | Reboot reason |
| `device-inventory/hw-type` | string | Hardware model |
| `device-inventory/serial-number` | string | Serial number |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §17. Switchport

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-switchport-oper.yang` |
| **XPath** | `/switchport-ios-xe-oper:switchport-oper-data` |
| **Sub ID** | 50007 |
| **Tier** | COOL (300s) |
| **Domain** | Interfaces |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | key | string | Table row |
| Switchport mode | operational mode (access/trunk) | enum | Table column |
| Access VLAN | access VLAN ID | int | Table column |
| Trunk native VLAN | native VLAN | int | Table column |
| Trunk allowed VLANs | allowed VLANs | string | Table column |

**Splunk Panel:** Switchport mode overview table — interface, mode (access/trunk), VLAN assignment. Port count by mode (pie chart).

#### Typed-Leaf Requirements

Root XPath: `/switchport-ios-xe-oper:switchport-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | string | Interface name |
| operational mode (access/trunk) | enum | Switchport mode |
| access VLAN ID | int | Access VLAN |
| native VLAN | int | Trunk native VLAN |
| allowed VLANs | string | Trunk allowed VLANs |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §18. Transceiver / Optics

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-transceiver-oper.yang` |
| **XPath** | `/xcvr-ios-xe-oper:transceiver-oper-data` |
| **Sub ID** | 50008 |
| **Tier** | COOL (300s) |
| **Domain** | Interfaces |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | key | string | Table row |
| Transceiver type | type/vendor/part | string | Table |
| TX power (dBm) | output power | gauge | Time chart |
| RX power (dBm) | input power | gauge | Time chart |
| Temperature (C) | temperature | gauge | Time chart |
| Voltage (V) | voltage | gauge | Table |
| Bias current (mA) | bias current | gauge | Table |

**Splunk Panel:** Optics health table (port, type, TX/RX power, temp), alert on RX power below threshold.

#### Typed-Leaf Requirements

Root XPath: `/xcvr-ios-xe-oper:transceiver-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | string | Interface name |
| type/vendor/part | string | Transceiver type |
| output power | gauge | TX power (dBm) |
| input power | gauge | RX power (dBm) |
| temperature | gauge | Temperature (C) |
| voltage | gauge | Voltage (V) |
| bias current | gauge | Bias current (mA) |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §19. UDLD

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-udld-oper.yang` |
| **XPath** | `/udld-ios-xe-oper:udld-oper-data` |
| **Sub ID** | 50009 |
| **Tier** | COOL (300s) |
| **Domain** | Interfaces |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface | key | string | Table row |
| UDLD neighbor status | neighbor state | enum | Status indicator |
| Direction | direction | string | Table |

**Splunk Panel:** UDLD neighbor status table with bidirectional/unidirectional indicators.

#### Typed-Leaf Requirements

Root XPath: `/udld-ios-xe-oper:udld-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | string | Interface |
| neighbor state | enum | UDLD neighbor status |
| direction | string | Direction |

#### Activation Guidance

**Minimum Enablement Objective:** Enable UDLD globally and per interface where appropriate.

**Telemetry Success Condition:** UDLD neighbor or operational state becomes populated.

**Verification CLI:** `show udld neighbors`

**Reference Guide:** Interface and Hardware Components Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/int_hw/b_1718_int_and_hw_9300_cg.html

---

### §20. 802.1X / Identity Sessions

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-identity-oper.yang` |
| **XPath** | `/identity-ios-xe-oper:identity-oper-data` |
| **Sub ID** | 50010 |
| **Tier** | COOL (300s) |
| **Domain** | Security and Identity |
| **Dependency** | Service-Dependent |
| **Risk** | High |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| MAC address | `session-context-data/mac` | string | Table row |
| Interface name | `session-context-data/intf-name` | string | Table |
| State | `session-context-data/state` | enum | Status indicator |
| Method ID | `session-context-data/method-id` | string | Table |
| IPv4 address | `session-context-data/ipv4` | string | Table |
| VLAN ID | `session-context-data/vlan-id` | int | Table |
| Device name | `session-context-data/device-name` | string | Table |
| Device type | `session-context-data/device-type` | string | Table |
| Policy name | `session-context-data/policy-name` | string | Table |
| Authorized | `session-context-data/authorized` | bool | Status indicator |
| AAA session ID | `session-context-data/aaa-sess-id` | string | Detail |
| AAA server status | `session-context-data/aaa-server/server-status` | string | Table |
| EPM service template | `epm-service-block/template-name` | string | Table |

**Splunk Panel:** Active 802.1X sessions table (MAC, interface, state, device type, VLAN), session count gauge, auth method breakdown (pie chart).

#### Typed-Leaf Requirements

Root XPath: `/identity-ios-xe-oper:identity-oper-data`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `session-context-data/mac` | string | Endpoint identity key. |
| `session-context-data/intf-name` | string | Access port correlation field. |
| `session-context-data/state` | enum | Session lifecycle state. |
| `session-context-data/method-id` | string | Authentication method context. |
| `session-context-data/ipv4` | string | Endpoint IP identity. |
| `session-context-data/vlan-id` | count | Access VLAN context. |
| `session-context-data/device-name` | string | Endpoint name if discovered. |
| `session-context-data/device-type` | string | Endpoint classification field. |
| `session-context-data/policy-name` | string | Authorization policy context. |
| `session-context-data/authorized` | bool | True or false authorization outcome; must drive summary state. |
| `session-context-data/aaa-sess-id` | string | AAA correlation key. |
| `session-context-data/aaa-server/server-status` | string | Upstream AAA disposition detail. |
| `epm-service-block/template-name` | string | Service template or policy context. |

#### Activation Guidance

**Minimum Enablement Objective:** Enable AAA and dot1x with at least one authenticator port and a real endpoint.

**Telemetry Success Condition:** Authentication session state and identity context are populated.

**Verification CLI:** `show authentication sessions interface <if>`

**Reference Guide:** Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html

---

### §21. TCAM Utilization

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-tcam-oper.yang` |
| **XPath** | `/tcam-ios-xe-oper:tcam-details` |
| **Sub ID** | 50011 |
| **Tier** | COOL (300s) |
| **Domain** | Platform and Resources |
| **Dependency** | Baseline |
| **Risk** | Low |
| **Platforms** | All C9K; SDM template and TCAM allocation vary by platform ASIC |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| ASIC number | `tcam-detail/asic-no` (key) | int | Group-by |
| Table name | `tcam-detail/name` (key) | string | Group-by (Security ACE, Control Plane Entries, etc.) |
| **TCAM entries used** | `tcam-detail/tcam-entries-used` | gauge | **Bar gauge (% of max)** |
| TCAM entries max | (reference value per table/SDM) | int | Reference line |

**Splunk Panel:** TCAM utilization bar chart per SDM table/category per ASIC, percentage gauge, alert when >80% utilized. Variable selector for table name.
**Note:** `/tcam-ios-xe-oper:tcam-details` is marked as "Deprecated" in mdt-capabilities-oper but is still widely used. Verify on 17.12+.

#### Typed-Leaf Requirements

Root XPath: `/tcam-ios-xe-oper:tcam-details`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `tcam-detail/asic-no` (key) | int | ASIC number |
| `tcam-detail/name` (key) | string | Table name |
| `tcam-detail/tcam-entries-used` | gauge | **TCAM entries used** |
| (reference value per table/SDM) | int | TCAM entries max |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §22. MDT Subscription Health

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-mdt-oper-v2.yang` |
| **XPath** | `/mdt-oper-v2:mdt-oper-v2-data` |
| **Sub ID** | 50012 |
| **Tier** | COOL (300s) |
| **Domain** | Operations |
| **Dependency** | Baseline |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Subscription ID | key | int | Table row |
| Subscription type | type (configured/dynamic) | string | Table |
| State | state (valid/invalid) | enum | Status indicator |
| XPath filter | filter xpath | string | Table column |
| Updates sent | update count | counter | Time chart |
| Connection state | receiver state | enum | **Status indicator** (Connected/Connecting/Disconnected) |

**Splunk Panel:** MDT health overview table — sub ID, xpath, state, connection status, updates sent. Alert on any "Disconnected" or "Invalid" state.

#### Typed-Leaf Requirements

Root XPath: `/mdt-oper-v2:mdt-oper-v2-data`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| subscription key | count | Subscription identity and correlation key. |
| type | string | Configured versus dynamic subscription context. |
| state | enum | Valid, invalid, or similar health state. |
| filter xpath | string | Confirms the actual subscribed filter. |
| update count | counter | Volume/activity indicator for telemetry liveliness. |
| receiver state | enum | Transport/session health indicator. |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §23. Software Install

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-install-oper.yang` |
| **XPath** | `/install-ios-xe-oper:install-oper-data` |
| **Sub ID** | 50013 |
| **Tier** | COOL (300s) |
| **Domain** | Operations |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Package name | install package name | string | Table |
| Package version | install package version | string | Table |
| Package state | state (active/committed) | enum | Status indicator |

**Splunk Panel:** Installed software packages table per switch (version compliance check).

#### Typed-Leaf Requirements

Root XPath: `/install-ios-xe-oper:install-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| install package name | string | Package name |
| install package version | string | Package version |
| state (active/committed) | enum | Package state |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §24. BGP State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-bgp-oper.yang` |
| **XPath** | `/bgp-ios-xe-oper:bgp-state-data` |
| **Sub ID** | 60008 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Neighbor ID | `neighbors/neighbor/neighbor-id` (key) | string | Table row |
| **Session state** | `neighbors/neighbor/session-state` | enum | **Status indicator** (Established/Connect/Idle/Active) |
| Prefixes received | `neighbors/neighbor/prefix-activity/received/current-prefixes` | gauge | Table / time chart |
| Prefixes sent | `neighbors/neighbor/prefix-activity/sent/current-prefixes` | gauge | Table |
| Up time | `neighbors/neighbor/up-time` | string | Table |
| AS number | `neighbors/neighbor/as` | int | Table |
| Installed prefixes | `neighbors/neighbor/installed-prefixes` | gauge | Table |
| BGP version | BGP version fields | int | Table |
| Messages received | neighbor message counters | counter | Time chart |
| Messages sent | neighbor message counters | counter | Time chart |

**Splunk Panel:** BGP neighbor summary table (neighbor, AS, state, prefixes received/sent, uptime), status indicator grid (all Established = green), alert on state != Established.

#### Typed-Leaf Requirements

Root XPath: `/bgp-ios-xe-oper:bgp-state-data`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `neighbors/neighbor/neighbor-id` | string | Neighbor identity key. |
| `neighbors/neighbor/session-state` | enum | Primary BGP adjacency state. |
| `neighbors/neighbor/prefix-activity/received/current-prefixes` | count | Current inbound prefix scale. |
| `neighbors/neighbor/prefix-activity/sent/current-prefixes` | count | Current outbound prefix scale. |
| `neighbors/neighbor/up-time` | string | Session duration. |
| `neighbors/neighbor/as` | count | Remote AS context. |
| `neighbors/neighbor/installed-prefixes` | count | Effective installed route count. |
| version fields | count | BGP protocol version detail. |
| message counters | counter | Session activity and churn analysis. |

#### Activation Guidance

**Minimum Enablement Objective:** Configure a BGP process and at least one reachable neighbor with an active address family.

**Telemetry Success Condition:** Neighbor state transitions from absent to a meaningful state, ideally Established.

**Verification CLI:** `show bgp ipv4 unicast summary`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §25. OSPF State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-ospf-oper.yang` |
| **XPath** | `/ospf-ios-xe-oper:ospf-oper-data` |
| **Sub ID** | 60009 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Instance number | `ospf-instance/af` and `router-id` | int/string | Group-by |
| Area ID | `ospf-instance/ospf-area/area-id` | int | Table |
| **Neighbor ID** | `ospf-instance/ospf-area/ospf-interface/ospf-neighbor/neighbor-id` (key) | string | Table row |
| **Neighbor state** | `ospf-instance/ospf-area/ospf-interface/ospf-neighbor/state` | enum | **Status indicator** (Full/2Way/Init/Down) |
| Neighbor address | neighbor address | string | Table |
| Interface name | `ospf-instance/ospf-area/ospf-interface/name` | string | Table |
| Interface cost | `ospf-instance/ospf-area/ospf-interface/cost` | int | Table |
| DR IP | `ospf-instance/ospf-area/ospf-interface/dr-address` | string | Table |
| BDR IP | `ospf-instance/ospf-area/ospf-interface/bdr-address` | string | Table |
| LSA count | area LSA summary | int | Table |

**Splunk Panel:** OSPF neighbor table (neighbor ID, area, interface, state, DR/BDR), state indicator (all Full = green), area summary table.

#### Typed-Leaf Requirements

Root XPath: `/ospf-ios-xe-oper:ospf-oper-data`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `ospf-instance/af` and `router-id` | string | OSPF instance identity. |
| `ospf-instance/ospf-area/area-id` | count | Area context. |
| `ospf-instance/ospf-area/ospf-interface/ospf-neighbor/neighbor-id` | string | Neighbor key. |
| `ospf-instance/ospf-area/ospf-interface/ospf-neighbor/state` | enum | Neighbor adjacency state. |
| neighbor address | string | Peer address detail. |
| `ospf-instance/ospf-area/ospf-interface/name` | string | Interface context. |
| `ospf-instance/ospf-area/ospf-interface/cost` | count | Path cost metric. |
| `ospf-instance/ospf-area/ospf-interface/dr-address` | string | DR identity. |
| `ospf-instance/ospf-area/ospf-interface/bdr-address` | string | BDR identity. |
| LSA summary fields | count | Topology scale and churn context. |

#### Activation Guidance

**Minimum Enablement Objective:** Configure an OSPF process and at least one active interface or network statement on both sides.

**Telemetry Success Condition:** OSPF neighbor and area data populate.

**Verification CLI:** `show ip ospf neighbor`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §26. IETF Routing Table (RIB)

| | |
|---|---|
| **YANG Module** | `ietf-routing.yang` |
| **XPath** | `/rt:routing-state` |
| **Sub ID** | 60028 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Routing instance name | `routing-instance/name` (key) | string | Dimension |
| Routing instance type | `routing-instance/type` | identityref | Table column |
| RIB name | `routing-instance/ribs/rib/name` (key) | string | Dimension |
| Interface name | `routing-instance/interfaces/interface` (key) | string | Table column |
| Routing protocol type | `routing-instance/routing-protocols/routing-protocol/type` (key) | identityref | Table / pie chart |
| Routing protocol name | `routing-instance/routing-protocols/routing-protocol/name` (key) | string | Table column |

**Splunk Panel:** IETF routing state: active routing instances, associated RIBs and protocols. Provides a vendor-neutral view of which routing protocols are active, complementing native models (§24 BGP, §25 OSPF, §47 EIGRP, §48 IS-IS).

#### Typed-Leaf Requirements

Root XPath: `/rt:routing-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `routing-instance/name` (key) | string | Routing instance name |
| `routing-instance/type` | identityref | Routing instance type |
| `routing-instance/ribs/rib/name` (key) | string | RIB name |
| `routing-instance/interfaces/interface` (key) | string | Interface name |
| `routing-instance/routing-protocols/routing-protocol/type` (key) | identityref | Routing protocol type |
| `routing-instance/routing-protocols/routing-protocol/name` (key) | string | Routing protocol name |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §27. DHCP Pool Stats

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-dhcp-oper.yang` |
| **XPath** | `/dhcp-ios-xe-oper:dhcp-oper-data` |
| **Sub ID** | 50014 |
| **Tier** | COOL (300s) |
| **Domain** | Network Services |
| **Dependency** | Feature-Only |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Pool name | key | string | Table row |
| Allocated addresses | allocated count | gauge | Bar chart |
| Available addresses | available count | gauge | Bar chart |
| Utilization % | calculated | gauge | Percent gauge |

**Splunk Panel:** DHCP pool utilization bar chart (allocated vs available), alert when >90% utilized.

#### Typed-Leaf Requirements

Root XPath: `/dhcp-ios-xe-oper:dhcp-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | string | Pool name |
| allocated count | gauge | Allocated addresses |
| available count | gauge | Available addresses |
| calculated | gauge | Utilization % |

#### Activation Guidance

**Minimum Enablement Objective:** Create a DHCP pool and serve at least one active client subnet.

**Telemetry Success Condition:** Pool utilization and bindings appear.

**Verification CLI:** `show ip dhcp pool`; `show ip dhcp binding`

**Reference Guide:** IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html

---

### §28. High Availability State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-ha-oper.yang` |
| **XPath** | `/ha-ios-xe-oper:ha-oper-data` |
| **Sub ID** | 50015 |
| **Tier** | COOL (300s) |
| **Domain** | Platform and Resources |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |
| **Platforms** | C9400/C9600 dual-supervisor primarily; C9200/C9300/C9500 report single-active |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| HA state | active/standby/init | enum | Single value status |
| Switchover reason | last switchover reason | string | Table |
| Switchover time | last switchover time | datetime | Table |

**Splunk Panel:** HA state indicator per switch (Active/Standby), last switchover reason and time.

#### Typed-Leaf Requirements

Root XPath: `/ha-ios-xe-oper:ha-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| active/standby/init | enum | HA state |
| last switchover reason | string | Switchover reason |
| last switchover time | datetime | Switchover time |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §29. Linecard Status

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-linecard-oper.yang` |
| **XPath** | `/linecard-ios-xe-oper:linecard-oper-data` |
| **Sub ID** | 50016 |
| **Tier** | COOL (300s) |
| **Domain** | Platform and Resources |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |
| **Platforms** | C9400/C9600 modular chassis primarily; fixed-form C9200/C9300/C9500 report a single linecard |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Slot number | key | int | Table row |
| Linecard state | state | enum (active/standby/inserted) | Status indicator |
| Card type | type | string | Table |
| Serial number | serial | string | Table |

**Splunk Panel:** Linecard inventory and status table (relevant for C9400/C9600; informational for C9300).

#### Typed-Leaf Requirements

Root XPath: `/linecard-ios-xe-oper:linecard-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | int | Slot number |
| state | enum (active/standby/inserted) | Linecard state |
| type | string | Card type |
| serial | string | Serial number |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §30. TrustSec (SGT/SXP)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-trustsec-oper.yang` |
| **XPath** | `/trustsec-ios-xe-oper:trustsec-state` |
| **Sub ID** | 50017 |
| **Tier** | COOL (300s) |
| **Domain** | Security and Identity |
| **Dependency** | Service-Dependent |
| **Risk** | High |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| SGT tag value | `cts-rolebased-sgtmaps` entries | int | Table |
| SGT IP binding | IP-to-SGT mapping | string | Table |
| SXP connection peer | `cts-sxp-connections` peer IP | string | Table |
| SXP connection state | state | enum | Status indicator |
| SXP connection mode | speaker/listener | enum | Table |

**Splunk Panel:** SGT assignment table, SXP connection status table, SGT count (single value).

#### Typed-Leaf Requirements

Root XPath: `/trustsec-ios-xe-oper:trustsec-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `cts-rolebased-sgtmaps` entries | int | SGT tag value |
| IP-to-SGT mapping | string | SGT IP binding |
| `cts-sxp-connections` peer IP | string | SXP connection peer |
| state | enum | SXP connection state |
| speaker/listener | enum | SXP connection mode |

#### Activation Guidance

**Minimum Enablement Objective:** Enable only in a dedicated lab with clear AAA and policy intent.

**Telemetry Success Condition:** CTS state, SGT, or SXP context appears with meaningful entries.

**Verification CLI:** `show cts role-based permissions`; `show cts interface`

**Reference Guide:** Cisco TrustSec Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/cts/b_1718_cts_9300_cg.html

---

### §31. LACP / Port-Channel (via interfaces-oper)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-interfaces-oper.yang` |
| **XPath** | `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state` |
| **Sub ID** | 50018 |
| **Tier** | COOL (300s) |
| **Domain** | Interfaces |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Aggregate interface name | `name` (Port-channelX) | string | Table row |
| Member links | `lag-aggregate-state/member-link` | list | Table column |
| Member link state | per-member oper state | enum | Status indicator |
| LAG type | static/LACP | string | Table |
| LACP activity counters | `lacp-oper` data | counter | Time chart |

**Splunk Panel:** Port-channel member status table (aggregate, members, status), alert on member down.

#### Typed-Leaf Requirements

Root XPath: `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `name` (Port-channelX) | string | Aggregate interface name |
| `lag-aggregate-state/member-link` | list | Member links |
| per-member oper state | enum | Member link state |
| static/LACP | string | LAG type |
| `lacp-oper` data | counter | LACP activity counters |

#### Activation Guidance

**Minimum Enablement Objective:** Configure a port-channel with at least one operational LACP member on both ends.

**Telemetry Success Condition:** Port-channel aggregate state and members populate.

**Verification CLI:** `show etherchannel summary`

**Reference Guide:** Layer 2 Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/lyr2/b_1718_lyr2_9300_cg.html

---

### §32. ACL Hit Counters

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-acl-oper.yang` |
| **XPath** | `/acl-ios-xe-oper:access-lists/access-list` |
| **Sub ID** | 50019 |
| **Tier** | COOL (300s) |
| **Domain** | Security and Identity |
| **Dependency** | Traffic-Dependent |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| ACL name | `access-control-list-name` (key) | string | Dimension |
| ACL type | `access-control-list-type` | enum | Table column |
| Rule name | `access-list-entry/rule-name` (key) | string | Dimension |
| Match count | `access-list-entry/match-counter` | counter64 | Time chart (rate) |

**Splunk Panel:** Per-ACL/per-rule match counters time chart (rate of hits over time), top-10 most-hit ACE rules bar chart, zero-hit rules table for cleanup auditing.

#### Typed-Leaf Requirements

Root XPath: `/acl-ios-xe-oper:access-lists/access-list`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `access-control-list-name` (key) | string | ACL name |
| `access-control-list-type` | enum | ACL type |
| `access-list-entry/rule-name` (key) | string | Rule name |
| `access-list-entry/match-counter` | counter64 | Match count |

#### Activation Guidance

**Minimum Enablement Objective:** Apply an ACL in a real forwarding path and generate matching traffic.

**Telemetry Success Condition:** Hit counters increment.

**Verification CLI:** `show access-lists`

**Reference Guide:** Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html

---

### §33. NTP Synchronization

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-ntp-oper.yang` |
| **XPath** | `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info` |
| **Sub ID** | 60010 |
| **Tier** | WARM (60s) |
| **Domain** | Network Services |
| **Dependency** | Service-Dependent |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Association ID | `ntp-associations/assoc-id` (key) | uint16 | Dimension |
| Peer reachability | `ntp-associations/peer-reach` | uint8 | Gauge |
| Stratum | `ntp-associations/peer-stratum` | uint32 | Single value |
| Delay | `ntp-associations/delay` | decimal64 | Time chart |
| Offset | `ntp-associations/offset` | decimal64 | Time chart |
| Jitter | `ntp-associations/jitter` | decimal64 | Time chart |
| Selection status | `ntp-associations/peer-selection-status` | enum | Status indicator |

**Splunk Panel:** NTP offset/jitter time chart per peer, stratum single value, reachability gauge (255 = all recent polls succeeded), alert on offset > 100ms or reachability < 255.

#### Typed-Leaf Requirements

Root XPath: `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `ntp-associations/assoc-id` (key) | uint16 | Association ID |
| `ntp-associations/peer-reach` | uint8 | Peer reachability |
| `ntp-associations/peer-stratum` | uint32 | Stratum |
| `ntp-associations/delay` | decimal64 | Delay |
| `ntp-associations/offset` | decimal64 | Offset |
| `ntp-associations/jitter` | decimal64 | Jitter |
| `ntp-associations/peer-selection-status` | enum | Selection status |

#### Activation Guidance

**Minimum Enablement Objective:** Configure reachable NTP servers and allow synchronization to occur.

**Telemetry Success Condition:** NTP status and associations become valid.

**Verification CLI:** `show ntp status`; `show ntp associations`

**Reference Guide:** System Management Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sys_mgmt/b_1718_sys_mgmt_9300_cg.html

---

### §34. BFD Sessions

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-bfd-oper.yang` |
| **XPath** | `/bfd-ios-xe-oper:bfd-state/sessions` |
| **Sub ID** | 60011 |
| **Tier** | WARM (60s) |
| **Domain** | Network Services |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Session type | `session/type` (key) | enum | Dimension |
| Interface | `bfd-nbr/interface` (key) | string | Dimension |
| Neighbor IP | `bfd-nbr/ip` (key) | ip-address | Dimension |
| Local state | `state` | enum | Status indicator |
| Remote state | `remote-state` | enum | Status indicator |

**Splunk Panel:** BFD session status table (neighbor, interface, state), alert on state != Up.

#### Typed-Leaf Requirements

Root XPath: `/bfd-ios-xe-oper:bfd-state/sessions`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `session/type` (key) | enum | Session type |
| `bfd-nbr/interface` (key) | string | Interface |
| `bfd-nbr/ip` (key) | ip-address | Neighbor IP |
| `state` | enum | Local state |
| `remote-state` | enum | Remote state |

#### Activation Guidance

**Minimum Enablement Objective:** Enable BFD as part of a real routed adjacency, not as an isolated feature.

**Telemetry Success Condition:** BFD sessions appear with a stable state.

**Verification CLI:** `show bfd neighbors`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §35. HSRP State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-hsrp-oper.yang` |
| **XPath** | `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info` |
| **Sub ID** | 60012 |
| **Tier** | WARM (60s) |
| **Domain** | Network Services |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Group ID | `group-id` (key) | uint16 | Dimension |
| Interface | `if-name` (key) | string | Dimension |
| Priority | `priority` | uint32 | Single value |
| State | `state` | enum | Status indicator |
| Active IP | `active-ip` | ip-address | Table column |
| Standby IP | `standby-ip` | ip-address | Table column |
| Virtual IP | `virtual-ip` | ip-address | Table column |

**Splunk Panel:** HSRP group status table (group, interface, state, active/standby/virtual IPs, priority), alert on state change from Active to non-Active.

#### Typed-Leaf Requirements

Root XPath: `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `group-id` (key) | uint16 | Group ID |
| `if-name` (key) | string | Interface |
| `priority` | uint32 | Priority |
| `state` | enum | State |
| `active-ip` | ip-address | Active IP |
| `standby-ip` | ip-address | Standby IP |
| `virtual-ip` | ip-address | Virtual IP |

#### Activation Guidance

**Minimum Enablement Objective:** Configure HSRP on a shared subnet across at least two switches.

**Telemetry Success Condition:** Group state, virtual IP, and role populate.

**Verification CLI:** `show standby brief`

**Reference Guide:** IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html

---

### §36. VRRP State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-vrrp-oper.yang` |
| **XPath** | `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state` |
| **Sub ID** | 60013 |
| **Tier** | WARM (60s) |
| **Domain** | Network Services |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface | `if-number` (key) | uint32 | Dimension |
| Group ID | `group-id` (key) | uint32 | Dimension |
| Address type | `addr-type` (key) | enum | Dimension |
| VRRP state | `vrrp-state` | enum | Status indicator |
| Priority | `priority` | uint32 | Single value |
| Virtual IP | `virtual-ip` | ip-address | Table column |
| Master IP | `master-ip` | ip-address | Table column |

**Splunk Panel:** VRRP group status table similar to HSRP, alert on state != Master when expected.

#### Typed-Leaf Requirements

Root XPath: `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `if-number` (key) | uint32 | Interface |
| `group-id` (key) | uint32 | Group ID |
| `addr-type` (key) | enum | Address type |
| `vrrp-state` | enum | VRRP state |
| `priority` | uint32 | Priority |
| `virtual-ip` | ip-address | Virtual IP |
| `master-ip` | ip-address | Master IP |

#### Activation Guidance

**Minimum Enablement Objective:** Configure VRRP on a shared subnet across at least two switches.

**Telemetry Success Condition:** Group state, virtual IP, and role populate.

**Verification CLI:** `show vrrp brief`

**Reference Guide:** IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html

---

### §37. Flexible NetFlow / Flow Monitor

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-flow-monitor-oper.yang` |
| **XPath** | `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor` |
| **Sub ID** | 60014 |
| **Tier** | WARM (60s) |
| **Domain** | Network Services |
| **Dependency** | Traffic-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Monitor name | `name` (key) | string | Dimension |
| Flows added | `flow-monitor-statistics/flows-added` | uint64 | Time chart (rate) |
| Flows aged | `flow-monitor-statistics/flows-aged` | uint64 | Time chart (rate) |
| Active flows | (flows-added minus flows-aged) | calculated | Gauge |
| Cache entries | `flow-cache-statistics` | uint64 | Gauge |
| Export packets sent | `flow-export-statistics` | uint64 | Time chart (rate) |

**Splunk Panel:** Active flow count gauge per monitor, flows added/aged rate time chart, export statistics counters. Useful for validating NetFlow data is being generated and exported.

#### Typed-Leaf Requirements

Root XPath: `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `name` (key) | string | Monitor name |
| `flow-monitor-statistics/flows-added` | uint64 | Flows added |
| `flow-monitor-statistics/flows-aged` | uint64 | Flows aged |
| (flows-added minus flows-aged) | calculated | Active flows |
| `flow-cache-statistics` | uint64 | Cache entries |
| `flow-export-statistics` | uint64 | Export packets sent |

#### Activation Guidance

**Minimum Enablement Objective:** Configure a flow record, exporter, and monitor, then apply it to a traffic-carrying interface.

**Telemetry Success Condition:** Flow cache entries appear and exporter state is meaningful.

**Verification CLI:** `show flow monitor <name> cache`

**Reference Guide:** Network Management Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/nmgmt/b_1718_nmgmt_9300_cg.html

---

### §38. IP SLA Probes

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-ip-sla-oper.yang` |
| **XPath** | `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry` |
| **Sub ID** | 60015 |
| **Tier** | WARM (60s) |
| **Domain** | Network Services |
| **Dependency** | Feature-Only |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Operation ID | `oper-id` (key) | uint32 | Dimension |
| Operation type | `oper-type` | enum | Table column |
| Return code | `latest-return-code` | enum | Status indicator |
| Success count | `success-count` | uint32 | Time chart |
| Failure count | `failure-count` | uint32 | Time chart |
| Latest RTT | `rtt-info/latest-rtt` | uint64 | Time chart |
| Threshold exceeded | `threshold-occured` | boolean | Alert |
| Start time | `latest-oper-start-time` | date-and-time | Table column |

**Splunk Panel:** Per-probe RTT time chart, success/failure ratio pie chart, return code status table, alert on failure-count increment or threshold-occured = true.

#### Typed-Leaf Requirements

Root XPath: `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `oper-id` (key) | uint32 | Operation ID |
| `oper-type` | enum | Operation type |
| `latest-return-code` | enum | Return code |
| `success-count` | uint32 | Success count |
| `failure-count` | uint32 | Failure count |
| `rtt-info/latest-rtt` | uint64 | Latest RTT |
| `threshold-occured` | boolean | Threshold exceeded |
| `latest-oper-start-time` | date-and-time | Start time |

#### Activation Guidance

**Minimum Enablement Objective:** Create and schedule a continuously running IP SLA operation to a reachable target.

**Telemetry Success Condition:** Operation state and statistics populate.

**Verification CLI:** `show ip sla statistics`

**Reference Guide:** Network Management Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/nmgmt/b_1718_nmgmt_9300_cg.html

---

### §39. AAA / RADIUS / TACACS Statistics

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-aaa-oper.yang` |
| **XPath** | `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats` |
| **Sub ID** | 50020 |
| **Tier** | COOL (300s) |
| **Domain** | Security and Identity |
| **Dependency** | Service-Dependent |
| **Risk** | High |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Server group | `group-name` (key) | string | Dimension |
| Server IP | `radius-server-ip` (key) | ip-address | Dimension |
| Auth port | `auth-port` (key) | uint16 | Dimension |
| Access accepts | `authen-access-accepts` | uint32 | Time chart (rate) |
| Access rejects | `authen-access-rejects` | uint32 | Time chart (rate) |
| Connection opens | `connection-opens` | uint32 | Time chart (rate) |
| TACACS server | `aaa-tacacs-stats/tacacs-server-address` (key) | ip-address | Dimension |

**Splunk Panel:** RADIUS accept/reject ratio time chart per server, TACACS connection status table, total auth request rate, alert on high reject rate or server unreachable.

#### Typed-Leaf Requirements

Root XPath: `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `group-name` (key) | string | Server group |
| `radius-server-ip` (key) | ip-address | Server IP |
| `auth-port` (key) | uint16 | Auth port |
| `authen-access-accepts` | uint32 | Access accepts |
| `authen-access-rejects` | uint32 | Access rejects |
| `connection-opens` | uint32 | Connection opens |
| `aaa-tacacs-stats/tacacs-server-address` (key) | ip-address | TACACS server |

#### Activation Guidance

**Minimum Enablement Objective:** Configure AAA with at least one reachable authentication backend and generate real auth events.

**Telemetry Success Condition:** AAA statistics populate with meaningful outcomes.

**Verification CLI:** `show aaa servers`; `show radius statistics`; `show tacacs`

**Reference Guide:** Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html

---

### §40. Port Security

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-psecure-oper.yang` |
| **XPath** | `/psecure-ios-xe-oper:psecure-oper-data/psecure-state` |
| **Sub ID** | 50021 |
| **Tier** | COOL (300s) |
| **Domain** | Security and Identity |
| **Dependency** | Traffic-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface | `if-name` (key) | string | Dimension |
| VLAN | `psecure-entry/vlan` (key) | uint16 | Dimension |
| MAC address | `psecure-entry/mac` (key) | mac-address | Table column |
| Secure type | `psecure-entry/type` | enum | Table column |
| Age remaining | `psecure-entry/age-remain` | uint32 (min) | Table column |

**Splunk Panel:** Port security summary table (interface, secured MACs, type), count of secured ports (single value), alert on violation events.

#### Typed-Leaf Requirements

Root XPath: `/psecure-ios-xe-oper:psecure-oper-data/psecure-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `if-name` (key) | string | Interface |
| `psecure-entry/vlan` (key) | uint16 | VLAN |
| `psecure-entry/mac` (key) | mac-address | MAC address |
| `psecure-entry/type` | enum | Secure type |
| `psecure-entry/age-remain` | uint32 (min) | Age remaining |

#### Activation Guidance

**Minimum Enablement Objective:** Enable port security on an access interface with a live endpoint.

**Telemetry Success Condition:** Learned secure MAC state and counters populate.

**Verification CLI:** `show port-security interface <if>`

**Reference Guide:** Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html

---

### §41. MACsec / MKA Encryption

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-macsec-oper.yang + Cisco-IOS-XE-mka-oper.yang` |
| **XPath** | `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics` |
| **Sub ID** | 50022 (MACsec) / 50023 (MKA) |
| **Tier** | COOL (300s) |
| **Domain** | Security and Identity |
| **Dependency** | Peer-Dependent |
| **Risk** | High |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface | `if-name` (key) | string | Dimension |
| TX untagged pkts | `tx-untag-pkts` | uint64 | Time chart |
| RX no-tag pkts | `rx-notag-pkts` | uint64 | Time chart |
| SC encrypted pkts | `sc-encrypt-pkts` | uint64 | Time chart (rate) |
| SC auth-only pkts | `sc-auth-only-pkts` | uint64 | Time chart (rate) |
| MKA PDU RX | `mkpdu-stats-rx` | uint32 | Time chart (rate) |
| MKA PDU TX | `mkpdu-stats-tx` | uint32 | Time chart (rate) |
| SAK generation errors | `mka-err-sak-gen` | uint32 | Alert counter |

**Splunk Panel:** MACsec encrypted/untagged traffic counters per interface, MKA PDU exchange rate, alert on SAK generation errors or untagged packet spikes.

#### Typed-Leaf Requirements

Root XPath: `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `if-name` | string | Protected interface identity. |
| `tx-untag-pkts` | counter | Traffic behavior indicator. |
| `rx-notag-pkts` | counter | Validation and mismatch indicator. |
| `sc-encrypt-pkts` | counter | Core encrypted traffic counter. |
| `sc-auth-only-pkts` | counter | Auth-only traffic counter. |
| `mkpdu-stats-rx` | counter | MKA control-plane receive activity. |
| `mkpdu-stats-tx` | counter | MKA control-plane transmit activity. |
| `mka-err-sak-gen` | counter | Key-management error signal. |

#### Activation Guidance

**Minimum Enablement Objective:** Configure both ends of a link with compatible MACsec and MKA policy.

**Telemetry Success Condition:** MACsec and MKA sessions populate with operational counters.

**Verification CLI:** `show macsec interface`; `show mka session`

**Reference Guide:** Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html

---

### §42. VRF Operational State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-vrf-oper.yang` |
| **XPath** | `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry` |
| **Sub ID** | 50024 |
| **Tier** | COOL (300s) |
| **Domain** | L3 Routing |
| **Dependency** | Feature-Only |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VRF name | `vrf-name` (key) | string | Dimension |
| Address family | `address-family-entry/address-family` | enum | Table column |
| Member interfaces | `interface` (leaf-list) | string[] | Table column |

**Splunk Panel:** VRF membership overview table (VRF name, address family, assigned interfaces), VRF count (single value).

#### Typed-Leaf Requirements

Root XPath: `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `vrf-name` (key) | string | VRF name |
| `address-family-entry/address-family` | enum | Address family |
| `interface` (leaf-list) | string[] | Member interfaces |

#### Activation Guidance

**Minimum Enablement Objective:** Create one or more non-default VRFs and bind interfaces or SVIs as needed.

**Telemetry Success Condition:** VRF entries and routed context populate.

**Verification CLI:** `show vrf`; `show ip route vrf <name>`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §43. Data Plane Resources (TCAM/EM per Feature)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-switch-dp-resources-oper.yang` |
| **XPath** | `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource` |
| **Sub ID** | 50025 |
| **Tier** | COOL (300s) |
| **Domain** | Platform and Resources |
| **Dependency** | Baseline |
| **Risk** | Low |
| **Platforms** | All C9K; resource categories and TCAM/EM partitions vary by ASIC (UADP 2.0/3.0) |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Location | `fru/slot/bay/chassis/node` (keys) | string | Dimension |
| Feature | `feature` (key) | enum | Dimension |
| Protocol | `protocol` (key) | enum | Dimension |
| Direction | `direction` (key) | enum | Dimension |
| Max TCAM % used | `max-tcam-percentage-used` | decimal64 | Bar chart / Gauge |
| Max EM % used | `max-em-percentage-used` | decimal64 | Bar chart / Gauge |

**Splunk Panel:** Per-feature TCAM/EM utilization bar chart (grouped by feature+protocol+direction), percentage gauge with alert thresholds, complements section 21 TCAM by showing per-feature breakdown.

#### Typed-Leaf Requirements

Root XPath: `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| location keys | string | Hardware locality for capacity hot spots. |
| `feature` | enum | Resource consumer identity. |
| `protocol` | enum | Protocol context for the resource use. |
| `direction` | enum | Ingress or egress context. |
| `max-tcam-percentage-used` | decimal64 percent | Primary TCAM utilization signal. |
| `max-em-percentage-used` | decimal64 percent | Primary EM utilization signal. |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §44. CPU Punt/Inject Counters

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-switch-dp-punt-inject-oper.yang` |
| **XPath** | `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats` |
| **Sub ID** | 30004 |
| **Tier** | HOT (30s) |
| **Domain** | Platform and Resources |
| **Dependency** | Baseline |
| **Risk** | Low |
| **Platforms** | All C9K; CPU queue layout and punt-cause names vary by platform/ASIC |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| CPU queue ID | `cpuq-id` (key) | uint8 | Dimension |
| Queue name | `cpu-punt-queue-name` | string | Dimension |
| RX received (current) | `rx-recv-cur` | uint64 | Time chart (rate) |
| RX dropped (current) | `rx-dropped-cur` | uint64 | Time chart (rate) |

**Splunk Panel:** Per-CPU-queue punt rate time chart, drop rate time chart, drop-to-receive ratio gauge. Critical for CoPP monitoring — high drops indicate control plane overload.

#### Typed-Leaf Requirements

Root XPath: `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `cpuq-id` | count | CPU queue identifier. |
| `cpu-punt-queue-name` | string | Queue label for operator readability. |
| `rx-recv-cur` | counter | Current punted packets received by the queue. |
| `rx-dropped-cur` | counter | Current dropped packets at the queue; should drive exception views. |

> **Profile A (Baseline)** — Active on most Catalyst 9300 devices without extra configuration.

---

### §45. PoE Health (Detailed Port-Level)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-poe-health-oper.yang` |
| **XPath** | `/poe-health-xe:poe-health-oper-data` |
| **Sub ID** | 60029 |
| **Tier** | WARM (60s) |
| **Domain** | Environment and Power |
| **Dependency** | Hardware-Conditional |
| **Risk** | Discover-Only |
| **Platforms** | C9200/C9300/C9400 PoE-capable models; C9500/C9600 with PoE line cards |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Port number | `port-num` (key) | uint32 | Dimension |
| Port state | `port-state` | enum | Status indicator |
| Port event | `port-event` | enum | Table column |
| Port voltage | `port-voltage` | uint64 | Time chart |
| Consumed power (signal) | `signal-pair-info/consumed-power` | uint32 | Time chart |
| Consumed power (spare) | `spare-pair-info/consumed-power` | uint32 | Time chart |
| Shutdown count | `poe-meta-data/port-shutdown-cnt` | uint16 | Counter |
| MOSFET fault count | `poe-meta-data/mosfet-fault-cnt` | uint16 | Alert counter |
| Over-temp count | `poe-meta-data/over-tmp-cnt` | uint16 | Alert counter |
| Internal error count | `poe-meta-data/internal-err-cnt` | uint16 | Alert counter |
| Event time | `event-time` | date-and-time | Time stamp |

**Splunk Panel:** PoE port health event timeline, fault counter summary table, port voltage trend line. Complements section 6 by providing hardware-level diagnostics and fault history.

#### Typed-Leaf Requirements

Root XPath: `/poe-health-xe:poe-health-oper-data`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `port-num` | count | Port identity. |
| `port-state` | enum | Present operational health state. |
| `port-event` | enum | Most recent significant PoE event. |
| `port-voltage` | count | Electrical reading; unit depends on model encoding and should remain raw until validated against device output. |
| `signal-pair-info/consumed-power` | milliwatts | Consumed power on signal pair. |
| `spare-pair-info/consumed-power` | milliwatts | Consumed power on spare pair. |
| `poe-meta-data/port-shutdown-cnt` | counter | Historical shutdown count. |
| `poe-meta-data/mosfet-fault-cnt` | counter | Hardware fault count. |
| `poe-meta-data/over-tmp-cnt` | counter | Over-temperature fault count. |
| `poe-meta-data/internal-err-cnt` | counter | Internal error count. |
| `event-time` | timestamp | Time of last relevant PoE event. |

Requirement note: this section is intentionally more detailed than §6 because `Cisco-IOS-XE-poe-health-oper` is one of the stronger Cat 9K-specific operational differentiators.

### Remaining Features

The remaining feature sections below use the exact source type labels already documented in [plan.md](plan.md). This keeps the PRD aligned with the engineering reference while extending the leaf-and-type coverage across the full telemetry scope.

#### Activation Guidance

**Minimum Enablement Objective:** Use on PoE-capable platforms with powered endpoints attached.

**Telemetry Success Condition:** Port health and fault telemetry populate on active PoE ports.

**Verification CLI:** `show power inline`; `show power inline police`

**Reference Guide:** Interface and Hardware Components Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/int_hw/b_1718_int_and_hw_9300_cg.html

---

### §46. CEF / FIB State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-fib-oper.yang` |
| **XPath** | `/fib-ios-xe-oper:fib-oper-data` |
| **Sub ID** | 60016 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Baseline (extended) |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Total adjacencies | `adjacency-table/num-adjacencies` | uint32 | Gauge |
| Complete adjacencies | `adjacency-table/num-complete-adjacencies` | uint32 | Gauge |
| Incomplete adjacencies | `adjacency-table/num-incomplete-adjacencies` | uint32 | Alert counter |
| FIB enabled (IPv4) | `cef-state/fib/ipv4/fib-enabled` | boolean | Status indicator |
| FIB running (IPv4) | `cef-state/fib/ipv4/fib-running` | boolean | Status indicator |
| IPv4 punt total | `cef-statistics/ipv4-switching/total-punt` | uint64 | Time chart (rate) |
| IPv4 drop total | `cef-statistics/ipv4-switching/total-drop` | uint64 | Time chart (rate) |

**Splunk Panel:** CEF adjacency summary gauges (total/complete/incomplete), IPv4/IPv6 punt and drop rate time chart, FIB enabled/running status indicator, alert on incomplete adjacency count increase or high punt/drop rate.

#### Typed-Leaf Requirements

Root XPath: `/fib-ios-xe-oper:fib-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `adjacency-table/num-adjacencies` | uint32 | Total adjacencies |
| `adjacency-table/num-complete-adjacencies` | uint32 | Complete adjacencies |
| `adjacency-table/num-incomplete-adjacencies` | uint32 | Incomplete adjacencies |
| `cef-state/fib/ipv4/fib-enabled` | boolean | FIB enabled (IPv4) |
| `cef-state/fib/ipv4/fib-running` | boolean | FIB running (IPv4) |
| `cef-statistics/ipv4-switching/total-punt` | uint64 | IPv4 punt total |
| `cef-statistics/ipv4-switching/total-drop` | uint64 | IPv4 drop total |

> **Profile A Extended** — Usually available in a campus lab but may be platform- or topology-dependent.

---

### §47. EIGRP Routing (if applicable)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-eigrp-oper.yang` |
| **XPath** | `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance` |
| **Sub ID** | 50026 |
| **Tier** | COOL (300s) |
| **Domain** | L3 Routing |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| AFI | `afi` (key) | enum | Dimension |
| VRF | `vrf-name` (key) | string | Dimension |
| AS number | `as-num` (key) | uint16 | Dimension |
| Interface | `eigrp-interface/name` (key) | string | Dimension |
| Neighbor address | `eigrp-nbr/nbr-address` (key) | ip-address | Table column |
| Route metric | `eigrp-route/metric` | uint64 | Table column |
| Next hop | `eigrp-route/nexthop` | ip-address | Table column |

**Splunk Panel:** EIGRP neighbor table (address, interface, AS), topology table (prefix, metric, next-hop), neighbor count gauge.

#### Typed-Leaf Requirements

Root XPath: `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `afi` (key) | enum | AFI |
| `vrf-name` (key) | string | VRF |
| `as-num` (key) | uint16 | AS number |
| `eigrp-interface/name` (key) | string | Interface |
| `eigrp-nbr/nbr-address` (key) | ip-address | Neighbor address |
| `eigrp-route/metric` | uint64 | Route metric |
| `eigrp-route/nexthop` | ip-address | Next hop |

#### Activation Guidance

**Minimum Enablement Objective:** Configure only in a deliberate EIGRP lab with a real neighbor.

**Telemetry Success Condition:** Neighbor and instance state populate.

**Verification CLI:** `show ip eigrp neighbors`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §48. IS-IS Routing (if applicable)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-isis-oper.yang` |
| **XPath** | `/isis-ios-xe-oper:isis-oper-data/isis-instance` |
| **Sub ID** | 50027 |
| **Tier** | COOL (300s) |
| **Domain** | L3 Routing |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Instance tag | `tag` (key) | string | Dimension |
| System ID | `isis-neighbor/system-id` (key) | phys-address | Dimension |
| Level | `isis-neighbor/level` (key) | enum | Dimension |
| Interface | `isis-neighbor/if-name` (key) | string | Dimension |
| Neighbor state | `isis-neighbor/state` | enum | Status indicator |
| Hold time | `isis-neighbor/holdtime` | uint32 (sec) | Gauge |

**Splunk Panel:** IS-IS neighbor adjacency table with state indicators, alert on state != Up.

#### Typed-Leaf Requirements

Root XPath: `/isis-ios-xe-oper:isis-oper-data/isis-instance`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `tag` (key) | string | Instance tag |
| `isis-neighbor/system-id` (key) | phys-address | System ID |
| `isis-neighbor/level` (key) | enum | Level |
| `isis-neighbor/if-name` (key) | string | Interface |
| `isis-neighbor/state` | enum | Neighbor state |
| `isis-neighbor/holdtime` | uint32 (sec) | Hold time |

#### Activation Guidance

**Minimum Enablement Objective:** Configure only in a deliberate IS-IS lab with a real peer and participating interfaces.

**Telemetry Success Condition:** Neighbor and instance state populate.

**Verification CLI:** `show isis neighbors`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §49. BGP Neighbor Detail

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-bgp-nbr-oper.yang` |
| **XPath** | `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data` |
| **Sub ID** | 60017 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Neighbor address | `bgp-nbr-data/ip` (key) | ip-address | Dimension |
| Interface name | `bgp-nbr-data/if-name` (key) | string | Dimension |
| Address family | `bgp-nbr-data/af` (key) | enum | Dimension |
| VRF / NI | `bgp-nbr-data/ni-name` (key) | string | Dimension |
| TCP FSM state | `bgp-nbr-data/conn/state` | enum | Status indicator |
| Connection mode | `bgp-nbr-data/conn/mode` | enum | Table column |
| Received current prefixes | `bgp-nbr-cntrs/prfx-act/rcvd/cur-prfx` | uint64 | Gauge |
| Sent current prefixes | `bgp-nbr-cntrs/prfx-act/sent/cur-prfx` | uint64 | Gauge |
| Updates received | `bgp-nbr-cntrs/rcvd/updates` | uint32 | Time chart (rate) |
| Updates sent | `bgp-nbr-cntrs/sent/updates` | uint32 | Time chart (rate) |

**Splunk Panel:** Per-neighbor BGP detail table (state, AFI/SAFI, VRF, prefix counts), update counters trend, alert on neighbors leaving established states.

#### Typed-Leaf Requirements

Root XPath: `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `bgp-nbr-data/ip` (key) | ip-address | Neighbor address |
| `bgp-nbr-data/if-name` (key) | string | Interface |
| `bgp-nbr-data/af` (key) | enum | Address family |
| `bgp-nbr-data/ni-name` (key) | string | VRF / NI |
| `bgp-nbr-data/conn/state` | enum | TCP FSM state |
| `bgp-nbr-data/conn/mode` | enum | Connection mode |
| `bgp-nbr-cntrs/prfx-act/rcvd/cur-prfx` | uint64 | Received prefixes |
| `bgp-nbr-cntrs/prfx-act/sent/cur-prfx` | uint64 | Sent prefixes |
| `bgp-nbr-cntrs/rcvd/updates` | uint32 | Updates received |
| `bgp-nbr-cntrs/sent/updates` | uint32 | Updates sent |

#### Activation Guidance

**Minimum Enablement Objective:** Requires an active BGP session (see §24). Provides richer per-neighbor counters and prefix-level stats not available in the §24 root XPath.

**Telemetry Success Condition:** Per-neighbor prefix counts and update counters appear alongside session state.

**Verification CLI:** `show bgp neighbors`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §50. BGP RIB Detail

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-bgp-rib-oper.yang` |
| **XPath** | `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route` |
| **Sub ID** | 50028 |
| **Tier** | COOL (300s) |
| **Domain** | L3 Routing |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Prefix | `prefix` (key) | ip-prefix | Dimension |
| VRF / NI | `ni-name` (key) | string | Dimension |
| AFI/SAFI | `afi-safi` (key) | enum | Dimension |
| Route version | `version` | uint32 | Table column |
| Available paths | `avail-paths` | uint32 | Gauge |
| Next hop | `bgp-path/nh` | ip-address | Table column |
| MED | `bgp-path/metric` | uint32 | Table column |
| Local preference | `bgp-path/lp` | uint32 | Table column |
| Weight | `bgp-path/weight` | uint32 | Table column |
| Origin | `bgp-path/origin` | enum | Status indicator |

**Splunk Panel:** BGP prefix table (prefix, VRF, path count, next-hop, local-pref, MED), top prefixes by path fan-out, route-origin distribution chart.

#### Typed-Leaf Requirements

Root XPath: `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `prefix` (key) | ip-prefix | Prefix |
| `ni-name` (key) | string | VRF / NI |
| `afi-safi` (key) | enum | AFI/SAFI |
| `version` | uint32 | Route version |
| `avail-paths` | uint32 | Available paths |
| `bgp-path/nh` | ip-address | Next hop |
| `bgp-path/metric` | uint32 | MED |
| `bgp-path/lp` | uint32 | Local preference |
| `bgp-path/weight` | uint32 | Weight |
| `bgp-path/origin` | enum | Origin |

#### Activation Guidance

**Minimum Enablement Objective:** Requires an active BGP session with routes received. Best-path RIB will be empty until a neighbor is established and prefix exchange occurs.

**Telemetry Success Condition:** BGP route entries appear with path attributes (MED, local-pref, next-hop).

**Verification CLI:** `show bgp ipv4 unicast`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §51. High-Scale ARP

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-ip-arp-oper.yang` |
| **XPath** | `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry` |
| **Sub ID** | 50029 |
| **Tier** | COOL (300s) |
| **Domain** | L2 Topology |
| **Dependency** | Traffic-Dependent |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| IPv4 address | `addr` (key) | ipv4-address | Dimension |
| Interface | `if-name` (key) | string | Dimension |
| MAC address | `hw-addr` | mac-address | Table column |
| ARP mode | `mode` | enum | Status indicator |
| Update time | `update-time` | date-and-time | Table column |

**Splunk Panel:** High-scale ARP table by VRF and interface, mode distribution chart, churn view using update-time recency.

#### Typed-Leaf Requirements

Root XPath: `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `addr` (key) | ipv4-address | IPv4 address |
| `if-name` (key) | string | Interface |
| `hw-addr` | mac-address | MAC address |
| `mode` | enum | ARP mode |
| `update-time` | date-and-time | Update time |

#### Activation Guidance

**Minimum Enablement Objective:** Requires L3 interfaces with active ARP entries. Uses a finer-grained native ARP model than §12. Useful when L2 traffic is present on the segment.

**Telemetry Success Condition:** ARP table entries appear with hardware addresses and timestamps.

**Verification CLI:** `show ip arp`

**Reference Guide:** IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html

---

### §52. IPv6 Neighbor Discovery

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-ipv6-nd-oper.yang` |
| **XPath** | `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry` |
| **Sub ID** | 50030 |
| **Tier** | COOL (300s) |
| **Domain** | L2 Topology |
| **Dependency** | Peer-Dependent |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| IPv6 address | `v6addr` (key) | ipv6-address | Dimension |
| Interface | `if-name` (key) | string | Dimension |
| MAC address | `mac-addr` | mac-address | Table column |
| ND mode | `mode` | enum | Status indicator |
| Neighbor state | `state` | enum | Status indicator |
| Update time | `update-time` | date-and-time | Table column |
| Is router | `is-router` | boolean | Table column |

**Splunk Panel:** IPv6 neighbor state table, state distribution chart, stale/probe/incomplete alert indicator.

#### Typed-Leaf Requirements

Root XPath: `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `v6addr` (key) | ipv6-address | IPv6 address |
| `if-name` (key) | string | Interface |
| `mac-addr` | mac-address | MAC address |
| `mode` | enum | ND mode |
| `state` | enum | Neighbor state |
| `update-time` | date-and-time | Update time |
| `is-router` | boolean | Is router |

#### Activation Guidance

**Minimum Enablement Objective:** Requires IPv6 addressing on at least one interface with reachable IPv6 neighbors.

**Telemetry Success Condition:** IPv6 ND entries appear with state (reachable, stale, probe, incomplete).

**Verification CLI:** `show ipv6 neighbors`

**Reference Guide:** IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html

---

### §53. IS-IS Interface Detail

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-isis-intf-oper.yang` |
| **XPath** | `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type` |
| **Sub ID** | 60018 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Peer-Dependent |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Instance tag | `tag` (key) | string | Dimension |
| Interface | `isis-if/if-name` (key) | string | Dimension |
| Interface enabled | `isis-if/is-enabled` | boolean | Status indicator |
| Circuit type | `isis-if/circuit-type` | enum | Table column |
| Neighbor system ID | `isis-if-nbr/system-id` (key) | phys-address | Dimension |
| Neighbor level | `isis-if-nbr/level` (key) | enum | Dimension |
| Neighbor state | `isis-if-nbr/adj-state` | enum | Status indicator |
| Neighbor IPv4 | `isis-if-nbr/nbr-ipv4-addr` | ip-address | Table column |
| Neighbor uptime | `isis-if-nbr/up-time` | date-and-time | Table column |

**Splunk Panel:** IS-IS interface and adjacency detail table, adjacency-state summary, per-interface enablement status view.

#### Typed-Leaf Requirements

Root XPath: `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `tag` (key) | string | Instance tag |
| `isis-if/if-name` (key) | string | Interface |
| `isis-if/is-enabled` | boolean | Interface enabled |
| `isis-if/circuit-type` | enum | Circuit type |
| `isis-if-nbr/system-id` (key) | phys-address | Neighbor system ID |
| `isis-if-nbr/level` (key) | enum | Neighbor level |
| `isis-if-nbr/adj-state` | enum | Neighbor state |
| `isis-if-nbr/nbr-ipv4-addr` | ip-address | Neighbor IPv4 |
| `isis-if-nbr/up-time` | date-and-time | Neighbor uptime |

#### Activation Guidance

**Minimum Enablement Objective:** Requires IS-IS enabled on interfaces with at least one established adjacency (see §48). Provides per-interface adjacency data not available in the §48 root XPath.

**Telemetry Success Condition:** Interface-level adjacency state and neighbor detail populate.

**Verification CLI:** `show isis interface`

**Reference Guide:** IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html

---

### §54. Multicast Routing State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-mroute-oper.yang` |
| **XPath** | `/mroute-ios-xe-oper:mroute-oper-data/mroute-state` |
| **Sub ID** | 60019 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Feature-Only |
| **Risk** | Medium |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Source | `source` (key) | ip-address | Dimension |
| Group | `group` (key) | ip-address | Dimension |
| VRF | `vrf` (key) | string | Dimension |
| Address family | `af` (key) | enum | Dimension |
| Ingress interface | `ingress-if/if-name` | string | Table column |
| RPF neighbor | `rpf-nbr` | ip-address | Table column |
| Multicast mode | `mroute-mode` | enum | Status indicator |
| Software packets/sec | `sw-packets-per-second` | uint64 | Time chart |
| Software kbps | `sw-kbits-per-second` | uint64 | Time chart |
| Software RPF failures | `sw-rpf-failed` | uint64 | Alert counter |

**Splunk Panel:** Multicast tree table (S,G, VRF, RPF), software traffic trends, alert on rising RPF failures.

#### Typed-Leaf Requirements

Root XPath: `/mroute-ios-xe-oper:mroute-oper-data/mroute-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `source` (key) | ip-address | Source |
| `group` (key) | ip-address | Group |
| `vrf` (key) | string | VRF |
| `af` (key) | enum | Address family |
| `ingress-if/if-name` | string | Ingress interface |
| `rpf-nbr` | ip-address | RPF neighbor |
| `mroute-mode` | enum | Multicast mode |
| `sw-packets-per-second` | uint64 | Software packets/sec |
| `sw-kbits-per-second` | uint64 | Software kbps |
| `sw-rpf-failed` | uint64 | Software RPF failures |

#### Activation Guidance

**Minimum Enablement Objective:** Enable IP multicast routing and configure PIM on at least one interface. At least one active (S,G) or (*,G) entry must exist for data to appear.

**Telemetry Success Condition:** Multicast routing table entries appear with ingress interface, RPF neighbor, and traffic rates.

**Verification CLI:** `show ip mroute`; `show ip pim neighbor`

**Reference Guide:** IP Multicast Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip_multicast/b_1718_ip_multicast_9300_cg.html

---

### §55. Stack Member / Stackwise Virtual Detail

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-stack-member-oper.yang` |
| **XPath** | `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info` |
| **Sub ID** | 60020 |
| **Tier** | WARM (60s) |
| **Domain** | Platform and Resources |
| **Dependency** | Hardware-Conditional |
| **Risk** | Discover-Only |
| **Platforms** | C9200/C9300 stackable models and C9300 StackWise Virtual; C9400/C9500/C9600 do not stack |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Chassis number | `chassis-num` (key) | uint8 | Dimension |
| Stack mode | `stack-mode` | enum | Status indicator |
| Boot time | `mbr-boottime` | date-and-time | Table column |
| Peer latency | `latency` | uint32 (ns) | Gauge |
| SVL bandwidth | `svl-bw` | uint32 (Gbps) | Gauge |
| Stack port link OK | `mbr-port/link-ok` | boolean | Status indicator |
| Stack port active | `mbr-port/link-actv` | boolean | Status indicator |

**Splunk Panel:** Stack member inventory table, Stackwise Virtual health gauges, stack-port status view, alert on link loss or peer-latency anomalies.

#### Typed-Leaf Requirements

Root XPath: `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `chassis-num` (key) | uint8 | Chassis number |
| `stack-mode` | enum | Stack mode |
| `mbr-boottime` | date-and-time | Boot time |
| `latency` | uint32 (ns) | Peer latency |
| `svl-bw` | uint32 (Gbps) | SVL bandwidth |
| `mbr-port/link-ok` | boolean | Stack port link OK |
| `mbr-port/link-actv` | boolean | Stack port active |

#### Activation Guidance

**Minimum Enablement Objective:** Only meaningful on stacked or Stackwise Virtual (SVL) deployments. On a standalone device the data will be empty or minimal.

**Telemetry Success Condition:** Stack member info appears with chassis role, SVL bandwidth, and stack-port link status.

**Verification CLI:** `show stackwise-virtual`; `show switch detail`

**Reference Guide:** Stacking Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/stck_mgr/b_1718_stck_mgr_9300_cg.html

---

### §56. Tunnel Interface State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-tunnel-oper.yang` |
| **XPath** | `/ios-tunnel-oper:tunnel-oper-data/tunnel-if` |
| **Sub ID** | 60021 |
| **Tier** | WARM (60s) |
| **Domain** | Interfaces |
| **Dependency** | Feature-Only |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Tunnel name | `name` (key) | string | Dimension |
| Tunnel mode | `mode` | enum | Status indicator |
| Interface VRF | `intf-vrf` | string | Dimension |
| Admin status | `admin-status` | enum | Status indicator |
| Oper status | `status` | enum | Status indicator |
| Source address | `src-addr` | ip-address | Table column |
| Destination address | `dst-addr` | ip-address | Table column |
| MTU | `mtu` | uint32 | Gauge |
| TX bandwidth | `tx-bandwidth` | uint32 (kbps) | Time chart |
| RX bandwidth | `rx-bandwidth` | uint32 (kbps) | Time chart |

**Splunk Panel:** Tunnel health table (status, endpoints, VRF, mode), bandwidth trend chart, alert on tunnel down transitions.

#### Typed-Leaf Requirements

Root XPath: `/ios-tunnel-oper:tunnel-oper-data/tunnel-if`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `name` (key) | string | Tunnel name |
| `mode` | enum | Tunnel mode |
| `intf-vrf` | string | Interface VRF |
| `admin-status` | enum | Admin status |
| `status` | enum | Oper status |
| `src-addr` | ip-address | Source address |
| `dst-addr` | ip-address | Destination address |
| `mtu` | uint32 | MTU |
| `tx-bandwidth` | uint32 (kbps) | TX bandwidth |
| `rx-bandwidth` | uint32 (kbps) | RX bandwidth |

#### Activation Guidance

**Minimum Enablement Objective:** Configure at least one tunnel interface (GRE, IPinIP, or equivalent). The subscription will be empty until a tunnel interface exists.

**Telemetry Success Condition:** Tunnel admin/oper status, endpoint addresses, and bandwidth metrics appear.

**Verification CLI:** `show interfaces tunnel <num>`

**Reference Guide:** Interface and Hardware Components Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/int_hw/b_1718_int_and_hw_9300_cg.html

---

### §57. YANG Management Plane Interfaces

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-yang-interfaces-oper.yang` |
| **XPath** | `/yang-interfaces-oper:yang-interfaces-oper-data` |
| **Sub ID** | 50031 |
| **Tier** | COOL (300s) |
| **Domain** | Operations |
| **Dependency** | Service-Dependent |
| **Risk** | Low |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Local VRF | `local-vrf/vrf-name` (key) | string | Dimension |
| Local VRF state | `local-vrf/state` | enum | Status indicator |
| NETCONF SSH host key | `ssh-server/hostkey-name` | string | Table column |
| RSA-SHA2-256 enabled | `ssh-server/hostkey-alg/rsa-sha2-256` | boolean | Status indicator |
| AES128-CTR enabled | `ssh-server/ciphers/aes128-ctr` | boolean | Status indicator |
| HMAC-SHA2-256 enabled | `ssh-server/macs/hmac-sha2-256` | boolean | Status indicator |

**Splunk Panel:** Management-plane readiness table (VRF reachability and SSH algorithm posture), alert when NETCONF local VRF state is down.

#### Typed-Leaf Requirements

Root XPath: `/yang-interfaces-oper:yang-interfaces-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `local-vrf/vrf-name` (key) | string | Local VRF |
| `local-vrf/state` | enum | Local VRF state |
| `ssh-server/hostkey-name` | string | NETCONF SSH host key |
| `ssh-server/hostkey-alg/rsa-sha2-256` | boolean | RSA-SHA2-256 enabled |
| `ssh-server/ciphers/aes128-ctr` | boolean | AES128-CTR enabled |
| `ssh-server/macs/hmac-sha2-256` | boolean | HMAC-SHA2-256 enabled |

#### Activation Guidance

**Minimum Enablement Objective:** Requires NETCONF or RESTCONF to be enabled. The subscription monitors the management-plane SSH and VRF configuration used by YANG interfaces.

**Telemetry Success Condition:** Local VRF state and SSH algorithm posture appear in the telemetry stream.

**Verification CLI:** `show netconf-yang status`; `show platform software yang-management process`

**Reference Guide:** Programmability Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b_1718_programmability_cg.html

---

### §59. PIM Multicast State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-pim-oper.yang` |
| **XPath** | `/pim-ios-xe-oper:pim-oper-data` |
| **Sub ID** | 60022 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Service-Dependent |
| **Risk** | Low |
| **Platforms** | All C9K (C9200, C9300, C9400, C9500, C9600); model available since IOS XE 17.3.1 |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VRF | `pim-neighbor-entry/af (key)` | enum (ipv4/ipv6) | Dimension |
| VRF name | `pim-neighbor-entry/vrf (key)` | string | Dimension |
| Interface name | `pim-neighbor-entry/if-name (key)` | string | Dimension |
| Neighbor address | `pim-neighbor-entry/nbr-addr` | ip-address | Table column |
| Neighbor uptime | `pim-neighbor-entry/uptime` | string | Table column |
| Neighbor expiry | `pim-neighbor-entry/expires` | string | Status indicator |
| DR priority | `pim-neighbor-entry/dr-priority` | uint32 | Table column |
| Is DR | `pim-neighbor-entry/is-dr` | boolean | Status indicator |
| RP address | `pim-rp-entry/rp-addr (key)` | ip-address | Table column |
| RP source | `pim-rp-mapping-entry/state/info-source` | ip-address | Table column |
| RP uptime | `pim-rp-mapping-entry/state/rp-uptime` | string | Table column |
| Interface PIM mode | `pim-if-entry/pim-mode` | enum | Dimension |

**Splunk Panel:** PIM neighbor table with uptime and DR election status per interface, RP mapping summary, alert when PIM neighbor count drops or RP mapping expires.

#### Typed-Leaf Requirements

Root XPath: `/pim-ios-xe-oper:pim-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `pim-neighbor-entry/af (key)` | enum | Address family |
| `pim-neighbor-entry/vrf (key)` | string | VRF name |
| `pim-neighbor-entry/if-name (key)` | string | Interface name |
| `pim-neighbor-entry/nbr-addr` | ip-address | Neighbor address |
| `pim-neighbor-entry/uptime` | string | Neighbor uptime |
| `pim-neighbor-entry/dr-priority` | uint32 | DR priority |
| `pim-neighbor-entry/is-dr` | boolean | Is designated router |
| `pim-rp-entry/rp-addr (key)` | ip-address | RP address |
| `pim-if-entry/pim-mode` | enum | PIM mode |

#### Activation Guidance

**Minimum Enablement Objective:** Requires PIM to be enabled on at least one interface (`ip pim sparse-mode` or `ip pim dense-mode`). RP mapping (static or Auto-RP/BSR) should be configured for useful RP data.

**Telemetry Success Condition:** PIM neighbor entries and RP mappings appear in the telemetry stream.

**Verification CLI:** `show ip pim neighbor`; `show ip pim rp mapping`; `show ip pim interface`

**Reference Guide:** IP Multicast Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipmulti_pim/configuration/xe-17/imc-pim-xe-17-book.html

---
### §60. MPLS LDP Operational State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-mpls-ldp-oper.yang` |
| **XPath** | `/mpls-ldp-ios-xe-oper:mpls-ldp-oper-data` |
| **Sub ID** | 60023 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Service-Dependent |
| **Risk** | Low |
| **Platforms** | Primarily C9500, C9600; available on C9300/C9400 when MPLS is licensed/enabled. Model since IOS XE 16.5.1 |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VRF name | `mpls-ldp-vrf/vrf-name (key)` | string | Dimension |
| LDP peer address | `mpls-ldp-peer/peer-id` | string | Table column |
| Peer state | `mpls-ldp-peer/state` | enum | Status indicator |
| Session uptime | `mpls-ldp-peer/sess-up-time` | string | Table column |
| Label space ID | `mpls-ldp-peer/label-space-id` | uint16 | Dimension |
| Graceful restart enabled | `mpls-ldp-peer/graceful-restart-enabled` | boolean | Status indicator |
| LDP interface name | `mpls-ldp-intf/intf-name (key)` | string | Dimension |

**Splunk Panel:** MPLS LDP peer table showing peer state, session uptime, and graceful-restart status. Alert when peer state transitions away from operational.

#### Typed-Leaf Requirements

Root XPath: `/mpls-ldp-ios-xe-oper:mpls-ldp-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `mpls-ldp-vrf/vrf-name (key)` | string | VRF name |
| `mpls-ldp-peer/peer-id` | string | LDP peer ID |
| `mpls-ldp-peer/state` | enum | Peer state |
| `mpls-ldp-peer/sess-up-time` | string | Session uptime |
| `mpls-ldp-peer/graceful-restart-enabled` | boolean | GR enabled |
| `mpls-ldp-intf/intf-name (key)` | string | Interface name |

#### Activation Guidance

**Minimum Enablement Objective:** Requires MPLS LDP to be enabled globally (`mpls ldp router-id`) and on at least one interface (`mpls ip`). At least one LDP peer session should be established.

**Telemetry Success Condition:** LDP peer entries with session state and uptime appear in the telemetry stream.

**Verification CLI:** `show mpls ldp neighbor`; `show mpls ldp bindings`; `show mpls interfaces`

**Reference Guide:** MPLS Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_ldp/configuration/xe-17/mp-ldp-xe-17-book.html

---
### §61. MPLS Forwarding (LFIB)

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-mpls-forwarding-oper.yang` |
| **XPath** | `/mpls-forwarding-ios-xe-oper:mpls-forwarding-oper-data` |
| **Sub ID** | 50032 |
| **Tier** | COOL (300s) |
| **Domain** | L3 Routing |
| **Dependency** | Service-Dependent |
| **Risk** | Low |
| **Platforms** | Primarily C9500, C9600; available on C9300/C9400 when MPLS is licensed/enabled. Model since IOS XE 16.5.1 |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Local label | `mpls-forwarding-entry/local-label (key)` | uint32 | Dimension |
| Outgoing label | `mpls-forwarding-entry/outgoing-label` | string | Table column |
| Prefix | `mpls-forwarding-entry/prefix` | string | Table column |
| Outgoing interface | `mpls-forwarding-entry/outgoing-interface` | string | Dimension |
| Next hop | `mpls-forwarding-entry/next-hop` | ip-address | Table column |
| Bytes switched | `mpls-forwarding-entry/bytes-switched` | uint64 (counter) | Line chart |
| Connection ID | `mpls-forwarding-entry/connection-id` | uint32 | Dimension |

**Splunk Panel:** MPLS LFIB table showing label-to-prefix bindings, outgoing interfaces, and bytes-switched counters. Useful for verifying label path continuity.

#### Typed-Leaf Requirements

Root XPath: `/mpls-forwarding-ios-xe-oper:mpls-forwarding-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `mpls-forwarding-entry/local-label (key)` | uint32 | Local label |
| `mpls-forwarding-entry/outgoing-label` | string | Outgoing label |
| `mpls-forwarding-entry/prefix` | string | Destination prefix |
| `mpls-forwarding-entry/outgoing-interface` | string | Outgoing interface |
| `mpls-forwarding-entry/next-hop` | ip-address | Next hop |
| `mpls-forwarding-entry/bytes-switched` | uint64 | Bytes switched |

#### Activation Guidance

**Minimum Enablement Objective:** Requires MPLS forwarding to be active with label bindings in the LFIB. Typically accompanies LDP or RSVP-TE label distribution.

**Telemetry Success Condition:** LFIB entries with local/outgoing labels and bytes-switched counters appear in the telemetry stream.

**Verification CLI:** `show mpls forwarding-table`; `show mpls forwarding-table detail`

**Reference Guide:** MPLS Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/mp_ldp/configuration/xe-17/mp-ldp-xe-17-book.html

---
### §62. LISP Operational State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-lisp-oper.yang` |
| **XPath** | `/lisp-ios-xe-oper:lisp-state` |
| **Sub ID** | 60024 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Service-Dependent |
| **Risk** | Low |
| **Platforms** | All C9K (SD-Access deployments); model available since IOS XE 16.7.1 |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| LISP router instance ID | `lisp-routers/lisp-router/instance-id (key)` | uint32 | Dimension |
| AF type | `lisp-routers/lisp-router/af (key)` | enum | Dimension |
| Local EID prefix | `lisp-routers/lisp-router/local-eids/local-eid/prefix` | string | Table column |
| Map-server address | `lisp-routers/lisp-router/map-servers/map-server/addr` | ip-address | Table column |
| Map-server state | `lisp-routers/lisp-router/map-servers/map-server/state` | enum | Status indicator |
| Site registration count | `lisp-routers/lisp-router/site/site-registration` | uint32 | Single value |
| RLOC address | `lisp-routers/lisp-router/local-eids/local-eid/rlocs/rloc/rloc-addr` | ip-address | Table column |
| RLOC state | `lisp-routers/lisp-router/local-eids/local-eid/rlocs/rloc/rloc-state` | enum | Status indicator |

**Splunk Panel:** LISP EID/RLOC mapping table, map-server reachability status, site registration count. Critical for SD-Access fabric monitoring — alert on map-server state changes.

#### Typed-Leaf Requirements

Root XPath: `/lisp-ios-xe-oper:lisp-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `lisp-routers/lisp-router/instance-id (key)` | uint32 | LISP instance ID |
| `lisp-routers/lisp-router/af (key)` | enum | Address family |
| `lisp-routers/lisp-router/local-eids/local-eid/prefix` | string | Local EID prefix |
| `lisp-routers/lisp-router/map-servers/map-server/addr` | ip-address | Map-server address |
| `lisp-routers/lisp-router/map-servers/map-server/state` | enum | Map-server state |
| `lisp-routers/lisp-router/local-eids/local-eid/rlocs/rloc/rloc-addr` | ip-address | RLOC address |
| `lisp-routers/lisp-router/local-eids/local-eid/rlocs/rloc/rloc-state` | enum | RLOC state |

#### Activation Guidance

**Minimum Enablement Objective:** Requires LISP to be configured — typically via SD-Access (DNA Center) provisioning or manual `router lisp` configuration with at least one instance-id and EID/RLOC mapping.

**Telemetry Success Condition:** LISP router instances with EID prefixes, map-server addresses, and RLOC states appear in the telemetry stream.

**Verification CLI:** `show lisp session`; `show lisp site`; `show lisp eid-table summary`; `show lisp map-server`

**Reference Guide:** LISP Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_lisp/configuration/xe-17/irl-xe-17-book.html

---
### §63. VXLAN NVE Tunnel Endpoints

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-nve-oper.yang` |
| **XPath** | `/nve-ios-xe-oper:nve-oper-data` |
| **Sub ID** | 60025 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Service-Dependent |
| **Risk** | Low |
| **Platforms** | C9300, C9400, C9500, C9600 (VXLAN-capable SKUs); model available since IOS XE 17.15.1 |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| NVE interface | `nve-intf/if-name (key)` | string | Dimension |
| Source interface | `nve-intf/src-if-name` | string | Table column |
| Admin state | `nve-intf/admin-state` | enum | Status indicator |
| Oper state | `nve-intf/oper-state` | enum | Status indicator |
| VNI ID | `nve-intf/vni/vni-id (key)` | uint32 | Dimension |
| VNI state | `nve-intf/vni/vni-state` | enum | Status indicator |
| Peer IP | `nve-intf/vni/peers/peer/peer-ip` | ip-address | Table column |
| Peer state | `nve-intf/vni/peers/peer/peer-state` | enum | Status indicator |

**Splunk Panel:** NVE tunnel endpoint table showing VNI-to-peer mappings, admin/oper state, and peer reachability. Alert on NVE oper-state down or peer-state changes.

#### Typed-Leaf Requirements

Root XPath: `/nve-ios-xe-oper:nve-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `nve-intf/if-name (key)` | string | NVE interface name |
| `nve-intf/src-if-name` | string | Source interface |
| `nve-intf/admin-state` | enum | Admin state |
| `nve-intf/oper-state` | enum | Oper state |
| `nve-intf/vni/vni-id (key)` | uint32 | VNI ID |
| `nve-intf/vni/vni-state` | enum | VNI state |
| `nve-intf/vni/peers/peer/peer-ip` | ip-address | Peer IP |
| `nve-intf/vni/peers/peer/peer-state` | enum | Peer state |

#### Activation Guidance

**Minimum Enablement Objective:** Requires at least one NVE interface (`interface nve 1`) with a VXLAN source interface and VNI mappings configured. Typically used with EVPN or flood-and-learn VXLAN.

**Telemetry Success Condition:** NVE interface entries with VNI states and peer reachability appear in the telemetry stream.

**Verification CLI:** `show nve peers`; `show nve vni`; `show nve interface nve 1`

**Reference Guide:** VXLAN Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/cether/configuration/xe-17/ce-xe-17-book.html

---
### §64. EVPN Operational State

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-evpn-oper.yang` |
| **XPath** | `/evpn-ios-xe-oper:evpn-oper-data` |
| **Sub ID** | 60026 |
| **Tier** | WARM (60s) |
| **Domain** | L3 Routing |
| **Dependency** | Service-Dependent |
| **Risk** | Low |
| **Platforms** | C9500, C9600 (EVPN VXLAN); C9300/C9400 with EVPN support varies by release. Model since IOS XE 17.17.1 |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| EVPN instance ID | `evpn-instance/evi (key)` | uint32 | Dimension |
| Encapsulation type | `evpn-instance/encap-type` | enum | Dimension |
| RD | `evpn-instance/rd` | string | Table column |
| Import RT | `evpn-instance/import-rt` | string | Table column |
| Export RT | `evpn-instance/export-rt` | string | Table column |
| Bridge domain | `evpn-instance/bridge-domain-id` | uint32 | Dimension |
| MAC route count | `evpn-instance/mac-count` | uint32 (gauge) | Single value |
| IP route count | `evpn-instance/ip-count` | uint32 (gauge) | Single value |

**Splunk Panel:** EVPN instance summary showing EVI-to-VNI bindings, RT configuration, and MAC/IP route counts per instance. Alert on unexpected MAC count spikes.

#### Typed-Leaf Requirements

Root XPath: `/evpn-ios-xe-oper:evpn-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `evpn-instance/evi (key)` | uint32 | EVPN instance ID |
| `evpn-instance/encap-type` | enum | Encapsulation type |
| `evpn-instance/rd` | string | Route distinguisher |
| `evpn-instance/import-rt` | string | Import route-target |
| `evpn-instance/export-rt` | string | Export route-target |
| `evpn-instance/bridge-domain-id` | uint32 | Bridge domain ID |
| `evpn-instance/mac-count` | uint32 | MAC route count |
| `evpn-instance/ip-count` | uint32 | IP route count |

#### Activation Guidance

**Minimum Enablement Objective:** Requires EVPN to be configured with at least one EVI (EVPN instance) bound to a VNI or bridge domain. Typically deployed with VXLAN fabric.

**Telemetry Success Condition:** EVPN instance entries with EVI bindings, RD/RT, and MAC/IP counts appear in the telemetry stream.

**Verification CLI:** `show l2vpn evpn summary`; `show l2vpn evpn evi detail`; `show bgp l2vpn evpn summary`

**Reference Guide:** EVPN VXLAN Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/cether/configuration/xe-17/ce-xe-17-book/evpn-vxlan.html

---
### §65. PTP / SyncE Timing

| | |
|---|---|
| **YANG Module** | `Cisco-IOS-XE-ptp-synce-oper.yang` |
| **XPath** | `/ptp-synce-ios-xe-oper:ptp-synce-oper-data` |
| **Sub ID** | 50033 |
| **Tier** | COOL (300s) |
| **Domain** | Platform and Resources |
| **Dependency** | Service-Dependent |
| **Risk** | Low |
| **Platforms** | C9K models with timing/PTP hardware support (varies by SKU); model available since IOS XE 16.8.1 |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| PTP clock ID | `ptp-data/clock-id` | string | Dimension |
| PTP domain | `ptp-data/domain` | uint8 | Dimension |
| Clock state | `ptp-data/clock-state` | enum | Status indicator |
| Grandmaster clock ID | `ptp-data/gm-clock-id` | string | Table column |
| Mean path delay (ns) | `ptp-data/mean-path-delay` | int64 (gauge) | Sparkline |
| Offset from master (ns) | `ptp-data/offset-from-master` | int64 (gauge) | Sparkline — alert on drift |
| Steps removed | `ptp-data/steps-removed` | uint16 (gauge) | Single value |
| SyncE clock state | `synce-data/synce-clock-state` | enum | Status indicator |
| SyncE selected source | `synce-data/selected-source` | string | Table column |

**Splunk Panel:** PTP clock synchronization status: offset-from-master, mean-path-delay, grandmaster identity. SyncE clock state and selected source. Alert on clock state changes or offset drift beyond threshold.

#### Typed-Leaf Requirements

Root XPath: `/ptp-synce-ios-xe-oper:ptp-synce-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `ptp-data/clock-id` | string | PTP clock ID |
| `ptp-data/domain` | uint8 | PTP domain |
| `ptp-data/clock-state` | enum | PTP clock state |
| `ptp-data/gm-clock-id` | string | Grandmaster clock ID |
| `ptp-data/mean-path-delay` | int64 | Mean path delay (ns) |
| `ptp-data/offset-from-master` | int64 | Offset from master (ns) |
| `ptp-data/steps-removed` | uint16 | Steps removed |
| `synce-data/synce-clock-state` | enum | SyncE clock state |
| `synce-data/selected-source` | string | SyncE selected source |

#### Activation Guidance

**Minimum Enablement Objective:** Requires PTP (IEEE 1588) or SyncE to be configured on the device. PTP requires `ptp clock ordinary domain <N>` and at least one PTP-enabled interface.

**Telemetry Success Condition:** PTP clock state, offset-from-master, and/or SyncE clock state appear in the telemetry stream.

**Verification CLI:** `show ptp clock`; `show ptp port`; `show network-clocks synchronization`

**Reference Guide:** PTP Configuration Guide: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ptp/configuration/xe-17/ptp-xe-17-book.html

---
### §67. IETF Interfaces Operational State

| | |
|---|---|
| **YANG Module** | `ietf-interfaces.yang` |
| **XPath** | `/if:interfaces-state/interface` |
| **Sub ID** | 60027 |
| **Tier** | WARM (60s) |
| **Domain** | Interfaces |
| **Dependency** | Always-On |
| **Risk** | Low |
| **Platforms** | All C9K; IETF interfaces model available since IOS XE 16.3.1 |

#### KPI Table

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | `interface/name (key)` | string | Dimension |
| Admin status | `interface/admin-status` | enum (up/down/testing) | Status indicator |
| Oper status | `interface/oper-status` | enum | Status indicator |
| Speed (bps) | `interface/speed` | gauge64 | Single value |
| Last change | `interface/last-change` | date-and-time | Table column |
| In octets | `interface/statistics/in-octets` | uint64 (counter) | Line chart |
| In unicast packets | `interface/statistics/in-unicast-pkts` | uint64 (counter) | Line chart |
| In broadcast packets | `interface/statistics/in-broadcast-pkts` | uint64 (counter) | Line chart |
| In multicast packets | `interface/statistics/in-multicast-pkts` | uint64 (counter) | Line chart |
| In discards | `interface/statistics/in-discards` | uint32 (counter) | Line chart — alert on rise |
| In errors | `interface/statistics/in-errors` | uint32 (counter) | Line chart — alert on rise |
| In unknown protos | `interface/statistics/in-unknown-protos` | uint32 (counter) | Line chart |
| Out octets | `interface/statistics/out-octets` | uint64 (counter) | Line chart |
| Out unicast packets | `interface/statistics/out-unicast-pkts` | uint64 (counter) | Line chart |
| Out broadcast packets | `interface/statistics/out-broadcast-pkts` | uint64 (counter) | Line chart |
| Out multicast packets | `interface/statistics/out-multicast-pkts` | uint64 (counter) | Line chart |
| Out discards | `interface/statistics/out-discards` | uint32 (counter) | Line chart — alert on rise |
| Out errors | `interface/statistics/out-errors` | uint32 (counter) | Line chart — alert on rise |

**Splunk Panel:** IETF standards-based interface counters: per-interface in/out octets, unicast/broadcast/multicast packets, errors, and discards. Provides a vendor-neutral view complementing the native §7 interface model. Includes discontinuity tracking via `discontinuity-time`.

#### Typed-Leaf Requirements

Root XPath: `/if:interfaces-state/interface`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `interface/name (key)` | string | Interface name |
| `interface/admin-status` | enum | Admin status |
| `interface/oper-status` | enum | Oper status |
| `interface/speed` | gauge64 | Interface speed (bps) |
| `interface/last-change` | date-and-time | Last state change |
| `interface/statistics/in-octets` | uint64 | In octets |
| `interface/statistics/in-unicast-pkts` | uint64 | In unicast packets |
| `interface/statistics/in-discards` | uint32 | In discards |
| `interface/statistics/in-errors` | uint32 | In errors |
| `interface/statistics/out-octets` | uint64 | Out octets |
| `interface/statistics/out-unicast-pkts` | uint64 | Out unicast packets |
| `interface/statistics/out-discards` | uint32 | Out discards |
| `interface/statistics/out-errors` | uint32 | Out errors |

#### Activation Guidance

**Minimum Enablement Objective:** Always available — the IETF interfaces model provides operational state for all interfaces without additional feature configuration. Complements the native Cisco-IOS-XE-interfaces-oper model (§7) with a standards-based counter set aligned with IF-MIB.

**Telemetry Success Condition:** Per-interface admin/oper status and traffic counters appear in the telemetry stream.

**Verification CLI:** `show interfaces`; `show interfaces counters`; `show ip interface brief`

**Reference Guide:** RFC 8343 (YANG Interface Management)

---

---

## Part IV: IOS XE Subscription Configuration

Complete gRPC dial-out subscription config for all 65 target features and 66 subscriptions. Subscription IDs use a tier-based scheme: 30xxx (HOT), 60xxx (WARM), 50xxx (COOL). Receiver IP and port are placeholders — update to match your OTel collector.

Variables to customize before applying:
- `RECEIVER_IP` — OTel collector IP address (e.g., 10.1.1.3)
- `RECEIVER_PORT` — gRPC listen port (e.g., 57500)

```
! ============================================================
! Prerequisite: gRPC Dial-Out Receiver Profile
! ============================================================
telemetry receiver protocol otel-collector
 host ip-address RECEIVER_IP RECEIVER_PORT
 protocol grpc-tcp

! ============================================================
! HOT TIER — 30-second polling (3000 centiseconds)
! CPU, Interfaces, Process Memory, Punt/Inject
! ============================================================

! --- §1. CPU Utilization ---
telemetry ietf subscription 30001
 encoding encode-kvgpb
 filter xpath /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §3. Process Memory ---
telemetry ietf subscription 30002
 encoding encode-kvgpb
 filter xpath /process-memory-ios-xe-oper:memory-usage-processes
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §7. Interface Statistics ---
telemetry ietf subscription 30003
 encoding encode-kvgpb
 filter xpath /interfaces-ios-xe-oper:interfaces/interface
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §44. CPU Punt/Inject Counters ---
telemetry ietf subscription 30004
 encoding encode-kvgpb
 filter xpath /switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================
! WARM TIER — 60-second polling (6000 centiseconds)
! Environment, Platform, Routing, STP, Stack, PoE, FHRP, etc.
! ============================================================

! --- §2. Memory Statistics ---
telemetry ietf subscription 60001
 encoding encode-kvgpb
 filter xpath /memory-ios-xe-oper:memory-statistics/memory-statistic
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §4. System DRAM (Platform Software) ---
telemetry ietf subscription 60002
 encoding encode-kvgpb
 filter xpath /platform-sw-ios-xe-oper:cisco-platform-software/control-processes
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §5. Environment Sensors ---
telemetry ietf subscription 60003
 encoding encode-kvgpb
 filter xpath /environment-ios-xe-oper:environment-sensors
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §6. PoE Operational Data ---
telemetry ietf subscription 60004
 encoding encode-kvgpb
 filter xpath /poe-ios-xe-oper:poe-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §8. Spanning Tree ---
telemetry ietf subscription 60005
 encoding encode-kvgpb
 filter xpath /stp-ios-xe-oper:stp-details
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §9. Stack Health ---
telemetry ietf subscription 60006
 encoding encode-kvgpb
 filter xpath /stack-ios-xe-oper:stack-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §15. Platform Components ---
telemetry ietf subscription 60007
 encoding encode-kvgpb
 filter xpath /platform-ios-xe-oper:components
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §24. BGP State ---
telemetry ietf subscription 60008
 encoding encode-kvgpb
 filter xpath /bgp-ios-xe-oper:bgp-state-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §25. OSPF State ---
telemetry ietf subscription 60009
 encoding encode-kvgpb
 filter xpath /ospf-ios-xe-oper:ospf-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §33. NTP Synchronization ---
telemetry ietf subscription 60010
 encoding encode-kvgpb
 filter xpath /ntp-ios-xe-oper:ntp-oper-data/ntp-status-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §34. BFD Sessions ---
telemetry ietf subscription 60011
 encoding encode-kvgpb
 filter xpath /bfd-ios-xe-oper:bfd-state/sessions
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §35. HSRP State ---
telemetry ietf subscription 60012
 encoding encode-kvgpb
 filter xpath /hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §36. VRRP State ---
telemetry ietf subscription 60013
 encoding encode-kvgpb
 filter xpath /vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §37. Flexible NetFlow / Flow Monitor ---
telemetry ietf subscription 60014
 encoding encode-kvgpb
 filter xpath /flow-monitor-ios-xe-oper:flow-monitors/flow-monitor
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §38. IP SLA Probes ---
telemetry ietf subscription 60015
 encoding encode-kvgpb
 filter xpath /ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §45. PoE Health (Detailed Port-Level) ---
telemetry ietf subscription 60029
 encoding encode-kvgpb
 filter xpath /poe-health-xe:poe-health-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §46. CEF / FIB State ---
telemetry ietf subscription 60016
 encoding encode-kvgpb
 filter xpath /fib-ios-xe-oper:fib-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §49. BGP Neighbor Detail ---
telemetry ietf subscription 60017
 encoding encode-kvgpb
 filter xpath /bgp-nbr-ios-xe-oper:bgp-nbr-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §53. IS-IS Interface Detail ---
telemetry ietf subscription 60018
 encoding encode-kvgpb
 filter xpath /isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §54. Multicast Routing State ---
telemetry ietf subscription 60019
 encoding encode-kvgpb
 filter xpath /mroute-ios-xe-oper:mroute-oper-data/mroute-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §55. Stack Member / Stackwise Virtual Detail ---
telemetry ietf subscription 60020
 encoding encode-kvgpb
 filter xpath /stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §56. Tunnel Interface State ---
telemetry ietf subscription 60021
 encoding encode-kvgpb
 filter xpath /ios-tunnel-oper:tunnel-oper-data/tunnel-if
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================

! --- §59. PIM Multicast State ---
telemetry ietf subscription 60022
 encoding encode-kvgpb
 filter xpath /pim-ios-xe-oper:pim-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §60. MPLS LDP Operational State ---
telemetry ietf subscription 60023
 encoding encode-kvgpb
 filter xpath /mpls-ldp-ios-xe-oper:mpls-ldp-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §62. LISP Operational State ---
telemetry ietf subscription 60024
 encoding encode-kvgpb
 filter xpath /lisp-ios-xe-oper:lisp-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §63. VXLAN NVE Tunnel Endpoints ---
telemetry ietf subscription 60025
 encoding encode-kvgpb
 filter xpath /nve-ios-xe-oper:nve-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §64. EVPN Operational State ---
telemetry ietf subscription 60026
 encoding encode-kvgpb
 filter xpath /evpn-ios-xe-oper:evpn-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp


! --- §67. IETF Interfaces Operational State ---
telemetry ietf subscription 60027
 encoding encode-kvgpb
 filter xpath /if:interfaces-state/interface
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §26. IETF Routing State ---
telemetry ietf subscription 60028
 encoding encode-kvgpb
 filter xpath /rt:routing-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! COOL TIER — 300-second polling (30000 centiseconds)
! Inventory, slow-changing state, security features
! ============================================================

! --- §10. VLANs ---
telemetry ietf subscription 50001
 encoding encode-kvgpb
 filter xpath /vlan-ios-xe-oper:vlans
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §11. MAC Address Table (MATM) ---
telemetry ietf subscription 50002
 encoding encode-kvgpb
 filter xpath /matm-ios-xe-oper:matm-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §12. ARP Table ---
telemetry ietf subscription 50003
 encoding encode-kvgpb
 filter xpath /arp-ios-xe-oper:arp-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §13. LLDP Neighbors ---
telemetry ietf subscription 50004
 encoding encode-kvgpb
 filter xpath /lldp-ios-xe-oper:lldp-entries
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §14. CDP Neighbors ---
telemetry ietf subscription 50005
 encoding encode-kvgpb
 filter xpath /cdp-ios-xe-oper:cdp-neighbor-details
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §16. Device Hardware (Uptime, SW Version) ---
telemetry ietf subscription 50006
 encoding encode-kvgpb
 filter xpath /device-hardware-xe-oper:device-hardware-data/device-hardware
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §17. Switchport ---
telemetry ietf subscription 50007
 encoding encode-kvgpb
 filter xpath /switchport-ios-xe-oper:switchport-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §18. Transceiver / Optics ---
telemetry ietf subscription 50008
 encoding encode-kvgpb
 filter xpath /xcvr-ios-xe-oper:transceiver-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §19. UDLD ---
telemetry ietf subscription 50009
 encoding encode-kvgpb
 filter xpath /udld-ios-xe-oper:udld-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §20. 802.1X / Identity Sessions ---
telemetry ietf subscription 50010
 encoding encode-kvgpb
 filter xpath /identity-ios-xe-oper:identity-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §21. TCAM Utilization ---
telemetry ietf subscription 50011
 encoding encode-kvgpb
 filter xpath /tcam-ios-xe-oper:tcam-details
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §22. MDT Subscription Health ---
telemetry ietf subscription 50012
 encoding encode-kvgpb
 filter xpath /mdt-oper-v2:mdt-oper-v2-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §23. Software Install ---
telemetry ietf subscription 50013
 encoding encode-kvgpb
 filter xpath /install-ios-xe-oper:install-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp


! --- §27. DHCP Pool Stats ---
telemetry ietf subscription 50014
 encoding encode-kvgpb
 filter xpath /dhcp-ios-xe-oper:dhcp-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §28. High Availability State ---
telemetry ietf subscription 50015
 encoding encode-kvgpb
 filter xpath /ha-ios-xe-oper:ha-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §29. Linecard Status ---
telemetry ietf subscription 50016
 encoding encode-kvgpb
 filter xpath /linecard-ios-xe-oper:linecard-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §30. TrustSec (SGT/SXP) ---
telemetry ietf subscription 50017
 encoding encode-kvgpb
 filter xpath /trustsec-ios-xe-oper:trustsec-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §31. LACP / Port-Channel ---
telemetry ietf subscription 50018
 encoding encode-kvgpb
 filter xpath /interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §32. ACL Hit Counters ---
telemetry ietf subscription 50019
 encoding encode-kvgpb
 filter xpath /acl-ios-xe-oper:access-lists/access-list
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §39. AAA / RADIUS / TACACS Statistics ---
telemetry ietf subscription 50020
 encoding encode-kvgpb
 filter xpath /aaa-ios-xe-oper:aaa-data/aaa-radius-stats
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §40. Port Security ---
telemetry ietf subscription 50021
 encoding encode-kvgpb
 filter xpath /psecure-ios-xe-oper:psecure-oper-data/psecure-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §41a. MACsec Encryption ---
telemetry ietf subscription 50022
 encoding encode-kvgpb
 filter xpath /macsec-ios-xe-oper:macsec-oper-data/macsec-statistics
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §41b. MKA Statistics ---
telemetry ietf subscription 50023
 encoding encode-kvgpb
 filter xpath /mka-ios-xe-oper:mka-oper-data/mka-statistics
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §42. VRF Operational State ---
telemetry ietf subscription 50024
 encoding encode-kvgpb
 filter xpath /vrf-ios-xe-oper:vrf-oper-data/vrf-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §43. Data Plane Resources (TCAM/EM per Feature) ---
telemetry ietf subscription 50025
 encoding encode-kvgpb
 filter xpath /dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §47. EIGRP Routing ---
telemetry ietf subscription 50026
 encoding encode-kvgpb
 filter xpath /eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §48. IS-IS Routing ---
telemetry ietf subscription 50027
 encoding encode-kvgpb
 filter xpath /isis-ios-xe-oper:isis-oper-data/isis-instance
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §50. BGP RIB Detail ---
telemetry ietf subscription 50028
 encoding encode-kvgpb
 filter xpath /bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §51. High-Scale ARP ---
telemetry ietf subscription 50029
 encoding encode-kvgpb
 filter xpath /ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §52. IPv6 Neighbor Discovery ---
telemetry ietf subscription 50030
 encoding encode-kvgpb
 filter xpath /ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §57. YANG Management Plane Interfaces ---
telemetry ietf subscription 50031
 encoding encode-kvgpb
 filter xpath /yang-interfaces-oper:yang-interfaces-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================
! --- §61. MPLS Forwarding (LFIB) ---
telemetry ietf subscription 50032
 encoding encode-kvgpb
 filter xpath /mpls-forwarding-ios-xe-oper:mpls-forwarding-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §65. PTP / SyncE Timing ---
telemetry ietf subscription 50033
 encoding encode-kvgpb
 filter xpath /ptp-synce-ios-xe-oper:ptp-synce-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! Verification Commands
! ============================================================
! show telemetry ietf subscription all
! show telemetry ietf subscription 30001 detail
! show telemetry ietf subscription 30001 receiver
! show telemetry internal connection
! show telemetry internal sensor subscription 30001
```

### Subscription Summary Table

| Sub ID | § | Feature | filter xpath | Interval |
|--------|---|---------|-------------|----------|
| 30001 | 1 | CPU Utilization | `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization` | 30s |
| 60001 | 2 | Memory Statistics | `/memory-ios-xe-oper:memory-statistics/memory-statistic` | 60s |
| 30002 | 3 | Process Memory | `/process-memory-ios-xe-oper:memory-usage-processes` | 30s |
| 60002 | 4 | System DRAM | `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes` | 60s |
| 60003 | 5 | Environment Sensors | `/environment-ios-xe-oper:environment-sensors` | 60s |
| 60004 | 6 | PoE | `/poe-ios-xe-oper:poe-oper-data` | 60s |
| 30003 | 7 | Interfaces | `/interfaces-ios-xe-oper:interfaces/interface` | 30s |
| 60005 | 8 | STP | `/stp-ios-xe-oper:stp-details` | 60s |
| 60006 | 9 | Stack | `/stack-ios-xe-oper:stack-oper-data` | 60s |
| 50001 | 10 | VLANs | `/vlan-ios-xe-oper:vlans` | 300s |
| 50002 | 11 | MATM | `/matm-ios-xe-oper:matm-oper-data` | 300s |
| 50003 | 12 | ARP | `/arp-ios-xe-oper:arp-data` | 300s |
| 50004 | 13 | LLDP | `/lldp-ios-xe-oper:lldp-entries` | 300s |
| 50005 | 14 | CDP | `/cdp-ios-xe-oper:cdp-neighbor-details` | 300s |
| 60007 | 15 | Platform Components | `/platform-ios-xe-oper:components` | 60s |
| 50006 | 16 | Device Hardware | `/device-hardware-xe-oper:device-hardware-data/device-hardware` | 300s |
| 50007 | 17 | Switchport | `/switchport-ios-xe-oper:switchport-oper-data` | 300s |
| 50008 | 18 | Transceiver | `/xcvr-ios-xe-oper:transceiver-oper-data` | 300s |
| 50009 | 19 | UDLD | `/udld-ios-xe-oper:udld-oper-data` | 300s |
| 50010 | 20 | Identity/802.1X | `/identity-ios-xe-oper:identity-oper-data` | 300s |
| 50011 | 21 | TCAM | `/tcam-ios-xe-oper:tcam-details` | 300s |
| 50012 | 22 | MDT Health | `/mdt-oper-v2:mdt-oper-v2-data` | 300s |
| 50013 | 23 | Software Install | `/install-ios-xe-oper:install-oper-data` | 300s |
| 60008 | 24 | BGP | `/bgp-ios-xe-oper:bgp-state-data` | 60s |
| 60009 | 25 | OSPF | `/ospf-ios-xe-oper:ospf-oper-data` | 60s |
| 60028 | 26 | IETF Routing State | `/rt:routing-state` | 60s |
| 50014 | 27 | DHCP | `/dhcp-ios-xe-oper:dhcp-oper-data` | 300s |
| 50015 | 28 | HA State | `/ha-ios-xe-oper:ha-oper-data` | 300s |
| 50016 | 29 | Linecard | `/linecard-ios-xe-oper:linecard-oper-data` | 300s |
| 50017 | 30 | TrustSec | `/trustsec-ios-xe-oper:trustsec-state` | 300s |
| 50018 | 31 | LACP/Port-Channel | `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state` | 300s |
| 50019 | 32 | ACL Counters | `/acl-ios-xe-oper:access-lists/access-list` | 300s |
| 60010 | 33 | NTP | `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info` | 60s |
| 60011 | 34 | BFD | `/bfd-ios-xe-oper:bfd-state/sessions` | 60s |
| 60012 | 35 | HSRP | `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info` | 60s |
| 60013 | 36 | VRRP | `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state` | 60s |
| 60014 | 37 | Flow Monitor | `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor` | 60s |
| 60015 | 38 | IP SLA | `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry` | 60s |
| 50020 | 39 | AAA/RADIUS | `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats` | 300s |
| 50021 | 40 | Port Security | `/psecure-ios-xe-oper:psecure-oper-data/psecure-state` | 300s |
| 50022 | 41a | MACsec | `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics` | 300s |
| 50023 | 41b | MKA | `/mka-ios-xe-oper:mka-oper-data/mka-statistics` | 300s |
| 50024 | 42 | VRF | `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry` | 300s |
| 50025 | 43 | DP Resources | `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource` | 300s |
| 30004 | 44 | Punt/Inject | `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats` | 30s |
| 60029 | 45 | PoE Health | `/poe-health-xe:poe-health-oper-data` | 60s |
| 60016 | 46 | CEF/FIB | `/fib-ios-xe-oper:fib-oper-data` | 60s |
| 50026 | 47 | EIGRP | `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance` | 300s |
| 50027 | 48 | IS-IS | `/isis-ios-xe-oper:isis-oper-data/isis-instance` | 300s |
| 60017 | 49 | BGP Neighbor Detail | `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data` | 60s |
| 50028 | 50 | BGP RIB Detail | `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route` | 300s |
| 50029 | 51 | High-Scale ARP | `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry` | 300s |
| 50030 | 52 | IPv6 Neighbor Discovery | `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry` | 300s |
| 60018 | 53 | IS-IS Interface Detail | `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type` | 60s |
| 60019 | 54 | Multicast Routing State | `/mroute-ios-xe-oper:mroute-oper-data/mroute-state` | 60s |
| 60020 | 55 | Stack Member / Stackwise Virtual Detail | `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info` | 60s |
| 60021 | 56 | Tunnel Interface State | `/ios-tunnel-oper:tunnel-oper-data/tunnel-if` | 60s |
| 50031 | 57 | YANG Management Plane Interfaces | `/yang-interfaces-oper:yang-interfaces-oper-data` | 300s |
| 60022 | 59 | PIM Multicast State | `/pim-ios-xe-oper:pim-oper-data` | 60s |
| 60023 | 60 | MPLS LDP Operational State | `/mpls-ldp-ios-xe-oper:mpls-ldp-oper-data` | 60s |
| 50032 | 61 | MPLS Forwarding (LFIB) | `/mpls-forwarding-ios-xe-oper:mpls-forwarding-oper-data` | 300s |
| 60024 | 62 | LISP Operational State | `/lisp-ios-xe-oper:lisp-state` | 60s |
| 60025 | 63 | VXLAN NVE Tunnel Endpoints | `/nve-ios-xe-oper:nve-oper-data` | 60s |
| 60026 | 64 | EVPN Operational State | `/evpn-ios-xe-oper:evpn-oper-data` | 60s |
| 50033 | 65 | PTP / SyncE Timing | `/ptp-synce-ios-xe-oper:ptp-synce-oper-data` | 300s |
| 60027 | 67 | IETF Interfaces Operational State | `/if:interfaces-state/interface` | 60s |

---



## Recommended Polling Intervals

| Tier | Interval | Feature Areas |
|------|----------|---------------|
| Hot (real-time) | 30s (3000 cs) | CPU, interfaces (rx/tx kbps), process memory, punt/inject counters |
| Warm (near-real-time) | 60s (6000 cs) | Environment sensors, platform components, BGP, BGP neighbor detail, OSPF, STP, stack, stack-member detail, PoE, BFD, HSRP/VRRP, IP SLA, NTP, CEF/FIB, IS-IS interface detail, multicast routing, tunnel state, flow monitor, PIM, MPLS LDP, LISP, VXLAN NVE, EVPN, IETF routing, IETF interfaces, PoE health |
| Cool (inventory/slow-change) | 300s (30000 cs) | VLANs, MAC table, ARP, high-scale ARP, IPv6 ND, LLDP, CDP, switchport, transceiver, TCAM, DHCP, device-hardware, install, MDT health, HA, linecard, TrustSec, identity, UDLD, ACL counters, AAA/RADIUS, port security, MACsec/MKA, VRF, DP resources, EIGRP, IS-IS, BGP RIB detail, YANG management-plane interfaces, MPLS forwarding (LFIB), PTP/SyncE |

Recommendation: 60s for environment/interfaces/cpu/platform and 15min for device-hardware.

---

## IOS XE Subscription Configuration (filter xpath)

Complete gRPC dial-out subscription config for all 65 target features and 66 subscriptions. Subscription IDs use a tier-based scheme: 30xxx (HOT), 60xxx (WARM), 50xxx (COOL). Receiver IP and port are placeholders — update to match your OTel collector.

Variables to customize before applying:
- `RECEIVER_IP` — OTel collector IP address (e.g., 10.1.1.3)
- `RECEIVER_PORT` — gRPC listen port (e.g., 57500)

```
! ============================================================
! Prerequisite: gRPC Dial-Out Receiver Profile
! ============================================================
telemetry receiver protocol otel-collector
 host ip-address RECEIVER_IP RECEIVER_PORT
 protocol grpc-tcp

! ============================================================
! HOT TIER — 30-second polling (3000 centiseconds)
! CPU, Interfaces, Process Memory, Punt/Inject
! ============================================================

! --- §1. CPU Utilization ---
telemetry ietf subscription 30001
 encoding encode-kvgpb
 filter xpath /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §3. Process Memory ---
telemetry ietf subscription 30002
 encoding encode-kvgpb
 filter xpath /process-memory-ios-xe-oper:memory-usage-processes
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §7. Interface Statistics ---
telemetry ietf subscription 30003
 encoding encode-kvgpb
 filter xpath /interfaces-ios-xe-oper:interfaces/interface
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §44. CPU Punt/Inject Counters ---
telemetry ietf subscription 30004
 encoding encode-kvgpb
 filter xpath /switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================
! WARM TIER — 60-second polling (6000 centiseconds)
! Environment, Platform, Routing, STP, Stack, PoE, FHRP, etc.
! ============================================================

! --- §2. Memory Statistics ---
telemetry ietf subscription 60001
 encoding encode-kvgpb
 filter xpath /memory-ios-xe-oper:memory-statistics/memory-statistic
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §4. System DRAM (Platform Software) ---
telemetry ietf subscription 60002
 encoding encode-kvgpb
 filter xpath /platform-sw-ios-xe-oper:cisco-platform-software/control-processes
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §5. Environment Sensors ---
telemetry ietf subscription 60003
 encoding encode-kvgpb
 filter xpath /environment-ios-xe-oper:environment-sensors
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §6. PoE Operational Data ---
telemetry ietf subscription 60004
 encoding encode-kvgpb
 filter xpath /poe-ios-xe-oper:poe-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §8. Spanning Tree ---
telemetry ietf subscription 60005
 encoding encode-kvgpb
 filter xpath /stp-ios-xe-oper:stp-details
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §9. Stack Health ---
telemetry ietf subscription 60006
 encoding encode-kvgpb
 filter xpath /stack-ios-xe-oper:stack-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §15. Platform Components ---
telemetry ietf subscription 60007
 encoding encode-kvgpb
 filter xpath /platform-ios-xe-oper:components
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §24. BGP State ---
telemetry ietf subscription 60008
 encoding encode-kvgpb
 filter xpath /bgp-ios-xe-oper:bgp-state-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §25. OSPF State ---
telemetry ietf subscription 60009
 encoding encode-kvgpb
 filter xpath /ospf-ios-xe-oper:ospf-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §33. NTP Synchronization ---
telemetry ietf subscription 60010
 encoding encode-kvgpb
 filter xpath /ntp-ios-xe-oper:ntp-oper-data/ntp-status-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §34. BFD Sessions ---
telemetry ietf subscription 60011
 encoding encode-kvgpb
 filter xpath /bfd-ios-xe-oper:bfd-state/sessions
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §35. HSRP State ---
telemetry ietf subscription 60012
 encoding encode-kvgpb
 filter xpath /hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §36. VRRP State ---
telemetry ietf subscription 60013
 encoding encode-kvgpb
 filter xpath /vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §37. Flexible NetFlow / Flow Monitor ---
telemetry ietf subscription 60014
 encoding encode-kvgpb
 filter xpath /flow-monitor-ios-xe-oper:flow-monitors/flow-monitor
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §38. IP SLA Probes ---
telemetry ietf subscription 60015
 encoding encode-kvgpb
 filter xpath /ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §45. PoE Health (Detailed Port-Level) ---
telemetry ietf subscription 60029
 encoding encode-kvgpb
 filter xpath /poe-health-xe:poe-health-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §46. CEF / FIB State ---
telemetry ietf subscription 60016
 encoding encode-kvgpb
 filter xpath /fib-ios-xe-oper:fib-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §49. BGP Neighbor Detail ---
telemetry ietf subscription 60017
 encoding encode-kvgpb
 filter xpath /bgp-nbr-ios-xe-oper:bgp-nbr-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §53. IS-IS Interface Detail ---
telemetry ietf subscription 60018
 encoding encode-kvgpb
 filter xpath /isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §54. Multicast Routing State ---
telemetry ietf subscription 60019
 encoding encode-kvgpb
 filter xpath /mroute-ios-xe-oper:mroute-oper-data/mroute-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §55. Stack Member / Stackwise Virtual Detail ---
telemetry ietf subscription 60020
 encoding encode-kvgpb
 filter xpath /stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §56. Tunnel Interface State ---
telemetry ietf subscription 60021
 encoding encode-kvgpb
 filter xpath /ios-tunnel-oper:tunnel-oper-data/tunnel-if
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================

! --- §59. PIM Multicast State ---
telemetry ietf subscription 60022
 encoding encode-kvgpb
 filter xpath /pim-ios-xe-oper:pim-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §60. MPLS LDP Operational State ---
telemetry ietf subscription 60023
 encoding encode-kvgpb
 filter xpath /mpls-ldp-ios-xe-oper:mpls-ldp-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §62. LISP Operational State ---
telemetry ietf subscription 60024
 encoding encode-kvgpb
 filter xpath /lisp-ios-xe-oper:lisp-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §63. VXLAN NVE Tunnel Endpoints ---
telemetry ietf subscription 60025
 encoding encode-kvgpb
 filter xpath /nve-ios-xe-oper:nve-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §64. EVPN Operational State ---
telemetry ietf subscription 60026
 encoding encode-kvgpb
 filter xpath /evpn-ios-xe-oper:evpn-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp


! --- §67. IETF Interfaces Operational State ---
telemetry ietf subscription 60027
 encoding encode-kvgpb
 filter xpath /if:interfaces-state/interface
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §26. IETF Routing State ---
telemetry ietf subscription 60028
 encoding encode-kvgpb
 filter xpath /rt:routing-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! COOL TIER — 300-second polling (30000 centiseconds)
! Inventory, slow-changing state, security features
! ============================================================

! --- §10. VLANs ---
telemetry ietf subscription 50001
 encoding encode-kvgpb
 filter xpath /vlan-ios-xe-oper:vlans
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §11. MAC Address Table (MATM) ---
telemetry ietf subscription 50002
 encoding encode-kvgpb
 filter xpath /matm-ios-xe-oper:matm-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §12. ARP Table ---
telemetry ietf subscription 50003
 encoding encode-kvgpb
 filter xpath /arp-ios-xe-oper:arp-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §13. LLDP Neighbors ---
telemetry ietf subscription 50004
 encoding encode-kvgpb
 filter xpath /lldp-ios-xe-oper:lldp-entries
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §14. CDP Neighbors ---
telemetry ietf subscription 50005
 encoding encode-kvgpb
 filter xpath /cdp-ios-xe-oper:cdp-neighbor-details
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §16. Device Hardware (Uptime, SW Version) ---
telemetry ietf subscription 50006
 encoding encode-kvgpb
 filter xpath /device-hardware-xe-oper:device-hardware-data/device-hardware
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §17. Switchport ---
telemetry ietf subscription 50007
 encoding encode-kvgpb
 filter xpath /switchport-ios-xe-oper:switchport-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §18. Transceiver / Optics ---
telemetry ietf subscription 50008
 encoding encode-kvgpb
 filter xpath /xcvr-ios-xe-oper:transceiver-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §19. UDLD ---
telemetry ietf subscription 50009
 encoding encode-kvgpb
 filter xpath /udld-ios-xe-oper:udld-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §20. 802.1X / Identity Sessions ---
telemetry ietf subscription 50010
 encoding encode-kvgpb
 filter xpath /identity-ios-xe-oper:identity-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §21. TCAM Utilization ---
telemetry ietf subscription 50011
 encoding encode-kvgpb
 filter xpath /tcam-ios-xe-oper:tcam-details
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §22. MDT Subscription Health ---
telemetry ietf subscription 50012
 encoding encode-kvgpb
 filter xpath /mdt-oper-v2:mdt-oper-v2-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §23. Software Install ---
telemetry ietf subscription 50013
 encoding encode-kvgpb
 filter xpath /install-ios-xe-oper:install-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp


! --- §27. DHCP Pool Stats ---
telemetry ietf subscription 50014
 encoding encode-kvgpb
 filter xpath /dhcp-ios-xe-oper:dhcp-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §28. High Availability State ---
telemetry ietf subscription 50015
 encoding encode-kvgpb
 filter xpath /ha-ios-xe-oper:ha-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §29. Linecard Status ---
telemetry ietf subscription 50016
 encoding encode-kvgpb
 filter xpath /linecard-ios-xe-oper:linecard-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §30. TrustSec (SGT/SXP) ---
telemetry ietf subscription 50017
 encoding encode-kvgpb
 filter xpath /trustsec-ios-xe-oper:trustsec-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §31. LACP / Port-Channel ---
telemetry ietf subscription 50018
 encoding encode-kvgpb
 filter xpath /interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §32. ACL Hit Counters ---
telemetry ietf subscription 50019
 encoding encode-kvgpb
 filter xpath /acl-ios-xe-oper:access-lists/access-list
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §39. AAA / RADIUS / TACACS Statistics ---
telemetry ietf subscription 50020
 encoding encode-kvgpb
 filter xpath /aaa-ios-xe-oper:aaa-data/aaa-radius-stats
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §40. Port Security ---
telemetry ietf subscription 50021
 encoding encode-kvgpb
 filter xpath /psecure-ios-xe-oper:psecure-oper-data/psecure-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §41a. MACsec Encryption ---
telemetry ietf subscription 50022
 encoding encode-kvgpb
 filter xpath /macsec-ios-xe-oper:macsec-oper-data/macsec-statistics
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §41b. MKA Statistics ---
telemetry ietf subscription 50023
 encoding encode-kvgpb
 filter xpath /mka-ios-xe-oper:mka-oper-data/mka-statistics
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §42. VRF Operational State ---
telemetry ietf subscription 50024
 encoding encode-kvgpb
 filter xpath /vrf-ios-xe-oper:vrf-oper-data/vrf-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §43. Data Plane Resources (TCAM/EM per Feature) ---
telemetry ietf subscription 50025
 encoding encode-kvgpb
 filter xpath /dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §47. EIGRP Routing ---
telemetry ietf subscription 50026
 encoding encode-kvgpb
 filter xpath /eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §48. IS-IS Routing ---
telemetry ietf subscription 50027
 encoding encode-kvgpb
 filter xpath /isis-ios-xe-oper:isis-oper-data/isis-instance
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §50. BGP RIB Detail ---
telemetry ietf subscription 50028
 encoding encode-kvgpb
 filter xpath /bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §51. High-Scale ARP ---
telemetry ietf subscription 50029
 encoding encode-kvgpb
 filter xpath /ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §52. IPv6 Neighbor Discovery ---
telemetry ietf subscription 50030
 encoding encode-kvgpb
 filter xpath /ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §57. YANG Management Plane Interfaces ---
telemetry ietf subscription 50031
 encoding encode-kvgpb
 filter xpath /yang-interfaces-oper:yang-interfaces-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================
! --- §61. MPLS Forwarding (LFIB) ---
telemetry ietf subscription 50032
 encoding encode-kvgpb
 filter xpath /mpls-forwarding-ios-xe-oper:mpls-forwarding-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §65. PTP / SyncE Timing ---
telemetry ietf subscription 50033
 encoding encode-kvgpb
 filter xpath /ptp-synce-ios-xe-oper:ptp-synce-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! Verification Commands
! ============================================================
! show telemetry ietf subscription all
! show telemetry ietf subscription 30001 detail
! show telemetry ietf subscription 30001 receiver
! show telemetry internal connection
! show telemetry internal sensor subscription 30001
```

### Subscription Summary Table

| Sub ID | § | Feature | filter xpath | Interval |
|--------|---|---------|-------------|----------|
| 30001 | 1 | CPU Utilization | `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization` | 30s |
| 60001 | 2 | Memory Statistics | `/memory-ios-xe-oper:memory-statistics/memory-statistic` | 60s |
| 30002 | 3 | Process Memory | `/process-memory-ios-xe-oper:memory-usage-processes` | 30s |
| 60002 | 4 | System DRAM | `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes` | 60s |
| 60003 | 5 | Environment Sensors | `/environment-ios-xe-oper:environment-sensors` | 60s |
| 60004 | 6 | PoE | `/poe-ios-xe-oper:poe-oper-data` | 60s |
| 30003 | 7 | Interfaces | `/interfaces-ios-xe-oper:interfaces/interface` | 30s |
| 60005 | 8 | STP | `/stp-ios-xe-oper:stp-details` | 60s |
| 60006 | 9 | Stack | `/stack-ios-xe-oper:stack-oper-data` | 60s |
| 50001 | 10 | VLANs | `/vlan-ios-xe-oper:vlans` | 300s |
| 50002 | 11 | MATM | `/matm-ios-xe-oper:matm-oper-data` | 300s |
| 50003 | 12 | ARP | `/arp-ios-xe-oper:arp-data` | 300s |
| 50004 | 13 | LLDP | `/lldp-ios-xe-oper:lldp-entries` | 300s |
| 50005 | 14 | CDP | `/cdp-ios-xe-oper:cdp-neighbor-details` | 300s |
| 60007 | 15 | Platform Components | `/platform-ios-xe-oper:components` | 60s |
| 50006 | 16 | Device Hardware | `/device-hardware-xe-oper:device-hardware-data/device-hardware` | 300s |
| 50007 | 17 | Switchport | `/switchport-ios-xe-oper:switchport-oper-data` | 300s |
| 50008 | 18 | Transceiver | `/xcvr-ios-xe-oper:transceiver-oper-data` | 300s |
| 50009 | 19 | UDLD | `/udld-ios-xe-oper:udld-oper-data` | 300s |
| 50010 | 20 | Identity/802.1X | `/identity-ios-xe-oper:identity-oper-data` | 300s |
| 50011 | 21 | TCAM | `/tcam-ios-xe-oper:tcam-details` | 300s |
| 50012 | 22 | MDT Health | `/mdt-oper-v2:mdt-oper-v2-data` | 300s |
| 50013 | 23 | Software Install | `/install-ios-xe-oper:install-oper-data` | 300s |
| 60008 | 24 | BGP | `/bgp-ios-xe-oper:bgp-state-data` | 60s |
| 60009 | 25 | OSPF | `/ospf-ios-xe-oper:ospf-oper-data` | 60s |
| 60028 | 26 | IETF Routing State | `/rt:routing-state` | 60s |
| 50014 | 27 | DHCP | `/dhcp-ios-xe-oper:dhcp-oper-data` | 300s |
| 50015 | 28 | HA State | `/ha-ios-xe-oper:ha-oper-data` | 300s |
| 50016 | 29 | Linecard | `/linecard-ios-xe-oper:linecard-oper-data` | 300s |
| 50017 | 30 | TrustSec | `/trustsec-ios-xe-oper:trustsec-state` | 300s |
| 50018 | 31 | LACP/Port-Channel | `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state` | 300s |
| 50019 | 32 | ACL Counters | `/acl-ios-xe-oper:access-lists/access-list` | 300s |
| 60010 | 33 | NTP | `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info` | 60s |
| 60011 | 34 | BFD | `/bfd-ios-xe-oper:bfd-state/sessions` | 60s |
| 60012 | 35 | HSRP | `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info` | 60s |
| 60013 | 36 | VRRP | `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state` | 60s |
| 60014 | 37 | Flow Monitor | `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor` | 60s |
| 60015 | 38 | IP SLA | `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry` | 60s |
| 50020 | 39 | AAA/RADIUS | `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats` | 300s |
| 50021 | 40 | Port Security | `/psecure-ios-xe-oper:psecure-oper-data/psecure-state` | 300s |
| 50022 | 41a | MACsec | `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics` | 300s |
| 50023 | 41b | MKA | `/mka-ios-xe-oper:mka-oper-data/mka-statistics` | 300s |
| 50024 | 42 | VRF | `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry` | 300s |
| 50025 | 43 | DP Resources | `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource` | 300s |
| 30004 | 44 | Punt/Inject | `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats` | 30s |
| 60029 | 45 | PoE Health | `/poe-health-xe:poe-health-oper-data` | 60s |
| 60016 | 46 | CEF/FIB | `/fib-ios-xe-oper:fib-oper-data` | 60s |
| 50026 | 47 | EIGRP | `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance` | 300s |
| 50027 | 48 | IS-IS | `/isis-ios-xe-oper:isis-oper-data/isis-instance` | 300s |
| 60017 | 49 | BGP Neighbor Detail | `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data` | 60s |
| 50028 | 50 | BGP RIB Detail | `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route` | 300s |
| 50029 | 51 | High-Scale ARP | `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry` | 300s |
| 50030 | 52 | IPv6 Neighbor Discovery | `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry` | 300s |
| 60018 | 53 | IS-IS Interface Detail | `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type` | 60s |
| 60019 | 54 | Multicast Routing State | `/mroute-ios-xe-oper:mroute-oper-data/mroute-state` | 60s |
| 60020 | 55 | Stack Member / Stackwise Virtual Detail | `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info` | 60s |
| 60021 | 56 | Tunnel Interface State | `/ios-tunnel-oper:tunnel-oper-data/tunnel-if` | 60s |
| 50031 | 57 | YANG Management Plane Interfaces | `/yang-interfaces-oper:yang-interfaces-oper-data` | 300s |
| 60022 | 59 | PIM Multicast State | `/pim-ios-xe-oper:pim-oper-data` | 60s |
| 60023 | 60 | MPLS LDP Operational State | `/mpls-ldp-ios-xe-oper:mpls-ldp-oper-data` | 60s |
| 50032 | 61 | MPLS Forwarding (LFIB) | `/mpls-forwarding-ios-xe-oper:mpls-forwarding-oper-data` | 300s |
| 60024 | 62 | LISP Operational State | `/lisp-ios-xe-oper:lisp-state` | 60s |
| 60025 | 63 | VXLAN NVE Tunnel Endpoints | `/nve-ios-xe-oper:nve-oper-data` | 60s |
| 60026 | 64 | EVPN Operational State | `/evpn-ios-xe-oper:evpn-oper-data` | 60s |
| 50033 | 65 | PTP / SyncE Timing | `/ptp-synce-ios-xe-oper:ptp-synce-oper-data` | 300s |
| 60027 | 67 | IETF Interfaces Operational State | `/if:interfaces-state/interface` | 60s |

---

## Known Platform Limitations (IOS XE MDT)

The following XPath categories have been tested and confirmed **permanently invalid** on Catalyst 9300/C9300X via the yang-push stream on IOS XE 26.01.1. They may work via NETCONF/RESTCONF but cannot be subscribed via MDT dial-out.

### QoS / DiffServ Statistics

All DiffServ/QoS variants return `Invalid XPath filter`:

| XPath attempted | Result |
|----------------|--------|
| `/diffserv-ios-xe-oper:diffserv-interfaces` | INVALID |
| `/diffserv-target-ios-xe-oper:diffserv-target-entries` | INVALID |
| `/qos-ios-xe-oper:qos-oper-data` | INVALID |
| `/policy-ios-xe-oper:policy-oper-data` | INVALID |

> **Note:** QoS per-class statistics ARE collected as nested `diffserv-info` within the interface statistics subscription (sub 30003, §7). Use SNMP (CISCO-CLASS-BASED-QOS-MIB) or NETCONF/RESTCONF as alternatives for dedicated QoS counters.

### IETF Module Prefix Aliases

IOS XE MDT (yang-push stream) requires the **short prefix alias** defined in the YANG module's `prefix` statement, **not** the full module name:

| Fails (module name) | Works (prefix alias) | Module |
|---------------------|---------------------|--------|
| `/ietf-interfaces:interfaces-state` | `/if:interfaces-state/interface` | ietf-interfaces |
| `/ietf-routing:routing-state` | `/rt:routing-state` | ietf-routing |

The IETF modules ARE loaded on the switch (confirmed via `show netconf-yang status`) but the yang-push publisher resolves only the canonical prefix defined in the module header (`prefix if;`, `prefix rt;`).

### Silent Subscriptions (Feature Not Configured)

The following 10 subscriptions are valid XPaths but return no data unless the corresponding feature is configured on the switch:

| Sub | Feature | Activation Required |
|-----|---------|-------------------|
| 50008 | Transceivers | SFP/SFP+ modules installed |
| 50009 | UDLD | `udld enable` on interfaces |
| 50016 | Linecard | Modular chassis (C9400/C9600) |
| 50018 | LACP | Port-channel with LACP configured |
| 60023 | MPLS LDP | `mpls ldp` routing config |
| 50032 | MPLS Forwarding | MPLS label switching enabled |
| 60024 | LISP | LISP site/EID config |
| 60025 | VXLAN NVE | NVE interface + VNI config |
| 60026 | EVPN | EVPN instance config |
| 50033 | PTP/SyncE | PTP boundary/transparent clock |

## On-Change Capable Features

These features support on-change telemetry via mdt-capabilities-oper (periodic-only decision stands, but documented for future):

`/platform-ios-xe-oper:components`, `/poe-ios-xe-oper:poe-oper-data`, `/stacking-ios-xe-oper:stacking-oper-data`, `/vlan-ios-xe-oper:vlans`, `/xcvr-ios-xe-oper:transceiver-oper-data`, `/trustsec-ios-xe-oper:trustsec-state`, `/ha-ios-xe-oper:ha-oper-data`, `/linecard-ios-xe-oper:linecard-oper-data`, `/cdp-ios-xe-oper:cdp-neighbor-details`, `/interfaces-ios-xe-oper:interfaces/interface`, `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state`

---

## Reference Links

- **MDT White Paper:** http://cs.co/mdtwp
- **Grafana Device Health Dashboard 13462:** https://grafana.com/grafana/dashboards/13462
- **Grafana PoE Dashboard 17238:** https://grafana.com/grafana/dashboards/17238-catalyst-poe-dashboard/
- **MDT GitHub (TIG):** https://github.com/jeremycohoe/cisco-ios-xe-mdt
- **MDT PoE GitHub:** https://github.com/jeremycohoe/cisco-mdt-poe
- **OTEL Receiver GitHub:** https://github.com/jeremycohoe/otel-grpc-cisco-receiver
- **IOS XE DevNet:** https://developer.cisco.com/iosxe/
- **YANG Models on GitHub:** https://github.com/YangModels/yang/tree/main/vendor/cisco/xe
- **SNMP OID to YANG XPath Mapping CSV:** https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17181/iosxe-snmp-OID-xpath-mapping.csv
- **IOS XE OpenAPI Swagger:** https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/
- **dCloud Lab:** https://dcloud2.cisco.com/demo/catalyst-9000-ios-xe-programmability-automation-lab-v1
- **MDT Config Guide:** https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/model-driven-telemetry.html

---

---

## Part V: Domain Requirements

### 1. System Health

This domain should show whether the device control plane is healthy and whether memory pressure is visible before users see service impact.

Feature expectations:

- §1 CPU should provide current and trend visibility
- §2 Memory should provide used versus free visibility by pool
- §3 Process Memory should provide top consumers for troubleshooting
- §4 DRAM should provide platform-level memory health distinct from process pools

Required panel styles:

- gauges for current state
- time charts for CPU and memory trends
- top-N charts for process memory
- summary tables for process or pool breakdown

### 2. Environment and Power

This domain should show environmental health, PoE allocation, and PoE fault conditions.

Feature expectations:

- §5 must separate temperature, fan, and power supply views
- §6 should show per-port PoE consumption and allocation state
- §45 should show detailed PoE hardware faults and port event history

Required panel styles:

- status tables for PSU and fan state
- time charts for temperature and PoE power trends
- per-port bar charts for PoE load
- detail table for PoE health counters

### 3. Interfaces

This domain should show interface traffic, errors, switching mode, optical health, and aggregation status.

Feature expectations:

- §7 is the primary operational interface dashboard and should receive the deepest coverage
- §17 should show switchport mode and VLAN assignment
- §18 should show optics telemetry and module health
- §19 should show UDLD adjacency state
- §31 should show port-channel and member status

Required panel styles:

- traffic trend charts
- error and discard tables
- status grids
- optics health tables
- port-channel member tables

### 4. L2 Topology

This domain should show forwarding adjacency and discovery context for layer-2 operations.

Feature expectations:

- §8 should show STP state and topology-change indicators
- §10 should show VLAN inventory and membership
- §11 and §12 should expose MAC and ARP lookup context
- §13 and §14 should expose neighbor discovery context

Required panel styles:

- status grids for STP state
- inventory tables for VLAN, MAC, and ARP
- neighbor discovery tables
- count panels for entries and neighbors

### 5. L3 Routing

This domain should show routing adjacencies, route inventory, VRF separation, and forwarding-state health.

Feature expectations:

- §24 and §25 should emphasize neighbor session health
- §26 should show route inventory and source protocol breakdown
- §42 should show VRF membership and structure
- §46 should show forwarding readiness and punt or drop behavior
- §47 and §48 should be included when those protocols exist on the device

Required panel styles:

- neighbor state tables
- route browser tables
- protocol distribution charts
- status indicators for forwarding readiness
- trend charts for punt and drop counters

### 6. Security and Identity

This domain should show who is connected, how policy is applied, and whether encrypted or controlled access features are healthy.

Feature expectations:

- §20 should show active identity sessions and authorization context
- §30 should show TrustSec mappings and SXP state
- §32 should show ACL hit activity
- §39 should show AAA server outcomes
- §40 should show secured-port inventory
- §41 should show MACsec and MKA operational counters

Required panel styles:

- identity session tables
- state tables
- hit-rate trends
- auth result trends
- encryption counters and error indicators

### 7. Network Services

This domain should show foundational service health and control-plane service visibility.

Feature expectations:

- §27 should show DHCP utilization
- §33 should show time synchronization quality
- §34 should show BFD adjacency state
- §35 and §36 should show first-hop redundancy state
- §37 should show flow export and monitor activity
- §38 should show synthetic probe performance and failures

Required panel styles:

- utilization charts
- state tables
- trend charts for jitter, RTT, and counters
- compact summary cards for high-level service health

### 8. Platform and Resources

This domain should show chassis, stack, hardware inventory, forwarding resources, and platform stress signals.

Feature expectations:

- §9 should show stack member and stack-port state
- §15 and §16 should show hardware inventory and software version identity
- §21 and §43 should show resource utilization and capacity pressure
- §28 and §29 should show HA and linecard state where applicable
- §44 should show punt and inject pressure on CPU queues

Required panel styles:

- hardware and stack inventory tables
- status grids for member state
- utilization gauges and bar charts for TCAM and data-plane resources
- trend charts for punt or drop pressure

### 9. Operations

This domain should show whether telemetry itself is healthy and whether software inventory is in the expected state.

Feature expectations:

- §22 should clearly show subscription validity, connection state, and update counts
- §23 should show installed packages and state

Required panel styles:

- status tables
- telemetry health summary cards
- inventory tables for package state

---

## Part VI: Lab Topology and Activation Runbook

## Lab Topology Assumptions For This Project

The working lab topology for Version 3 is:

| Role | Device | Address | Notes |
|---|---|---|---|
| Primary switch | C9300-1 | 10.1.1.5 | Main telemetry source and default place to start validation. |
| Secondary switch | C9300-2 | 10.1.1.55 | Peer for adjacency-dependent features. |
| Ubuntu server | Ubuntu | 10.1.1.3 | Shared services host for NTP, RADIUS, flow collection, IP SLA targets, and traffic generation. |
| Inter-switch link | Gi1/0/47 on both switches | n/a | Single physical link; use it as an 802.1Q trunk, not as a port-channel member. |
| Ubuntu uplink | Gi1/0/48 on both switches | n/a | Access port on VLAN 10; connects each switch directly to the Ubuntu server. |

The rest of this guide assumes:

- `Gi1/0/47` on both switches is configured as the inter-switch trunk
- `Gi1/0/48` on both switches is configured as the Ubuntu uplink (access VLAN 10)

## What This Topology Can And Cannot Demonstrate

The current topology is good enough for many peer-based features, but not all of them.

| Feature Class | Status In Current Lab | Reason |
|---|---|---|
| BGP, OSPF, EIGRP, IS-IS, BFD | Fully demonstrable | Two switches can form real adjacencies over a transit VLAN. |
| HSRP, VRRP | Fully demonstrable | Two switches can share a VLAN and form first-hop redundancy groups. |
| GRE tunnel telemetry | Fully demonstrable | Two loopbacks over the routed transit path are enough. |
| MACsec | Conditionally demonstrable | Depends on platform support, licenses, and using the inter-switch link as the MACsec-secured link. |
| ACL counters, Flow Monitor, IP SLA, ARP, IPv6 ND | Fully demonstrable | Ubuntu can act as target, responder, collector, or traffic source. |
| DHCP | Partially demonstrable | Best exercised with an Ubuntu DHCP client namespace or a second endpoint. |
| 802.1X / AAA | Partially demonstrable | Ubuntu can host FreeRADIUS, but a separate supplicant endpoint is preferred for realistic auth session telemetry. |
| TrustSec | Not realistically complete | A useful demo usually needs ISE or at least a more deliberate CTS design. |
| LACP / Port-Channel | Not demonstrable with current wiring | A single inter-switch physical link cannot produce a meaningful LACP bundle. |
| Stack, Stack Member, HA, Linecard | Hardware-conditional | These require actual stack or HA conditions, not just two standalone switches. |
| PoE / PoE Health | Endpoint-conditional | Requires powered devices on PoE-capable ports. |

## Recommended Lab VLAN And Address Plan

To activate the largest number of features with the current topology, use the inter-switch link as a trunk and split functions by VLAN.

| VLAN | Purpose | C9300-1 | C9300-2 | Ubuntu |
|---|---|---|---|---|
| 10 | Shared services / user VLAN | 10.1.1.5/24 | 10.1.1.55/24 | 10.1.1.3/24 |
| 20 | VRRP demo VLAN | 10.1.20.2/24 | 10.1.20.3/24 | not required |
| 30 | DHCP demo VLAN | 10.1.30.1/24 | optional | optional namespace client |
| 47 | Routed transit VLAN between switches | 10.47.0.1/30 | 10.47.0.2/30 | not required |

Use these loopbacks for routing and tunnel features:

- C9300-1 Loopback0: `10.255.0.1/32`
- C9300-2 Loopback0: `10.255.0.2/32`

## Recommended Per-Device Configuration Model

### Shared switch base on both C9300s

```ios
service timestamps debug datetime msec
service timestamps log datetime msec
ip routing
ipv6 unicast-routing
lldp run
cdp run
udld enable
ip multicast-routing distributed
restconf
netconf-yang

vlan 10
 name LAB-SERVICES
vlan 20
 name LAB-VRRP
vlan 30
 name LAB-DHCP
vlan 47
 name LAB-TRANSIT

interface GigabitEthernet1/0/47
 description INTER-SWITCH-TRUNK
 switchport
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,47
 udld port aggressive
 no shutdown

interface GigabitEthernet1/0/48
 description UBUNTU-UPLINK
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown

interface Vlan47
 description ROUTING-TRANSIT
 ip ospf network point-to-point
 ip pim sparse-mode
 ipv6 enable
 isis network point-to-point
 no shutdown
```

### C9300-1 specific config

```ios
hostname C9300-1

interface Vlan10
 description SERVICES-VLAN
 ip address 10.1.1.5 255.255.255.0
 standby version 2
 standby 10 ip 10.1.1.1
 standby 10 priority 110
 standby 10 preempt
 ip pim sparse-mode
 ipv6 address 2001:db8:10::5/64
 no shutdown

interface Vlan20
 description VRRP-DEMO
 ip address 10.1.20.2 255.255.255.0
 vrrp 20 ip 10.1.20.1
 vrrp 20 priority 110
 vrrp 20 preempt
 no shutdown

interface Vlan30
 description DHCP-DEMO
 ip address 10.1.30.1 255.255.255.0
 no shutdown

interface Vlan47
 ip address 10.47.0.1 255.255.255.252
 bfd interval 150 min_rx 150 multiplier 3
 ip router isis LAB
 ip ospf 100 area 0
 ipv6 address 2001:db8:47::1/64

interface Loopback0
 ip address 10.255.0.1 255.255.255.255
 ip router isis LAB
 ip ospf 100 area 0

router ospf 100
 router-id 10.255.0.1
 passive-interface default
 no passive-interface Vlan47

router eigrp LAB
 address-family ipv4 unicast autonomous-system 100
  af-interface Vlan47
   bfd
  exit-af-interface
  network 10.47.0.0 0.0.0.3
  network 10.255.0.1 0.0.0.0
 exit-address-family

router isis LAB
 net 49.0001.0000.0000.0001.00
 is-type level-2-only

router bgp 65001
 bgp log-neighbor-changes
 neighbor 10.47.0.2 remote-as 65002
 neighbor 10.47.0.2 fall-over bfd
 address-family ipv4 unicast
  network 10.255.0.1 mask 255.255.255.255
  neighbor 10.47.0.2 activate
 exit-address-family

ip dhcp excluded-address 10.1.30.1 10.1.30.20
ip dhcp pool LAB-CLIENTS
 network 10.1.30.0 255.255.255.0
 default-router 10.1.30.1
 dns-server 10.1.1.3

ip access-list extended LAB-COUNT
 permit icmp host 10.1.1.3 any
 permit tcp host 10.1.1.3 any eq 22
 permit ip any any

interface Vlan10
 ip access-group LAB-COUNT in

flow record LAB-REC
 match ipv4 source address
 match ipv4 destination address
 collect transport source-port
 collect transport destination-port

flow exporter LAB-EXP
 destination 10.1.1.3
 transport udp 2055

flow monitor LAB-MON
 record LAB-REC
 exporter LAB-EXP

interface Vlan10
 ip flow monitor LAB-MON input

ip sla 10
 icmp-echo 10.1.1.3 source-interface Vlan10
 frequency 30
ip sla schedule 10 life forever start-time now

ntp server 10.1.1.3 prefer
```

### C9300-2 specific config

```ios
hostname C9300-2

interface Vlan10
 description SERVICES-VLAN
 ip address 10.1.1.55 255.255.255.0
 standby version 2
 standby 10 ip 10.1.1.1
 standby 10 priority 100
 standby 10 preempt
 ip pim sparse-mode
 ipv6 address 2001:db8:10::55/64
 no shutdown

interface Vlan20
 description VRRP-DEMO
 ip address 10.1.20.3 255.255.255.0
 vrrp 20 ip 10.1.20.1
 vrrp 20 priority 100
 vrrp 20 preempt
 no shutdown

interface Vlan47
 ip address 10.47.0.2 255.255.255.252
 bfd interval 150 min_rx 150 multiplier 3
 ip router isis LAB
 ip ospf 100 area 0
 ipv6 address 2001:db8:47::2/64

interface Loopback0
 ip address 10.255.0.2 255.255.255.255
 ip router isis LAB
 ip ospf 100 area 0

router ospf 100
 router-id 10.255.0.2
 passive-interface default
 no passive-interface Vlan47

router eigrp LAB
 address-family ipv4 unicast autonomous-system 100
  af-interface Vlan47
   bfd
  exit-af-interface
  network 10.47.0.0 0.0.0.3
  network 10.255.0.2 0.0.0.0
 exit-address-family

router isis LAB
 net 49.0001.0000.0000.0002.00
 is-type level-2-only

router bgp 65002
 bgp log-neighbor-changes
 neighbor 10.47.0.1 remote-as 65001
 neighbor 10.47.0.1 fall-over bfd
 address-family ipv4 unicast
  network 10.255.0.2 mask 255.255.255.255
  neighbor 10.47.0.1 activate
 exit-address-family

ntp server 10.1.1.3 prefer
```

### Ubuntu server role at 10.1.1.3

Ubuntu should be treated as a shared services box, not just a passive endpoint.

Recommended services:

- `chrony` or `ntpd` for switch NTP telemetry
- `FreeRADIUS` for AAA and 802.1X backend testing
- `nfcapd`, `pmacct`, or another NetFlow collector for flow exporter reachability
- `iperf3`, `ping`, `scapy`, or `mausezahn` for traffic generation
- `lldpd` if LLDP visibility from the Linux host is desired
- `smcroute` or multicast test tools if multicast telemetry is being exercised

Example Ubuntu setup goals:

```bash
sudo apt-get update
sudo apt-get install -y chrony freeradius nfdump lldpd iperf3 smcroute
```

For NTP, bind chrony to `10.1.1.3`.

For flow monitoring, listen on UDP `2055`.

For DHCP validation, either:

- attach a second endpoint to VLAN 30, or
- create an Ubuntu VLAN or namespace client on the connected NIC and request a lease from `10.1.30.1`

## Recommended Minimum Lab CLI Patterns

These snippets are activation patterns, not production designs.

### BGP

```ios
router bgp 65100
 bgp log-neighbor-changes
 neighbor 10.0.0.2 remote-as 65200
 address-family ipv4
  neighbor 10.0.0.2 activate
```

### OSPF

```ios
router ospf 100
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.3 area 0
```

### NTP

```ios
ntp server 192.0.2.10 prefer
ntp server 192.0.2.11
```

### DHCP Pool

```ios
ip dhcp excluded-address 10.10.10.1 10.10.10.20
ip dhcp pool USERS
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 8.8.8.8
```

### HSRP

```ios
interface Vlan10
 ip address 10.10.10.2 255.255.255.0
 standby version 2
 standby 10 ip 10.10.10.1
 standby 10 priority 110
 standby 10 preempt
```

### VRRP

```ios
interface Vlan20
 ip address 10.20.20.2 255.255.255.0
 vrrp 20 ip 10.20.20.1
 vrrp 20 priority 110
 vrrp 20 preempt
```

### Flexible NetFlow

```ios
flow record IPV4-REC
 match ipv4 source address
 match ipv4 destination address
 collect transport source-port
 collect transport destination-port

flow exporter LAB-EXP
 destination 192.0.2.50
 transport udp 2055

flow monitor LAB-MON
 record IPV4-REC
 exporter LAB-EXP

interface GigabitEthernet1/0/1
 ip flow monitor LAB-MON input
```

### IP SLA

```ios
ip sla 10
 icmp-echo 198.51.100.10 source-interface Vlan10
 frequency 30
ip sla schedule 10 life forever start-time now
```

### 802.1X

```ios
aaa new-model
dot1x system-auth-control

interface GigabitEthernet1/0/10
 description DOT1X-TEST-PORT
 switchport mode access
 authentication port-control auto
 mab
 dot1x pae authenticator
 spanning-tree portfast
```

### Port Security

```ios
interface GigabitEthernet1/0/11
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
```

### LACP Port-Channel

```ios
interface range GigabitEthernet1/0/21-22
 channel-group 1 mode active

interface Port-channel1
 switchport mode trunk
```

### UDLD

```ios
udld enable
interface GigabitEthernet1/0/23
 udld port aggressive
```

## Ordered Lab Activation Runbook

This is the recommended command-order for bringing the lab up from a blank-but-reachable starting point.

The goal is to avoid enabling higher-level features before the lower-level prerequisites have already been proven.

### Step 1. Enable transport and telemetry prerequisites on both switches

Apply first on `10.1.1.5`, then on `10.1.1.55`:

- `ip routing`
- `ipv6 unicast-routing`
- `lldp run`
- `cdp run`
- `udld enable`
- `restconf`
- `netconf-yang`

Validate:

- `show telemetry ietf subscription all`
- `show platform software yang-management process`
- `show running-config | include restconf|netconf-yang|lldp run|cdp run`

Expected telemetry to become meaningful:

- baseline platform and interface signals
- §13 LLDP once neighbors exist
- §14 CDP once neighbors exist
- §57 YANG Management Plane Interfaces once NETCONF/RESTCONF are active

### Step 2. Build the L2 underlay and access attachment

Apply trunks and VLANs on both switches, then verify Ubuntu is reachable on `Gi1/0/48` of both switches in VLAN 10.

Validate:

- `show interfaces trunk`
- `show vlan brief`
- `show lldp neighbors detail`
- `show cdp neighbors detail`
- `show udld neighbors`

Expected telemetry to populate or improve:

- §8 STP
- §10 VLANs
- §13 LLDP
- §14 CDP
- §17 Switchport
- §19 UDLD

### Step 3. Bring up the routed transit and loopbacks

Configure `Vlan47` and `Loopback0` on both switches before any routing protocol is enabled.

Validate:

- `show ip interface brief | include Vlan47|Loopback0`
- `show ipv6 interface brief | include Vlan47`
- `ping 10.47.0.2 source 10.47.0.1`
- `ping 10.255.0.2 source 10.255.0.1`

Expected telemetry to populate or improve:

- §7 Interface Statistics
- §12 ARP Table
- §46 CEF / FIB State
- §51 High-Scale ARP
- §52 IPv6 Neighbor Discovery after IPv6 peers answer

### Step 4. Bring up Ubuntu shared services before protocol work

Start Ubuntu services in this order:

1. `chrony`
2. NetFlow collector on UDP `2055`
3. `lldpd`
4. optional `FreeRADIUS`
5. traffic tools such as `iperf3`

Validate from Ubuntu:

- `ss -ulpn | grep 2055`
- `chronyc sources`
- `systemctl status lldpd`

Validate from C9300-1:

- `ping 10.1.1.3`
- `show ip arp vlan 10`

Expected telemetry to populate or improve:

- §12 ARP Table
- §33 NTP once the switches are pointed at Ubuntu
- §37 Flow Monitor once exporter is configured
- §51 High-Scale ARP

### Step 5. Enable OSPF and BFD on the transit VLAN

Bring OSPF up first, then confirm BFD is bound to the routed adjacency.

Validate:

- `show ip ospf neighbor`
- `show ip ospf interface vlan 47`
- `show bfd neighbors`

Expected telemetry to populate or improve:

- §25 OSPF State
- §34 BFD Sessions
- §46 CEF / FIB State

### Step 6. Enable EIGRP on the same transit and loopbacks

Only do this after OSPF and BFD are already healthy so adjacency failures are easier to isolate.

Validate:

- `show ip eigrp neighbors`
- `show ip eigrp topology`

Expected telemetry to populate or improve:

- §47 EIGRP Routing

### Step 7. Enable IS-IS and then verify interface-level detail

Bring up the IS-IS instance and only then check the interface-level model.

Validate:

- `show isis neighbors`
- `show isis interface`

Expected telemetry to populate or improve:

- §48 IS-IS Routing
- §53 IS-IS Interface Detail

### Step 8. Enable BGP last among routing protocols

Bring up BGP after the underlay is already stable so BGP issues are not confused with basic reachability issues.

Validate:

- `show bgp ipv4 unicast summary`
- `show bgp ipv4 unicast`
- `show bgp ipv4 unicast neighbors 10.47.0.2`

Expected telemetry to populate or improve:

- §24 BGP State
- §49 BGP Neighbor Detail
- §50 BGP RIB Detail

### Step 9. Enable first-hop redundancy on shared VLANs

Bring up HSRP on VLAN 10 and VRRP on VLAN 20 after the L2 trunk and SVIs are already healthy.

Validate:

- `show standby brief`
- `show vrrp brief`
- `ping 10.1.1.1`
- `ping 10.1.20.1`

Expected telemetry to populate or improve:

- §35 HSRP State
- §36 VRRP State

### Step 10. Enable service features on C9300-1

Apply in this order:

1. DHCP pool on VLAN 30
2. NTP server pointing to `10.1.1.3`
3. ACL on VLAN 10
4. Flow exporter and monitor toward `10.1.1.3`
5. IP SLA ICMP echo to `10.1.1.3`

Validate:

- `show ip dhcp pool`
- `show ip dhcp binding`
- `show ntp status`
- `show ntp associations`
- `show access-lists LAB-COUNT`
- `show flow exporter`
- `show flow monitor LAB-MON cache`
- `show ip sla statistics`

Expected telemetry to populate or improve:

- §27 DHCP Pool Stats
- §32 ACL Hit Counters
- §33 NTP Synchronization
- §37 Flow Monitor
- §38 IP SLA Probes

### Step 11. Force ARP and IPv6 ND to become meaningfully non-empty

Generate both IPv4 and IPv6 traffic between Ubuntu and the switches.

Validate:

- `show ip arp`
- `show ipv6 neighbors`
- `ping 10.1.1.3 source vlan 10`
- `ping ipv6 2001:db8:10::5 source 2001:db8:10::55`

Expected telemetry to populate or improve:

- §12 ARP Table
- §51 High-Scale ARP
- §52 IPv6 Neighbor Discovery

### Step 12. Build the GRE tunnel if tunnel telemetry is required

Use the loopbacks as tunnel endpoints only after BGP or OSPF has already ensured reachability.

Validate:

- `show interface tunnel 0`
- `show ip interface brief | include Tunnel0`
- `ping <remote-tunnel-ip> source <local-tunnel-ip>`

Expected telemetry to populate or improve:

- §56 Tunnel Interface State

### Step 13. Enable multicast only after baseline routing is stable

Configure PIM on the participating VLANs and use Ubuntu to source or join multicast traffic.

Validate:

- `show ip pim neighbor`
- `show ip mroute`

Expected telemetry to populate or improve:

- §54 Multicast Routing State

### Step 14. Optional high-risk phases

Only proceed after user approval.

Order:

1. MACsec / MKA on the inter-switch link
2. AAA with Ubuntu FreeRADIUS
3. 802.1X with a real supplicant host

Validate:

- `show macsec interface`
- `show mka session`
- `show aaa servers`
- `show radius statistics`
- `show authentication sessions interface <if>`

Expected telemetry to populate or improve:

- §39 AAA / RADIUS / TACACS
- §20 802.1X / Identity Sessions
- §41 MACsec / MKA

### Step 15. Detect-only and topology-limited features

Do not burn time trying to force these with the current wiring unless the lab changes:

- LACP / Port-Channel requires at least two physical links
- Stack / Stack Member / HA require stacked or HA hardware conditions
- PoE and PoE Health require powered endpoints
- TrustSec should remain manual or detect-only in this topology

Use only verification commands:

- `show etherchannel summary`
- `show switch detail`
- `show stackwise-virtual`
- `show power inline`
- `show cts interface`

Expected telemetry behavior:

- empty or low-value data is normal here and should not be treated as a collector fault

## Lab Capture Status — Round 7 (April 19 2026)

### Summary

| Metric | Value |
|--------|-------|
| Subscriptions with numeric metric output | **53 / 68** (77.9%) |
| Subscriptions with data received (any type) | **54 / 68** (79.4%) |
| Permanent gaps (no data expected) | 14 |
| Receiver-side info-only (data arrives, no numeric output) | 1 (sub 50018) |

### Subscription Status Per ID

Subscriptions confirmed active (file output produced):
`30001–50007, 50010–60009, 50014–50015, 50017, 50019–30004, 60016–50031, 60022, 50023`

Sub 50018 — LACP / Port-Channel (`lag-aggregate-state`):
- **Status: Data received, info-only** — Switch sends the XPath successfully. All fields
  (`lag-type`, `bundle-state`, `mode`, `fallback-enabled`) are YANG string/enum types.
  The receiver classifies this as `semantic_type: info` and produces no numeric metric output.
  No output directory is written. This is a receiver design choice, not a switch gap.
- C9300-2 Port-channel30 (Gi1/0/11, UP/connected) was created to provide a live bundle.
  Data was confirmed arriving at the receiver from both switches.

### Permanent Gaps (14 subscriptions — no data possible in this lab)

| Sub ID | Feature | Reason |
|--------|---------|--------|
| 50008 | Transceiver/Optics | No SFP transceivers inserted |
| 50009 | UDLD | No bidirectional neighbor (TOR in path, not under control) |
| 50016 | Linecard Status | Fixed-form-factor chassis — no line cards present |
| 60023 | MPLS LDP | MPLS not enabled (no MPLS license/config) |
| 50032 | MPLS Forwarding | MPLS not enabled |
| 60024 | LISP | LISP not configured |
| 60025 | VXLAN NVE | VXLAN not configured |
| 60026 | EVPN | EVPN not configured |
| 50033 | PTP/SyncE | No PTP clock hardware module present |

### Race Condition Fix (April 19 2026)

`rfc_yang_parser.go` `AnalyzeTelemetryPath()` had a concurrent map read/write race on the
`p.modules` map (multiple gRPC goroutines calling simultaneously). Fixed by adding
`sync.RWMutex` (`modulesMu`) to `RFC6020Parser` with double-checked locking on the
dynamic module creation path. Binary rebuilt and deployed.

---

## Feature-Specific Reality Notes For This Lab

### LACP / Port-Channel

Sub 50018 (`/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state`) fires correctly.
All YANG leaf types are string/enum — the receiver produces no numeric metrics but the
subscription is operationally valid. Port-channel30 (Gi1/0/11, ISR4331 uplink) is UP on
C9300-2 to provide a live bundle for this subscription.

Do not try to demonstrate LACP on `Gi1/0/47` with the current single-link wiring. The telemetry will remain structurally unconvincing because there is no real bundle.

### 802.1X / AAA

Ubuntu can host the RADIUS service, but that does not automatically create useful access-session telemetry. For realistic `identity-oper` data, use either:

1. a second host as the supplicant, or
2. a second Ubuntu NIC dedicated to supplicant testing.

### MACsec / MKA

The inter-switch link is the correct place to exercise MACsec. This is one of the few high-risk features that is still reasonable in the current topology because both link ends are under direct control.

### TrustSec

Treat TrustSec as detect-only or manually-curated in this lab unless an ISE-backed design is explicitly in scope.

### Stack / Stack Member / HA

Do not classify empty `stack-member-oper`, `stack-oper`, `ha-oper`, or `linecard-oper` telemetry as a collector problem when the hardware is simply not in a stacked or HA-capable state.

### Multicast Routing

`mroute-oper` will remain low-value until Ubuntu is used to source or join multicast traffic and both switches run a multicast control plane on the shared path.

---

## YANG Structure to Splunk Field Mapping Guide

This section explains how the RFC 7950 YANG constructs (containers, lists, keys, leaves, leaf-lists) map to Splunk fields when telemetry data arrives via gRPC dial-out with kvGPB encoding.

### How gRPC kvGPB Flattens the YANG Tree

When IOS XE streams a YANG model via kvGPB (key-value Google Protocol Buffers), the hierarchical YANG tree is flattened into a set of key-value pairs per telemetry message:

- **Keys** from YANG `list` nodes become **dimension fields** — they identify _which_ instance the metrics belong to
- **Leaves** (non-key) become **metric fields** — they carry the actual values
- **Nested containers** have their leaf names prefixed with the container path, using `/` as separator
- **Each list entry** produces a separate telemetry message row — one row per unique key combination

### YANG Construct → Splunk Field Mapping

| YANG Construct | kvGPB Behavior | Splunk Index Strategy | Splunk Queries |
|---------------|----------------|----------------------|----------------|
| **`container`** (top-level) | Defines the XPath subscription path | Becomes the `source` or is embedded in the metric name prefix | Filter by `source="/xpath..."` |
| **`list` with `key`** | Each list entry = one telemetry row; key fields are sent as string fields | Key values → **dimensions** in the Metrics Index (indexed fields for fast filtering) | `| mstats ... WHERE interface_name="GigabitEthernet1/0/1"` |
| **`leaf` (non-key, numeric)** | Sent as a numeric value | → **metric_name** in Metrics Index (e.g., `metric_name:in_octets`) | `| mstats avg(in_octets) WHERE ...` |
| **`leaf` (non-key, string/enum)** | Sent as a string value | → **dimension** field (indexed string for filtering, not a metric) | `WHERE oper_status="if-oper-state-ready"` |
| **`leaf-list`** | Repeated values sent as array | → multi-value dimension field or joined string | Use `mvcount()` or `mvindex()` in SPL |
| **Nested `container`** | Leaves prefixed with container name in field path | Field name = `parent_container/leaf_name` or flattened with underscore | `statistics/in_octets` or `statistics_in_octets` depending on collector |
| **Nested `list` inside `list`** | Produces separate rows with both parent and child keys | Both parent and child keys become dimensions; child metrics are in the child rows | Join parent+child keys or use subsearch |
| **`choice`/`case`** | Only the active case leaves are present | Handle absent fields with `coalesce()` or `if(isnotnull(...))` | Different panels per case, or unified with coalesce |

### Practical Examples

#### Example 1: Simple Container (CPU Utilization)
```
YANG tree:
  container cpu-usage
    └─ container cpu-utilization
         ├─ leaf five-seconds (uint8)
         ├─ leaf one-minute (uint8)
         └─ leaf five-minutes (uint8)
```

**Splunk Metrics Index mapping:**
- No keys → one row per switch per poll interval
- `metric_name:five_seconds`, `metric_name:one_minute`, `metric_name:five_minutes`
- Dimension: `source` (switch hostname/IP from telemetry header)

**SPL query:**
```spl
| mstats avg(five_seconds) prestats=true WHERE index=cisco_mdt source="*cpu-usage*"
  BY host span=1m
| timechart avg(five_seconds) BY host
```

#### Example 2: Keyed List (Interface Statistics)
```
YANG tree:
  container interfaces
    └─ list interface [key: name]
         ├─ leaf name (string) ← KEY → dimension
         ├─ leaf oper-status (enum) ← string → dimension
         └─ container statistics
              ├─ leaf in-octets (uint64) ← numeric → metric
              ├─ leaf out-octets (uint64) ← numeric → metric
              ├─ leaf in-errors (uint64) ← numeric → metric
              └─ leaf out-errors (uint64) ← numeric → metric
```

**Splunk Metrics Index mapping:**
- One row per `name` (interface) per poll → each interface is a separate event
- Key `name` → dimension field `name` (e.g., "GigabitEthernet1/0/1")
- `oper-status` → dimension field (string, filterable)
- `statistics/in-octets` → `metric_name:statistics/in_octets` (numeric metric)

**SPL query — Rate calculation (delta per second):**
```spl
| mstats rate(statistics/in_octets) AS rx_bps prestats=true
  WHERE index=cisco_mdt source="*interfaces*" name="GigabitEthernet1/0/*"
  BY host, name span=1m
| timechart avg(rx_bps) BY name
```

#### Example 3: Multi-Key List (Environment Sensors)
```
YANG tree:
  container environment-sensors
    └─ list environment-sensor [key: name, location]
         ├─ leaf name (string) ← KEY
         ├─ leaf location (string) ← KEY
         ├─ leaf state (string) ← dimension
         ├─ leaf current-reading (uint32) ← metric
         ├─ leaf sensor-units (enum) ← dimension
         └─ leaf sensor-name (enum) ← dimension
```

**Splunk Metrics Index mapping:**
- Composite key: `name` + `location` → both are dimensions
- Filter by `sensor_name="temperature"` to isolate temperature sensors
- `current-reading` is the metric; `sensor-units` tells you the unit (celsius, watts, rpm, etc.)

**SPL query — Temperature sensors only:**
```spl
| mstats latest(current_reading) AS reading prestats=true
  WHERE index=cisco_mdt source="*environment*" sensor_name="temperature"
  BY host, name, location span=5m
| timechart latest(reading) BY name
```

#### Example 4: Deeply Nested List (STP per-instance per-interface)
```
YANG tree:
  container stp-details
    └─ list stp-detail [key: instance]
         ├─ leaf instance (string) ← KEY (e.g., VLAN0100)
         ├─ leaf bridge-priority (uint32) ← metric
         └─ container interfaces
              └─ list interface [key: name]
                   ├─ leaf name (string) ← KEY
                   ├─ leaf role (enum) ← dimension
                   ├─ leaf state (enum) ← dimension
                   └─ leaf cost (uint64) ← metric
```

**Splunk handling of nested lists:**
- The subscription XPath determines what level of data you get
- Subscribe to `/stp-ios-xe-oper:stp-details/stp-detail` → get instance-level data
- Subscribe to `/stp-ios-xe-oper:stp-details/stp-detail/interfaces/interface` → get per-interface data with both `instance` (parent key) and `name` (child key) as dimensions
- Best practice: Subscribe at the deepest list level you need metrics from; parent keys are included automatically

**SPL query — STP port states:**
```spl
| mstats latest(cost) prestats=true
  WHERE index=cisco_mdt source="*stp*"
  BY host, instance, name, role, state span=5m
| stats latest(cost) AS cost, latest(role) AS role, latest(state) AS state
  BY host, instance, name
| where state="stp-blocking"
```

#### Example 5: Location-Keyed Platform Data (DP Resources)
```
YANG tree:
  container switch-dp-resources-oper-data
    └─ list location [key: fru, slot, bay, chassis, node]
         └─ list dp-feature-resource [key: feature, protocol, direction]
              ├─ leaf max-tcam-percentage-used (decimal64) ← metric
              └─ leaf max-em-percentage-used (decimal64) ← metric
```

**Splunk handling of 5-part composite keys:**
- All 5 location keys + 3 feature keys = 8 dimension fields per row
- For C9300 stacks, `chassis` differentiates stack members
- In SPL, filter or group by the relevant dimension:

```spl
| mstats max(max_tcam_percentage_used) AS tcam_pct prestats=true
  WHERE index=cisco_mdt source="*dp-resources*"
  BY host, chassis, feature, protocol span=5m
| timechart max(tcam_pct) BY feature
```

### Key Splunk Best Practices for YANG Telemetry

1. **Use Metrics Index (MPREFIX), not Events Index** — telemetry is high-volume numeric data; Metrics Index is 10x more efficient for storage and query speed

2. **Map YANG keys to Splunk dimensions** — Every YANG `list` key should be indexed as a dimension field in the Metrics Index. This enables fast `WHERE` filtering without full event scanning

3. **Map numeric leaves to metric_name** — Use `metric_name:leaf_path` format. The OTel collector typically handles this mapping

4. **Map string/enum leaves to dimensions** — Enum values like `oper-status`, `state`, `role` are string dimensions, not metrics. Use them in `WHERE` clauses and `BY` groupings

5. **Rate calculations for counters** — Most counter64 values (in-octets, match-counter, etc.) are monotonically increasing. Use `| mstats rate(metric) ...` to compute per-second rates, or `| mstats latest(metric) ...` and calculate delta manually

6. **Handle absent fields** — Not all leaves are always present (e.g., `choice`/`case` in YANG, or sensors that don't exist on a platform). Use `coalesce()` or `isnotnull()` guards

7. **Composite keys need all parts** — When a YANG list has multi-part keys (e.g., `name + location` for environment sensors), you need all key fields in your `BY` clause to avoid incorrect aggregation

8. **Subscription XPath depth determines data** — Subscribing to a parent container gets all child data but may be too broad. Subscribing to a specific nested list gets only that data with parent keys included. Choose the narrowest XPath that covers your needed KPIs

9. **Field name encoding** — The gRPC-to-Splunk pipeline (OTel collector) may transform field names: `/` → `_` or `.`, YANG hyphens → underscores. Verify actual field names in Splunk with `| mstats list(_dims)` after first data arrives

10. **Leaf-list handling** — YANG `leaf-list` (e.g., VRF member interfaces) becomes a multi-value field. Use `mvcount()` to count members, `mvindex()` to extract specific values, or `mvexpand()` to create one row per value

---

---

## Appendix A: LLM Execution Contract

If an LLM uses this guide to activate feature-dependent telemetry, it should follow this exact logic.

### Phase 1: Baseline Activation

1. Configure or validate the baseline telemetry pack.
2. Confirm the collector path and MDT health telemetry are working.
3. Verify that baseline features are non-empty before touching feature-dependent configuration.

### Phase 2: Empty-Feature Classification

For any empty feature, determine whether the reason is:

- unsupported model
- valid model but feature disabled
- feature enabled but no peer or endpoint
- feature enabled but no traffic
- feature enabled but external service unreachable
- hardware not applicable on this device

### Phase 3: Safe Activation Decision

Only proceed when the dependency class and automation risk class justify action.

- `Low`: may be auto-enabled in a lab after basic sanity checks.
- `Medium`: may be enabled only when the peer or topology assumption is already known to be correct.
- `High`: require explicit user confirmation before applying changes.
- `Discover-Only`: do not fabricate the feature; detect whether the platform already supports and uses it.

### Phase 4: Post-Change Validation

After any config change:

1. run feature verification CLI
2. re-check RESTCONF or live telemetry payloads
3. confirm data is non-empty and semantically meaningful
4. only then recommend visualizations or dashboard coverage

## Recommended Interpretation Rules for Empty Data

Use these rules consistently.

- Empty BGP or OSPF usually means there is no configured or active peer.
- Empty BFD usually means there is no dependent routed feature using BFD.
- Empty HSRP or VRRP usually means no redundant peer exists on the same subnet.
- Empty Flow Monitor often means the monitor is not applied or traffic is absent.
- Empty ACL counters often mean the ACL exists but matching traffic is absent.
- Empty AAA or 802.1X often means backend services or live access sessions are absent.
- Empty MACsec usually means the far end is not configured for a compatible policy.
- Empty PoE health often means the platform or connected endpoint mix does not exercise that data path.

---

## Appendix B: Repo Example Coverage Audit

## Repo Example Coverage Review

The cloned [cisco-ios-xe-mdt/README.md](cisco-ios-xe-mdt/README.md) and companion example configs were reviewed to ensure their example subscriptions are explicitly accounted for in this project.

Result:

- The repo does not introduce a major new Catalyst 9300 operational feature area that is missing from this PRD's current 48-feature scope.
- Most repo examples are either exact matches to existing feature roots, narrower subpaths of already-covered features, or OpenConfig equivalents of features already modeled here with Cisco-IOS-XE oper data.
- Event-driven examples from the repo are called out separately below and remain out of scope for the current requirements phase.
- Non-C9300 or wireless-controller examples in the repo are useful references, but they are not part of the Catalyst 9300 requirements baseline.

### Direct Coverage of Repo Examples

The following repo examples are already directly covered by the current feature inventory and typed-leaf appendix:

| Repo Example XPath | Repo Example Source | PRD Coverage | Notes |
|---|---|---|---|
| `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization` | periodic gRPC, gNMI, Telegraf examples | §1 CPU Utilization | Direct root match. |
| `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/five-seconds` | C9800 and mTLS examples | §1 CPU Utilization | Narrower leaf path of the same feature. |
| `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/one-minute` | C9800 examples | §1 CPU Utilization | Already covered in the typed leaf table. |
| `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/five-minutes` | C9800 examples | §1 CPU Utilization | Already covered in the typed leaf table. |
| `/memory-ios-xe-oper:memory-statistics/memory-statistic` | periodic gRPC and gNMI examples | §2 Memory Statistics | Direct root match. |
| `/process-memory-ios-xe-oper:memory-usage-processes/memory-usage-process` | periodic gRPC examples | §3 Process Memory | Narrower child path of the §3 feature. |
| `/environment-ios-xe-oper:environment-sensors` | periodic gRPC and gNMI examples | §5 Environment Sensors | Direct root match. |
| `/poe-ios-xe-oper:poe-oper-data` | device-health examples | §6 Power over Ethernet | Direct root match. |
| `/interfaces-ios-xe-oper:interfaces/interface` | periodic gRPC and gNMI examples | §7 Interface Statistics | Direct root match. |
| `/interfaces-ios-xe-oper:interfaces/interface[name="GigabitEthernet1"]/statistics` | C9800 examples | §7 Interface Statistics | Interface-specific narrowed path already covered by the §7 root. |
| `/lldp-ios-xe-oper:lldp-entries` | periodic gRPC examples | §13 LLDP Neighbors | Direct root match. |
| `/lldp-ios-xe-oper:lldp-entries/lldp-intf-details/` | gNMI examples | §13 LLDP Neighbors | Narrower child path already represented in the leaf appendix. |
| `/cdp-ios-xe-oper:cdp-neighbor-details` | gNMI examples | §14 CDP Neighbors | Direct root match. |
| `/platform-ios-xe-oper:components` | gNMI and sustainability examples | §15 Platform Components | Direct root match. |
| `/platform-ios-xe-oper:components/component` | sustainability examples | §15 Platform Components | Narrower child path of the same feature. |
| `/platform-ios-xe-oper:components/component/platform-properties/platform-property` | sustainability examples | §15 Platform Components | Important repo-specific subpath under the existing platform feature. |
| `/mdt-oper:mdt-oper-data/mdt-subscriptions` | gNMI examples | §22 MDT Subscription Health | Explicit legacy-path equivalent of the v2 MDT root already noted in the plan. |
| `/bgp-ios-xe-oper:bgp-state-data/neighbors/neighbor/session-state` | periodic gRPC examples | §24 BGP State | Narrower child path already covered by the §24 root and typed leaves. |
| `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state` | LACP mapping via interfaces-oper | §31 LACP / Port-Channel | Direct root match. |
| `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats` | current scope reference versus gNMI system AAA examples | §39 AAA / RADIUS / TACACS | Native AAA feature remains covered in the current PRD. |

### Repo Examples Covered as Sustainability or Granularity Variants

The sustainability lab under [cisco-ios-xe-mdt/sustainability/ztp.py](cisco-ios-xe-mdt/sustainability/ztp.py) and [cisco-ios-xe-mdt/sustainability/terraform.tf](cisco-ios-xe-mdt/sustainability/terraform.tf) uses more granular subpaths than the main plan. These should be explicitly recognized as accepted example variants of existing features.

| Repo Sustainability XPath | PRD Feature Mapping | Requirement Interpretation |
|---|---|---|
| `/environment-sensors` | §5 Environment Sensors | Same operational story as the namespaced environment root; treat as shorthand or CLI alias example. |
| `/oc-platform:components` | §15 Platform Components, plus OpenConfig mapping below | Broad OpenConfig platform inventory example. |
| `/platform-ios-xe-oper:components/component` | §15 Platform Components | Native per-component inventory and health example. |
| `/platform-ios-xe-oper:components/component/platform-properties/platform-property` | §15 Platform Components | Platform property inventory detail should stay in drill-down scope, not overview scope. |
| `/poe-oper-data/poe-module` | §6 Power over Ethernet | Module-level PoE capacity and supply context under the broader PoE feature. |
| `/poe-oper-data/poe-port-detail` | §6 Power over Ethernet | Already central to the §6 typed-leaf requirements. |
| `/poe-oper-data/poe-stack` | §6 Power over Ethernet | Stack-level PoE aggregation detail under the same feature. |
| `/poe-oper-data/poe-switch` | §6 Power over Ethernet | Switch-level PoE aggregation detail under the same feature. |

Requirement implication:

- The PRD should treat these repo subpaths as example subscription shapes that refine feature granularity, not as separate new feature domains.
- If a future subscription matrix is added, these narrower repo examples should be listed as approved subscription variants beneath the same parent feature.

### OpenConfig Examples Mapped to Current Native Features

The repo includes several OpenConfig and gNMI examples. These should be acknowledged in the PRD because they are part of the example corpus, but for Catalyst 9300 requirements they remain secondary to the native Cisco-IOS-XE oper models.

| Repo OpenConfig XPath | Current PRD Mapping | Requirements Position |
|---|---|---|
| `/oc-platform:components/component/state/temperature` | §5 Environment Sensors and §15 Platform Components | Valid example, but the PRD prefers native environment sensors for temperature semantics on C9300. |
| `/oc-platform:components/component/fan/state` | §5 Environment Sensors and §15 Platform Components | Useful equivalent for fan state, secondary to native environment/platform data. |
| `/oc-platform:components/component/power-supply/state` | §5 Environment Sensors and §15 Platform Components | Equivalent PSU view; keep as reference, not primary subscription guidance. |
| `/oc-sys:system/state` | §16 Device Hardware | Useful for boot time and system identity context, but native hardware and platform-oper remain primary. |
| `/oc-if:interfaces/interface/state/counters` | §7 Interface Statistics | OpenConfig equivalent of interface counters; valid reference example. |
| `/if:interfaces-state/interface[name="GigabitEthernet1"]/statistics` | §7 Interface Statistics | IETF equivalent of interface counters; scope already covered by the interface feature. |
| `/if:interfaces-state` | §7 Interface Statistics | General IETF interface-state example; not a new feature area. |
| `/components/component` | §15 Platform Components | OpenConfig gNMI equivalent of platform component inventory. |
| `/system/state` | §16 Device Hardware | Broad system identity/state example. |
| `/system/processes/process` | §3 Process Memory and §1 CPU Utilization | Related process-health view, but the current PRD keeps Cisco-IOS-XE process models as primary. |
| `/lacp/interfaces/interface` | §31 LACP / Port-Channel | OpenConfig equivalent; native interfaces-oper remains the primary C9300 recommendation. |
| `/macsec/interfaces/interface` | §41 MACsec / MKA Encryption | OpenConfig equivalent; native MACsec and MKA oper data remain primary. |
| `/macsec/mka/policies/policy` | §41 MACsec / MKA Encryption | OpenConfig policy view, secondary reference. |
| `/macsec/mka/key-chains/key-chain` | §41 MACsec / MKA Encryption | OpenConfig key-chain view, secondary reference. |
| `/macsec/mka/state/counters` | §41 MACsec / MKA Encryption | OpenConfig counter view aligned to the same security feature. |
| `/vlans/vlan` | §10 VLANs | OpenConfig equivalent for VLAN inventory. |
| `/network-instances/network-instance/vlans/vlan` | §10 VLANs and §42 VRF Operational State | Related OC VLAN-within-network-instance example; no new feature required. |
| `/system/aaa` | §39 AAA / RADIUS / TACACS | OpenConfig AAA equivalent; native AAA statistics remain primary. |

Requirements implication:

- The repo examples confirm that the PRD should document native Cisco-IOS-XE roots as primary for Catalyst 9300.
- OpenConfig examples should be recorded as acceptable interoperability or alternative-collector examples, not as replacements for the native scope already chosen here.

### Explicitly Out of Scope for This PRD: Event Examples

The repo includes on-change and notification-oriented examples in [cisco-ios-xe-mdt/c9300-grpc-onchange-examples.cfg](cisco-ios-xe-mdt/c9300-grpc-onchange-examples.cfg). These should be documented separately and treated as out of scope for the current dashboard requirements phase.

| Event XPath | Event Type | Scope Decision |
|---|---|---|
| `/ios-events-ios-xe-oper:bgp-peer-state-change` | Routing adjacency event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:ospf-neighbor-state-change` | Routing adjacency event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:ospf-interface-state-change` | Routing interface event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:interface-state-change` | Interface operational event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:interface-admin-state-change` | Interface administrative event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:memory-usage` | Memory alarm or event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:cpu-usage` | CPU alarm or event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:sdcard-fault` | Storage fault event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:system-reboot-complete` | System lifecycle event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:system-reboot-issued` | System lifecycle event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:flash-fault` | Storage fault event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:system-login-change` | Access event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:system-logout-change` | Access event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:tempsensor-fault` | Environmental fault event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:disk-usage` | Storage usage event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:usb-state-change` | Hardware event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:sfp-state-change` | Optics event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:sfp-support-state` | Optics capability event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:fantray-fault` | Environmental hardware event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:fan-fault` | Environmental hardware event | Out of scope for current periodic dashboard requirements. |
| `/ios-events-ios-xe-oper:tempsensor-state` | Environmental state event | Out of scope for current periodic dashboard requirements. |

Related note:

- The repo also includes `/ios:native` as an on-change configuration-streaming example. This is not an operational KPI source for the current dashboard requirements and remains out of scope for now.

### Additional Repo Examples Not Added to Current Catalyst 9300 Scope

The repo contains valid telemetry examples that do not belong in the current Catalyst 9300 dashboard requirements baseline.

| Repo Example | Why It Is Not Added to Current Scope |
|---|---|
| Wireless examples such as `Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data` in the repo README | Wireless controller and AP telemetry are outside the Catalyst 9300 access-switch requirements baseline. |
| BLE streaming example `/wireless-ble-ltx-oper:ble-ltx-oper-data/ble-ltx-ap-streaming` in [cisco-ios-xe-mdt/c9800-grpc-periodic.cfg](cisco-ios-xe-mdt/c9800-grpc-periodic.cfg) | This is a wireless-controller use case, not a Catalyst 9300 campus-switch operational requirement. |
| C9800-specific examples used to demonstrate leaf-level CPU and interface subscriptions | Useful as telemetry technique references, but not part of the C9300 feature inventory. |

Final coverage conclusion:

- The repo's Catalyst-oriented periodic examples are now explicitly accounted for in this PRD either as direct feature coverage, approved subpath variants, or OpenConfig equivalents.
- The repo's event examples are explicitly documented as separate and out of scope for now.
- The repo's wireless and controller-oriented examples are documented as informative references, but they do not change the current Catalyst 9300 requirements scope.

## Subscription Matrix

This matrix defines the preferred subscription XPath for each Catalyst 9300 feature and records any accepted alternative example paths found in the cloned repo.

Interpretation rules:

- Preferred native XPath means the default subscription target for this project's Catalyst 9300 requirements.
- Accepted repo alternatives are allowed reference paths from the cloned repo, usually as narrower child paths or OpenConfig or IETF equivalents.
- Event and config-streaming paths are intentionally excluded from this matrix because they are out of scope for the current periodic requirements.

| § | Feature | Preferred Native XPath | Accepted Repo Example Alternatives | Matrix Status |
|---|---|---|---|---|
| 1 | CPU Utilization | `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization` | `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/five-seconds`; `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/one-minute`; `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/five-minutes`; `/components/component/cpu` | Native root preferred; repo shows leaf-specific and OpenConfig variants. |
| 2 | Memory Statistics | `/memory-ios-xe-oper:memory-statistics/memory-statistic` | `/memory-ios-xe-oper:memory-statistics`; `/Cisco-IOS-XE-memory-oper:memory-statistics/memory-statistic` | Native root preferred; repo shows parent-path and RFC7951 naming variants. |
| 3 | Process Memory | `/process-memory-ios-xe-oper:memory-usage-processes` | `/process-memory-ios-xe-oper:memory-usage-processes/memory-usage-process`; `/system/processes/process` | Native process-memory root preferred; repo shows child-path and OpenConfig process equivalents. |
| 4 | System DRAM | `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes` | None noted in cloned repo | Use preferred native path only. |
| 5 | Environment Sensors | `/environment-ios-xe-oper:environment-sensors` | `/environment-sensors`; `/oc-platform:components/component/state/temperature`; `/oc-platform:components/component/fan/state`; `/oc-platform:components/component/power-supply/state` | Native environment root preferred; repo shows shorthand and OpenConfig environment views. |
| 6 | Power over Ethernet | `/poe-ios-xe-oper:poe-oper-data` | `/poe-ios-xe-oper:poe-oper-data/poe-switch`; `/poe-oper-data/poe-module`; `/poe-oper-data/poe-port-detail`; `/poe-oper-data/poe-stack`; `/poe-oper-data/poe-switch` | Native aggregate PoE root preferred; repo shows accepted narrower module, port, stack, and switch subpaths. |
| 7 | Interface Statistics | `/interfaces-ios-xe-oper:interfaces/interface` | `/interfaces-ios-xe-oper:interfaces/interface[name="GigabitEthernet1"]/statistics`; `/oc-if:interfaces/interface/state/counters`; `/if:interfaces-state`; `/if:interfaces-state/interface[name="GigabitEthernet1"]/statistics`; `/interfaces/interface`; `/interfaces/interface[name=Vlan1]/` | Native interfaces-oper root preferred; repo shows interface-specific, IETF, and OpenConfig equivalents. |
| 8 | Spanning Tree Protocol | `/stp-ios-xe-oper:stp-details` | None noted in cloned repo | Use preferred native path only. |
| 9 | Stack Health | `/stack-ios-xe-oper:stack-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 10 | VLANs | `/vlan-ios-xe-oper:vlans` | `/vlans/vlan`; `/network-instances/network-instance/vlans/vlan` | Native VLAN root preferred; repo shows OpenConfig VLAN inventory equivalents. |
| 11 | MAC Address Table | `/matm-ios-xe-oper:matm-oper-data` | Same root appears in repo examples | Direct native repo match. |
| 12 | ARP Table | `/arp-ios-xe-oper:arp-data` | Same root appears in repo examples | Direct native repo match. |
| 13 | LLDP Neighbors | `/lldp-ios-xe-oper:lldp-entries` | `/lldp-ios-xe-oper:lldp-entries/lldp-intf-details/` | Native LLDP root preferred; repo shows accepted child-path refinement. |
| 14 | CDP Neighbors | `/cdp-ios-xe-oper:cdp-neighbor-details` | Same root appears in repo examples | Direct native repo match. |
| 15 | Platform Components | `/platform-ios-xe-oper:components` | `/platform-ios-xe-oper:components/component`; `/platform-ios-xe-oper:components/component/platform-properties/platform-property`; `/oc-platform:components`; `/components/component`; `/components/component/state` | Native platform root preferred; repo shows narrower native and OpenConfig platform variants. |
| 16 | Device Hardware | `/device-hardware-xe-oper:device-hardware-data/device-hardware` | `/oc-sys:system/state`; `/system/state` | Native device-hardware root preferred; repo shows system-state equivalents for identity and uptime context. |
| 17 | Switchport | `/switchport-ios-xe-oper:switchport-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 18 | Transceiver / Optics | `/xcvr-ios-xe-oper:transceiver-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 19 | UDLD | `/udld-ios-xe-oper:udld-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 20 | 802.1X / Identity Sessions | `/identity-ios-xe-oper:identity-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 21 | TCAM Utilization | `/tcam-ios-xe-oper:tcam-details` | `/tcam-ios-xe-oper:tcam-details/tcam-detail/tcam-entries-used` | Native TCAM root preferred; repo shows accepted leaf-specific on-change example. |
| 22 | MDT Subscription Health | `/mdt-oper-v2:mdt-oper-v2-data` | `/mdt-oper:mdt-oper-data/mdt-subscriptions` | v2 MDT root preferred; repo legacy MDT path remains accepted as an alternative. |
| 23 | Software Install | `/install-ios-xe-oper:install-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 24 | BGP State | `/bgp-ios-xe-oper:bgp-state-data` | `/bgp-ios-xe-oper:bgp-state-data/neighbors/neighbor/session-state` | Native BGP state root preferred; repo shows accepted session-state subpath. |
| 25 | OSPF State | `/ospf-ios-xe-oper:ospf-oper-data` | None periodic; event examples intentionally excluded | Use preferred native periodic root only. |
| 26 | IETF Routing State | `/rt:routing-state` | None noted in cloned repo | Use preferred IETF routing path only. |
| 27 | DHCP Pool Stats | `/dhcp-ios-xe-oper:dhcp-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 28 | High Availability State | `/ha-ios-xe-oper:ha-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 29 | Linecard Status | `/linecard-ios-xe-oper:linecard-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 30 | TrustSec | `/trustsec-ios-xe-oper:trustsec-state` | None noted in cloned repo | Use preferred native path only. |
| 31 | LACP / Port-Channel | `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state` | `/lacp/interfaces/interface` | Native interfaces-oper path preferred; repo shows OpenConfig LACP equivalent. |
| 32 | ACL Hit Counters | `/acl-ios-xe-oper:access-lists/access-list` | None noted in cloned repo | Use preferred native path only. |
| 33 | NTP Synchronization | `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info` | None noted in cloned repo | Use preferred native path only. |
| 34 | BFD Sessions | `/bfd-ios-xe-oper:bfd-state/sessions` | None noted in cloned repo | Use preferred native path only. |
| 35 | HSRP State | `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info` | None noted in cloned repo | Use preferred native path only. |
| 36 | VRRP State | `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state` | None noted in cloned repo | Use preferred native path only. |
| 37 | Flow Monitor | `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor` | None noted in cloned repo | Use preferred native path only. |
| 38 | IP SLA Probes | `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry` | None noted in cloned repo | Use preferred native path only. |
| 39 | AAA / RADIUS / TACACS | `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats` | `/system/aaa` | Native AAA statistics root preferred; repo shows OpenConfig AAA equivalent. |
| 40 | Port Security | `/psecure-ios-xe-oper:psecure-oper-data/psecure-state` | None noted in cloned repo | Use preferred native path only. |
| 41 | MACsec / MKA Encryption | `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics` | `/macsec/interfaces/interface`; `/macsec/mka/policies/policy`; `/macsec/mka/key-chains/key-chain`; `/macsec/mka/state/counters` | Native MACsec oper root preferred; repo shows accepted OpenConfig MACsec and MKA equivalents. |
| 42 | VRF Operational State | `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry` | None noted in cloned repo | Use preferred native path only. |
| 43 | Data Plane Resources | `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource` | None noted in cloned repo | Use preferred native path only. |
| 44 | CPU Punt/Inject Counters | `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats` | None noted in cloned repo | Use preferred native path only. |
| 45 | PoE Health | `/poe-health-xe:poe-health-oper-data` | No direct repo equivalent; broader PoE examples exist under §6 | Keep PoE health as a separate native-only feature. |
| 46 | CEF / FIB State | `/fib-ios-xe-oper:fib-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 47 | EIGRP Routing | `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance` | None noted in cloned repo | Use preferred native path only. |
| 48 | IS-IS Routing | `/isis-ios-xe-oper:isis-oper-data/isis-instance` | None noted in cloned repo | Use preferred native path only. |
| 59 | PIM Multicast State | `/pim-ios-xe-oper:pim-oper-data` | None noted | Use preferred path only. |
| 60 | MPLS LDP Operational State | `/mpls-ldp-ios-xe-oper:mpls-ldp-oper-data` | None noted | Use preferred path only. |
| 61 | MPLS Forwarding (LFIB) | `/mpls-forwarding-ios-xe-oper:mpls-forwarding-oper-data` | None noted | Use preferred path only. |
| 62 | LISP Operational State | `/lisp-ios-xe-oper:lisp-state` | None noted | Use preferred path only. |
| 63 | VXLAN NVE Tunnel Endpoints | `/nve-ios-xe-oper:nve-oper-data` | None noted | Use preferred path only. |
| 64 | EVPN Operational State | `/evpn-ios-xe-oper:evpn-oper-data` | None noted | Use preferred path only. |
| 65 | PTP / SyncE Timing | `/ptp-synce-ios-xe-oper:ptp-synce-oper-data` | None noted | Use preferred path only. |
| 67 | IETF Interfaces Operational State | `/if:interfaces-state/interface` | None noted | Use preferred path only. |

Matrix conclusion:

- The preferred subscription set remains the native Cisco-IOS-XE and IETF paths already defined in the current feature inventory.
- The cloned repo contributes approved alternative examples mostly for CPU, memory, interfaces, environment, platform, PoE, LLDP, MDT health, BGP, LACP, AAA, and MACsec.
- Features without listed alternatives should continue using the current preferred native XPath as the sole requirement baseline.
