"""Review: render every slide of the HTML to a PNG, measure overflow, words, contrast. Then check the PPTX."""
import hashlib
import json
from pathlib import Path

from . import brand as brandmod
from . import pptx_out
from .layout import H, W
from .source import words

MAX_WORDS = 60
MAX_BULLETS = 6
PLAYWRIGHT_HINT = ('Slide images need Playwright: python3 -m pip install --user playwright && '
                   'python3 -m playwright install chromium')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def screenshots(html_path, folder, count):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, PLAYWRIGHT_HINT
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': W, 'height': H})
            page.goto(Path(html_path).resolve().as_uri() + '#1')
            page.wait_for_timeout(300)
            page.evaluate('document.fonts.ready')
            overflow = page.evaluate('window.deckCheck()')
            for n in range(1, count + 1):
                page.evaluate('show(%d)' % (n - 1))
                page.wait_for_timeout(60)
                file = folder / ('slide_%02d.png' % n)
                page.screenshot(path=str(file))
                files.append(file)
            browser.close()
    except Exception as exc:  # a missing browser binary is the usual cause
        return None, 'Could not start Chromium (%s). %s' % (str(exc).splitlines()[0][:160], PLAYWRIGHT_HINT)
    return {'files': files, 'overflow': overflow}, ''


def montage(files, out):
    try:
        from PIL import Image
    except ImportError:
        return None
    cols = 4
    tw, th = 480, 270
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16), (40, 40, 40))
    for i, f in enumerate(files):
        with Image.open(f) as im:
            thumb = im.convert('RGB').resize((tw, th))
        sheet.paste(thumb, (16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 16)))
    sheet.save(out)
    return out


def review(slides, built, brand, html_path, folder):
    problems, warnings = [], []
    for item in brandmod.contrast_report(brand):
        if not item['ok']:
            problems.append('Brand contrast too low: %s is %.2f:1, needs %.1f:1. Change a colour with '
                            '"shelf-decks brand set colours.<name>=#hex".' % (item['pair'], item['ratio'], item['needs']))
    for s in slides:
        n = words(s)
        if n > MAX_WORDS:
            warnings.append('Slide %d has %d words. Cut words or split the slide (aim for under %d).' % (
                s['number'], n, MAX_WORDS))
        if len(s['bullets']) > MAX_BULLETS:
            warnings.append('Slide %d has %d bullets. Split it so each slide makes one point.' % (s['number'], len(s['bullets'])))
        if '[' in s['title'] and ']' in s['title']:
            problems.append('Slide %d title still has bracketed template text: %s' % (s['number'], s['title']))
    shots, hint = screenshots(html_path, folder, len(built))
    if shots is None:
        warnings.append(hint + ' Without it, overflow could not be measured.')
        files, overflow = [], []
    else:
        files, overflow = shots['files'], shots['overflow']
        for o in overflow:
            problems.append('Slide %d: the %s text does not fit (needs %d px, has %d px): "%s". Cut words; '
                            'do not shrink the type.' % (o['slide'], o['role'], o['need'], o['have'], o['text']))
    sheet = montage(files, folder / 'montage.png') if files else None
    result = {'html': Path(html_path).name, 'html_sha256': sha(html_path), 'slides': len(built),
              'ok': not problems, 'problems': problems, 'warnings': warnings,
              'images': [f.name for f in files], 'montage': sheet.name if sheet else '',
              'measured': shots is not None, 'contrast': brandmod.contrast_report(brand)}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'review.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = ['# Deck review', '', 'HTML: ' + Path(html_path).name, 'Result: ' + ('PASS' if result['ok'] else 'FAIL'), '']
    lines += ['## Problems (fix before export)', ''] + ['- ' + p for p in problems] + ['' if problems else '- None', '']
    lines += ['## Warnings', ''] + ['- ' + w for w in warnings] + ['' if warnings else '- None', '']
    lines += ['## Look at every slide', '', 'Open `montage.png`, then each `slide_NN.png` at full size. A pass means',
              'nothing overflows and the colours are readable. Only you can judge whether each slide makes its point.', '']
    (folder / 'review.md').write_text('\n'.join(lines))
    return result


def verify(slides, brand, pptx_path):
    """Check the PowerPoint against the deck source: count, text, fonts, colours, notes."""
    info = pptx_out.inspect(pptx_path)
    problems = []
    if (info['width_px'], info['height_px']) != (W, H):
        problems.append('Slide size is %dx%d, expected 16:9.' % (info['width_px'], info['height_px']))
    if len(info['slides']) != len(slides):
        problems.append('PowerPoint has %d slides, the deck has %d.' % (len(info['slides']), len(slides)))
    fonts = {brand['fonts']['heading'], brand['fonts']['body']}
    palette = {v.upper() for v in brand['colours'].values()}
    for s, got in zip(slides, info['slides']):
        joined = ' '.join(got['texts'])
        if s['title'] and s['title'].replace('**', '') not in joined:
            problems.append('Slide %d: the title is missing from the PowerPoint.' % s['number'])
        stray = set(got['fonts']) - fonts
        if stray:
            problems.append('Slide %d uses fonts outside the brand: %s' % (s['number'], ', '.join(sorted(stray))))
        off = {c.upper() for c in got['colours']} - palette
        if off:
            problems.append('Slide %d uses colours outside the brand: %s' % (s['number'], ', '.join(sorted(off))))
        if bool(s['notes']) != got['notes']:
            problems.append('Slide %d: speaker notes did not carry over.' % s['number'])
    return {'ok': not problems, 'problems': problems, 'slides': len(info['slides']),
            'fonts': sorted({f for g in info['slides'] for f in g['fonts']}),
            'editable_text_boxes': sum(len(g['texts']) for g in info['slides'])}
