#!/usr/bin/env bash
PY=../../../.venv-harness/bin/python
for pid in C9200 C9300-24UX C9500 C9600 C9800; do
  echo "=== $(date +%H:%M:%S) $pid ==="
  $PY gnmi_subscribe.py --device "$pid" 2>&1 | tail -4
  sleep 12
done
echo "=== ALL DONE $(date +%H:%M:%S) ==="
