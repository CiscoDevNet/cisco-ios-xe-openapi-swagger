# YANG Module Accountability Report

**Date:** March 30, 2026
**IOS-XE Version:** 17.18.1
**Total YANG Modules:** 848
**Modules with OpenAPI Specs:** 425 (50.1%)
**Modules with YANG Trees:** 589
**Modules in Multiple Categories:** 18

> **Interactive Report:** [View the HTML accountability report](yang-accountability.html) with search, filtering, and clickable links.

---

## Executive Summary

This report provides **100% accountability** for every YANG module in the
`references/17181-YANG-modules/` folder. Each module is either:

1. **Documented** with one or more OpenAPI specs (some modules appear in multiple categories)
2. **Excluded** with documented reason (types, deviations, augments, etc.)

---

## Category Summary

| Classification | Total | With Specs | Coverage | Notes |
|----------------|-------|------------|----------|-------|
| **oper** | 200 | 199 | 100% |  |
| **rpc** | 63 | 50 | 79% |  |
| **cfg** | 61 | 40 | 66% |  |
| **openconfig** | 95 | 61 | 64% |  |
| **ietf** | 33 | 23 | 70% |  |
| **events** | 41 | 41 | 100% |  |
| **native** | 1 | 0 | 0% |  |
| **other** | 32 | 10 | 31% |  |
| **types** | 64 | 0 | N/A | Excluded by design |
| **deviation** | 98 | 0 | N/A | Excluded by design |
| **common** | 21 | 1 | N/A | Excluded by design |
| **native-aug** | 139 | 0 | N/A | Excluded by design |

---

## Detailed Module List

### OPER (200 modules)

| Module | Categories | Spec Links | Tree |
|--------|------------|------------|------|
| Cisco-IOS-XE-aaa-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-aaa-oper) | [🌳](yang-trees/Cisco-IOS-XE-aaa-oper.html) |
| Cisco-IOS-XE-acl-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-acl-oper) | [🌳](yang-trees/Cisco-IOS-XE-acl-oper.html) |
| Cisco-IOS-XE-app-cflowd-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-app-cflowd-oper) | [🌳](yang-trees/Cisco-IOS-XE-app-cflowd-oper.html) |
| Cisco-IOS-XE-app-hosting-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-app-hosting-oper) | [🌳](yang-trees/Cisco-IOS-XE-app-hosting-oper.html) |
| Cisco-IOS-XE-appqoe-http-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-appqoe-http-oper) | [🌳](yang-trees/Cisco-IOS-XE-appqoe-http-oper.html) |
| Cisco-IOS-XE-appqoe-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-appqoe-oper) | [🌳](yang-trees/Cisco-IOS-XE-appqoe-oper.html) |
| Cisco-IOS-XE-appqoe-serv-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-appqoe-serv-oper) | [🌳](yang-trees/Cisco-IOS-XE-appqoe-serv-oper.html) |
| Cisco-IOS-XE-appqoe-sslproxy-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-appqoe-sslproxy-oper) | [🌳](yang-trees/Cisco-IOS-XE-appqoe-sslproxy-oper.html) |
| Cisco-IOS-XE-appqoe-tcpproxy-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-appqoe-tcpproxy-oper) | [🌳](yang-trees/Cisco-IOS-XE-appqoe-tcpproxy-oper.html) |
| Cisco-IOS-XE-arp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-arp-oper) | [🌳](yang-trees/Cisco-IOS-XE-arp-oper.html) |
| Cisco-IOS-XE-aws-cw-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-aws-cw-oper) | [🌳](yang-trees/Cisco-IOS-XE-aws-cw-oper.html) |
| Cisco-IOS-XE-aws-s3-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-aws-s3-oper) | [🌳](yang-trees/Cisco-IOS-XE-aws-s3-oper.html) |
| Cisco-IOS-XE-bbu-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-bbu-oper) | [🌳](yang-trees/Cisco-IOS-XE-bbu-oper.html) |
| Cisco-IOS-XE-bfd-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-bfd-oper) | [🌳](yang-trees/Cisco-IOS-XE-bfd-oper.html) |
| Cisco-IOS-XE-bgp-nbr-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-bgp-nbr-oper) | [🌳](yang-trees/Cisco-IOS-XE-bgp-nbr-oper.html) |
| Cisco-IOS-XE-bgp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-bgp-oper) | [🌳](yang-trees/Cisco-IOS-XE-bgp-oper.html) |
| Cisco-IOS-XE-bgp-rib-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-bgp-rib-oper) | [🌳](yang-trees/Cisco-IOS-XE-bgp-rib-oper.html) |
| Cisco-IOS-XE-bgp-route-oper | - | ❌ No spec | - |
| Cisco-IOS-XE-boot-integrity-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-boot-integrity-oper) | [🌳](yang-trees/Cisco-IOS-XE-boot-integrity-oper.html) |
| Cisco-IOS-XE-breakout-port-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-breakout-port-oper) | [🌳](yang-trees/Cisco-IOS-XE-breakout-port-oper.html) |
| Cisco-IOS-XE-bridge-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-bridge-oper) | [🌳](yang-trees/Cisco-IOS-XE-bridge-oper.html) |
| Cisco-IOS-XE-cable-diag-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-cable-diag-oper) | [🌳](yang-trees/Cisco-IOS-XE-cable-diag-oper.html) |
| Cisco-IOS-XE-cdp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-cdp-oper) | [🌳](yang-trees/Cisco-IOS-XE-cdp-oper.html) |
| Cisco-IOS-XE-cellwan-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-cellwan-oper) | [🌳](yang-trees/Cisco-IOS-XE-cellwan-oper.html) |
| Cisco-IOS-XE-cfm-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-cfm-oper) | [🌳](yang-trees/Cisco-IOS-XE-cfm-oper.html) |
| Cisco-IOS-XE-checkpoint-archive-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-checkpoint-archive-oper) | [🌳](yang-trees/Cisco-IOS-XE-checkpoint-archive-oper.html) |
| Cisco-IOS-XE-cloud-services-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-cloud-services-oper) | [🌳](yang-trees/Cisco-IOS-XE-cloud-services-oper.html) |
| Cisco-IOS-XE-controller-shdsl-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-controller-shdsl-oper) | [🌳](yang-trees/Cisco-IOS-XE-controller-shdsl-oper.html) |
| Cisco-IOS-XE-controller-t1e1-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-controller-t1e1-oper) | [🌳](yang-trees/Cisco-IOS-XE-controller-t1e1-oper.html) |
| Cisco-IOS-XE-controller-vdsl-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-controller-vdsl-oper) | [🌳](yang-trees/Cisco-IOS-XE-controller-vdsl-oper.html) |
| Cisco-IOS-XE-crypto-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-crypto-oper) | [🌳](yang-trees/Cisco-IOS-XE-crypto-oper.html) |
| Cisco-IOS-XE-crypto-pki-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-crypto-pki-oper) | [🌳](yang-trees/Cisco-IOS-XE-crypto-pki-oper.html) |
| Cisco-IOS-XE-device-hardware-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-device-hardware-oper) | [🌳](yang-trees/Cisco-IOS-XE-device-hardware-oper.html) |
| Cisco-IOS-XE-dhcp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-dhcp-oper) | [🌳](yang-trees/Cisco-IOS-XE-dhcp-oper.html) |
| Cisco-IOS-XE-dhcp-security-track-server-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-dhcp-security-track-server-oper) | [🌳](yang-trees/Cisco-IOS-XE-dhcp-security-track-server-oper.html) |
| Cisco-IOS-XE-diffserv-target-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-diffserv-target-oper) | [🌳](yang-trees/Cisco-IOS-XE-diffserv-target-oper.html) |
| Cisco-IOS-XE-digital-io-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-digital-io-oper) | [🌳](yang-trees/Cisco-IOS-XE-digital-io-oper.html) |
| Cisco-IOS-XE-dlr-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-dlr-oper) | [🌳](yang-trees/Cisco-IOS-XE-dlr-oper.html) |
| Cisco-IOS-XE-dns-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-dns-oper) | [🌳](yang-trees/Cisco-IOS-XE-dns-oper.html) |
| Cisco-IOS-XE-dre-cp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-dre-cp-oper) | [🌳](yang-trees/Cisco-IOS-XE-dre-cp-oper.html) |
| Cisco-IOS-XE-dre-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-dre-oper) | [🌳](yang-trees/Cisco-IOS-XE-dre-oper.html) |
| Cisco-IOS-XE-eem-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-eem-oper) | [🌳](yang-trees/Cisco-IOS-XE-eem-oper.html) |
| Cisco-IOS-XE-efp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-efp-oper) | [🌳](yang-trees/Cisco-IOS-XE-efp-oper.html) |
| Cisco-IOS-XE-eigrp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-eigrp-oper) | [🌳](yang-trees/Cisco-IOS-XE-eigrp-oper.html) |
| Cisco-IOS-XE-embedded-ap-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-embedded-ap-oper) | [🌳](yang-trees/Cisco-IOS-XE-embedded-ap-oper.html) |
| Cisco-IOS-XE-endpoint-tracker-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-endpoint-tracker-oper) | [🌳](yang-trees/Cisco-IOS-XE-endpoint-tracker-oper.html) |
| Cisco-IOS-XE-environment-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-environment-oper) | [🌳](yang-trees/Cisco-IOS-XE-environment-oper.html) |
| Cisco-IOS-XE-eogre-tunnel-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-eogre-tunnel-oper) | [🌳](yang-trees/Cisco-IOS-XE-eogre-tunnel-oper.html) |
| Cisco-IOS-XE-evpn-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-evpn-oper) | [🌳](yang-trees/Cisco-IOS-XE-evpn-oper.html) |
| Cisco-IOS-XE-fib-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-fib-oper) | [🌳](yang-trees/Cisco-IOS-XE-fib-oper.html) |
| Cisco-IOS-XE-flow-monitor-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-flow-monitor-oper) | [🌳](yang-trees/Cisco-IOS-XE-flow-monitor-oper.html) |
| Cisco-IOS-XE-fw-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-fw-oper) | [🌳](yang-trees/Cisco-IOS-XE-fw-oper.html) |
| Cisco-IOS-XE-fwd-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-fwd-oper) | [🌳](yang-trees/Cisco-IOS-XE-fwd-oper.html) |
| Cisco-IOS-XE-geo-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-geo-oper) | [🌳](yang-trees/Cisco-IOS-XE-geo-oper.html) |
| Cisco-IOS-XE-gir-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-gir-oper) | [🌳](yang-trees/Cisco-IOS-XE-gir-oper.html) |
| Cisco-IOS-XE-gnss-dr-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-gnss-dr-oper) | [🌳](yang-trees/Cisco-IOS-XE-gnss-dr-oper.html) |
| Cisco-IOS-XE-gnss-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-gnss-oper) | [🌳](yang-trees/Cisco-IOS-XE-gnss-oper.html) |
| Cisco-IOS-XE-group-policy-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-group-policy-oper) | [🌳](yang-trees/Cisco-IOS-XE-group-policy-oper.html) |
| Cisco-IOS-XE-ha-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ha-oper) | [🌳](yang-trees/Cisco-IOS-XE-ha-oper.html) |
| Cisco-IOS-XE-hsr-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-hsr-oper) | [🌳](yang-trees/Cisco-IOS-XE-hsr-oper.html) |
| Cisco-IOS-XE-hsrp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-hsrp-oper) | [🌳](yang-trees/Cisco-IOS-XE-hsrp-oper.html) |
| Cisco-IOS-XE-identity-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-identity-oper) | [🌳](yang-trees/Cisco-IOS-XE-identity-oper.html) |
| Cisco-IOS-XE-ignition-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ignition-oper) | [🌳](yang-trees/Cisco-IOS-XE-ignition-oper.html) |
| Cisco-IOS-XE-install-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-install-oper) | [🌳](yang-trees/Cisco-IOS-XE-install-oper.html) |
| Cisco-IOS-XE-interfaces-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-interfaces-oper) | [🌳](yang-trees/Cisco-IOS-XE-interfaces-oper.html) |
| Cisco-IOS-XE-ip-arp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ip-arp-oper) | [🌳](yang-trees/Cisco-IOS-XE-ip-arp-oper.html) |
| Cisco-IOS-XE-ip-sla-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ip-sla-oper) | [🌳](yang-trees/Cisco-IOS-XE-ip-sla-oper.html) |
| Cisco-IOS-XE-ipv6-nd-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ipv6-nd-oper) | [🌳](yang-trees/Cisco-IOS-XE-ipv6-nd-oper.html) |
| Cisco-IOS-XE-ipv6-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ipv6-oper) | [🌳](yang-trees/Cisco-IOS-XE-ipv6-oper.html) |
| Cisco-IOS-XE-isdn-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-isdn-oper) | [🌳](yang-trees/Cisco-IOS-XE-isdn-oper.html) |
| Cisco-IOS-XE-isis-intf-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-isis-intf-oper) | [🌳](yang-trees/Cisco-IOS-XE-isis-intf-oper.html) |
| Cisco-IOS-XE-isis-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-isis-oper) | [🌳](yang-trees/Cisco-IOS-XE-isis-oper.html) |
| Cisco-IOS-XE-l2nat-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-l2nat-oper) | [🌳](yang-trees/Cisco-IOS-XE-l2nat-oper.html) |
| Cisco-IOS-XE-l2tp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-l2tp-oper) | [🌳](yang-trees/Cisco-IOS-XE-l2tp-oper.html) |
| Cisco-IOS-XE-l2vpn-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-l2vpn-oper) | [🌳](yang-trees/Cisco-IOS-XE-l2vpn-oper.html) |
| Cisco-IOS-XE-lacp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-lacp-oper) | [🌳](yang-trees/Cisco-IOS-XE-lacp-oper.html) |
| Cisco-IOS-XE-line-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-line-oper) | [🌳](yang-trees/Cisco-IOS-XE-line-oper.html) |
| Cisco-IOS-XE-linecard-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-linecard-oper) | [🌳](yang-trees/Cisco-IOS-XE-linecard-oper.html) |
| Cisco-IOS-XE-lisp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-lisp-oper) | [🌳](yang-trees/Cisco-IOS-XE-lisp-oper.html) |
| Cisco-IOS-XE-livetools-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-livetools-oper) | [🌳](yang-trees/Cisco-IOS-XE-livetools-oper.html) |
| Cisco-IOS-XE-lldp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-lldp-oper) | [🌳](yang-trees/Cisco-IOS-XE-lldp-oper.html) |
| Cisco-IOS-XE-lorawan-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-lorawan-oper) | [🌳](yang-trees/Cisco-IOS-XE-lorawan-oper.html) |
| Cisco-IOS-XE-lte450-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-lte450-oper) | [🌳](yang-trees/Cisco-IOS-XE-lte450-oper.html) |
| Cisco-IOS-XE-macsec-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-macsec-oper) | [🌳](yang-trees/Cisco-IOS-XE-macsec-oper.html) |
| Cisco-IOS-XE-matm-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-matm-oper) | [🌳](yang-trees/Cisco-IOS-XE-matm-oper.html) |
| Cisco-IOS-XE-mdt-capabilities-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mdt-capabilities-oper) | [🌳](yang-trees/Cisco-IOS-XE-mdt-capabilities-oper.html) |
| Cisco-IOS-XE-mdt-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mdt-oper) | [🌳](yang-trees/Cisco-IOS-XE-mdt-oper.html) |
| Cisco-IOS-XE-mdt-oper-v2 | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mdt-oper-v2) | [🌳](yang-trees/Cisco-IOS-XE-mdt-oper-v2.html) |
| Cisco-IOS-XE-mdt-stats-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mdt-stats-oper) | [🌳](yang-trees/Cisco-IOS-XE-mdt-stats-oper.html) |
| Cisco-IOS-XE-memory-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-memory-oper) | [🌳](yang-trees/Cisco-IOS-XE-memory-oper.html) |
| Cisco-IOS-XE-meraki-connect-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-meraki-connect-oper) | [🌳](yang-trees/Cisco-IOS-XE-meraki-connect-oper.html) |
| Cisco-IOS-XE-mka-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mka-oper) | [🌳](yang-trees/Cisco-IOS-XE-mka-oper.html) |
| Cisco-IOS-XE-mlppp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mlppp-oper) | [🌳](yang-trees/Cisco-IOS-XE-mlppp-oper.html) |
| Cisco-IOS-XE-mpls-forwarding-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mpls-forwarding-oper) | [🌳](yang-trees/Cisco-IOS-XE-mpls-forwarding-oper.html) |
| Cisco-IOS-XE-mpls-ldp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mpls-ldp-oper) | [🌳](yang-trees/Cisco-IOS-XE-mpls-ldp-oper.html) |
| Cisco-IOS-XE-mpls-te-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mpls-te-oper) | [🌳](yang-trees/Cisco-IOS-XE-mpls-te-oper.html) |
| Cisco-IOS-XE-mroute-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mroute-oper) | [🌳](yang-trees/Cisco-IOS-XE-mroute-oper.html) |
| Cisco-IOS-XE-mrp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-mrp-oper) | [🌳](yang-trees/Cisco-IOS-XE-mrp-oper.html) |
| Cisco-IOS-XE-msdp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-msdp-oper) | [🌳](yang-trees/Cisco-IOS-XE-msdp-oper.html) |
| Cisco-IOS-XE-nat-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-nat-oper) | [🌳](yang-trees/Cisco-IOS-XE-nat-oper.html) |
| Cisco-IOS-XE-ncch-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ncch-oper) | [🌳](yang-trees/Cisco-IOS-XE-ncch-oper.html) |
| Cisco-IOS-XE-netconf-diag-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-netconf-diag-oper) | [🌳](yang-trees/Cisco-IOS-XE-netconf-diag-oper.html) |
| Cisco-IOS-XE-ntp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ntp-oper) | [🌳](yang-trees/Cisco-IOS-XE-ntp-oper.html) |
| Cisco-IOS-XE-nve-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-nve-oper) | [🌳](yang-trees/Cisco-IOS-XE-nve-oper.html) |
| Cisco-IOS-XE-nwpi-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-nwpi-oper) | [🌳](yang-trees/Cisco-IOS-XE-nwpi-oper.html) |
| Cisco-IOS-XE-omp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-omp-oper) | [🌳](yang-trees/Cisco-IOS-XE-omp-oper.html) |
| Cisco-IOS-XE-ospf-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ospf-oper) | [🌳](yang-trees/Cisco-IOS-XE-ospf-oper.html) |
| Cisco-IOS-XE-perf-measure-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-perf-measure-oper) | [🌳](yang-trees/Cisco-IOS-XE-perf-measure-oper.html) |
| Cisco-IOS-XE-pim-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-pim-oper) | [🌳](yang-trees/Cisco-IOS-XE-pim-oper.html) |
| Cisco-IOS-XE-platform-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-platform-oper) | [🌳](yang-trees/Cisco-IOS-XE-platform-oper.html) |
| Cisco-IOS-XE-platform-software-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-platform-software-oper) | [🌳](yang-trees/Cisco-IOS-XE-platform-software-oper.html) |
| Cisco-IOS-XE-poe-health-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-poe-health-oper) | [🌳](yang-trees/Cisco-IOS-XE-poe-health-oper.html) |
| Cisco-IOS-XE-poe-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-poe-oper) | [🌳](yang-trees/Cisco-IOS-XE-poe-oper.html) |
| Cisco-IOS-XE-policymap-target-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-policymap-target-oper) | [🌳](yang-trees/Cisco-IOS-XE-policymap-target-oper.html) |
| Cisco-IOS-XE-ppp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ppp-oper) | [🌳](yang-trees/Cisco-IOS-XE-ppp-oper.html) |
| Cisco-IOS-XE-process-cpu-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-process-cpu-oper) | [🌳](yang-trees/Cisco-IOS-XE-process-cpu-oper.html) |
| Cisco-IOS-XE-process-memory-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-process-memory-oper) | [🌳](yang-trees/Cisco-IOS-XE-process-memory-oper.html) |
| Cisco-IOS-XE-prp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-prp-oper) | [🌳](yang-trees/Cisco-IOS-XE-prp-oper.html) |
| Cisco-IOS-XE-psecure-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-psecure-oper) | [🌳](yang-trees/Cisco-IOS-XE-psecure-oper.html) |
| Cisco-IOS-XE-qfp-appqoe-dp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-qfp-appqoe-dp-oper) | [🌳](yang-trees/Cisco-IOS-XE-qfp-appqoe-dp-oper.html) |
| Cisco-IOS-XE-qfp-classification-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-qfp-classification-oper) | [🌳](yang-trees/Cisco-IOS-XE-qfp-classification-oper.html) |
| Cisco-IOS-XE-qfp-crypto-dp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-qfp-crypto-dp-oper) | [🌳](yang-trees/Cisco-IOS-XE-qfp-crypto-dp-oper.html) |
| Cisco-IOS-XE-qfp-dp-cmn-stats-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-qfp-dp-cmn-stats-oper) | [🌳](yang-trees/Cisco-IOS-XE-qfp-dp-cmn-stats-oper.html) |
| Cisco-IOS-XE-qfp-resource-utilization-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-qfp-resource-utilization-oper) | [🌳](yang-trees/Cisco-IOS-XE-qfp-resource-utilization-oper.html) |
| Cisco-IOS-XE-qfp-stats-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-qfp-stats-oper) | [🌳](yang-trees/Cisco-IOS-XE-qfp-stats-oper.html) |
| Cisco-IOS-XE-rawsocket-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-rawsocket-oper) | [🌳](yang-trees/Cisco-IOS-XE-rawsocket-oper.html) |
| Cisco-IOS-XE-rg-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-rg-oper) | [🌳](yang-trees/Cisco-IOS-XE-rg-oper.html) |
| Cisco-IOS-XE-rif-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-rif-oper) | [🌳](yang-trees/Cisco-IOS-XE-rif-oper.html) |
| Cisco-IOS-XE-scada-gw-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-scada-gw-oper) | [🌳](yang-trees/Cisco-IOS-XE-scada-gw-oper.html) |
| Cisco-IOS-XE-sd-vxlan-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-sd-vxlan-oper) | [🌳](yang-trees/Cisco-IOS-XE-sd-vxlan-oper.html) |
| Cisco-IOS-XE-sdwan-aaa-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-sdwan-aaa-oper) | [🌳](yang-trees/Cisco-IOS-XE-sdwan-aaa-oper.html) |
| Cisco-IOS-XE-sdwan-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-sdwan-oper) | [🌳](yang-trees/Cisco-IOS-XE-sdwan-oper.html) |
| Cisco-IOS-XE-service-chain-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-service-chain-oper) | [🌳](yang-trees/Cisco-IOS-XE-service-chain-oper.html) |
| Cisco-IOS-XE-service-insertion-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-service-insertion-oper) | [🌳](yang-trees/Cisco-IOS-XE-service-insertion-oper.html) |
| Cisco-IOS-XE-spanning-tree-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-spanning-tree-oper) | [🌳](yang-trees/Cisco-IOS-XE-spanning-tree-oper.html) |
| Cisco-IOS-XE-stack-member-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-stack-member-oper) | [🌳](yang-trees/Cisco-IOS-XE-stack-member-oper.html) |
| Cisco-IOS-XE-stack-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-stack-oper) | [🌳](yang-trees/Cisco-IOS-XE-stack-oper.html) |
| Cisco-IOS-XE-stacking-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-stacking-oper) | [🌳](yang-trees/Cisco-IOS-XE-stacking-oper.html) |
| Cisco-IOS-XE-steering-policy-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-steering-policy-oper) | [🌳](yang-trees/Cisco-IOS-XE-steering-policy-oper.html) |
| Cisco-IOS-XE-switch-cp-svl-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-switch-cp-svl-oper) | [🌳](yang-trees/Cisco-IOS-XE-switch-cp-svl-oper.html) |
| Cisco-IOS-XE-switch-dp-mac-learning-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-switch-dp-mac-learning-oper) | [🌳](yang-trees/Cisco-IOS-XE-switch-dp-mac-learning-oper.html) |
| Cisco-IOS-XE-switch-dp-punt-inject-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-switch-dp-punt-inject-oper) | [🌳](yang-trees/Cisco-IOS-XE-switch-dp-punt-inject-oper.html) |
| Cisco-IOS-XE-switch-dp-resources-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-switch-dp-resources-oper) | [🌳](yang-trees/Cisco-IOS-XE-switch-dp-resources-oper.html) |
| Cisco-IOS-XE-switch-ptp-dp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-switch-ptp-dp-oper) | [🌳](yang-trees/Cisco-IOS-XE-switch-ptp-dp-oper.html) |
| Cisco-IOS-XE-switch-ptp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-switch-ptp-oper) | [🌳](yang-trees/Cisco-IOS-XE-switch-ptp-oper.html) |
| Cisco-IOS-XE-switchport-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-switchport-oper) | [🌳](yang-trees/Cisco-IOS-XE-switchport-oper.html) |
| Cisco-IOS-XE-system-integrity-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-system-integrity-oper) | [🌳](yang-trees/Cisco-IOS-XE-system-integrity-oper.html) |
| Cisco-IOS-XE-tcam-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-tcam-oper) | [🌳](yang-trees/Cisco-IOS-XE-tcam-oper.html) |
| Cisco-IOS-XE-teyes-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-teyes-oper) | [🌳](yang-trees/Cisco-IOS-XE-teyes-oper.html) |
| Cisco-IOS-XE-transceiver-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-transceiver-oper) | [🌳](yang-trees/Cisco-IOS-XE-transceiver-oper.html) |
| Cisco-IOS-XE-trustsec-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-trustsec-oper) | [🌳](yang-trees/Cisco-IOS-XE-trustsec-oper.html) |
| Cisco-IOS-XE-tunnel-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-tunnel-oper) | [🌳](yang-trees/Cisco-IOS-XE-tunnel-oper.html) |
| Cisco-IOS-XE-ucse-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ucse-oper) | [🌳](yang-trees/Cisco-IOS-XE-ucse-oper.html) |
| Cisco-IOS-XE-udld-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-udld-oper) | [🌳](yang-trees/Cisco-IOS-XE-udld-oper.html) |
| Cisco-IOS-XE-uidp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-uidp-oper) | [🌳](yang-trees/Cisco-IOS-XE-uidp-oper.html) |
| Cisco-IOS-XE-umbrella-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-umbrella-oper) | [🌳](yang-trees/Cisco-IOS-XE-umbrella-oper.html) |
| Cisco-IOS-XE-umbrella-oper-dp | Operational, Events | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-umbrella-oper-dp) [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-umbrella-oper-dp) | [🌳](yang-trees/Cisco-IOS-XE-umbrella-oper-dp.html) |
| Cisco-IOS-XE-uplink-autoconfig-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-uplink-autoconfig-oper) | [🌳](yang-trees/Cisco-IOS-XE-uplink-autoconfig-oper.html) |
| Cisco-IOS-XE-utd-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-utd-oper) | [🌳](yang-trees/Cisco-IOS-XE-utd-oper.html) |
| Cisco-IOS-XE-vdsp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-vdsp-oper) | [🌳](yang-trees/Cisco-IOS-XE-vdsp-oper.html) |
| Cisco-IOS-XE-vlan-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-vlan-oper) | [🌳](yang-trees/Cisco-IOS-XE-vlan-oper.html) |
| Cisco-IOS-XE-voice-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-voice-oper) | [🌳](yang-trees/Cisco-IOS-XE-voice-oper.html) |
| Cisco-IOS-XE-vrf-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-vrf-oper) | [🌳](yang-trees/Cisco-IOS-XE-vrf-oper.html) |
| Cisco-IOS-XE-vrrp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-vrrp-oper) | [🌳](yang-trees/Cisco-IOS-XE-vrrp-oper.html) |
| Cisco-IOS-XE-wireless-access-point-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-access-point-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-access-point-oper.html) |
| Cisco-IOS-XE-wireless-afc-cloud-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-afc-cloud-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-afc-cloud-oper.html) |
| Cisco-IOS-XE-wireless-afc-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-afc-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-afc-oper.html) |
| Cisco-IOS-XE-wireless-ap-global-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-ap-global-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-ap-global-oper.html) |
| Cisco-IOS-XE-wireless-awips-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-awips-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-awips-oper.html) |
| Cisco-IOS-XE-wireless-ble-ltx-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-ble-ltx-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-ble-ltx-oper.html) |
| Cisco-IOS-XE-wireless-ble-mgmt-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-ble-mgmt-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-ble-mgmt-oper.html) |
| Cisco-IOS-XE-wireless-cisco-spaces-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-cisco-spaces-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-cisco-spaces-oper.html) |
| Cisco-IOS-XE-wireless-client-global-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-client-global-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-client-global-oper.html) |
| Cisco-IOS-XE-wireless-client-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-client-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-client-oper.html) |
| Cisco-IOS-XE-wireless-cts-sxp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-cts-sxp-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-cts-sxp-oper.html) |
| Cisco-IOS-XE-wireless-general-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-general-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-general-oper.html) |
| Cisco-IOS-XE-wireless-geolocation-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-geolocation-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-geolocation-oper.html) |
| Cisco-IOS-XE-wireless-hyperlocation-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-hyperlocation-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-hyperlocation-oper.html) |
| Cisco-IOS-XE-wireless-lisp-agent-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-lisp-agent-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-lisp-agent-oper.html) |
| Cisco-IOS-XE-wireless-location-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-location-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-location-oper.html) |
| Cisco-IOS-XE-wireless-mcast-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mcast-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mcast-oper.html) |
| Cisco-IOS-XE-wireless-mdns-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mdns-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mdns-oper.html) |
| Cisco-IOS-XE-wireless-mesh-global-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mesh-global-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mesh-global-oper.html) |
| Cisco-IOS-XE-wireless-mesh-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mesh-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mesh-oper.html) |
| Cisco-IOS-XE-wireless-mobility-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mobility-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mobility-oper.html) |
| Cisco-IOS-XE-wireless-nmsp-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-nmsp-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-nmsp-oper.html) |
| Cisco-IOS-XE-wireless-rfid-global-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rfid-global-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rfid-global-oper.html) |
| Cisco-IOS-XE-wireless-rfid-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rfid-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rfid-oper.html) |
| Cisco-IOS-XE-wireless-rogue-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rogue-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rogue-oper.html) |
| Cisco-IOS-XE-wireless-rrm-emul-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rrm-emul-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rrm-emul-oper.html) |
| Cisco-IOS-XE-wireless-rrm-global-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rrm-global-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rrm-global-oper.html) |
| Cisco-IOS-XE-wireless-rrm-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rrm-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rrm-oper.html) |
| Cisco-IOS-XE-wireless-rule-mdns-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rule-mdns-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rule-mdns-oper.html) |
| Cisco-IOS-XE-wireless-sdavc-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-sdavc-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-sdavc-oper.html) |
| Cisco-IOS-XE-wireless-sisf-global-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-sisf-global-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-sisf-global-oper.html) |
| Cisco-IOS-XE-wireless-tunnel-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-tunnel-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-tunnel-oper.html) |
| Cisco-IOS-XE-wireless-urwbnet-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-urwbnet-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-urwbnet-oper.html) |
| Cisco-IOS-XE-wireless-wlan-global-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-wlan-global-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-wlan-global-oper.html) |
| Cisco-IOS-XE-wpan-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wpan-oper) | [🌳](yang-trees/Cisco-IOS-XE-wpan-oper.html) |
| Cisco-IOS-XE-yang-interfaces-oper | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-yang-interfaces-oper) | [🌳](yang-trees/Cisco-IOS-XE-yang-interfaces-oper.html) |

### RPC (63 modules)

| Module | Categories | Spec Links | Tree |
|--------|------------|------------|------|
| Cisco-IOS-XE-aaa-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-aaa-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-aaa-actions-rpc.html) |
| Cisco-IOS-XE-aaa-rpc | - | ❌ No spec | - |
| Cisco-IOS-XE-arp-rpc | - | ❌ No spec | - |
| Cisco-IOS-XE-bgp-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-bgp-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-bgp-actions-rpc.html) |
| Cisco-IOS-XE-bgp-rpc | - | ❌ No spec | - |
| Cisco-IOS-XE-cable-diag-rpc | - | ❌ No spec | [🌳](yang-trees/Cisco-IOS-XE-cable-diag-rpc.html) |
| Cisco-IOS-XE-cellular-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-cellular-rpc) | [🌳](yang-trees/Cisco-IOS-XE-cellular-rpc.html) |
| Cisco-IOS-XE-chassis-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-chassis-rpc) | [🌳](yang-trees/Cisco-IOS-XE-chassis-rpc.html) |
| Cisco-IOS-XE-cli-preview-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-cli-preview-rpc) | [🌳](yang-trees/Cisco-IOS-XE-cli-preview-rpc.html) |
| Cisco-IOS-XE-cli-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-cli-rpc) | [🌳](yang-trees/Cisco-IOS-XE-cli-rpc.html) |
| Cisco-IOS-XE-cloud-services-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-cloud-services-rpc) | [🌳](yang-trees/Cisco-IOS-XE-cloud-services-rpc.html) |
| Cisco-IOS-XE-crypto-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-crypto-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-crypto-actions-rpc.html) |
| Cisco-IOS-XE-crypto-rpc | - | ❌ No spec | - |
| Cisco-IOS-XE-cts-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-cts-rpc) | [🌳](yang-trees/Cisco-IOS-XE-cts-rpc.html) |
| Cisco-IOS-XE-cwan-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-cwan-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-cwan-actions-rpc.html) |
| Cisco-IOS-XE-cwan-fw-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-cwan-fw-rpc) | [🌳](yang-trees/Cisco-IOS-XE-cwan-fw-rpc.html) |
| Cisco-IOS-XE-dhcp-rpc | - | ❌ No spec | - |
| Cisco-IOS-XE-embedded-ap-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-embedded-ap-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-embedded-ap-actions-rpc.html) |
| Cisco-IOS-XE-ethernet-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-ethernet-rpc) | [🌳](yang-trees/Cisco-IOS-XE-ethernet-rpc.html) |
| Cisco-IOS-XE-factory-reset-secure-rpc | - | ❌ No spec | [🌳](yang-trees/Cisco-IOS-XE-factory-reset-secure-rpc.html) |
| Cisco-IOS-XE-flow-rpc | - | ❌ No spec | [🌳](yang-trees/Cisco-IOS-XE-flow-rpc.html) |
| Cisco-IOS-XE-geo-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-geo-rpc) | [🌳](yang-trees/Cisco-IOS-XE-geo-rpc.html) |
| Cisco-IOS-XE-install-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-install-rpc) | [🌳](yang-trees/Cisco-IOS-XE-install-rpc.html) |
| Cisco-IOS-XE-line-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-line-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-line-actions-rpc.html) |
| Cisco-IOS-XE-livetools-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-livetools-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-livetools-actions-rpc.html) |
| Cisco-IOS-XE-logging-ios-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-logging-ios-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-logging-ios-actions-rpc.html) |
| Cisco-IOS-XE-meraki-leds-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-meraki-leds-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-meraki-leds-actions-rpc.html) |
| Cisco-IOS-XE-multicast-rpc | - | ❌ No spec | - |
| Cisco-IOS-XE-netconf-diag-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-netconf-diag-rpc) | [🌳](yang-trees/Cisco-IOS-XE-netconf-diag-rpc.html) |
| Cisco-IOS-XE-nwpi-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-nwpi-rpc) | [🌳](yang-trees/Cisco-IOS-XE-nwpi-rpc.html) |
| Cisco-IOS-XE-omp-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-omp-rpc) | [🌳](yang-trees/Cisco-IOS-XE-omp-rpc.html) |
| Cisco-IOS-XE-ospf-rpc | - | ❌ No spec | - |
| Cisco-IOS-XE-platform-rpc | - | ❌ No spec | - |
| Cisco-IOS-XE-port-bounce-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-port-bounce-rpc) | [🌳](yang-trees/Cisco-IOS-XE-port-bounce-rpc.html) |
| Cisco-IOS-XE-port-security-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-port-security-rpc) | [🌳](yang-trees/Cisco-IOS-XE-port-security-rpc.html) |
| Cisco-IOS-XE-power-supply-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-power-supply-rpc) | [🌳](yang-trees/Cisco-IOS-XE-power-supply-rpc.html) |
| Cisco-IOS-XE-rescue-config-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-rescue-config-rpc) | [🌳](yang-trees/Cisco-IOS-XE-rescue-config-rpc.html) |
| Cisco-IOS-XE-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-rpc) | [🌳](yang-trees/Cisco-IOS-XE-rpc.html) |
| Cisco-IOS-XE-sdwan-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-sdwan-rpc) | [🌳](yang-trees/Cisco-IOS-XE-sdwan-rpc.html) |
| Cisco-IOS-XE-sslproxy-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-sslproxy-rpc) | [🌳](yang-trees/Cisco-IOS-XE-sslproxy-rpc.html) |
| Cisco-IOS-XE-stack-power-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-stack-power-rpc) | [🌳](yang-trees/Cisco-IOS-XE-stack-power-rpc.html) |
| Cisco-IOS-XE-switch-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-switch-rpc) | [🌳](yang-trees/Cisco-IOS-XE-switch-rpc.html) |
| Cisco-IOS-XE-tech-support-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-tech-support-rpc) | [🌳](yang-trees/Cisco-IOS-XE-tech-support-rpc.html) |
| Cisco-IOS-XE-trace-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-trace-rpc) | [🌳](yang-trees/Cisco-IOS-XE-trace-rpc.html) |
| Cisco-IOS-XE-uac-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-uac-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-uac-actions-rpc.html) |
| Cisco-IOS-XE-ucse-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-ucse-rpc) | [🌳](yang-trees/Cisco-IOS-XE-ucse-rpc.html) |
| Cisco-IOS-XE-umbrella-rpc | - | ❌ No spec | [🌳](yang-trees/Cisco-IOS-XE-umbrella-rpc.html) |
| Cisco-IOS-XE-utd-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-utd-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-utd-actions-rpc.html) |
| Cisco-IOS-XE-utd-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-utd-rpc) | [🌳](yang-trees/Cisco-IOS-XE-utd-rpc.html) |
| Cisco-IOS-XE-verify-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-verify-rpc) | [🌳](yang-trees/Cisco-IOS-XE-verify-rpc.html) |
| Cisco-IOS-XE-voice-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-voice-rpc) | [🌳](yang-trees/Cisco-IOS-XE-voice-rpc.html) |
| Cisco-IOS-XE-wireless-access-point-cfg-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-access-point-cfg-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-access-point-cfg-rpc.html) |
| Cisco-IOS-XE-wireless-access-point-cmd-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-access-point-cmd-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-access-point-cmd-rpc.html) |
| Cisco-IOS-XE-wireless-actions-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-actions-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-actions-rpc.html) |
| Cisco-IOS-XE-wireless-ble-mgmt-cmd-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-ble-mgmt-cmd-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-ble-mgmt-cmd-rpc.html) |
| Cisco-IOS-XE-wireless-client-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-client-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-client-rpc.html) |
| Cisco-IOS-XE-wireless-mesh-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mesh-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mesh-rpc.html) |
| Cisco-IOS-XE-wireless-rogue-authz-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rogue-authz-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rogue-authz-rpc.html) |
| Cisco-IOS-XE-wireless-rrm-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rrm-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rrm-rpc.html) |
| Cisco-IOS-XE-wireless-tech-support-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-wireless-tech-support-rpc) | [🌳](yang-trees/Cisco-IOS-XE-wireless-tech-support-rpc.html) |
| Cisco-IOS-XE-xcopy-rpc | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=Cisco-IOS-XE-xcopy-rpc) | [🌳](yang-trees/Cisco-IOS-XE-xcopy-rpc.html) |
| Cisco-IOS-XE-zone-rpc | - | ❌ No spec | [🌳](yang-trees/Cisco-IOS-XE-zone-rpc.html) |
| cisco-ia | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=cisco-ia) | [🌳](yang-trees/cisco-ia.html) |

### CFG (61 modules)

| Module | Categories | Spec Links | Tree |
|--------|------------|------------|------|
| Cisco-IOS-XE-app-hosting-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-app-hosting-cfg) | [🌳](yang-trees/Cisco-IOS-XE-app-hosting-cfg.html) |
| Cisco-IOS-XE-aws-cw-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-aws-cw-cfg) | [🌳](yang-trees/Cisco-IOS-XE-aws-cw-cfg.html) |
| Cisco-IOS-XE-aws-s3-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-aws-s3-cfg) | [🌳](yang-trees/Cisco-IOS-XE-aws-s3-cfg.html) |
| Cisco-IOS-XE-cloud-services-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-cloud-services-cfg) | [🌳](yang-trees/Cisco-IOS-XE-cloud-services-cfg.html) |
| Cisco-IOS-XE-ctrl-mng-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-ctrl-mng-cfg) | [🌳](yang-trees/Cisco-IOS-XE-ctrl-mng-cfg.html) |
| Cisco-IOS-XE-eigrp-obsolete | - | ❌ No spec | - |
| Cisco-IOS-XE-ethernet-cfm-efp | - | ❌ No spec | - |
| Cisco-IOS-XE-ethernet-oam | - | ❌ No spec | - |
| Cisco-IOS-XE-features | - | ❌ No spec | - |
| Cisco-IOS-XE-gnmi-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-gnmi-cfg) | [🌳](yang-trees/Cisco-IOS-XE-gnmi-cfg.html) |
| Cisco-IOS-XE-grpc-tunnel-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-grpc-tunnel-cfg) | [🌳](yang-trees/Cisco-IOS-XE-grpc-tunnel-cfg.html) |
| Cisco-IOS-XE-hsrp | - | ❌ No spec | - |
| Cisco-IOS-XE-interfaces | - | ❌ No spec | - |
| Cisco-IOS-XE-ip | - | ❌ No spec | - |
| Cisco-IOS-XE-ipv6 | - | ❌ No spec | - |
| Cisco-IOS-XE-license | - | ❌ No spec | - |
| Cisco-IOS-XE-line | - | ❌ No spec | - |
| Cisco-IOS-XE-location | - | ❌ No spec | - |
| Cisco-IOS-XE-logging | - | ❌ No spec | - |
| Cisco-IOS-XE-mdt-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-mdt-cfg) | [🌳](yang-trees/Cisco-IOS-XE-mdt-cfg.html) |
| Cisco-IOS-XE-ncch-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-ncch-cfg) | [🌳](yang-trees/Cisco-IOS-XE-ncch-cfg.html) |
| Cisco-IOS-XE-ospf-obsolete | - | ❌ No spec | - |
| Cisco-IOS-XE-parser | - | ❌ No spec | - |
| Cisco-IOS-XE-qfp-stats | Operational | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-qfp-stats) | [🌳](yang-trees/Cisco-IOS-XE-qfp-stats.html) |
| Cisco-IOS-XE-sip-ua | - | ❌ No spec | - |
| Cisco-IOS-XE-sisf | - | ❌ No spec | - |
| Cisco-IOS-XE-sslproxy-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-sslproxy-cfg) | [🌳](yang-trees/Cisco-IOS-XE-sslproxy-cfg.html) |
| Cisco-IOS-XE-transceiver-monitor | - | ❌ No spec | - |
| Cisco-IOS-XE-transport | - | ❌ No spec | - |
| Cisco-IOS-XE-voice-class | - | ❌ No spec | - |
| Cisco-IOS-XE-voice-dspfarm | - | ❌ No spec | - |
| Cisco-IOS-XE-voice-register | - | ❌ No spec | - |
| Cisco-IOS-XE-wireless-ap-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-ap-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-ap-cfg.html) |
| Cisco-IOS-XE-wireless-apf-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-apf-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-apf-cfg.html) |
| Cisco-IOS-XE-wireless-cts-sxp-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-cts-sxp-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-cts-sxp-cfg.html) |
| Cisco-IOS-XE-wireless-dot11-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-dot11-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-dot11-cfg.html) |
| Cisco-IOS-XE-wireless-dot15-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-dot15-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-dot15-cfg.html) |
| Cisco-IOS-XE-wireless-fabric-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-fabric-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-fabric-cfg.html) |
| Cisco-IOS-XE-wireless-flex-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-flex-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-flex-cfg.html) |
| Cisco-IOS-XE-wireless-fqdn-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-fqdn-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-fqdn-cfg.html) |
| Cisco-IOS-XE-wireless-general-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-general-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-general-cfg.html) |
| Cisco-IOS-XE-wireless-hotspot-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-hotspot-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-hotspot-cfg.html) |
| Cisco-IOS-XE-wireless-location-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-location-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-location-cfg.html) |
| Cisco-IOS-XE-wireless-mesh-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mesh-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mesh-cfg.html) |
| Cisco-IOS-XE-wireless-mobility-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mobility-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mobility-cfg.html) |
| Cisco-IOS-XE-wireless-mstream-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-mstream-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-mstream-cfg.html) |
| Cisco-IOS-XE-wireless-power-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-power-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-power-cfg.html) |
| Cisco-IOS-XE-wireless-radio-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-radio-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-radio-cfg.html) |
| Cisco-IOS-XE-wireless-rf-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rf-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rf-cfg.html) |
| Cisco-IOS-XE-wireless-rfid-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rfid-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rfid-cfg.html) |
| Cisco-IOS-XE-wireless-rlan-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rlan-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rlan-cfg.html) |
| Cisco-IOS-XE-wireless-rogue-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rogue-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rogue-cfg.html) |
| Cisco-IOS-XE-wireless-rrm-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rrm-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rrm-cfg.html) |
| Cisco-IOS-XE-wireless-rule-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-rule-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-rule-cfg.html) |
| Cisco-IOS-XE-wireless-security-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-security-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-security-cfg.html) |
| Cisco-IOS-XE-wireless-site-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-site-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-site-cfg.html) |
| Cisco-IOS-XE-wireless-tunnel-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-tunnel-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-tunnel-cfg.html) |
| Cisco-IOS-XE-wireless-urwb-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-urwb-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-urwb-cfg.html) |
| Cisco-IOS-XE-wireless-wat-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-wat-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-wat-cfg.html) |
| Cisco-IOS-XE-wireless-wlan-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-wireless-wlan-cfg) | [🌳](yang-trees/Cisco-IOS-XE-wireless-wlan-cfg.html) |
| Cisco-IOS-XE-yang-interfaces-cfg | Configuration | [Configuration](swagger-cfg-model/index-v2.html#spec=Cisco-IOS-XE-yang-interfaces-cfg) | [🌳](yang-trees/Cisco-IOS-XE-yang-interfaces-cfg.html) |

### OPENCONFIG (95 modules)

| Module | Categories | Spec Links | Tree |
|--------|------------|------------|------|
| openconfig-aaa | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-aaa) | [🌳](yang-trees/openconfig-aaa.html) |
| openconfig-aaa-radius | - | ❌ No spec | - |
| openconfig-aaa-tacacs | - | ❌ No spec | - |
| openconfig-access-points | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-access-points) | [🌳](yang-trees/openconfig-access-points.html) |
| openconfig-acl | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-acl) | [🌳](yang-trees/openconfig-acl.html) |
| openconfig-aft | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-aft) | [🌳](yang-trees/openconfig-aft.html) |
| openconfig-aft-ethernet | - | ❌ No spec | - |
| openconfig-aft-ipv4 | - | ❌ No spec | - |
| openconfig-aft-ipv6 | - | ❌ No spec | - |
| openconfig-aft-mpls | - | ❌ No spec | - |
| openconfig-aft-network-instance | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-aft-network-instance) | [🌳](yang-trees/openconfig-aft-network-instance.html) |
| openconfig-aft-pf | - | ❌ No spec | - |
| openconfig-aft-state-synced | - | ❌ No spec | - |
| openconfig-alarms | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-alarms) | [🌳](yang-trees/openconfig-alarms.html) |
| openconfig-ap-manager | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-ap-manager) | [🌳](yang-trees/openconfig-ap-manager.html) |
| openconfig-bfd | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-bfd) | [🌳](yang-trees/openconfig-bfd.html) |
| openconfig-bgp | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-bgp) | [🌳](yang-trees/openconfig-bgp.html) |
| openconfig-bgp-errors | - | ❌ No spec | - |
| openconfig-bgp-global | - | ❌ No spec | - |
| openconfig-bgp-neighbor | - | ❌ No spec | - |
| openconfig-bgp-peer-group | - | ❌ No spec | - |
| openconfig-bgp-policy | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-bgp-policy) | [🌳](yang-trees/openconfig-bgp-policy.html) |
| openconfig-ethernet-segments | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-ethernet-segments) | [🌳](yang-trees/openconfig-ethernet-segments.html) |
| openconfig-evpn | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-evpn) | [🌳](yang-trees/openconfig-evpn.html) |
| openconfig-extensions | - | ❌ No spec | - |
| openconfig-if-aggregate | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-if-aggregate) | [🌳](yang-trees/openconfig-if-aggregate.html) |
| openconfig-if-ethernet | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-if-ethernet) | [🌳](yang-trees/openconfig-if-ethernet.html) |
| openconfig-if-ip | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-if-ip) | [🌳](yang-trees/openconfig-if-ip.html) |
| openconfig-if-ip-ext | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-if-ip-ext) | [🌳](yang-trees/openconfig-if-ip-ext.html) |
| openconfig-if-poe | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-if-poe) | [🌳](yang-trees/openconfig-if-poe.html) |
| openconfig-igmp | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-igmp) | [🌳](yang-trees/openconfig-igmp.html) |
| openconfig-interfaces | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-interfaces) | [🌳](yang-trees/openconfig-interfaces.html) |
| openconfig-isis | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-isis) | [🌳](yang-trees/openconfig-isis.html) |
| openconfig-isis-lsp | - | ❌ No spec | - |
| openconfig-isis-policy | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-isis-policy) | [🌳](yang-trees/openconfig-isis-policy.html) |
| openconfig-isis-routing | - | ❌ No spec | - |
| openconfig-keychain | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-keychain) | [🌳](yang-trees/openconfig-keychain.html) |
| openconfig-lacp | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-lacp) | [🌳](yang-trees/openconfig-lacp.html) |
| openconfig-license | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-license) | [🌳](yang-trees/openconfig-license.html) |
| openconfig-lldp | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-lldp) | [🌳](yang-trees/openconfig-lldp.html) |
| openconfig-local-routing | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-local-routing) | [🌳](yang-trees/openconfig-local-routing.html) |
| openconfig-macsec | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-macsec) | [🌳](yang-trees/openconfig-macsec.html) |
| openconfig-messages | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-messages) | [🌳](yang-trees/openconfig-messages.html) |
| openconfig-mpls | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-mpls) | [🌳](yang-trees/openconfig-mpls.html) |
| openconfig-mpls-igp | - | ❌ No spec | - |
| openconfig-mpls-ldp | - | ❌ No spec | - |
| openconfig-mpls-rsvp | - | ❌ No spec | - |
| openconfig-mpls-sr | - | ❌ No spec | - |
| openconfig-mpls-static | - | ❌ No spec | - |
| openconfig-mpls-te | - | ❌ No spec | - |
| openconfig-network-instance | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-network-instance) | [🌳](yang-trees/openconfig-network-instance.html) |
| openconfig-network-instance-l2 | - | ❌ No spec | - |
| openconfig-network-instance-l3 | - | ❌ No spec | - |
| openconfig-network-instance-policy | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-network-instance-policy) | [🌳](yang-trees/openconfig-network-instance-policy.html) |
| openconfig-openflow | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-openflow) | [🌳](yang-trees/openconfig-openflow.html) |
| openconfig-ospf-policy | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-ospf-policy) | [🌳](yang-trees/openconfig-ospf-policy.html) |
| openconfig-ospfv2 | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-ospfv2) | [🌳](yang-trees/openconfig-ospfv2.html) |
| openconfig-ospfv2-area | - | ❌ No spec | - |
| openconfig-ospfv2-area-interface | - | ❌ No spec | - |
| openconfig-ospfv2-global | - | ❌ No spec | - |
| openconfig-ospfv2-lsdb | - | ❌ No spec | - |
| openconfig-packet-match | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-packet-match) | [🌳](yang-trees/openconfig-packet-match.html) |
| openconfig-pcep | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-pcep) | [🌳](yang-trees/openconfig-pcep.html) |
| openconfig-pf-forwarding-policies | - | ❌ No spec | - |
| openconfig-pf-interfaces | - | ❌ No spec | - |
| openconfig-pf-path-groups | - | ❌ No spec | - |
| openconfig-pf-srte | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-pf-srte) | [🌳](yang-trees/openconfig-pf-srte.html) |
| openconfig-pim | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-pim) | [🌳](yang-trees/openconfig-pim.html) |
| openconfig-platform | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-platform) | [🌳](yang-trees/openconfig-platform.html) |
| openconfig-platform-cpu | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-platform-cpu) | [🌳](yang-trees/openconfig-platform-cpu.html) |
| openconfig-platform-fan | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-platform-fan) | [🌳](yang-trees/openconfig-platform-fan.html) |
| openconfig-platform-linecard | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-platform-linecard) | [🌳](yang-trees/openconfig-platform-linecard.html) |
| openconfig-platform-port | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-platform-port) | [🌳](yang-trees/openconfig-platform-port.html) |
| openconfig-platform-psu | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-platform-psu) | [🌳](yang-trees/openconfig-platform-psu.html) |
| openconfig-platform-transceiver | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-platform-transceiver) | [🌳](yang-trees/openconfig-platform-transceiver.html) |
| openconfig-policy-forwarding | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-policy-forwarding) | [🌳](yang-trees/openconfig-policy-forwarding.html) |
| openconfig-procmon | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-procmon) | [🌳](yang-trees/openconfig-procmon.html) |
| openconfig-programming-errors | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-programming-errors) | [🌳](yang-trees/openconfig-programming-errors.html) |
| openconfig-rib-bgp | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-rib-bgp) | [🌳](yang-trees/openconfig-rib-bgp.html) |
| openconfig-rib-bgp-attributes | - | ❌ No spec | - |
| openconfig-rib-bgp-ext | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-rib-bgp-ext) | [🌳](yang-trees/openconfig-rib-bgp-ext.html) |
| openconfig-rib-bgp-shared-attributes | - | ❌ No spec | - |
| openconfig-rib-bgp-table-attributes | - | ❌ No spec | - |
| openconfig-rib-bgp-tables | - | ❌ No spec | - |
| openconfig-route-summary | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-route-summary) | [🌳](yang-trees/openconfig-route-summary.html) |
| openconfig-routing-policy | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-routing-policy) | [🌳](yang-trees/openconfig-routing-policy.html) |
| openconfig-segment-routing | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-segment-routing) | [🌳](yang-trees/openconfig-segment-routing.html) |
| openconfig-spanning-tree | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-spanning-tree) | [🌳](yang-trees/openconfig-spanning-tree.html) |
| openconfig-system | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-system) | [🌳](yang-trees/openconfig-system.html) |
| openconfig-system-grpc | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-system-grpc) | [🌳](yang-trees/openconfig-system-grpc.html) |
| openconfig-system-logging | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-system-logging) | [🌳](yang-trees/openconfig-system-logging.html) |
| openconfig-system-terminal | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-system-terminal) | [🌳](yang-trees/openconfig-system-terminal.html) |
| openconfig-vlan | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-vlan) | [🌳](yang-trees/openconfig-vlan.html) |
| openconfig-wifi-mac | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-wifi-mac) | [🌳](yang-trees/openconfig-wifi-mac.html) |
| openconfig-wifi-phy | OpenConfig | [OpenConfig](swagger-openconfig-model/index-v2.html#spec=openconfig-wifi-phy) | [🌳](yang-trees/openconfig-wifi-phy.html) |

### IETF (33 modules)

| Module | Categories | Spec Links | Tree |
|--------|------------|------------|------|
| iana-crypt-hash | - | ❌ No spec | - |
| iana-if-type | - | ❌ No spec | - |
| ietf-datastores | - | ❌ No spec | - |
| ietf-diffserv-action | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-diffserv-action) | [🌳](yang-trees/ietf-diffserv-action.html) |
| ietf-diffserv-classifier | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-diffserv-classifier) | [🌳](yang-trees/ietf-diffserv-classifier.html) |
| ietf-diffserv-policy | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-diffserv-policy) | [🌳](yang-trees/ietf-diffserv-policy.html) |
| ietf-diffserv-target | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-diffserv-target) | [🌳](yang-trees/ietf-diffserv-target.html) |
| ietf-event-notifications | IETF, RPC, Events | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-event-notifications) [RPC](swagger-rpc-model/index-v2.html#spec=ietf-event-notifications) [Events](swagger-events-model/index-v2.html#spec=ietf-event-notifications) | [🌳](yang-trees/ietf-event-notifications.html) |
| ietf-interfaces | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-interfaces) | [🌳](yang-trees/ietf-interfaces.html) |
| ietf-interfaces-ext | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-interfaces-ext) | [🌳](yang-trees/ietf-interfaces-ext.html) |
| ietf-ip | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-ip) | [🌳](yang-trees/ietf-ip.html) |
| ietf-ipv4-unicast-routing | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-ipv4-unicast-routing) | [🌳](yang-trees/ietf-ipv4-unicast-routing.html) |
| ietf-ipv6-unicast-routing | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-ipv6-unicast-routing) | [🌳](yang-trees/ietf-ipv6-unicast-routing.html) |
| ietf-key-chain | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-key-chain) | [🌳](yang-trees/ietf-key-chain.html) |
| ietf-netconf | IETF, RPC | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-netconf) [RPC](swagger-rpc-model/index-v2.html#spec=ietf-netconf) | [🌳](yang-trees/ietf-netconf.html) |
| ietf-netconf-acm | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-netconf-acm) | [🌳](yang-trees/ietf-netconf-acm.html) |
| ietf-netconf-monitoring | IETF, RPC | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-netconf-monitoring) [RPC](swagger-rpc-model/index-v2.html#spec=ietf-netconf-monitoring) | [🌳](yang-trees/ietf-netconf-monitoring.html) |
| ietf-netconf-notifications | IETF, Events | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-netconf-notifications) [Events](swagger-events-model/index-v2.html#spec=ietf-netconf-notifications) | [🌳](yang-trees/ietf-netconf-notifications.html) |
| ietf-netconf-otlp-context | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-netconf-otlp-context) | [🌳](yang-trees/ietf-netconf-otlp-context.html) |
| ietf-netconf-otlp-context-traceparent-version-1.0 | - | ❌ No spec | - |
| ietf-netconf-otlp-context-tracestate-version-1.0 | - | ❌ No spec | - |
| ietf-netconf-with-defaults | - | ❌ No spec | [🌳](yang-trees/ietf-netconf-with-defaults.html) |
| ietf-ospf | IETF, Events | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-ospf) [Events](swagger-events-model/index-v2.html#spec=ietf-ospf) | [🌳](yang-trees/ietf-ospf.html) |
| ietf-restconf | - | ❌ No spec | - |
| ietf-restconf-monitoring | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-restconf-monitoring) | [🌳](yang-trees/ietf-restconf-monitoring.html) |
| ietf-routing | IETF, RPC | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-routing) [RPC](swagger-rpc-model/index-v2.html#spec=ietf-routing) | [🌳](yang-trees/ietf-routing.html) |
| ietf-yang-library | IETF, Events | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-yang-library) [Events](swagger-events-model/index-v2.html#spec=ietf-yang-library) | [🌳](yang-trees/ietf-yang-library.html) |
| ietf-yang-patch | - | ❌ No spec | - |
| ietf-yang-patch-ann | - | ❌ No spec | - |
| ietf-yang-push | IETF, Events | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-yang-push) [Events](swagger-events-model/index-v2.html#spec=ietf-yang-push) | [🌳](yang-trees/ietf-yang-push.html) |
| ietf-yang-schema-mount | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-yang-schema-mount) | [🌳](yang-trees/ietf-yang-schema-mount.html) |
| ietf-yang-smiv2 | - | ❌ No spec | - |
| ietf-yang-structure-ext | IETF | [IETF](swagger-ietf-model/index-v2.html#spec=ietf-yang-structure-ext) | [🌳](yang-trees/ietf-yang-structure-ext.html) |

### EVENTS (41 modules)

| Module | Categories | Spec Links | Tree |
|--------|------------|------------|------|
| Cisco-IOS-XE-aaa-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-aaa-events) | [🌳](yang-trees/Cisco-IOS-XE-aaa-events.html) |
| Cisco-IOS-XE-appqoe-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-appqoe-events) | [🌳](yang-trees/Cisco-IOS-XE-appqoe-events.html) |
| Cisco-IOS-XE-controller-shdsl-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-controller-shdsl-events) | [🌳](yang-trees/Cisco-IOS-XE-controller-shdsl-events.html) |
| Cisco-IOS-XE-crypto-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-crypto-events) | [🌳](yang-trees/Cisco-IOS-XE-crypto-events.html) |
| Cisco-IOS-XE-crypto-pki-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-crypto-pki-events) | [🌳](yang-trees/Cisco-IOS-XE-crypto-pki-events.html) |
| Cisco-IOS-XE-dca-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-dca-events) | [🌳](yang-trees/Cisco-IOS-XE-dca-events.html) |
| Cisco-IOS-XE-endpoint-tracker-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-endpoint-tracker-events) | [🌳](yang-trees/Cisco-IOS-XE-endpoint-tracker-events.html) |
| Cisco-IOS-XE-fib-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-fib-events) | [🌳](yang-trees/Cisco-IOS-XE-fib-events.html) |
| Cisco-IOS-XE-geo-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-geo-events) | [🌳](yang-trees/Cisco-IOS-XE-geo-events.html) |
| Cisco-IOS-XE-hsrp-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-hsrp-events) | [🌳](yang-trees/Cisco-IOS-XE-hsrp-events.html) |
| Cisco-IOS-XE-im-events-oper | Operational, Events | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-im-events-oper) [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-im-events-oper) | [🌳](yang-trees/Cisco-IOS-XE-im-events-oper.html) |
| Cisco-IOS-XE-install-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-install-events) | [🌳](yang-trees/Cisco-IOS-XE-install-events.html) |
| Cisco-IOS-XE-interface-bw-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-interface-bw-events) | [🌳](yang-trees/Cisco-IOS-XE-interface-bw-events.html) |
| Cisco-IOS-XE-ios-events-oper | Operational, Events | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-ios-events-oper) [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-ios-events-oper) | [🌳](yang-trees/Cisco-IOS-XE-ios-events-oper.html) |
| Cisco-IOS-XE-ip-sla-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-ip-sla-events) | [🌳](yang-trees/Cisco-IOS-XE-ip-sla-events.html) |
| Cisco-IOS-XE-line-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-line-events) | [🌳](yang-trees/Cisco-IOS-XE-line-events.html) |
| Cisco-IOS-XE-loop-detect-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-loop-detect-events) | [🌳](yang-trees/Cisco-IOS-XE-loop-detect-events.html) |
| Cisco-IOS-XE-matm-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-matm-events) | [🌳](yang-trees/Cisco-IOS-XE-matm-events.html) |
| Cisco-IOS-XE-mcast-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-mcast-events) | [🌳](yang-trees/Cisco-IOS-XE-mcast-events.html) |
| Cisco-IOS-XE-nat-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-nat-events) | [🌳](yang-trees/Cisco-IOS-XE-nat-events.html) |
| Cisco-IOS-XE-ngfw-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-ngfw-events) | [🌳](yang-trees/Cisco-IOS-XE-ngfw-events.html) |
| Cisco-IOS-XE-ospf-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-ospf-events) | [🌳](yang-trees/Cisco-IOS-XE-ospf-events.html) |
| Cisco-IOS-XE-perf-measure-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-perf-measure-events) | [🌳](yang-trees/Cisco-IOS-XE-perf-measure-events.html) |
| Cisco-IOS-XE-platform-events-oper | Operational, Events | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-platform-events-oper) [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-platform-events-oper) | [🌳](yang-trees/Cisco-IOS-XE-platform-events-oper.html) |
| Cisco-IOS-XE-platform-software-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-platform-software-events) | [🌳](yang-trees/Cisco-IOS-XE-platform-software-events.html) |
| Cisco-IOS-XE-port-bounce-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-port-bounce-events) | [🌳](yang-trees/Cisco-IOS-XE-port-bounce-events.html) |
| Cisco-IOS-XE-qfp-resource-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-qfp-resource-events) | [🌳](yang-trees/Cisco-IOS-XE-qfp-resource-events.html) |
| Cisco-IOS-XE-red-app-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-red-app-events) | [🌳](yang-trees/Cisco-IOS-XE-red-app-events.html) |
| Cisco-IOS-XE-sm-events-oper | Operational, Events | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-sm-events-oper) [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-sm-events-oper) | [🌳](yang-trees/Cisco-IOS-XE-sm-events-oper.html) |
| Cisco-IOS-XE-spanning-tree-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-spanning-tree-events) | [🌳](yang-trees/Cisco-IOS-XE-spanning-tree-events.html) |
| Cisco-IOS-XE-stack-mgr-events-oper | Operational, Events | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-stack-mgr-events-oper) [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-stack-mgr-events-oper) | [🌳](yang-trees/Cisco-IOS-XE-stack-mgr-events-oper.html) |
| Cisco-IOS-XE-tech-support-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-tech-support-events) | [🌳](yang-trees/Cisco-IOS-XE-tech-support-events.html) |
| Cisco-IOS-XE-trace-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-trace-events) | [🌳](yang-trees/Cisco-IOS-XE-trace-events.html) |
| Cisco-IOS-XE-udld-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-udld-events) | [🌳](yang-trees/Cisco-IOS-XE-udld-events.html) |
| Cisco-IOS-XE-utd-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-utd-events) | [🌳](yang-trees/Cisco-IOS-XE-utd-events.html) |
| Cisco-IOS-XE-verify-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-verify-events) | [🌳](yang-trees/Cisco-IOS-XE-verify-events.html) |
| Cisco-IOS-XE-wireless-events-oper | Operational, Events | [Operational](swagger-oper-model/index-v2.html#spec=Cisco-IOS-XE-wireless-events-oper) [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-wireless-events-oper) | [🌳](yang-trees/Cisco-IOS-XE-wireless-events-oper.html) |
| Cisco-IOS-XE-xcopy-events | Events | [Events](swagger-events-model/index-v2.html#spec=Cisco-IOS-XE-xcopy-events) | [🌳](yang-trees/Cisco-IOS-XE-xcopy-events.html) |
| cisco-bridge-domain | RPC, Events, Other | [RPC](swagger-rpc-model/index-v2.html#spec=cisco-bridge-domain) [Events](swagger-events-model/index-v2.html#spec=cisco-bridge-domain) [Other](swagger-other-model/index-v2.html#spec=cisco-bridge-domain) | [🌳](yang-trees/cisco-bridge-domain.html) |
| cisco-pw | Events, Other | [Events](swagger-events-model/index-v2.html#spec=cisco-pw) [Other](swagger-other-model/index-v2.html#spec=cisco-pw) | [🌳](yang-trees/cisco-pw.html) |
| cisco-smart-license | RPC, Events, Other | [RPC](swagger-rpc-model/index-v2.html#spec=cisco-smart-license) [Events](swagger-events-model/index-v2.html#spec=cisco-smart-license) [Other](swagger-other-model/index-v2.html#spec=cisco-smart-license) | [🌳](yang-trees/cisco-smart-license.html) |

### NATIVE (1 modules)

| Module | Categories | Spec Links | Tree |
|--------|------------|------------|------|
| Cisco-IOS-XE-native | - | ❌ No spec | [🌳](yang-trees/Cisco-IOS-XE-native.html) |

### OTHER (32 modules)

| Module | Categories | Spec Links | Tree |
|--------|------------|------------|------|
| cisco-ethernet | Other | [Other](swagger-other-model/index-v2.html#spec=cisco-ethernet) | [🌳](yang-trees/cisco-ethernet.html) |
| cisco-evpn-service | Other | [Other](swagger-other-model/index-v2.html#spec=cisco-evpn-service) | [🌳](yang-trees/cisco-evpn-service.html) |
| cisco-extensions | - | ❌ No spec | - |
| cisco-ospf | - | ❌ No spec | - |
| cisco-policy | - | ❌ No spec | [🌳](yang-trees/cisco-policy.html) |
| cisco-policy-filters | Other | [Other](swagger-other-model/index-v2.html#spec=cisco-policy-filters) | [🌳](yang-trees/cisco-policy-filters.html) |
| cisco-policy-target | - | ❌ No spec | [🌳](yang-trees/cisco-policy-target.html) |
| cisco-routing-ext | - | ❌ No spec | - |
| cisco-self-mgmt | Other | [Other](swagger-other-model/index-v2.html#spec=cisco-self-mgmt) | [🌳](yang-trees/cisco-self-mgmt.html) |
| cisco-semver-internal | - | ❌ No spec | - |
| cisco-storm-control | - | ❌ No spec | - |
| cisco-xe-ietf-routing-ext | - | ❌ No spec | - |
| cisco-xe-ietf-yang-push-ext | - | ❌ No spec | [🌳](yang-trees/cisco-xe-ietf-yang-push-ext.html) |
| confd_dyncfg | Other | [Other](swagger-other-model/index-v2.html#spec=confd_dyncfg) | [🌳](yang-trees/confd_dyncfg.html) |
| nvo | Other | [Other](swagger-other-model/index-v2.html#spec=nvo) | [🌳](yang-trees/nvo.html) |
| policy-attr | - | ❌ No spec | - |
| tailf-aaa | - | ❌ No spec | [🌳](yang-trees/tailf-aaa.html) |
| tailf-acm | - | ❌ No spec | [🌳](yang-trees/tailf-acm.html) |
| tailf-cli-extensions | - | ❌ No spec | - |
| tailf-confd-monitoring | - | ❌ No spec | [🌳](yang-trees/tailf-confd-monitoring.html) |
| tailf-confd-monitoring2 | - | ❌ No spec | [🌳](yang-trees/tailf-confd-monitoring2.html) |
| tailf-key-rotation | - | ❌ No spec | [🌳](yang-trees/tailf-key-rotation.html) |
| tailf-kicker | Events | [Events](swagger-events-model/index-v2.html#spec=tailf-kicker) | [🌳](yang-trees/tailf-kicker.html) |
| tailf-meta-extensions | - | ❌ No spec | - |
| tailf-netconf-extensions | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=tailf-netconf-extensions) | [🌳](yang-trees/tailf-netconf-extensions.html) |
| tailf-netconf-inactive | - | ❌ No spec | [🌳](yang-trees/tailf-netconf-inactive.html) |
| tailf-netconf-monitoring | - | ❌ No spec | [🌳](yang-trees/tailf-netconf-monitoring.html) |
| tailf-netconf-query | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=tailf-netconf-query) | [🌳](yang-trees/tailf-netconf-query.html) |
| tailf-netconf-transactions | RPC | [RPC](swagger-rpc-model/index-v2.html#spec=tailf-netconf-transactions) | [🌳](yang-trees/tailf-netconf-transactions.html) |
| tailf-rest-query | - | ❌ No spec | - |
| tailf-restconf-error | - | ❌ No spec | - |
| tailf-yang-patch | - | ❌ No spec | - |

### TYPES (64 modules)

*Type definitions only*

<details>
<summary>Click to expand 64 types modules</summary>

| Module | Tree |
|--------|------|
| Cisco-IOS-XE-aaa-types | - |
| Cisco-IOS-XE-appqoe-types | - |
| Cisco-IOS-XE-common-types | - |
| Cisco-IOS-XE-dmi-common-types | - |
| Cisco-IOS-XE-event-history-types | - |
| Cisco-IOS-XE-install-event-types | - |
| Cisco-IOS-XE-install-oper-types | - |
| Cisco-IOS-XE-livetools-common-types | - |
| Cisco-IOS-XE-nwpi-types | - |
| Cisco-IOS-XE-red-app-common-types | - |
| Cisco-IOS-XE-sdwan-types | - |
| Cisco-IOS-XE-sm-enum-types | - |
| Cisco-IOS-XE-tunnel-types | - |
| Cisco-IOS-XE-types | - |
| Cisco-IOS-XE-vrrp-types | - |
| Cisco-IOS-XE-wireless-afc-types | - |
| Cisco-IOS-XE-wireless-ap-types | - |
| Cisco-IOS-XE-wireless-client-types | - |
| Cisco-IOS-XE-wireless-enum-types | - |
| Cisco-IOS-XE-wireless-geolocation-types | - |
| Cisco-IOS-XE-wireless-mobility-types | - |
| Cisco-IOS-XE-wireless-rogue-types | - |
| Cisco-IOS-XE-wireless-rrm-types | - |
| Cisco-IOS-XE-wireless-tunnel-types | - |
| Cisco-IOS-XE-wireless-types | - |
| Cisco-IOS-XE-wireless-urwb-common-types | - |
| Cisco-IOS-XE-wsa-types | - |
| cisco-smart-license-errors | - |
| common-mpls-types | - |
| ietf-inet-types | - |
| ietf-routing-types | - |
| ietf-yang-types | - |
| openconfig-aaa-types | - |
| openconfig-aft-types | - |
| openconfig-alarm-types | - |
| openconfig-bgp-types | - |
| openconfig-evpn-types | - |
| openconfig-if-types | - |
| openconfig-igmp-types | - |
| openconfig-inet-types | - |
| openconfig-isis-lsdb-types | - |
| openconfig-isis-types | - |
| openconfig-keychain-types | - |
| openconfig-lldp-types | - |
| openconfig-macsec-types | - |
| openconfig-mpls-types | - |
| openconfig-network-instance-types | - |
| openconfig-openflow-types | - |
| openconfig-ospf-types | - |
| openconfig-packet-match-types | - |
| openconfig-pim-types | - |
| openconfig-platform-types | - |
| openconfig-policy-types | - |
| openconfig-rib-bgp-types | - |
| openconfig-segment-routing-types | - |
| openconfig-spanning-tree-types | - |
| openconfig-transport-types | - |
| openconfig-types | - |
| openconfig-vlan-types | - |
| openconfig-wifi-types | - |
| openconfig-yang-types | - |
| pim | - |
| policy-types | - |
| tailf-xsd-types | - |

</details>

### DEVIATION (98 modules)

*Deviation module - modifies other modules*

<details>
<summary>Click to expand 98 deviation modules</summary>

| Module | Tree |
|--------|------|
| Cisco-IOS-XE-aaa-deviation | - |
| Cisco-IOS-XE-aging-time-deviation | - |
| Cisco-IOS-XE-cdp-deviation | - |
| Cisco-IOS-XE-cef-deviation | - |
| Cisco-IOS-XE-cts-routing-deviation | - |
| Cisco-IOS-XE-cts-switching-deviation | - |
| Cisco-IOS-XE-dhcp-deviation | - |
| Cisco-IOS-XE-dialer-deviation | - |
| Cisco-IOS-XE-ethernet-deviation | - |
| Cisco-IOS-XE-ethernet-mcp-deviation | - |
| Cisco-IOS-XE-flow-deviation | - |
| Cisco-IOS-XE-interfaces-cat9k-deviation | - |
| Cisco-IOS-XE-interfaces-deviation | - |
| Cisco-IOS-XE-interfaces-wlc-deviation | - |
| Cisco-IOS-XE-line-common-deviation | - |
| Cisco-IOS-XE-line-deviation | - |
| Cisco-IOS-XE-line-nonquake-deviation | - |
| Cisco-IOS-XE-lisp-deviation | - |
| Cisco-IOS-XE-logging-deviation | - |
| Cisco-IOS-XE-nd-deviation | - |
| Cisco-IOS-XE-ospf-deviation | - |
| Cisco-IOS-XE-ospfv3-deviation | - |
| Cisco-IOS-XE-perf-measure-deviation | - |
| Cisco-IOS-XE-pnp-deviation | - |
| Cisco-IOS-XE-poch-lb-switch-deviation | - |
| Cisco-IOS-XE-policy-cat9k-deviation | - |
| Cisco-IOS-XE-policy-deviation | - |
| Cisco-IOS-XE-policy-mcp-deviation | - |
| Cisco-IOS-XE-policy-vxe-deviation | - |
| Cisco-IOS-XE-policy-wlc-deviation | - |
| Cisco-IOS-XE-port-channel-crankshaft-deviation | - |
| Cisco-IOS-XE-port-channel-deviation | - |
| Cisco-IOS-XE-port-channel-unsupported-deviation | - |
| Cisco-IOS-XE-power-deviation | - |
| Cisco-IOS-XE-ppp-mcp-deviation | - |
| Cisco-IOS-XE-sanet-deviation | - |
| Cisco-IOS-XE-snmp-deviation | - |
| Cisco-IOS-XE-switch-deviation | - |
| Cisco-IOS-XE-switchport-deviation | - |
| Cisco-IOS-XE-switchport-ewlc-deviation | - |
| Cisco-IOS-XE-vlan-ewlc-deviation | - |
| Cisco-IOS-XE-vlan-vxe-deviation | - |
| Cisco-IOS-XE-vrrp-deviation | - |
| cisco-xe-ietf-event-notifications-deviation | - |
| cisco-xe-ietf-ip-deviation | - |
| cisco-xe-ietf-ipv4-unicast-routing-deviation | - |
| cisco-xe-ietf-ipv6-unicast-routing-deviation | - |
| cisco-xe-ietf-ospf-deviation | - |
| cisco-xe-ietf-routing-deviation | - |
| cisco-xe-ietf-yang-push-deviation | - |
| cisco-xe-openconfig-access-points-deviation | - |
| cisco-xe-openconfig-acl-deviation | - |
| cisco-xe-openconfig-acl-ext | - |
| cisco-xe-openconfig-aft-deviation | - |
| cisco-xe-openconfig-bgp-deviation | - |
| cisco-xe-openconfig-bgp-policy-deviation | - |
| cisco-xe-openconfig-ethernet-segments-deviation | - |
| cisco-xe-openconfig-evpn-deviation | - |
| cisco-xe-openconfig-if-ethernet-ext | [🌳](yang-trees/cisco-xe-openconfig-if-ethernet-ext.html) |
| cisco-xe-openconfig-if-ip-deviation | - |
| cisco-xe-openconfig-if-poe-deviation | - |
| cisco-xe-openconfig-interfaces-deviation | - |
| cisco-xe-openconfig-interfaces-ext | [🌳](yang-trees/cisco-xe-openconfig-interfaces-ext.html) |
| cisco-xe-openconfig-isis-deviation | - |
| cisco-xe-openconfig-isis-policy-deviation | - |
| cisco-xe-openconfig-lldp-deviation | - |
| cisco-xe-openconfig-local-routing-deviation | - |
| cisco-xe-openconfig-mpls-deviation | - |
| cisco-xe-openconfig-network-instance-deviation | - |
| cisco-xe-openconfig-network-instance-l2-deviation | - |
| cisco-xe-openconfig-openflow-deviation | - |
| cisco-xe-openconfig-platform-ext | [🌳](yang-trees/cisco-xe-openconfig-platform-ext.html) |
| cisco-xe-openconfig-rib-bgp-ext | [🌳](yang-trees/cisco-xe-openconfig-rib-bgp-ext.html) |
| cisco-xe-openconfig-routing-policy-deviation | - |
| cisco-xe-openconfig-segment-routing-deviation | - |
| cisco-xe-openconfig-spanning-tree-deviation | - |
| cisco-xe-openconfig-spanning-tree-ext | [🌳](yang-trees/cisco-xe-openconfig-spanning-tree-ext.html) |
| cisco-xe-openconfig-system-ext | [🌳](yang-trees/cisco-xe-openconfig-system-ext.html) |
| cisco-xe-openconfig-system-grpc-deviation | - |
| cisco-xe-openconfig-vlan-ext | [🌳](yang-trees/cisco-xe-openconfig-vlan-ext.html) |
| cisco-xe-routing-asr-openconfig-if-ethernet-deviation | - |
| cisco-xe-routing-csr-openconfig-platform-deviation | - |
| cisco-xe-routing-isr-openconfig-if-ethernet-deviation | - |
| cisco-xe-routing-isr-openconfig-platform-deviation | - |
| cisco-xe-routing-openconfig-system-deviation | - |
| cisco-xe-routing-openconfig-system-ext | [🌳](yang-trees/cisco-xe-routing-openconfig-system-ext.html) |
| cisco-xe-routing-openconfig-system-grpc-deviation | - |
| cisco-xe-routing-openconfig-vlan-deviation | - |
| cisco-xe-switching-cat9k-openconfig-system-deviation | - |
| cisco-xe-switching-openconfig-if-ethernet-deviation | - |
| cisco-xe-switching-openconfig-interfaces-deviation | - |
| cisco-xe-switching-openconfig-lacp-deviation | - |
| cisco-xe-switching-openconfig-platform-deviation | - |
| cisco-xe-switching-openconfig-vlan-deviation | - |
| cisco-xe-wireless-openconfig-if-ethernet-deviation | - |
| cisco-xe-wireless-openconfig-vlan-deviation | - |
| common-mpls-static-devs | - |
| nvo-devs | - |

</details>

### COMMON (21 modules)

*Common/shared protocol module*

<details>
<summary>Click to expand 21 common modules</summary>

| Module | Tree |
|--------|------|
| Cisco-IOS-XE-aws-common-cfg | - |
| Cisco-IOS-XE-aws-common-oper | - |
| Cisco-IOS-XE-bgp-common-oper | - |
| Cisco-IOS-XE-controller-shdsl-common | - |
| Cisco-IOS-XE-interface-common | - |
| Cisco-IOS-XE-ios-common-oper | - |
| Cisco-IOS-XE-mdt-common-defs | - |
| Cisco-IOS-XE-ospf-common | - |
| Cisco-IOS-XE-platform-common-oper | - |
| Cisco-IOS-XE-utd-common-oper | - |
| cisco-bridge-common | - |
| cisco-semver | - |
| common-mpls-static | [🌳](yang-trees/common-mpls-static.html) |
| openconfig-aft-common | - |
| openconfig-bgp-common | - |
| openconfig-bgp-common-multiprotocol | - |
| openconfig-bgp-common-structure | - |
| openconfig-ospfv2-common | - |
| tailf-common | - |
| tailf-common-monitoring2 | - |
| tailf-common-query | - |

</details>

### NATIVE-AUG (139 modules)

*Augments native module - included in native specs*

<details>
<summary>Click to expand 139 native-aug modules</summary>

| Module | Tree |
|--------|------|
| Cisco-IOS-XE-aaa | [🌳](yang-trees/Cisco-IOS-XE-aaa.html) |
| Cisco-IOS-XE-acl | [🌳](yang-trees/Cisco-IOS-XE-acl.html) |
| Cisco-IOS-XE-adsl | [🌳](yang-trees/Cisco-IOS-XE-adsl.html) |
| Cisco-IOS-XE-alarm-profile | [🌳](yang-trees/Cisco-IOS-XE-alarm-profile.html) |
| Cisco-IOS-XE-app-hosting | [🌳](yang-trees/Cisco-IOS-XE-app-hosting.html) |
| Cisco-IOS-XE-arp | [🌳](yang-trees/Cisco-IOS-XE-arp.html) |
| Cisco-IOS-XE-atm | [🌳](yang-trees/Cisco-IOS-XE-atm.html) |
| Cisco-IOS-XE-avb | [🌳](yang-trees/Cisco-IOS-XE-avb.html) |
| Cisco-IOS-XE-bba-group | [🌳](yang-trees/Cisco-IOS-XE-bba-group.html) |
| Cisco-IOS-XE-bfd | [🌳](yang-trees/Cisco-IOS-XE-bfd.html) |
| Cisco-IOS-XE-bgp | [🌳](yang-trees/Cisco-IOS-XE-bgp.html) |
| Cisco-IOS-XE-bridge | [🌳](yang-trees/Cisco-IOS-XE-bridge.html) |
| Cisco-IOS-XE-bridge-domain | [🌳](yang-trees/Cisco-IOS-XE-bridge-domain.html) |
| Cisco-IOS-XE-buffers | [🌳](yang-trees/Cisco-IOS-XE-buffers.html) |
| Cisco-IOS-XE-call-home | [🌳](yang-trees/Cisco-IOS-XE-call-home.html) |
| Cisco-IOS-XE-card | [🌳](yang-trees/Cisco-IOS-XE-card.html) |
| Cisco-IOS-XE-cdp | [🌳](yang-trees/Cisco-IOS-XE-cdp.html) |
| Cisco-IOS-XE-cef | [🌳](yang-trees/Cisco-IOS-XE-cef.html) |
| Cisco-IOS-XE-cellular | [🌳](yang-trees/Cisco-IOS-XE-cellular.html) |
| Cisco-IOS-XE-clns | [🌳](yang-trees/Cisco-IOS-XE-clns.html) |
| Cisco-IOS-XE-coap | [🌳](yang-trees/Cisco-IOS-XE-coap.html) |
| Cisco-IOS-XE-controller | [🌳](yang-trees/Cisco-IOS-XE-controller.html) |
| Cisco-IOS-XE-crypto | [🌳](yang-trees/Cisco-IOS-XE-crypto.html) |
| Cisco-IOS-XE-cts | [🌳](yang-trees/Cisco-IOS-XE-cts.html) |
| Cisco-IOS-XE-cwmp | [🌳](yang-trees/Cisco-IOS-XE-cwmp.html) |
| Cisco-IOS-XE-dapr | [🌳](yang-trees/Cisco-IOS-XE-dapr.html) |
| Cisco-IOS-XE-device-sensor | [🌳](yang-trees/Cisco-IOS-XE-device-sensor.html) |
| Cisco-IOS-XE-device-tracking | [🌳](yang-trees/Cisco-IOS-XE-device-tracking.html) |
| Cisco-IOS-XE-dhcp | [🌳](yang-trees/Cisco-IOS-XE-dhcp.html) |
| Cisco-IOS-XE-diagnostics | [🌳](yang-trees/Cisco-IOS-XE-diagnostics.html) |
| Cisco-IOS-XE-dialer | [🌳](yang-trees/Cisco-IOS-XE-dialer.html) |
| Cisco-IOS-XE-digitalio | [🌳](yang-trees/Cisco-IOS-XE-digitalio.html) |
| Cisco-IOS-XE-dlr | [🌳](yang-trees/Cisco-IOS-XE-dlr.html) |
| Cisco-IOS-XE-dot1x | [🌳](yang-trees/Cisco-IOS-XE-dot1x.html) |
| Cisco-IOS-XE-dying-gasp | [🌳](yang-trees/Cisco-IOS-XE-dying-gasp.html) |
| Cisco-IOS-XE-eem | [🌳](yang-trees/Cisco-IOS-XE-eem.html) |
| Cisco-IOS-XE-eigrp | [🌳](yang-trees/Cisco-IOS-XE-eigrp.html) |
| Cisco-IOS-XE-eta | [🌳](yang-trees/Cisco-IOS-XE-eta.html) |
| Cisco-IOS-XE-ethernet | [🌳](yang-trees/Cisco-IOS-XE-ethernet.html) |
| Cisco-IOS-XE-ethinternal-subslot | [🌳](yang-trees/Cisco-IOS-XE-ethinternal-subslot.html) |
| Cisco-IOS-XE-ezpm | [🌳](yang-trees/Cisco-IOS-XE-ezpm.html) |
| Cisco-IOS-XE-flow | [🌳](yang-trees/Cisco-IOS-XE-flow.html) |
| Cisco-IOS-XE-fqdn | [🌳](yang-trees/Cisco-IOS-XE-fqdn.html) |
| Cisco-IOS-XE-frame-relay | [🌳](yang-trees/Cisco-IOS-XE-frame-relay.html) |
| Cisco-IOS-XE-geo | [🌳](yang-trees/Cisco-IOS-XE-geo.html) |
| Cisco-IOS-XE-gnss | [🌳](yang-trees/Cisco-IOS-XE-gnss.html) |
| Cisco-IOS-XE-group-policy | [🌳](yang-trees/Cisco-IOS-XE-group-policy.html) |
| Cisco-IOS-XE-http | [🌳](yang-trees/Cisco-IOS-XE-http.html) |
| Cisco-IOS-XE-icmp | [🌳](yang-trees/Cisco-IOS-XE-icmp.html) |
| Cisco-IOS-XE-ida | [🌳](yang-trees/Cisco-IOS-XE-ida.html) |
| Cisco-IOS-XE-igmp | [🌳](yang-trees/Cisco-IOS-XE-igmp.html) |
| Cisco-IOS-XE-ipc | [🌳](yang-trees/Cisco-IOS-XE-ipc.html) |
| Cisco-IOS-XE-ipmux | [🌳](yang-trees/Cisco-IOS-XE-ipmux.html) |
| Cisco-IOS-XE-irig | [🌳](yang-trees/Cisco-IOS-XE-irig.html) |
| Cisco-IOS-XE-isdn | [🌳](yang-trees/Cisco-IOS-XE-isdn.html) |
| Cisco-IOS-XE-isg | [🌳](yang-trees/Cisco-IOS-XE-isg.html) |
| Cisco-IOS-XE-isis | [🌳](yang-trees/Cisco-IOS-XE-isis.html) |
| Cisco-IOS-XE-iwanfabric | [🌳](yang-trees/Cisco-IOS-XE-iwanfabric.html) |
| Cisco-IOS-XE-kron | [🌳](yang-trees/Cisco-IOS-XE-kron.html) |
| Cisco-IOS-XE-l2nat | [🌳](yang-trees/Cisco-IOS-XE-l2nat.html) |
| Cisco-IOS-XE-l2vpn | [🌳](yang-trees/Cisco-IOS-XE-l2vpn.html) |
| Cisco-IOS-XE-l3nat-iox | [🌳](yang-trees/Cisco-IOS-XE-l3nat-iox.html) |
| Cisco-IOS-XE-l3vpn | [🌳](yang-trees/Cisco-IOS-XE-l3vpn.html) |
| Cisco-IOS-XE-lisp | [🌳](yang-trees/Cisco-IOS-XE-lisp.html) |
| Cisco-IOS-XE-lldp | [🌳](yang-trees/Cisco-IOS-XE-lldp.html) |
| Cisco-IOS-XE-loop-detect | [🌳](yang-trees/Cisco-IOS-XE-loop-detect.html) |
| Cisco-IOS-XE-lorawan | [🌳](yang-trees/Cisco-IOS-XE-lorawan.html) |
| Cisco-IOS-XE-lte450 | [🌳](yang-trees/Cisco-IOS-XE-lte450.html) |
| Cisco-IOS-XE-mdns-gateway | [🌳](yang-trees/Cisco-IOS-XE-mdns-gateway.html) |
| Cisco-IOS-XE-mka | [🌳](yang-trees/Cisco-IOS-XE-mka.html) |
| Cisco-IOS-XE-mld | [🌳](yang-trees/Cisco-IOS-XE-mld.html) |
| Cisco-IOS-XE-mmode | [🌳](yang-trees/Cisco-IOS-XE-mmode.html) |
| Cisco-IOS-XE-mobileip | [🌳](yang-trees/Cisco-IOS-XE-mobileip.html) |
| Cisco-IOS-XE-mpls | [🌳](yang-trees/Cisco-IOS-XE-mpls.html) |
| Cisco-IOS-XE-mrp | [🌳](yang-trees/Cisco-IOS-XE-mrp.html) |
| Cisco-IOS-XE-multicast | [🌳](yang-trees/Cisco-IOS-XE-multicast.html) |
| Cisco-IOS-XE-mvrp | [🌳](yang-trees/Cisco-IOS-XE-mvrp.html) |
| Cisco-IOS-XE-nam | [🌳](yang-trees/Cisco-IOS-XE-nam.html) |
| Cisco-IOS-XE-nat | [🌳](yang-trees/Cisco-IOS-XE-nat.html) |
| Cisco-IOS-XE-nbar | [🌳](yang-trees/Cisco-IOS-XE-nbar.html) |
| Cisco-IOS-XE-nd | [🌳](yang-trees/Cisco-IOS-XE-nd.html) |
| Cisco-IOS-XE-nhrp | [🌳](yang-trees/Cisco-IOS-XE-nhrp.html) |
| Cisco-IOS-XE-ntp | [🌳](yang-trees/Cisco-IOS-XE-ntp.html) |
| Cisco-IOS-XE-object-group | [🌳](yang-trees/Cisco-IOS-XE-object-group.html) |
| Cisco-IOS-XE-ospf | [🌳](yang-trees/Cisco-IOS-XE-ospf.html) |
| Cisco-IOS-XE-ospfv3 | [🌳](yang-trees/Cisco-IOS-XE-ospfv3.html) |
| Cisco-IOS-XE-otv | [🌳](yang-trees/Cisco-IOS-XE-otv.html) |
| Cisco-IOS-XE-pae | [🌳](yang-trees/Cisco-IOS-XE-pae.html) |
| Cisco-IOS-XE-pathmgr | [🌳](yang-trees/Cisco-IOS-XE-pathmgr.html) |
| Cisco-IOS-XE-perf-measure | [🌳](yang-trees/Cisco-IOS-XE-perf-measure.html) |
| Cisco-IOS-XE-pfr | [🌳](yang-trees/Cisco-IOS-XE-pfr.html) |
| Cisco-IOS-XE-platform | [🌳](yang-trees/Cisco-IOS-XE-platform.html) |
| Cisco-IOS-XE-pnp | [🌳](yang-trees/Cisco-IOS-XE-pnp.html) |
| Cisco-IOS-XE-policy | [🌳](yang-trees/Cisco-IOS-XE-policy.html) |
| Cisco-IOS-XE-power | [🌳](yang-trees/Cisco-IOS-XE-power.html) |
| Cisco-IOS-XE-ppp | [🌳](yang-trees/Cisco-IOS-XE-ppp.html) |
| Cisco-IOS-XE-pppoe | [🌳](yang-trees/Cisco-IOS-XE-pppoe.html) |
| Cisco-IOS-XE-prp | [🌳](yang-trees/Cisco-IOS-XE-prp.html) |
| Cisco-IOS-XE-ptp | [🌳](yang-trees/Cisco-IOS-XE-ptp.html) |
| Cisco-IOS-XE-qos | [🌳](yang-trees/Cisco-IOS-XE-qos.html) |
| Cisco-IOS-XE-rawsocket | [🌳](yang-trees/Cisco-IOS-XE-rawsocket.html) |
| Cisco-IOS-XE-rip | [🌳](yang-trees/Cisco-IOS-XE-rip.html) |
| Cisco-IOS-XE-rmi-dad | [🌳](yang-trees/Cisco-IOS-XE-rmi-dad.html) |
| Cisco-IOS-XE-route-map | [🌳](yang-trees/Cisco-IOS-XE-route-map.html) |
| Cisco-IOS-XE-rsvp | [🌳](yang-trees/Cisco-IOS-XE-rsvp.html) |
| Cisco-IOS-XE-sanet | [🌳](yang-trees/Cisco-IOS-XE-sanet.html) |
| Cisco-IOS-XE-scada-gw | [🌳](yang-trees/Cisco-IOS-XE-scada-gw.html) |
| Cisco-IOS-XE-segment-routing | [🌳](yang-trees/Cisco-IOS-XE-segment-routing.html) |
| Cisco-IOS-XE-serial | [🌳](yang-trees/Cisco-IOS-XE-serial.html) |
| Cisco-IOS-XE-service-discovery | [🌳](yang-trees/Cisco-IOS-XE-service-discovery.html) |
| Cisco-IOS-XE-service-insertion | [🌳](yang-trees/Cisco-IOS-XE-service-insertion.html) |
| Cisco-IOS-XE-service-routing | [🌳](yang-trees/Cisco-IOS-XE-service-routing.html) |
| Cisco-IOS-XE-site-manager | [🌳](yang-trees/Cisco-IOS-XE-site-manager.html) |
| Cisco-IOS-XE-sla | [🌳](yang-trees/Cisco-IOS-XE-sla.html) |
| Cisco-IOS-XE-snmp | [🌳](yang-trees/Cisco-IOS-XE-snmp.html) |
| Cisco-IOS-XE-spanning-tree | [🌳](yang-trees/Cisco-IOS-XE-spanning-tree.html) |
| Cisco-IOS-XE-stackwise-virtual | [🌳](yang-trees/Cisco-IOS-XE-stackwise-virtual.html) |
| Cisco-IOS-XE-switch | [🌳](yang-trees/Cisco-IOS-XE-switch.html) |
| Cisco-IOS-XE-synce | [🌳](yang-trees/Cisco-IOS-XE-synce.html) |
| Cisco-IOS-XE-template | [🌳](yang-trees/Cisco-IOS-XE-template.html) |
| Cisco-IOS-XE-track | [🌳](yang-trees/Cisco-IOS-XE-track.html) |
| Cisco-IOS-XE-tunnel | [🌳](yang-trees/Cisco-IOS-XE-tunnel.html) |
| Cisco-IOS-XE-ucse | [🌳](yang-trees/Cisco-IOS-XE-ucse.html) |
| Cisco-IOS-XE-udld | [🌳](yang-trees/Cisco-IOS-XE-udld.html) |
| Cisco-IOS-XE-umbrella | [🌳](yang-trees/Cisco-IOS-XE-umbrella.html) |
| Cisco-IOS-XE-uplink-autoconfig | [🌳](yang-trees/Cisco-IOS-XE-uplink-autoconfig.html) |
| Cisco-IOS-XE-utd | [🌳](yang-trees/Cisco-IOS-XE-utd.html) |
| Cisco-IOS-XE-vlan | [🌳](yang-trees/Cisco-IOS-XE-vlan.html) |
| Cisco-IOS-XE-voice | [🌳](yang-trees/Cisco-IOS-XE-voice.html) |
| Cisco-IOS-XE-voice-port | [🌳](yang-trees/Cisco-IOS-XE-voice-port.html) |
| Cisco-IOS-XE-vpdn | [🌳](yang-trees/Cisco-IOS-XE-vpdn.html) |
| Cisco-IOS-XE-vrrp | [🌳](yang-trees/Cisco-IOS-XE-vrrp.html) |
| Cisco-IOS-XE-vservice | [🌳](yang-trees/Cisco-IOS-XE-vservice.html) |
| Cisco-IOS-XE-vstack | [🌳](yang-trees/Cisco-IOS-XE-vstack.html) |
| Cisco-IOS-XE-vtp | [🌳](yang-trees/Cisco-IOS-XE-vtp.html) |
| Cisco-IOS-XE-vxlan | [🌳](yang-trees/Cisco-IOS-XE-vxlan.html) |
| Cisco-IOS-XE-wccp | [🌳](yang-trees/Cisco-IOS-XE-wccp.html) |
| Cisco-IOS-XE-wsma | [🌳](yang-trees/Cisco-IOS-XE-wsma.html) |
| Cisco-IOS-XE-zone | [🌳](yang-trees/Cisco-IOS-XE-zone.html) |

</details>

---

## Modules in Multiple Categories (18)

These modules appear in more than one swagger category:

| Module | Categories |
|--------|------------|
| Cisco-IOS-XE-im-events-oper | Operational, Events |
| Cisco-IOS-XE-ios-events-oper | Operational, Events |
| Cisco-IOS-XE-platform-events-oper | Operational, Events |
| Cisco-IOS-XE-sm-events-oper | Operational, Events |
| Cisco-IOS-XE-stack-mgr-events-oper | Operational, Events |
| Cisco-IOS-XE-umbrella-oper-dp | Operational, Events |
| Cisco-IOS-XE-wireless-events-oper | Operational, Events |
| cisco-bridge-domain | RPC, Events, Other |
| cisco-pw | Events, Other |
| cisco-smart-license | RPC, Events, Other |
| ietf-event-notifications | IETF, RPC, Events |
| ietf-netconf | IETF, RPC |
| ietf-netconf-monitoring | IETF, RPC |
| ietf-netconf-notifications | IETF, Events |
| ietf-ospf | IETF, Events |
| ietf-routing | IETF, RPC |
| ietf-yang-library | IETF, Events |
| ietf-yang-push | IETF, Events |

---

## Exclusion Categories Explained

| Classification | Reason |
|----------------|--------|
| **types** | Contains only `typedef` and `grouping` statements — no API operations |
| **deviation** | Modifies other modules' behavior — no standalone API |
| **common** | Infrastructure modules (tailf-*, cisco-semver) — shared types only |
| **native-aug** | Augments Cisco-IOS-XE-native — content is included in Native Config specs |

*Report generated: 2026-03-30T19:58:43.425676*