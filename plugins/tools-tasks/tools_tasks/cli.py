"""tools-tasks: turn briefs into tasks that get done, in your own ClickUp through ClickUp's official MCP server."""
import argparse
import json
import sys
from pathlib import Path

from . import __version__, tasks

SAMPLE_OPEN = [
    {'name': 'Send the page layout to Northwind', 'due': '2026-10-20', 'priority': 2, 'list': 'Northwind', 'status': 'open'},
    {'name': 'Invoice Contoso for October', 'due': '2026-10-24', 'priority': 1, 'list': 'Contoso', 'status': 'open'},
    {'name': 'Book the photographer', 'due': '2026-10-26', 'priority': 3, 'list': 'Northwind', 'status': 'open'},
    {'name': 'Update the website footer', 'due': None, 'priority': 4, 'list': 'Acme Studio', 'status': 'open'},
    {'name': 'Renew the domain', 'due': '2026-10-01', 'priority': 2, 'list': 'Acme Studio', 'status': 'done'},
]


def new(args):
    out = Path(args.out).expanduser()
    if out.exists():
        print('Not overwriting %s. Use a new _v2 name.' % out)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tasks.TEMPLATE.format(title=args.title, source=args.source or 'not stated'))
    print('Wrote an empty task list: %s' % out)
    return 0


def check(args):
    problems = tasks.check(Path(args.file).expanduser().read_text())
    if problems:
        print('FAIL: %d problem(s)' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    print('PASS: every task starts with a verb and has an owner, a due date and a "done when".')
    return 0


def do_today(args):
    data = json.loads(Path(args.file).expanduser().read_text())
    picked, overdue = tasks.today(data, args.on, args.limit)
    if overdue:
        print('Overdue, by list:')
        for name, items in sorted(overdue.items()):
            print('  %s: %s' % (name, '; '.join('%s (due %s)' % (t['name'], t['due']) for t in items)))
    print('Today, at most %d:' % args.limit)
    for i, t in enumerate(picked, 1):
        print('  %d. %s  [%s, due %s]' % (i, t['name'], t.get('list') or 'No list', t.get('due') or 'no date'))
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'northwind_tasks_v1.md').write_text(tasks.SAMPLE)
    (folder / 'open-tasks_v1.json').write_text(json.dumps(SAMPLE_OPEN, indent=2))
    print('Practice files in %s (fictional): northwind_tasks_v1.md, open-tasks_v1.json' % folder)
    print('Next: tools-tasks check %s, then tools-tasks today %s --on 2026-10-26' % (folder / 'northwind_tasks_v1.md', folder / 'open-tasks_v1.json'))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-tasks', description=__doc__)
    p.add_argument('--version', action='version', version='tools-tasks ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('new', help='an empty task list for a brief')
    s.add_argument('out')
    s.add_argument('--title', required=True)
    s.add_argument('--source')
    s.set_defaults(run=new)
    s = sub.add_parser('check', help='check a task list before it goes into ClickUp')
    s.add_argument('file')
    s.set_defaults(run=check)
    s = sub.add_parser('today', help='overdue by list, and at most three for today, from a JSON list of open tasks')
    s.add_argument('file')
    s.add_argument('--on', help='YYYY-MM-DD, default today')
    s.add_argument('--limit', type=int, default=tasks.TODAY_LIMIT)
    s.set_defaults(run=do_today)
    s = sub.add_parser('sample', help='practice files')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except FileNotFoundError as error:
        print('File not found: ' + str(error.filename), file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError) as error:
        print('Could not read that file: %s' % error, file=sys.stderr)
        return 1
