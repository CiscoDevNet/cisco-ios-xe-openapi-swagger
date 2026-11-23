# 0008 — No secrets, hashes or credential usernames in public data or history

- Status: accepted
- Date: 2026-11-21
- Component: device-harness
- Commit/PR: (history rewrite of both repos, 2026-11-21; supersedes 0005)

## Context
GitGuardian public monitoring (incident 3498322) flagged a username/password in
`netconf-getconfig-live-data.json` in a past commit. A full review found the published data
and history had also carried type 7 (reversible) and type 9/5 hashes, the plaintext AP / lab
password, the TACACS+ key and SNMP communities. Masking was by leaf name only, so path-joined
telemetry keys (`…:key/key`), nested `password/text` objects, underscore names, hashes and
many CLI forms slipped through, and the CI gate shared those blind spots. Cisco policy
requires revoking an exposed secret and removing it from the repository and its history.

## Decision
Supersedes 0005: lab credentials ARE sensitive in a public repo. One rule set
(`redact_payload.py`) masks by normalised leaf name, by structure (secret containers), by value
(crypt hashes, PEM) and in CLI text, and also masks usernames tied to credentials, always with
the fixed `***REDACTED***`. `scrub_published_data.py` re-scrubs all published device data.
Gates scan payloads embedded as strings and every tracked text file, including SHA-256 hashes
of previously leaked values. The credentials were rotated, then both repos' history was
rewritten (`git filter-repo`) and force-pushed.

## Alternatives rejected
Rotate only and keep history (fails the policy and keeps GitGuardian open); delete the device
datasets (loses the feature; field-level masking is enough); masking with a hash or prefix of
the value (still leaks or allows matching).

## Consequences
Every clone and fork made before 2026-11-21 still holds the old history: re-clone, never push
from an old clone. GitHub Support must purge cached views and unreachable commits. New leaks:
rotate first, then scrub HEAD and rewrite history. Never paste device output into docs, tests
or fixtures; use values containing `FAKE`.

## Follow-up (2026-11-24)
An independent audit of the published data after the rewrite found the lab username still in
MIB columns (`ccmHistoryEventTerminalUser`, `ccmCTIDWhoChanged`, `casnUserId`,
`cSipCfgAaaUsername`), OpenConfig `admin-username`, NACM `rule-list` names, mdt-oper-v2
`mdt-connections/peer-id` (the dial-in session user) and telemetry list
keys (`keys` / `samples[].keys` of `native/username*` rows, where the parent is the word `keys`,
not the list). Rules added: `USERNAME_SUFFIX` (…username / …userid / …terminaluser /
…whochanged), `rule-list` in `USERNAME_LISTS`, `USERNAME_IN_CONTEXT` (peer-id),
`p-user` / `p-pass` (MDT proxy credentials), and `redact_list_keys(keys, path)`, which
judges list keys by the row `path`. List keys are identifiers, so keys under password /
credential containers (line `first`, AP `wtp_mac`) stay visible. 28 files re-scrubbed.
Checked and kept: `*-pem` fields are public SUDI / CA certificates (no private keys); values
shaped like type 7 are serial numbers, MD5 fingerprints and boot-integrity hashes.
Generally: when adding a dataset, check new username-bearing leaves against the lab user
(compare in code, never print), and add a `FAKE` test to `tests/test_redaction_rules.py`.
