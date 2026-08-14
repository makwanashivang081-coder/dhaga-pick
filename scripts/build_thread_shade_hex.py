"""Sample official Royal shade-card PNGs → models/thread_shade_hex.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

ROOT = Path(__file__).resolve().parents[1]
CARD_DIR = ROOT / "data" / "_shade_cards"
OUT = ROOT / "models" / "thread_shade_hex.json"

CODE_RE = re.compile(r"^(\d{1,4})([A-Za-z]{0,3})$")


def normalize_key(num: str, mods: str) -> str:
    mods = (mods or "").upper().replace(" ", "")
    if not mods:
        return num
    return f"{num}.{mods}"


def sample_swatch(arr: np.ndarray, x: int, y: int, ww: int, hh: int):
    h, w = arr.shape[:2]
    best = None
    for dx0, dx1 in ((ww + 10, ww + 100), (ww + 25, ww + 150), (ww + 50, ww + 170)):
        sx0 = min(w - 1, x + dx0)
        sx1 = min(w, x + dx1)
        sy0 = max(0, y - max(6, hh))
        sy1 = min(h, y + max(hh * 2, 28))
        patch = arr[sy0:sy1, sx0:sx1]
        if patch.size < 80:
            continue
        rgb = patch.reshape(-1, 3).astype(np.float32)
        lum = rgb.mean(axis=1)
        chroma = rgb.max(axis=1) - rgb.min(axis=1)
        mask = (lum > 35) & (lum < 238) & (chroma > 6)
        if int(mask.sum()) < 25:
            mask = (lum > 28) & (lum < 245)
        if int(mask.sum()) < 15:
            continue
        sel = rgb[mask]
        p65 = np.percentile(sel, 65, axis=0)
        med = np.median(sel, axis=0)
        col = 0.6 * p65 + 0.4 * med
        rgb_t = tuple(int(round(float(c))) for c in col)
        score = int(mask.sum()) + int(float(chroma[mask].mean()) * 2)
        if best is None or score > best[0]:
            best = (score, rgb_t)
    return None if best is None else best[1]


def extract_page(path: Path, scale_max: int = 2400) -> dict:
    im = Image.open(path).convert("RGB")
    w0, h0 = im.size
    scale = min(1.0, scale_max / max(w0, h0))
    im_ocr = im.resize((int(w0 * scale), int(h0 * scale))) if scale < 1 else im
    arr = np.array(im)
    data = pytesseract.image_to_data(
        im_ocr,
        output_type=pytesseract.Output.DICT,
        config="--psm 11",
    )
    found: dict[str, dict] = {}
    for i, txt in enumerate(data["text"]):
        t = (txt or "").strip().replace(" ", "").replace(".", "")
        m = CODE_RE.match(t)
        if not m:
            continue
        conf = float(data["conf"][i])
        if conf < 55:
            continue
        num, mods = m.group(1), m.group(2)
        if len(num) > 4:
            continue
        key = normalize_key(num, mods)
        x = int(data["left"][i] / scale)
        y = int(data["top"][i] / scale)
        ww = max(8, int(data["width"][i] / scale))
        hh = max(8, int(data["height"][i] / scale))
        rgb = sample_swatch(arr, x, y, ww, hh)
        if not rgb:
            continue
        hex_c = "#{:02x}{:02x}{:02x}".format(*rgb)
        prev = found.get(key)
        if prev is None or conf > prev["conf"]:
            found[key] = {"hex": hex_c, "conf": conf, "src": path.name}
    return found


def main() -> None:
    pages = sorted(CARD_DIR.glob("vol1_hi_*.png")) + sorted(CARD_DIR.glob("vol8_hi_*.png"))
    merged: dict[str, dict] = {}
    for p in pages:
        print("page", p.name)
        found = extract_page(p)
        print(" ", len(found), "codes")
        for k, v in found.items():
            if k not in merged or v["conf"] > merged[k]["conf"]:
                merged[k] = v

    # Confirmed from inspected Vol.1 crops (prevent OCR-neighbour bleed).
    overrides = {
        "315": "#8b765e",
        "118": "#ded3b1",
        "118.L": "#e3dec4",
        "118.LL": "#e2e0cf",
        "8": "#dbd5cd",
        # 8.L was OCR-sampled from a neighbouring red strip; L/LL of 8 are lighter cream.
        "8.L": "#e8e4dc",
        "8.LL": "#f2efe8",
        "722": "#5aafbc",
        "65": "#f4b4b4",
    }
    for k, hx in overrides.items():
        merged[k] = {"hex": hx, "conf": 99.0, "src": "manual_verified_crop"}

    def sort_key(item: str) -> tuple:
        m = re.match(r"(\d+)(.*)", item)
        return (int(m.group(1)), m.group(2) if m else item)

    codes = {k: v["hex"] for k, v in sorted(merged.items(), key=lambda kv: sort_key(kv[0]))}
    payload = {
        "source": "Royal Embroidery Threads Viscose Vol.1 + Vol.8 E-catalog (sampled swatches)",
        "note": "Dots use official shade-card samples. Screen may differ slightly from physical cone. Unknown codes show no colour dot.",
        "brand_default": "royal",
        "codes": codes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("wrote", OUT, "count", len(codes))
    for c in ("315", "118", "722", "8", "105", "110", "190", "188", "741", "834"):
        print(c, codes.get(c))


if __name__ == "__main__":
    main()
