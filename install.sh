#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [ "$#" -eq 0 ]; then
  exec bash "$ROOT/scripts/install_v1.sh"
fi
exec python3 "$ROOT/scripts/install_pack.py" "$@"
