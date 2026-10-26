"""Portable proof output: never commit the producing Mac's absolute paths."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
# Build evidence stays out of git (course content and proof live with the Skool course).
EVIDENCE=ROOT/'.evidence'
EVIDENCE.mkdir(exist_ok=True)


def portable(text):
    text=str(text).replace(str(ROOT),'<worktree>')
    text=text.replace(str(ROOT.resolve()),'<worktree>')
    text=re.sub(r'/Users/[^/\s"\'\\]+','$HOME',text)
    return '\n'.join(line.rstrip() for line in text.splitlines())
