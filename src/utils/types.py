"""Shared types and constants for Jeetubhai colour recommendation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

BRANDS = ("Raj", "Royal")
MAX_NEEDLES = 5
TOP_K = 10

# Kept for backwards compatibility; prefer utils.cloth_vocab.resolve_cloth
CLOTH_ALIASES: dict[str, str] = {
    "firoji": "firozi",
    "froji": "firozi",
    "firoj": "firozi",
    "marron": "maroon",
    "rast": "rust",
    "gran": "green",
    "blak": "black",
    "roma": "rama",
    "muster": "mustard",
    "plane": "plain",
    "gajji": "gajri",
    "gajari": "gajri",
    "phoni": "peach",
    "phore": "peach",
    "phonu": "peach",
    "phora": "peach",
    "fone": "peach",
    "phone": "peach",
    "chone": "cream",
    "peat": "peach",
    "peal": "peach",
    "gray": "grey",
}

PART_ALIASES: dict[str, str] = {
    "nake": "neck",
    "nack": "neck",
    "asteen": "astin",
    "boder": "border",
    "buti": "butti",
    "booty": "butti",
    "kk": "kp",
}


@dataclass
class Recipe:
    recipe_id: str
    source_page: str
    design_no: str
    parts: str
    cloth: str
    needles: list[str]  # n1..n5, may include empty
    tikli: str
    jari_note: str
    image: str
    notes: str
    clarity: str
    thread_count: int = 0
    has_jari: bool = False
    design_type: str = ""

    def __post_init__(self) -> None:
        self.needles = [(n or "").strip() for n in self.needles[:MAX_NEEDLES]]
        while len(self.needles) < MAX_NEEDLES:
            self.needles.append("")
        self.thread_count = sum(1 for n in self.needles if n and "jari" not in n.lower())
        # count jari slots separately but still toward machine occupancy
        jari_slots = sum(1 for n in self.needles if n and "jari" in n.lower())
        self.has_jari = jari_slots > 0 or bool(self.jari_note)
        occupied = sum(1 for n in self.needles if n)
        self.thread_count = occupied  # machine needle count including jari position
        self.design_type = primary_design_type(self.parts)


@dataclass
class RankedRecipe:
    recipe: Recipe
    score: float
    rank: int
    match_reason: str


@dataclass
class PredictRequest:
    cloth: str
    design_no: str = ""
    parts: str = ""
    thread_count: int = 0  # 0 = any
    tikli: Optional[str] = None
    locked_n1: Optional[str] = None
    similar_design_nos: list[str] = field(default_factory=list)


@dataclass
class PredictResponse:
    best: RankedRecipe
    options: list[RankedRecipe] = field(default_factory=list)


def primary_design_type(parts: str) -> str:
    p = (parts or "").lower()
    for a, b in PART_ALIASES.items():
        p = p.replace(a, b)
    order = [
        ("neck+border", "neck_border"),
        ("neck+astin", "neck_astin"),
        ("neck", "neck"),
        ("border", "border"),
        ("kp", "kp"),
        ("kurta", "kp"),
        ("body", "body"),
        ("daman", "daman"),
        ("astin", "astin"),
        ("butti", "butti"),
        ("cp", "cp"),
        ("patti", "patti"),
    ]
    for key, label in order:
        if key in p:
            return label
    return "other"


def normalize_cloth(value: str) -> str:
    try:
        from utils.cloth_vocab import normalize_cloth_value

        return normalize_cloth_value(value)
    except Exception:
        s = (value or "").strip().lower()
        return CLOTH_ALIASES.get(s, s)


def normalize_parts(value: str) -> str:
    s = (value or "").strip().lower()
    for a, b in PART_ALIASES.items():
        s = s.replace(a, b)
    return " ".join(s.split())


def is_jari_thread(text: str) -> bool:
    return "jari" in (text or "").lower()
