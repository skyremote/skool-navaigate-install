"""Write and check a sub-agent brief.

A sub-agent knows only what its brief says. A brief that passes this check has an
objective with a measurable finish line, a return format, the tools to use and
avoid, explicit boundaries and a stopping point.
"""
import re
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / 'templates' / 'brief_v1.md'
REQUIRED = ('objective', 'format', 'tools', 'boundaries', 'stop')
PLACEHOLDER = re.compile(r'<[^<>\n]{3,}>')
HEADING = re.compile(r'^#{2,3}\s+(.+?)\s*$')
MEASURABLE = re.compile(r'\d|\b(?:pass(?:es)?|fail(?:s)?|exactly|at most|at least|each|every|file|table|list|count|zero|no more than)\b', re.I)


def template():
    return TEMPLATE.read_text()


def sections(text):
    """Map lower-case heading -> body text for ## and ### headings."""
    found, current, buf = {}, None, []
    for line in text.splitlines():
        match = HEADING.match(line)
        if match:
            if current is not None:
                found[current] = '\n'.join(buf).strip()
            current, buf = match.group(1).strip().lower(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        found[current] = '\n'.join(buf).strip()
    return found


def field(body, label):
    match = re.search(r'^\s*%s\s*:\s*(.*)$' % re.escape(label), body, re.I | re.M)
    return match.group(1).strip() if match else None


def check(text):
    """Return a list of problems. An empty list means the brief is ready to send."""
    problems = []
    found = sections(text)
    for name in REQUIRED:
        if name not in found:
            problems.append('Missing section: ## %s' % name.capitalize())
        elif not found[name]:
            problems.append('Section %s is empty' % name.capitalize())
    if PLACEHOLDER.search(text):
        problems.append('Still has <placeholders>: ' + ', '.join(sorted(set(PLACEHOLDER.findall(text)))[:3]))
    objective = found.get('objective', '')
    done = field(objective, 'Done when')
    if objective and not done:
        problems.append('Objective has no "Done when:" line, so nobody can tell when it is finished')
    elif done and not MEASURABLE.search(done):
        problems.append('"Done when" is not measurable: name a count, a file, or a check that passes')
    tools = found.get('tools', '')
    if tools and field(tools, 'Use') is None:
        problems.append('Tools has no "Use:" line')
    boundaries = found.get('boundaries', '')
    if boundaries and field(boundaries, 'Do not touch') is None:
        problems.append('Boundaries has no "Do not touch:" line')
    stop = found.get('stop', '')
    if stop and not re.search(r'\d|\bwhen\b|\bafter\b|\bonce\b', stop, re.I):
        problems.append('Stop does not say when to stop: give a condition or a limit')
    return problems
