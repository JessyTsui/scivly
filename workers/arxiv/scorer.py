from __future__ import annotations

import math
import re
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from typing import Any

from .models import ArxivPaper, ComponentScores, ScoringProfile, ScoringResult

try:
    from workers.common.config import (
        load_default_triage_profile,
        load_institution_priors,
        load_lab_priors,
    )
except ModuleNotFoundError:  # pragma: no cover - pytest package resolution fallback
    from common.config import (
        load_default_triage_profile,
        load_institution_priors,
        load_lab_priors,
    )


DEFAULT_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "cs.AI": ["agent", "reasoning", "planning", "tool use", "decision making"],
    "cs.CL": ["language model", "retrieval", "translation", "prompting", "evaluation"],
    "cs.CV": ["vision", "segmentation", "detection", "diffusion", "image generation"],
    "cs.LG": ["optimization", "generalization", "fine-tuning", "representation learning"],
    "cs.RO": ["robot", "policy", "manipulation", "control", "sim-to-real"],
    "stat.ML": ["generalization", "probabilistic", "causal", "uncertainty", "estimation"],
}

ACTIONABILITY_PATTERNS: dict[str, tuple[str, ...]] = {
    "project_page_in_comment": ("http://", "https://", "project page"),
    "code_release_in_comment": ("github.com", "code available", "source code", "implementation"),
    "benchmark_language": ("benchmark", "leaderboard", "state-of-the-art", "sota", "evaluation"),
    "dataset_release_language": ("dataset", "corpus", "release", "data collection"),
    "accepted_to_venue_comment": ("accepted to", "to appear in", "camera ready", "best paper"),
    "survey_or_tutorial": ("survey", "tutorial", "review"),
}

COMMENT_ONLY_ACTIONABILITY_SIGNALS = {
    "project_page_in_comment",
    "code_release_in_comment",
    "accepted_to_venue_comment",
}

OUT_OF_SCOPE_PATTERNS = (
    "corrigendum",
    "withdrawn",
    "retracted",
    "medical imaging dataset only",
    "protein folding",
)

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
}


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().split())


def _normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", _normalize_text(value)).strip()


def _tokenize(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def _contains_phrase(normalized_text: str, phrase: str) -> bool:
    normalized_phrase = _normalize_key(phrase)
    if not normalized_phrase:
        return False
    pattern = rf"(?<![a-z0-9]){re.escape(normalized_phrase)}(?![a-z0-9])"
    return re.search(pattern, normalized_text) is not None


def _clamp(lower: float, upper: float, value: float) -> float:
    return max(lower, min(upper, value))


def _round_score(value: float) -> float:
    return round(value, 2)


class MetadataScorer:
    def __init__(
        self,
        profile: ScoringProfile | None = None,
        *,
        scoring_config: dict[str, Any] | None = None,
        institution_priors: dict[str, Any] | None = None,
        lab_priors: dict[str, Any] | None = None,
    ) -> None:
        self.scoring_config = scoring_config or load_default_triage_profile()
        self.profile = self._build_profile(profile)
        self.point_budget = self.scoring_config.get("point_budget", {})
        self.thresholds = self.scoring_config.get("thresholds", {})
        self.penalty_config = self.scoring_config.get("penalties", {})
        self.category_priors = self.scoring_config.get("category_priors", {})
        self.prestige_config = self.scoring_config.get("prestige_priors", {})
        self.actionability_config = self.scoring_config.get("actionability_signals", {})
        self.uncertainty_discounts = self.scoring_config.get("uncertainty_discounts", {})
        self.institution_lookup = self._build_alias_lookup(
            institution_priors or load_institution_priors(),
            entries_key="institutions",
        )
        self.lab_lookup = self._build_alias_lookup(
            lab_priors or load_lab_priors(),
            entries_key="labs",
        )

    def score_paper(
        self,
        paper: ArxivPaper,
        *,
        cohort: Sequence[ArxivPaper] | None = None,
    ) -> ScoringResult:
        cohort_papers = cohort or [paper]
        matched_rules: list[str] = []

        topical_score, topical_meta = self._score_topical_relevance(paper)
        matched_rules.extend(topical_meta["rules"])

        prestige_score, prestige_meta = self._score_prestige_priors(paper)
        matched_rules.extend(prestige_meta["rules"])

        actionability_score, actionability_meta = self._score_actionability(paper)
        matched_rules.extend(actionability_meta["rules"])

        profile_fit_score, profile_fit_meta = self._score_profile_fit(paper)
        matched_rules.extend(profile_fit_meta["rules"])

        novelty_score, novelty_meta = self._score_novelty_diversity(paper, cohort_papers)
        matched_rules.extend(novelty_meta["rules"])

        penalties_score, penalties_meta = self._score_penalties(
            paper=paper,
            topical_ratio=topical_meta["ratio"],
            prestige_score=prestige_score,
            max_similarity=novelty_meta["max_similarity"],
        )
        matched_rules.extend(penalties_meta["rules"])

        component_scores = ComponentScores(
            topical_relevance=_round_score(topical_score),
            prestige_priors=_round_score(prestige_score),
            actionability=_round_score(actionability_score),
            profile_fit=_round_score(profile_fit_score),
            novelty_diversity=_round_score(novelty_score),
            penalties=_round_score(penalties_score),
        )

        total_score = _clamp(
            0.0,
            100.0,
            component_scores.topical_relevance
            + component_scores.prestige_priors
            + component_scores.actionability
            + component_scores.profile_fit
            + component_scores.novelty_diversity
            + component_scores.penalties,
        )
        threshold_decision = self._resolve_threshold_decision(total_score)
        explanation = self._build_explanation(
            paper=paper,
            component_scores=component_scores,
            threshold_decision=threshold_decision,
            topical_meta=topical_meta,
            prestige_meta=prestige_meta,
            actionability_meta=actionability_meta,
            profile_fit_meta=profile_fit_meta,
            novelty_meta=novelty_meta,
            penalties_meta=penalties_meta,
        )

        return ScoringResult(
            paper_id=paper.arxiv_id,
            total_score=_round_score(total_score),
            component_scores=component_scores,
            matched_rules=list(dict.fromkeys(matched_rules)),
            threshold_decision=threshold_decision,
            explanation=explanation,
        )

    def score_papers(self, papers: Iterable[ArxivPaper]) -> list[ScoringResult]:
        paper_list = list(papers)
        results = [self.score_paper(paper, cohort=paper_list) for paper in paper_list]
        results.sort(key=lambda result: result.total_score, reverse=True)
        return results

    def _build_profile(self, profile: ScoringProfile | None) -> ScoringProfile:
        if profile is None:
            return ScoringProfile(categories=self.scoring_config.get("include_primary_categories", []))

        categories = list(profile.categories)
        keywords = list(profile.keywords)
        for category in categories:
            for suggestion in DEFAULT_CATEGORY_KEYWORDS.get(category, []):
                if suggestion.lower() not in {keyword.lower() for keyword in keywords}:
                    keywords.append(suggestion)
        return profile.model_copy(update={"keywords": keywords})

    def _build_alias_lookup(
        self,
        priors: dict[str, Any],
        *,
        entries_key: str,
    ) -> list[dict[str, Any]]:
        tiers = priors.get("tiers", {})
        entries = priors.get(entries_key, [])
        lookup: list[dict[str, Any]] = []
        for entry in entries:
            tier_name = entry.get("tier")
            tier = tiers.get(tier_name, {})
            score = float(tier.get("score", 0.0))
            aliases = entry.get("aliases") or [entry.get("name", "")]
            lookup.append(
                {
                    "name": entry.get("name", ""),
                    "score": score,
                    "aliases": [_normalize_key(alias) for alias in aliases if alias],
                }
            )
        return lookup

    def _score_topical_relevance(self, paper: ArxivPaper) -> tuple[float, dict[str, Any]]:
        budget = float(self.point_budget.get("topical_relevance", 45))
        text = _normalize_key(f"{paper.title} {paper.abstract}")
        category_signal = max(
            (float(self.category_priors.get(category, 0.0)) for category in paper.categories),
            default=float(self.category_priors.get(paper.primary_category, 0.0)),
        )

        profile_terms = self.profile.keywords or DEFAULT_CATEGORY_KEYWORDS.get(paper.primary_category, [])
        matched_keywords = [term for term in profile_terms if _contains_phrase(text, term)]
        keyword_coverage = (
            len({term.lower() for term in matched_keywords}) / len({term.lower() for term in profile_terms})
            if profile_terms
            else 0.0
        )

        profile_category_match = 1.0 if paper.primary_category in self.profile.categories else 0.0
        ratio = _clamp(
            0.0,
            1.0,
            (0.55 * keyword_coverage) + (0.30 * category_signal) + (0.15 * profile_category_match),
        )
        score = budget * ratio

        rules = []
        if matched_keywords:
            rules.append(f"topical:keywords:{','.join(sorted({term.lower() for term in matched_keywords}))}")
        if category_signal > 0:
            rules.append(f"topical:category_prior:{paper.primary_category}")
        if profile_category_match:
            rules.append(f"topical:profile_category:{paper.primary_category}")

        return score, {
            "ratio": ratio,
            "category_signal": category_signal,
            "matched_keywords": matched_keywords,
            "rules": rules,
        }

    def _score_prestige_priors(self, paper: ArxivPaper) -> tuple[float, dict[str, Any]]:
        budget = float(self.point_budget.get("prestige_priors", 20))
        author_weight = float(self.prestige_config.get("author_weight", 0.45))
        institution_weight = float(self.prestige_config.get("institution_weight", 0.30))
        lab_weight = float(self.prestige_config.get("lab_weight", 0.25))
        author_count = max(len(paper.authors), 1)
        normalization = _clamp(0.55, 1.0, 2.2 / math.sqrt(author_count))

        tracked_authors = {_normalize_key(name) for name in self.profile.tracked_authors}
        matched_authors = [
            author.name for author in paper.authors if _normalize_key(author.name) in tracked_authors
        ]
        author_prior = 1.0 if matched_authors else 0.0

        institution_score, institution_rules = self._resolve_affiliation_prior(
            paper=paper,
            lookup=self.institution_lookup,
            config_key="inferred_affiliation_factor",
            label="institution",
        )
        lab_score, lab_rules = self._resolve_affiliation_prior(
            paper=paper,
            lookup=self.lab_lookup,
            config_key="inferred_lab_factor",
            label="lab",
        )

        prestige_raw = (
            (author_weight * author_prior)
            + (institution_weight * institution_score)
            + (lab_weight * lab_score)
        )
        score = budget * prestige_raw * normalization
        score = min(score, float(self.prestige_config.get("max_points_after_caps", 18)))
        if author_prior == 0 and lab_score == 0:
            score = min(score, float(self.prestige_config.get("max_points_from_institution_only", 8)))
        if author_prior == 0 and institution_score == 0:
            score = min(score, float(self.prestige_config.get("max_points_from_lab_only", 8)))

        rules = []
        if matched_authors:
            rules.append(f"prestige:tracked_author:{','.join(sorted(matched_authors))}")
        rules.extend(institution_rules)
        rules.extend(lab_rules)

        return score, {
            "matched_authors": matched_authors,
            "institution_score": institution_score,
            "lab_score": lab_score,
            "rules": rules,
        }

    def _score_actionability(self, paper: ArxivPaper) -> tuple[float, dict[str, Any]]:
        budget = float(self.point_budget.get("actionability", 15))
        comment_text = _normalize_text(paper.comment or "")
        metadata_text = _normalize_text(f"{paper.title} {paper.abstract}")
        normalized_comment_text = _normalize_key(comment_text)
        normalized_metadata_text = _normalize_key(metadata_text)
        matched_signals: list[str] = []
        matched_strength = 0.0

        for signal_name, weight in self.actionability_config.items():
            patterns = ACTIONABILITY_PATTERNS.get(signal_name, ())
            target_text = comment_text if signal_name in COMMENT_ONLY_ACTIONABILITY_SIGNALS else metadata_text
            normalized_target_text = (
                normalized_comment_text
                if signal_name in COMMENT_ONLY_ACTIONABILITY_SIGNALS
                else normalized_metadata_text
            )
            if patterns and any(
                pattern in target_text if any(marker in pattern for marker in ("://", ".com", ".io", ".ai"))
                else _contains_phrase(normalized_target_text, pattern)
                for pattern in patterns
            ):
                matched_signals.append(signal_name)
                matched_strength += float(weight)

        ratio = _clamp(0.0, 1.0, matched_strength / 2.0)
        score = budget * ratio

        return score, {
            "matched_signals": matched_signals,
            "rules": [f"actionability:{signal}" for signal in matched_signals],
        }

    def _score_profile_fit(self, paper: ArxivPaper) -> tuple[float, dict[str, Any]]:
        budget = float(self.point_budget.get("profile_fit_and_freshness", 10))
        text = _normalize_key(f"{paper.title} {paper.abstract}")

        matched_themes = [theme for theme in self.profile.themes if _contains_phrase(text, theme)]
        theme_coverage = (
            len({theme.lower() for theme in matched_themes}) / len({theme.lower() for theme in self.profile.themes})
            if self.profile.themes
            else 0.0
        )
        tracked_author_hit = 1.0 if any(
            _normalize_key(author.name) in {_normalize_key(name) for name in self.profile.tracked_authors}
            for author in paper.authors
        ) else 0.0
        category_alignment = 1.0 if paper.primary_category in self.profile.categories else 0.0

        now = datetime.now(timezone.utc)
        age_days = max((now - paper.updated).total_seconds() / 86_400, 0.0)
        freshness = _clamp(0.0, 1.0, 1 - (age_days / 7))

        ratio = _clamp(
            0.0,
            1.0,
            (0.40 * theme_coverage)
            + (0.25 * tracked_author_hit)
            + (0.20 * freshness)
            + (0.15 * category_alignment),
        )
        score = budget * ratio

        rules = []
        if matched_themes:
            rules.append(f"profile_fit:themes:{','.join(sorted({theme.lower() for theme in matched_themes}))}")
        if tracked_author_hit:
            rules.append("profile_fit:tracked_author")
        if category_alignment:
            rules.append(f"profile_fit:category:{paper.primary_category}")
        if freshness >= 0.75:
            rules.append("profile_fit:fresh")

        return score, {
            "matched_themes": matched_themes,
            "freshness": freshness,
            "rules": rules,
        }

    def _score_novelty_diversity(
        self,
        paper: ArxivPaper,
        cohort: Sequence[ArxivPaper],
    ) -> tuple[float, dict[str, Any]]:
        budget = float(self.point_budget.get("novelty_and_diversity", 10))
        paper_tokens = _tokenize(f"{paper.title} {paper.abstract}")
        max_similarity = 0.0
        for candidate in cohort:
            if candidate.arxiv_id == paper.arxiv_id:
                continue
            if candidate.updated.date() != paper.updated.date():
                continue
            candidate_tokens = _tokenize(f"{candidate.title} {candidate.abstract}")
            if not paper_tokens or not candidate_tokens:
                continue
            intersection = paper_tokens.intersection(candidate_tokens)
            union = paper_tokens.union(candidate_tokens)
            similarity = len(intersection) / len(union)
            max_similarity = max(max_similarity, similarity)

        ratio = _clamp(0.2, 1.0, 1 - (0.85 * max_similarity))
        score = budget * ratio

        rules = []
        if max_similarity < 0.35:
            rules.append("novelty:distinct_same_day")
        elif max_similarity >= 0.72:
            rules.append("novelty:clustered_same_day")

        return score, {
            "max_similarity": max_similarity,
            "rules": rules,
        }

    def _score_penalties(
        self,
        *,
        paper: ArxivPaper,
        topical_ratio: float,
        prestige_score: float,
        max_similarity: float,
    ) -> tuple[float, dict[str, Any]]:
        total_penalty = 0.0
        rules: list[str] = []
        text = _normalize_key(f"{paper.title} {paper.abstract} {paper.comment or ''}")

        if len(paper.abstract) < 360:
            total_penalty += float(self.penalty_config.get("weak_abstract", 0))
            rules.append("penalty:weak_abstract")

        negative_keywords = [_normalize_key(term) for term in self.profile.negative_keywords]
        if negative_keywords and any(_contains_phrase(text, term) for term in negative_keywords):
            total_penalty += float(self.penalty_config.get("keyword_profile_conflict", 0))
            rules.append("penalty:keyword_profile_conflict")

        if topical_ratio < 0.25 and any(_contains_phrase(text, pattern) for pattern in OUT_OF_SCOPE_PATTERNS):
            total_penalty += float(self.penalty_config.get("likely_cross_domain_out_of_scope", 0))
            rules.append("penalty:likely_cross_domain_out_of_scope")

        if max_similarity >= 0.82:
            total_penalty += float(self.penalty_config.get("duplicate_same_day_cluster", 0))
            rules.append("penalty:duplicate_same_day_cluster")

        if prestige_score >= 8 and topical_ratio < 0.30:
            total_penalty += float(self.penalty_config.get("prestige_without_topic_fit", 0))
            rules.append("penalty:prestige_without_topic_fit")

        floor = float(self.point_budget.get("penalties", -25))
        total_penalty = max(total_penalty, floor)
        return total_penalty, {"rules": rules}

    def _resolve_affiliation_prior(
        self,
        *,
        paper: ArxivPaper,
        lookup: list[dict[str, Any]],
        config_key: str,
        label: str,
    ) -> tuple[float, list[str]]:
        best_score = 0.0
        matched_rule = ""
        explicit_matches = self._extract_affiliation_matches(
            texts=[author.affiliation for author in paper.authors if author.affiliation],
            lookup=lookup,
        )
        if explicit_matches:
            best_match = max(explicit_matches, key=lambda item: item["score"])
            best_score = best_match["score"]
            matched_rule = f"prestige:{label}:{best_match['name']}"
        else:
            inferred_matches = self._extract_text_matches(
                texts=[paper.comment or "", paper.journal_ref or ""],
                lookup=lookup,
            )
            if inferred_matches:
                best_match = max(inferred_matches, key=lambda item: item["score"])
                best_score = best_match["score"] * float(self.uncertainty_discounts.get(config_key, 1.0))
                matched_rule = f"prestige:{label}_inferred:{best_match['name']}"

        return best_score, [matched_rule] if matched_rule else []

    def _extract_affiliation_matches(
        self,
        *,
        texts: Sequence[str],
        lookup: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for text in texts:
            segments = [segment.strip() for segment in re.split(r"[,;/()]", text) if segment.strip()]
            normalized_segments = {_normalize_key(text), *(_normalize_key(segment) for segment in segments)}
            for entry in lookup:
                if any(alias in normalized_segments for alias in entry["aliases"]):
                    matches.append(entry)
        return matches

    def _extract_text_matches(
        self,
        *,
        texts: Sequence[str],
        lookup: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        normalized_texts = [_normalize_key(text) for text in texts if text]
        for entry in lookup:
            for alias in entry["aliases"]:
                alias_tokens = alias.split()
                if not alias_tokens:
                    continue
                pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"
                if any(re.search(pattern, text) for text in normalized_texts):
                    matches.append(entry)
                    break
        return matches

    def _resolve_threshold_decision(self, total_score: float) -> str:
        drop_below = float(self.thresholds.get("drop_below", 35))
        pdf_download_at = float(self.thresholds.get("pdf_download_at", 55))
        llm_rerank_at = float(self.thresholds.get("llm_rerank_at", 65))
        digest_candidate_at = float(self.thresholds.get("digest_candidate_at", 75))
        source_fetch_at = float(self.thresholds.get("source_fetch_at", 82))

        if total_score < drop_below:
            return "drop"
        if total_score < pdf_download_at:
            return "metadata_only"
        if total_score < llm_rerank_at:
            return "pdf_download"
        if total_score < digest_candidate_at:
            return "llm_rerank"
        if total_score < source_fetch_at:
            return "digest_candidate"
        return "source_fetch"

    def _build_explanation(
        self,
        *,
        paper: ArxivPaper,
        component_scores: ComponentScores,
        threshold_decision: str,
        topical_meta: dict[str, Any],
        prestige_meta: dict[str, Any],
        actionability_meta: dict[str, Any],
        profile_fit_meta: dict[str, Any],
        novelty_meta: dict[str, Any],
        penalties_meta: dict[str, Any],
    ) -> str:
        segments = [
            f"{paper.arxiv_id} scored {component_scores.topical_relevance}/45 on topical relevance",
            f"with keywords {', '.join(topical_meta['matched_keywords'][:4]) or 'none'}",
            f"and category prior {paper.primary_category}.",
            f"Prestige contributed {component_scores.prestige_priors}/20",
            f"from authors {', '.join(prestige_meta['matched_authors']) or 'none'}",
            "and affiliation priors.",
            f"Actionability reached {component_scores.actionability}/15",
            f"via {', '.join(actionability_meta['matched_signals']) or 'no explicit delivery signals'}.",
            f"Profile fit scored {component_scores.profile_fit}/10",
            f"with freshness {profile_fit_meta['freshness']:.2f}.",
            f"Novelty scored {component_scores.novelty_diversity}/10",
            f"with max same-day similarity {novelty_meta['max_similarity']:.2f}.",
            f"Penalties totaled {component_scores.penalties}.",
            f"Final decision: {threshold_decision}.",
        ]
        if penalties_meta["rules"]:
            segments.append(f"Penalty triggers: {', '.join(penalties_meta['rules'])}.")
        return " ".join(segments)
