"""Captions: group the kept words into cues, write SRT, draw cue images for burning in.

Burning uses Pillow images and FFmpeg's overlay filter, so it works on FFmpeg builds
without libass (the Homebrew build has no subtitles filter).
"""
import os
import textwrap
from pathlib import Path

from .core import ShelfError
from .plan import inside, to_output

FONT_CANDIDATES = [
    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    '/System/Library/Fonts/Helvetica.ttc',
    '/Library/Fonts/Arial Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',
    'C:/Windows/Fonts/arialbd.ttf',
]


def kept_words(words, removals):
    """Words that survive the cut, retimed to the edited film, with punctuation tidied at each cut."""
    out, dropped = [], []
    for w in words:
        mid = (w['start'] + w['end']) / 2
        if inside(mid, removals):
            dropped.append(w)
            continue
        start, end = to_output(w['start'], removals), to_output(w['end'], removals)
        item = dict(w, start=start, end=max(end, start + 0.05))
        if dropped:
            first = dropped[0]['text']
            # "Erm, the rest" becomes "The rest": a removed word that opened a sentence passes on its capital.
            if first[:1].isupper() and item['text'][:1].islower():
                item['text'] = item['text'][:1].upper() + item['text'][1:]
            # "show you, uh, how" becomes "show you how".
            if out and out[-1]['text'].endswith(',') and dropped[-1]['text'].endswith(','):
                out[-1] = dict(out[-1], text=out[-1]['text'][:-1])
            dropped = []
        out.append(item)
    return out


def build_cues(words, max_chars=36, max_seconds=3.0, gap_break=0.6, uppercase=False):
    cues, current = [], []

    def flush():
        if current:
            text = ' '.join(w['text'] for w in current).strip()
            cues.append({'start': current[0]['start'], 'end': current[-1]['end'],
                         'text': text.upper() if uppercase else text})

    for w in words:
        if current:
            length = len(' '.join(x['text'] for x in current)) + 1 + len(w['text'])
            too_long = length > max_chars
            too_slow = w['end'] - current[0]['start'] > max_seconds
            gap = w['start'] - current[-1]['end'] > gap_break
            sentence = current[-1]['text'].rstrip().endswith(('.', '?', '!'))
            if too_long or too_slow or gap or sentence:
                flush()
                current = []
        current.append(w)
    flush()
    # Hold each cue a moment after its last word, without running into the next cue.
    for i, cue in enumerate(cues):
        limit = cues[i + 1]['start'] if i + 1 < len(cues) else cue['end'] + 0.6
        cue['end'] = round(min(max(cue['end'] + 0.15, cue['start'] + 0.6), limit), 3)
        cue['start'] = round(cue['start'], 3)
    return [c for c in cues if c['end'] > c['start']]


def stamp(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def srt(cues):
    blocks = []
    for n, c in enumerate(cues, 1):
        blocks.append('%d\n%s --> %s\n%s\n' % (n, stamp(c['start']), stamp(c['end']), c['text']))
    return '\n'.join(blocks)


def parse_srt(text):
    cues = []
    for block in text.strip().split('\n\n'):
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        a, b = lines[1].split(' --> ')
        cues.append({'start': _secs(a), 'end': _secs(b), 'text': ' '.join(lines[2:])})
    return cues


def _secs(value):
    hms, ms = value.strip().split(',')
    h, m, s = (int(x) for x in hms.split(':'))
    return h * 3600 + m * 60 + s + int(ms) / 1000.0


def colour(value):
    value = value.lstrip('#')
    if len(value) not in (6, 8):
        raise ShelfError('Colours are hex, such as #FFFFFF or #000000B8 (last two digits are opacity).')
    parts = [int(value[i:i + 2], 16) for i in range(0, len(value), 2)]
    return tuple(parts) if len(parts) == 4 else tuple(parts) + (255,)


def find_font(choice):
    if choice:
        path = Path(os.path.expanduser(choice))
        if not path.exists():
            raise ShelfError('Caption font not found: ' + choice)
        return str(path)
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return ''


def _pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise ShelfError('Burnt-in captions need Pillow. Run: python3 -m pip install --user Pillow')
    return Image, ImageDraw, ImageFont


def draw_cue(text, width, height, style):
    Image, ImageDraw, ImageFont = _pillow()
    size = max(16, int(height * style['size_ratio']))
    font_path = find_font(style.get('font', ''))
    font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    wrap_at = max(10, int(style['max_chars'] * 1.1))
    lines = textwrap.wrap(text, wrap_at)[:2] or ['']
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    line_h = int(size * 1.25)
    text_w = max(b[2] - b[0] for b in boxes)
    pad_x, pad_y = int(size * 0.55), int(size * 0.3)
    box_w = min(width - 40, text_w + 2 * pad_x)
    box_h = line_h * len(lines) + 2 * pad_y
    bottom = height - max(90, int(height * style['margin_ratio']))
    left = (width - box_w) // 2
    top = bottom - box_h
    draw.rounded_rectangle([left, top, left + box_w, bottom], radius=int(size * 0.35), fill=colour(style['box']))
    for i, line in enumerate(lines):
        b = boxes[i]
        x = (width - (b[2] - b[0])) // 2 - b[0]
        y = top + pad_y + i * line_h + (line_h - (b[3] - b[1])) // 2 - b[1]
        draw.text((x, y), line, font=font, fill=colour(style['colour']))
    return image, {'top': top, 'bottom': bottom, 'left': left, 'right': left + box_w}


def overlay_images(cues, width, height, style, folder):
    """Write one transparent PNG per cue plus a blank, and an FFmpeg concat list that times them."""
    Image, _, _ = _pillow()
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    blank = folder / 'blank.png'
    Image.new('RGBA', (width, height), (0, 0, 0, 0)).save(blank)
    entries, cursor, boxes = [], 0.0, []
    for n, cue in enumerate(cues, 1):
        if cue['start'] > cursor + 0.001:
            entries.append((blank, cue['start'] - cursor))
        image, box = draw_cue(cue['text'], width, height, style)
        file = folder / ('cue_%04d.png' % n)
        image.save(file)
        boxes.append(box)
        entries.append((file, cue['end'] - cue['start']))
        cursor = cue['end']
    entries.append((blank, 1.0))
    lines = ['ffconcat version 1.0']
    for file, seconds in entries:
        lines.append("file '%s'" % file.name)
        lines.append('duration %.3f' % max(seconds, 0.001))
    lines.append("file '%s'" % blank.name)
    listing = folder / 'captions.ffconcat'
    listing.write_text('\n'.join(lines) + '\n')
    return listing, boxes
