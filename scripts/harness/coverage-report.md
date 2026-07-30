# RESTCONF Data Coverage Report

- **Device model (PID):** `C9300-24UX`
- **IOS XE version:** `26.1.1`
- **Generated:** 2026-07-30T22:54:01Z
- **Transport:** RESTCONF GET (read-only)

> **Platform note:** On IOS XE a GET of a parent container does not return all descendant data — many nodes only materialize on a direct GET of that container, and deeper still. Coverage below reflects per-container/depth scanning; a single root GET undercounts.

## Summary

| Category | Modules | With data | 0 data | Data paths | Lines | Data size |
|---|---:|---:|---:|---:|---:|---:|
| oper | 214 | 60 | 154 | 686 | 162,823 | 3.44 MB |
| mib | 147 | 62 | 85 | 62 | 39,766 | 1.08 MB |
| cfg | 40 | 4 | 36 | 19 | 594 | 0.01 MB |
| native-config | 408 | 57 | 351 | 257 | 9,577 | 0.11 MB |
| ietf | 21 | 9 | 12 | 37 | 35,206 | 0.94 MB |
| openconfig | 42 | 10 | 32 | 23 | 37,817 | 0.70 MB |
| other | 8 | 2 | 6 | 19 | 1,421 | 0.03 MB |
| **TOTAL** | **880** | **204** | **676** | **1103** | **287,204** | **6.32 MB** |

## oper

60 of 214 modules returned data (686 data paths, 3.44 MB).

### Modules WITH data

| Module | Data paths | Lines | Size |
|---|---:|---:|---:|
| `Cisco-IOS-XE-platform-software-oper` | 5 | 39,434 | 1,241,762 B |
| `Cisco-IOS-XE-process-cpu-oper` | 8 | 27,427 | 470,126 B |
| `Cisco-IOS-XE-fib-oper` | 79 | 17,975 | 323,142 B |
| `Cisco-IOS-XE-interfaces-oper` | 2 | 12,748 | 286,088 B |
| `Cisco-IOS-XE-process-memory-oper` | 2 | 12,460 | 206,165 B |
| `Cisco-IOS-XE-switch-dp-resources-oper` | 2 | 9,358 | 133,145 B |
| `Cisco-IOS-XE-acl-oper` | 2 | 9,512 | 100,910 B |
| `Cisco-IOS-XE-platform-oper` | 2 | 5,800 | 94,535 B |
| `Cisco-IOS-XE-install-oper` | 2 | 2,250 | 57,150 B |
| `Cisco-IOS-XE-mlppp-oper` | 21 | 2,176 | 53,917 B |
| `Cisco-IOS-XE-spanning-tree-oper` | 30 | 2,519 | 53,154 B |
| `Cisco-IOS-XE-crypto-pki-oper` | 15 | 1,824 | 45,905 B |
| `Cisco-IOS-XE-mdt-capabilities-oper` | 8 | 2,040 | 37,042 B |
| `Cisco-IOS-XE-switchport-oper` | 2 | 2,316 | 34,440 B |
| `Cisco-IOS-XE-device-hardware-oper` | 18 | 1,181 | 28,977 B |
| `Cisco-IOS-XE-cdp-oper` | 2 | 836 | 23,333 B |
| `Cisco-IOS-XE-crypto-oper` | 73 | 1,352 | 22,745 B |
| `Cisco-IOS-XE-boot-integrity-oper` | 15 | 211 | 20,404 B |
| `Cisco-IOS-XE-mka-oper` | 19 | 906 | 19,538 B |
| `Cisco-IOS-XE-transceiver-oper` | 2 | 886 | 18,287 B |
| `Cisco-IOS-XE-poe-oper` | 5 | 696 | 17,625 B |
| `Cisco-IOS-XE-matm-oper` | 2 | 920 | 15,711 B |
| `Cisco-IOS-XE-macsec-oper` | 2 | 730 | 14,046 B |
| `Cisco-IOS-XE-switch-dp-punt-inject-oper` | 2 | 668 | 13,056 B |
| `Cisco-IOS-XE-mdt-oper-v2` | 9 | 551 | 12,561 B |
| `Cisco-IOS-XE-matm-state-oper` | 2 | 748 | 10,041 B |
| `Cisco-IOS-XE-bgp-oper` | 5 | 833 | 8,815 B |
| `Cisco-IOS-XE-aaa-oper` | 70 | 380 | 8,150 B |
| `Cisco-IOS-XE-identity-oper` | 73 | 563 | 7,360 B |
| `Cisco-IOS-XE-gir-oper` | 45 | 308 | 6,512 B |
| `Cisco-IOS-XE-environment-oper` | 8 | 265 | 5,569 B |
| `Cisco-IOS-XE-arp-oper` | 2 | 230 | 5,341 B |
| `Cisco-IOS-XE-system-security-oper` | 2 | 250 | 4,841 B |
| `Cisco-IOS-XE-vlan-oper` | 2 | 316 | 4,391 B |
| `Cisco-IOS-XE-mdt-stats-oper` | 3 | 292 | 4,223 B |
| `Cisco-IOS-XE-ntp-oper` | 11 | 226 | 4,089 B |
| `Cisco-IOS-XE-eem-oper` | 2 | 172 | 3,773 B |
| `Cisco-IOS-XE-yang-interfaces-oper` | 31 | 203 | 3,539 B |
| `Cisco-IOS-XE-stack-oper` | 8 | 155 | 3,197 B |
| `Cisco-IOS-XE-ip-arp-oper` | 2 | 130 | 2,886 B |
| `Cisco-IOS-XE-stack-member-oper` | 2 | 144 | 2,447 B |
| `Cisco-IOS-XE-switch-ptp-oper` | 3 | 108 | 2,397 B |
| `Cisco-IOS-XE-ppp-oper` | 18 | 108 | 1,527 B |
| `Cisco-IOS-XE-ha-oper` | 12 | 60 | 1,198 B |
| `Cisco-IOS-XE-memory-oper` | 2 | 58 | 1,053 B |
| `Cisco-IOS-XE-switch-dp-mac-learning-oper` | 2 | 58 | 958 B |
| `Cisco-IOS-XE-trustsec-oper` | 9 | 44 | 914 B |
| `Cisco-IOS-XE-rib-oper` | 3 | 80 | 897 B |
| `Cisco-IOS-XE-gnss-oper` | 2 | 32 | 808 B |
| `Cisco-IOS-XE-bfd-oper` | 9 | 45 | 797 B |
| `Cisco-IOS-XE-dns-oper` | 2 | 38 | 499 B |
| `Cisco-IOS-XE-dhcp-oper` | 6 | 30 | 456 B |
| `Cisco-IOS-XE-vrf-oper` | 2 | 38 | 415 B |
| `Cisco-IOS-XE-ipv6-nd-oper` | 2 | 26 | 321 B |
| `Cisco-IOS-XE-netconf-diag-oper` | 4 | 20 | 320 B |
| `Cisco-IOS-XE-checkpoint-archive-oper` | 4 | 16 | 251 B |
| `Cisco-IOS-XE-switch-cp-svl-oper` | 2 | 24 | 251 B |
| `Cisco-IOS-XE-switch-ptp-dp-oper` | 2 | 24 | 251 B |
| `Cisco-IOS-XE-ospf-oper` | 3 | 15 | 235 B |
| `Cisco-IOS-XE-l2vpn-oper` | 2 | 8 | 113 B |

### Modules with 0 data (154)

- **not present (404)** (107): `Cisco-IOS-XE-app-cflowd-oper`, `Cisco-IOS-XE-appqoe-http-oper`, `Cisco-IOS-XE-appqoe-oper`, `Cisco-IOS-XE-appqoe-serv-oper`, `Cisco-IOS-XE-appqoe-sslproxy-oper`, `Cisco-IOS-XE-appqoe-tcpproxy-oper`, `Cisco-IOS-XE-bbu-oper`, `Cisco-IOS-XE-bridge-oper`, `Cisco-IOS-XE-controller-shdsl-oper`, `Cisco-IOS-XE-controller-t1e1-oper`, `Cisco-IOS-XE-controller-vdsl-oper`, `Cisco-IOS-XE-diffserv-target-oper`, `Cisco-IOS-XE-digital-io-oper`, `Cisco-IOS-XE-dlr-oper`, `Cisco-IOS-XE-dns-defense-oper`, `Cisco-IOS-XE-dre-cp-oper`, `Cisco-IOS-XE-dre-oper`, `Cisco-IOS-XE-embedded-ap-oper`, `Cisco-IOS-XE-endpoint-tracker-oper`, `Cisco-IOS-XE-eogre-tunnel-oper`, `Cisco-IOS-XE-fw-oper`, `Cisco-IOS-XE-geo-oper`, `Cisco-IOS-XE-gnss-dr-oper`, `Cisco-IOS-XE-hsr-oper`, `Cisco-IOS-XE-iad-oper`, `Cisco-IOS-XE-ignition-oper`, `Cisco-IOS-XE-im-events-oper`, `Cisco-IOS-XE-ios-events-oper`, `Cisco-IOS-XE-isdn-oper`, `Cisco-IOS-XE-l2nat-oper`, `Cisco-IOS-XE-line-oper`, `Cisco-IOS-XE-lorawan-oper`, `Cisco-IOS-XE-lte450-oper`, `Cisco-IOS-XE-mdt-oper`, `Cisco-IOS-XE-mrp-oper`, `Cisco-IOS-XE-nwpi-oper`, `Cisco-IOS-XE-omp-oper`, `Cisco-IOS-XE-platform-events-oper`, `Cisco-IOS-XE-policymap-target-oper`, `Cisco-IOS-XE-prp-oper`, `Cisco-IOS-XE-qfp-appqoe-dp-oper`, `Cisco-IOS-XE-qfp-classification-oper`, `Cisco-IOS-XE-qfp-crypto-dp-oper`, `Cisco-IOS-XE-qfp-dp-cmn-stats-oper`, `Cisco-IOS-XE-qfp-resource-utilization-oper`, `Cisco-IOS-XE-qfp-stats-oper`, `Cisco-IOS-XE-rawsocket-oper`, `Cisco-IOS-XE-rg-oper`, `Cisco-IOS-XE-rif-oper`, `Cisco-IOS-XE-scada-gw-oper`, `Cisco-IOS-XE-sd-vxlan-oper`, `Cisco-IOS-XE-sdwan-aaa-oper`, `Cisco-IOS-XE-sdwan-ipsec-oper`, `Cisco-IOS-XE-sdwan-oper`, `Cisco-IOS-XE-service-chain-oper`, `Cisco-IOS-XE-service-insertion-oper`, `Cisco-IOS-XE-sm-events-oper`, `Cisco-IOS-XE-sr-oper`, `Cisco-IOS-XE-sse-oper`, `Cisco-IOS-XE-stack-info-oper`, `Cisco-IOS-XE-stack-mgr-events-oper`, `Cisco-IOS-XE-stacking-oper`, `Cisco-IOS-XE-tcam-oper`, `Cisco-IOS-XE-teyes-oper`, `Cisco-IOS-XE-ucse-oper`, `Cisco-IOS-XE-uidp-oper`, `Cisco-IOS-XE-umbrella-oper-dp`, `Cisco-IOS-XE-uplink-autoconfig-oper`, `Cisco-IOS-XE-vdsp-oper`, `Cisco-IOS-XE-voice-oper`, `Cisco-IOS-XE-wireless-access-point-oper`, `Cisco-IOS-XE-wireless-afc-cloud-oper`, `Cisco-IOS-XE-wireless-afc-oper`, `Cisco-IOS-XE-wireless-ap-global-oper`, `Cisco-IOS-XE-wireless-awips-oper`, `Cisco-IOS-XE-wireless-ble-ltx-oper`, `Cisco-IOS-XE-wireless-ble-mgmt-oper`, `Cisco-IOS-XE-wireless-cisco-spaces-oper`, `Cisco-IOS-XE-wireless-client-global-oper`, `Cisco-IOS-XE-wireless-client-oper`, `Cisco-IOS-XE-wireless-cts-sxp-oper`, `Cisco-IOS-XE-wireless-events-oper`, `Cisco-IOS-XE-wireless-general-oper`, `Cisco-IOS-XE-wireless-geolocation-oper`, `Cisco-IOS-XE-wireless-hyperlocation-oper`, `Cisco-IOS-XE-wireless-lisp-agent-oper`, `Cisco-IOS-XE-wireless-location-oper`, `Cisco-IOS-XE-wireless-mcast-oper`, `Cisco-IOS-XE-wireless-mdns-oper`, `Cisco-IOS-XE-wireless-mesh-global-oper`, `Cisco-IOS-XE-wireless-mesh-oper`, `Cisco-IOS-XE-wireless-mobility-oper`, `Cisco-IOS-XE-wireless-nmsp-oper`, `Cisco-IOS-XE-wireless-rfid-global-oper`, `Cisco-IOS-XE-wireless-rfid-oper`, `Cisco-IOS-XE-wireless-rogue-oper`, `Cisco-IOS-XE-wireless-rrm-emul-oper`, `Cisco-IOS-XE-wireless-rrm-global-oper`, `Cisco-IOS-XE-wireless-rrm-oper`, `Cisco-IOS-XE-wireless-rule-mdns-oper`, `Cisco-IOS-XE-wireless-sdavc-oper`, `Cisco-IOS-XE-wireless-sisf-global-oper`, `Cisco-IOS-XE-wireless-tunnel-oper`, `Cisco-IOS-XE-wireless-urwb-oper`, `Cisco-IOS-XE-wireless-urwbnet-oper`, `Cisco-IOS-XE-wireless-wlan-global-oper`, `Cisco-IOS-XE-wpan-oper`
- **empty (204)** (46): `Cisco-IOS-XE-app-hosting-oper`, `Cisco-IOS-XE-aws-cw-oper`, `Cisco-IOS-XE-aws-s3-oper`, `Cisco-IOS-XE-bgp-nbr-oper`, `Cisco-IOS-XE-bgp-rib-oper`, `Cisco-IOS-XE-breakout-port-oper`, `Cisco-IOS-XE-cable-diag-oper`, `Cisco-IOS-XE-cellwan-oper`, `Cisco-IOS-XE-cfm-oper`, `Cisco-IOS-XE-dhcp-security-track-server-oper`, `Cisco-IOS-XE-efp-oper`, `Cisco-IOS-XE-eigrp-oper`, `Cisco-IOS-XE-evpn-oper`, `Cisco-IOS-XE-flow-monitor-oper`, `Cisco-IOS-XE-fwd-oper`, `Cisco-IOS-XE-group-policy-oper`, `Cisco-IOS-XE-hsrp-oper`, `Cisco-IOS-XE-ip-sla-oper`, `Cisco-IOS-XE-ipv6-oper`, `Cisco-IOS-XE-isis-intf-oper`, `Cisco-IOS-XE-isis-oper`, `Cisco-IOS-XE-l2tp-oper`, `Cisco-IOS-XE-lacp-oper`, `Cisco-IOS-XE-linecard-oper`, `Cisco-IOS-XE-lisp-oper`, `Cisco-IOS-XE-livetools-oper`, `Cisco-IOS-XE-meraki-connect-oper`, `Cisco-IOS-XE-mpls-forwarding-oper`, `Cisco-IOS-XE-mpls-ldp-oper`, `Cisco-IOS-XE-mpls-te-oper`, `Cisco-IOS-XE-mroute-oper`, `Cisco-IOS-XE-msdp-oper`, `Cisco-IOS-XE-nat-oper`, `Cisco-IOS-XE-ncch-oper`, `Cisco-IOS-XE-nve-oper`, `Cisco-IOS-XE-perf-measure-oper`, `Cisco-IOS-XE-pim-oper`, `Cisco-IOS-XE-poe-health-oper`, `Cisco-IOS-XE-psecure-oper`, `Cisco-IOS-XE-steering-policy-oper`, `Cisco-IOS-XE-system-integrity-oper`, `Cisco-IOS-XE-tunnel-oper`, `Cisco-IOS-XE-udld-oper`, `Cisco-IOS-XE-umbrella-oper`, `Cisco-IOS-XE-utd-oper`, `Cisco-IOS-XE-vrrp-oper`
- **other** (1): `Cisco-IOS-XE-cloud-services-oper`

## mib

62 of 147 modules returned data (62 data paths, 1.08 MB).

### Modules WITH data

| Module | Data paths | Lines | Size |
|---|---:|---:|---:|
| `CISCO-PROCESS-MIB` | 1 | 11,550 | 346,305 B |
| `CISCO-FLASH-MIB` | 1 | 3,502 | 101,136 B |
| `CISCO-VTP-MIB` | 1 | 1,423 | 82,600 B |
| `IP-MIB` | 1 | 3,440 | 66,139 B |
| `IF-MIB` | 1 | 3,107 | 65,560 B |
| `CISCO-CEF-MIB` | 1 | 2,287 | 54,823 B |
| `EtherLike-MIB` | 1 | 1,567 | 40,713 B |
| `CISCO-STP-EXTENSIONS-MIB` | 1 | 1,732 | 40,298 B |
| `ENTITY-MIB` | 1 | 1,524 | 39,523 B |
| `CISCO-IF-EXTENSION-MIB` | 1 | 1,904 | 39,043 B |
| `POWER-ETHERNET-MIB` | 1 | 770 | 35,058 B |
| `SNMPv2-MIB` | 1 | 719 | 32,905 B |
| `RFC1213-MIB` | 1 | 1,304 | 25,930 B |
| `CISCO-ENHANCED-MEMPOOL-MIB` | 1 | 632 | 15,889 B |
| `CISCO-CDP-MIB` | 1 | 490 | 13,855 B |
| `CISCO-VLAN-MEMBERSHIP-MIB` | 1 | 471 | 12,750 B |
| `LLDP-MIB` | 1 | 407 | 10,949 B |
| `BRIDGE-MIB` | 1 | 412 | 9,028 B |
| `CISCO-NTP-MIB` | 1 | 200 | 4,894 B |
| `UDP-MIB` | 1 | 196 | 4,530 B |
| `CISCO-NBAR-PROTOCOL-DISCOVERY-MIB` | 1 | 311 | 4,205 B |
| `CISCO-ENTITY-SENSOR-MIB` | 1 | 126 | 3,270 B |
| `CISCO-CONFIG-MAN-MIB` | 1 | 92 | 2,995 B |
| `CISCO-ETHERLIKE-EXT-MIB` | 1 | 173 | 2,975 B |
| `CISCO-IGMP-FILTER-MIB` | 1 | 187 | 2,863 B |
| `DIFFSERV-MIB` | 1 | 227 | 2,735 B |
| `CISCO-IPSEC-FLOW-MONITOR-MIB` | 1 | 89 | 2,567 B |
| `CISCO-ENVMON-MIB` | 1 | 78 | 2,180 B |
| `CISCO-STACKWISE-MIB` | 1 | 86 | 2,046 B |
| `CISCO-RF-MIB` | 1 | 63 | 1,567 B |
| `IP-FORWARD-MIB` | 1 | 65 | 1,459 B |
| `MPLS-VPN-MIB` | 1 | 48 | 1,285 B |
| `CISCO-AAA-SERVER-MIB` | 1 | 49 | 1,184 B |
| `CISCO-IMAGE-MIB` | 1 | 40 | 948 B |
| `CISCO-POWER-ETHERNET-EXT-MIB` | 1 | 51 | 919 B |
| `CISCO-ENTITY-FRU-CONTROL-MIB` | 1 | 52 | 886 B |
| `CISCO-IPSEC-MIB` | 1 | 35 | 853 B |
| `TCP-MIB` | 1 | 44 | 805 B |
| `CISCO-SYSLOG-MIB` | 1 | 27 | 727 B |
| `CISCO-DATA-COLLECTION-MIB` | 1 | 22 | 432 B |
| `RMON2-MIB` | 1 | 16 | 392 B |
| `CISCO-BULK-FILE-MIB` | 1 | 20 | 376 B |
| `CISCO-VLAN-IFTABLE-RELATIONSHIP-MIB` | 1 | 23 | 358 B |
| `CISCO-PIM-MIB` | 1 | 15 | 326 B |
| `CISCO-ENTITY-QFP-MIB` | 1 | 14 | 323 B |
| `CISCO-IETF-ISIS-MIB` | 1 | 15 | 312 B |
| `DISMAN-EXPRESSION-MIB` | 1 | 11 | 278 B |
| `PIM-MIB` | 1 | 18 | 267 B |
| `CISCO-IP-URPF-MIB` | 1 | 18 | 265 B |
| `NOTIFICATION-LOG-MIB` | 1 | 12 | 219 B |
| `SNMP-FRAMEWORK-MIB` | 1 | 10 | 177 B |
| `CISCO-IETF-BFD-MIB` | 1 | 9 | 175 B |
| `CISCO-FTP-CLIENT-MIB` | 1 | 10 | 151 B |
| `DRAFT-MSDP-MIB` | 1 | 10 | 151 B |
| `SNMP-TARGET-MIB` | 1 | 9 | 146 B |
| `OSPF-MIB` | 1 | 9 | 130 B |
| `IPMROUTE-STD-MIB` | 1 | 8 | 108 B |
| `BGP4-MIB` | 1 | 9 | 99 B |
| `CISCO-IPMROUTE-MIB` | 1 | 7 | 97 B |
| `CISCO-HSRP-MIB` | 1 | 7 | 83 B |
| `CISCO-BGP4-MIB` | 1 | 7 | 69 B |
| `NHRP-MIB` | 1 | 7 | 67 B |

### Modules with 0 data (85)

- **not present (404)** (33): `ATM-MIB`, `CISCO-ATM-PVCTRAP-EXTN-MIB`, `CISCO-ATM-QOS-MIB`, `CISCO-DIAL-CONTROL-MIB`, `CISCO-IETF-ATM2-PVCTRAP-MIB`, `CISCO-IETF-ATM2-PVCTRAP-MIB-EXTN`, `CISCO-IETF-FRR-MIB`, `CISCO-IETF-MPLS-ID-STD-03-MIB`, `CISCO-IETF-MPLS-TE-EXT-STD-03-MIB`, `CISCO-IETF-PW-ATM-MIB`, `CISCO-IETF-PW-ENET-MIB`, `CISCO-IETF-PW-MIB`, `CISCO-IETF-PW-MPLS-MIB`, `CISCO-IETF-PW-TDM-MIB`, `CISCO-MPLS-LSR-EXT-STD-MIB`, `CISCO-SESS-BORDER-CTRLR-CALL-STATS-MIB`, `CISCO-SESS-BORDER-CTRLR-STATS-MIB`, `CISCO-SONET-MIB`, `CISCO-SUBSCRIBER-SESSION-MIB`, `CISCO-VOICE-COMMON-DIAL-CONTROL-MIB`, `CISCO-VOICE-DIAL-CONTROL-MIB`, `CISCO-VOICE-DNIS-MIB`, `DIAL-CONTROL-MIB`, `DS1-MIB`, `DS3-MIB`, `FRAME-RELAY-DTE-MIB`, `MPLS-L3VPN-STD-MIB`, `MPLS-LDP-GENERIC-STD-MIB`, `MPLS-LDP-STD-MIB`, `MPLS-LSR-STD-MIB`, `MPLS-TE-STD-MIB`, `RSVP-MIB`, `SONET-MIB`
- **empty (204)** (51): `CISCO-AAA-SESSION-MIB`, `CISCO-BGP-POLICY-ACCOUNTING-MIB`, `CISCO-CBP-TARGET-MIB`, `CISCO-CONFIG-COPY-MIB`, `CISCO-CONTEXT-MAPPING-MIB`, `CISCO-DOT3-OAM-MIB`, `CISCO-DYNAMIC-TEMPLATE-MIB`, `CISCO-EIGRP-MIB`, `CISCO-EMBEDDED-EVENT-MGR-MIB`, `CISCO-ENTITY-ALARM-MIB`, `CISCO-ENTITY-EXT-MIB`, `CISCO-ETHER-CFM-MIB`, `CISCO-HSRP-EXT-MIB`, `CISCO-IMAGE-LICENSE-MGMT-MIB`, `CISCO-IP-LOCAL-POOL-MIB`, `CISCO-IP-TAP-MIB`, `CISCO-IPSEC-POLICY-MAP-MIB`, `CISCO-IPSLA-AUTOMEASURE-MIB`, `CISCO-IPSLA-ECHO-MIB`, `CISCO-IPSLA-JITTER-MIB`, `CISCO-LICENSE-MGMT-MIB`, `CISCO-MEDIA-GATEWAY-MIB`, `CISCO-NETSYNC-MIB`, `CISCO-OSPF-MIB`, `CISCO-OSPF-TRAP-MIB`, `CISCO-PING-MIB`, `CISCO-PTP-MIB`, `CISCO-QOS-PIB-MIB`, `CISCO-RADIUS-EXT-MIB`, `CISCO-SIP-UA-MIB`, `CISCO-TAP2-MIB`, `CISCO-UBE-MIB`, `CISCO-UNIFIED-FIREWALL-MIB`, `CISCO-VPDN-MGMT-MIB`, `DISMAN-EVENT-MIB`, `ENTITY-SENSOR-MIB`, `ENTITY-STATE-MIB`, `ETHER-WIS`, `EXPRESSION-MIB`, `IGMP-STD-MIB`, `INT-SERV-MIB`, `INTEGRATED-SERVICES-MIB`, `OSPF-TRAP-MIB`, `P-BRIDGE-MIB`, `Q-BRIDGE-MIB`, `RFC1315-MIB`, `RMON-MIB`, `SNMP-PROXY-MIB`, `TOKEN-RING-RMON-MIB`, `TOKENRING-MIB`, `TUNNEL-MIB`
- **error** (1): `CISCO-RTTMON-MIB`

## cfg

4 of 40 modules returned data (19 data paths, 0.01 MB).

### Modules WITH data

| Module | Data paths | Lines | Size |
|---|---:|---:|---:|
| `Cisco-IOS-XE-mdt-cfg` | 5 | 527 | 8,276 B |
| `Cisco-IOS-XE-gnmi-cfg` | 8 | 40 | 714 B |
| `Cisco-IOS-XE-yang-interfaces-cfg` | 4 | 19 | 332 B |
| `Cisco-IOS-XE-cloud-services-cfg` | 2 | 8 | 135 B |

### Modules with 0 data (36)

- **not present (404)** (31): `Cisco-IOS-XE-ctrl-mng-cfg`, `Cisco-IOS-XE-sslproxy-cfg`, `Cisco-IOS-XE-wireless-access-point-cfg-rpc`, `Cisco-IOS-XE-wireless-ap-cfg`, `Cisco-IOS-XE-wireless-apf-cfg`, `Cisco-IOS-XE-wireless-cts-sxp-cfg`, `Cisco-IOS-XE-wireless-dot11-cfg`, `Cisco-IOS-XE-wireless-dot15-cfg`, `Cisco-IOS-XE-wireless-fabric-cfg`, `Cisco-IOS-XE-wireless-flex-cfg`, `Cisco-IOS-XE-wireless-fqdn-cfg`, `Cisco-IOS-XE-wireless-general-cfg`, `Cisco-IOS-XE-wireless-hotspot-cfg`, `Cisco-IOS-XE-wireless-location-cfg`, `Cisco-IOS-XE-wireless-mesh-cfg`, `Cisco-IOS-XE-wireless-mobility-cfg`, `Cisco-IOS-XE-wireless-mstream-cfg`, `Cisco-IOS-XE-wireless-power-cfg`, `Cisco-IOS-XE-wireless-radio-cfg`, `Cisco-IOS-XE-wireless-rf-cfg`, `Cisco-IOS-XE-wireless-rfid-cfg`, `Cisco-IOS-XE-wireless-rlan-cfg`, `Cisco-IOS-XE-wireless-rogue-cfg`, `Cisco-IOS-XE-wireless-rrm-cfg`, `Cisco-IOS-XE-wireless-rule-cfg`, `Cisco-IOS-XE-wireless-security-cfg`, `Cisco-IOS-XE-wireless-site-cfg`, `Cisco-IOS-XE-wireless-tunnel-cfg`, `Cisco-IOS-XE-wireless-urwb-cfg`, `Cisco-IOS-XE-wireless-wat-cfg`, `Cisco-IOS-XE-wireless-wlan-cfg`
- **empty (204)** (5): `Cisco-IOS-XE-app-hosting-cfg`, `Cisco-IOS-XE-aws-cw-cfg`, `Cisco-IOS-XE-aws-s3-cfg`, `Cisco-IOS-XE-grpc-tunnel-cfg`, `Cisco-IOS-XE-ncch-cfg`

## native-config

57 of 408 modules returned data (257 data paths, 0.11 MB).

### Modules WITH data

| Module | Data paths | Lines | Size |
|---|---:|---:|---:|
| `native-aug-ip-1` | 42 | 2,956 | 35,698 B |
| `native-services` | 28 | 1,784 | 20,729 B |
| `native-services-2` | 10 | 1,506 | 18,065 B |
| `native-interfaces` | 3 | 628 | 6,188 B |
| `native-qos` | 1 | 196 | 3,610 B |
| `native-aug-policy` | 2 | 196 | 3,578 B |
| `native-aug-line` | 3 | 310 | 2,996 B |
| `native-aug-crypto-1` | 6 | 144 | 1,879 B |
| `native-aug-event` | 2 | 166 | 1,677 B |
| `native-aug-ipv6` | 17 | 166 | 1,675 B |
| `native-services-1` | 9 | 166 | 1,632 B |
| `native-switching` | 15 | 157 | 1,416 B |
| `native-aug-call-home` | 14 | 74 | 1,078 B |
| `native-services-3` | 9 | 112 | 1,032 B |
| `native-crypto` | 1 | 68 | 937 B |
| `native-aaa` | 3 | 73 | 753 B |
| `native-aug-logging` | 6 | 56 | 631 B |
| `native-cli` | 2 | 26 | 597 B |
| `native-aug-aaa` | 6 | 76 | 504 B |
| `native-snmp` | 2 | 36 | 461 B |
| `native-logging` | 2 | 43 | 448 B |
| `native-aug-ntp` | 6 | 46 | 384 B |
| `native-aug-transceivers` | 5 | 45 | 367 B |
| `native-aug-snmp-server` | 4 | 30 | 363 B |
| `native-aug-interface-6` | 1 | 40 | 362 B |
| `native-license` | 1 | 23 | 360 B |
| `native-00-day0` | 4 | 34 | 337 B |
| `native-aug-template-1` | 1 | 22 | 284 B |
| `native-aug-license` | 3 | 27 | 273 B |
| `native-aug-interface-1` | 1 | 31 | 269 B |
| `native-aug-tacacs-server` | 5 | 18 | 216 B |
| `native-aug-spanning-tree` | 4 | 20 | 208 B |
| `native-identity` | 2 | 22 | 202 B |
| `native-monitor` | 1 | 13 | 199 B |
| `native-ntp` | 1 | 21 | 197 B |
| `native-aug-tacacs` | 2 | 22 | 190 B |
| `native-aug-service` | 4 | 24 | 172 B |
| `native-aug-username` | 1 | 14 | 167 B |
| `native-aug-snmp` | 3 | 21 | 148 B |
| `native-00-interface-basics` | 1 | 19 | 141 B |
| `native-login` | 3 | 15 | 136 B |
| `native-diagnostic` | 2 | 12 | 130 B |
| `native-arp` | 1 | 12 | 125 B |
| `native-aug-control-plane` | 2 | 8 | 120 B |
| `native-aug-vlan` | 1 | 17 | 111 B |
| `native-aug-vrf` | 1 | 11 | 102 B |
| `native-aug-arp` | 1 | 10 | 99 B |
| `native-00-core` | 2 | 6 | 89 B |
| `native-ha` | 2 | 8 | 86 B |
| `native-platform` | 1 | 8 | 74 B |
| `native-switch` | 1 | 8 | 74 B |
| `native-aug-vtp` | 2 | 8 | 72 B |
| `native-aug-diagnostic` | 1 | 3 | 45 B |
| `native-lldp` | 1 | 7 | 43 B |
| `native-aug-archive` | 1 | 5 | 38 B |
| `native-aug-clock` | 1 | 3 | 35 B |
| `native-aug-lldp` | 1 | 5 | 33 B |

### Modules with 0 data (351)

- **not present (404)** (220): `native-alarm`, `native-alarm-profile`, `native-app-hosting`, `native-application`, `native-aug-access-list`, `native-aug-alarm`, `native-aug-alarm-contact`, `native-aug-alarm-profile`, `native-aug-alias`, `native-aug-app-hosting`, `native-aug-application`, `native-aug-auto`, `native-aug-autoconf`, `native-aug-avb`, `native-aug-avc`, `native-aug-bba-group`, `native-aug-bridge`, `native-aug-bridge-domain`, `native-aug-call`, `native-aug-call-manager-fallback`, `native-aug-card`, `native-aug-ccm-manager`, `native-aug-cef`, `native-aug-cip`, `native-aug-coap`, `native-aug-codec`, `native-aug-control-plane-host`, `native-aug-controller`, `native-aug-credentials`, `native-aug-cwmp`, `native-aug-dapr`, `native-aug-device`, `native-aug-device-sensor`, `native-aug-dial-peer`, `native-aug-dialer`, `native-aug-dialer-list`, `native-aug-dlr`, `native-aug-domain`, `native-aug-dsapp`, `native-aug-dspfarm`, `native-aug-dying-gasp`, `native-aug-energywise`, `native-aug-esmc`, `native-aug-esmc-synce`, `native-aug-et-analytics`, `native-aug-ethernet-internal`, `native-aug-feature`, `native-aug-frame-relay`, `native-aug-gateway`, `native-aug-geo`, `native-aug-gnss`, `native-aug-gw-accounting`, `native-aug-hsr-hsr-mode`, `native-aug-hsr-prp-mode`, `native-aug-hsr-ring`, `native-aug-http`, `native-aug-hw-module`, `native-aug-hw-switch`, `native-aug-ida`, `native-aug-identity`, `native-aug-irig`, `native-aug-isdn`, `native-aug-kron`, `native-aug-l2nat`, `native-aug-l2protocol-tunnel`, `native-aug-l2tp-class`, `native-aug-l2vpn-config`, `native-aug-l3nat-iox`, `native-aug-login`, `native-aug-mac-address-table`, `native-aug-maintenance-template`, `native-aug-management`, `native-aug-md-list`, `native-aug-mdns-sd`, `native-aug-media`, `native-aug-mgmt-traffic`, `native-aug-module`, `native-aug-mrp`, `native-aug-multilink`, `native-aug-named-ordering-route-map`, `native-aug-nat64`, `native-aug-nat66`, `native-aug-network-clock`, `native-aug-network-policy`, `native-aug-nhrp`, `native-aug-num-exp`, `native-aug-openflow`, `native-aug-otv`, `native-aug-password`, `native-aug-performance-measurement`, `native-aug-pfr`, `native-aug-pfr-map`, `native-aug-pm-agent`, `native-aug-pnp`, `native-aug-power`, `native-aug-profinet`, `native-aug-prp`, `native-aug-pseudowire-class`, `native-aug-qos-overhead-accounting`, `native-aug-redun-management`, `native-aug-redundancy`, `native-aug-relay`, `native-aug-rep`, `native-aug-rmon`, `native-aug-route-map`, `native-aug-route-tag`, `native-aug-router-1`, `native-aug-router-2`, `native-aug-sampler`, `native-aug-scada`, `native-aug-scada-gw`, `native-aug-sccp-config`, `native-aug-sdm`, `native-aug-security`, `native-aug-segment-routing`, `native-aug-service-chain`, `native-aug-service-export`, `native-aug-service-group`, `native-aug-service-list`, `native-aug-service-template`, `native-aug-setup`, `native-aug-shell`, `native-aug-sip-ua`, `native-aug-site-manager`, `native-aug-stack-mac`, `native-aug-stack-power`, `native-aug-stackwise-virtual`, `native-aug-statistics`, `native-aug-stcapp-config`, `native-aug-switch`, `native-aug-switch-global-config`, `native-aug-switch-virtual`, `native-aug-table-map`, `native-aug-tftp-server-config`, `native-aug-time-range`, `native-aug-tod-clock`, `native-aug-transport-map`, `native-aug-trunk`, `native-aug-uc`, `native-aug-ucse`, `native-aug-uplink`, `native-aug-utd`, `native-aug-utd-mt`, `native-aug-utd-st`, `native-aug-virtual-service`, `native-aug-voice`, `native-aug-voice-card`, `native-aug-voice-card-sb`, `native-aug-voice-port`, `native-aug-vpdn`, `native-aug-vstack`, `native-aug-vxlan`, `native-aug-xconnect`, `native-aug-zone`, `native-aug-zone-pair`, `native-bba-group`, `native-call`, `native-call-manager-fallback`, `native-ccm-manager`, `native-cip`, `native-codec`, `native-credentials`, `native-dapr`, `native-dial-peer`, `native-dlr`, `native-dsapp`, `native-dspfarm`, `native-dying-gasp`, `native-esmc`, `native-esmc-synce`, `native-et-analytics`, `native-ethernet-internal`, `native-fabric-group`, `native-gateway`, `native-geo`, `native-gnss`, `native-gw-accounting`, `native-hsr-hsr-mode`, `native-hsr-prp-mode`, `native-hsr-ring`, `native-http`, `native-ida`, `native-irig`, `native-isdn`, `native-l2nat`, `native-l3nat-iox`, `native-media`, `native-mrp`, `native-nat64`, `native-nat66`, `native-num-exp`, `native-pm-agent`, `native-profinet`, `native-prp`, `native-relay`, `native-scada`, `native-scada-gw`, `native-sccp`, `native-sccp-config`, `native-security`, `native-sip-ua`, `native-site-manager`, `native-statistics`, `native-stcapp`, `native-stcapp-config`, `native-switch-virtual`, `native-trunk`, `native-uc`, `native-ucse`, `native-utd`, `native-utd-mt`, `native-utd-st`, `native-utd-unified-policy`, `native-voice`, `native-voice-card`, `native-voice-card-sb`, `native-voice-port`, `native-vpdn`, `native-vpn`, `native-wireless`
- **empty (204)** (131): `native-00-routing-basics`, `native-access-list`, `native-access-session`, `native-aug-access-session`, `native-aug-authentication`, `native-aug-banner`, `native-aug-bfd`, `native-aug-bfd-template`, `native-aug-boot`, `native-aug-buffers`, `native-aug-cdp`, `native-aug-clns`, `native-aug-crypto-2`, `native-aug-cts`, `native-aug-device-tracking`, `native-aug-dot1x`, `native-aug-eap`, `native-aug-enable`, `native-aug-ethernet`, `native-aug-fallback`, `native-aug-file`, `native-aug-flow`, `native-aug-fqdn`, `native-aug-global-address-family`, `native-aug-group-policy`, `native-aug-interface-2`, `native-aug-interface-3`, `native-aug-interface-4`, `native-aug-interface-5`, `native-aug-interface-7`, `native-aug-interface-8`, `native-aug-interface-9`, `native-aug-ip-2`, `native-aug-ipc`, `native-aug-key`, `native-aug-l2`, `native-aug-l2vpn`, `native-aug-l3vpn`, `native-aug-ldap`, `native-aug-location`, `native-aug-mab`, `native-aug-mac`, `native-aug-macro`, `native-aug-mka`, `native-aug-monitor`, `native-aug-mpls`, `native-aug-mvrp`, `native-aug-object-group`, `native-aug-parameter-map`, `native-aug-parser`, `native-aug-performance`, `native-aug-platform`, `native-aug-port-channel`, `native-aug-ppp`, `native-aug-privilege`, `native-aug-process`, `native-aug-ptp`, `native-aug-qos`, `native-aug-radius`, `native-aug-radius-server`, `native-aug-service-insertion`, `native-aug-service-routing`, `native-aug-system`, `native-aug-template-2`, `native-aug-track`, `native-aug-transport`, `native-aug-udld`, `native-aug-user-name`, `native-aug-wsma`, `native-authentication`, `native-auto`, `native-autoconf`, `native-bridge`, `native-buffers`, `native-cef`, `native-coap`, `native-device`, `native-device-sensor`, `native-dhcp`, `native-dialer`, `native-dialer-list`, `native-dns`, `native-dot1x`, `native-energywise`, `native-feature`, `native-fqdn`, `native-group-policy`, `native-hw-switch`, `native-ipc`, `native-kron`, `native-l2protocol-tunnel`, `native-l2vpn-config`, `native-maintenance-template`, `native-mdns-sd`, `native-mgmt-traffic`, `native-mpls`, `native-named-ordering-route-map`, `native-network-policy`, `native-nhrp`, `native-object-group`, `native-openflow`, `native-pae`, `native-password`, `native-pnp`, `native-power`, `native-qos-overhead-accounting`, `native-rep`, `native-route-tag`, `native-router`, `native-router-bgp`, `native-router-eigrp`, `native-router-isis`, `native-router-lisp`, `native-router-lisp-list`, `native-router-nhrp`, `native-router-ospf`, `native-router-rip`, `native-routing`, `native-service-export`, `native-service-group`, `native-service-list`, `native-service-routing`, `native-service-template`, `native-shell`, `native-stack-mac`, `native-switch-global-config`, `native-uplink`, `native-vstack`, `native-xconnect`, `native-zone`, `native-zone-pair`

## ietf

9 of 21 modules returned data (37 data paths, 0.94 MB).

### Modules WITH data

| Module | Data paths | Lines | Size |
|---|---:|---:|---:|
| `ietf-netconf-monitoring` | 10 | 20,833 | 550,916 B |
| `ietf-yang-library` | 2 | 9,525 | 284,214 B |
| `ietf-interfaces` | 4 | 3,020 | 68,149 B |
| `ietf-diffserv-classifier` | 2 | 728 | 17,269 B |
| `ietf-event-notifications` | 6 | 324 | 11,059 B |
| `ietf-routing` | 4 | 516 | 7,852 B |
| `ietf-restconf-monitoring` | 5 | 158 | 3,948 B |
| `ietf-netconf-acm` | 2 | 58 | 760 B |
| `ietf-diffserv-policy` | 2 | 44 | 658 B |

### Modules with 0 data (12)

- **not present (404)** (11): `ietf-diffserv-action`, `ietf-diffserv-target`, `ietf-ip`, `ietf-ipv4-unicast-routing`, `ietf-ipv6-unicast-routing`, `ietf-netconf`, `ietf-netconf-notifications`, `ietf-netconf-otlp-context`, `ietf-ospf`, `ietf-yang-schema-mount`, `ietf-yang-structure-ext`
- **empty (204)** (1): `ietf-key-chain`

## openconfig

10 of 42 modules returned data (23 data paths, 0.70 MB).

### Modules WITH data

| Module | Data paths | Lines | Size |
|---|---:|---:|---:|
| `openconfig-interfaces` | 2 | 14,340 | 283,210 B |
| `openconfig-platform` | 2 | 5,882 | 130,172 B |
| `openconfig-system` | 3 | 7,179 | 110,623 B |
| `openconfig-acl` | 2 | 4,327 | 71,744 B |
| `openconfig-spanning-tree` | 3 | 1,386 | 33,814 B |
| `openconfig-network-instance` | 2 | 1,536 | 22,419 B |
| `openconfig-macsec` | 1 | 1,172 | 17,655 B |
| `openconfig-bfd` | 3 | 942 | 12,599 B |
| `openconfig-lldp` | 3 | 684 | 12,226 B |
| `openconfig-vlan` | 2 | 369 | 3,997 B |

### Modules with 0 data (32)

- **not present (404)** (26): `openconfig-aaa`, `openconfig-access-points`, `openconfig-aft`, `openconfig-alarms`, `openconfig-ap-manager`, `openconfig-bgp`, `openconfig-evpn`, `openconfig-if-ethernet`, `openconfig-igmp`, `openconfig-isis`, `openconfig-license`, `openconfig-local-routing`, `openconfig-mpls`, `openconfig-ospfv2`, `openconfig-packet-match`, `openconfig-pcep`, `openconfig-pim`, `openconfig-platform-transceiver`, `openconfig-policy-forwarding`, `openconfig-procmon`, `openconfig-rib-bgp`, `openconfig-segment-routing`, `openconfig-system-logging`, `openconfig-system-terminal`, `openconfig-wifi-mac`, `openconfig-wifi-phy`
- **empty (204)** (6): `openconfig-ethernet-segments`, `openconfig-keychain`, `openconfig-lacp`, `openconfig-messages`, `openconfig-qos`, `openconfig-routing-policy`

## other

2 of 8 modules returned data (19 data paths, 0.03 MB).

### Modules WITH data

| Module | Data paths | Lines | Size |
|---|---:|---:|---:|
| `cisco-self-mgmt` | 1 | 817 | 18,237 B |
| `cisco-smart-license` | 18 | 604 | 11,284 B |

### Modules with 0 data (6)

- **not present (404)** (5): `cisco-bridge-domain`, `cisco-ethernet`, `cisco-policy-filters`, `cisco-pw`, `confd_dyncfg`
- **empty (204)** (1): `nvo`

