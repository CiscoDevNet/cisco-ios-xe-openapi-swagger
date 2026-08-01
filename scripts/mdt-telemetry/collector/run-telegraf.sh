#!/usr/bin/env bash
# Start Telegraf as a local Cisco MDT gRPC dial-out receiver on THIS host.
#
#   ./run-telegraf.sh            # start in background (container: mdt-telegraf)
#   ./run-telegraf.sh --stop     # stop and remove the container
#
# Point a device subscription's receiver at <this-host-ip>:57500 (grpc-tcp).
# Decoded payloads land in ./output/mdt-live.json (gitignored).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="telegraf:latest"
NAME="mdt-telegraf"
PORT="57500"

if [[ "${1:-}" == "--stop" ]]; then
  docker rm -f "$NAME" >/dev/null 2>&1 && echo "stopped $NAME" || echo "$NAME not running"
  exit 0
fi

mkdir -p "$HERE/output"
docker pull -q "$IMAGE" >/dev/null
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" \
  -p "${PORT}:${PORT}" \
  -v "$HERE/telegraf-mdt.conf:/etc/telegraf/telegraf.conf:ro" \
  -v "$HERE/output:/output" \
  "$IMAGE" >/dev/null

echo "Telegraf listening on 0.0.0.0:${PORT}  (container: $NAME)"
echo "Captured payloads -> $HERE/output/mdt-live.json"
