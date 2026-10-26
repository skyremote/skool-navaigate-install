/* Deck engine — the member's brand.json: where it lives, how it loads, and a
   contrast check so text stays readable in the member's colours. */

const fs = require("fs");
const os = require("os");
const path = require("path");
const { memberProfile, profiles } = require("./profiles.js");

// Where the member's own brand.json lives (written by `shelf-decks init`).
function configDir() {
  if (process.env.SHELF_DECKS_HOME) return path.resolve(process.env.SHELF_DECKS_HOME);
  const xdg = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
  return path.join(xdg, "shelf-decks");
}
function defaultBrandPath() { return path.join(configDir(), "brand.json"); }

// Lookup order: the spec's own `brand:` path, a brand.json beside the spec,
// $SHELF_DECKS_BRAND, then the member's saved brand.
function findBrand(specDir, specBrand) {
  const tries = [];
  if (specBrand) tries.push(path.resolve(specDir, specBrand));
  tries.push(path.join(specDir, "brand.json"));
  if (process.env.SHELF_DECKS_BRAND) tries.push(path.resolve(process.env.SHELF_DECKS_BRAND));
  tries.push(defaultBrandPath());
  for (const t of tries) if (fs.existsSync(t)) return t;
  return null;
}

function loadBrand(file) {
  let data;
  try { data = JSON.parse(fs.readFileSync(file, "utf8")); }
  catch (e) { throw new Error(`${file} is not valid JSON: ${e.message}`); }
  return memberProfile(data, { baseDir: path.dirname(file) });
}

// Resolve the profile a spec asks for. "member" = the member's brand.json.
function resolveProfile(spec, specDir) {
  if (spec.profile === "member" || (!spec.profile && findBrand(specDir, spec.brand))) {
    const file = findBrand(specDir, spec.brand);
    if (!file) throw new Error(`profile "member" needs a brand.json. Run: shelf-decks init (writes ${defaultBrandPath()})`);
    return { P: loadBrand(file), brandFile: file, name: "member" };
  }
  const name = spec.profile || "editorial-light";
  const base = profiles[name];
  if (!base) throw new Error(`Unknown profile "${name}". Options: ${Object.keys(profiles).join(", ")}, member`);
  return { P: Object.assign({}, base), brandFile: null, name };
}

/* ---------- WCAG contrast ---------- */
function luminance(hex) {
  const n = parseInt(hex, 16);
  const ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(c => {
    const s = c / 255; return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
}
function contrast(a, b) {
  const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
}
// The text/ground pairs the builders actually use, with the minimum each needs.
function contrastReport(P) {
  const pairs = [
    ["title text (ink) on the page (bg)", P.ink, P.bg, 4.5],
    ["body text (body) on the page (bg)", P.body, P.bg, 4.5],
    ["card text (body2) on a card (paper)", P.body2, P.paper, 4.5],
    ["eyebrow (accentD) on the page (bg)", P.accentD, P.bg, 4.5],
    ["white titles on dark slides (slate)", "FFFFFF", P.slate, 4.5],
    ["big numbers (accentD) on a card (paper)", P.accentD, P.paper, 3],
  ];
  return pairs.map(([label, fg, bg, min]) => {
    const r = contrast(fg, bg);
    return { label, fg, bg, ratio: Math.round(r * 100) / 100, min, ok: r >= min };
  });
}

module.exports = { configDir, defaultBrandPath, findBrand, loadBrand, resolveProfile, contrast, contrastReport };
