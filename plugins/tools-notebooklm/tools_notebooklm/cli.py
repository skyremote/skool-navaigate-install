"""tools-notebooklm: turn your own files into NotebookLM notebooks, audio overviews, quizzes and study guides, with the public notebooklm-py CLI."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__, plan

INSTALL = 'pipx install notebooklm-py   (then: notebooklm login, which opens your browser once)'


def doctor(_args):
    print('tools-notebooklm ' + __version__)
    cli = shutil.which('notebooklm')
    if not cli:
        print('notebooklm-py: not installed. ' + INSTALL)
        print('It is an unofficial client for your own Google account; Google can change NotebookLM at any time.')
        return 2
    check = subprocess.run([cli, 'auth', 'check'], capture_output=True, text=True, timeout=60)
    print('notebooklm-py: installed, ' + ('signed in' if check.returncode == 0 else 'not signed in. Run: notebooklm login'))
    return 0 if check.returncode == 0 else 2


def do_plan(args):
    rows = plan.inventory(args.folder)
    good = [r for r in rows if r['ok']]
    for r in rows:
        print('%-4s %-6s %s%s' % ('ok' if r['ok'] else 'SKIP', r['kind'][:6], r['source'], '' if r['ok'] else '  (' + r['why'] + ')'))
    groups = plan.batches(rows)
    print('%d source(s) can go in, %d cannot.' % (len(good), len(rows) - len(good)))
    if len(groups) > 1:
        print('That is more than %d sources, so make %d notebooks (split by topic, not alphabetically).' % (plan.MAX_SOURCES, len(groups)))
    if not good:
        return 1
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'northwind-brief.md').write_text('# Northwind Bakery brief (fictional)\n\nNorthwind takes about 40 cake orders a week by phone. '
                                               'The first version of the booking page takes celebration cakes only.\n')
    (folder / 'meeting-notes.txt').write_text('Kick-off call notes (fictional): layout due Friday; deposit question open.\n')
    (folder / 'links.txt').write_text('https://en.wikipedia.org/wiki/Bakery\n')
    (folder / 'old-plan.pages').write_text('a format NotebookLM does not take')
    print('Practice sources in %s (fictional). Next: tools-notebooklm plan %s' % (folder, folder))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-notebooklm', description=__doc__)
    p.add_argument('--version', action='version', version='tools-notebooklm ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='notebooklm-py installed and signed in?').set_defaults(run=doctor)
    s = sub.add_parser('plan', help='which files and links in a folder can become sources')
    s.add_argument('folder')
    s.set_defaults(run=do_plan)
    s = sub.add_parser('sample', help='a practice folder of sources')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print('notebooklm did not answer. Check your connection.', file=sys.stderr)
        return 2
