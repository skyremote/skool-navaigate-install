"""Sandbox steps for shelf-decks, run by tests/shelf-video/sandbox_proof.py shelf-decks."""
from pathlib import Path


def run(r, home, work):
    browsers = Path.home() / 'Library/Caches/ms-playwright'
    if browsers.is_dir():
        # Chromium is a tool, like FFmpeg: reuse the copy already downloaded on this Mac.
        r.env['PLAYWRIGHT_BROWSERS_PATH'] = str(browsers)
    work.mkdir(parents=True, exist_ok=True)
    deck = work / 'acme-sample'
    r.run(['python3', '-m', 'pip', 'install', '--user', '--disable-pip-version-check', 'python-pptx', 'Pillow', 'playwright'],
          note='The tools step from the README. They are already present for this Python, so pip only confirms them.')
    r.run(['shelf-decks', '--version'])
    r.run(['shelf-decks', 'brand', 'check'], note='A new member has no brand yet, so the defaults show.')
    r.run(['shelf-decks', 'brand', 'set', 'colours.accent=orange'], expect=1, note='Colours must be hex.')
    r.run(['shelf-decks', 'brand', 'set', 'name=Acme Studio'])
    r.run(['shelf-decks', 'brand', 'set', 'colours.accent=#C2410C'])
    r.run(['shelf-decks', 'sample', deck])
    r.run(['cat', deck / 'deck.md'])
    r.run(['shelf-decks', 'export', deck], expect=1, note='Export refuses before an HTML build.')
    r.run(['shelf-decks', 'build', deck])
    r.run(['shelf-decks', 'export', deck], expect=1, note='Export refuses before a review.')
    r.run(['shelf-decks', 'review', deck])
    r.run(['ls', deck / 'out/review_v1'])
    r.run(['shelf-decks', 'export', deck, '--pdf'])
    r.run(['shelf-decks', 'verify', deck])
    long = work / 'too-long'
    long.mkdir()
    (long / 'deck.md').write_text('# Too long\n\n---\n# One slide, far too many words\n' + ' '.join(['word'] * 300) + '\n')
    r.run(['shelf-decks', 'build', long], note='A deliberately overfull slide, to prove review catches it.')
    r.run(['shelf-decks', 'review', long], expect=1)
