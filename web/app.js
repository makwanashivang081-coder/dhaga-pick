const state = {
  cloth: "",
  clothRaw: "",
  shadeValue: 50,
  exactDesignNo: "",
  similarDesignNos: [],
  hasDesignPhoto: false,
  tikliNeedle: 0,
  uploadFile: null,
  maxNeedles: 3,
  currentNeedle: 1,
  locked: {},
  resolveTimer: null,
};

const el = {
  swatches: document.getElementById("cloth-swatches"),
  clothPicked: document.getElementById("cloth-picked"),
  clothText: document.getElementById("cloth-text"),
  shadePanel: document.getElementById("shade-panel"),
  shadeColourName: document.getElementById("shade-colour-name"),
  shadeBar: document.getElementById("shade-bar"),
  shadeMidLabel: document.getElementById("shade-mid-label"),
  clothVerify: document.getElementById("cloth-verify"),
  parts: document.getElementById("parts"),
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
  lockedSummary: document.getElementById("locked-summary"),
  needleOptions: document.getElementById("needle-options"),
  backNeedle: document.getElementById("back-needle"),
  finalPanel: document.getElementById("final-panel"),
  finalMap: document.getElementById("final-map"),
  again: document.getElementById("again"),
};

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function shadeWord(v) {
  if (v <= 33) return "Lighter";
  if (v >= 67) return "Darker";
  return "Normal";
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

function mixRgb(a, b, t) {
  return {
    r: Math.round(a.r + (b.r - a.r) * t),
    g: Math.round(a.g + (b.g - a.g) * t),
    b: Math.round(a.b + (b.b - a.b) * t),
  };
}

function rgbCss(c) {
  return "rgb(" + c.r + "," + c.g + "," + c.b + ")";
}

function setShadeBarGradient(hex) {
  if (!el.shadeBar) return;
  const mid = parseHex(hex || "#2f9e44");
  const light = mixRgb(mid, { r: 255, g: 252, b: 240 }, 0.72);
  const dark = mixRgb(mid, { r: 20, g: 16, b: 12 }, 0.55);
  el.shadeBar.style.background =
    "linear-gradient(90deg, " + rgbCss(light) + " 0%, " + rgbCss(mid) + " 50%, " + rgbCss(dark) + " 100%)";
}

function showShadePanel(label, hex) {
  if (!el.shadePanel) return;
  el.shadePanel.hidden = false;
  if (el.shadeColourName) el.shadeColourName.textContent = label || state.cloth || "Colour";
  setShadeBarGradient(hex || "#888");
  updateShadeLabel();
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

// Local fallback so colour pick never dies if API is old / offline
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
  const shadeBit = shade === "light" ? " · lighter" : shade === "dark" ? " · darker" : "";
  const message =
    cleaned !== base && cleaned !== clothId
      ? 'You wrote "' + raw + '" -> we take it as ' + label + shadeBit
      : "Using " + label + shadeBit;
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
    data.shade === "light" ? " · lighter" : data.shade === "dark" ? " · darker" : "";
  if (el.clothVerify) {
    el.clothVerify.textContent = data.message || "Using " + data.understood_as;
    el.clothVerify.className = "cloth-verify ok";
  }
  el.clothPicked.textContent =
    "Selected: " + (data.understood_as || data.label || data.cloth_id) + shadeBit;
  el.clothPicked.style.color = "#0b5f53";
  markSwatchSelected(data.cloth_id, data.label, false);
  showShadePanel(data.understood_as || data.label, data.hex);
}

async function resolveClothNow() {
  const text = (el.clothText.value || "").trim() || state.clothRaw || state.cloth;
  if (!text) {
    if (el.clothVerify) {
      el.clothVerify.textContent = "Tap a colour, then set lighter / darker";
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
        el.clothVerify.textContent =
          "Could not understand that colour — try a chip or type peach / gulabi / lilo";
        el.clothVerify.className = "cloth-verify bad";
      }
      return local.cloth_id ? local : null;
    }
    const data = await res.json();
    if (!data.cloth_id) {
      if (local.cloth_id) return local;
      el.clothVerify.textContent = data.message || "Could not understand colour";
      el.clothVerify.className = "cloth-verify bad";
      return data;
    }
    state.clothRaw = text;
    applyResolvedCloth(data);
    return data;
  } catch (err) {
    if (local.cloth_id) return local;
    if (el.clothVerify) {
      el.clothVerify.textContent = "Could not understand that colour — try tapping a colour chip";
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
      el.clothPicked.textContent = "Selected: " + label;
      el.clothPicked.style.color = "#0b5f53";
      showShadePanel(label, hex);
      el.clothVerify.textContent = "Now slide for lighter or darker " + label;
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
    el.pastRecipes.innerHTML =
      '<p class="meta">No needle history in the colour book for this design yet.</p>';
    return;
  }
  el.pastRecipes.innerHTML = rows
    .map((r) => {
      const slots = [
        [1, r.n1],
        [2, r.n2],
        [3, r.n3],
        [4, r.n4],
        [5, r.n5],
      ].filter(([, n]) => (n || "").trim());
      const needleHtml = slots
        .map(([i, n]) => {
          // colour filled client-side roughly via data attribute after paint; keep text for now
          return `<span class="past-n" data-thread="${escapeHtml(n)}"><em>N${i}</em> ${escapeHtml(n)}</span>`;
        })
        .join("");
      return `
        <div class="past-card">
          <div class="past-top">
            <strong>${escapeHtml(r.cloth || "—")}</strong>
            <span>${escapeHtml(r.parts || "")}</span>
          </div>
          <div class="past-needles">${needleHtml || "<span class='meta'>No needles</span>"}</div>
          ${r.tikli_needle ? '<div class="past-tikli">Tikli on Needle ' + escapeHtml(String(r.tikli_needle)) + "</div>" : r.tikli ? '<div class="past-tikli">Tikli</div>' : ""}
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
  // if still empty, keep whatever matched_design_nos already set
  if (!rows.length) {
    el.similarRow.hidden = true;
    el.similarList.innerHTML = "";
    return;
  }
  el.similarRow.hidden = false;
  const label = el.similarRow.querySelector(".similar-label");
  if (label) {
    label.textContent = hasExact ? "Also similar designs" : "Similar past designs";
  }
  el.similarList.innerHTML = rows
    .map((r) => {
      const exactBadge = r.exact ? ' <span class="exact-badge">exact</span>' : "";
      return `
      <div class="similar-chip${r.exact ? " is-exact" : ""}">
        ${r.thumb_url ? `<img src="${escapeHtml(r.thumb_url)}" alt="" loading="lazy" />` : ""}
        <span>${escapeHtml(r.design_no)} · ${escapeHtml(r.part || "")}${exactBadge}</span>
      </div>`;
    })
    .join("");
}

function resetNeedleFlow() {
  state.locked = {};
  state.currentNeedle = 1;
  el.finalPanel.hidden = true;
  el.stepPanel.hidden = true;
  el.resetPicks.hidden = true;
  el.needleOptions.innerHTML = "";
  el.lockedSummary.innerHTML = "";
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
  el.clothPicked.textContent = "Please tap a cloth colour or type one";
  el.clothPicked.style.color = "#c0392b";
  el.swatches.scrollIntoView({ behavior: "smooth", block: "center" });
  return false;
}

async function loadNeedleOptions() {
  const ok = await ensureCloth();
  if (!ok) return;

  state.maxNeedles = Number(el.threads.value || 3);
  el.stepPanel.hidden = false;
  el.finalPanel.hidden = true;
  el.resetPicks.hidden = false;
  el.stepTitle.textContent = "Needle " + state.currentNeedle + " · pick 1 of 10";
  el.stepMeta.textContent = "Choose dhaga for needle " + state.currentNeedle;
  el.backNeedle.hidden = state.currentNeedle <= 1;
  renderLockedSummary();

  if (state.uploadFile) {
    await fetchSimilarUpload(state.uploadFile);
  }

  const body = {
    cloth: state.cloth,
    cloth_raw: (el.clothText.value || "").trim() || state.clothRaw || state.cloth,
    shade_value: state.shadeValue,
    design_no: state.exactDesignNo || "",
    parts: el.parts.value.trim(),
    gallery_path: "",
    similar_design_nos: state.similarDesignNos,
    has_design_photo: Boolean(state.hasDesignPhoto || state.uploadFile),
    locked_needles: Object.fromEntries(Object.entries(state.locked).map(([k, v]) => [String(k), v])),
    target_needle: state.currentNeedle,
  };

  el.needleOptions.innerHTML = '<p class="meta">Loading options…</p>';
  try {
    const res = await fetch("/api/recommend-needle", {
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
    if (data.similar_designs && data.similar_designs.length) showSimilar(data.similar_designs);
    renderNeedleOptions(data.options || []);
  } catch (err) {
    el.needleOptions.innerHTML = '<p class="meta">Could not load options. Is the server running?</p>';
  }
}

function showTikli(info) {
  state.tikliNeedle = info && info.tikli_needle ? Number(info.tikli_needle) : 0;
  if (el.tikliBanner) {
    if (info && info.has_tikli && info.tikli_needle) {
      el.tikliBanner.hidden = false;
      el.tikliBanner.innerHTML =
        "Tikli runs on <strong>Needle " +
        info.tikli_needle +
        "</strong> <em>· from past recipes</em>";
    } else {
      el.tikliBanner.hidden = true;
      el.tikliBanner.textContent = "";
    }
  }
  if (el.finalTikli) {
    if (info && info.has_tikli && info.tikli_needle) {
      el.finalTikli.hidden = false;
      el.finalTikli.innerHTML =
        "Tikli runs on <strong>Needle " + info.tikli_needle + "</strong>";
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
  let title;
  let detail;
  if (n > 0) {
    title = "Design accuracy boost: +" + n + "%";
    detail =
      note ||
      ("Uploaded design improved colour choosing by about " + n + "% vs cloth colour alone");
    if (designNo) detail += " · matched #" + designNo;
    else if (matched.length) detail += " · close to #" + matched.slice(0, 3).join(", #");
  } else if (state.hasDesignPhoto || state.uploadFile) {
    title = "Design accuracy boost: +0%";
    detail =
      note ||
      "Design photo uploaded, but no close past design match — using cloth colour only";
  } else {
    title = "Design accuracy boost: +0%";
    detail = "No design photo — suggestions from cloth colour only";
  }
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

function renderLockedSummary() {
  const keys = Object.keys(state.locked).map(Number).sort((a, b) => a - b);
  if (!keys.length) {
    el.lockedSummary.innerHTML = "";
    return;
  }
  el.lockedSummary.innerHTML = keys
    .map((n) => '<span class="lock-pill">N' + n + ": " + escapeHtml(state.locked[n]) + "</span>")
    .join("");
}

function renderNeedleOptions(options) {
  if (!options.length) {
    el.needleOptions.innerHTML = '<p class="meta">No options found. Try another cloth.</p>';
    return;
  }
  el.needleOptions.innerHTML = options
    .map((opt, idx) => {
      const best = opt.rank === 1 ? "best" : "";
      const hex = opt.thread_hex || "#c4b8a5";
      const tikliClass = opt.is_tikli_needle ? " has-tikli" : "";
      const tikliPill = opt.is_tikli_needle
        ? '<span class="tikli-pill">Tikli here</span>'
        : opt.tikli_needle
          ? '<span class="tikli-pill">Tikli N' + opt.tikli_needle + '</span>'
          : "";
      return `
        <button type="button" class="dhaga-card ${best}${tikliClass}" data-thread="${escapeHtml(opt.thread)}" style="animation-delay:${idx * 0.03}s">
          <div class="dhaga-top">
            <strong>#${opt.rank}${opt.rank === 1 ? " · Best" : ""}${tikliPill}</strong>
            <span class="badge">${escapeHtml(opt.match_reason || "")}</span>
          </div>
          <div class="dhaga-thread-row">
            <span class="thread-dot" style="background:${escapeHtml(hex)}" title="Approx thread colour"></span>
            <div class="dhaga-thread">${escapeHtml(opt.thread)}</div>
          </div>
        </button>`;
    })
    .join("");

  el.needleOptions.querySelectorAll(".dhaga-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      const thread = btn.getAttribute("data-thread") || "";
      if (!thread) return;
      btn.classList.add("pop");
      chooseThread(thread);
    });
  });
}

function chooseThread(thread) {
  state.locked[state.currentNeedle] = thread;
  if (state.currentNeedle >= state.maxNeedles) {
    showFinal();
    return;
  }
  state.currentNeedle += 1;
  loadNeedleOptions();
}

function showFinal() {
  el.stepPanel.hidden = true;
  el.finalPanel.hidden = false;
  const keys = Object.keys(state.locked).map(Number).sort((a, b) => a - b);
  el.finalMap.innerHTML = keys
    .map(
      (n) => `
      <div class="final-row">
        <span class="nlabel">Needle ${n}${state.tikliNeedle === n ? " · Tikli" : ""}</span>
        <span class="nval">${escapeHtml(state.locked[n])}${state.tikliNeedle === n ? " · Tikli" : ""}</span>
      </div>`
    )
    .join("");
}

bindSwatches();
updateShadeLabel();

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
    <div><strong>Design photo selected</strong><p>${escapeHtml(file.name)}</p></div>
  `;
  await fetchSimilarUpload(file);
});

el.galleryClear.addEventListener("click", clearGallery);

el.start.addEventListener("click", () => {
  state.locked = {};
  state.currentNeedle = 1;
  loadNeedleOptions();
});

el.resetPicks.addEventListener("click", resetNeedleFlow);

el.backNeedle.addEventListener("click", () => {
  if (state.currentNeedle <= 1) return;
  delete state.locked[state.currentNeedle - 1];
  state.currentNeedle -= 1;
  loadNeedleOptions();
});

el.again.addEventListener("click", () => {
  resetNeedleFlow();
  window.scrollTo({ top: 0, behavior: "smooth" });
});
