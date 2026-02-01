# RPC Validation Findings

## Summary
Verified RPC specifications against YANG sources using `pyang -f tree` to identify discrepancies.

## Issues Found

### 1. Choice Statements Not Supported ❌
**Impact:** HIGH - Affects 40+ RPC operations

The generator does NOT handle YANG `choice` statements correctly. When a YANG RPC has:
```yang
+---w (alternative-choice)
   +--:(ap-identifier-name)
   |  +---w ap-name     string
   +--:(ap-identifier-mac-address)
      +---w mac-addr    yang:mac-address
```

The generator creates:
```json
{
  "ap-name": {"type": "string"},
  "mac-addr": {"type": "string"}
},
"required": ["ap-name", "mac-addr"]
```

**Expected:**
- Should use OpenAPI `oneOf` or `anyOf`
- Only ONE alternative should be required

**Affected RPCs:**
- `Cisco-IOS-XE-wireless-access-point-cmd-rpc`: convert-ap-to-meraki, set-ap-tags, set-rad-capwap-reset, ap-reset (20+ operations)
- `Cisco-IOS-XE-wireless-mesh-rpc`: set-rap-eth-daisychain-super-root, exec-linktest-ap (5+ operations)
- `Cisco-IOS-XE-install-rpc`: install operations with choice statements

### 2. Type Mapping Issues
**Impact:** MEDIUM

**Example:** convert-ap-to-meraki
- YANG: `force-convert     boolean`
- Generated: `"force-convert": {"type": "string"}`

Boolean fields are being mapped to string instead of boolean type.

## Correctly Handled Cases ✅

### Empty Input RPCs
These RPCs legitimately have NO inputs and correctly show empty properties:

**Cisco-IOS-XE-sslproxy-rpc:**
- sslproxy-update-ca-bundle
- sslproxy-update-ca-tp-label
- sslproxy-update-ec-key
- sslproxy-update-rsa-key

**Cisco-IOS-XE-wireless-mesh-rpc:**
- rrm-80211a-channel-update-mesh
- rrm-80211b-channel-update-mesh

**Cisco-IOS-XE-wireless-access-point-cmd-rpc:**
- ap-image-upgrade-dry-run

### Simple Input RPCs
These RPCs have simple inputs (no choice statements) and are correctly generated:

**Cisco-IOS-XE-rescue-config-rpc:**
- rescue-config-apply: force field present ✅
- rescue-config-save: comment field present ✅

**Cisco-IOS-XE-wireless-access-point-cmd-rpc:**
- set-rad-predownload-all: uuid field present ✅
- ap-image-predownload-abort: uuid field present ✅
- image-site-filter-add: image-name, site-name present ✅

## Verification Commands

```powershell
# Check YANG tree
pyang -f tree Cisco-IOS-XE-wireless-access-point-cmd-rpc.yang

# Find empty properties in specs
grep -r '"properties": {}' swagger-rpc-model/api/

# Search for specific RPC
grep -A 20 "ap-image-upgrade-dry-run" swagger-rpc-model/api/Cisco-IOS-XE-wireless-access-point-cmd-rpc.json
```

## Recommendations

1. **Add choice statement support to generator** - Priority: HIGH
   - Parse `(choice-name)` and `--:(case-name)` from pyang tree
   - Generate OpenAPI `oneOf` schemas
   - Update required fields to match choice semantics

2. **Fix boolean type mapping** - Priority: MEDIUM
   - Check for `type boolean` in YANG
   - Map to `{"type": "boolean"}` in OpenAPI

3. **Add leaf-list support** - Priority: LOW
   - Handle array types with `type: array, items: {type: ...}`

## Statistics

- **Total RPC Modules:** 53
- **Total RPC Operations:** 284
- **Empty properties found:** 20+
- **Legitimately empty:** ~10 (verified correct)
- **Missing choice support:** ~40+ operations
- **Type mapping issues:** ~15+ boolean fields

## Next Steps

1. Update RPC generator to parse choice statements
2. Add oneOf schema generation
3. Fix boolean type mapping
4. Regenerate all RPC specifications
5. Re-verify against YANG sources
