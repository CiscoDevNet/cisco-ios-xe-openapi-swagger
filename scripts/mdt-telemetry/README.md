# MDT Telemetry Bundle — Catalyst 9300

A self-contained, portable package of the Catalyst 9300 Model-Driven Telemetry
(MDT) work: **collected captures**, the **validation/generation harness**, and
the **decisions and reference material**. Copy this folder into the larger
project to resume the work and expand it to additional devices.

> This is a migration bundle. Everything needed to rebuild, validate, and extend
> the telemetry pipeline lives inside this folder — no dependencies on the
> original workspace layout.

## What this pipeline does

65 YANG operational models are streamed from a Catalyst 9300 (IOS XE 17.12+) via
gRPC dial-out (TCP/57500, kvGPB) into an OpenTelemetry Collector, then exported
to a Splunk Metrics Index and visualized in a SimpleXML dashboard.

```
Catalyst 9300  ──gRPC dial-out──▶  OTel Collector  ──HEC──▶  Splunk Metrics Index  ──▶  Dashboard
 (cisco_mdt receiver)                (config/collector-config.yaml)   (cisco_mdt)      (config/splunk-dashboard.xml)
```

## Bundle layout

| Folder | Contents |
|--------|----------|
| `captures/` | 55 real telemetry capture files (`.txt`) from two live C9300 switches, plus an index (`README.md`). Authoritative source for exact metric field names and dimensions. |
| `harness/validation/` | The core harness. `subscriptions.yaml` (single source of truth), `validate.py` (RESTCONF validator), `generate_ios_config.py` (IOS XE CLI generator), `report.py`, and prior run output under `results/`. |
| `harness/device-scripts/` | Device-facing helpers: `run_cli_commands.py` (SSH show-command collector), `insert_cli_output.py`, `generate_cli_reference.py`, and a sample `cli-outputs.json`. |
| `config/` | `collector-config.yaml` (OTel pipeline) and `splunk-dashboard.xml` (58-panel dashboard). |
| `docs/` | Decisions and reference: `AGENTS.md` (project guidelines/conventions), `plan.md` (telemetry plan), `prd-18april2026.md` (PRD), `telemetry-reference-v2.md` (unified 65-feature reference), `cli-reference.md` (CLI/RESTCONF/JSON reference), `feature-enablement-guide.md`. |

## Key conventions (carried over)

- **Subscription IDs** use a tier-based scheme: `30xxx` = HOT (30s), `60xxx` =
  WARM (60s), `50xxx` = COOL (300s). MACsec = `50022`, MKA = `50023`.
- **`subscriptions.yaml` is canonical** — every other artifact (IOS config, OTel
  config, dashboard, reference docs) derives from it. Add a feature there first,
  then regenerate.
- **XPaths** use the module-prefix form: `/module-prefix:container/leaf`.
- **Splunk field names** derive from YANG leaf names with hyphens → underscores
  (e.g. `five-seconds` → `five_seconds`); nested containers use `_` separators.
- See `docs/AGENTS.md` for the full polling-tier assignment table and RESTCONF
  notes (depth=4, path-fallback rules, LLDP sub-path quirk).

## Current state

- **66 subscriptions defined** in `harness/validation/subscriptions.yaml`.
- **55 produced data** on the two reference switches; **10 were silent** because
  the underlying feature was not configured (no SFPs, no MPLS/LISP/VXLAN/EVPN,
  fixed chassis, etc.). See `captures/README.md` for the silent list and reasons.
- Reference switches: `cat9300x-pod10a` / `cat9300-pod10b`, IOS XE 26.01.1.

## Resume the work (new environment)

1. **Install harness prerequisites**
   ```bash
   cd harness/validation
   pip install requests pyyaml urllib3   # validate.py / generate_ios_config.py
   pip install paramiko                  # only for harness/device-scripts
   ```

2. **Generate the IOS XE subscription config** for your collector's IP
   ```bash
   python generate_ios_config.py --receiver-ip <collector-ip> --out c9300-mdt.cfg
   ```
   Paste the result onto the switch (requires `restconf` and
   `ip http secure-server`).

3. **Validate subscriptions against a live switch**
   ```bash
   python validate.py --host <switch-ip> --user admin --pass <password>
   # variants: --sample-only, --check-only, --sub 30001 30003
   python report.py --out results/summary.md
   ```

4. **Stand up the pipeline** — deploy `config/collector-config.yaml` on your OTel
   Collector (point the `cisco_mdt` receiver at TCP/57500 and the exporter at
   your Splunk HEC), then import `config/splunk-dashboard.xml`.

## Expand to more devices

- **More switches of the same type**: the subscriptions and dashboard apply
  as-is. Push the generated IOS config to each device pointing at the same
  collector; the `cisco_mdt` receiver multiplexes by source.
- **New platforms (e.g. C9500/C9800)**: some YANG modules differ. Run
  `validate.py` against the new platform to discover 404s (module not present)
  and empty results (feature not configured), then branch/extend
  `subscriptions.yaml` per platform. Re-run `generate_ios_config.py` per device
  class.
- **New features**: add the entry to `subscriptions.yaml` first (ID in the right
  tier range, XPath, expected keys/metrics), regenerate the IOS config, validate,
  then add capture-derived field names to the dashboard.

## Security notes

- **Device scripts read credentials from environment variables** — no secrets are
  committed in this bundle. Before running the device-facing helpers:
  ```bash
  export MDT_HOST=your-switch.example.com
  export MDT_USER=admin
  export MDT_PASS=...        # or leave unset to be prompted (getpass)
  ```
- The `validate.py` / `generate_ios_config.py` tools take `--host/--user/--pass`
  flags; do not hardcode credentials.
- `captures/`, `docs/`, and `harness/validation/results/` contain the reference
  lab's **hostnames and captured operational data** (neighbor names, MACs, IPs).
  These are lab identifiers, not secrets, but scrub them if this bundle leaves a
  trusted environment.

## Provenance

Copied from the `MDT-Telemetry` workspace. Originals remain in place; device
scripts in this bundle were modified only to remove hardcoded credentials.
