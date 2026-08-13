# 0001 — Serve live data as lean specs, not injected bodies

- Status: accepted
- Date: 2026-07-31
- Component: live-data
- Commit/PR: 5ed0be000

## Context
Real captured RESTCONF responses were first injected into each OpenAPI spec under
an `x-cisco-live-examples` vendor extension. This bloated the native-augment
specs to ~19 MB each (≈411 MB across 311 specs) and slowed the Swagger viewers.

## Decision
Keep the specs **lean** — each spec carries only its synthetic schema `example`.
Real bodies are served separately (see 0002) and consumed only by the Live Data
page + an in-viewer banner. No path/operation/module counts change (G-6 safe).

## Alternatives rejected
Keep injecting bodies — rejected: unbounded spec bloat, slow viewers, and every
spot that loads a spec pays for data it doesn't need.

## Consequences
Viewers stay fast; specs stay diffable. Docs that described injection had to be
corrected (README/APP_MAP/FAQ). The Live Data page owns the body-rendering path.
