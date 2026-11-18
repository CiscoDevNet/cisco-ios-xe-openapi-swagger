"""Guard releases/<ver>/platform-api-counts.json (scripts/build_platform_api_counts.py)."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FILES = sorted((ROOT / "releases").glob("*/platform-api-counts.json"))


def test_counts_exist_for_every_platform_support_release():
    have = {p.parent.name for p in FILES}
    want = {p.parent.name for p in (ROOT / "releases").glob("*/platform-support.json")}
    assert want <= have, f"missing platform-api-counts.json for {sorted(want - have)}"


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.parent.name)
def test_platform_counts_are_bounded_by_release_total(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["release"] == path.parent.name
    total = data["all"]
    assert total["paths"] > 0 and total["operations"] >= total["paths"]
    support = json.loads((path.parent / "platform-support.json").read_text(encoding="utf-8"))
    assert [p["id"] for p in data["platforms"]] == [p["id"] for p in support["platforms"]]
    for plat in data["platforms"]:
        assert 0 < plat["paths"] <= total["paths"], plat["id"]
        assert plat["operations"] <= total["operations"], plat["id"]
        for cat, c in plat["by_category"].items():
            assert c["paths"] <= total["by_category"][cat]["paths"], (plat["id"], cat)
    # Unmapped specs should stay a handful; a jump means module attribution broke.
    assert len(data["unmapped"]["specs"]) <= 10
    attr = data["native_attribution"]
    assert attr["augment_attributed"] >= 0.5 * attr["paths"], "native augment attribution collapsed"
