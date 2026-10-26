/* Deck engine — headless-Chrome slide capture.
   Ported from the html-deck-export script (export-deck.mjs): it opens the
   reveal.js deck in headless Chrome, steps through every slide the way a
   presenter would (entrance animations play, web fonts load), and captures each
   slide. Used three ways:
     shots()  -> one PNG per slide + a contact sheet, for the visual review
     pdf()    -> a PDF with one page per slide, for sending
     bake()   -> PNG fallbacks for live diagram slides, for the PPTX

   Needs puppeteer-core + pdf-lib (installed by `shelf-decks setup`) and a
   Chrome, Edge, Brave or Chromium already on the machine. */

const fs = require("fs");
const os = require("os");
const path = require("path");
const { pathToFileURL } = require("url");

const NO_CHROME =
  "No Chrome or Chromium found. Install Google Chrome (https://www.google.com/chrome/), " +
  "or run `npx playwright install chromium`, or set CHROME_PATH to the browser's executable.";

/* ----------------------------------------------- find a Chrome binary -- */
function findChrome(explicit) {
  const home = os.homedir();
  const candidates = [
    explicit,
    process.env.CHROME_PATH,
    process.env.PUPPETEER_EXECUTABLE_PATH,
    // macOS system installs
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    // Windows system installs
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    // Linux
    "/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium",
  ].filter(Boolean);
  for (const c of candidates) if (fs.existsSync(c)) return c;

  // Cached browsers from puppeteer / playwright installs
  const globs = [
    [path.join(home, ".cache", "puppeteer", "chrome"),
      d => ["chrome-mac-arm64", "chrome-mac-x64", "chrome-linux64", "chrome-win64"]
        .flatMap(p => [
          path.join(d, p, "Google Chrome for Testing.app", "Contents", "MacOS", "Google Chrome for Testing"),
          path.join(d, p, "chrome"), path.join(d, p, "chrome.exe"),
        ])],
    [path.join(home, "Library", "Caches", "ms-playwright"),
      d => ["chrome-mac-arm64", "chrome-mac", "chrome-linux", "chrome-win"]
        .flatMap(p => [
          path.join(d, p, "Google Chrome for Testing.app", "Contents", "MacOS", "Google Chrome for Testing"),
          path.join(d, p, "Chromium.app", "Contents", "MacOS", "Chromium"),
          path.join(d, p, "chrome"), path.join(d, p, "chrome.exe"),
        ])],
    [path.join(home, ".cache", "ms-playwright"),
      d => [path.join(d, "chrome-linux", "chrome"), path.join(d, "chrome-linux64", "chrome")]],
    [path.join(home, "AppData", "Local", "ms-playwright"),
      d => [path.join(d, "chrome-win", "chrome.exe")]],
  ];
  for (const [root, expand] of globs) {
    if (!fs.existsSync(root)) continue;
    const dirs = fs.readdirSync(root).filter(n => /^(chromium|chrome|mac_arm|mac_x64|win64|linux)-/.test(n) || /^\d/.test(n)).sort().reverse();
    for (const dir of dirs) {
      const base = path.join(root, dir);
      let subs = [];
      try { subs = fs.readdirSync(base, { withFileTypes: true }).filter(e => e.isDirectory()).map(e => path.join(base, e.name)); } catch (e) {}
      for (const lvl of [base, ...subs]) for (const p of expand(lvl)) if (fs.existsSync(p)) return p;
    }
  }
  return null;
}

/* -------------------------------------------------------------- render -- */
// Open the deck, wait for reveal.js and fonts, hide presenter chrome.
async function openDeck(htmlPath, opts = {}) {
  const chromePath = findChrome(opts.chrome);
  if (!chromePath) throw new Error(NO_CHROME);
  const puppeteer = require("puppeteer-core");
  const scale = Number(opts.scale || 2);
  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ["--force-color-profile=srgb", "--hide-scrollbars", "--font-render-hinting=none", "--allow-file-access-from-files"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: scale });
  await page.goto(pathToFileURL(path.resolve(htmlPath)).href, { waitUntil: "load", timeout: 60000 });
  // The engine's HTML exposes its reveal.js instance as window.deck; other
  // reveal decks use the global Reveal. __R is whichever one is running.
  const hasReveal = await page
    .waitForFunction(() => {
      const r = [window.deck, window.Reveal].find(x => x && x.isReady && x.isReady());
      if (r) window.__R = r;
      return !!r;
    }, { timeout: 20000 })
    .then(() => true).catch(() => false);
  await page.evaluate(() => document.fonts.ready);
  let slideW = 1280, slideH = 720, count = 1;
  if (hasReveal) {
    ({ slideW, slideH, count } = await page.evaluate(() => {
      const R = window.__R;
      const cfg = R.getConfig();
      R.configure({ fragments: false, controls: false, progress: false, slideNumber: false });
      const sections = document.querySelectorAll(".reveal .slides section:not(.stack)");
      return { slideW: cfg.width || 1280, slideH: cfg.height || 720, count: sections.length };
    }));
    await page.setViewport({ width: slideW, height: slideH, deviceScaleFactor: scale });
    await page.addStyleTag({ content: ".reveal .controls,.reveal .progress,.reveal .slide-number,#hint,#talk,#diagpop{display:none!important}" });
  }
  return { browser, page, hasReveal, slideW, slideH, count, chromePath };
}

// Capture slides (all, or the given 0-based indices) as image buffers.
async function captureSlides(htmlPath, opts = {}) {
  const settleMs = Number(opts.wait || 2500);
  const imgType = opts.jpeg ? "jpeg" : "png";
  const d = await openDeck(htmlPath, opts);
  try {
    if (opts.indices && !d.hasReveal) throw new Error("reveal.js did not start in the deck, so single slides cannot be captured");
    const indices = opts.indices || [...Array(d.count).keys()];
    const shots = [];
    for (const i of indices) {
      if (d.hasReveal) {
        await d.page.evaluate(idx => {
          const R = window.__R;
          const ind = R.getIndices(R.getSlides()[idx]);
          R.slide(ind.h, ind.v);
        }, i);
      }
      await new Promise(r => setTimeout(r, settleMs)); // let entrance animations finish
      shots.push({ index: i, buf: await d.page.screenshot({ type: imgType, ...(opts.jpeg ? { quality: 92 } : {}) }) });
      if (opts.log !== false) console.log(`  captured slide ${i + 1}/${d.count}`);
    }
    return { shots, slideW: d.slideW, slideH: d.slideH, count: d.count, imgType };
  } finally {
    await d.browser.close();
  }
}

// One PNG per slide plus a contact sheet, for the visual review.
async function shots(htmlPath, outDir, opts = {}) {
  fs.mkdirSync(outDir, { recursive: true });
  const r = await captureSlides(htmlPath, Object.assign({ scale: 1.5 }, opts));
  const files = r.shots.map(s => {
    const f = path.join(outDir, `slide-${String(s.index + 1).padStart(2, "0")}.png`);
    fs.writeFileSync(f, s.buf);
    return f;
  });
  const sheet = path.join(outDir, "contact-sheet.png");
  await contactSheet(files, sheet, opts);
  return { files, sheet };
}

// A 4-across grid of the slide images, numbered, to see the deck as a sequence.
async function contactSheet(files, outFile, opts = {}) {
  const puppeteer = require("puppeteer-core");
  const browser = await puppeteer.launch({ executablePath: findChrome(opts.chrome), headless: true, args: ["--allow-file-access-from-files"] });
  try {
    const page = await browser.newPage();
    const cols = 4, w = 400, h = 225, gap = 16;
    const rows = Math.ceil(files.length / cols);
    await page.setViewport({ width: cols * w + (cols + 1) * gap, height: rows * (h + 30) + (rows + 1) * gap, deviceScaleFactor: 1 });
    const cells = files.map((f, i) => `<figure><img src="${pathToFileURL(f).href}"><figcaption>${i + 1}</figcaption></figure>`).join("");
    const tmp = path.join(path.dirname(outFile), ".contact.html");
    fs.writeFileSync(tmp, `<!doctype html><style>body{margin:0;padding:${gap}px;background:#2a2c30;font:600 14px sans-serif;color:#ddd;display:grid;grid-template-columns:repeat(${cols},${w}px);gap:${gap}px}figure{margin:0}img{width:${w}px;height:${h}px;display:block}figcaption{padding-top:6px}</style>${cells}`);
    await page.goto(pathToFileURL(tmp).href, { waitUntil: "load" });
    await page.screenshot({ path: outFile, fullPage: true });
    fs.unlinkSync(tmp);
  } finally { await browser.close(); }
}

// A PDF with one page per slide (pixel-faithful to the HTML deck).
async function pdf(htmlPath, outPdf, opts = {}) {
  const { PDFDocument } = require("pdf-lib");
  const r = await captureSlides(htmlPath, opts);
  const doc = await PDFDocument.create();
  for (const s of r.shots) {
    const img = r.imgType === "jpeg" ? await doc.embedJpg(s.buf) : await doc.embedPng(s.buf);
    const p = doc.addPage([r.slideW, r.slideH]);
    p.drawImage(img, { x: 0, y: 0, width: r.slideW, height: r.slideH });
  }
  fs.writeFileSync(outPdf, await doc.save());
  return { file: outPdf, pages: r.shots.length };
}

// Bake chosen slides to PNG files: { slideIndex: outPath }.
async function bake(htmlPath, targets, opts = {}) {
  const indices = Object.keys(targets).map(Number);
  if (!indices.length) return [];
  const r = await captureSlides(htmlPath, Object.assign({ wait: 3800, scale: 2, log: false }, opts, { indices }));
  return r.shots.map(s => { fs.writeFileSync(targets[s.index], s.buf); return targets[s.index]; });
}

module.exports = { findChrome, openDeck, captureSlides, shots, contactSheet, pdf, bake, NO_CHROME };
