/* Deck engine — live animated/interactive diagram slides (HTML only).
   A profile-driven registry of diagram KINDS, graduated from a one-off
   post-processor. Each kind is a pure (data, P, slide) -> { html, css }
   function. ALL colours come from the profile P (via colorOf), ALL content
   comes from slide.data — nothing brand-specific is baked here. The PPTX/PDF
   path bakes these slides to a flat picture (see builders-pptx B.diagram).

   Factory: require("./diagrams.js")() -> { html, css, KINDS }
     html(slide, P) -> the diagram's inner HTML for one <section>.
     css(kind)      -> the static CSS that kind needs (de-duped by render.js).
     KINDS          -> the list of registered diagram kinds.

   render.js injects each used kind's css once, plus the shared chrome CSS and
   the hover-popup JS engine, only when a deck actually contains a diagram. */

const { colorOf } = require("./profiles.js");

const esc = (s) => String(s == null ? "" : s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

module.exports = function () {
  // ---- shared chrome (kicker / title / viz / legend / footer) ----
  // Reads kicker+title+footer from the slide and the bottom brand line from P.
  function chrome(P, o, viz, legend, hint) {
    const h = hint ? `<div class="dhint">${esc(hint)}</div>` : "";
    const leg = legend ? `<div class="dleg">${legend}</div>` : "";
    const brand = esc(P.label || "");
    const foot = o.footer ? esc(o.footer) : "";
    return `<div class="dwrap">${h}<div class="kick">${esc(o.kicker)}</div>`
      + `<div class="dtitle">${esc(o.title)}</div><div class="dviz">${viz}</div>${leg}`
      + `<div class="dfoot"><span><b>${brand}</b></span>`
      + `<span>${foot}</span></div></div>`;
  }
  const swatch = (c, label, extra = "") =>
    `<span class="k"><span class="sw" style="background:${c}${extra}"></span>${esc(label)}</span>`;

  // ---- registry: kind -> { html(data,P,slide), css(P) } ----
  const KIND = {};

  // relationship — a central hub with N satellite nodes, coloured edges, an
  // optional live "re-score" fragment that fades in over an existing node.
  KIND.relationship = {
    html(data, P, o) {
      const hx = (t) => "#" + colorOf(P, t);
      const nodes = data.nodes || [];
      const hx0 = data.hubX != null ? data.hubX : 150;
      const hy = data.hubY != null ? data.hubY : 255;
      const sx = hx0 + 62;
      let edges = "";
      nodes.forEach((n, i) => {
        const x = n.x, y = n.y, ex = x, ey = y + 22;
        const L = Math.round(Math.hypot(ex - sx, ey - hy)) + 2;
        const dotted = n.link === "dotted";
        const dash = dotted ? ` stroke-dasharray="2,7"` : "";
        const col = dotted ? hx("mutedL") : hx("slate2");
        const w = dotted ? "1.6" : "2.4";
        edges += `<line class="redge" style="--i:${i};--len:${L}px" x1="${sx}" y1="${hy}" x2="${ex}" y2="${ey}" `
          + `stroke="${col}" stroke-width="${w}" stroke-dasharray="${L}"${dash}/>`;
      });
      let cards = "";
      nodes.forEach((n, i) => {
        const tone = n.tone || "accent";
        const bar = hx(n.color || "muted");
        cards += `<g class="rnode" style="--i:${i}" data-pop data-tone="${esc(tone)}" data-title="${esc(n.name)}" data-desc="${esc(n.note || "")}">`
          + `<rect x="${n.x}" y="${n.y}" rx="9" width="232" height="58" fill="#FFFFFF" stroke="${hx("line")}"/>`
          + `<rect x="${n.x}" y="${n.y}" rx="9" width="6" height="58" fill="${bar}"/>`
          + `<text x="${n.x + 22}" y="${n.y + 25}" font-family="${P.htmlDisplay}" font-weight="700" font-size="18" fill="${hx("slate")}">${esc(n.name)}</text>`
          + `<text x="${n.x + 22}" y="${n.y + 45}" font-family="${P.htmlFont}" font-size="12.5" fill="${hx("muted")}">${esc(n.role || "")}</text></g>`;
      });
      const hub = data.hub || {};
      const hubG = `<g class="rhub"><rect x="${hx0 - 66}" y="${hy - 31}" rx="10" width="132" height="62" fill="${hx("accentD")}"/>`
        + `<text x="${hx0}" y="${hy - 3}" text-anchor="middle" font-family="${P.htmlDisplay}" font-weight="700" font-size="19" fill="#fff">${esc(hub.title || "")}</text>`
        + `<text x="${hx0}" y="${hy + 17}" text-anchor="middle" font-family="${P.htmlFont}" font-size="11.5" fill="${hx("accentL")}">${esc(hub.sub || "")}</text></g>`;
      let rescore = "";
      const rs = data.rescore;
      if (rs) {
        const itx = rs.x, ity = rs.y;
        rescore = `<g class="rescore">`
          + `<line x1="${itx}" y1="${ity + 22}" x2="${hx0 + 62}" y2="${hy}" stroke="${hx("coral")}" stroke-width="2" stroke-dasharray="2,7"/>`
          + `<rect x="${itx}" y="${ity}" rx="9" width="6" height="58" fill="${hx("coral")}"/>`
          + `<rect x="${itx + 150}" y="${ity - 30}" rx="6" width="150" height="26" fill="${hx("coral")}"/>`
          + `<text x="${itx + 225}" y="${ity - 12}" text-anchor="middle" font-family="${P.htmlDisplay}" font-weight="700" font-size="12" fill="#fff">${esc(rs.label || "")}</text></g>`;
      }
      const svg = `<svg viewBox="0 0 1080 540" preserveAspectRatio="xMidYMid meet" class="relsvg">${edges}${hubG}${cards}${rescore}</svg>`;
      const legend = (data.legend || []).map(l =>
        swatch(hx(l.color || "muted"), l.label, l.dashed ? `;border:1.5px dashed ${hx("mutedL")}` : "")).join("");
      const viz = `<div class="relmap" style="position:absolute;inset:0">${chrome(P, o, svg, legend, o.hint)}</div>`;
      return viz;
    },
  };

  // matrix — a buying/coverage grid generalised: rows x columns of cells whose
  // state ('own' filled / 'open' dashed / 'play' highlighted, hoverable) is
  // supplied per cell. The 'play' cells carry a popup with the ranked move.
  KIND.matrix = {
    html(data, P, o) {
      const hx = (t) => "#" + colorOf(P, t);
      const cols = data.columns || [];
      const rows = data.rows || [];
      const states = data.states || {
        own: { fill: `background:${hx("accentD")}` },
        open: { fill: `background:transparent;border:1.5px dashed ${hx("mutedL")}` },
        play: { fill: `background:${hx("coral")}1A;border:2px solid ${hx("coral")}` },
      };
      const rowHeadLabel = data.rowHead || "";
      const th = cols.map(c =>
        `<th style="font-size:13px;font-weight:600;color:${hx("muted")};padding:8px 6px;text-align:center;border-bottom:1px solid ${hx("mutedL")}">${esc(c)}</th>`).join("");
      let body = "", idx = 0;
      rows.forEach((r) => {
        let tds = "";
        (r.cells || []).forEach((cell) => {
          idx += 1;
          const kind = typeof cell === "string" ? cell : (cell.state || "open");
          const st = (states[kind] && states[kind].fill) || states.open.fill;
          let dataAttr = "";
          let cls = "wcell";
          if (kind === "play") {
            cls = "wcell wplay";
            const pd = (typeof cell === "object" && cell.note) || "";
            const pt = (typeof cell === "object" && cell.title) || "Ranked play";
            dataAttr = ` data-pop data-tone="coral" data-title="${esc(pt)}" data-desc="${esc(pd)}"`;
          }
          tds += `<td style="padding:8px 6px;text-align:center;border-bottom:1px solid ${hx("line")}">`
            + `<span class="${cls}"${dataAttr} style="--i:${idx};${st};width:46px;height:26px;border-radius:5px;display:inline-block"></span></td>`;
        });
        body += `<tr><td style="text-align:left;font-size:16px;color:${hx("slate")};font-weight:500;padding:8px 6px;border-bottom:1px solid ${hx("line")}">${esc(r.label)}</td>${tds}</tr>`;
      });
      const table = `<table class="wstable" style="border-collapse:collapse;width:100%">`
        + `<tr><th style="text-align:left;font-size:13px;font-weight:600;color:${hx("muted")};padding:8px 6px;border-bottom:1px solid ${hx("mutedL")};width:210px">${esc(rowHeadLabel)}</th>${th}</tr>${body}</table>`;
      const legend = (data.legend || []).map(l => {
        let extra = "";
        if (l.dashed) extra = `;border:1.5px dashed ${hx("mutedL")}`;
        if (l.outline) extra = `;border:2px solid ${hx(l.outline)}`;
        const c = l.transparent ? "transparent" : hx(l.color || "muted");
        return swatch(c, l.label, extra);
      }).join("");
      const viz = `<div style="display:flex;align-items:center;height:100%">${table}</div>`;
      return `<div class="wsg" style="position:absolute;inset:0">${chrome(P, o, viz, legend, o.hint)}</div>`;
    },
  };

  // loop — an N-node cycle on a ring, with drawn arcs, edge labels, a flowing
  // pulse around the ring, a pulsing core label and hoverable nodes.
  KIND.loop = {
    html(data, P, o) {
      const hx = (t) => "#" + colorOf(P, t);
      const cx = data.cx != null ? data.cx : 540;
      const cy = data.cy != null ? data.cy : 250;
      const r = data.r != null ? data.r : 158;
      const nodes = data.nodes || [];
      const N = nodes.length || 1;
      const pts = nodes.map((_, i) => {
        const a = -Math.PI / 2 + (i * 2 * Math.PI) / N;
        return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
      });
      const arclen = Math.round((2 * Math.PI * r) / N) + 4;
      let g = `<defs><marker id="lah" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">`
        + `<path d="M0,0 L9,4.5 L0,9 z" fill="${hx("mutedL")}"/></marker></defs>`;
      let flow = "";
      for (let i = 0; i < N; i++) {
        const [x1, y1] = pts[i];
        const [x2, y2] = pts[(i + 1) % N];
        const d = `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 0 1 ${x2.toFixed(1)} ${y2.toFixed(1)}`;
        g += `<path class="larc" style="--i:${i};--len:${arclen}px" d="${d}" fill="none" stroke="${hx("mutedL")}" stroke-width="2" stroke-dasharray="${arclen}" marker-end="url(#lah)"/>`;
        flow += `<path class="lflow" d="${d}" fill="none" stroke="${hx("accent")}" stroke-width="2.6"/>`;
        const edgeLabel = nodes[i].edge || "";
        if (edgeLabel) {
          const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
          const ox = (mx - cx) * 0.17, oy = (my - cy) * 0.17;
          g += `<text x="${(mx + ox).toFixed(0)}" y="${(my + oy).toFixed(0)}" text-anchor="middle" font-family="${P.htmlFont}" font-size="13" fill="${hx("muted")}">${esc(edgeLabel)}</text>`;
        }
      }
      let nodesG = "";
      nodes.forEach((n, i) => {
        const [x, y] = pts[i];
        nodesG += `<g class="lnode" style="--i:${i}" data-pop data-tone="${esc(n.tone || "accent")}" data-title="${esc(n.label)}" `
          + `data-desc="${esc(n.note || "")}" data-in="${esc(n.in || "")}" data-out="${esc(n.out || "")}">`
          + `<circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="64" fill="#FFFFFF" stroke="${hx("accentD")}" stroke-width="1.6"/>`
          + `<text x="${x.toFixed(0)}" y="${(y + 5).toFixed(0)}" text-anchor="middle" font-family="${P.htmlDisplay}" font-weight="700" font-size="16" fill="${hx("slate")}">${esc(n.label)}</text></g>`;
      });
      const core = data.core
        ? `<text class="lcore" x="${cx}" y="${cy + 6}" text-anchor="middle" font-family="${P.htmlDisplay}" font-weight="700" font-size="21" fill="${hx("accentD")}">${esc(data.core)}</text>`
        : "";
      const svg = `<svg viewBox="0 0 1080 500" preserveAspectRatio="xMidYMid meet">${g}${flow}${nodesG}${core}</svg>`;
      return `<div class="loopd" style="position:absolute;inset:0">${chrome(P, o, svg, "", o.hint)}</div>`;
    },
  };

  // checklist — N rows each with a status colour glyph, a label and an evidence
  // line. Generalises a qualification/scorecard list. Laid out in two columns.
  KIND.checklist = {
    html(data, P, o) {
      const hx = (t) => "#" + colorOf(P, t);
      const rows = data.rows || [];
      let cells = "";
      rows.forEach((row, i) => {
        const c = hx(row.color || "muted");
        const glyph = row.glyph != null ? row.glyph : (i + 1);
        cells += `<div class="mrow" style="--i:${i}; display:grid; grid-template-columns:30px 1fr; gap:12px; align-items:start; padding:7px 0; border-bottom:1px solid ${hx("line")};">`
          + `<div style="width:27px;height:27px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:${P.htmlDisplay};font-weight:700;font-size:14px;color:#fff;background:${c}">${esc(glyph)}</div>`
          + `<div><div style="font-size:17px;font-weight:600;color:${hx("slate")}">${esc(row.label)}</div>`
          + `<div style="font-size:13.5px;color:${hx("muted")};line-height:1.34;margin-top:2px">${esc(row.evidence || "")}</div></div></div>`;
      });
      const grid = `<div class="medd" style="display:grid;grid-template-columns:1fr 1fr;gap:9px 34px;align-content:center;height:100%">${cells}</div>`;
      const legend = (data.legend || []).map(l => swatch(hx(l.color || "muted"), l.label)).join("");
      return `<div class="medd-wrap" style="position:absolute;inset:0">${chrome(P, o, grid, legend, o.hint)}</div>`;
    },
  };

  // flow — a simple left->right sequence of stages with connecting arrows.
  KIND.flow = {
    html(data, P, o) {
      const hx = (t) => "#" + colorOf(P, t);
      const stages = data.stages || [];
      const N = stages.length || 1;
      const W = 1080, H = 360;
      // Boxes shrink with the stage count so every arrow keeps at least 56px.
      const boxW = Math.min(200, Math.floor((W - (N - 1) * 56) / N)), boxH = 96, gap = (W - N * boxW) / Math.max(1, N - 1);
      const cy = H / 2;
      let g = `<defs><marker id="fah" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">`
        + `<path d="M0,0 L10,5 L0,10 z" fill="${hx("accentD")}"/></marker></defs>`;
      stages.forEach((st, i) => {
        const x = i * (boxW + gap);
        const y = cy - boxH / 2;
        g += `<g class="fnode" style="--i:${i}" data-pop data-tone="${esc(st.tone || "accent")}" data-title="${esc(st.label)}" data-desc="${esc(st.note || "")}">`
          + `<rect class="fbox" x="${x}" y="${y}" rx="10" width="${boxW}" height="${boxH}" fill="#FFFFFF" stroke="${hx("accentD")}" stroke-width="1.6"/>`
          + `<rect x="${x}" y="${y}" rx="10" width="${boxW}" height="6" fill="${hx(st.color || "accent")}"/>`
          + `<text x="${x + boxW / 2}" y="${cy + 5}" text-anchor="middle" font-family="${P.htmlDisplay}" font-weight="700" font-size="16" fill="${hx("slate")}">${esc(st.label)}</text></g>`;
        if (i < N - 1) {
          const ax1 = x + boxW + 6, ax2 = x + boxW + gap - 6;
          g += `<line class="farr" style="--i:${i}" x1="${ax1}" y1="${cy}" x2="${ax2}" y2="${cy}" stroke="${hx("accentD")}" stroke-width="2" stroke-dasharray="${Math.round(ax2 - ax1)}" marker-end="url(#fah)"/>`;
        }
      });
      const svg = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet" class="flowsvg">${g}</svg>`;
      return `<div class="flowd" style="position:absolute;inset:0">${chrome(P, o, svg, "", o.hint)}</div>`;
    },
  };

  const KINDS = Object.keys(KIND);

  // Resolve a slide -> its diagram HTML. The slide names its kind in slide.diagram.
  function html(slide, P) {
    const kind = slide.diagram;
    const k = KIND[kind];
    if (!k) throw new Error(`Unknown diagram kind "${kind}". Options: ${KINDS.join(", ")}`);
    return k.html(slide.data || {}, P, slide);
  }

  // ---- CSS ----
  // Shared chrome + popup styling, profile-driven via the CSS custom props that
  // builders-html.js already emits on :root (--paper/--ink/--accent/etc.), so no
  // hard-coded hex here either. Returned once by css('__base__').
  const BASE_CSS = `
.reveal section.diagram-slide{ background:var(--paper); padding:0; }
.dwrap{ position:absolute; inset:0; padding:60px 84px 64px; display:flex; flex-direction:column; font-family:var(--font); color:var(--slate); }
.dwrap .kick{ font-family:var(--font); font-weight:600; font-size:15px; letter-spacing:.2em; text-transform:uppercase; color:var(--accentD); }
.dwrap .dtitle{ font-family:var(--display); font-weight:var(--dw); font-size:46px; line-height:1.04; letter-spacing:-.01em; color:var(--slate); margin-top:12px; max-width:26ch; }
.dwrap .dviz{ flex:1; min-height:0; margin-top:12px; }
.dwrap .dviz svg{ width:100%; height:100%; display:block; }
.dwrap .dleg{ display:flex; gap:24px; margin-top:8px; flex-wrap:wrap; font-size:14px; color:var(--muted); }
.dwrap .dleg .k{ display:inline-flex; align-items:center; gap:7px; }
.dwrap .dleg .sw{ width:13px; height:13px; border-radius:3px; display:inline-block; }
.dwrap .dfoot{ position:absolute; left:84px; right:84px; bottom:26px; display:flex; justify-content:space-between; font-size:12px; letter-spacing:.16em; text-transform:uppercase; color:var(--mutedL); border-top:1px solid var(--line); padding-top:11px; }
.dwrap .dfoot b{ color:var(--slate); font-weight:600; }
.dhint{ position:absolute; right:84px; top:64px; font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--mutedL); opacity:.0; animation:hintin .6s ease 1s forwards; }
@keyframes hintin{ to{ opacity:.75 } }

/* keyframes */
@keyframes draw { to { stroke-dashoffset:0; } }
@keyframes rise { from { opacity:0; transform:translateY(16px);} to { opacity:1; transform:none;} }
@keyframes pop  { from { opacity:0; transform:scale(.82);} to { opacity:1; transform:scale(1);} }
@keyframes flow { to { stroke-dashoffset:-266; } }
@keyframes corepulse { 0%,100%{ opacity:.78; } 50%{ opacity:1; } }
@keyframes glow { 0%,100%{ filter:drop-shadow(0 0 0 rgba(0,0,0,0)); } 50%{ filter:drop-shadow(0 0 6px var(--coral)); } }
@keyframes fadein { from { opacity:0; } to { opacity:1; } }

/* floating popup card (JS-driven, works on hash-jump) */
#diagpop{ position:fixed; z-index:9999; display:none; width:300px; max-width:84vw; background:#FFFFFF; border:1px solid var(--line); border-radius:12px; box-shadow:0 18px 50px -12px rgba(0,0,0,.32), 0 4px 14px rgba(0,0,0,.12); font-family:var(--font); color:var(--slate); overflow:hidden; opacity:0; transform:translateY(6px) scale(.985); transition:opacity .16s ease, transform .16s ease; pointer-events:none; }
#diagpop.on{ opacity:1; transform:none; }
#diagpop .dp-bar{ height:5px; background:var(--accent); }
#diagpop.tone-coral .dp-bar{ background:var(--coral); }
#diagpop.tone-green .dp-bar{ background:var(--green); }
#diagpop.tone-amber .dp-bar{ background:var(--amber); }
#diagpop .dp-body{ padding:14px 16px 15px; }
#diagpop .dp-t{ font-family:var(--display); font-weight:700; font-size:16px; color:var(--slate); letter-spacing:-.01em; }
#diagpop .dp-d{ font-size:13px; line-height:1.42; color:var(--muted); margin-top:5px; }
#diagpop .dp-io{ display:flex; align-items:center; gap:7px; margin-top:11px; flex-wrap:wrap; }
#diagpop .dp-chip{ font-size:11px; font-weight:600; padding:4px 9px; border-radius:999px; white-space:nowrap; }
#diagpop .dp-in{ background:var(--card); color:var(--accentD); }
#diagpop .dp-out{ background:var(--card); color:var(--green); }
#diagpop .dp-arr{ color:var(--mutedL); font-size:13px; }`;

  const KIND_CSS = {
    relationship: `
.relmap .redge{ stroke-dashoffset: var(--len); }
.reveal section.present .relmap .redge{ animation: draw .9s ease forwards; animation-delay: calc(var(--i)*.1s); }
.relmap .rnode{ opacity:0; transform-box:fill-box; transform-origin:center; transition: transform .15s ease; cursor:pointer; }
.reveal section.present .relmap .rnode{ animation: rise .55s ease forwards; animation-delay: calc(.5s + var(--i)*.1s); }
.relmap .rnode:hover{ filter: drop-shadow(0 10px 20px rgba(0,0,0,.20)); }
.relmap .rhub{ opacity:0; transform-box:fill-box; transform-origin:center; }
.reveal section.present .relmap .rhub{ animation: pop .5s ease forwards; }
.relmap .rescore{ opacity:0; }
.reveal section.present .relmap .rescore{ animation: fadein .7s ease 2.9s forwards; }`,
    matrix: `
.wsg .wcell{ opacity:0; transform:scale(.8); transform-origin:center; }
.reveal section.present .wsg .wcell{ animation: pop .45s cubic-bezier(.2,.8,.2,1) forwards; animation-delay: calc(var(--i)*.022s); }
.reveal section.present .wsg .wplay{ animation: pop .45s ease forwards, glow 2.4s ease-in-out 1.5s infinite; }
.wsg .wcell.wplay{ cursor:pointer; transition:transform .15s; }
.wsg .wcell.wplay:hover{ transform: scale(1.12); outline:2px solid var(--coral); outline-offset:3px; }`,
    loop: `
.loopd .lnode{ opacity:0; transform-box:fill-box; transform-origin:center; cursor:pointer; }
.reveal section.present .loopd .lnode{ animation: pop .5s ease forwards; animation-delay: calc(.3s + var(--i)*.14s); }
.loopd .larc{ stroke-dashoffset: var(--len); }
.reveal section.present .loopd .larc{ animation: draw 1s ease forwards; animation-delay: calc(var(--i)*.14s); }
.loopd .lflow{ stroke-dasharray:6 260; opacity:0; }
.reveal section.present .loopd .lflow{ opacity:1; animation: flow 3.4s linear 1.2s infinite; }
.loopd .lcore{ animation: corepulse 2.6s ease-in-out infinite; }
.loopd .lnode circle{ transition: stroke .15s ease, stroke-width .15s ease; }
.loopd .lnode:hover{ filter: drop-shadow(0 10px 22px rgba(0,0,0,.22)); }
.loopd .lnode:hover circle{ stroke:var(--accentD); stroke-width:3; }`,
    checklist: `
.medd .mrow{ opacity:0; }
.reveal section.present .medd .mrow{ animation: rise .5s ease forwards; animation-delay: calc(var(--i)*.07s); }`,
    flow: `
.flowd .fnode{ opacity:0; transform-box:fill-box; transform-origin:center; cursor:pointer; }
.reveal section.present .flowd .fnode{ animation: pop .5s ease forwards; animation-delay: calc(.2s + var(--i)*.12s); }
.flowd .fnode rect.fbox{ transition: stroke .15s ease, stroke-width .15s ease; }
.flowd .fnode:hover rect.fbox{ stroke:var(--accentD); stroke-width:3; }
.flowd .fnode:hover{ filter: drop-shadow(0 10px 22px rgba(0,0,0,.22)); }
.flowd .farr{ stroke-dashoffset: var(--len, 0); }
.reveal section.present .flowd .farr{ animation: draw .8s ease forwards; animation-delay: calc(.4s + var(--i)*.12s); }`,
  };

  // The popup JS engine — generic, hash-jump safe. render.js injects it once.
  const POPUP_JS = `
(function(){
  if(document.getElementById('diagpop')) return;
  var pop=document.createElement('div'); pop.id='diagpop'; document.body.appendChild(pop);
  var cur=null, hideT=null;
  function show(el){
    cur=el; if(hideT){clearTimeout(hideT);hideT=null;}
    var t=el.getAttribute('data-title')||'', d=el.getAttribute('data-desc')||'';
    var i=el.getAttribute('data-in')||'', o=el.getAttribute('data-out')||'';
    var tone=el.getAttribute('data-tone')||'accent';
    var io=(i||o)?'<div class="dp-io"><span class="dp-chip dp-in">'+i+'</span><span class="dp-arr">\\u2192</span><span class="dp-chip dp-out">'+o+'</span></div>':'';
    pop.className='tone-'+tone;
    pop.innerHTML='<div class="dp-bar"></div><div class="dp-body"><div class="dp-t">'+t+'</div>'+(d?'<div class="dp-d">'+d+'</div>':'')+io+'</div>';
    pop.style.display='block';
    var r=el.getBoundingClientRect(), pr=pop.getBoundingClientRect();
    var left=r.left+r.width/2-pr.width/2, top=r.top-pr.height-14;
    if(top<8) top=r.bottom+14;
    left=Math.max(10,Math.min(left,window.innerWidth-pr.width-10));
    pop.style.left=left+'px'; pop.style.top=top+'px';
    requestAnimationFrame(function(){pop.classList.add('on');});
  }
  function hide(){ pop.classList.remove('on'); cur=null; hideT=setTimeout(function(){if(!cur)pop.style.display='none';},180); }
  document.addEventListener('mouseover',function(e){
    var el=e.target.closest&&e.target.closest('[data-pop]'); if(el&&el!==cur) show(el);
  });
  document.addEventListener('mouseout',function(e){
    var el=e.target.closest&&e.target.closest('[data-pop]');
    if(el){var to=e.relatedTarget; if(!to||!(el===to||el.contains(to))) hide();}
  });
})();`;

  // Profile-driven custom props the diagram CSS leans on beyond the base set
  // already on :root. Scoped to .diagram-slide + #diagpop so diagram-free decks
  // (which never get this block injected) stay byte-identical.
  function vars(P) {
    const hx = (t) => "#" + colorOf(P, t);
    return `.reveal section.diagram-slide,#diagpop{--green:${hx("green")};--amber:${hx("amber")};}`;
  }

  // css(kind): '__base__' -> shared chrome+popup CSS; a kind name -> that kind's CSS.
  function css(kind) {
    if (kind === "__base__") return BASE_CSS;
    return KIND_CSS[kind] || "";
  }

  return { html, css, vars, KINDS, popupJs: POPUP_JS };
};
