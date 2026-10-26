"""Check that a skill earns its place: short description, short body, three evals.

The thresholds follow Anthropic's skill guidance (October 2026): a body under
500 lines, a description that leads with the use case, and at least three eval
cases run against a no-skill baseline.
"""
import json
import re
from pathlib import Path

from .frontmatter import sentences, split

MAX_BODY_LINES = 500
MAX_DESCRIPTION_CHARS = 1024     # hard limit for skills uploaded to claude.ai
WARN_DESCRIPTION_CHARS = 300     # every listed character is paid for on every turn
MAX_SENTENCES = 2
MIN_EVAL_CASES = 3
NAME = re.compile(r'^[a-z0-9][a-z0-9-]{0,63}$')
TODO = re.compile(r'\bTODO:')


def find_skills(path):
    """Return every SKILL.md under a skill folder, a plugin, or a skills folder."""
    path = Path(path).expanduser()
    if path.is_file() and path.name == 'SKILL.md':
        return [path]
    if (path / 'SKILL.md').is_file():
        return [path / 'SKILL.md']
    found = sorted(path.glob('skills/*/SKILL.md')) or sorted(path.glob('*/SKILL.md'))
    return found


def plugin_root(skill_file):
    """The nearest folder above a SKILL.md that has a plugin manifest, if any."""
    for parent in [skill_file.parent] + list(skill_file.parents):
        if (parent / '.claude-plugin' / 'plugin.json').is_file():
            return parent
    return None


def eval_cases(root):
    """Map case name -> (case folder, grader files) for the plugin eval suite."""
    cases = {}
    if root is None:
        return cases
    evals = root / 'evals'
    manifest = root / '.claude-plugin' / 'plugin.json'
    try:
        custom = json.loads(manifest.read_text()).get('experimental', {}).get('evals')
    except (OSError, ValueError, AttributeError):
        custom = None
    if custom:
        evals = root / custom
    if not evals.is_dir():
        return cases
    for marker in sorted(list(evals.rglob('prompt.md')) + list(evals.rglob('case.yaml'))):
        if 'results' in marker.relative_to(evals).parts:
            continue
        case = marker.parent
        cases.setdefault(case.name, (case, sorted((case / 'graders').glob('*.md'))))
    return cases


def grader_types(files):
    kinds = []
    for item in files:
        meta, _, _ = split(item.read_text(errors='replace'))
        kinds.append((item.name, meta.get('type', ''), meta))
    return kinds


def check_skill(skill_file):
    """Return a report dict with errors and warnings for one SKILL.md."""
    text = skill_file.read_text(errors='replace')
    meta, body, _ = split(text)
    folder = skill_file.parent.name
    errors, warnings = [], []
    name = meta.get('name', folder)
    description = meta.get('description', '')
    listing = len(name) + len(description) + len(meta.get('when_to_use', ''))
    body_lines = len(body.splitlines())
    if not meta:
        errors.append('No frontmatter: start the file with --- name/description ---')
    if not NAME.match(name):
        errors.append('Name must be lowercase letters, digits and hyphens, at most 64 characters')
    if not description:
        errors.append('No description: Claude cannot tell when to use this skill')
    elif len(description) > MAX_DESCRIPTION_CHARS:
        errors.append('Description is %d characters; keep it under %d' % (len(description), MAX_DESCRIPTION_CHARS))
    elif len(description) > WARN_DESCRIPTION_CHARS:
        warnings.append('Description is %d characters; aim for under %d' % (len(description), WARN_DESCRIPTION_CHARS))
    count = sentences(description)
    if count > MAX_SENTENCES:
        errors.append('Description has %d sentences; use one or two' % count)
    if body_lines >= MAX_BODY_LINES:
        errors.append('Body is %d lines; move detail into reference files' % body_lines)
    if TODO.search(text):
        errors.append('SKILL.md still contains TODO')
    root = plugin_root(skill_file)
    cases = eval_cases(root)
    fired = not_fired = 0
    for _, graders in cases.values():
        for _, kind, meta_g in grader_types(graders):
            if kind == 'tool_used' and meta_g.get('tool') == 'Skill':
                if meta_g.get('max') == '0':
                    not_fired += 1
                else:
                    fired += 1
    for case, (folder, graders) in cases.items():
        if not graders:
            errors.append('Eval case %s has no graders' % case)
        for item in graders:
            if TODO.search(item.read_text(errors='replace')):
                errors.append('Eval case %s still contains TODO' % case)
                break
        prompt = folder / 'prompt.md'
        if prompt.is_file() and TODO.search(prompt.read_text(errors='replace')):
            errors.append('Eval case %s prompt still contains TODO' % case)
    if root is None:
        warnings.append('No plugin manifest found, so claude plugin eval cannot run this skill yet')
    if len(cases) < MIN_EVAL_CASES:
        errors.append('%d eval cases; write at least %d' % (len(cases), MIN_EVAL_CASES))
    if cases and not fired:
        warnings.append('No eval checks that the skill fired (tool_used: Skill)')
    if cases and not not_fired:
        warnings.append('No eval checks that the skill stays quiet when it should')
    return {
        'skill': name,
        'path': str(skill_file),
        'description_chars': len(description),
        'description_sentences': count,
        'listing_chars': listing,
        'listing_tokens_estimate': (listing + 3) // 4,
        'body_lines': body_lines,
        'eval_cases': sorted(cases),
        'errors': errors,
        'warnings': warnings,
        'ok': not errors,
    }


def format_report(report):
    mark = 'PASS' if report['ok'] else 'FAIL'
    lines = ['%s  %s' % (mark, report['skill']),
             '  description: %d chars, %d sentence(s)' % (report['description_chars'], report['description_sentences']),
             '  listing cost: about %d tokens on every turn' % report['listing_tokens_estimate'],
             '  body: %d lines (limit %d)' % (report['body_lines'], MAX_BODY_LINES),
             '  evals: %d case(s) %s' % (len(report['eval_cases']), ', '.join(report['eval_cases']))]
    lines += ['  error: ' + item for item in report['errors']]
    lines += ['  warning: ' + item for item in report['warnings']]
    return '\n'.join(lines)
