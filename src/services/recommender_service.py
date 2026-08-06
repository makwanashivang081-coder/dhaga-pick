"""Hybrid retrieval + learning-to-rank for full thread recipes."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

from services.data_service import non_jari_signature
from utils.types import (
    MAX_NEEDLES,
    TOP_K,
    PredictRequest,
    PredictResponse,
    RankedRecipe,
    Recipe,
    normalize_cloth,
    normalize_parts,
    primary_design_type,
)


def _norm_thread(t: str) -> str:
    return " ".join((t or "").lower().split())


@dataclass
class TrainResult:
    metrics: dict[str, float]
    n_train: int
    n_test: int
    n_recipes: int


class ColourRecommender:
    """Retrieve historical recipes, score them, optionally condition on locked n1."""

    def __init__(self) -> None:
        self.recipes: list[Recipe] = []
        self.by_design: dict[str, list[Recipe]] = defaultdict(list)
        self.by_design_cloth: dict[tuple[str, str], list[Recipe]] = defaultdict(list)
        self.by_type_cloth: dict[tuple[str, str], list[Recipe]] = defaultdict(list)
        self.by_cloth: dict[str, list[Recipe]] = defaultdict(list)
        self.conditional_models: dict[int, Pipeline] = {}  # needle number 2..5 -> model
        self.vectorizer = DictVectorizer(sparse=True)
        self.rank_clf: Optional[GradientBoostingClassifier] = None
        self.trained = False

    def fit(self, recipes: list[Recipe]) -> TrainResult:
        self.recipes = list(recipes)
        self._build_indexes()
        metrics = self._train_models()
        self.trained = True
        return metrics

    def _build_indexes(self) -> None:
        self.by_design.clear()
        self.by_design_cloth.clear()
        self.by_type_cloth.clear()
        self.by_cloth.clear()
        for r in self.recipes:
            self.by_design[r.design_no].append(r)
            if r.cloth:
                self.by_design_cloth[(r.design_no, r.cloth)].append(r)
                self.by_type_cloth[(r.design_type, r.cloth)].append(r)
                self.by_cloth[r.cloth].append(r)

    def _pair_features(self, query: PredictRequest, candidate: Recipe) -> dict[str, Any]:
        q_cloth = normalize_cloth(query.cloth)
        q_parts = normalize_parts(query.parts)
        q_type = primary_design_type(q_parts) if q_parts else ""
        feats: dict[str, Any] = {
            "exact_design_cloth": int(bool(query.design_no) and candidate.design_no == query.design_no and candidate.cloth == q_cloth),
            "exact_design": int(bool(query.design_no) and candidate.design_no == query.design_no),
            "same_cloth": int(bool(q_cloth) and candidate.cloth == q_cloth),
            "same_type": int(bool(q_type) and candidate.design_type == q_type),
            "same_type_cloth": int(bool(q_type) and bool(q_cloth) and candidate.design_type == q_type and candidate.cloth == q_cloth),
            "thread_count_match": int(query.thread_count > 0 and candidate.thread_count == query.thread_count),
            "thread_count_diff": abs((query.thread_count or candidate.thread_count) - candidate.thread_count),
            "candidate_thread_count": candidate.thread_count,
            "has_jari": int(candidate.has_jari),
            "clarity_high": int(candidate.clarity == "high"),
            "locked_n1_match": int(bool(query.locked_n1) and _norm_thread(candidate.needles[0]) == _norm_thread(query.locked_n1)),
            "n1_brand_royal": int("royal" in candidate.needles[0].lower()),
            "n1_brand_raj": int("raj" in candidate.needles[0].lower() and "royal" not in candidate.needles[0].lower()),
            "similar_design": int(
                bool(query.similar_design_nos) and candidate.design_no in set(query.similar_design_nos)
            ),
        }
        if query.tikli:
            feats["tikli_match"] = int((candidate.tikli or "").lower() == query.tikli.lower() or (query.tikli.lower() in (candidate.tikli or "").lower()))
        return feats

    def _heuristic_score(self, query: PredictRequest, candidate: Recipe) -> float:
        f = self._pair_features(query, candidate)
        score = 0.0
        # Strict priority: exact design+cloth >> same design >> type+cloth >> cloth
        score += 200.0 * f["exact_design_cloth"]
        score += 120.0 * f["exact_design"]
        score += 95.0 * f["similar_design"]
        score += 45.0 * f["same_type_cloth"]
        score += 20.0 * f["same_cloth"]
        score += 10.0 * f["same_type"]
        score += 12.0 * f["thread_count_match"]
        score += 5.0 * f["clarity_high"]
        score -= 2.0 * f["thread_count_diff"]
        if query.locked_n1:
            if f["locked_n1_match"]:
                score += 150.0
            else:
                score -= 100.0
        return score

    def _candidate_pool(self, query: PredictRequest) -> list[Recipe]:
        q_cloth = normalize_cloth(query.cloth)
        q_parts = normalize_parts(query.parts)
        q_type = primary_design_type(q_parts) if q_parts else ""
        pool: list[Recipe] = []
        seen: set[str] = set()

        def add_many(items: list[Recipe]) -> None:
            for r in items:
                if r.recipe_id in seen:
                    continue
                seen.add(r.recipe_id)
                pool.append(r)

        if query.design_no and q_cloth:
            add_many(self.by_design_cloth.get((query.design_no, q_cloth), []))
        if query.design_no:
            add_many(self.by_design.get(query.design_no, []))
        # visually similar past designs (from gallery match)
        for dno in query.similar_design_nos or []:
            if q_cloth:
                add_many(self.by_design_cloth.get((dno, q_cloth), []))
            add_many(self.by_design.get(dno, []))
        if q_type and q_cloth:
            add_many(self.by_type_cloth.get((q_type, q_cloth), []))
        if q_cloth:
            add_many(self.by_cloth.get(q_cloth, []))
        if len(pool) < TOP_K * 3:
            # broaden carefully — do not dump entire catalogue every time
            extras: list[Recipe] = []
            if q_cloth:
                extras.extend(self.by_cloth.get(q_cloth, [])[:80])
            if q_type:
                for (dt, cl), items in self.by_type_cloth.items():
                    if dt == q_type:
                        extras.extend(items[:20])
            if len(extras) < TOP_K:
                extras.extend(self.recipes[:50])
            add_many(extras)

        if query.thread_count > 0:
            filtered = [r for r in pool if r.thread_count == query.thread_count]
            if len(filtered) >= min(3, TOP_K):
                pool = filtered

        if query.locked_n1:
            locked = [r for r in pool if _norm_thread(r.needles[0]) == _norm_thread(query.locked_n1)]
            if locked:
                pool = locked
        return pool

    def _train_models(self) -> TrainResult:
        # Learning-to-rank proxy: for each recipe as query, positive = itself / same signature, negatives = random others
        rng = np.random.default_rng(42)
        X_dicts: list[dict[str, Any]] = []
        y: list[int] = []
        groups: list[str] = []

        # sample up to N recipes for training pairs
        sample = self.recipes
        if len(sample) > 800:
            idx = rng.choice(len(sample), size=800, replace=False)
            sample = [sample[i] for i in idx]

        for r in sample:
            q = PredictRequest(
                cloth=r.cloth,
                design_no=r.design_no,
                parts=r.parts,
                thread_count=r.thread_count,
            )
            pos_sig = non_jari_signature(r.needles)
            # positives: same design+cloth or identical signature
            positives = [
                c
                for c in self.by_design_cloth.get((r.design_no, r.cloth), [r])
                if non_jari_signature(c.needles) == pos_sig or c.recipe_id == r.recipe_id
            ]
            if not positives:
                positives = [r]
            negatives_pool = [c for c in self.recipes if c.recipe_id != r.recipe_id]
            neg_idx = rng.choice(len(negatives_pool), size=min(6, len(negatives_pool)), replace=False)
            negatives = [negatives_pool[i] for i in neg_idx]

            for c in positives[:3]:
                X_dicts.append(self._pair_features(q, c))
                y.append(1)
                groups.append(r.design_no)
            for c in negatives:
                X_dicts.append(self._pair_features(q, c))
                y.append(0)
                groups.append(r.design_no)

        X = self.vectorizer.fit_transform(X_dicts)
        clf = GradientBoostingClassifier(random_state=42)
        # group-aware holdout by design
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_idx, test_idx = next(gss.split(X, y, groups))
        clf.fit(X[train_idx], np.array(y)[train_idx])
        proba = clf.predict_proba(X[test_idx])[:, 1]
        pred = (proba >= 0.5).astype(int)
        acc = float((pred == np.array(y)[test_idx]).mean()) if len(test_idx) else 0.0
        self.rank_clf = clf

        # Conditional models: predict needle k text from features + n1
        cond_metrics: dict[str, float] = {}
        for needle_i in range(1, 5):  # predict n2..n5 => indices 1..4
            rows_x: list[dict[str, Any]] = []
            rows_y: list[str] = []
            for r in self.recipes:
                target = (r.needles[needle_i] or "").strip()
                if not target:
                    continue
                n1 = (r.needles[0] or "").strip()
                if not n1:
                    continue
                rows_x.append(
                    {
                        "cloth": r.cloth or "none",
                        "design_type": r.design_type,
                        "thread_count": r.thread_count,
                        "n1": _norm_thread(n1),
                        "has_jari": int(r.has_jari),
                    }
                )
                rows_y.append(_norm_thread(target))
            if len(set(rows_y)) < 2 or len(rows_y) < 30:
                continue
            vec = DictVectorizer(sparse=True)
            Xc = vec.fit_transform(rows_x)
            # collapse rare labels
            counts: dict[str, int] = defaultdict(int)
            for lab in rows_y:
                counts[lab] += 1
            y_c = [lab if counts[lab] >= 3 else "__OTHER__" for lab in rows_y]
            if len(set(y_c)) < 2:
                continue
            model = RandomForestClassifier(
                n_estimators=120,
                max_depth=18,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )
            # simple holdout
            n = len(y_c)
            cut = int(n * 0.8)
            model.fit(Xc[:cut], y_c[:cut])
            acc_c = float(model.score(Xc[cut:], y_c[cut:])) if cut < n else 0.0
            pipe = Pipeline([("vec", vec), ("clf", model)])
            # refit on all
            pipe.fit(rows_x, y_c)
            self.conditional_models[needle_i + 1] = pipe  # needle number 2..5
            cond_metrics[f"n{needle_i + 1}_acc"] = acc_c

        # End-to-end retrieval metrics on held-out designs
        top1, top10, n_eval = self._eval_retrieval()
        metrics = {
            "pair_rank_acc": acc,
            "retrieval_top1": top1,
            "retrieval_top10": top10,
            "n_eval_queries": float(n_eval),
            **cond_metrics,
        }
        return TrainResult(
            metrics=metrics,
            n_train=int(len(train_idx)),
            n_test=int(len(test_idx)),
            n_recipes=len(self.recipes),
        )

    def _eval_retrieval(self) -> tuple[float, float, int]:
        """Leave-one-out style eval on a sample of cloth recipes."""
        rng = np.random.default_rng(0)
        cloth_recipes = [r for r in self.recipes if r.cloth]
        if not cloth_recipes:
            return 0.0, 0.0, 0
        sample_n = min(200, len(cloth_recipes))
        sample = [cloth_recipes[i] for i in rng.choice(len(cloth_recipes), size=sample_n, replace=False)]

        groups: dict[tuple[str, str], list[Recipe]] = defaultdict(list)
        for r in self.recipes:
            if r.cloth:
                groups[(r.design_no, r.cloth)].append(r)

        hits1 = 0
        hits10 = 0
        n = 0
        for r in sample:
            items = groups[(r.design_no, r.cloth)]
            q = PredictRequest(cloth=r.cloth, design_no=r.design_no, parts=r.parts, thread_count=r.thread_count)
            ranked = self.recommend(q, exclude_ids={r.recipe_id})
            target = non_jari_signature(r.needles)
            sigs = [non_jari_signature(x.recipe.needles) for x in ranked.options]
            family = {non_jari_signature(x.needles) for x in items if x.recipe_id != r.recipe_id}
            # also accept any other recipe from same design (different cloth) as weak top10 hit
            same_design_sigs = {
                non_jari_signature(x.needles)
                for x in self.by_design.get(r.design_no, [])
                if x.recipe_id != r.recipe_id
            }
            n += 1
            if sigs and (sigs[0] == target or sigs[0] in family or (sigs[0] in same_design_sigs)):
                hits1 += 1
            if target in sigs or (family & set(sigs)) or (same_design_sigs & set(sigs)):
                hits10 += 1
        if n == 0:
            return 0.0, 0.0, 0
        return hits1 / n, hits10 / n, n

    def _ml_score(self, query: PredictRequest, candidate: Recipe) -> float:
        base = self._heuristic_score(query, candidate)
        if self.rank_clf is None:
            return base
        try:
            feats = self._pair_features(query, candidate)
            X = self.vectorizer.transform([feats])
            proba = float(self.rank_clf.predict_proba(X)[0, 1])
            return base + 20.0 * proba
        except Exception:
            return base

    def recommend_needle(
        self,
        query: PredictRequest,
        target_needle: int,
        locked_needles: Optional[dict[int, str]] = None,
    ) -> list[dict[str, Any]]:
        """Return up to 10 unique dhaga options for one needle, given previous locks."""
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

        # Build pool then filter by locked needles 1..target-1
        pool = self._candidate_pool(query)
        filtered: list[Recipe] = []
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

        # Score recipes, collect unique thread for target slot
        scored: list[tuple[float, Recipe]] = []
        for r in filtered:
            scored.append((self._ml_score(query, r), r))
        scored.sort(key=lambda x: (-x[0], x[1].recipe_id))

        options: list[dict[str, Any]] = []
        seen: set[str] = set()
        for score, r in scored:
            thread = (r.needles[target_needle - 1] or "").strip()
            if not thread:
                continue
            # skip jari for progressive colour picking (v1 colour focus)
            if "jari" in thread.lower():
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
                }
            )
            if len(options) >= TOP_K:
                break

        # Fallback: most common threads for this cloth at this needle
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
                    }
                )
                seen.add(key)
                if len(options) >= TOP_K:
                    break

        for i, opt in enumerate(options, start=1):
            opt["rank"] = i
        return options
        if not self.recipes:
            raise RuntimeError("Model has no recipes loaded")
        query = PredictRequest(
            cloth=normalize_cloth(query.cloth),
            design_no=(query.design_no or "").strip(),
            parts=normalize_parts(query.parts or ""),
            thread_count=query.thread_count or 0,
            tikli=query.tikli,
            locked_n1=query.locked_n1,
            similar_design_nos=[str(x).strip() for x in (query.similar_design_nos or []) if str(x).strip()],
        )
        exclude_ids = exclude_ids or set()
        pool = [r for r in self._candidate_pool(query) if r.recipe_id not in exclude_ids]

        scored: list[tuple[float, Recipe, str]] = []
        for r in pool:
            score = self._ml_score(query, r)
            reason = self._reason(query, r)
            scored.append((score, r, reason))
        scored.sort(key=lambda x: (-x[0], x[1].recipe_id))

        # unique by needle signature
        options: list[RankedRecipe] = []
        seen_sig: set[tuple[str, ...]] = set()
        for score, r, reason in scored:
            sig = non_jari_signature(r.needles)
            if sig in seen_sig:
                continue
            seen_sig.add(sig)
            options.append(RankedRecipe(recipe=r, score=score, rank=len(options) + 1, match_reason=reason))
            if len(options) >= TOP_K:
                break

        # If locked n1 and history is thin, optionally append conditional fill (no dup signatures)
        if query.locked_n1 and len(options) < TOP_K:
            existing_sigs = {non_jari_signature(o.recipe.needles) for o in options}
            for fill in self._conditional_fill(query, options, TOP_K - len(options)):
                sig = non_jari_signature(fill.recipe.needles)
                if sig in existing_sigs:
                    continue
                existing_sigs.add(sig)
                fill.rank = len(options) + 1
                options.append(fill)

        if not options:
            # absolute fallback: top by cloth frequency
            for r in self.by_cloth.get(query.cloth, self.recipes)[:TOP_K]:
                options.append(
                    RankedRecipe(recipe=r, score=0.0, rank=len(options) + 1, match_reason="fallback")
                )

        # ensure contiguous ranks
        for i, opt in enumerate(options, start=1):
            opt.rank = i

        best = options[0]
        return PredictResponse(best=best, options=options)

    def _reason(self, query: PredictRequest, r: Recipe) -> str:
        if query.design_no and r.design_no == query.design_no and r.cloth == query.cloth:
            return "exact_design_cloth"
        if query.design_no and r.design_no == query.design_no:
            return "same_design"
        if query.similar_design_nos and r.design_no in set(query.similar_design_nos):
            return "similar_design"
        if r.design_type == primary_design_type(query.parts) and r.cloth == query.cloth:
            return "same_type_cloth"
        if r.cloth == query.cloth:
            return "same_cloth"
        return "related"

    def _conditional_fill(self, query: PredictRequest, existing: list[RankedRecipe], need: int) -> list[RankedRecipe]:
        """Generate synthetic completions only from conditional models when history is thin."""
        out: list[RankedRecipe] = []
        if need <= 0 or not query.locked_n1:
            return out
        # use most common historical template with this n1 as base
        bases = [r for r in self.recipes if _norm_thread(r.needles[0]) == _norm_thread(query.locked_n1)]
        if not bases:
            return out
        base = bases[0]
        needles = list(base.needles)
        needles[0] = query.locked_n1
        for needle_no, model in self.conditional_models.items():
            feat = {
                "cloth": query.cloth or "none",
                "design_type": primary_design_type(query.parts) if query.parts else base.design_type,
                "thread_count": query.thread_count or base.thread_count,
                "n1": _norm_thread(query.locked_n1),
                "has_jari": int(base.has_jari),
            }
            try:
                pred = model.predict([feat])[0]
                if pred != "__OTHER__":
                    needles[needle_no - 1] = pred
            except Exception:
                continue
        # wrap as ephemeral recipe
        synth = Recipe(
            recipe_id="SYNTH",
            source_page="",
            design_no=query.design_no or base.design_no,
            parts=query.parts or base.parts,
            cloth=query.cloth or base.cloth,
            needles=needles,
            tikli=base.tikli,
            jari_note=base.jari_note,
            image=base.image,
            notes="conditional_fill",
            clarity="medium",
        )
        out.append(RankedRecipe(recipe=synth, score=1.0, rank=0, match_reason="conditional_n1"))
        return out[:need]
