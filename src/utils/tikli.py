"""Parse tikli presence + which needle number it runs on."""
from __future__ import annotations

import re
from collections import Counter
from typing import Optional


def parse_tikli_needle(tikli_raw: str, needles: Optional[list[str]] = None) -> Optional[int]:
    """
    Return needle number 1..5 if tikli is present, else None.
    Understands book notes like 'tikli', 'circle-dot under col3', 'n3', 'needle 2'.
    """
    raw = (tikli_raw or "").strip()
    if not raw:
        return None
    low = raw.lower()
    # explicit column / needle markers from the handwritten book
    m = re.search(r"\bcol(?:umn)?\s*([1-5])\b", low)
    if m:
        return int(m.group(1))
    m = re.search(r"\bn(?:eedle)?\s*([1-5])\b", low)
    if m:
        return int(m.group(1))
    m = re.search(r"\b([1-5])\b", low)
    if m and ("tikli" in low or "dot" in low or "circle" in low or "under" in low):
        return int(m.group(1))

    # Present but needle not written → use last filled colour column (book layout)
    if "tikli" in low or "dot" in low or "circle" in low:
        needles = needles or []
        last = 0
        for i, n in enumerate(needles[:5], start=1):
            if (n or "").strip():
                last = i
        return last or None
    return None


def tikli_label(needle: Optional[int], has_tikli: bool = True) -> str:
    if not has_tikli and not needle:
        return ""
    if needle:
        return f"Tikli on Needle {needle}"
    return "Tikli (needle not marked)"


def majority_tikli_needle(items: list[tuple[str, list[str]]]) -> Optional[int]:
    """items: list of (tikli_raw, needles)."""
    votes: Counter[int] = Counter()
    for tikli_raw, needles in items:
        n = parse_tikli_needle(tikli_raw, needles)
        if n:
            votes[n] += 1
    if not votes:
        return None
    return votes.most_common(1)[0][0]
