"""The triage brief: Action needed, Waiting on, FYI. Every item names the sender, date and subject it came from."""
import re

PILES = ('Action needed', 'Waiting on', 'FYI')
FIELDS = ('From', 'Date', 'Subject')
SEND_WORDS = re.compile(r'\b(i|we) (have )?(sent|replied|forwarded|emailed)\b|\bsent (it|the reply|your reply)\b', re.I)

TEMPLATE = """# Inbox brief: {date}

Read-only: nothing was sent, archived or deleted.

## Action needed
- From: <sender> | Date: <date> | Subject: <subject> | Why: <what they need from you> | Draft: <one line, or none>

## Waiting on
- From: <sender> | Date: <date> | Subject: <subject> | Why: <what you are waiting for>

## FYI
- From: <sender> | Date: <date> | Subject: <subject> | Why: <one line>
"""


def piles(text):
    found, current = {}, None
    for line in text.splitlines():
        heading = re.match(r'^##\s+(.+?)\s*$', line)
        if heading:
            current = heading.group(1).strip()
            found[current] = []
        elif current and line.strip().startswith(('-', '*')):
            found[current].append(line.strip())
    return found


def field(line, name):
    match = re.search(r'\b' + name + r'\s*:\s*([^|]+)', line)
    return match.group(1).strip() if match else ''


def check(text):
    """Return problems. An empty list means the brief passes."""
    if re.search(r'<[^>\n]{3,}>', text):
        return ['The brief still has template placeholders like <...>.']
    problems = []
    found = piles(text)
    for pile in PILES:
        if pile not in found:
            problems.append('Missing pile: ## ' + pile)
    for pile, items in found.items():
        for item in items:
            if item.lstrip('-* ').lower().startswith('none'):
                continue
            for name in FIELDS:
                if not field(item, name):
                    problems.append('%s item has no %s: %s' % (pile, name, item[:80]))
            if pile == 'Action needed' and not field(item, 'Why'):
                problems.append('Action needed item says no Why: ' + item[:80])
    if SEND_WORDS.search(text):
        problems.append('The brief claims something was sent. This pack never sends: drafts only.')
    if 'Read-only' not in text:
        problems.append('Say at the top that the brief is read-only: nothing was sent, archived or deleted.')
    return problems


def count(text):
    return {pile: len([i for i in items if not i.lstrip('-* ').lower().startswith('none')])
            for pile, items in piles(text).items() if pile in PILES}
