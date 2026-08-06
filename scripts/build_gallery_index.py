"""Build perceptual-hash index for Jeetubhai design gallery."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from services.gallery_service import GalleryIndex


def main() -> None:
    gallery_root = ROOT / "Jeetubhai Images"
    out = ROOT / "models" / "gallery_index.joblib"
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"indexing {gallery_root} ...")
    index = GalleryIndex.build(gallery_root)
    index.save(out)
    print(f"indexed {len(index.items)} images -> {out}")
    if index.items:
        sample = index.items[0]
        sims = index.find_similar(image_path=Path(sample.abs_path), top_k=5, exclude_rel=sample.rel_path)
        print("sample similar to", sample.rel_path)
        for item, dist in sims:
            print(f"  d={dist:2d}  {item.design_no}  {item.part}  {item.rel_path}")


if __name__ == "__main__":
    main()
