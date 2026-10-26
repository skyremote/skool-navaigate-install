#!/usr/bin/env bash
# YOUR AIOS 2.0: the AIOS step for bb. Run it after BB Overlay (github.com/skyremote/bb-overlay), which gives bb
# the NavAIgate look, Kanban, to-dos and the mods. This step adds the course:
#   1. the AIOS start pack for Claude Code (and for Codex, when Codex is installed);
#   2. a bb project for the member's AIOS folder (or keeps the one that exists);
#   3. the prompt library: the "AIOS course" page in the bb sidebar, and every prompt saved in
#      bb's built-in Prompt Library (Ctrl+R in any chat box).
# It never installs, changes or removes BB Overlay. If BB Overlay is missing, it says so and gives its one line.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/skyremote/skool-navaigate-install/main/bb-kit/install.sh | bash
#   bash install.sh [--folder <path>] [--name <project name>] [--all] [--ref <git ref>] [--dry-run]
#
#   --folder   your AIOS folder (default: ~/AIOS). Created if missing; existing files are never touched.
#   --name     the bb project name, used only when the folder has no bb project yet (default: "My AIOS").
#   --all      also install every core pack now (aios-complete), instead of one pack per module.
#   --ref      the branch or tag of this repository to install from (default: main).
#   --dry-run  print what would happen and change nothing.
# Safe to re-run: every step checks first and keeps what is already there.
set -euo pipefail

REPO_SLUG="skyremote/skool-navaigate-install"
REPO_URL="https://github.com/$REPO_SLUG.git"
OVERLAY_LINE="curl -fsSL https://raw.githubusercontent.com/skyremote/bb-overlay/main/install.sh | bash"
MARKET="navaigate-aios"

FOLDER="$HOME/AIOS"; NAME="My AIOS"; ALL=0; REF="main"; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --folder) FOLDER="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    --all) ALL=1; shift;;
    --ref) REF="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    -h|--help) sed -n '2,20p' "$0"; exit 0;;
    *) echo "Unknown option: $1 (try --help)" >&2; exit 2;;
  esac
done
FOLDER="${FOLDER/#\~/$HOME}"

OK=(); SKIPPED=(); FAILED=()
say()  { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
run()  { if [ $DRY = 1 ]; then say "  [dry run] $*"; return 0; fi; "$@"; }
ok()   { OK+=("$1"); say "  OK   $1"; }
skip() { SKIPPED+=("$1"); say "  SKIP $1"; }
fail() { FAILED+=("$1"); say "  FAIL $1"; }

step "Checking the tools"
BB="$(command -v bb || true)"
BUNDLED="/Applications/bb.app/Contents/Resources/app.asar.unpacked/node_modules/bb-app/host-daemon/dist/bb"
if [ -z "$BB" ] && [ -x "$BUNDLED" ]; then BB="$BUNDLED"; fi
[ -n "$BB" ] || { say "bb is not installed. Install it from https://getbb.app, open it once, then run this again."; exit 1; }
"$BB" status >/dev/null 2>&1 || { say "bb is installed but not running. Open the bb app, then run this again."; exit 1; }
say "  bb      $("$BB" --version 2>/dev/null | head -1)"
command -v claude >/dev/null || { say "Claude Code is not installed. Install it from https://claude.com/claude-code, sign in once, then run this again."; exit 1; }
say "  claude  $(claude --version 2>/dev/null | head -1)"
command -v git >/dev/null || { say "git is missing. On a Mac run: xcode-select --install"; exit 1; }
command -v python3 >/dev/null || { say "python3 is missing. On a Mac run: xcode-select --install"; exit 1; }
CODEX="$(command -v codex || true)"
[ -n "$CODEX" ] && say "  codex   found" || say "  codex   not installed (fine: the kit sets up Claude Code; add Codex later)"

step "Your AIOS folder"
if [ -d "$FOLDER" ]; then say "  Keeping $FOLDER (nothing inside is changed)"; else run mkdir -p "$FOLDER"; say "  Created $FOLDER"; fi
ok "AIOS folder: $FOLDER"

step "The AIOS packs for Claude Code"
if claude plugin marketplace list 2>/dev/null | grep -q "$MARKET"; then
  say "  The $MARKET marketplace is already added"
else
  run claude plugin marketplace add "$REPO_SLUG" && say "  Added the $MARKET marketplace"
fi
PACK="aios"; [ $ALL = 1 ] && PACK="aios-complete"
if run claude plugin install "$PACK@$MARKET"; then ok "Claude Code: $PACK installed"; else fail "Claude Code: $PACK did not install"; fi

if [ -n "$CODEX" ]; then
  step "The AIOS start pack for Codex"
  KIT="$HOME/.local/share/aios/kit"
  if [ -d "$KIT/.git" ]; then run git -C "$KIT" pull --ff-only -q || true; else run mkdir -p "$(dirname "$KIT")"; run git clone -q --depth 1 --branch "$REF" "$REPO_URL" "$KIT"; fi
  if run bash "$KIT/install.sh" aios; then ok "Codex: aios linked"; else fail "Codex: aios did not link (run $KIT/install.sh aios to see why)"; fi
fi

step "Your bb project"
PROJECT_ID="$("$BB" project list --json 2>/dev/null | python3 -c '
import json, os, sys
folder = os.path.realpath(sys.argv[1])
for p in json.load(sys.stdin):
    for s in p.get("sources", []):
        if s.get("path") and os.path.realpath(s["path"]) == folder:
            print(p["id"]); sys.exit(0)
' "$FOLDER" 2>/dev/null || true)"
if [ -n "$PROJECT_ID" ]; then
  say "  Keeping the bb project for this folder ($PROJECT_ID)"
elif [ $DRY = 1 ]; then
  say "  [dry run] bb project create --name \"$NAME\" --root \"$FOLDER\""
else
  PROJECT_ID="$("$BB" project create --name "$NAME" --root "$FOLDER" --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')"
  say "  Created the bb project \"$NAME\" ($PROJECT_ID)"
fi
ok "bb project: $NAME"

step "The prompt library"
installed() { "$BB" plugin list 2>/dev/null | grep -q "^$1@"; }
if installed aios-starter; then
  say "  AIOS Starter is already installed (update it with: bb plugin update aios-starter)"
else
  run "$BB" plugin install "git:$REPO_URL@$REF" --subdirectory bb-kit/plugin --yes
fi
if [ -n "$PROJECT_ID" ]; then run "$BB" plugin config aios-starter set projectId "$PROJECT_ID" >/dev/null || true; fi
installed aios-starter && ok "AIOS course page in the bb sidebar" || { [ $DRY = 1 ] || fail "AIOS Starter plugin did not install"; }
run "$BB" plugin enable bb--prompt-library >/dev/null 2>&1 || true
if [ $DRY = 1 ]; then say "  [dry run] bb aios-kit star"
elif "$BB" aios-kit star; then ok "Every prompt saved in the Prompt Library (Ctrl+R)"
else skip "Prompt Library: run 'bb aios-kit star' once bb has reloaded"; fi

step "BB Overlay"
if installed navaigate-workspace; then
  ok "BB Overlay is installed"
else
  skip "BB Overlay is not installed. It gives bb the NavAIgate look, Kanban, to-dos and the mods. Install it with: $OVERLAY_LINE"
fi

step "Done"
for x in "${OK[@]}"; do say "  OK   $x"; done
for x in "${SKIPPED[@]+"${SKIPPED[@]}"}"; do say "  SKIP $x"; done
for x in "${FAILED[@]+"${FAILED[@]}"}"; do say "  FAIL $x"; done
say ""
say "Next: open bb, click \"AIOS course\" in the sidebar, open module 1 and press Start chat on prompt 1.1."
say "Or press Ctrl+R in any bb chat box and type AIOS."
[ ${#FAILED[@]} -eq 0 ]
