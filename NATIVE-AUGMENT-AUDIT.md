# NATIVE AUGMENT MODULE AUDIT - COMPLETE REPORT

**Date:** February 9, 2026 (Updated: Phase 2 Complete)  
**Total Modules Audited:** 22  
**Complete Coverage:** 20/22 (91%)  
**Operational-Only (no config YANG):** 2/22 (macsec, trustsec)  
**Current Endpoints:** 253 (across 22 native-*.json files)  
**Status:** ✅ PHASE 2 COMPLETE — kron and lldp now covered

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

## ✅ LAYER 2 PROTOCOLS (6/6 - 100% Complete)

| Module | YANG Tree | Swagger | Location |
|--------|-----------|---------|----------|
| **cdp** | ✓ | ✓ | native-protocols.json (line 367) |
| **udld** | ✓ | ✓ | native-protocols.json (line 1213) |
| **lacp** | ✓ | ✓ | native-protocols.json (line 925) |
| **stp** | ✓ | ✓ | native-00-top-level-containers.json (as `spanning-tree`) |
| **vtp** | ✓ | ✓ | native-switching-l2.json (line 436) |
| **lldp** | ✓ (oper) | ✓ | native-l2-discovery.json (Phase 2) |

**Status:** ✅ All Layer 2 protocols documented

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

## ✅ SCHEDULER / AUTOMATION (2/2 - 100% Complete)

| Module | YANG Tree | Swagger | Location |
|--------|-----------|---------|----------|
| **scheduler** | ✓ | ✓ | native-other.json (line 5514) - Process scheduling |
| **kron** | ✓ | ✓ | native-app-services.json (Phase 2) |

**Note:**
- `kron` and `scheduler` are **DIFFERENT** modules
- `kron` = Job/event scheduling (CLI: `kron occurrence`, `kron policy-list`)
- `scheduler` = Process CPU time allocation (CLI: `scheduler allocate`)
- **kron now covered in Phase 2 ✅**

---

## 📊 SUMMARY STATISTICS

### Overall Coverage
- **Total Modules:** 22
- **Complete:** 20 (91%)
- **Operational-Only (no config YANG):** 2 (macsec, trustsec)

### By Category
- **Routing Protocols:** 7/7 (100%) ✅
- **First-Hop Redundancy:** 3/3 (100%) ✅
- **Layer 2 Protocols:** 6/6 (100%) ✅
- **Security/TrustSec:** 3/5 (60%) ⚠️ (macsec + trustsec are operational-only)
- **Scheduler/Automation:** 2/2 (100%) ✅

---

## ✅ ALL ACTIONS COMPLETED (Phase 2)

### ~~PRIORITY 1: Add kron to Native Config Model~~ ✅ DONE

**kron is now covered in `native-app-services.json` (Phase 2, Batch 1)**

- **YANG Module:** Cisco-IOS-XE-kron.yang
- **Augments:** `/ios:native/` → creates `kron` container
- **Contains:**
  - `occurrence` - Scheduled events/jobs
  - `policy-list` - CLI commands to execute
- **Added to:** `native-app-services.json`
- **Endpoints:**
  ```
  GET    /data/Cisco-IOS-XE-native:native/kron
  PUT    /data/Cisco-IOS-XE-native:native/kron
  PATCH  /data/Cisco-IOS-XE-native:native/kron
  DELETE /data/Cisco-IOS-XE-native:native/kron
  ```

---

### ~~PRIORITY 2: Investigate lldp/macsec/trustsec~~ ✅ RESOLVED

1. **lldp** - ✅ Now covered in `native-l2-discovery.json` (Phase 2, Batch 2)
   - Config endpoint added: `/data/Cisco-IOS-XE-native:native/lldp`

2. **macsec** - ⚠️ Operational data only (no config YANG)
   - Only Cisco-IOS-XE-macsec-oper.html exists
   - Config is via `interface macsec` settings (part of interface model)
   - No standalone config endpoint needed

3. **trustsec** - ⚠️ Operational data only (no config YANG)
   - Only Cisco-IOS-XE-trustsec-oper.html exists
   - Config via `cts` container (already documented in native-security-access.json)
   - No standalone config endpoint needed

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

**The Native Config Model has comprehensive coverage (91%) of audited native augment modules.**

**Phase 2 resolved all critical gaps:**
- ✅ kron added to native-app-services.json
- ✅ lldp added to native-l2-discovery.json
- ⚠️ macsec/trustsec confirmed operational-only (no config YANG exists)

**Full project coverage:** 151 of 163 native augment modules (93%) — see [native-augment-accountability.html](swagger-native-config-model/native-augment-accountability.html) for the complete 163-module report.
