---
name: Spec or YANG accuracy issue
about: A generated OpenAPI spec doesn't match the YANG model or doesn't work on a real device
title: "[spec] "
labels: spec-accuracy
assignees: ''
---

<!--
Use this template when the issue is the *content* of a spec (wrong path,
wrong type, missing operation, example doesn't validate on a real device)
rather than a UI bug. If the underlying YANG model itself is wrong, please
file upstream at https://github.com/YangModels/yang instead.
-->

### Affected spec

- Release: <!-- e.g. 26.1.1 -->
- Category: <!-- oper / native-config / openconfig / ietf / mib / rpc / events / cfg / other -->
- YANG module: <!-- e.g. Cisco-IOS-XE-bgp-oper -->
- Path / operation: <!-- e.g. GET /restconf/data/bgp-oper-data/bgp-state-data -->
- Permalink (Copy Share Link from the spec viewer): <!-- paste here -->


### What's wrong?

<!-- Wrong path, wrong type, missing field, broken example body, 400/404 on device, etc. -->


### Expected behaviour

<!-- What the spec should say or what the device actually returns. -->


### Device evidence (highly valued)

<!--
If you tested this on a real IOS-XE device, paste the request + response.
Redact hostnames / IPs / secrets. `scripts/validate_examples_c9kv.py` output
also works great here.
-->

```http

```


### Environment

- Device platform: <!-- e.g. Catalyst 9300, ASR 1001-X, CSR1000v, sandbox -->
- Device IOS-XE version: <!-- output of `show version | i Cisco IOS XE` -->


### Anything else?

<!-- Related modules, deviations, links to upstream YANG issues, etc. -->
