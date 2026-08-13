# 0002 — Redaction must catch bare `key`/`md5` and module-prefixed leaves

- Status: accepted
- Date: 2026-07-31
- Component: device-harness
- Commit/PR: 92822eb90

## Context
The repo is public. `redact.py` masked values whose leaf name matched
`password`/`secret`/`community`/etc. A due-diligence scan found a TACACS shared
key leaked via a leaf simply named `key` — and RESTCONF also module-qualifies it
(`Cisco-IOS-XE-aaa:key`), so a prefix could dodge substring matching.

## Decision
Add an exact-name set (`key`, `md5`, `key-string`, `message-digest-key`,
`authentication-key`, …) and strip the module prefix before matching.
`build_live_examples_index.py` **re-scrubs every value at publish time** so
committed data is clean even if a capture predates a redaction fix. A test scans
the published `live-data/` tree.

## Alternatives rejected
Redact every field containing "key" — rejected: over-redacts benign `key-id`,
`public-key`, `keychain-name`. Drop whole credential modules — rejected: loses
useful structure; field-level redaction is more surgical.

## Consequences
Lab creds are throwaway, but plaintext secrets never publish. Gotcha for future
work: a leaf name alone isn't enough — confirm the exact YANG key, and remember
values are also re-scrubbed at publish time.
