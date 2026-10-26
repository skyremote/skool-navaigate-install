/* Deck engine — PPTX renderer (pptxgenjs).
   13 parameterised builders, profile-driven. Ported from a hand-tuned
   gold-standard pptxgenjs deck template. Title-part colours are semantic ("accent",
   "ink", "coral", "white", "accentD") and resolved per profile.

   Factory: require("./builders-pptx.js")(pptx, P, { imgDir })
   Returns { builders, helpers }. */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const { colorOf } = require("./profiles.js");
const { imageSize } = require("./images.js");

module.exports = function (pptx, P, opts = {}) {
  const imgDir = opts.imgDir || process.cwd();
  pptx.defineLayout({ name: "W16x9", width: 13.333, height: 7.5 });
  pptx.layout = "W16x9";
  const PW = 13.333, PH = 7.5, M = 0.9;

  const CROP = path.join(opts.cropDir || imgDir, ".crop");
  try { fs.mkdirSync(CROP, { recursive: true }); } catch (e) {}

  // Image size read from the PNG/JPEG header (no external tool needed).
  function srcDims(p) { return imageSize(p); }
  // macOS: pre-crop with sips (pixel-exact). Elsewhere, or if sips fails, return
  // null and coverImage() lets pptxgenjs crop with sizing:"cover" instead.
  const HAS_SIPS = process.platform === "darwin" && !process.env.SHELF_DECKS_NO_SIPS && (() => {
    try { execSync("command -v sips", { stdio: "pipe" }); return true; } catch (e) { return false; }
  })();
  function cropToAspect(src, aspect) {
    const { w: sw, h: sh } = srcDims(src); const a = sw / sh;
    if (Math.abs(a - aspect) < 0.01) return src;
    if (!HAS_SIPS) return null;
    let cw, ch; if (a > aspect) { ch = sh; cw = Math.round(sh * aspect); } else { cw = sw; ch = Math.round(sw / aspect); }
    const ext = path.extname(src), base = path.basename(src, ext);
    const mt = Math.round(fs.statSync(src).mtimeMs);
    const out = path.join(CROP, `${base}_${cw}x${ch}_${mt}${ext}`);
    try {
      if (!fs.existsSync(out)) execSync(`sips -c ${ch} ${cw} "${src}" -o "${out}"`, { stdio: "pipe" });
    } catch (e) { return null; }
    return out;
  }
  function imgPath(name) {
    if (!name) return null;
    if (fs.existsSync(name)) return name;
    for (const c of [name, `${name}.png`, `${name}.jpg`, path.join(imgDir, name),
                     path.join(imgDir, `${name}.png`), path.join(imgDir, `${name}.jpg`)])
      if (fs.existsSync(c)) return c;
    return null;
  }
  function coverImage(slide, name, x, y, w, h, extra = {}) {
    const p = imgPath(name);
    if (!p) return false;
    const cropped = cropToAspect(p, w / h);
    if (cropped) { slide.addImage({ path: cropped, x, y, w, h, ...extra }); return true; }
    const d = srcDims(p); // no sips: let pptxgenjs crop to the frame
    slide.addImage({ path: p, x, y, w, h: w * d.h / d.w, sizing: { type: "cover", w, h }, ...extra });
    return true;
  }

  // Brand logo (P.logo, from brand.json): bottom-right of light slides, top-left of the cover.
  const LOGO = P.logo && fs.existsSync(P.logo) ? (() => { const d = imageSize(P.logo); return { path: P.logo, ratio: d.w / d.h }; })() : null;
  function logo(slide, x, y, h, alignRight) {
    if (!LOGO) return;
    const w = h * LOGO.ratio;
    slide.addImage({ path: LOGO.path, x: alignRight ? x - w : x, y, w, h });
  }

  const col = (t) => colorOf(P, t);
  function parts(arr) {
    return (Array.isArray(arr) ? arr : [{ text: arr }]).map(p =>
      ({ text: p.text, color: col(p.color || p.c || "ink") }));
  }

  function corner(slide) {
    slide.addShape(pptx.shapes.RIGHT_TRIANGLE, { x: PW - 1.05, y: 0, w: 1.05, h: 1.05,
      fill: { color: P.accent }, line: { type: "none" }, flipH: true });
  }
  function eyebrow(slide, text, color = P.accentD) {
    slide.addText((text || "").toUpperCase(), { x: M, y: 0.5, w: 9, h: 0.3, fontFace: P.font, bold: true,
      fontSize: 11.5, color, charSpacing: 3, align: "left", margin: 0 });
  }
  function title(slide, p, o = {}) {
    slide.addText(parts(p).map(x => ({ text: x.text, options: { fontFace: P.display, italic: false,
      fontSize: o.size ?? 41, color: x.color, charSpacing: 0.2 } })),
      { x: M - 0.05, y: o.y ?? 0.86, w: o.w ?? 11.4, h: o.h ?? 0.95, align: "left", margin: 0, lineSpacingMultiple: 0.95 });
  }
  function dek(slide, text, o = {}) {
    if (!text) return;
    slide.addText(text, { x: M, y: o.y ?? 1.78, w: o.w ?? 10.7, h: 0.6, fontFace: P.font,
      fontSize: o.size ?? 15.5, color: o.color ?? P.body, align: "left", margin: 0, lineSpacingMultiple: 1.12 });
  }
  function footer(slide, caption, onDark = false) {
    slide.addText(P.label, { x: M, y: PH - 0.5, w: 5, h: 0.3, fontFace: P.font, bold: true,
      fontSize: 8.5, color: onDark ? "B8AFA2" : P.muted, charSpacing: 2, margin: 0 });
    // Split slides keep the caption on the text panel, left-aligned after the label.
    const narrow = slide._footerRight, capX = narrow ? M + 2.5 : M;
    if (caption) slide.addText(caption, { x: capX, y: PH - 0.62, w: narrow ? narrow - capX - 1.45 : PW - 2 * M, h: 0.4, fontFace: P.font,
      italic: true, fontSize: narrow ? 9 : 11, color: onDark ? "D9D1C5" : P.muted, align: narrow ? "left" : "center", margin: 0 });
    if (!onDark) logo(slide, slide._footerRight || PW - M, PH - 0.6, 0.3, true);
  }
  function lightSlide() { const s = pptx.addSlide(); s.background = { color: P.bg }; return s; }
  function shadowSoft(f) { return { type: "outer", color: "7A7368", opacity: f ? 0.3 : 0.16, blur: f ? 12 : 6, offset: f ? 4 : 2, angle: 90 }; }

  const B = {};

  B.cover = function (o) {
    const s = pptx.addSlide(); s.background = { color: P.bg };
    const split = 5.55; const hasImg = coverImage(s, o.image || "cover", split, 0, PW - split, PH);
    if (!hasImg) s.addShape(pptx.shapes.RECTANGLE, { x: split, y: 0, w: PW - split, h: PH, fill: { color: P.slate }, line: { type: "none" } });
    s.addShape(pptx.shapes.RECTANGLE, { x: split - 0.06, y: 0, w: 0.06, h: PH, fill: { color: P.accent }, line: { type: "none" } });
    s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: 0.16, h: PH, fill: { color: P.accent }, line: { type: "none" } });
    logo(s, 0.58, 0.46, 0.46, false);
    if (o.eyebrow) s.addText(o.eyebrow.toUpperCase(), { x: M, y: 1.35, w: 4.6, h: 0.3, fontFace: P.font, bold: true,
      fontSize: 11.5, color: P.accentD, charSpacing: 2.5, margin: 0 });
    s.addText(parts(o.titleParts || o.title).map(p => ({ text: p.text, options: { color: p.color } })),
      { x: M - 0.04, y: o.titleY ?? 1.95, w: o.titleW ?? 4.95, h: o.titleH ?? 1.7, fontFace: P.display, italic: false,
        fontSize: o.titleSize ?? 84, charSpacing: 0.2, align: "left", margin: 0, lineSpacingMultiple: o.titleLS ?? 0.92 });
    if (o.tagline) s.addText(o.tagline, { x: M, y: o.taglineY ?? 3.78, w: 4.45, h: 0.9, fontFace: P.font, fontSize: 18,
      color: P.ink, align: "left", margin: 0, lineSpacingMultiple: 1.12 });
    s.addShape(pptx.shapes.RECTANGLE, { x: M, y: o.seamY ?? 4.78, w: 0.55, h: 0.045, fill: { color: P.accent }, line: { type: "none" } });
    if (o.promise) s.addText(o.promise, { x: M, y: o.promiseY ?? 4.98, w: 4.4, h: 1.2, fontFace: P.font, italic: true, fontSize: 13,
      color: P.body, align: "left", margin: 0, lineSpacingMultiple: 1.25 });
    return s;
  };

  B.divider = function (o) {
    const s = pptx.addSlide(); s.background = { color: P.slate };
    const hasImg = coverImage(s, o.image, 0, 0, PW, PH);
    s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: PW, h: PH, fill: { color: "1A1410", transparency: hasImg ? 42 : 8 }, line: { type: "none" } });
    s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: 0.16, h: PH, fill: { color: P.accent }, line: { type: "none" } });
    const long = (o.title || "").length > 16, tSize = long ? 60 : 80, tY = long ? 2.55 : 2.9, subY = long ? 4.95 : 4.55;
    if (o.kicker) s.addText(o.kicker.toUpperCase(), { x: M, y: tY - 0.42, w: 7, h: 0.4, fontFace: P.font, bold: true,
      fontSize: 13, color: P.accentL, charSpacing: 3, margin: 0 });
    s.addText(o.title, { x: M - 0.05, y: tY, w: 11.5, h: 2.0, fontFace: P.display, italic: false, fontSize: tSize, color: "FFFFFF",
      align: "left", margin: 0, charSpacing: 0.2, lineSpacingMultiple: 0.92,
      shadow: { type: "outer", color: "000000", opacity: 0.35, blur: 7, offset: 3, angle: 90 } });
    if (o.sub) s.addText(o.sub, { x: M, y: subY, w: 10.4, h: 0.7, fontFace: P.font, fontSize: 15, color: "EFE9E0",
      align: "left", margin: 0, lineSpacingMultiple: 1.15 });
    return s;
  };

  // o.dark: opt-in full-slate inverted statement (rhythm break) — omit for the
  // original light-paper look (default behaviour unchanged).
  B.statement = function (o) {
    const dark = !!o.dark;
    const s = pptx.addSlide(); s.background = { color: dark ? P.slate : P.bg };
    corner(s); eyebrow(s, o.eyebrow, dark ? P.accentL : P.accentD);
    const lines = Array.isArray(o.lines) ? o.lines : [{ text: o.title, c: "ink" }];
    s.addText(lines.map((l, i) => ({ text: l.text + (i < lines.length - 1 ? "\n" : ""), options: { color: col(l.color || l.c || (dark ? "white" : "ink")) } })),
      { x: M - 0.05, y: o.y ?? 1.55, w: 11.5, h: 2.6, fontFace: P.display, italic: false, fontSize: o.size ?? 62,
        align: "left", margin: 0, lineSpacingMultiple: 0.92, charSpacing: 0.2 });
    if (o.body) s.addText(o.body, { x: M, y: o.bodyY ?? 4.5, w: 10.7, h: 1.0, fontFace: P.font, fontSize: 17, color: dark ? "D9D1C5" : P.body,
      align: "left", margin: 0, lineSpacingMultiple: 1.2 });
    if (o.bodyBold) s.addText(o.bodyBold, { x: M, y: o.bodyBoldY ?? 5.65, w: 10.7, h: 0.8, fontFace: P.font, bold: true,
      fontSize: 17, color: dark ? "F5F1E4" : P.ink, align: "left", margin: 0, lineSpacingMultiple: 1.2 });
    footer(s, o.footer, dark); return s;
  };

  B.cards = function (o) {
    const s = lightSlide(); corner(s); eyebrow(s, o.eyebrow);
    title(s, o.titleParts || o.title, { size: o.size }); dek(s, o.dek);
    const items = o.items, n = items.length, numbered = items.some(i => i.num);
    const gap = n >= 5 ? 0.225 : 0.26, top = o.top ?? 2.7, h = o.cardH ?? (numbered ? 3.55 : 2.85);
    const cardW = (PW - 2 * M - gap * (n - 1)) / n, startX = M;
    items.forEach((it, i) => {
      const x = startX + i * (cardW + gap);
      s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: cardW, h, fill: { color: P.paper }, line: { color: P.line, width: 1 }, shadow: shadowSoft(false) });
      if (numbered) {
        s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: cardW, h: 0.09, fill: { color: P.accent }, line: { type: "none" } });
        s.addText(it.num, { x: x + 0.18, y: top + 0.28, w: cardW - 0.3, h: 0.95, fontFace: P.display, italic: false, fontSize: 50, color: P.accent, margin: 0, align: "left" });
        s.addText(it.title, { x: x + 0.2, y: top + 1.32, w: cardW - 0.28, h: 0.5, fontFace: P.displayXB, fontSize: n >= 6 ? 15 : 17, color: P.ink, margin: 0, align: "left", charSpacing: 0.2 });
        s.addText(it.desc, { x: x + 0.2, y: top + 1.85, w: cardW - 0.4, h: h - 2.0, fontFace: P.font, fontSize: 11.5, color: P.body2, margin: 0, align: "left", lineSpacingMultiple: 1.2, valign: "top" });
      } else {
        s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: 0.09, h, fill: { color: P.accent }, line: { type: "none" } });
        s.addText(it.title, { x: x + 0.32, y: top + 0.34, w: cardW - 0.5, h: 0.95, fontFace: P.displayXB, fontSize: n >= 5 ? 20 : 25, color: P.ink, margin: 0, align: "left", charSpacing: 0.2, lineSpacingMultiple: 0.92 });
        s.addShape(pptx.shapes.RECTANGLE, { x: x + 0.34, y: top + 1.28, w: 0.5, h: 0.04, fill: { color: P.accent }, line: { type: "none" } });
        s.addText(it.desc, { x: x + 0.32, y: top + 1.45, w: cardW - 0.6, h: h - 1.55, fontFace: P.font, fontSize: 13, color: P.body2, margin: 0, align: "left", lineSpacingMultiple: 1.22, valign: "top" });
      }
    });
    footer(s, o.footer); return s;
  };

  // left/right.dark: opt-in inverted (slate) column for contrast/rhythm — omit for
  // the original two-tone paper/card look (default behaviour unchanged).
  B.compare = function (o) {
    const s = lightSlide(); corner(s); eyebrow(s, o.eyebrow); title(s, o.titleParts || o.title, { size: o.size }); dek(s, o.dek);
    const top = o.top ?? 2.78, h = o.cardH ?? 3.6, gap = 0.5, colW = (PW - 2 * M - gap) / 2, startX = M;
    function column(x, c, fill, barColor, headColor, textColor, bulletColor, lineColor) {
      s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: colW, h, fill: { color: fill }, line: { color: lineColor || P.line, width: 1 } });
      s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: colW, h: 0.1, fill: { color: barColor }, line: { type: "none" } });
      s.addText(c.title.toUpperCase(), { x: x + 0.42, y: top + 0.3, w: colW - 0.8, h: 0.45, fontFace: P.displayXB, fontSize: 20, color: headColor, margin: 0, charSpacing: 0.5 });
      s.addText(c.items.map(t => ({ text: t, options: { bullet: { indent: 16 }, breakLine: true } })),
        { x: x + 0.42, y: top + 0.95, w: colW - 0.8, h: h - 1.2, fontFace: P.font, fontSize: 13.5, color: textColor, margin: 0, paraSpaceAfter: 12, bulletColor, lineSpacingMultiple: 1.12, valign: "top" });
    }
    column(startX, o.left, o.left.dark ? P.slate : P.paper, P.accent, o.left.dark ? P.accentL : P.accentD, o.left.dark ? "C9C2B0" : "47423B", P.accent, o.left.dark ? P.slate2 : P.line);
    column(startX + colW + gap, o.right, o.right.dark ? P.slate : P.card, o.right.dark ? P.accent : P.muted, o.right.dark ? P.accentL : P.muted, o.right.dark ? "C9C2B0" : "7A736A", o.right.dark ? P.accent : P.muted, o.right.dark ? P.slate2 : P.line);
    footer(s, o.footer); return s;
  };

  B.close = function (o) {
    const s = pptx.addSlide(); s.background = { color: P.slate };
    const hasImg = coverImage(s, o.image || "cover", 0, 0, PW, PH);
    s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: PW, h: PH, fill: { color: "1A1410", transparency: hasImg ? 22 : 6 }, line: { type: "none" } });
    s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: 0.16, h: PH, fill: { color: P.accent }, line: { type: "none" } });
    if (o.kicker) s.addText(o.kicker.toUpperCase(), { x: M, y: 1.35, w: 8, h: 0.35, fontFace: P.font, bold: true, fontSize: 12, color: P.accentL, charSpacing: 3, margin: 0 });
    s.addText(o.title, { x: M - 0.05, y: 1.78, w: 11.5, h: 1.2, fontFace: P.display, italic: false, fontSize: o.size ?? 74, color: "FFFFFF", margin: 0, charSpacing: 0.2,
      shadow: { type: "outer", color: "000000", opacity: 0.35, blur: 7, offset: 3, angle: 90 } });
    if (o.promise) s.addText(o.promise, { x: M, y: 3.25, w: 11, h: 0.5, fontFace: P.font, italic: true, fontSize: 19, color: "F2ECE2", margin: 0 });
    s.addShape(pptx.shapes.RECTANGLE, { x: M, y: 4.05, w: 0.6, h: 0.05, fill: { color: P.accent }, line: { type: "none" } });
    if (o.sub) s.addText(o.sub, { x: M, y: 4.35, w: 11, h: 0.5, fontFace: P.font, bold: true, fontSize: 16, color: "FFFFFF", margin: 0 });
    if (o.ctaPrimary) {
      s.addShape(pptx.shapes.RECTANGLE, { x: M, y: 5.25, w: 4.35, h: 0.72, fill: { color: P.accent }, line: { type: "none" } });
      s.addText(o.ctaPrimary, { x: M, y: 5.25, w: 4.35, h: 0.72, fontFace: P.font, bold: true, fontSize: 15, color: "1A1410", align: "center", valign: "middle", margin: 0 });
    }
    if (o.ctaSub) s.addText(o.ctaSub, { x: M + 4.6, y: 5.25, w: 6, h: 0.72, fontFace: P.font, italic: true, fontSize: 13, color: "E0D8CC", align: "left", valign: "middle", margin: 0 });
    return s;
  };

  B.bigStats = function (o) {
    const s = lightSlide(); corner(s); eyebrow(s, o.eyebrow);
    title(s, o.titleParts || o.title, { size: o.size }); dek(s, o.dek);
    const items = o.items, n = items.length, gap = 0.3, top = o.top ?? 2.85, h = o.cardH ?? 3.55;
    const cardW = (PW - 2 * M - gap * (n - 1)) / n, startX = M;
    items.forEach((it, i) => {
      const x = startX + i * (cardW + gap);
      s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: cardW, h, fill: { color: P.paper }, line: { color: P.line, width: 1 }, shadow: shadowSoft(false) });
      s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: cardW, h: 0.09, fill: { color: P.accent }, line: { type: "none" } });
      const numSize = it.size || (it.num.length >= 5 ? 38 : it.num.length >= 4 ? 48 : it.num.length >= 3 ? 58 : 68);
      s.addText(it.num, { x: x + 0.28, y: top + 0.55, w: cardW - 0.5, h: 1.0, fontFace: P.display, italic: false, fontSize: numSize, color: P.accentD, margin: 0, align: "left", charSpacing: -1, valign: "top" });
      if (it.unit) s.addText(it.unit.toUpperCase(), { x: x + 0.28, y: top + 1.75, w: cardW - 0.5, h: 0.35, fontFace: P.font, bold: true, fontSize: 11, color: P.accent, charSpacing: 2, margin: 0, align: "left" });
      s.addShape(pptx.shapes.RECTANGLE, { x: x + 0.3, y: top + 2.2, w: 0.5, h: 0.04, fill: { color: P.accent }, line: { type: "none" } });
      s.addText(it.label, { x: x + 0.28, y: top + 2.35, w: cardW - 0.55, h: h - 2.4, fontFace: P.font, fontSize: 12.5, color: P.body, margin: 0, align: "left", lineSpacingMultiple: 1.22, valign: "top" });
    });
    footer(s, o.footer); return s;
  };

  B.timelineAlt = function (o) {
    const s = lightSlide(); corner(s); eyebrow(s, o.eyebrow);
    title(s, o.titleParts || o.title, { size: o.size }); dek(s, o.dek);
    const ph = o.phases, n = ph.length, axisY = o.axisY ?? 4.5;
    const startX = M + 0.2, endX = PW - M - 0.2;
    s.addShape(pptx.shapes.RECTANGLE, { x: startX, y: axisY, w: endX - startX, h: 0.03, fill: { color: P.line }, line: { type: "none" } });
    ph.forEach((p, i) => {
      const last = i === n - 1, acc = last ? P.coral : P.accent, accD = last ? P.coral : P.accentD;
      const t = n === 1 ? 0.5 : i / (n - 1);
      const cx = startX + t * (endX - startX);
      const above = i % 2 === 0;
      s.addShape(pptx.shapes.OVAL, { x: cx - 0.13, y: axisY - 0.115, w: 0.26, h: 0.26, fill: { color: acc }, line: { color: P.bg, width: 2 },
        shadow: last ? { type: "outer", color: acc, opacity: 0.45, blur: 10, offset: 0, angle: 0 } : undefined });
      const colW = 2.45, colX = cx - colW / 2;
      if (above) {
        s.addText((p.label || "").toUpperCase(), { x: colX, y: axisY - 1.65, w: colW, h: 0.32, fontFace: P.font, bold: true, fontSize: 10.5, color: accD, charSpacing: 2, margin: 0, align: "center" });
        s.addText(p.title, { x: colX, y: axisY - 1.28, w: colW, h: 0.6, fontFace: P.displayXB, fontSize: 16, color: P.ink, margin: 0, align: "center", lineSpacingMultiple: 0.95 });
        s.addText(p.desc, { x: colX, y: axisY - 0.6, w: colW, h: 0.45, fontFace: P.font, fontSize: 11, color: P.body2, margin: 0, align: "center", lineSpacingMultiple: 1.15 });
      } else {
        s.addText((p.label || "").toUpperCase(), { x: colX, y: axisY + 0.25, w: colW, h: 0.32, fontFace: P.font, bold: true, fontSize: 10.5, color: accD, charSpacing: 2, margin: 0, align: "center" });
        s.addText(p.title, { x: colX, y: axisY + 0.6, w: colW, h: 0.6, fontFace: P.displayXB, fontSize: 16, color: P.ink, margin: 0, align: "center", lineSpacingMultiple: 0.95 });
        s.addText(p.desc, { x: colX, y: axisY + 1.3, w: colW, h: 0.6, fontFace: P.font, fontSize: 11, color: P.body2, margin: 0, align: "center", lineSpacingMultiple: 1.15 });
      }
    });
    footer(s, o.footer); return s;
  };

  B.split = function (o) {
    const s = lightSlide(); corner(s);
    const imgX = 7.3, imgW = PW - imgX;
    const hasImg = coverImage(s, o.image, imgX, 0, imgW, PH);
    if (!hasImg) s.addShape(pptx.shapes.RECTANGLE, { x: imgX, y: 0, w: imgW, h: PH, fill: { color: P.slate }, line: { type: "none" } });
    s.addShape(pptx.shapes.RECTANGLE, { x: imgX - 0.05, y: 0, w: 0.05, h: PH, fill: { color: P.accent }, line: { type: "none" } });
    if (o.eyebrow) s.addText(o.eyebrow.toUpperCase(), { x: M, y: 1.4, w: 6.2, h: 0.32, fontFace: P.font, bold: true, fontSize: 11.5, color: P.accentD, charSpacing: 3, margin: 0 });
    const tp = parts(o.titleParts || o.title);
    s.addText(tp.map((p, i) => ({ text: p.text, options: { color: p.color } })),
      { x: M - 0.04, y: o.titleY ?? 1.95, w: 6.0, h: o.titleH ?? 2.3, fontFace: P.display, italic: false, fontSize: o.titleSize ?? 44, align: "left", margin: 0, lineSpacingMultiple: 0.92, charSpacing: 0.2 });
    if (o.body) s.addText(o.body, { x: M, y: o.bodyY ?? 4.5, w: 6.0, h: 1.2, fontFace: P.font, fontSize: 14.5, color: P.body, align: "left", margin: 0, lineSpacingMultiple: 1.25 });
    if (o.pills && o.pills.length) {
      const py = o.pillsY ?? 5.95, gap = 0.12, h = 0.38; let x = M;
      o.pills.forEach((p) => {
        const w = 0.32 + p.length * 0.095;
        s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y: py, w, h, fill: { color: P.bg }, line: { color: P.accent, width: 1 }, rectRadius: 0.19 });
        s.addText(p.toUpperCase(), { x, y: py, w, h, fontFace: P.font, bold: true, fontSize: 9.5, color: P.accentD, charSpacing: 1.8, align: "center", valign: "middle", margin: 0 });
        x += w + gap;
      });
    }
    s._footerRight = imgX - 0.4; // keep the logo on the text panel, off the image
    footer(s, o.footer); return s;
  };

  B.calculator = function (o) {
    const s = lightSlide(); corner(s); eyebrow(s, o.eyebrow);
    title(s, o.titleParts || o.title, { size: o.size }); dek(s, o.dek);
    const top = o.top ?? 2.55, rowH = 0.5, gap = 0.08; const W = PW - 2 * M;
    const fY = top;
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: M, y: fY, w: W, h: 0.72, fill: { color: P.paper }, line: { color: P.accent, width: 1.8 }, rectRadius: 0.08, shadow: shadowSoft(true) });
    s.addText(o.foundation.name, { x: M + 0.35, y: fY + 0.09, w: W - 5, h: 0.32, fontFace: P.displayXB, fontSize: 16, color: P.ink, margin: 0, align: "left" });
    s.addText(o.foundation.sub || "Required foundation layer", { x: M + 0.35, y: fY + 0.4, w: W - 5, h: 0.28, fontFace: P.font, fontSize: 11, color: P.accentD, margin: 0, align: "left", charSpacing: 0.5 });
    s.addText(o.foundation.price, { x: M + W - 3.3, y: fY + 0.17, w: 1.8, h: 0.45, fontFace: P.display, italic: false, fontSize: 22, color: P.ink, margin: 0, align: "right" });
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: M + W - 1.35, y: fY + 0.22, w: 1.15, h: 0.32, fill: { color: P.bg }, line: { color: P.accent, width: 1 }, rectRadius: 0.16 });
    s.addText("REQUIRED", { x: M + W - 1.35, y: fY + 0.22, w: 1.15, h: 0.32, fontFace: P.font, bold: true, fontSize: 9, color: P.accentD, charSpacing: 2, align: "center", valign: "middle", margin: 0 });
    let y = fY + 0.72 + 0.25;
    o.modules.forEach((m) => {
      s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: M, y, w: W, h: rowH, fill: { color: P.paper }, line: { color: P.line, width: 0.75 }, rectRadius: 0.06 });
      s.addText(m.name, { x: M + 0.35, y, w: W - 3.5, h: rowH, fontFace: P.displayXB, fontSize: 13.5, color: P.ink, margin: 0, align: "left", valign: "middle" });
      s.addText(m.price, { x: M + W - 2.5, y, w: 1.4, h: rowH, fontFace: P.display, italic: false, fontSize: 16, color: P.ink, margin: 0, align: "right", valign: "middle" });
      const tx = M + W - 0.95, ty = y + (rowH - 0.28) / 2;
      s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: tx, y: ty, w: 0.68, h: 0.28, fill: { color: P.accent }, line: { type: "none" }, rectRadius: 0.14 });
      s.addShape(pptx.shapes.OVAL, { x: tx + 0.42, y: ty + 0.035, w: 0.21, h: 0.21, fill: { color: "FFFFFF" }, line: { type: "none" }, shadow: { type: "outer", color: "000000", opacity: 0.2, blur: 3, offset: 1, angle: 90 } });
      y += rowH + gap;
    });
    y += 0.06;
    s.addShape(pptx.shapes.RECTANGLE, { x: M, y: y - 0.04, w: W, h: 0.02, fill: { color: P.line }, line: { type: "none" } });
    s.addText(o.totalLabel || "Total", { x: M + 0.35, y: y + 0.04, w: 6, h: 0.45, fontFace: P.displayXB, fontSize: 17, color: P.accentD, margin: 0, align: "left", valign: "middle" });
    s.addText(o.total, { x: M + W - 3, y: y + 0.04, w: 2.65, h: 0.5, fontFace: P.display, italic: false, fontSize: 28, color: P.ink, margin: 0, align: "right", valign: "middle", charSpacing: -0.5 });
    footer(s, o.footer); return s;
  };

  // o.gridCols: opt-in multi-row module grid (e.g. 8 deliverables as 2x4 instead of
  // a single cramped row of 8). Omit for the original single-row layout — default
  // behaviour (rows===1) is unchanged. Optional numeralSize/numeralY/headX/titleY/
  // subY/top/cardH/gap/foundationH let a deck retune spacing for the new shape.
  B.modules = function (o) {
    const s = lightSlide(); corner(s); eyebrow(s, o.eyebrow);
    const items = o.items, n = items.length;
    const cols = o.gridCols || n, rows = Math.ceil(n / cols);
    // numeralH: keep the numeral's own text-box bottom edge clear of the card grid
    // below it — LibreOffice's renderer has been observed to mis-render the glyph
    // when a shadowed card shape overlaps a large-font text box on the same slide.
    // No charSpacing: a single glyph has nothing to kern against.
    s.addText(o.numeral || "6", { x: M - 0.1, y: o.numeralY ?? 1.55, w: 2.1, h: o.numeralH ?? 2.6, fontFace: P.display, italic: false, fontSize: o.numeralSize ?? 200, color: P.accent, margin: 0, align: "left" });
    const tx = M + (o.headX ?? 2.05);
    s.addText(o.title, { x: tx, y: o.titleY ?? 1.65, w: PW - tx - M, h: 0.95, fontFace: P.display, italic: false, fontSize: 42, color: P.ink, margin: 0, align: "left", charSpacing: 0.2, lineSpacingMultiple: 0.95 });
    if (o.sub) s.addText(o.sub, { x: tx, y: o.subY ?? 2.7, w: PW - tx - M, h: 0.6, fontFace: P.font, fontSize: 15, color: P.body, margin: 0, align: "left", lineSpacingMultiple: 1.18 });
    const gap = o.gap ?? 0.22, top = o.top ?? 4.0, h = o.cardH ?? 1.55;
    const cardW = (PW - 2 * M - gap * (cols - 1)) / cols, startX = M;
    items.forEach((it, i) => {
      const c = i % cols, r = Math.floor(i / cols);
      const x = startX + c * (cardW + gap), y = top + r * (h + gap);
      s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y, w: cardW, h, fill: { color: P.paper }, line: { color: P.line, width: 1 }, rectRadius: 0.08, shadow: shadowSoft(false) });
      s.addText(it.num || String(i + 1).padStart(2, "0"), { x: x + 0.22, y: y + 0.18, w: cardW - 0.4, h: 0.3, fontFace: P.font, bold: true, fontSize: 10, color: P.accentD, charSpacing: 1.8, margin: 0, align: "left" });
      s.addShape(pptx.shapes.RECTANGLE, { x: x + 0.22, y: y + 0.5, w: 0.4, h: 0.03, fill: { color: P.accent }, line: { type: "none" } });
      if (rows === 1) {
        s.addText(it.name, { x: x + 0.22, y: y + h - 0.5, w: cardW - 0.4, h: 0.4, fontFace: P.displayXB, fontSize: n >= 6 ? 12 : 14, color: P.ink, margin: 0, align: "left", valign: "bottom", lineSpacingMultiple: 0.95 });
        s.addShape(pptx.shapes.RECTANGLE, { x: x + cardW / 2 - 0.015, y: y + h + 0.06, w: 0.03, h: 0.22, fill: { color: P.accent }, line: { type: "none" } });
      } else {
        s.addText(it.name, { x: x + 0.22, y: y + 0.62, w: cardW - 0.4, h: h - 0.75, fontFace: P.displayXB, fontSize: 13, color: P.ink, margin: 0, align: "left", valign: "top", lineSpacingMultiple: 1.0 });
      }
    });
    const fbY = o.foundationY ?? (top + rows * h + (rows - 1) * gap + (rows === 1 ? 0.4 : 0.28)), fbH = o.foundationH ?? 0.78;
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: M, y: fbY, w: PW - 2 * M, h: fbH, fill: { color: P.accent }, line: { type: "none" }, rectRadius: 0.1, shadow: { type: "outer", color: P.accent, opacity: 0.45, blur: 18, offset: 0, angle: 0 } });
    s.addText(o.foundationLabel || "Foundation", { x: M, y: o.foundationSub ? fbY + 0.04 : fbY + (fbH - 0.42) / 2, w: PW - 2 * M, h: 0.42, fontFace: P.display, italic: false, fontSize: 26, color: P.slate, margin: 0, align: "center", charSpacing: 2 });
    if (o.foundationSub) s.addText(o.foundationSub, { x: M, y: fbY + 0.44, w: PW - 2 * M, h: 0.3, fontFace: P.font, bold: true, fontSize: 11, color: P.slate, charSpacing: 5, align: "center", margin: 0 });
    footer(s, o.footer); return s;
  };

  B.outcomeBars = function (o) {
    const s = lightSlide(); corner(s); eyebrow(s, o.eyebrow);
    s.addText(parts(o.titleParts || o.title).map(p => ({ text: p.text, options: { color: p.color } })),
      { x: M - 0.05, y: 0.86, w: 11.4, h: 1.6, fontFace: P.display, italic: false, fontSize: o.size ?? 46, align: "left", margin: 0, lineSpacingMultiple: 0.95, charSpacing: 0.2 });
    const top = o.top ?? 2.7, h = o.cardH ?? 4.05, gap = 0.4, colW = (PW - 2 * M - gap) / 2;
    o.outcomes.forEach((c, i) => {
      const x = M + i * (colW + gap);
      s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: colW, h, fill: { color: P.paper }, line: { color: P.line, width: 1 }, shadow: shadowSoft(false) });
      s.addShape(pptx.shapes.RECTANGLE, { x, y: top, w: colW, h: 0.08, fill: { color: P.accent }, line: { type: "none" } });
      s.addText(`OUTCOME 0${i + 1}`, { x: x + 0.4, y: top + 0.28, w: colW - 0.7, h: 0.3, fontFace: P.font, bold: true, fontSize: 11, color: P.accent, charSpacing: 2.5, margin: 0, align: "left" });
      s.addText(c.title, { x: x + 0.4, y: top + 0.6, w: colW - 0.7, h: 0.5, fontFace: P.displayXB, fontSize: 18, color: P.ink, margin: 0, align: "left", lineSpacingMultiple: 0.95 });
      s.addText(c.stat, { x: x + 0.4, y: top + 1.15, w: colW - 0.7, h: 0.95, fontFace: P.display, italic: false, fontSize: c.statSize || 56, color: P.accentD, margin: 0, align: "left", charSpacing: -1, valign: "top" });
      s.addText(c.subLabel.toUpperCase(), { x: x + 0.4, y: top + 2.0, w: colW - 0.7, h: 0.3, fontFace: P.font, bold: true, fontSize: 10.5, color: P.muted, charSpacing: 2, margin: 0, align: "left" });
      s.addText(c.desc, { x: x + 0.4, y: top + 2.3, w: colW - 0.7, h: 0.65, fontFace: P.font, fontSize: 11.5, color: P.body2, margin: 0, align: "left", lineSpacingMultiple: 1.22, valign: "top" });
      const barY = top + h - 0.78;
      s.addText((c.baselineLabel || "Baseline").toUpperCase(), { x: x + 0.4, y: barY - 0.26, w: 1.6, h: 0.2, fontFace: P.font, bold: true, fontSize: 9, color: P.muted, charSpacing: 1.5, margin: 0, align: "left" });
      s.addText((c.withLabel || "After").toUpperCase(), { x: x + colW - 2.1, y: barY - 0.26, w: 1.7, h: 0.2, fontFace: P.font, bold: true, fontSize: 9, color: P.accentD, charSpacing: 1.5, margin: 0, align: "right" });
      const barFullW = colW - 0.8;
      const baseW = barFullW * (c.baselineRatio || 0.4);
      s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: x + 0.4, y: barY, w: baseW, h: 0.16, fill: { color: P.card }, line: { type: "none" }, rectRadius: 0.08 });
      s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x: x + 0.4, y: barY + 0.24, w: barFullW, h: 0.16, fill: { color: P.accent }, line: { type: "none" }, rectRadius: 0.08 });
      if (c.barCaption) s.addText(c.barCaption, { x: x + 0.4, y: barY + 0.44, w: colW - 0.7, h: 0.22, fontFace: P.font, italic: true, fontSize: 10, color: P.muted, margin: 0, align: "right" });
    });
    footer(s, o.footer); return s;
  };

  // items[i].tone: "light" | "gold" | (unset = default dark slate) — opt-in per-card
  // colour variation so a 2x2 grid can break from uniform slate when a deck wants it.
  B.darkGrid = function (o) {
    const s = lightSlide(); corner(s); eyebrow(s, o.eyebrow);
    const tp = parts(o.titleParts || o.title);
    s.addText(tp.map((p, i) => ({ text: p.text, options: { color: p.color } })),
      { x: M - 0.05, y: 0.86, w: 11.4, h: 1.85, fontFace: P.display, italic: false, fontSize: o.size ?? 44, align: "left", margin: 0, lineSpacingMultiple: 0.95, charSpacing: 0.2 });
    const items = o.items, gap = 0.25, top = o.top ?? 3.05, h = o.cardH ?? 1.85;
    const cardW = (PW - 2 * M - gap) / 2;
    items.forEach((it, i) => {
      const c = i % 2, r = Math.floor(i / 2);
      const x = M + c * (cardW + gap), y = top + r * (h + gap);
      const tone = it.tone;
      const fill = tone === "light" ? P.paper : tone === "gold" ? P.accent : P.slate;
      const lineColor = tone === "light" ? P.line : tone === "gold" ? P.accentD : P.slate2;
      const numColor = tone === "gold" ? P.slate : tone === "light" ? P.accentD : P.accentL;
      const titleColor = tone === "gold" ? P.slate : tone === "light" ? P.ink : "FFFFFF";
      const descColor = tone === "gold" ? "3B2E14" : tone === "light" ? P.body2 : P.mutedL;
      s.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y, w: cardW, h, fill: { color: fill }, line: { color: lineColor, width: 1 }, rectRadius: 0.08 });
      s.addText(it.num || String(i + 1).padStart(2, "0"), { x: x + 0.35, y: y + 0.18, w: cardW - 0.6, h: 0.28, fontFace: P.font, bold: true, fontSize: 11, color: numColor, charSpacing: 2.5, margin: 0, align: "left" });
      s.addText(it.title, { x: x + 0.35, y: y + 0.5, w: cardW - 0.6, h: 0.5, fontFace: P.displayXB, fontSize: 20, color: titleColor, margin: 0, align: "left", lineSpacingMultiple: 0.95, charSpacing: 0.1 });
      s.addText(it.desc, { x: x + 0.35, y: y + 1.05, w: cardW - 0.6, h: h - 1.15, fontFace: P.font, fontSize: 11.5, color: descColor, margin: 0, align: "left", lineSpacingMultiple: 1.22, valign: "top" });
    });
    footer(s, o.footer); return s;
  };

  B.art = function (o) {
    const s = pptx.addSlide(); s.background = { color: P.slate };
    const hasImg = coverImage(s, o.image, 0, 0, PW, PH);
    if (!hasImg) s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: PW, h: PH, fill: { color: P.slate }, line: { type: "none" } });
    if (o.edge !== false) s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: 0.16, h: PH, fill: { color: P.accent }, line: { type: "none" } });
    return s;
  };

  // Diagrams (type:"diagram") are live/interactive only in HTML; in PPTX/PDF they
  // bake to a flat PNG via the art builder — so a diagram slide should always
  // carry an image: (the baked screenshot of the live diagram).
  B.diagram = (o) => B.art(o);

  // Full-bleed image hero with a live title overlaid on a soft-scrimmed left.
  B.hero = function (o) {
    const s = pptx.addSlide(); s.background = { color: P.slate };
    const hasImg = coverImage(s, o.image, 0, 0, PW, PH);
    if (!hasImg) s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: PW, h: PH, fill: { color: P.slate }, line: { type: "none" } });
    // approximate a left-to-right fade with two stacked scrim rects
    s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: 5.0, h: PH, fill: { color: "0B1016", transparency: 16 }, line: { type: "none" } });
    s.addShape(pptx.shapes.RECTANGLE, { x: 5.0, y: 0, w: 2.4, h: PH, fill: { color: "0B1016", transparency: 56 }, line: { type: "none" } });
    s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: 0.16, h: PH, fill: { color: P.accent }, line: { type: "none" } });
    if (o.eyebrow) s.addText(o.eyebrow.toUpperCase(), { x: M, y: 2.35, w: 6, h: 0.35, fontFace: P.font, bold: true, fontSize: 12.5, color: P.coral, charSpacing: 3, margin: 0 });
    const tp = parts(o.titleParts || o.title);
    s.addText(tp.map((p, i) => ({ text: p.text, options: { color: p.color } })),
      { x: M - 0.04, y: 2.78, w: 6.5, h: 2.2, fontFace: P.display, italic: false, fontSize: o.size || 44, align: "left", margin: 0, lineSpacingMultiple: 0.96, charSpacing: 0.2 });
    if (o.sub) s.addText(o.sub, { x: M, y: 4.85, w: 6.2, h: 1.0, fontFace: P.font, fontSize: 14.5, color: "D7DEE6", margin: 0, lineSpacingMultiple: 1.25 });
    return s;
  };

  return { builders: B, helpers: { corner, eyebrow, title, dek, footer, lightSlide, shadowSoft, coverImage, PW, PH, M } };
};
