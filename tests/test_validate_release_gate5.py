"""validate_release gate 5 must fail when a spec's tree page (or an accountability tree link) is missing."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_release.py"
spec = importlib.util.spec_from_file_location("validate_release", SCRIPT)
validate_release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_release)


def _release(tmp_path: Path, tree_pages: list[str], tree_urls: list[str]) -> Path:
    rel = tmp_path / "rel"
    (rel / "swagger-oper-model" / "api").mkdir(parents=True)
    (rel / "yang-trees").mkdir()
    for module in ("mod-a", "mod-b"):
        (rel / "swagger-oper-model" / "api" / f"{module}.json").write_text("{}", encoding="utf-8")
    for page in tree_pages:
        (rel / "yang-trees" / f"{page}.html").write_text("<html></html>", encoding="utf-8")
    audit = {"results": [{"module": m, "status": "generated", "reason": None} for m in ("mod-a", "mod-b")]}
    (rel / "tree_audit.json").write_text(json.dumps(audit), encoding="utf-8")
    report = {"modules": [{"name": url, "tree_url": f"yang-trees/{url}.html"} for url in tree_urls]}
    (rel / "yang_accountability.json").write_text(json.dumps(report), encoding="utf-8")
    return rel


def test_gate5_passes_when_all_tree_pages_exist(tmp_path):
    errs: list[str] = []
    validate_release.gate_spec_tree_links(_release(tmp_path, ["mod-a", "mod-b"], ["mod-a"]), errs)
    assert errs == []


def test_gate5_fails_on_missing_spec_tree_page(tmp_path):
    errs: list[str] = []
    validate_release.gate_spec_tree_links(_release(tmp_path, ["mod-a"], []), errs)
    assert len(errs) == 1 and "mod-b" in errs[0]


def test_gate5_fails_on_broken_accountability_tree_link(tmp_path):
    errs: list[str] = []
    validate_release.gate_spec_tree_links(_release(tmp_path, ["mod-a", "mod-b"], ["mod-gone"]), errs)
    assert len(errs) == 1 and "mod-gone" in errs[0]
