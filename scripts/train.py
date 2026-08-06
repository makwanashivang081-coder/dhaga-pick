"""Train Jeetubhai colour recommender and save artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from services.data_service import dedupe_recipes, load_recipes
from services.recommender_service import ColourRecommender


def main() -> None:
    data_dir = ROOT / "data"
    models_dir = ROOT / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # Use all rows with needles (user wants max data); clarity still used as a feature
    recipes = dedupe_recipes(load_recipes(data_dir, prefer_high_clarity=False))
    if not recipes:
        raise SystemExit("No recipes found in data/")

    model = ColourRecommender()
    result = model.fit(recipes)

    artifact = {
        "model": model,
        "metrics": result.metrics,
        "n_recipes": result.n_recipes,
        "n_train_pairs": result.n_train,
        "n_test_pairs": result.n_test,
    }
    out_path = models_dir / "colour_recommender.joblib"
    joblib.dump(artifact, out_path)

    metrics_path = models_dir / "metrics.json"
    metrics_path.write_text(
        json.dumps(
            {
                "metrics": result.metrics,
                "n_recipes": result.n_recipes,
                "n_train_pairs": result.n_train,
                "n_test_pairs": result.n_test,
                "model_path": str(out_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=== TRAINING COMPLETE ===")
    print(f"recipes: {result.n_recipes}")
    print(f"pair train/test: {result.n_train}/{result.n_test}")
    for k, v in result.metrics.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    print(f"saved: {out_path}")
    print(f"metrics: {metrics_path}")

    # smoke prediction
    sample = next((r for r in recipes if r.cloth), recipes[0])
    from utils.types import PredictRequest

    pred = model.recommend(
        PredictRequest(
            cloth=sample.cloth or "green",
            design_no=sample.design_no,
            parts=sample.parts,
            thread_count=sample.thread_count,
        )
    )
    print("=== SMOKE PREDICT ===")
    print(f"query cloth={sample.cloth} design={sample.design_no} parts={sample.parts}")
    for opt in pred.options:
        needles = " | ".join(f"n{i+1}={t}" for i, t in enumerate(opt.recipe.needles) if t)
        print(f"#{opt.rank} [{opt.match_reason}] score={opt.score:.1f} :: {needles}")


if __name__ == "__main__":
    main()
