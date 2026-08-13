# Copilot / AI agent instructions

**Read [AGENTS.md](../AGENTS.md) first** — it is the authoritative agent guide
(source-of-truth docs, the 9 model categories, conventions, safety, dev/prod
deploy, corp-proxy rule). Do not duplicate its content; update it when behavior
changes.

## Decision ledger — [memory/](../memory/)
Before changing a webapp component, **read `memory/<component>/*.md`** — the
project's *why* plus the constraints and gotchas that already cost someone time
(redaction gaps, the `%2F` double-encode 404, management "shared-fate" that can
cut all remote access, platform limits like C9200L=no-routing / C9840=OSPF-only).

- Treat an `accepted` entry as a **constraint**, not a suggestion.
- When you make a decision with a tradeoff, **add an entry** (see
  `memory/README.md` + `memory/_template.md`); supersede rather than rewrite.

Layer roles: **CHANGELOG.md** = *what* changed · **spec docs** (DEVICE_DATA_COLLECTION,
VERSIONING, APP_MAP, …) = *how* it works now · **memory/** = *why*.
