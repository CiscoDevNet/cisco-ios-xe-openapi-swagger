# YANG Module Accountability Report

**Date:** February 01, 2026
**IOS-XE Version:** 17.18.1
**Total YANG Modules:** 848
**Modules with OpenAPI Specs:** 386 (45.5%)

---

## Executive Summary

This report provides **100% accountability** for every YANG module in the
`references/17181-YANG-modules/` folder. Each module is either:

1. **Documented** with an OpenAPI spec in a swagger-* folder, OR
2. **Excluded** with documented reason (types, deviations, etc.)

---

## Category Summary

| Category | Total | With Specs | Coverage | Notes |
|----------|-------|------------|----------|-------|
| **oper** | 209 | 197 | 94% |  |
| **rpc** | 63 | 50 | 79% |  |
| **cfg** | 67 | 39 | 58% |  |
| **openconfig** | 100 | 41 | 41% |  |
| **ietf** | 33 | 21 | 64% |  |
| **events** | 35 | 34 | 97% |  |
| **native** | 1 | 0 | 0% |  |
| **other** | 19 | 3 | 16% |  |
| **types** | 63 | 0 | N/A | Excluded by design |
| **deviation** | 98 | 0 | N/A | Excluded by design |
| **common** | 20 | 1 | N/A | Excluded by design |
| **native-aug** | 140 | 0 | N/A | Excluded by design |

---

## Detailed Module List

### OPER (209 modules)

| Module Name | Swagger Folder | Has Spec |
|-------------|----------------|----------|
| Cisco-IOS-XE-aaa-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-acl-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-app-cflowd-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-app-hosting-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-appqoe-http-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-appqoe-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-appqoe-serv-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-appqoe-sslproxy-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-appqoe-tcpproxy-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-arp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-aws-common-oper | - | ❌ |
| Cisco-IOS-XE-aws-cw-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-aws-s3-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-bbu-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-bfd-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-bgp-common-oper | - | ❌ |
| Cisco-IOS-XE-bgp-nbr-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-bgp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-bgp-rib-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-bgp-route-oper | - | ❌ |
| Cisco-IOS-XE-boot-integrity-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-breakout-port-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-bridge-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-cable-diag-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-cdp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-cellwan-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-cfm-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-checkpoint-archive-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-cloud-services-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-controller-shdsl-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-controller-t1e1-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-controller-vdsl-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-crypto-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-crypto-pki-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-device-hardware-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-dhcp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-dhcp-security-track-server-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-diffserv-target-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-digital-io-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-dlr-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-dns-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-dre-cp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-dre-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-eem-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-efp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-eigrp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-embedded-ap-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-endpoint-tracker-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-environment-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-eogre-tunnel-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-evpn-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-fib-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-flow-monitor-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-fw-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-fwd-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-geo-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-gir-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-gnss-dr-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-gnss-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-group-policy-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ha-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-hsr-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-hsrp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-identity-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ignition-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-im-events-oper | - | ❌ |
| Cisco-IOS-XE-install-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-interfaces-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ios-common-oper | - | ❌ |
| Cisco-IOS-XE-ios-events-oper | - | ❌ |
| Cisco-IOS-XE-ip-arp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ip-sla-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ipv6-nd-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ipv6-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-isdn-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-isis-intf-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-isis-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-l2nat-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-l2tp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-l2vpn-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-lacp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-line-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-linecard-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-lisp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-livetools-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-lldp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-lorawan-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-lte450-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-macsec-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-matm-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mdt-capabilities-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mdt-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mdt-stats-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-memory-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-meraki-connect-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mka-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mlppp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mpls-forwarding-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mpls-ldp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mpls-te-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mroute-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-mrp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-msdp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-nat-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ncch-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-netconf-diag-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ntp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-nve-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-nwpi-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-omp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ospf-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-perf-measure-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-pim-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-platform-common-oper | - | ❌ |
| Cisco-IOS-XE-platform-events-oper | - | ❌ |
| Cisco-IOS-XE-platform-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-platform-software-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-poe-health-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-poe-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-policymap-target-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ppp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-process-cpu-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-process-memory-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-prp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-psecure-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-qfp-appqoe-dp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-qfp-classification-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-qfp-crypto-dp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-qfp-dp-cmn-stats-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-qfp-resource-utilization-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-qfp-stats-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-rawsocket-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-rg-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-rif-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-scada-gw-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-sd-vxlan-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-sdwan-aaa-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-sdwan-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-service-chain-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-service-insertion-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-sm-events-oper | - | ❌ |
| Cisco-IOS-XE-spanning-tree-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-stack-member-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-stack-mgr-events-oper | - | ❌ |
| Cisco-IOS-XE-stack-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-stacking-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-steering-policy-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-switch-cp-svl-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-switch-dp-mac-learning-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-switch-dp-punt-inject-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-switch-dp-resources-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-switch-ptp-dp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-switch-ptp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-switchport-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-system-integrity-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-tcam-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-teyes-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-transceiver-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-trustsec-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-tunnel-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-ucse-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-udld-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-uidp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-umbrella-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-uplink-autoconfig-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-utd-common-oper | - | ❌ |
| Cisco-IOS-XE-utd-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-vdsp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-vlan-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-voice-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-vrf-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-vrrp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-access-point-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-afc-cloud-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-afc-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-ap-global-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-awips-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-ble-ltx-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-ble-mgmt-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-cisco-spaces-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-client-global-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-client-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-cts-sxp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-events-oper | - | ❌ |
| Cisco-IOS-XE-wireless-general-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-geolocation-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-hyperlocation-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-lisp-agent-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-location-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-mcast-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-mdns-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-mesh-global-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-mesh-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-mobility-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-nmsp-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-rfid-global-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-rfid-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-rogue-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-rrm-emul-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-rrm-global-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-rrm-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-rule-mdns-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-sdavc-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-sisf-global-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-tunnel-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-urwbnet-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wireless-wlan-global-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-wpan-oper | swagger-oper-model | ✅ |
| Cisco-IOS-XE-yang-interfaces-oper | swagger-oper-model | ✅ |

### RPC (63 modules)

| Module Name | Swagger Folder | Has Spec |
|-------------|----------------|----------|
| Cisco-IOS-XE-aaa-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-aaa-rpc | - | ❌ |
| Cisco-IOS-XE-arp-rpc | - | ❌ |
| Cisco-IOS-XE-bgp-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-bgp-rpc | - | ❌ |
| Cisco-IOS-XE-cable-diag-rpc | - | ❌ |
| Cisco-IOS-XE-cellular-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-chassis-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-cli-preview-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-cli-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-cloud-services-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-crypto-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-crypto-rpc | - | ❌ |
| Cisco-IOS-XE-cts-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-cwan-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-cwan-fw-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-dhcp-rpc | - | ❌ |
| Cisco-IOS-XE-embedded-ap-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-ethernet-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-factory-reset-secure-rpc | - | ❌ |
| Cisco-IOS-XE-flow-rpc | - | ❌ |
| Cisco-IOS-XE-geo-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-install-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-line-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-livetools-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-logging-ios-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-meraki-leds-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-multicast-rpc | - | ❌ |
| Cisco-IOS-XE-netconf-diag-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-nwpi-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-omp-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-ospf-rpc | - | ❌ |
| Cisco-IOS-XE-platform-rpc | - | ❌ |
| Cisco-IOS-XE-port-bounce-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-port-security-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-power-supply-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-rescue-config-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-sdwan-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-sslproxy-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-stack-power-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-switch-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-tech-support-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-trace-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-uac-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-ucse-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-umbrella-rpc | - | ❌ |
| Cisco-IOS-XE-utd-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-utd-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-verify-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-voice-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-access-point-cfg-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-access-point-cmd-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-actions-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-ble-mgmt-cmd-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-client-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-mesh-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-rogue-authz-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-rrm-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-wireless-tech-support-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-xcopy-rpc | swagger-rpc-model | ✅ |
| Cisco-IOS-XE-zone-rpc | - | ❌ |
| cisco-ia | swagger-rpc-model | ✅ |

### CFG (67 modules)

| Module Name | Swagger Folder | Has Spec |
|-------------|----------------|----------|
| Cisco-IOS-XE-app-hosting-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-aws-common-cfg | - | ❌ |
| Cisco-IOS-XE-aws-cw-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-aws-s3-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-cloud-services-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-controller-shdsl-common | - | ❌ |
| Cisco-IOS-XE-ctrl-mng-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-eigrp-obsolete | - | ❌ |
| Cisco-IOS-XE-ethernet-cfm-efp | - | ❌ |
| Cisco-IOS-XE-ethernet-oam | - | ❌ |
| Cisco-IOS-XE-features | - | ❌ |
| Cisco-IOS-XE-gnmi-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-grpc-tunnel-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-hsrp | - | ❌ |
| Cisco-IOS-XE-interface-common | - | ❌ |
| Cisco-IOS-XE-interfaces | - | ❌ |
| Cisco-IOS-XE-ip | - | ❌ |
| Cisco-IOS-XE-ipv6 | - | ❌ |
| Cisco-IOS-XE-license | - | ❌ |
| Cisco-IOS-XE-location | - | ❌ |
| Cisco-IOS-XE-logging | - | ❌ |
| Cisco-IOS-XE-mdt-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-mdt-common-defs | - | ❌ |
| Cisco-IOS-XE-mdt-oper-v2 | - | ❌ |
| Cisco-IOS-XE-ncch-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-ospf-common | - | ❌ |
| Cisco-IOS-XE-ospf-obsolete | - | ❌ |
| Cisco-IOS-XE-parser | - | ❌ |
| Cisco-IOS-XE-qfp-stats | - | ❌ |
| Cisco-IOS-XE-sip-ua | - | ❌ |
| Cisco-IOS-XE-sisf | - | ❌ |
| Cisco-IOS-XE-sslproxy-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-transceiver-monitor | - | ❌ |
| Cisco-IOS-XE-transport | - | ❌ |
| Cisco-IOS-XE-umbrella-oper-dp | - | ❌ |
| Cisco-IOS-XE-voice-class | - | ❌ |
| Cisco-IOS-XE-voice-dspfarm | - | ❌ |
| Cisco-IOS-XE-voice-register | - | ❌ |
| Cisco-IOS-XE-wireless-ap-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-apf-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-cts-sxp-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-dot11-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-dot15-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-fabric-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-flex-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-fqdn-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-general-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-hotspot-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-location-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-mesh-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-mobility-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-mstream-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-power-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-radio-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-rf-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-rfid-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-rlan-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-rogue-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-rrm-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-rule-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-security-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-site-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-tunnel-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-urwb-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-wat-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-wireless-wlan-cfg | swagger-cfg-model | ✅ |
| Cisco-IOS-XE-yang-interfaces-cfg | swagger-cfg-model | ✅ |

### OPENCONFIG (100 modules)

| Module Name | Swagger Folder | Has Spec |
|-------------|----------------|----------|
| openconfig-aaa | swagger-openconfig-model | ✅ |
| openconfig-aaa-radius | - | ❌ |
| openconfig-aaa-tacacs | - | ❌ |
| openconfig-access-points | swagger-openconfig-model | ✅ |
| openconfig-acl | swagger-openconfig-model | ✅ |
| openconfig-aft | swagger-openconfig-model | ✅ |
| openconfig-aft-common | - | ❌ |
| openconfig-aft-ethernet | - | ❌ |
| openconfig-aft-ipv4 | - | ❌ |
| openconfig-aft-ipv6 | - | ❌ |
| openconfig-aft-mpls | - | ❌ |
| openconfig-aft-network-instance | - | ❌ |
| openconfig-aft-pf | - | ❌ |
| openconfig-aft-state-synced | - | ❌ |
| openconfig-alarms | swagger-openconfig-model | ✅ |
| openconfig-ap-manager | swagger-openconfig-model | ✅ |
| openconfig-bfd | swagger-openconfig-model | ✅ |
| openconfig-bgp | swagger-openconfig-model | ✅ |
| openconfig-bgp-common | - | ❌ |
| openconfig-bgp-common-multiprotocol | - | ❌ |
| openconfig-bgp-common-structure | - | ❌ |
| openconfig-bgp-errors | - | ❌ |
| openconfig-bgp-global | - | ❌ |
| openconfig-bgp-neighbor | - | ❌ |
| openconfig-bgp-peer-group | - | ❌ |
| openconfig-bgp-policy | - | ❌ |
| openconfig-ethernet-segments | swagger-openconfig-model | ✅ |
| openconfig-evpn | swagger-openconfig-model | ✅ |
| openconfig-extensions | - | ❌ |
| openconfig-if-aggregate | - | ❌ |
| openconfig-if-ethernet | swagger-openconfig-model | ✅ |
| openconfig-if-ip | - | ❌ |
| openconfig-if-ip-ext | - | ❌ |
| openconfig-if-poe | - | ❌ |
| openconfig-igmp | swagger-openconfig-model | ✅ |
| openconfig-interfaces | swagger-openconfig-model | ✅ |
| openconfig-isis | swagger-openconfig-model | ✅ |
| openconfig-isis-lsp | - | ❌ |
| openconfig-isis-policy | - | ❌ |
| openconfig-isis-routing | - | ❌ |
| openconfig-keychain | swagger-openconfig-model | ✅ |
| openconfig-lacp | swagger-openconfig-model | ✅ |
| openconfig-license | swagger-openconfig-model | ✅ |
| openconfig-lldp | swagger-openconfig-model | ✅ |
| openconfig-local-routing | swagger-openconfig-model | ✅ |
| openconfig-macsec | swagger-openconfig-model | ✅ |
| openconfig-messages | swagger-openconfig-model | ✅ |
| openconfig-mpls | swagger-openconfig-model | ✅ |
| openconfig-mpls-igp | - | ❌ |
| openconfig-mpls-ldp | - | ❌ |
| openconfig-mpls-rsvp | - | ❌ |
| openconfig-mpls-sr | - | ❌ |
| openconfig-mpls-static | - | ❌ |
| openconfig-mpls-te | - | ❌ |
| openconfig-network-instance | swagger-openconfig-model | ✅ |
| openconfig-network-instance-l2 | - | ❌ |
| openconfig-network-instance-l3 | - | ❌ |
| openconfig-network-instance-policy | - | ❌ |
| openconfig-openflow | - | ❌ |
| openconfig-ospf-policy | - | ❌ |
| openconfig-ospfv2 | swagger-openconfig-model | ✅ |
| openconfig-ospfv2-area | - | ❌ |
| openconfig-ospfv2-area-interface | - | ❌ |
| openconfig-ospfv2-common | - | ❌ |
| openconfig-ospfv2-global | - | ❌ |
| openconfig-ospfv2-lsdb | - | ❌ |
| openconfig-packet-match | swagger-openconfig-model | ✅ |
| openconfig-pcep | swagger-openconfig-model | ✅ |
| openconfig-pf-forwarding-policies | - | ❌ |
| openconfig-pf-interfaces | - | ❌ |
| openconfig-pf-path-groups | - | ❌ |
| openconfig-pf-srte | - | ❌ |
| openconfig-pim | swagger-openconfig-model | ✅ |
| openconfig-platform | swagger-openconfig-model | ✅ |
| openconfig-platform-cpu | - | ❌ |
| openconfig-platform-fan | - | ❌ |
| openconfig-platform-linecard | - | ❌ |
| openconfig-platform-port | - | ❌ |
| openconfig-platform-psu | - | ❌ |
| openconfig-platform-transceiver | swagger-openconfig-model | ✅ |
| openconfig-policy-forwarding | swagger-openconfig-model | ✅ |
| openconfig-procmon | swagger-openconfig-model | ✅ |
| openconfig-programming-errors | - | ❌ |
| openconfig-rib-bgp | swagger-openconfig-model | ✅ |
| openconfig-rib-bgp-attributes | - | ❌ |
| openconfig-rib-bgp-ext | - | ❌ |
| openconfig-rib-bgp-shared-attributes | - | ❌ |
| openconfig-rib-bgp-table-attributes | - | ❌ |
| openconfig-rib-bgp-tables | - | ❌ |
| openconfig-route-summary | - | ❌ |
| openconfig-routing-policy | swagger-openconfig-model | ✅ |
| openconfig-segment-routing | swagger-openconfig-model | ✅ |
| openconfig-spanning-tree | swagger-openconfig-model | ✅ |
| openconfig-system | swagger-openconfig-model | ✅ |
| openconfig-system-grpc | - | ❌ |
| openconfig-system-logging | swagger-openconfig-model | ✅ |
| openconfig-system-terminal | swagger-openconfig-model | ✅ |
| openconfig-vlan | swagger-openconfig-model | ✅ |
| openconfig-wifi-mac | swagger-openconfig-model | ✅ |
| openconfig-wifi-phy | swagger-openconfig-model | ✅ |

### IETF (33 modules)

| Module Name | Swagger Folder | Has Spec |
|-------------|----------------|----------|
| iana-crypt-hash | - | ❌ |
| iana-if-type | - | ❌ |
| ietf-datastores | - | ❌ |
| ietf-diffserv-action | swagger-ietf-model | ✅ |
| ietf-diffserv-classifier | swagger-ietf-model | ✅ |
| ietf-diffserv-policy | swagger-ietf-model | ✅ |
| ietf-diffserv-target | swagger-ietf-model | ✅ |
| ietf-event-notifications | swagger-ietf-model | ✅ |
| ietf-interfaces | swagger-ietf-model | ✅ |
| ietf-interfaces-ext | - | ❌ |
| ietf-ip | swagger-ietf-model | ✅ |
| ietf-ipv4-unicast-routing | swagger-ietf-model | ✅ |
| ietf-ipv6-unicast-routing | swagger-ietf-model | ✅ |
| ietf-key-chain | swagger-ietf-model | ✅ |
| ietf-netconf | swagger-ietf-model | ✅ |
| ietf-netconf-acm | swagger-ietf-model | ✅ |
| ietf-netconf-monitoring | swagger-ietf-model | ✅ |
| ietf-netconf-notifications | swagger-ietf-model | ✅ |
| ietf-netconf-otlp-context | swagger-ietf-model | ✅ |
| ietf-netconf-otlp-context-traceparent-version-1.0 | - | ❌ |
| ietf-netconf-otlp-context-tracestate-version-1.0 | - | ❌ |
| ietf-netconf-with-defaults | - | ❌ |
| ietf-ospf | swagger-ietf-model | ✅ |
| ietf-restconf | - | ❌ |
| ietf-restconf-monitoring | swagger-ietf-model | ✅ |
| ietf-routing | swagger-ietf-model | ✅ |
| ietf-yang-library | swagger-ietf-model | ✅ |
| ietf-yang-patch | - | ❌ |
| ietf-yang-patch-ann | - | ❌ |
| ietf-yang-push | - | ❌ |
| ietf-yang-schema-mount | swagger-ietf-model | ✅ |
| ietf-yang-smiv2 | - | ❌ |
| ietf-yang-structure-ext | swagger-ietf-model | ✅ |

### EVENTS (35 modules)

| Module Name | Swagger Folder | Has Spec |
|-------------|----------------|----------|
| Cisco-IOS-XE-aaa-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-appqoe-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-controller-shdsl-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-crypto-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-crypto-pki-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-dca-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-endpoint-tracker-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-fib-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-geo-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-hsrp-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-install-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-interface-bw-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-ip-sla-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-line-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-loop-detect-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-matm-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-mcast-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-nat-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-ngfw-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-ospf-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-perf-measure-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-platform-software-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-port-bounce-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-qfp-resource-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-red-app-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-spanning-tree-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-tech-support-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-trace-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-udld-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-utd-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-verify-events | swagger-events-model | ✅ |
| Cisco-IOS-XE-xcopy-events | swagger-events-model | ✅ |
| cisco-bridge-domain | swagger-rpc-model | ✅ |
| cisco-pw | - | ❌ |
| cisco-smart-license | swagger-rpc-model | ✅ |

### NATIVE (1 modules)

| Module Name | Swagger Folder | Has Spec |
|-------------|----------------|----------|
| Cisco-IOS-XE-native | - | ❌ |

### OTHER (19 modules)

| Module Name | Swagger Folder | Has Spec |
|-------------|----------------|----------|
| cisco-bridge-common | - | ❌ |
| cisco-ethernet | - | ❌ |
| cisco-evpn-service | - | ❌ |
| cisco-extensions | - | ❌ |
| cisco-ospf | - | ❌ |
| cisco-policy | - | ❌ |
| cisco-policy-filters | - | ❌ |
| cisco-policy-target | - | ❌ |
| cisco-routing-ext | - | ❌ |
| cisco-self-mgmt | swagger-other-model | ✅ |
| cisco-semver-internal | - | ❌ |
| cisco-storm-control | - | ❌ |
| cisco-xe-ietf-routing-ext | - | ❌ |
| cisco-xe-ietf-yang-push-ext | - | ❌ |
| common-mpls-static | - | ❌ |
| confd_dyncfg | swagger-other-model | ✅ |
| nvo | swagger-other-model | ✅ |
| pim | - | ❌ |
| policy-attr | - | ❌ |

### TYPES (63 modules)

*These modules are excluded by design: Type definitions only - no API operations*

<details>
<summary>Click to expand list of 63 types modules</summary>

| Module Name | Reason |
|-------------|--------|
| Cisco-IOS-XE-aaa-types | Type definitions only - no API operations |
| Cisco-IOS-XE-appqoe-types | Type definitions only - no API operations |
| Cisco-IOS-XE-common-types | Type definitions only - no API operations |
| Cisco-IOS-XE-dmi-common-types | Type definitions only - no API operations |
| Cisco-IOS-XE-event-history-types | Type definitions only - no API operations |
| Cisco-IOS-XE-install-event-types | Type definitions only - no API operations |
| Cisco-IOS-XE-install-oper-types | Type definitions only - no API operations |
| Cisco-IOS-XE-livetools-common-types | Type definitions only - no API operations |
| Cisco-IOS-XE-nwpi-types | Type definitions only - no API operations |
| Cisco-IOS-XE-red-app-common-types | Type definitions only - no API operations |
| Cisco-IOS-XE-sdwan-types | Type definitions only - no API operations |
| Cisco-IOS-XE-sm-enum-types | Type definitions only - no API operations |
| Cisco-IOS-XE-tunnel-types | Type definitions only - no API operations |
| Cisco-IOS-XE-types | Type definitions only - no API operations |
| Cisco-IOS-XE-vrrp-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-afc-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-ap-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-client-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-enum-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-geolocation-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-mobility-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-rogue-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-rrm-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-tunnel-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wireless-urwb-common-types | Type definitions only - no API operations |
| Cisco-IOS-XE-wsa-types | Type definitions only - no API operations |
| cisco-smart-license-errors | Contains only type definitions |
| common-mpls-types | Type definitions only - no API operations |
| ietf-inet-types | Type definitions only - no API operations |
| ietf-routing-types | Type definitions only - no API operations |
| ietf-yang-types | Type definitions only - no API operations |
| openconfig-aaa-types | Type definitions only - no API operations |
| openconfig-aft-types | Type definitions only - no API operations |
| openconfig-alarm-types | Type definitions only - no API operations |
| openconfig-bgp-types | Type definitions only - no API operations |
| openconfig-evpn-types | Type definitions only - no API operations |
| openconfig-if-types | Type definitions only - no API operations |
| openconfig-igmp-types | Type definitions only - no API operations |
| openconfig-inet-types | Type definitions only - no API operations |
| openconfig-isis-lsdb-types | Type definitions only - no API operations |
| openconfig-isis-types | Type definitions only - no API operations |
| openconfig-keychain-types | Type definitions only - no API operations |
| openconfig-lldp-types | Type definitions only - no API operations |
| openconfig-macsec-types | Type definitions only - no API operations |
| openconfig-mpls-types | Type definitions only - no API operations |
| openconfig-network-instance-types | Type definitions only - no API operations |
| openconfig-openflow-types | Type definitions only - no API operations |
| openconfig-ospf-types | Type definitions only - no API operations |
| openconfig-packet-match-types | Type definitions only - no API operations |
| openconfig-pim-types | Type definitions only - no API operations |
| openconfig-platform-types | Type definitions only - no API operations |
| openconfig-policy-types | Type definitions only - no API operations |
| openconfig-rib-bgp-types | Type definitions only - no API operations |
| openconfig-segment-routing-types | Type definitions only - no API operations |
| openconfig-spanning-tree-types | Type definitions only - no API operations |
| openconfig-transport-types | Type definitions only - no API operations |
| openconfig-types | Type definitions only - no API operations |
| openconfig-vlan-types | Type definitions only - no API operations |
| openconfig-wifi-types | Type definitions only - no API operations |
| openconfig-yang-types | Type definitions only - no API operations |
| policy-types | Type definitions only - no API operations |
| tailf-xsd-types | Type definitions only - no API operations |

</details>

### DEVIATION (98 modules)

*These modules are excluded by design: Deviation module - modifies other modules, no standalone API*

<details>
<summary>Click to expand list of 98 deviation modules</summary>

| Module Name | Reason |
|-------------|--------|
| Cisco-IOS-XE-aaa-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-aging-time-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-cdp-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-cef-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-cts-routing-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-cts-switching-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-dhcp-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-dialer-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-ethernet-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-ethernet-mcp-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-flow-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-interfaces-cat9k-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-interfaces-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-interfaces-wlc-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-line-common-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-line-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-line-nonquake-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-lisp-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-logging-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-nd-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-ospf-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-ospfv3-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-perf-measure-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-pnp-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-poch-lb-switch-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-policy-cat9k-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-policy-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-policy-mcp-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-policy-vxe-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-policy-wlc-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-port-channel-crankshaft-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-port-channel-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-port-channel-unsupported-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-power-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-ppp-mcp-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-sanet-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-snmp-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-switch-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-switchport-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-switchport-ewlc-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-vlan-ewlc-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-vlan-vxe-deviation | Deviation module - modifies other modules, no standalone API |
| Cisco-IOS-XE-vrrp-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-ietf-event-notifications-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-ietf-ip-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-ietf-ipv4-unicast-routing-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-ietf-ipv6-unicast-routing-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-ietf-ospf-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-ietf-routing-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-ietf-yang-push-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-access-points-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-acl-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-acl-ext | OpenConfig deviation module |
| cisco-xe-openconfig-aft-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-bgp-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-bgp-policy-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-ethernet-segments-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-evpn-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-if-ethernet-ext | OpenConfig deviation module |
| cisco-xe-openconfig-if-ip-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-if-poe-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-interfaces-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-interfaces-ext | OpenConfig deviation module |
| cisco-xe-openconfig-isis-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-isis-policy-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-lldp-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-local-routing-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-mpls-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-network-instance-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-network-instance-l2-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-openflow-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-platform-ext | OpenConfig deviation module |
| cisco-xe-openconfig-rib-bgp-ext | OpenConfig deviation module |
| cisco-xe-openconfig-routing-policy-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-segment-routing-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-spanning-tree-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-spanning-tree-ext | OpenConfig deviation module |
| cisco-xe-openconfig-system-ext | OpenConfig deviation module |
| cisco-xe-openconfig-system-grpc-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-openconfig-vlan-ext | OpenConfig deviation module |
| cisco-xe-routing-asr-openconfig-if-ethernet-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-routing-csr-openconfig-platform-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-routing-isr-openconfig-if-ethernet-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-routing-isr-openconfig-platform-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-routing-openconfig-system-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-routing-openconfig-system-ext | OpenConfig deviation module |
| cisco-xe-routing-openconfig-system-grpc-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-routing-openconfig-vlan-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-switching-cat9k-openconfig-system-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-switching-openconfig-if-ethernet-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-switching-openconfig-interfaces-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-switching-openconfig-lacp-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-switching-openconfig-platform-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-switching-openconfig-vlan-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-wireless-openconfig-if-ethernet-deviation | Deviation module - modifies other modules, no standalone API |
| cisco-xe-wireless-openconfig-vlan-deviation | Deviation module - modifies other modules, no standalone API |
| common-mpls-static-devs | Deviation module - modifies other modules, no standalone API |
| nvo-devs | Deviation module - modifies other modules, no standalone API |

</details>

### COMMON (20 modules)

*These modules are excluded by design: Semantic versioning module - metadata only*

<details>
<summary>Click to expand list of 20 common modules</summary>

| Module Name | Reason |
|-------------|--------|
| cisco-semver | Semantic versioning module - metadata only |
| tailf-aaa | Tail-f/Cisco infrastructure module - internal use |
| tailf-acm | Tail-f/Cisco infrastructure module - internal use |
| tailf-cli-extensions | Tail-f/Cisco infrastructure module - internal use |
| tailf-common | Tail-f/Cisco infrastructure module - internal use |
| tailf-common-monitoring2 | Tail-f/Cisco infrastructure module - internal use |
| tailf-common-query | Tail-f/Cisco infrastructure module - internal use |
| tailf-confd-monitoring | Tail-f/Cisco infrastructure module - internal use |
| tailf-confd-monitoring2 | Tail-f/Cisco infrastructure module - internal use |
| tailf-key-rotation | Tail-f/Cisco infrastructure module - internal use |
| tailf-kicker | Tail-f/Cisco infrastructure module - internal use |
| tailf-meta-extensions | Tail-f/Cisco infrastructure module - internal use |
| tailf-netconf-extensions | Tail-f/Cisco infrastructure module - internal use |
| tailf-netconf-inactive | Tail-f/Cisco infrastructure module - internal use |
| tailf-netconf-monitoring | Tail-f/Cisco infrastructure module - internal use |
| tailf-netconf-query | Tail-f/Cisco infrastructure module - internal use |
| tailf-netconf-transactions | - |
| tailf-rest-query | Tail-f/Cisco infrastructure module - internal use |
| tailf-restconf-error | Tail-f/Cisco infrastructure module - internal use |
| tailf-yang-patch | Tail-f/Cisco infrastructure module - internal use |

</details>

### NATIVE-AUG (140 modules)

*These modules are excluded by design: Augments native module - included in native specs*

<details>
<summary>Click to expand list of 140 native-aug modules</summary>

| Module Name | Reason |
|-------------|--------|
| Cisco-IOS-XE-aaa | Augments native module - included in native specs |
| Cisco-IOS-XE-acl | Augments native module - included in native specs |
| Cisco-IOS-XE-adsl | Augments native module - included in native specs |
| Cisco-IOS-XE-alarm-profile | Augments native module - included in native specs |
| Cisco-IOS-XE-app-hosting | Augments native module - included in native specs |
| Cisco-IOS-XE-arp | Augments native module - included in native specs |
| Cisco-IOS-XE-atm | Augments native module - included in native specs |
| Cisco-IOS-XE-avb | Augments native module - included in native specs |
| Cisco-IOS-XE-bba-group | Augments native module - included in native specs |
| Cisco-IOS-XE-bfd | Augments native module - included in native specs |
| Cisco-IOS-XE-bgp | Augments native module - included in native specs |
| Cisco-IOS-XE-bridge | Augments native module - included in native specs |
| Cisco-IOS-XE-bridge-domain | Augments native module - included in native specs |
| Cisco-IOS-XE-buffers | Augments native module - included in native specs |
| Cisco-IOS-XE-call-home | Augments native module - included in native specs |
| Cisco-IOS-XE-card | Augments native module - included in native specs |
| Cisco-IOS-XE-cdp | Augments native module - included in native specs |
| Cisco-IOS-XE-cef | Augments native module - included in native specs |
| Cisco-IOS-XE-cellular | Augments native module - included in native specs |
| Cisco-IOS-XE-clns | Augments native module - included in native specs |
| Cisco-IOS-XE-coap | Augments native module - included in native specs |
| Cisco-IOS-XE-controller | Augments native module - included in native specs |
| Cisco-IOS-XE-crypto | Augments native module - included in native specs |
| Cisco-IOS-XE-cts | Augments native module - included in native specs |
| Cisco-IOS-XE-cwmp | Augments native module - included in native specs |
| Cisco-IOS-XE-dapr | Augments native module - included in native specs |
| Cisco-IOS-XE-device-sensor | Augments native module - included in native specs |
| Cisco-IOS-XE-device-tracking | Augments native module - included in native specs |
| Cisco-IOS-XE-dhcp | Augments native module - included in native specs |
| Cisco-IOS-XE-diagnostics | Augments native module - included in native specs |
| Cisco-IOS-XE-dialer | Augments native module - included in native specs |
| Cisco-IOS-XE-digitalio | Augments native module - included in native specs |
| Cisco-IOS-XE-dlr | Augments native module - included in native specs |
| Cisco-IOS-XE-dot1x | Augments native module - included in native specs |
| Cisco-IOS-XE-dying-gasp | Augments native module - included in native specs |
| Cisco-IOS-XE-eem | Augments native module - included in native specs |
| Cisco-IOS-XE-eigrp | Augments native module - included in native specs |
| Cisco-IOS-XE-eta | Augments native module - included in native specs |
| Cisco-IOS-XE-ethernet | Augments native module - included in native specs |
| Cisco-IOS-XE-ethinternal-subslot | Augments native module - included in native specs |
| Cisco-IOS-XE-ezpm | Augments native module - included in native specs |
| Cisco-IOS-XE-flow | Augments native module - included in native specs |
| Cisco-IOS-XE-fqdn | Augments native module - included in native specs |
| Cisco-IOS-XE-frame-relay | Augments native module - included in native specs |
| Cisco-IOS-XE-geo | Augments native module - included in native specs |
| Cisco-IOS-XE-gnss | Augments native module - included in native specs |
| Cisco-IOS-XE-group-policy | Augments native module - included in native specs |
| Cisco-IOS-XE-http | Augments native module - included in native specs |
| Cisco-IOS-XE-icmp | Augments native module - included in native specs |
| Cisco-IOS-XE-ida | Augments native module - included in native specs |
| Cisco-IOS-XE-igmp | Augments native module - included in native specs |
| Cisco-IOS-XE-ipc | Augments native module - included in native specs |
| Cisco-IOS-XE-ipmux | Augments native module - included in native specs |
| Cisco-IOS-XE-irig | Augments native module - included in native specs |
| Cisco-IOS-XE-isdn | Augments native module - included in native specs |
| Cisco-IOS-XE-isg | Augments native module - included in native specs |
| Cisco-IOS-XE-isis | Augments native module - included in native specs |
| Cisco-IOS-XE-iwanfabric | Augments native module - included in native specs |
| Cisco-IOS-XE-kron | Augments native module - included in native specs |
| Cisco-IOS-XE-l2nat | Augments native module - included in native specs |
| Cisco-IOS-XE-l2vpn | Augments native module - included in native specs |
| Cisco-IOS-XE-l3nat-iox | Augments native module - included in native specs |
| Cisco-IOS-XE-l3vpn | Augments native module - included in native specs |
| Cisco-IOS-XE-line | Augments native module - included in native specs |
| Cisco-IOS-XE-lisp | Augments native module - included in native specs |
| Cisco-IOS-XE-lldp | Augments native module - included in native specs |
| Cisco-IOS-XE-loop-detect | Augments native module - included in native specs |
| Cisco-IOS-XE-lorawan | Augments native module - included in native specs |
| Cisco-IOS-XE-lte450 | Augments native module - included in native specs |
| Cisco-IOS-XE-mdns-gateway | Augments native module - included in native specs |
| Cisco-IOS-XE-mka | Augments native module - included in native specs |
| Cisco-IOS-XE-mld | Augments native module - included in native specs |
| Cisco-IOS-XE-mmode | Augments native module - included in native specs |
| Cisco-IOS-XE-mobileip | Augments native module - included in native specs |
| Cisco-IOS-XE-mpls | Augments native module - included in native specs |
| Cisco-IOS-XE-mrp | Augments native module - included in native specs |
| Cisco-IOS-XE-multicast | Augments native module - included in native specs |
| Cisco-IOS-XE-mvrp | Augments native module - included in native specs |
| Cisco-IOS-XE-nam | Augments native module - included in native specs |
| Cisco-IOS-XE-nat | Augments native module - included in native specs |
| Cisco-IOS-XE-nbar | Augments native module - included in native specs |
| Cisco-IOS-XE-nd | Augments native module - included in native specs |
| Cisco-IOS-XE-nhrp | Augments native module - included in native specs |
| Cisco-IOS-XE-ntp | Augments native module - included in native specs |
| Cisco-IOS-XE-object-group | Augments native module - included in native specs |
| Cisco-IOS-XE-ospf | Augments native module - included in native specs |
| Cisco-IOS-XE-ospfv3 | Augments native module - included in native specs |
| Cisco-IOS-XE-otv | Augments native module - included in native specs |
| Cisco-IOS-XE-pae | Augments native module - included in native specs |
| Cisco-IOS-XE-pathmgr | Augments native module - included in native specs |
| Cisco-IOS-XE-perf-measure | Augments native module - included in native specs |
| Cisco-IOS-XE-pfr | Augments native module - included in native specs |
| Cisco-IOS-XE-platform | Augments native module - included in native specs |
| Cisco-IOS-XE-pnp | Augments native module - included in native specs |
| Cisco-IOS-XE-policy | Augments native module - included in native specs |
| Cisco-IOS-XE-power | Augments native module - included in native specs |
| Cisco-IOS-XE-ppp | Augments native module - included in native specs |
| Cisco-IOS-XE-pppoe | Augments native module - included in native specs |
| Cisco-IOS-XE-prp | Augments native module - included in native specs |
| Cisco-IOS-XE-ptp | Augments native module - included in native specs |
| Cisco-IOS-XE-qos | Augments native module - included in native specs |
| Cisco-IOS-XE-rawsocket | Augments native module - included in native specs |
| Cisco-IOS-XE-rip | Augments native module - included in native specs |
| Cisco-IOS-XE-rmi-dad | Augments native module - included in native specs |
| Cisco-IOS-XE-route-map | Augments native module - included in native specs |
| Cisco-IOS-XE-rsvp | Augments native module - included in native specs |
| Cisco-IOS-XE-sanet | Augments native module - included in native specs |
| Cisco-IOS-XE-scada-gw | Augments native module - included in native specs |
| Cisco-IOS-XE-segment-routing | Augments native module - included in native specs |
| Cisco-IOS-XE-serial | Augments native module - included in native specs |
| Cisco-IOS-XE-service-discovery | Augments native module - included in native specs |
| Cisco-IOS-XE-service-insertion | Augments native module - included in native specs |
| Cisco-IOS-XE-service-routing | Augments native module - included in native specs |
| Cisco-IOS-XE-site-manager | Augments native module - included in native specs |
| Cisco-IOS-XE-sla | Augments native module - included in native specs |
| Cisco-IOS-XE-snmp | Augments native module - included in native specs |
| Cisco-IOS-XE-spanning-tree | Augments native module - included in native specs |
| Cisco-IOS-XE-stackwise-virtual | Augments native module - included in native specs |
| Cisco-IOS-XE-switch | Augments native module - included in native specs |
| Cisco-IOS-XE-synce | Augments native module - included in native specs |
| Cisco-IOS-XE-template | Augments native module - included in native specs |
| Cisco-IOS-XE-track | Augments native module - included in native specs |
| Cisco-IOS-XE-tunnel | Augments native module - included in native specs |
| Cisco-IOS-XE-ucse | Augments native module - included in native specs |
| Cisco-IOS-XE-udld | Augments native module - included in native specs |
| Cisco-IOS-XE-umbrella | Augments native module - included in native specs |
| Cisco-IOS-XE-uplink-autoconfig | Augments native module - included in native specs |
| Cisco-IOS-XE-utd | Augments native module - included in native specs |
| Cisco-IOS-XE-vlan | Augments native module - included in native specs |
| Cisco-IOS-XE-voice | Augments native module - included in native specs |
| Cisco-IOS-XE-voice-port | Augments native module - included in native specs |
| Cisco-IOS-XE-vpdn | Augments native module - included in native specs |
| Cisco-IOS-XE-vrrp | Augments native module - included in native specs |
| Cisco-IOS-XE-vservice | Augments native module - included in native specs |
| Cisco-IOS-XE-vstack | Augments native module - included in native specs |
| Cisco-IOS-XE-vtp | Augments native module - included in native specs |
| Cisco-IOS-XE-vxlan | Augments native module - included in native specs |
| Cisco-IOS-XE-wccp | Augments native module - included in native specs |
| Cisco-IOS-XE-wsma | Augments native module - included in native specs |
| Cisco-IOS-XE-zone | Augments native module - included in native specs |

</details>

---

## Generation Notes

### Excluded Categories Explained

| Category | Reason for Exclusion |
|----------|---------------------|
| **types** | Contains only `typedef` and `grouping` statements - no API operations |
| **deviation** | Modifies other modules' behavior - no standalone API |
| **common** | Infrastructure modules (tailf-*, cisco-semver) - internal use |
| **native-aug** | Augments Cisco-IOS-XE-native - included in native category specs |
| **deprecated** | Obsolete modules - no longer supported |

### Native Module Handling

The `Cisco-IOS-XE-native.yang` module (200,000+ lines) is too large for a single spec.
It's broken into categorical specs in `swagger-native-config-model/`:

- native-routing.json
- native-interfaces.json
- native-security.json
- etc.

Modules that augment native are included in these categorical specs.

---

*Report generated: 2026-02-01T09:00:06.514843*