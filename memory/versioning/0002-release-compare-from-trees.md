# 0002 — Release comparison diffs pyang trees, not generated specs

- Status: accepted
- Date: 2026-10-04
- Component: versioning
- Commit/PR: e99d9382f

## Context
The "What Changed Between Releases" page needs module and schema-node differences between
adjacent releases. Older releases' specs were produced by earlier generator versions, so
diffing specs reports generator changes as YANG changes (false removals).

## Decision
`scripts/build_release_compare.py` diffs the resolved pyang trees (groupings, augments and
submodules applied) plus YANG revision statements, from pinned inputs only. Output lives in
`releases/compare/`.

## Alternatives rejected
Diff the OpenAPI specs (generator drift); link to the external release-overview markdown only
(not browsable per module, not per release pair).

## Consequences
Adding a release requires re-running `build_release_compare.py`. For 26.1.1 → 26.2.1 the result
matches the upstream overview (+23 / −1 modules).
