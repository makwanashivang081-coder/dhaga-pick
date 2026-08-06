"""Approximate Raj/Royal thread colours for UI dots (not exact shade-card matches)."""
from __future__ import annotations

import re
from functools import lru_cache

# Rough “upar se” map for common codes seen in Jeetubhai book.
# Not shade-card accurate — dad-friendly hint only.
_BASE: dict[str, str] = {
    "8": "#f2e6d8",
    "33": "#c9a66b",
    "65": "#d4a017",
    "75": "#e8d5a3",
    "110": "#f5f0e6",
    "118": "#f7f3ea",
    "125": "#f0c4a0",
    "188": "#2f6fed",
    "190": "#c9a227",
    "235": "#e8b4bc",
    "315": "#c45c26",
    "321": "#8b3a2a",
    "335": "#d4762c",
    "341": "#a3482b",
    "343": "#b85c38",
    "372": "#6b4c9a",
    "710": "#2a6f4e",
    "722": "#1f6b4a",
    "723": "#245c3a",
    "727": "#3d8b6e",
    "728": "#2f7a55",
    "741": "#d4af37",
    "751": "#e6c35c",
    "820": "#1a1a1a",
    "834": "#5c4033",
    "840": "#4a3728",
    "m": "#c0c0c0",
    "md": "#9aa0a6",
    "bch": "#d4af37",
}

_HUE_BANDS = [
    (0, 50, "#f5f0e6"),
    (51, 100, "#f0d78c"),
    (101, 150, "#e8b4bc"),
    (151, 200, "#c9a227"),
    (201, 250, "#e89cae"),
    (251, 300, "#c45c26"),
    (301, 350, "#b85c38"),
    (351, 400, "#6b4c9a"),
    (401, 500, "#4c6ef5"),
    (501, 600, "#0b7285"),
    (601, 700, "#2f9e44"),
    (701, 800, "#1f6b4a"),
    (801, 900, "#5c4033"),
    (901, 9999, "#212529"),
]


def _parse(thread: str) -> tuple[str, str]:
    s = " ".join((thread or "").strip().split())
    if not s:
        return "", ""
    low = s.lower()
    m = re.match(r"^([a-z]+)\b", low)
    if m and not re.search(r"\d", m.group(1)):
        return m.group(1), low[m.end() :].strip()
    m = re.match(r"^(\d+)\s*([a-z]*)", low)
    if not m:
        return low, ""
    return m.group(1), (m.group(2) or "").lower()


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
    mods = (mods or "").lower()
    factor = 1.0
    if "ll" in mods:
        factor = 1.35
    elif re.search(r"(^|[^a-z])l([^a-z]|$)", mods) or " nl" in f" {mods}" or mods.startswith("nl"):
        factor = 1.2
    elif "dd" in mods:
        factor = 0.55
    elif re.search(r"(^|[^a-z])d([^a-z]|$)", mods):
        factor = 0.72
    if abs(factor - 1.0) < 0.01:
        return hex_color
    return _scale_hex(hex_color, factor)


def _band_for_number(n: int) -> str:
    for lo, hi, hx in _HUE_BANDS:
        if lo <= n <= hi:
            return hx
    return "#868e96"


@lru_cache(maxsize=2048)
def thread_approx_hex(thread: str) -> str:
    """Approximate display colour for a thread label like '65 Royal' / '118 L Royal'."""
    s = (thread or "").strip()
    if not s:
        return "#c4b8a5"
    low = s.lower()
    if "jari" in low or "zari" in low:
        return "#d4af37"
    code, mods = _parse(s)
    blob = f"{mods} {low}"
    if code in _BASE:
        return _apply_modifiers(_BASE[code], blob)
    if code.isdigit():
        return _apply_modifiers(_band_for_number(int(code)), blob)
    palette = [
        "#e03131",
        "#ff922b",
        "#f4d03f",
        "#2f9e44",
        "#22b8cf",
        "#4c6ef5",
        "#9b59b6",
        "#d6336c",
        "#8d6e63",
        "#868e96",
    ]
    return palette[sum(ord(c) for c in low) % len(palette)]


def enrich_options_with_thread_colour(options: list[dict]) -> list[dict]:
    for opt in options:
        thread = opt.get("thread") or ""
        opt["thread_hex"] = thread_approx_hex(thread)
        opt["thread_colour_note"] = "approx"
    return options
