"""A small, dependency-free reader for the YAML frontmatter used by rules and skills.

It understands the subset these files use: `key: value`, quoted values, block scalars
(`>` and `|`) and simple lists (`- item` lines or a comma-separated string).
"""


def split(text):
    """Return (frontmatter_text or None, body_text)."""
    if not text.startswith('---'):
        return None, text
    lines = text.split('\n')
    if lines[0].strip() != '---':
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == '---':
            return '\n'.join(lines[1:index]), '\n'.join(lines[index + 1:])
    return None, text


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
        return value[1:-1]
    return value


def parse(block):
    """Parse a frontmatter block into a dict of strings and lists."""
    data = {}
    if block is None:
        return data
    lines = block.split('\n')
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith('#') or line[:1] in ' \t':
            index += 1
            continue
        if ':' not in line:
            index += 1
            continue
        key, _, rest = line.partition(':')
        key = key.strip()
        rest = rest.strip()
        index += 1
        if rest in ('>', '|', '>-', '|-', '>+', '|+'):
            parts = []
            while index < len(lines) and (not lines[index].strip() or lines[index][:1] in ' \t'):
                parts.append(lines[index].strip())
                index += 1
            joiner = ' ' if rest.startswith('>') else '\n'
            data[key] = joiner.join(p for p in parts if p).strip()
        elif rest == '':
            items = []
            while index < len(lines) and (not lines[index].strip() or lines[index][:1] in ' \t'):
                stripped = lines[index].strip()
                if stripped.startswith('- '):
                    items.append(_unquote(stripped[2:]))
                elif stripped == '-':
                    items.append('')
                index += 1
            data[key] = items
        elif rest.startswith('[') and rest.endswith(']'):
            data[key] = [_unquote(v) for v in rest[1:-1].split(',') if v.strip()]
        else:
            data[key] = _unquote(rest)
    return data


def as_list(value):
    """Normalise a `paths` value: a list, or a comma-separated string."""
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v]
    return [v.strip() for v in str(value).split(',') if v.strip()]
