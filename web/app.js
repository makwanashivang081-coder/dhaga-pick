const LANG_KEY = "dhaga_pick_lang";

const I18N = {
  en: {
    heroTitle: "Pick cloth, then pick a dhaga strip",
    heroSub: "Tap a bold colour. Optionally add a design photo. Then choose one of 5 recipe strips.",
    stepCloth: "1 · Cloth colour — tap one",
    tapColour: "Tap a colour above",
    shadeAsk: "How light / dark is this cloth?",
    lighter: "Lighter",
    normal: "Normal",
    darker: "Darker",
    slideShade: "Slide for lighter or darker shade",
    orType: "Or type the colour (if not in the list)",
    typeColour: "Type here: phone, gulabi, lilo, પીળો…",
    stepPhoto: "2 · Design photo (optional)",
    choosePhoto: "Choose from my gallery",
    clearPhoto: "Clear photo",
    similarPast: "Similar past designs",
    alsoSimilar: "Also similar designs",
    totalNeedles: "Total needles",
    showStrips: "Show 5 recipe strips",
    resetPicks: "Reset",
    pickStrip: "Pick a recipe strip",
    pickStripMeta: "Tap recipe 1–5. You can change anytime.",
    sixColours: "6 colour options",
    approxNote: "Colour chips follow Royal shade card (screen approx)",
    useThis: "Use this recipe",
    finalRecipe: "Final recipe",
    yourMap: "Your chosen dhaga strip",
    changeStrip: "Choose another strip",
    startOver: "Start over",
    selected: "Selected",
    pleaseCloth: "Please tap a cloth colour or type one",
    loading: "Loading strips…",
    noRecipes: "No recipes found. Try another cloth.",
    serverDown: "Could not load recipes. Is the server running?",
    photoSelected: "Design photo selected",
    recipe: "Recipe",
    best: "Best",
    needle: "N",
    tikliHere: "Tikli",
    colourPicked: "Thread colour",
    clothPalette: "Chosen cloth palette",
    pastNone: "No needle history in the colour book for this design yet.",
    noNeedles: "No needles",
    nowSlide: "Now slide for lighter or darker",
    using: "Using",
  },
  gu: {
    heroTitle: "કપડાનો રંગ પસંદ કરો, પછી ધાગાની પટ્ટી",
    heroSub: "બોલ્ડ રંગ દબાવો. ફોટો ઐચ્છિક છે. પછી 5 પટ્ટીઓમાંથી એક પસંદ કરો.",
    stepCloth: "1 · કપડાનો રંગ — એક દબાવો",
    tapColour: "ઉપરથી રંગ દબાવો",
    shadeAsk: "આ કપડું આછું છે કે ઘેરું?",
    lighter: "આછું",
    normal: "સામાન્ય",
    darker: "ઘેરું",
    slideShade: "આછા / ઘેરા માટે સ્લાઇડ કરો",
    orType: "અથવા રંગ લખો (યાદીમાં ન હોય તો)",
    typeColour: "અહીં લખો: phone, gulabi, lilo, પીળો…",
    stepPhoto: "2 · ડિઝાઇન ફોટો (ઐચ્છિક)",
    choosePhoto: "ગેલેરીમાંથી પસંદ કરો",
    clearPhoto: "ફોટો કાઢો",
    similarPast: "મળતી જૂની ડિઝાઇન",
    alsoSimilar: "અન્ય મળતી ડિઝાઇન",
    totalNeedles: "કુલ સોય",
    showStrips: "5 પટ્ટીઓ બતાવો",
    resetPicks: "રીસેટ",
    pickStrip: "ધાગાની પટ્ટી પસંદ કરો",
    pickStripMeta: "રેસિપી 1–5 દબાવો. ગમે ત્યારે બદલી શકો.",
    sixColours: "6 રંગ વિકલ્પ",
    approxNote: "રંગ શેડ કાર્ડ પ્રમાણે (સ્ક્રીન અંદાજ)",
    useThis: "આ રેસિપી વાપરો",
    finalRecipe: "અંતિમ રેસિપી",
    yourMap: "તમારી પસંદ કરેલી ધાગા પટ્ટી",
    changeStrip: "બીજી પટ્ટી પસંદ કરો",
    startOver: "ફરી શરૂ",
    selected: "પસંદ",
    pleaseCloth: "કૃપા કરી કપડાનો રંગ દબાવો અથવા લખો",
    loading: "પટ્ટીઓ લાવી રહ્યા છીએ…",
    noRecipes: "રેસિપી ન મળી. બીજો રંગ અજમાવો.",
    serverDown: "રેસિપી ન લાગી. સર્વર ચાલુ છે?",
    photoSelected: "ડિઝાઇન ફોટો પસંદ થયો",
    recipe: "રેસિપી",
    best: "શ્રેષ્ઠ",
    needle: "સોય",
    tikliHere: "ટિકલી",
    colourPicked: "ધાગાનો રંગ",
    clothPalette: "પસંદ કરેલા કપડાની પેલેટ",
    pastNone: "આ ડિઝાઇન માટે હજુ કલર બુકમાં સોય નથી.",
    noNeedles: "સોય નથી",
    nowSlide: "હવે આછા / ઘેરા માટે સ્લાઇડ કરો",
    using: "વાપરી રહ્યા છીએ",
  },
};

const state = {
  lang: "en",
  cloth: "",
  clothRaw: "",
  clothHex: "#128C7E",
  clothLabel: "",
  shadeValue: 50,
  exactDesignNo: "",
  similarDesignNos: [],
  hasDesignPhoto: false,
  tikliNeedle: 0,
  uploadFile: null,
  maxNeedles: 3,
  recipes: [],
  colourOptions: [],
  selectedRank: 0,
  pickedThread: "",
  pickedHex: "",
  resolveTimer: null,
};

const el = {
  swatches: document.getElementById("cloth-swatches"),
  clothPicked: document.getElementById("cloth-picked"),
  clothText: document.getElementById("cloth-text"),
  chosenStrip: document.getElementById("chosen-cloth-strip"),
  chosenLabel: document.getElementById("chosen-cloth-label"),
  shadePanel: document.getElementById("shade-panel"),
  shadeColourName: document.getElementById("shade-colour-name"),
  shadeBar: document.getElementById("shade-bar"),
  shadeMidLabel: document.getElementById("shade-mid-label"),
  clothVerify: document.getElementById("cloth-verify"),
  threads: document.getElementById("threads"),
  openGallery: document.getElementById("open-gallery"),
  galleryUpload: document.getElementById("gallery-upload"),
  galleryClear: document.getElementById("gallery-clear"),
  gallerySelected: document.getElementById("gallery-selected"),
  exactDesign: document.getElementById("exact-design"),
  exactTitle: document.getElementById("exact-title"),
  exactMeta: document.getElementById("exact-meta"),
  pastRecipes: document.getElementById("past-recipes"),
  similarRow: document.getElementById("similar-row"),
  similarList: document.getElementById("similar-list"),
  start: document.getElementById("start"),
  resetPicks: document.getElementById("reset-picks"),
  stepPanel: document.getElementById("step-panel"),
  stepTitle: document.getElementById("step-title"),
  stepMeta: document.getElementById("step-meta"),
  designHelp: document.getElementById("design-help"),
  tikliBanner: document.getElementById("tikli-banner"),
  finalTikli: document.getElementById("final-tikli"),
  recipeStrips: document.getElementById("recipe-strips"),
  colourOptions: document.getElementById("colour-options"),
  pickedThread: document.getElementById("picked-thread"),
  useStrip: document.getElementById("use-strip"),
  changeStrip: document.getElementById("change-strip"),
  finalPanel: document.getElementById("final-panel"),
  finalMap: document.getElementById("final-map"),
  again: document.getElementById("again"),
};

function t(key) {
  const pack = I18N[state.lang] || I18N.en;
  return pack[key] || I18N.en[key] || key;
}

function applyLang(lang) {
  state.lang = lang === "gu" ? "gu" : "en";
  try {
    localStorage.setItem(LANG_KEY, state.lang);
  } catch (err) {
    /* ignore */
  }
  document.documentElement.lang = state.lang === "gu" ? "gu" : "en";
  document.body.classList.toggle("lang-gu", state.lang === "gu");
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-lang") === state.lang);
  });
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    if (!key) return;
    node.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    const key = node.getAttribute("data-i18n-placeholder");
    if (key) node.setAttribute("placeholder", t(key));
  });
  if (el.shadeMidLabel) el.shadeMidLabel.textContent = shadeWord(state.shadeValue);
  if (state.clothLabel && el.chosenLabel) {
    el.chosenLabel.textContent = t("clothPalette") + " · " + clothDisplayName();
  }
}

function loadSavedLang() {
  let lang = "en";
  try {
    lang = localStorage.getItem(LANG_KEY) || "en";
  } catch (err) {
    lang = "en";
  }
  applyLang(lang);
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function shadeWord(v) {
  if (v <= 33) return t("lighter");
  if (v >= 67) return t("darker");
  return t("normal");
}

function updateShadeLabel() {
  if (el.shadeMidLabel) el.shadeMidLabel.textContent = shadeWord(state.shadeValue);
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

function mixRgb(a, b, tAmt) {
  return {
    r: Math.round(a.r + (b.r - a.r) * tAmt),
    g: Math.round(a.g + (b.g - a.g) * tAmt),
    b: Math.round(a.b + (b.b - a.b) * tAmt),
  };
}

function rgbCss(c) {
  return "rgb(" + c.r + "," + c.g + "," + c.b + ")";
}

function setShadeBarGradient(hex) {
  if (!el.shadeBar) return;
  const mid = parseHex(hex || "#128C7E");
  const light = mixRgb(mid, { r: 255, g: 252, b: 240 }, 0.78);
  const lightMid = mixRgb(mid, { r: 255, g: 252, b: 240 }, 0.38);
  const darkMid = mixRgb(mid, { r: 18, g: 12, b: 8 }, 0.32);
  const dark = mixRgb(mid, { r: 18, g: 12, b: 8 }, 0.62);
  el.shadeBar.style.background =
    "linear-gradient(90deg, " +
    rgbCss(light) +
    " 0%, " +
    rgbCss(lightMid) +
    " 25%, " +
    rgbCss(mid) +
    " 50%, " +
    rgbCss(darkMid) +
    " 75%, " +
    rgbCss(dark) +
    " 100%)";
  paintClothPalette(hex);
}

function paintClothPalette(hex) {
  if (!el.chosenStrip) return;
  const mid = parseHex(hex || state.clothHex || "#128C7E");
  const light = mixRgb(mid, { r: 255, g: 250, b: 240 }, 0.55);
  const dark = mixRgb(mid, { r: 20, g: 14, b: 10 }, 0.48);
  const chips = el.chosenStrip.querySelectorAll(".paint-cloth-chip");
  if (chips[0]) chips[0].style.background = rgbCss(light);
  if (chips[1]) chips[1].style.background = rgbCss(mid);
  if (chips[2]) chips[2].style.background = rgbCss(dark);
}

function clothDisplayName() {
  if (state.lang === "gu") {
    const btn = el.swatches.querySelector(".swatch.selected");
    const gu = btn && btn.getAttribute("data-gu");
    if (gu) return gu;
  }
  return state.clothLabel || state.cloth || "";
}

function showShadePanel(label, hex) {
  if (!el.shadePanel) return;
  el.shadePanel.hidden = false;
  state.clothHex = hex || state.clothHex;
  state.clothLabel = label || state.clothLabel;
  if (el.shadeColourName) el.shadeColourName.textContent = clothDisplayName() || label || "Colour";
  setShadeBarGradient(hex || "#888");
  updateShadeLabel();
  if (el.chosenStrip) {
    el.chosenStrip.hidden = false;
    if (el.chosenLabel) {
      el.chosenLabel.textContent = t("clothPalette") + " · " + (clothDisplayName() || label || "");
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

function markSwatchSelected(id, label, animate) {
  const buttons = el.swatches.querySelectorAll(".swatch");
  let hex = "#888888";
  let found = false;
  buttons.forEach((b) => {
    const match = (b.getAttribute("data-id") || "") === id;
    b.classList.toggle("selected", match);
    if (match) {
      found = true;
      hex = swatchHex(b);
      if (animate) {
        b.classList.add("pop");
        setTimeout(() => b.classList.remove("pop"), 280);
      }
    }
  });
  if (!found && label) {
    buttons.forEach((b) => {
      const match =
        (b.getAttribute("data-label") || "").toLowerCase() === String(label).toLowerCase();
      b.classList.toggle("selected", match);
      if (match) {
        found = true;
        hex = swatchHex(b);
      }
    });
  }
  el.swatches.classList.toggle("has-selection", Boolean(found || state.cloth));
  return hex;
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
  beige: "fawn",
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

function localResolveCloth(text, shadeValue) {
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
    const safe = cleaned.replace(/"/g, "");
    const btn = el.swatches.querySelector('.swatch[data-id="' + safe + '"]');
    if (btn) base = cleaned;
  }
  if (!base) {
    return {
      cloth_id: "",
      label: "",
      hex: "#ccc",
      shade: shadeValue <= 33 ? "light" : shadeValue >= 67 ? "dark" : "mid",
      message: 'Could not understand "' + raw + '"',
      understood_as: "",
    };
  }
  let clothId = base;
  let shade = "mid";
  if (shadeValue <= 33) shade = "light";
  else if (shadeValue >= 67) shade = "dark";
  const lightMap = {
    green: "light green",
    pink: "pink",
    blue: "sky blue",
    peach: "peach",
    yellow: "lemon",
    red: "tomato",
  };
  const darkMap = {
    green: "mehndi",
    pink: "rani",
    blue: "navy blue",
    peach: "orange",
    yellow: "mustard",
    red: "maroon",
  };
  if (shade === "light" && lightMap[base]) clothId = lightMap[base];
  if (shade === "dark" && darkMap[base]) clothId = darkMap[base];
  const btn =
    el.swatches.querySelector('.swatch[data-id="' + clothId + '"]') ||
    el.swatches.querySelector('.swatch[data-id="' + base + '"]');
  const label =
    (btn && btn.getAttribute("data-label")) ||
    base.replace(/\b\w/g, (c) => c.toUpperCase());
  const hex = btn ? swatchHex(btn) : "#888";
  const shadeBit = shade === "light" ? " · " + t("lighter") : shade === "dark" ? " · " + t("darker") : "";
  const message =
    cleaned !== base && cleaned !== clothId
      ? t("using") + " " + label + shadeBit
      : t("using") + " " + label + shadeBit;
  return {
    cloth_id: clothId,
    label,
    hex,
    shade,
    message,
    understood_as: label,
  };
}

function applyResolvedCloth(data) {
  if (!data || !data.cloth_id) return;
  state.cloth = data.cloth_id;
  const shadeBit =
    data.shade === "light" ? " · " + t("lighter") : data.shade === "dark" ? " · " + t("darker") : "";
  if (el.clothVerify) {
    el.clothVerify.textContent = data.message || t("using") + " " + data.understood_as;
    el.clothVerify.className = "cloth-verify ok";
  }
  el.clothPicked.textContent =
    t("selected") + ": " + (data.understood_as || data.label || data.cloth_id) + shadeBit;
  el.clothPicked.style.color = "#075E54";
  const hex = markSwatchSelected(data.cloth_id, data.label, false);
  showShadePanel(data.understood_as || data.label, data.hex || hex);
}

async function resolveClothNow() {
  const text = (el.clothText.value || "").trim() || state.clothRaw || state.cloth;
  if (!text) {
    if (el.clothVerify) {
      el.clothVerify.textContent = t("slideShade");
      el.clothVerify.className = "cloth-verify";
    }
    return null;
  }

  const local = localResolveCloth(text, state.shadeValue);
  if (local.cloth_id) {
    state.clothRaw = text;
    applyResolvedCloth(local);
  }

  try {
    const res = await fetch("/api/resolve-cloth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, shade_value: state.shadeValue }),
    });
    if (!res.ok) {
      if (!local.cloth_id && el.clothVerify) {
        el.clothVerify.textContent = t("pleaseCloth");
        el.clothVerify.className = "cloth-verify bad";
      }
      return local.cloth_id ? local : null;
    }
    const data = await res.json();
    if (!data.cloth_id) {
      if (local.cloth_id) return local;
      el.clothVerify.textContent = data.message || t("pleaseCloth");
      el.clothVerify.className = "cloth-verify bad";
      return data;
    }
    state.clothRaw = text;
    applyResolvedCloth(data);
    return data;
  } catch (err) {
    if (local.cloth_id) return local;
    if (el.clothVerify) {
      el.clothVerify.textContent = t("pleaseCloth");
      el.clothVerify.className = "cloth-verify bad";
    }
    return null;
  }
}

function bindSwatches() {
  const buttons = el.swatches.querySelectorAll(".swatch");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-id") || "";
      const label = btn.getAttribute("data-label") || id;
      const hex = swatchHex(btn);
      el.clothText.value = "";
      state.shadeValue = 50;
      el.shadeBar.value = "50";
      updateShadeLabel();
      state.cloth = id;
      state.clothRaw = id;
      markSwatchSelected(id, label, true);
      el.clothPicked.textContent = t("selected") + ": " + (state.lang === "gu" ? (btn.getAttribute("data-gu") || label) : label);
      el.clothPicked.style.color = "#075E54";
      showShadePanel(label, hex);
      el.clothVerify.textContent = t("nowSlide") + " " + (state.lang === "gu" ? (btn.getAttribute("data-gu") || label) : label);
      el.clothVerify.className = "cloth-verify ok";
      resolveClothNow();
      el.shadePanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });
}

function clearGallery() {
  state.similarDesignNos = [];
  state.exactDesignNo = "";
  state.hasDesignPhoto = false;
  state.uploadFile = null;
  el.galleryUpload.value = "";
  el.galleryClear.hidden = true;
  el.gallerySelected.hidden = true;
  el.gallerySelected.innerHTML = "";
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
    if (matched.length) {
      state.similarDesignNos = matched;
    }
    showSimilar(data.similar || [], Boolean(data.exact_design));
    if (!state.similarDesignNos.length && state.exactDesignNo) {
      state.similarDesignNos = [state.exactDesignNo];
    }
  } catch (err) {
    console.error(err);
  }
}

function paintChipHtml(chip) {
  const hex = chip.thread_hex || "";
  const fillClass = hex ? "paint-fill" : "paint-fill unknown";
  const fillStyle = hex ? ` style="background:${escapeHtml(hex)}"` : "";
  const tikli = chip.is_tikli ? `<em class="chip-tikli">${escapeHtml(t("tikliHere"))}</em>` : "";
  return `
    <div class="paint-chip${chip.is_tikli ? " is-tikli" : ""}${chip.thread && chip.thread === state.pickedThread ? " selected" : ""}" data-thread="${escapeHtml(chip.thread || "")}" data-hex="${escapeHtml(hex)}">
      <span class="${fillClass}"${fillStyle}></span>
      <span class="paint-meta">
        <strong>${escapeHtml(t("needle"))}${chip.needle}</strong>
        <span>${escapeHtml(chip.thread || "")}</span>
        ${tikli}
      </span>
    </div>`;
}

function stripHtml(chips, extraClass) {
  const list = (chips || []).filter((c) => (c.thread || "").trim());
  if (!list.length) return `<p class="meta">${escapeHtml(t("noNeedles"))}</p>`;
  return `<div class="paint-strip ${extraClass || ""}">${list.map(paintChipHtml).join("")}</div>`;
}

function showExactDesign(exact) {
  if (!el.exactDesign) return;
  if (!exact || !exact.design_no) {
    clearExactDesign();
    return;
  }
  state.exactDesignNo = String(exact.design_no);
  state.similarDesignNos = [
    state.exactDesignNo,
    ...state.similarDesignNos.filter((d) => d !== state.exactDesignNo),
  ];
  el.exactDesign.hidden = false;
  el.exactTitle.textContent = exact.message || "Exact same design found: #" + exact.design_no;
  const cloths = (exact.cloths_used || []).join(", ");
  el.exactMeta.textContent = cloths
    ? "Past cloths for this design: " + cloths
    : exact.past_count
      ? exact.past_count + " past recipes"
      : "Matched in gallery — no colour-book rows yet for this number";

  const rows = exact.past_recipes || [];
  if (!rows.length) {
    el.pastRecipes.innerHTML = '<p class="meta">' + escapeHtml(t("pastNone")) + "</p>";
    return;
  }
  el.pastRecipes.innerHTML = rows
    .map((r) => {
      const chips = r.chips && r.chips.length
        ? r.chips
        : [r.n1, r.n2, r.n3, r.n4, r.n5]
            .map((n, i) => ({ needle: i + 1, thread: n || "", thread_hex: "", is_tikli: r.tikli_needle === i + 1 }))
            .filter((c) => c.thread);
      return `
        <div class="past-card">
          <div class="past-top">
            <strong>${escapeHtml(r.cloth || "—")}</strong>
          </div>
          ${stripHtml(chips, "compact")}
        </div>`;
    })
    .join("");
}

function showSimilar(rows, hasExact) {
  const nos = [...new Set(rows.map((r) => r.design_no).filter(Boolean))];
  if (nos.length) {
    if (state.exactDesignNo) {
      state.similarDesignNos = [state.exactDesignNo, ...nos.filter((d) => d !== state.exactDesignNo)];
    } else {
      state.similarDesignNos = nos;
    }
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
  if (label) {
    label.textContent = hasExact ? t("alsoSimilar") : t("similarPast");
  }
  el.similarList.innerHTML = rows
    .map((r) => {
      const exactBadge = r.exact ? ' <span class="exact-badge">exact</span>' : "";
      return `
      <div class="similar-chip${r.exact ? " is-exact" : ""}">
        ${r.thumb_url ? `<img src="${escapeHtml(r.thumb_url)}" alt="" loading="lazy" />` : ""}
        <span>${escapeHtml(r.design_no)}${exactBadge}</span>
      </div>`;
    })
    .join("");
}

function resetStripFlow() {
  state.recipes = [];
  state.colourOptions = [];
  state.selectedRank = 0;
  el.finalPanel.hidden = true;
  el.stepPanel.hidden = true;
  el.resetPicks.hidden = true;
  el.recipeStrips.innerHTML = "";
  el.colourOptions.innerHTML = "";
  el.pickedThread.hidden = true;
  el.pickedThread.innerHTML = "";
  el.useStrip.hidden = true;
  if (el.designHelp) {
    el.designHelp.hidden = true;
    el.designHelp.textContent = "";
  }
}

async function ensureCloth() {
  if (el.clothText.value.trim() || state.cloth) {
    const data = await resolveClothNow();
    if (data && data.cloth_id) return true;
    if (state.cloth) return true;
  }
  el.clothPicked.textContent = t("pleaseCloth");
  el.clothPicked.style.color = "#c0392b";
  el.swatches.scrollIntoView({ behavior: "smooth", block: "center" });
  return false;
}

async function loadRecipes() {
  const ok = await ensureCloth();
  if (!ok) return;

  state.maxNeedles = Number(el.threads.value || 3);
  el.stepPanel.hidden = false;
  el.finalPanel.hidden = true;
  el.resetPicks.hidden = false;
  el.useStrip.hidden = !state.selectedRank;
  el.recipeStrips.innerHTML = '<p class="meta">' + escapeHtml(t("loading")) + "</p>";

  if (state.uploadFile) {
    await fetchSimilarUpload(state.uploadFile);
  }

  const body = {
    cloth: state.cloth,
    cloth_raw: (el.clothText.value || "").trim() || state.clothRaw || state.cloth,
    shade_value: state.shadeValue,
    design_no: state.exactDesignNo || "",
    thread_count: state.maxNeedles,
    similar_design_nos: state.similarDesignNos,
    has_design_photo: Boolean(state.hasDesignPhoto || state.uploadFile),
  };

  try {
    const res = await fetch("/api/recommend-recipes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("fail");
    const data = await res.json();
    if (data.cloth && data.cloth.message && el.clothVerify) {
      el.clothVerify.textContent = data.cloth.message;
      el.clothVerify.className = "cloth-verify ok";
    }
    if (data.cloth && data.cloth.cloth_id) {
      state.cloth = data.cloth.cloth_id;
    }
    showDesignHelp(data.design_help_percent, data.design_help_note, data);
    showTikli(data.tikli || null);
    state.recipes = data.recipes || [];
    state.colourOptions = data.colour_options || [];
    if (!state.selectedRank && state.recipes.length) state.selectedRank = 1;
    renderRecipeStrips();
    renderColourOptions();
    el.stepPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    el.recipeStrips.innerHTML = '<p class="meta">' + escapeHtml(t("serverDown")) + "</p>";
  }
}

function showTikli(info) {
  state.tikliNeedle = info && info.tikli_needle ? Number(info.tikli_needle) : 0;
  if (el.tikliBanner) {
    if (info && info.has_tikli && info.tikli_needle) {
      el.tikliBanner.hidden = false;
      el.tikliBanner.innerHTML =
        escapeHtml(t("tikliHere")) +
        " · <strong>" +
        escapeHtml(t("needle")) +
        info.tikli_needle +
        "</strong>";
    } else {
      el.tikliBanner.hidden = true;
      el.tikliBanner.textContent = "";
    }
  }
  if (el.finalTikli) {
    if (info && info.has_tikli && info.tikli_needle) {
      el.finalTikli.hidden = false;
      el.finalTikli.innerHTML =
        escapeHtml(t("tikliHere")) +
        " · <strong>" +
        escapeHtml(t("needle")) +
        info.tikli_needle +
        "</strong>";
    } else {
      el.finalTikli.hidden = true;
      el.finalTikli.textContent = "";
    }
  }
}

function showDesignHelp(pct, note, meta) {
  if (!el.designHelp) return;
  const n = Math.max(0, Math.min(100, Number(pct) || 0));
  const matched = (meta && meta.similar_used) || [];
  const designNo = (meta && meta.design_no_used) || "";
  el.designHelp.hidden = false;
  el.designHelp.className = "design-help" + (n > 0 ? " has-help" : "");
  let title = "Design +" + n + "%";
  let detail = note || "";
  if (designNo) detail += " · #" + designNo;
  else if (matched.length) detail += " · #" + matched.slice(0, 3).join(", #");
  el.designHelp.innerHTML =
    "<div class='design-help-top'><strong>" +
    escapeHtml(title) +
    "</strong></div>" +
    "<div class='design-help-bar'><span style='width:" +
    n +
    "%'></span></div>" +
    "<p class='design-help-note'>" +
    escapeHtml(detail) +
    "</p>";
}

function selectedRecipe() {
  return state.recipes.find((r) => r.rank === state.selectedRank) || state.recipes[0] || null;
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
      state.pickedHex = rec0.chips[0].thread_hex || "";
    }
  }
  el.recipeStrips.innerHTML = state.recipes
    .map((rec) => {
      const on = rec.rank === state.selectedRank ? " selected" : "";
      const best = rec.rank === 1 ? " best" : "";
      const chips = rec.chips || [];
      const mark = rec.rank === state.selectedRank ? " ✓" : "";
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
      state.selectedRank = Number(btn.getAttribute("data-rank") || 1);
      state.pickedThread = "";
      state.pickedHex = "";
      renderRecipeStrips();
      el.useStrip.hidden = false;
    });
  });
  el.recipeStrips.querySelectorAll(".paint-chip").forEach((chip) => {
    chip.addEventListener("click", (ev) => {
      ev.stopPropagation();
      const thread = chip.getAttribute("data-thread") || "";
      const hex = chip.getAttribute("data-hex") || "";
      state.pickedThread = thread;
      state.pickedHex = hex;
      const parent = chip.closest(".recipe-strip-card");
      if (parent) {
        state.selectedRank = Number(parent.getAttribute("data-rank") || state.selectedRank);
      }
      renderRecipeStrips();
      el.useStrip.hidden = false;
    });
  });
  el.useStrip.hidden = !state.selectedRank;
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
      const hex = opt.thread_hex || "";
      const fill = hex
        ? `style="background:${escapeHtml(hex)}"`
        : "";
      const unk = hex ? "" : " unknown";
      const on = (opt.thread || "") === state.pickedThread ? " selected" : "";
      return `
        <button type="button" class="paint-chip colour-opt${on}" data-thread="${escapeHtml(opt.thread || "")}" data-hex="${escapeHtml(hex)}">
          <span class="paint-fill${unk}" ${fill}></span>
          <span class="paint-meta">
            <strong>${opt.rank}</strong>
            <span>${escapeHtml(opt.thread || "")}</span>
          </span>
        </button>`;
    })
    .join("");
  el.colourOptions.querySelectorAll(".colour-opt").forEach((btn) => {
    btn.addEventListener("click", () => {
      el.colourOptions.querySelectorAll(".colour-opt").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      showPickedThread(btn.getAttribute("data-thread") || "", btn.getAttribute("data-hex") || "");
      renderRecipeStrips();
    });
  });
}

function showPickedThread(thread, hex) {
  if (!el.pickedThread || !thread) return;
  state.pickedThread = thread;
  state.pickedHex = hex || "";
  el.pickedThread.hidden = false;
  const fill = hex
    ? `style="background:${escapeHtml(hex)}"`
    : "";
  const unk = hex ? "" : " unknown";
  el.pickedThread.innerHTML = `
    <div class="picked-thread-chip">
      <span class="paint-fill big${unk}" ${fill}></span>
      <div>
        <p class="picked-kicker">${escapeHtml(t("colourPicked"))}</p>
        <p class="picked-name">${escapeHtml(thread)}</p>
      </div>
    </div>`;
}

function showSelectedThreadPreview() {
  if (state.pickedThread) {
    showPickedThread(state.pickedThread, state.pickedHex);
    return;
  }
  const rec = selectedRecipe();
  if (!rec || !rec.chips || !rec.chips.length) return;
  const first = rec.chips[0];
  showPickedThread(first.thread, first.thread_hex || "");
}

function showFinal() {
  const rec = selectedRecipe();
  if (!rec) return;
  el.stepPanel.hidden = true;
  el.finalPanel.hidden = false;
  const chips = rec.chips || [];
  el.finalMap.innerHTML = `
    <div class="final-strip-wrap">
      <p class="strip-num">${escapeHtml(t("recipe"))} ${rec.rank}${rec.rank === 1 ? " · " + t("best") : ""}</p>
      ${stripHtml(chips, "final")}
    </div>
    <div class="final-rows">
      ${chips
        .map(
          (c) => `
        <div class="final-row">
          <span class="nlabel">${escapeHtml(t("needle"))}${c.needle}${c.is_tikli ? " · " + t("tikliHere") : ""}</span>
          <span class="nval-wrap">
            <span class="thread-dot" style="${c.thread_hex ? "background:" + escapeHtml(c.thread_hex) : ""}"></span>
            <span class="nval">${escapeHtml(c.thread)}${c.is_tikli ? " · " + t("tikliHere") : ""}</span>
          </span>
        </div>`
        )
        .join("")}
    </div>`;
}

loadSavedLang();
bindSwatches();
updateShadeLabel();

document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => applyLang(btn.getAttribute("data-lang") || "en"));
});

el.clothText.addEventListener("input", () => {
  clearTimeout(state.resolveTimer);
  state.resolveTimer = setTimeout(() => {
    state.shadeValue = Number(el.shadeBar.value || 50);
    resolveClothNow();
  }, 350);
});
el.clothText.addEventListener("change", resolveClothNow);
el.clothText.addEventListener("blur", resolveClothNow);

el.shadeBar.addEventListener("input", () => {
  state.shadeValue = Number(el.shadeBar.value || 50);
  updateShadeLabel();
  clearTimeout(state.resolveTimer);
  state.resolveTimer = setTimeout(resolveClothNow, 150);
});

el.openGallery.addEventListener("click", () => {
  el.galleryUpload.click();
});

el.galleryUpload.addEventListener("change", async () => {
  const file = el.galleryUpload.files && el.galleryUpload.files[0];
  if (!file) return;
  state.uploadFile = file;
  state.hasDesignPhoto = true;
  el.galleryClear.hidden = false;
  el.gallerySelected.hidden = false;
  el.gallerySelected.innerHTML = `
    <img src="${URL.createObjectURL(file)}" alt="" />
    <div><strong>${escapeHtml(t("photoSelected"))}</strong><p>${escapeHtml(file.name)}</p></div>
  `;
  await fetchSimilarUpload(file);
});

el.galleryClear.addEventListener("click", clearGallery);

el.start.addEventListener("click", () => {
  state.selectedRank = 0;
  loadRecipes();
});

el.resetPicks.addEventListener("click", resetStripFlow);

el.useStrip.addEventListener("click", showFinal);

el.changeStrip.addEventListener("click", () => {
  el.finalPanel.hidden = true;
  el.stepPanel.hidden = false;
  el.stepPanel.scrollIntoView({ behavior: "smooth", block: "start" });
});

el.again.addEventListener("click", () => {
  resetStripFlow();
  window.scrollTo({ top: 0, behavior: "smooth" });
});
