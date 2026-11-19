"""Device Data short links: every path on every method/device round-trips through its short code."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DATASETS = {
    "mdt": "telemetry-live-data.json", "restconf": "restconf-live-data.json",
    "netconf-get": "netconf-get-live-data.json", "netconf-getconfig": "netconf-getconfig-live-data.json",
    "netconf-sub": "netconf-sub-live-data.json", "netconf-sub-config": "netconf-sub-config-live-data.json",
    "gnmi-get": "gnmi-get-live-data.json", "gnmi-getconfig": "gnmi-getconfig-live-data.json",
    "gnmi-state": "gnmi-state-live-data.json", "gnmi-sub": "gnmi-sub-live-data.json",
}

# Loads device-data.js with a DOM stub (init never runs) and checks the exported link helpers.
NODE_CHECK = r"""
const fs = require('fs'); const vm = require('vm');
const [script, datasetsJson] = process.argv.slice(1);
const context = { window: {}, document: { readyState: 'loading', addEventListener() {} }, location: {}, history: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync(script, 'utf8'), context);
const links = context.window.__DeviceDataLinks;
const failures = []; let checked = 0;
for (const [method, file] of Object.entries(JSON.parse(datasetsJson))) {
  if (!fs.existsSync(file)) continue;
  if (links.methodFromAlias(links.SHORT_METHODS[method]) !== method) failures.push(['alias', method]);
  const paths = JSON.parse(fs.readFileSync(file, 'utf8')).paths;
  for (const row of paths) {
    const code = links.shortCode(paths, row.path);
    const back = links.resolveShort(paths, row.pid, code);
    checked++;
    if (back !== row.path) failures.push([method, row.pid, row.path, code, back]);
  }
}
console.log(JSON.stringify({ checked, failures: failures.slice(0, 10), failureCount: failures.length }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_short_codes_round_trip_on_every_dataset():
    datasets = {method: str(REPO / name) for method, name in DATASETS.items()}
    result = subprocess.run(["node", "-e", NODE_CHECK, str(REPO / "device-data.js"), json.dumps(datasets)],
                            capture_output=True, text=True, check=True, timeout=600)
    report = json.loads(result.stdout.strip().splitlines()[-1])
    assert report["checked"] > 1000
    assert report["failureCount"] == 0, report["failures"]


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_short_code_is_readable_and_minimal():
    sample = [
        {"pid": "C9500", "path": "/oc-if:interfaces"},
        {"pid": "C9500", "path": "/oc-if:interfaces/interface/state/counters"},
        {"pid": "C9500", "path": "/oc-if:interfaces/interface/subinterfaces/subinterface/state/counters"},
        {"pid": "C9500", "path": "/interfaces-ios-xe-oper:interfaces"},
    ]
    script = NODE_CHECK.split("const failures")[0] + (
        "const paths = %s;\n"
        "console.log(JSON.stringify(paths.map(p => links.shortCode(paths, p.path))));\n" % json.dumps(sample))
    result = subprocess.run(["node", "-e", script, str(REPO / "device-data.js"), "{}"],
                            capture_output=True, text=True, check=True, timeout=60)
    codes = json.loads(result.stdout.strip().splitlines()[-1])
    assert codes == [
        "oc-if:interfaces",
        "oc-if:interface/state/counters",
        "oc-if:subinterface/state/counters",
        "interfaces-ios-xe-oper:interfaces",
    ]
