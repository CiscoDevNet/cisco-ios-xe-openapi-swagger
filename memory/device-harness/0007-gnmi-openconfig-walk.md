# 0007 — gNMI: nested OpenConfig walk, value-aware "data", crash roots, per-path payloads

- Status: accepted
- Date: 2026-11-18
- Component: device-harness
- Commit/PR: (this change)

## Context
The user asked for OpenConfig (starting with openconfig-interfaces) over gNMI, the whole set,
expanded. The published gNMI datasets had **no** OpenConfig data at all: on every device a Get
of `/notif-bis:streams` reset the connection and left gnmib refusing connections, and the old
collector recorded every later root (all 51 OpenConfig roots included) as a per-path error
instead of reconnecting. Payloads were also cut at 40 KB (`openconfig:/interfaces` alone is
164 KB), and the spec-derived node catalog knew 6 openconfig-interfaces nodes (no augments).

## Decision
- **Schema walk.** `gnmi_oc_catalog.py` loads the release's OpenConfig YANG with pyang
  (augments + generic `cisco-xe-openconfig-*` deviations; routing/wireless platform deviations
  excluded) and writes `output/openconfig-nodes.json`: every container and list, 1,696 nodes on
  26.1.1 (openconfig-interfaces 142). IOS XE accepts only **unprefixed** gNMI elements
  (`openconfig:/interfaces/interface/ethernet/state`); prefixed augments are rejected.
- **Collector.** `gnmi_get.py` probes module roots, then OpenConfig nodes only under a parent
  that returned data; config/state are read only when `all` had data. Transport errors
  reconnect with backoff, then stop and save (`--resume`). `UNSAFE_PATHS` never sends
  `/notif-bis:streams` (all platforms) or `/confd_dyncfg:confdConfig` (C9200); `--skip` adds
  per-device roots. Raw payloads are kept whole (5 MB guard).
- **What counts as data.** IOS XE answers an unpopulated node with an update whose value is
  `{}` (gNMI) or an empty container skeleton (NETCONF). Data now requires a leaf value
  (`response_has_data`, `_once_has_data`, `netconf_get.xml_has_data`; a self-closing XML
  element is an `empty`-type leaf and counts).
- **Publishing.** `build_gnmi_dataset.py` writes one redacted file per (method, path) under
  `releases/<device_data>/gnmi-data/<method>/<sha1(path)[:16]>.json` with every device in
  `pids{PID:{value}}` (the RESTCONF live-data shape); the root datasets are an index with
  `file`. Nested OpenConfig rows appear only when populated. Not under `live-data/`, because
  a RESTCONF sidecar rebuild deletes that folder. A Get `config` / `state` body that equals the
  same device's `all` body (reply timestamps ignored) is not stored again: the row points at
  the `get` file and carries `same_as: "gnmi-get"` (user: dedupe, lossless only).
- **C9200L excluded.** Its gnmib also crashed (rc 134, process held down) on
  `/fib-ios-xe-oper:fib-oper-data`; a reload recovered it, but the user chose to ignore the
  C9200L for gNMI. Its partial Get (17 roots with data) stays; its old Subscribe file was
  re-classified offline.

## Alternatives rejected
- Spec paths as the nested catalog: the OpenConfig specs omit augments (openconfig-system has
  3 spec paths vs 111 schema containers).
- Probing every catalog node regardless of the parent: ~1,700 x 3 Gets per device, almost all
  of them `{}`.
- Inline payloads with a higher cap: the root datasets would grow to tens of MB and every page
  load would fetch them.

## Consequences
- Counts dropped where "data" was really `{}`: about 40–50 non-OpenConfig roots per device
  for gNMI, and 29 NETCONF get + 12 get-config rows. Old numbers were inflated, not lost.
- Payload files are large (~80 MB for 26.1.1 after dedupe): nested paths repeat slices of their
  parent, and only identical config/state bodies are shared (counters drift between reads, so
  most oper state differs from get-all). Each re-collection rewrites them in git.
- The catalog is per release: run `gnmi_oc_catalog.py --version <ver>` after a lab upgrade
  (26.2.1 adds 36 openconfig-telemetry nodes). The kit ships it (`build_kit.CATALOG_FILES`).
