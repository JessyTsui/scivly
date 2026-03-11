from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Text, bindparam, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.middleware.error_handler import APIError
from app.models import Paper, Vector
from app.paper_views import apply_date_window, extract_figures, latest_enrichment_subquery, summary_fallback
from app.schemas.common import PaginatedResponse
from app.schemas.paper import PaperFigureOut, PublicPaperListParams, PublicPaperOut
from app.semantic_search import SemanticSearchError, create_embedding_provider, vector_to_pgvector

router = APIRouter(prefix="/public/papers", tags=["Public Papers"])


def _paper_timestamp():
    return func.coalesce(Paper.published_at, Paper.updated_at)


def _public_paper_statement(*, enrichment=None):
    enrichment = enrichment if enrichment is not None else latest_enrichment_subquery()

    return (
        select(
            Paper.id,
            Paper.arxiv_id,
            Paper.version,
            Paper.title,
            Paper.abstract,
            Paper.authors,
            Paper.categories,
            Paper.primary_category,
            Paper.comment,
            Paper.journal_ref,
            Paper.doi,
            Paper.published_at,
            Paper.updated_at,
            enrichment.c.title_zh,
            enrichment.c.abstract_zh,
            enrichment.c.one_line_summary,
            enrichment.c.key_points,
            enrichment.c.method_summary,
            enrichment.c.conclusion_summary,
            enrichment.c.limitations,
            enrichment.c.figure_descriptions,
        )
        .outerjoin(enrichment, enrichment.c.paper_id == Paper.id)
    )


def _apply_public_filters(
    statement,
    params: PublicPaperListParams,
    *,
    include_query: bool = True,
):
    if include_query and params.q:
        needle = f"%{params.q.strip()}%"
        statement = statement.where(
            Paper.title.ilike(needle)
            | Paper.abstract.ilike(needle)
            | Paper.authors.cast(Text).ilike(needle)
        )

    if params.author:
        author_needle = f"%{params.author.strip()}%"
        statement = statement.where(Paper.authors.cast(Text).ilike(author_needle))

    if params.category and params.category != "all":
        statement = statement.where(Paper.categories.any(params.category))  # type: ignore[arg-type]

    return apply_date_window(statement, params.date_window, _paper_timestamp())


def _serialize_public_paper(row) -> PublicPaperOut:
    figures = [
        PaperFigureOut(label=label, description=description)
        for label, description in extract_figures(row.figure_descriptions)
    ]

    return PublicPaperOut(
        id=row.id,
        arxiv_id=row.arxiv_id,
        version=row.version,
        title=row.title,
        abstract=row.abstract,
        authors=row.authors or [],
        categories=row.categories or [],
        primary_category=row.primary_category or ((row.categories or ["unknown"])[0]),
        published_at=row.published_at or row.updated_at,
        updated_at=row.updated_at,
        comment=row.comment,
        journal_ref=row.journal_ref,
        doi=row.doi,
        title_zh=row.title_zh,
        abstract_zh=row.abstract_zh,
        one_line_summary=row.one_line_summary or summary_fallback(row.abstract),
        key_points=row.key_points or [],
        method_summary=row.method_summary,
        conclusion_summary=row.conclusion_summary,
        limitations=row.limitations,
        figures=figures,
    )


async def _get_public_paper_row(session: AsyncSession, paper_id: UUID):
    row = (await session.execute(_public_paper_statement().where(Paper.id == paper_id))).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="paper_not_found", message="Paper not found.")
    return row


@router.get("", response_model=PaginatedResponse[PublicPaperOut])
async def list_public_papers(
    params: PublicPaperListParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PublicPaperOut]:
    statement = _apply_public_filters(_public_paper_statement(), params)
    total = (await session.execute(select(func.count()).select_from(statement.subquery()))).scalar_one()

    paper_timestamp = _paper_timestamp()
    if params.sort == "oldest":
        statement = statement.order_by(paper_timestamp.asc().nullslast(), Paper.created_at.asc())
    else:
        statement = statement.order_by(paper_timestamp.desc().nullslast(), Paper.created_at.desc())

    rows = (
        await session.execute(
            statement.offset((params.page - 1) * params.per_page).limit(params.per_page)
        )
    ).all()

    return PaginatedResponse[PublicPaperOut](
        items=[_serialize_public_paper(row) for row in rows],
        total=total,
        page=params.page,
        per_page=params.per_page,
    )


@router.get("/search", response_model=PaginatedResponse[PublicPaperOut])
async def search_public_papers(
    q: str = Query(min_length=2, max_length=160),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=12, ge=1, le=60),
    author: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=32),
    date_window: Literal["24h", "72h", "7d", "30d", "all"] = "all",
    sort: Literal["relevance", "newest", "oldest"] = "relevance",
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PublicPaperOut]:
    params = PublicPaperListParams(
        page=page,
        per_page=per_page,
        q=q,
        author=author,
        category=category,
        date_window=date_window,
        sort=sort,
    )

    try:
        embedding_provider = create_embedding_provider()
        query_embedding = await embedding_provider.embed_text(q.strip())
    except SemanticSearchError:
        fallback_sort = "newest" if sort == "relevance" else sort
        return await list_public_papers(params.model_copy(update={"sort": fallback_sort}), session)

    query_vector = vector_to_pgvector(query_embedding)
    distance = Paper.embedding.op("<=>")(
        cast(
            bindparam("query_embedding", query_vector),
            Vector(embedding_provider.dimensions),
        )
    )
    paper_timestamp = _paper_timestamp()
    statement = _apply_public_filters(
        _public_paper_statement().where(Paper.embedding.is_not(None)),
        params,
        include_query=False,
    )
    total = (await session.execute(select(func.count()).select_from(statement.subquery()))).scalar_one()

    if total == 0:
        fallback_sort = "newest" if sort == "relevance" else sort
        return await list_public_papers(params.model_copy(update={"sort": fallback_sort}), session)

    statement = statement.add_columns(distance.label("distance")).params(query_embedding=query_vector)
    if sort == "oldest":
        statement = statement.order_by(paper_timestamp.asc().nullslast(), distance.asc(), Paper.created_at.asc())
    elif sort == "newest":
        statement = statement.order_by(paper_timestamp.desc().nullslast(), distance.asc(), Paper.created_at.desc())
    else:
        statement = statement.order_by(distance.asc(), paper_timestamp.desc().nullslast(), Paper.created_at.desc())

    rows = (
        await session.execute(
            statement.offset((page - 1) * per_page).limit(per_page)
        )
    ).all()

    return PaginatedResponse[PublicPaperOut](
        items=[_serialize_public_paper(row) for row in rows],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{paper_id}", response_model=PublicPaperOut)
async def get_public_paper(
    paper_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> PublicPaperOut:
    return _serialize_public_paper(await _get_public_paper_row(session, paper_id))
