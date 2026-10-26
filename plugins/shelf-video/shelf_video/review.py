"""A static review page: the plan beside the original recording. No server, no network."""
import html
from pathlib import Path

PAGE = """<!doctype html><html lang="en-GB"><meta charset="utf-8"><title>Edit plan review</title>
<style>body{font:16px/1.5 -apple-system,Segoe UI,sans-serif;margin:24px;background:#f6f5f1;color:#1c1c1c}
video{width:100%%;max-width:860px;border-radius:8px;background:#000}table{border-collapse:collapse;width:100%%;margin-top:18px}
td,th{border-bottom:1px solid #ddd;padding:8px;text-align:left;vertical-align:top}tr.cut td{background:#fff4e5}
button{font:inherit;padding:4px 10px;border-radius:6px;border:1px solid #999;background:#fff;cursor:pointer}
.k{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:#7a5a20}p.note{color:#555}</style>
<h1>Edit plan review</h1>
<p>%(summary)s</p>
<p class="note">Press <b>Hear it</b> to play two seconds either side of a proposal. Rows marked CUT are selected.
Nothing is cut until you approve. Tell your agent which numbers to drop or add, then approve it yourself.</p>
<video id="v" controls preload="metadata" src="%(src)s"></video>
<table><tr><th>#</th><th>Decision</th><th>Kind</th><th>Time</th><th>Words</th><th>Why</th><th></th></tr>%(rows)s</table>
<script>const v=document.getElementById('v');let stopAt=null;
function hear(a,b){v.currentTime=Math.max(0,a-2);stopAt=b+2;v.play();}
v.addEventListener('timeupdate',()=>{if(stopAt!==null&&v.currentTime>=stopAt){v.pause();stopAt=null;}});</script></html>
"""


def page(cuts, source, summary_text):
    rows = []
    for c in cuts:
        rows.append('<tr class="%s"><td>%d</td><td>%s</td><td class="k">%s</td><td>%.2f&ndash;%.2f s</td>'
                    '<td>%s</td><td>%s</td><td><button onclick="hear(%.3f,%.3f)">Hear it</button></td></tr>' % (
                        'cut' if c['selected'] else '', c['id'], 'CUT' if c['selected'] else 'keep',
                        html.escape(c['kind']), c['start'], c['end'], html.escape(c['text']) or '(silence)',
                        html.escape(c['reason']), c['start'], c['end']))
    return PAGE % {'summary': html.escape(summary_text), 'src': html.escape(Path(source).as_uri()),
                   'rows': ''.join(rows)}
