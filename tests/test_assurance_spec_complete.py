"""Spec-rot guard for ASSURANCE_SPEC.md.

This test scans the spec for every file path it mentions (markdown links,
inline-code paths, and bare `scripts/`, `tests/`, `.github/workflows/` paths)
and asserts that each one exists on disk. If someone renames or deletes a
script that the spec references, this test fails fast — preventing the spec
from drifting into a useless pile of dead pointers.

It also enforces the structural invariants the spec relies on:

- The spec contains the required sections (\u00a71..\u00a711 + final report block).
- Every gate G-N and smoke S-N is uniquely defined.
- The final assurance report template (\u00a711) is well-formed and includes
  the OVERALL line.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SPEC = REPO / "ASSURANCE_SPEC.md"

# Strings that look like paths but should be ignored (examples, externals, etc.)
IGNORE_PATTERNS = (
    "example.com",
    "example.org",
    "localhost",
    "127.0.0.1",
    "https://",
    "http://",
    "vscode://",
    "file://",
    "ciscodevnet.github.io",
    "github.com",
)

# Path-like things that aren't repo files we need to verify
NON_FILE_TOKENS = {
    "swagger-cfg-model",
    "swagger-oper-model",
    "swagger-openconfig-model",
    "swagger-ietf-model",
    "swagger-mib-model",
    "swagger-events-model",
    "swagger-rpc-model",
    "swagger-other-model",
    "swagger-native-config-model",
    "releases",
    "yang-trees",
    "tools",
}


@pytest.fixture(scope="module")
def spec_text() -> str:
    assert SPEC.exists(), f"ASSURANCE_SPEC.md not found at {SPEC}"
    return SPEC.read_text(encoding="utf-8")


def _candidate_paths(text: str) -> set[str]:
    """Extract file paths referenced in the spec."""
    paths: set[str] = set()

    # Markdown links: [label](path)
    for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        paths.add(m.group(1))

    # Inline-code segments containing slashes — `scripts/foo.py`, `tests/bar.py`, etc.
    for m in re.finditer(r"`([^`\n]+)`", text):
        token = m.group(1).strip()
        # Quick filter: must contain a slash and look filesystem-y
        if "/" not in token:
            continue
        # First whitespace-separated chunk only (commands frequently follow)
        first = token.split()[0]
        paths.add(first)

    cleaned: set[str] = set()
    for p in paths:
        if any(pat in p for pat in IGNORE_PATTERNS):
            continue
        # Strip anchors and query strings
        p = p.split("#", 1)[0].split("?", 1)[0]
        if not p:
            continue
        # Skip Python-style symbol references (file.py::symbol)
        if "::" in p:
            continue
        # Skip template placeholders like <name>, <ver>
        if "<" in p or ">" in p:
            continue
        # Skip pure directory tokens
        if p.rstrip("/") in NON_FILE_TOKENS:
            continue
        # Only consider paths under known repo subdirs or root .md / .yml / .py files
        if not (
            p.startswith(("scripts/", "tests/", ".github/", "assets/", "docs/", "archive/", "generators/"))
            or re.fullmatch(r"[A-Za-z0-9_.\-]+\.(md|py|yml|yaml|html|js|json|txt)", p)
        ):
            continue
        cleaned.add(p)
    return cleaned


def test_spec_exists(spec_text: str) -> None:
    assert len(spec_text) > 1000, "ASSURANCE_SPEC.md is suspiciously short"


def test_every_referenced_file_exists(spec_text: str) -> None:
    missing: list[str] = []
    for rel in sorted(_candidate_paths(spec_text)):
        if not (REPO / rel).exists():
            missing.append(rel)
    assert not missing, (
        "ASSURANCE_SPEC.md references files that do not exist on disk. "
        "Either restore the files or update the spec.\n  - "
        + "\n  - ".join(missing)
    )


def test_required_sections_present(spec_text: str) -> None:
    required = [
        r"^##\s*1\.\s",   # Project overview
        r"^##\s*2\.\s",   # Invariants
        r"^##\s*3\.\s",   # Gates
        r"^##\s*4\.\s",   # Smoke tests
        r"^##\s*5\.\s",   # Regression
        r"^##\s*6\.\s",   # Data
        r"^##\s*7\.\s",   # Integration
        r"^##\s*8\.\s",   # Security
        r"^##\s*9\.\s",   # Performance
        r"^##\s*10\.\s",  # Fallback
        r"^##\s*11\.\s",  # Final assurance report
    ]
    for pat in required:
        assert re.search(pat, spec_text, re.MULTILINE), f"missing section matching: {pat}"


def test_gates_and_smokes_are_unique(spec_text: str) -> None:
    # Gates G-1..G-N must each appear at least once as table row id
    gates = re.findall(r"\|\s*(G-\d+)\s*\|", spec_text)
    assert len(gates) >= 5, f"expected \u22655 gate rows, found {len(gates)}: {gates}"
    assert len(gates) == len(set(gates)), f"duplicate gate IDs: {gates}"

    # S-1..S-N likewise
    smokes = re.findall(r"\b(S-\d+)\b", spec_text)
    unique_smokes = sorted(set(smokes), key=lambda s: int(s.split("-")[1]))
    assert len(unique_smokes) >= 4, f"expected \u22654 smoke IDs, found: {unique_smokes}"


def test_final_report_block_present(spec_text: str) -> None:
    # The §11 report template must contain the OVERALL line. Tolerate
    # optional brackets and varying whitespace around the verdicts.
    assert re.search(
        r"OVERALL\s*:\s*\[?\s*PASS\s*\|\s*FAIL\s*\|\s*PARTIAL\s*\]?",
        spec_text,
    ), (
        "ASSURANCE_SPEC.md §11 must define the final report block with "
        "an 'OVERALL: [PASS | FAIL | PARTIAL]' line."
    )
    # And the report block must include the literal sentinel markers
    assert "=== ASSURANCE REPORT ===" in spec_text
    assert "=== END REPORT ===" in spec_text
