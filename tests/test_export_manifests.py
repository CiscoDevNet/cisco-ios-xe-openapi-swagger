"""Every download link on exports.html must resolve on the deployed site.

Postman and Bruno collections are built by the deploy workflow (gitignored), so
their manifest entries must point at the archive layout the generators produce
with ``--archive``. smoke S-9 checks the deployed files actually answer 200.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASES = sorted(p.parent.parent.name for p in REPO_ROOT.glob("releases/*/exports/postman-manifest.json"))
ARCHIVE_SUFFIX = {"postman": ".postman_collection.json.zip", "bruno": ".tar.gz"}
MAX_UNCOMPRESSED = 50 * 1024 * 1024


def _manifest(version: str, kind: str) -> dict:
    return json.loads((REPO_ROOT / "releases" / version / "exports" / f"{kind}-manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("kind", sorted(ARCHIVE_SUFFIX))
@pytest.mark.parametrize("version", RELEASES)
def test_downloads_are_deploy_built_archives(version, kind):
    collections = _manifest(version, kind)["collections"]
    assert collections, f"{version}: {kind} manifest lists no collections"
    prefix = f"releases/{version}/exports/{kind}/"
    for collection in collections:
        assert collection["path"].startswith(prefix) and collection["path"].endswith(ARCHIVE_SUFFIX[kind]), (
            f"{version}: {collection['path']} is not a downloadable {kind} archive; rebuild with --per-category --archive"
        )
        assert collection.get("uncompressed_bytes", 0) <= MAX_UNCOMPRESSED, (
            f"{collection['path']} is {collection['uncompressed_bytes']} bytes uncompressed (cap 50 MiB)"
        )


@pytest.mark.parametrize("version", RELEASES)
def test_postman_environment_is_listed(version):
    assert _manifest(version, "postman")["environment"].startswith(f"releases/{version}/exports/postman/")


@pytest.mark.parametrize("version", RELEASES)
def test_export_request_counts_match_release_operations(version):
    operations = json.loads((REPO_ROOT / "release_counts.json").read_text(encoding="utf-8"))["releases"][version]["totals"]["operations"]
    for kind in ARCHIVE_SUFFIX:
        requests = sum(c["request_count"] for c in _manifest(version, kind)["collections"])
        assert requests == operations, f"{version} {kind}: {requests} requests vs {operations} operations"
