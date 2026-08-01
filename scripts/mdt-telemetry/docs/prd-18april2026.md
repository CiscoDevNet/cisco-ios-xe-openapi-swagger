# Product Requirements Draft — Dashboard Requirements

## Scope

This document defines the dashboard requirements for the Catalyst 9300 MDT telemetry project.

The goal is to document what should eventually be shown in the dashboards, which YANG models and features supply that data, how the data should be grouped, and what level of visualization is expected.

This document does not define implementation details for Splunk XML, SPL, or final UX polish. It is a requirements and planning artifact.

## Purpose

The dashboards need to demonstrate that the telemetry pipeline can turn a large MDT subscription set into understandable operational views.

The requirements must make it easy to answer these questions:

- Which YANG models are included?
- Which operational feature does each model represent?
- How many KPI or metric rows are available from each feature?
- Which metrics are most important versus secondary?
- Which dashboard should show each feature?
- What visualization style best matches each feature?

## Decisions Confirmed

- Build requirements first, not dashboards.
- Use one overview dashboard plus multiple domain drill-down dashboards.
- Primary audiences are SE or demo use and network operations use.
- The requirements should be feature-centric, with clear domain groupings.
- Metrics should be tiered as Must-Have, Nice-to-Have, and Optional.
- Visualization type should be specified at the requirements level.
- Dashboards should support multiple devices through a device selector.
- Panel naming should stay traceable to the MDT feature or subscription number.
- Thresholds and alert rules are out of scope for this phase.

## Source of Truth

- [plan.md](plan.md): detailed KPI tables, XPaths, YANG modules, and Splunk visualization notes
- [feature-enablement-guide.md](feature-enablement-guide.md): feature prerequisites, minimal CLI, guide links, and the baseline-versus-activated subscription model
- [cli-reference.md](cli-reference.md): CLI and RESTCONF evidence of what the device exposes
- [validation/subscriptions.yaml](validation/subscriptions.yaml): canonical subscription definitions
- [splunk-dashboard.xml](splunk-dashboard.xml): existing single-dashboard implementation reference

## Requirements Summary

The current validated telemetry core covers:

- 48 feature areas
- 48 primary YANG feature sections
- 49 subscriptions when MACsec and MKA are counted separately
- 343 KPI rows in the validated core documented in [plan.md](plan.md)

Version 3 of the enablement model extends the target scope beyond that validated core.

The current target scope is now:

- 48 validated core feature areas
- 9 additional native IOS XE expansion features
- 57 total target feature areas
- 58 total subscriptions when MACsec and MKA are counted separately
- 417 total KPI rows in the current target plan
- OpenConfig explicitly excluded from the expansion set

The requirements document should therefore map:

- the 48 validated core features to dashboard domains immediately
- the 9 native expansion features to the next validation wave
- the 343 validated core KPI rows plus the new native expansion KPI rows to display priorities and visualization expectations
- each feature to a clear operational story

## Native IOS XE Expansion Set

The following feature areas extend the project beyond the original 48 without relying on OpenConfig.

| New § | Feature | Native YANG Module | Preferred XPath | Dashboard Intent |
|---|---|---|---|---|
| 49 | BGP Neighbor Detail | Cisco-IOS-XE-bgp-nbr-oper | `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data/bgp-nbr-data` | Per-neighbor state, transport posture, and counters. |
| 50 | BGP RIB Detail | Cisco-IOS-XE-bgp-rib-oper | `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route` | Prefix and path-level BGP routing visibility. |
| 51 | High-Scale ARP | Cisco-IOS-XE-ip-arp-oper | `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry` | Better ARP scale and on-change support than the older ARP model. |
| 52 | IPv6 Neighbor Discovery | Cisco-IOS-XE-ipv6-nd-oper | `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry` | IPv6 adjacency and reachability views. |
| 53 | IS-IS Interface Detail | Cisco-IOS-XE-isis-intf-oper | `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-intf` | Interface and adjacency detail for IS-IS. |
| 54 | Multicast Routing State | Cisco-IOS-XE-mroute-oper | `/mroute-ios-xe-oper:mroute-oper-data/mroute-state` | Multicast forwarding-tree and outgoing-interface views. |
| 55 | Stack Member / Stackwise Virtual Detail | Cisco-IOS-XE-stack-member-oper | `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info` | Deeper stack member and SVL visibility where hardware supports it. |
| 56 | Tunnel Interface State | Cisco-IOS-XE-tunnel-oper | `/ios-tunnel-oper:tunnel-oper-data/tunnel-if` | Tunnel health, status, and traffic counters. |
| 57 | YANG Management Plane Interfaces | Cisco-IOS-XE-yang-interfaces-oper | `/yang-interfaces-oper:yang-interfaces-oper-data` | NETCONF/RESTCONF SSH management-plane posture. |

These 9 features should be considered part of the requirements scope now, even if they are still behind the original 48-feature core in terms of lab validation depth.

## Dashboard Strategy

### Dashboard Model

The target dashboard strategy is two-layered:

1. One overview dashboard for fast device health and demo value
2. Multiple drill-down dashboards organized by operational domain

### Overview Dashboard Requirements

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

## Feature Inventory

This table is the bridge between YANG models, operational features, and dashboard domains.

| § | Feature | YANG Module | XPath | KPI Rows | Domain |
|---|---|---|---|---:|---|
| 1 | CPU Utilization | Cisco-IOS-XE-process-cpu-oper | `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization` | 3 | System Health |
| 2 | Memory Statistics | Cisco-IOS-XE-memory-oper | `/memory-ios-xe-oper:memory-statistics/memory-statistic` | 5 | System Health |
| 3 | Process Memory | Cisco-IOS-XE-process-memory-oper | `/process-memory-ios-xe-oper:memory-usage-processes` | 7 | System Health |
| 4 | System DRAM | Cisco-IOS-XE-platform-software-oper | `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes` | 3 | System Health |
| 5 | Environment Sensors | Cisco-IOS-XE-environment-oper | `/environment-ios-xe-oper:environment-sensors` | 10 | Environment and Power |
| 6 | Power over Ethernet | Cisco-IOS-XE-poe-oper | `/poe-ios-xe-oper:poe-oper-data` | 12 | Environment and Power |
| 7 | Interface Statistics | Cisco-IOS-XE-interfaces-oper | `/interfaces-ios-xe-oper:interfaces/interface` | 26 | Interfaces |
| 8 | Spanning Tree Protocol | Cisco-IOS-XE-spanning-tree-oper | `/stp-ios-xe-oper:stp-details` | 17 | L2 Topology |
| 9 | Stack Health | Cisco-IOS-XE-stack-oper | `/stack-ios-xe-oper:stack-oper-data` | 20 | Platform and Resources |
| 10 | VLANs | Cisco-IOS-XE-vlan-oper | `/vlan-ios-xe-oper:vlans` | 4 | L2 Topology |
| 11 | MAC Address Table | Cisco-IOS-XE-matm-oper | `/matm-ios-xe-oper:matm-oper-data` | 6 | L2 Topology |
| 12 | ARP Table | Cisco-IOS-XE-arp-oper | `/arp-ios-xe-oper:arp-data` | 6 | L2 Topology |
| 13 | LLDP Neighbors | Cisco-IOS-XE-lldp-oper | `/lldp-ios-xe-oper:lldp-entries` | 6 | L2 Topology |
| 14 | CDP Neighbors | Cisco-IOS-XE-cdp-oper | `/cdp-ios-xe-oper:cdp-neighbor-details` | 7 | L2 Topology |
| 15 | Platform Components | Cisco-IOS-XE-platform-oper | `/platform-ios-xe-oper:components` | 10 | Platform and Resources |
| 16 | Device Hardware | Cisco-IOS-XE-device-hardware-oper | `/device-hardware-xe-oper:device-hardware-data/device-hardware` | 5 | Platform and Resources |
| 17 | Switchport | Cisco-IOS-XE-switchport-oper | `/switchport-ios-xe-oper:switchport-oper-data` | 5 | Interfaces |
| 18 | Transceiver / Optics | Cisco-IOS-XE-transceiver-oper | `/xcvr-ios-xe-oper:transceiver-oper-data` | 7 | Interfaces |
| 19 | UDLD | Cisco-IOS-XE-udld-oper | `/udld-ios-xe-oper:udld-oper-data` | 3 | Interfaces |
| 20 | 802.1X / Identity Sessions | Cisco-IOS-XE-identity-oper | `/identity-ios-xe-oper:identity-oper-data` | 13 | Security and Identity |
| 21 | TCAM Utilization | Cisco-IOS-XE-tcam-oper | `/tcam-ios-xe-oper:tcam-details` | 4 | Platform and Resources |
| 22 | MDT Subscription Health | Cisco-IOS-XE-mdt-oper-v2 | `/mdt-oper-v2:mdt-oper-v2-data` | 6 | Operations |
| 23 | Software Install | Cisco-IOS-XE-install-oper | `/install-ios-xe-oper:install-oper-data` | 3 | Operations |
| 24 | BGP State | Cisco-IOS-XE-bgp-oper | `/bgp-ios-xe-oper:bgp-state-data` | 10 | L3 Routing |
| 25 | OSPF State | Cisco-IOS-XE-ospf-oper | `/ospf-ios-xe-oper:ospf-oper-data` | 10 | L3 Routing |
| 26 | IETF Routing Table | ietf-routing | `/ietf-routing:routing/ribs/rib` | 6 | L3 Routing |
| 27 | DHCP Pool Stats | Cisco-IOS-XE-dhcp-oper | `/dhcp-ios-xe-oper:dhcp-oper-data` | 4 | Network Services |
| 28 | High Availability State | Cisco-IOS-XE-ha-oper | `/ha-ios-xe-oper:ha-oper-data` | 3 | Platform and Resources |
| 29 | Linecard Status | Cisco-IOS-XE-linecard-oper | `/linecard-ios-xe-oper:linecard-oper-data` | 4 | Platform and Resources |
| 30 | TrustSec | Cisco-IOS-XE-trustsec-oper | `/trustsec-ios-xe-oper:trustsec-state` | 5 | Security and Identity |
| 31 | LACP / Port-Channel | Cisco-IOS-XE-interfaces-oper | `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state` | 5 | Interfaces |
| 32 | ACL Hit Counters | Cisco-IOS-XE-acl-oper | `/acl-ios-xe-oper:access-lists/access-list` | 4 | Security and Identity |
| 33 | NTP Synchronization | Cisco-IOS-XE-ntp-oper | `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info` | 7 | Network Services |
| 34 | BFD Sessions | Cisco-IOS-XE-bfd-oper | `/bfd-ios-xe-oper:bfd-state/sessions` | 5 | Network Services |
| 35 | HSRP State | Cisco-IOS-XE-hsrp-oper | `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info` | 7 | Network Services |
| 36 | VRRP State | Cisco-IOS-XE-vrrp-oper | `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state` | 7 | Network Services |
| 37 | Flow Monitor | Cisco-IOS-XE-flow-monitor-oper | `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor` | 6 | Network Services |
| 38 | IP SLA Probes | Cisco-IOS-XE-ip-sla-oper | `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry` | 8 | Network Services |
| 39 | AAA / RADIUS / TACACS | Cisco-IOS-XE-aaa-oper | `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats` | 7 | Security and Identity |
| 40 | Port Security | Cisco-IOS-XE-psecure-oper | `/psecure-ios-xe-oper:psecure-oper-data/psecure-state` | 5 | Security and Identity |
| 41 | MACsec / MKA Encryption | Cisco-IOS-XE-macsec-oper + Cisco-IOS-XE-mka-oper | `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics` | 8 | Security and Identity |
| 42 | VRF Operational State | Cisco-IOS-XE-vrf-oper | `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry` | 3 | L3 Routing |
| 43 | Data Plane Resources | Cisco-IOS-XE-switch-dp-resources-oper | `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource` | 6 | Platform and Resources |
| 44 | CPU Punt/Inject Counters | Cisco-IOS-XE-switch-dp-punt-inject-oper | `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats` | 4 | Platform and Resources |
| 45 | PoE Health | Cisco-IOS-XE-poe-health-oper | `/poe-health-oper:poe-health-oper-data/location/poe-port/port-health` | 11 | Environment and Power |
| 46 | CEF / FIB State | Cisco-IOS-XE-fib-oper | `/fib-ios-xe-oper:fib-oper-data` | 7 | L3 Routing |
| 47 | EIGRP Routing | Cisco-IOS-XE-eigrp-oper | `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance` | 7 | L3 Routing |
| 48 | IS-IS Routing | Cisco-IOS-XE-isis-oper | `/isis-ios-xe-oper:isis-oper-data/isis-instance` | 6 | L3 Routing |
| 49 | BGP Neighbor Detail | Cisco-IOS-XE-bgp-nbr-oper | `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data` | 10 | L3 Routing |
| 50 | BGP RIB Detail | Cisco-IOS-XE-bgp-rib-oper | `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route` | 10 | L3 Routing |
| 51 | High-Scale ARP | Cisco-IOS-XE-ip-arp-oper | `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry` | 5 | L2 Topology |
| 52 | IPv6 Neighbor Discovery | Cisco-IOS-XE-ipv6-nd-oper | `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry` | 7 | L2 Topology |
| 53 | IS-IS Interface Detail | Cisco-IOS-XE-isis-intf-oper | `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type` | 9 | L3 Routing |
| 54 | Multicast Routing State | Cisco-IOS-XE-mroute-oper | `/mroute-ios-xe-oper:mroute-oper-data/mroute-state` | 10 | L3 Routing |
| 55 | Stack Member / SVL Detail | Cisco-IOS-XE-stack-member-oper | `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info` | 7 | Platform and Resources |
| 56 | Tunnel Interface State | Cisco-IOS-XE-tunnel-oper | `/ios-tunnel-oper:tunnel-oper-data/tunnel-if` | 10 | Interfaces |
| 57 | YANG Management Interfaces | Cisco-IOS-XE-yang-interfaces-oper | `/yang-interfaces-oper:yang-interfaces-oper-data` | 6 | Operations |

## Domain Requirements

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

## Review of Current Dashboard Direction

The current dashboard implementation in [splunk-dashboard.xml](splunk-dashboard.xml) is a useful implementation reference, but the requirements should not be constrained by that current layout.

Important review points:

- the current dashboard is panel-centric; this PRD should stay feature-centric
- some features naturally split into multiple panels and that is acceptable
- some features are inventory-oriented and may remain table-heavy
- some protocols may be empty on a given device, but they still belong in scope because they represent valid models and subscriptions

## Summary Tables

### Metrics by Domain

| Domain | Features | KPI Rows |
|---|---:|---:|
| System Health | 4 | 18 |
| Environment and Power | 3 | 33 |
| Interfaces | 6 | 56 |
| L2 Topology | 8 | 58 |
| L3 Routing | 11 | 88 |
| Security and Identity | 6 | 42 |
| Network Services | 7 | 44 |
| Platform and Resources | 9 | 63 |
| Operations | 3 | 15 |
| Total | 57 | 417 |

### Coverage Statement

This PRD covers:

- all 57 target telemetry feature sections from [plan.md](plan.md) (48 validated core + 9 native IOS XE expansion)
- all 58 subscriptions when MACsec and MKA are counted separately
- all 417 KPI rows across the full feature set
- the mapping from feature to domain and from domain to intended dashboard purpose
- a typed leaf-and-type appendix spanning the full feature set

Detailed engineering reference remains in [plan.md](plan.md). This PRD now carries the dashboard-oriented mapping, Cat 9K oper review, and leaf/type expectations needed for requirements work.

## C9K 26.1 Oper Review

The upstream IOS XE YANG innovation README adds useful platform context for deciding how deep the dashboard requirements should go on Catalyst 9K.

Key findings from the C9k 26.1 view:

- IOS XE 26.1.1 exposes 887 YANG models overall, with 222 operational models.
- Cat 9K exposes 684 total YANG models at 26.1.1, including 428 Cisco-IOS-XE modules, 128 OpenConfig modules, 39 IETF modules, 21 Tailf modules, and 68 other support or deviation modules.
- Cat 9K has 53 platform-exclusive models, which confirms that the platform has materially deeper switching, platform, and campus-security operational coverage than Cat 9200.
- The current dashboard scope aligns well with those Cat 9K strengths because it already emphasizes switching, platform, PoE, telemetry health, identity, MACsec, and data-plane resource views.

The most relevant Cat 9K-exclusive or Cat 9K-strength oper modules for this telemetry plan are:

| Module | In Current Scope | PRD Feature Mapping | Why It Matters |
|---|---|---|---|
| `Cisco-IOS-XE-identity-oper` | Yes | §20 | Campus access-session and authorization visibility is a core Cat 9K story. |
| `Cisco-IOS-XE-macsec-oper` | Yes | §41 | MACsec is a differentiating campus security data source. |
| `Cisco-IOS-XE-poe-health-oper` | Yes | §45 | Detailed PoE fault telemetry is highly relevant for access-switch demos. |
| `Cisco-IOS-XE-spanning-tree-oper` | Yes | §8 | STP state is central to campus L2 operational views. |
| `Cisco-IOS-XE-tcam-oper` | Yes | §21 | TCAM pressure is an important platform-capacity signal on switching platforms. |
| `Cisco-IOS-XE-switch-dp-resources-oper` | Yes | §43 | Shows per-feature TCAM and EM utilization in the forwarding pipeline. |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper` | Yes | §44 | Exposes punt and CPU queue pressure that operators cannot infer from interface counters alone. |
| `Cisco-IOS-XE-udld-oper` | Yes | §19 | Useful campus edge protection and link-health signal. |
| `Cisco-IOS-XE-stacking-oper` | Partially | §9 | Confirms Cat 9K stack-specific telemetry depth. |
| `Cisco-IOS-XE-stack-info-oper` | Not yet directly subscribed | Related to §9 | Candidate future enhancement for stack inventory and role detail. |

Requirements implication:

- The PRD should continue to prefer Cisco-IOS-XE operational models for the primary Catalyst 9300 dashboard story.
- OpenConfig remains useful where the platform has broad support, but it should not replace richer Cat 9K-native oper coverage for switching and campus health.
- Deeper typed-leaf requirements are most valuable on the Cat 9K-exclusive or Cat 9K-rich modules because those are the modules most likely to differentiate the demo.

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
| 26 | IETF Routing Table | `/ietf-routing:routing-state` | None noted in cloned repo | Use preferred IETF routing path only. |
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
| 45 | PoE Health | `/poe-health-oper:poe-health-oper-data/location/poe-port/port-health` | No direct repo equivalent; broader PoE examples exist under §6 | Keep PoE health as a separate native-only feature. |
| 46 | CEF / FIB State | `/fib-ios-xe-oper:fib-oper-data` | None noted in cloned repo | Use preferred native path only. |
| 47 | EIGRP Routing | `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance` | None noted in cloned repo | Use preferred native path only. |
| 48 | IS-IS Routing | `/isis-ios-xe-oper:isis-oper-data/isis-instance` | None noted in cloned repo | Use preferred native path only. |

Matrix conclusion:

- The preferred subscription set remains the native Cisco-IOS-XE and IETF paths already defined in the current feature inventory.
- The cloned repo contributes approved alternative examples mostly for CPU, memory, interfaces, environment, platform, PoE, LLDP, MDT health, BGP, LACP, AAA, and MACsec.
- Features without listed alternatives should continue using the current preferred native XPath as the sole requirement baseline.

## Typed Leaf Requirements

This section adds a first deep-dive pass into the actual YANG leaf paths that matter for dashboard requirements.

The goal is to make the requirements document explicit about three things:

- which leaves should be used from each subscribed XPath
- what semantic type each leaf represents
- how the dashboard should interpret each leaf's units or state model

Type conventions used in this PRD:

| Label | Meaning |
|---|---|
| percent | Utilization or ratio that should be rendered as 0-100% |
| bytes | Capacity or memory quantity that should normally be converted to MB or GB |
| milliwatts | Power quantity that may be rendered as mW or W depending on panel density |
| count | Absolute integer quantity |
| counter | Monotonic counter that should usually be trended as rate or delta |
| enum | Operational state or mode value suitable for status panels or filtering |
| bool | True or false operational flag |
| string | Identifier, name, or descriptive text |
| timestamp | Time value that should be rendered as date-time |
| decimal64 | Fixed-point numeric quantity, often percentage or ratio |

### §1 CPU Utilization

Root XPath: `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `five-seconds` | percent | Primary current CPU health signal for overview and alerting. |
| `one-minute` | percent | Short smoothing signal for drill-down trend context. |
| `five-minutes` | percent | Long smoothing signal for sustained load context. |

### §2 Memory Statistics

Root XPath: `/memory-ios-xe-oper:memory-statistics/memory-statistic`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `total-memory` | bytes | Memory pool capacity baseline. |
| `used-memory` | bytes | Current consumed memory in the pool. |
| `free-memory` | bytes | Current available memory in the pool. |
| `lowest-usage` | bytes | Historical low-water reference for capacity analysis. |
| `name` | string | Pool identity, especially Processor versus reserve pools. |

### §3 Process Memory

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

### §4 System DRAM

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

### §5 Environment Sensors

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

### §6 Power over Ethernet

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

### §7 Interface Statistics

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

### §20 802.1X / Identity Sessions

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

### §22 MDT Subscription Health

Root XPath: `/mdt-oper-v2:mdt-oper-v2-data`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| subscription key | count | Subscription identity and correlation key. |
| type | string | Configured versus dynamic subscription context. |
| state | enum | Valid, invalid, or similar health state. |
| filter xpath | string | Confirms the actual subscribed filter. |
| update count | counter | Volume/activity indicator for telemetry liveliness. |
| receiver state | enum | Transport/session health indicator. |

### §24 BGP State

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

### §25 OSPF State

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

### §41 MACsec / MKA Encryption

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

### §43 Data Plane Resources

Root XPath: `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| location keys | string | Hardware locality for capacity hot spots. |
| `feature` | enum | Resource consumer identity. |
| `protocol` | enum | Protocol context for the resource use. |
| `direction` | enum | Ingress or egress context. |
| `max-tcam-percentage-used` | decimal64 percent | Primary TCAM utilization signal. |
| `max-em-percentage-used` | decimal64 percent | Primary EM utilization signal. |

### §44 CPU Punt/Inject Counters

Root XPath: `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats`

| Leaf | Semantic Type | Requirement Use |
|---|---|---|
| `cpuq-id` | count | CPU queue identifier. |
| `cpu-punt-queue-name` | string | Queue label for operator readability. |
| `rx-recv-cur` | counter | Current punted packets received by the queue. |
| `rx-dropped-cur` | counter | Current dropped packets at the queue; should drive exception views. |

### §45 PoE Health

Root XPath: `/poe-health-oper:poe-health-oper-data/location/poe-port/port-health`

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

### §8 Spanning Tree Protocol (STP)

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

### §9 Stack Health

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

### §10 VLANs

Root XPath: `/vlan-ios-xe-oper:vlans`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `vlan/id` (key) | int | VLAN ID |
| `vlan/name` | string | VLAN name |
| `vlan/status` | enum (active/suspended) | VLAN status |
| `vlan/vlan-interfaces/interface` | list | Member interfaces |

### §11 MAC Address Table (MATM)

Root XPath: `/matm-ios-xe-oper:matm-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `matm-table/vlan-id-number` (key) | int | VLAN ID |
| `matm-table/table-type` | string | Table type |
| `matm-table/aging-time` | int | Aging time |
| `matm-table/matm-mac-entry/mac` (key) | string | MAC address |
| `matm-table/matm-mac-entry/mat-addr-type` | enum (static/dynamic) | Entry type |
| `matm-table/matm-mac-entry/port` | string | Port |

### §12 ARP Table

Root XPath: `/arp-ios-xe-oper:arp-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `arp-vrf/vrf` (key) | string | VRF name |
| `arp-vrf/arp-entry/address` (key) | string | IP address |
| `arp-vrf/arp-entry/hardware` | string | MAC address |
| `arp-vrf/arp-entry/interface` | string | Interface |
| `arp-vrf/arp-entry/mode` | enum (dynamic/static) | Entry type |
| `arp-vrf/arp-entry/time` | string | Entry time |

### §13 LLDP Neighbors

Root XPath: `/lldp-ios-xe-oper:lldp-entries`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `lldp-intf-details/if-name` (key) | string | Local interface |
| `lldp-intf-details/lldp-neighbor-details/identifier` | string | Neighbor device ID |
| `lldp-intf-details/lldp-neighbor-details/port-id` | string | Neighbor port ID |
| `lldp-intf-details/lldp-neighbor-details/system-name` | string | Neighbor system name |
| `lldp-intf-details/lldp-neighbor-details/system-capabilities` | string | Capabilities |
| `lldp-intf-details/lldp-neighbor-details/mgmt-addrs` | string | Management address |

### §14 CDP Neighbors

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

### §15 Platform Components

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

### §16 Device Hardware (Uptime, SW Version, Boot Time)

Root XPath: `/device-hardware-xe-oper:device-hardware-data/device-hardware`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `device-system-data/software-version` | string | **Software version** |
| `device-system-data/boot-time` | datetime | **Boot time** |
| `device-system-data/last-reboot-reason` | string | Reboot reason |
| `device-inventory/hw-type` | string | Hardware model |
| `device-inventory/serial-number` | string | Serial number |

### §17 Switchport

Root XPath: `/switchport-ios-xe-oper:switchport-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | string | Interface name |
| operational mode (access/trunk) | enum | Switchport mode |
| access VLAN ID | int | Access VLAN |
| native VLAN | int | Trunk native VLAN |
| allowed VLANs | string | Trunk allowed VLANs |

### §18 Transceiver / Optics

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

### §19 UDLD

Root XPath: `/udld-ios-xe-oper:udld-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | string | Interface |
| neighbor state | enum | UDLD neighbor status |
| direction | string | Direction |

### §21 TCAM Utilization

Root XPath: `/tcam-ios-xe-oper:tcam-details`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `tcam-detail/asic-no` (key) | int | ASIC number |
| `tcam-detail/name` (key) | string | Table name |
| `tcam-detail/tcam-entries-used` | gauge | **TCAM entries used** |
| (reference value per table/SDM) | int | TCAM entries max |

### §23 Software Install

Root XPath: `/install-ios-xe-oper:install-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| install package name | string | Package name |
| install package version | string | Package version |
| state (active/committed) | enum | Package state |

### §26 IETF Routing Table (RIB)

Root XPath: `/ietf-routing:routing-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `rib/name` (key) | string | RIB name |
| `route/destination-prefix` | string | Destination prefix |
| `route/next-hop` | string | Next hop |
| `route/source-protocol` | enum (connected/static/ospf/bgp) | Source protocol |
| `route/metric` | int | Metric |
| `route/route-preference` | int | Route preference |

### §27 DHCP Pool Stats

Root XPath: `/dhcp-ios-xe-oper:dhcp-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | string | Pool name |
| allocated count | gauge | Allocated addresses |
| available count | gauge | Available addresses |
| calculated | gauge | Utilization % |

### §28 High Availability State

Root XPath: `/ha-ios-xe-oper:ha-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| active/standby/init | enum | HA state |
| last switchover reason | string | Switchover reason |
| last switchover time | datetime | Switchover time |

### §29 Linecard Status

Root XPath: `/linecard-ios-xe-oper:linecard-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| key | int | Slot number |
| state | enum (active/standby/inserted) | Linecard state |
| type | string | Card type |
| serial | string | Serial number |

### §30 TrustSec (SGT/SXP)

Root XPath: `/trustsec-ios-xe-oper:trustsec-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `cts-rolebased-sgtmaps` entries | int | SGT tag value |
| IP-to-SGT mapping | string | SGT IP binding |
| `cts-sxp-connections` peer IP | string | SXP connection peer |
| state | enum | SXP connection state |
| speaker/listener | enum | SXP connection mode |

### §31 LACP / Port-Channel (via interfaces-oper)

Root XPath: `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `name` (Port-channelX) | string | Aggregate interface name |
| `lag-aggregate-state/member-link` | list | Member links |
| per-member oper state | enum | Member link state |
| static/LACP | string | LAG type |
| `lacp-oper` data | counter | LACP activity counters |

### §32 ACL Hit Counters

Root XPath: `/acl-ios-xe-oper:access-lists/access-list`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `access-control-list-name` (key) | string | ACL name |
| `access-control-list-type` | enum | ACL type |
| `access-list-entry/rule-name` (key) | string | Rule name |
| `access-list-entry/match-counter` | counter64 | Match count |

### §33 NTP Synchronization

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

### §34 BFD Sessions

Root XPath: `/bfd-ios-xe-oper:bfd-state/sessions`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `session/type` (key) | enum | Session type |
| `bfd-nbr/interface` (key) | string | Interface |
| `bfd-nbr/ip` (key) | ip-address | Neighbor IP |
| `state` | enum | Local state |
| `remote-state` | enum | Remote state |

### §35 HSRP State

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

### §36 VRRP State

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

### §37 Flexible NetFlow / Flow Monitor

Root XPath: `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `name` (key) | string | Monitor name |
| `flow-monitor-statistics/flows-added` | uint64 | Flows added |
| `flow-monitor-statistics/flows-aged` | uint64 | Flows aged |
| (flows-added minus flows-aged) | calculated | Active flows |
| `flow-cache-statistics` | uint64 | Cache entries |
| `flow-export-statistics` | uint64 | Export packets sent |

### §38 IP SLA Probes

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

### §39 AAA / RADIUS / TACACS Statistics

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

### §40 Port Security

Root XPath: `/psecure-ios-xe-oper:psecure-oper-data/psecure-state`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `if-name` (key) | string | Interface |
| `psecure-entry/vlan` (key) | uint16 | VLAN |
| `psecure-entry/mac` (key) | mac-address | MAC address |
| `psecure-entry/type` | enum | Secure type |
| `psecure-entry/age-remain` | uint32 (min) | Age remaining |

### §42 VRF Operational State

Root XPath: `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `vrf-name` (key) | string | VRF name |
| `address-family-entry/address-family` | enum | Address family |
| `interface` (leaf-list) | string[] | Member interfaces |

### §46 CEF / FIB State

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

### §47 EIGRP Routing (if applicable)

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

### §48 IS-IS Routing (if applicable)

Root XPath: `/isis-ios-xe-oper:isis-oper-data/isis-instance`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `tag` (key) | string | Instance tag |
| `isis-neighbor/system-id` (key) | phys-address | System ID |
| `isis-neighbor/level` (key) | enum | Level |
| `isis-neighbor/if-name` (key) | string | Interface |
| `isis-neighbor/state` | enum | Neighbor state |
| `isis-neighbor/holdtime` | uint32 (sec) | Hold time |

### §49 BGP Neighbor Detail

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

### §50 BGP RIB Detail

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

### §51 High-Scale ARP

Root XPath: `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `addr` (key) | ipv4-address | IPv4 address |
| `if-name` (key) | string | Interface |
| `hw-addr` | mac-address | MAC address |
| `mode` | enum | ARP mode |
| `update-time` | date-and-time | Update time |

### §52 IPv6 Neighbor Discovery

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

### §53 IS-IS Interface Detail

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

### §54 Multicast Routing State

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

### §55 Stack Member / Stackwise Virtual Detail

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

### §56 Tunnel Interface State

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

### §57 YANG Management Plane Interfaces

Root XPath: `/yang-interfaces-oper:yang-interfaces-oper-data`

| Leaf | Source Type | Requirement Use |
|---|---|---|
| `local-vrf/vrf-name` (key) | string | Local VRF |
| `local-vrf/state` | enum | Local VRF state |
| `ssh-server/hostkey-name` | string | NETCONF SSH host key |
| `ssh-server/hostkey-alg/rsa-sha2-256` | boolean | RSA-SHA2-256 enabled |
| `ssh-server/ciphers/aes128-ctr` | boolean | AES128-CTR enabled |
| `ssh-server/macs/hmac-sha2-256` | boolean | HMAC-SHA2-256 enabled |

## Out of Scope for This Draft

- final Splunk XML implementation
- final SPL queries
- exact color palette and UX polish
- finalized thresholds and alert rules
- permissions, roles, or Splunk app packaging

## Next Step

The typed-leaf pass is now complete for all 57 features (§1–§57). The next authoring step should be to add per-feature metric tiering tables for Must-Have, Nice-to-Have, and Optional metrics, starting with the overview-critical domains:

1. System Health
2. Environment and Power
3. Interfaces
4. Operations

That step should still stay in markdown requirements form before any dashboard implementation begins.
