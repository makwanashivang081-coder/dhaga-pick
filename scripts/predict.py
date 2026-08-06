"""CLI inference: recommend 10 full thread recipes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.types import PredictRequest


def main() -> None:
    parser = argparse.ArgumentParser(description="Jeetubhai thread colour recommender")
    parser.add_argument("--cloth", required=True, help="Cloth colour e.g. green, peach, firozi")
    parser.add_argument("--design", default="", help="Design number e.g. 1237")
    parser.add_argument("--parts", default="", help="neck / border / kp / neck+border ...")
    parser.add_argument("--threads", type=int, default=0, help="Needle count 3-5 (0=any)")
    parser.add_argument("--tikli", default="", help="Optional tikli hint")
    parser.add_argument("--lock-n1", default="", help="Lock needle 1 thread; refresh 2-5 only")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args()

    artifact_path = ROOT / "models" / "colour_recommender.joblib"
    if not artifact_path.exists():
        raise SystemExit("Model not found. Run: python scripts/train.py")

    artifact = joblib.load(artifact_path)
    model = artifact["model"]

    req = PredictRequest(
        cloth=args.cloth,
        design_no=args.design,
        parts=args.parts,
        thread_count=args.threads,
        tikli=args.tikli or None,
        locked_n1=args.lock_n1 or None,
    )
    result = model.recommend(req)

    payload = {
        "query": {
            "cloth": req.cloth,
            "design_no": req.design_no,
            "parts": req.parts,
            "thread_count": req.thread_count,
            "locked_n1": req.locked_n1,
        },
        "best_rank": 1,
        "options": [
            {
                "rank": o.rank,
                "score": round(o.score, 3),
                "match_reason": o.match_reason,
                "design_no": o.recipe.design_no,
                "parts": o.recipe.parts,
                "cloth": o.recipe.cloth,
                "needles": {
                    f"n{i+1}": t for i, t in enumerate(o.recipe.needles) if t
                },
                "jari_note": o.recipe.jari_note,
                "tikli": o.recipe.tikli,
                "image": o.recipe.image,
                "source_page": o.recipe.source_page,
                "recipe_id": o.recipe.recipe_id,
            }
            for o in result.options
        ],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    print(f"Query: cloth={args.cloth} design={args.design or '-'} parts={args.parts or '-'} threads={args.threads or 'any'}")
    if args.lock_n1:
        print(f"Locked n1: {args.lock_n1} (options re-ranked for n2-n5)")
    print(f"Showing {len(result.options)} full recipes (#1 = best)\n")
    for o in result.options:
        needles = " | ".join(f"{i+1}:{t}" for i, t in enumerate(o.recipe.needles) if t)
        print(f"#{o.rank}  {needles}")
        print(f"    design={o.recipe.design_no} cloth={o.recipe.cloth or '-'} reason={o.match_reason} score={o.score:.1f}")


if __name__ == "__main__":
    main()
