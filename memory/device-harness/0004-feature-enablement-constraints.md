# 0004 — Feature-enablement is loopback/leaf-only; mgmt is shared-fate

- Status: accepted
- Date: 2026-08-02
- Component: device-harness
- Commit/PR: DEVICE_FEATURE_COVERAGE.md (Phase 0.5–1)

## Context
~626 of 937 modules return 404 = unconfigured features. To collect more we enable
features on the 6 devices — but they share a rack with a **live EVPN/Meraki
fabric**, and management is fragile.

## Decision
Enable features **only on loopbacks / leaf ports** of our 6 devices, never on
mgmt-bridging or fabric-facing ports, and never on Meraki/fabric devices. Writes:
back up `show run`, one device at a time, re-check RESTCONF reachability after
each, don't `write memory` until healthy (a reload reverts).

## Alternatives rejected
Convert an existing data link (e.g. C9300↔C9800 `Te0/0/0`) to a routed p2p for a
real adjacency — rejected after verifying C9800 mgmt is **in-band on Vlan311** and
3 APs ride that path; converting it would cut RESTCONF + drop the APs.

## Consequences
Hard facts to respect: the C9300 hub bridges `10.85.134.0/24` mgmt for
C9500/C9600; the `/24` also hosts the TOR + both console servers — break it and
there's **no remote recovery**. Platform limits: **C9200L** has no routing/
loopback; **C9840 WLC** is **OSPF-only** and its CLI is netmiko-hostile (use
`sshpass ssh` with legacy algos). Phase 1 routing is applied+saved; live-data not
yet re-collected.
