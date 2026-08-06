# Jeetubhai Colour Recommender

Trained hybrid model: historical recipe retrieval + ranking + optional n1-lock refresh for needles 2–5.

## Process

See `PROCESS_FLOW.md`.

## Train

```bash
python scripts/train.py
```

Writes:
- `models/colour_recommender.joblib`
- `models/metrics.json`

## Predict (10 full recipes, #1 = best)

```bash
python scripts/predict.py --cloth lemon --design 1237 --parts "neck+astin border"
python scripts/predict.py --cloth green --parts neck --threads 3
python scripts/predict.py --cloth green --design 1239 --lock-n1 "125 R Royal"
python scripts/predict.py --cloth peach --design 1240 --json
```

## Web UI (phone / tablet / PC)

```bash
python app.py
```

Or double-click `start_ui.bat`, then open **http://127.0.0.1:8000** (same Wi‑Fi: use your PC’s IP).

## Deploy on Vercel (share with dad / brother)

1. Push this folder to GitHub (exclude huge image folders — already in `.gitignore`).
2. Go to [vercel.com](https://vercel.com) → **Add New Project** → import that GitHub repo.
3. Deploy. You’ll get a link like `https://dhaga-pick.vercel.app` — open on any phone.

Needs `models/lite_recipes.json` + `models/gallery_index.json` (already generated). No heavy sklearn model on Vercel.

## Accuracy

```bash
python scripts/eval_accuracy.py
```

Report saved to `models/accuracy_report.json`.

## Notes

- v1 keeps jari in recipes; ranking prefers historical full maps.
- Tikli optional when present in data.
