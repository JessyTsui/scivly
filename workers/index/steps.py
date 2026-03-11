from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

import asyncpg

from workers.common.pipeline import PipelineStep
from workers.common.task import TaskType

from .embedder import EmbeddingProvider, build_paper_embedding_text, create_embedding_provider, vector_to_pgvector

@dataclass(frozen=True)
class IndexablePaper:
    paper_id: UUID
    title: str
    abstract: str
    authors: list[dict[str, Any]]
    categories: list[str]
    title_zh: str | None = None
    abstract_zh: str | None = None
    one_line_summary: str | None = None
    key_points: list[str] | None = None

    def to_document(self) -> dict[str, object]:
        return {
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "categories": self.categories,
            "title_zh": self.title_zh,
            "abstract_zh": self.abstract_zh,
            "one_line_summary": self.one_line_summary,
            "key_points": self.key_points or [],
        }


@dataclass(frozen=True)
class PaperEmbeddingRecord:
    paper_id: UUID
    vector: list[float]


@dataclass(frozen=True)
class IndexPaperRecord:
    paper_id: UUID
    document: str


class PaperEmbeddingStore(Protocol):
    async def fetch_papers(
        self,
        *,
        paper_ids: Sequence[UUID] | None = None,
        limit: int | None = None,
        force: bool = False,
    ) -> list[IndexablePaper]:
        """Load papers that should be embedded."""

    async def persist_embeddings(self, records: Sequence[PaperEmbeddingRecord]) -> int:
        """Persist embeddings into pgvector columns."""


class PostgresPaperEmbeddingStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = _normalize_database_url(database_url)

    async def fetch_papers(
        self,
        *,
        paper_ids: Sequence[UUID] | None = None,
        limit: int | None = None,
        force: bool = False,
    ) -> list[IndexablePaper]:
        if paper_ids is not None and not paper_ids:
            return []

        connection = await asyncpg.connect(self.database_url)
        try:
            query = """
            WITH latest_enrichment AS (
              SELECT DISTINCT ON (paper_id)
                paper_id,
                title_zh,
                abstract_zh,
                one_line_summary,
                key_points
              FROM paper_enrichments
              ORDER BY paper_id, created_at DESC
            )
            SELECT
              papers.id,
              papers.title,
              papers.abstract,
              papers.authors,
              papers.categories,
              latest_enrichment.title_zh,
              latest_enrichment.abstract_zh,
              latest_enrichment.one_line_summary,
              latest_enrichment.key_points
            FROM papers
            LEFT JOIN latest_enrichment
              ON latest_enrichment.paper_id = papers.id
            """
            conditions: list[str] = []
            params: list[object] = []

            if not force:
                conditions.append("papers.embedding IS NULL")
            if paper_ids is not None:
                params.append(list(paper_ids))
                conditions.append(f"papers.id = ANY(${len(params)}::uuid[])")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY papers.updated_at DESC"
            if limit is not None:
                params.append(limit)
                query += f" LIMIT ${len(params)}"

            rows = await connection.fetch(query, *params)
        finally:
            await connection.close()

        return [
            IndexablePaper(
                paper_id=row["id"],
                title=row["title"],
                abstract=row["abstract"],
                authors=list(row["authors"] or []),
                categories=list(row["categories"] or []),
                title_zh=row["title_zh"],
                abstract_zh=row["abstract_zh"],
                one_line_summary=row["one_line_summary"],
                key_points=list(row["key_points"] or []),
            )
            for row in rows
        ]

    async def persist_embeddings(self, records: Sequence[PaperEmbeddingRecord]) -> int:
        if not records:
            return 0

        connection = await asyncpg.connect(self.database_url)
        try:
            await connection.executemany(
                """
                UPDATE papers
                SET embedding = $2::vector
                WHERE id = $1::uuid
                """,
                [(record.paper_id, vector_to_pgvector(record.vector)) for record in records],
            )
        finally:
            await connection.close()

        return len(records)


class IndexPapersStep(PipelineStep):
    """Generate and persist paper embeddings for semantic search."""

    step_type = TaskType.INDEX

    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider | None = None,
        store: PaperEmbeddingStore | None = None,
        database_url: str | None = None,
        batch_size: int = 25,
    ) -> None:
        super().__init__()
        self.embedding_provider = embedding_provider or create_embedding_provider()
        self.store = store or PostgresPaperEmbeddingStore(
            database_url or _resolve_database_url(),
        )
        self.batch_size = batch_size

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        paper_ids = _parse_paper_ids(payload)
        limit = _parse_positive_int(payload.get("limit"))
        force = bool(payload.get("force"))
        papers = await self.store.fetch_papers(
            paper_ids=paper_ids,
            limit=limit,
            force=force,
        )
        if not papers:
            return {
                "indexed_count": 0,
                "indexed_paper_ids": [],
                "embedding_provider": self.embedding_provider.provider_name,
                "embedding_model": self.embedding_provider.model_name,
                "embedding_dimensions": self.embedding_provider.dimensions,
            }

        records: list[PaperEmbeddingRecord] = []
        for start in range(0, len(papers), self.batch_size):
            batch = papers[start : start + self.batch_size]
            vectors = await self.embedding_provider.embed_texts(
                [build_paper_embedding_text(paper.to_document()) for paper in batch]
            )
            records.extend(
                PaperEmbeddingRecord(
                    paper_id=paper.paper_id,
                    vector=vector,
                )
                for paper, vector in zip(batch, vectors, strict=True)
            )

        persisted = await self.store.persist_embeddings(records)
        return {
            "indexed_count": persisted,
            "indexed_paper_ids": [str(record.paper_id) for record in records],
            "embedding_provider": self.embedding_provider.provider_name,
            "embedding_model": self.embedding_provider.model_name,
            "embedding_dimensions": self.embedding_provider.dimensions,
        }


def _parse_paper_ids(payload: dict[str, Any]) -> list[UUID] | None:
    candidates: list[object] = []

    paper_id = payload.get("paper_id")
    if paper_id is not None:
        candidates.append(paper_id)

    paper_ids = payload.get("paper_ids")
    if isinstance(paper_ids, Sequence) and not isinstance(paper_ids, (str, bytes)):
        candidates.extend(paper_ids)

    if not candidates:
        return None

    unique_ids: list[UUID] = []
    seen: set[UUID] = set()
    for candidate in candidates:
        parsed = candidate if isinstance(candidate, UUID) else UUID(str(candidate))
        if parsed in seen:
            continue
        seen.add(parsed)
        unique_ids.append(parsed)
    return unique_ids


def _parse_positive_int(value: object) -> int | None:
    if value is None:
        return None
    parsed = int(str(value))
    return parsed if parsed > 0 else None


def _resolve_database_url() -> str:
    return _normalize_database_url(
        os.getenv("DATABASE_URL", "postgresql://localhost:5432/scivly")
    )


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if database_url.startswith("postgres+asyncpg://"):
        return database_url.replace("postgres+asyncpg://", "postgres://", 1)
    return database_url
