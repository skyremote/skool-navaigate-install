"""A small, dependency-free reader for SKILL.md frontmatter.

It understands the subset skills use: `key: value`, quoted values, folded
continuation lines and `>` or `|` block scalars. Anything else is kept as text.
"""
import re

KEY = re.compile(r'^([A-Za-z_][\w-]*):\s?(.*)$')


def split(text):
    """Return (frontmatter dict, body text, frontmatter line count)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}, text, 0
    for end in range(1, len(lines)):
        if lines[end].strip() == '---':
            break
    else:
        return {}, text, 0
    data, key = {}, None
    for raw in lines[1:end]:
        match = KEY.match(raw)
        if match and not raw.startswith((' ', '\t')):
            key, value = match.group(1), match.group(2).strip()
            data[key] = '' if value in ('>', '|', '>-', '|-') else value
        elif key and raw.strip():
            data[key] = (data[key] + ' ' + raw.strip()).strip()
    for name, value in data.items():
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            data[name] = value[1:-1]
    body = '\n'.join(lines[end + 1:])
    return data, body, end + 1


ABBREVIATIONS = re.compile(r'\b(?:e\.g|i\.e|etc|vs|approx|incl)\.', re.I)


def sentences(text):
    """Count sentences the way a reader would, ignoring common abbreviations."""
    cleaned = ABBREVIATIONS.sub('', text or '').strip()
    if not cleaned:
        return 0
    ends = re.findall(r'[.!?](?=\s|$)', cleaned)
    # A description without a final full stop still counts as one sentence.
    return len(ends) + (0 if re.search(r'[.!?]\s*$', cleaned) else 1)
