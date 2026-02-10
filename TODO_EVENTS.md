# Event Notifications Enhancement TODO

**Goal**: Add YANG-derived schemas with typed properties and realistic example values
to all 128 event notification specs in `swagger-events-model/api/`.

## Summary
| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Specs with schemas | 5/128 | **128/128** | 128/128 ✅ |
| Specs with examples | 0/128 | **128/128** | 128/128 ✅ |
| Total notification schemas | ~9 | **509** | ~492 ✅ |

**Status: COMPLETE** — All 128 event notification specs enhanced with YANG-derived schemas and examples.

## Legend
- [ ] Not started
- [x] Complete

## XE Event Notifications (39)

| # | File | Paths | Notifs | Has Schema | Has Examples | Status |
|---|------|-------|--------|------------|--------------|--------|
| 1 | Cisco-IOS-XE-aaa-events.json | 2 | 1 (test-aaa-authentication-update) | No | Yes | [x] |
| 2 | Cisco-IOS-XE-appqoe-events.json | 2 | 2 (appqoe-alarm, appqoe-event) | No | Yes | [x] |
| 3 | Cisco-IOS-XE-controller-shdsl-events.json | 2 | 6 (shdsl-dslgrp-state-update, shdsl-efmbond-link-rate-update, shdsl-efmbond-config-mismatch-notification +3 more) | No | Yes | [x] |
| 4 | Cisco-IOS-XE-crypto-events.json | 2 | 3 (ike-ipsec-event, nhrp-alarm, nhrp-event) | No | Yes | [x] |
| 5 | Cisco-IOS-XE-crypto-pki-events.json | 2 | 2 (pki-certificate-expiry, pki-certificate-event) | No | Yes | [x] |
| 6 | Cisco-IOS-XE-dca-events.json | 2 | 1 (dca-change-event) | No | Yes | [x] |
| 7 | Cisco-IOS-XE-endpoint-tracker-events.json | 2 | 2 (tracker-state-change, sc-status-change-event) | No | Yes | [x] |
| 8 | Cisco-IOS-XE-fib-events.json | 2 | 2 (fib-updates, fib-default-route-state-change) | No | Yes | [x] |
| 9 | Cisco-IOS-XE-geo-events.json | 2 | 1 (geo-db-update-event) | No | Yes | [x] |
| 10 | Cisco-IOS-XE-hsrp-events.json | 2 | 1 (hsrp-group-state-change) | No | Yes | [x] |
| 11 | Cisco-IOS-XE-im-events-oper.json | 2 | 1 (im-event) | No | Yes | [x] |
| 12 | Cisco-IOS-XE-install-events.json | 2 | 1 (install-status) | No | Yes | [x] |
| 13 | Cisco-IOS-XE-interface-bw-events.json | 2 | 1 (interface-bw) | No | Yes | [x] |
| 14 | Cisco-IOS-XE-ios-events-oper.json | 2 | 52 (bgp-peer-state-change, ospf-neighbor-state-change, ospf-interface-state-change +49 more) | No | Yes | [x] |
| 15 | Cisco-IOS-XE-ip-sla-events.json | 2 | 1 (ipsla-reaction-update) | No | Yes | [x] |
| 16 | Cisco-IOS-XE-line-events.json | 2 | 1 (line-state-event) | No | Yes | [x] |
| 17 | Cisco-IOS-XE-loop-detect-events.json | 2 | 1 (loopdetect-intf-event) | No | Yes | [x] |
| 18 | Cisco-IOS-XE-matm-events.json | 2 | 1 (mac-flap-intf-event) | No | Yes | [x] |
| 19 | Cisco-IOS-XE-mcast-events.json | 2 | 1 (pim-nbr-state-event) | No | Yes | [x] |
| 20 | Cisco-IOS-XE-nat-events.json | 2 | 2 (nat-route-change, nat-update) | No | Yes | [x] |
| 21 | Cisco-IOS-XE-ngfw-events.json | 2 | 1 (ngfw-event) | No | Yes | [x] |
| 22 | Cisco-IOS-XE-ospf-events.json | 2 | 2 (ospfv3-nbr-state-change, ospfv3-if-state-change) | No | Yes | [x] |
| 23 | Cisco-IOS-XE-perf-measure-events.json | 2 | 6 (pm-dm-probe-end-notif, pm-dm-aggr-end-notif, pm-dm-adv-event-notif +3 more) | No | Yes | [x] |
| 24 | Cisco-IOS-XE-platform-events-oper.json | 2 | 2 (platform-sensor-state-update, platform-component-state-update) | No | Yes | [x] |
| 25 | Cisco-IOS-XE-platform-software-events.json | 2 | 1 (process-state-event) | No | Yes | [x] |
| 26 | Cisco-IOS-XE-port-bounce-events.json | 2 | 1 (port-bounce-event) | No | Yes | [x] |
| 27 | Cisco-IOS-XE-qfp-resource-events.json | 2 | 2 (qfp-resource-usage, qfp-exmem-usage) | No | Yes | [x] |
| 28 | Cisco-IOS-XE-red-app-events.json | 2 | 1 (red-event) | No | Yes | [x] |
| 29 | Cisco-IOS-XE-sm-events-oper.json | 2 | 1 (sessionevent) | No | Yes | [x] |
| 30 | Cisco-IOS-XE-spanning-tree-events.json | 2 | 4 (stp-intf-guard-event, stp-intf-role-change, stp-intf-bpdu-sender-conflict-event +1 more) | No | Yes | [x] |
| 31 | Cisco-IOS-XE-stack-mgr-events-oper.json | 2 | 1 (stkmevent) | No | Yes | [x] |
| 32 | Cisco-IOS-XE-tech-support-events.json | 2 | 1 (tech-support-event) | No | Yes | [x] |
| 33 | Cisco-IOS-XE-trace-events.json | 2 | 1 (trace-status) | No | Yes | [x] |
| 34 | Cisco-IOS-XE-udld-events.json | 2 | 1 (udld-intf-event) | No | Yes | [x] |
| 35 | Cisco-IOS-XE-umbrella-oper-dp.json | 2 | 2 (umbrella-anycast-server-switch, umbrella-max-cft-flows) | Yes | No | [x] |
| 36 | Cisco-IOS-XE-utd-events.json | 2 | 1 (utd-con) | No | Yes | [x] |
| 37 | Cisco-IOS-XE-verify-events.json | 2 | 1 (verify-event) | No | Yes | [x] |
| 38 | Cisco-IOS-XE-wireless-events-oper.json | 2 | 5 (wsa-client-event, rogue-events, threshold-warning-event +2 more) | No | Yes | [x] |
| 39 | Cisco-IOS-XE-xcopy-events.json | 2 | 1 (xcopy-status) | No | Yes | [x] |

## MIB SNMP Trap Notifications (80)

| # | File | Paths | Notifs | Has Schema | Has Examples | Status |
|---|------|-------|--------|------------|--------------|--------|
| 1 | BGP4-MIB.json | 2 | 2 (bgpEstablished, bgpBackwardTransition) | No | No | [x] |
| 2 | BRIDGE-MIB.json | 3 | 2 (newRoot, topologyChange) | No | No | [x] |
| 3 | CISCO-AAA-SERVER-MIB.json | 1 | 1 (casServerStateChange) | No | No | [x] |
| 4 | CISCO-ATM-PVCTRAP-EXTN-MIB.json | 12 | 12 (catmIntfPvcOAMFailureTrap, catmIntfPvcSegCCOAMFailureTrap, catmIntfPvcEndCCOAMFailureTrap +9 more) | No | No | [x] |
| 5 | CISCO-BGP4-MIB.json | 10 | 10 (cbgpFsmStateChange, cbgpBackwardTransition, cbgpPrefixThresholdExceeded +7 more) | No | No | [x] |
| 6 | CISCO-BULK-FILE-MIB.json | 1 | 1 (cbfDefineFileCompletion) | No | No | [x] |
| 7 | CISCO-CEF-MIB.json | 4 | 4 (cefResourceFailure, cefPeerStateChange, cefPeerFIBStateChange +1 more) | No | No | [x] |
| 8 | CISCO-CONFIG-COPY-MIB.json | 1 | 1 (ccCopyCompletion) | No | No | [x] |
| 9 | CISCO-CONFIG-MAN-MIB.json | 3 | 3 (ciscoConfigManEvent, ccmCLIRunningConfigChanged, ccmCTIDRolledOver) | No | No | [x] |
| 10 | CISCO-DATA-COLLECTION-MIB.json | 2 | 2 (cdcVFileCollectionError, cdcFileXferComplete) | No | No | [x] |
| 11 | CISCO-DOT3-OAM-MIB.json | 2 | 2 (cdot3OamThresholdEvent, cdot3OamNonThresholdEvent) | No | No | [x] |
| 12 | CISCO-EIGRP-MIB.json | 2 | 2 (cEigrpAuthFailureEvent, cEigrpRouteStuckInActive) | No | No | [x] |
| 13 | CISCO-EMBEDDED-EVENT-MGR-MIB.json | 2 | 2 (cEventMgrServerEvent, cEventMgrPolicyEvent) | No | No | [x] |
| 14 | CISCO-ENHANCED-MEMPOOL-MIB.json | 1 | 1 (cempMemBufferNotify) | No | No | [x] |
| 15 | CISCO-ENTITY-ALARM-MIB.json | 2 | 2 (ceAlarmAsserted, ceAlarmCleared) | No | No | [x] |
| 16 | CISCO-ENTITY-FRU-CONTROL-MIB.json | 7 | 7 (cefcModuleStatusChange, cefcPowerStatusChange, cefcFRUInserted +4 more) | No | No | [x] |
| 17 | CISCO-ENTITY-QFP-MIB.json | 3 | 3 (ceqfpMemoryResRisingThreshNotif, ceqfpMemoryResFallingThreshNotif, ceqfpThroughputNotif) | No | No | [x] |
| 18 | CISCO-ENTITY-SENSOR-MIB.json | 2 | 2 (entSensorThresholdNotification, entSensorThresholdRecoveryNotification) | No | No | [x] |
| 19 | CISCO-ENVMON-MIB.json | 5 | 5 (ciscoEnvMonShutdownNotification, ciscoEnvMonVoltStatusChangeNotif, ciscoEnvMonTempStatusChangeNotif +2 more) | No | No | [x] |
| 20 | CISCO-ETHER-CFM-MIB.json | 8 | 8 (cEtherCfmCcMepUp, cEtherCfmCcMepDown, cEtherCfmCcCrossconnect +5 more) | No | No | [x] |
| 21 | CISCO-FLASH-MIB.json | 7 | 7 (ciscoFlashCopyCompletionTrap, ciscoFlashPartitioningCompletionTrap, ciscoFlashMiscOpCompletionTrap +4 more) | No | No | [x] |
| 22 | CISCO-HSRP-MIB.json | 1 | 1 (cHsrpStateChange) | No | No | [x] |
| 23 | CISCO-IETF-ATM2-PVCTRAP-MIB-EXTN.json | 2 | 2 (atmIntfPvcUpTrap, atmIntfPvcOAMFailureTrap) | Yes | No | [x] |
| 24 | CISCO-IETF-ATM2-PVCTRAP-MIB.json | 1 | 1 (atmIntfPvcFailuresTrap) | No | No | [x] |
| 25 | CISCO-IETF-BFD-MIB.json | 2 | 2 (ciscoBfdSessUp, ciscoBfdSessDown) | No | No | [x] |
| 26 | CISCO-IETF-FRR-MIB.json | 2 | 2 (cmplsFrrProtected, cmplsFrrUnProtected) | No | No | [x] |
| 27 | CISCO-IETF-ISIS-MIB.json | 18 | 18 (ciiDatabaseOverload, ciiManualAddressDrops, ciiCorruptedLSPDetected +15 more) | No | No | [x] |
| 28 | CISCO-IETF-PW-MIB.json | 2 | 2 (cpwVcDown, cpwVcUp) | No | No | [x] |
| 29 | CISCO-IF-EXTENSION-MIB.json | 3 | 3 (cieLinkDown, cieLinkUp, cieDelayedLinkUpDownNotif) | No | No | [x] |
| 30 | CISCO-IMAGE-LICENSE-MGMT-MIB.json | 1 | 1 (cilmBootImageLevelChanged) | No | No | [x] |
| 31 | CISCO-IP-LOCAL-POOL-MIB.json | 3 | 3 (ciscoIpLocalPoolInUseAddrNoti, cilpPercentAddrUsedLoNotif, cilpPercentAddrUsedHiNotif) | No | No | [x] |
| 32 | CISCO-IP-URPF-MIB.json | 1 | 1 (cipUrpfIfDropRateNotify) | No | No | [x] |
| 33 | CISCO-IPMROUTE-MIB.json | 1 | 1 (ciscoIpMRouteMissingHeartBeats) | No | No | [x] |
| 34 | CISCO-IPSEC-FLOW-MONITOR-MIB.json | 13 | 13 (cikeTunnelStart, cikeTunnelStop, cikeSysFailure +10 more) | No | No | [x] |
| 35 | CISCO-IPSEC-MIB.json | 7 | 7 (cipsIsakmpPolicyAdded, cipsIsakmpPolicyDeleted, cipsCryptomapAdded +4 more) | No | No | [x] |
| 36 | CISCO-LICENSE-MGMT-MIB.json | 14 | 14 (clmgmtLicenseExpired, clmgmtLicenseExpiryWarning, clmgmtLicenseUsageCountExceeded +11 more) | No | No | [x] |
| 37 | CISCO-NBAR-PROTOCOL-DISCOVERY-MIB.json | 2 | 2 (cnpdThresholdRisingEvent, cnpdThresholdFallingEvent) | No | No | [x] |
| 38 | CISCO-NETSYNC-MIB.json | 4 | 4 (ciscoNetsyncSelectedT0Clock, ciscoNetsyncSelectedT4Clock, ciscoNetsyncInputSignalFailureStatus +1 more) | No | No | [x] |
| 39 | CISCO-NTP-MIB.json | 5 | 5 (ciscoNtpSrvStatusChange, ciscoNtpHighPriorityConnFailure, ciscoNtpHighPriorityConnRestore +2 more) | No | No | [x] |
| 40 | CISCO-OSPF-TRAP-MIB.json | 14 | 13 (cospfIfConfigError, cospfVirtIfConfigError, cospfTxRetransmit +10 more) | No | No | [x] |
| 41 | CISCO-PIM-MIB.json | 5 | 5 (ciscoPimInterfaceUp, ciscoPimInterfaceDown, ciscoPimRPMappingChange +2 more) | No | No | [x] |
| 42 | CISCO-PING-MIB.json | 1 | 1 (ciscoPingCompletion) | No | No | [x] |
| 43 | CISCO-POWER-ETHERNET-EXT-MIB.json | 1 | 1 (cpeExtPolicingNotif) | No | No | [x] |
| 44 | CISCO-PROCESS-MIB.json | 2 | 2 (cpmCPURisingThreshold, cpmCPUFallingThreshold) | No | No | [x] |
| 45 | CISCO-RF-MIB.json | 3 | 3 (ciscoRFSwactNotif, ciscoRFProgressionNotif, ciscoRFIssuStateNotifRev1) | No | No | [x] |
| 46 | CISCO-RTTMON-MIB.json | 3 | 3 (rttMonNotification, rttMonLpdDiscoveryNotification, rttMonLpdGrpStatusNotification) | No | No | [x] |
| 47 | CISCO-SONET-MIB.json | 4 | 4 (ciscoSonetSectionStatusChange, ciscoSonetLineStatusChange, ciscoSonetPathStatusChange +1 more) | No | No | [x] |
| 48 | CISCO-STACKWISE-MIB.json | 23 | 23 (cswStackPortChange, cswStackNewMaster, cswStackMismatch +20 more) | No | No | [x] |
| 49 | CISCO-STP-EXTENSIONS-MIB.json | 3 | 3 (stpxInconsistencyUpdate, stpxRootInconsistencyUpdate, stpxLoopInconsistencyUpdate) | No | No | [x] |
| 50 | CISCO-SUBSCRIBER-SESSION-MIB.json | 4 | 4 (csubJobFinishedNotify, csubSessionRisingNotif, csubSessionFallingNotif +1 more) | No | No | [x] |
| 51 | CISCO-SYSLOG-MIB.json | 1 | 1 (clogMessageGenerated) | No | No | [x] |
| 52 | CISCO-TAP2-MIB.json | 5 | 5 (ciscoTap2MIBActive, ciscoTap2MediationTimedOut, ciscoTap2MediationDebug +2 more) | No | No | [x] |
| 53 | CISCO-UNIFIED-FIREWALL-MIB.json | 2 | 2 (ciscoUFwUrlfServerStateChange, ciscoUFwL2StaticMacAddressMoved) | No | No | [x] |
| 54 | CISCO-VLAN-MEMBERSHIP-MIB.json | 1 | 1 (vmVmpsChange) | No | No | [x] |
| 55 | CISCO-VOICE-DIAL-CONTROL-MIB.json | 5 | 5 (cvdcPoorQoVNotificationRev1, cvdcActiveDS0sHighNotification, cvdcActiveDS0sLowNotification +2 more) | No | No | [x] |
| 56 | CISCO-VOICE-DNIS-MIB.json | 1 | 1 (cvDnisMappingUrlInaccessible) | No | No | [x] |
| 57 | CISCO-VPDN-MGMT-MIB.json | 1 | 1 (cvpdnNotifSession) | No | No | [x] |
| 58 | CISCO-VTP-MIB.json | 12 | 12 (vtpConfigRevNumberError, vtpConfigDigestError, vtpServerDisabled +9 more) | No | No | [x] |
| 59 | DIAL-CONTROL-MIB.json | 2 | 2 (dialCtlPeerCallInformation, dialCtlPeerCallSetup) | No | No | [x] |
| 60 | DISMAN-EVENT-MIB.json | 5 | 5 (mteTriggerFired, mteTriggerRising, mteTriggerFalling +2 more) | No | No | [x] |
| 61 | DRAFT-MSDP-MIB.json | 2 | 2 (msdpEstablished, msdpBackwardTransition) | No | No | [x] |
| 62 | DS1-MIB.json | 1 | 1 (dsx1LineStatusChange) | No | No | [x] |
| 63 | DS3-MIB.json | 1 | 1 (dsx3LineStatusChange) | No | No | [x] |
| 64 | ENTITY-MIB.json | 1 | 1 (entConfigChange) | No | No | [x] |
| 65 | ENTITY-STATE-MIB.json | 2 | 2 (entStateOperEnabled, entStateOperDisabled) | No | No | [x] |
| 66 | FRAME-RELAY-DTE-MIB.json | 1 | 1 (frDLCIStatusChange) | No | No | [x] |
| 67 | IF-MIB.json | 2 | 2 (linkDown, linkUp) | No | No | [x] |
| 68 | LLDP-MIB.json | 1 | 1 (lldpRemTablesChange) | No | No | [x] |
| 69 | MPLS-L3VPN-STD-MIB.json | 6 | 6 (mplsL3VpnVrfUp, mplsL3VpnVrfDown, mplsL3VpnVrfRouteMidThreshExceeded +3 more) | No | No | [x] |
| 70 | MPLS-LDP-STD-MIB.json | 4 | 4 (mplsLdpInitSessionThresholdExceeded, mplsLdpPathVectorLimitMismatch, mplsLdpSessionUp +1 more) | No | No | [x] |
| 71 | MPLS-LSR-STD-MIB.json | 2 | 2 (mplsXCUp, mplsXCDown) | No | No | [x] |
| 72 | MPLS-TE-STD-MIB.json | 4 | 4 (mplsTunnelUp, mplsTunnelDown, mplsTunnelRerouted +1 more) | No | No | [x] |
| 73 | MPLS-VPN-MIB.json | 5 | 5 (mplsVrfIfUp, mplsVrfIfDown, mplsNumVrfRouteMidThreshExceeded +2 more) | No | No | [x] |
| 74 | OSPF-TRAP-MIB.json | 20 | 20 (ospfVirtIfStateChange, ospfNbrStateChange, ospfVirtNbrStateChange +17 more) | No | No | [x] |
| 75 | PIM-MIB.json | 1 | 1 (pimNeighborLoss) | No | No | [x] |
| 76 | POWER-ETHERNET-MIB.json | 3 | 3 (pethPsePortOnOffNotification, pethMainPowerUsageOnNotification, pethMainPowerUsageOffNotification) | No | No | [x] |
| 77 | RFC1315-MIB.json | 1 | 1 (frDLCIStatusChange) | No | No | [x] |
| 78 | RMON-MIB.json | 2 | 2 (risingAlarm, fallingAlarm) | No | No | [x] |
| 79 | RSVP-MIB.json | 2 | 2 (newFlow, lostFlow) | No | No | [x] |
| 80 | SNMPv2-MIB.json | 3 | 3 (coldStart, warmStart, authenticationFailure) | No | No | [x] |

## Other Event Notifications (9)

| # | File | Paths | Notifs | Has Schema | Has Examples | Status |
|---|------|-------|--------|------------|--------------|--------|
| 1 | cisco-bridge-domain.json | 1 | 1 (bd-state-notification) | Yes | No | [x] |
| 2 | cisco-pw.json | 2 | 2 (vc-up-notification, vc-down-notification) | Yes | No | [x] |
| 3 | cisco-smart-license.json | 24 | 24 (ready, enabled, registration-fail +21 more) | No | No | [x] |
| 4 | ietf-event-notifications.json | 7 | 7 (replay-complete, notification-complete, subscription-started +4 more) | No | No | [x] |
| 5 | ietf-netconf-notifications.json | 5 | 5 (netconf-config-change, netconf-capability-change, netconf-session-start +2 more) | No | No | [x] |
| 6 | ietf-ospf.json | 9 | 9 (if-state-change, if-config-error, nbr-state-change +6 more) | No | No | [x] |
| 7 | ietf-yang-library.json | 2 | 1 (yang-library-update) | No | No | [x] |
| 8 | ietf-yang-push.json | 2 | 2 (push-update, push-change-update) | No | No | [x] |
| 9 | tailf-kicker.json | 1 | 1 (kicker-triggered) | Yes | No | [x] |
