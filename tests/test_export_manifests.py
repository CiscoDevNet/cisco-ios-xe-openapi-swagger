"""Every download link on exports.html must resolve on the deployed site.

Postman files are committed, so they must exist in the repo. Bruno archives are
built by the deploy workflow (gitignored), so their manifest entries must point
at the .tar.gz layout that generate_bruno_collection.py --archive produces.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASES = sorted(p.parent.parent.name for p in REPO_ROOT.glob("releases/*/exports/postman-manifest.json"))


def _manifest(version: str, kind: str) -> dict:
    return json.loads((REPO_ROOT / "releases" / version / "exports" / f"{kind}-manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("version", RELEASES)
def test_postman_downloads_exist(version):
    manifest = _manifest(version, "postman")
    paths = [c["path"] for c in manifest["collections"]] + [manifest["environment"]]
    missing = [p for p in paths if not (REPO_ROOT / p).is_file()]
    assert not missing, f"{version}: postman manifest points at missing files: {missing}"


@pytest.mark.parametrize("version", RELEASES)
def test_bruno_downloads_are_deploy_built_archives(version):
    collections = _manifest(version, "bruno")["collections"]
    assert collections, f"{version}: bruno manifest lists no collections"
    prefix = f"releases/{version}/exports/bruno/"
    for collection in collections:
        assert collection["path"].startswith(prefix) and collection["path"].endswith(".tar.gz"), (
            f"{version}: {collection['path']} is not a downloadable archive; rebuild with "
            "generate_bruno_collection.py --per-category --archive"
        )
