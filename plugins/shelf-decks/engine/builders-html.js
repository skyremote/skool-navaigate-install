/* Deck engine — reveal.js HTML renderer.
   Same 13 builders, same unified spec as builders-pptx.js. Profile-driven via
   CSS custom properties, so one stylesheet serves every brand.
   Each builder returns { html, talk }.

   Factory: require("./builders-html.js")(P) -> { builders, css, rootVars } */

const { colorOf } = require("./profiles.js");

module.exports = function (P) {
  const hx = (t) => "#" + colorOf(P, t);
  const IN = 96; // px per inch at the engine's fixed 1280x720 (96dpi) canvas —
  // lets HTML honour the same o.top/o.cardH (inches) already used by the PPTX
  // renderer, so both outputs size cards from content instead of stretching.
  const px = (inches) => Math.round(inches * IN);
  const hexToRgb = (hex) => {
    const n = parseInt(String(hex).replace("#", ""), 16);
    return `${(n >> 16) & 255},${(n >> 8) & 255},${n & 255}`;
  };

  // ---- shared fragments ----
  const corner = () => `<div class="corner"></div>`;
  // P.logoUrl is set by render.js when the brand has a logo (copied beside the HTML).
  const footer = (text, onDark) =>
    `<div class="footer${onDark ? " on-dark" : ""}"><span class="brand">${P.label || ""}</span>${
      text ? `<span class="cap">${text}</span>` : ""}${
      P.logoUrl && !onDark ? `<img class="flogo" src="${P.logoUrl}" alt="">` : ""}</div>`;
  const eyebrow = (t, d = ".05s") => t ? `<div class="eyebrow anim" style="--d:${d}">${String(t).toUpperCase()}</div>` : "";

  // titleParts -> inline coloured spans, '\n' becomes a line break.
  function titleInner(o) {
    const tp = o.titleParts || [{ text: o.title || "" }];
    let html = "";
    tp.forEach((p) => {
      const c = hx(p.c || p.color || "ink");
      String(p.text).split("\n").forEach((seg, i) => {
        if (i > 0) html += "<br>";
        html += `<span style="color:${c}">${seg}</span>`;
      });
    });
    return html;
  }
  const title = (o, cls = "title", d = ".15s") =>
    `<h1 class="${cls} anim" style="--d:${d}">${titleInner(o)}</h1>`;
  const dek = (t, d = ".26s") => t ? `<p class="dek anim" style="--d:${d}">${t}</p>` : "";
  // image: "cover" -> images/cover.png; an explicit extension ("cover.jpg") is kept.
  const imgUrl = (o) => o.image ? (/\.(png|jpe?g|webp|gif|svg)$/i.test(o.image) ? `images/${o.image}` : `images/${o.image}.png`) : "";

  const B = {};

  B.cover = (o) => ({ talk: o.talk, html:
    `<div class="edge"></div>
     <div class="img anim-img" style="background-image:url('${imgUrl(o)}')"></div>
     <div class="seam"></div>
     ${P.logoUrl ? `<img class="clogo anim" style="--d:.02s" src="${P.logoUrl}" alt="">` : ""}
     <div class="panel">
       ${o.eyebrow ? `<div class="ceyebrow anim" style="--d:.05s">${o.eyebrow.toUpperCase()}</div>` : ""}
       <h1 class="ctitle anim" style="--d:.18s">${titleInner(o)}</h1>
       ${o.tagline ? `<p class="tagline anim" style="--d:.34s">${o.tagline}</p>` : ""}
       <div class="cseam anim" style="--d:.46s"></div>
       ${o.promise ? `<p class="promise anim" style="--d:.54s">${o.promise.replace(/\n/g, "<br>")}</p>` : ""}
     </div>`, cls: "cover" });

  B.bigStats = (o) => {
    const top = o.top ?? 2.85, h = o.cardH ?? 3.55;
    return { talk: o.talk, html:
    corner() + eyebrow(o.eyebrow) + title(o) + dek(o.dek) +
    `<div class="stats" style="top:${px(top)}px">${o.items.map((s, i) => {
      const size = s.size || (s.num.length >= 5 ? 40 : s.num.length >= 4 ? 48 : s.num.length >= 3 ? 56 : 60);
      return `<div class="stat anim" style="--d:${(0.4 + i * 0.1).toFixed(2)}s;height:${px(h)}px">
        <div class="card-bar"></div>
        <div class="stat-num" style="font-size:${size}px">${s.num}</div>
        ${s.unit ? `<div class="stat-unit">${s.unit}</div>` : ""}
        <div class="rule"></div>
        <div class="stat-label">${s.label}</div></div>`;
    }).join("")}</div>` + footer(o.footer), cls: "pad" };
  };

  B.timelineAlt = (o) => {
    const N = o.phases.length;
    const nodes = o.phases.map((p, i) => {
      const left = (9 + (i / (N - 1)) * 82).toFixed(2);
      const above = i % 2 === 0, last = i === N - 1;
      const t = p.mark ? p.title.replace(p.mark, `<span class="tl-mark">${p.mark}</span>`) : p.title;
      return `<div class="tl-item ${above ? "above" : "below"}${last ? " last" : ""}" style="left:${left}%;--i:${i}">
        <div class="tl-block"><div class="tl-label">${(p.label || "").toUpperCase()}</div>
        <div class="tl-title">${t}</div><div class="tl-desc">${p.desc}</div></div>
        <div class="tl-stem"></div><div class="tl-dot"></div></div>`;
    }).join("");
    return { talk: o.talk, cls: "pad timeline", html:
      corner() + eyebrow(o.eyebrow) + title(o) + dek(o.dek) +
      `<div class="tl"><div class="tl-axis"></div>${nodes}</div>` + footer(o.footer) };
  };

  B.split = (o) => ({ talk: o.talk, cls: "split", html:
    corner() +
    `<div class="img anim-img" style="background-image:url('${imgUrl(o)}')"></div>
     <div class="seam"></div>
     <div class="panel">
       ${eyebrow(o.eyebrow)}
       ${title(o, "title split-title", ".16s")}
       ${o.body ? `<p class="body anim" style="--d:.32s">${o.body}</p>` : ""}
       ${o.pills ? `<div class="pills anim" style="--d:.46s">${o.pills.map(p => `<span class="pill">${p}</span>`).join("")}</div>` : ""}
     </div>` + footer(o.footer) });

  B.divider = (o) => ({ talk: o.talk, cls: "fb divider", html:
    `<div class="bg anim-img" style="background-image:url('${imgUrl(o)}')"></div>
     <div class="ov" style="background:rgba(20,16,12,.5)"></div>
     <div class="edge"></div>
     <div class="content">
       ${o.kicker ? `<div class="kicker anim" style="--d:.1s">${o.kicker}</div>` : ""}
       <h1 class="fb-title anim" style="--d:.24s">${o.title}</h1>
       ${o.sub ? `<p class="fb-sub anim" style="--d:.42s">${o.sub}</p>` : ""}
     </div>` });

  B.outcomeBars = (o) => ({ talk: o.talk, cls: "pad outcomes", html:
    corner() + eyebrow(o.eyebrow) + title(o, "title oc-head") +
    `<div class="oc">${o.outcomes.map((c, i) => `
      <div class="oc-col anim" style="--d:${(0.34 + i * 0.14).toFixed(2)}s">
        <div class="oc-bar"></div>
        <div class="oc-tag">Outcome 0${i + 1}</div>
        <div class="oc-title">${c.title}</div>
        <div class="oc-stat" style="font-size:${(c.statSize || 56)}px">${c.stat}</div>
        <div class="oc-sub">${c.subLabel}</div>
        <div class="oc-desc">${c.desc}</div>
        <div class="oc-bars">
          <div class="oc-blabels"><span class="a">${c.baselineLabel || "Baseline"}</span><span class="b">${c.withLabel || "After"}</span></div>
          <div class="bar-base" style="--w:${Math.round((c.baselineRatio || 0.4) * 100)}%"></div>
          <div class="bar-with" style="--w:100%"></div>
          ${c.barCaption ? `<div class="oc-cap">${c.barCaption}</div>` : ""}
        </div></div>`).join("")}</div>` + footer(o.footer) });

  // items[i].tone: "light" | "gold" | (unset = default dark slate) — opt-in per-card
  // colour variation so a 2x2 grid can break from uniform slate when a deck wants it.
  B.darkGrid = (o) => {
    const top = o.top ?? 3.05, h = o.cardH ?? 1.85;
    return { talk: o.talk, cls: "pad darkgrid", html:
    corner() + eyebrow(o.eyebrow) + title(o, "title dg-head") +
    `<div class="dg" style="top:${px(top)}px;grid-template-rows:repeat(2,${px(h)}px)">${o.items.map((it, i) => `
      <div class="dg-card${it.tone ? " tone-" + it.tone : ""} anim" style="--d:${(0.34 + i * 0.1).toFixed(2)}s">
        <div class="dg-num">${it.num || String(i + 1).padStart(2, "0")}</div>
        <div class="dg-title">${it.title}</div>
        <div class="dg-desc">${it.desc}</div></div>`).join("")}</div>` + footer(o.footer) };
  };

  B.cards = (o) => {
    const n = o.items.length, numbered = o.items.some(i => i.num);
    const top = o.top ?? 2.7, h = o.cardH ?? (numbered ? 3.55 : 2.85);
    return { talk: o.talk, cls: "pad cards-slide", html:
      corner() + eyebrow(o.eyebrow) + title(o) + dek(o.dek) +
      `<div class="cards n${n}${numbered ? " numbered" : ""}" style="top:${px(top)}px">${o.items.map((it, i) => `
        <div class="card anim" style="--d:${(0.4 + i * 0.08).toFixed(2)}s;height:${px(h)}px">
          <div class="card-bar"></div>
          ${it.num ? `<div class="card-num">${it.num}</div>` : ""}
          <div class="card-title">${it.title}</div>
          <div class="card-rule"></div>
          <div class="card-desc">${it.desc}</div></div>`).join("")}</div>` + footer(o.footer) };
  };

  B.calculator = (o) => ({ talk: o.talk, cls: "pad calc-slide", html:
    corner() + eyebrow(o.eyebrow) + title(o) + dek(o.dek) +
    `<div class="calc">
       <div class="calc-row calc-foundation anim" style="--d:.36s">
         <div class="calc-name-wrap"><div class="calc-name">${o.foundation.name}</div>
         <div class="calc-sub">${(o.foundation.sub || "Required foundation layer").toUpperCase()}</div></div>
         <div class="calc-price">${o.foundation.price}</div><div class="req">REQUIRED</div>
       </div>
       ${o.modules.map((m, i) => `
       <div class="calc-row anim" style="--d:${(0.46 + i * 0.07).toFixed(2)}s">
         <div class="calc-name">${m.name}</div><div class="calc-price">${m.price}</div>
         <div class="toggle"><div class="knob"></div></div></div>`).join("")}
       <div class="calc-total anim" style="--d:${(0.5 + o.modules.length * 0.07).toFixed(2)}s">
         <div class="lbl">${o.totalLabel || "Total"}</div><div class="val">${o.total}</div></div>
     </div>` + footer(o.footer) });

  // o.gridCols: opt-in multi-row module grid (e.g. 8 deliverables as 2x4 instead of
  // a single cramped row of 8). Omit for the original single-row layout — default
  // behaviour (rows===1) is byte-for-byte unchanged. Optional numeralStyle/headStyle/
  // foundationStyle strings let a deck nudge the numeral/head/foundation position
  // when a multi-row grid frees up different vertical space.
  B.modules = (o) => {
    const n = o.items.length;
    const cols = o.gridCols || n, rows = Math.ceil(n / cols);
    // top/cardH/gap are inches (shared unit with the PPTX renderer), like the
    // other card-grid builders — px() converts for the HTML canvas.
    const top = px(o.top ?? 3.875), gap = px(o.gap ?? 0.167), h = px(o.cardH ?? 1.229);
    const gridStyle = rows > 1
      ? `top:${top}px;grid-template-columns:repeat(${cols},1fr);grid-template-rows:repeat(${rows},${h}px);grid-auto-flow:row;gap:${gap}px;`
      : `top:${top}px;`;
    return { talk: o.talk, cls: "modules", html:
    corner() +
    `<div class="eyebrow eb-abs anim" style="--d:.05s">${(o.eyebrow || "").toUpperCase()}</div>
     <div class="mod-numeral anim" style="--d:.18s${o.numeralStyle ? `;${o.numeralStyle}` : ""}">${o.numeral || n}</div>
     <div class="mod-head"${o.headStyle ? ` style="${o.headStyle}"` : ""}><h1 class="mod-title anim" style="--d:.26s">${o.title}</h1>
       ${o.sub ? `<p class="mod-sub anim" style="--d:.4s">${o.sub}</p>` : ""}</div>
     <div class="mod-cards mc${n}" style="${gridStyle}">${o.items.map((m, i) => `
       <div class="mod-card anim" style="--d:${(0.5 + i * 0.07).toFixed(2)}s${rows > 1 ? `;height:${h}px` : ""}">
         <div class="n">${m.num || String(i + 1).padStart(2, "0")}</div><div class="tick"></div>
         <div class="nm">${m.name}</div>${rows === 1 ? `<div class="stem"></div>` : ""}</div>`).join("")}</div>
     <div class="mod-foundation anim" style="--d:${(0.55 + n * 0.07).toFixed(2)}s${o.foundationStyle ? `;${o.foundationStyle}` : ""}">
       <div class="a">${o.foundationLabel || "Foundation"}</div><div class="b">${o.foundationSub || ""}</div></div>`
    + footer(o.footer) };
  };

  // left/right.dark: opt-in inverted (slate) column for contrast/rhythm — omit for
  // the original two-tone paper/card look (default behaviour unchanged).
  B.compare = (o) => {
    const top = o.top ?? 2.78, h = o.cardH ?? 3.6;
    const colHtml = (c, side, d) =>
      `<div class="cmp-col ${side}${c.dark ? " dark" : ""} anim" style="--d:${d};height:${px(h)}px"><div class="cmp-bar"></div>
        <div class="cmp-h">${c.title}</div>
        ${c.items.map(t => `<div class="cmp-li">${t}</div>`).join("")}</div>`;
    return { talk: o.talk, cls: "pad compare", html:
      corner() + eyebrow(o.eyebrow) + title(o) + dek(o.dek) +
      `<div class="cmp" style="top:${px(top)}px">${colHtml(o.left, "left", ".36s")}${colHtml(o.right, "right", ".48s")}</div>` + footer(o.footer) };
  };

  // o.dark: opt-in full-slate inverted statement (rhythm break from an all-paper
  // deck) — omit for the original light-paper look (default behaviour unchanged).
  B.statement = (o) => {
    const dark = !!o.dark;
    const lines = o.lines || [{ text: o.title }];
    const inner = lines.map(l => `<span style="color:${hx(l.c || l.color || (dark ? "white" : "ink"))}">${l.text}</span>`).join("<br>");
    return { talk: o.talk, cls: "pad statement" + (dark ? " dark" : ""), html:
      corner() + eyebrow(o.eyebrow) +
      `<div class="stmt">
         <h1 class="stmt-lines anim" style="--d:.15s">${inner}</h1>
         ${o.body ? `<p class="stmt-body anim" style="--d:.34s">${o.body}</p>` : ""}
         ${o.bodyBold ? `<p class="stmt-bold anim" style="--d:.46s">${o.bodyBold}</p>` : ""}
       </div>` + footer(o.footer, dark) };
  };

  B.close = (o) => ({ talk: o.talk, cls: "fb close", html:
    `<div class="bg anim-img" style="background-image:url('${imgUrl(o.image ? o : { image: "cover" })}')"></div>
     <div class="ov" style="background:rgba(20,16,12,.42)"></div>
     <div class="edge"></div>
     <div class="content">
       ${o.kicker ? `<div class="kicker anim" style="--d:.1s">${o.kicker}</div>` : ""}
       <h1 class="fb-title close-title anim" style="--d:.22s">${o.title}</h1>
       ${o.promise ? `<p class="close-promise anim" style="--d:.36s">${o.promise}</p>` : ""}
       <div class="close-rule anim" style="--d:.46s"></div>
       ${o.sub ? `<p class="close-sub anim" style="--d:.54s">${o.sub}</p>` : ""}
       ${o.ctaPrimary ? `<div class="cta anim" style="--d:.66s"><span class="cta-btn">${o.ctaPrimary}</span>${o.ctaSub ? `<span class="cta-sub">${o.ctaSub}</span>` : ""}</div>` : ""}
     </div>` });

  // Full-bleed bespoke graphic (baked composition). No overlay, no text. 16:9.
  // Art direction for every image comes from the brand's imageStyle (brand.json).
  B.art = (o) => ({ talk: o.talk, cls: "fb art", html:
    `<div class="bg anim-img" style="background-image:url('${imgUrl(o)}')"></div>` +
    (o.edge === false ? "" : `<div class="edge"></div>`) });

  // Live animated/interactive diagram (type:"diagram"). render.js renders these
  // via ./diagrams.js directly; this fallback only keeps the builder lookup from
  // throwing if a diagram slide ever reaches this path — it bakes to the art image.
  B.diagram = (o) => B.art(o);

  // Full-bleed image (object on the right) + live title overlaid on the
  // dark left, behind a soft left-gradient scrim so the object stays bright.
  B.hero = (o) => ({ talk: o.talk, cls: "fb hero", html:
    `<div class="bg anim-img" style="background-image:url('${imgUrl(o)}')"></div>
     <div class="hero-scrim"></div>
     <div class="edge"></div>
     <div class="hero-content">
       ${o.eyebrow ? `<div class="hero-eyebrow anim" style="--d:.1s">${String(o.eyebrow).toUpperCase()}</div>` : ""}
       <h1 class="hero-title anim" style="--d:.22s">${titleInner(o)}</h1>
       ${o.sub ? `<p class="hero-sub anim" style="--d:.4s">${o.sub}</p>` : ""}
     </div>` });

  // ---- profile-driven :root + static CSS ----
  const rootVars = `:root{
  --bg:${hx("bg")};--ink:${hx("ink")};--body:${hx("body")};--body2:${hx("body2")};
  --slate:${hx("slate")};--slate2:${hx("slate2")};--accent:${hx("accent")};--accentD:${hx("accentD")};
  --accentL:${hx("accentL")};--coral:${hx("coral")};--muted:${hx("muted")};--mutedL:${hx("mutedL")};
  --line:${hx("line")};--paper:${hx("paper")};--card:${hx("card")};
  --accentRGB:${hexToRgb(colorOf(P, "accent"))};
  --display:'${P.htmlDisplay}',sans-serif;--font:'${P.htmlFont}',sans-serif;
  --dw:${P.htmlDisplayWeight};--sw:${P.htmlDisplaySemi};--pad:72px;}`;

  const css = rootVars + "\n" + STATIC_CSS;
  return { builders: B, css, fontsHref: P.htmlFontsHref };
};

const STATIC_CSS = `
*{box-sizing:border-box;}
html,body{background:#0c0d0f;margin:0;padding:0;overflow:hidden;}
.reveal{font-family:var(--font);font-weight:400;color:var(--body);}
.reveal .slides{text-align:left;}
.reveal .slides section{width:1280px;height:720px;padding:0;overflow:hidden;background:var(--bg);box-shadow:0 0 60px rgba(0,0,0,.4);top:0!important;left:0!important;}
.reveal h1{font-family:var(--display);text-transform:none;margin:0;}
.reveal p{margin:0;}
.reveal .slides section.pad{padding:54px var(--pad) 40px;}
.corner{position:absolute;top:0;right:0;width:104px;height:104px;background:var(--accent);clip-path:polygon(100% 0,0 0,100% 100%);z-index:3;}
.footer{position:absolute;left:var(--pad);right:var(--pad);bottom:24px;height:18px;z-index:4;}
.split .footer{right:46%;}
.footer .brand{font-size:11px;font-weight:700;letter-spacing:2.5px;color:var(--muted);}
.footer .cap{position:absolute;left:0;right:0;top:0;text-align:center;font-style:italic;font-size:13px;color:var(--muted);}
.reveal p.dek{margin-top:14px;}
.split .footer{display:flex;gap:28px;align-items:baseline;}
.split .footer .cap{position:static;text-align:left;}
.footer .flogo{position:absolute;right:0;bottom:-6px;height:28px;width:auto;}
.cover .clogo{position:absolute;left:56px;top:44px;height:44px;width:auto;z-index:3;}
.footer.on-dark .brand{color:#B8AFA2;}.footer.on-dark .cap{color:#D9D1C5;}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:3px;color:var(--accentD);text-transform:uppercase;margin-bottom:18px;}
.title{font-weight:var(--dw);font-size:46px;line-height:1.13;letter-spacing:.2px;color:var(--ink);}
.dek{font-size:18px;line-height:1.3;color:var(--body);margin-top:30px;max-width:1000px;}
.reveal .slides section .anim{opacity:0;transform:translateY(18px);transition:opacity .6s ease, transform .6s cubic-bezier(.2,.7,.2,1);transition-delay:var(--d,0s);}
.reveal .slides section.present .anim{opacity:1;transform:none;}
.anim-img{opacity:0;transform:scale(1.06);transition:opacity 1.1s ease, transform 1.6s cubic-bezier(.2,.6,.2,1);}
.reveal .slides section.present .anim-img{opacity:1;transform:scale(1);}
.cover .edge{position:absolute;left:0;top:0;width:7px;height:100%;background:var(--accent);z-index:2;}
.cover .img{position:absolute;right:0;top:0;width:58%;height:100%;background-size:cover;background-position:center;}
.cover .seam{position:absolute;left:42%;top:0;width:5px;height:100%;background:var(--accent);z-index:2;}
.cover .panel{position:absolute;left:0;top:0;width:42%;height:100%;padding:0 56px;display:flex;flex-direction:column;justify-content:center;}
.cover .ceyebrow{font-size:12px;font-weight:700;letter-spacing:2.5px;color:var(--accentD);text-transform:uppercase;margin-bottom:26px;}
.cover .ctitle{font-family:var(--display);font-weight:var(--dw);font-size:62px;line-height:1.0;color:var(--ink);letter-spacing:.4px;}
.cover .tagline{font-size:19px;color:var(--ink);margin-top:26px;line-height:1.26;max-width:430px;}
.cover .cseam{width:46px;height:4px;background:var(--accent);margin:26px 0;}
.cover .promise{font-style:italic;font-size:14px;color:var(--body);line-height:1.5;}
.split .img{position:absolute;right:0;top:0;width:46%;height:100%;background-size:cover;background-position:center;}
.split .seam{position:absolute;left:54%;top:0;width:5px;height:100%;background:var(--accent);z-index:2;}
.split .panel{position:absolute;left:0;top:0;width:54%;height:100%;padding:0 64px;display:flex;flex-direction:column;justify-content:center;}
.split .split-title{font-size:40px;line-height:1.04;}
.split .body{font-size:16px;line-height:1.42;color:var(--body);margin-top:24px;max-width:560px;}
.pills{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px;}
.pill{border:1px solid var(--accent);border-radius:20px;padding:8px 16px;font-size:10.5px;font-weight:700;letter-spacing:1.6px;color:var(--accentD);text-transform:uppercase;}
.fb{position:absolute;inset:0;}
.fb .bg{position:absolute;inset:0;background-size:cover;background-position:center;}
.fb .ov{position:absolute;inset:0;}
.fb .edge{position:absolute;left:0;top:0;width:7px;height:100%;background:var(--accent);z-index:2;}
.fb .content{position:absolute;left:var(--pad);right:var(--pad);top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;z-index:2;}
.kicker{font-size:13px;font-weight:700;letter-spacing:3px;color:var(--accentL);text-transform:uppercase;margin-bottom:18px;}
.fb-title{font-family:var(--display);font-weight:var(--dw);font-size:64px;line-height:1.12;color:#fff;text-shadow:0 3px 12px rgba(0,0,0,.4);max-width:1000px;letter-spacing:.3px;}
.fb-sub{font-size:17px;color:#EFE9E0;margin-top:34px;max-width:820px;line-height:1.32;}
.close-title{font-size:74px;line-height:1.08;padding-bottom:6px;}
.close-promise{font-style:italic;font-size:19px;color:#F2ECE2;margin-top:40px;}
.close-rule{width:56px;height:5px;background:var(--accent);margin:24px 0;}
.close-sub{font-size:16px;font-weight:700;color:#fff;}
.cta{display:flex;align-items:center;margin-top:28px;}
.cta-btn{background:var(--accent);color:#1A1410;font-weight:700;font-size:15px;padding:15px 30px;letter-spacing:.3px;}
.cta-sub{font-style:italic;font-size:13px;color:#E0D8CC;margin-left:20px;}
.stats{position:absolute;left:var(--pad);right:var(--pad);display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:20px;}
.stat{position:relative;background:var(--paper);border:1px solid var(--line);box-shadow:0 5px 16px rgba(122,115,104,.14);padding:30px 22px;}
.card-bar{position:absolute;left:0;top:0;height:5px;width:100%;background:var(--accent);}
.stat-num{font-family:var(--display);font-weight:var(--dw);color:var(--accentD);line-height:1;letter-spacing:-1px;height:66px;display:flex;align-items:flex-end;}
.stat-unit{font-size:11px;font-weight:700;letter-spacing:2px;color:var(--accent);text-transform:uppercase;margin-top:16px;}
.stat .rule{width:34px;height:3px;background:var(--accent);margin:16px 0 14px;}
.stat-label{font-size:13px;line-height:1.34;color:var(--body);}
.cards{position:absolute;left:var(--pad);right:var(--pad);display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:18px;}
.card{position:relative;background:var(--paper);border:1px solid var(--line);box-shadow:0 5px 16px rgba(122,115,104,.14);padding:22px 18px;}
.card-num{font-family:var(--display);font-weight:var(--dw);font-size:46px;color:var(--accent);line-height:1;margin-bottom:12px;}
.cards.n6 .card-num{font-size:40px;}
.card-title{font-family:var(--display);font-weight:var(--sw);font-size:16px;color:var(--ink);margin-bottom:10px;letter-spacing:.3px;text-transform:uppercase;}
.cards.n6 .card-title{font-size:13.5px;}
.card-rule{display:none;}
.card-desc{font-size:12.5px;line-height:1.34;color:var(--body2);}
.cards.n6 .card-desc{font-size:11px;line-height:1.3;}
.oc{position:absolute;left:var(--pad);right:var(--pad);top:250px;bottom:62px;display:grid;grid-template-columns:1fr 1fr;gap:28px;}
.oc-col{position:relative;background:var(--paper);border:1px solid var(--line);box-shadow:0 5px 16px rgba(122,115,104,.14);padding:28px 32px;display:flex;flex-direction:column;}
.oc-bar{position:absolute;left:0;top:0;height:5px;width:100%;background:var(--accent);}
.oc-tag{font-size:11px;font-weight:700;letter-spacing:2.5px;color:var(--accent);text-transform:uppercase;}
.oc-title{font-family:var(--display);font-weight:var(--sw);font-size:18px;color:var(--ink);margin-top:8px;}
.oc-stat{font-family:var(--display);font-weight:var(--dw);color:var(--accentD);letter-spacing:-1px;margin-top:8px;line-height:1;}
.oc-sub{font-size:10.5px;font-weight:700;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-top:8px;}
.oc-desc{font-size:12.5px;line-height:1.36;color:var(--body2);margin-top:12px;}
.oc-bars{margin-top:auto;}
.oc-blabels{display:flex;justify-content:space-between;font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;}
.oc-blabels .a{color:var(--muted);}.oc-blabels .b{color:var(--accentD);}
.bar-base,.bar-with{height:14px;border-radius:7px;width:0;transition:width .9s cubic-bezier(.3,.7,.2,1);transition-delay:.5s;}
.bar-base{background:var(--card);}
.bar-with{background:var(--accent);margin-top:9px;transition-delay:.72s;}
.reveal .slides section.present .bar-base{width:var(--w);}
.reveal .slides section.present .bar-with{width:var(--w);}
.oc-cap{font-size:10px;font-style:italic;color:var(--muted);text-align:right;margin-top:9px;}
.dg{position:absolute;left:var(--pad);right:var(--pad);display:grid;grid-template-columns:1fr 1fr;gap:24px;}
.dg-card{position:relative;background:var(--slate);border:1px solid var(--slate2);border-radius:10px;padding:24px 28px;}
.dg-num{font-size:11px;font-weight:700;letter-spacing:2.5px;color:var(--accentL);}
.dg-title{font-family:var(--display);font-weight:var(--sw);font-size:20px;color:#fff;margin-top:10px;letter-spacing:.1px;}
.dg-desc{font-size:13px;line-height:1.38;color:var(--mutedL);margin-top:10px;}
.dg-card.tone-light{background:var(--paper);border-color:var(--line);}
.dg-card.tone-light .dg-title{color:var(--ink);}
.dg-card.tone-light .dg-desc{color:var(--body2);}
.dg-card.tone-light .dg-num{color:var(--accentD);}
.dg-card.tone-gold{background:var(--accent);border-color:var(--accentD);}
.dg-card.tone-gold .dg-title{color:var(--slate);}
.dg-card.tone-gold .dg-desc{color:#3B2E14;}
.dg-card.tone-gold .dg-num{color:var(--slate);}
.calc{position:absolute;left:var(--pad);right:var(--pad);top:210px;}
.calc-row{display:flex;align-items:center;background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:0 24px;height:46px;margin-bottom:8px;}
.calc-foundation{border:1.8px solid var(--accent);height:66px;box-shadow:0 6px 18px rgba(122,115,104,.2);margin-bottom:14px;}
.calc-name-wrap{flex:1;}
.calc-name{font-family:var(--display);font-weight:var(--sw);font-size:14px;color:var(--ink);flex:1;}
.calc-foundation .calc-name{font-size:17px;}
.calc-sub{font-size:11px;color:var(--accentD);letter-spacing:.8px;margin-top:4px;font-weight:600;}
.calc-price{font-family:var(--display);font-weight:var(--dw);font-size:16px;color:var(--ink);margin-right:20px;}
.calc-foundation .calc-price{font-size:22px;}
.req{border:1px solid var(--accent);border-radius:14px;padding:6px 14px;font-size:9px;font-weight:700;letter-spacing:2px;color:var(--accentD);}
.toggle{width:46px;height:24px;border-radius:14px;background:var(--accent);position:relative;flex:0 0 auto;}
.toggle .knob{position:absolute;right:3px;top:3px;width:18px;height:18px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.25);}
.calc-total{display:flex;align-items:center;margin-top:12px;border-top:2px solid var(--line);padding-top:12px;}
.calc-total .lbl{font-family:var(--display);font-weight:var(--sw);font-size:18px;color:var(--accentD);flex:1;}
.calc-total .val{font-family:var(--display);font-weight:var(--dw);font-size:30px;color:var(--ink);letter-spacing:-.5px;}
.modules{position:absolute;inset:0;background:var(--bg);}
.eb-abs{position:absolute;left:var(--pad);top:50px;}
.mod-numeral{position:absolute;left:58px;top:120px;font-family:var(--display);font-weight:var(--dw);font-size:230px;color:var(--accent);line-height:.8;letter-spacing:-6px;}
.mod-head{position:absolute;left:300px;right:var(--pad);top:150px;}
.mod-title{font-family:var(--display);font-weight:var(--dw);font-size:42px;color:var(--ink);line-height:1.18;}
.mod-sub{font-size:16px;color:var(--body);margin-top:36px;max-width:860px;line-height:1.3;}
.mod-cards{position:absolute;left:var(--pad);right:var(--pad);top:372px;display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:16px;}
.mod-card{position:relative;background:var(--paper);border:1px solid var(--line);border-radius:8px;height:118px;padding:16px;box-shadow:0 5px 14px rgba(122,115,104,.13);}
.mod-card .n{font-size:10px;font-weight:700;letter-spacing:1.8px;color:var(--accentD);}
.mod-card .tick{width:26px;height:3px;background:var(--accent);margin-top:10px;}
.mod-card .nm{position:absolute;bottom:14px;left:16px;right:16px;font-family:var(--display);font-weight:var(--sw);font-size:13px;color:var(--ink);line-height:1.05;}
.mod-card .stem{position:absolute;left:50%;bottom:-26px;width:3px;height:22px;background:var(--accent);transform:translateX(-50%);}
.mod-foundation{position:absolute;left:var(--pad);right:var(--pad);bottom:58px;height:78px;background:var(--accent);border-radius:12px;box-shadow:0 0 34px rgba(var(--accentRGB),.45);display:flex;flex-direction:column;align-items:center;justify-content:center;}
.mod-foundation .a{font-family:var(--display);font-weight:var(--dw);font-size:26px;color:var(--slate);letter-spacing:2px;}
.mod-foundation .b{font-size:11px;font-weight:700;letter-spacing:5px;color:var(--slate);margin-top:2px;}
.cmp{position:absolute;left:var(--pad);right:var(--pad);display:grid;grid-template-columns:1fr 1fr;gap:32px;}
.cmp-col{position:relative;border:1px solid var(--line);padding:30px 34px;}
.cmp-col.left{background:var(--paper);}.cmp-col.right{background:var(--card);}
.cmp-bar{position:absolute;left:0;top:0;height:6px;width:100%;}
.cmp-col.left .cmp-bar{background:var(--accent);}.cmp-col.right .cmp-bar{background:var(--muted);}
.cmp-h{font-family:var(--display);font-weight:var(--sw);font-size:20px;letter-spacing:.6px;text-transform:uppercase;margin-bottom:20px;}
.cmp-col.left .cmp-h{color:var(--accentD);}.cmp-col.right .cmp-h{color:var(--muted);}
.cmp-li{position:relative;padding-left:22px;font-size:14.5px;line-height:1.32;margin-bottom:16px;}
.cmp-col.left .cmp-li{color:#47423B;}.cmp-col.right .cmp-li{color:#7A736A;}
.cmp-li::before{content:'';position:absolute;left:0;top:6px;width:8px;height:8px;}
.cmp-col.left .cmp-li::before{background:var(--accent);}.cmp-col.right .cmp-li::before{background:var(--muted);}
.cmp-col.dark{background:var(--slate);border-color:var(--slate2);}
.cmp-col.dark .cmp-bar{background:var(--accent);}
.cmp-col.dark .cmp-h{color:var(--accentL);}
.cmp-col.dark .cmp-li{color:#C9C2B0;}
.cmp-col.dark .cmp-li::before{background:var(--accent);}
.stmt{position:absolute;left:var(--pad);right:var(--pad);top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;}
.stmt-lines{font-family:var(--display);font-weight:var(--dw);font-size:58px;line-height:1.18;letter-spacing:.3px;}
.stmt-body{font-size:18px;line-height:1.36;color:var(--body);margin-top:88px;max-width:1000px;}
.stmt-bold{font-weight:700;font-size:18px;color:var(--ink);margin-top:40px;}
section.statement.dark{background:var(--slate);}
section.statement.dark .eyebrow{color:var(--accentL);}
section.statement.dark .stmt-body{color:#D9D1C5;}
section.statement.dark .stmt-bold{color:#F5F1E4;}
section.statement.dark .footer .brand{color:#B8AFA2;}
.timeline .tl{position:absolute;left:0;right:0;top:300px;height:360px;}
.tl-axis{position:absolute;left:9%;top:50%;width:82%;height:3px;background:var(--line);transform:scaleX(0);transform-origin:left center;}
.reveal .slides section.present .tl-axis{transform:scaleX(1);transition:transform 1.15s cubic-bezier(.65,0,.2,1);transition-delay:.15s;}
.tl-item{position:absolute;top:50%;width:230px;margin-left:-115px;}
.tl-dot{position:absolute;left:50%;top:0;width:24px;height:24px;border-radius:50%;background:var(--accent);border:3px solid var(--bg);transform:translate(-50%,-50%) scale(0);box-shadow:0 2px 6px rgba(0,0,0,.12);}
.reveal .slides section.present .tl-dot{transform:translate(-50%,-50%) scale(1);transition:transform .55s cubic-bezier(.2,1.5,.4,1);transition-delay:calc(.4s + var(--i) * .16s);}
.tl-item.last .tl-dot{background:var(--coral);}
.tl-item.last .tl-dot::after{content:'';position:absolute;inset:-7px;border-radius:50%;border:2px solid var(--coral);opacity:0;animation:tlpulse 2.2s ease-out infinite;animation-delay:1.7s;}
@keyframes tlpulse{0%{transform:scale(.7);opacity:0;}25%{opacity:.7;}100%{transform:scale(1.9);opacity:0;}}
.tl-stem{position:absolute;left:50%;width:2px;height:0;background:var(--line);transform:translateX(-50%);}
.tl-item.above .tl-stem{bottom:50%;}.tl-item.below .tl-stem{top:50%;}
.reveal .slides section.present .tl-stem{height:22px;transition:height .4s ease;transition-delay:calc(.5s + var(--i) * .16s);}
.tl-block{position:absolute;left:0;right:0;text-align:center;opacity:0;transform:translateY(var(--shift,12px));}
.tl-item.above .tl-block{bottom:46px;--shift:14px;}.tl-item.below .tl-block{top:46px;--shift:-14px;}
.reveal .slides section.present .tl-block{opacity:1;transform:translateY(0);transition:opacity .6s ease, transform .6s cubic-bezier(.2,.7,.2,1);transition-delay:calc(.5s + var(--i) * .16s);}
.tl-label{font-size:11px;font-weight:700;letter-spacing:2px;color:var(--accentD);text-transform:uppercase;}
.tl-item.last .tl-label{color:var(--coral);}
.tl-title{font-family:var(--display);font-weight:var(--sw);font-size:17px;color:var(--ink);margin-top:8px;line-height:1.02;}
.tl-item.last .tl-title{color:var(--coral);}
.tl-desc{font-size:11.5px;color:var(--body2);margin-top:8px;line-height:1.22;padding:0 6px;}
.tl-mark{position:relative;color:var(--accentD);}
.tl-mark::after{content:'';position:absolute;left:0;right:0;bottom:-3px;height:2px;background:var(--accent);transform:scaleX(0);transform-origin:left;}
.reveal .slides section.present .tl-mark::after{transform:scaleX(1);transition:transform .5s ease;transition-delay:1.3s;}
#talk{position:fixed;left:0;right:0;bottom:0;z-index:60;background:rgba(28,34,44,.97);color:#EDE9E0;backdrop-filter:blur(8px);box-shadow:0 -8px 30px rgba(0,0,0,.35);border-top:3px solid var(--accent);transform:translateY(110%);transition:transform .42s cubic-bezier(.2,.7,.2,1);padding:18px 40px 22px;font-family:var(--font);}
#talk.open{transform:translateY(0);}
#talk .th{display:flex;align-items:baseline;gap:16px;margin-bottom:8px;}
#talk .tt{font-size:12px;font-weight:700;letter-spacing:3px;color:var(--accentL);}
#talk .tdir{font-size:12px;font-style:italic;color:#9FB3C6;}
#talk .tbody{font-size:17px;line-height:1.45;color:#F3EFE6;max-width:1100px;}
#talk .tx{position:absolute;right:22px;top:14px;font-size:11px;letter-spacing:2px;color:#7E909F;}
#hint{position:fixed;left:50%;top:18px;transform:translateX(-50%);z-index:55;font-family:var(--font);font-size:12px;color:#cfd6de;background:rgba(28,34,44,.82);padding:8px 16px;border-radius:20px;letter-spacing:.3px;white-space:nowrap;transition:opacity .5s ease;}
#hint b{color:var(--accentL);}
#hint.fade{opacity:0;}
.reveal .progress{color:var(--accent);height:4px;}
.reveal .controls{color:var(--accentD);opacity:.8;}
.reveal .slide-number{background:rgba(30,26,20,.55);color:#F5F1E4;font-family:var(--font);border-radius:4px;letter-spacing:.5px;}
.fb.hero .hero-scrim{position:absolute;inset:0;background:linear-gradient(90deg,rgba(11,16,22,.94) 0%,rgba(11,16,22,.66) 28%,rgba(11,16,22,0) 56%);z-index:1;}
.fb.hero .hero-content{position:absolute;left:var(--pad);top:0;bottom:0;width:55%;display:flex;flex-direction:column;justify-content:center;z-index:2;}
.hero-eyebrow{font-size:14px;font-weight:700;letter-spacing:4px;color:var(--coral);text-transform:uppercase;margin-bottom:20px;}
.hero-title{font-family:var(--display);font-weight:var(--dw);font-size:58px;line-height:1.06;color:#fff;letter-spacing:.3px;max-width:600px;}
.hero-sub{font-size:17px;color:#D7DEE6;margin-top:24px;max-width:540px;line-height:1.4;}
`;
