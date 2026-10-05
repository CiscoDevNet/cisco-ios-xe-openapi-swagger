# 0004 — Tree pages load the shared theme; site footer injection off

- Status: accepted
- Date: 2026-10-04
- Component: frontend
- Commit/PR: f5bad27e4

## Context
~4,200 generated YANG tree pages had only inline light styles and ignored the user's theme.
`site-chrome.js` also injects a footer whose links are relative to the site root, which breaks on
pages three levels deep (`releases/<ver>/yang-trees/`).

## Decision
`generate_all_pyang_trees.py` emits `site.css`, `assets/css/yang-tree.css` and `site-chrome.js`
(`THEME_ASSETS`) and `<body data-footer="off">`. Dark rules for tree pages live only in
`yang-tree.css`. The 24 hand-made 26.1.1 tree pages were patched the same way.

## Alternatives rejected
Inline a dark stylesheet per page (4,200 copies to maintain); make site-chrome depth-aware for
the footer (more JS for a footer the pages already have).

## Consequences
Template changes need all 6 releases regenerated (~25 minutes); output is otherwise identical,
and `tree_audit.json` changes only in timestamp/order (restore it). The legacy 26.1.1 pages are
not regenerated, so patch them by hand or retire them.
