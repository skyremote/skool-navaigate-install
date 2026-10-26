"""The findings ledger: every finding has a source link, a kind of source, and an honest confidence label."""
import re

KINDS = ('paper', 'practitioner', 'newsletter', 'video', 'web', 'official')
LEVELS = ('high', 'medium', 'low')
URL = re.compile(r'https?://\S+')

TEMPLATE = """# Research: {question}

Question: {question}
Date: {date}

## Findings
- <finding in one sentence> | Source: <link> | Kind: <paper, practitioner, newsletter, video, web or official> | Confidence: <high, medium or low>

## Where sources disagree
- <what disagrees, and the links on each side, or "none found">

## What we could not find
- <gaps, paywalls, sources that refused>
"""


def findings(text):
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.strip().lower() == '## findings'
            continue
        if inside and line.strip().startswith(('-', '*')):
            lines.append(line.strip())
    return lines


def field(line, name):
    match = re.search(name + r'\s*:\s*([^|]+)', line, re.I)
    return match.group(1).strip() if match else ''


def check(text):
    if re.search(r'<[^>\n]{3,}>', text):
        return ['The ledger still has template placeholders like <...>.']
    problems = []
    for section in ('## Findings', '## Where sources disagree', '## What we could not find'):
        if section not in text:
            problems.append('Missing section: ' + section)
    rows = findings(text)
    if not rows:
        problems.append('No findings listed.')
    kinds, high = set(), 0
    for row in rows:
        source, kind, level = field(row, 'Source'), field(row, 'Kind').lower(), field(row, 'Confidence').lower()
        if not URL.search(source):
            problems.append('Finding has no source link: ' + row[:70])
        if kind not in KINDS:
            problems.append('Kind must be one of %s: %s' % (', '.join(KINDS), row[:60]))
        if level not in LEVELS:
            problems.append('Confidence must be high, medium or low: ' + row[:60])
        kinds.add(kind)
        high += level == 'high'
    if rows and high == len(rows) and len(rows) > 2:
        problems.append('Every finding is "high". Label honestly: a single Reddit thread or one newsletter is not high.')
    if rows and len(kinds - {''}) < 2:
        problems.append('All findings come from one kind of source. Add a second kind before you conclude.')
    return problems
