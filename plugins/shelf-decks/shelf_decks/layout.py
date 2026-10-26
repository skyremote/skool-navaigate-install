"""Turn each slide into positioned boxes on a 1920 x 1080 canvas.

The HTML and the PowerPoint are both drawn from these boxes, so the two always match:
same positions, same type sizes (1 px here is 0.5 pt in PowerPoint), same colours.
"""
import re

from .brand import resolve

W, H = 1920, 1080
M = 120            # side margin
TITLE_Y, TITLE_H = 96, 170
BODY_Y = 300
FOOT_Y = 1000


def runs(text):
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    return [(p[2:-2], True) if p.startswith('**') and p.endswith('**') else (p, False) for p in parts if p]


def para(text, bullet=False, level=0):
    return {'runs': runs(text), 'bullet': bullet, 'level': level}


def text(x, y, w, h, paras, size, colour, font='body', bold=False, italic=False, align='left',
         anchor='top', line=1.2, space=0, role='body'):
    if isinstance(paras, str):
        paras = [para(paras)]
    return {'kind': 'text', 'x': x, 'y': y, 'w': w, 'h': h, 'paras': paras, 'size': size, 'colour': colour,
            'font': font, 'bold': bold, 'italic': italic, 'align': align, 'anchor': anchor, 'line': line,
            'space': space, 'role': role}


def rect(x, y, w, h, fill):
    return {'kind': 'rect', 'x': x, 'y': y, 'w': w, 'h': h, 'fill': fill}


def image(x, y, w, h, path, fit=True):
    if fit:
        try:
            from PIL import Image
            with Image.open(path) as im:
                iw, ih = im.size
            scale = min(w / iw, h / ih)
            nw, nh = int(iw * scale), int(ih * scale)
            x, y, w, h = x + (w - nw) // 2, y + (h - nh) // 2, nw, nh
        except ImportError:
            pass
    return {'kind': 'image', 'x': x, 'y': y, 'w': w, 'h': h, 'path': path}


def title_box(slide, c, y=TITLE_Y, h=TITLE_H, size=64):
    return text(M, y, W - 2 * M, h, slide['title'], size, c['text'], 'heading', bold=True, anchor='bottom',
                line=1.1, role='title')


def bullet_paras(items):
    return [para(t, bullet=True, level=lvl) for t, lvl in items]


def chrome(slide, brand, total, els):
    """Footer, slide number and small logo on content slides."""
    c = brand['colours']
    footer = brand.get('footer') or brand.get('name') or ''
    els.append(rect(M, FOOT_Y - 24, W - 2 * M, 2, c['surface']))
    els.append(text(M, FOOT_Y, 1200, 40, footer, 22, c['muted'], role='footer'))
    els.append(text(W - M - 200, FOOT_Y, 200, 40, '%d / %d' % (slide['number'], total), 22, c['muted'],
                    align='right', role='footer'))
    if brand.get('logo'):
        els.append(image(W - M - 220, 40, 220, 70, resolve(brand, brand['logo'])))


def build(slide, brand, total):
    c = brand['colours']
    lay = slide['layout']
    bg = c['background']
    els = []
    if lay in ('title', 'closing'):
        if brand.get('logo'):
            els.append(image(M, 90, 360, 120, resolve(brand, brand['logo'])))
        els.append(rect(M, 372, 140, 10, c['accent']))
        els.append(text(M, 410, W - 2 * M, 330, slide['title'], 96, c['text'], 'heading', bold=True,
                        anchor='middle', line=1.05, role='title'))
        sub = slide['subtitle'] or ' '.join(slide['paras'])
        if sub:
            els.append(text(M, 760, W - 2 * M, 140, sub, 40, c['muted'], line=1.25, role='subtitle'))
    elif lay == 'section':
        bg = c['accent']
        els.append(text(M, 380, W - 2 * M, 260, slide['title'], 88, c['accent_text'], 'heading', bold=True,
                        anchor='bottom', line=1.05, role='title'))
        if slide['subtitle']:
            els.append(text(M, 670, W - 2 * M, 120, slide['subtitle'], 40, c['accent_text'], role='subtitle'))
    elif lay == 'bullets':
        els.append(title_box(slide, c))
        paras = [para(p) for p in slide['paras']] + bullet_paras(slide['bullets'])
        if slide['subtitle']:
            els.append(text(M, BODY_Y - 20, W - 2 * M, 60, slide['subtitle'], 32, c['accent'], bold=True, role='kicker'))
        els.append(text(M, BODY_Y + (60 if slide['subtitle'] else 0), W - 2 * M - 200,
                        640 - (60 if slide['subtitle'] else 0), paras, 40, c['text'], line=1.3, space=22))
    elif lay == 'two-column':
        els.append(title_box(slide, c))
        colw = (W - 2 * M - 80) // 2
        for i, col in enumerate(slide['columns']):
            x = M + i * (colw + 80)
            els.append(rect(x, BODY_Y, colw, 8, c['accent']))
            els.append(text(x, BODY_Y + 30, colw, 70, col['heading'], 36, c['text'], 'heading', bold=True, role='heading'))
            els.append(text(x, BODY_Y + 120, colw, 520, bullet_paras(col['bullets']), 34, c['text'], line=1.3, space=18))
    elif lay == 'stat':
        els.append(title_box(slide, c))
        n = len(slide['pairs'])
        gap = 60
        colw = (W - 2 * M - gap * (n - 1)) // n
        for i, (value, label) in enumerate(slide['pairs']):
            x = M + i * (colw + gap)
            els.append(rect(x, BODY_Y + 20, colw, 560, c['surface']))
            els.append(text(x + 40, BODY_Y + 80, colw - 80, 220, value, 140 if n < 3 else 120, c['accent'], 'heading',
                            bold=True, anchor='bottom', line=1.0, role='stat'))
            els.append(text(x + 40, BODY_Y + 330, colw - 80, 220, label, 34, c['text'], line=1.25, role='label'))
        els.append(text(M, 910, W - 2 * M, 40, 'Source: ' + slide['source'], 22, c['muted'], role='source'))
    elif lay == 'bars':
        els.append(title_box(slide, c))
        values = [float(v.replace(',', '').rstrip('%')) for _, v in slide['pairs']]
        top = max(values) or 1.0
        n = len(values)
        row = min(90, 600 // n)
        labelw, barx = 520, M + 560
        maxw = W - M - barx - 180
        for i, ((label, raw), value) in enumerate(zip(slide['pairs'], values)):
            y = BODY_Y + 10 + i * row
            els.append(text(M, y, labelw, row - 16, label, 32, c['text'], anchor='middle', align='right', role='label'))
            width = max(4, int(maxw * value / top))
            els.append(rect(barx, y + 8, width, row - 32, c['accent']))
            els.append(text(barx + width + 16, y, 170, row - 16, raw, 32, c['text'], bold=True, anchor='middle',
                            role='value'))
        els.append(text(M, 910, W - 2 * M, 40, 'Source: ' + slide['source'], 22, c['muted'], role='source'))
    elif lay == 'quote':
        els.append(rect(M, 260, 12, 420, c['accent']))
        els.append(text(M + 70, 230, W - 2 * M - 200, 480, '“' + slide['quote'] + '”', 60, c['text'],
                        'heading', italic=True, anchor='middle', line=1.25, role='quote'))
        if slide['by']:
            els.append(text(M + 70, 740, W - 2 * M - 200, 60, slide['by'], 32, c['muted'], role='by'))
        if slide['title']:
            els.append(text(M + 70, 150, W - 2 * M - 200, 60, slide['title'], 28, c['accent'], bold=True, role='kicker'))
    elif lay == 'image':
        split = 760
        els.append(text(M, 200, split - M - 40, 300, slide['title'], 64, c['text'], 'heading', bold=True,
                        anchor='bottom', line=1.1, role='title'))
        body = [para(p) for p in slide['paras']] + bullet_paras(slide['bullets'])
        if body:
            els.append(text(M, 540, split - M - 40, 400, body, 32, c['text'], line=1.35, space=16))
        els.append(image(split + 40, 130, W - split - 40 - M, 780, slide['image']))
        if slide['alt']:
            els.append(text(split + 40, 922, W - split - 40 - M, 36, slide['alt'], 20, c['muted'], align='center',
                            role='caption'))
    if lay not in ('title', 'closing', 'section'):
        chrome(slide, brand, total, els)
    return {'number': slide['number'], 'layout': lay, 'background': bg, 'elements': els, 'notes': slide['notes'],
            'title': slide['title']}


def build_all(slides, brand):
    return [build(s, brand, len(slides)) for s in slides]
