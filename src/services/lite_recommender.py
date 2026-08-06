"""Lightweight recommender for Vercel — no sklearn at runtime."""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from utils.types import (
    MAX_NEEDLES,
    TOP_K,
    PredictRequest,
    normalize_cloth,
    normalize_parts,
    primary_design_type,
)
from utils.tikli import majority_tikli_needle, parse_tikli_needle, tikli_label


def _norm_thread(t: str) -> str:
    return " ".join((t or "").lower().split())


@dataclass
class LiteRecipe:
    recipe_id: str
    design_no: str
    parts: str
    cloth: str
    needles: list[str]
    design_type: str
    thread_count: int
    clarity: str
    tikli: str = ""
    tikli_needle: Optional[int] = None

    def __post_init__(self) -> None:
        if self.tikli_needle is None and self.tikli:
            self.tikli_needle = parse_tikli_needle(self.tikli, self.needles)


class LiteRecommender:
    def __init__(self, recipes: list[LiteRecipe]) -> None:
        self.recipes = recipes
        self.by_design: dict[str, list[LiteRecipe]] = defaultdict(list)
        self.by_design_cloth: dict[tuple[str, str], list[LiteRecipe]] = defaultdict(list)
        self.by_type_cloth: dict[tuple[str, str], list[LiteRecipe]] = defaultdict(list)
        self.by_cloth: dict[str, list[LiteRecipe]] = defaultdict(list)
        for r in recipes:
            self.by_design[r.design_no].append(r)
            if r.cloth:
                self.by_design_cloth[(r.design_no, r.cloth)].append(r)
                self.by_type_cloth[(r.design_type, r.cloth)].append(r)
                self.by_cloth[r.cloth].append(r)

    @classmethod
    def load(cls, path: Path) -> "LiteRecommender":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        recipes = []
        for row in data["recipes"]:
            recipes.append(
                LiteRecipe(
                    recipe_id=row.get("recipe_id", ""),
                    design_no=row.get("design_no", ""),
                    parts=row.get("parts", ""),
                    cloth=row.get("cloth", ""),
                    needles=list(row.get("needles") or []),
                    design_type=row.get("design_type", ""),
                    thread_count=int(row.get("thread_count") or 0),
                    clarity=row.get("clarity", ""),
                    tikli=row.get("tikli") or "",
                    tikli_needle=row.get("tikli_needle"),
                )
            )
        return cls(recipes)

    def _score(self, query: PredictRequest, r: LiteRecipe, locked: dict[int, str]) -> float:
        q_cloth = normalize_cloth(query.cloth)
        q_parts = normalize_parts(query.parts or "")
        q_type = primary_design_type(q_parts) if q_parts else ""
        score = 0.0
        if query.design_no and r.design_no == query.design_no and r.cloth == q_cloth:
            score += 200
        elif query.design_no and r.design_no == query.design_no:
            score += 120
        if query.similar_design_nos and r.design_no in set(query.similar_design_nos):
            score += 95
        if q_type and r.design_type == q_type and r.cloth == q_cloth:
            score += 45
        elif r.cloth == q_cloth:
            score += 20
        elif q_type and r.design_type == q_type:
            score += 10
        if query.thread_count and r.thread_count == query.thread_count:
            score += 12
        if r.clarity == "high":
            score += 5
        # reward matching already-chosen needles
        for n, thread in locked.items():
            if 1 <= n <= MAX_NEEDLES and _norm_thread(r.needles[n - 1]) == _norm_thread(thread):
                score += 80
            elif 1 <= n <= MAX_NEEDLES and (r.needles[n - 1] or "").strip():
                score -= 40
        return score

    def _reason(self, query: PredictRequest, r: LiteRecipe) -> str:
        q_cloth = normalize_cloth(query.cloth)
        q_parts = normalize_parts(query.parts or "")
        q_type = primary_design_type(q_parts) if q_parts else ""
        if query.design_no and r.design_no == query.design_no and r.cloth == q_cloth:
            return "exact_design_cloth"
        if query.design_no and r.design_no == query.design_no:
            return "same_design"
        if query.similar_design_nos and r.design_no in set(query.similar_design_nos):
            return "similar_design"
        if q_type and r.design_type == q_type and r.cloth == q_cloth:
            return "same_type_cloth"
        if r.cloth == q_cloth:
            return "same_cloth"
        return "related"

    def _pool(self, query: PredictRequest) -> list[LiteRecipe]:
        q_cloth = normalize_cloth(query.cloth)
        q_parts = normalize_parts(query.parts or "")
        q_type = primary_design_type(q_parts) if q_parts else ""
        pool: list[LiteRecipe] = []
        seen: set[str] = set()

        def add_many(items: list[LiteRecipe]) -> None:
            for r in items:
                if r.recipe_id in seen:
                    continue
                seen.add(r.recipe_id)
                pool.append(r)

        if query.design_no and q_cloth:
            add_many(self.by_design_cloth.get((query.design_no, q_cloth), []))
        if query.design_no:
            add_many(self.by_design.get(query.design_no, []))
        for dno in query.similar_design_nos or []:
            if q_cloth:
                add_many(self.by_design_cloth.get((dno, q_cloth), []))
            add_many(self.by_design.get(dno, []))
        if q_type and q_cloth:
            add_many(self.by_type_cloth.get((q_type, q_cloth), []))
        if q_cloth:
            add_many(self.by_cloth.get(q_cloth, [])[:120])
        if len(pool) < TOP_K:
            add_many(self.recipes[:80])
        return pool

    def recommend_needle(
        self,
        query: PredictRequest,
        target_needle: int,
        locked_needles: Optional[dict[int, str]] = None,
    ) -> list[dict[str, Any]]:
        if target_needle < 1 or target_needle > MAX_NEEDLES:
            raise ValueError("target_needle must be 1..5")
        locked_needles = locked_needles or {}
        query = PredictRequest(
            cloth=normalize_cloth(query.cloth),
            design_no=(query.design_no or "").strip(),
            parts=normalize_parts(query.parts or ""),
            thread_count=query.thread_count or 0,
            similar_design_nos=[str(x).strip() for x in (query.similar_design_nos or []) if str(x).strip()],
        )

        pool = self._pool(query)
        filtered: list[LiteRecipe] = []
        for r in pool:
            ok = True
            for n, thread in locked_needles.items():
                if n < 1 or n > MAX_NEEDLES:
                    continue
                if _norm_thread(r.needles[n - 1]) != _norm_thread(thread):
                    ok = False
                    break
            if ok:
                filtered.append(r)
        if not filtered:
            filtered = pool

        scored = sorted(
            ((self._score(query, r, locked_needles), r) for r in filtered),
            key=lambda x: (-x[0], x[1].recipe_id),
        )

        options: list[dict[str, Any]] = []
        seen: set[str] = set()
        for score, r in scored:
            thread = (r.needles[target_needle - 1] or "").strip()
            if not thread or "jari" in thread.lower():
                continue
            key = _norm_thread(thread)
            if key in seen:
                continue
            seen.add(key)
            options.append(
                {
                    "rank": len(options) + 1,
                    "thread": thread,
                    "score": round(float(score), 2),
                    "from_design": r.design_no,
                    "from_parts": r.parts,
                    "from_cloth": r.cloth,
                    "match_reason": self._reason(query, r),
                    "tikli": r.tikli or "",
                    "tikli_needle": r.tikli_needle,
                    "tikli_label": tikli_label(r.tikli_needle, bool(r.tikli or r.tikli_needle)),
                    "is_tikli_needle": bool(r.tikli_needle == target_needle),
                }
            )
            if len(options) >= TOP_K:
                break

        if len(options) < TOP_K:
            counts: dict[str, tuple[int, str]] = {}
            for r in self.by_cloth.get(query.cloth, self.recipes):
                thread = (r.needles[target_needle - 1] or "").strip()
                if not thread or "jari" in thread.lower():
                    continue
                key = _norm_thread(thread)
                if key in seen:
                    continue
                prev = counts.get(key)
                counts[key] = ((prev[0] + 1) if prev else 1, thread)
            for key, (cnt, thread) in sorted(counts.items(), key=lambda x: -x[1][0]):
                options.append(
                    {
                        "rank": len(options) + 1,
                        "thread": thread,
                        "score": float(cnt),
                        "from_design": "",
                        "from_parts": "",
                        "from_cloth": query.cloth,
                        "match_reason": "cloth_common",
                        "tikli": "",
                        "tikli_needle": None,
                        "tikli_label": "",
                        "is_tikli_needle": False,
                    }
                )
                seen.add(key)
                if len(options) >= TOP_K:
                    break

        for i, opt in enumerate(options, start=1):
            opt["rank"] = i
        return options

    def suggest_tikli(self, query: PredictRequest) -> dict[str, Any]:
        """Majority tikli needle from exact / similar / cloth-matched history."""
        q = PredictRequest(
            cloth=normalize_cloth(query.cloth),
            design_no=(query.design_no or "").strip(),
            parts=normalize_parts(query.parts or ""),
            thread_count=query.thread_count or 0,
            similar_design_nos=[str(x).strip() for x in (query.similar_design_nos or []) if str(x).strip()],
        )
        pool = self._pool(q)
        items = [(r.tikli, r.needles) for r in pool if (r.tikli or r.tikli_needle)]
        needle = majority_tikli_needle(items)
        # also count explicit tikli_needle fields
        if needle is None:
            votes = [r.tikli_needle for r in pool if r.tikli_needle]
            if votes:
                from collections import Counter

                needle = Counter(votes).most_common(1)[0][0]
        has = bool(items) or bool(needle)
        return {
            "has_tikli": has and needle is not None,
            "tikli_needle": needle,
            "tikli_label": tikli_label(needle, has),
            "from_recipes": len(items),
        }

    def design_history(self, design_no: str) -> list[dict[str, Any]]:
        """All past recipes for an exact design number (every cloth / part seen)."""
        dno = (design_no or "").strip()
        if not dno:
            return []
        rows = self.by_design.get(dno) or []
        out: list[dict[str, Any]] = []
        for r in rows:
            needles = [n for n in r.needles if (n or "").strip()]
            out.append(
                {
                    "recipe_id": r.recipe_id,
                    "design_no": r.design_no,
                    "parts": r.parts,
                    "cloth": r.cloth,
                    "needles": needles,
                    "n1": r.needles[0] if len(r.needles) > 0 else "",
                    "n2": r.needles[1] if len(r.needles) > 1 else "",
                    "n3": r.needles[2] if len(r.needles) > 2 else "",
                    "n4": r.needles[3] if len(r.needles) > 3 else "",
                    "n5": r.needles[4] if len(r.needles) > 4 else "",
                    "thread_count": r.thread_count,
                    "clarity": r.clarity,
                    "tikli": r.tikli or "",
                    "tikli_needle": r.tikli_needle,
                    "tikli_label": tikli_label(r.tikli_needle, bool(r.tikli or r.tikli_needle)),
                }
            )
        # cloth then parts for dad-friendly scan
        out.sort(key=lambda x: ((x.get("cloth") or ""), (x.get("parts") or ""), x.get("recipe_id") or ""))
        return out

    def design_help_percent(
        self,
        query: PredictRequest,
        target_needle: int,
        locked_needles: Optional[dict[int, str]] = None,
        options_with: Optional[list[dict[str, Any]]] = None,
    ) -> int:
        """How much the design photo / matched design numbers guide the top-10 (0–100)."""
        similar = [str(x).strip() for x in (query.similar_design_nos or []) if str(x).strip()]
        exact = (query.design_no or "").strip()
        design_ctx = list(dict.fromkeys(([exact] if exact else []) + similar))
        if not design_ctx:
            return 0

        locked_needles = locked_needles or {}
        with_opts = options_with
        if with_opts is None:
            with_opts = self.recommend_needle(query, target_needle, locked_needles)

        # Fair baseline: cloth/parts only — no design photo / design number
        without_query = PredictRequest(
            cloth=query.cloth,
            design_no="",
            parts=query.parts or "",
            thread_count=query.thread_count or 0,
            similar_design_nos=[],
        )
        without_opts = self.recommend_needle(without_query, target_needle, locked_needles)

        with_threads = [(_norm_thread(o.get("thread", "")), o) for o in with_opts]
        without_set = {_norm_thread(o.get("thread", "")) for o in without_opts}
        design_set = set(design_ctx)

        if not with_threads:
            # Matched a design number but no needle options — still some help signal
            has_hist = any(self.by_design.get(d) for d in design_ctx)
            return 18 if has_hist else 8

        changed = sum(1 for t, _ in with_threads if t and t not in without_set)
        change_pct = 100.0 * changed / len(with_threads)

        design_hits = sum(
            1
            for _, o in with_threads
            if o.get("match_reason") in {"similar_design", "exact_design_cloth", "same_design"}
            or (o.get("from_design") or "") in design_set
        )
        hit_pct = 100.0 * design_hits / len(with_threads)

        top_with = float(with_opts[0].get("score") or 0) if with_opts else 0.0
        top_without = float(without_opts[0].get("score") or 0) if without_opts else 0.0
        if top_without > 0:
            lift_pct = max(0.0, min(100.0, 100.0 * (top_with - top_without) / max(top_without, 1e-6)))
        else:
            lift_pct = 45.0 if top_with > 0 else 0.0

        # History coverage: do we actually have recipes for matched designs?
        hist_n = sum(len(self.by_design.get(d) or []) for d in design_ctx)
        hist_pct = min(100.0, 15.0 * hist_n)  # up to ~100 if many past rows

        blended = 0.35 * change_pct + 0.30 * hit_pct + 0.20 * lift_pct + 0.15 * hist_pct

        # Floors so a real gallery match never reads as "0% / cloth only"
        if exact:
            blended = max(blended, 40.0)
        elif similar:
            blended = max(blended, 28.0 if hist_n else 16.0)
        if design_hits or changed or hist_n:
            blended = max(blended, 22.0)

        return int(round(min(100.0, blended)))
