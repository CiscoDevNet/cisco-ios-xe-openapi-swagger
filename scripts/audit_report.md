# 📊 Swagger vs YANG Tree Completeness Audit Report

**Generated:** February 10, 2026
**Total Specs Audited:** 614
**Specs Without Trees:** 48

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| 🔴 CRITICAL | 94 | Gap score ≥ 70 — Swagger has very few paths vs YANG tree |
| 🟠 HIGH | 13 | Gap score 50-69 — Significant modeling gaps |
| 🟡 MEDIUM | 36 | Gap score 30-49 — Moderate gaps, many containers missing |
| 🔵 LOW | 71 | Gap score 10-29 — Minor gaps, mostly complete |
| 🟢 GOOD | 400 | Gap score < 10 — Well modeled |

## 🔴 CRITICAL — Severely Under-Modeled Specs

These specs have the largest gap between YANG tree nodes and Swagger paths.

| # | Module | Folder | Swagger Paths | Tree Containers+Lists | Path Coverage | Schema Props | Tree Leaves | Leaf Coverage | Gap Score |
|---|--------|--------|---------------|----------------------|---------------|-------------|-------------|---------------|-----------|
| 1 | cisco-bridge-domain | swagger-events-model | 1 | 49 | 2.0% | 1 | 179 | 0.6% | 98.4 |
| 2 | LLDP-MIB | swagger-events-model | 1 | 26 | 3.8% | 0 | 76 | 0.0% | 97.3 |
| 3 | CISCO-RTTMON-MIB | swagger-events-model | 3 | 69 | 4.3% | 0 | 512 | 0.0% | 97.0 |
| 4 | RMON-MIB | swagger-events-model | 2 | 47 | 4.3% | 0 | 185 | 0.0% | 97.0 |
| 5 | CISCO-VPDN-MGMT-MIB | swagger-events-model | 1 | 22 | 4.5% | 0 | 96 | 0.0% | 96.8 |
| 6 | DS1-MIB | swagger-events-model | 1 | 19 | 5.3% | 0 | 96 | 0.0% | 96.3 |
| 7 | DS3-MIB | swagger-events-model | 1 | 19 | 5.3% | 0 | 82 | 0.0% | 96.3 |
| 8 | OSPF-TRAP-MIB | swagger-mib-model | 1 | 99 | 1.0% | 22 | 198 | 11.1% | 96.0 |
| 9 | PIM-MIB | swagger-events-model | 1 | 17 | 5.9% | 0 | 45 | 0.0% | 95.9 |
| 10 | CISCO-STP-EXTENSIONS-MIB | swagger-events-model | 3 | 48 | 6.2% | 0 | 115 | 0.0% | 95.6 |
| 11 | CISCO-VLAN-MEMBERSHIP-MIB | swagger-events-model | 1 | 16 | 6.2% | 0 | 36 | 0.0% | 95.6 |
| 12 | CISCO-DOT3-OAM-MIB | swagger-events-model | 2 | 29 | 6.9% | 0 | 114 | 0.0% | 95.2 |
| 13 | CISCO-VOICE-DIAL-CONTROL-MIB | swagger-events-model | 5 | 73 | 6.8% | 0 | 294 | 0.0% | 95.2 |
| 14 | CISCO-NBAR-PROTOCOL-DISCOVERY-MIB | swagger-events-model | 2 | 28 | 7.1% | 0 | 74 | 0.0% | 95.0 |
| 15 | CISCO-PROCESS-MIB | swagger-events-model | 2 | 28 | 7.1% | 0 | 139 | 0.0% | 95.0 |
| 16 | DIAL-CONTROL-MIB | swagger-events-model | 2 | 28 | 7.1% | 0 | 122 | 0.0% | 95.0 |
| 17 | CISCO-OSPF-TRAP-MIB | swagger-mib-model | 1 | 95 | 1.1% | 45 | 293 | 15.4% | 94.7 |
| 18 | CISCO-POWER-ETHERNET-EXT-MIB | swagger-events-model | 1 | 13 | 7.7% | 0 | 56 | 0.0% | 94.6 |
| 19 | CISCO-SYSLOG-MIB | swagger-events-model | 1 | 13 | 7.7% | 0 | 29 | 0.0% | 94.6 |
| 20 | CISCO-UNIFIED-FIREWALL-MIB | swagger-events-model | 2 | 26 | 7.7% | 0 | 130 | 0.0% | 94.6 |
| 21 | RSVP-MIB | swagger-events-model | 2 | 26 | 7.7% | 0 | 168 | 0.0% | 94.6 |
| 22 | CISCO-EMBEDDED-EVENT-MGR-MIB | swagger-events-model | 2 | 24 | 8.3% | 0 | 70 | 0.0% | 94.2 |
| 23 | ENTITY-MIB | swagger-events-model | 1 | 12 | 8.3% | 0 | 33 | 0.0% | 94.2 |
| 24 | CISCO-IF-EXTENSION-MIB | swagger-events-model | 3 | 35 | 8.6% | 0 | 96 | 0.0% | 94.0 |
| 25 | CISCO-BULK-FILE-MIB | swagger-events-model | 1 | 11 | 9.1% | 0 | 38 | 0.0% | 93.6 |
| 26 | CISCO-CONFIG-COPY-MIB | swagger-events-model | 1 | 11 | 9.1% | 0 | 32 | 0.0% | 93.6 |
| 27 | CISCO-ENHANCED-MEMPOOL-MIB | swagger-events-model | 1 | 11 | 9.1% | 0 | 71 | 0.0% | 93.6 |
| 28 | CISCO-ENTITY-ALARM-MIB | swagger-events-model | 2 | 22 | 9.1% | 0 | 47 | 0.0% | 93.6 |
| 29 | Cisco-IOS-XE-ip-sla-events | swagger-events-model | 2 | 22 | 9.1% | 0 | 85 | 0.0% | 93.6 |
| 30 | CISCO-IP-URPF-MIB | swagger-events-model | 1 | 11 | 9.1% | 0 | 26 | 0.0% | 93.6 |
| 31 | RFC1315-MIB | swagger-events-model | 1 | 11 | 9.1% | 0 | 36 | 0.0% | 93.6 |
| 32 | CISCO-CEF-MIB | swagger-events-model | 4 | 42 | 9.5% | 0 | 162 | 0.0% | 93.3 |
| 33 | ietf-yang-push | swagger-events-model | 2 | 20 | 10.0% | 0 | 51 | 0.0% | 93.0 |
| 34 | DISMAN-EVENT-MIB | swagger-events-model | 5 | 47 | 10.6% | 0 | 111 | 0.0% | 92.6 |
| 35 | cisco-pw | swagger-events-model | 2 | 20 | 10.0% | 2 | 129 | 1.6% | 92.5 |
| 36 | CISCO-DATA-COLLECTION-MIB | swagger-events-model | 2 | 18 | 11.1% | 0 | 67 | 0.0% | 92.2 |
| 37 | CISCO-IETF-PW-MIB | swagger-events-model | 2 | 18 | 11.1% | 0 | 73 | 0.0% | 92.2 |
| 38 | CISCO-IMAGE-LICENSE-MGMT-MIB | swagger-events-model | 1 | 9 | 11.1% | 0 | 23 | 0.0% | 92.2 |
| 39 | Cisco-IOS-XE-stack-mgr-events-oper | swagger-events-model | 2 | 18 | 11.1% | 0 | 80 | 0.0% | 92.2 |
| 40 | FRAME-RELAY-DTE-MIB | swagger-events-model | 1 | 9 | 11.1% | 0 | 44 | 0.0% | 92.2 |
| 41 | MPLS-LSR-STD-MIB | swagger-events-model | 2 | 18 | 11.1% | 0 | 89 | 0.0% | 92.2 |
| 42 | CISCO-SONET-MIB | swagger-events-model | 4 | 33 | 12.1% | 0 | 96 | 0.0% | 91.5 |
| 43 | CISCO-EIGRP-MIB | swagger-events-model | 2 | 16 | 12.5% | 0 | 104 | 0.0% | 91.2 |
| 44 | CISCO-IPMROUTE-MIB | swagger-events-model | 1 | 8 | 12.5% | 0 | 44 | 0.0% | 91.2 |
| 45 | CISCO-RF-MIB | swagger-events-model | 3 | 24 | 12.5% | 0 | 56 | 0.0% | 91.2 |
| 46 | CISCO-SUBSCRIBER-SESSION-MIB | swagger-events-model | 4 | 32 | 12.5% | 0 | 170 | 0.0% | 91.2 |
| 47 | MPLS-LDP-STD-MIB | swagger-events-model | 4 | 32 | 12.5% | 0 | 143 | 0.0% | 91.2 |
| 48 | ietf-yang-library | swagger-events-model | 2 | 15 | 13.3% | 0 | 18 | 0.0% | 90.7 |
| 49 | IF-MIB | swagger-events-model | 2 | 15 | 13.3% | 0 | 57 | 0.0% | 90.7 |
| 50 | CISCO-ENTITY-FRU-CONTROL-MIB | swagger-events-model | 7 | 50 | 14.0% | 0 | 97 | 0.0% | 90.2 |
| 51 | CISCO-AAA-SERVER-MIB | swagger-events-model | 1 | 7 | 14.3% | 0 | 47 | 0.0% | 90.0 |
| 52 | CISCO-IETF-BFD-MIB | swagger-events-model | 2 | 14 | 14.3% | 0 | 56 | 0.0% | 90.0 |
| 53 | CISCO-IETF-FRR-MIB | swagger-events-model | 2 | 14 | 14.3% | 0 | 66 | 0.0% | 90.0 |
| 54 | CISCO-NETSYNC-MIB | swagger-events-model | 4 | 28 | 14.3% | 0 | 104 | 0.0% | 90.0 |
| 55 | CISCO-VOICE-DNIS-MIB | swagger-events-model | 1 | 7 | 14.3% | 0 | 14 | 0.0% | 90.0 |
| 56 | CISCO-OSPF-TRAP-MIB | swagger-events-model | 14 | 95 | 14.7% | 0 | 293 | 0.0% | 89.7 |
| 57 | CISCO-ENVMON-MIB | swagger-events-model | 5 | 31 | 16.1% | 0 | 64 | 0.0% | 88.7 |
| 58 | CISCO-ENTITY-QFP-MIB | swagger-events-model | 3 | 18 | 16.7% | 0 | 62 | 0.0% | 88.3 |
| 59 | CISCO-ENTITY-SENSOR-MIB | swagger-events-model | 2 | 12 | 16.7% | 0 | 33 | 0.0% | 88.3 |
| 60 | CISCO-IETF-ATM2-PVCTRAP-MIB | swagger-events-model | 1 | 6 | 16.7% | 0 | 15 | 0.0% | 88.3 |
| 61 | CISCO-IP-LOCAL-POOL-MIB | swagger-events-model | 3 | 18 | 16.7% | 0 | 40 | 0.0% | 88.3 |
| 62 | CISCO-PING-MIB | swagger-events-model | 1 | 6 | 16.7% | 0 | 23 | 0.0% | 88.3 |
| 63 | MPLS-TE-STD-MIB | swagger-events-model | 4 | 23 | 17.4% | 0 | 139 | 0.0% | 87.8 |
| 64 | CISCO-IETF-ISIS-MIB | swagger-events-model | 18 | 102 | 17.6% | 0 | 244 | 0.0% | 87.6 |
| 65 | CISCO-ATM-PVCTRAP-EXTN-MIB | swagger-events-model | 12 | 64 | 18.8% | 0 | 200 | 0.0% | 86.9 |
| 66 | CISCO-FLASH-MIB | swagger-events-model | 7 | 36 | 19.4% | 0 | 128 | 0.0% | 86.4 |
| 67 | CISCO-ETHER-CFM-MIB | swagger-events-model | 8 | 41 | 19.5% | 0 | 166 | 0.0% | 86.3 |
| 68 | tailf-kicker | swagger-events-model | 1 | 6 | 16.7% | 1 | 15 | 6.7% | 86.3 |
| 69 | BGP4-MIB | swagger-events-model | 2 | 10 | 20.0% | 0 | 49 | 0.0% | 86.0 |
| 70 | CISCO-HSRP-MIB | swagger-events-model | 1 | 5 | 20.0% | 0 | 23 | 0.0% | 86.0 |
| 71 | DRAFT-MSDP-MIB | swagger-events-model | 2 | 10 | 20.0% | 0 | 54 | 0.0% | 86.0 |
| 72 | OSPF-TRAP-MIB | swagger-events-model | 20 | 99 | 20.2% | 0 | 198 | 0.0% | 85.9 |
| 73 | CISCO-PIM-MIB | swagger-mib-model | 2 | 21 | 9.5% | 9 | 34 | 26.5% | 85.4 |
| 74 | BRIDGE-MIB | swagger-events-model | 3 | 14 | 21.4% | 0 | 47 | 0.0% | 85.0 |
| 75 | CISCO-CONFIG-MAN-MIB | swagger-events-model | 3 | 14 | 21.4% | 0 | 42 | 0.0% | 85.0 |
| 76 | CISCO-BGP4-MIB | swagger-events-model | 10 | 46 | 21.7% | 0 | 181 | 0.0% | 84.8 |
| 77 | CISCO-IPSEC-FLOW-MONITOR-MIB | swagger-events-model | 13 | 60 | 21.7% | 0 | 488 | 0.0% | 84.8 |
| 78 | CISCO-LICENSE-MGMT-MIB | swagger-events-model | 14 | 64 | 21.9% | 0 | 237 | 0.0% | 84.7 |
| 79 | CISCO-IETF-ATM2-PVCTRAP-MIB-EXTN | swagger-events-model | 2 | 10 | 20.0% | 2 | 24 | 8.3% | 83.5 |
| 80 | CISCO-PIM-MIB | swagger-events-model | 5 | 21 | 23.8% | 0 | 34 | 0.0% | 83.3 |
| 81 | ietf-event-notifications | swagger-events-model | 7 | 29 | 24.1% | 0 | 67 | 0.0% | 83.1 |
| 82 | Cisco-IOS-XE-sm-events-oper | swagger-events-model | 2 | 8 | 25.0% | 0 | 22 | 0.0% | 82.5 |
| 83 | Cisco-IOS-XE-wireless-events-oper | swagger-events-model | 2 | 8 | 25.0% | 0 | 59 | 0.0% | 82.5 |
| 84 | CISCO-IPSEC-MIB | swagger-events-model | 7 | 26 | 26.9% | 0 | 71 | 0.0% | 81.2 |
| 85 | CISCO-ETHER-CFM-MIB | swagger-mib-model | 6 | 41 | 14.6% | 52 | 166 | 31.3% | 80.4 |
| 86 | ENTITY-STATE-MIB | swagger-events-model | 2 | 7 | 28.6% | 0 | 15 | 0.0% | 80.0 |
| 87 | MPLS-L3VPN-STD-MIB | swagger-events-model | 6 | 21 | 28.6% | 0 | 85 | 0.0% | 80.0 |
| 88 | CISCO-VTP-MIB | swagger-events-model | 12 | 41 | 29.3% | 0 | 175 | 0.0% | 79.5 |
| 89 | CISCO-TAP2-MIB | swagger-events-model | 5 | 17 | 29.4% | 0 | 49 | 0.0% | 79.4 |
| 90 | POWER-ETHERNET-MIB | swagger-events-model | 3 | 10 | 30.0% | 0 | 28 | 0.0% | 79.0 |
| 91 | Cisco-IOS-XE-controller-shdsl-events | swagger-events-model | 2 | 6 | 33.3% | 0 | 29 | 0.0% | 76.7 |
| 92 | cisco-smart-license | swagger-events-model | 24 | 71 | 33.8% | 0 | 221 | 0.0% | 76.3 |
| 93 | MPLS-VPN-MIB | swagger-events-model | 5 | 14 | 35.7% | 0 | 80 | 0.0% | 75.0 |
| 94 | ietf-ospf | swagger-events-model | 9 | 23 | 39.1% | 0 | 81 | 0.0% | 72.6 |

## 🟠 HIGH — Significant Gaps

| # | Module | Folder | Swagger Paths | Tree C+L | Path Coverage | Gap Score |
|---|--------|--------|---------------|----------|---------------|-----------|
| 1 | CISCO-STACKWISE-MIB | swagger-events-model | 23 | 48 | 47.9% | 66.5 |
| 2 | CISCO-NTP-MIB | swagger-events-model | 5 | 10 | 50.0% | 65.0 |
| 3 | SNMPv2-MIB | swagger-events-model | 3 | 6 | 50.0% | 65.0 |
| 4 | common-mpls-static | swagger-other-model | 51 | 126 | 40.5% | 63.3 |
| 5 | SNMP-FRAMEWORK-MIB | swagger-mib-model | 1 | 2 | 50.0% | 57.5 |
| 6 | ietf-netconf-notifications | swagger-events-model | 5 | 8 | 62.5% | 56.2 |
| 7 | Cisco-IOS-XE-perf-measure-oper | swagger-oper-model | 39 | 118 | 33.1% | 56.0 |
| 8 | openconfig-network-instance | swagger-openconfig-model | 1076 | 2155 | 49.9% | 55.4 |
| 9 | CISCO-IETF-MPLS-ID-STD-03-MIB | swagger-mib-model | 1 | 2 | 50.0% | 55.0 |
| 10 | CISCO-UBE-MIB | swagger-mib-model | 1 | 2 | 50.0% | 55.0 |
| 11 | Cisco-IOS-XE-spanning-tree-events | swagger-events-model | 2 | 3 | 66.7% | 53.3 |
| 12 | Cisco-IOS-XE-livetools-actions-rpc | swagger-rpc-model | 7 | 10 | 70.0% | 51.0 |
| 13 | openconfig-access-points | swagger-openconfig-model | 144 | 215 | 67.0% | 51.0 |

## 🟡 MEDIUM — Moderate Gaps

| # | Module | Folder | Swagger Paths | Tree C+L | Path Coverage | Gap Score |
|---|--------|--------|---------------|----------|---------------|-----------|
| 1 | Cisco-IOS-XE-install-oper | swagger-oper-model | 72 | 182 | 39.6% | 48.8 |
| 2 | Cisco-IOS-XE-acl-oper | swagger-oper-model | 24 | 67 | 35.8% | 44.9 |
| 3 | CISCO-RADIUS-EXT-MIB | swagger-mib-model | 3 | 4 | 75.0% | 44.9 |
| 4 | CISCO-LICENSE-MGMT-MIB | swagger-mib-model | 38 | 64 | 59.4% | 44.5 |
| 5 | openconfig-system | swagger-openconfig-model | 78 | 141 | 55.3% | 43.9 |
| 6 | openconfig-mpls | swagger-openconfig-model | 110 | 197 | 55.8% | 41.3 |
| 7 | cisco-ethernet | swagger-other-model | 3 | 5 | 60.0% | 40.9 |
| 8 | CISCO-STACKWISE-MIB | swagger-mib-model | 31 | 48 | 64.6% | 39.3 |
| 9 | Cisco-IOS-XE-appqoe-serv-oper | swagger-oper-model | 84 | 166 | 50.6% | 34.6 |
| 10 | CISCO-IPMROUTE-MIB | swagger-mib-model | 6 | 8 | 75.0% | 34.5 |
| 11 | DIAL-CONTROL-MIB | swagger-mib-model | 17 | 28 | 60.7% | 34.4 |
| 12 | openconfig-spanning-tree | swagger-openconfig-model | 21 | 41 | 51.2% | 34.1 |
| 13 | CISCO-RF-MIB | swagger-mib-model | 18 | 24 | 75.0% | 34.1 |
| 14 | CISCO-ENVMON-MIB | swagger-mib-model | 22 | 31 | 71.0% | 33.4 |
| 15 | Cisco-IOS-XE-ospf-oper | swagger-oper-model | 141 | 256 | 55.1% | 31.4 |
| 16 | Cisco-IOS-XE-aaa-actions-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 17 | Cisco-IOS-XE-cellular-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 18 | Cisco-IOS-XE-cli-preview-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 19 | Cisco-IOS-XE-cli-rpc | swagger-rpc-model | 3 | 3 | 100.0% | 30.0 |
| 20 | Cisco-IOS-XE-cts-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 21 | Cisco-IOS-XE-cwan-actions-rpc | swagger-rpc-model | 3 | 3 | 100.0% | 30.0 |
| 22 | Cisco-IOS-XE-cwan-fw-rpc | swagger-rpc-model | 2 | 2 | 100.0% | 30.0 |
| 23 | Cisco-IOS-XE-port-bounce-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 24 | Cisco-IOS-XE-rescue-config-rpc | swagger-rpc-model | 5 | 5 | 100.0% | 30.0 |
| 25 | Cisco-IOS-XE-switch-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 26 | Cisco-IOS-XE-tech-support-rpc | swagger-rpc-model | 2 | 2 | 100.0% | 30.0 |
| 27 | Cisco-IOS-XE-trace-rpc | swagger-rpc-model | 2 | 2 | 100.0% | 30.0 |
| 28 | Cisco-IOS-XE-ucse-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 29 | Cisco-IOS-XE-utd-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 30 | Cisco-IOS-XE-verify-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 31 | Cisco-IOS-XE-wireless-tech-support-rpc | swagger-rpc-model | 2 | 2 | 100.0% | 30.0 |
| 32 | Cisco-IOS-XE-xcopy-rpc | swagger-rpc-model | 1 | 1 | 100.0% | 30.0 |
| 33 | Cisco-IOS-XE-ios-events-oper | swagger-events-model | 2 | 2 | 100.0% | 30.0 |
| 34 | Cisco-IOS-XE-line-events | swagger-events-model | 2 | 1 | 100.0% | 30.0 |
| 35 | Cisco-IOS-XE-platform-events-oper | swagger-events-model | 2 | 2 | 100.0% | 30.0 |
| 36 | Cisco-IOS-XE-platform-software-events | swagger-events-model | 2 | 1 | 100.0% | 30.0 |

## 🔵 LOW — 71 specs with minor gaps (score 10-29)

<details><summary>Click to expand</summary>

| Module | Paths | Tree C+L | Coverage | Score |
|--------|-------|----------|----------|-------|
| openconfig-acl | 38 | 55 | 69.1% | 29.7 |
| Cisco-IOS-XE-qfp-stats | 1 | 1 | 100.0% | 29.6 |
| Cisco-IOS-XE-wireless-geolocation-oper | 12 | 11 | 100.0% | 28.9 |
| ietf-key-chain | 10 | 17 | 58.8% | 28.8 |
| Cisco-IOS-XE-wireless-apf-cfg | 7 | 6 | 100.0% | 28.7 |
| Cisco-IOS-XE-ctrl-mng-cfg | 6 | 6 | 100.0% | 28.6 |
| Cisco-IOS-XE-wireless-rogue-oper | 31 | 52 | 59.6% | 28.3 |
| Cisco-IOS-XE-ip-sla-oper | 204 | 342 | 59.6% | 28.2 |
| cisco-policy-filters | 153 | 66 | 100.0% | 28.1 |
| Cisco-IOS-XE-appqoe-tcpproxy-oper | 3 | 5 | 60.0% | 28.0 |
| Cisco-IOS-XE-boot-integrity-oper | 3 | 5 | 60.0% | 28.0 |
| ietf-event-notifications | 25 | 29 | 86.2% | 28.0 |
| Cisco-IOS-XE-umbrella-oper-dp | 2 | 2 | 100.0% | 27.8 |
| CISCO-AAA-SERVER-MIB | 6 | 7 | 85.7% | 27.2 |
| CISCO-EMBEDDED-EVENT-MGR-MIB | 16 | 24 | 66.7% | 27.2 |
| Cisco-IOS-XE-l2nat-oper | 5 | 8 | 62.5% | 26.2 |
| Cisco-IOS-XE-lldp-oper | 10 | 16 | 62.5% | 26.2 |
| ietf-netconf-notifications | 8 | 8 | 100.0% | 25.0 |
| Cisco-IOS-XE-bfd-oper | 13 | 20 | 65.0% | 24.5 |
| Cisco-IOS-XE-wireless-afc-oper | 35 | 38 | 92.1% | 24.0 |
| ENTITY-STATE-MIB | 5 | 7 | 71.4% | 24.0 |
| Cisco-IOS-XE-l2vpn-oper | 31 | 47 | 66.0% | 23.8 |
| cisco-smart-license | 101 | 71 | 100.0% | 23.6 |
| Cisco-IOS-XE-ntp-oper | 8 | 12 | 66.7% | 23.3 |
| Cisco-IOS-XE-sslproxy-cfg | 2 | 3 | 66.7% | 23.3 |
| Cisco-IOS-XE-wireless-power-cfg | 8 | 12 | 66.7% | 23.3 |
| CISCO-SIP-UA-MIB | 46 | 29 | 100.0% | 23.2 |
| Cisco-IOS-XE-mrp-oper | 13 | 19 | 68.4% | 22.1 |
| Cisco-IOS-XE-wireless-wlan-cfg | 57 | 83 | 68.7% | 21.9 |
| Cisco-IOS-XE-stack-member-oper | 9 | 13 | 69.2% | 21.5 |
| Cisco-IOS-XE-bridge-oper | 5 | 7 | 71.4% | 20.0 |
| Cisco-IOS-XE-isis-intf-oper | 5 | 7 | 71.4% | 20.0 |
| openconfig-openflow | 17 | 12 | 100.0% | 19.4 |
| Cisco-IOS-XE-wireless-nmsp-oper | 11 | 15 | 73.3% | 18.7 |
| Cisco-IOS-XE-dre-oper | 39 | 53 | 73.6% | 18.5 |
| CISCO-IETF-ATM2-PVCTRAP-MIB | 5 | 6 | 83.3% | 17.7 |
| Cisco-IOS-XE-bgp-nbr-oper | 9 | 12 | 75.0% | 17.5 |
| Cisco-IOS-XE-fw-oper | 6 | 8 | 75.0% | 17.5 |
| Cisco-IOS-XE-mdt-oper-v2 | 15 | 20 | 75.0% | 17.5 |
| openconfig-if-ethernet | 3 | 4 | 75.0% | 17.5 |
| ietf-diffserv-policy | 9 | 12 | 75.0% | 17.5 |
| Cisco-IOS-XE-wireless-client-global-oper | 39 | 50 | 78.0% | 17.4 |
| CISCO-BGP4-MIB | 41 | 46 | 89.1% | 17.4 |
| cisco-bridge-domain | 194 | 49 | 100.0% | 17.4 |
| SNMPv2-MIB | 8 | 6 | 100.0% | 17.1 |
| Cisco-IOS-XE-controller-shdsl-oper | 21 | 15 | 100.0% | 16.8 |
| openconfig-routing-policy | 45 | 59 | 76.3% | 16.6 |
| Cisco-IOS-XE-dhcp-oper | 42 | 55 | 76.4% | 16.5 |
| Cisco-IOS-XE-wireless-rfid-global-oper | 10 | 13 | 76.9% | 16.2 |
| Cisco-IOS-XE-yang-interfaces-cfg | 17 | 22 | 77.3% | 15.9 |
| Cisco-IOS-XE-wireless-afc-cloud-oper | 7 | 9 | 77.8% | 15.6 |
| openconfig-platform | 32 | 41 | 78.0% | 15.4 |
| Cisco-IOS-XE-mdt-cfg | 27 | 34 | 79.4% | 14.4 |
| RFC1213-MIB | 48 | 23 | 100.0% | 13.5 |
| Cisco-IOS-XE-mroute-oper | 17 | 21 | 81.0% | 13.3 |
| Cisco-IOS-XE-wireless-access-point-oper | 222 | 274 | 81.0% | 13.3 |
| ietf-yang-library | 17 | 15 | 100.0% | 13.3 |
| Cisco-IOS-XE-wireless-ble-ltx-oper | 31 | 38 | 81.6% | 12.9 |
| CISCO-ATM-PVCTRAP-EXTN-MIB | 60 | 64 | 93.8% | 12.9 |
| Cisco-IOS-XE-crypto-oper | 190 | 232 | 81.9% | 12.7 |
| Cisco-IOS-XE-cdp-oper | 5 | 6 | 83.3% | 11.7 |
| openconfig-local-routing | 15 | 18 | 83.3% | 11.7 |
| CISCO-PING-MIB | 5 | 6 | 83.3% | 11.7 |
| CISCO-IETF-PW-ATM-MIB | 5 | 3 | 100.0% | 11.2 |
| openconfig-bfd | 16 | 19 | 84.2% | 11.1 |
| Cisco-IOS-XE-wireless-dot11-cfg | 22 | 26 | 84.6% | 10.8 |
| openconfig-interfaces | 11 | 13 | 84.6% | 10.8 |
| Cisco-IOS-XE-wireless-rrm-oper | 34 | 40 | 85.0% | 10.5 |
| ietf-diffserv-action | 23 | 27 | 85.2% | 10.4 |
| CISCO-UNIFIED-FIREWALL-MIB | 40 | 26 | 100.0% | 10.4 |
| Cisco-IOS-XE-yang-interfaces-oper | 6 | 7 | 85.7% | 10.0 |

</details>

## 🟢 GOOD — 400 specs well-modeled (score < 10)

These 400 specs have adequate path and schema coverage.

## ℹ️ Specs Without YANG Trees (48)

These specs have no corresponding YANG tree file and could not be audited.

| Module | Folder | Paths | Ops |
|--------|--------|-------|-----|
| openconfig-aaa | swagger-openconfig-model | 3 | 12 |
| openconfig-aft | swagger-openconfig-model | 7 | 28 |
| openconfig-bgp | swagger-openconfig-model | 4 | 16 |
| openconfig-evpn | swagger-openconfig-model | 11 | 40 |
| openconfig-igmp | swagger-openconfig-model | 2 | 8 |
| openconfig-isis | swagger-openconfig-model | 4 | 16 |
| openconfig-license | swagger-openconfig-model | 1 | 4 |
| openconfig-ospfv2 | swagger-openconfig-model | 8 | 26 |
| openconfig-packet-match | swagger-openconfig-model | 3 | 12 |
| openconfig-pcep | swagger-openconfig-model | 1 | 4 |
| openconfig-pim | swagger-openconfig-model | 2 | 8 |
| openconfig-policy-forwarding | swagger-openconfig-model | 1 | 4 |
| openconfig-procmon | swagger-openconfig-model | 8 | 28 |
| openconfig-rib-bgp | swagger-openconfig-model | 32 | 122 |
| openconfig-segment-routing | swagger-openconfig-model | 132 | 466 |
| openconfig-system-logging | swagger-openconfig-model | 1 | 4 |
| openconfig-system-terminal | swagger-openconfig-model | 3 | 12 |
| ietf-ipv4-unicast-routing | swagger-ietf-model | 8 | 28 |
| ietf-netconf-otlp-context | swagger-ietf-model | 1 | 4 |
| ietf-yang-structure-ext | swagger-ietf-model | 1 | 4 |
| native-00-top-level-containers | swagger-native-config-model | 5 | 20 |
| native-00-top-level-leafs | swagger-native-config-model | 8 | 29 |
| native-aaa | swagger-native-config-model | 4 | 16 |
| native-app-services | swagger-native-config-model | 7 | 28 |
| native-crypto | swagger-native-config-model | 5 | 20 |
| native-industrial-iot | swagger-native-config-model | 11 | 44 |
| native-intf-ethernet | swagger-native-config-model | 13 | 52 |
| native-intf-service | swagger-native-config-model | 15 | 60 |
| native-intf-virtual | swagger-native-config-model | 18 | 72 |
| native-intf-wan | swagger-native-config-model | 17 | 68 |
| native-ip | swagger-native-config-model | 10 | 40 |
| native-l2-discovery | swagger-native-config-model | 5 | 20 |
| native-line | swagger-native-config-model | 4 | 16 |
| native-misc-ext | swagger-native-config-model | 10 | 38 |
| native-other | swagger-native-config-model | 82 | 328 |
| native-platform-diag | swagger-native-config-model | 13 | 52 |
| native-platform-system | swagger-native-config-model | 16 | 64 |
| native-policy | swagger-native-config-model | 5 | 20 |
| native-protocols | swagger-native-config-model | 17 | 68 |
| native-qos-policy | swagger-native-config-model | 2 | 8 |
| native-router | swagger-native-config-model | 7 | 28 |
| native-routing-multicast | swagger-native-config-model | 8 | 32 |
| native-security-access | swagger-native-config-model | 16 | 64 |
| native-security-services | swagger-native-config-model | 7 | 28 |
| native-switching-l2 | swagger-native-config-model | 9 | 36 |
| native-vrf | swagger-native-config-model | 2 | 8 |
| native-wan-legacy | swagger-native-config-model | 12 | 48 |
| cisco-self-mgmt | swagger-other-model | 1 | 2 |

