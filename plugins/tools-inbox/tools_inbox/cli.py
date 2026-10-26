"""tools-inbox: triage that never sends. Composio on your own account; drafts only; reminders to yourself only."""
import argparse
import sys
from datetime import date
from pathlib import Path

from . import __version__, composio, config, guard, triage

SAMPLE = """# Inbox brief: practice (fictional Acme Studio inbox)

Read-only: nothing was sent, archived or deleted.

## Action needed
- From: Priya at Northwind Bakery | Date: Mon 20 Oct | Subject: Layout sign-off | Why: she asks for the layout by Friday | Draft: Thanks Priya, the layout comes to you on Friday morning.
- From: Contoso accounts | Date: Tue 21 Oct | Subject: PO number for October | Why: they need the PO on the invoice | Draft: none

## Waiting on
- From: Tom at Northwind Bakery | Date: Mon 20 Oct | Subject: Cake photos | Why: the six photos he promised

## FYI
- From: Hosting provider | Date: Wed 22 Oct | Subject: Renewal receipt | Why: receipt for your books
"""


def doctor(_args):
    print('tools-inbox ' + __version__)
    try:
        where = config.where('COMPOSIO_API_KEY', 'composio_api_key')
    except config.KeyError_ as error:
        print('Composio API key: ' + str(error))
        return 1
    print('Sending guard: on (every MCP tool that sends, replies or forwards email is blocked; drafts are allowed)')
    if not where:
        print('Composio API key: not set. The triage method still works with any Gmail MCP you have connected.')
        print('Practise first: tools-inbox sample ~/Inbox-practice')
        print(composio.NO_KEY)
        return 2
    print('Composio API key: found in your ' + where + ' (not shown)')
    print('Next: tools-inbox accounts')
    return 0


def show_accounts(_args):
    rows = composio.accounts(composio.api_key())
    if not rows:
        print('No connected accounts yet. Connect Gmail in the Composio dashboard.')
        return 1
    for row in rows:
        print('%-14s %-8s %-30s %s' % (row['toolkit'], row['status'], row['user_id'] or '(no address shown)', row['id']))
    return 0


def new_brief(args):
    out = Path(args.out).expanduser()
    if out.exists():
        print('Not overwriting ' + str(out) + '. Use a new _v2 name.')
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(triage.TEMPLATE.format(date=args.date or date.today().isoformat()))
    print('Wrote an empty brief: ' + str(out))
    return 0


def check_brief(args):
    text = Path(args.brief).expanduser().read_text()
    problems = triage.check(text)
    if problems:
        print('FAIL: %d problem(s)' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    counts = triage.count(text)
    print('PASS: %d need action, %d waiting, %d FYI. Nothing was sent.' % (
        counts.get('Action needed', 0), counts.get('Waiting on', 0), counts.get('FYI', 0)))
    return 0


def make_sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'inbox-brief_practice_v1.md'
    path.write_text(SAMPLE)
    print('Practice brief for the fictional Acme Studio inbox: ' + str(path))
    print('Next: tools-inbox check ' + str(path))
    return 0


def remind(args):
    if not args.yes:
        print('A reminder sends one email to your own address. Add --yes once you have read the subject and body.')
        return 1
    own = composio.remind(composio.api_key(), args.subject, args.body, account_id=args.account, to=args.to)
    print('Sent the reminder to your own address, ' + own + '.')
    return 0


def schedule_line(args):
    command = '%s remind --subject %s --body %s --yes' % (
        str(Path(sys.argv[0]).resolve()) if sys.argv and sys.argv[0] else 'tools-inbox',
        _quote(args.subject), _quote(args.body))
    print('# Add this line with: crontab -e   (a sleeping laptop skips it; use an always-on machine for must-arrive reminders)')
    print('%s  %s >> /tmp/tools-inbox-reminder.log 2>&1' % (args.cron, command))
    return 0


def _quote(text):
    return "'" + text.replace("'", "'\\''") + "'"


def parser():
    p = argparse.ArgumentParser(prog='tools-inbox', description=__doc__)
    p.add_argument('--version', action='version', version='tools-inbox ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='check the key and the sending guard').set_defaults(run=doctor)
    sub.add_parser('accounts', help='your Composio connections (Gmail, Calendar)').set_defaults(run=show_accounts)
    s = sub.add_parser('new', help='an empty triage brief')
    s.add_argument('out')
    s.add_argument('--date')
    s.set_defaults(run=new_brief)
    s = sub.add_parser('check', help='check a triage brief')
    s.add_argument('brief')
    s.set_defaults(run=check_brief)
    s = sub.add_parser('sample', help='a fictional practice brief')
    s.add_argument('folder')
    s.set_defaults(run=make_sample)
    s = sub.add_parser('remind', help='send ONE reminder to your own address')
    s.add_argument('--subject', required=True)
    s.add_argument('--body', required=True)
    s.add_argument('--account', help='the ca_... id, if you connected more than one Gmail')
    s.add_argument('--to', help='only your own address is accepted')
    s.add_argument('--yes', action='store_true')
    s.set_defaults(run=remind)
    s = sub.add_parser('schedule', help='print a cron line for a recurring reminder (writes nothing)')
    s.add_argument('--cron', default='0 8 * * 1-5', help='cron timing, default weekdays at 8am')
    s.add_argument('--subject', required=True)
    s.add_argument('--body', required=True)
    s.set_defaults(run=schedule_line)
    sub.add_parser('guard', help='the PreToolUse hook (Claude Code runs this)')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == 'guard':
        return guard.main()
    try:
        return args.run(args)
    except (composio.ComposioError, config.KeyError_) as error:
        print(str(error), file=sys.stderr)
        return 2
    except FileNotFoundError as error:
        print('File not found: ' + str(error.filename), file=sys.stderr)
        return 1
