# Native Config Model Enhancement Plan

**Created:** February 1, 2026  
**Goal:** Transform Native Config from 1,910 paths to 3,000+ with production-quality examples  
**Timeline:** 4 Phases - Execute systematically

---

## Current State

- **Total Paths:** 1,910
- **Leafs:** 9 (depth-0 only: hostname, version, config-register, etc.)
- **Containers/Lists:** 1,901 (complex nested objects)
- **Categories:** 11 (some over 800 paths)
- **Examples:** Basic placeholders
- **Validation:** None

---

## Phase 1: Extract All Leafs at All Depths

**Objective:** Extract simple value APIs (leafs) at ALL depths, not just depth-0

**Target:** 2,500-3,000 total paths

### Tasks:
- [x] Modify `extract_nested_paths()` in generate_native_openapi_v2.py ✅
  - [x] Remove `if depth == 0:` restriction on leaf extraction (lines 572-620) ✅
  - [x] Extract leafs at depths 1-10 ✅
  - [x] Preserve leaf metadata (type, description) ✅
- [x] Test generation ✅
  - [x] Run generator: `python generators/generate_native_openapi_v2.py` ✅
  - [x] Verify path count increased significantly ✅
  - [x] Check that leaf examples generate correctly ✅
- [x] Update UI ✅
  - [x] Update path counts in index.html ✅
  - [x] Update manifest.json total_paths ✅
- [x] Commit & Push ✅
  - [x] Message: "Phase 1 COMPLETE: Extract leafs at all depths - 1,910 to 5,267 paths (+176%)" ✅

**Expected Outcomes:**
- [x] Total paths > 2,500 → **ACHIEVED: 5,267 paths (+176%)** ✅
- [x] Leafs extracted from: interface/description, banner/motd/banner-text, etc. ✅
- [x] All existing paths still work ✅

**Success Criteria:** Path count increases by 600-1,000+ → **EXCEEDED: +3,357 paths**

---

## Phase 2: Production-Quality Examples & Schema Validation

**Objective:** Make every API production-ready with realistic data and validation

### Tasks:

#### 2A: Enhanced Examples
- [x] Update `create_example_data()` function (lines 84-230) ✅
  - [x] **IP Addresses:** Corporate ranges ✅
    - [x] IPv4: 10.10.10.1, 172.16.0.1 (not 192.168.x.x) ✅
    - [x] IPv6: 2001:db8:1::1, fd00::1 ✅
  - [x] **Interfaces:** Realistic naming ✅
    - [x] Gi1/0/24, Te1/1/1, Po1 (real port numbers) ✅
    - [x] Loopback0, Vlan100, Tunnel10 ✅
  - [x] **Descriptions:** Network engineer style ✅
    - [x] "UPLINK_TO_DC2_CORE", "MGMT_VLAN", "BACKUP_LINK" ✅
    - [x] "BGP_PEER_AS65002", "HSRP_STANDBY" ✅
  - [x] **VLANs:** Common IDs ✅
    - [x] 100 (data), 200 (voice), 999 (native) ✅
  - [x] **AS Numbers:** Believable ✅
    - [x] Private: 64512-65534 ✅
    - [x] Public: 65001, 65002 ✅
  - [x] **Hostnames:** Data center naming ✅
    - [x] DC1-CORE-SW01, BRANCH-RTR-01, ACCESS-SW-FL2-01 ✅

#### 2B: Schema Validation
- [x] Add validation patterns to schemas ✅
  - [x] **Hostnames:** ✅
    - [x] Pattern: `^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$` ✅
    - [x] minLength: 1, maxLength: 63 ✅
  - [x] **VLANs:** ✅
    - [x] minimum: 1, maximum: 4094 ✅
  - [x] **IP Addresses:** ✅
    - [x] Pattern: `^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$` ✅
  - [x] **MAC Addresses:** ✅
    - [x] Pattern: `^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$` ✅
  - [x] **Interface Names:** ✅
    - [x] Pattern: `^(GigabitEthernet|TenGigabitEthernet|Loopback|Vlan|Tunnel)[0-9/]+$` ✅

#### 2C: Testing
- [x] Generate all specs with new examples ✅
- [x] Spot-check 20+ paths for realistic data ✅
- [x] Verify schemas validate correctly in Swagger UI ✅
- [ ] Test against real device (optional)

#### 2D: Commit & Push
- [x] Message: "Phase 2 COMPLETE: Production examples (10.x IPs, Gi1/0/24, realistic descriptions) + schema validation" ✅

**Expected Outcomes:**
- [x] 100% of examples are copy-paste ready for production ✅
- [x] All simple types have validation patterns ✅
- [x] Professional appearance in Swagger UI ✅

**Success Criteria:** Every example looks like real network engineer config → **ACHIEVED**

---

## Phase 3: Reorganize into Focused Categories

**Objective:** Split large categories, create intuitive navigation

**Target:** 15-18 categories, max 350 paths each

### Tasks:

#### 3A: Split "Services" (872 paths)
- [ ] Create new categories in `category_keywords` dict:
  - [ ] **native-aaa:** authentication, authorization, RADIUS, TACACS
  - [ ] **native-dhcp:** DHCP server, relay, pools
  - [ ] **native-ntp:** NTP server, peers, authentication
  - [ ] **native-snmp:** SNMP community, traps, server
  - [ ] **native-logging:** Syslog, buffered, console logging
  - [ ] **native-dns:** Domain lookup, name-server
- [ ] Update categorization logic to check new categories first

#### 3B: Add New Categories
- [ ] **native-ha:** High availability configs
  - [ ] Keywords: hsrp, vrrp, redundancy, stack, issu
- [ ] **native-cli:** User interface configs
  - [ ] Keywords: banner, parser, line, alias
- [ ] **native-license:** Licensing and smart licensing
  - [ ] Keywords: license, smart-licensing, call-home

#### 3C: Update Category Titles
- [ ] Add to `category_titles` dict in `create_openapi_spec()`
- [ ] Update priority_categories list with new order

#### 3D: Regenerate & Update UI
- [ ] Run generator
- [ ] Update swagger-native-config-model/index.html module list
- [ ] Verify all categories < 350 paths
- [ ] Test navigation in browser

#### 3E: Commit & Push
- [ ] Message: "Phase 3: Split into 18 focused categories - max 350 paths each"

**Expected Outcomes:**
- [ ] 18 categories total
- [ ] Easy to find specific configs (DHCP, NTP, etc.)
- [ ] Faster page loads (smaller files)

**Success Criteria:** Average category size < 200 paths, max < 350

---

## Phase 4: Quick Start Collections

**Objective:** Curated mini-specs for common workflows

### Tasks:

#### 4A: Create Day-0 Quick Start
- [ ] **native-00-day0.json** (15-20 paths)
  - [ ] Hostname
  - [ ] Domain name
  - [ ] Enable secret
  - [ ] Username/password
  - [ ] SSH server enable
  - [ ] Line vty configs
  - [ ] NTP server
  - [ ] Logging buffered
  - [ ] SNMP community (read-only)
  - [ ] Banner login/motd

#### 4B: Create Interface Quick Start
- [ ] **native-00-interface-basics.json** (20-25 paths)
  - [ ] interface/description
  - [ ] interface/ip/address
  - [ ] interface/shutdown
  - [ ] interface/speed
  - [ ] interface/duplex
  - [ ] interface/switchport/mode
  - [ ] interface/switchport/access/vlan
  - [ ] interface/mtu
  - [ ] interface/cdp/enable
  - [ ] interface/lldp/transmit

#### 4C: Create Routing Quick Start
- [ ] **native-00-routing-basics.json** (15-20 paths)
  - [ ] router/bgp/as-number
  - [ ] router/bgp/neighbor/ip
  - [ ] router/ospf/process-id
  - [ ] router/ospf/network
  - [ ] ip/route (static routes)
  - [ ] ipv6/route
  - [ ] redistribute/connected
  - [ ] route-map basics

#### 4D: Update Generator Logic
- [ ] Add "day0", "interface-basics", "routing-basics" to core category detection
- [ ] Create manual curation function for these specific paths
- [ ] Generate with "00-" prefix to appear first

#### 4E: Update UI
- [ ] Add ⭐ emoji to quick start modules
- [ ] Update welcome message to highlight quick starts
- [ ] Auto-load "day0" on first page visit
- [ ] Update module counts in index.html

#### 4F: Commit & Push
- [ ] Message: "Phase 4: Add 3 Quick Start collections for common workflows"

**Expected Outcomes:**
- [ ] 3 new quick-start files
- [ ] Each < 25 paths
- [ ] New users productive in < 30 seconds

**Success Criteria:** Can configure basic router/switch without reading docs

---

## Final Verification

After all phases complete:

- [ ] **Total paths:** 2,500-3,000+
- [ ] **Categories:** 18-20 focused groups
- [ ] **Quick starts:** 3 curated collections
- [ ] **Examples:** 100% production-realistic
- [ ] **Validation:** All simple types have patterns/ranges
- [ ] **UI:** Clean, fast, intuitive navigation
- [ ] **GitHub Pages:** All files < 5MB, deploys successfully
- [ ] **Documentation:** README updated with new features

---

## Rollback Plan

If any phase fails:
1. Check git log: `git log --oneline -10`
2. Revert to previous commit: `git reset --hard <commit-hash>`
3. Fix issue
4. Re-run phase

---

## Progress Tracking

**Phase 1:** ✅ COMPLETE (1,910 → 5,267 paths, +176%)  
**Phase 2:** ✅ COMPLETE (Production examples + schema validation)  
**Phase 3:** ⏳ Not Started  
**Phase 4:** ⏳ Not Started  

**Overall Progress:** 50% (2/4 phases)

---

## Notes

- Test after EACH phase before moving to next
- Commit after EACH phase with clear message
- Keep file sizes < 5MB for GitHub Pages
- Preserve backward compatibility (existing paths keep working)
