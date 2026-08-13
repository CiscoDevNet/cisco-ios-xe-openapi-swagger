# 0001 — Strict CSP: no inline scripts on hub pages

- Status: accepted
- Date: 2026 (frontend hardening)
- Component: frontend
- Commit/PR: see AGENTS.md §6 (CSP)

## Context
The site is public and static. Inline `<script>` blocks are an XSS foothold and
force a permissive CSP.

## Decision
All executable JS lives in external `.js`; hub pages run a strict CSP
(`script-src 'self' <analytics hosts>`; no `'unsafe-inline'`). DOM is built via
helpers (no `innerHTML`), and event handlers are attached in JS (not inline
`onclick` attributes).

## Alternatives rejected
Allow `'unsafe-inline'` for convenience — rejected: defeats the point of CSP.

## Consequences
Any new UI must ship JS as an external file and use `addEventListener`, not
inline attributes (the `el()` helper's `onclick` uses `addEventListener`, which is
CSP-safe). Adding a new CDN requires a CSP host entry.
