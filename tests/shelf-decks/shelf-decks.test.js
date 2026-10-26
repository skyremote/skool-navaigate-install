// Unit tests for the shelf-decks pack (2.0.1). Run: node --test tests/shelf-decks/
// Needs the pack's Node packages: `npm install` in plugins/shelf-decks, or `shelf-decks setup`.
// The bake test also needs Chrome; set SHELF_DECKS_SKIP_BROWSER=1 to skip it.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const PACK = path.resolve(__dirname, "../../plugins/shelf-decks");
const BIN = path.join(PACK, "bin", "shelf-decks");
const SAMPLE = path.join(PACK, "samples", "northwind");
process.env.NODE_PATH = [path.join(PACK, "node_modules"), process.env.SHELF_DECKS_DATA && path.join(process.env.SHELF_DECKS_DATA, "node_modules")].filter(Boolean).join(path.delimiter);
require("module").Module._initPaths();

const { memberProfile, profiles, mix } = require(path.join(PACK, "engine", "profiles.js"));
const brandLib = require(path.join(PACK, "engine", "brand.js"));
const { imageSize } = require(path.join(PACK, "engine", "images.js"));
const has = (m) => { try { require.resolve(m); return true; } catch (e) { return false; } };
const HAVE_DEPS = has("pptxgenjs") && has("jszip");
const tmp = (p) => fs.mkdtempSync(path.join(os.tmpdir(), `shelf-decks-${p}-`));
function cli(args, env = {}, cwd) {
  const home = env.SHELF_DECKS_HOME || tmp("home");
  const r = spawnSync(process.execPath, [BIN, ...args], { cwd: cwd || os.tmpdir(), encoding: "utf8",
    env: Object.assign({}, process.env, { SHELF_DECKS_HOME: home, SHELF_DECKS_BRAND: "" }, env) });
  return { code: r.status, out: (r.stdout || "") + (r.stderr || "") };
}
function copySample(dir) {
  fs.cpSync(SAMPLE, dir, { recursive: true, filter: (s) => !/_v\d+\.|revealjs|\.baked\.png|\/brand$|\.crop|review/.test(s) });
  return path.join(dir, "deck.js");
}

/* ------------------------------------------------ member profile merge -- */

test("member profile: brand colours override editorial-light, '#' is stripped, the rest is inherited", () => {
  const P = memberProfile({ label: "ACME", colours: { accent: "#c2410c", ink: "1C1917", bg: "#FFF" } });
  assert.equal(P.accent, "C2410C");
  assert.equal(P.ink, "1C1917");
  assert.equal(P.bg, "FFFFFF");
  assert.equal(P.label, "ACME");
  assert.equal(P.slate, profiles["editorial-light"].slate);
  assert.equal(P.htmlDisplay, "Poppins");
});

test("member profile: accentD and accentL are derived from accent when not given", () => {
  const P = memberProfile({ colours: { accent: "808080" } });
  assert.equal(P.accentD, mix("808080", -0.42));
  assert.equal(P.accentL, mix("808080", 0.35));
  assert.ok(parseInt(P.accentD, 16) < parseInt("808080", 16));
  assert.ok(parseInt(P.accentL, 16) > parseInt("808080", 16));
  const Q = memberProfile({ colours: { accent: "808080", accentD: "111111" } });
  assert.equal(Q.accentD, "111111");
});

test("member profile: fonts, web-font href, PPTX font names, logo path and image style", () => {
  const P = memberProfile({
    fonts: { display: "Fraunces", body: "Work Sans", href: "https://fonts.example/x.css", displayPptx: "Georgia", bodyPptx: "Arial" },
    logo: "logo.png", imageStyle: "flat illustration",
  }, { baseDir: "/brand/dir" });
  assert.equal(P.htmlDisplay, "Fraunces");
  assert.equal(P.htmlFont, "Work Sans");
  assert.equal(P.htmlFontsHref, "https://fonts.example/x.css");
  assert.equal(P.display, "Georgia");
  assert.equal(P.font, "Arial");
  assert.equal(P.logo, path.resolve("/brand/dir", "logo.png"));
  assert.equal(P.imageStyle, "flat illustration");
});

test("member profile: bad colours and unknown keys are refused with a clear message", () => {
  assert.throws(() => memberProfile({ colours: { accent: "orange" } }), /must be a hex colour/);
  assert.throws(() => memberProfile({ colours: { accentColour: "123456" } }), /unknown colour "accentColour"/);
});

test("profiles: only editorial-light ships; removed brand profiles are refused", () => {
  assert.deepEqual(Object.keys(profiles), ["editorial-light"]);
  const dir = tmp("prof");
  for (const name of ["navaigate-blue", "navaigate-gold", "autodesk", "comxo"]) {
    assert.throws(() => brandLib.resolveProfile({ profile: name, slides: [] }, dir), /Unknown profile/);
  }
  assert.equal(brandLib.resolveProfile({ profile: "editorial-light" }, dir).name, "editorial-light");
});

test("profile member: uses the brand.json beside the spec, else the member's saved brand", () => {
  const dir = tmp("res");
  fs.writeFileSync(path.join(dir, "brand.json"), JSON.stringify({ label: "BESIDE", colours: { accent: "123456" } }));
  const r = brandLib.resolveProfile({ profile: "member" }, dir);
  assert.equal(r.P.label, "BESIDE");
  const empty = tmp("res2"), home = tmp("home");
  const old = process.env.SHELF_DECKS_HOME;
  process.env.SHELF_DECKS_HOME = home;
  try {
    assert.throws(() => brandLib.resolveProfile({ profile: "member" }, empty), /needs a brand.json/);
    fs.writeFileSync(path.join(home, "brand.json"), JSON.stringify({ label: "SAVED" }));
    assert.equal(brandLib.resolveProfile({ profile: "member" }, empty).P.label, "SAVED");
  } finally { if (old === undefined) delete process.env.SHELF_DECKS_HOME; else process.env.SHELF_DECKS_HOME = old; }
});

test("contrast report flags unreadable pairs", () => {
  const good = brandLib.contrastReport(memberProfile({ colours: { ink: "111111", bg: "FFFFFF" } }));
  assert.ok(good.find(r => r.label.startsWith("title text")).ok);
  const bad = brandLib.contrastReport(memberProfile({ colours: { ink: "DDDDDD", bg: "FFFFFF" } }));
  assert.equal(bad.find(r => r.label.startsWith("title text")).ok, false);
});

test("imageSize reads PNG and JPEG headers", () => {
  assert.deepEqual(imageSize(path.join(SAMPLE, "logo.png")), { w: 520, h: 120, type: "png" });
  const j = imageSize(path.join(SAMPLE, "images", "close.jpg"));
  assert.equal(j.type, "jpeg");
  assert.equal(j.w, 1920);
  assert.equal(j.h, 1080);
});

/* --------------------------------------------------- full render -------- */

test("sample renders to HTML and PPTX that match: 10 slides, notes, brand fonts, logo", { skip: !HAVE_DEPS && "run npm install in plugins/shelf-decks" }, async () => {
  const { renderDeck } = require(path.join(PACK, "engine", "render.js"));
  const dir = tmp("render");
  const spec = copySample(dir);
  const r = await renderDeck(spec, { bake: false });
  assert.equal(r.version, 1);
  assert.equal(r.profile, "member");
  const html = fs.readFileSync(r.html, "utf8");
  assert.equal((html.match(/<section class=/g) || []).length, 10);
  assert.equal((html.match(/<aside class="notes">/g) || []).length, 10);
  assert.match(html, /--display:'Fraunces'/);
  assert.match(html, /fonts\.googleapis\.com\/css2\?family=Fraunces/);
  assert.match(html, /src="brand\/logo\.png"/);
  assert.match(html, /class="diagram-slide"/);
  assert.match(html, /window\.deck = deck/);
  assert.ok(fs.existsSync(path.join(dir, "revealjs", "reveal.js")));
  assert.ok(fs.existsSync(path.join(dir, "brand", "logo.png")));

  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(fs.readFileSync(r.pptx));
  const slides = Object.keys(zip.files).filter(f => /^ppt\/slides\/slide\d+\.xml$/.test(f));
  assert.equal(slides.length, 10);
  const notes = Object.keys(zip.files).filter(f => /^ppt\/notesSlides\/notesSlide\d+\.xml$/.test(f));
  assert.equal(notes.length, 10);
  const s2 = await zip.file("ppt/slides/slide2.xml").async("string");
  assert.match(s2, /The first shop is full/);
  assert.match(s2, /Georgia/); // brand.json displayPptx
  assert.match(s2, /Source: Northwind till and card data/);
  const media = Object.keys(zip.files).filter(f => f.startsWith("ppt/media/"));
  assert.ok(media.length >= 4, "cover, split, close images and the logo are embedded");
  assert.ok(r.warnings.some(w => /baking is off/.test(w)));
});

test("never overwrite: a second render writes _v2 and leaves _v1 alone", { skip: !HAVE_DEPS && "deps missing" }, async () => {
  const { renderDeck } = require(path.join(PACK, "engine", "render.js"));
  const dir = tmp("ver");
  const spec = copySample(dir);
  const a = await renderDeck(spec, { bake: false });
  const before = fs.statSync(a.pptx).mtimeMs;
  const b = await renderDeck(spec, { bake: false });
  assert.equal(b.version, 2);
  assert.match(b.html, /_v2\.html$/);
  assert.equal(fs.statSync(a.pptx).mtimeMs, before);
});

test("diagram slides without a PNG are baked in Chrome for the PPTX", { skip: (!HAVE_DEPS || !has("puppeteer-core") || process.env.SHELF_DECKS_SKIP_BROWSER || !require(path.join(PACK, "engine", "capture.js")).findChrome()) && "needs Chrome and puppeteer-core", timeout: 600000 }, async () => {
  const { renderDeck } = require(path.join(PACK, "engine", "render.js"));
  const dir = tmp("bake");
  const spec = copySample(dir);
  const r = await renderDeck(spec, { htmlOnly: false });
  const baked = path.join(dir, "images", "flow.baked.png");
  assert.ok(fs.existsSync(baked), r.warnings.join("; "));
  assert.deepEqual([imageSize(baked).w, imageSize(baked).h], [2560, 1440]);
});

/* --------------------------------------------------------- CLI ---------- */

test("cli: --version and help", () => {
  assert.match(cli(["--version"]).out, /^shelf-decks 2\.0\.1/);
  const h = cli(["--help"]).out;
  for (const c of ["check", "setup", "init", "sample", "new", "render", "shots", "pdf"]) assert.match(h, new RegExp(`shelf-decks ${c}`));
});

test("cli: init writes brand.json in SHELF_DECKS_HOME, updates it, and refuses a bad colour", () => {
  const home = tmp("home");
  const a = cli(["init", "--name", "Acme Studio", "--accent", "#C2410C", "--display", "Fraunces", "--body", "Inter"], { SHELF_DECKS_HOME: home });
  assert.equal(a.code, 0, a.out);
  const b = JSON.parse(fs.readFileSync(path.join(home, "brand.json"), "utf8"));
  assert.equal(b.label, "ACME STUDIO");
  assert.equal(b.colours.accent, "C2410C");
  assert.match(b.fonts.href, /family=Fraunces/);
  assert.match(a.out, /title text/);
  const c = cli(["init", "--ink", "1C1917"], { SHELF_DECKS_HOME: home });
  assert.equal(c.code, 0);
  const b2 = JSON.parse(fs.readFileSync(path.join(home, "brand.json"), "utf8"));
  assert.equal(b2.colours.ink, "1C1917");
  assert.equal(b2.colours.accent, "C2410C");
  const d = cli(["init", "--accent", "orange"], { SHELF_DECKS_HOME: home });
  assert.notEqual(d.code, 0);
  assert.match(d.out, /Not saved/);
  assert.equal(JSON.parse(fs.readFileSync(path.join(home, "brand.json"), "utf8")).colours.accent, "C2410C");
});

test("cli: sample copies the deck with its brand; new starts a member deck without one; both refuse a full folder", () => {
  const root = tmp("cli");
  const s = cli(["sample", path.join(root, "nw")]);
  assert.equal(s.code, 0, s.out);
  assert.ok(fs.existsSync(path.join(root, "nw", "brand.json")));
  assert.ok(fs.existsSync(path.join(root, "nw", "images", "cover.png")));
  assert.notEqual(cli(["sample", path.join(root, "nw")]).code, 0);
  const n = cli(["new", path.join(root, "q3-review")]);
  assert.equal(n.code, 0, n.out);
  const spec = fs.readFileSync(path.join(root, "q3-review", "deck.js"), "utf8");
  assert.match(spec, /profile: "member"/);
  assert.match(spec, /name: "q3-review"/);
  assert.ok(!fs.existsSync(path.join(root, "q3-review", "brand.json")));
  assert.notEqual(cli(["new", path.join(root, "q3-review")]).code, 0);
});

test("cli: pdf refuses to overwrite an existing PDF", () => {
  const dir = tmp("pdf");
  fs.writeFileSync(path.join(dir, "d_v1.html"), "<html></html>");
  fs.writeFileSync(path.join(dir, "d_v1.pdf"), "x");
  const r = cli(["pdf", path.join(dir, "d_v1.html")]);
  if (/Missing Node packages/.test(r.out)) return; // deps not installed here
  assert.notEqual(r.code, 0);
  assert.match(r.out, /never overwrites/);
  assert.equal(fs.readFileSync(path.join(dir, "d_v1.pdf"), "utf8"), "x");
});

/* ---------------------------------------------- de-branding guard ------- */

test("no removed profile, client brand or private string survives in the pack", () => {
  // "navaigate-aios" is the marketplace's id in install commands, not branding.
  const banned = [/navaigate(?!-aios)/i,/autodesk/i, /comxo/i, /katana/i, /navaigate-(blue|gold)/, /nano banana/i, /AIOS[_ ]Playbook/i, /Daniel/, /\/Users\//];
  const hits = [];
  (function walk(dir) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      // node_modules and local eval results are gitignored, never shipped
      if (["node_modules", ".git", "results"].includes(e.name)) continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { walk(p); continue; }
      if (!/\.(js|json|md|css|html|txt)$|^shelf-decks$/.test(e.name)) continue;
      const text = fs.readFileSync(p, "utf8");
      // INTEGRATION.md is the provenance note for the maintainer: it may name where the
      // engine came from, but never a client brand.
      const rules = e.name === "INTEGRATION.md" ? banned.filter(b => !["/navaigate(?!-aios)/i", "/Daniel/"].includes(String(b))) : banned;
      for (const b of rules) if (b.test(text)) hits.push(`${path.relative(PACK, p)}: ${b}`);
    }
  })(PACK);
  assert.deepEqual(hits, []);
});

test("SKILL.md stays under 500 lines with a short description", () => {
  const s = fs.readFileSync(path.join(PACK, "skills", "shelf-decks", "SKILL.md"), "utf8");
  assert.ok(s.split("\n").length < 500);
  const desc = s.match(/^description: (.*)$/m)[1];
  assert.ok((desc.match(/\.(\s|$)/g) || []).length <= 2, "one or two sentences");
});

test("plugin.json and MARKETPLACE_ENTRY.json carry version 2.0.1", () => {
  for (const f of [".claude-plugin/plugin.json", "MARKETPLACE_ENTRY.json", "package.json"]) {
    assert.equal(JSON.parse(fs.readFileSync(path.join(PACK, f), "utf8")).version, "2.0.1", f);
  }
});
