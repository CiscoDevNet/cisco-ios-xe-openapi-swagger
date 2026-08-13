# 0002 — Service worker: stale-while-revalidate for HTML/JS/CSS

- Status: accepted
- Date: 2026 (frontend)
- Component: frontend
- Commit/PR: service-worker.js

## Context
GitHub Pages has no runtime; users should get fast loads but still pick up UI
updates without a forced cache-version bump every change.

## Decision
Serve HTML/JS/CSS **stale-while-revalidate** (instant from cache, refetch in
background → update lands on the *next* load). `releases/**` artifacts are
network-first/network-only so versioned data is always current.

## Alternatives rejected
Cache-first with a manual `CACHE_VERSION` bump per change — rejected: easy to
forget, ships stale UI. Network-first for everything — rejected: slower loads,
offline-fragile.

## Consequences
Gotcha: after pushing JS, the first reload may show the *old* script; a second
reload has the new one. When testing a JS change locally, reload twice (or
hard-reload). Don't rely on an immediate update for a single reload.
