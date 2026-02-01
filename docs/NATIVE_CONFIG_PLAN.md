# Native Config Model - Comprehensive Build Plan

## Overview
Build complete OpenAPI specs for Cisco-IOS-XE-native.yang with all 31 included submodules

## Current State
- **YANG Tree Size**: 7,202 lines (depth=4)
- **Current Specs**: 10 category-based JSON files
- **Categories**: interfaces, routing, security, switching, services, qos, mpls, vpn, wireless, system
- **Generator**: `generators/generate_native_openapi_v2.py` (612 lines)

## YANG Module Structure
```
Cisco-IOS-XE-native.yang (main module)
├── Includes 31 submodules:
│   ├── Cisco-IOS-XE-parser
│   ├── Cisco-IOS-XE-license
│   ├── Cisco-IOS-XE-line
│   ├── Cisco-IOS-XE-logging
│   ├── Cisco-IOS-XE-ip
│   ├── Cisco-IOS-XE-ipv6
│   ├── Cisco-IOS-XE-interfaces
│   ├── Cisco-IOS-XE-hsrp
│   ├── Cisco-IOS-XE-location
│   ├── Cisco-IOS-XE-transceiver-monitor
│   ├── Cisco-IOS-XE-transport
│   └── (and 20 more...)
└── Imports:
    ├── ietf-inet-types
    ├── Cisco-IOS-XE-types
    ├── Cisco-IOS-XE-features
    └── Cisco-IOS-XE-interface-common
```

## Success Strategy

### Phase 1: Enhance Current Generator (PRIORITY)
**Goal**: Add realistic examples and improve existing 10 categories

1. **Add Example Generation**
   - Copy `create_example_data()` from MIB/IETF generators
   - Context-aware examples for network configs
   - Examples: `hostname router1`, `interface Gi1/0/1`, `ip address 192.168.1.1 255.255.255.0`

2. **Improve Path Extraction**
   - Better handle nested containers
   - Parse list keys properly
   - Handle choice/case statements
   - Process augment statements from submodules

3. **Enhance Categorization**
   - Add more specific keywords for better routing
   - Create "uncategorized" catch-all for orphaned paths

### Phase 2: Expand Coverage
**Goal**: Add missing major feature areas

4. **New Categories to Add**:
   - `platform` - hardware-specific configs (stack, modules, breakout)
   - `call-home` - smart licensing, diagnostic reporting
   - `monitor` - SPAN, RSPAN, ERSPAN, flow monitoring
   - `aaa` - authentication, authorization, accounting
   - `crypto` - IPsec, IKEv2, certificates, PKI
   - `voice` - telephony, SIP, H.323

5. **Submodule Integration**:
   - Parse included submodules explicitly
   - Extract paths from each submodule
   - Maintain proper namespacing

### Phase 3: Deep-Dive Critical Areas
**Goal**: Comprehensive coverage of most-used features

6. **Interfaces** (Highest Priority):
   - All interface types: GigabitEthernet, TenGigE, Loopback, Vlan, Tunnel, etc.
   - Interface configuration: IP addressing, VRFs, QoS, security
   - Switchport modes: access, trunk, dynamic
   - Advanced: breakout, channel-groups, port-security

7. **Routing Protocols**:
   - BGP: neighbors, address-families, route-maps
   - OSPF: processes, areas, interfaces, authentication
   - EIGRP: AS configuration, metrics, stub
   - Static routes: IPv4, IPv6, VRF-aware

8. **Security Features**:
   - ACLs: standard, extended, IPv6, named
   - Zone-based firewall: zones, policies, class-maps
   - AAA: RADIUS, TACACS+, local authentication
   - Crypto: site-to-site VPN, FlexVPN, DMVPN

### Phase 4: Validation & Testing
**Goal**: Ensure accuracy and completeness

9. **Validation Steps**:
   - Compare generated paths against pyang tree output
   - Test with real device configurations
   - Validate schema against YANG models
   - Check for duplicate paths

10. **Quality Metrics**:
    - Path coverage: target 80%+ of tree
    - Example accuracy: all examples should be valid CLI
    - Schema completeness: proper types, enums, constraints

## Technical Approach

### Tool Stack
```
pyang -f tree Cisco-IOS-XE-native.yang --tree-depth=4
pyang -f tree Cisco-IOS-XE-native.yang --tree-depth=10 (full depth)
pyang --validate Cisco-IOS-XE-native.yang (validation)
```

### Generator Enhancements Needed

1. **Better YANG Parsing**:
   ```python
   def parse_submodules(self):
       """Parse all included submodules"""
       for submodule in self.included_modules:
           submodule_path = self.yang_dir / f"{submodule}.yang"
           if submodule_path.exists():
               self.parse_yang_file(submodule_path)
   ```

2. **Example Generation**:
   ```python
   def create_example_data(self, schema, path_name):
       """Generate context-aware examples"""
       if 'interface' in path_name.lower():
           return {
               "name": "GigabitEthernet1/0/1",
               "description": "Uplink to Core",
               "ip": {"address": "192.168.1.1", "mask": "255.255.255.0"}
           }
       # ... more context rules
   ```

3. **Comprehensive Categorization**:
   ```python
   categories = {
       'interfaces': [...],
       'routing': [...],
       'security': [...],
       'switching': [...],
       'qos': [...],
       'mpls': [...],
       'vpn': [...],
       'wireless': [...],
       'platform': ['hw-module', 'stack', 'switch', 'breakout'],
       'call-home': ['call-home', 'license', 'smart-licensing'],
       'monitor': ['monitor', 'span', 'rspan', 'erspan', 'flow'],
       'aaa': ['aaa', 'radius', 'tacacs', 'authentication'],
       'crypto': ['crypto', 'ikev2', 'ipsec', 'pki', 'key'],
       'voice': ['voice', 'dial-peer', 'voice-class', 'sip'],
       'system': [...],
       'uncategorized': []  # catch-all
   }
   ```

## File References
- YANG tree saved to: `docs/native-yang-tree.txt` (7,202 lines)
- Current generator: `generators/generate_native_openapi_v2.py`
- Output directory: `swagger-native-config-model/api/`
- Source YANG: `references/17181-YANG-modules/Cisco-IOS-XE-native.yang`

## Success Criteria
- [ ] All 10 current categories have realistic examples
- [ ] 6 new categories added (platform, call-home, monitor, aaa, crypto, voice)
- [ ] Interfaces category has comprehensive coverage
- [ ] Example data is context-aware and valid
- [ ] Total path coverage > 80% of pyang tree
- [ ] All generated specs validate against schemas
- [ ] UI loads and displays specs correctly

## Next Steps
1. Review this plan
2. Start with Phase 1: Add example generation to current generator
3. Test with interfaces category first
4. Iterate and expand
