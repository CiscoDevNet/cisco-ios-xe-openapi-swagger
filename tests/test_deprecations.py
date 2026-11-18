"""Deprecation census (scripts/build_deprecations.py, deprecations.html).

Unit tests pin the status-inheritance and change-classification rules on tiny
modules; the data tests keep the published releases/<ver>/deprecations/ output
internally consistent. Regenerate the data with:
    python scripts/build_deprecations.py --version <ver>   (oldest release first)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_deprecations as bd  # noqa: E402
from _yang_status import lex_status_statements  # noqa: E402
from pyang import context, repository  # noqa: E402

HEADER = 'yang-version 1.1; namespace "urn:{0}"; prefix {0};'


def _census(tmp_path: Path, label: str, name: str, body: str):
    folder = tmp_path / label
    folder.mkdir()
    text = f"module {name} {{ {HEADER.format(name)}\n{body}\n}}\n"
    path = folder / f"{name}.yang"
    path.write_text(text, encoding="utf-8")
    parsed = bd.parse_sources([path], {path: text})
    ctx = context.Context(repository.FileRepository(str(folder), use_env=False))
    ctx.add_module(str(path), text)
    ctx.validate()
    walker = bd.TreeWalker()
    for module in ctx.modules.values():
        if module.keyword == "module":
            walker.walk_module(module)
    return parsed, walker, bd.reconcile(parsed, walker, set())


def test_lexer_ignores_strings_and_comments():
    text = '''
    leaf a { description "status deprecated; is not a statement"; status deprecated; }
    // status obsolete;
    /* status obsolete; */
    leaf b { status "obs" + 'olete'; }
    '''
    assert lex_status_statements(text) == [(2, "deprecated"), (5, "obsolete")]


def test_walker_inherits_status_from_parents_and_uses(tmp_path):
    _, walker, items = _census(tmp_path, "w", "w", """
      grouping g { leaf a { type string; status deprecated; } leaf b { type string; } }
      container top {
        leaf old { type string; status obsolete; }
        container legacy { status deprecated; leaf x { type string; } leaf y { type string; status obsolete; } }
        container one { uses g; }
        container two { uses g { status obsolete; } }
      }""")
    cols = {c: i for i, c in enumerate(bd.NODE_COLUMNS)}
    rows = {r[cols["path"]]: r for r in walker.rows["w"]}
    assert set(rows) == {"/w:top/old", "/w:top/legacy", "/w:top/legacy/y",
                         "/w:top/one/a", "/w:top/two/a", "/w:top/two/b"}
    assert all(r[cols["top_most"]] for r in rows.values())
    a2 = rows["/w:top/two/a"]
    assert (a2[cols["status"]], a2[cols["effective"]], a2[cols["via"]]) == ("deprecated", "obsolete", "uses g")
    assert rows["/w:top/two/b"][cols["status"]] == "current"
    assert walker.effective[("deprecated", "w")] == 3  # legacy, legacy/x, one/a
    assert walker.effective[("obsolete", "w")] == 4    # old, legacy/y, two/a, two/b

    by_name = {it["name"]: it for it in items["w"]}
    assert by_name["a"]["bucket"] == "schema-node"
    assert (by_name["a"]["instances"], by_name["a"]["top_most_instances"]) == (2, 1)
    assert by_name["g"]["bucket"] == "instantiation"
    assert not [it for it in items["w"] if it["bucket"] == "unexplained"]


def test_changes_separate_status_changes_from_new_instances(tmp_path):
    prev = _census(tmp_path, "prev", "t", """
      grouping g { leaf a { type string; status deprecated; } }
      container top {
        container eth { uses g; }
        leaf keep { type string; }
        leaf gone { type string; status deprecated; }
      }""")
    cur = _census(tmp_path, "cur", "t", """
      grouping g { leaf a { type string; status deprecated; } }
      container top {
        container eth { uses g; }
        container eth2 { uses g; }
        leaf keep { type string; status deprecated; }
        leaf added { type string; status obsolete; }
      }""")
    prev_dir = tmp_path / "prev-census"
    (prev_dir / "modules").mkdir(parents=True)
    (prev_dir / "modules" / "t.json").write_text(
        json.dumps(bd.module_shard("prev", "t", "cfg", prev[1], prev[2])), encoding="utf-8")

    changes = bd.compute_changes(prev_dir, prev[0].keys, cur[0], cur[1], cur[2], lambda m: "cfg")
    statements = {e["name"]: e["type"] for e in changes["entries"] if e["element"] == "statement"}
    assert statements == {"keep": "newly-deprecated", "added": "added-obsolete", "gone": "removed"}
    nodes = {e["path"]: (e["type"], e.get("cause")) for e in changes["entries"] if e["element"] == "node"}
    assert nodes == {
        "/t:top/eth2/a": ("newly-deprecated", "new-instance"),
        "/t:top/keep": ("newly-deprecated", "status-change"),
        "/t:top/added": ("newly-obsolete", "status-change"),
        "/t:top/gone": ("removed", None),
    }
    assert changes["summary"]["nodes_new_instance"] == 1


def test_same_target_augments_keep_separate_identities(tmp_path):
    body = """
      container top {{ container e {{ leaf a {{ type string; }} }} }}
      augment "/t:top/t:e" {{ leaf b {{ type string; }} }}
      {extra}"""
    prev = _census(tmp_path, "prev", "t", body.format(
        extra='augment "/t:top/t:e" { status deprecated; leaf c { type string; } }'))
    cur = _census(tmp_path, "cur", "t", body.format(extra=""))
    prev_dir = tmp_path / "prev-census"
    (prev_dir / "modules").mkdir(parents=True)
    (prev_dir / "modules" / "t.json").write_text(
        json.dumps(bd.module_shard("prev", "t", "mib", prev[1], prev[2])), encoding="utf-8")
    changes = bd.compute_changes(prev_dir, prev[0].keys, cur[0], cur[1], cur[2], lambda m: "mib")
    statements = [(e["keyword"], e["type"]) for e in changes["entries"] if e["element"] == "statement"]
    assert statements == [("augment", "removed")]


def test_unfetched_release_fails_instead_of_using_legacy_sources():
    with pytest.raises(SystemExit, match="not found"):
        bd.build("99.9.9", verify=False, workers=1)


# ------------------------------------------------------------ published data

def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


VERSIONS = [r["ver"] for r in _load(REPO_ROOT / "releases" / "index.json")["releases"]]


@pytest.mark.parametrize("ver", VERSIONS)
def test_published_census_is_consistent(ver):
    base = REPO_ROOT / "releases" / ver / "deprecations"
    index = _load(base / "index.json")
    v = index["validation"]
    assert v["passed"] and not v["unexplained"] and not v["lexical_vs_parsed_mismatches"]
    assert v["lexical_status_statements"] == v["parsed_status_statements"]
    assert sum(v["by_bucket"].values()) == v["flagged_statements"]

    shards = {p.stem for p in (base / "modules").glob("*.json")}
    assert shards == set(index["by_module"])
    totals = {st: {"statements": 0, "explicit_nodes": 0, "top_most_nodes": 0} for st in bd.FLAGGED}
    for name, entry in index["by_module"].items():
        shard = _load(base / "modules" / f"{name}.json")
        cols = {c: i for i, c in enumerate(shard["node_columns"])}
        for st in bd.FLAGGED:
            assert entry[st]["statements"] == sum(1 for it in shard["items"] if it["status"] == st)
            assert entry[st]["explicit_nodes"] == sum(1 for r in shard["nodes"] if r[cols["status"]] == st)
            assert entry[st]["top_most_nodes"] == sum(
                1 for r in shard["nodes"] if r[cols["top_most"]] and r[cols["effective"]] == st)
            for k in totals[st]:
                totals[st][k] += entry[st][k]
    for st in bd.FLAGGED:
        for k, value in totals[st].items():
            assert index["totals"][st][k] == value
    assert sum(index["totals"][st]["statements"] for st in bd.FLAGGED) == v["flagged_statements"]

    if index["changes"] and index["changes"].get("summary"):
        changes = _load(base / "changes.json")
        assert changes["from"] == index["changes"]["from"] == VERSIONS[VERSIONS.index(ver) + 1]
        assert changes["summary"] == index["changes"]["summary"]


@pytest.mark.parametrize("ver", VERSIONS)
def test_mib_metadata_counts_match_census(ver):
    census = _load(REPO_ROOT / "releases" / ver / "deprecations" / "index.json")["by_module"]
    for mib in _load(REPO_ROOT / "releases" / ver / "mib-metadata.json")["mibs"]:
        entry = census.get(mib["name"])
        expected = (entry["deprecated"]["statements"], entry["obsolete"]["statements"]) if entry else (0, 0)
        assert (mib["deprecated_count"], mib["obsolete_count"]) == expected, mib["name"]
