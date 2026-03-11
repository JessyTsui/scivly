from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from . import Base, Vector


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (
        UniqueConstraint("arxiv_id", name="uq_papers_arxiv_id"),
        CheckConstraint("version > 0", name="chk_papers_version_positive"),
        CheckConstraint("length(trim(title)) > 0", name="chk_papers_title_nonempty"),
        CheckConstraint("length(trim(abstract)) > 0", name="chk_papers_abstract_nonempty"),
        CheckConstraint("pdf_status IN ('missing', 'stored', 'failed')", name="chk_papers_pdf_status"),
        Index("ix_papers_primary_category", "primary_category"),
        Index("ix_papers_pdf_status", "pdf_status"),
        Index("ix_papers_published_at", text("published_at DESC")),
        Index("ix_papers_updated_at", text("updated_at DESC")),
        Index("ix_papers_categories_gin", "categories", postgresql_using="gin"),
        Index(
            "ix_papers_authors_gin",
            "authors",
            postgresql_using="gin",
            postgresql_ops={"authors": "jsonb_path_ops"},
        ),
        Index(
            "ix_papers_embedding_ivfflat",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    arxiv_id: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    categories: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False, server_default=text("'{}'::text[]"))
    primary_category: Mapped[str | None] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text)
    journal_ref: Mapped[str | None] = mapped_column(Text)
    doi: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    pdf_path: Mapped[str | None] = mapped_column(Text)
    pdf_status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'missing'"))
    raw_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    embedding: Mapped[Any | None] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class PaperScore(Base):
    __tablename__ = "paper_scores"
    __table_args__ = (
        UniqueConstraint("paper_id", "workspace_id", "profile_id", "score_version", name="uq_paper_scores_snapshot"),
        CheckConstraint(
            "threshold_decision IN ('drop', 'metadata_only', 'pdf_candidate', 'rerank_candidate', 'digest_candidate', 'source_fetch_candidate')",
            name="chk_paper_scores_threshold_decision",
        ),
        CheckConstraint("total_score BETWEEN -37 AND 112", name="chk_paper_scores_total_score_reasonable"),
        CheckConstraint("topical_relevance BETWEEN 0 AND 45", name="chk_paper_scores_topical_relevance"),
        CheckConstraint("prestige_priors BETWEEN 0 AND 20", name="chk_paper_scores_prestige_priors"),
        CheckConstraint("actionability BETWEEN 0 AND 15", name="chk_paper_scores_actionability"),
        CheckConstraint("profile_fit BETWEEN 0 AND 10", name="chk_paper_scores_profile_fit"),
        CheckConstraint("novelty_diversity BETWEEN 0 AND 10", name="chk_paper_scores_novelty_diversity"),
        CheckConstraint("penalties BETWEEN -25 AND 0", name="chk_paper_scores_penalties"),
        CheckConstraint("llm_rerank_delta BETWEEN -12 AND 12", name="chk_paper_scores_llm_rerank_delta"),
        Index("ix_paper_scores_workspace_created_at", text("workspace_id, created_at DESC")),
        Index("ix_paper_scores_profile_id", "profile_id"),
        Index("ix_paper_scores_threshold_decision", "threshold_decision"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    score_version: Mapped[str] = mapped_column(Text, nullable=False)
    total_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    topical_relevance: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    prestige_priors: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    actionability: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    profile_fit: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    novelty_diversity: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    penalties: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, server_default=text("0"))
    matched_rules: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    threshold_decision: Mapped[str] = mapped_column(Text, nullable=False)
    llm_rerank_delta: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, server_default=text("0"))
    llm_rerank_reasons: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class PaperEnrichment(Base):
    __tablename__ = "paper_enrichments"
    __table_args__ = (
        UniqueConstraint("paper_id", "enrichment_model", name="uq_paper_enrichments_paper_model"),
        CheckConstraint("enrichment_cost >= 0", name="chk_paper_enrichments_cost_nonnegative"),
        Index("ix_paper_enrichments_paper_id", "paper_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
    )
    title_zh: Mapped[str | None] = mapped_column(Text)
    abstract_zh: Mapped[str | None] = mapped_column(Text)
    one_line_summary: Mapped[str | None] = mapped_column(Text)
    key_points: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    method_summary: Mapped[str | None] = mapped_column(Text)
    conclusion_summary: Mapped[str | None] = mapped_column(Text)
    limitations: Mapped[str | None] = mapped_column(Text)
    figure_descriptions: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    enrichment_model: Mapped[str] = mapped_column(Text, nullable=False)
    enrichment_cost: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, server_default=text("0"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
