# ASSURANCE_SPEC.md — cisco-ios-xe-openapi-swagger

> Mandatory post-change validation for any LLM coding agent touching this repo.
> Run **every applicable check** below before reporting work complete. Report
> in the exact [Final assurance report](#final-assurance-report-required) format
> at the bottom — no exceptions.

---

## 1. Project overview

Static GitHub Pages site that documents every Cisco IOS-XE YANG model as
browsable OpenAPI/Swagger specs, multi-release. Pure front-end (vanilla
HTML/JS, no backend). Python generators build the artifacts under
`releases/<ver>/`; a GitHub Actions workflow validates and deploys to
`https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/`.

**Primary users (in priority order):**

1. Cisco network engineers locating RESTCONF endpoints for a YANG module.
2. Telemetry / MDT subscribers selecting xpaths.
3. Developers generating client code via [code-generator.html](code-generator.html).
4. Public web — anyone arriving from a search engine on a deep-link.

**Releases tracked:** `17.9.x`, `17.12.x`, `17.15.x`, `17.18.1`, `26.1.1` (default).

**Viewer categories (9):** `swagger-oper-model`, `swagger-cfg-model`,
`swagger-native-config-model`, `swagger-openconfig-model`, `swagger-rpc-model`,
`swagger-ietf-model`, `swagger-mib-model`, `swagger-events-model`,
`swagger-other-model`.

**Hub pages:** [index.html](index.html), [platform-coverage.html](platform-coverage.html),
[yang-accountability.html](yang-accountability.html), [telemetry.html](telemetry.html),
[tree-compare.html](tree-compare.html), [code-generator.html](code-generator.html),
[exports.html](exports.html), [about.html](about.html), [404.html](404.html).

**Git remotes:** `dev` = jeremycohoe fork (staging, push freely); `prod` =
CiscoDevNet (live Pages, push only on deliberate releases). See
[AGENTS.md](AGENTS.md) for full conventions.

---

## 2. Critical invariants (red lines)

These are the user-declared "must never break" rules. **Any failure here is
a FAIL, regardless of what else passes.**

| ID | Invariant | How verified |
|---|---|---|
| INV-1 | Live site homepage loads (no broken hub) | Smoke test S-1 |
| INV-2 | Deep-links shared externally (`#spec=<name>`) resolve to the correct viewer + module | Smoke tests S-2, S-3 |
| INV-3 | Per-release artifact counts (modules / paths / ops) match each viewer's `manifest.json` | `scripts/validate_release.py` |
| INV-4 | No YANG module silently disappears between releases without explanation | Regression check R-3 |
| INV-5 | CSP stays strict — no `'unsafe-inline'` or new remote `script-src` on hub pages | `tests/test_security_regressions.py` |
| INV-6 | Default release stays `26.1.1` unless an explicit task changes it | Regression check R-1 |
| INV-7 | `service-worker.js` `CACHE_VERSION` bumps whenever a cached asset changes | Regression check R-2 |
| INV-8 | localStorage keys (`theme`, recents, favorites) keep their existing shape | Regression check R-4 |

---

## 3. Required validation commands

Run **in this order**. Stop on first FAIL and report; do not proceed past a
required gate. PowerShell 5.1 syntax (`;` not `&&`); cwd = repo root.

### 3.1 Environment setup (once per session)
```powershell
cd "<repo-root>\cisco-ios-xe-openapi-swagger"
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'
```

### 3.2 Required gates (must PASS)

| # | Gate | Command | Failure means |
|---|---|---|---|
| G-1 | Unit tests | `python -X utf8 -m pytest tests/test_no_emoji.py tests/test_security_regressions.py -q` | Emoji introduced, or CSP/XSS regression — **block deploy** |
| G-2 | Per-release validation (only releases you touched) | `python -X utf8 scripts/validate_release.py --version 26.1.1` (repeat for each touched release) | Manifest / artifact mismatch — **block deploy** |
| G-3 | Manifest schema check (informational only — 6 known-failing) | `python -X utf8 -m pytest tests/test_manifest_schema.py -q` | Only **new** failures count; record pre-existing 6 as baseline |
| G-4 | Internal link integrity (workflow `linkcheck.yml`) | Trigger via GitHub Actions OR locally: `python -X utf8 scripts/audit_refs.py` if changes touch HTML/JS/Markdown links | Broken internal link — **block deploy** |
| G-5 | GitHub Actions `Deploy to GitHub Pages` workflow finished `success` for the deploy commit | `gh run list --workflow=deploy-pages.yml --limit 1` OR API: `https://api.github.com/repos/CiscoDevNet/cisco-ios-xe-openapi-swagger/actions/runs?per_page=1` | If `failure` at the `Deploy to GitHub Pages` step itself (last step) → likely transient infra; **retry with empty commit** `git commit --allow-empty -m "chore: retrigger Pages deploy"` |

### 3.3 Informational only (run, record, never gate)

- `.github/workflows/lighthouse.yml`
- `.github/workflows/a11y.yml`
- `.github/workflows/htmlcheck.yml`

Record their status in the report but do not block on them.

### 3.4 Build commands (reference)

Most changes only edit HTML/JS/JSON — no build needed. For regenerating
release artifacts:

```powershell
python -X utf8 scripts/build_release.py --version 26.1.1
python -X utf8 scripts/generate_platform_support.py
python -X utf8 scripts/generate_search_index.py
python -X utf8 scripts/generate_sitemap.py
```

---

## 4. Critical smoke tests (the top-3 user flows)

These are the user-ranked critical flows. **Required to verify any UI change
to the live deployed Pages site.**

Use the integrated browser (or `Invoke-WebRequest` for headless checks).
Each smoke test has an exact pass criterion — record what you actually saw,
not what you expect.

### S-1 — Viewer renders a spec
- **URL:** `https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/swagger-oper-model/index.html#spec=Cisco-IOS-XE-tcam-oper`
- **PASS criteria (all of):**
  - Page title contains `Operational APIs`
  - Sidebar shows ≥ 200 specs for 26.1.1 (currently 215)
  - Right pane shows endpoints under `Cisco-IOS-XE-tcam-oper`
  - **Platform badge bar** at top of viewer shows `cat9k` chip (Switching, blue)
  - No new CSP errors in console (existing `validator.swagger.io` CSP block is **expected, ignore**)
- **FAIL if:** stuck on "Loading…" > 10s, sidebar empty, badge bar shows
  the "No NETCONF capability entry for…" fallback for a real YANG module
  (not a sub-spec), or any **new** console errors not in the known list.

### S-2 — Deep-link to operational module
- **URL:** `https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/swagger-oper-model/index.html#spec=Cisco-IOS-XE-bgp-oper`
- **PASS criteria:**
  - Spec auto-loads (no manual click needed)
  - Badge bar shows ≥ 6 platforms (currently 7: asr1k, c8000v, c8500, cat9k, ess3x00, ie3x00, isr1k)
- **FAIL if:** lands on the default landing pane and never resolves the hash.

### S-3 — Module accountability diff
- **URL:** `https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/yang-accountability.html`
- **PASS criteria:**
  - Page renders without "Loading…" stuck > 10s
  - At least one release column populated with module counts
  - Switching between releases updates the table
- **FAIL if:** empty table, JS errors in console, or `yang_accountability.json` 404s.

### S-4 (regression — added 2026-06-02) — platform-coverage matrix
- **URL:** `https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/platform-coverage.html`
- **PASS criteria:**
  - Release dropdown populated with all 5 releases (26.1.1 selected)
  - Summary line shows `1006 of 1006 modules · 10 platforms · release 26.1.1`
  - Matrix table renders with ≥ 100 visible rows
- **FAIL if:** stuck on "Loading…" (likely CSP-blocked inline script; fix
  per [CSP fix history](#known-fragile-areas)).

> **Coverage note:** `platform-coverage.html` is included in
> `tests/test_security_regressions.py::STRICT_CSP_PAGES` as of 2026-06-09,
> so any reintroduction of an inline `<script>` block is caught by G-1.

---

## 5. Regression checks

Run these whenever you touch the corresponding area.

| ID | Trigger | Check | Command |
|---|---|---|---|
| R-1 | Any HTML/JS edit to a hub page | Confirm default release still `26.1.1` | `grep -rn "26\.1\.1\|17\.18\.1" releases/index.json platform-support-index.json` and visually confirm `default:"26.1.1"` |
| R-2 | Any edit to a file cached by SW | Bump `CACHE_VERSION` in `service-worker.js` line 16 | `grep -n "CACHE_VERSION" service-worker.js` — version string must differ from `main` HEAD |
| R-3 | Any change to generators or `releases/` | Module count parity across releases | `python -X utf8 scripts/audit_swagger_vs_tree.py` and inspect deltas — any module that **disappears without appearing in `NATIVE-AUGMENT-AUDIT.md` or release notes is a FAIL** |
| R-4 | Any JS edit to `index-app.js`, `recent-favorites.js`, `assets/js/site-chrome.js` | localStorage shape unchanged | Manually load deployed site, set theme to dark, add a favorite, reload — both must persist |
| R-5 | Any edit to `swagger-native-config-model/index.html` or `assets/js/platform-support.js` | Native sub-spec → `Cisco-IOS-XE-native` resolution still works | Smoke: visit `swagger-native-config-model/index.html#spec=native-bgp` and confirm badge bar shows 10 platforms |
| R-6 | Any edit to `404.html` | Hash-aware deep-link recovery still routes `#spec=...` to the correct viewer | Visit `swagger-foo-model/` (intentional 404) with `#spec=Cisco-IOS-XE-tcam-oper` → must redirect to `swagger-oper-model/` |

---

## 6. Data validation checks

**This is the highest-priority section** — the user's stated worst-case is
"missing APIs and missing YANG modules" or "specs render but data is wrong".

| ID | Check | Command | Pass criteria |
|---|---|---|---|
| D-1 | Manifest `total_modules` equals actual `.json` file count (excluding `manifest.json` + `_*.json`) | `python -X utf8 scripts/validate_release.py --version <v>` for each touched release | Exit 0, no `❌` lines |
| D-2 | Every viewer's `manifest.json` is parseable JSON | `python -X utf8 -c "import json,glob; [json.load(open(f, encoding='utf-8')) for f in glob.glob('releases/*/swagger-*-model/api/manifest.json')]"` | No exception |
| D-3 | `search-index.json` contains every module from every manifest | `python -X utf8 scripts/check_native_coverage.py` (or equivalent — see also `scripts/audit_swagger_vs_tree.py`) | No "missing in search-index" warnings |
| D-4 | `platform-support-index.json` lists all 5 releases and points at a default that exists | `Invoke-WebRequest .../platform-support-index.json \| ConvertFrom-Json` — assert `releases.Count -eq 5` and `releases -contains default` | Both true |
| D-5 | No duplicate operation IDs within any spec | `python -X utf8 scripts/audit_opid_duplicates.py` | Empty report |
| D-6 | Per-release `platform-support.json` parses and has > 800 modules each | `Get-ChildItem releases/*/platform-support.json \| % { (Get-Content $_ -Raw \| ConvertFrom-Json).modules.PSObject.Properties.Count }` | All ≥ 800 |
| D-7 | No emoji / no UTF-8 mojibake reintroduced | Part of G-1 | — |

**Rule of thumb:** if a module count drops by **more than 5 between commits**,
treat as suspect and explain in the report.

---

## 7. Integration checks

There is **no backend, no LLM, no third-party API** the site depends on at
runtime. The only integration is **GitHub Pages itself**.

- **GitHub Pages deploy:** G-5 covers this. Note: the `actions/deploy-pages@v5`
  step occasionally fails transiently (observed 2026-06-02 and 2026-06-09 on
  this repo, also seen 2026-06-01 in the wider Pages incident). Retry with an
  empty commit before declaring FAIL.
- **`validator.swagger.io`:** intentionally blocked by CSP. The console error
  `Loading the image 'https://validator.swagger.io/validator?...' violates...`
  is **expected** — do not report as a regression.
- **`fonts.googleapis.com` / `fonts.gstatic.com`:** allowed by CSP but the page
  must remain functional with the local fallback (`-apple-system, sans-serif`).
  Do not add any new external `script-src` or `connect-src` origin.

---

## 8. Security / privacy checks

| ID | Check | Command | Pass criteria |
|---|---|---|---|
| SEC-1 | No URL-controlled value flows into a DOM sink unescaped | Part of G-1 (`test_no_url_to_dom_sink`) | All tests pass |
| SEC-2 | No `javascript:` URL or unguarded `location.href = ... + ...` redirect | Part of G-1 (`test_no_javascript_url_redirect`) | All tests pass |
| SEC-3 | Strict-CSP hub pages contain no inline executable `<script>` | Part of G-1 (`test_strict_csp_pages_have_no_inline_exec_script`) | All tests pass |
| SEC-4 | CSP header in every hub page contains `default-src 'self'` and does **not** contain `'unsafe-inline'` or `'unsafe-eval'` for `script-src` | `grep -n "Content-Security-Policy" *.html` and visually inspect | None loosened |
| SEC-5 | No new external origins added to `connect-src` / `script-src` / `frame-src` | `git diff main -- '*.html'` and inspect CSP lines | No new origins |
| SEC-6 | No secrets, tokens, or internal hostnames committed | `git diff main` review | None present |
| SEC-7 | No analytics / tracking / fingerprinting added | `grep -rn "google-analytics\|gtag\|hotjar\|mixpanel\|segment\|amplitude" --include="*.html" --include="*.js"` | Empty |

The site collects **no PII**, uses no cookies, and stores only
`theme` + recents/favorites in `localStorage`. Any change that broadens
client-side storage is a privacy regression.

---

## 9. Performance checks

Per user direction, only **link integrity** is a required gate; perf and
a11y are informational.

| ID | Check | Status | Notes |
|---|---|---|---|
| P-1 | `linkcheck.yml` workflow | **Required PASS** | Broken internal link → FAIL |
| P-2 | `lighthouse.yml` workflow | Informational | Record score deltas in report |
| P-3 | `a11y.yml` workflow | Informational | Record violations in report |
| P-4 | `htmlcheck.yml` workflow | Informational | Record validation errors in report |
| P-5 | Total deploy artifact size growth | Informational | Workflow prints `du -sh deploy`; flag if > +10 MB in one commit |
| P-6 | Large-file warning (>50 MB) | Informational | Known: `tools/IOS-XE-RESTCONF-v2-deep-part1.postman_collection.json` (91 MB), `tools/IOS-XE-RESTCONF-v1.postman_collection.json` (65 MB) — do not add more |

---

## 10. What to do when a check cannot be run

| Situation | Action | Mark as |
|---|---|---|
| Network unreachable, can't fetch live URL | Run `Invoke-WebRequest -UseBasicParsing` on `localhost` after `python -m http.server` in `deploy/` if available; otherwise skip the smoke test | **PARTIAL** — explain which smoke was skipped and why |
| GitHub Actions API rate-limited | Wait, OR check the green check on the commit page directly; if neither possible, mark G-5 as **PARTIAL** | **PARTIAL** |
| Browser tool unavailable | Use `Invoke-WebRequest` to fetch HTML + a single referenced JS asset and confirm both return 200 and content includes expected substrings | **PARTIAL** — note the substring assertions used |
| A required script (e.g. `validate_release.py`) is missing from the repo | Do **NOT** invent equivalents | **FAIL** — and surface the missing file as a finding |
| Test suite errors out before running (e.g. missing pytest) | Install: `python -m pip install pytest` then retry. If still failing, mark **FAIL** and report the install error verbatim | **FAIL** |
| User's change is purely a docs/README/comment edit | Skip S-* and most data checks. **Still run G-1 and SEC-* tests.** | **PASS** with explicit list of skipped sections and one-line justification |

**Never** report `PASS` for a check you did not actually run. Use `PARTIAL`
with explicit "could not run because…" reasoning.

---

## 11. Final assurance report (REQUIRED)

After running all applicable checks, append this exact block to the end of
your reply to the user. Do not omit fields. Do not add free-form prose
between fields.

```
=== ASSURANCE REPORT ===
Commit:           <sha or "uncommitted">
Files changed:    <count> (<comma list of top-level dirs touched>)
Releases touched: <list, e.g. "26.1.1, 17.18.1" or "none">

GATES (required):
  G-1 unit tests:                [PASS|FAIL|PARTIAL] <one-line evidence>
  G-2 validate_release per ver:  [PASS|FAIL|PARTIAL|N/A] <per-release results>
  G-4 linkcheck:                 [PASS|FAIL|PARTIAL|N/A] <evidence>
  G-5 Pages deploy:              [PASS|FAIL|PARTIAL|N/A] <run URL + conclusion>

SMOKE (live site):
  S-1 viewer renders spec:       [PASS|FAIL|SKIPPED] <observation>
  S-2 deep-link bgp-oper:        [PASS|FAIL|SKIPPED] <observation>
  S-3 yang-accountability:       [PASS|FAIL|SKIPPED] <observation>
  S-4 platform-coverage matrix:  [PASS|FAIL|SKIPPED] <observation>

REGRESSION:
  R-1..R-6:                      [PASS|FAIL|N/A per item] <details only for non-PASS>

DATA:
  D-1..D-7:                      [PASS|FAIL|N/A per item] <details only for non-PASS>

SECURITY:
  SEC-1..SEC-7:                  [PASS|FAIL|N/A per item] <details only for non-PASS>

PERF (informational):
  P-1 linkcheck:                 [PASS|FAIL|N/A]
  P-2..P-4 lighthouse/a11y/html: <scores/violations or "not run">
  P-5 artifact size delta:       <e.g. "+0.3 MB" or "not measured">

SKIPPED CHECKS:
  - <id>: <reason>

NEW FINDINGS / FOLLOW-UPS:
  - <bullet list, or "none">

OVERALL: [PASS | FAIL | PARTIAL]
Rationale: <one or two sentences. Required even on PASS.>
=== END REPORT ===
```

**Decision rules for `OVERALL`:**
- **PASS** — every required gate (G-1, G-2, G-4, G-5), every applicable
  smoke test, and every applicable regression/data/security check is `PASS`.
- **FAIL** — any required gate is `FAIL`, OR any smoke/regression/data/
  security check is `FAIL`, OR an invariant from §2 was violated.
- **PARTIAL** — no `FAIL`s, but one or more applicable checks could not be
  run. List every skipped check with its reason in the `SKIPPED CHECKS:`
  section — an empty list contradicts a `PARTIAL` verdict.

---

## Known fragile areas (read before starting work)

1. **Inline `<script>` blocks on hub pages** — CSP `default-src 'self'`
   blocks them silently (no fallback, no UI message — page just freezes).
   Move JS to `assets/js/<name>.js` and reference via `<script src=...>`.
   `tests/test_security_regressions.py::test_strict_csp_pages_have_no_inline_exec_script`
   guards every hub page including `platform-coverage.html` (added
   2026-06-09). Add any new hub page to the `STRICT_CSP_PAGES` list when
   you create it.

2. **Manifest count off-by-one** — `.github/workflows/deploy-pages.yml`
   "Validate manifests" step must exclude both `manifest.json` AND
   `_*.json` helper indexes (`_paths_index.json`, etc.). A bare
   `grep -v manifest` breaks every model dir. See
   [`scripts/validate_release.py`](scripts/validate_release.py) `is_spec_file()`.

3. **`actions/deploy-pages@v5` transient failure** — even with a clean
   build, the final deploy step occasionally returns failure due to Pages
   infra. Retry with `git commit --allow-empty -m "chore: retrigger Pages deploy"`
   before treating as a real bug.

4. **Service worker caching** — `service-worker.js` line 16
   `CACHE_VERSION` must bump on every release of static assets, else
   users see stale cached versions indefinitely.

5. **Native viewer sub-spec naming** — `swagger-native-config-model` splits
   `Cisco-IOS-XE-native` into sub-specs (`native-aaa`, `native-bgp`,
   `native-00-core`, …). The platform-badge lookup resolves these via
   `assets/js/platform-support.js::resolveModuleName` — preserve that
   mapping if you refactor.

6. **PowerShell exit-1 on `git push`** — `git push` writes progress to
   stderr; PowerShell returns exit 1 even on success. Confirm by parsing
   the `<old>..<new> main -> main` line, not the exit code.

7. **OneDrive read-only `.git` paths** — `git rm -rf` and
   `git remote rename` may hang on prompts. Use Python `shutil.rmtree`
   with `onerror=chmod` fallback for cleanup.
