# Native Config XPath Coverage Analysis

## Summary
- **Total Paths Generated**: 1,155
- **Previous (Top-level only)**: 242  
- **Improvement**: 913 additional paths (477% increase)

## Path Distribution by Category

| Category | Paths | Example Paths |
|----------|-------|---------------|
| Interfaces | 195 | `native/interface`, `native/monitor/session={id}/source/interface={name}` |
| System | 723 | `native/banner`, `native/clock`, `native/scheduler` |
| Security | 51 | `native/aaa`, `native/radius-server`, `native/tacacs` |
| Platform | 59 | `native/hw-module`, `native/stack`, `native/redundancy` |
| Services | 42 | `native/ntp`, `native/archive`, `native/boot` |
| QoS | 21 | `native/policy`, `native/class-map`, `native/policy-map` |
| Crypto | 16 | `native/crypto/ikev2`, `native/crypto/pki` |
| Routing | 11 | `native/router`, `native/ip/route` |
| Switching | 18 | `native/vlan`, `native/spanning-tree`, `native/vtp` |
| Monitor | 14 | `native/monitor/session={id}`, `native/flow` |
| MPLS | 2 | `native/mpls` |
| Call-Home | 1 | `native/call-home` |
| Voice | 1 | `native/voice` |
| VPN | 1 | `native/vpn` |

## Recursive Extraction Features

### Depth Coverage
- **Max Depth**: 10 levels
- **Example Deep Path**: `native/monitor/session={id}/type/erspan-source/source/interface={name}` (6 levels)

### List Handling
- Each YANG list generates **2 REST endpoints**:
  1. **Collection endpoint**: `/native/list-name` (GET all, POST create)
  2. **Item endpoint**: `/native/list-name={key}` (GET/PUT/PATCH/DELETE specific item)

### Nested Containers
Recursively extracts:
- Containers within containers
- Lists within containers
- Containers within lists
- Lists within lists

## Example Path Hierarchies

### Interface Configuration
```
native/interface
native/interface/AppNav-Compress
native/interface/AppNav-Compress/arp
native/interface/AppNav-Compress/bfd
native/interface/AppNav-Compress/mpls
```

### Monitor/SPAN Sessions
```
native/monitor/session={id}
native/monitor/session={id}/type
native/monitor/session={id}/type/erspan-source
native/monitor/session={id}/type/erspan-source/source
native/monitor/session={id}/type/erspan-source/source/interface={name}
```

### Redundancy Configuration
```
native/redundancy
native/redundancy/interchassis
native/redundancy/interchassis/group={group-number}
native/redundancy/interchassis/group={group-number}/backbone
native/redundancy/interchassis/group={group-number}/backbone/interface-list={id}
```

## Coverage Validation

### Extraction Method
1. Parse `Cisco-IOS-XE-native.yang` module
2. Load 11 included submodules (parser, license, line, logging, ip, ipv6, interfaces, hsrp, location, transceiver-monitor, transport)
3. Extract native container
4. Recursively traverse all nested containers and lists up to depth 10
5. Generate OpenAPI paths with proper RESTCONF formatting

### Known Limitations
- **Groupings**: Some YANG models use grouping/uses extensively - not all groupings are fully expanded
- **Augments**: External modules that augment native may not be included
- **Choices/Cases**: Complex choice statements may be simplified
- **When/Must**: Conditional nodes always included (conditions in description)

## Next Steps for 100% Coverage

1. **Verify grouping expansion**: Check if all `uses` statements are resolved
2. **Include augments**: Add paths from modules that augment native
3. **Depth analysis**: Confirm max depth reached matches YANG model
4. **Compare with pyang**: Generate comprehensive tree for validation

## Technical Implementation

### Recursive Function
```python
def extract_nested_paths(self, content, parent_path, depth=0, max_depth=10):
    # Recursively extract containers and lists
    # Returns list of path dictionaries with schema
```

### Path Structure
```python
{
    'path': 'native/container/subcontainer',
    'name': 'subcontainer',
    'description': 'Container description',
    'schema': {...},
    'is_list': False,
    'depth': 2
}
```

### Generated OpenAPI Paths
- **Container**: `/data/Cisco-IOS-XE-native:native/container`
- **List Collection**: `/data/Cisco-IOS-XE-native:native/list-name`  
- **List Item**: `/data/Cisco-IOS-XE-native:native/list-name={key}`
