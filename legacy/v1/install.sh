#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DESTS=(
  "$HOME/.claude/skills"
  "$HOME/.cursor/skills"
  "$HOME/.codex/skills"
  "$HOME/.agents/skills"
)
# Link every community skill. If this machine already has a real house
# copy (directory or a symlink that does not point into this repo), leave it.
# That way members get the full shelf and Daniel's house skills stay put.

for dest in "${DESTS[@]}"; do
  mkdir -p "$dest"
  for skill in "$ROOT"/skills/*; do
    [ -d "$skill" ] || continue
    name="$(basename "$skill")"
    if [ -e "$dest/$name" ] && [ ! -L "$dest/$name" ]; then
      echo "skip existing directory $dest/$name"
      continue
    fi
    if [ -L "$dest/$name" ]; then
      target="$(readlink "$dest/$name")"
      case "$target" in
        "$ROOT"*) ;;
        *) echo "skip house link $dest/$name -> $target"; continue ;;
      esac
    fi
    ln -sfn "$skill" "$dest/$name"
    echo "linked $name -> $dest/$name"
  done
done
echo
echo "Restart Claude Code, Cursor, or Codex, then type /aios"
