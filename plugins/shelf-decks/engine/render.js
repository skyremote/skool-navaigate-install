#!/usr/bin/env node
/* Deck engine — render one deck spec into BOTH an animated reveal.js HTML
   (primary, for review) and a PPTX (export). HTML first.

   Usage:
     node render.js <deck.js> [--html-only] [--pptx-only] [--no-bake]

   Deck spec (module.exports):
     { profile:"member" | "editorial-light", name:"My_Deck", outDir:".", imagesDir:"images",
       title:"My Deck", slides:[ {type, ...opts, talk}, ... ] }

   Outputs are versioned and never overwritten: <name>_v1.html + <name>_v1.pptx,
   then _v2 on the next render, and so on. Live diagram slides with no PNG
   fallback are baked to images/<image>.baked.png in headless Chrome so the
   PPTX gets a picture of the diagram instead of a blank slide. */

const fs = require("fs");
const path = require("path");
const { resolveProfile } = require("./brand.js");
const makePptx = require("./builders-pptx.js");
const makeHtml = require("./builders-html.js");
const makeDiagrams = require("./diagrams.js");

const esc = (s) => String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// Next free version: <name>_vN where neither the .html nor the .pptx exists yet.
function nextVersion(outDir, name) {
  let n = 1;
  while (["html", "pptx", "pdf"].some(ext => fs.existsSync(path.join(outDir, `${name}_v${n}.${ext}`)))) n++;
  return n;
}

function loadSpec(deckPath) {
  delete require.cache[require.resolve(deckPath)];
  const spec = require(deckPath);
  if (!spec || !Array.isArray(spec.slides) || !spec.slides.length) throw new Error(`${deckPath}: the spec needs a slides: [...] array`);
  return spec;
}

// Find a slide image the way the PPTX renderer does (name, name.png, name.jpg, in imgDir).
function findImage(imgDir, name) {
  if (!name) return null;
  for (const c of [name, path.join(imgDir, name), path.join(imgDir, `${name}.png`), path.join(imgDir, `${name}.jpg`)])
    if (fs.existsSync(c) && fs.statSync(c).isFile()) return c;
  return null;
}

function renderHtml(spec, P, slides, outHtml, outDir) {
  const { builders, css, fontsHref } = makeHtml(P);
  const D = makeDiagrams();
  const usedKinds = new Set(); // diagram kinds present -> de-duped CSS injection
  const TALKS = [];
  const sections = slides.map((sl) => {
    TALKS.push(sl.talk || "");
    if (sl.type === "diagram") {
      usedKinds.add(sl.diagram);
      return `<section class="diagram-slide">${D.html(sl, P)}<aside class="notes">${esc(sl.talk)}</aside></section>`;
    }
    const fn = builders[sl.type];
    if (!fn) throw new Error(`No HTML builder for slide type "${sl.type}"`);
    const r = fn(sl);
    return `<section class="${r.cls}">${r.html}<aside class="notes">${esc(sl.talk)}</aside></section>`;
  });

  // Diagram CSS + popup JS — injected ONCE, and ONLY when the deck actually
  // has a diagram slide, so diagram-free decks render byte-identically.
  let diagramCss = "", diagramJs = "";
  if (usedKinds.size) {
    const parts = [D.vars(P), D.css("__base__")];
    for (const k of usedKinds) parts.push(D.css(k));
    diagramCss = `\n<style id="diagram-css">${parts.join("\n")}</style>`;
    diagramJs = `\n<script id="diagpop-js">${D.popupJs}</script>`;
  }

  // copy runtime
  const rtSrc = path.resolve(__dirname, "..", "reveal-runtime");
  const rtDst = path.join(outDir, "revealjs");
  fs.mkdirSync(rtDst, { recursive: true });
  for (const f of fs.readdirSync(rtSrc)) fs.copyFileSync(path.join(rtSrc, f), path.join(rtDst, f));

  const html = `<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(spec.title || spec.name)}</title>
${fontsHref ? `<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="${fontsHref}" rel="stylesheet">` : ""}
<link rel="stylesheet" href="revealjs/reset.css">
<link rel="stylesheet" href="revealjs/reveal.css">
<style>${css}</style>${diagramCss}
</head>
<body>
<div class="reveal"><div class="slides">
${sections.join("\n")}
</div></div>

<div id="talk">
  <div class="tx">PRESS T TO HIDE</div>
  <div class="th"><span class="tt">TALK TRACK</span><span class="tdir" id="tdir"></span></div>
  <div class="tbody" id="tbody"></div>
</div>
<div id="hint">Press <b>T</b> talk track &middot; <b>S</b> speaker view &middot; <b>&rarr;</b> next</div>

<script src="revealjs/reveal.js"></script>
<script src="revealjs/notes.js"></script>
<script>
const TALKS = ${JSON.stringify(TALKS)};
const deck = new Reveal({
  width:1280, height:720, margin:0, minScale:0.2, maxScale:4,
  transition:'fade', transitionSpeed:'slow', backgroundTransition:'fade',
  controls:true, progress:true, slideNumber:'c/t', hash:true, center:false,
  plugins:[ RevealNotes ],
});
deck.initialize();
window.deck = deck; // lets the screenshot and PDF capture drive this instance
function splitTalk(s){ const i=s.indexOf('\\n\\n'); return i===-1?{dir:'',body:s.trim()}:{dir:s.slice(0,i).trim(),body:s.slice(i+2).trim()}; }
function updateTalk(){ const t=splitTalk(TALKS[deck.getIndices().h]||''); document.getElementById('tdir').textContent=t.dir; document.getElementById('tbody').textContent=t.body; }
deck.on('ready',updateTalk); deck.on('slidechanged',updateTalk);
const talkEl=document.getElementById('talk');
deck.addKeyBinding({keyCode:84,key:'T',description:'Toggle talk track'},()=>talkEl.classList.toggle('open'));
const hint=document.getElementById('hint'); setTimeout(()=>hint.classList.add('fade'),2500);
deck.on('slidechanged',()=>hint.classList.add('fade'));
</script>${diagramJs}
</body>
</html>`;
  fs.writeFileSync(outHtml, html);
}

function renderPptx(P, slides, outPptx, imgDir, outDir) {
  const PptxGenJS = require("pptxgenjs");
  const pptx = new PptxGenJS();
  const { builders } = makePptx(pptx, P, { imgDir, cropDir: outDir });
  slides.forEach((sl) => {
    const fn = builders[sl.type];
    if (!fn) throw new Error(`No PPTX builder for slide type "${sl.type}"`);
    const s = fn(sl);
    if (sl.talk && s && s.addNotes) s.addNotes(sl.talk);
  });
  return pptx.writeFile({ fileName: outPptx });
}

// Render a spec. Returns { html, pptx, version, slides, profile, warnings }.
async function renderDeck(deckPath, opts = {}) {
  deckPath = path.resolve(deckPath);
  const spec = loadSpec(deckPath);
  const specDir = path.dirname(deckPath);
  const { P: base, brandFile, name: profileName } = resolveProfile(spec, specDir);
  // Per-deck palette/label overrides merge on top of the chosen profile.
  const P = Object.assign({}, base, spec.profileOverrides || {});

  const outDir = path.resolve(specDir, opts.outDir || spec.outDir || ".");
  const name = spec.name || path.basename(deckPath, ".js");
  const imgDir = path.resolve(outDir, spec.imagesDir || "images");
  fs.mkdirSync(outDir, { recursive: true });
  const version = nextVersion(outDir, name);
  const stem = path.join(outDir, `${name}_v${version}`);
  const warnings = [];

  // Brand logo: copy beside the HTML so the deck folder travels as one.
  if (P.logo) {
    if (fs.existsSync(P.logo)) {
      const ext = path.extname(P.logo).toLowerCase() || ".png";
      fs.mkdirSync(path.join(outDir, "brand"), { recursive: true });
      const dst = path.join(outDir, "brand", `logo${ext}`);
      if (path.resolve(P.logo) !== path.resolve(dst)) fs.copyFileSync(P.logo, dst);
      P.logoUrl = `brand/logo${ext}`;
    } else {
      warnings.push(`logo not found: ${P.logo} (set "logo" in brand.json to a PNG or JPEG)`);
      P.logo = "";
    }
  }

  const slides = spec.slides.map(s => Object.assign({}, s));
  const out = { version, slides: slides.length, profile: profileName, brandFile, warnings, html: null, pptx: null };

  // ---------- 1. HTML (reveal.js) — the review copy ----------
  if (!opts.pptxOnly) {
    out.html = `${stem}.html`;
    renderHtml(spec, P, slides, out.html, outDir);
  }

  // ---------- 2. Bake live diagrams that have no PNG fallback ----------
  const bakeTargets = {};
  slides.forEach((sl, i) => {
    if (sl.type !== "diagram" || findImage(imgDir, sl.image)) return;
    const baseName = String(sl.image || `diagram-${i + 1}`).replace(/\.(png|jpe?g)$/i, "");
    bakeTargets[i] = path.join(imgDir, `${baseName}.baked.png`);
  });
  if (Object.keys(bakeTargets).length && !opts.htmlOnly) {
    let htmlForBake = out.html;
    if (!htmlForBake) { htmlForBake = `${stem}.bake.html`; renderHtml(spec, P, slides, htmlForBake, outDir); }
    if (opts.bake === false) {
      warnings.push("diagram slides have no image: and baking is off; their PPTX slides will be blank");
    } else {
      try {
        fs.mkdirSync(imgDir, { recursive: true });
        await require("./capture.js").bake(htmlForBake, bakeTargets);
        for (const [i, f] of Object.entries(bakeTargets)) slides[i].image = f;
      } catch (e) {
        warnings.push(`could not bake the diagram slides (${e.message.split("\n")[0]}); give each diagram an image: PNG, or the PPTX slide stays blank`);
      }
    }
    if (htmlForBake !== out.html) fs.rmSync(htmlForBake, { force: true });
  }

  // ---------- 3. PPTX — the editable copy ----------
  if (!opts.htmlOnly) {
    out.pptx = `${stem}.pptx`;
    await renderPptx(P, slides, out.pptx, imgDir, outDir);
  }
  return out;
}

async function main() {
  const args = process.argv.slice(2);
  const deck = args.find(a => !a.startsWith("--"));
  if (!deck) { console.error("Usage: node render.js <deck.js> [--html-only] [--pptx-only] [--no-bake]"); process.exit(2); }
  const r = await renderDeck(deck, {
    htmlOnly: args.includes("--html-only"), pptxOnly: args.includes("--pptx-only"), bake: !args.includes("--no-bake"),
  });
  if (r.html) console.log("WROTE " + r.html + `  (${r.slides} slides)`);
  if (r.pptx) console.log("WROTE " + r.pptx);
  for (const w of r.warnings) console.warn("WARNING: " + w);
}

if (require.main === module) main().catch(e => { console.error("ERROR: " + e.message); process.exit(1); });

module.exports = { renderDeck, nextVersion, findImage };
