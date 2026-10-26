"""Write the deck as one self-contained HTML file: fonts, logo and images are embedded."""
import base64
import html
import json
import mimetypes
from pathlib import Path

from .brand import resolve
from .layout import H, W

FALLBACK = "'Helvetica Neue',Arial,sans-serif"


def data_uri(path):
    mime = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(Path(path).read_bytes()).decode())


def font_css(brand):
    out = []
    for role in ('heading', 'body'):
        file = brand['fonts'].get(role + '_file')
        if file:
            path = resolve(brand, file)
            fmt = 'opentype' if path.lower().endswith('.otf') else 'truetype'
            out.append("@font-face{font-family:'%s';src:url(%s) format('%s');font-display:block}" % (
                'Brand' + role.title(), data_uri(path), fmt))
    return ''.join(out)


def family(brand, role):
    name = brand['fonts'][role]
    embedded = "'Brand%s'," % role.title() if brand['fonts'].get(role + '_file') else ''
    return "%s'%s',%s" % (embedded, name.replace("'", ''), FALLBACK)


def element(el, brand, cache):
    style = 'left:%dpx;top:%dpx;width:%dpx;height:%dpx;' % (el['x'], el['y'], el['w'], el['h'])
    if el['kind'] == 'rect':
        return '<div class="r" style="%sbackground:%s"></div>' % (style, el['fill'])
    if el['kind'] == 'image':
        if el['path'] not in cache:
            cache[el['path']] = data_uri(el['path'])
        return '<img class="i" alt="" style="%s" src="%s">' % (style, cache[el['path']])
    justify = {'top': 'flex-start', 'middle': 'center', 'bottom': 'flex-end'}[el['anchor']]
    style += ('justify-content:%s;text-align:%s;font-size:%dpx;line-height:%s;color:%s;font-family:%s;'
              'font-weight:%s;font-style:%s' % (justify, el['align'], el['size'], el['line'], el['colour'],
                                               family(brand, el['font']), 700 if el['bold'] else 400,
                                               'italic' if el['italic'] else 'normal'))
    paras = []
    for i, p in enumerate(el['paras']):
        inner = ''.join('<b>%s</b>' % html.escape(t) if b else html.escape(t) for t, b in p['runs'])
        cls = ' class="b%d"' % p['level'] if p['bullet'] else ''
        gap = el['space'] if i < len(el['paras']) - 1 else 0
        paras.append('<p%s style="margin:0 0 %dpx 0">%s</p>' % (cls, gap, inner))
    return '<div class="t" data-role="%s" style="%s"><div class="in">%s</div></div>' % (el['role'], style, ''.join(paras))


SCRIPT = """
const slides=[...document.querySelectorAll('.s')];let cur=0;
function fit(){const k=Math.min(innerWidth/%(W)d,innerHeight/%(H)d);document.documentElement.style.setProperty('--k',k);}
function show(n){cur=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('on',i===cur));
 history.replaceState(null,'','#'+(cur+1));}
addEventListener('resize',fit);
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))show(cur+1);
 if(['ArrowLeft','PageUp'].includes(e.key))show(cur-1);if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1);
 if(e.key==='n'||e.key==='N')document.body.classList.toggle('notes');});
addEventListener('click',e=>{if(e.target.closest('aside'))return;show(cur+(e.clientX>innerWidth/3?1:-1));});
window.deckCheck=function(){const out=[],was=cur;slides.forEach((s,i)=>{show(i);s.querySelectorAll('.t').forEach(t=>{const n=t.firstElementChild;
 if(n.scrollHeight>t.clientHeight+1||n.scrollWidth>t.clientWidth+1)out.push({slide:i+1,role:t.dataset.role,
 need:n.scrollHeight,have:t.clientHeight,text:t.innerText.slice(0,60)});});});show(was);return out;};
fit();show((parseInt(location.hash.slice(1))||1)-1);
""" % {'W': W, 'H': H}


def render(meta, built, brand, out_path):
    cache = {}
    sections = []
    for s in built:
        notes = '<aside>%s</aside>' % html.escape(s['notes']).replace('\n', '<br>') if s['notes'] else ''
        sections.append('<section class="s" data-layout="%s" style="background:%s">%s%s</section>' % (
            s['layout'], s['background'], ''.join(element(e, brand, cache) for e in s['elements']), notes))
    title = meta.get('title') or (built[0]['title'] if built else 'Deck')
    css = (font_css(brand) +
           'html,body{margin:0;height:100%%;background:#111;overflow:hidden}'
           '.s{position:absolute;left:50%%;top:50%%;width:%dpx;height:%dpx;margin:-%dpx 0 0 -%dpx;transform:scale(var(--k,1));'
           'display:none;overflow:hidden}.s.on{display:block}'
           '.r,.i,.t{position:absolute;box-sizing:border-box}.i{object-fit:contain}'
           '.t{display:flex;flex-direction:column;overflow:hidden}.t p{white-space:pre-wrap;overflow-wrap:break-word}'
           '.b0,.b1{position:relative;padding-left:1.1em}.b1{margin-left:1.2em!important}'
           '.b0:before,.b1:before{content:"\\2022";position:absolute;left:0;color:%s}'
           'aside{display:none;position:absolute;left:40px;right:40px;bottom:40px;background:rgba(0,0,0,.85);color:#fff;'
           'font:28px/1.4 sans-serif;padding:24px;border-radius:8px}body.notes aside{display:block}'
           % (W, H, H // 2, W // 2, brand['colours']['accent']))
    doc = ('<!doctype html><html lang="en-GB"><meta charset="utf-8"><meta name="viewport" content="width=device-width,'
           'initial-scale=1"><title>%s</title><meta name="generator" content="shelf-decks 2.0.0">'
           '<script type="application/json" id="deck-meta">%s</script><style>%s</style><body>%s<script>%s</script></body></html>\n'
           % (html.escape(title), json.dumps({'slides': len(built), 'brand': brand.get('name', '')}), css,
              ''.join(sections), SCRIPT))
    Path(out_path).write_text(doc)
    return out_path
