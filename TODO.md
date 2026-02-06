# TODO List

## Add YANG-Aligned Example Data to Native Config Model APIs

- [x] #1: Add examples to native-00-top-level-leafs.json (8 endpoints)
  - File: swagger-native-config-model/api/native-00-top-level-leafs.json
  - Description: Add YANG-aligned example data for hostname, version, config-register, aqm-register-fnf, boot-end-marker, boot-start-marker, captive-portal-bypass, disable-eadi
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 13 examples total (hostname already had PUT example, added PATCH + all PUT/PATCH for remaining 7 endpoints)

- [x] #2: Add examples to native-00-top-level-containers.json (5 endpoints)
  - File: swagger-native-config-model/api/native-00-top-level-containers.json
  - Description: Add examples for vlan, logging, snmp-server, nat, spanning-tree
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 10 examples (PUT + PATCH for all 5 endpoints with realistic YANG data)

- [x] #3: Add examples to native-ip.json (8 endpoints)
  - File: swagger-native-config-model/api/native-ip.json
  - Description: Add examples for ip, ip access-list, ip dhcp, ip domain, ip http, ip nat, ip route, ip ssh
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 16 examples (PUT + PATCH for all 8 endpoints with realistic IP configs, ACLs, routes, DHCP pools, DNS, NAT, HTTP, SSH)

- [x] #4: Add examples to native-router.json (7 endpoints)
  - File: swagger-native-config-model/api/native-router.json
  - Description: Add examples for router, router bgp, router eigrp, router isis, router lisp, router ospf, router rip
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 14 examples (PUT + PATCH for all 7 endpoints with OSPF, BGP, EIGRP, RIP, ISIS, LISP configs)

- [x] #5: Add examples to native-crypto.json (5 endpoints)
  - File: swagger-native-config-model/api/native-crypto.json
  - Description: Add examples for crypto, crypto ikev2, crypto ipsec, crypto keyring, crypto pki
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 10 examples (PUT + PATCH for all 5 endpoints with PKI, IKEv2, IPsec, keyring configs)

- [x] #6: Add examples to native-aaa.json (4 endpoints)
  - File: swagger-native-config-model/api/native-aaa.json
  - Description: Add examples for aaa, aaa accounting, aaa authentication, aaa authorization
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 8 examples (PUT + PATCH for all 4 endpoints with authentication, authorization, accounting method lists)

- [x] #7: Add examples to native-line.json (4 endpoints)
  - File: swagger-native-config-model/api/native-line.json
  - Description: Add examples for line, line aux, line console, line vty
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 8 examples (PUT + PATCH for all 4 endpoints with console, VTY, AUX configs)

- [x] #8: Add examples to native-vrf.json (2 endpoints)
  - File: swagger-native-config-model/api/native-vrf.json
  - Description: Add examples for vrf, vrf definition
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 4 examples (PUT + PATCH for both endpoints with MPLS VPN, route-target configs)

- [x] #9: Add examples to native-platform-system.json (15 endpoints)
  - File: swagger-native-config-model/api/native-platform-system.json
  - Description: Add examples for banner, boot, card, clock, default, exception, hw-module, location, memory, module, setup, software, stack-power, system, upgrade
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data
  - Completed: Added 30 examples (PUT + PATCH for all 15 endpoints with platform/system configs)

- [ ] #10: Add examples to native-protocols.json (17 endpoints)
  - File: swagger-native-config-model/api/native-protocols.json
  - Description: Add examples for bfd, bfd-template, cdp, clns, frame-relay, l2vpn, l2vpn-config, l3vpn, lacp, mpls, multilink, mvrp, ntp, ppp, ptp, udld, xconnect
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data

- [ ] #11: Add examples to native-security-access.json (15 endpoints)
  - File: swagger-native-config-model/api/native-security-access.json
  - Description: Add examples for cts, device-tracking, dot1x, eap, enable, identity, login, mab, mka, password, privilege, radius, radius-server, tacacs, tacacs-server
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data

- [ ] #12: Add examples to native-switching-l2.json (9 endpoints)
  - File: swagger-native-config-model/api/native-switching-l2.json
  - Description: Add examples for bridge-domain, ethernet, l2, mac, mac-address-table, otv, port-channel, vtp, vxlan
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data

- [ ] #13: Add examples to native-qos-policy.json (2 endpoints)
  - File: swagger-native-config-model/api/native-qos-policy.json
  - Description: Add examples for parameter-map, qos
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data

- [ ] #14: Add examples to native-other.json - Part 1 (first 27 endpoints: alarm-contact through fhrp)
  - File: swagger-native-config-model/api/native-other.json
  - Description: Add examples for alarm-contact, alias, archive, avb, avc, call-home, cisp, controller, control-plane, control-plane-host, cwmp, domain, endpoint-tracker, epm, errdisable, event, fabric, facility-alarm, fallback, fhrp, file, flow, global-address-family, iox, ipv6, key, l2tp
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data

- [ ] #15: Add examples to native-other.json - Part 2 (middle 27 endpoints: l2tp-class through route-map)
  - File: swagger-native-config-model/api/native-other.json
  - Description: Add examples for l2tp-class, ldap, license, macro, management, md-list, memory-size, metadata, mls, monitor, native, network-clock, object-group, parser, performance, performance-measurement, pfr, pfr-map, platform, process, profile, pseudowire-class, redundancy, redun-management, remote-management, rmon, route-map
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data

- [ ] #16: Add examples to native-other.json - Part 3 (last 28 endpoints: route-tag through zone-pair)
  - File: swagger-native-config-model/api/native-other.json
  - Description: Add examples for route-tag, sampler, scada-gw, scheduler, sdm, segment-routing, service, service-chain, service-insertion, snmp, stackwise-virtual, standby, subscriber-config, table-map, template, tftp-server-config, time-range, tod-clock, track, transport, transport-map, username, user-name, virtual-service, virtual-template, wsma, zone, zone-pair
  - Acceptance: All PUT/PATCH operations have "example" field with valid YANG-conformant data

## Fix Existing TODO Comments in Other Models

- [ ] #17: Fix TODO descriptions in cisco-pw.json
  - File: swagger-other-model/api/cisco-pw.json
  - Description: Replace 7 placeholder "TODO" descriptions with proper documentation (lines 1900, 1916, 1941, 1946, 1960, 1965, 1988)
  - Acceptance: All "description": "TODO" replaced with meaningful descriptions from YANG model

- [ ] #18: Fix TODO descriptions in openconfig-mpls.json
  - File: swagger-openconfig-model/api/openconfig-mpls.json
  - Description: Replace 28 placeholder "TODO" descriptions with proper documentation
  - Acceptance: All "description": "TODO" replaced with meaningful descriptions from YANG model
