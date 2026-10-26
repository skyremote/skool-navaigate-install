"""tools-meetings: Granola transcripts in, a checked decision record out."""
import argparse
import json
import sys
from pathlib import Path

from . import __version__, config, granola, record, sample


def doctor(_args):
    print('tools-meetings ' + __version__)
    print('Python ' + '.'.join(map(str, sys.version_info[:3])) + ': ok')
    try:
        where = config.where('GRANOLA_API_KEY', 'granola_api_key')
    except config.KeyError_ as error:
        print('Granola API key: ' + str(error))
        return 1
    if where:
        print('Granola API key: found in your ' + where + ' (not shown)')
        print('Next: tools-meetings list 5')
        return 0
    print('Granola API key: not set. You can still practise: tools-meetings sample ~/Meetings-practice')
    print(granola.NO_KEY)
    return 2


def key():
    return granola.api_key()


def show_list(args):
    notes = granola.list_notes(args.n, key())
    if args.query:
        notes = [n for n in notes if args.query.lower() in granola.title_of(n).lower()]
    if args.json:
        print(json.dumps([{'id': n.get('id'), 'title': granola.title_of(n), 'date': granola.date_of(n)} for n in notes], indent=2))
        return 0
    if not notes:
        print('No meetings matched. Widen the search: --n 200')
    for n in notes:
        print('%-16s  %-60s  [%s]' % (granola.date_of(n), granola.title_of(n)[:60], n.get('id', '')))
    return 0


def show_summary(args):
    n = granola.note(args.id, key())
    print('# ' + granola.title_of(n) + '\n' + granola.date_of(n))
    people = granola.attendees_of(n)
    if people:
        print('Attendees: ' + ', '.join(people))
    print('\nGranola summary (a summary, not the words said):\n')
    print(n.get('summary_markdown') or n.get('summary_text') or '(no summary)')
    return 0


def show_transcript(args):
    n = granola.note(args.id, key(), transcript=True)
    text = granola.transcript_text(n, me=args.me, raw=args.raw)
    if not text:
        print('This meeting has no transcript yet.')
        return 3
    out = '# %s, transcript\n%s\n\n%s\n' % (granola.title_of(n), granola.date_of(n), text)
    if args.out:
        Path(args.out).expanduser().write_text(out)
        print('Saved the transcript to ' + args.out)
    else:
        print(out)
    return 0


def make_sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    transcript = folder / 'northwind-kickoff_transcript_v1.txt'
    transcript.write_text('# %s, transcript\n%s\n\n%s' % (sample.TITLE, sample.DATE, sample.TRANSCRIPT))
    template = folder / 'northwind-kickoff_record_v1.md'
    if not template.exists():
        template.write_text(record.TEMPLATE.format(title=sample.TITLE, date=sample.DATE, source=transcript.name))
    print('Practice call for the fictional Northwind Bakery and Acme Studio:')
    print('  transcript: ' + str(transcript))
    print('  record to fill in: ' + str(template))
    print('Next: ask your agent to fill in the record, then run tools-meetings check ' + str(template) + ' --source ' + str(transcript))
    return 0


def new_record(args):
    out = Path(args.out).expanduser()
    if out.exists():
        print('Not overwriting ' + str(out) + '. Use a new _v2 name.')
        return 1
    out.write_text(record.TEMPLATE.format(title=args.title, date=args.date or 'date not stated', source=args.source))
    print('Wrote an empty record: ' + str(out))
    return 0


def check_record(args):
    problems = record.check(Path(args.record).expanduser().read_text(), Path(args.source).expanduser().read_text())
    if problems:
        print('FAIL: %d problem(s)' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    print('PASS: every owner, number and quote is in the transcript.')
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-meetings', description=__doc__)
    p.add_argument('--version', action='version', version='tools-meetings ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='check Python and the Granola key').set_defaults(run=doctor)
    s = sub.add_parser('list', help='recent meetings, newest first')
    s.add_argument('n', nargs='?', type=int, default=25)
    s.add_argument('--query', help='only titles containing these words')
    s.add_argument('--json', action='store_true')
    s.set_defaults(run=show_list)
    s = sub.add_parser('search', help='find meetings by title')
    s.add_argument('query')
    s.add_argument('--n', type=int, default=80)
    s.add_argument('--json', action='store_true')
    s.set_defaults(run=show_list)
    s = sub.add_parser('summary', help="Granola's own summary of one meeting")
    s.add_argument('id')
    s.set_defaults(run=show_summary)
    s = sub.add_parser('transcript', help='the words said in one meeting')
    s.add_argument('id')
    s.add_argument('--me', default='Me', help='your name, for your own lines')
    s.add_argument('--raw', action='store_true', help='one line per segment, with timestamps')
    s.add_argument('--out', help='save to this file instead of printing')
    s.set_defaults(run=show_transcript)
    s = sub.add_parser('sample', help='a fictional practice call and an empty record')
    s.add_argument('folder')
    s.set_defaults(run=make_sample)
    s = sub.add_parser('new', help='an empty decision record')
    s.add_argument('out')
    s.add_argument('--title', required=True)
    s.add_argument('--date')
    s.add_argument('--source', required=True, help='the transcript file name')
    s.set_defaults(run=new_record)
    s = sub.add_parser('check', help='check a record against its transcript')
    s.add_argument('record')
    s.add_argument('--source', required=True)
    s.set_defaults(run=check_record)
    sub.add_parser('mcp', help='run as an MCP server (Claude Code starts this for you)')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == 'mcp':
        from .mcp_server import serve
        return serve()
    try:
        return args.run(args)
    except (granola.GranolaError, config.KeyError_) as error:
        print(str(error), file=sys.stderr)
        return 2
    except FileNotFoundError as error:
        print('File not found: ' + str(error.filename), file=sys.stderr)
        return 1
