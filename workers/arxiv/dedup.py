from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field

from .models import ArxivPaper


ARXIV_ID_PATTERN = re.compile(
    r"(?P<id>(?:[a-z\-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5}))(?:v(?P<version>\d+))?$",
    flags=re.IGNORECASE,
)


class DeduplicationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_id: str
    merged_versions: list[int] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    paper: ArxivPaper


def _extract_identifier(raw_id: str) -> str:
    candidate = raw_id.strip().rstrip("/")
    for marker in ("/abs/", "/pdf/"):
        if marker in candidate:
            candidate = candidate.split(marker, maxsplit=1)[1]
    if candidate.endswith(".pdf"):
        candidate = candidate[:-4]
    return candidate


def canonicalize_arxiv_id(raw_id: str) -> str:
    candidate = _extract_identifier(raw_id)
    match = ARXIV_ID_PATTERN.search(candidate)
    if not match:
        raise ValueError(f"Unsupported arXiv identifier: {raw_id}")
    return match.group("id")


def extract_version(raw_id: str, fallback: int = 1) -> int:
    candidate = _extract_identifier(raw_id)
    match = ARXIV_ID_PATTERN.search(candidate)
    if not match or not match.group("version"):
        return fallback
    return int(match.group("version"))


def _merge_categories(papers: list[ArxivPaper]) -> list[str]:
    categories: list[str] = []
    seen: set[str] = set()
    for paper in papers:
        for category in paper.categories:
            if category not in seen:
                seen.add(category)
                categories.append(category)
    return categories


def deduplicate_papers(papers: Iterable[ArxivPaper]) -> list[DeduplicationRecord]:
    grouped: dict[str, list[ArxivPaper]] = defaultdict(list)

    for paper in papers:
        canonical_id = canonicalize_arxiv_id(paper.arxiv_id)
        normalized_paper = paper.model_copy(
            update={
                "arxiv_id": canonical_id,
                "version": extract_version(paper.arxiv_id, fallback=paper.version),
            }
        )
        grouped[canonical_id].append(normalized_paper)

    deduplicated: list[DeduplicationRecord] = []
    for canonical_id, group in grouped.items():
        ordered_group = sorted(
            group,
            key=lambda paper: (paper.version, paper.updated, paper.published, len(paper.categories)),
            reverse=True,
        )
        latest = ordered_group[0]
        merged_categories = _merge_categories(ordered_group)
        merged_versions = sorted({paper.version for paper in ordered_group})

        merged_paper = latest.model_copy(
            update={
                "arxiv_id": canonical_id,
                "version": max(merged_versions),
                "categories": merged_categories,
                "primary_category": latest.primary_category or merged_categories[0],
                "comment": next((paper.comment for paper in ordered_group if paper.comment), None),
                "journal_ref": next(
                    (paper.journal_ref for paper in ordered_group if paper.journal_ref),
                    None,
                ),
                "doi": next((paper.doi for paper in ordered_group if paper.doi), None),
            }
        )
        deduplicated.append(
            DeduplicationRecord(
                canonical_id=canonical_id,
                merged_versions=merged_versions,
                source_ids=list(dict.fromkeys(f"{canonical_id}v{paper.version}" for paper in ordered_group)),
                paper=merged_paper,
            )
        )

    deduplicated.sort(key=lambda record: (record.paper.updated, record.paper.published), reverse=True)
    return deduplicated
