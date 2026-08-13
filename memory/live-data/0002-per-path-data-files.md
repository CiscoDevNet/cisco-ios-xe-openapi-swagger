# 0002 — Per-path data files + tiny index (not one blob)

- Status: accepted
- Date: 2026-07-31
- Component: live-data
- Commit/PR: 5ed0be000

## Context
With bodies out of the specs (see 0001), the Live Data page still needs the real
responses on demand. The full captured set is large (~42 MB, 2,699 paths × 6 PIDs).

## Decision
Emit one small file per captured path: `releases/<ver>/live-data/<category>/
<module>/<sha1(path)[:16]>.json` (all PIDs for that path). Plus a lightweight
`live-examples-index.json` (nav + coverage, **no bodies**) and a tiny
`live-modules.json` (~32 KB) for the in-viewer banner. The page fetches only the
one file for the path a user drills into.

## Alternatives rejected
One big `live-examples.json` blob — rejected: the page (and the viewer banner)
would download megabytes to show one path.

## Consequences
Fast drill-down; the index/banner load is trivial. Build is deterministic
(`build_live_examples_index.py`) and re-scrubs values at publish time. Many small
files, but git handles them and the per-path granularity is worth it.
