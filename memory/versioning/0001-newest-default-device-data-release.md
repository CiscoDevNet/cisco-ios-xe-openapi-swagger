# 0001 — Newest release is the default; device data has its own release

- Status: accepted
- Date: 2026-10-04
- Component: versioning
- Commit/PR: 2712b3e1c

## Context
26.2.1 was added while every lab capture came from 26.1.1, and about ten tools hard-coded
`26.1.1`. Keeping the old release as default (to keep device data visible) hid the newest
models; switching the default by editing those ten places would repeat on every release.

## Decision
`releases/index.json` `default` is always the newest active release (enforced by
`test_default_is_newest_release`). A separate `device_data` key names the release the lab
devices run; every device-data tool reads it via `scripts/_release_paths.device_data_release()`.
Viewers on a release without captures show the `device_data` captures with a caveat line.

## Alternatives rejected
Keep 26.1.1 as default until the lab upgrades (users land on stale models); copy captures into
26.2.1 (mislabels data as 26.2.1).

## Consequences
After a lab upgrade, flip `device_data` and re-collect (VERSIONING.md 8.2). The previous
release keeps its `live-data/`. New code must never hard-code a release for device data.
