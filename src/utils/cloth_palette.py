"""Cloth colour swatches for dad-friendly picking."""
from __future__ import annotations

from utils.cloth_vocab import CANONICAL


def cloth_palette(available: list[str] | None = None) -> list[dict[str, str]]:
    """Return swatches — prefer colours present in data, always include full palette."""
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    avail = {(a or "").strip().lower() for a in (available or []) if a}

    # First: colours that appear in recipes (and are in canonical)
    for key in sorted(avail):
        meta = CANONICAL.get(key)
        if not meta or key in seen:
            continue
        seen.add(key)
        out.append({"id": key, "label": meta["label"], "hex": meta["hex"], "gu": meta.get("gu", "")})

    # Then fill remaining canonical colours so typing/shade always has a home
    for key, meta in CANONICAL.items():
        if key in seen:
            continue
        seen.add(key)
        out.append({"id": key, "label": meta["label"], "hex": meta["hex"], "gu": meta.get("gu", "")})

    out.sort(key=lambda x: x["label"].lower())
    return out
