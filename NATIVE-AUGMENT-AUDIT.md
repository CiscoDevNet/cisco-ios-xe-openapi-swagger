# NATIVE AUGMENT MODULE AUDIT - COMPLETE REPORT

**Date:** February 9, 2026  
**Total Modules Audited:** 22  
**Complete Coverage:** 18/22 (82%)  
**Missing:** 4/22 (18%)  
**Current Endpoints:** 183 (across 14 native-*.json files)  
**Status:** ✅ VERIFIED - kron is confirmed MISSING

---

## ✅ ROUTING PROTOCOLS (7/7 - 100% Complete)

| Module | YANG Tree | Swagger | Location |
|--------|-----------|---------|----------|
| **bgp** | ✓ | ✓ | native-router.json |
| **eigrp** | ✓ | ✓ | native-router.json |
| **ospf** | ✓ | ✓ | native-router.json + ietf-ospf.json |
| **ospfv3** | ✓ | ✓ | native-router.json |
| **rip** | ✓ | ✓ | native-router.json |
| **isis** | ✓ | ✓ | native-router.json |
| **route-map** | ✓ | ✓ | native-other.json (line 5142) |

**Status:** ✅ All routing protocols documented

---

## ✅ FIRST-HOP REDUNDANCY (3/3 - 100% Complete)

| Module | YANG Tree | Swagger | Location |
|--------|-----------|---------|----------|
| **hsrp** | ✓ | ✓ | native-other.json (as `standby`, line 6233) |
| **vrrp** | ✓ | ✓ | native-other.json (as `fhrp`, line 1944) |
| **track** | ✓ | ✓ | native-other.json (line 6969) |

**Status:** ✅ All FHRP protocols documented

---

## ⚠️ LAYER 2 PROTOCOLS (5/6 - 83% Complete)

| Module | YANG Tree | Swagger | Location |
|--------|-----------|---------|----------|
| **cdp** | ✓ | ✓ | native-protocols.json (line 367) |
| **udld** | ✓ | ✓ | native-protocols.json (line 1213) |
| **lacp** | ✓ | ✓ | native-protocols.json (line 925) |
| **stp** | ✓ | ✓ | native-00-top-level-containers.json (as `spanning-tree`) |
| **vtp** | ✓ | ✓ | native-switching-l2.json (line 436) |
| **lldp** | ✓ (oper) | ❌ | **MISSING** - Cisco-IOS-XE-lldp-oper.html only |

**Status:** ⚠️ LLDP missing - may be operational data only

---

## ⚠️ SECURITY / TRUSTSEC (3/5 - 60% Complete)

| Module | YANG Tree | Swagger | Location |
|--------|-----------|---------|----------|
| **dot1x** | ✓ | ✓ | native-security-access.json (line 419) |
| **cts** | ✓ | ✓ | native-security-access.json (line 817) |
| **mka** | ✓ | ✓ | native-security-access.json (line 1414) |
| **macsec** | ✓ (oper) | ❌ | **MISSING** - Cisco-IOS-XE-macsec-oper.html only |
| **trustsec** | ✓ (oper) | ❌ | **MISSING** - Cisco-IOS-XE-trustsec-oper.html only |

**Status:** ⚠️ MACsec and TrustSec missing - may be operational data only

---

## ❌ SCHEDULER / AUTOMATION (1/2 - 50% Complete)

| Module | YANG Tree | Swagger | Location |
|--------|-----------|---------|----------|
| **scheduler** | ✓ | ✓ | native-other.json (line 5514) - Process scheduling |
| **kron** | ✓ | ❌ | **MISSING** - Cisco-IOS-XE-kron.html exists |

**Critical Finding:**
- `kron` and `scheduler` are **DIFFERENT** modules
- `kron` = Job/event scheduling (CLI: `kron occurrence`, `kron policy-list`)
- `scheduler` = Process CPU time allocation (CLI: `scheduler allocate`)
- **kron HAS config YANG but NO Swagger API**

---

## 📊 SUMMARY STATISTICS

### Overall Coverage
- **Total Modules:** 22
- **Complete:** 18 (82%)
- **Missing:** 4 (18%)

### By Category
- **Routing Protocols:** 7/7 (100%) ✅
- **First-Hop Redundancy:** 3/3 (100%) ✅
- **Layer 2 Protocols:** 5/6 (83%) ⚠️
- **Security/TrustSec:** 3/5 (60%) ⚠️
- **Scheduler/Automation:** 1/2 (50%) ❌

---

## 🚨 ACTION REQUIRED

### PRIORITY 1: Add kron to Native Config Model

**kron is the ONLY config module with YANG but no Swagger API**

- **YANG Module:** Cisco-IOS-XE-kron.yang
- **Augments:** `/ios:native/` → creates `kron` container
- **Contains:**
  - `occurrence` - Scheduled events/jobs
  - `policy-list` - CLI commands to execute
- **Should be added to:** `native-other.json`
- **Endpoints needed:**
  ```
  GET    /data/Cisco-IOS-XE-native:native/kron
  PUT    /data/Cisco-IOS-XE-native:native/kron
  PATCH  /data/Cisco-IOS-XE-native:native/kron
  DELETE /data/Cisco-IOS-XE-native:native/kron
  ```

**Example kron config:**
```json
{
  "Cisco-IOS-XE-native:kron": {
    "occurrence": [
      {
        "name": "backup-config",
        "at": "02:00",
        "recurring": true,
        "policy-list": "backup-policy"
      }
    ],
    "policy-list": [
      {
        "name": "backup-policy",
        "cli": [
          "copy running-config tftp://server/backup.cfg"
        ]
      }
    ]
  }
}
```

---

### PRIORITY 2: Investigate lldp/macsec/trustsec

**These modules only have operational YANG (read-only data)**

1. **lldp** - Cisco-IOS-XE-lldp-oper.html
   - May not have config YANG
   - Config might be via `interface` settings only
   - Verify if Cisco-IOS-XE-lldp.yang (config) exists

2. **macsec** - Cisco-IOS-XE-macsec-oper.html
   - Operational data only
   - Config might be via `interface macsec` settings
   - Verify if Cisco-IOS-XE-macsec.yang (config) exists

3. **trustsec** - Cisco-IOS-XE-trustsec-oper.html
   - Operational data only
   - Config via `cts` container (already documented)
   - May not need separate endpoint

---

## 📋 VERIFICATION DETAILS

### YANG Tree Files Found (yang-trees/)
All 22 modules have YANG tree HTML files:
- ✓ Cisco-IOS-XE-kron.html
- ✓ BGP4-MIB.html, Cisco-IOS-XE-bgp.html
- ✓ CISCO-EIGRP-MIB.html, Cisco-IOS-XE-eigrp.html
- ✓ Cisco-IOS-XE-ospf-events.html, Cisco-IOS-XE-ospf.html
- ✓ Cisco-IOS-XE-ospfv3.html
- ✓ Cisco-IOS-XE-rip.html
- ✓ CISCO-IETF-ISIS-MIB.html
- ✓ Cisco-IOS-XE-vrrp-oper.html
- ✓ CISCO-HSRP-EXT-MIB.html
- ✓ Cisco-IOS-XE-device-tracking.html
- ✓ Cisco-IOS-XE-route-map.html
- ✓ CISCO-CDP-MIB.html
- ✓ Cisco-IOS-XE-lldp-oper.html
- ✓ Cisco-IOS-XE-udld-events.html
- ✓ Cisco-IOS-XE-lacp-oper.html
- ✓ CISCO-STP-EXTENSIONS-MIB.html
- ✓ Cisco-IOS-XE-vtp.html
- ✓ Cisco-IOS-XE-cts-rpc.html
- ✓ Cisco-IOS-XE-trustsec-oper.html
- ✓ Cisco-IOS-XE-dot1x.html
- ✓ Cisco-IOS-XE-mka-oper.html
- ✓ Cisco-IOS-XE-macsec-oper.html

### Swagger API Files (swagger-native-config-model/api/)
- native-router.json - Contains bgp, eigrp, ospf, ospfv3, rip, isis
- native-other.json - Contains route-map, hsrp (standby), vrrp (fhrp), track, scheduler
- native-protocols.json - Contains cdp, udld, lacp
- native-switching-l2.json - Contains vtp
- native-00-top-level-containers.json - Contains stp (spanning-tree)
- native-security-access.json - Contains dot1x, cts, mka

---

## ✅ CONCLUSION

**The Native Config Model has excellent coverage (82%) of native augment modules.**

**Only 1 critical gap:** kron scheduler configuration needs to be added.

**Next Steps:**
1. Add kron endpoints to native-other.json
2. Verify lldp/macsec/trustsec have config YANG modules
3. Update documentation to reflect complete coverage
