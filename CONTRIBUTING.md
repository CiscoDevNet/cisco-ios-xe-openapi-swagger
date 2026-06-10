# Contributing

Thanks for your interest in improving the Cisco IOS XE OpenAPI documentation hub.

## Quick orientation

- Project type: **static GitHub Pages site** (no backend, no runtime build)
- The bulk of the work happens in `generators/` (Python → OpenAPI) and `scripts/` (post-processing)
- See [AGENTS.md](AGENTS.md) for repo conventions, common tasks, and pitfalls

## Setup

```powershell
git clone https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger.git
cd cisco-ios-xe-openapi-swagger

# Python tooling
python -m pip install --upgrade pip
python -m pip install pyang requests

# Optional dev/test tooling (only needed if you run the test suite or live smoke test)
python -m pip install pytest ftfy playwright
python -m playwright install chromium

# Preview the site
python -m http.server 8000
# → http://localhost:8000
```

## Verifying the build pipeline

```powershell
# Schema unit tests for all 45 manifests (also gated in CI via .github/workflows/tests.yml)
python -X utf8 -m pytest tests/ -v

# Headless smoke test against the live deployment (or a staging URL via --base-url)
python -X utf8 scripts/smoke_live.py
```

## Workflow

1. **Branch** off `main`: `git checkout -b feat/<short-name>`
2. **Make focused changes** — see "What goes where" below
3. **Re-run** the relevant generator/post-processor so committed artifacts stay consistent
4. **Verify locally** — load the affected spec(s) in Swagger UI via the local server
5. **Commit** generator changes *and* their generated outputs in the same commit
6. **Open a PR** with before/after notes (screenshots help for UI changes)

## What goes where

| Change | Edit | Then run |
|---|---|---|
| Add a realistic example value | [scripts/enrich_v2_specs.py](scripts/enrich_v2_specs.py) (`get_example_for_field` / `CONTAINER_FILL`) | `python scripts/enrich_v2_specs.py` |
| Generate specs for a new YANG module | The matching `generators/generate_*_from_tree.py` | Generator → enrich → search index |
| Add a path-based example template | `_build_example_from_path()` in `enrich_v2_specs.py` | `python scripts/enrich_v2_specs.py` |
| Update search behavior | [search.js](search.js) | (refresh browser) |
| Update the search index after spec changes | — | `python scripts/generate_search_index.py` |
| Add a UI feature | The corresponding `*.js` file (no inline scripts) | (refresh browser) |
| Bump YANG release version | All generators + many scripts (touches 100+ files) | **Discuss in an issue first** |

## Walkthrough: add a missing operational spec

End-to-end example of the most common contribution shape. Substitute your
YANG module name for `Cisco-IOS-XE-foo-oper`.

1. **Confirm the gap.** Open [yang-accountability.html](yang-accountability.html),
   filter by status = `Missing spec`, and locate the module. The "Reason" column
   tells you if it was deliberately excluded (skip) or just unbuilt (proceed).
2. **Find the tree.** YANG trees live under `yang-trees/<version>/`. The file is
   `Cisco-IOS-XE-foo-oper.tree` for the 17.18.1 default; per-release copies live
   under `releases/<ver>/yang-trees/`.
3. **Run the matching generator.** Most categories use
   `generators/generate_<category>_from_tree.py`:
   ```powershell
   python generators/generate_oper_from_tree.py `
     --tree yang-trees/Cisco-IOS-XE-foo-oper.tree `
     --out swagger-oper-model/api/Cisco-IOS-XE-foo-oper.json
   ```
   For 26.1.1, also pass `--release 26.1.1` and write under
   `releases/26.1.1/swagger-oper-model/api/`.
4. **Enrich examples.** `python scripts/enrich_v2_specs.py` walks every spec
   and fills realistic `example` values from the heuristics in
   `get_example_for_field()` / `CONTAINER_FILL`.
5. **Refresh the search index.** `python scripts/generate_search_index.py`
   rebuilds `search-index.json` (root + per release).
6. **Refresh accountability.** `python scripts/generate_accountability.py`
   updates `yang_accountability.json` so the module flips from "Missing spec"
   to "Documented".
7. **Refresh manifests.** `python scripts/fix_manifest_schema.py` recomputes
   `total_modules`/`total_paths`/`total_operations`/`spec_count` on every
   affected `manifest.json` so the viewer header math stays correct.
8. **Run the test suite.** `python -X utf8 -m pytest tests/ -v` — all 143
   manifest schema tests must pass.
9. **Preview.** `python -m http.server 8000`, open
   `http://localhost:8000/swagger-oper-model/index.html#spec=Cisco-IOS-XE-foo-oper`,
   click through a couple of paths and confirm the examples render.
10. **Commit the generator output alongside the generator change** in a single
    commit so reviewers can reproduce the diff with one `python` command.

## Rules of thumb

- **Don't hand-edit generated specs** under `swagger-*-model/api/`. They get overwritten.
- **Don't add inline `<script>` or `onclick=`** — strict CSP will block them.
- **Always escape strings** before assigning to `innerHTML`. Use `escapeHtml()` from `search.js`.
- **Always wrap localStorage** writes in try/catch and surface failures via `showToast()`.
- **Keep PRs focused.** A spec-content fix and a UI change should be separate PRs.

## Verifying changes

For spec changes:

```powershell
python scripts/validate_quality.py
python scripts/audit_examples.py
```

For live-device validation (requires a reachable IOS XE 17.18.1+ device):

```powershell
python scripts/validate_examples_c9kv.py `
  --host <ip> --username <user> --password <pw> `
  --patch-only --dry-run
```

## Reporting issues

When filing an issue, include:

- Spec file path (e.g., `swagger-native-config-model/api/native-switching.json`)
- The affected operation (method + path)
- Expected vs actual (screenshot or JSON snippet)
- IOS XE version if validating against a device

## Code of conduct

Be kind, be specific, be patient. This is a community resource that benefits the broader Cisco
network automation ecosystem.
