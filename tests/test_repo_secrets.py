"""Guard: no secret material in any tracked text file (GitGuardian incident 3498322).

tests/test_dataset_secrets.py checks the published device datasets field by field; this
test covers everything else that is tracked (docs, scripts, tests, HTML reports, data
files): Cisco crypt hashes, private keys, CLI secrets with an encryption type, and any
value that leaked before (stored only as SHA-256, so this file holds no secret).

Fixtures that need a secret-looking value must include ``FAKE`` in it.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "mdt-telemetry" / "collector"))

import redact_payload as rp  # noqa: E402

# Generated from public YANG / third-party code; never carry device data.
SKIP = re.compile(
    r"^(releases/[^/]+/swagger-[a-z-]+-model/api/|releases/[^/]+/yang-trees/|releases/[^/]+/deprecations/"
    r"|yang-trees/|references/|assets/vendor/|archive/)"
    r"|\.(png|jpe?g|gif|ico|svg|woff2?|ttf|zip|gz|tar|pdf|xlsx?)$")
PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----(.*?)-----END [A-Z ]*PRIVATE KEY-----", re.S)
TOKEN = re.compile(r"[^\s\"'<>,;(){}\[\]\\`]+")

# SHA-256 of values that leaked before the 2026-11-21 cleanup (all rotated). A match
# means a real credential was pasted back into the repo.
LEAKED_SHA256: set[str] = {
    "04fee1860a4e36fae5582c715ce6d81cc15a87de0df3b5b04373af7aa7e32e59",
    "31198006d159fc35ec1c34c32249776b1cdc32e86617a53a4ad1295bc0533282",
    "33e4502b1275f450003aaf9f1b9c707e036baffb2d9130046e7ab646efe1ba04",
    "36052cf022cb30713f0dac923f1f461fb59100ed45a26dc26654133ab88d4d55",
    "41080fabbc9a020ae3973f59324055bd2b98c3d6f6e62f4ae78c4fcdbe8a9a61",
    "44973dc2151470f3b26f2fae8c88fdce261f9d1082baff4f3c756398d9c8ac0d",
    "4cd1e75730e3d205ab221b1166df9fd7c4e004d68d9ff2d796ccefb4527ec100",
    "506af96ed2632c57a307288057ff381b8fc18aceebab70558e5aa702ef189104",
    "5ad697351a4c9b1355b5606833bbd7510b5c80a0e5cf7536de909c94a250c79f",
    "5c461ebb3a59e9a43a1995edc22577d226d5245f5b064355b6acfef898b94747",
    "75958b5c5ad015b2036889bd516bb347483fc994c35d4be708bd4857104df8e5",
    "7b61f6bbf72d7f179f928e593960024ce810b3638fba5ba583b3b890eb3c4214",
    "7e12d7bebcabd87f0beb73ed63105bc82a60c3f79967cde327909185348d1dbd",
    "7f571c3f7225d1e973a0e44ad2305e520740aaa0df57d3e07b5c781ddcef44e5",
    "7fb0d8dd61d6cb22702a663604819edadf69c985bd203877d971dbe2b465ce4b",
    "81e7de13d51f5c12f31031ca39f3965d322ba0e62a0dbd81b5e4648b6e1dedbd",
    "83286212c10f1284d2bb1befd05388fd47be1ff304c3aa05e4104832a16f1ba7",
    "85ec85418e9410e7e613ec98aae6db4defc158e9a129755ec06cc98b7bade648",
    "a4d47904a22f2bde593ddc3e314e6c1c483c1dc41e38b6d13d641c2e872f2572",
    "a72aa1254ebb37fbf30eb02a7c7c20f9b53d965d87c29cc6963b016840b6f675",
    "aa6e8c34580f31720effd9c5306492f1e27ca603c02035061596fad6736cdf7a",
    "bc0c6c1bca4d964cecf14c9bcf26f70b801b3d03d260eaf8ae118025c281ae36",
    "beafea0ead5dcde5a3fe50a9f3a4cba7e2bc8be2a34c3439e18f151cdfec9743",
    "c525bf833a2ef85514db50b76761db70b37737083bb557ace89f9f48cfbe9f6c",
    "c79eb1ca1dfab2bf7f08347b2e87d461d62435e2941c3d42c0551d55c35e6a2c",
    "d67d5652fab2182040a4fcb2877cbfca07ede42a4406d3ba0d46a880dc11c036",
    "e0964b5fb7f335482fa39ce2ec77799fd1c29c26f1fd524265d0196cb085f007",
    "e7ac4f1c18972dfa65b3f1074a02ba9533c6bc117369e7b7594bfeb3470a4dfc",
    "e85fe94de5636a8dc072784c804c0bb991f6194f5634c7fb1fd6366bc67d330b",
    "eb6086774df8573818fb74dc47ccd06c91885bb380c4867b693c85b34e809de6",
    "efca12869a209687583bef664c480b9016dfeafe337226de9f90174522b1b5ff",
    "f202a197096bc352dc99c95cda76b91f08c04a19c9a9877d7aa7dcefec15072a",
    "fb5a06135ed1734229c7292500ce28dc51c4fe72e629583330d5ec5a47d3a02a",
    "ff4781f427a3370c0f57c9dc55542984437a96686fffcf985f508cddc9b7ce8a",
}
LEAKED_LENGTHS = {32, 34, 8, 10, 11, 12, 13, 14, 15, 16, 61}


def _tracked_text_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True).stdout
    for rel in out.decode("utf-8", "replace").split("\0"):
        if not rel or SKIP.search(rel):
            continue
        path = REPO / rel
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b"\0" in data[:4096]:
            continue
        yield rel, data.decode("utf-8", "replace")


def _findings(rel: str, text: str) -> list[str]:
    problems = []
    for m in rp.CRYPT.finditer(text):
        if not rp._placeholder(m.group(0)[3:]):
            problems.append(f"{rel}: crypt hash at offset {m.start()}")
    for m in PRIVATE_KEY.finditer(text):
        if "fake" not in m.group(1).lower() and len(m.group(1).strip()) > 40:
            problems.append(f"{rel}: private key block at offset {m.start()}")
    for n, line in enumerate(text.split("\n"), 1):
        for m in rp._TYPED_CLI_SECRET.finditer(line):
            if not rp._placeholder(m.group(1)) and m.group(1) != rp.REDACTED:
                problems.append(f"{rel}:{n}: CLI secret with encryption type")
    if LEAKED_SHA256:
        for m in TOKEN.finditer(text):
            tok = m.group(0)
            for cand in {tok, tok.strip(".:!?"), tok.split("=")[-1]}:
                if len(cand) in LEAKED_LENGTHS and hashlib.sha256(cand.encode()).hexdigest() in LEAKED_SHA256:
                    problems.append(f"{rel}: previously leaked value at offset {m.start()}")
    return problems


def test_no_secret_material_in_tracked_files():
    problems = []
    for rel, text in _tracked_text_files():
        problems.extend(_findings(rel, text))
    assert not problems, f"{len(problems)} secret finding(s): {problems[:10]}"


def test_scanner_catches_each_secret_class():
    hash9 = "$9$" + "ABCDEFGHijklmn/opq.RSTUV"
    typed = "tacacs-server key 7 " + "104D0A1B2C3D"
    key = "-----BEGIN RSA PRIVATE KEY-----\n" + "M" * 64 + "\n-----END RSA PRIVATE KEY-----"
    found = _findings("x", "\n".join([f"enable secret 9 {hash9}", typed, key]))
    assert len(found) >= 3
    assert not _findings("x", "enable secret 9 <hash>\nusername u password 7 FAKE0822\nkey 7 ***REDACTED***")
