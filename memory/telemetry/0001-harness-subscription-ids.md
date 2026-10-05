# 0001 — Harness MDT uses subscription ids 9xxxxx; device standing subscriptions are left alone

- Status: accepted
- Date: 2026-10-04
- Component: telemetry
- Commit/PR: a255aa7f6

## Context
C9300-STACK8-WAN has standing MDT subscriptions (ids 30002, 50023, 60007, ...) that stream to
this VM's receiver (:57500). They looked intentional, so they were not removed, but they polluted
every harness MDT capture and inflated record counts.

## Decision
Harness subscriptions use ids 900000+. Telegraf keeps only `subscription = ["9?????"]`
(tagpass), and batch idle detection and `split-mdt` count only those records.

## Alternatives rejected
Remove the standing subscriptions (someone configured them; not ours to delete without asking);
run the harness receiver on another port (devices' ACLs/firewalls already allow 57500).

## Consequences
The standing subscriptions remain on the Stack. Whether to keep them is an open question for
the user. Any new collector must use 9xxxxx ids.
