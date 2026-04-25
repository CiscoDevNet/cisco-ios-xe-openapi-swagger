# Contributing

Thanks for your interest in improving the Cisco IOS-XE OpenAPI documentation hub.

## Quick orientation

- Project type: **static GitHub Pages site** (no backend, no runtime build)
- The bulk of the work happens in `generators/` (Python → OpenAPI) and `scripts/` (post-processing)
- See [AGENTS.md](AGENTS.md) for repo conventions, common tasks, and pitfalls

## Setup

```powershell
git clone https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger.git
cd cisco-ios-xe-openapi-swagger

# Python tooling
python -m pip install --upgrade pip
python -m pip install pyang requests

# Preview the site
python -m http.server 8000
# → http://localhost:8000
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

## Rules of thumb

- **Don't hand-edit generated specs** under `swagger-*-model/api-v2/`. They get overwritten.
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

For live-device validation (requires a reachable IOS-XE 17.18.1+ device):

```powershell
python scripts/validate_examples_c9kv.py `
  --host <ip> --username <user> --password <pw> `
  --patch-only --dry-run
```

## Reporting issues

When filing an issue, include:

- Spec file path (e.g., `swagger-native-config-model/api-v2/native-switching.json`)
- The affected operation (method + path)
- Expected vs actual (screenshot or JSON snippet)
- IOS-XE version if validating against a device

## Code of conduct

Be kind, be specific, be patient. This is a community resource that benefits the broader Cisco
network automation ecosystem.
