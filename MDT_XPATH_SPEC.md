# MDT / gRPC Dial-Out Filter XPath Specification

**Status:** Active (Phase 0 of multi-version rollout)
**Scope:** Defines how the project derives, stores, and surfaces Model-Driven Telemetry (MDT) filter xpaths for gRPC dial-out subscriptions. Companion to [VERSIONING.md](VERSIONING.md) and [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md).

The authoritative reference for human-curated subscription metadata is `telemetry-reference-v2.md` at the workspace root.

---

## 1. The rule

For an operational YANG container at module-prefix `<prefix>` and absolute path `<path>`, the MDT filter xpath used in `subscription` configuration is:

```
filter xpath /<prefix>:<path-without-leading-slash>
```

Worked examples (taken from `telemetry-reference-v2.md`):

| Feature | YANG container path | Filter xpath |
|---------|---------------------|--------------|
| CPU utilization | `/cpu-usage/cpu-utilization` (module `Cisco-IOS-XE-process-cpu-oper`, prefix `process-cpu-ios-xe-oper`) | `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization` |
| Memory statistics | `/memory-statistics/memory-statistic` (`memory-ios-xe-oper`) | `/memory-ios-xe-oper:memory-statistics/memory-statistic` |
| Interface stats | `/interfaces/interface` (`interfaces-ios-xe-oper`) | `/interfaces-ios-xe-oper:interfaces/interface` |
| Environment sensors | `/environment-sensors` (`environment-ios-xe-oper`) | `/environment-ios-xe-oper:environment-sensors` |
| BGP state | `/bgp-state-data` (`bgp-ios-xe-oper`) | `/bgp-ios-xe-oper:bgp-state-data` |

The filter xpath always begins with a single `/`, then the YANG module's `prefix:` (no slash between `/` and the prefix), then the YANG path (no leading slash on the path component).

## 2. Validation regex

CI gate (see [VERSIONING.md §9](VERSIONING.md#9-ci-gates-per-release)) validates every emitted xpath against:

```
^/[a-z][a-z0-9\-]*:[A-Za-z][A-Za-z0-9_\-]*(/[A-Za-z][A-Za-z0-9_\-]*(\[[^\]]+\])?)*$
```

This permits:
- a single module prefix segment immediately after the leading `/`,
- subsequent path segments separated by `/`,
- optional list-key predicates in `[name='Gi0/0/1']` shape on any segment.

It forbids: leading `/<container>` without a prefix; multiple `:` segments; spaces; non-ASCII characters.

## 3. OpenAPI extensions

Operational-model OpenAPI specs annotate operations with the following vendor extensions. All are optional; absence means the operation is not currently flagged as a recommended MDT subscription target.

| Key | Type | Description |
|-----|------|-------------|
| `x-mdt-filter-xpath` | string | The filter xpath produced by §1 (one operation may be the recommended subscription root for multiple xpaths; in that case the annotation is on the closest matching operation). |
| `x-mdt-tier` | enum: `HOT` \| `WARM` \| `COOL` | Subscription tier from `telemetry-reference-v2.md`. |
| `x-mdt-cadence-seconds` | integer | Recommended sample interval. Conventional values: `30` (HOT), `60` (WARM), `300` (COOL). Use `0` to denote on-change. |
| `x-mdt-encoding` | enum: `kvGPB` \| `JSON_IETF` | Wire encoding. Default `kvGPB`. |
| `x-mdt-on-change-capable` | boolean | True if this xpath supports on-change (subscribe interval `0`). |
| `x-mdt-feature-section` | string | Anchor link back to the matching `§N` section in `telemetry-reference-v2.md`, e.g. `#§1-cpu-utilization`. |

Example fragment in an oper-model spec operation:

```json
{
  "get": {
    "summary": "Read cpu-usage/cpu-utilization",
    "x-mdt-filter-xpath": "/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization",
    "x-mdt-tier": "WARM",
    "x-mdt-cadence-seconds": 60,
    "x-mdt-encoding": "kvGPB",
    "x-mdt-on-change-capable": false,
    "x-mdt-feature-section": "telemetry-reference-v2.md#§1-cpu-utilization"
  }
}
```

## 4. `telemetry-index.json` (per release)

The annotation pass also emits `releases/<ver>/telemetry-index.json` consumed by the global telemetry browser (`telemetry.html`). Schema:

```json
{
  "version": "26.1.1",
  "generated": "2026-04-25T12:00:00Z",
  "entries": [
    {
      "module": "Cisco-IOS-XE-process-cpu-oper",
      "spec": "swagger-oper-model/api-v2/Cisco-IOS-XE-process-cpu-oper.json",
      "operation_id": "get-cpu-usage-cpu-utilization",
      "feature_section": "telemetry-reference-v2.md#§1-cpu-utilization",
      "feature_title": "CPU Utilization",
      "filter_xpath": "/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization",
      "tier": "WARM",
      "cadence_seconds": 60,
      "encoding": "kvGPB",
      "on_change_capable": false
    }
  ]
}
```

## 5. Annotation source of truth

The annotation pipeline (`scripts/annotate_mdt_xpaths.py`) joins three inputs:

1. **`telemetry-reference-v2.md`** — provides the authoritative `feature → xpath, tier, cadence, on-change-capable` mapping. The script parses each `§N` section and the "Subscription Summary Table" in Part IV.
2. **The OpenAPI spec for that module** — locates the operation whose path most closely matches the YANG container path, and writes the extensions onto that operation.
3. **The pyang tree** (`releases/<ver>/yang-trees/<module>.html`) — used as a fallback to confirm the prefix and that the container exists in the source YANG; if the tree disagrees with the reference doc, the build emits a warning and skips the annotation rather than emitting a wrong xpath.

If a feature in `telemetry-reference-v2.md` references a module not present in the active release (e.g. a 26.1.1-only module annotating into a 17.9.x build), the annotator records it in the per-release `telemetry-skipped.json` with reason `module-not-in-release`. This is allowed and not a CI failure.

## 6. UI surfaces

Three surfaces, all reading the data above (no separate copy):

1. **Per-operation badge** — Swagger UI plugin in `swagger-oper-model/index-v2.html` reads `x-mdt-filter-xpath` from the rendered operation and injects an "MDT" badge with copy-to-clipboard.
2. **Per-viewer MDT panel** — collapsible side panel listing every `x-mdt-filter-xpath` in the currently loaded oper spec; searchable; jumps to the matching operation when clicked.
3. **Global telemetry browser** (`telemetry.html`) — loads `releases/<ver>/telemetry-index.json`; filters by tier (HOT/WARM/COOL), encoding, on-change-capable; deep-links into the appropriate oper-model viewer with `#ver=<v>&spec=swagger-oper-model/<module>` and scrolls to the matching operation.

## 7. Out of scope

- Generating Postman/Bruno MDT subscribe payloads from these annotations (deferred; the project records this as a future enhancement).
- gNMI dial-in / dial-out path syntax (the rule and validation in §1–2 are RESTCONF/MDT-flavored YANG xpath; gNMI prefix-relative paths require a different shape).
- Subscriptions for non-operational models (config, RPC, events). Those are not MDT subscription targets.
