from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .models import ArxivPaper

try:
    from workers.common.config import load_default_triage_profile
except ModuleNotFoundError:  # pragma: no cover - pytest package resolution fallback
    from common.config import load_default_triage_profile


class HardFilterResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paper_id: str
    passed: bool
    reasons: list[str] = Field(default_factory=list)


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().split())


def _is_category_allowed(paper: ArxivPaper, profile: dict[str, Any]) -> bool:
    allowed_primary = set(profile.get("include_primary_categories", []))
    allowed_secondary = set(profile.get("include_secondary_categories", []))
    paper_categories = set(paper.categories)
    if paper.primary_category in allowed_primary:
        return True
    return bool(paper_categories.intersection(allowed_primary | allowed_secondary))


def evaluate_hard_filters(
    paper: ArxivPaper,
    profile: dict[str, Any] | None = None,
) -> HardFilterResult:
    scoring_profile = profile or load_default_triage_profile()
    hard_filters = scoring_profile.get("hard_filters", {})
    reasons: list[str] = []

    if not _is_category_allowed(paper, scoring_profile):
        reasons.append("category_not_allowed")

    title = paper.title.strip()
    abstract = paper.abstract.strip()
    comment = (paper.comment or "").strip()

    if hard_filters.get("require_title", True) and not title:
        reasons.append("missing_title")

    if hard_filters.get("require_abstract", True) and not abstract:
        reasons.append("missing_abstract")

    title_for_keywords = " ".join([title, comment, abstract[:240]])
    normalized_title = _normalize_text(title_for_keywords)
    reject_keywords = hard_filters.get("reject_title_keywords", [])
    for keyword in reject_keywords:
        if _normalize_text(keyword) in normalized_title:
            reasons.append("withdrawn_or_errata")
            break

    min_abstract_characters = int(hard_filters.get("min_abstract_characters", 0))
    if abstract and len(abstract) < min_abstract_characters:
        reasons.append("abstract_too_short")

    max_title_characters = int(hard_filters.get("max_title_characters", 10_000))
    if title and len(title) > max_title_characters:
        reasons.append("title_too_long")

    return HardFilterResult(
        paper_id=paper.arxiv_id,
        passed=not reasons,
        reasons=reasons,
    )


def apply_hard_filters(
    papers: Iterable[ArxivPaper],
    profile: dict[str, Any] | None = None,
) -> tuple[list[ArxivPaper], list[HardFilterResult]]:
    passed: list[ArxivPaper] = []
    rejected: list[HardFilterResult] = []

    for paper in papers:
        result = evaluate_hard_filters(paper=paper, profile=profile)
        if result.passed:
            passed.append(paper)
        else:
            rejected.append(result)

    return passed, rejected
