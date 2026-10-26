"""aios-rules: set up your folder and rules, check the always-on budget, run the monthly audit."""
import argparse
import sys
from pathlib import Path

from . import __version__, audit, check, setup


def build_parser():
    parser = argparse.ArgumentParser(prog='aios-rules', description=__doc__)
    parser.add_argument('--version', action='version', version='aios-rules ' + __version__)
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('init', help='create the folder map, a starter AGENTS.md, the CLAUDE.md bridge and scoped rules')
    p.add_argument('--dir', default='.', help='your AIOS folder (default: here)')
    p.add_argument('--business', help='your business name, for the starter AGENTS.md')
    p.add_argument('--owner', help='your name, for the starter AGENTS.md')
    p.add_argument('--no-folders', action='store_true', help='keep your own folders; only add the rules files')
    p.add_argument('--dry-run', action='store_true', help='show what would be created; write nothing')

    p = sub.add_parser('check', help='count lines and approximate tokens of everything always loaded')
    p.add_argument('--dir', default='.', help='the folder you start the harness in (default: here)')
    p.add_argument('--harness', choices=['claude', 'codex', 'cursor', 'all'], default='claude')
    p.add_argument('--json', action='store_true', help='print the full result as JSON')
    p.add_argument('--max-lines', dest='total_lines_max', type=int, help='total always-loaded lines budget')
    p.add_argument('--max-tokens', dest='total_tokens_max', type=int, help='total always-loaded tokens budget')
    p.add_argument('--file-lines', dest='file_lines_max', type=int, help='limit for one file')

    p = sub.add_parser('audit', help='monthly audit: check, /doctor prompt-audit and /skill-doctor into a dated file')
    p.add_argument('--dir', default='.', help='your AIOS folder (default: here)')
    p.add_argument('--out', help='where to write the audit (default: 80_aios/audits)')
    p.add_argument('--no-claude', action='store_true', help='only run the budget check')
    p.add_argument('--timeout', type=int, default=900, help='seconds allowed for each Claude Code step')

    p = sub.add_parser('cursor-rules', help='mirror .claude/rules into .cursor/rules so Cursor gets the same scoped rules')
    p.add_argument('--dir', default='.', help='your AIOS folder (default: here)')
    p.add_argument('--dry-run', action='store_true')
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    try:
        if args.command == 'check':
            return check.main(args)
        if args.command == 'init':
            report = setup.init(args.dir, args.business, args.owner, not args.no_folders, args.dry_run)
            sys.stdout.write(setup.render(report, args.dir))
            sys.stdout.write('Next: fill in the {{...}} lines in AGENTS.md, then run: aios-rules check\n')
            return 0
        if args.command == 'cursor-rules':
            sys.stdout.write(setup.render(setup.cursor_rules(args.dir, args.dry_run), args.dir))
            return 0
        if args.command == 'audit':
            path, status = audit.audit(args.dir, args.out, not args.no_claude, args.timeout)
            try:
                shown = './' + path.relative_to(Path(args.dir).resolve()).as_posix()
            except ValueError:
                shown = str(path)
            sys.stdout.write('Wrote %s\n' % shown)
            sys.stdout.write('Budget %(budget)s; prompt audit %(prompt_audit)s; skill doctor %(skill_doctor)s.\n' % status)
            return 0
    except OSError as exc:
        sys.stderr.write('aios-rules stopped: %s\n' % exc)
        return 2
    return 2
