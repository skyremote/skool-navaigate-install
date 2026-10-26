"""aios-verify: init, run, scan, screenshot, try, and the two hook entry points (guard, gate)."""
import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .checks import ConfigError, find_root, format_results, run_checks
from .gate import evaluate
from .guard import decide, hook, load_extra, staged_secrets
from .screenshot import take
from .setup import apply


def read_payload():
    try:
        return json.loads(sys.stdin.read() or '{}')
    except ValueError:
        return {}


def cmd_guard(args):
    # PreToolUse hook. Any internal error must not block the member's work: no opinion.
    try:
        answer = hook(read_payload())
    except Exception as exc:  # noqa: BLE001
        print('aios-verify guard error: %s' % exc, file=sys.stderr)
        return 0
    if answer:
        print(json.dumps(answer))
    return 0


def cmd_gate(args):
    # Stop hook. Same rule: an error in the gate itself never traps the session.
    try:
        answer = evaluate(read_payload())
    except Exception as exc:  # noqa: BLE001
        answer = {'systemMessage': 'AIOS verify gate error, checks not run: %s' % exc}
    if answer:
        print(json.dumps(answer))
    return 0


def cmd_init(args):
    written, skipped = apply(args.path, git_hook=args.git_hook, dry_run=args.dry_run)
    verb = 'Would write' if args.dry_run else 'Wrote'
    for item in written:
        print('%s %s' % (verb, item))
    for item in skipped:
        print('Kept existing %s' % item)
    print('Next: open .aios/verify.json, check the commands are right, then run: aios-verify run')
    return 0


def cmd_run(args):
    root = find_root(args.path)
    if root is None:
        print('No .aios/verify.json here or above. Run: aios-verify init', file=sys.stderr)
        return 2
    results = run_checks(root, gate_only=args.gate_only)
    print(json.dumps(results, indent=2) if args.json else format_results(results))
    return 0 if all(r['passed'] for r in results) else 1


def cmd_scan(args):
    found = staged_secrets(args.path, all_tracked=args.all)
    if not found:
        print('No secrets found in the %s.' % ('uncommitted changes' if args.all else 'staged changes'))
        return 0
    print('Secrets found (values not shown):')
    for name, label in found:
        print('  %s: %s' % (name, label))
    return 1


def cmd_screenshot(args):
    out = take(args.target, out=args.out, size=args.size, cwd=args.path)
    print('Saved %s' % out)
    return 0


def cmd_try(args):
    decision, reason = decide(args.command, args.path, load_extra(args.path))
    print({'deny': 'DENY', 'ask': 'ASK', None: 'ALLOW'}[decision] + ('  ' + reason if reason else ''))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog='aios-verify', description='Checks, a Stop gate and hard-rule hooks.')
    parser.add_argument('--version', action='version', version='aios-verify ' + __version__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='add .aios/verify.json, the verify skill, REVIEW.md and the PR template')
    init.add_argument('--path', default='.')
    init.add_argument('--git-hook', action='store_true', help='also add a git pre-commit hook (for Codex, Cursor and people)')
    init.add_argument('--dry-run', action='store_true')
    init.set_defaults(run=cmd_init)
    run = sub.add_parser('run', help='run every check in .aios/verify.json')
    run.add_argument('--path', default='.')
    run.add_argument('--gate-only', action='store_true', help='skip checks marked "gate": false')
    run.add_argument('--json', action='store_true')
    run.set_defaults(run=cmd_run)
    scan = sub.add_parser('scan', help='look for secrets in the staged changes')
    scan.add_argument('--path', default='.')
    scan.add_argument('--all', action='store_true', help='scan every uncommitted change, not just staged')
    scan.set_defaults(run=cmd_scan)
    shot = sub.add_parser('screenshot', help='screenshot a URL or a local HTML file')
    shot.add_argument('target')
    shot.add_argument('--out', default='.aios/screenshot.png')
    shot.add_argument('--size', default='1280,800')
    shot.add_argument('--path', default='.')
    shot.set_defaults(run=cmd_screenshot)
    try_ = sub.add_parser('try', help='show what the hard-rule hook would do with a command')
    try_.add_argument('command')
    try_.add_argument('--path', default='.')
    try_.set_defaults(run=cmd_try)
    guard = sub.add_parser('guard', help='PreToolUse hook entry point (reads JSON on stdin)')
    guard.set_defaults(run=cmd_guard)
    gate = sub.add_parser('gate', help='Stop hook entry point (reads JSON on stdin)')
    gate.set_defaults(run=cmd_gate)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except (ConfigError, ValueError, OSError, RuntimeError) as exc:
        print('Stopped: %s' % exc, file=sys.stderr)
        return 1
