"""Files that ship-pack writes into a new pack. Placeholders use str.format."""

SKILL = """---
name: {skill}
description: {todo}: one sentence on what this skill does, then "Use for /{skill}, ..." with the words a member would type.
---

# {skill}

{todo}: write the steps the agent follows, one instruction per line.

1. Ask for the one input you need, if it is missing.
2. Do the job.
3. Run a check that proves it worked, and show the real output.

Keep this file under 500 lines. Put long reference material in references/ next to it.
Never ask for a key or token in the chat: secrets belong in the plugin's userConfig with "sensitive": true.
"""

EVAL_CASES = {
    'happy-path': ("""---
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

{todo}: the most common request, written the way a member would type it, without naming the skill.
""", '{todo}-a-word-the-right-answer-always-contains'),
    'edge-case': ("""---
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

{todo}: a request with a missing input or an unusual detail, so the skill must ask or adapt.
""", '{todo}-a-word-the-right-answer-always-contains'),
    'must-refuse': ("""---
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

{todo}: a request the skill must refuse or redirect, for example pasting an API key into the chat.
""", '{todo}-a-word-the-right-answer-always-contains'),
}

REGEX_GRADER = """---
type: regex
pattern: '{pattern}'
flags: i
---
"""

SKILL_GRADER = """---
type: tool_used
tool: Skill
input_match: '"skill"\\s*:\\s*"(?:[\\w-]+:)?{skill}"'
---
"""

README = """# {name}

{description}

## Install

Claude Code:

```
/plugin install {name} --marketplace <your-github-name>/<your-repo>
```

On Claude Code older than 2.1.275, add the marketplace first:

```
/plugin marketplace add <your-github-name>/<your-repo>
/plugin install {name}@<your-marketplace-name>
```

Codex and Cursor, from a clone of the repository:

```
./{name}/install.sh
```

Restart the harness, then type `/{skill}` (in Codex, `${skill}`).

## Prove it

```
python3 -m unittest discover {name}/tests
claude plugin validate {name} --strict
claude plugin eval {name} --runs 1
```
"""

CHANGELOG = """# Changelog

## {version} - {date}

- {note}
"""

CHANGELOG_ENTRY = """## {version} - {date}

- {note}
"""

INSTALL_SH = """#!/bin/sh
# Install {name} for Codex, Cursor and shared agent skills by linking its skills.
# Claude Code installs it from your marketplace instead. Run with --uninstall to remove the links.
# It never replaces a file or folder it did not create.
set -eu
PACK="$(cd "$(dirname "$0")" && pwd)"
MODE="${{1:-install}}"
for parent in "$HOME/.codex/skills" "$HOME/.cursor/skills" "$HOME/.agents/skills"; do
  for skill in "$PACK"/skills/*/; do
    name="$(basename "$skill")"
    dest="$parent/$name"
    if [ "$MODE" = "--uninstall" ]; then
      if [ -L "$dest" ] && [ "$(readlink "$dest")" = "${{skill%/}}" ]; then rm "$dest"; echo "Removed $dest"; fi
      continue
    fi
    if [ -e "$dest" ] || [ -L "$dest" ]; then
      if [ -L "$dest" ] && [ "$(readlink "$dest")" = "${{skill%/}}" ]; then echo "Already linked $dest"; continue; fi
      echo "Stopped: $dest already exists and is not this pack's link. Move it aside yourself." >&2
      exit 1
    fi
    mkdir -p "$parent"
    ln -s "${{skill%/}}" "$dest"
    echo "Linked $dest"
  done
done
if [ -d "$PACK/bin" ]; then
  for tool in "$PACK"/bin/*; do
    dest="$HOME/.local/bin/$(basename "$tool")"
    if [ "$MODE" = "--uninstall" ]; then
      if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$tool" ]; then rm "$dest"; echo "Removed $dest"; fi
      continue
    fi
    if [ -e "$dest" ] && ! {{ [ -L "$dest" ] && [ "$(readlink "$dest")" = "$tool" ]; }}; then
      echo "Stopped: $dest already exists. Move it aside yourself." >&2
      exit 1
    fi
    mkdir -p "$HOME/.local/bin"
    ln -sf "$tool" "$dest"
    echo "Linked $dest"
  done
fi
[ "$MODE" = "--uninstall" ] || echo "Installed {name}. Restart Codex and Cursor."
"""

TEST_PACK = '''"""Structure tests for this pack. Standard library only: python3 -m unittest discover tests"""
import json
import re
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
SECRET = re.compile(r'(sk-[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]{20,}\\.|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16})')


class PackShape(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((PACK / '.claude-plugin/plugin.json').read_text())

    def test_manifest(self):
        self.assertRegex(self.manifest['name'], r'^[a-z0-9][a-z0-9-]+$')
        self.assertRegex(self.manifest['version'], r'^\\d+\\.\\d+\\.\\d+$')
        self.assertTrue(self.manifest.get('description'))

    def test_skills_have_frontmatter_and_stay_short(self):
        skills = list((PACK / 'skills').glob('*/SKILL.md'))
        self.assertTrue(skills)
        for skill in skills:
            text = skill.read_text()
            self.assertTrue(text.startswith('---\\nname: ' + skill.parent.name + '\\n'), skill)
            self.assertIn('\\ndescription: ', text.split('\\n---', 2)[0])
            self.assertLess(len(text.splitlines()), 500, skill)

    def test_three_eval_cases_with_graders(self):
        cases = [p.parent for p in (PACK / 'evals').glob('*/prompt.md')]
        self.assertGreaterEqual(len(cases), 3)
        for case in cases:
            self.assertTrue(list((case / 'graders').glob('*.md')), case)

    def test_secrets_are_sensitive_and_absent(self):
        for key, spec in (self.manifest.get('userConfig') or {}).items():
            if re.search(r'token|secret|password|key', key, re.I):
                self.assertTrue(spec.get('sensitive'), key)
        for path in PACK.rglob('*'):
            if path.is_file() and 'results' not in path.parts:
                try:
                    self.assertIsNone(SECRET.search(path.read_text()), path)
                except UnicodeDecodeError:
                    pass


if __name__ == '__main__':
    unittest.main()
'''
