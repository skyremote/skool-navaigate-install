"""Read the crew's agent files (frontmatter only) so members can see what each one may do."""
import re
from pathlib import Path

READ_ONLY = {'Read', 'Grep', 'Glob', 'WebFetch', 'WebSearch'}


def frontmatter(text):
    lines = text.splitlines()
    data = {}
    if not lines or lines[0].strip() != '---':
        return data
    for line in lines[1:]:
        if line.strip() == '---':
            break
        match = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if match:
            data[match.group(1)] = match.group(2).strip().strip('"\'')
    return data


def crew(folder):
    agents = []
    for path in sorted(Path(folder).glob('*.md')):
        meta = frontmatter(path.read_text())
        tools = [t.strip() for t in meta.get('tools', '').split(',') if t.strip()]
        agents.append({'name': meta.get('name', path.stem), 'tools': ', '.join(tools),
                       'read_only': bool(tools) and set(tools) <= READ_ONLY,
                       'model': meta.get('model', ''), 'omit_claude_md': meta.get('omitClaudeMd') == 'true',
                       'description': meta.get('description', '')[:70]})
    return agents
