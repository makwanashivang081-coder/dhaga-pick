"""Data loading and cleaning service."""
from __future__ import annotations

import csv
from pathlib import Path

from utils.types import Recipe, is_jari_thread, normalize_cloth, normalize_parts


def _parse_row(row: dict[str, str]) -> Recipe | None:
    needles = [row.get(f"n{i}", "") or "" for i in range(1, 6)]
    if not any(n.strip() for n in needles):
        return None
    design_no = (row.get("design_no") or "").strip()
    if not design_no:
        return None
    return Recipe(
        recipe_id=(row.get("recipe_id") or "").strip(),
        source_page=(row.get("source_page") or "").strip(),
        design_no=design_no,
        parts=normalize_parts(row.get("parts") or ""),
        cloth=normalize_cloth(row.get("cloth") or ""),
        needles=needles,
        tikli=(row.get("tikli") or "").strip(),
        jari_note=(row.get("jari_note") or "").strip(),
        image=(row.get("image") or "").strip(),
        notes=(row.get("notes") or "").strip(),
        clarity=(row.get("clarity") or "").strip() or "medium",
    )


def load_recipes(data_dir: Path, prefer_high_clarity: bool = False) -> list[Recipe]:
    """Load with_cloth + no_cloth. Prefer high clarity when flag set, else use all with needles."""
    recipes: list[Recipe] = []
    for name in ("with_cloth.csv", "no_cloth.csv"):
        path = data_dir / name
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                recipe = _parse_row(row)
                if recipe is None:
                    continue
                if prefer_high_clarity and recipe.clarity != "high":
                    continue
                recipes.append(recipe)
    return recipes


def recipe_key(recipe: Recipe) -> tuple[str, ...]:
    return (recipe.design_no, recipe.cloth, recipe.parts, *recipe.needles)


def dedupe_recipes(recipes: list[Recipe]) -> list[Recipe]:
    seen: set[tuple[str, ...]] = set()
    out: list[Recipe] = []
    for r in recipes:
        k = recipe_key(r)
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def colour_slots_for_v1(needles: list[str]) -> list[str]:
    """Needle colours used for ranking similarity; jari kept but marked."""
    return [n.strip() for n in needles]


def non_jari_signature(needles: list[str]) -> tuple[str, ...]:
    """Signature ignoring empty and treating jari as placeholder for match flexibility."""
    sig: list[str] = []
    for n in needles:
        n = (n or "").strip()
        if not n:
            sig.append("")
        elif is_jari_thread(n):
            sig.append("__JARI__")
        else:
            sig.append(n.lower())
    return tuple(sig)
