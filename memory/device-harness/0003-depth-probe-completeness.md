# 0003 — Root GETs are complete; verified by depth-probe (structure, not values)

- Status: accepted
- Date: 2026-08-01
- Component: device-harness
- Commit/PR: 6e1d92af2

## Context
Open question: does a deeper *keyed* GET (e.g. `component=<key>/…`) return data
the module-root GET omits? If so, exhaustive-per-path collection would miss it.

## Decision
Built `depth_probe.py` (`--discover`) to answer it empirically. Full 6-device ×
7-category sweep: **no module hides data behind keyed lists.** The 3 containers a
root ever omits (`aaa-users`, `mdt-subscriptions`, interfaces `general`) are
already captured as their own non-keyed paths by exhaustive per-path GET. So the
default collection (NOT `--roots-only`) is complete.

## Alternatives rejected
Offline subtree expansion (synthesize child paths) — rejected: full-subtree per
node ≈ +71 MB/+12.6k files (repo bloat); shallow-slice adds empty nodes and a
different UX. `--roots-only` mode — would MISS those 3 containers.

## Consequences
Two gotchas encoded in the tool: (1) percent-encode list-key values but don't let
`build_restconf_url` re-quote them (`%2F`→`%252F`→404); (2) classify by key-path
**structure**, not values — volatile oper counters (e.g. tick-count) look like
"new data" otherwise. Probe has a circuit breaker + unsafe-module skip.
