#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DESTS=(
  "$HOME/.claude/skills"
  "$HOME/.cursor/skills"
  "$HOME/.codex/skills"
  "$HOME/.agents/skills"
)
for dest in "${DESTS[@]}"; do
  mkdir -p "$dest"
  for skill in "$ROOT"/skills/*; do
    [ -d "$skill" ] || continue
    name="$(basename "$skill")"
    ln -sfn "$skill" "$dest/$name"
    echo "linked $name -> $dest/$name"
  done
done
echo
echo "Restart Claude Code, Cursor, or Codex, then type /aios"
