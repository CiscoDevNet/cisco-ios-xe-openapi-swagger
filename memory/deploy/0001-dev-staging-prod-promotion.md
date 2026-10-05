# 0001 — Dev → staging smoke → fast-forward prod

- Status: accepted
- Date: 2026-10-03
- Component: deploy
- Commit/PR: 8cb9a1d21 (first promotion), every promotion since

## Context
Two Pages sites: `origin` (jeremycohoe, staging) and `prod` (CiscoDevNet). Pushing straight to
prod shipped regressions; a 2026-10-04 run of commits was red in CI for hours unnoticed.

## Decision
Push to origin; wait for both `tests` and `Deploy` runs on that commit; run
`scripts/smoke_assurance.py` against staging and require `0 FAIL`; then fast-forward prod
(`git push prod origin/main:refs/heads/main`, only if prod is an ancestor), wait for its runs,
and smoke prod. Staging Pages uses the workflow build (same as prod).

## Alternatives rejected
PR-based promotion (no reviewers; adds latency without checks); pushing to prod first.

## Consequences
Pushing needs a classic PAT with `repo` scope and at most 90 days' lifetime (Cisco policy;
fine-grained tokens get read-only). It will expire; renew it in `~/.git-credentials` when pushes
return 403. `grep -q " 0 FAIL"` must gate the prod push (`tail -1` does not stop on failure).
