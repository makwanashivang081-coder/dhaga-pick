"""Cloth colour vocabulary: English + Gujarati + factory typos → palette ids."""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher, get_close_matches
from typing import Optional

# Canonical palette used in UI + recommender (base mid shade)
CANONICAL: dict[str, dict[str, str]] = {
    "green": {"label": "Green", "hex": "#2f9e44", "gu": "લીલો"},
    "light green": {"label": "Light green", "hex": "#8ce99a", "gu": "આછો લીલો"},
    "pink": {"label": "Pink", "hex": "#f783ac", "gu": "ગુલાબી"},
    "blue": {"label": "Blue", "hex": "#4c6ef5", "gu": "વાદળી"},
    "sky blue": {"label": "Sky blue", "hex": "#74c0fc", "gu": "આકાશી"},
    "navy blue": {"label": "Navy blue", "hex": "#1c3d7a", "gu": "ઘેરો વાદળી"},
    "yellow": {"label": "Yellow", "hex": "#f4d03f", "gu": "પીળો"},
    "lemon": {"label": "Lemon", "hex": "#ffe066", "gu": "લીંબુ"},
    "purple": {"label": "Purple", "hex": "#9b59b6", "gu": "જાંબલી"},
    "violet": {"label": "Violet", "hex": "#7950f2", "gu": "વાયોલેટ"},
    "firozi": {"label": "Firozi", "hex": "#22b8cf", "gu": "ફિરોઝી"},
    "orange": {"label": "Orange", "hex": "#ff922b", "gu": "નારંગી"},
    "peach": {"label": "Peach", "hex": "#ffc9a8", "gu": "પીચ"},
    "grey": {"label": "Grey", "hex": "#868e96", "gu": "રાખોડી"},
    "red": {"label": "Red", "hex": "#e03131", "gu": "લાલ"},
    "rama": {"label": "Rama", "hex": "#0b7285", "gu": "રામા"},
    "black": {"label": "Black", "hex": "#212529", "gu": "કાળો"},
    "cream": {"label": "Cream", "hex": "#fff3bf", "gu": "ક્રીમ"},
    "brown": {"label": "Brown", "hex": "#8d6e63", "gu": "ભૂરો"},
    "rust": {"label": "Rust", "hex": "#c0392b", "gu": "રસ્ટ"},
    "maroon": {"label": "Maroon", "hex": "#7b1e3a", "gu": "મેરૂન"},
    "wine": {"label": "Wine", "hex": "#5c0a1f", "gu": "વાઇન"},
    "fawn": {"label": "Badami", "hex": "#d4a574", "gu": "બદામી"},
    "gold": {"label": "Gold", "hex": "#e6b422", "gu": "સોનેરી"},
    "mustard": {"label": "Mustard", "hex": "#e1a100", "gu": "રાઈ / મસ્ટર્ડ"},
    "chiku": {"label": "Chiku", "hex": "#c4a484", "gu": "ચીકૂ"},
    "white": {"label": "White", "hex": "#f8f9fa", "gu": "સફેદ"},
    "gajri": {"label": "Gajri", "hex": "#e8590c", "gu": "ગાજરી"},
    "pista": {"label": "Pista", "hex": "#a3d977", "gu": "પિસ્તા"},
    "rani": {"label": "Rani", "hex": "#d6336c", "gu": "રાણી"},
    "mehndi": {"label": "Mehndi", "hex": "#5c7a1a", "gu": "મેંદી"},
    "khaki": {"label": "Khaki", "hex": "#b5a642", "gu": "ખાકી"},
    "tomato": {"label": "Tomato", "hex": "#fa5252", "gu": "ટમેટો"},
    "offwhite": {"label": "Off white", "hex": "#f5f0e6", "gu": "ઑફ વ્હાઇટ"},
    "burgundy": {"label": "Burgundy", "hex": "#6b1c2a", "gu": "બર્ગન્ડી"},
}

# light / mid / dark ids that exist (or map) in recipe history
SHADE_FAMILY: dict[str, dict[str, list[str]]] = {
    "green": {
        "light": ["light green", "l.green", "l green", "pista"],
        "mid": ["green"],
        "dark": ["d.green", "d green", "mehndi", "mendi"],
    },
    "light green": {
        "light": ["light green", "l.green", "pista"],
        "mid": ["light green", "green"],
        "dark": ["green", "d.green"],
    },
    "pink": {
        "light": ["l.pink", "l pink", "l. pink"],
        "mid": ["pink"],
        "dark": ["d.pink", "d pink", "rani", "maroon"],
    },
    "blue": {
        "light": ["sky blue", "skyblue", "l.blue", "l blue"],
        "mid": ["blue"],
        "dark": ["navy blue", "n.blue", "n blue", "d.blue", "dark blue", "rama"],
    },
    "sky blue": {
        "light": ["sky blue", "skyblue", "l.blue"],
        "mid": ["sky blue", "blue"],
        "dark": ["blue", "rama", "navy blue"],
    },
    "navy blue": {
        "light": ["blue", "sky blue"],
        "mid": ["navy blue", "n.blue"],
        "dark": ["navy blue", "rama", "black"],
    },
    "yellow": {
        "light": ["lemon", "cream", "yellow cream"],
        "mid": ["yellow"],
        "dark": ["mustard", "gold"],
    },
    "lemon": {
        "light": ["lemon", "cream"],
        "mid": ["lemon", "yellow"],
        "dark": ["yellow", "mustard"],
    },
    "purple": {
        "light": ["l.purple", "l purple", "violet"],
        "mid": ["purple"],
        "dark": ["d.purple", "d purple", "wine"],
    },
    "violet": {
        "light": ["l.purple", "violet"],
        "mid": ["violet", "purple"],
        "dark": ["purple", "d.purple"],
    },
    "firozi": {
        "light": ["sky blue", "firozi"],
        "mid": ["firozi"],
        "dark": ["rama", "blue"],
    },
    "orange": {
        "light": ["l.orange", "l orange", "peach"],
        "mid": ["orange", "gajri"],
        "dark": ["rust", "gajri", "tomato"],
    },
    "peach": {
        "light": ["peach", "cream", "fawn"],
        "mid": ["peach"],
        "dark": ["orange", "gajri", "fawn"],
    },
    "grey": {
        "light": ["offwhite", "grey", "d.gray"],
        "mid": ["grey"],
        "dark": ["d.gray", "brown", "black"],
    },
    "red": {
        "light": ["tomato", "gajri", "rani"],
        "mid": ["red"],
        "dark": ["maroon", "wine", "burgundy", "rust"],
    },
    "rama": {
        "light": ["firozi", "sky blue", "rama"],
        "mid": ["rama"],
        "dark": ["d.rama", "navy blue", "blue"],
    },
    "black": {"light": ["grey", "brown"], "mid": ["black"], "dark": ["black"]},
    "cream": {
        "light": ["white", "offwhite", "cream"],
        "mid": ["cream", "light cream"],
        "dark": ["fawn", "chiku", "yellow cream"],
    },
    "brown": {
        "light": ["fawn", "chiku", "khaki"],
        "mid": ["brown"],
        "dark": ["rust", "maroon", "black"],
    },
    "rust": {
        "light": ["orange", "gajri", "fawn"],
        "mid": ["rust"],
        "dark": ["maroon", "wine", "brown"],
    },
    "maroon": {
        "light": ["rani", "red", "gajri"],
        "mid": ["maroon", "burgundy"],
        "dark": ["wine", "burgundy", "black"],
    },
    "wine": {
        "light": ["maroon", "rani"],
        "mid": ["wine"],
        "dark": ["wine", "black"],
    },
    "fawn": {
        "light": ["cream", "peach", "fawn"],
        "mid": ["fawn", "chiku"],
        "dark": ["chiku", "brown", "khaki"],
    },
    "gold": {
        "light": ["lemon", "mustard", "cream"],
        "mid": ["gold", "mustard"],
        "dark": ["mustard", "brown"],
    },
    "mustard": {
        "light": ["lemon", "yellow", "gold"],
        "mid": ["mustard"],
        "dark": ["gold", "brown"],
    },
    "chiku": {
        "light": ["fawn", "cream", "peach"],
        "mid": ["chiku"],
        "dark": ["brown", "khaki"],
    },
    "white": {
        "light": ["white", "offwhite"],
        "mid": ["white", "offwhite"],
        "dark": ["cream", "offwhite"],
    },
    "gajri": {
        "light": ["peach", "orange", "l.orange"],
        "mid": ["gajri", "orange"],
        "dark": ["rust", "red", "tomato"],
    },
    "pista": {
        "light": ["pista", "light green"],
        "mid": ["pista", "green"],
        "dark": ["green", "mehndi"],
    },
    "rani": {
        "light": ["pink", "l.pink", "rani"],
        "mid": ["rani"],
        "dark": ["maroon", "wine", "red"],
    },
    "mehndi": {
        "light": ["pista", "green", "light green"],
        "mid": ["mehndi", "mendi"],
        "dark": ["mehndi", "brown", "d.green"],
    },
    "khaki": {
        "light": ["fawn", "chiku", "khaki"],
        "mid": ["khaki", "khakhi", "kakhi"],
        "dark": ["brown", "chiku"],
    },
    "tomato": {
        "light": ["gajri", "orange", "red"],
        "mid": ["tomato", "red"],
        "dark": ["rust", "maroon"],
    },
    "offwhite": {
        "light": ["white", "offwhite"],
        "mid": ["offwhite", "cream"],
        "dark": ["cream", "fawn"],
    },
    "burgundy": {
        "light": ["maroon", "rani"],
        "mid": ["burgundy", "maroon"],
        "dark": ["wine", "black"],
    },
}

# All aliases → canonical base id (before shade)
_ALIASES: dict[str, str] = {
    "firoji": "firozi",
    "froji": "firozi",
    "firoj": "firozi",
    "firji": "firozi",
    "turquoise": "firozi",
    "marron": "maroon",
    "marun": "maroon",
    "rast": "rust",
    "gran": "green",
    "gren": "green",
    "blak": "black",
    "blok": "black",
    "roma": "rama",
    "ramma": "rama",
    "muster": "mustard",
    "musturd": "mustard",
    "plane": "cream",
    "plain": "cream",
    "gajji": "gajri",
    "gajari": "gajri",
    "gajar": "gajri",
    "carrot": "gajri",
    "phoni": "peach",
    "phore": "peach",
    "phonu": "peach",
    "phora": "peach",
    "fone": "peach",
    "phone": "peach",
    "phon": "peach",
    "phn": "peach",
    "peat": "peach",
    "peal": "peach",
    "pech": "peach",
    "peech": "peach",
    "gray": "grey",
    "gry": "grey",
    "skyblue": "sky blue",
    "sky": "sky blue",
    "navy": "navy blue",
    "n blue": "navy blue",
    "n.blue": "navy blue",
    "dark blue": "navy blue",
    "lightgreen": "light green",
    "l green": "light green",
    "l.green": "light green",
    "c green": "green",
    "c. green": "green",
    "off white": "offwhite",
    "off-white": "offwhite",
    "mendi": "mehndi",
    "mehendi": "mehndi",
    "henna": "mehndi",
    "khakhi": "khaki",
    "kakhi": "khaki",
    "kaki": "khaki",
    "chikoo": "chiku",
    "chickoo": "chiku",
    "chikku": "chiku",
    "wine red": "wine",
    "wine colour": "wine",
    "saffron": "mustard",
    "kesar": "mustard",
    "beige": "fawn",
    "badami": "fawn",
    "badaami": "fawn",
    "badam": "fawn",
    "fawn": "fawn",
    "light brown": "fawn",
    "skin beige": "fawn",
    "skin": "peach",
    "skin colour": "peach",
    "skin color": "peach",
    "flesh": "peach",
    "magenta": "rani",
    "hot pink": "rani",
    "cyan": "firozi",
    "aqua": "firozi",
    "teal": "rama",
    "sea green": "rama",
    "olive": "mehndi",
    "parrot": "pista",
    "parrot green": "pista",
    "pista green": "pista",
    "golden": "gold",
    "silver": "grey",
    "cream yellow": "cream",
    "yellow cream": "cream",
    "d pink": "pink",
    "d.pink": "pink",
    "l pink": "pink",
    "l.pink": "pink",
    "d purple": "purple",
    "d.purple": "purple",
    "l purple": "purple",
    "l.purple": "purple",
    "d green": "green",
    "d.green": "green",
    "d rama": "rama",
    "d.rama": "rama",
    "d gray": "grey",
    "d.gray": "grey",
    "l orange": "orange",
    "l.orange": "orange",
    "l blue": "sky blue",
    "l.blue": "sky blue",
    "g.blue": "blue",
    "g blue": "blue",
    "burgandy": "burgundy",
    "lilo": "green",
    "leelo": "green",
    "lilu": "green",
    "leelu": "green",
    "achho lilo": "light green",
    "gulabi": "pink",
    "gulaabi": "pink",
    "gulabi rang": "pink",
    "vadali": "blue",
    "vadli": "blue",
    "neelo": "blue",
    "nilo": "blue",
    "akashi": "sky blue",
    "aakashi": "sky blue",
    "pilo": "yellow",
    "peelo": "yellow",
    "pilu": "yellow",
    "jambli": "purple",
    "jaambli": "purple",
    "jamboo": "purple",
    "narangi": "orange",
    "naranagi": "orange",
    "santra": "orange",
    "lal": "red",
    "laal": "red",
    "kalo": "black",
    "kaalo": "black",
    "safed": "white",
    "saphed": "white",
    "dhole": "white",
    "bhuro": "brown",
    "bhooro": "brown",
    "rakhodi": "grey",
    "rakhodu": "grey",
    "rai": "mustard",
    "kesari": "mustard",
    "kesri": "mustard",
    "soneri": "gold",
    "sonero": "gold",
    "mehndi rang": "mehndi",
    "ranni": "rani",
    "raani": "rani",
    "gaajari": "gajri",
    "pista rang": "pista",
    "cream rang": "cream",
    "peach rang": "peach",
    "phone rang": "peach",
    "phon rang": "peach",
    "લીલો": "green",
    "લીલું": "green",
    "લીલી": "green",
    "આછો લીલો": "light green",
    "ગુલાબી": "pink",
    "વાદળી": "blue",
    "વાદળું": "blue",
    "આકાશી": "sky blue",
    "પીળો": "yellow",
    "પીળું": "yellow",
    "લીંબુ": "lemon",
    "જાંબલી": "purple",
    "ફિરોઝી": "firozi",
    "નારંગી": "orange",
    "પીચ": "peach",
    "ફોન": "peach",
    "રાખોડી": "grey",
    "લાલ": "red",
    "રામા": "rama",
    "કાળો": "black",
    "કાળું": "black",
    "ક્રીમ": "cream",
    "ભૂરો": "brown",
    "રસ્ટ": "rust",
    "મેરૂન": "maroon",
    "વાઇન": "wine",
    "ફૉન": "peach",
    "સોનેરી": "gold",
    "મસ્ટર્ડ": "mustard",
    "રાઈ": "mustard",
    "ચીકૂ": "chiku",
    "સફેદ": "white",
    "ગાજરી": "gajri",
    "પિસ્તા": "pista",
    "રાણી": "rani",
    "મેંદી": "mehndi",
    "ખાકી": "khaki",
    "ટમેટો": "tomato",
}

for _cid, _meta in CANONICAL.items():
    _ALIASES[_cid] = _cid
    _ALIASES[_meta["label"].lower()] = _cid
    if _meta.get("gu"):
        for part in _meta["gu"].replace("/", " ").split():
            p = part.strip().lower()
            if p and p not in _ALIASES:
                _ALIASES[p] = _cid


@dataclass
class ClothResolve:
    input_text: str
    cloth_id: str
    label: str
    hex: str
    gujarati: str
    shade: str  # light | mid | dark
    shade_value: int  # 0..100
    confidence: float
    message: str
    understood_as: str


def _clean(text: str) -> str:
    s = (text or "").strip().lower()
    for ch in (",", ".", ";", ":", "!", "?", "#", "/", "\\", "(", ")", "[", "]"):
        s = s.replace(ch, " ")
    s = " ".join(s.split())
    tokens = [
        t
        for t in s.split()
        if t not in {"rang", "colour", "color", "cloth", "kapda", "fabric", "the", "a", "of"}
    ]
    return " ".join(tokens) if tokens else s


def _lookup_alias(text: str) -> Optional[str]:
    if not text:
        return None
    if text in _ALIASES and _ALIASES[text]:
        return _ALIASES[text]
    compact = text.replace(" ", "")
    if compact in _ALIASES and _ALIASES[compact]:
        return _ALIASES[compact]
    return None


def _fuzzy(text: str) -> Optional[tuple[str, float]]:
    keys = list({k for k, v in _ALIASES.items() if v})
    keys.extend(CANONICAL.keys())
    matches = get_close_matches(text, keys, n=1, cutoff=0.72)
    if not matches:
        for tok in text.split():
            if len(tok) < 3:
                continue
            m = get_close_matches(tok, keys, n=1, cutoff=0.78)
            if m:
                matches = m
                break
    if not matches:
        return None
    key = matches[0]
    cloth = _ALIASES.get(key) or (key if key in CANONICAL else None)
    if not cloth:
        return None
    conf = SequenceMatcher(None, text, key).ratio()
    return cloth, float(conf)


def shade_bucket(shade_value: int) -> str:
    v = max(0, min(100, int(shade_value)))
    if v <= 33:
        return "light"
    if v >= 67:
        return "dark"
    return "mid"


def apply_shade(
    base_id: str, shade_value: int, known_cloths: Optional[set[str]] = None
) -> tuple[str, str]:
    bucket = shade_bucket(shade_value)
    family = SHADE_FAMILY.get(base_id) or {
        "light": [base_id],
        "mid": [base_id],
        "dark": [base_id],
    }
    candidates = list(family.get(bucket) or [base_id])
    if bucket != "mid":
        candidates.extend(family.get("mid") or [base_id])
    candidates.append(base_id)

    known = {(k or "").strip().lower() for k in (known_cloths or set())}

    # Prefer exact recipe cloth names first (light/dark spellings in the book)
    if known:
        for c in candidates:
            key = c.strip().lower()
            if key in known:
                return key, bucket
        # fall back to canonical bases that exist in recipes
        for c in candidates:
            key = c.strip().lower()
            if key in CANONICAL and key in known:
                return key, bucket

    for c in candidates:
        key = c.strip().lower()
        if key in CANONICAL:
            return key, bucket
    return base_id, bucket


def resolve_cloth(
    text: str,
    shade_value: int = 50,
    known_cloths: Optional[set[str]] = None,
) -> ClothResolve:
    raw = (text or "").strip()
    cleaned = _clean(raw)
    shade_value = max(0, min(100, int(shade_value)))

    if not cleaned:
        return ClothResolve(
            input_text=raw,
            cloth_id="",
            label="",
            hex="#ccc",
            gujarati="",
            shade=shade_bucket(shade_value),
            shade_value=shade_value,
            confidence=0.0,
            message="Type a cloth colour (English or Gujarati)",
            understood_as="",
        )

    base: Optional[str] = _lookup_alias(cleaned)
    conf = 1.0 if base else 0.0
    if not base:
        fuzzy = _fuzzy(cleaned)
        if fuzzy:
            base, conf = fuzzy
    if not base:
        for tok in cleaned.split():
            base = _lookup_alias(tok)
            if base:
                conf = 0.85
                break
            fuzzy = _fuzzy(tok)
            if fuzzy:
                base, conf = fuzzy
                break

    if not base:
        return ClothResolve(
            input_text=raw,
            cloth_id="",
            label="",
            hex="#ccc",
            gujarati="",
            shade=shade_bucket(shade_value),
            shade_value=shade_value,
            confidence=0.0,
            message=f"Could not understand \"{raw}\". Try Green / lilo / Peach / phone…",
            understood_as="",
        )

    cloth_id, shade = apply_shade(base, shade_value, known_cloths)
    meta = CANONICAL.get(base) or CANONICAL.get(cloth_id) or {"label": base.title(), "hex": "#bbb", "gu": ""}
    label = (CANONICAL.get(cloth_id) or meta)["label"]
    hex_c = (CANONICAL.get(cloth_id) or meta)["hex"]
    gu = meta.get("gu") or ""

    typed_norm = cleaned
    shown = label
    if typed_norm in {base, cloth_id, label.lower()} and shade == "mid":
        message = f"Using {shown}" + (f" ({gu})" if gu else "")
    else:
        message = f'You wrote "{raw}" -> we take it as {shown}'
        if shade != "mid":
            message += f" · {shade} shade"
        if gu:
            message += f" ({gu})"

    return ClothResolve(
        input_text=raw,
        cloth_id=cloth_id,
        label=label,
        hex=hex_c,
        gujarati=gu,
        shade=shade,
        shade_value=shade_value,
        confidence=round(conf, 2),
        message=message,
        understood_as=shown,
    )


def _hex_to_rgb(hex_c: str) -> tuple[int, int, int]:
    h = (hex_c or "#888888").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    n = int(h[:6], 16)
    return (n >> 16) & 255, (n >> 8) & 255, n & 255


def _rgb_dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def nearest_cloth_from_rgb(
    r: int,
    g: int,
    b: int,
    known_cloths: Optional[set[str]] = None,
) -> ClothResolve:
    """Map a sampled photo RGB to the closest palette cloth."""
    target = (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))
    known = known_cloths or set()
    keys = [k for k in CANONICAL if not known or k in known]
    if not keys:
        keys = list(CANONICAL.keys())
    best_key = keys[0]
    best_d = 1e9
    for key in keys:
        hx = CANONICAL[key].get("hex") or "#bbb"
        d = _rgb_dist(target, _hex_to_rgb(hx))
        if d < best_d:
            best_d = d
            best_key = key
    meta = CANONICAL[best_key]
    sampled = "#{:02x}{:02x}{:02x}".format(*target)
    conf = max(0.0, min(1.0, 1.0 - best_d / 441.0))
    gu = meta.get("gu") or ""
    label = meta["label"]
    message = f"From photo we guess {label}"
    if gu:
        message += f" ({gu})"
    return ClothResolve(
        input_text=f"photo:{sampled}",
        cloth_id=best_key,
        label=label,
        hex=meta["hex"],
        gujarati=gu,
        shade="mid",
        shade_value=50,
        confidence=round(conf, 2),
        message=message,
        understood_as=label,
    )


def normalize_cloth_value(value: str) -> str:
    """Backward-compatible normalizer for load/train paths."""
    r = resolve_cloth(value, shade_value=50)
    return r.cloth_id or (value or "").strip().lower()
