# 0005 — Mask secrets by content; lab credentials are not treated as sensitive

- Status: accepted
- Date: 2026-10-04
- Component: device-harness
- Commit/PR: 276c221e1

## Context
The MDT dataset builder never redacted, so the lab SNMP read community was published, and
communities also appeared as CLI text and as SNMP `community-config` list keys, which key-name
masking cannot see. The lab device password had been in three generator docstrings since
2026-02 and remains in git history.

## Decision
Every dataset builder masks secrets by content as well as by key (`redact_payload.py`,
`harness/redact.py`), and `tests/test_dataset_secrets.py` scans every published dataset. The
user decided (2026-10-04) that the lab password and SNMP community are not sensitive: no
rotation and no git-history rewrite.

## Alternatives rejected
Rotate credentials and force-push rewritten history to both repos (user declined: lab-only
devices; forks and clones would keep the history anyway).

## Consequences
Masking stays mandatory for anything published (other users' devices via the kit may carry
real secrets). Do not reopen the rotation question unless the devices leave the lab.
