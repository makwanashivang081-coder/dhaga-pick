"""Export lightweight JSON model for Vercel deploy."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from services.data_service import dedupe_recipes, load_recipes
from utils.tikli import parse_tikli_needle


def main() -> None:
    recipes = dedupe_recipes(load_recipes(ROOT / "data", prefer_high_clarity=False))
    payload = {
        "recipes": [
            {
                "recipe_id": r.recipe_id,
                "design_no": r.design_no,
                "parts": r.parts,
                "cloth": r.cloth,
                "needles": r.needles,
                "design_type": r.design_type,
                "thread_count": r.thread_count,
                "clarity": r.clarity,
                "tikli": r.tikli or "",
                "tikli_needle": parse_tikli_needle(r.tikli or "", r.needles),
            }
            for r in recipes
        ]
    }
    out = ROOT / "models" / "lite_recipes.json"
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    with_tikli = sum(1 for r in payload["recipes"] if r["tikli_needle"])
    print(
        f"wrote {len(recipes)} recipes ({with_tikli} with tikli needle) -> {out} "
        f"({out.stat().st_size / 1024:.0f} KB)"
    )


if __name__ == "__main__":
    main()
