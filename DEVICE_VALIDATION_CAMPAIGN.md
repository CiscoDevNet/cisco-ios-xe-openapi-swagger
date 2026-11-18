# Device Validation Campaign — Master Plan (DRAFT for review)

> **Status: DRAFT — do not start implementation yet.**
> This document is for iterative review. We will refine scope, add test-harness
> details, add device details, define the observability/accountability capture
> (syslog + EEM catch-all CLI), review repeatedly, and **only then** begin work.
>
> Goal: turn the published specs from *browsable* into *executable*, prove it by
> exercising the Cat9k-applicable subset of ~90,000 operations against a real
> device, and capture — for every call — the **resulting CLI and syslog** so each
> API is provably mapped to device behavior. Then promote device-verified minimal
> payloads back into the specs.

Status legend: ⬜ not started · 🟡 in progress · ✅ done · ❓ open question

---

## 0. Open questions to resolve before we build (review checklist)

- ❓ Example storage: inline `x-example-minimal` in specs vs. sidecar `_examples_index.json` (size budget).
- ❓ Config choice metadata: extend config generators to emit `x-yang-choices`, or use safe fallback first.
- ❓ Device details: exact platform/model, IOS-XE version, mgmt reachability, test VRF/scopes.
- ❓ EEM applet method: catch-all `event cli` applet vs. `archive log config` + `logging` correlation.
- ❓ Syslog transport: on-box buffer scrape via RESTCONF/CLI vs. remote syslog collector.
- ❓ Correlation key: how we tie a RESTCONF op → the CLI lines → the syslog events (timestamp window vs. marker).
- ❓ Run scale/throttle: concurrency + rate that the box's RESTCONF/nginx tolerates.

---

## 1. Decisions (locked 2026-06-15)

| Topic | Decision |
|---|---|
| Target device | **Single Catalyst 9000 switch** (IOS-XE). Pre-filter the call set to what this platform actually supports. |
| Write authorization | **Phase 1 = read-only (GET) only.** Writes/RPCs are a later, separately-authorized phase. |
| Payload strategy | **Bake `x-example-minimal` into the specs** (single source of truth) and have the harness consume the same field. |
| Harness location | **New folder `tools/device-harness/`** — Python driver, resumable run log. |
| Definition of done | **Device-verified minimal example payloads promoted into the specs**, plus a per-op CLI+syslog accountability record. |
| Accountability capture | **EEM catch-all applet records applied CLI; syslog captured and correlated per call.** *(NEW — details below, TBD)* |

Secrets rule: credentials are **never** committed or typed into chat. They come from env
vars / interactive terminal prompt at run time.

---

## 2. Why the specs are not directly executable today (the real problem)

1. **RPC choice bloat.** `rpc:hw-module` (and most RPCs) render the *entire* YANG `choice`
   tree — every mutually-exclusive sub-command (`switch`, `subslot`, `beacon`, `led`, …)
   as sibling optional properties. RESTCONF requires **exactly one** choice branch; posting
   the whole schema-shaped object → `400 malformed message`.
   - Good news: the RPC generator already emits **`x-yang-choices`** metadata describing
     which properties are mutually exclusive. That is exactly what the minimizer needs.
2. **Config over-specification.** A native VLAN body that includes every optional leaf will
   include leaves the platform doesn't support → `400`. The minimal valid body is tiny
   (list key + the one or two leaves you actually want).
3. **List keys.** Config models carry list keys in the **RESTCONF URL path** (path params),
   so config *bodies* often don't repeat them. RPC inputs carry keys inline. The minimizer
   must handle both.

---

## 3. Known gaps discovered during planning (address in Phase 0)

- **`x-yang-choices` is RPC-only.** `generate_rpc_openapi_v2.py` emits it; the native-config /
  other generators do **not**. The minimizer either (a) gets choice metadata extended into the
  config generators, or (b) falls back to "emit no optional choice branches" for config.
- **Example storage size budget.** Baking a full example into all 11,610 native-config write
  paths could re-introduce the file-bloat we just fought. Mitigation options (decide in Phase 0):
  - Only bake examples for **write-capable** ops (RPC + config PUT/PATCH), never GET.
  - Cap example depth/char budget (same pattern as the `kw` field: `_KW_MAX_CHARS`).
  - If still too big, store examples in a **sidecar `_examples_index.json`** per category.

---

## 4. Observability & accountability (NEW — to be refined)

We don't just want HTTP status codes; we want to know **what each RESTCONF call actually did**
on the device, expressed as native CLI and syslog. This becomes a durable "API → CLI" map.

### 4.1 EEM catch-all applet (captures applied CLI)
Use an Embedded Event Manager applet that fires on **any** configuration CLI and logs the
command, so every RESTCONF-driven config change leaves a CLI breadcrumb in syslog.

> **DRAFT — to validate on the box. Do not apply yet.**
```
! Catch-all: log every config command that is applied (RESTCONF or CLI)
event manager applet CATCHALL-CONFIG
 event cli pattern ".*" sync no skip no
 action 1.0 syslog priority informational msg "EEM-CFG-CLI: $_cli_msg"
 action 2.0 set _exit_status "1"
```
Open items:
- ❓ `event cli` fires for **CLI-entered** commands; confirm whether RESTCONF/NETCONF-applied
  config triggers `event cli` or whether we need **`archive` config-change logging** instead:
  ```
  archive
   log config
    logging enable
    logging size 1000
    notify syslog contenttype plaintext
    hidekeys
  ```
  `show archive log config all` then yields the exact CLI deltas with a session id — likely the
  **more reliable** path for RESTCONF-applied changes. **Decision pending: archive-log-config is the
  leading candidate; EEM catch-all as supplement.**
- ❓ Whether to also capture `show running-config` diff (before/after) per write as ground truth.

### 4.2 Syslog capture
- Per call, capture new syslog lines generated in the call's time window.
- Options: scrape `show logging` over RESTCONF/CLI after each call (simple, on-box buffer), or
  point the box at a **remote syslog collector** the harness reads (cleaner correlation, more setup).
- Ensure timestamps are high-resolution: `service timestamps log datetime msec`.

### 4.3 Correlation strategy (RESTCONF op ↔ CLI ↔ syslog)
- Inject a **marker** around each write: a harmless, uniquely-identifiable change (or a
  `logging` marker) so the archive-log-config session / syslog window is unambiguous.
- Record per op: `op_id, http_status, request_body, archive_cli[], syslog_lines[], running_diff`.
- For **Phase 1 (read-only)** there is no config change, so CLI/syslog capture is mostly N/A;
  this accountability machinery is exercised in **Phase 2 (writes/RPCs)**.

### 4.4 Artifacts produced
- `accountability/<op_id>.json` — body + CLI + syslog + diff per validated op.
- A rolled-up **API↔CLI map** (e.g. `api_to_cli.json`) suitable for docs / the published site.

---

## 5. Phased plan

### Phase 0 — Offline payload synthesis (no device) ⬜
- `minimizer.py` — schema (+`x-yang-choices`) → minimal valid body:
  - Object w/ choices: include only **one** case (first `mandatory`, else first), recurse.
  - List: include `x-key` leaves when key is in body (RPC); skip when key is URL path param (config).
  - Leaf synthesis: `enum`→first · `pattern`→safe literal · int→`minimum`/1 (clamp `maximum`) · string→placeholder · bool→`true`.
  - Drop optional non-key containers off the chosen path; respect `mandatory`.
- Wire into generators: each **write** op gets `x-example-minimal` + OpenAPI `examples`.
- Proof set first: `rpc:hw-module` (beacon) + one native VLAN spec. Eyeball before scaling.

### Phase 1 — Read-only device sweep ⬜ (read creds only)
- `catalog.py` — unify all 9 `_paths_index.json` into one op list.
- `capability.py` — `GET .../ietf-yang-library` → supported modules/features → intersect with catalog.
- `classify.py` — tag each op: `oper-get` · `config-get` · `config-write` · `rpc` + risk.
- `driver.py` — async **GET-only** (method allow-list enforced **in code**), concurrency 8–16,
  backoff on `429/503`, per-call timeout.
- `runlog.sqlite` — resumable: `op_id, method, url, status, latency_ms, bytes, err, ts`.
- `report.py` — coverage matrix + summary; `404/405` ⇒ unsupported ⇒ prune.

### Phase 2 — Example validation, accountability & promotion ⬜ (separate write authorization)
- Per write op on a **safe scope**: capture baseline → apply `x-example-minimal` →
  **capture CLI (archive log config) + syslog** → verify → **revert**.
- RPCs: explicit **allow-list** only (beacon on/off, `show`-style). Never reload/power-cycle/erase.
- Promote device-validated bodies into specs as `x-example-minimal` + `x-verified: true`,
  and emit the API↔CLI map.

---

## 6. Proposed folder layout

```
tools/device-harness/
  DEVICE_VALIDATION_CAMPAIGN.md   # (this file may live at repo root; TBD)
  README.md                       # how to run, env vars, safety notes
  config.example.yaml             # host, port, verify_tls, concurrency, scopes (NO secrets)
  catalog.py                      # unify the 9 _paths_index.json
  capability.py                   # yang-library -> supported-module set -> intersect
  classify.py                     # per-op type + risk tag
  minimizer.py                    # schema (+x-yang-choices) -> minimal valid body (shared w/ generators)
  driver.py                       # async sweep, allow-list, retry/backoff, checkpoint
  accountability.py               # EEM/archive-log-config + syslog capture + correlation
  report.py                       # coverage matrix + API<->CLI map
  runlog.sqlite                   # resumable run state (gitignored)
  accountability/                 # per-op CLI+syslog+diff json (gitignored)
```

Auth/access: RESTCONF over HTTPS; `Accept/Content-Type: application/yang-data+json`.
Credentials from `XE_HOST` / `XE_USER` / `XE_PASS` env (or interactive prompt). Never in repo.

---

## 7. Device details (TO FILL IN during review)

| Field | Value |
|---|---|
| Platform / model | _TBD_ |
| IOS-XE version | _TBD_ |
| Mgmt IP / RESTCONF port | _TBD (default 443)_ |
| Auth method | _TBD (basic / token)_ |
| Test VRF / safe interfaces | _TBD_ |
| Snapshot/revert available? | _TBD_ |
| Remote syslog collector? | _TBD_ |
| Maintenance window | _TBD_ |

---

## 8. Risk controls

- **Read-only enforced in code** (not config) for Phase 1.
- **Capability pre-filter** avoids hammering the box with thousands of `404`s.
- **Rate limiting + backoff** so on-box nginx/RESTCONF isn't overwhelmed.
- **Resumable run log** so a large sweep survives interruption and never double-fires.
- **Phase gating**: no writes until Phase 1 is clean *and* write authorization is granted.
- **Capture-before-change + revert** for every Phase 2 write; nothing left dirty.

---

## 9. Review log (append as we iterate)

- 2026-06-15 — Initial draft created. Pending: example-storage decision, config `x-yang-choices`,
  device details, EEM-vs-archive-log-config decision, syslog transport, correlation key.
