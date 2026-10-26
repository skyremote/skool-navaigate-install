"""`aios-bb`: bb as the cockpit for your AIOS folder (setup, cards and the daily loop)."""
import argparse
import os
import sys

from . import __version__
from . import cockpit as c


def project_id(bb, args):
    """--project, else the project whose folder this is, else the current bb thread's project."""
    if getattr(args, 'project', None):
        return args.project
    found = c.find_project(bb, args.folder)
    if found:
        return found['id']
    if os.environ.get('BB_PROJECT_ID'):
        return os.environ['BB_PROJECT_ID']
    raise ValueError('No bb project points at %s yet. Run: aios-bb setup' % args.folder)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='aios-bb', description=__doc__)
    parser.add_argument('--version', action='version', version='aios-bb ' + __version__)
    parser.add_argument('--folder', default='.', help='Your AIOS folder (default: this folder)')
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('doctor', help='Check bb, its providers, git and the board')
    s = sub.add_parser('setup', help='Create the bb project for this folder and the four board lanes')
    s.add_argument('--name', help='Project name (default: the folder name)')
    s.add_argument('--dry-run', action='store_true')
    m = sub.add_parser('card', help='Move a thread card: backlog, in-progress, review or done')
    m.add_argument('lane')
    m.add_argument('--thread', help='Thread id or exact title (default: this thread)')
    m.add_argument('--note', help='A short status note for the card')
    t = sub.add_parser('today', help='Start of day: what is waiting, in Review, running and queued')
    t.add_argument('--project')
    h = sub.add_parser('hand', help='Hand a job to a new thread in its own worktree')
    h.add_argument('title')
    h.add_argument('--prompt-file', required=True)
    h.add_argument('--provider', default='claude', choices=['claude', 'codex'])
    h.add_argument('--project')
    h.add_argument('--no-worktree', action='store_true', help='Run in the project folder instead of a worktree')
    h.add_argument('--plan', action='store_true', help='Plan first, then wait for your approval')
    e = sub.add_parser('close', help='End of day: what is in Review, still running and done')
    e.add_argument('--project')
    e.add_argument('--archive-done', action='store_true')
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 2
    bb = c.Bb()
    try:
        if args.cmd == 'doctor':
            rows = c.doctor(bb, args.folder)
            for status, message in rows:
                print('%-4s %s' % (status, message))
            return 1 if any(r[0] == 'FAIL' for r in rows) else 0
        if args.cmd == 'setup':
            project, log = c.setup(bb, args.folder, args.name, args.dry_run)
            print('\n'.join(log))
            if project and not args.dry_run:
                print('Next: open bb, pick "%s" in the sidebar, and start your first thread.' % project.get('name'))
            return 0
        if args.cmd == 'card':
            print(c.move_card(bb, args.thread, args.lane, args.note))
            return 0
        if args.cmd == 'today':
            text, _ = c.today(bb, project_id(bb, args))
            print(text)
            return 0
        if args.cmd == 'hand':
            thread = c.hand(bb, project_id(bb, args), args.title, args.prompt_file, args.provider,
                            not args.no_worktree, args.plan)
            print('Started "%s" (%s) on %s. It is in In progress.' % (args.title, thread.get('id'), args.provider))
            return 0
        if args.cmd == 'close':
            print(c.close(bb, project_id(bb, args), args.archive_done))
            return 0
    except (ValueError, c.BbError) as exc:
        print('Stopped: %s' % exc, file=sys.stderr)
        return 2
    return 2
