# MDT Telemetry Validation Framework

Tools to systematically validate the current 58 MDT telemetry subscriptions against a real Catalyst 9300.

## Files

| File | Purpose |
|------|---------|
| `subscriptions.yaml` | Single source of truth for all subscription definitions (IDs, XPaths, expected fields, tiers) |
| `validate.py` | Connects to the switch via RESTCONF to push subs, check state, and sample operational data |
| `generate_ios_config.py` | Generates copy-paste IOS XE CLI config from `subscriptions.yaml` |
| `report.py` | Generates a markdown summary from validation results |
| `results/` | Directory for validation output JSON and reports |

## Prerequisites

```bash
pip install requests pyyaml urllib3
```

The target switch needs:
```
ip http secure-server
restconf
```

## Quick Start

### 1. Generate the IOS XE subscription config
```bash
# Print to stdout with custom receiver IP
python generate_ios_config.py --receiver-ip 10.1.1.3 --receiver-port 57500

# Write to file
python generate_ios_config.py --receiver-ip 10.1.1.3 --out c9300-mdt.cfg
```

### 2. Validate subscriptions against a live switch

```bash
# Full validation: push subscriptions, check state, sample data
python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED***

# Just sample operational data (don't push subscriptions)
python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --sample-only

# Just check subscription state (already pushed)
python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --check-only

# Validate specific subscriptions only
python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --sub 1001 1005 1007
```

### 3. Generate a summary report

```bash
# Summarize latest validation result
python report.py

# Write to markdown file
python report.py --out results/summary.md
```

## Workflow

```
subscriptions.yaml
       │
       ├──→ generate_ios_config.py ──→ c9300-mdt.cfg (paste to switch)
       │
       ├──→ validate.py ──→ results/validation-<host>-<timestamp>.json
       │                         │
       │                         └──→ report.py ──→ summary.md
       │
       └──→ (used by collector-config.yaml and Splunk dashboard)
```

## Subscription ID Scheme

- IDs start at `1001` and generally match the `plan.md` section number: Sub 1001 = §1 CPU, Sub 1007 = §7 Interfaces, Sub 1057 = §57 YANG management plane interfaces.
- Exception: §41 has two subs (MACsec=1041, MKA=1141).
- Sections 49-57 are the native IOS XE V3 expansion set and should be validated as the next wave after the original 48-feature core.

## What validate.py checks

1. **RESTCONF GET** on the operational XPath — does the YANG module exist on this platform?
2. **Field extraction** — what keys, metrics, and dimensions are actually returned?
3. **Expected vs actual** — compares returned fields against `expected_keys` and `expected_metrics` from `subscriptions.yaml`
4. **Subscription state** — is the subscription active on the device?

Results are categorized as:
- **Data returned** — YANG module is supported and data is populated
- **Empty** — YANG module exists but no data (feature not configured, e.g., BGP with no neighbors)
- **Not found (404)** — YANG module not available on this platform/version → remove from config
- **Error** — connection issue, timeout, or unexpected response
