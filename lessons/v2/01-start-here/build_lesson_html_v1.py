#!/usr/bin/env python3
"""Turn a lesson_v1.md into paste-ready Skool HTML in the YOUR AIOS 2.0 classroom shell.

Usage: python3 lessons/v2/01-start-here/build_lesson_html_v1.py lessons/v2/<NN>-<slug>/lesson_v1.md
Writes lesson_v1.html beside the source. Handles the subset the lessons use: headings, paragraphs,
lists, tables, fenced code, block quotes (proof boxes), inline code, bold, links and the
[VIDEO: ...] / [SCREENSHOT: ...] markers.
"""
import html
import re
import sys
from pathlib import Path

STYLE = ('body{background:#efeee9;color:#171717;font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0}'
         'main{max-width:900px;margin:40px auto;padding:36px;background:white;border:1px solid #dedbd3;border-radius:12px}'
         'h1{font-size:34px;line-height:1.15}h2{margin-top:36px;font-size:24px;line-height:1.3}h3{font-size:20px;margin-top:30px}'
         'a{color:#765421}pre{background:#f4f1e9;padding:18px;overflow:auto;white-space:pre-wrap;font:14px/1.55 ui-monospace,monospace}'
         'code{font-size:14px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top}'
         'img{width:100%;border-radius:10px}.label{color:#765421;font-size:13px;letter-spacing:1px;text-transform:uppercase}'
         '.note{color:#666;font-size:14px}.byline{color:#666;font-size:14px;margin:0}'
         '.placeholder{border:2px dashed #c9a96a;background:#fbf7ee;border-radius:10px;padding:16px 18px;margin:20px 0;font-size:15px;color:#5a4520}'
         '.proof{border-left:4px solid #765421;background:#f7f4ec;padding:14px 18px;margin:24px 0;border-radius:0 10px 10px 0}'
         '.proof p{margin:6px 0}.resources{margin-top:28px}@media(max-width:650px){main{padding:20px;margin:12px}h1{font-size:28px}}')


def inline(text):
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 1:
            out.append('<code>%s</code>' % html.escape(part[1:-1]))
            continue
        part = html.escape(part, quote=False)
        part = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', part)
        part = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', part)
        part = part.replace(' -- ', ' &ndash; ').replace('—', '&mdash;')
        out.append(part)
    return ''.join(out)


def marker(line, meta):
    m = re.match(r'^\[(VIDEO|SCREENSHOT|NARRATION):\s*([^\]]+)\]$', line.strip())
    if not m:
        return None
    kind, name = m.group(1), m.group(2).strip()
    if kind == 'VIDEO':
        body = ('Tutorial video for this lesson (NavMotion, 1920x1080, narrated in my voice, captions burnt in). '
                'File: <code>%s</code>. Upload it to Skool as this lesson\'s video.' % html.escape(name))
    elif kind == 'NARRATION':
        body = 'Listen to this lesson in my voice. File: <code>%s</code>.' % html.escape(name)
    else:
        body = 'Screenshot: <code>%s</code>. Host it on Backblaze with the lesson media and replace this box with the image.' % html.escape(name)
    return '<div class="placeholder"><span class="label">%s</span><br>%s</div>' % (kind.title(), body)


def convert(md):
    meta = {}
    if md.startswith('---\n'):
        end = md.index('\n---', 4)
        for line in md[4:end].split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                meta[key.strip()] = value.strip().strip('"')
        md = md[end + 4:].lstrip('\n')
    lines = md.split('\n')
    out, i = [], 0
    title = meta.get('title', 'Lesson')
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('# '):
            title = line[2:].strip()
            out.append('<h2>%s</h2><p class="byline">Written by Daniel Wright &middot; NavAIgate</p>' % inline(title))
            if meta.get('narration'):
                out.append(marker('[NARRATION: %s]' % meta['narration'], meta))
            i += 1
            continue
        if line.startswith('## '):
            out.append('<h3>%s</h3>' % inline(line[3:].strip()))
            i += 1
            continue
        if line.startswith('### '):
            out.append('<h4>%s</h4>' % inline(line[4:].strip()))
            i += 1
            continue
        m = marker(line, meta)
        if m:
            out.append(m)
            i += 1
            continue
        if line.startswith('```'):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            i += 1
            out.append('<pre>%s</pre>' % html.escape('\n'.join(code), quote=False))
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.match(r'^:?-+:?$', c) for c in r)]
            table = '<table><tr>%s</tr>' % ''.join('<th>%s</th>' % inline(c) for c in head)
            table += ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in body)
            out.append(table + '</table>')
            continue
        if line.startswith('> '):
            quote = []
            while i < len(lines) and lines[i].startswith('>'):
                quote.append(lines[i][1:].strip())
                i += 1
            text = ' '.join(quote)
            text = re.sub(r'^\*\*Proof:\*\*\s*', '', text)
            out.append('<div class="proof"><span class="label">Proof</span><p>%s</p></div>' % inline(text))
            continue
        if re.match(r'^(\d+\.|-) ', line):
            ordered = bool(re.match(r'^\d+\.', line))
            items = []
            while i < len(lines) and re.match(r'^(\d+\.|-) ', lines[i]):
                item = re.sub(r'^(\d+\.|-) ', '', lines[i])
                i += 1
                while i < len(lines) and lines[i].startswith('   ') and lines[i].strip():
                    item += ' ' + lines[i].strip()
                    i += 1
                items.append('<li>%s</li>' % inline(item))
            tag = 'ol' if ordered else 'ul'
            out.append('<%s>%s</%s>' % (tag, ''.join(items), tag))
            continue
        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#|```|\||> |\d+\. |- |\[(VIDEO|SCREENSHOT))', lines[i]):
            para.append(lines[i].strip())
            i += 1
        text = ' '.join(para)
        if text in ('— Daniel', '- Daniel', '&mdash; Daniel'):
            out.append('<p>&mdash; Daniel</p>')
        else:
            out.append('<p>%s</p>' % inline(text))
    doc = ('<!doctype html><html lang="en-GB"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>%s</title><style>%s</style><main><article>%s</article></main></html>\n'
           % (html.escape(title), STYLE, ''.join(out)))
    return doc


def main():
    for arg in sys.argv[1:]:
        source = Path(arg)
        target = source.with_suffix('.html')
        target.write_text(convert(source.read_text(encoding='utf-8')), encoding='utf-8')
        print('Wrote', target)


if __name__ == '__main__':
    main()
