"""tools-offers: the public Hormozi Growth Engine on the books YOU own, plus the James Smith teaching skill."""
import argparse
import sys
from pathlib import Path

from . import __version__, engine

ENGINE = 'https://github.com/skyremote/hormozi-growth-engine'
JAMES = 'https://github.com/skyremote/james-smith'


def home():
    return Path.home()


def doctor(args):
    print('tools-offers ' + __version__)
    found, agent = engine.installed(home(), args.harness)
    missing = [s for s, ok in found.items() if not ok]
    code = 0
    if missing:
        print('Growth Engine skills missing (%s): %s' % (args.harness, ', '.join(missing)))
        print('Install once: git clone %s ~/hormozi-growth-engine && ~/hormozi-growth-engine/install.sh %s' % (
            ENGINE, 'codex' if args.harness == 'codex' else 'claude'))
        code = 2
    else:
        print('Growth Engine skills: all five installed (%s)%s' % (args.harness, ', with the hormozi agent' if agent else ''))
        state = engine.pointed(home(), args.harness)
        print('Corpus: ' + {'set': 'pointed at your own corpus',
                            'placeholder': 'not pointed yet. Without it the skills run on their summaries and cannot cite pages.'}[state])
        if state == 'placeholder':
            print('Next: tools-offers corpus init ~/Hormozi-corpus, distil your books, then tools-offers corpus point ~/Hormozi-corpus --yes')
    james = any((home() / d / 'james-smith/SKILL.md').is_file() for d in ('.claude/skills', '.codex/skills', '.agents/skills'))
    print('James Smith skill: ' + ('installed' if james else 'optional. git clone %s ~/.claude/skills/james-smith' % JAMES))
    return code


def corpus_init(args):
    made = engine.init(args.root)
    print('Corpus folders ready in %s (%d made). Fill them from the books you own:' % (args.root, len(made)))
    print('  one Markdown file per chapter in <book>/corpus/, your own words, with [p.NNN] page markers inline.')
    print('Never copy the books into it, and never share it.')
    return 0


def corpus_check(args):
    report = engine.coverage(args.root)
    print('%-14s %9s %11s %13s' % ('Book', 'Chapters', 'With pages', 'Page markers'))
    for book, row in report.items():
        print('%-14s %9d %11d %13d' % (book, row['chapters'], row['with_pages'], row['page_markers']))
    if not any(r['with_pages'] for r in report.values()):
        print('No chapter has page markers yet, so Ask Hormozi cannot cite pages.')
        return 1
    return 0


def corpus_point(args):
    changed = engine.point(home(), args.root, args.harness, write=args.yes)
    if not changed:
        print('Nothing to change: no installed engine file still reads %s.' % engine.PLACEHOLDER)
        return 0
    for path in changed:
        print(('Pointed ' if args.yes else 'Would point ') + str(path))
    if not args.yes:
        print('Run again with --yes to write these %d file(s).' % len(changed))
        return 1
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-offers', description=__doc__)
    p.add_argument('--version', action='version', version='tools-offers ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('doctor', help='engine installed? corpus pointed? James Smith skill?')
    s.add_argument('--harness', choices=sorted(engine.HARNESS_DIRS), default='claude')
    s.set_defaults(run=doctor)
    corpus = sub.add_parser('corpus', help='your own corpus from your own books').add_subparsers(dest='action', required=True)
    s = corpus.add_parser('init')
    s.add_argument('root')
    s.set_defaults(run=corpus_init)
    s = corpus.add_parser('check')
    s.add_argument('root')
    s.set_defaults(run=corpus_check)
    s = corpus.add_parser('point')
    s.add_argument('root')
    s.add_argument('--harness', choices=sorted(engine.HARNESS_DIRS), default='claude')
    s.add_argument('--yes', action='store_true')
    s.set_defaults(run=corpus_point)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except engine.EngineError as error:
        print(str(error), file=sys.stderr)
        return 1
