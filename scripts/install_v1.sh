#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
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
        "$ROOT"/plugins/*) echo "skip existing 2.0 link $dest/$name"; continue ;;
        "$ROOT"*) ;;
        *) echo "skip house link $dest/$name -> $target"; continue ;;
      esac
    fi
    ln -sfn "$skill" "$dest/$name"
    echo "linked $name -> $dest/$name"
  done
done
# prompt-stack: the /stack skill finds its CLI two folders above the skill
# folder, so link bin/prompt-stack into ~/.claude/bin (and the other harnesses).
# The link resolves back into this repo, so lib/ and stack.json are found.
for dest in "${DESTS[@]}"; do
  bindir="$(dirname "$dest")/bin"
  mkdir -p "$bindir"
  if [ -e "$bindir/prompt-stack" ] && [ ! -L "$bindir/prompt-stack" ]; then
    echo "skip existing $bindir/prompt-stack"
    continue
  fi
  ln -sfn "$ROOT/bin/prompt-stack" "$bindir/prompt-stack"
  echo "linked prompt-stack -> $bindir/prompt-stack"
done

# prompt-stack: register the UserPromptSubmit hook in Claude Code settings.
# Merges into any existing hooks, backs the file up first, and is safe to rerun.
python3 - "$ROOT" <<'PY'
import json, os, shutil, sys, time
root = sys.argv[1]
path = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
cmd = 'python3 "%s/hooks/inject.py"' % root
data = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if raw.strip():
        try:
            data = json.loads(raw)
        except ValueError:
            sys.exit("settings.json is not valid JSON, so the prompt-stack hook was not added. Fix it and rerun ./install.sh")
    if not isinstance(data, dict):
        sys.exit("settings.json is not a JSON object, so the prompt-stack hook was not added.")
groups = data.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
state = "new"
for g in groups:
    for h in g.get("hooks", []):
        c = h.get("command", "")
        if c == cmd:
            state = "same"
        elif "hooks/inject.py" in c and "prompt-stack" not in c and state == "new" and c.startswith("python3") and root.split("/")[-1] in c:
            h["command"] = cmd  # this repo moved: repoint
            state = "moved"
if state == "same":
    print("prompt-stack hook already registered")
else:
    if state == "new":
        groups.append({"hooks": [{"type": "command", "command": cmd, "timeout": 5}]})
    if os.path.exists(path):
        bak = path + ".bak-" + time.strftime("%Y%m%d-%H%M%S")
        shutil.copy2(path, bak)
        print("backed up settings.json -> " + bak)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)
    print("prompt-stack hook " + ("repointed" if state == "moved" else "registered") + " in " + path)
PY

echo
echo "Restart Claude Code, Cursor, or Codex, then type /aios"
