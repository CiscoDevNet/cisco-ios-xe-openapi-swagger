#!/usr/bin/env python3
"""
generate_bruno_collection.py — Per-(version, model-category) Bruno collections.

Bruno (https://docs.usebruno.com/) is a Postman alternative whose collections are
stored as plain ``.bru`` files inside a directory tree, one file per request. This
generator emits one Bruno collection per (release, model-category) pair under
``releases/<ver>/exports/bruno/<category>/`` plus a top-level ``bruno.json``
metadata file Bruno uses to identify the folder as a collection.

Hard 50 MB cap per collection (per VERSIONING.md §9 gate 7); individual ``.bru``
files are tiny so that limit is rarely hit. If hit anyway, the script auto-splits
by adding ``-part-N`` suffix folders and records the split in
``releases/<ver>/exports/bruno-manifest.json``.

Usage:
    python scripts/generate_bruno_collection.py --version 26.1.1 --per-category --max-mb 50
    python scripts/generate_bruno_collection.py --version 26.1.1 --per-category --archive

``--archive`` replaces each collection folder with a deterministic ``.tar.gz``
(a browser cannot download a folder; ~245k tiny .bru files also compress far
better as one solid stream than as a zip). The deploy workflow builds these.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import shutil
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import (PROJECT_ROOT, MODEL_CATEGORIES, ReleasePaths)  # type: ignore  # noqa: E402

METHODS = ("get", "put", "patch", "post", "delete", "head", "options")
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._\-]+")
# Specs ship servers as https://{device}[:{port}]/restconf or a literal lab IP;
# Bruno only substitutes {{var}}, so every request uses one variable origin.
SERVER_ORIGIN_RE = re.compile(r"^https?://[^/]+")
BRUNO_ORIGIN = "https://{{host}}:{{port}}"

COLLECTION_BRU = """meta {
  name: %s
}

auth {
  mode: basic
}

auth:basic {
  username: {{username}}
  password: {{password}}
}
"""

ENVIRONMENT_BRU = """vars {
  host: 10.0.0.1
  port: 443
  username: admin
}
vars:secret [
  password
]
"""


def safe_name(s: str) -> str:
    s = SAFE_NAME_RE.sub("_", s).strip("._")
    return s[:200] or "request"


def render_bru_request(seq: int, name: str, method: str, url: str,
                       summary: str | None, body_example: dict | None) -> str:
    """Produce a minimal but valid Bruno .bru file body."""
    out_lines: list[str] = []
    out_lines.append("meta {")
    out_lines.append(f"  name: {name}")
    out_lines.append("  type: http")
    out_lines.append(f"  seq: {seq}")
    out_lines.append("}")
    out_lines.append("")
    out_lines.append(f"{method} {{")
    out_lines.append(f"  url: {url}")
    out_lines.append("  body: " + ("json" if body_example else "none"))
    out_lines.append("  auth: inherit")
    out_lines.append("}")
    out_lines.append("")
    out_lines.append("headers {")
    out_lines.append("  Accept: application/yang-data+json")
    if body_example:
        out_lines.append("  Content-Type: application/yang-data+json")
    out_lines.append("}")
    if body_example is not None:
        out_lines.append("")
        out_lines.append("body:json {")
        try:
            payload = json.dumps(body_example, indent=2)
        except Exception:
            payload = "{}"
        for ln in payload.splitlines():
            out_lines.append("  " + ln)
        out_lines.append("}")
    if summary:
        out_lines.append("")
        out_lines.append("docs {")
        for ln in summary.splitlines():
            out_lines.append("  " + ln)
        out_lines.append("}")
    return "\n".join(out_lines) + "\n"


def collect_requests_from_spec(spec_path: Path) -> list[dict]:
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    server = ""
    servers = spec.get("servers") or []
    if servers and isinstance(servers, list):
        s0 = servers[0]
        if isinstance(s0, dict):
            server = s0.get("url", "") or ""
    if not server:
        server = "https://{host}/restconf/data"
    server = SERVER_ORIGIN_RE.sub(BRUNO_ORIGIN, server, count=1)

    out: list[dict] = []
    for path, methods in (spec.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        for method in METHODS:
            op = methods.get(method)
            if not isinstance(op, dict):
                continue
            example: dict | None = None
            rb = op.get("requestBody")
            if isinstance(rb, dict):
                content = rb.get("content") or {}
                for ct, cdef in content.items():
                    if not isinstance(cdef, dict):
                        continue
                    if "example" in cdef:
                        example = cdef["example"]
                        break
                    examples = cdef.get("examples") or {}
                    if examples:
                        first = next(iter(examples.values()))
                        if isinstance(first, dict) and "value" in first:
                            example = first["value"]
                            break
            out.append({
                "name": safe_name(op.get("operationId") or f"{method.upper()} {path}"),
                "method": method.upper(),
                "url": server.rstrip("/") + path,
                "summary": op.get("summary") or "",
                "body": example if method in ("put", "patch", "post") else None,
                "spec": spec_path.stem,
            })
    return out


def _init_collection_dir(collection_dir: Path, name: str) -> None:
    collection_dir.mkdir(parents=True, exist_ok=True)
    meta = {"name": name, "version": "1", "type": "collection"}
    (collection_dir / "bruno.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (collection_dir / "collection.bru").write_text(COLLECTION_BRU % name, encoding="utf-8")
    env_dir = collection_dir / "environments"
    env_dir.mkdir(exist_ok=True)
    (env_dir / "IOS-XE.bru").write_text(ENVIRONMENT_BRU, encoding="utf-8")


def write_collection(out_dir: Path, version: str, category: str,
                     requests: list[dict], max_bytes: int) -> list[dict]:
    """Write requests into out_dir; auto-split into -part-N if size exceeds cap."""
    parts: list[dict] = []
    cur_dir = out_dir
    cur_size = 0
    cur_name = f"IOS-XE-{version}-{category}"
    cur_part = 1
    _init_collection_dir(cur_dir, cur_name)

    seq = 1
    written_in_part = 0
    for req in requests:
        body = render_bru_request(seq, req["name"], req["method"], req["url"],
                                  req.get("summary"), req.get("body"))
        b = body.encode("utf-8")
        if cur_size + len(b) > max_bytes and written_in_part > 0:
            parts.append({"name": cur_name, "path": cur_dir.relative_to(PROJECT_ROOT).as_posix(),
                          "request_count": written_in_part, "size_bytes": cur_size})
            cur_part += 1
            cur_name = f"IOS-XE-{version}-{category}-part-{cur_part}"
            cur_dir = out_dir.parent / f"{out_dir.name}-part-{cur_part}"
            _init_collection_dir(cur_dir, cur_name)
            cur_size = 0
            written_in_part = 0
            seq = 1

        # Group by spec into subfolders for clarity.
        sub = cur_dir / safe_name(req["spec"])
        sub.mkdir(parents=True, exist_ok=True)
        # Bruno on Windows trips the MAX_PATH (260) limit when filenames echo
        # the (already long) module name. Truncate the seq filename so the
        # absolute path always fits, and prepend ``\\?\`` for the actual write.
        max_basename = 80
        basename = f"{seq:04d}-{req['name']}"
        if len(basename) > max_basename:
            basename = basename[:max_basename]
        f = sub / f"{basename}.bru"
        f_str = str(f)
        if os.name == "nt" and len(f_str) > 240 and not f_str.startswith("\\\\?\\"):
            f_str = "\\\\?\\" + f_str
        Path(f_str).write_bytes(b)
        cur_size += len(b)
        written_in_part += 1
        seq += 1

    parts.append({"name": cur_name, "path": cur_dir.relative_to(PROJECT_ROOT).as_posix(),
                  "request_count": written_in_part, "size_bytes": cur_size})
    return parts


def archive_collection(collection_dir: Path) -> Path:
    """Pack a collection folder into ``<folder>.tar.gz`` and delete the folder.

    Byte-for-byte reproducible: sorted members, zeroed mtimes/owners, and a
    zeroed gzip header timestamp."""
    archive = collection_dir.with_name(collection_dir.name + ".tar.gz")

    def normalize(info: tarfile.TarInfo) -> tarfile.TarInfo:
        info.mtime = 0
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        info.mode = 0o755 if info.isdir() else 0o644
        return info

    with open(archive, "wb") as raw, \
            gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz, \
            tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
        members = [collection_dir, *sorted(collection_dir.rglob("*"))]
        for member in members:
            arcname = member.relative_to(collection_dir.parent).as_posix()
            tar.add(member, arcname=arcname, recursive=False, filter=normalize)
    shutil.rmtree(collection_dir)
    return archive


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", required=True)
    p.add_argument("--per-category", action="store_true",
                   help="Emit one collection per model-category (recommended)")
    p.add_argument("--max-mb", type=int, default=50,
                   help="Hard cap per collection in MB (default 50)")
    p.add_argument("--archive", action="store_true",
                   help="Replace each collection folder with a downloadable .tar.gz")
    args = p.parse_args()

    rp = ReleasePaths(version=args.version, legacy=True)
    max_bytes = args.max_mb * 1024 * 1024
    bruno_root = rp.exports_dir("bruno")
    if bruno_root.is_dir():
        shutil.rmtree(bruno_root)  # drop parts/archives left by a previous layout
    bruno_root.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    if not args.per_category:
        all_requests: list[dict] = []
        for cat in MODEL_CATEGORIES:
            for spec in sorted(rp.spec_dir(cat).glob("*.json")):
                if spec.name == "manifest.json":
                    continue
                all_requests.extend(collect_requests_from_spec(spec))
        target = bruno_root / f"IOS-XE-{args.version}-all"
        parts = write_collection(target, args.version, "all", all_requests, max_bytes)
        manifest.extend(parts)
    else:
        for cat in MODEL_CATEGORIES:
            requests: list[dict] = []
            for spec in sorted(rp.spec_dir(cat).glob("*.json")):
                if spec.name == "manifest.json":
                    continue
                requests.extend(collect_requests_from_spec(spec))
            if not requests:
                continue
            cat_short = cat.replace("swagger-", "").replace("-model", "")
            target = bruno_root / f"IOS-XE-{args.version}-{cat_short}"
            parts = write_collection(target, args.version, cat_short, requests, max_bytes)
            manifest.extend(parts)

    if args.archive:
        for part in manifest:
            archive = archive_collection(PROJECT_ROOT / part["path"])
            part["path"] = archive.relative_to(PROJECT_ROOT).as_posix()
            part["uncompressed_bytes"] = part["size_bytes"]
            part["size_bytes"] = archive.stat().st_size
            part["format"] = "tar.gz"

    mpath = rp.exports_dir() / "bruno-manifest.json"
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps({
        "version": args.version,
        "generated": datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
        "max_bytes": max_bytes,
        "collections": manifest,
    }, indent=2) + "\n", encoding="utf-8")

    total_requests = sum(c["request_count"] for c in manifest)
    print(f"[bruno] wrote {len(manifest)} collection part(s), total "
          f"{total_requests} request(s) → {bruno_root.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
