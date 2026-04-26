#!/usr/bin/env python3
"""
annotate_mdt_xpaths.py — Annotate operational specs with MDT/gRPC dial-out filter xpaths.

Parses ``telemetry-reference-v2.md`` (workspace root) and the active release's oper-model
OpenAPI specs, then injects the ``x-mdt-*`` extensions defined in MDT_XPATH_SPEC.md onto
the matching operations. Also emits ``releases/<ver>/telemetry-index.json`` consumed by
the global telemetry browser.

Idempotent. Safe to re-run.

Usage:
    python scripts/annotate_mdt_xpaths.py --version 26.1.1
    python scripts/annotate_mdt_xpaths.py --version 26.1.1 --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import PROJECT_ROOT, ReleasePaths  # type: ignore  # noqa: E402

WORKSPACE_ROOT = PROJECT_ROOT.parent
TELEMETRY_REF = WORKSPACE_ROOT / "telemetry-reference-v2.md"

# §N section header. Captures section number + title text.
RE_SECTION = re.compile(r"^### §(\d+)\.\s+(.+?)\s*$", re.MULTILINE)
RE_META_ROW = re.compile(r"^\|\s*\*\*([^*]+?)\*\*\s*\|\s*(.+?)\s*\|\s*$", re.MULTILINE)
RE_BACKTICK = re.compile(r"`([^`]+)`")
RE_TIER = re.compile(r"\b(HOT|WARM|COOL)\b\s*\((\d+)s\)", re.IGNORECASE)

MDT_XPATH_RE = re.compile(
    r"^/[a-z][a-z0-9\-]*:[A-Za-z][A-Za-z0-9_\-]*"
    r"(/[A-Za-z][A-Za-z0-9_\-]*(\[[^\]]+\])?)*$"
)


def parse_telemetry_reference() -> list[dict]:
    """Return one entry per §N section that has YANG Module + XPath + Tier."""
    if not TELEMETRY_REF.is_file():
        sys.stderr.write(f"[mdt] missing telemetry reference: {TELEMETRY_REF}\n")
        return []
    text = TELEMETRY_REF.read_text(encoding="utf-8")

    # Split into sections by header line.
    matches = list(RE_SECTION.finditer(text))
    entries: list[dict] = []
    for i, m in enumerate(matches):
        sec_num = m.group(1)
        title = m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end]

        meta: dict[str, str] = {}
        for kv in RE_META_ROW.finditer(body):
            key = kv.group(1).strip().lower()
            val = kv.group(2).strip()
            meta[key] = val

        xpath_raw = meta.get("xpath", "")
        xpath_m = RE_BACKTICK.search(xpath_raw)
        if not xpath_m:
            continue
        xpath = xpath_m.group(1)

        # Some entries use a non-standard prefix shape (e.g. /if: or /rt:); accept those too.
        if not xpath.startswith("/"):
            continue

        tier_text = meta.get("tier", "")
        tier_m = RE_TIER.search(tier_text)
        if not tier_m:
            continue
        tier = tier_m.group(1).upper()
        cadence = int(tier_m.group(2))

        yang_module_raw = meta.get("yang module", "")
        ym = RE_BACKTICK.search(yang_module_raw)
        yang_module = ym.group(1).removesuffix(".yang") if ym else ""

        # Anchor for feature_section: GitHub-style anchor of the section heading.
        anchor = f"§{sec_num}-" + re.sub(
            r"[^a-z0-9]+", "-", title.lower()
        ).strip("-")

        entries.append({
            "section_number": int(sec_num),
            "feature_title": title,
            "feature_section": f"telemetry-reference-v2.md#{anchor}",
            "yang_module": yang_module,
            "filter_xpath": xpath,
            "tier": tier,
            "cadence_seconds": cadence,
            "encoding": "kvGPB",
            "on_change_capable": "on-change" in body.lower()
                                 and "not on-change" not in body.lower(),
            "domain": meta.get("domain", ""),
        })
    return entries


def derive_module_from_xpath(xpath: str) -> str | None:
    """Heuristic: '/process-cpu-ios-xe-oper:cpu-usage/...' → module hint 'process-cpu-ios-xe-oper'."""
    m = re.match(r"^/([a-z][a-z0-9\-]*):", xpath)
    return m.group(1) if m else None


def find_matching_spec(entry: dict, oper_dir: Path) -> Path | None:
    """Locate the OpenAPI spec for a telemetry entry."""
    yang = entry.get("yang_module") or ""
    if yang:
        cand = oper_dir / f"{yang}.json"
        if cand.is_file():
            return cand
    prefix = derive_module_from_xpath(entry["filter_xpath"])
    if prefix:
        # Try Cisco-IOS-XE-<x>-oper.json where prefix = '<x>-ios-xe-oper'
        m = re.match(r"^([a-z0-9\-]+?)-ios-xe-oper$", prefix)
        if m:
            cand = oper_dir / f"Cisco-IOS-XE-{m.group(1)}-oper.json"
            if cand.is_file():
                return cand
        # Try Cisco-IOS-XE-<prefix>.json
        cand = oper_dir / f"Cisco-IOS-XE-{prefix}.json"
        if cand.is_file():
            return cand
    return None


def find_matching_operation(spec: dict, xpath: str) -> tuple[str, str] | None:
    """Return (path, method) of the first GET whose path best matches the xpath tail."""
    paths = spec.get("paths") or {}
    if not isinstance(paths, dict):
        return None
    # Strip the leading "/<prefix>:" and split.
    tail = re.sub(r"^/[a-z][a-z0-9\-]*:", "/", xpath)
    tail_parts = [seg for seg in tail.split("/") if seg]
    candidates: list[tuple[int, str, str]] = []
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        if "get" not in methods:
            continue
        # Match by counting how many of our tail parts appear in the spec path, in order.
        score = 0
        cursor = 0
        for part in tail_parts:
            idx = path.find(part, cursor)
            if idx == -1:
                break
            score += 1
            cursor = idx + len(part)
        if score:
            candidates.append((score, path, "get"))
    if not candidates:
        return None
    candidates.sort(key=lambda t: (t[0], -len(t[1])), reverse=True)
    return candidates[0][1], candidates[0][2]


def annotate(version: str, dry_run: bool) -> int:
    rp = ReleasePaths(version=version, legacy=True)
    oper_dir = rp.spec_dir("swagger-oper-model")
    if not oper_dir.is_dir():
        sys.stderr.write(f"[mdt] no oper-model spec dir: {oper_dir}\n")
        return 1

    entries = parse_telemetry_reference()
    if not entries:
        sys.stderr.write("[mdt] no usable telemetry entries parsed\n")
        return 1
    print(f"[mdt] parsed {len(entries)} telemetry entries from "
          f"{TELEMETRY_REF.relative_to(WORKSPACE_ROOT)}")

    annotated_ops: list[dict] = []
    skipped: list[dict] = []
    by_spec_writes: dict[Path, dict] = {}

    for e in entries:
        if not MDT_XPATH_RE.match(e["filter_xpath"]):
            skipped.append({"entry": e["feature_title"], "reason": "xpath-shape-rejected",
                            "xpath": e["filter_xpath"]})
            continue
        spec_path = find_matching_spec(e, oper_dir)
        if not spec_path:
            skipped.append({"entry": e["feature_title"], "reason": "module-not-in-release",
                            "xpath": e["filter_xpath"]})
            continue
        if spec_path in by_spec_writes:
            spec = by_spec_writes[spec_path]
        else:
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
            except Exception as exc:
                skipped.append({"entry": e["feature_title"], "reason": f"spec-parse-error:{exc}"})
                continue
            by_spec_writes[spec_path] = spec
        op_match = find_matching_operation(spec, e["filter_xpath"])
        if not op_match:
            skipped.append({"entry": e["feature_title"], "reason": "no-matching-operation",
                            "xpath": e["filter_xpath"], "spec": spec_path.name})
            continue
        path, method = op_match
        op = spec["paths"][path][method]
        op["x-mdt-filter-xpath"] = e["filter_xpath"]
        op["x-mdt-tier"] = e["tier"]
        op["x-mdt-cadence-seconds"] = e["cadence_seconds"]
        op["x-mdt-encoding"] = e["encoding"]
        op["x-mdt-on-change-capable"] = e["on_change_capable"]
        op["x-mdt-feature-section"] = e["feature_section"]

        annotated_ops.append({
            "module": spec_path.stem,
            "spec": str(spec_path.relative_to(rp.release_root))
                    if rp.release_root in spec_path.parents
                    else str(spec_path.relative_to(PROJECT_ROOT)),
            "operation_path": path,
            "operation_method": method,
            "operation_id": op.get("operationId", ""),
            "feature_section": e["feature_section"],
            "feature_title": e["feature_title"],
            "filter_xpath": e["filter_xpath"],
            "tier": e["tier"],
            "cadence_seconds": e["cadence_seconds"],
            "encoding": e["encoding"],
            "on_change_capable": e["on_change_capable"],
        })

    if not dry_run:
        for spec_path, spec in by_spec_writes.items():
            spec_path.write_text(
                json.dumps(spec, indent=2) + "\n", encoding="utf-8"
            )

        rp.release_root.mkdir(parents=True, exist_ok=True)
        rp.telemetry_index().write_text(
            json.dumps({
                "version": version,
                "generated": datetime.now(timezone.utc).replace(microsecond=0)
                    .isoformat().replace("+00:00", "Z"),
                "source": "telemetry-reference-v2.md",
                "entries": annotated_ops,
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        rp.telemetry_skipped().write_text(
            json.dumps({"version": version, "skipped": skipped}, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"[mdt] annotated={len(annotated_ops)} specs-touched={len(by_spec_writes)} "
          f"skipped={len(skipped)}{' (dry-run)' if dry_run else ''}")
    by_reason: dict[str, int] = {}
    for s in skipped:
        by_reason[s["reason"]] = by_reason.get(s["reason"], 0) + 1
    for r, n in sorted(by_reason.items()):
        print(f"        ↳ {r}: {n}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", required=True)
    p.add_argument("--dry-run", action="store_true",
                   help="Parse and report, but do not write files")
    args = p.parse_args()
    return annotate(args.version, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
