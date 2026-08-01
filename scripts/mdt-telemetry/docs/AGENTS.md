# Project Guidelines

## Overview

Catalyst 9300 MDT (Model-Driven Telemetry) pipeline: 65 YANG operational models (48 validated core + 9 native IOS XE expansion + 8 validated platform expansion) streamed via gRPC dial-out through an OpenTelemetry Collector into a Splunk Metrics Index. This repo contains the telemetry plan, validation framework, OTel collector config, Splunk dashboard, and CLI/RESTCONF reference.

## Architecture

- **Device**: Catalyst 9300 (IOS XE 17.12+), gRPC dial-out on TCP/57500, kvGPB encoding
- **Collector**: OpenTelemetry Collector with `cisco_mdt` receiver → Splunk HEC exporter
- **Backend**: Splunk Enterprise with Metrics Index (`cisco_mdt`) and SimpleXML dashboard
- **Validation**: Python scripts using RESTCONF GET to verify YANG model availability

## Key Files

| File | Purpose |
|------|---------|
| `telemetry-reference-v2.md` | Unified reference — 65 target features, KPIs, subscription configs, YANG mapping |
| `cli-reference.md` | CLI show commands, live CLI output, RESTCONF examples, JSON samples |
| `splunk-dashboard.xml` | Splunk SimpleXML dashboard (58 panels, dark theme) |
| `collector-config.yaml` | OTel Collector pipeline config |
| `validation/subscriptions.yaml` | Single source of truth for all 66 subscription definitions |
| `validation/validate.py` | RESTCONF-based subscription validator |
| `validation/generate_ios_config.py` | Generates IOS XE CLI config from subscriptions.yaml |

## Conventions

### Subscription IDs

Subscription IDs use a tier-based scheme: `30xxx` (HOT), `60xxx` (WARM), `50xxx` (COOL). MACsec uses 50022 and MKA uses 50023.

### YANG XPaths

- XPaths use the module prefix form: `/module-prefix:container/leaf`
- The `subscriptions.yaml` file is the canonical source — all other files derive from it
- When adding a new feature, update `subscriptions.yaml` first, then regenerate configs

### Splunk Field Names

Splunk field names are derived from YANG leaf names with hyphens converted to underscores (e.g., `five-seconds` → `five_seconds`). Nested containers use underscore separators.

### Polling Tiers

| Tier | Interval | Use For |
|------|----------|---------|
| HOT | 30s | CPU, process memory, interface counters, punt/inject |
| WARM | 60s | Memory, DRAM, environment, PoE, STP, stack, stack-member detail, platform, routing protocols, BGP neighbor detail, FHRP, BFD, NTP, IP SLA, flow monitor, CEF/FIB, IS-IS interface detail, PoE health, tunnel, multicast, PIM, MPLS LDP, LISP, VXLAN NVE, EVPN, IETF routing, IETF interfaces |
| COOL | 300s | VLANs, MAC, ARP, LLDP, CDP, device HW, switchport, transceiver, UDLD, 802.1X, TCAM, MDT health, install, DHCP, HA, linecard, TrustSec, LACP, ACL, AAA, port security, MACsec/MKA, VRF, DP resources, EIGRP, IS-IS, BGP RIB, IPv6 ND, high-scale ARP, YANG mgmt interfaces, MPLS forwarding (LFIB), PTP/SyncE |

## Build and Test

### Validation

```bash
cd validation
pip3 install requests pyyaml urllib3
python3 validate.py --host <switch-ip> --user admin --pass <password>
python3 report.py --out results/summary.md
```

### Generate IOS XE Config

```bash
python3 validation/generate_ios_config.py --receiver-ip <collector-ip> --out c9300-mdt.cfg
```

### Run CLI Commands on Device (SSH)

```bash
python3 run_cli_commands.py   # Outputs cli-outputs.json
python3 insert_cli_output.py  # Merges CLI output into cli-reference.md
```

## Device Access

Device credentials and hostnames are stored in script arguments and environment variables — never hardcode credentials in committed files. Use `--user` and `--pass` flags or environment variables.

## RESTCONF Notes

- Default depth parameter: `depth=4` on all RESTCONF GETs
- Some YANG models need RESTCONF path fallback (truncating nested list segments on 404)
- LLDP queries use the sub-path `lldp-entries/lldp-entry` to avoid response truncation
- The `validate.py` script handles all known prefix-to-module mappings for XPath conversion
