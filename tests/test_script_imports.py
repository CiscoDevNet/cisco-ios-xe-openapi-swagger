"""Every local helper module imported by scripts/*.py must be committed.

scripts/_release_paths.py was once hidden by the ``scripts/_*.py`` gitignore
rule, which broke ten generators on every fresh clone.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"


def _local_imports() -> set[str]:
    names: set[str] = set()
    for script in SCRIPTS_DIR.glob("*.py"):
        tree = ast.parse(script.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names.add(node.module.split(".")[0])
            elif isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
    names.discard("__future__")
    return {name for name in names if (SCRIPTS_DIR / f"{name}.py").exists() or name.startswith("_")}


@pytest.mark.parametrize("module", sorted(_local_imports()))
def test_local_helper_is_present_and_not_gitignored(module):
    helper = SCRIPTS_DIR / f"{module}.py"
    assert helper.is_file(), f"scripts/{module}.py is imported but missing"
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(helper)], cwd=SCRIPTS_DIR.parent, check=False,
    ).returncode == 0
    assert not ignored, f"scripts/{module}.py is gitignored; add a !negation to .gitignore"
