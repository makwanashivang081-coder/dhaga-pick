"""Gallery image index + visual similarity for design matching."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import json

import imagehash
from PIL import Image, ImageOps

GALLERY_EXTS = {".jpg", ".jpeg", ".bmp", ".png", ".webp"}


@dataclass
class GalleryItem:
    design_no: str
    part: str
    rel_path: str
    abs_path: str
    phash: str


class GalleryIndex:
    def __init__(self, root: Path, items: list[GalleryItem] | None = None) -> None:
        self.root = Path(root)
        self.items: list[GalleryItem] = items or []

    @classmethod
    def build(cls, root: Path) -> "GalleryIndex":
        root = Path(root)
        items: list[GalleryItem] = []
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in GALLERY_EXTS:
                continue
            if path.name.lower() in {".picasa.ini", "thumbs.db"}:
                continue
            design_no, part = _parse_name(path.stem)
            try:
                ph = _phash(path)
            except Exception:
                continue
            rel = str(path.relative_to(root)).replace("\\", "/")
            items.append(
                GalleryItem(
                    design_no=design_no,
                    part=part,
                    rel_path=rel,
                    abs_path=str(path),
                    phash=str(ph),
                )
            )
        items.sort(key=lambda x: (x.design_no, x.part, x.rel_path))
        return cls(root=root, items=items)

    def save(self, path: Path) -> None:
        path = Path(path)
        payload = {
            "root": str(self.root),
            "items": [
                {
                    "design_no": x.design_no,
                    "part": x.part,
                    "rel_path": x.rel_path,
                    "abs_path": x.abs_path,
                    "phash": x.phash,
                }
                for x in self.items
            ],
        }
        if path.suffix.lower() == ".json":
            path.write_text(json.dumps(payload), encoding="utf-8")
            return
        import joblib

        joblib.dump(payload, path)

    @classmethod
    def load(cls, path: Path) -> "GalleryIndex":
        path = Path(path)
        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            import joblib

            data = joblib.load(path)
        items = [GalleryItem(**row) for row in data["items"]]
        return cls(root=Path(data.get("root") or "."), items=items)

    def list_items(self, q: str = "", limit: int = 80, offset: int = 0) -> list[GalleryItem]:
        query = (q or "").strip().lower()
        rows = self.items
        if query:
            rows = [
                i
                for i in rows
                if query in i.design_no.lower()
                or query in i.part.lower()
                or query in i.rel_path.lower()
            ]
        return rows[offset : offset + limit]

    def find_similar(
        self,
        image_path: Optional[Path] = None,
        image: Optional[Image.Image] = None,
        top_k: int = 8,
        exclude_rel: str = "",
    ) -> list[tuple[GalleryItem, int]]:
        """Return [(item, hamming_distance), ...] lowest distance first."""
        if image is None:
            if image_path is None:
                raise ValueError("image_path or image required")
            query_hash = _phash(Path(image_path))
        else:
            query_hash = imagehash.phash(_prepare(image))

        scored: list[tuple[GalleryItem, int]] = []
        for item in self.items:
            if exclude_rel and item.rel_path.replace("\\", "/") == exclude_rel.replace("\\", "/"):
                continue
            dist = query_hash - imagehash.hex_to_hash(item.phash)
            scored.append((item, int(dist)))
        scored.sort(key=lambda x: (x[1], x[0].design_no))
        return scored[:top_k]

    def resolve(self, rel_path: str) -> Path:
        rel = rel_path.replace("\\", "/").lstrip("/")
        full = (self.root / rel).resolve()
        root = self.root.resolve()
        if root not in full.parents and full != root:
            # also allow if file is under root
            if not str(full).startswith(str(root)):
                raise ValueError("path outside gallery")
        if not full.exists() or not full.is_file():
            raise FileNotFoundError(rel_path)
        return full


def _parse_name(stem: str) -> tuple[str, str]:
    m = re.match(r"^(\d+)\s*(.*)$", stem.strip(), re.I)
    if not m:
        return "", stem.strip().lower()
    design_no = m.group(1)
    part = re.sub(r"\b(200|250|400|450|500)\b", "", m.group(2), flags=re.I)
    part = re.sub(r"\s+", " ", part).strip(" -_").lower()
    part = part.replace("nake", "neck").replace("nack", "neck").replace("boder", "border")
    return design_no, part


def _prepare(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    return img


def _phash(path: Path) -> imagehash.ImageHash:
    with Image.open(path) as im:
        return imagehash.phash(_prepare(im))
