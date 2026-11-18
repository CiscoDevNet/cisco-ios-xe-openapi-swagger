# 0003 — Deprecation census: parsed, reconciled, matched by statement identity

- Status: accepted
- Date: 2026-11-17
- Component: versioning
- Commit/PR: 838dba05f

## Context
`deprecations.html` must show every `status deprecated` / `status obsolete` in a release, and
users want the counts to be exact. A plain grep overcounts (status text inside descriptions) and
undercounts what users see (a reused grouping or a flagged parent flags many nodes). The OpenAPI
specs do not carry status at all. A first change-list version also reported nodes under new
interface types (FourHundredGigE, ...) as "newly deprecated" although their grouping was already
deprecated.

## Decision
`scripts/build_deprecations.py` runs independent passes and fails unless they agree: a
parser-independent tokenizer (`scripts/_yang_status.py`) and pyang's parser must find the same
status statements per file; every flagged statement must land in one bucket (schema node,
definition, uses/augment, SMIv2 alias, or unreached with a verified reason); `--verify-trees`
matches `pyang -f tree` x/o markers per module. Effective status inherits from parent, uses /
grouping and augment. Changes between releases are keyed per statement by (module, keyword,
context, name, ordinal among same-key siblings), not line numbers; node changes caused only by a
new copy of an already-flagged definition are marked `cause: new-instance`. Deviation modules are
parsed but not applied.

## Alternatives rejected
Grep counts (wrong both ways); counting from the OpenAPI specs (no status); matching changes by
line number (shifts every release) or by node path only (new copies look like new deprecations);
applying all deviations at once (prunes nodes other platforms still have).

## Consequences
Needs the release's YANG sources locally (`references/<ver>/`, gitignored); the script refuses to
run without them rather than falling back to another release. Build oldest release first; a new
release not yet in `releases/index.json` compares against the current newest. Output is ~23 MB
per release (~1.2 MB gzipped). `mib-metadata.json` counts use the same tokenizer and a test keeps
them equal to the census.
