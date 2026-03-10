"""Digest assembly utilities."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable as IterableABC
from datetime import datetime, timezone
from typing import Any, Iterable



def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DigestAssembler:
    """Group scored papers into digest sections and pick top entries."""

    def __init__(self, *, max_papers_per_section: int = 3) -> None:
        self.max_papers_per_section = max_papers_per_section

    def assemble(
        self,
        scored_papers: Iterable[dict[str, Any]],
        *,
        workspace_name: str = "Scivly",
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        generated_time = generated_at or utc_now()
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for paper in scored_papers:
            grouped[self._group_key(paper)].append(paper)

        sections = []
        for group_key, papers in grouped.items():
            selected = sorted(
                papers,
                key=lambda paper: (
                    float(paper.get("total_score", 0.0)),
                    paper.get("published_at", ""),
                    paper.get("title", ""),
                ),
                reverse=True,
            )[: self.max_papers_per_section]
            sections.append(
                {
                    "section_id": group_key,
                    "section_title": self._section_title(group_key),
                    "paper_count": len(selected),
                    "papers": [self._serialize_paper(paper) for paper in selected],
                }
            )

        sections.sort(
            key=lambda section: (
                max((paper["score"] for paper in section["papers"]), default=0.0),
                section["section_title"],
            ),
            reverse=True,
        )

        total_papers = sum(section["paper_count"] for section in sections)
        return {
            "title": f"{workspace_name} Research Digest",
            "generated_at": generated_time.isoformat(),
            "summary": {
                "section_count": len(sections),
                "paper_count": total_papers,
            },
            "sections": sections,
        }

    def _group_key(self, paper: dict[str, Any]) -> str:
        matched_topics = self._normalize_string_list(paper.get("matched_topics"))
        if matched_topics:
            return matched_topics[0].lower().replace(" ", "-")

        primary_category = paper.get("primary_category")
        if primary_category:
            return str(primary_category).lower()

        categories = self._normalize_string_list(paper.get("categories"))
        if categories:
            return categories[0].lower()

        return "general"

    def _section_title(self, group_key: str) -> str:
        return group_key.replace("-", " ").upper()

    def _serialize_paper(self, paper: dict[str, Any]) -> dict[str, Any]:
        matched_rules = self._normalize_string_list(paper.get("matched_rules"))
        return {
            "paper_id": str(paper.get("paper_id") or paper.get("id") or ""),
            "title": paper.get("title", "Untitled paper"),
            "summary": paper.get("one_line_summary") or paper.get("summary") or "",
            "score": float(paper.get("total_score", 0.0)),
            "primary_category": paper.get("primary_category"),
            "categories": self._normalize_string_list(paper.get("categories")),
            "reasons": matched_rules[:3],
        }

    def _normalize_string_list(self, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, IterableABC) and not isinstance(value, (bytes, dict)):
            return [str(item) for item in value if item is not None]
        return [str(value)]
