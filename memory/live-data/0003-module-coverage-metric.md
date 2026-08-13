# 0003 — Coverage shown as module coverage, not per-leaf-path %

- Status: accepted
- Date: 2026-07-31
- Component: live-data
- Commit/PR: cb028b651

## Context
The Live Data coverage bar first showed captured paths ÷ total enumerated GET
paths. That denominator is dominated by keyed-list entries and deep native-config
leaves (native-config alone = 50,716 paths), so it read a misleading ~1–3 %.

## Decision
Show **module coverage** = captured modules ÷ total modules per category (e.g.
oper 42 %, mib 65 %). The tangible captured-path count stays as the headline
number; a note explains that unconfigured/keyed/empty leaves make a path-% understate reality.

## Alternatives rejected
Keep the path-% (with a disclaimer) — rejected: it looks broken and undersells
real coverage. Compute a "capturable" path denominator — more code for a metric
modules already express cleanly.

## Consequences
Coverage reads honestly. Depends on `captured_modules`/`total_modules` in the
index (already emitted).
