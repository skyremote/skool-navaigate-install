#!/usr/bin/env bash
# Release prep: tag every plugin whose plugin.json version has no <name>--v<version> tag yet.
# Run by the chief of staff at release, from a clean checkout of the release commit:
#   scripts/release_tags.sh --dry-run    show what would be tagged
#   scripts/release_tags.sh              create the tags locally
#   scripts/release_tags.sh --push       create them and push each to origin
# Version ranges such as "^2.0" in a pack's dependencies resolve against these tags.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE="${CLAUDE_BIN:-claude}"
FLAGS=()
for arg in "$@"; do
  case "$arg" in
    --dry-run|--push) FLAGS+=("$arg") ;;
    *) echo "Unknown option: $arg (use --dry-run or --push)" >&2; exit 2 ;;
  esac
done
python3 "$ROOT/scripts/build_catalogue.py" --check
remote_tags="$(git -C "$ROOT" ls-remote --tags origin 2>/dev/null | sed 's#.*refs/tags/##; s#\^{}$##' || true)"
tagged=0; skipped=0
for manifest in "$ROOT/.claude-plugin/plugin.json" "$ROOT"/plugins/*/.claude-plugin/plugin.json; do
  [ -f "$manifest" ] || continue
  dir="$(dirname "$(dirname "$manifest")")"
  read -r name version < <(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["name"], d["version"])' "$manifest")
  tag="${name}--v${version}"
  if git -C "$ROOT" rev-parse -q --verify "refs/tags/$tag" >/dev/null || grep -qxF "$tag" <<<"$remote_tags"; then
    echo "skip $tag (already tagged)"; skipped=$((skipped+1)); continue
  fi
  echo "tag  $tag"
  (cd "$dir" && "$CLAUDE" plugin tag ${FLAGS[@]+"${FLAGS[@]}"} .)
  tagged=$((tagged+1))
done
echo "Tagged $tagged, skipped $skipped."
