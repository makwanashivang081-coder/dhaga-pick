"""FastAPI app — mobile + Vercel friendly (lite model, no sklearn)."""
from __future__ import annotations

import io
import sys
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from services.gallery_service import GalleryIndex  # noqa: E402
from services.lite_recommender import LiteRecommender  # noqa: E402
from utils.cloth_palette import cloth_palette  # noqa: E402
from utils.cloth_vocab import nearest_cloth_from_rgb, resolve_cloth  # noqa: E402
from utils.thread_colors import (  # noqa: E402
    enrich_options_with_thread_colour,
    enrich_recipe_needles,
)
from utils.types import PredictRequest  # noqa: E402

LITE_PATH = ROOT / "models" / "lite_recipes.json"
GALLERY_JSON = ROOT / "models" / "gallery_index.json"
GALLERY_JOBLIB = ROOT / "models" / "gallery_index.joblib"
GALLERY_ROOT = ROOT / "Jeetubhai Images"
STATIC_DIR = ROOT / "web"

app = FastAPI(title="Dhaga Pick", version="1.5.0")
_model: LiteRecommender | None = None
_gallery: GalleryIndex | None = None


def get_model() -> LiteRecommender:
    global _model
    if _model is None:
        if not LITE_PATH.exists():
            raise HTTPException(500, "Missing models/lite_recipes.json — run scripts/export_lite_model.py")
        _model = LiteRecommender.load(LITE_PATH)
    return _model


def get_gallery() -> GalleryIndex | None:
    global _gallery
    if _gallery is None:
        for path in (GALLERY_JSON, GALLERY_JOBLIB):
            if path.exists():
                try:
                    _gallery = GalleryIndex.load(path)
                    break
                except Exception:
                    _gallery = None
        if _gallery is None and GALLERY_ROOT.exists():
            try:
                _gallery = GalleryIndex.build(GALLERY_ROOT)
                GALLERY_JSON.parent.mkdir(parents=True, exist_ok=True)
                _gallery.save(GALLERY_JSON)
            except Exception:
                _gallery = None
    return _gallery


class NeedleStepBody(BaseModel):
    cloth: str = Field(..., min_length=1)
    cloth_raw: str = ""
    shade_value: int = Field(default=50, ge=0, le=100)
    design_no: str = ""
    parts: str = ""
    thread_count: int = 0
    gallery_path: str = ""
    similar_design_nos: list[str] = Field(default_factory=list)
    locked_needles: dict[str, str] = Field(default_factory=dict)
    target_needle: int = Field(..., ge=1, le=5)
    has_design_photo: bool = False


class RecipesBody(BaseModel):
    cloth: str = Field(..., min_length=1)
    cloth_raw: str = ""
    shade_value: int = Field(default=50, ge=0, le=100)
    design_no: str = ""
    thread_count: int = 0
    similar_design_nos: list[str] = Field(default_factory=list)
    has_design_photo: bool = False


class ResolveClothBody(BaseModel):
    text: str = ""
    shade_value: int = Field(default=50, ge=0, le=100)


@app.on_event("startup")
def startup() -> None:
    try:
        get_model()
    except Exception:
        pass
    try:
        get_gallery()
    except Exception:
        pass


@app.get("/api/health")
def health():
    model = get_model()
    cloths = sorted({r.cloth for r in model.recipes if r.cloth})
    gallery = get_gallery()
    return {
        "ok": True,
        "recipes": len(model.recipes),
        "cloths": cloths,
        "cloth_swatches": cloth_palette(cloths),
        "gallery_images": len(gallery.items) if gallery else 0,
    }


def _sample_cloth_rgb(img: Image.Image) -> tuple[int, int, int]:
    """Dominant cloth colour from centre of photo (screen approx)."""
    img = img.convert("RGB")
    w, h = img.size
    crop = img.crop((int(w * 0.18), int(h * 0.18), int(w * 0.82), int(h * 0.82)))
    crop = crop.resize((56, 56), Image.Resampling.LANCZOS)
    pixels = list(crop.getdata())
    usable: list[tuple[int, int, int]] = []
    for pr, pg, pb in pixels:
        lum = (pr + pg + pb) / 3
        spread = max(pr, pg, pb) - min(pr, pg, pb)
        if lum < 16 or lum > 248:
            continue
        if spread < 6:
            continue
        usable.append((pr, pg, pb))
    if not usable:
        usable = list(pixels)
    r = sum(p[0] for p in usable) // len(usable)
    g = sum(p[1] for p in usable) // len(usable)
    b = sum(p[2] for p in usable) // len(usable)
    return r, g, b


@app.post("/api/detect-cloth-color")
async def detect_cloth_color(file: UploadFile = File(...)):
    """Guess cloth palette colour from a photo; user confirms in UI."""
    if not file.filename:
        raise HTTPException(400, "Upload a cloth photo")
    raw = await file.read()
    try:
        img = Image.open(io.BytesIO(raw))
    except Exception as exc:
        raise HTTPException(400, "Could not read image") from exc
    r, g, b = _sample_cloth_rgb(img)
    model = get_model()
    known = {c for c in {r.cloth for r in model.recipes if r.cloth}}
    resolved = nearest_cloth_from_rgb(r, g, b, known_cloths=known)
    sampled_hex = "#{:02x}{:02x}{:02x}".format(r, g, b)
    return {
        "sampled_rgb": {"r": r, "g": g, "b": b},
        "sampled_hex": sampled_hex,
        "cloth_id": resolved.cloth_id,
        "label": resolved.label,
        "hex": resolved.hex,
        "gujarati": resolved.gujarati,
        "confidence": resolved.confidence,
        "message": resolved.message,
        "understood_as": resolved.understood_as,
    }


@app.post("/api/resolve-cloth")
def api_resolve_cloth(body: ResolveClothBody):
    model = get_model()
    known = {r.cloth for r in model.recipes if r.cloth}
    resolved = resolve_cloth(body.text, shade_value=body.shade_value, known_cloths=known)
    return {
        "input_text": resolved.input_text,
        "cloth_id": resolved.cloth_id,
        "label": resolved.label,
        "hex": resolved.hex,
        "gujarati": resolved.gujarati,
        "shade": resolved.shade,
        "shade_value": resolved.shade_value,
        "confidence": resolved.confidence,
        "message": resolved.message,
        "understood_as": resolved.understood_as,
    }


# phash Hamming distance: 0–4 ≈ same / near-identical photo of that design
EXACT_DESIGN_DISTANCE = 4
# still feed ranking with reasonably close gallery hits
USEFUL_SIMILAR_DISTANCE = 18


def _similar_payload(matches: list) -> list[dict]:
    out = []
    for item, dist in matches:
        if not item.design_no:
            continue
        thumb = ""
        try:
            p = Path(item.abs_path)
            if p.exists():
                thumb = f"/api/gallery/image?path={item.rel_path}"
        except Exception:
            thumb = ""
        out.append(
            {
                "design_no": item.design_no,
                "part": item.part,
                "path": item.rel_path,
                "distance": dist,
                "exact": int(dist) <= EXACT_DESIGN_DISTANCE,
                "useful": int(dist) <= USEFUL_SIMILAR_DISTANCE,
                "thumb_url": thumb,
            }
        )
    return out


def _exact_design_payload(matches: list, model: LiteRecommender) -> dict | None:
    """If gallery hit is near-identical, return that design + full past recipe history."""
    exact_hits = [(item, dist) for item, dist in matches if item.design_no and int(dist) <= EXACT_DESIGN_DISTANCE]
    if not exact_hits:
        return None
    # closest first; if tie, prefer design with more history
    exact_hits.sort(key=lambda x: (x[1], -len(model.by_design.get(x[0].design_no, []))))
    best_item, best_dist = exact_hits[0]
    dno = best_item.design_no
    history = model.design_history(dno)
    cloths = sorted({h["cloth"] for h in history if h.get("cloth")})
    return {
        "design_no": dno,
        "part": best_item.part,
        "distance": int(best_dist),
        "is_exact": True,
        "message": (
            f"Exact same design found: #{dno}"
            + (f" ({best_item.part})" if best_item.part else "")
            + f" — {len(history)} past recipe(s) in your book"
        ),
        "past_count": len(history),
        "cloths_used": cloths,
        "past_recipes": [_with_chips(h) for h in history],
    }


def _with_chips(row: dict) -> dict:
    needles = row.get("needles") or [row.get(f"n{i}", "") for i in range(1, 6)]
    tikli_n = row.get("tikli_needle")
    try:
        tikli_n = int(tikli_n) if tikli_n else None
    except (TypeError, ValueError):
        tikli_n = None
    out = dict(row)
    out["chips"] = enrich_recipe_needles(list(needles), tikli_n)
    return out


@app.post("/api/gallery/similar")
async def gallery_similar(
    path: str = Form(""),
    top_k: int = Form(8),
    file: UploadFile | None = File(None),
):
    gallery = get_gallery()
    if gallery is None:
        return {"source": "none", "similar": [], "exact_design": None}
    matches: list = []
    source = "none"
    if file is not None and file.filename:
        raw = await file.read()
        img = Image.open(io.BytesIO(raw))
        matches = gallery.find_similar(image=img, top_k=max(int(top_k) or 8, 12))
        source = "upload"
    elif path:
        try:
            full = gallery.resolve(path)
        except Exception as exc:
            raise HTTPException(404, str(exc)) from exc
        matches = gallery.find_similar(image_path=full, top_k=max(int(top_k) or 8, 12), exclude_rel=path)
        source = path
    else:
        raise HTTPException(400, "Provide upload file")

    model = get_model()
    exact = _exact_design_payload(matches, model)
    similar = _similar_payload(matches[:8])
    # Always prefer useful (close) design numbers for ranking; fall back to top hits
    useful_nos = []
    for row in similar:
        if row.get("useful") or row.get("exact"):
            useful_nos.append(row["design_no"])
    if not useful_nos:
        useful_nos = [row["design_no"] for row in similar if row.get("design_no")]
    if exact and exact.get("design_no"):
        useful_nos = [exact["design_no"]] + [n for n in useful_nos if n != exact["design_no"]]
    return {
        "source": source,
        "similar": similar,
        "exact_design": exact,
        "matched_design_nos": list(dict.fromkeys(useful_nos))[:8],
    }


@app.get("/api/design-history")
def design_history(design_no: str):
    model = get_model()
    dno = (design_no or "").strip()
    history = model.design_history(dno)
    return {
        "design_no": dno,
        "past_count": len(history),
        "cloths_used": sorted({h["cloth"] for h in history if h.get("cloth")}),
        "past_recipes": [_with_chips(h) for h in history],
    }


@app.get("/api/gallery/image")
def gallery_image(path: str):
    gallery = get_gallery()
    if gallery is None:
        raise HTTPException(404, "Gallery unavailable")
    try:
        full = gallery.resolve(path)
    except Exception as exc:
        raise HTTPException(404, str(exc)) from exc
    return FileResponse(full)


@app.post("/api/recommend-needle")
def recommend_needle(body: NeedleStepBody):
    model = get_model()
    similar_nos = list(body.similar_design_nos or [])
    parts = body.parts
    known = {r.cloth for r in model.recipes if r.cloth}

    # Resolve typed / shaded cloth when raw text provided
    cloth = (body.cloth or "").strip()
    cloth_info = None
    raw = (body.cloth_raw or body.cloth or "").strip()
    if raw:
        resolved = resolve_cloth(raw, shade_value=body.shade_value, known_cloths=known)
        if resolved.cloth_id:
            cloth = resolved.cloth_id
            cloth_info = {
                "cloth_id": resolved.cloth_id,
                "label": resolved.label,
                "message": resolved.message,
                "shade": resolved.shade,
                "understood_as": resolved.understood_as,
            }

    locked: dict[int, str] = {}
    for k, v in (body.locked_needles or {}).items():
        try:
            n = int(k)
        except ValueError:
            continue
        if v and v.strip():
            locked[n] = v.strip()

    req = PredictRequest(
        cloth=cloth,
        design_no=(body.design_no or "").strip(),
        parts=parts.strip(),
        thread_count=body.thread_count or 0,
        similar_design_nos=similar_nos,
    )
    options = model.recommend_needle(req, target_needle=body.target_needle, locked_needles=locked)
    options = enrich_options_with_thread_colour(options)
    help_pct = model.design_help_percent(
        req, target_needle=body.target_needle, locked_needles=locked, options_with=options
    )
    tikli_info = model.suggest_tikli(req)

    has_photo = bool(body.has_design_photo)
    has_match = bool(similar_nos or (body.design_no or "").strip())
    if has_match and help_pct > 0:
        note = f"Design photo / matched designs improve colour choosing by about {help_pct}%"
    elif has_photo and not has_match:
        note = "Design photo uploaded, but no close match in your past designs — cloth colour only (0%)"
        help_pct = 0
    elif has_photo and has_match and help_pct == 0:
        note = "Design matched, but past recipes did not change these needle picks (low design help)"
    else:
        note = "No design photo — suggestions from cloth colour only (0%)"

    return {
        "target_needle": body.target_needle,
        "locked_needles": {str(k): v for k, v in sorted(locked.items())},
        "count": len(options),
        "options": options,
        "cloth": cloth_info or {"cloth_id": cloth, "label": cloth, "message": "", "shade": "mid"},
        "design_help_percent": help_pct,
        "design_help_note": note,
        "similar_used": similar_nos,
        "design_no_used": (body.design_no or "").strip(),
        "design_accuracy_boost": help_pct,
        "tikli": tikli_info,
    }


@app.post("/api/recommend-recipes")
def recommend_recipes(body: RecipesBody):
    """Five full dhaga strips + six extra colour chips. Parts (neck etc.) are ignored."""
    model = get_model()
    similar_nos = list(body.similar_design_nos or [])
    known = {r.cloth for r in model.recipes if r.cloth}

    cloth = (body.cloth or "").strip()
    cloth_info = None
    raw = (body.cloth_raw or body.cloth or "").strip()
    if raw:
        resolved = resolve_cloth(raw, shade_value=body.shade_value, known_cloths=known)
        if resolved.cloth_id:
            cloth = resolved.cloth_id
            cloth_info = {
                "cloth_id": resolved.cloth_id,
                "label": resolved.label,
                "message": resolved.message,
                "shade": resolved.shade,
                "understood_as": resolved.understood_as,
                "hex": resolved.hex,
                "gujarati": resolved.gujarati,
            }

    req = PredictRequest(
        cloth=cloth,
        design_no=(body.design_no or "").strip(),
        parts="",
        thread_count=body.thread_count or 0,
        similar_design_nos=similar_nos,
    )
    recipes, colours = model.recommend_recipes(req, top_n=5, colour_n=6)
    for rec in recipes:
        rec["chips"] = enrich_recipe_needles(rec.get("needles") or [], rec.get("tikli_needle"))
    colours = enrich_options_with_thread_colour(colours)
    for i, c in enumerate(colours, start=1):
        c["rank"] = i

    help_pct = model.design_help_percent(req, target_needle=1, locked_needles={}, options_with=None)
    tikli_info = model.suggest_tikli(req)

    has_photo = bool(body.has_design_photo)
    has_match = bool(similar_nos or (body.design_no or "").strip())
    if has_match and help_pct > 0:
        note = f"Design photo / matched designs improve colour choosing by about {help_pct}%"
    elif has_photo and not has_match:
        note = "Design photo uploaded, but no close match in your past designs — cloth colour only (0%)"
        help_pct = 0
    elif has_photo and has_match and help_pct == 0:
        note = "Design matched, but past recipes did not change these picks (low design help)"
    else:
        note = "No design photo — suggestions from cloth colour only (0%)"

    return {
        "count": len(recipes),
        "recipes": recipes,
        "colour_options": colours,
        "cloth": cloth_info or {"cloth_id": cloth, "label": cloth, "message": "", "shade": "mid"},
        "design_help_percent": help_pct,
        "design_help_note": note,
        "similar_used": similar_nos,
        "design_no_used": (body.design_no or "").strip(),
        "tikli": tikli_info,
    }


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
