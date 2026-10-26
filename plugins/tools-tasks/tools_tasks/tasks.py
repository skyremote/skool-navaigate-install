"""Tasks that get done: a verb, an owner, a date and a "done when", and no more than three for today."""
import re
from datetime import date

VERB_FIRST = re.compile(r'^(?:\[[ x]\]\s*)?([A-Za-z]+)')
VAGUE = ('work on', 'look into', 'think about', 'deal with', 'handle', 'sort out', 'follow up on stuff', 'misc')
TODAY_LIMIT = 3

TEMPLATE = """# Tasks: {title}

From: {source}

## Tasks
- <Verb> <one clear outcome> | Owner: <name> | Due: <YYYY-MM-DD or no date> | Done when: <what you can see when it is finished>
"""

SAMPLE = """# Tasks: Northwind booking page (practice)

From: northwind-kickoff_record_v1.md

## Tasks
- Send the page layout to Northwind | Owner: Sam | Due: 2026-10-31 | Done when: Northwind has the layout PDF in their inbox
- Collect photos of the six best-selling cakes | Owner: Tom (Northwind) | Due: no date | Done when: six photos are in the shared folder
- Ask the accountant about a 20 percent deposit | Owner: Priya (Northwind) | Due: no date | Done when: a yes or no is written in the project notes
"""


def task_lines(text):
    rows, inside = [], False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.strip().lower() == '## tasks'
            continue
        if inside and line.strip().startswith(('-', '*')):
            rows.append(line.strip().lstrip('-* ').strip())
    return rows


def part(line, name):
    match = re.search(name + r'\s*:\s*([^|]+)', line, re.I)
    return match.group(1).strip() if match else ''


def check(text):
    if re.search(r'<[^>\n]{3,}>', text):
        return ['The task list still has template placeholders like <...>.']
    rows = task_lines(text)
    if not rows:
        return ['No tasks under "## Tasks".']
    problems = []
    for row in rows:
        title = row.split('|')[0].strip()
        if any(v in title.lower() for v in VAGUE):
            problems.append('Too vague: "%s". Name the outcome (Send, Book, Write, Decide...).' % title[:60])
        if not VERB_FIRST.match(title) or title.split()[0].lower().endswith(('ing', 'tion')):
            problems.append('Start with a verb: "%s".' % title[:60])
        if not part(row, 'Owner'):
            problems.append('No owner: "%s".' % title[:60])
        due = part(row, 'Due')
        if not due:
            problems.append('No due date (write "no date" if there is none): "%s".' % title[:60])
        elif due.lower() != 'no date':
            try:
                date.fromisoformat(due)
            except ValueError:
                problems.append('Due must be YYYY-MM-DD or "no date": "%s".' % due)
        if not part(row, 'Done when'):
            problems.append('No "Done when": "%s".' % title[:60])
    return problems


def today(tasks, on=None, limit=TODAY_LIMIT):
    """Pick today's few: overdue first (oldest first), then due today, then by priority (1 urgent .. 4 low)."""
    on = on or date.today().isoformat()
    open_tasks = [t for t in tasks if str(t.get('status', '')).lower() not in ('done', 'complete', 'closed')]
    def key(t):
        due = t.get('due') or '9999-12-31'
        return (0 if due < on else 1 if due == on else 2, due, int(t.get('priority') or 3))
    ranked = sorted(open_tasks, key=key)
    overdue = [t for t in ranked if (t.get('due') or '9999') < on]
    groups = {}
    for t in overdue:
        groups.setdefault(t.get('list') or 'No list', []).append(t)
    return ranked[:limit], groups
