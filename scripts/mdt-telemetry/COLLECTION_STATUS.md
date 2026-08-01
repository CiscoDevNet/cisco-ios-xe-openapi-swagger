# MDT Live Telemetry Collection — Status & Resume Guide

Working notes for the live Model-Driven Telemetry (MDT) collection pipeline.
Everything here is **local / not pushed to GitHub** (per the standing publish gate).
Last updated: 2026-07-31.

## 1. What this is

A dev pipeline that streams **real** MDT from the six lab Catalyst devices into a
receiver on this host, so the web app's **Telemetry Data** page can show live,
per-device telemetry across all model categories (oper, OpenConfig, native-config,
cfg, ietf) — the streaming counterpart to the RESTCONF **Live Data** page.

```
Catalyst device ── gRPC dial-out (kvGPB, :57500) ──▶ Telegraf (cisco_telemetry_mdt)
                                                       └─▶ collector/output/mdt-live.json
                                          build_live_dataset.py ─▶ telemetry-live-data.json
```

## 2. Host / receiver facts

- Collector host IPs (ens160): **10.85.134.200** and 10.85.134.204 (/26).
- Receiver: **Telegraf** container `mdt-telegraf`, listening `0.0.0.0:57500`
  (plaintext grpc-tcp). Config: `scripts/mdt-telemetry/collector/telegraf-mdt.conf`.
  Start/stop: `scripts/mdt-telemetry/collector/run-telegraf.sh [--stop]`.
- Note: the OTel Collector path was dropped — neither the contrib nor Splunk image
  ships a `cisco_mdt` receiver anymore. Telegraf's `cisco_telemetry_mdt` decodes
  Cisco MDT natively (no protos to compile).

## 3. Devices (scripts/harness/inventory.json) + how each reaches the collector

Credentials: `scripts/harness/.env` (`IOSXE_USER` / `IOSXE_PASS`).
Management interface is `Gi0/0` in **Mgmt-vrf** on all units. The collector is on
the management network; each device's usable path was determined empirically:

| PID | Mgmt IP | Path to collector |
|-----|---------|-------------------|
| C9300-24UX | 10.85.134.70 | global |
| C9200 | 10.85.134.72 | global |
| C9800 | 10.85.134.83 | global |
| C9400 | 10.85.134.71 | **Mgmt-vrf** |
| C9500 | 10.85.134.95 | **Mgmt-vrf** |
| C9600 | 10.85.134.75 | **Mgmt-vrf** |

`collect_fleet.py` **auto-detects** this per device (pings the receiver via global,
then Mgmt-vrf) and sets `source-vrf` + `source-address` accordingly. This is why the
first sweep left C9400/9500/9600 in `Transport requested` — they need `source-vrf
Mgmt-vrf`; fixed now.

## 4. Key behaviors learned

- **First payload is immediate.** With `update-policy periodic 30000` (300s), IOS XE
  sends the full first snapshot on subscription establishment, then goes quiet for the
  period. So a large period = one clean snapshot, no second cycle interleaving.
- **Completeness = idle detection, not the period.** `collect_fleet.py` waits until the
  receiver stops writing new records for a few seconds (`--idle`), capped by `--window` —
  captures complete payloads in seconds, not minutes.
- **Cleanup is guaranteed.** Every subscription is removed after its capture window and
  in a `finally` block. Temp sub-IDs use the 900000+ range; nothing is saved to
  startup-config. Verified no stragglers on C9300.
- **Sub-IDs stay clear of the DNAC assurance subs** already on the devices (500–504, 750,
  751, 8882 → `DNAC_ASSURANCE_RECEIVER` at 10.85.134.108:25103, TLS).

## 5. Tools (scripts/mdt-telemetry/collector/)

| Script | Purpose |
|--------|---------|
| `run-telegraf.sh` | Start/stop the Telegraf MDT receiver on this host. |
| `telegraf-mdt.conf` | Telegraf config (cisco_telemetry_mdt :57500 → output/mdt-live.json). |
| `collect_one_payload.py` | Push ONE sub to ONE device, capture, remove. Flags: `--source-vrf`, `--source-address`, `--period-cs`, `--xpath`, `--timeout`, `--apply`. |
| `collect_fleet.py` | Batched fleet sweep: enumerate xpaths → per-device VRF auto-detect → push/capture/remove per batch. Flags: `--depth`, `--categories`, `--per-cat-cap`, `--batch-size`, `--period-cs`, `--idle`, `--window`, `--source-vrf auto`, `--devices`, `--apply`. |
| `enumerate_xpaths.py` | Count/list depth≤N subscribable xpaths per category from the specs. |
| `profile_subcaps.py` | GET a device's `mdt-capabilities` (read-only) — subscribable paths + policy. |
| `show_device_telemetry.py` | Dump a device's existing telemetry config + receiver state (read-only). |
| `diag_reachability.py` | Routing/VRF/ping diagnostics device→collector (read-only). |
| `build_live_dataset.py` | Telegraf output + fleet-plan → `telemetry-live-data.json` (per PID × category × xpath). |
| `enumerate_xpaths.py` | Enumerate depth≤N xpaths per flavor from specs (uses the YANG **prefix** map — see §11). |
| `count_subscribable.py` | Count container/list (subscribable) nodes per flavor; `--dump` writes the catalog `output/subscribable-nodes.json` (18,898 nodes / 312 modules). |
| `walk_xpaths.py` | **Exhaustive, resumable, crash-isolating** discovery — one xpath at a time, checkpointed, survives reloads (see §12). |
| `walk_status.py` | One-shot progress summary for a running walk (use with `watch`). |
| `cleanup_stragglers.py` | Remove any leftover temp subs (ID ≥ 900000) after an interrupted run. |
| `walk_status.py` | Progress/rate/ETA/crashers summary for a walk: `walk_status.py <PID>` (use with `watch`). |
| `mib_catalog.py` | Build `output/mib-nodes.json` — MIB nodes with the SNMP->MDT `/<MOD>:<MOD>/…` rule. |
| `extract_sample.py` | Show captured keys + leaf values per xpath from a capture file (inspect payload depth). |
| `walk_all.py` | **Per-device orchestrator**: walks ALL flavors (+ MIB) in sequence, resumable, one process per device. |

## 6. Run guide

```bash
cd /opt/xeswagger/cisco-ios-xe-openapi-swagger
PY=.venv-harness/bin/python

# 0. Receiver (once):
scripts/mdt-telemetry/collector/run-telegraf.sh        # --stop to stop

# 1. Sanity: one payload from one device:
$PY scripts/mdt-telemetry/collector/collect_one_payload.py --device C9300 --apply

# 2. Fleet sweep (auto VRF, GENTLE defaults, idle capture):
$PY scripts/mdt-telemetry/collector/collect_fleet.py \
    --devices C9300 --include-bundle --depth 2 --per-cat-cap 40 --apply
#   Gentle defaults: --batch-size 5, --pace 4, --max-cpu 70 (CPU health gate).
#   Straggler safety net after any interruption:
#   $PY scripts/mdt-telemetry/collector/cleanup_stragglers.py [--device C9300]

# 3. Build the per-device dataset for the web app:
$PY scripts/mdt-telemetry/collector/build_live_dataset.py
```

## 7. Current status (2026-08-01)

**Five flavors walking in parallel** — one Telegraf receiver (:57500), per-device files via
`tagpass` on `source` (§13); each device auto-picks its VRF; per-device checkpoints.

| Device | Flavor | Path | Notes |
|--------|--------|------|-------|
| C9300 | oper (3,198) | global | running |
| C9400 | openconfig (225) | Mgmt-vrf | **done** (20 streamed) — now free |
| C9200 | cfg (522) | global | running — mostly *invalid* (config via periodic is low-yield) |
| C9800 | **wireless** (760) | global | running — high yield (WLC richly populated) |
| C9500 | **MIB** (956) | Mgmt-vrf | running — SNMP->MDT bridge streams (§14) |

- **Zero crashers** across all five. Speed ~10 xpaths/min/device (fast_cli + `--window 10 --idle 3 --pace 0`).
- Catalog `output/subscribable-nodes.json` = 18,898 container/list nodes; MIB catalog `output/mib-nodes.json` = 956.
- OpenConfig depth/keys **proven complete** (§15): container subscriptions deliver the full nested
  subtree + list keys; deep OC (SR/EVPN) is silent only because those features aren't configured.
- Web app: bundle-based `telemetry-data` page + toggle with `live-data`. **Live per-PID/category UI not wired yet.**

## 8. Recommended next collection

1. **Finish the small flavors** on the freed C9400: `ietf` (144) then `other` (150) — quick.
2. **native-config: do NOT walk all 14,659.** Config is low-yield via periodic (cfg = 385/447
   invalid). Subscribe to **top-level containers only** (`--category native-config --max-depth 2`,
   ~690) — the native root streams the whole config subtree in one go. For real config *change*
   monitoring use **on-change**, not periodic (a walker `--update-policy` enhancement, later).
3. **Let oper/wireless/MIB finish** (checkpointed; resume anytime).
4. **Then build the payoff**: per-device live dataset from the capture files (+ fix PID mapping)
   and wire per-PID + category into `telemetry-data.js` — the original goal.
5. **Publish gate.** Nothing pushed to GitHub yet.

## 9. Safety notes

- Inventory marks devices `writable: false` (RESTCONF GET-only guard). We push telemetry
  config with explicit user authorization; every temp sub is auto-removed.
- `output/` and any real `testbed.yaml` are gitignored; captures stay local.

## 10. Incident & gentle-collection rules (2026-07-31)

**A too-aggressive sweep RELOADED the C9300.** Pushing ~90 subscriptions in batches of 30
(with ~37 large snapshots streaming at once) spiked the control plane; the device went dark
and rebooted (uptime confirmed the reload). It auto-recovered in ~3 min, clean (the reload
cleared the unsaved temp subs). **39 xpaths were confirmed streaming beforehand** →
`output/c9300-known-streaming.json` (the known-list foundation).

Rules baked into `collect_fleet.py` (gentle by default) — do not weaken without care:
- **Small batches** (`--batch-size 5`).
- **CPU health gate**: read 1-minute control-plane CPU before each batch; abort if the
  device is unresponsive, back off then abort if CPU ≥ `--max-cpu` (70).
- **Pacing** (`--pace 4`s) between batches.
- One device at a time when discovering; expand only after the known-good list is set.
- If interrupted, run `cleanup_stragglers.py` (removes temp subs ≥ 900000).

## 11. Critical fix: YANG prefix map (2026-07-31)

MDT `filter xpath` requires the YANG **prefix** (`/arp-ios-xe-oper:arp-data`), **not** the
module **name** (`/Cisco-IOS-XE-arp-oper:arp-data`). `yang-prefix-map.json` is nested
(`{module_count, modules:{<module>:<prefix>}, version}`); `enumerate_xpaths.prefix_map()`
was returning the outer wrapper, so every lookup missed and fell back to the module name
— **all enumerated xpaths were invalid** (device replies "Subscription invalid"). Fixed to
return `data["modules"]`; the catalog was regenerated. Verified: the prefix form streams,
the name form is rejected.

**Defect caveat:** the earlier C9300 reload batch (appqoe/app-hosting) was configured in
the *invalid* module-name form. So the reload is either (a) the device rebooting under a
burst of invalid-xpath config, and/or (b) appqoe crashing with correct prefixes — needs a
correct-prefix re-test. See `output/crash-batch-c9300.json`.

**RESOLVED (2026-08-01):** the oper walk tested all 187 appqoe/app-hosting nodes with correct
prefixes → 153 invalid, 34 silent, **0 crashed**. So the reload was the *invalid module-name
burst*, not appqoe. Net defect for Cisco: **a burst of invalid-xpath subscription config can
reload a C9300 (26.1.1)** — valid xpaths one-at-a-time have caused zero reloads.

## 12. Exhaustive, resumable, crash-isolating discovery

For complete / overnight collection, `walk_xpaths.py` walks the catalog **one xpath at a
time** so every result — and every crash — is unambiguous.

- Classifies each xpath: **streamed / silent / invalid / crashed / error**.
- **Checkpoints after every xpath** → `output/walk-<PID>.json`. Re-running **resumes**
  (terminal statuses skipped; `error` retried; `--retry-crashers` re-tests crashers).
- **Survives reloads**: detects the device going unreachable, records the offending xpath
  in `crashers`, waits (up to `--recover-timeout`, default 900s) for the reboot, reconnects,
  and continues.
- `pkill -f walk_xpaths` (or Ctrl-C) to pause; the checkpoint is always safe. Re-run the
  same command to resume.

```bash
PY=.venv-harness/bin/python
# One flavor at a time, find crashers (no --exclude):
$PY scripts/mdt-telemetry/collector/walk_xpaths.py --device C9300 --category oper --apply
# Collect-only pass (skip known crashers):
#   ... --category oper --exclude appqoe lldp --apply

# Real-time monitor (progress, rate, ETA, crashers):
watch -n 5 $PY scripts/mdt-telemetry/collector/walk_status.py
```

Rebuild the catalog if the specs change:
```bash
$PY scripts/mdt-telemetry/collector/count_subscribable.py \
   --dump scripts/mdt-telemetry/collector/output/subscribable-nodes.json
```

**Run scope:** all containers+lists = 18,898 (redundant/huge). Practical targets: top-level
~719, or top+2nd ~2,666. Walk **one flavor at a time**, starting with oper.

## 13. Parallel walks — one receiver, per-device files

Telegraf listens once on :57500; `[[outputs.file]]` blocks with `[outputs.file.tagpass] source`
route each device's stream to its own file (`output/mdt-<PID>.json`) plus a catch-all
`mdt-live.json`. Source hostnames: C9300=`JCOHOE-C9300-2`, C9400=`JCOHOE-C9400`,
C9200=`JCOHOE-C9200L`, C9500=`JCOHOE-C9500`, C9800=`JCOHOE-9840-ZTP`. Add a device by copying
a block. Each walk uses `--capture-file output/mdt-<PID>.json` so parallel runs never
cross-contaminate. Launch each with its own `nohup` (do NOT chain with `disown &&`).

## 14. MIB (SNMP->MDT bridge) and wireless

- **MIB** filter xpaths use a different rule: `/data/IF-MIB:ifTable/ifEntry` -> `/IF-MIB:IF-MIB/ifTable/ifEntry`
  (module name as prefix AND root). Build with `mib_catalog.py` -> `output/mib-nodes.json` (956 nodes);
  walk with `--catalog output/mib-nodes.json`. Requires an **SNMP community** on the device
  (already present on C9500). Validated: IF-MIB streamed 58 records.
- **Wireless** is just the `oper` flavor filtered to `wireless-*` modules on the C9800 (a WLC):
  `walk_xpaths.py --device C9800 --category oper --include wireless --apply` (760 nodes, high yield).

## 15. OpenConfig depth & keys (proven complete)

The OC catalog already reaches depth 7 (225 container/lists); key-stripping the `={key}` paths
adds 0 nodes. Subscribing to a parent container delivers the **entire nested subtree + list keys**
(keys arrive as metric tags, leaves as `path/to/leaf = value`). Evidence from C9400
(`extract_sample.py output/mdt-C9400.json --grep openconfig-network-instance`):
`network-instances/network-instance` (key `name=Mgmt-vrf`) streams ~6-7 levels deep into
`afts/ipv4_unicast/ipv4_entry/state/counters/...`; compound keys like `id=..,name=..` are captured.
## 16. FULL exhaustive run — all devices, all models (2026-08-01)

Goal: every device collects **every flavor**, all nested containers/lists, keyed values.
`walk_all.py` runs one orchestrator per device that chains the flavors small->big
(`openconfig, ietf, other, cfg, mib, oper, native-config`), each as a resumable
`walk_xpaths` step with its own checkpoint `walk-<device>-<flavor>.json`.

```bash
for d in C9300 C9400 C9200 C9500 C9800; do
  nohup .venv-harness/bin/python scripts/mdt-telemetry/collector/walk_all.py \
        --device $d --mib > scripts/mdt-telemetry/collector/output/walk-all-$d.log 2>&1 &
done
```

- Running on 5 devices (C9600 left for the other task; add when free).
- **Long pole = native-config full (14,659 nodes/device)** → multi-day at ~10/min; oper ~5h;
  the rest ~1-2h each. Fully resumable: `pkill -f walk_all; pkill -f walk_xpaths` to pause,
  re-run the loop to resume (done flavors exit instantly).
- MIB requires an SNMP community; present on C9500, may be absent elsewhere (those stay silent).
- Monitor a flavor: `walk_status.py` reads `walk-<PID>.json`; per-flavor files are `walk-<device>-<flavor>.json`.
- Rebuild the web dataset anytime: `build_live_dataset.py` (reads the per-device `mdt-<PID>.json`).
