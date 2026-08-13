# 0001 — GET-only safety core for the collection harness

- Status: accepted
- Date: 2026-07 (Track B harness)
- Component: device-harness
- Commit/PR: see DEVICE_DATA_COLLECTION.md §4

## Context
The harness talks to real, shared lab devices (some adjacent to a live EVPN
fabric). A stray write could disrupt production or the fabric.

## Decision
Every device request routes through `request.restconf_get`, which hard-refuses
any non-GET method (`assert_get_only` raises). Config writes are a separate,
explicitly-gated action — never through the collection path. `KNOWN_UNSAFE_MODULES`
(lldp-oper, CISCO-RTTMON-MIB, CISCO-VOICE-DIAL-CONTROL-MIB) are skipped because a
GET of them crashed/reset devices.

## Alternatives rejected
A general RESTCONF client used for both read and write — rejected: one bug =
an unintended write to a shared box.

## Consequences
Collection is provably read-only. Feature-enablement writes (see 0004) use a
separate netmiko path with backups, one-device-at-a-time, and not-saved-until-healthy.
