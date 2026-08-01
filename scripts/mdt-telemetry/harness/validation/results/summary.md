# MDT Validation Report — jcohoe-c9300-2.cisco.com

**Timestamp:** 20260412T222957Z
**Total subscriptions:** 49

## Summary

| Status | Count |
|--------|-------|
| Data returned | 37 |
| Empty (feature not configured) | 12 |
| Not found (404 — unsupported) | 0 |
| Error | 0 |

## Subscriptions with Data

| Sub ID | § | Name | Fields | Missing Keys | Missing Metrics |
|--------|---|------|--------|-------------|----------------|
| 1001 | 1 | CPU Utilization | 16 | — | — |
| 1002 | 2 | Memory Statistics | 7 | — | — |
| 1003 | 3 | Process Memory | 10 | — | — |
| 1004 | 4 | System DRAM | 28 | — | — |
| 1005 | 5 | Environment Sensors | 20 | — | — |
| 1006 | 6 | PoE Operational Data | 169 | — | — |
| 1007 | 7 | Interface Statistics | 113 | — | — |
| 1008 | 8 | Spanning Tree | 72 | — | interfaces/interface/cost, interfaces/interface/forward-transitions |
| 1009 | 9 | Stack Health | 38 | — | — |
| 1010 | 10 | VLANs | 8 | — | — |
| 1011 | 11 | MAC Address Table | 11 | — | — |
| 1012 | 12 | ARP Table | 21 | — | — |
| 1013 | 13 | LLDP Neighbors | 13 | — | — |
| 1014 | 14 | CDP Neighbors | 45 | — | — |
| 1015 | 15 | Platform Components | 26 | — | — |
| 1016 | 16 | Device Hardware | 25 | — | — |
| 1017 | 17 | Switchport | 5 | — | — |
| 1018 | 18 | Transceiver / Optics | 113 | — | — |
| 1020 | 20 | 802.1X / Identity Sessions | 73 | — | — |
| 1021 | 21 | TCAM Utilization | 8 | — | — |
| 1022 | 22 | MDT Subscription Health | 48 | — | — |
| 1023 | 23 | Software Install | 53 | — | — |
| 1024 | 24 | BGP State | 8 | — | prefix-activity/received/current-prefixes, prefix-activity/sent/current-prefixes |
| 1025 | 25 | OSPF State | 3 | router-id | — |
| 1026 | 26 | IETF Routing Table | 9 | — | — |
| 1027 | 27 | DHCP Pool Stats | 6 | — | — |
| 1028 | 28 | High Availability | 12 | — | — |
| 1030 | 30 | TrustSec | 9 | — | — |
| 1031 | 31 | LACP / Port-Channel | 113 | — | — |
| 1032 | 32 | ACL Hit Counters | 9 | — | match-counter |
| 1033 | 33 | NTP Synchronization | 32 | — | — |
| 1041 | 41a | MACsec | 7 | — | sc-encrypt-pkts |
| 1042 | 42 | VRF | 5 | — | — |
| 1043 | 43 | Data Plane Resources | 20 | — | — |
| 1044 | 44 | CPU Punt/Inject Counters | 15 | — | — |
| 1046 | 46 | CEF / FIB State | 156 | — | — |
| 1141 | 41b | MKA | 8 | — | — |

## Empty Data (Feature Not Configured)

These subscriptions returned HTTP 204 — the YANG module exists but no data is populated. This is expected if the feature is not configured on the device.

| Sub ID | § | Name | YANG Module |
|--------|---|------|------------|
| 1019 | 19 | UDLD | Cisco-IOS-XE-udld-oper |
| 1029 | 29 | Linecard Status | Cisco-IOS-XE-linecard-oper |
| 1034 | 34 | BFD Sessions | Cisco-IOS-XE-bfd-oper |
| 1035 | 35 | HSRP State | Cisco-IOS-XE-hsrp-oper |
| 1036 | 36 | VRRP State | Cisco-IOS-XE-vrrp-oper |
| 1037 | 37 | Flow Monitor | Cisco-IOS-XE-flow-monitor-oper |
| 1038 | 38 | IP SLA Probes | Cisco-IOS-XE-ip-sla-oper |
| 1039 | 39 | AAA / RADIUS | Cisco-IOS-XE-aaa-oper |
| 1040 | 40 | Port Security | Cisco-IOS-XE-psecure-oper |
| 1045 | 45 | PoE Health | Cisco-IOS-XE-poe-health-oper |
| 1047 | 47 | EIGRP | Cisco-IOS-XE-eigrp-oper |
| 1048 | 48 | IS-IS | Cisco-IOS-XE-isis-oper |

## Field Inventory (first 20 fields per subscription)

### §1 — CPU Utilization (Sub 1001)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization` | container |  |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/five-seconds` | int | 0 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/five-seconds-intr` | int | 0 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/one-minute` | int | 2 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/five-minutes` | int | 1 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes` | container |  |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process` | list | 624 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/pid` | int | 1 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/name` | str | Chunk Manager |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/tty` | int | 0 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/total-run-time` | str | 3 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/invocation-count` | int | 21 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/avg-run-time` | str | 142 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/five-seconds` | str | 0.0 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/one-minute` | str | 0.0 |
| `Cisco-IOS-XE-process-cpu-oper:cpu-utilization/cpu-usage-processes/cpu-usage-process[0]/five-minutes` | str | 0.0 |

### §2 — Memory Statistics (Sub 1002)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-memory-oper:memory-statistic` | list | 3 |
| `Cisco-IOS-XE-memory-oper:memory-statistic[0]/name` | str | Processor |
| `Cisco-IOS-XE-memory-oper:memory-statistic[0]/total-memory` | str | 1074181564 |
| `Cisco-IOS-XE-memory-oper:memory-statistic[0]/used-memory` | str | 338151084 |
| `Cisco-IOS-XE-memory-oper:memory-statistic[0]/free-memory` | str | 736030480 |
| `Cisco-IOS-XE-memory-oper:memory-statistic[0]/lowest-usage` | str | 729537324 |
| `Cisco-IOS-XE-memory-oper:memory-statistic[0]/highest-usage` | str | 733842368 |

### §3 — Process Memory (Sub 1003)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes` | container |  |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process` | list | 624 |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process[0]/pid` | int | 1 |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process[0]/name` | str | Chunk Manager |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process[0]/tty` | int | 0 |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process[0]/allocated-memory` | str | 848840 |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process[0]/freed-memory` | str | 6976 |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process[0]/holding-memory` | str | 871824 |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process[0]/get-buffers` | int | 0 |
| `Cisco-IOS-XE-process-memory-oper:memory-usage-processes/memory-usage-process[0]/ret-buffers` | int | 0 |

### §4 — System DRAM (Sub 1004)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-platform-software-oper:control-processes` | container |  |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process` | list | 1 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/fru` | str | fru-rp |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/slot` | int | 0 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/bay` | int | 0 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/chassis` | int | 1 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/control-process-status` | str | online |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/updated` | str | 0 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/load-average-stats` | container |  |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/load-average-stats/load-average-status` | str | Healthy |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/load-avg-minutes` | container |  |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/load-avg-minutes/load-avg-minute` | list | 0 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/memory-stats` | container |  |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/memory-stats/memory-status` | str | Healthy |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/memory-stats/total` | str | 7678304 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/memory-stats/used-number` | str | 4139112 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/memory-stats/used-percent` | str | 54 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/memory-stats/free-number` | str | 3539192 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/memory-stats/free-percent` | str | 46 |
| `Cisco-IOS-XE-platform-software-oper:control-processes/control-process[0]/memory-stats/available-number` | str | 3539192 |

### §5 — Environment Sensors (Sub 1005)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-environment-oper:environment-sensors` | container |  |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor` | list | 8 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/name` | str | Inlet Temp Sensor |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/location` | str | Switch 1 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/state` | str | Norm |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/current-reading` | int | 40 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/sensor-units` | str | celsius |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/low-critical-threshold` | int | -10 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/low-normal-threshold` | int | 0 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/high-normal-threshold` | int | 46 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/high-critical-threshold` | int | 56 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/sensor-name` | str | temperature |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/hi-minor-thrsld` | int | 56 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/environment-sensor[0]/hi-major-thrsld` | int | 56 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/env-stat` | container |  |
| `Cisco-IOS-XE-environment-oper:environment-sensors/env-stat/crit-alrm` | int | 0 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/env-stat/minor-alrm` | int | 0 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/env-stat/major-alrm` | int | 0 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/env-stat/cancl-snsrs` | int | 0 |
| `Cisco-IOS-XE-environment-oper:environment-sensors/env-stat/null-st-snsrs` | int | 0 |

### §6 — PoE Operational Data (Sub 1006)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-poe-oper:poe-oper-data` | container |  |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail` | list | 2 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/intf-name` | str | TenGigabitEthernet1/0/14 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/power-used` | str | 30.0 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/pd-class` | str | pd-ieee4 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/device-detected` | bool | True |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/device-name` | str |  CW9166I-A |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/police` | bool | False |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/power-admin-max` | str | 60.0 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/power-from-pse` | str | 30.0 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/power-to-pd` | str | 30.0 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/power-consumption` | str | 10.89 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/max-power-drawn` | str | 12.12 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/oper-state` | str | on |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/admin-state` | str | admin-state-auto |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/oper-power` | str | 10.89 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/admin-police` | str | police-action-none |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/oper-police` | str | oper-police-none |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/cutoff-power-police` | str | 30.0 |
| `Cisco-IOS-XE-poe-oper:poe-oper-data/poe-port-detail[0]/power-negotiation-used` | str | power-negotiation-cdp |

### §7 — Interface Statistics (Sub 1007)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-interfaces-oper:interface` | list | 45 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/name` | str | AppGigabitEthernet1/0/1 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/interface-type` | str | iana-iftype-ethernet-csmacd |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/admin-status` | str | if-state-up |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/oper-status` | str | if-oper-state-ready |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/last-change` | str | 2026-03-28T00:39:32.678+00:00 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/if-index` | int | 49 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/phys-address` | str | 70:0b:4f:f5:c2:a9 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/speed` | str | 1000000000 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics` | container |  |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/discontinuity-time` | str | 2026-03-28T00:37:20.334+00:00 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-octets` | str | 22830995 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-unicast-pkts` | str | 196078 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-broadcast-pkts` | str | 144229 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-multicast-pkts` | str | 144228 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-discards` | int | 0 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-errors` | int | 0 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-unknown-protos` | int | 0 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/out-octets` | int | 1043583065 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/out-unicast-pkts` | str | 13167342 |

### §8 — Spanning Tree (Sub 1008)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-spanning-tree-oper:stp-details` | container |  |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail` | list | 4 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/instance` | str | VLAN0001 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/hello-time` | int | 2 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/max-age` | int | 20 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/forwarding-delay` | int | 15 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/hold-count` | int | 6 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/bridge-priority` | int | 32769 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/bridge-address` | str | 70:0b:4f:f5:c2:80 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/designated-root-priority` | int | 32769 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/designated-root-address` | str | 08:ec:f5:c7:da:00 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/root-port` | int | 1 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/root-cost` | str | 20000 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/hold-time` | str | 1 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/topology-changes` | str | 3 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/time-of-last-topology-change` | str | 1970-01-16T21:15:20+00:00 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/interfaces` | container |  |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/interfaces/interface` | list | 0 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/root-if-name` | str | TenGigabitEthernet1/0/1 |
| `Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-detail[0]/protocol` | str | stp-proto-rstp |

### §9 — Stack Health (Sub 1009)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-stack-oper:stack-oper-data` | container |  |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node` | list | 1 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/chassis-number` | int | 1 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/priority` | int | 1 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/serial-number` | str | FOC2237U0A1 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/latency` | int | 0 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/keepalive-counters` | container |  |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/keepalive-counters/sent` | str | 0 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/keepalive-counters/received` | str | 0 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/keepalive-counters/sent-failure` | str | 0 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/keepalive-counters/receive-failure` | str | 0 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/keepalive-counters/consecutive-losses` | str | 0 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/interface-mtu` | int | 1500 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/role` | str | role-active |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/node-state` | str | state-ready |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/stack-mode` | str | mode-stackwise-rear |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/sso-ready-flag` | bool | False |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/mac-address` | str | 70:0b:4f:f5:c2:80 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/stack-ports` | list | 2 |
| `Cisco-IOS-XE-stack-oper:stack-oper-data/stack-node[0]/stack-ports[0]/port-num` | int | 1 |

### §10 — VLANs (Sub 1010)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-vlan-oper:vlans` | container |  |
| `Cisco-IOS-XE-vlan-oper:vlans/vlan` | list | 9 |
| `Cisco-IOS-XE-vlan-oper:vlans/vlan[0]/id` | int | 1 |
| `Cisco-IOS-XE-vlan-oper:vlans/vlan[0]/name` | str | default |
| `Cisco-IOS-XE-vlan-oper:vlans/vlan[0]/status` | str | active |
| `Cisco-IOS-XE-vlan-oper:vlans/vlan[0]/vlan-interfaces` | list | 4 |
| `Cisco-IOS-XE-vlan-oper:vlans/vlan[0]/vlan-interfaces[0]/interface` | str | AppGigabitEthernet1/0/1 |
| `Cisco-IOS-XE-vlan-oper:vlans/vlan[0]/vlan-interfaces[0]/subinterface` | int | 0 |

### §11 — MAC Address Table (Sub 1011)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-matm-oper:matm-oper-data` | container |  |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table` | list | 6 |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/table-type` | str | mat-vlan |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/vlan-id-number` | int | 1 |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/aging-time` | int | 300 |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/matm-mac-entry` | list | 4 |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/matm-mac-entry[0]/table-type` | str | mat-vlan |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/matm-mac-entry[0]/vlan-id-number` | int | 1 |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/matm-mac-entry[0]/mac` | str | 08:ec:f5:c7:da:01 |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/matm-mac-entry[0]/mat-addr-type` | str | dynamic |
| `Cisco-IOS-XE-matm-oper:matm-oper-data/matm-table[0]/matm-mac-entry[0]/port` | str | TenGigabitEthernet1/0/1 |

### §12 — ARP Table (Sub 1012)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-arp-oper:arp-data` | container |  |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf` | list | 2 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/vrf` | str | Default |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper` | list | 6 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper[0]/address` | str | 10.85.134.65 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper[0]/enctype` | str | ios-encaps-type-arpa |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper[0]/interface` | str | Vlan311 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper[0]/type` | str | ios-linktype-ip |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper[0]/mode` | str | ios-arp-mode-dynamic |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper[0]/hwtype` | str | ios-snpa-type-ieee48 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper[0]/hardware` | str | 70:1f:53:9b:0f:da |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-oper[0]/time` | str | 2026-04-12T22:30:17.047+00:00 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-entry` | list | 6 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-entry[0]/address` | str | 10.85.134.65 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-entry[0]/interface` | str | Vlan311 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-entry[0]/enctype` | str | ios-encaps-type-arpa |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-entry[0]/type` | str | ios-linktype-ip |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-entry[0]/mode` | str | ios-arp-mode-dynamic |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-entry[0]/hwtype` | str | ios-snpa-type-ieee48 |
| `Cisco-IOS-XE-arp-oper:arp-data/arp-vrf[0]/arp-entry[0]/hardware` | str | 70:1f:53:9b:0f:da |

### §13 — LLDP Neighbors (Sub 1013)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-lldp-oper:lldp-entry` | list | 5 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/device-id` | str | AP6CD6.E359.20FC |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/local-interface` | str | Te1/0/16 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/connecting-interface` | str | Gi0 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/ttl` | int | 120 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/capabilities` | container |  |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/capabilities/bridge` | list | 1 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/port-vlan-id` | int | 0 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/mau-type` | int | 30 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/auto-neg` | container |  |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/auto-neg/enabled` | list | 1 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/auto-neg/supported` | list | 1 |
| `Cisco-IOS-XE-lldp-oper:lldp-entry[0]/local-efp-id` | int | 0 |

### §14 — CDP Neighbors (Sub 1014)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details` | container |  |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail` | list | 7 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/device-id` | int | 206 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/device-name` | str | JCOHOE-C9600 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/local-intf-name` | str | TenGigabitEthernet1/0/13 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/port-id` | str | GigabitEthernet0/0 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/capability` | str | Router Switch IGMP  |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/platform-name` | str | cisco C9606R |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/version` | str | Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFT |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/duplex` | str | cdp-full-duplex |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/adv-version` | str | cdp-advertised-v2 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/hello-message` | container |  |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/hello-message/oui` | str |  |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/hello-message/protocol-id` | str |  |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/hello-message/payload-value` | str |  |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/hello-message/payload-len` | int | 0 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/vty-mgmt-domain` | str |  |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/native-vlan` | int | 0 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/vvid-tag` | int | 0 |
| `Cisco-IOS-XE-cdp-oper:cdp-neighbor-details/cdp-neighbor-detail[0]/vvid` | int | 0 |

### §15 — Platform Components (Sub 1015)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-platform-oper:components` | container |  |
| `Cisco-IOS-XE-platform-oper:components/component` | list | 55 |
| `Cisco-IOS-XE-platform-oper:components/component[0]/cname` | str | Fan1/1 |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state` | container |  |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/type` | str | comp-fan |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/id` | str | 1017 |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/description` | str | Switch 1 - FAN 1 |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/mfg-name` | str |  |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/version` | str |  |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/serial-no` | str |  |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/part-no` | str |  |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/temp` | container |  |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/location` | str | 1/0/1/0 |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/empty` | bool | False |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/mfg-date` | str | 1970-01-01T00:00:00+00:00 |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/firmware-ver` | str |  |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/removable` | bool | True |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/status` | str | status-active |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/comp-alarm-data` | container |  |
| `Cisco-IOS-XE-platform-oper:components/component[0]/state/parent` | str | Switch1 |

### §16 — Device Hardware (Sub 1016)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-device-hardware-oper:device-hardware` | container |  |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory` | list | 9 |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/hw-type` | str | hw-type-emmc |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/hw-dev-index` | int | 0 |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/version` | str | V02 |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/part-number` | str | C9300-24UX |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/serial-number` | str | FOC2237U0A1 |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/hw-description` | str | c93xx Stack |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/dev-name` | str | c93xx Stack |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/field-replaceable` | bool | False |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-inventory[0]/hw-class` | str | hw-class-physical |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data` | container |  |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data/current-time` | str | 2026-04-12T22:30:22+00:00 |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data/boot-time` | str | 2026-03-28T00:38:58+00:00 |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data/software-version` | str | Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFT |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data/rommon-version` | str | IOS-XE ROMMON |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data/last-reboot-reason` | str | Reload Command |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data/reason-severity` | str | normal |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data/unsaved-config` | bool | True |
| `Cisco-IOS-XE-device-hardware-oper:device-hardware/device-system-data/reload-history-support` | list | 1 |

### §17 — Switchport (Sub 1017)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-switchport-oper:switchport-oper-data` | container |  |
| `Cisco-IOS-XE-switchport-oper:switchport-oper-data/switchport-info` | list | 41 |
| `Cisco-IOS-XE-switchport-oper:switchport-oper-data/switchport-info[0]/if-name` | str | TwentyFiveGigE1/1/1 |
| `Cisco-IOS-XE-switchport-oper:switchport-oper-data/switchport-info[0]/enabled` | list | 1 |
| `Cisco-IOS-XE-switchport-oper:switchport-oper-data/switchport-info[0]/admin-mode` | str | admin-dyn-auto |

### §18 — Transceiver / Optics (Sub 1018)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data` | container |  |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver` | list | 3 |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/name` | str | TenGigabitEthernet1/1/1 |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/enabled` | bool | True |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/present` | bool | True |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/identifier` | str | SFP/SFP+ |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/connector` | str | LC connector |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/ethernet-pmd` | str | 1000BaseSX SFP |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/vendor` | str | CISCO-AVAGO |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/vendor-part` | str | SFBR-5766PZ |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/vendor-rev` | str |  |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/serial-no` | str | AGM12011449 |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/fault-condition` | bool | False |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/date` | str | 080102 |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/sonet` | str | unknown |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/otn` | str | otn-undefined |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/internal-temp` | str | 0.0 |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/output-power` | container |  |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/output-power/instant` | str | 0.0 |
| `Cisco-IOS-XE-transceiver-oper:transceiver-oper-data/transceiver[0]/output-power/avg` | str | 0.0 |

### §20 — 802.1X / Identity Sessions (Sub 1020)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-identity-oper:identity-oper-data` | container |  |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats` | container |  |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-rx` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-rx-start` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-rx-logoff` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-rx-resp` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-rx-resp-id` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-rx-req` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-rx-invalid` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-rx-len-error` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-tx` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-tx-start` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-tx-logoff` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-tx-resp` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-tx-req` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-retx-req` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-retx-req-fail` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-tx-req-id` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-retx-req-id` | int | 0 |
| `Cisco-IOS-XE-identity-oper:identity-oper-data/dot1x-global-stats/eapol-retx-req-id-fail` | int | 0 |

### §21 — TCAM Utilization (Sub 1021)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-tcam-oper:tcam-details` | container |  |
| `Cisco-IOS-XE-tcam-oper:tcam-details/tcam-detail` | list | 40 |
| `Cisco-IOS-XE-tcam-oper:tcam-details/tcam-detail[0]/asic-no` | int | 0 |
| `Cisco-IOS-XE-tcam-oper:tcam-details/tcam-detail[0]/name` | str | PBR ACL |
| `Cisco-IOS-XE-tcam-oper:tcam-details/tcam-detail[0]/hash-entries-max` | int | 0 |
| `Cisco-IOS-XE-tcam-oper:tcam-details/tcam-detail[0]/tcam-entries-max` | int | 1024 |
| `Cisco-IOS-XE-tcam-oper:tcam-details/tcam-detail[0]/hash-entries-used` | int | 0 |
| `Cisco-IOS-XE-tcam-oper:tcam-details/tcam-detail[0]/tcam-entries-used` | int | 0 |

### §22 — MDT Subscription Health (Sub 1022)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data` | container |  |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-streams` | container |  |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-streams/stream` | list | 3 |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions` | list | 8 |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/subscription-id` | int | 500 |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/base` | container |  |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/base/stream` | str | native |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/base/encoding` | str | encode-tdl |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/base/source-vrf` | str |  |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/base/source-address` | str | 10.85.134.70 |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/base/rcvr-type` | str | rcvr-type-protocol |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/base/period` | int | 60000 |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/base/tdl-uri` | str | /services;serviceName=ios_oper/poe_port_detail |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/type` | str | sub-type-static |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/state` | str | sub-state-valid |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/state-explanation` | str | Subscription validated |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/last-state-change-time` | str | 2026-03-28T00:39:29.325373+00:00 |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/mdt-receiver-names` | list | 1 |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/mdt-receiver-names[0]/name` | str | DNAC_ASSURANCE_RECEIVER |
| `Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscriptions[0]/mdt-receiver-names[0]/con-index` | int | 23 |

### §23 — Software Install (Sub 1023)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-install-oper:install-oper-data` | container |  |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information` | list | 1 |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/fru` | str | fru-rp |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/slot` | int | 0 |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/bay` | int | 0 |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/chassis` | int | 1 |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-packages` | list | 25 |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-packages[0]/pkg-dir` | str | /mnt/sd3/user |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-packages[0]/pkg-name` | str | cat9k-lni.S2C.SSA.pkg |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-packages[0]/ios-dir` | str | flash: |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-packages[0]/pkg-data` | container |  |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-packages[0]/cisco-image-name` | str | cat9k-lni.S2C.SSA.pkg |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-packages[0]/pkg-action` | str | install-package-action-none |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-version-info` | list | 3 |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-version-info[0]/version` | str | 17.15.03.0.5635 |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-version-info[0]/version-extension` | str | 1742971872 |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-version-info[0]/is-default` | bool | False |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-version-info[0]/previous` | str | install-version-state-present |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-version-info[0]/current` | str | install-version-state-present |
| `Cisco-IOS-XE-install-oper:install-oper-data/install-location-information[0]/install-version-info[0]/src-filename` | str | /mnt/sd3/user/cat9k_iosxe.17.15.03.SPA.bin |

### §24 — BGP State (Sub 1024)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-bgp-oper:bgp-state-data` | container |  |
| `Cisco-IOS-XE-bgp-oper:bgp-state-data/bgp-route-vrfs` | container |  |
| `Cisco-IOS-XE-bgp-oper:bgp-state-data/bgp-route-vrfs/bgp-route-vrf` | list | 2 |
| `Cisco-IOS-XE-bgp-oper:bgp-state-data/bgp-route-vrfs/bgp-route-vrf[0]/vrf` | str | default |
| `Cisco-IOS-XE-bgp-oper:bgp-state-data/bgp-route-vrfs/bgp-route-vrf[0]/bgp-route-afs` | container |  |
| `Cisco-IOS-XE-bgp-oper:bgp-state-data/bgp-route-rds` | container |  |
| `Cisco-IOS-XE-bgp-oper:bgp-state-data/bgp-route-rds/bgp-route-rd` | list | 1 |
| `Cisco-IOS-XE-bgp-oper:bgp-state-data/bgp-route-rds/bgp-route-rd[0]/rd-value` | str | 0:0 |

### §25 — OSPF State (Sub 1025)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-ospf-oper:ospf-oper-data` | container |  |
| `Cisco-IOS-XE-ospf-oper:ospf-oper-data/ospf-state` | container |  |
| `Cisco-IOS-XE-ospf-oper:ospf-oper-data/ospf-state/op-mode` | str | ospf-ships-in-the-night |

### §26 — IETF Routing Table (Sub 1026)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `ietf-routing:routing-state` | container |  |
| `ietf-routing:routing-state/routing-instance` | list | 3 |
| `ietf-routing:routing-state/routing-instance[0]/name` | str | default |
| `ietf-routing:routing-state/routing-instance[0]/type` | str | ietf-routing:default-routing-instance |
| `ietf-routing:routing-state/routing-instance[0]/router-id` | str | 0.0.0.0 |
| `ietf-routing:routing-state/routing-instance[0]/routing-protocols` | container |  |
| `ietf-routing:routing-state/routing-instance[0]/routing-protocols/routing-protocol` | list | 0 |
| `ietf-routing:routing-state/routing-instance[0]/ribs` | container |  |
| `ietf-routing:routing-state/routing-instance[0]/ribs/rib` | list | 0 |

### §27 — DHCP Pool Stats (Sub 1027)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-dhcp-oper:dhcp-oper-data` | container |  |
| `Cisco-IOS-XE-dhcp-oper:dhcp-oper-data/dhcpv6-relay-binding-stats` | container |  |
| `Cisco-IOS-XE-dhcp-oper:dhcp-oper-data/dhcpv6-relay-binding-stats/bndg-cnt` | int | 0 |
| `Cisco-IOS-XE-dhcp-oper:dhcp-oper-data/dhcpv6-relay-binding-stats/iana-bndg-cnt` | int | 0 |
| `Cisco-IOS-XE-dhcp-oper:dhcp-oper-data/dhcpv6-relay-binding-stats/iapd-bndg-cnt` | int | 0 |
| `Cisco-IOS-XE-dhcp-oper:dhcp-oper-data/dhcpv6-relay-binding-stats/bulk-lq-bndg-cnt` | int | 0 |

### §28 — High Availability (Sub 1028)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-ha-oper:ha-oper-data` | container |  |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra` | container |  |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/ha-state` | str | db-rf-active |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/peer-state` | str | db-rf-disabled |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/last-switchover-time` | str | 1970-01-01T00:00:00+00:00 |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/last-switchover-reason` | str | none |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/image-version` | str | 17.18.2 |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/leaf-mode` | str | SSO |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/ha-enabled` | bool | False |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/has-switchover-occured` | bool | False |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/switchover-count` | int | 0 |
| `Cisco-IOS-XE-ha-oper:ha-oper-data/ha-infra/standby-failure-count` | int | 0 |

### §30 — TrustSec (Sub 1030)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-trustsec-oper:trustsec-state` | container |  |
| `Cisco-IOS-XE-trustsec-oper:trustsec-state/cts-pac` | container |  |
| `Cisco-IOS-XE-trustsec-oper:trustsec-state/cts-env-data` | container |  |
| `Cisco-IOS-XE-trustsec-oper:trustsec-state/cts-env-data/status` | str | env-download-in-progress |
| `Cisco-IOS-XE-trustsec-oper:trustsec-state/cts-env-data/device-sgt` | int | 0 |
| `Cisco-IOS-XE-trustsec-oper:trustsec-state/cts-env-data/total-num-servers` | int | 0 |
| `Cisco-IOS-XE-trustsec-oper:trustsec-state/cts-env-data/life-time` | int | 0 |
| `Cisco-IOS-XE-trustsec-oper:trustsec-state/cts-env-data/last-updated-time` | str | 1970-01-01T00:00:00+00:00 |
| `Cisco-IOS-XE-trustsec-oper:trustsec-state/cts-env-data/next-refresh-time` | str | 1970-01-01T00:00:00+00:00 |

### §31 — LACP / Port-Channel (Sub 1031)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-interfaces-oper:interface` | list | 45 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/name` | str | AppGigabitEthernet1/0/1 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/interface-type` | str | iana-iftype-ethernet-csmacd |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/admin-status` | str | if-state-up |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/oper-status` | str | if-oper-state-ready |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/last-change` | str | 2026-03-28T00:39:33.308+00:00 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/if-index` | int | 49 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/phys-address` | str | 70:0b:4f:f5:c2:a9 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/speed` | str | 1000000000 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics` | container |  |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/discontinuity-time` | str | 2026-03-28T00:37:20.964+00:00 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-octets` | str | 22831121 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-unicast-pkts` | str | 196079 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-broadcast-pkts` | str | 144230 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-multicast-pkts` | str | 144229 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-discards` | int | 0 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-errors` | int | 0 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/in-unknown-protos` | int | 0 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/out-octets` | int | 1043589615 |
| `Cisco-IOS-XE-interfaces-oper:interface[0]/statistics/out-unicast-pkts` | str | 13167423 |

### §32 — ACL Hit Counters (Sub 1032)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-acl-oper:access-list` | list | 12 |
| `Cisco-IOS-XE-acl-oper:access-list[0]/access-control-list-name` | str | SACL1 |
| `Cisco-IOS-XE-acl-oper:access-list[0]/access-list-entries` | container |  |
| `Cisco-IOS-XE-acl-oper:access-list[0]/access-list-entries/access-list-entry` | list | 1 |
| `Cisco-IOS-XE-acl-oper:access-list[0]/access-list-entries/access-list-entry[0]/rule-name` | int | 10 |
| `Cisco-IOS-XE-acl-oper:access-list[0]/access-list-entries/access-list-entry[0]/access-list-entries-oper-data` | container |  |
| `Cisco-IOS-XE-acl-oper:access-list[0]/access-list-entries/access-list-entry[0]/access-list-entries-rule-data` | container |  |
| `Cisco-IOS-XE-acl-oper:access-list[0]/access-control-list-type` | str | v4-standard-acl |
| `Cisco-IOS-XE-acl-oper:access-list[0]/access-control-list-type-flags` | str |  |

### §33 — NTP Synchronization (Sub 1033)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-ntp-oper:ntp-status-info` | container |  |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/refid` | container |  |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/refid/kod-data` | container |  |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/refid/kod-data/kod-type` | str | ntp-ref-init |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/reftime` | str | 1970-01-01T00:00:00+00:00 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/sys-poll` | int | 3 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/stratum` | int | 16 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/root-delay` | str | 0.0 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/root-disp` | str | 20619.97 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/offset` | str | 0.0 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations` | list | 2 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/assoc-id` | int | 48932 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/peer-reach` | int | 0 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/peer-stratum` | int | 16 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/refid` | container |  |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/refid/kod-data` | container |  |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/reftime` | str | 1970-01-01T00:00:00+00:00 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/last-poll-time` | str | 0 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/poll` | int | 6 |
| `Cisco-IOS-XE-ntp-oper:ntp-status-info/ntp-associations[0]/delay` | str | 0.0 |

### §41a — MACsec (Sub 1041)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-macsec-oper:macsec-statistics` | list | 45 |
| `Cisco-IOS-XE-macsec-oper:macsec-statistics[0]/if-name` | str | AppGigabitEthernet1/0/1 |
| `Cisco-IOS-XE-macsec-oper:macsec-statistics[0]/tx-untag-pkts` | str | 0 |
| `Cisco-IOS-XE-macsec-oper:macsec-statistics[0]/rx-notag-pkts` | str | 0 |
| `Cisco-IOS-XE-macsec-oper:macsec-statistics[0]/rx-badtag-pkts` | str | 0 |
| `Cisco-IOS-XE-macsec-oper:macsec-statistics[0]/rx-unknownsci-pkts` | str | 0 |
| `Cisco-IOS-XE-macsec-oper:macsec-statistics[0]/rx-nosci-pkts` | str | 0 |

### §42 — VRF (Sub 1042)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-vrf-oper:vrf-entry` | list | 1 |
| `Cisco-IOS-XE-vrf-oper:vrf-entry[0]/vrf-name` | str | Mgmt-vrf |
| `Cisco-IOS-XE-vrf-oper:vrf-entry[0]/interface` | list | 1 |
| `Cisco-IOS-XE-vrf-oper:vrf-entry[0]/address-family-entry` | list | 2 |
| `Cisco-IOS-XE-vrf-oper:vrf-entry[0]/address-family-entry[0]/address-family` | str | ipv4-unicast |

### §43 — Data Plane Resources (Sub 1043)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-switch-dp-resources-oper:location` | list | 1 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/fru` | str | fru-fp |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/slot` | int | 0 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/bay` | int | 0 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/chassis` | int | 1 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/node` | int | 0 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource` | list | 53 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/feature` | str | dp-feature-mac-address-table |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/protocol` | str | dp-proto-mpls |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/direction` | str | dp-direction-ingress |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/max-tcam-percentage-used` | str | 2.15 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/max-em-percentage-used` | str | 0.17 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/max-acl-ids-percentage-used` | str | 0.0 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/max-lpm-percentage-used` | str | 0.0 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/instance-list` | list | 2 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/instance-list[0]/id` | int | 0 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/instance-list[0]/physical-location` | container |  |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/instance-list[0]/table-data` | list | 0 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/shared-ftr-list` | list | 1 |
| `Cisco-IOS-XE-switch-dp-resources-oper:location[0]/dp-feature-resource[0]/shared-ftr-list[0]/ftr-info` | container |  |

### §44 — CPU Punt/Inject Counters (Sub 1044)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location` | list | 1 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/fru` | str | fru-fp |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/slot` | int | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/bay` | int | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/chassis` | int | 1 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/node` | int | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats` | list | 32 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats[0]/cpuq-id` | int | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats[0]/rx-recv-prev` | str | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats[0]/rx-recv-cur` | str | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats[0]/rx-recv-delta` | str | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats[0]/rx-dropped-prev` | str | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats[0]/rx-dropped-cur` | str | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats[0]/rx-dropped-delta` | str | 0 |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper:location[0]/punt-inject-cpuq-brief-stats[0]/cpu-punt-queue-name` | str | CPU_Q_DOT1X_AUTH |

### §46 — CEF / FIB State (Sub 1046)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-fib-oper:fib-oper-data` | container |  |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry` | list | 4 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/instance-name` | str | IPv4:Default |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/af` | str | fib-addr-fam-ipv4 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/num-pfx` | int | 17 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/num-pfx-fwd` | int | 17 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/num-pfx-non-fwd` | int | 0 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/fib-entries` | list | 17 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/fib-entries[0]/ip-addr` | str | 0.0.0.0/0 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/fib-entries[0]/instance-name` | str | IPv4:Default |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/fib-entries[0]/af` | str | fib-addr-fam-ipv4 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/fib-entries[0]/num-paths` | int | 1 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/fib-entries[0]/packets-forwarded` | str | 0 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/fib-entries[0]/octets-forwarded` | str | 0 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/fib-ni-entry[0]/fib-entries[0]/fib-nexthop-entries` | list | 0 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/adjacency-table` | container |  |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/adjacency-table/num-adjacencies` | int | 6 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/adjacency-table/num-complete-adjacencies` | int | 6 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/adjacency-table/num-incomplete-adjacencies` | int | 0 |
| `Cisco-IOS-XE-fib-oper:fib-oper-data/adjacency-table/adjacency-entry` | list | 6 |

### §41b — MKA (Sub 1141)

| Field Path | Type | Sample Value |
|-----------|------|-------------|
| `Cisco-IOS-XE-mka-oper:mka-statistics` | list | 45 |
| `Cisco-IOS-XE-mka-oper:mka-statistics[0]/if-name` | str | AppGigabitEthernet1/0/1 |
| `Cisco-IOS-XE-mka-oper:mka-statistics[0]/mkpdu-stats-rx` | int | 0 |
| `Cisco-IOS-XE-mka-oper:mka-statistics[0]/mkpdu-stats-rx-distsak` | int | 0 |
| `Cisco-IOS-XE-mka-oper:mka-statistics[0]/mkpdu-stats-rx-distcak` | int | 0 |
| `Cisco-IOS-XE-mka-oper:mka-statistics[0]/mkpdu-stats-tx` | int | 0 |
| `Cisco-IOS-XE-mka-oper:mka-statistics[0]/mkpdu-stats-tx-distsak` | int | 0 |
| `Cisco-IOS-XE-mka-oper:mka-statistics[0]/mkpdu-stats-tx-distcak` | int | 0 |
