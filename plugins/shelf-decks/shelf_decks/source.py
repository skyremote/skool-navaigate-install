"""Read a deck written in plain Markdown.

    ---                         optional front matter
    title: Q3 client review
    ---
    [title]                     the layout, on the first line of a slide
    # Q3 client review          the slide title
    ## Acme Studio, October 2026  a subtitle
    - a bullet                  bullets (indent two spaces for a second level)
    plain lines                 a paragraph
    - 42% :: Repeat clients     a stat or a bar (value :: label, or label :: number for bars)
    > A quote                   a quote, with "-- Name, role" under it
    ![alt](images/team.png)     an image, relative to the deck file
    source: Acme CRM, Sept 2026 a source line, required on stat and bars slides
    notes: what to say          speaker notes (may run to the end of the slide)
    ---                         a line with three dashes starts the next slide
"""
import re
from pathlib import Path

LAYOUTS = ('title', 'section', 'bullets', 'two-column', 'stat', 'bars', 'quote', 'image', 'closing')


class DeckError(ValueError):
    pass


def split_front(text):
    meta = {}
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end > 0:
            head = text[4:end]
            if all(':' in line for line in head.splitlines() if line.strip()) and not head.lstrip().startswith('['):
                for line in head.splitlines():
                    if line.strip():
                        key, _, value = line.partition(':')
                        meta[key.strip()] = value.strip()
                text = text[end + 5:]
    return meta, text


def parse(text, base=None):
    meta, body = split_front(text.replace('\r\n', '\n'))
    chunks = re.split(r'\n-{3,}\s*\n', '\n' + body.strip() + '\n')
    slides = []
    for n, chunk in enumerate((c.strip('\n') for c in chunks), 1):
        if chunk.strip():
            slides.append(parse_slide(chunk, n, base))
    if not slides:
        raise DeckError('The deck has no slides. Separate slides with a line of three dashes: ---')
    for i, s in enumerate(slides, 1):
        s['number'] = i
    return meta, slides


def parse_slide(chunk, n, base):
    lines = chunk.split('\n')
    layout = None
    first = lines[0].strip()
    m = re.fullmatch(r'\[([a-z-]+)\]', first)
    if m:
        layout = m.group(1)
        lines = lines[1:]
        if layout not in LAYOUTS:
            raise DeckError('Slide %d: unknown layout [%s]. Use one of: %s' % (n, layout, ', '.join(LAYOUTS)))
    slide = {'layout': layout, 'title': '', 'subtitle': '', 'bullets': [], 'paras': [], 'pairs': [],
             'quote': '', 'by': '', 'image': '', 'alt': '', 'source': '', 'notes': '', 'columns': []}
    notes = []
    in_notes = False
    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if in_notes:
            notes.append(s)
            continue
        if not s:
            continue
        if s.lower().startswith('notes:'):
            in_notes = True
            notes.append(s[6:].strip())
        elif s.startswith('### '):
            slide['columns'].append({'heading': s[4:].strip(), 'bullets': []})
        elif s.startswith('## '):
            slide['subtitle'] = s[3:].strip()
        elif s.startswith('# '):
            slide['title'] = s[2:].strip()
        elif s.startswith('> '):
            slide['quote'] = (slide['quote'] + ' ' + s[2:].strip()).strip()
        elif s.startswith('-- ') or s.startswith('— '):
            slide['by'] = s[3:].strip() if s.startswith('-- ') else s[2:].strip()
        elif re.match(r'!\[[^\]]*\]\([^)]+\)', s):
            alt, src = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', s).groups()
            path = Path(src).expanduser()
            if base and not path.is_absolute():
                path = Path(base) / path
            slide['image'], slide['alt'] = str(path), alt
        elif s.lower().startswith('source:'):
            slide['source'] = s[7:].strip()
        elif s.startswith('- ') or s.startswith('* '):
            item = s[2:].strip()
            level = 1 if (len(line) - len(line.lstrip())) >= 2 else 0
            if '::' in item:
                a, b = (x.strip() for x in item.split('::', 1))
                slide['pairs'].append((a, b))
            elif slide['columns']:
                slide['columns'][-1]['bullets'].append((item, level))
            else:
                slide['bullets'].append((item, level))
        else:
            slide['paras'].append(s)
    slide['notes'] = '\n'.join(notes).strip()
    if not slide['layout']:
        slide['layout'] = guess(slide, n)
    check(slide, n)
    return slide


def guess(slide, n):
    if n == 1:
        return 'title'
    if slide['quote']:
        return 'quote'
    if slide['image']:
        return 'image'
    if len(slide['columns']) == 2:
        return 'two-column'
    if slide['pairs']:
        return 'stat'
    return 'bullets'


def check(slide, n):
    lay = slide['layout']
    if not slide['title'] and lay not in ('quote',):
        raise DeckError('Slide %d [%s] needs a title line starting with "# ".' % (n, lay))
    if lay == 'two-column' and len(slide['columns']) != 2:
        raise DeckError('Slide %d [two-column] needs exactly two "### " headings, one per column.' % n)
    if lay == 'stat' and not 1 <= len(slide['pairs']) <= 3:
        raise DeckError('Slide %d [stat] needs one to three lines like "- 42% :: Repeat clients".' % n)
    if lay == 'bars':
        if not 2 <= len(slide['pairs']) <= 7:
            raise DeckError('Slide %d [bars] needs two to seven lines like "- Bookings :: 42".' % n)
        for label, value in slide['pairs']:
            try:
                float(value.replace(',', '').rstrip('%'))
            except ValueError:
                raise DeckError('Slide %d [bars]: "%s" is not a number. Write "- %s :: 42".' % (n, value, label))
    if lay in ('stat', 'bars') and not slide['source']:
        raise DeckError('Slide %d [%s] shows numbers, so it needs a "source:" line saying whose figures and when.' % (n, lay))
    if lay == 'quote' and not slide['quote']:
        raise DeckError('Slide %d [quote] needs a line starting with "> ".' % n)
    if lay == 'image':
        if not slide['image']:
            raise DeckError('Slide %d [image] needs an image line: ![what it shows](images/file.png)' % n)
        if not Path(slide['image']).exists():
            raise DeckError('Slide %d: image not found: %s' % (n, slide['image']))
        if Path(slide['image']).suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            raise DeckError('Slide %d: use a PNG or JPG image, PowerPoint needs one.' % n)


def words(slide):
    text = ' '.join([slide['subtitle'], slide['quote']] + slide['paras'] + [b for b, _ in slide['bullets']]
                    + [c['heading'] + ' ' + ' '.join(b for b, _ in c['bullets']) for c in slide['columns']]
                    + [a + ' ' + b for a, b in slide['pairs']])
    return len(re.findall(r"[\w'%.,-]+", text))
