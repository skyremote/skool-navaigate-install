#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
START_STEP="${1:-01}"
if [[ ! "$START_STEP" =~ ^(0[1-9]|1[0-5])$ ]]; then
  echo "Use a two-digit starting step, 01 to 15" >&2
  exit 1
fi
if [ "$START_STEP" = 01 ]; then
python3 video/prepare_checkout_v2.py
if [ -e /tmp/aios-member-sandbox ]; then
  mv /tmp/aios-member-sandbox "/tmp/aios-member-sandbox-before-video-$(date +%s)"
fi
mkdir -p /tmp/aios-member-sandbox
fi
export HOME=/tmp/aios-member-sandbox
export CLAUDE_CONFIG_DIR="$HOME/.claude"
export CODEX_HOME="$HOME/.codex"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
export TMPDIR=/tmp
unset AIOS_BRAIN_TURSO_URL AIOS_BRAIN_TURSO_TOKEN SUPADATA_API_KEY
export PATH="$HOME/.local/bin:$PATH"
BRAIN_DEMO_REF=''
if [ "$START_STEP" -gt 10 ]; then
  BRAIN_DEMO_REF="$("$HOME/.local/bin/brain" search 'Lighthouse budget' | python3 -c 'import json,sys; print(json.load(sys.stdin)["hits"][0]["ref"])')"
fi
HEALTH_PAGES=3
INVENTORY_PAGES=5
python3 video/build_tapes_v2.py
for tape in video/tapes/*_v2.tape; do
  STEP_NAME="$(basename "$tape")"
  if [[ "${STEP_NAME:0:2}" < "$START_STEP" ]]; then continue; fi
  case "$tape" in
    *10_read-memory*)
      BRAIN_DEMO_REF="$("$HOME/.local/bin/brain" search 'Lighthouse budget' | python3 -c 'import json,sys; print(json.load(sys.stdin)["hits"][0]["ref"])')"
      ;;
    *11_check-health*)
      HEALTH_PAGES="$("$HOME/.local/bin/brain" status | python3 -c 'import math,sys; n=sum(max(1,math.ceil(len(s.rstrip())/100)) for s in sys.stdin); print(max(1,math.ceil(n/22)))')"
      ;;
    *15_check-all-harnesses*)
      INVENTORY_PAGES="$(python3 /tmp/aios-video-checkout-v2/plugins/aios/scripts/status.py | python3 -c 'import math,sys; n=sum(max(1,math.ceil(len(s.rstrip())/100)) for s in sys.stdin); print(max(1,math.ceil(n/22)))')"
      ;;
  esac
  python3 video/build_tapes_v2.py --ref "$BRAIN_DEMO_REF" --health-pages "$HEALTH_PAGES" --inventory-pages "$INVENTORY_PAGES"
  RECORD_LOG="/tmp/aios-vhs-${STEP_NAME}.log"
  if vhs "$tape" > "$RECORD_LOG" 2>&1; then
    cat "$RECORD_LOG"
  elif rg -q 'could not start browser' "$RECORD_LOG"; then
    # A failed browser boot has not executed any tape command. Retry once.
    cat "$RECORD_LOG"
    vhs "$tape"
  else
    cat "$RECORD_LOG"
    exit 1
  fi
done
python3 video/check_clips_v2.py
python3 video/extract_screens_v2.py
python3 video/build_shotlist_v2.py
