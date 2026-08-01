# Catalyst 9300 MDT Feature Enablement Guide V3

## Purpose

This document defines how feature-dependent telemetry should be enabled, validated, and operationalized on Catalyst 9300 switches running IOS XE 17.18 or later 17.x releases.

It exists to solve a specific problem in this project:

- a telemetry subscription can be syntactically correct
- the YANG model can be present on the platform
- the telemetry pipeline can be healthy
- and the resulting data can still be empty because the underlying switch feature is not configured, not active, or not producing meaningful operational state

This guide turns that ambiguity into a predictable operating model for both human operators and LLM-driven automation.

## Scope

This guide covers:

- which telemetry features should work on most Catalyst 9300 devices without extra feature configuration
- which features require additional switch configuration before telemetry becomes useful
- what minimum lab configuration is usually required to activate each feature
- what CLI verification should prove the feature is genuinely active
- which Cisco Catalyst 9300 IOS XE 17.18 guide family should be used as the primary reference
- how an LLM should reason about empty telemetry before making changes

This guide does not attempt to replace Cisco product documentation or define production network designs. It is a telemetry enablement and validation guide for this project.

## Intended Consumers

This guide is written for two consumers:

1. Human operators building a repeatable Catalyst 9300 telemetry lab.
2. An automation LLM that will connect to one or more Catalyst 9300 switches, enable features where appropriate, validate that telemetry becomes non-empty, and then feed validated data into chart and dashboard recommendations.

## Version 3 Design Principles

Version 3 is based on these rules:

- Separate baseline telemetry from feature-activated telemetry.
- Treat empty telemetry as a state classification problem before treating it as a fault.
- Prefer the minimum safe configuration that produces meaningful operational state.
- Distinguish local-only features from peer-dependent and service-dependent features.
- Distinguish low-risk automation targets from high-risk security or identity features.
- Use Catalyst 9300 IOS XE 17.18 guide families when available, but tolerate adjacent 17.x chapter references when the chapter is easier to verify than the book-level index.

## Core Problem Model

Each feature should be interpreted through five states.

| State | Meaning | LLM Interpretation |
|---|---|---|
| Available | The model exists on the platform and release. | Feature is technically supported. |
| Subscribed | The telemetry subscription is configured and valid. | Transport path is ready. |
| Enabled | The switch feature has been configured locally. | The switch is prepared to generate state. |
| Active | The feature has live operational context such as a peer, endpoint, service, or traffic. | Telemetry should now become non-empty or materially richer. |
| Validated | CLI and telemetry both confirm the feature is producing useful data. | Safe to recommend charts, panels, and verification logic. |

The most important V3 behavior change is this:

- `subscribed` is not enough
- `enabled` is not always enough
- the desired state for most feature-dependent telemetry is `validated`

## Deployment Profiles

Use two deployment profiles.

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

## Feature Activation Catalog

This is the operational center of the document.

The goal is not to provide full production config. The goal is to tell an operator or an LLM exactly what kind of precondition is needed before telemetry should be expected to contain useful data.

| § | Feature | Dependency Class | Risk | Minimum Enablement Objective | Telemetry Success Condition | Primary Verification CLI | Preferred Cisco Guide |
|---|---|---|---|---|---|---|---|
| 13 | LLDP Neighbors | Peer-Dependent | Low | Ensure LLDP is enabled and a live neighbor is present. | Neighbor entries appear with interface and system identity. | `show lldp neighbors detail` | Interface and Hardware Components Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/int_hw/b_1718_int_and_hw_9300_cg.html |
| 19 | UDLD | Peer-Dependent | Medium | Enable UDLD globally and per interface where appropriate. | UDLD neighbor or operational state becomes populated. | `show udld neighbors` | Interface and Hardware Components Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/int_hw/b_1718_int_and_hw_9300_cg.html |
| 20 | 802.1X / Identity Sessions | Service-Dependent | High | Enable AAA and dot1x with at least one authenticator port and a real endpoint. | Authentication session state and identity context are populated. | `show authentication sessions interface <if>` | Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html |
| 24 | BGP State | Peer-Dependent | Medium | Configure a BGP process and at least one reachable neighbor with an active address family. | Neighbor state transitions from absent to a meaningful state, ideally Established. | `show bgp ipv4 unicast summary` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 25 | OSPF State | Peer-Dependent | Medium | Configure an OSPF process and at least one active interface or network statement on both sides. | OSPF neighbor and area data populate. | `show ip ospf neighbor` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 27 | DHCP Pool Stats | Feature-Only | Low | Create a DHCP pool and serve at least one active client subnet. | Pool utilization and bindings appear. | `show ip dhcp pool`; `show ip dhcp binding` | IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html |
| 30 | TrustSec | Service-Dependent | High | Enable only in a dedicated lab with clear AAA and policy intent. | CTS state, SGT, or SXP context appears with meaningful entries. | `show cts role-based permissions`; `show cts interface` | Cisco TrustSec Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/cts/b_1718_cts_9300_cg.html |
| 31 | LACP / Port-Channel | Peer-Dependent | Medium | Configure a port-channel with at least one operational LACP member on both ends. | Port-channel aggregate state and members populate. | `show etherchannel summary` | Layer 2 Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/lyr2/b_1718_lyr2_9300_cg.html |
| 32 | ACL Hit Counters | Traffic-Dependent | Low | Apply an ACL in a real forwarding path and generate matching traffic. | Hit counters increment. | `show access-lists` | Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html |
| 33 | NTP Synchronization | Service-Dependent | Low | Configure reachable NTP servers and allow synchronization to occur. | NTP status and associations become valid. | `show ntp status`; `show ntp associations` | System Management Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sys_mgmt/b_1718_sys_mgmt_9300_cg.html |
| 34 | BFD Sessions | Peer-Dependent | Medium | Enable BFD as part of a real routed adjacency, not as an isolated feature. | BFD sessions appear with a stable state. | `show bfd neighbors` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 35 | HSRP State | Peer-Dependent | Medium | Configure HSRP on a shared subnet across at least two switches. | Group state, virtual IP, and role populate. | `show standby brief` | IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html |
| 36 | VRRP State | Peer-Dependent | Medium | Configure VRRP on a shared subnet across at least two switches. | Group state, virtual IP, and role populate. | `show vrrp brief` | IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html |
| 37 | Flow Monitor | Traffic-Dependent | Medium | Configure a flow record, exporter, and monitor, then apply it to a traffic-carrying interface. | Flow cache entries appear and exporter state is meaningful. | `show flow monitor <name> cache` | Network Management Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/nmgmt/b_1718_nmgmt_9300_cg.html |
| 38 | IP SLA Probes | Feature-Only | Low | Create and schedule a continuously running IP SLA operation to a reachable target. | Operation state and statistics populate. | `show ip sla statistics` | Network Management Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/nmgmt/b_1718_nmgmt_9300_cg.html |
| 39 | AAA / RADIUS / TACACS | Service-Dependent | High | Configure AAA with at least one reachable authentication backend and generate real auth events. | AAA statistics populate with meaningful outcomes. | `show aaa servers`; `show radius statistics`; `show tacacs` | Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html |
| 40 | Port Security | Traffic-Dependent | Medium | Enable port security on an access interface with a live endpoint. | Learned secure MAC state and counters populate. | `show port-security interface <if>` | Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html |
| 41 | MACsec / MKA Encryption | Peer-Dependent | High | Configure both ends of a link with compatible MACsec and MKA policy. | MACsec and MKA sessions populate with operational counters. | `show macsec interface`; `show mka session` | Security Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html |
| 42 | VRF Operational State | Feature-Only | Low | Create one or more non-default VRFs and bind interfaces or SVIs as needed. | VRF entries and routed context populate. | `show vrf`; `show ip route vrf <name>` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 45 | PoE Health | Hardware-Conditional | Discover-Only | Use on PoE-capable platforms with powered endpoints attached. | Port health and fault telemetry populate on active PoE ports. | `show power inline`; `show power inline police` | Interface and Hardware Components Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/int_hw/b_1718_int_and_hw_9300_cg.html |
| 47 | EIGRP Routing | Peer-Dependent | Medium | Configure only in a deliberate EIGRP lab with a real neighbor. | Neighbor and instance state populate. | `show ip eigrp neighbors` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 48 | IS-IS Routing | Peer-Dependent | Medium | Configure only in a deliberate IS-IS lab with a real peer and participating interfaces. | Neighbor and instance state populate. | `show isis neighbors` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 49 | BGP Neighbor Detail | Peer-Dependent | Medium | Requires an active BGP session (see §24). Provides richer per-neighbor counters and prefix-level stats not available in the §24 root XPath. | Per-neighbor prefix counts and update counters appear alongside session state. | `show bgp neighbors` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 50 | BGP RIB Detail | Peer-Dependent | Medium | Requires an active BGP session with routes received. Best-path RIB will be empty until a neighbor is established and prefix exchange occurs. | BGP route entries appear with path attributes (MED, local-pref, next-hop). | `show bgp ipv4 unicast` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 51 | High-Scale ARP | Traffic-Dependent | Low | Requires L3 interfaces with active ARP entries. Uses a finer-grained native ARP model than §12. Useful when L2 traffic is present on the segment. | ARP table entries appear with hardware addresses and timestamps. | `show ip arp` | IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html |
| 52 | IPv6 Neighbor Discovery | Peer-Dependent | Low | Requires IPv6 addressing on at least one interface with reachable IPv6 neighbors. | IPv6 ND entries appear with state (reachable, stale, probe, incomplete). | `show ipv6 neighbors` | IP Addressing Services Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip/b_1718_ip_9300_cg.html |
| 53 | IS-IS Interface Detail | Peer-Dependent | Medium | Requires IS-IS enabled on interfaces with at least one established adjacency (see §48). Provides per-interface adjacency data not available in the §48 root XPath. | Interface-level adjacency state and neighbor detail populate. | `show isis interface` | IP Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/rtng/b_1718_rtng_9300_cg.html |
| 54 | Multicast Routing State | Feature-Only | Medium | Enable IP multicast routing and configure PIM on at least one interface. At least one active (S,G) or (*,G) entry must exist for data to appear. | Multicast routing table entries appear with ingress interface, RPF neighbor, and traffic rates. | `show ip mroute`; `show ip pim neighbor` | IP Multicast Routing Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/ip_multicast/b_1718_ip_multicast_9300_cg.html |
| 55 | Stack Member / Stackwise Virtual Detail | Hardware-Conditional | Discover-Only | Only meaningful on stacked or Stackwise Virtual (SVL) deployments. On a standalone device the data will be empty or minimal. | Stack member info appears with chassis role, SVL bandwidth, and stack-port link status. | `show stackwise-virtual`; `show switch detail` | Stacking Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/stck_mgr/b_1718_stck_mgr_9300_cg.html |
| 56 | Tunnel Interface State | Feature-Only | Low | Configure at least one tunnel interface (GRE, IPinIP, or equivalent). The subscription will be empty until a tunnel interface exists. | Tunnel admin/oper status, endpoint addresses, and bandwidth metrics appear. | `show interfaces tunnel <num>` | Interface and Hardware Components Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/int_hw/b_1718_int_and_hw_9300_cg.html |
| 57 | YANG Management Plane Interfaces | Service-Dependent | Low | Requires NETCONF or RESTCONF to be enabled. The subscription monitors the management-plane SSH and VRF configuration used by YANG interfaces. | Local VRF state and SSH algorithm posture appear in the telemetry stream. | `show netconf-yang status`; `show platform software yang-management process` | Programmability Configuration Guide 17.18.x: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b_1718_programmability_cg.html |

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

## LLM Execution Contract

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

## Native IOS XE Expansion Beyond The 48-Feature Core

The 48-feature core remains the validated baseline for this project, but it is no longer the scope ceiling.

Version 3 adds a native IOS XE expansion set that should be treated as part of the target Catalyst 9300 telemetry coverage.

- Validated core: 48 feature areas already documented in [plan.md](plan.md)
- Native expansion set: 9 additional feature areas using Cisco IOS XE native operational models only
- OpenConfig is explicitly excluded from this expansion set

These additional features should be treated as `phase-2 native coverage` until they are validated on the lab switches with the same rigor as the original 48.

| New § | Feature | Native YANG Module | Preferred XPath | Why It Matters | Current Lab Status |
|---|---|---|---|---|---|
| 49 | BGP Neighbor Detail | Cisco-IOS-XE-bgp-nbr-oper | `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data/bgp-nbr-data` | Separates per-neighbor state and counters from the older aggregate BGP view. | Fully demonstrable with the two-switch lab. |
| 50 | BGP RIB Detail | Cisco-IOS-XE-bgp-rib-oper | `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route` | Adds path-level prefix visibility beyond summary neighbor state. | Fully demonstrable with loopbacks and BGP peering. |
| 51 | High-Scale ARP | Cisco-IOS-XE-ip-arp-oper | `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry` | Better ARP telemetry for scale and on-change behavior than the older ARP model. | Fully demonstrable with the Ubuntu host and SVI gatewaying. |
| 52 | IPv6 Neighbor Discovery | Cisco-IOS-XE-ipv6-nd-oper | `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry` | Adds IPv6 adjacency visibility that the current 48-feature core does not cover. | Demonstrable after enabling IPv6 on the demo VLANs. |
| 53 | IS-IS Interface Detail | Cisco-IOS-XE-isis-intf-oper | `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-intf` | Adds interface-level IS-IS adjacency detail beyond instance-level IS-IS state. | Fully demonstrable with an IS-IS adjacency over the inter-switch transit VLAN. |
| 54 | Multicast Routing State | Cisco-IOS-XE-mroute-oper | `/mroute-ios-xe-oper:mroute-oper-data/mroute-state` | Adds multicast forwarding tree and egress-interface state. | Partially demonstrable; needs multicast traffic from Ubuntu and PIM enabled on both switches. |
| 55 | Stack Member / Stackwise Virtual Detail | Cisco-IOS-XE-stack-member-oper | `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info` | Provides stack-member and Stackwise Virtual detail beyond the older stack-oper summary. | Not fully demonstrable unless the hardware is actually stacked or Stackwise Virtual is configured and supported. |
| 56 | Tunnel Interface State | Cisco-IOS-XE-tunnel-oper | `/ios-tunnel-oper:tunnel-oper-data/tunnel-if` | Adds GRE or other tunnel operational state and counters. | Fully demonstrable with a GRE tunnel between loopbacks on the two switches. |
| 57 | YANG Management Plane Interfaces | Cisco-IOS-XE-yang-interfaces-oper | `/yang-interfaces-oper:yang-interfaces-oper-data` | Verifies NETCONF/RESTCONF SSH posture and VRF exposure for the management plane itself. | Fully demonstrable after NETCONF/RESTCONF are enabled. |

## Lab Topology Assumptions For This Project

The working lab topology for Version 3 is:

| Role | Device | Address | Notes |
|---|---|---|---|
| Primary switch | C9300-1 | 10.1.1.5 | Main telemetry source and default place to start validation. |
| Secondary switch | C9300-2 | 10.1.1.55 | Peer for adjacency-dependent features. |
| Ubuntu server | Ubuntu | 10.1.1.3 | Shared services host for NTP, RADIUS, flow collection, IP SLA targets, and traffic generation. |
| Inter-switch link | Gi1/0/47 on both switches | n/a | Single physical link; use it as an 802.1Q trunk, not as a port-channel member. |

Unless the user says otherwise, the rest of this guide assumes:

- `Gi1/0/47` on both switches is configured as the inter-switch trunk
- one free access port on C9300-1 is available for Ubuntu service attachment
- examples below use `Gi1/0/10` on C9300-1 as that Ubuntu-facing port

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

interface GigabitEthernet1/0/10
 description UBUNTU-SERVICE-HOST
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown

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

Apply trunks and VLANs on both switches, then place Ubuntu on `Gi1/0/10` of C9300-1 in VLAN 10.

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

## Feature-Specific Reality Notes For This Lab

### LACP / Port-Channel

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

## What This Means for the Dashboard Strategy

This guide reinforces a key dashboard requirement:

- there should be one dashboard and one core subscription set that work on most Catalyst 9300 devices regardless of feature-specific configuration

That baseline dashboard should emphasize:

- platform health
- control-plane health
- interface health
- telemetry health
- environmental state

Feature-activated dashboards or drill-downs should only be expected to populate after the corresponding feature is configured and validated.

That means the dashboard model should be:

1. Baseline overview that works almost everywhere.
2. Conditional drill-downs whose value depends on feature activation.

## Relationship to Other Project Documents

This guide complements the rest of the project as follows.

- [plan.md](plan.md): defines the telemetry feature catalog, KPIs, and subscriptions.
- [prd-18april2026.md](prd-18april2026.md): defines dashboard and subscription requirements.
- [cli-reference.md](cli-reference.md): provides operational show-command evidence and RESTCONF examples.
- [README.md](README.md): explains deployment of the pipeline.

This V3 guide adds the missing operational decision layer between subscription validity and meaningful feature telemetry, and it extends the project beyond the original 48-feature core with a native IOS XE-only expansion model tied to the actual lab topology.

## Canonical Cisco Entry Point

When a feature-specific chapter URL changes across 17.x trains, begin with the Catalyst 9300 configuration guide index:

https://www.cisco.com/c/en/us/support/switches/catalyst-9300-series-switches/products-installation-and-configuration-guides-list.html
