# FAQ

Frequently-asked questions about the Cisco IOS-XE OpenAPI / YANG documentation site
(<https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/>).

For the architecture overview see [README.md](README.md); for the release-cadence
runbook see [VERSIONING.md](VERSIONING.md).

---

## Site usage

### Can I use this site offline?

Yes. The site is a Progressive Web App: on first visit a service worker
([service-worker.js](service-worker.js)) pre-caches the app shell (HTML, CSS, JS,
icons, manifest) and serves it offline. Spec JSON, YANG-tree HTML and search-index
files are fetched on demand and cached opportunistically. To install on
Chrome/Edge use the address-bar **Install** action; on iOS Safari use **Share →
Add to Home Screen**.

When a new build is deployed and you have an open tab, a small bottom-right
**Reload** card appears (Tier-9 update-available toast). Click **Reload** to
activate the new version; the page refreshes exactly once.

### How do I find APIs for Catalyst 9k / IOS-XE features?

Three entry points, in order of precision:

1. **Universal search** on the [home page](index.html) — type any keyword
   (`bgp`, `interface`, `mac-address`, `crypto`...). Results group by module
   *and* now surface individual operations (Tier-7 hub-search-ops).
2. **Per-category viewers** (`swagger-cfg-model/`, `swagger-oper-model/`,
   `swagger-native-config-model/`, `swagger-ietf-model/`,
   `swagger-openconfig-model/`, `swagger-mib-model/`, `swagger-rpc-model/`,
   `swagger-events-model/`, `swagger-other-model/`) — each ships a paths-search
   box that walks every spec chunk and deep-links into the right operation.
3. **YANG accountability** — [yang-accountability.html](yang-accountability.html)
   maps every IOS-XE YANG module to its category, spec presence, and (when
   excluded) the documented reason.

Use the version selector in the top nav to switch between 17.9.x, 17.12.x,
17.15.x, 17.18.1 and 26.1.1.

### How do I validate config on a real device?

This site only documents the API surface — it does not push config. Use one of:

* **Postman / Bruno collections** — see "Postman / Bruno exports" below.
* **Code generator** — [code-generator.html](code-generator.html) emits ready-to-run
  curl, Python (`requests`), Ansible, Go and JavaScript snippets for any
  operation, with the device IP, credentials and CSRF/Token plumbing pre-wired.
* **RESTCONF** — every operation page exposes the canonical RESTCONF URL
  (`https://<device>/restconf/data/...`); pair with `Accept:
  application/yang-data+json` and HTTP basic auth (or the configured AAA scheme).
* **NETCONF** — for the `swagger-rpc-model` category, use `<rpc>` over port 830;
  payloads are JSON-Schema mirrors of the YANG `input`/`output` containers.

Always test config changes on a lab device first. The
[release-validate gates](VERSIONING.md#9-release-validate-gates) confirm spec
shape, but only a real device confirms semantics.

### How do I subscribe to MDT (Model-Driven Telemetry)?

* Open [telemetry.html](telemetry.html). The page is generated from
  `releases/<ver>/telemetry-index.json` and lists every YANG xpath that has
  passed the `mdt-annotate` build step's xpath-sanity gate.
* Each entry includes the canonical xpath, recommended period, and a copy-to-
  clipboard YANG-Push subscription template (`establish-subscription` over
  NETCONF, plus a gNMI/dial-out variant).
* For end-to-end pipelines (collector + decoder + dashboard) see the
  [telemetry-reference-v2.md](telemetry-reference-v2.md) cookbook.

### How do shareable deep-links work?

Every URL the **Copy Share Link** button produces uses a fixed hash format
so the link opens directly on the same spec, operation, and IOS-XE release:

```
https://<host>/<category>/index.html?ver=<release>#ver=<release>&spec=<module>&op=<operationId>
```

* `?ver=` and `#ver=` carry the active release (e.g. `26.1.1`). The viewer
  reads from the query first; the hash copy is what survives reloads and
  what other tooling (e.g. `recent-favorites.js`) snapshots.
* `#spec=` is the YANG module file name without the `.json` extension
  (e.g. `Cisco-IOS-XE-native`).
* `#op=` is the OpenAPI `operationId`, which the build step makes globally
  unique so the same hash always lands on exactly one operation.

If the spec doesn't exist in the requested release the viewer surfaces a
yellow toast and falls back to the module list. If you land on a 404 page,
[404.html](404.html) parses the same hash and forwards you to the nearest
correct viewer automatically.

**Keyboard shortcuts:** `/` or `Ctrl+K` focuses the search box on the home
page and every viewer.

---

## Postman / Bruno exports

### Where are the collections?

[exports.html](exports.html) lists every release that has a populated
`releases/<ver>/exports/` directory. Per-category Postman v2.1 collections live
under `releases/<ver>/exports/postman/` and a Postman environment file ships
alongside.

Bruno collection bodies are git-ignored to keep the repo size bounded; only
the `bruno-manifest.json` ships. Regenerate them locally:

```bash
python scripts/generate_bruno_collection.py --version 26.1.1 --per-category --max-mb 50
```

The same script exists for Postman:

```bash
python scripts/generate_postman_v2_collection.py --version 26.1.1 --per-category --max-mb 50
```

### Why are collections split per category?

A single combined collection would exceed Postman's practical import limit and
the 50 MB per-collection gate enforced by
[scripts/validate_release.py](scripts/validate_release.py) gate 7. Splitting by
category (cfg / oper / native-config / ietf / openconfig / mib / rpc / events /
other) keeps each collection import-sized and lets users pull only the surface
they need.

### Can I use the OpenAPI specs directly?

Yes. Each spec under `releases/<ver>/swagger-<cat>-model/api/*.json` is a
self-contained OpenAPI 3.0 document. Use it with any OpenAPI-aware tool
(openapi-generator, Stoplight, Insomnia, Bruno's OpenAPI import, etc.). The
specs are also rendered live in the per-category Swagger-UI viewers on the site.

---

## Contributing / build

### How do I add a new release?

See [VERSIONING.md §8 — Adding a new release: runbook](VERSIONING.md#8-adding-a-new-release--runbook).
Short version: add the YangModels submodule, run `python scripts/build_release.py
--version <new-ver>`, validate with `python scripts/validate_release.py --version
<new-ver>`, then commit and push.

### Where do I report a problem?

Open an issue on the [GitHub repository](https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger/issues).
Include the release, viewer category, and module name (or screenshot of the
operation row). PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
