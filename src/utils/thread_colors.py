"""Map Raj/Royal thread labels → shade-card hex for UI dots.

Only verified codes from models/thread_shade_hex.json are shown.
Unknown codes get no fake colour (avoids rust-for-315 style mismatches).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SHADE_PATH = _ROOT / "models" / "thread_shade_hex.json"

# Jari / metallic — not on viscose shade card numbering.
_SPECIAL: dict[str, str] = {
    "jari": "#d4af37",
    "zari": "#d4af37",
    "vw": "#d4af37",
    "bch": "#d4af37",
    "m": "#c0c0c0",
    "md": "#9aa0a6",
    "lg": "#e8d48b",
    "badla": "#d4af37",
    "black": "#1a1a1a",
    "white": "#f5f5f5",
    "silver": "#c0c0c0",
}


@lru_cache(maxsize=1)
def _shade_codes() -> dict[str, str]:
    if not _SHADE_PATH.exists():
        return {}
    try:
        data = json.loads(_SHADE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    codes = data.get("codes") or {}
    return {str(k).upper(): str(v).lower() for k, v in codes.items() if v}


def _parse(thread: str) -> tuple[str, str, str]:
    """Return (numeric_or_alpha_code, modifiers, brand)."""
    s = " ".join((thread or "").strip().split())
    if not s:
        return "", "", ""
    low = s.lower()
    brand = ""
    if re.search(r"\broyal\b", low):
        brand = "royal"
    elif re.search(r"\braj\b", low):
        brand = "raj"

    # Strip brand / filler words so they are never treated as L/D modifiers.
    core = re.sub(r"\b(royal|raj|thread|dhaga|viscose)\b", " ", low)
    core = " ".join(core.split())

    m = re.match(r"^([a-z]+)\b", core)
    if m and not re.search(r"\d", m.group(1)):
        return m.group(1), core[m.end() :].strip(), brand

    m = re.match(r"^(\d+)(.*)", core)
    if m:
        mods = re.sub(r"[^a-z]", "", (m.group(2) or "").lower())
        return m.group(1), mods, brand

    return core, "", brand


def _modifier_keys(code: str, mods: str) -> list[str]:
    """Lookup keys from most specific to base, e.g. 118.LL → 118.L → 118."""
    mods = re.sub(r"[^a-z]", "", (mods or "").lower())
    keys: list[str] = []
    if mods:
        keys.append(f"{code}.{mods.upper()}")
        for i in range(len(mods) - 1, 0, -1):
            keys.append(f"{code}.{mods[:i].upper()}")
    # longest modifier tokens first
    for token in ("ll", "dd", "nl", "nd", "st", "dr", "lr", "ds", "dt"):
        if token in mods:
            keys.append(f"{code}.{token.upper()}")
    for token in ("l", "d", "n", "s", "b", "f", "r", "t", "p", "u", "c", "h"):
        if token in mods:
            keys.append(f"{code}.{token.upper()}")
    keys.append(code)
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for k in keys:
        ku = k.upper()
        if ku not in seen:
            seen.add(ku)
            out.append(ku)
    return out


def _scale_hex(hex_color: str, factor: float) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    rgb = [int(h[i : i + 2], 16) for i in (0, 2, 4)]
    if factor > 1:
        t = min(1.0, factor - 1.0)
        rgb = [int(c + (255 - c) * t) for c in rgb]
    else:
        rgb = [max(0, min(255, int(c * factor))) for c in rgb]
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _apply_modifiers(hex_color: str, mods: str) -> str:
    """Lighten/darken only when shade card lacks that exact modifier key."""
    mods = (mods or "").lower()
    factor = 1.0
    if "ll" in mods:
        factor = 1.28
    elif re.search(r"(^|[^a-z])l([^a-z]|$)", mods) or "nl" in mods:
        factor = 1.16
    elif "dd" in mods:
        factor = 0.55
    elif re.search(r"(^|[^a-z])d([^a-z]|$)", mods):
        factor = 0.78
    if abs(factor - 1.0) < 0.01:
        return hex_color
    return _scale_hex(hex_color, factor)


@lru_cache(maxsize=1)
def _numeric_bases() -> dict[int, str]:
    out: dict[int, str] = {}
    for key, hx in _shade_codes().items():
        m = re.match(r"^(\d+)$", key)
        if m:
            out[int(m.group(1))] = hx
    return out


def _nearest_numeric_hex(num: int) -> str | None:
    bases = _numeric_bases()
    if not bases:
        return None
    if num in bases:
        return bases[num]
    nearest = min(bases.keys(), key=lambda n: abs(n - num))
    return bases[nearest]


@lru_cache(maxsize=4096)
def thread_approx_hex(thread: str) -> str | None:
    """Shade-card hex for a label like '315 Royal', or None if unknown."""
    s = (thread or "").strip()
    if not s:
        return None
    low = s.lower()
    if "jari" in low or "zari" in low:
        return _SPECIAL["jari"]

    code, mods, _brand = _parse(s)
    if not code:
        return None

    if code in _SPECIAL and not code.isdigit():
        return _SPECIAL[code]

    shade = _shade_codes()
    if not shade:
        return None

    # Use parsed modifiers only — never the full label (avoids "Royal" → L).
    for key in _modifier_keys(code, mods):
        if key in shade:
            hx = shade[key]
            if "." in key:
                return hx
            return _apply_modifiers(hx, mods)

    if code.isdigit():
        near = _nearest_numeric_hex(int(code))
        if near:
            return _apply_modifiers(near, mods)

    return None


def enrich_options_with_thread_colour(options: list[dict]) -> list[dict]:
    for opt in options:
        thread = opt.get("thread") or ""
        hx = thread_approx_hex(thread)
        if hx:
            opt["thread_hex"] = hx
            opt["thread_colour_note"] = "shade_card"
        else:
            opt.pop("thread_hex", None)
            opt["thread_colour_note"] = "unknown"
    return options


def needle_chip(needle: int, thread: str, tikli_needle: int | None = None) -> dict:
    """One paint-strip chip: needle index, thread label, shade-card hex if known."""
    t = (thread or "").strip()
    hx = thread_approx_hex(t) if t else None
    return {
        "needle": needle,
        "thread": t,
        "thread_hex": hx,
        "thread_colour_note": "shade_card" if hx else "unknown",
        "is_tikli": bool(tikli_needle and tikli_needle == needle),
    }


def enrich_recipe_needles(needles: list[str], tikli_needle: int | None = None) -> list[dict]:
    chips: list[dict] = []
    for i, thread in enumerate(list(needles or [])[:5], start=1):
        t = (thread or "").strip()
        if not t:
            continue
        chips.append(needle_chip(i, t, tikli_needle))
    return chips
