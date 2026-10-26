"""shelf-decks command line: build the HTML, review it, export the PowerPoint, verify it."""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

from . import brand as brandmod
from . import html_out, layout, pptx_out, review, sample, source

VERSION = '2.0.0'


class Stop(ValueError):
    pass


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def deck_file(value):
    p = Path(value).expanduser().resolve()
    if p.is_dir():
        p = p / 'deck.md'
    if not p.exists():
        raise Stop('Deck not found: %s. Start one with: shelf-decks new <folder>' % p)
    return p


def pick_brand(deck, explicit):
    if explicit:
        return brandmod.load(explicit)
    local = deck.parent / 'brand.json'
    if local.exists():
        return brandmod.load(local)
    return brandmod.load()


def out_dir(deck):
    return deck.parent / 'out'


def versions(deck):
    found = []
    for f in out_dir(deck).glob('deck_v*.html'):
        m = re.fullmatch(r'deck_v(\d+)\.html', f.name)
        if m:
            found.append(int(m.group(1)))
    return sorted(found)


def load_deck(deck, brand_path):
    brand = pick_brand(deck, brand_path)
    meta, slides = source.parse(deck.read_text(), deck.parent)
    return brand, meta, slides


def cmd_build(a):
    deck = deck_file(a.deck)
    brand, meta, slides = load_deck(deck, a.brand)
    built = layout.build_all(slides, brand)
    n = (versions(deck) or [0])[-1] + 1
    out = out_dir(deck)
    out.mkdir(exist_ok=True)
    html = out / ('deck_v%d.html' % n)
    html_out.render(meta, built, brand, html)
    state = {'version': n, 'deck_sha256': sha(deck), 'html_sha256': sha(html), 'brand': brand.get('_file') or 'defaults',
             'slides': len(slides), 'built_at': datetime.datetime.now().isoformat(timespec='seconds')}
    (out / ('deck_v%d.build.json' % n)).write_text(json.dumps(state, indent=2) + '\n')
    print('Built %s (%d slides, brand: %s)' % (html, len(slides), brand.get('name')))
    print('Open it in a browser: arrow keys move, N shows speaker notes.')
    print('Next: shelf-decks review "%s"' % deck)


def latest(deck):
    vs = versions(deck)
    if not vs:
        raise Stop('No HTML build yet. Run: shelf-decks build "%s"' % deck)
    n = vs[-1]
    state = json.loads((out_dir(deck) / ('deck_v%d.build.json' % n)).read_text())
    if state['deck_sha256'] != sha(deck):
        raise Stop('deck.md changed after deck_v%d was built. Build again so the review matches: shelf-decks build "%s"' % (n, deck))
    return n, out_dir(deck) / ('deck_v%d.html' % n), state


def cmd_review(a):
    deck = deck_file(a.deck)
    brand, meta, slides = load_deck(deck, a.brand)
    n, html, _ = latest(deck)
    folder = out_dir(deck) / ('review_v%d' % n)
    built = layout.build_all(slides, brand)
    result = review.review(slides, built, brand, html, folder)
    print(('PASS' if result['ok'] else 'FAIL') + ': review of deck_v%d.html' % n)
    for p in result['problems']:
        print('Problem: ' + p)
    for w in result['warnings']:
        print('Warning: ' + w)
    if result['images']:
        print('Slide images: %s (montage.png shows them all)' % folder)
    print('Report: ' + str(folder / 'review.md'))
    if result['ok']:
        print('Next: look at every slide, then: shelf-decks export "%s"' % deck)
    return 0 if result['ok'] else 1


def cmd_export(a):
    deck = deck_file(a.deck)
    brand, meta, slides = load_deck(deck, a.brand)
    n, html, state = latest(deck)
    report = out_dir(deck) / ('review_v%d' % n) / 'review.json'
    if not report.exists():
        raise Stop('Review deck_v%d first: shelf-decks review "%s"' % (n, deck))
    result = json.loads(report.read_text())
    if result['html_sha256'] != state['html_sha256']:
        raise Stop('The review does not match deck_v%d.html. Review again.' % n)
    if not result['ok']:
        raise Stop('The review of deck_v%d found problems. Fix them, build and review again. See %s' % (n, report.parent / 'review.md'))
    built = layout.build_all(slides, brand)
    target = out_dir(deck) / ('deck_v%d.pptx' % n)
    if target.exists() and not a.replace:
        raise Stop('%s already exists. Build a new version, or pass --replace to write it again.' % target.name)
    pptx_out.render(meta, built, brand, target)
    print('Exported %s (%d slides, editable text)' % (target, len(built)))
    if a.pdf:
        images = [report.parent / f for f in result['images']]
        if not images:
            print('No slide images to make a PDF from (install Playwright and review again).')
        else:
            from PIL import Image
            pages = [Image.open(f).convert('RGB') for f in images]
            pdf = target.with_suffix('.pdf')
            pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=144)
            print('PDF for sharing: %s' % pdf)
    print('Next: shelf-decks verify "%s"' % deck)


def cmd_verify(a):
    deck = deck_file(a.deck)
    brand, meta, slides = load_deck(deck, a.brand)
    n, _, _ = latest(deck)
    target = Path(a.pptx).expanduser() if a.pptx else out_dir(deck) / ('deck_v%d.pptx' % n)
    if not target.exists():
        raise Stop('No PowerPoint to check. Run: shelf-decks export "%s"' % deck)
    result = review.verify(slides, brand, target)
    (target.with_suffix('.verify.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(('PASS' if result['ok'] else 'FAIL') + ': %s, %d slides, %d editable text boxes, fonts: %s' % (
        target.name, result['slides'], result['editable_text_boxes'], ', '.join(result['fonts'])))
    for p in result['problems']:
        print('Problem: ' + p)
    print('Fonts must be installed on the computer that opens the file. Send the PDF when you are not sure.')
    return 0 if result['ok'] else 1


def cmd_new(a):
    folder = Path(a.folder).expanduser().resolve()
    target = folder / 'deck.md'
    if target.exists():
        raise Stop('%s already exists. I will not overwrite a deck.' % target)
    folder.mkdir(parents=True, exist_ok=True)
    b = brandmod.load()
    target.write_text(sample.STARTER.format(title=a.title, name=b['name'],
                                            month=datetime.date.today().strftime('%B %Y')))
    print('Started %s. Write one point per slide, then: shelf-decks build "%s"' % (target, target))


def cmd_sample(a):
    folder = sample.make(a.folder)
    print('Sample deck: %s (fictional Acme Studio, with its own brand.json and logo)' % (folder / 'deck.md'))
    print('Next: shelf-decks build "%s"' % (folder / 'deck.md'))


def cmd_brand(a):
    path = a.brand
    if a.action == 'set':
        if not a.pair or '=' not in a.pair:
            raise Stop('Use: shelf-decks brand set colours.accent=#C2410C')
        key, value = a.pair.split('=', 1)
        file = brandmod.set_value(key.strip(), value.strip(), path)
        print('Saved ' + str(file))
    b = brandmod.load(path)
    shown = {k: v for k, v in b.items() if not k.startswith('_')}
    print(json.dumps(shown, indent=2))
    print('Brand file: ' + (b['_file'] or str(brandmod.default_path()) + ' (not created yet; defaults shown)'))
    if a.action in ('check', 'set'):
        bad = 0
        for item in brandmod.contrast_report(b):
            print('%-36s %5.2f:1  needs %.1f:1  %s' % (item['pair'], item['ratio'], item['needs'], 'ok' if item['ok'] else 'TOO LOW'))
            bad += not item['ok']
        return 1 if bad else 0


def parser():
    p = argparse.ArgumentParser(prog='shelf-decks', description='Build a deck in your own brand: HTML first, then PowerPoint.')
    p.add_argument('--version', action='version', version='shelf-decks ' + VERSION)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('brand', help='Show, set or check your brand')
    s.add_argument('action', nargs='?', choices=['show', 'set', 'check'], default='show')
    s.add_argument('pair', nargs='?')
    s.add_argument('--brand', help='A brand file other than your default')
    s.set_defaults(func=cmd_brand)
    s = sub.add_parser('new', help='Start a deck.md with the basic layouts')
    s.add_argument('folder')
    s.add_argument('--title', default='Untitled deck')
    s.set_defaults(func=cmd_new)
    s = sub.add_parser('sample', help='Make the fictional Acme Studio sample deck')
    s.add_argument('folder')
    s.set_defaults(func=cmd_sample)
    for name, func, text in (('build', cmd_build, 'Write the HTML deck'), ('review', cmd_review, 'Render and check every slide'),
                             ('export', cmd_export, 'Write the editable PowerPoint'), ('verify', cmd_verify, 'Check the PowerPoint')):
        s = sub.add_parser(name, help=text)
        s.add_argument('deck', help='deck.md, or its folder')
        s.add_argument('--brand', help='Brand file (default: brand.json beside the deck, then your settings)')
        if name == 'export':
            s.add_argument('--pdf', action='store_true', help='Also write a PDF of the reviewed slides')
            s.add_argument('--replace', action='store_true', help='Write this version again')
        if name == 'verify':
            s.add_argument('--pptx', help='A PowerPoint other than the latest export')
        s.set_defaults(func=func)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.func(args) or 0
    except (Stop, source.DeckError, brandmod.BrandError, pptx_out.PptxMissing, ValueError) as exc:
        print('Stopped: ' + str(exc), file=sys.stderr)
        return 1
