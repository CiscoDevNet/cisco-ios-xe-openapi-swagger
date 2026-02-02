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
- [ ] Modify `extract_nested_paths()` in generate_native_openapi_v2.py
  - [ ] Remove `if depth == 0:` restriction on leaf extraction (lines 572-620)
  - [ ] Extract leafs at depths 1-10
  - [ ] Preserve leaf metadata (type, description)
- [ ] Test generation
  - [ ] Run generator: `python generators/generate_native_openapi_v2.py`
  - [ ] Verify path count increased significantly
  - [ ] Check that leaf examples generate correctly
- [ ] Update UI
  - [ ] Update path counts in index.html
  - [ ] Update manifest.json total_paths
- [ ] Commit & Push
  - [ ] Message: "Phase 1: Extract leafs at all depths - expand from 1,910 to X paths"

**Expected Outcomes:**
- [ ] Total paths > 2,500
- [ ] Leafs extracted from: interface/description, banner/motd/banner-text, etc.
- [ ] All existing paths still work

**Success Criteria:** Path count increases by 600-1,000+

---

## Phase 2: Production-Quality Examples & Schema Validation

**Objective:** Make every API production-ready with realistic data and validation

### Tasks:

#### 2A: Enhanced Examples
- [ ] Update `create_example_data()` function (lines 84-230)
  - [ ] **IP Addresses:** Corporate ranges
    - [ ] IPv4: 10.10.10.1, 172.16.0.1 (not 192.168.x.x)
    - [ ] IPv6: 2001:db8:1::1, fd00::1
  - [ ] **Interfaces:** Realistic naming
    - [ ] Gi1/0/24, Te1/1/1, Po1 (real port numbers)
    - [ ] Loopback0, Vlan100, Tunnel10
  - [ ] **Descriptions:** Network engineer style
    - [ ] "UPLINK_TO_DC2_CORE", "MGMT_VLAN", "BACKUP_LINK"
    - [ ] "BGP_PEER_AS65002", "HSRP_STANDBY"
  - [ ] **VLANs:** Common IDs
    - [ ] 100 (data), 200 (voice), 999 (native)
  - [ ] **AS Numbers:** Believable
    - [ ] Private: 64512-65534
    - [ ] Public: 65001, 65002
  - [ ] **Hostnames:** Data center naming
    - [ ] DC1-CORE-SW01, BRANCH-RTR-01, ACCESS-SW-FL2-01

#### 2B: Schema Validation
- [ ] Add validation patterns to schemas
  - [ ] **Hostnames:** 
    - [ ] Pattern: `^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$`
    - [ ] minLength: 1, maxLength: 63
  - [ ] **VLANs:**
    - [ ] minimum: 1, maximum: 4094
  - [ ] **IP Addresses:**
    - [ ] Pattern: `^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$`
  - [ ] **MAC Addresses:**
    - [ ] Pattern: `^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$`
  - [ ] **Interface Names:**
    - [ ] Pattern: `^(GigabitEthernet|TenGigabitEthernet|Loopback|Vlan|Tunnel)[0-9/]+$`

#### 2C: Testing
- [ ] Generate all specs with new examples
- [ ] Spot-check 20+ paths for realistic data
- [ ] Verify schemas validate correctly in Swagger UI
- [ ] Test against real device (optional)

#### 2D: Commit & Push
- [ ] Message: "Phase 2: Production examples and schema validation for all paths"

**Expected Outcomes:**
- [ ] 100% of examples are copy-paste ready for production
- [ ] All simple types have validation patterns
- [ ] Professional appearance in Swagger UI

**Success Criteria:** Every example looks like real network engineer config

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

**Phase 1:** ⏳ Not Started  
**Phase 2:** ⏳ Not Started  
**Phase 3:** ⏳ Not Started  
**Phase 4:** ⏳ Not Started  

**Overall Progress:** 0% (0/4 phases)

---

## Notes

- Test after EACH phase before moving to next
- Commit after EACH phase with clear message
- Keep file sizes < 5MB for GitHub Pages
- Preserve backward compatibility (existing paths keep working)
