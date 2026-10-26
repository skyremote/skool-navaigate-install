/* Deck engine — brand profiles.
   One profile drives BOTH renderers (PPTX + reveal.js HTML).
   Colours are bare hex (no '#') so pptxgenjs is happy; the HTML renderer adds '#'.
   Title-part / line colours are referenced semantically in deck specs
   ("accent", "ink", "coral", "white", "accentD") and resolved per profile.

   Two profiles:
   - "editorial-light": the neutral default (Poppins display + Inter body).
   - "member": built at run time from the member's brand.json by memberProfile(). */

const FONTS_GOOGLE =
  "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&family=Inter:wght@400;500;600;700&display=swap";

const profiles = {
  // Generic light editorial — neutral, one cool accent. The default.
  "editorial-light": {
    label: "",
    bg:"F4F3EF", ink:"17181B", body:"44464B", body2:"5A5C63",
    slate:"202329", slate2:"343842", accent:"6E7F8C", accentD:"3D4A55", accentL:"9CABB6",
    coral:"C07A55", muted:"7E8088", mutedL:"A2A6AE", line:"DFDDD6", paper:"FCFBF8", card:"E9E7E0",
    green:"3E7C63", amber:"C28A3A",
    display:"Poppins Black", displayXB:"Poppins SemiBold", font:"Inter",
    htmlDisplay:"Poppins", htmlFont:"Inter", htmlFontsHref:FONTS_GOOGLE,
    htmlDisplayWeight:900, htmlDisplaySemi:600,
    logo:"", imageStyle:"",
  },
};

// Resolve a semantic colour token to a profile hex (no '#').
function colorOf(P, token) {
  if (!token) return P.ink;
  if (token === "white") return "FFFFFF";
  return P[token] || token; // allow raw hex passthrough
}

// Default type: Poppins (display) + Inter (body) across HTML/PPTX/PDF.
// A member's brand.json overrides it with their own fonts.
const LOCKED_FONTS = {
  display: "Poppins Black", displayXB: "Poppins SemiBold", font: "Inter",
  htmlDisplay: "Poppins", htmlFont: "Inter", htmlFontsHref: FONTS_GOOGLE,
  htmlDisplayWeight: 900, htmlDisplaySemi: 600,
};

/* ---------- member profile (brand.json -> profile) ---------- */

// The colour keys a brand.json may set. Every one is optional; the rest come
// from editorial-light, and accentD/accentL are derived from accent if absent.
const COLOUR_KEYS = ["bg", "ink", "body", "body2", "slate", "slate2", "accent", "accentD", "accentL",
  "coral", "muted", "mutedL", "line", "paper", "card", "green", "amber"];

function bareHex(v, key) {
  const s = String(v == null ? "" : v).trim().replace(/^#/, "").toUpperCase();
  const full = s.length === 3 ? s.split("").map(c => c + c).join("") : s;
  if (!/^[0-9A-F]{6}$/.test(full)) throw new Error(`brand.json: colour "${key}" must be a hex colour like 1F6F5C (got "${v}")`);
  return full;
}

// Mix a hex colour toward black (amount < 0) or white (amount > 0).
function mix(hex, amount) {
  const n = parseInt(hex, 16);
  const ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(c =>
    Math.round(amount < 0 ? c * (1 + amount) : c + (255 - c) * amount));
  return ch.map(c => c.toString(16).padStart(2, "0")).join("").toUpperCase();
}

// brand.json shape (every field optional):
// { "label": "NORTHWIND BAKERY",
//   "colours": { "accent": "C8743A", "ink": "2B211A", ... },     bare hex, '#' tolerated
//   "fonts": { "display": "Fraunces", "body": "Work Sans",
//              "href": "https://fonts.googleapis.com/css2?...",   web fonts for the HTML
//              "displayPptx": "Fraunces SemiBold", "displaySemiPptx": "Fraunces", "bodyPptx": "Work Sans",
//              "displayWeight": 700, "displaySemiWeight": 600 },
//   "logo": "logo.png",                                           path, relative to brand.json
//   "imageStyle": "warm documentary photography, ..." }          art direction for every image
function memberProfile(brand, opts = {}) {
  if (!brand || typeof brand !== "object") throw new Error("brand.json: expected a JSON object");
  const P = Object.assign({}, profiles["editorial-light"]);
  const c = brand.colours || brand.colors || {};
  for (const k of Object.keys(c)) {
    if (!COLOUR_KEYS.includes(k)) throw new Error(`brand.json: unknown colour "${k}". Known: ${COLOUR_KEYS.join(", ")}`);
    P[k] = bareHex(c[k], k);
  }
  if (c.accent && !c.accentD) P.accentD = mix(P.accent, -0.42);
  if (c.accent && !c.accentL) P.accentL = mix(P.accent, 0.35);
  if (c.accent && !c.coral) P.coral = P.accent;
  if (brand.label != null) P.label = String(brand.label);
  const f = brand.fonts || {};
  if (f.display) {
    P.htmlDisplay = f.display;
    P.display = f.displayPptx || f.display;
    P.displayXB = f.displaySemiPptx || f.displayPptx || f.display;
    P.htmlDisplayWeight = f.displayWeight || 700;
    P.htmlDisplaySemi = f.displaySemiWeight || 600;
  }
  if (f.body) { P.htmlFont = f.body; P.font = f.bodyPptx || f.body; }
  if (f.display || f.body) P.htmlFontsHref = f.href || "";
  else if (f.href) P.htmlFontsHref = f.href;
  if (brand.logo) P.logo = opts.baseDir ? require("path").resolve(opts.baseDir, brand.logo) : brand.logo;
  if (brand.imageStyle) P.imageStyle = String(brand.imageStyle);
  return P;
}

module.exports = { profiles, colorOf, FONTS_GOOGLE, LOCKED_FONTS, memberProfile, COLOUR_KEYS, mix };
