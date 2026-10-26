"""The decision record: decisions, actions with owners, open questions, each tied to the transcript.

`check` refuses a record that invents an owner, a number or a date that is not in the transcript.
"""
import re

SECTIONS = ('Decisions', 'Actions', 'Open questions', 'Source')
NOT_STATED = ('not stated', 'not said', 'unknown', 'proposed')
NUMBER = re.compile(r'(?<![\w.])\d[\d,.:/]*\d(?![\w])|(?<![\w.])\d(?![\w.:/])')

TEMPLATE = """# Decision record: {title}

Meeting: {title}, {date}. Source: {source}.

## Decisions
- <what was decided, in plain words> (quote: "<the words that show it>")

## Actions
- <action> | Owner: <a name said in the call, or "not stated"> | Due: <a date said in the call, or "not stated"> | Quote: "<the words>"

## Open questions
- <what was left open, and who can answer it, or "not stated">

## Source
{source}
"""


def sections(text):
    found, current = {}, None
    for line in text.splitlines():
        heading = re.match(r'^##\s+(.+?)\s*$', line)
        if heading:
            current = heading.group(1).strip()
            found[current] = []
        elif current:
            found[current].append(line)
    return found


def numbers(text):
    return [n.rstrip('.,:') for n in NUMBER.findall(text)]


def field(line, name):
    match = re.search(name + r'\s*:\s*([^|]+)', line, re.I)
    return match.group(1).strip().strip('"') if match else None


def check(record, source):
    """Return a list of problems. An empty list means the record passes."""
    problems = []
    if re.search(r'<[^>\n]{3,}>', record):
        return ['The record still has template placeholders like <...>. Fill them in, or delete the line.']
    parts = sections(record)
    for name in SECTIONS:
        if name not in parts:
            problems.append('Missing section: ## ' + name)
    plain_source = ' '.join(source.split()).lower()
    source_numbers = set(numbers(source))
    actions = [l for l in parts.get('Actions', []) if l.strip().startswith(('-', '*'))]
    if 'Actions' in parts and not actions:
        problems.append('No actions listed. If the call agreed none, write "- None agreed | Owner: not stated | Due: not stated"')
    for line in actions:
        if line.strip().lstrip('-* ').lower().startswith('none agreed'):
            continue
        owner, due = field(line, 'Owner'), field(line, 'Due')
        if owner is None:
            problems.append('Action has no Owner field: ' + line.strip())
        elif owner.lower() not in NOT_STATED and owner.lower() not in ('me', 'others') and owner.lower() not in plain_source:
            problems.append('Owner "%s" is not named in the transcript. Use a name from the call or "not stated".' % owner)
        if due is None:
            problems.append('Action has no Due field: ' + line.strip())
    body = '\n'.join(l for name, lines in parts.items() if name != 'Source' for l in lines)
    for n in numbers(body):
        if n not in source_numbers:
            problems.append('The number %s is not in the transcript. Remove it or quote where it was said.' % n)
    for quote in re.findall(r'"([^"\n]{12,})"', body):
        if ' '.join(quote.split()).lower() not in plain_source:
            problems.append('Quote not found word for word in the transcript: "%s"' % quote[:60])
    return problems
