# memory/ — decision ledger ("why")

Append-only records of **decisions with a tradeoff** for each webapp component.
This is the project's *why* — the reasoning, constraints, and roads not taken,
which get lost between sessions.

## For AI agents (read this first)
1. **Before changing a component, read its folder:** `memory/<component>/*.md`.
   Entries encode **constraints and gotchas** — following them prevents repeating
   mistakes that already cost someone time (e.g. redaction gaps, the `%2F`
   double-encode 404, mgmt "shared-fate" that can cut all remote access).
2. **Treat an `accepted` entry as a constraint**, not a suggestion. If you must
   go against one, add a **new** entry that `supersedes NNNN` explaining why.
3. **When you make a decision with a tradeoff, add an entry** (copy `_template.md`).
   That's how the next agent learns what you learned.
4. Entries are short by design — a paragraph per section. Skim the folder; it's fast.


## What goes where (don't duplicate)

| Layer | Answers | Lives in |
|---|---|---|
| **What** changed, when | release/round deltas | `CHANGELOG.md` |
| **How** it works *now* | current behavior/spec | `DEVICE_DATA_COLLECTION.md`, `VERSIONING.md`, `APP_MAP.md`, … |
| **Why** we chose X over Y | this folder | `memory/<component>/NNNN-*.md` |

## The filter (write it only if the answer is "yes")
> *Would a future agent or human waste time, or repeat a mistake, without this?*

Capture: irreversible/high-cost decisions, rejected alternatives, safety
constraints learned the hard way, gotchas that bit us.
Skip: routine changes (→ CHANGELOG), how-it-works-now (→ spec docs), obvious
choices with no tradeoff, blow-by-blow logs.

## How to add an entry
1. Copy `_template.md` into the right component folder.
2. Number it `NNNN` (next number in that folder).
3. Keep each section to a tight paragraph. A paragraph beats a page.
4. **Append-only:** never rewrite an accepted entry — add a new one that
   `supersedes NNNN`, and set the old one's status to `superseded-by NNNN`.
5. Link the commit/PR.

## Component map (one folder per webapp area — see APP_MAP.md)
- `live-data/` — Live Data page + `releases/<ver>/live-data/` data files
- `device-harness/` — `scripts/harness/` GET collection, redaction, depth-probe, feature enablement
- `frontend/` — hub, viewers, CSP, service worker, shared JS
- `versioning/` — multi-release layout, URL contract (see VERSIONING.md)
- `deploy/` — GitHub Pages, dev/prod remotes, CI gates
- `telemetry/` — MDT/gRPC dial-out effort (`scripts/mdt-telemetry/`)
- `search/` — Fuse.js index + query behavior

Add a folder when a new component earns its first decision. One entry in a
folder is fine.
