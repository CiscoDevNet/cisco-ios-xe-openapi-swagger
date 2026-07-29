# C9K RESTCONF Harness — Handoff (Track B)

Self-contained context for continuing on the VM that can reach the 6 Catalyst
9000 switches. Keep this file at the repo root. This is the sole context carrier
— the web-app session's chat memory does not travel with the SCP.

## 1. What we're building
A dev-only Python harness (Track B) that connects to 6 real Catalyst 9000
switches (C9200/9300/9400/9500/9600, IOS XE 26.1.1) over RESTCONF and:
1. GET phase (first, strictly READ-ONLY): comprehensive GETs across oper + mib +
   cfg + native models per device; store raw responses locally.
2. Value-discovery: index the captures so we can search a value (e.g. 633024) or
   keyword (policer/dot1x/forus/l2-control) and get back the exact
   pid/module/path/leaf that returned it (CLI-output -> YANG-path mapping).
3. CRUD phase (LATER, separately gated): controlled config changes with backup,
   dry-run, confirmation, and rollback.

Two parallel tracks: Track A = the static web app (other session/workspace);
Track B = this harness (this VM). Web-app injection of captured data is DEFERRED
until we have multi-PID captures.

## 2. Canonical use case
CLI: `show platform hardware fed switch active qos queue stats internal cpu policer`
-> FED control-plane CPU punt-queue policers: queue names (DOT1X Auth, L2 Control,
"Forus" traffic, ...) with accept/drop counters (e.g. 633024).
Goal: find the RESTCONF path returning that data per PID.
Leading candidate found in the 26.1.1 specs:
  Module: Cisco-IOS-XE-switch-dp-punt-inject-oper
  Path:   /data/Cisco-IOS-XE-switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats
  Leaves: cpuq-id, cpu-punt-queue-name
Live capture is the arbiter: confirm whether the policer accept/drop counters
(633024) are returned there, in a sibling leaf, or not modeled in YANG at all
(a "not available via RESTCONF" result is still a valid finding).
Adjacent leads: Cisco-IOS-XE-fib-oper (total-punt/total-punt2host),
Cisco-IOS-XE-platform-software-oper.

## 3. Repo facts the harness needs
- Specs are OpenAPI 3.0 JSON under releases/26.1.1/swagger-<cat>-model/api/*.json.
  servers.url = https://{device}:{port}/restconf ; paths like /data/Cisco-IOS-XE-...:...
  RESTCONF URL = "https://<host>:<port>/restconf" + <openapi path>.
- GET-only categories: oper (~22,144 paths) + mib (~4,272). cfg/native are CRUD
  but can be GET too (read running config). rpc = POST /operations (skip in GET phase).
- Path source per category manifest: releases/26.1.1/swagger-<cat>-model/api/manifest.json ("modules": [...]).
- Existing code to REUSE:
  - scripts/validate_examples_c9kv.py -> restconf_request(method, host, path, payload,
    username, password, port=443): requests + HTTP Basic + verify=False + timeout=30,
    HEADERS = application/yang-data+json. Also has extract_write_examples() for PUT/PATCH/POST
    (useful for the later CRUD phase). Reuse the request pattern; add a GET-only wrapper.
    NOTE: this file is gitignored (local scratch) but travels with an SCP of the folder.
  - scripts/build_paths_index.py -> pattern for building/consuming a JSON search index.
  - scripts/apply_example_overlay.py + references/native-example-overlay.yaml -> overlay injection (Phase 4).
  - scripts/add_oper_examples.py -> domain-aware example injection (Phase 4 alt).
- Run env: `python -X utf8 ...`; `pip install requests`. Confirm Python 3 + requests on the VM first.
- Tests live in tests/ (pytest). Add harness tests + a secret-scan guard for any committed scrubbed capture.

## 4. Harness design (GET phase)
Directory: scripts/harness/ (dev-only; NOT wired into build_release.py, CI, or the Pages deploy).
- request.py: single restconf_get(host, port, path, auth, timeout) that HARD-REFUSES any
  non-GET method (raise). This guard is the safety core for the whole GET phase.
- inventory: scripts/harness/inventory.json (GITIGNORED) =
  [{ "name": "sw1", "pid": "C9300-48T", "host": "10.x.x.x", "port": 443,
     "os_version": "26.1.1", "writable": false }]
  A committed scripts/harness/inventory.example.json ships with placeholders.
- creds: env vars IOSXE_USER / IOSXE_PASS (or per-host in a gitignored secrets file).
  Never write creds into captures or logs.
- path enumeration: read the 4 category manifests -> load each module spec -> collect every
  GET path. Exhaustive per-path GET is the chosen mode; also provide a --roots-only fast mode
  (GET each module root container once; the subtree contains child data).
- capture format: scripts/harness/captures/<device-name>/<category>/<module>__<path-hash>.json =
  { device, pid, host, module, category, path, restconf_url, http_status, fetched_at,
    os_version, response }  (raw response verbatim). captures/ is GITIGNORED.
- robustness: concurrency cap (4-8), per-request timeout, retry/backoff on 5xx/timeouts,
  resume (skip already-captured), rate-limit, per-module summary (200/404/empty/error).
  Handle 204/empty bodies and non-JSON gracefully.
- pilot first: capture ONE device, just the switch-dp-punt-inject-oper path, to prove the
  pipeline end-to-end, then scale to all modules and all 6 devices.

## 5. Value-discovery index
scripts/harness/build_capture_index.py (mirror scripts/build_paths_index.py):
- Walk every captured response; recursively flatten to rows (device, pid, module, path,
  leaf_xpath, value). Emit scripts/harness/capture-index.json (or SQLite for speed).
scripts/harness/find_value.py:
- Query by value (exact/substring, e.g. 633024) OR keyword (policer, dot1x, forus, l2-control,
  cpu-punt-queue-name) -> list of (device, pid, module, path, leaf, value).
- Emit a per-PID coverage matrix (module/path x PID -> has-data / 404 / empty).
Optional: a small offline HTML/JSON report to browse results.

## 6. Sanitization / safety (repo is PUBLIC - CiscoDevNet)
- Raw captures stay LOCAL and GITIGNORED. Nothing device-real is committed until scrubbed + reviewed.
- Redaction level chosen: LIGHT (strip obvious secrets/keys - passwords, community strings,
  certs, private keys, tokens). IPs/serials/MACs/hostnames kept (lab data) UNLESS the data
  classification says otherwise (confirm before committing anything).
- Add a tests/ secret-scan guard over any committed scrubbed capture (regex for
  BEGIN PRIVATE KEY, password/secret fields, SNMP community, etc.).
- Creds only from env/gitignored files; never in outputs.
- GET-only guard enforced in code for this phase.

## 7. Phase 5 - CRUD (LATER; do NOT start until GET capture is solid)
Separate opt-in write mode on top of the default GET-only guard:
- Lab-writable allowlist: refuse writes unless inventory host has "writable": true.
- Backup-before/after: GET the target subtree + running-config before any change; snapshot pre/post.
- Dry-run default: print exact method + URL + body; require --apply and per-change confirmation.
- Reversible/idempotent changes only to start (e.g. a benign interface description or loopback).
- Rollback: keep the pre-change payload; restore and verify.
- Reuse validate_examples_c9kv.py extract_write_examples() to source PUT/PATCH/POST bodies,
  but never fire without the guardrails above.
- Purpose: prove documented write examples work per PID; capture real before/after pairs.

## 8. .gitignore additions (already applied in this repo)
```
scripts/harness/captures/
scripts/harness/inventory.json
scripts/harness/secrets*
scripts/harness/capture-index.*
!scripts/harness/inventory.example.json
```

## 9. Kickoff steps on the VM
1. Confirm Python 3 + `pip install requests`; confirm RESTCONF reachability to one device
   (`curl -k -u <user> https://<host>/restconf/data/Cisco-IOS-XE-native:native/hostname
    -H "Accept: application/yang-data+json"`).
2. Create scripts/harness/ with request.py (GET-only) and the collector; copy
   inventory.example.json -> inventory.json (gitignored) and fill in the 6 devices.
3. Set env: IOSXE_USER / IOSXE_PASS.
4. Pilot: capture switch-dp-punt-inject-oper on ONE device; verify capture format + that
   punt-inject-cpuq-brief-stats returns queue names/counters. Search for 633024.
5. Scale to all oper/mib/cfg/native modules, then all 6 devices (resume-safe).
6. Build capture-index + find_value; produce the CLI->YANG mapping + per-PID coverage.
7. Report back; then plan Phase 4 (web-app injection) and Phase 5 (CRUD).

## 10. Open prereqs to confirm on arrival
- Python/requests present on the VM; direct HTTPS/443 to devices or via jump host?
- The 6 devices' mgmt IPs + exact PIDs + whether lab (affects redaction depth).
- Data classification: is keeping serials/MACs/IPs acceptable for the PUBLIC repo?
