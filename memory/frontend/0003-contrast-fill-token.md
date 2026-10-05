# 0003 — Contrast: one fill token for white text; category hues darkened

- Status: accepted
- Date: 2026-10-04
- Component: frontend
- Commit/PR: f5bad27e4, ee8e26859

## Context
Dark mode remaps `--c-brand-600` / `--accent` to #42a5f5 so links read well on dark
backgrounds, but the same variables were used as backgrounds under white text (2.65:1). Many
category chips used Material 500 colours (#4CAF50, #00BCD4, #F57C00) under white text (2.3–2.8:1).

## Decision
`--c-brand-fill` (#1565c0 light / #1976d2 dark, site.css) is the only background allowed under
white text. Category chips, badges and viewer accents use darker shades of the same hues
(#2E7D32, #00838F, #B45309, #BF360C, #00796B, ...) so text and fills reach 4.5:1 in both themes.

## Alternatives rejected
Dark text on the light fills (breaks the established white-on-colour chip style); leave as is
(fails WCAG AA; several labels were nearly invisible).

## Consequences
Chart.js series and legend swatches keep the original Material 500 colours, so a chip and its
chart series can differ slightly in shade. Use `var(--c-brand-fill)`, never `var(--accent)`,
for any new filled button.
