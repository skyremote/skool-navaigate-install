"""Compare two headless runs of the same task, for example one loop against one loop plus a reviewer.

Input: the JSON that `claude -p "<task>" --output-format json` prints. A file of
stream-json lines also works; the last `result` line is used.
"""
import json
from pathlib import Path


class CompareError(ValueError):
    pass


def load(path):
    text = Path(path).read_text()
    try:
        data = json.loads(text)
    except ValueError:
        data = None
        for line in reversed(text.splitlines()):
            line = line.strip()
            if not line.startswith('{'):
                continue
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if item.get('type') == 'result':
                data = item
                break
    if isinstance(data, list):
        data = next((item for item in reversed(data) if isinstance(item, dict) and item.get('type') == 'result'), None)
    if not isinstance(data, dict) or 'duration_ms' not in data:
        raise CompareError('%s is not a claude -p --output-format json result' % path)
    return data


def summary(data):
    usage = data.get('usage') or {}
    tokens = sum(int(usage.get(key) or 0) for key in
                 ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'))
    # Sub-agent tokens are reported per model; include every model's totals when present.
    models = data.get('modelUsage') or {}
    if models:
        tokens = sum(int(m.get('inputTokens') or 0) + int(m.get('outputTokens') or 0) +
                     int(m.get('cacheReadInputTokens') or 0) + int(m.get('cacheCreationInputTokens') or 0)
                     for m in models.values())
    stats = data.get('subagent_stats') or {}
    return {
        'seconds': round((data.get('duration_ms') or 0) / 1000.0, 1),
        'turns': data.get('num_turns') or 0,
        'tokens': tokens,
        'cost_usd': round(float(data.get('total_cost_usd') or 0), 4),
        'subagents': int(stats.get('spawned') or 0),
        'ok': not data.get('is_error') and data.get('subtype') == 'success',
    }


def ratio(a, b):
    return None if not a else round(b / float(a), 2)


def compare(first, second, labels=('one loop', 'with reviewer'), wall=None):
    a, b = summary(load(first)), summary(load(second))
    rows = []
    if wall:
        rows.append(('wall clock (s)', wall[0], wall[1], ratio(wall[0], wall[1])))
    for key, title in (('seconds', 'reported time (s)'), ('turns', 'turns'), ('tokens', 'tokens'),
                       ('cost_usd', 'list-price cost (USD)'), ('subagents', 'sub-agents spawned')):
        rows.append((title, a[key], b[key], ratio(a[key], b[key])))
    return {'labels': labels, 'first': a, 'second': b, 'rows': rows, 'wall': list(wall) if wall else None}


def format_table(result):
    first, second = result['labels']
    lines = ['%-24s %14s %14s %8s' % ('', first, second, 'ratio')]
    for title, a, b, r in result['rows']:
        lines.append('%-24s %14s %14s %8s' % (title, a, b, '-' if r is None else '%sx' % r))
    if not result['first']['ok'] or not result['second']['ok']:
        lines.append('Warning: one run did not finish successfully, so the comparison is not fair.')
    if (result['first']['subagents'] or result['second']['subagents']) and not result.get('wall'):
        lines.append('Note: reported time can leave out time spent waiting for a sub-agent. '
                     'Time both runs with `time` and pass --wall to compare real wall clock.')
    lines.append('Keep the reviewer only if it found a real problem the single loop missed.')
    lines.append('Write down what it found (or "nothing") next to these numbers before you decide.')
    return '\n'.join(lines)
