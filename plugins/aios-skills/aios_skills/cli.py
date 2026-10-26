"""aios-skill: new, check, audit and hide. Run aios-skill --help."""
import argparse
import json
import sys

from . import __version__
from .audit import collect, format_rows
from .check import check_skill, find_skills, format_report
from .hide import STATES, HideError, apply, plan
from .scaffold import ScaffoldError, create


def cmd_new(args):
    target, files = create(args.name, args.description, root=args.dir, project=args.project)
    print('Created %s' % target)
    for item in files:
        print('  ' + item)
    print('Next: replace every TODO, then run: aios-skill check %s' % target)
    print('Then test it against a no-skill baseline: claude plugin eval %s --runs 1' % target)
    return 0


def cmd_check(args):
    skills = find_skills(args.path)
    if not skills:
        print('No SKILL.md found under %s' % args.path, file=sys.stderr)
        return 1
    reports = [check_skill(path) for path in skills]
    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        print('\n'.join(format_report(report) for report in reports))
    return 0 if all(report['ok'] for report in reports) else 1


def cmd_audit(args):
    rows = collect()
    print(json.dumps(rows, indent=2) if args.json else format_rows(rows, args.top))
    return 0


def cmd_hide(args):
    if args.dry_run:
        path, old, new = plan(args.skill, args.state, args.scope)
        print('Would write %s:' % path)
        print(json.dumps({'skillOverrides': new.get('skillOverrides', {})}, indent=2))
        return 0
    path, backup, changed = apply(args.skill, args.state, args.scope)
    if not changed:
        print('No change: %s is already %s in %s' % (args.skill, args.state, path))
    else:
        print('Set %s to %s in %s' % (args.skill, args.state, path))
        if backup:
            print('Backup: %s' % backup)
    print('Start a new session (or run /reload-plugins) for the change to apply.')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog='aios-skill', description='Write, check, measure and hide skills.')
    parser.add_argument('--version', action='version', version='aios-skill ' + __version__)
    sub = parser.add_subparsers(dest='command', required=True)
    new = sub.add_parser('new', help='create a skill with three eval cases')
    new.add_argument('name')
    new.add_argument('--description', required=True, help='one or two sentences: what it does and when to use it')
    where = new.add_mutually_exclusive_group()
    where.add_argument('--project', action='store_true', help='create it in ./.claude/skills (default ~/.claude/skills)')
    where.add_argument('--dir', help='create it in this folder instead')
    new.set_defaults(run=cmd_new)
    check = sub.add_parser('check', help='check description, length, TODOs and evals')
    check.add_argument('path', nargs='?', default='.')
    check.add_argument('--json', action='store_true')
    check.set_defaults(run=cmd_check)
    audit = sub.add_parser('audit', help='list your skills by listing cost')
    audit.add_argument('--top', type=int, default=20)
    audit.add_argument('--json', action='store_true')
    audit.set_defaults(run=cmd_audit)
    hide = sub.add_parser('hide', help='set a skill to on, name-only, user-invocable-only or off')
    hide.add_argument('skill')
    hide.add_argument('state', choices=STATES)
    hide.add_argument('--scope', choices=('local', 'project', 'user'), default='local')
    hide.add_argument('--dry-run', action='store_true')
    hide.set_defaults(run=cmd_hide)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except (ScaffoldError, HideError, OSError) as exc:
        print('Stopped: %s' % exc, file=sys.stderr)
        return 1
