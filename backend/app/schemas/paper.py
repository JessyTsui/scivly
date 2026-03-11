from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import APIModel


class PaperAuthor(APIModel):
    name: str
    affiliation: str | None = None


class PaperOut(APIModel):
    id: UUID
    arxiv_id: str
    version: int
    title: str
    abstract: str
    authors: list[PaperAuthor]
    categories: list[str]
    primary_category: str
    published_at: datetime
    updated_at: datetime
    comment: str | None = None
    doi: str | None = None
    one_line_summary: str | None = None


class PaperScoreOut(APIModel):
    id: UUID
    paper_id: UUID
    workspace_id: UUID
    profile_id: UUID
    score_version: str
    total_score: float
    topical_relevance: float
    prestige_priors: float
    actionability: float
    profile_fit: float
    novelty_diversity: float
    penalties: float
    threshold_decision: Literal[
        "drop",
        "metadata_only",
        "pdf_queue",
        "pdf_candidate",
        "rerank",
        "rerank_candidate",
        "digest_candidate",
        "source_fetch",
        "source_fetch_candidate",
    ]
    matched_rules: list[str]
    llm_rerank_delta: float
    llm_rerank_reasons: list[str]
    created_at: datetime


class PaperListParams(APIModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    query: str | None = Field(default=None, max_length=160)
    category: str | None = Field(default=None, max_length=32)
    workspace_id: UUID | None = None
    sort: Literal["published_at", "score"] = "published_at"
