from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.middleware.error_handler import APIError
from app.models import Paper, PaperEnrichment, PaperScore
from app.persistence import format_reason_payload, format_rule_payload
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.paper import PaperListParams, PaperOut, PaperScoreOut

router = APIRouter(prefix="/papers", tags=["Papers"])


def _latest_enrichment_subquery():
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
            PaperEnrichment.one_line_summary.label("one_line_summary"),
        )
        .join(
            latest_created,
            (PaperEnrichment.paper_id == latest_created.c.paper_id)
            & (PaperEnrichment.created_at == latest_created.c.created_at),
        )
        .subquery()
    )


def _latest_score_subquery(workspace_id: UUID):
    latest_created = (
        select(
            PaperScore.paper_id.label("paper_id"),
            func.max(PaperScore.created_at).label("created_at"),
        )
        .where(PaperScore.workspace_id == workspace_id)
        .group_by(PaperScore.paper_id)
        .subquery()
    )

    return (
        select(
            PaperScore.paper_id.label("paper_id"),
            PaperScore.total_score.label("total_score"),
        )
        .join(
            latest_created,
            (PaperScore.paper_id == latest_created.c.paper_id)
            & (PaperScore.created_at == latest_created.c.created_at),
        )
        .where(PaperScore.workspace_id == workspace_id)
        .subquery()
    )


def _serialize_paper(row) -> PaperOut:
    return PaperOut(
        id=row.id,
        arxiv_id=row.arxiv_id,
        version=row.version,
        title=row.title,
        abstract=row.abstract,
        authors=row.authors or [],
        categories=row.categories or [],
        primary_category=row.primary_category or "",
        published_at=row.published_at or row.updated_at,
        updated_at=row.updated_at,
        comment=row.comment,
        doi=row.doi,
        one_line_summary=row.one_line_summary,
    )


def _serialize_score(row) -> PaperScoreOut:
    return PaperScoreOut(
        id=row.id,
        paper_id=row.paper_id,
        workspace_id=row.workspace_id,
        profile_id=row.profile_id,
        score_version=row.score_version,
        total_score=float(row.total_score),
        topical_relevance=float(row.topical_relevance),
        prestige_priors=float(row.prestige_priors),
        actionability=float(row.actionability),
        profile_fit=float(row.profile_fit),
        novelty_diversity=float(row.novelty_diversity),
        penalties=float(row.penalties),
        threshold_decision=row.threshold_decision,
        matched_rules=[format_rule_payload(item) for item in row.matched_rules or []],
        llm_rerank_delta=float(row.llm_rerank_delta),
        llm_rerank_reasons=[format_reason_payload(item) for item in row.llm_rerank_reasons or []],
        created_at=row.created_at,
    )


def _paper_statement(current_user: UserOut):
    enrichment = _latest_enrichment_subquery()
    score = _latest_score_subquery(current_user.workspace_id)
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
            Paper.published_at,
            Paper.updated_at,
            Paper.comment,
            Paper.doi,
            enrichment.c.one_line_summary,
            score.c.total_score,
        )
        .outerjoin(enrichment, enrichment.c.paper_id == Paper.id)
        .outerjoin(score, score.c.paper_id == Paper.id)
    )


async def _get_paper_row(session: AsyncSession, paper_id: UUID, current_user: UserOut):
    row = (
        await session.execute(
            _paper_statement(current_user)
            .where(Paper.id == paper_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="paper_not_found", message="Paper not found.")
    return row


@router.get("", response_model=PaginatedResponse[PaperOut])
async def list_papers(
    params: PaperListParams = Depends(),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PaperOut]:
    statement = _paper_statement(current_user)

    if params.query:
        needle = f"%{params.query.strip()}%"
        statement = statement.where(Paper.title.ilike(needle) | Paper.abstract.ilike(needle))
    if params.category:
        statement = statement.where(Paper.categories.any(params.category))

    total = (
        await session.execute(select(func.count()).select_from(statement.subquery()))
    ).scalar_one()

    if params.sort == "score":
        statement = statement.order_by(statement.selected_columns.total_score.desc().nullslast(), Paper.published_at.desc())
    else:
        statement = statement.order_by(Paper.published_at.desc(), Paper.created_at.desc())

    rows = (
        await session.execute(
            statement.offset((params.page - 1) * params.per_page).limit(params.per_page)
        )
    ).all()

    return PaginatedResponse[PaperOut](
        items=[_serialize_paper(row) for row in rows],
        total=total,
        page=params.page,
        per_page=params.per_page,
    )


@router.get("/search", response_model=PaginatedResponse[PaperOut])
async def search_papers(
    q: str = Query(min_length=2, max_length=160),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PaperOut]:
    params = PaperListParams(page=page, per_page=per_page, query=q)
    return await list_papers(params, current_user, session)


@router.get("/{paper_id}", response_model=PaperOut)
async def get_paper(
    paper_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaperOut:
    return _serialize_paper(await _get_paper_row(session, paper_id, current_user))


@router.get("/{paper_id}/scores", response_model=list[PaperScoreOut])
async def get_paper_scores(
    paper_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[PaperScoreOut]:
    await _get_paper_row(session, paper_id, current_user)

    rows = (
        await session.execute(
            select(
                PaperScore.id,
                PaperScore.paper_id,
                PaperScore.workspace_id,
                PaperScore.profile_id,
                PaperScore.score_version,
                PaperScore.total_score,
                PaperScore.topical_relevance,
                PaperScore.prestige_priors,
                PaperScore.actionability,
                PaperScore.profile_fit,
                PaperScore.novelty_diversity,
                PaperScore.penalties,
                PaperScore.threshold_decision,
                PaperScore.matched_rules,
                PaperScore.llm_rerank_delta,
                PaperScore.llm_rerank_reasons,
                PaperScore.created_at,
            )
            .where(PaperScore.paper_id == paper_id)
            .where(PaperScore.workspace_id == current_user.workspace_id)
            .order_by(PaperScore.created_at.desc())
        )
    ).all()

    return [_serialize_score(row) for row in rows]
