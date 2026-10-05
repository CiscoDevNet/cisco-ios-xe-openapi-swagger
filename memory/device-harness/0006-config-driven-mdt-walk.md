# 0006 — Config-driven MDT walk: walk what is configured, until it is matched

- Status: accepted
- Date: 2026-10-05
- Component: device-harness
- Commit/PR: (this change)

## Context
The per-xpath MDT walk tests ~18,000 catalog xpaths one at a time (~5 per minute over a WAN),
so a full walk takes days, and almost all native-config xpaths are for features that are not
configured. The user asked (2026-10-05) for the harness to capture `show running-config` and
`show running-config | format restconf-json` first, then collect the configured native data
until it is matched 100%.

## Decision
- `config_get.py` (SSH) writes `output/config-<PID>.json`: masked `show_run`, top-level
  sections, and the parsed restconf-json (native plus every `*-cfg` model the config populates).
  It is the first `kit.py collect` method and goes into bundles.
- `prune_walk_catalog.py` keeps every native-config / cfg xpath whose full path exists in that
  JSON (configured wins even if every other device rejected it: the C9800's wireless models),
  plus xpaths that streamed on another walked device.
- Oper is runtime state, not config, so it is pruned by fleet history only (what streamed
  elsewhere). Kits ship that history as `fleet-walk-<flavor>.json`.
- `kit.py walk` walks the pruned catalogs, re-tries configured xpaths that stayed silent with a
  longer window (`--retry-window`, separate `-retry` state), and writes `match-<PID>.json`.
  **Matched** = streamed or rejected by the device (`invalid`): a rejected subscription can never
  stream, so 100% means no configured xpath is silent or unwalked.

## Evidence
Leave-one-out over six walked devices: native-config kept 192–270 of 14,659 xpaths and 299/300
of those that streamed (miss: `/ios:native/identity`); cfg kept 77–127 of 522 and 101/101.
A RESTCONF-presence filter for oper was rejected: 40–98% recall.

## Consequences
Configured is not the same as streamable: on C9300-24UX 119 of 246 configured native xpaths
are rejected and 42 stay silent at 10 s, so 100% "streamed" is not reachable; report the match
buckets instead. Unconfigured features are not walked by design; enable them first
(DEVICE_FEATURE_COVERAGE.md) if their data is wanted.
