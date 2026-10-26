"""List personal and project skills by what their listing costs on every turn.

This is the static half of the picture. /skill-doctor adds the usage half
(which skills were never invoked). Use both before you hide anything.
"""
import json
from pathlib import Path

from .frontmatter import split
from .hide import settings_path


def overrides(home, cwd):
    merged = {}
    for scope in ('user', 'project', 'local'):
        path = settings_path(scope, home, cwd)
        try:
            data = json.loads(path.read_text()) if path.exists() else {}
        except (ValueError, OSError):
            continue
        if isinstance(data, dict) and isinstance(data.get('skillOverrides'), dict):
            merged.update(data['skillOverrides'])
    return merged


def collect(home=None, cwd=None):
    home, cwd = Path(home or Path.home()), Path(cwd or Path.cwd())
    states = overrides(home, cwd)
    rows, seen = [], set()
    for where, root in (('personal', home / '.claude' / 'skills'), ('project', cwd / '.claude' / 'skills')):
        if not root.is_dir() or root.resolve() in seen:
            continue
        seen.add(root.resolve())
        for skill in sorted(root.glob('*/SKILL.md')):
            meta, body, _ = split(skill.read_text(errors='replace'))
            name = meta.get('name', skill.parent.name)
            text = name + meta.get('description', '') + meta.get('when_to_use', '')
            state = states.get(name, 'on')
            listed = len(text) if state == 'on' else len(name) if state == 'name-only' else 0
            rows.append({'skill': name, 'where': where, 'state': state, 'listing_chars': listed,
                         'tokens_estimate': (listed + 3) // 4, 'body_lines': len(body.splitlines())})
    rows.sort(key=lambda row: -row['listing_chars'])
    return rows


def format_rows(rows, top=20):
    if not rows:
        return 'No personal or project skills found in ~/.claude/skills or .claude/skills.'
    total = sum(row['tokens_estimate'] for row in rows)
    lines = ['%-32s %-9s %-20s %7s' % ('skill', 'where', 'state', 'tokens')]
    for row in rows[:top]:
        lines.append('%-32s %-9s %-20s %7d' % (row['skill'][:32], row['where'], row['state'], row['tokens_estimate']))
    if len(rows) > top:
        lines.append('... %d more' % (len(rows) - top))
    lines.append('Total listing: about %d tokens on every turn, across %d skills.' % (total, len(rows)))
    lines.append('Next: run /skill-doctor to see which of these you never use, then hide those first.')
    return '\n'.join(lines)
