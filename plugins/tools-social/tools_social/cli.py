"""tools-social: one source to every platform on your own Blotato account, and nothing goes out without a release time."""
import argparse
import json
import sys
from pathlib import Path

from . import __version__, posts, release


def doctor(_args):
    print('tools-social ' + __version__)
    print('Release gate: on (Blotato posts and reschedules need "publish now", or a date, time and timezone you gave)')
    receipt = release.load()
    print('Current release on record: ' + (receipt['level'] + (' at ' + receipt['local'] if receipt.get('local') else '')
                                           if receipt else 'none'))
    print('Blotato: connect it in your harness (README, Install). In Claude Code the plugin adds it when your key is set.')
    return 0


def do_release(args):
    if args.level == 'clear':
        path = release.receipt_path()
        if path.exists():
            path.unlink()
        print('Release cleared. Nothing can be posted until the member gives a time again.')
        return 0
    try:
        receipt = release.live(args.words) if args.level == 'now' else release.scheduled(args.words, args.at or '', args.tz or '')
    except release.ReleaseError as error:
        print('READY, not released: ' + str(error))
        return 1
    release.save(receipt)
    if receipt['level'] == 'live':
        print('LIVE: the member asked to publish now. Valid for 30 minutes.')
    else:
        print('SCHEDULED: %s, which is %s. Pass scheduledTime=%s to Blotato. Valid for 30 minutes.' % (
            receipt['local'], receipt['utc'], receipt['utc']))
    return 0


def check(args):
    problems = posts.check(posts.load(args.pack))
    if problems:
        print('FAIL: %d problem(s)' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    print('PASS: every platform has three hooks, fits its limits, and promises nothing it cannot deliver.')
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'northwind_posts_v1.json'
    path.write_text(json.dumps(posts.SAMPLE, indent=2))
    print('A practice post pack for the fictional Northwind Bakery: ' + str(path))
    print('Next: tools-social check ' + str(path))
    return 0


def gate(_args):
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    reason = release.decide(str(event.get('tool_name', '')), event.get('tool_input') or {}, release.load())
    if reason:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                                 'permissionDecisionReason': reason}}))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-social', description=__doc__)
    p.add_argument('--version', action='version', version='tools-social ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='the release gate and what is on record').set_defaults(run=doctor)
    s = sub.add_parser('release', help="record the member's release instruction")
    s.add_argument('level', choices=['now', 'schedule', 'clear'])
    s.add_argument('--words', default='', help="the member's exact words")
    s.add_argument('--at', help='local date and time, YYYY-MM-DDTHH:MM')
    s.add_argument('--tz', help='timezone name, e.g. Europe/London')
    s.set_defaults(run=do_release)
    s = sub.add_parser('check', help='check a post pack (JSON)')
    s.add_argument('pack')
    s.set_defaults(run=check)
    s = sub.add_parser('sample', help='a fictional practice pack')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    sub.add_parser('gate', help='the PreToolUse hook (Claude Code runs this)').set_defaults(run=gate)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except FileNotFoundError as error:
        print('File not found: ' + str(error.filename), file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError) as error:
        print('Could not read that file: ' + str(error), file=sys.stderr)
        return 1
