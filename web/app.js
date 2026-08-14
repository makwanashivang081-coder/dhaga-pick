const STR = {
  heroTitle: "Photo of cloth → pick dhaga strip",
  heroSub: "Tap a cloth photo. We guess the colour — you approve. Then pick one of 5 recipe strips.",
  stepClothPhoto: "1 · Cloth photo",
  pickClothPhoto: "Tap cloth photo",
  guessAsk: "We think your cloth is:",
  approveCloth: "Yes, correct",
  rejectCloth: "Pick different colour",
  detecting: "Reading cloth colour from photo…",
  detectFail: "Could not read photo — tap a colour below",
  stepClothManual: "Or tap cloth colour",
  orType: "Or type the colour",
  typeColour: "Type: phone, gulabi, lilo, yellow…",
  stepDesignPhoto: "2 · Design photo (optional)",
  chooseDesignPhoto: "Choose design photo",
  clearPhoto: "Clear photo",
  similarPast: "Similar past designs",
  alsoSimilar: "Also similar designs",
  totalNeedles: "Total needles",
  showStrips: "Show 5 recipe strips",
  resetPicks: "Reset",
  pickStrip: "Pick a recipe strip",
  pickStripMeta: "Tap recipe 1–5. Needle number = cloth colour, strip = dhaga colour.",
  modeRecipes: "Recipes",
  modePersonalised: "Personalised",
  personalisedHint: "Tap any dhaga strip below to set each needle (1–5) from different recipes.",
  personalisedRecipe: "Personalised recipe",
  needleSlot: "Needle",
  slotEmpty: "Tap a strip below",
  personalisedReady: "All needles set — tap Use this recipe",
  sixColours: "6 colour options",
  approxNote: "Colour strips follow Royal shade card (screen approx)",
  useThis: "Use this recipe",
  finalRecipe: "Final recipe",
  changeStrip: "Choose another strip",
  startOver: "Start over",
  selected: "Selected",
  pleaseCloth: "Please approve cloth colour from photo or tap one",
  loading: "Loading strips…",
  noRecipes: "No recipes found. Try another cloth.",
  serverDown: "Could not load recipes. Is the server running?",
  photoSelected: "Design photo selected",
  recipe: "Recipe",
  best: "Best",
  needle: "N",
  tikliHere: "Tikli",
  colourPicked: "Thread colour",
  pastNone: "No needle history in the colour book for this design yet.",
  noNeedles: "No needles",
  using: "Using",
  approveFirst: "Approve cloth colour first",
  sampledFromPhoto: "Sampled from your photo",
  matchedPalette: "Matched to palette",
};

const state = {
  cloth: "",
  clothRaw: "",
  clothHex: "#128C7E",
  clothLabel: "",
  sampledHex: "",
  clothApproved: false,
  clothPhotoFile: null,
  clothPhotoUrl: "",
  exactDesignNo: "",
  similarDesignNos: [],
  hasDesignPhoto: false,
  designPhotoFile: null,
  tikliNeedle: 0,
  maxNeedles: 3,
  recipes: [],
  colourOptions: [],
  selectedRank: 0,
  pickedThread: "",
  pickedHex: "",
  mode: "standard",
  personalisedPicks: {},
  resolveTimer: null,
};

const el = {
  pageBg: document.getElementById("page-bg"),
  mainShell: document.getElementById("main-shell"),
  swatches: document.getElementById("cloth-swatches"),
  clothPicked: document.getElementById("cloth-picked"),
  clothText: document.getElementById("cloth-text"),
  manualClothBlock: document.getElementById("manual-cloth-block"),
  openClothPhoto: document.getElementById("open-cloth-photo"),
  clothPhotoUpload: document.getElementById("cloth-photo-upload"),
  clothPhotoPreview: document.getElementById("cloth-photo-preview"),
  clothApproval: document.getElementById("cloth-approval"),
  clothGuessStrip: document.getElementById("cloth-guess-strip"),
  clothGuessLabel: document.getElementById("cloth-guess-label"),
  clothGuessMeta: document.getElementById("cloth-guess-meta"),
  approveCloth: document.getElementById("approve-cloth"),
  rejectCloth: document.getElementById("reject-cloth"),
  threads: document.getElementById("threads"),
  openDesignPhoto: document.getElementById("open-design-photo"),
  designPhotoUpload: document.getElementById("design-photo-upload"),
  designClear: document.getElementById("design-clear"),
  designSelected: document.getElementById("design-selected"),
  exactDesign: document.getElementById("exact-design"),
  exactTitle: document.getElementById("exact-title"),
  exactMeta: document.getElementById("exact-meta"),
  pastRecipes: document.getElementById("past-recipes"),
  similarRow: document.getElementById("similar-row"),
  similarList: document.getElementById("similar-list"),
  start: document.getElementById("start"),
  resetPicks: document.getElementById("reset-picks"),
  stepPanel: document.getElementById("step-panel"),
  designHelp: document.getElementById("design-help"),
  tikliBanner: document.getElementById("tikli-banner"),
  recipeStrips: document.getElementById("recipe-strips"),
  modeRecipes: document.getElementById("mode-recipes"),
  modePersonalised: document.getElementById("mode-personalised"),
  personalisedPanel: document.getElementById("personalised-panel"),
  personalisedSlots: document.getElementById("personalised-slots"),
  colourOptions: document.getElementById("colour-options"),
  pickedThread: document.getElementById("picked-thread"),
  useStrip: document.getElementById("use-strip"),
  finalCanvas: document.getElementById("final-canvas"),
  finalCanvasBg: document.getElementById("final-canvas-bg"),
  finalClothName: document.getElementById("final-cloth-name"),
  finalDhagaStrips: document.getElementById("final-dhaga-strips"),
  finalTikli: document.getElementById("final-tikli"),
  changeStrip: document.getElementById("change-strip"),
  again: document.getElementById("again"),
};

function t(key) {
  return STR[key] || key;
}

function applyStrings() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    if (key) node.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    const key = node.getAttribute("data-i18n-placeholder");
    if (key) node.setAttribute("placeholder", t(key));
  });
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function parseHex(hex) {
  let h = String(hex || "#888888").trim();
  if (h.startsWith("rgb")) {
    const m = h.match(/(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
    if (m) return { r: +m[1], g: +m[2], b: +m[3] };
  }
  h = h.replace("#", "");
  const full = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
  const n = parseInt(full.slice(0, 6), 16);
  if (Number.isNaN(n)) return { r: 136, g: 136, b: 136 };
  return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
}

function rgbCss(c) {
  if (typeof c === "string") return c;
  return "rgb(" + c.r + "," + c.g + "," + c.b + ")";
}

function hexFromRgb(r, g, b) {
  return (
    "#" +
    [r, g, b]
      .map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0"))
      .join("")
  );
}

function clothTextOn(hex) {
  const { r, g, b } = parseHex(hex);
  const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return lum > 0.62 ? "#111b21" : "#ffffff";
}

function rgbToHex(c) {
  return (
    "#" +
    [c.r, c.g, c.b]
      .map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0"))
      .join("")
  );
}

const SPECIAL_THREAD = {
  jari: "#d4af37",
  zari: "#d4af37",
  vw: "#d4af37",
  bch: "#d4af37",
  m: "#c0c0c0",
  md: "#9aa0a6",
  lg: "#e8d48b",
  badla: "#d4af37",
  black: "#1a1a1a",
  white: "#f5f5f5",
  silver: "#c0c0c0",
};

let shadeCodes = null;
let numericBases = null;

function buildNumericBases() {
  numericBases = {};
  for (const [k, v] of Object.entries(shadeCodes || {})) {
    if (/^\d+$/.test(k)) numericBases[+k] = v;
  }
  return numericBases;
}

function nearestNumericHex(num) {
  const bases = numericBases || buildNumericBases();
  const keys = Object.keys(bases).map(Number);
  if (!keys.length) return "";
  if (bases[num]) return bases[num];
  const nearest = keys.reduce((a, b) => (Math.abs(b - num) < Math.abs(a - num) ? b : a));
  return bases[nearest] || "";
}

async function loadShadeCodes() {
  if (shadeCodes) return shadeCodes;
  try {
    const res = await fetch("/api/thread-shades");
    if (!res.ok) throw new Error("no shades");
    const data = await res.json();
    shadeCodes = {};
    for (const [k, v] of Object.entries(data.codes || {})) {
      if (v) shadeCodes[String(k).toUpperCase()] = String(v).toLowerCase();
    }
    buildNumericBases();
  } catch (err) {
    shadeCodes = {};
  }
  return shadeCodes;
}

function parseThreadLabel(thread) {
  let s = String(thread || "").trim().replace(/\s+/g, " ");
  if (!s) return { code: "", mods: "" };
  const low = s.toLowerCase();
  const core = low.replace(/\b(royal|raj|thread|dhaga|viscose)\b/g, " ").replace(/\s+/g, " ").trim();
  let m = core.match(/^([a-z]+)\b/);
  if (m && !/\d/.test(m[1])) return { code: m[1], mods: core.slice(m[0].length).trim() };
  m = core.match(/^(\d+)(.*)/);
  if (!m) return { code: core, mods: "" };
  return { code: m[1], mods: (m[2] || "").replace(/[^a-z]/g, "") };
}

function modifierKeys(code, mods) {
  mods = (mods || "").replace(/[^a-z]/g, "");
  const keys = [];
  if (mods) {
    keys.push(code + "." + mods.toUpperCase());
    for (let i = mods.length - 1; i > 0; i--) keys.push(code + "." + mods.slice(0, i).toUpperCase());
  }
  for (const token of ["ll", "dd", "nl", "nd", "st", "dr", "lr", "ds", "dt"]) {
    if (mods.includes(token)) keys.push(code + "." + token.toUpperCase());
  }
  for (const token of ["l", "d", "n", "s", "b", "f", "r", "t", "p", "u", "c", "h"]) {
    if (mods.includes(token)) keys.push(code + "." + token.toUpperCase());
  }
  keys.push(code);
  const seen = new Set();
  return keys.filter((k) => {
    const ku = k.toUpperCase();
    if (seen.has(ku)) return false;
    seen.add(ku);
    return true;
  });
}

function applyModifiers(hex, mods) {
  mods = (mods || "").toLowerCase();
  let factor = 1;
  if (mods.includes("ll")) factor = 1.28;
  else if (/l/.test(mods) || mods.includes("nl")) factor = 1.16;
  else if (mods.includes("dd")) factor = 0.55;
  else if (/d/.test(mods)) factor = 0.78;
  if (Math.abs(factor - 1) < 0.01) return hex;
  const c = parseHex(hex);
  if (factor > 1) {
    const t = Math.min(1, factor - 1);
    return rgbToHex({
      r: c.r + (255 - c.r) * t,
      g: c.g + (255 - c.g) * t,
      b: c.b + (255 - c.b) * t,
    });
  }
  return rgbToHex({ r: c.r * factor, g: c.g * factor, b: c.b * factor });
}

function lookupThreadHex(thread) {
  const s = String(thread || "").trim();
  if (!s) return "";
  const low = s.toLowerCase();
  if (low.includes("jari") || low.includes("zari")) return SPECIAL_THREAD.jari;
  const { code, mods } = parseThreadLabel(s);
  if (!code) return "";
  if (SPECIAL_THREAD[code] && !/^\d+$/.test(code)) return SPECIAL_THREAD[code];
  const codes = shadeCodes || {};
  for (const key of modifierKeys(code, mods)) {
    const ku = key.toUpperCase();
    if (codes[ku]) return key.includes(".") ? codes[ku] : applyModifiers(codes[ku], mods);
  }
  if (/^\d+$/.test(code)) {
    const near = nearestNumericHex(+code);
    if (near) return applyModifiers(near, mods);
  }
  return "";
}

function chipHex(chip) {
  return (chip && (chip.thread_hex || lookupThreadHex(chip.thread))) || "";
}

async function enrichChipsHex(chips) {
  await loadShadeCodes();
  for (const c of chips || []) {
    if (!c.thread_hex) {
      const hx = lookupThreadHex(c.thread);
      if (hx) c.thread_hex = hx;
    }
  }
  return chips;
}

async function enrichRecipesData() {
  await loadShadeCodes();
  for (const rec of state.recipes || []) {
    await enrichChipsHex(rec.chips);
  }
  for (const opt of state.colourOptions || []) {
    if (!opt.thread_hex) {
      const hx = lookupThreadHex(opt.thread);
      if (hx) opt.thread_hex = hx;
    }
  }
}

function swatchHex(btn) {
  if (!btn) return "#888888";
  const fromData = btn.getAttribute("data-hex");
  if (fromData) return fromData;
  const dot = btn.querySelector(".dot");
  if (dot && dot.style.background) return dot.style.background;
  return "#888888";
}

function clothDisplayName() {
  return state.clothLabel || state.cloth || "";
}

function updateStartButton() {
  if (!el.start) return;
  el.start.disabled = !state.clothApproved || !state.cloth;
}

function markSwatchSelected(id, label) {
  let hex = "#888888";
  el.swatches.querySelectorAll(".swatch").forEach((b) => {
    const match = (b.getAttribute("data-id") || "") === id;
    b.classList.toggle("selected", match);
    if (match) hex = swatchHex(b);
  });
  el.swatches.classList.toggle("has-selection", Boolean(id));
  return hex;
}

function setCloth(id, label, hex, approved) {
  state.cloth = id;
  state.clothLabel = label || id;
  state.clothHex = hex || state.clothHex;
  state.clothApproved = approved !== false;
  markSwatchSelected(id, label);
  updateStartButton();
  if (el.clothPicked && state.clothApproved) {
    el.clothPicked.hidden = false;
    el.clothPicked.textContent = t("selected") + ": " + clothDisplayName();
    el.clothPicked.style.color = "#075E54";
  }
}

function clothStripHtml(hex, label, extraClass) {
  const h = hex || "#888";
  return `
    <div class="cloth-strip-preview ${extraClass || ""}">
      <span class="cloth-strip-bar" style="background:${escapeHtml(h)}"></span>
      ${label ? `<span class="cloth-strip-caption">${escapeHtml(label)}</span>` : ""}
    </div>`;
}

function dhagaRowHtml(chip, opts) {
  const o = opts || {};
  const clothHex = o.clothHex || state.clothHex || "#128C7E";
  const threadHex = chipHex(chip);
  const num = chip.needle;
  const labelColor = threadHex ? clothTextOn(threadHex) : "#111b21";
  const numColor = threadHex ? clothHex : "#111b21";
  const numShadow = threadHex
    ? "0 0 4px rgba(255,255,255,0.95),0 0 8px rgba(255,255,255,0.75),0 2px 6px rgba(0,0,0,0.55)"
    : "none";
  const tikli = chip.is_tikli
    ? `<span class="chip-tikli">${escapeHtml(t("tikliHere"))}</span>`
    : "";
  const size = o.large ? " dhaga-row-large" : "";
  const onCloth = o.onCloth ? " on-cloth" : "";
  const picked =
    o.picked || (state.mode === "personalised" && state.personalisedPicks[num] && state.personalisedPicks[num].thread === chip.thread)
      ? " picked"
      : "";
  const bg = threadHex || "#b0b0b0";
  return `
    <div class="dhaga-row${size}${onCloth}${picked}${chip.is_tikli ? " is-tikli" : ""}" data-needle="${num}">
      <div class="dhaga-strip-bar${threadHex ? "" : " approx"}" style="background:${escapeHtml(bg)}">
        <span class="needle-on-strip" style="color:${escapeHtml(numColor)};text-shadow:${numShadow}">${num}</span>
        <span class="dhaga-on-strip-label" style="color:${labelColor}">
          <strong>${escapeHtml(String(chip.thread || ""))}</strong>${tikli}
        </span>
      </div>
    </div>`;
}

function paintChipHtml(chip) {
  return dhagaRowHtml(chip, { clothHex: state.clothHex });
}

function stripHtml(chips, extraClass) {
  const list = (chips || []).filter((c) => (c.thread || "").trim()).slice(0, state.maxNeedles);
  if (!list.length) return `<p class="meta">${escapeHtml(t("noNeedles"))}</p>`;
  return `<div class="paint-strip ${extraClass || ""}">${list.map(paintChipHtml).join("")}</div>`;
}

function nearestSwatchLocal(r, g, b) {
  let best = null;
  let bestD = Infinity;
  el.swatches.querySelectorAll(".swatch").forEach((btn) => {
    const hex = swatchHex(btn);
    const c = parseHex(hex);
    const d = Math.sqrt((c.r - r) ** 2 + (c.g - g) ** 2 + (c.b - b) ** 2);
    if (d < bestD) {
      bestD = d;
      best = btn;
    }
  });
  if (!best) return null;
  return {
    cloth_id: best.getAttribute("data-id") || "",
    label: best.getAttribute("data-label") || "",
    hex: swatchHex(best),
    gujarati: "",
    confidence: Math.max(0, 1 - bestD / 441),
  };
}

async function sampleColorFromFile(file) {
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = reject;
      image.src = url;
    });
    const size = 96;
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, size, size);
    const data = ctx.getImageData(0, 0, size, size).data;
    const margin = Math.floor(size * 0.12);
    const cx = (size - 1) / 2;
    const cy = (size - 1) / 2;
    const maxDist = Math.sqrt(cx * cx + cy * cy) || 1;
    const usable = [];
    for (let y = margin; y < size - margin; y++) {
      for (let x = margin; x < size - margin; x++) {
        const i = (y * size + x) * 4;
        const pr = data[i];
        const pg = data[i + 1];
        const pb = data[i + 2];
        const lum = (pr + pg + pb) / 3;
        const spread = Math.max(pr, pg, pb) - Math.min(pr, pg, pb);
        if (lum < 20 || lum > 245) continue;
        if (spread < 7) continue;
        const dist = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2);
        const w = 1 - (dist / maxDist) * 0.55;
        const score = w * (0.55 + Math.min(spread / 128, 1));
        usable.push([pr, pg, pb, score]);
      }
    }
    const pool = usable.length ? usable : [[128, 128, 128, 1]];
    const total = pool.reduce((s, p) => s + p[3], 0) || 1;
    const r = pool.reduce((s, p) => s + p[0] * p[3], 0) / total;
    const g = pool.reduce((s, p) => s + p[1] * p[3], 0) / total;
    const b = pool.reduce((s, p) => s + p[2] * p[3], 0) / total;
    return { r, g, b, sampled_hex: hexFromRgb(r, g, b) };
  } finally {
    URL.revokeObjectURL(url);
  }
}

async function detectClothFromPhoto(file) {
  let data = null;
  try {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch("/api/detect-cloth-color", { method: "POST", body: fd });
    if (res.ok) data = await res.json();
  } catch (err) {
    /* offline fallback below */
  }
  if (data && data.cloth_id) return data;
  const sample = await sampleColorFromFile(file);
  const local = nearestSwatchLocal(sample.r, sample.g, sample.b);
  if (!local) return null;
  return {
    sampled_hex: sample.sampled_hex,
    cloth_id: local.cloth_id,
    label: local.label,
    hex: local.hex,
    gujarati: local.gujarati,
    confidence: local.confidence,
    message: t("matchedPalette") + ": " + local.label,
    understood_as: local.label,
  };
}

function showClothApproval(data) {
  if (!el.clothApproval || !data) return;
  state.sampledHex = data.sampled_hex || data.hex || "";
  const name = data.label || data.understood_as;
  el.clothApproval.hidden = false;
  el.clothGuessStrip.innerHTML = `
    <div class="cloth-guess-pair">
      ${clothStripHtml(data.sampled_hex, t("sampledFromPhoto"), "sampled")}
      ${clothStripHtml(data.hex, t("matchedPalette"), "matched")}
    </div>`;
  el.clothGuessLabel.textContent = name || data.cloth_id;
  const pct = Math.round((Number(data.confidence) || 0) * 100);
  el.clothGuessMeta.textContent = (data.message || "") + (pct ? " · ~" + pct + "%" : "");
  state.cloth = data.cloth_id;
  state.clothLabel = data.label || data.cloth_id;
  state.clothHex = data.hex || state.sampledHex;
  state.clothApproved = false;
  updateStartButton();
}

function approveClothGuess() {
  state.clothApproved = true;
  if (el.clothApproval) el.clothApproval.hidden = true;
  setCloth(state.cloth, state.clothLabel, state.clothHex, true);
}

function rejectClothGuess() {
  state.clothApproved = false;
  if (el.clothApproval) el.clothApproval.hidden = true;
  if (el.manualClothBlock) el.manualClothBlock.hidden = false;
  updateStartButton();
}

async function onClothPhotoPicked(file) {
  if (!file) return;
  state.clothPhotoFile = file;
  state.clothApproved = false;
  if (state.clothPhotoUrl) URL.revokeObjectURL(state.clothPhotoUrl);
  state.clothPhotoUrl = URL.createObjectURL(file);
  el.clothPhotoPreview.hidden = false;
  el.clothPhotoPreview.innerHTML = `
    <img src="${state.clothPhotoUrl}" alt="" />
    <p>${escapeHtml(t("detecting"))}</p>`;
  el.clothApproval.hidden = true;
  el.manualClothBlock.hidden = true;
  updateStartButton();
  const data = await detectClothFromPhoto(file);
  el.clothPhotoPreview.innerHTML = `<img src="${state.clothPhotoUrl}" alt="" />`;
  if (!data || !data.cloth_id) {
    el.clothPhotoPreview.innerHTML += `<p class="meta bad">${escapeHtml(t("detectFail"))}</p>`;
    el.manualClothBlock.hidden = false;
    return;
  }
  showClothApproval(data);
}

const LOCAL_ALIASES = {
  phone: "peach",
  phon: "peach",
  fone: "peach",
  peach: "peach",
  gulabi: "pink",
  pink: "pink",
  lilo: "green",
  leelo: "green",
  green: "green",
  pilo: "yellow",
  yellow: "yellow",
  badami: "fawn",
  fawn: "fawn",
  gray: "grey",
  grey: "grey",
  safed: "white",
  white: "white",
  kalo: "black",
  black: "black",
  lal: "red",
  red: "red",
  narangi: "orange",
  orange: "orange",
  cream: "cream",
  maroon: "maroon",
  wine: "wine",
  rama: "rama",
  firozi: "firozi",
  purple: "purple",
  blue: "blue",
  brown: "brown",
  gold: "gold",
  mustard: "mustard",
  lemon: "lemon",
  chiku: "chiku",
  pista: "pista",
  rani: "rani",
  gajri: "gajri",
  rust: "rust",
  violet: "violet",
  "sky blue": "sky blue",
  "light green": "light green",
};

function localResolveCloth(text) {
  const raw = String(text || "").trim();
  const cleaned = raw.toLowerCase().replace(/[.,;:!?]/g, " ").replace(/\s+/g, " ").trim();
  let base = LOCAL_ALIASES[cleaned] || "";
  if (!base) {
    for (const tok of cleaned.split(" ")) {
      if (LOCAL_ALIASES[tok]) {
        base = LOCAL_ALIASES[tok];
        break;
      }
    }
  }
  if (!base) {
    const btn = el.swatches.querySelector('.swatch[data-id="' + cleaned.replace(/"/g, "") + '"]');
    if (btn) base = cleaned;
  }
  if (!base) return null;
  const btn = el.swatches.querySelector('.swatch[data-id="' + base + '"]');
  if (!btn) return null;
  return {
    cloth_id: base,
    label: btn.getAttribute("data-label") || base,
    hex: swatchHex(btn),
    message: t("using") + " " + (btn.getAttribute("data-label") || base),
  };
}

async function resolveClothNow() {
  const text = (el.clothText.value || "").trim();
  if (!text) return null;
  const local = localResolveCloth(text);
  if (local) {
    state.clothRaw = text;
    setCloth(local.cloth_id, local.label, local.hex, true);
  }
  try {
    const res = await fetch("/api/resolve-cloth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, shade_value: 50 }),
    });
    if (!res.ok) return local;
    const data = await res.json();
    if (data.cloth_id) {
      state.clothRaw = text;
      setCloth(data.cloth_id, data.label || data.understood_as, data.hex, true);
    }
    return data;
  } catch (err) {
    return local;
  }
}

function bindSwatches() {
  el.swatches.querySelectorAll(".swatch").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-id") || "";
      const label = btn.getAttribute("data-label") || id;
      el.clothText.value = "";
      state.clothRaw = id;
      setCloth(id, label, swatchHex(btn), true);
      if (el.clothApproval) el.clothApproval.hidden = true;
    });
  });
}

function clearDesignPhoto() {
  state.similarDesignNos = [];
  state.exactDesignNo = "";
  state.hasDesignPhoto = false;
  state.designPhotoFile = null;
  el.designPhotoUpload.value = "";
  el.designClear.hidden = true;
  el.designSelected.hidden = true;
  el.designSelected.innerHTML = "";
  el.similarRow.hidden = true;
  el.similarList.innerHTML = "";
  clearExactDesign();
}

function clearExactDesign() {
  state.exactDesignNo = "";
  if (!el.exactDesign) return;
  el.exactDesign.hidden = true;
  el.exactTitle.textContent = "";
  el.exactMeta.textContent = "";
  el.pastRecipes.innerHTML = "";
}

async function fetchSimilarUpload(file) {
  try {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("top_k", "8");
    const res = await fetch("/api/gallery/similar", { method: "POST", body: fd });
    if (!res.ok) {
      state.similarDesignNos = state.exactDesignNo ? [state.exactDesignNo] : [];
      return;
    }
    const data = await res.json();
    showExactDesign(data.exact_design || null);
    const matched = data.matched_design_nos || [];
    if (matched.length) state.similarDesignNos = matched;
    showSimilar(data.similar || [], Boolean(data.exact_design));
    if (!state.similarDesignNos.length && state.exactDesignNo) {
      state.similarDesignNos = [state.exactDesignNo];
    }
  } catch (err) {
    console.error(err);
  }
}

function showExactDesign(exact) {
  if (!el.exactDesign) return;
  if (!exact || !exact.design_no) {
    clearExactDesign();
    return;
  }
  state.exactDesignNo = String(exact.design_no);
  state.similarDesignNos = [state.exactDesignNo, ...state.similarDesignNos.filter((d) => d !== state.exactDesignNo)];
  el.exactDesign.hidden = false;
  el.exactTitle.textContent = exact.message || "Exact same design found: #" + exact.design_no;
  const cloths = (exact.cloths_used || []).join(", ");
  el.exactMeta.textContent = cloths
    ? "Past cloths: " + cloths
    : exact.past_count
      ? exact.past_count + " past recipes"
      : "Matched in gallery";

  const rows = exact.past_recipes || [];
  if (!rows.length) {
    el.pastRecipes.innerHTML = '<p class="meta">' + escapeHtml(t("pastNone")) + "</p>";
    return;
  }
  el.pastRecipes.innerHTML = rows
    .map((r) => {
      const chips =
        r.chips && r.chips.length
          ? r.chips
          : [r.n1, r.n2, r.n3, r.n4, r.n5]
              .map((n, i) => ({
                needle: i + 1,
                thread: n || "",
                thread_hex: "",
                is_tikli: r.tikli_needle === i + 1,
              }))
              .filter((c) => c.thread);
      return `<div class="past-card"><div class="past-top"><strong>${escapeHtml(r.cloth || "—")}</strong></div>${stripHtml(chips, "compact")}</div>`;
    })
    .join("");
}

function showSimilar(rows, hasExact) {
  const nos = [...new Set(rows.map((r) => r.design_no).filter(Boolean))];
  if (nos.length) {
    state.similarDesignNos = state.exactDesignNo
      ? [state.exactDesignNo, ...nos.filter((d) => d !== state.exactDesignNo)]
      : nos;
  } else if (state.exactDesignNo) {
    state.similarDesignNos = [state.exactDesignNo];
  }
  if (!rows.length) {
    el.similarRow.hidden = true;
    el.similarList.innerHTML = "";
    return;
  }
  el.similarRow.hidden = false;
  const label = el.similarRow.querySelector(".similar-label");
  if (label) label.textContent = hasExact ? t("alsoSimilar") : t("similarPast");
  el.similarList.innerHTML = rows
    .map((r) => {
      const badge = r.exact ? ' <span class="exact-badge">exact</span>' : "";
      return `<div class="similar-chip${r.exact ? " is-exact" : ""}">${r.thumb_url ? `<img src="${escapeHtml(r.thumb_url)}" alt="" loading="lazy" />` : ""}<span>${escapeHtml(r.design_no)}${badge}</span></div>`;
    })
    .join("");
}

function resetStripFlow() {
  state.recipes = [];
  state.colourOptions = [];
  state.selectedRank = 0;
  state.pickedThread = "";
  state.pickedHex = "";
  state.mode = "standard";
  state.personalisedPicks = {};
  el.finalCanvas.hidden = true;
  document.body.classList.remove("final-mode");
  document.body.style.background = "";
  document.body.style.removeProperty("--final-cloth");
  if (el.pageBg) el.pageBg.style.display = "";
  el.mainShell.hidden = false;
  const formPanel = el.mainShell.querySelector("#form-panel");
  if (formPanel) formPanel.hidden = false;
  el.stepPanel.hidden = true;
  el.resetPicks.hidden = true;
  el.recipeStrips.innerHTML = "";
  el.colourOptions.innerHTML = "";
  el.pickedThread.hidden = true;
  el.pickedThread.innerHTML = "";
  el.useStrip.hidden = true;
  if (el.modeRecipes) el.modeRecipes.classList.add("active");
  if (el.modePersonalised) el.modePersonalised.classList.remove("active");
  if (el.personalisedPanel) el.personalisedPanel.hidden = true;
  if (el.personalisedSlots) el.personalisedSlots.innerHTML = "";
  if (el.designHelp) {
    el.designHelp.hidden = true;
    el.designHelp.textContent = "";
  }
}

async function ensureCloth() {
  if (!state.clothApproved || !state.cloth) {
    if (el.clothPicked) {
      el.clothPicked.hidden = false;
      el.clothPicked.textContent = t("approveFirst");
      el.clothPicked.style.color = "#c0392b";
    }
    return false;
  }
  if (el.clothText.value.trim()) await resolveClothNow();
  return true;
}

async function loadRecipes() {
  const ok = await ensureCloth();
  if (!ok) return;

  state.maxNeedles = Number(el.threads.value || 3);
  el.stepPanel.hidden = false;
  el.finalCanvas.hidden = true;
  document.body.classList.remove("final-mode");
  document.body.style.background = "";
  document.body.style.removeProperty("--final-cloth");
  if (el.pageBg) el.pageBg.style.display = "";
  el.mainShell.hidden = false;
  el.resetPicks.hidden = false;
  el.recipeStrips.innerHTML = '<p class="meta">' + escapeHtml(t("loading")) + "</p>";

  if (state.designPhotoFile) await fetchSimilarUpload(state.designPhotoFile);

  const body = {
    cloth: state.cloth,
    cloth_raw: (el.clothText.value || "").trim() || state.clothRaw || state.cloth,
    shade_value: 50,
    design_no: state.exactDesignNo || "",
    thread_count: state.maxNeedles,
    similar_design_nos: state.similarDesignNos,
    has_design_photo: Boolean(state.hasDesignPhoto || state.designPhotoFile),
  };

  try {
    const res = await fetch("/api/recommend-recipes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("fail");
    const data = await res.json();
    if (data.cloth && data.cloth.cloth_id) state.cloth = data.cloth.cloth_id;
    if (data.cloth && data.cloth.hex) state.clothHex = data.cloth.hex;
    showDesignHelp(data.design_help_percent, data.design_help_note, data);
    showTikli(data.tikli || null);
    state.recipes = data.recipes || [];
    state.colourOptions = data.colour_options || [];
    await enrichRecipesData();
    if (!state.selectedRank && state.recipes.length) state.selectedRank = 1;
    if (el.modeRecipes) el.modeRecipes.classList.toggle("active", state.mode === "standard");
    if (el.modePersonalised) el.modePersonalised.classList.toggle("active", state.mode === "personalised");
    renderPersonalisedPanel();
    renderRecipeStrips();
    renderColourOptions();
    el.stepPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    el.recipeStrips.innerHTML = '<p class="meta">' + escapeHtml(t("serverDown")) + "</p>";
  }
}

function showTikli(info) {
  state.tikliNeedle = info && info.tikli_needle ? Number(info.tikli_needle) : 0;
  const html =
    info && info.has_tikli && info.tikli_needle
      ? escapeHtml(t("tikliHere")) + " · <strong>" + escapeHtml(t("needle")) + info.tikli_needle + "</strong>"
      : "";
  if (el.tikliBanner) {
    el.tikliBanner.hidden = !html;
    el.tikliBanner.innerHTML = html;
  }
  if (el.finalTikli) {
    el.finalTikli.hidden = !html;
    el.finalTikli.innerHTML = html;
  }
}

function showDesignHelp(pct, note, meta) {
  if (!el.designHelp) return;
  const n = Math.max(0, Math.min(100, Number(pct) || 0));
  el.designHelp.hidden = false;
  el.designHelp.className = "design-help" + (n > 0 ? " has-help" : "");
  el.designHelp.innerHTML =
    "<div class='design-help-top'><strong>Design +" +
    n +
    "%</strong></div><div class='design-help-bar'><span style='width:" +
    n +
    "%'></span></div><p class='design-help-note'>" +
    escapeHtml(note || "") +
    "</p>";
}

function selectedRecipe() {
  if (state.mode === "personalised" && personalisedComplete()) {
    return { rank: "P", label: t("personalisedRecipe"), chips: personalisedChips() };
  }
  return state.recipes.find((r) => r.rank === state.selectedRank) || state.recipes[0] || null;
}

function personalisedChips() {
  const out = [];
  for (let i = 1; i <= state.maxNeedles; i++) {
    const p = state.personalisedPicks[i];
    if (!p || !p.thread) continue;
    out.push({
      needle: i,
      thread: p.thread,
      thread_hex: p.thread_hex || lookupThreadHex(p.thread),
      is_tikli: Boolean(p.is_tikli),
    });
  }
  return out;
}

function personalisedComplete() {
  for (let i = 1; i <= state.maxNeedles; i++) {
    const p = state.personalisedPicks[i];
    if (!p || !(p.thread || "").trim()) return false;
  }
  return true;
}

function setRecipeMode(mode) {
  state.mode = mode === "personalised" ? "personalised" : "standard";
  if (state.mode === "personalised") {
    state.personalisedPicks = {};
    state.selectedRank = 0;
  }
  if (el.modeRecipes) el.modeRecipes.classList.toggle("active", state.mode === "standard");
  if (el.modePersonalised) el.modePersonalised.classList.toggle("active", state.mode === "personalised");
  renderPersonalisedPanel();
  renderRecipeStrips();
  updateUseStripButton();
}

function renderPersonalisedPanel() {
  if (!el.personalisedPanel || !el.personalisedSlots) return;
  const show = state.mode === "personalised";
  el.personalisedPanel.hidden = !show;
  if (!show) {
    el.personalisedSlots.innerHTML = "";
    return;
  }
  const slots = [];
  for (let i = 1; i <= state.maxNeedles; i++) {
    const pick = state.personalisedPicks[i];
    if (pick && pick.thread) {
      slots.push(dhagaRowHtml({ ...pick, needle: i }, { clothHex: state.clothHex, picked: true }));
    } else {
      slots.push(
        `<div class="personalised-slot-empty"><span class="slot-num" style="color:${escapeHtml(state.clothHex)}">${i}</span><span>${escapeHtml(t("slotEmpty"))}</span></div>`
      );
    }
  }
  el.personalisedSlots.innerHTML =
    `<p class="meta personalised-hint">${escapeHtml(t("personalisedHint"))}</p>` +
    `<div class="personalised-slots-row">${slots.join("")}</div>` +
    (personalisedComplete() ? `<p class="meta personalised-ready">${escapeHtml(t("personalisedReady"))}</p>` : "");
}

function updateUseStripButton() {
  if (!el.useStrip) return;
  if (state.mode === "personalised") {
    el.useStrip.hidden = !personalisedComplete();
  } else {
    el.useStrip.hidden = !state.selectedRank;
  }
}

function assignPersonalisedPick(chip) {
  if (!chip || !chip.needle) return;
  state.personalisedPicks[chip.needle] = {
    needle: chip.needle,
    thread: chip.thread,
    thread_hex: chipHex(chip),
    is_tikli: Boolean(chip.is_tikli),
  };
  renderPersonalisedPanel();
  renderRecipeStrips();
  updateUseStripButton();
}

function renderRecipeStrips() {
  if (!state.recipes.length) {
    el.recipeStrips.innerHTML = '<p class="meta">' + escapeHtml(t("noRecipes")) + "</p>";
    el.useStrip.hidden = true;
    return;
  }
  if (!state.pickedThread) {
    const rec0 = selectedRecipe();
    if (rec0 && rec0.chips && rec0.chips[0]) {
      state.pickedThread = rec0.chips[0].thread || "";
      state.pickedHex = chipHex(rec0.chips[0]) || "";
    }
  }
  el.recipeStrips.innerHTML = state.recipes
    .map((rec) => {
      const on = rec.rank === state.selectedRank ? " selected" : "";
      const best = rec.rank === 1 ? " best" : "";
      const mark = rec.rank === state.selectedRank ? " ✓" : "";
      const chips = (rec.chips || []).slice(0, state.maxNeedles);
      return `
        <button type="button" class="recipe-strip-card${on}${best}" data-rank="${rec.rank}">
          <div class="strip-head">
            <span class="strip-num">${escapeHtml(t("recipe"))} ${rec.rank}${mark}</span>
            ${rec.rank === 1 ? `<span class="badge">${escapeHtml(t("best"))}</span>` : ""}
          </div>
          ${stripHtml(chips)}
        </button>`;
    })
    .join("");

  el.recipeStrips.querySelectorAll(".recipe-strip-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (state.mode === "personalised") return;
      state.selectedRank = Number(btn.getAttribute("data-rank") || 1);
      state.pickedThread = "";
      state.pickedHex = "";
      renderRecipeStrips();
      updateUseStripButton();
    });
  });
  el.recipeStrips.querySelectorAll(".dhaga-row").forEach((row) => {
    row.addEventListener("click", (ev) => {
      ev.stopPropagation();
      const wrap = row.closest(".recipe-strip-card");
      const nameEl = row.querySelector(".dhaga-on-strip-label strong");
      const bar = row.querySelector(".dhaga-strip-bar");
      const needle = Number(row.getAttribute("data-needle") || 0);
      const thread = nameEl ? nameEl.textContent.trim() : "";
      const hex = bar && bar.style.background ? bar.style.background : lookupThreadHex(thread);
      if (state.mode === "personalised") {
        const rec = state.recipes.find((r) => r.rank === Number(wrap && wrap.getAttribute("data-rank")));
        const chip = (rec && rec.chips || []).find((c) => c.needle === needle && c.thread === thread) || {
          needle,
          thread,
          thread_hex: hex,
          is_tikli: false,
        };
        assignPersonalisedPick(chip);
        return;
      }
      state.pickedThread = thread;
      state.pickedHex = hex;
      if (wrap) state.selectedRank = Number(wrap.getAttribute("data-rank") || state.selectedRank);
      renderRecipeStrips();
      updateUseStripButton();
    });
  });
  updateUseStripButton();
  if (state.mode === "personalised") renderPersonalisedPanel();
  showSelectedThreadPreview();
}

function renderColourOptions() {
  const opts = (state.colourOptions || []).slice(0, 6);
  if (!opts.length) {
    el.colourOptions.innerHTML = "";
    return;
  }
  el.colourOptions.innerHTML = opts
    .map((opt) => {
      const chip = {
        needle: opt.rank,
        thread: opt.thread,
        thread_hex: opt.thread_hex || "",
        is_tikli: false,
      };
      const hx = chipHex(chip);
      const on = (opt.thread || "") === state.pickedThread ? " selected" : "";
      return `<button type="button" class="colour-opt-btn${on}" data-thread="${escapeHtml(opt.thread || "")}" data-hex="${escapeHtml(hx)}">${dhagaRowHtml(chip, { clothHex: state.clothHex })}</button>`;
    })
    .join("");
  el.colourOptions.querySelectorAll(".colour-opt-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.pickedThread = btn.getAttribute("data-thread") || "";
      state.pickedHex = btn.getAttribute("data-hex") || "";
      renderColourOptions();
      renderRecipeStrips();
    });
  });
}

function showPickedThread(thread, hex) {
  if (!el.pickedThread || !thread) return;
  state.pickedThread = thread;
  state.pickedHex = hex || "";
  el.pickedThread.hidden = false;
  el.pickedThread.innerHTML = `
    <p class="picked-kicker">${escapeHtml(t("colourPicked"))}</p>
    ${dhagaRowHtml({ needle: "?", thread, thread_hex: hex, is_tikli: false }, { clothHex: state.clothHex, large: true })}`;
}

function showSelectedThreadPreview() {
  if (state.pickedThread) {
    showPickedThread(state.pickedThread, state.pickedHex);
    return;
  }
  const rec = selectedRecipe();
  if (!rec || !rec.chips || !rec.chips.length) return;
  const first = rec.chips[0];
  showPickedThread(first.thread, chipHex(first) || "");
}

function showFinal() {
  const rec = selectedRecipe();
  if (!rec) return;
  const chips = (rec.chips || []).slice(0, state.maxNeedles);
  const cloth = state.clothHex || "#128C7E";
  el.stepPanel.hidden = true;
  el.mainShell.hidden = true;
  document.body.classList.add("final-mode");
  document.body.style.setProperty("--final-cloth", cloth);
  document.body.style.background = cloth;
  if (el.pageBg) el.pageBg.style.display = "none";
  el.finalCanvas.hidden = false;
  el.finalCanvasBg.style.background = cloth;
  el.finalClothName.textContent =
    clothDisplayName() +
    " · " +
    (rec.rank === "P" ? t("personalisedRecipe") : t("recipe") + " " + rec.rank);
  el.finalDhagaStrips.innerHTML = chips
    .map((c) => dhagaRowHtml(c, { clothHex: cloth, large: true, onCloth: true }))
    .join("");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

loadShadeCodes();
applyStrings();
bindSwatches();
updateStartButton();

el.clothText.addEventListener("input", () => {
  clearTimeout(state.resolveTimer);
  state.resolveTimer = setTimeout(resolveClothNow, 350);
});
el.clothText.addEventListener("change", resolveClothNow);
el.clothText.addEventListener("blur", resolveClothNow);

el.openClothPhoto.addEventListener("click", () => el.clothPhotoUpload.click());
el.clothPhotoUpload.addEventListener("change", async () => {
  const file = el.clothPhotoUpload.files && el.clothPhotoUpload.files[0];
  if (file) await onClothPhotoPicked(file);
});
el.approveCloth.addEventListener("click", approveClothGuess);
el.rejectCloth.addEventListener("click", rejectClothGuess);

el.openDesignPhoto.addEventListener("click", () => el.designPhotoUpload.click());
el.designPhotoUpload.addEventListener("change", async () => {
  const file = el.designPhotoUpload.files && el.designPhotoUpload.files[0];
  if (!file) return;
  state.designPhotoFile = file;
  state.hasDesignPhoto = true;
  el.designClear.hidden = false;
  el.designSelected.hidden = false;
  el.designSelected.innerHTML = `<img src="${URL.createObjectURL(file)}" alt="" /><div><strong>${escapeHtml(t("photoSelected"))}</strong><p>${escapeHtml(file.name)}</p></div>`;
  await fetchSimilarUpload(file);
});
el.designClear.addEventListener("click", clearDesignPhoto);

el.start.addEventListener("click", () => {
  state.selectedRank = 0;
  state.mode = "standard";
  state.personalisedPicks = {};
  loadRecipes();
});
el.resetPicks.addEventListener("click", resetStripFlow);
if (el.modeRecipes) el.modeRecipes.addEventListener("click", () => setRecipeMode("standard"));
if (el.modePersonalised) el.modePersonalised.addEventListener("click", () => setRecipeMode("personalised"));
el.useStrip.addEventListener("click", showFinal);
el.changeStrip.addEventListener("click", () => {
  el.finalCanvas.hidden = true;
  document.body.classList.remove("final-mode");
  document.body.style.background = "";
  document.body.style.removeProperty("--final-cloth");
  if (el.pageBg) el.pageBg.style.display = "";
  el.mainShell.hidden = false;
  el.stepPanel.hidden = false;
  el.stepPanel.scrollIntoView({ behavior: "smooth", block: "start" });
});
el.again.addEventListener("click", () => {
  resetStripFlow();
  window.scrollTo({ top: 0, behavior: "smooth" });
});
