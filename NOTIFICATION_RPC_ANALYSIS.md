# Comprehensive Event Notification & RPC Analysis
## Cisco IOS-XE 17.18.1 YANG Models

Last Updated: February 1, 2026

---

## Executive Summary

**Total Modules:** 848 YANG modules  
**Notification-Enabled Modules:** 53 modules with 200+ notifications  
**RPC-Enabled Modules:** 59 modules with 350+ RPC operations  

### Coverage in OpenAPI Specs

| Category | Indexed | Missing | Notes |
|----------|---------|---------|-------|
| **Event Notifications** | 32 | 21 | Main `-events.yang` modules indexed |
| **RPC Operations** | 53 | 6 | Most RPC modules indexed |
| **Critical Missing** | - | 1 | **Cisco-IOS-XE-ios-events-oper** (53 notifications!) |

---

## Part 1: Event Notifications (Pub/Sub)

### Top 10 Notification-Rich Modules

| Rank | Module | Notifications | Status | Category |
|------|--------|---------------|--------|----------|
| 1 | **Cisco-IOS-XE-ios-events-oper** | 53 | ❌ **MISSING** | Core system events |
| 2 | cisco-smart-license | 24 | ✅ Partial (in Other model) | Licensing |
| 3 | ietf-event-notifications | 10 | ✅ Standard RFC 8639 | IETF standard |
| 4 | ietf-ospf | 9 | ✅ Partial (in IETF model) | Routing |
| 5 | ietf-netconf-notifications | 6 | ✅ Included | NETCONF |
| 6 | Cisco-IOS-XE-controller-shdsl-events | 6 | ✅ Indexed | Controller |
| 7 | Cisco-IOS-XE-perf-measure-events | 6 | ✅ Indexed | Performance |
| 8 | Cisco-IOS-XE-wireless-events-oper | 5 | ❌ **MISSING** | Wireless |
| 9 | Cisco-IOS-XE-wpan-oper | 4 | ✅ In Oper model | Wireless PAN |
| 10 | Cisco-IOS-XE-spanning-tree-events | 4 | ✅ Indexed | Switching |

### Notification Categories

#### Infrastructure Events (53 notifications)
**Module:** `Cisco-IOS-XE-ios-events-oper` ❌ **NOT INDEXED**

Key notifications include:
- **Interface Events:**
  - `interface-admin-state` - Admin state changes (up/down)
  - `interface-oper-state` - Operational state changes
  - `port-bounce-notification` - Port flapping
  - `bridge-oper-state` - Bridge state changes

- **Routing Protocol Events:**
  - `ospf-neighbor-state` - OSPF neighbor changes
  - `ospf-interface-state` - OSPF interface state
  - `bgp-peer-state` - BGP peer state changes
  - `eigrp-neighbor-state` - EIGRP neighbor changes

- **System Events:**
  - `dhcp-server-state` - DHCP server state
  - `syslog-notification` - Syslog message events
  - `cpu-threshold-notification` - CPU utilization
  - `memory-threshold-notification` - Memory utilization
  - `temperature-threshold` - Temperature alarms
  - `fan-state` - Fan failure notifications

- **Security Events:**
  - `radius-server-state` - RADIUS auth state
  - `tacacs-server-state` - TACACS+ state
  - `dot1x-auth-state` - 802.1X authentication
  - `macsec-session-notification` - MACsec events

**Total:** 53 critical infrastructure notifications

**Location:** Should be in Events Model or Operational Model  
**YANG File:** [Cisco-IOS-XE-ios-events-oper.yang](references/17181-YANG-modules/Cisco-IOS-XE-ios-events-oper.yang)

#### Crypto/Security Events (11 notifications)
**Modules:** Crypto-events, crypto-pki-events
- IKE/IPsec tunnel events
- Certificate lifecycle (install, expiry, grant, reject)
- NHRP alarms and events

**Status:** ✅ Indexed in Events Model

#### Wireless Events (15+ notifications)
**Modules:** Multiple wireless-related
- AP state changes
- Client associations/disassociations
- RF interference detection
- Roguedetection

**Status:** ⚠️ Partial - Main wireless-events-oper missing

#### Application Events (4 notifications)
**Modules:** appqoe-events
- AppQoE alarms
- Service chain events

**Status:** ✅ Indexed

#### Controller Events (6 notifications)
**Modules:** controller-shdsl-events
- SHDSL line state changes
- EFM bond rate changes

**Status:** ✅ Indexed

---

## Part 2: RPC Operations (Request/Response)

### Top 10 RPC-Rich Modules

| Rank | Module | RPCs | Status | Category |
|------|--------|------|--------|----------|
| 1 | Cisco-IOS-XE-wireless-access-point-cmd-rpc | 51 | ✅ Indexed | Wireless AP commands |
| 2 | Cisco-IOS-XE-wireless-access-point-cfg-rpc | 44 | ✅ Indexed | Wireless AP config |
| 3 | **Cisco-IOS-XE-rpc** | 21 | ✅ Indexed | **Core system RPCs** |
| 4 | Cisco-IOS-XE-wireless-mesh-rpc | 21 | ✅ Indexed | Wireless mesh |
| 5 | Cisco-IOS-XE-wireless-rogue-authz-rpc | 15 | ✅ Indexed | Rogue management |
| 6 | ietf-netconf | 13 | ✅ Standard | NETCONF protocol |
| 7 | cisco-smart-license | 13 | ✅ In Other model | Licensing ops |
| 8 | Cisco-IOS-XE-install-rpc | 10 | ✅ Indexed | Software install |
| 9 | Cisco-IOS-XE-wireless-ble-mgmt-cmd-rpc | 8 | ✅ Indexed | BLE management |
| 10 | cisco-ia | 8 | ⚠️ Reference only | Infrastructure |

### RPC Categories

#### Core System Operations (21 RPCs)
**Module:** `Cisco-IOS-XE-rpc` ✅ **INDEXED**

Essential operations:
- `save-config` - Save running config
- `reload` - Reload device
- `factory-reset` - Factory reset
- `copy` - Copy files
- `license` - License management
- `test` - System diagnostics
- `clear` - Clear statistics
- `debug` - Enable debugging
- `ping` - Network connectivity test
- `traceroute` - Path tracing
- `default` - Reset to default

**Status:** ✅ Fully indexed in RPC Model  
**API:** https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-rpc-model/

#### Software Management (10 RPCs)
**Module:** `Cisco-IOS-XE-install-rpc`
- Install packages
- Activate/deactivate images  
- Commit/rollback software
- Auto-abort timer

**Status:** ✅ Indexed

#### Wireless Operations (140+ RPCs)
**Modules:** Multiple wireless-*-rpc modules
- AP provisioning and control
- Client management
- RF management
- Mesh configuration
- Rogue detection/authorization

**Status:** ✅ Fully indexed

#### Security Operations (12 RPCs)
**Modules:** crypto-actions-rpc, aaa-actions-rpc, cts-rpc
- Clear crypto sessions
- Test AAA authentication/authorization
- TrustSec policy updates
- SSL proxy operations

**Status:** ✅ Indexed

#### Network Tools (7 RPCs)
**Modules:** livetools-actions-rpc, livetools-oper
- Ping
- Traceroute
- Packet capture
- Network diagnostics

**Status:** ✅ Indexed

#### Troubleshooting (8 RPCs)
**Modules:** tech-support-rpc, trace-rpc, cli-rpc
- Generate tech-support
- Trace collection
- CLI command execution

**Status:** ✅ Indexed

---

## Part 3: Missing/Unmapped Modules

### Critical Missing Notification Module

**Cisco-IOS-XE-ios-events-oper.yang** ❌
- **Notifications:** 53 (most in entire platform!)
- **Category:** Core infrastructure events
- **Reason Missing:** Name pattern mismatch
  - Events generator looks for: `*-events.yang`
  - This module is: `*-events-oper.yang`
- **Impact:** HIGH - Missing interface state changes, routing events, system alarms
- **Resolution:** Manual addition required

### Other Missing Event Modules

1. **Cisco-IOS-XE-wireless-events-oper.yang** (5 notifications)
   - Wireless infrastructure events
   - Should be in Events or Operational model

2. **Cisco-IOS-XE-platform-events-oper.yang** (2 notifications)
   - Platform hardware events

3. **Cisco-IOS-XE-im-events-oper.yang** (1 notification)
   - Interface manager events

4. **Cisco-IOS-XE-stack-mgr-events-oper.yang** (0 data paths)
   - Stack management events

5. **Cisco-IOS-XE-sm-events-oper.yang** (0 data paths)
   - Session manager events

### Modules with Both Notifications AND Data

Several modules contain both:
- **cisco-bridge-domain.yang** - Has 1 notification + config/operational data
- **cisco-smart-license.yang** - Has 24 notifications + operational data  
- **Cisco-IOS-XE-wpan-oper.yang** - Has 4 notifications + operational data
- **Cisco-IOS-XE-umbrella-oper-dp.yang** - Has 2 notifications + operational data

These are correctly split between models based on primary purpose.

---

## Part 4: Subscription Mechanisms

### YANG Push (RFC 8639)
**Module:** `ietf-event-notifications`, `ietf-yang-push`

Subscription types:
- Periodic subscriptions
- On-change subscriptions  
- Dynamic vs configured subscriptions

**RPCs:**
- `establish-subscription`
- `modify-subscription`
- `delete-subscription`
- `kill-subscription`
- `resync-subscription`

### NETCONF Notifications (RFC 5277)
**Module:** `ietf-netconf-notifications`

Standard notifications:
- `netconf-config-change`
- `netconf-capability-change`
- `netconf-session-start`
- `netconf-session-end`
- `netconf-confirmed-commit`
- `netconf-session-alarm`

---

## Part 5: Recommendations

### Immediate Actions

1. **Add Cisco-IOS-XE-ios-events-oper to Events Model**
   - Create OpenAPI spec with 53 notifications
   - Update manifest
   - Critical for interface/routing/system event monitoring

2. **Add Missing Wireless Event Module**
   - Cisco-IOS-XE-wireless-events-oper
   - 5 wireless infrastructure notifications

3. **Document Event vs Operational Distinction**
   - Clarify when to use Events model (subscriptions)
   - vs Operational model (polling)

### Best Practices

#### When to Use Events (Notifications)
✅ Use for real-time monitoring:
- Interface state changes
- Routing protocol neighbor changes
- Security events (auth failures, intrusions)
- Hardware alarms (temperature, fan, power)
- Certificate expiry warnings

**Mechanism:** YANG Push subscriptions (on-change or periodic)  
**Protocol:** NETCONF/RESTCONF subscriptions  
**Latency:** Real-time (sub-second)

#### When to Use Operational Data (Polling)
✅ Use for periodic collection:
- Statistics and counters
- Configuration state verification
- Inventory and hardware details
- Performance metrics

**Mechanism:** GET requests on operational data  
**Protocol:** RESTCONF/NETCONF  
**Latency:** Poll interval (seconds to minutes)

#### When to Use RPCs
✅ Use for actions:
- Execute commands (reload, save-config)
- Trigger operations (install software)
- Run diagnostics (ping, traceroute)
- Manage services (license activation)

**Mechanism:** RPC/action invocation  
**Protocol:** NETCONF/RESTCONF  
**Pattern:** Request/Response

---

## Part 6: Quick Reference

### Find Interface Admin State Change

**Real-time notification:**
```
Module: Cisco-IOS-XE-ios-events-oper (NOT YET INDEXED)
Notification: interface-admin-state
Fields: if-name, new-admin-state, severity-level
```

**Current state polling:**
```
Module: Cisco-IOS-XE-interfaces-oper (INDEXED)
Path: /data/interfaces-ios-xe-oper:interfaces/interface={name}
Fields: admin-status, oper-status, last-change
API: https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-oper-model/
```

### Save Configuration

**RPC:**
```
Module: Cisco-IOS-XE-rpc (INDEXED) 
RPC: save-config
API: https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-rpc-model/
Endpoint: POST /operations/cisco-ia:save-config
```

### BGP Neighbor State Change

**Real-time notification:**
```
Module: Cisco-IOS-XE-ios-events-oper (NOT YET INDEXED)
Notification: bgp-peer-state
```

**Current state polling:**
```
Module: Cisco-IOS-XE-bgp-oper (INDEXED)
Path: /data/bgp-state-data:bgp-state-data
API: https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-oper-model/
```

### OSPF Neighbor State

**Real-time notification:**
```
Module: Cisco-IOS-XE-ios-events-oper (NOT YET INDEXED)
Notification: ospf-neighbor-state
```

**IETF standard notification:**
```
Module: Cisco-IOS-XE-ospf-events (INDEXED)
Notifications: ospf-neighbor-event, ospf-interface-event
API: https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-events-model/
```

---

## Part 7: Complete Module Lists

### All Notification Modules (53 modules)

```
Cisco-IOS-XE-ios-events-oper              53 notifications ❌ NOT INDEXED
cisco-smart-license                       24 notifications ✅ In Other
ietf-event-notifications                  10 notifications ✅ IETF
ietf-ospf                                  9 notifications ✅ IETF
ietf-netconf-notifications                 6 notifications ✅ Included
Cisco-IOS-XE-controller-shdsl-events       6 notifications ✅ Events
Cisco-IOS-XE-perf-measure-events           6 notifications ✅ Events
Cisco-IOS-XE-wireless-events-oper          5 notifications ❌ NOT INDEXED
Cisco-IOS-XE-wpan-oper                     4 notifications ✅ Oper
Cisco-IOS-XE-spanning-tree-events          4 notifications ✅ Events
ietf-yang-push                             4 notifications ✅ Included
tailf-kicker                               3 notifications ⚠️ Tailf extension
Cisco-IOS-XE-crypto-events                 3 notifications ✅ Events
Cisco-IOS-XE-platform-events-oper          2 notifications ❌ NOT INDEXED
Cisco-IOS-XE-nat-events                    2 notifications ✅ Events
Cisco-IOS-XE-ospf-events                   2 notifications ✅ Events
cisco-pw                                   2 notifications ⚠️ Reference
ietf-yang-library                          2 notifications ✅ Included
Cisco-IOS-XE-qfp-resource-events           2 notifications ✅ Events
Cisco-IOS-XE-umbrella-oper-dp              2 notifications ✅ Oper
Cisco-IOS-XE-appqoe-events                 2 notifications ✅ Events
Cisco-IOS-XE-crypto-pki-events             2 notifications ✅ Events
Cisco-IOS-XE-fib-events                    2 notifications ✅ Events
Cisco-IOS-XE-endpoint-tracker-events       2 notifications ✅ Events
+ 29 more modules with 1 notification each
```

### All RPC Modules (59 modules)

```
Cisco-IOS-XE-wireless-access-point-cmd-rpc    51 RPCs ✅ RPC
Cisco-IOS-XE-wireless-access-point-cfg-rpc    44 RPCs ✅ RPC
Cisco-IOS-XE-rpc                              21 RPCs ✅ RPC
Cisco-IOS-XE-wireless-mesh-rpc                21 RPCs ✅ RPC
Cisco-IOS-XE-wireless-rogue-authz-rpc         15 RPCs ✅ RPC
ietf-netconf                                  13 RPCs ✅ Standard
cisco-smart-license                           13 RPCs ✅ Other
Cisco-IOS-XE-install-rpc                      10 RPCs ✅ RPC
Cisco-IOS-XE-wireless-ble-mgmt-cmd-rpc         8 RPCs ✅ RPC
cisco-ia                                       8 RPCs ⚠️ Reference
Cisco-IOS-XE-livetools-actions-rpc             7 RPCs ✅ RPC
ietf-event-notifications                       6 RPCs ✅ Standard
Cisco-IOS-XE-rescue-config-rpc                 5 RPCs ✅ RPC
tailf-netconf-query                            5 RPCs ⚠️ Tailf
Cisco-IOS-XE-wireless-rrm-rpc                  5 RPCs ✅ RPC
Cisco-IOS-XE-utd-actions-rpc                   5 RPCs ✅ RPC
Cisco-IOS-XE-wireless-client-rpc               4 RPCs ✅ RPC
Cisco-IOS-XE-sslproxy-rpc                      4 RPCs ✅ RPC
tailf-netconf-transactions                     4 RPCs ⚠️ Tailf
Cisco-IOS-XE-crypto-actions-rpc                4 RPCs ✅ RPC
+ 39 more modules with 1-3 RPCs each
```

---

## Conclusion

The Cisco IOS-XE 17.18.1 platform provides extensive event notification and RPC capabilities across 848 YANG modules. While most are properly indexed, the **critical Cisco-IOS-XE-ios-events-oper module** containing 53 infrastructure notifications is currently missing from the OpenAPI specifications.

**Priority:** Add ios-events-oper to enable real-time monitoring of:
- Interface state changes
- Routing protocol events  
- System health alarms
- Security events

This module is the most important missing piece for comprehensive network automation and monitoring.
