"""tools-research: research papers, Substack and Reddit with links, and a findings ledger with honest confidence labels."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

from . import __version__, config, ledger, sources

SAMPLE = """# Research: do small bakeries benefit from online cake ordering? (practice)

Question: do small bakeries benefit from online cake ordering?
Date: 2026-10-26

## Findings
- Owners report fewer missed phone orders after adding online ordering. | Source: https://reddit.com/r/smallbusiness/comments/example1 | Kind: practitioner | Confidence: low
- Online ordering studies in food retail show higher average order values. | Source: https://doi.org/10.0000/example | Kind: paper | Confidence: medium
- A bakery newsletter describes moving celebration cakes online first. | Source: https://example.substack.com/p/cakes-online | Kind: newsletter | Confidence: low

## Where sources disagree
- None found in this practice ledger.

## What we could not find
- Numbers for bakeries under ten staff.
"""


def show(rows, as_json, fmt):
    if as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    if not rows:
        print('Nothing found. Try other words.')
        return 1
    for row in rows:
        print(fmt(row))
    return 0


def doctor(_args):
    print('tools-research ' + __version__)
    print('Research papers (OpenAlex): free, no key.' + (' Polite-pool email: set.' if config.where('OPENALEX_EMAIL', 'openalex_email') else ''))
    print('Substack: free, no key (public posts only).')
    reddit = config.where('REDDIT_CLIENT_ID', 'reddit_client_id') and config.where('REDDIT_CLIENT_SECRET', 'reddit_client_secret')
    print('Reddit: ' + ('your app id and secret are set (not shown)' if reddit else 'needs your own free Reddit app. Run: tools-research reddit search "test" for the steps.'))
    print('YouTube consensus: optional, the public consensus skill (github.com/GoodLadTom/consensus) on your own Supadata key.')
    return 0 if reddit else 2


def papers(args):
    return show(sources.papers(args.query, args.n, most_cited=args.most_cited), args.json,
                lambda r: '%s (%s), cited %d\n  %s%s' % (r['title'], r['year'], r['cited_by'], r['url'],
                                                         '\n  free PDF: ' + r['free_pdf'] if r['free_pdf'] else ''))


def substack(args):
    if args.action == 'archive':
        return show(sources.substack_archive(args.target, args.n), args.json,
                    lambda r: '%s  %s%s\n  %s' % (r['date'], r['title'], ' (paid)' if r['paid'] else '', r['url']))
    post = sources.substack_post(args.target)
    if args.json:
        print(json.dumps(post, indent=2, ensure_ascii=False))
    else:
        print('# %s\n%s  %s\n\n%s' % (post['title'], post['date'], post['url'], post['text']))
    return 0


def reddit(args):
    if args.action == 'search':
        return show(sources.reddit_search(args.target, args.n, args.period, args.subreddit), args.json,
                    lambda r: 'r/%s  %d points, %d comments  %s\n  %s' % (r['subreddit'], r['score'], r['comments'], r['title'], r['url']))
    thread = sources.reddit_thread(args.target, args.n)
    if args.json:
        print(json.dumps(thread, indent=2, ensure_ascii=False))
        return 0
    print('# %s\n%s\n\n%s\n' % (thread['title'], thread['url'], thread['text']))
    for c in thread['top_comments']:
        print('[%d] %s\n' % (c['score'], c['text']))
    return 0


def new(args):
    out = Path(args.out).expanduser()
    if out.exists():
        print('Not overwriting %s. Use a new _v2 name.' % out)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(ledger.TEMPLATE.format(question=args.question, date=date.today().isoformat()))
    print('Wrote an empty findings ledger: %s' % out)
    return 0


def check(args):
    problems = ledger.check(Path(args.ledger).expanduser().read_text())
    if problems:
        print('FAIL: %d problem(s)' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    print('PASS: every finding has a link, a kind of source and a confidence label.')
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'bakery-ordering_ledger_practice_v1.md'
    path.write_text(SAMPLE)
    print('A practice findings ledger (fictional links): %s\nNext: tools-research check %s' % (path, path))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-research', description=__doc__)
    p.add_argument('--version', action='version', version='tools-research ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='which sources are ready').set_defaults(run=doctor)
    s = sub.add_parser('papers', help='research papers (OpenAlex, free)')
    s.add_argument('query')
    s.add_argument('--n', type=int, default=8)
    s.add_argument('--most-cited', action='store_true', help='sort by citations instead of relevance')
    s.add_argument('--json', action='store_true')
    s.set_defaults(run=papers)
    s = sub.add_parser('substack', help='a publication\'s posts, or one post\'s text (free)')
    s.add_argument('action', choices=['archive', 'post'])
    s.add_argument('target', help='a publication name or address, or a post link')
    s.add_argument('--n', type=int, default=10)
    s.add_argument('--json', action='store_true')
    s.set_defaults(run=substack)
    s = sub.add_parser('reddit', help='search Reddit or read a thread (your own free Reddit app)')
    s.add_argument('action', choices=['search', 'thread'])
    s.add_argument('target', help='search words, or a thread link or id')
    s.add_argument('--n', type=int, default=10)
    s.add_argument('--period', default='year', choices=['day', 'week', 'month', 'year', 'all'])
    s.add_argument('--subreddit')
    s.add_argument('--json', action='store_true')
    s.set_defaults(run=reddit)
    s = sub.add_parser('new', help='an empty findings ledger')
    s.add_argument('out')
    s.add_argument('--question', required=True)
    s.set_defaults(run=new)
    s = sub.add_parser('check', help='check a findings ledger')
    s.add_argument('ledger')
    s.set_defaults(run=check)
    s = sub.add_parser('sample', help='a practice ledger')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except (sources.SourceError, config.KeyError_) as error:
        print(str(error), file=sys.stderr)
        return 2
    except FileNotFoundError as error:
        print('File not found: ' + str(error.filename), file=sys.stderr)
        return 1
