"""Create a new skill with its three eval cases, ready for claude plugin eval.

The layout is a skills-directory plugin, the same shape `claude plugin init`
writes: SKILL.md at the root, a manifest that points at it, and an evals/ suite.
"""
import json
import os
from pathlib import Path

from .check import MAX_DESCRIPTION_CHARS, MAX_SENTENCES, NAME
from .frontmatter import sentences

SKILL = """---
name: {name}
description: {description}
---

# {title}

## When to use
TODO: one line on the job this skill does, and one line on when it should stay quiet.

## Steps
1. TODO: the first thing Claude does.
2. TODO: the next step. Name exact commands and file paths.
3. TODO: the check that proves the job is done (a test, a file, a count).

## Never
- TODO: the one mistake this skill exists to prevent.

## Finish
Show the result of the check, then one next action.
"""

FIRED = """---
type: tool_used
tool: Skill
input_match: '"skill"\\s*:\\s*"(?:[\\w-]+:)?{name}"'
---
"""

NOT_FIRED = """---
type: tool_used
tool: Skill
input_match: '"skill"\\s*:\\s*"(?:[\\w-]+:)?{name}"'
min: 0
max: 0
arm: both
---
"""

RESULT = """---
type: llm
---

TODO: PASS if the reply contains <the concrete thing a good answer has>.
FAIL if <what a wrong or missing answer looks like>.
"""

PROMPT = """---
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

TODO: {hint}
"""

CASES = {
    'should-fire': ('a request a member would type that this skill must handle. Do not name the skill.',
                    {'skill-fired.md': FIRED, 'result.md': RESULT}),
    'edge-case': ('a harder version of the same request: missing details, an awkward input, or a trap.',
                  {'skill-fired.md': FIRED, 'result.md': RESULT}),
    'should-not-fire': ('a nearby request this skill must NOT handle, so you know it stays quiet.',
                        {'skill-quiet.md': NOT_FIRED}),
}


class ScaffoldError(ValueError):
    pass


def validate(name, description):
    if not NAME.match(name or ''):
        raise ScaffoldError('Use a name of lowercase letters, digits and hyphens, for example weekly-report')
    description = ' '.join((description or '').split())
    if not description:
        raise ScaffoldError('Give a description: what the skill does and when to use it, in one or two sentences')
    if len(description) > MAX_DESCRIPTION_CHARS:
        raise ScaffoldError('The description is %d characters; keep it under %d' % (len(description), MAX_DESCRIPTION_CHARS))
    if sentences(description) > MAX_SENTENCES:
        raise ScaffoldError('The description has more than two sentences; cut it to one or two')
    if '\n' in description or ': ' in description or description.startswith(('-', '[', '{', '>', '|', '#')):
        description = json.dumps(description)
    return description


def default_root(project=False, home=None):
    if project:
        return Path.cwd() / '.claude' / 'skills'
    return Path(home or Path.home()) / '.claude' / 'skills'


def create(name, description, root=None, project=False, author=None):
    """Write the skill. Never overwrites: an existing folder stops the run."""
    safe_description = validate(name, description)
    root = Path(root).expanduser() if root else default_root(project)
    target = root / name
    if target.exists():
        raise ScaffoldError('%s already exists; choose another name or edit it directly' % target)
    files = {
        'SKILL.md': SKILL.format(name=name, description=safe_description, title=name.replace('-', ' ').capitalize()),
        '.claude-plugin/plugin.json': json.dumps({
            'name': name,
            'version': '0.1.0',
            'description': ' '.join(description.split()),
            'author': {'name': author or os.environ.get('USER', 'you')},
            'skills': ['./'],
        }, indent=2) + '\n',
        'evals/.gitignore': 'results/\n',
    }
    for case, (hint, graders) in CASES.items():
        files['evals/%s/prompt.md' % case] = PROMPT.format(hint=hint)
        for grader, template in graders.items():
            files['evals/%s/graders/%s' % (case, grader)] = template.format(name=name)
    for relative, content in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return target, sorted(files)
