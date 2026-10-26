#!/usr/bin/env bash
# Replays only fictional data in the named synthetic member HOME.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ -e /tmp/aios-member-sandbox ]; then
  mv /tmp/aios-member-sandbox "/tmp/aios-member-sandbox-before-video-$(date +%s)"
fi
mkdir -p /tmp/aios-member-sandbox
export HOME=/tmp/aios-member-sandbox
export CLAUDE_CONFIG_DIR="$HOME/.claude"
export CODEX_HOME="$HOME/.codex"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
unset AIOS_BRAIN_TURSO_URL AIOS_BRAIN_TURSO_TOKEN SUPADATA_API_KEY
export PATH="$HOME/.local/bin:$PATH"
python3 video/build_tapes_v1.py
for tape in video/tapes/*_v1.tape; do
  case "$tape" in
    *10_read-memory*)
      BRAIN_DEMO_REF="$(brain search 'Lighthouse budget' | python3 -c 'import json,sys; print(json.load(sys.stdin)["hits"][0]["ref"])')"
      python3 video/build_tapes_v1.py --ref "$BRAIN_DEMO_REF"
      ;;
  esac
  vhs "$tape"
done
python3 video/check_clips_v1.py
