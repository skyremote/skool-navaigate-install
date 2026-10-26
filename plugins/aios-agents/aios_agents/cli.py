"""aios-agent: brief new, brief check, compare and crew. Run aios-agent --help."""
import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .brief import check, template
from .compare import CompareError, compare, format_table

AGENTS = Path(__file__).resolve().parents[1] / 'agents'


def cmd_brief_new(args):
    text = template()
    if args.out:
        out = Path(args.out)
        if out.exists():
            print('Stopped: %s already exists' % out, file=sys.stderr)
            return 1
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print('Wrote %s. Fill every <placeholder>, then run: aios-agent brief check %s' % (out, out))
    else:
        sys.stdout.write(text)
    return 0


def cmd_brief_check(args):
    text = sys.stdin.read() if args.file == '-' else Path(args.file).read_text()
    problems = check(text)
    if args.json:
        print(json.dumps({'ok': not problems, 'problems': problems}, indent=2))
    elif problems:
        print('NOT READY')
        for item in problems:
            print('  - ' + item)
    else:
        print('READY: objective, finish line, format, tools, boundaries and stop are all there.')
    return 1 if problems else 0


def cmd_compare(args):
    result = compare(args.first, args.second, tuple(args.labels), tuple(args.wall) if args.wall else None)
    print(json.dumps(result, indent=2) if args.json else format_table(result))
    return 0


def cmd_result(args):
    from .compare import load
    data = load(args.file)
    used = (data.get('subagent_stats') or {}).get('by_type') or {}
    print('Sub-agents used: ' + (', '.join('%s (%d)' % kv for kv in used.items()) or 'none'))
    print()
    print(data.get('result', '').strip() or '(no final reply)')
    return 0


def cmd_crew(args):
    from .crew import crew
    for agent in crew(AGENTS):
        print('%-16s tools: %-34s %s' % (agent['name'], agent['tools'], agent['description']))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog='aios-agent', description='Brief, check and measure sub-agents.')
    parser.add_argument('--version', action='version', version='aios-agent ' + __version__)
    sub = parser.add_subparsers(dest='command', required=True)
    brief = sub.add_parser('brief', help='write or check a sub-agent brief')
    bsub = brief.add_subparsers(dest='action', required=True)
    new = bsub.add_parser('new', help='print the brief template, or write it with --out')
    new.add_argument('--out')
    new.set_defaults(run=cmd_brief_new)
    chk = bsub.add_parser('check', help='check a brief file (or - for stdin)')
    chk.add_argument('file')
    chk.add_argument('--json', action='store_true')
    chk.set_defaults(run=cmd_brief_check)
    cmp_ = sub.add_parser('compare', help='compare two claude -p --output-format json results')
    cmp_.add_argument('first')
    cmp_.add_argument('second')
    cmp_.add_argument('--labels', nargs=2, default=['one loop', 'with reviewer'])
    cmp_.add_argument('--wall', nargs=2, type=float, metavar=('FIRST_S', 'SECOND_S'),
                      help='wall-clock seconds you measured for each run, for example with time')
    cmp_.add_argument('--json', action='store_true')
    cmp_.set_defaults(run=cmd_compare)
    res = sub.add_parser('result', help='print the final reply of a claude -p --output-format json result')
    res.add_argument('file')
    res.set_defaults(run=cmd_result)
    crew = sub.add_parser('crew', help='list the three agents in this pack and their tools')
    crew.set_defaults(run=cmd_crew)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except (CompareError, OSError) as exc:
        print('Stopped: %s' % exc, file=sys.stderr)
        return 1
