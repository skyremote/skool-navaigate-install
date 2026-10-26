"""A reverse-engineering investigation: a scope you are allowed to work in, then findings tied to REA evidence."""
import re

BASES = ('my own software', 'public website', 'licence allows it', 'written permission', 'interoperability')
STATUSES = ('observed', 'inferred', 'unknown')
OFF_LIMITS = re.compile(r'\b(crack|keygen|bypass (the )?(licen[cs]e|drm|paywall|login|activation)|remove (the )?drm|pirat)', re.I)

SCOPE = """# Scope: {target}

Target: {target}
Whose it is: <who owns it>
Basis: <one of: my own software, public website, licence allows it, written permission, interoperability>
Question: {question}
Will do: <static reading of the shipped files, observing my own runs>
Will not do: break licence checks or DRM, get past logins or paywalls, attack anyone's servers, publish their code

## Findings
- <one claim> | Evidence: <REA evidence_id, or file and offset> | Status: <observed, inferred or unknown>

## Unknowns
- <what is still unproven, and what would prove it>
"""

SAMPLE = """# Scope: Acme Studio price calculator (practice)

Target: a pricing page on the member's own practice site (fictional Acme Studio)
Whose it is: the member
Basis: my own software
Question: how does the calculator turn the number of pages into a price?
Will do: static reading of the shipped JavaScript bundle
Will not do: break licence checks or DRM, get past logins or paywalls, attack anyone's servers, publish their code

## Findings
- The price is pages times a unit rate, plus a fixed setup fee. | Evidence: ev_js_0001 (calculatePrice in main.js) | Status: observed
- The unit rate drops after ten pages. | Evidence: ev_js_0002 (rate table) | Status: observed
- Discount codes are checked on the server, not in the page. | Evidence: ev_js_0003 (fetch to /api/discount) | Status: inferred

## Unknowns
- How the server checks a discount code: not in the shipped files; only the site owner's server code would prove it.
"""


def field(text, name):
    match = re.search(r'^' + name + r':\s*(.+)$', text, re.M)
    return match.group(1).strip() if match else ''


def findings(text):
    rows, inside = [], False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.strip().lower() == '## findings'
            continue
        if inside and line.strip().startswith(('-', '*')):
            rows.append(line.strip())
    return rows


def part(line, name):
    match = re.search(name + r'\s*:\s*([^|]+)', line, re.I)
    return match.group(1).strip() if match else ''


def check(text):
    if re.search(r'<[^>\n]{3,}>', text):
        return ['The scope still has template placeholders like <...>. Fill in the target, owner and basis first.']
    problems = []
    basis = field(text, 'Basis').lower()
    if not any(b in basis for b in BASES):
        problems.append('Basis must be one of: %s.' % ', '.join(BASES))
    if not field(text, 'Whose it is'):
        problems.append('Say whose software it is.')
    if OFF_LIMITS.search(field(text, 'Question') + ' ' + field(text, 'Will do')):
        problems.append('This pack does not help break licence checks, DRM, logins or paywalls.')
    rows = findings(text)
    if not rows:
        problems.append('No findings yet.')
    for row in rows:
        if not part(row, 'Evidence'):
            problems.append('Finding has no evidence: ' + row[:70])
        status = part(row, 'Status').lower()
        if status not in STATUSES:
            problems.append('Status must be observed, inferred or unknown: ' + row[:60])
        if status == 'observed' and re.search(r'\b(probably|likely|seems|might)\b', row, re.I):
            problems.append('An "observed" finding cannot say probably or likely. Mark it inferred: ' + row[:60])
    if '## Unknowns' not in text:
        problems.append('Add an "## Unknowns" section, even if it says none.')
    return problems
