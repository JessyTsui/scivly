from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select

from app.models import PaperEnrichment

DATE_WINDOW_HOURS = {
    "24h": 24,
    "72h": 72,
    "7d": 24 * 7,
    "30d": 24 * 30,
}


def latest_enrichment_subquery():
    latest_created = (
        select(
            PaperEnrichment.paper_id.label("paper_id"),
            func.max(PaperEnrichment.created_at).label("created_at"),
        )
        .group_by(PaperEnrichment.paper_id)
        .subquery()
    )

    return (
        select(
            PaperEnrichment.paper_id.label("paper_id"),
            PaperEnrichment.title_zh.label("title_zh"),
            PaperEnrichment.abstract_zh.label("abstract_zh"),
            PaperEnrichment.one_line_summary.label("one_line_summary"),
            PaperEnrichment.key_points.label("key_points"),
            PaperEnrichment.method_summary.label("method_summary"),
            PaperEnrichment.conclusion_summary.label("conclusion_summary"),
            PaperEnrichment.limitations.label("limitations"),
            PaperEnrichment.figure_descriptions.label("figure_descriptions"),
        )
        .join(
            latest_created,
            (PaperEnrichment.paper_id == latest_created.c.paper_id)
            & (PaperEnrichment.created_at == latest_created.c.created_at),
        )
        .subquery()
    )


def summary_fallback(abstract: str) -> str:
    compact = " ".join(abstract.split())
    if len(compact) <= 180:
        return compact
    return f"{compact[:177].rstrip()}..."


def extract_figures(value: object) -> list[tuple[str, str]]:
    if not isinstance(value, list):
        return []

    figures: list[tuple[str, str]] = []
    for index, item in enumerate(value, start=1):
        if isinstance(item, str):
            description = item.strip()
            if description:
                figures.append((f"Figure {index}", description))
            continue

        if not isinstance(item, dict):
            continue

        raw_description = item.get("description")
        if not isinstance(raw_description, str) or not raw_description.strip():
            continue

        raw_figure = item.get("figure")
        label = (
            raw_figure.strip()
            if isinstance(raw_figure, str) and raw_figure.strip()
            else f"Figure {index}"
        )
        figures.append((label, raw_description.strip()))

    return figures


def figure_descriptions(value: object) -> list[str]:
    return [
        f"{label}: {description}" if label and label != description else description
        for label, description in extract_figures(value)
    ]


def apply_date_window(statement, date_window: str, column: Any):
    if date_window == "all":
        return statement

    cutoff = datetime.now(timezone.utc) - timedelta(hours=DATE_WINDOW_HOURS[date_window])
    return statement.where(column.is_not(None)).where(column >= cutoff)
