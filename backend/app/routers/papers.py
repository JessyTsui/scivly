from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Text, bindparam, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.middleware.error_handler import APIError
from app.models import Paper, PaperEnrichment, PaperScore, TopicProfile, Vector
from app.persistence import format_reason_payload, format_rule_payload
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.paper import MatchedRuleGroups, PaperListParams, PaperOut, PaperScoreOut
from app.semantic_search import SemanticSearchError, create_embedding_provider, vector_to_pgvector

router = APIRouter(prefix="/papers", tags=["Papers"])

DATE_WINDOW_HOURS = {
    "24h": 24,
    "72h": 72,
    "7d": 24 * 7,
    "30d": 24 * 30,
}


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
            PaperScore.id.label("score_id"),
            PaperScore.workspace_id.label("score_workspace_id"),
            PaperScore.profile_id.label("score_profile_id"),
            PaperScore.score_version.label("score_version"),
            PaperScore.total_score.label("total_score"),
            PaperScore.topical_relevance.label("topical_relevance"),
            PaperScore.prestige_priors.label("prestige_priors"),
            PaperScore.actionability.label("actionability"),
            PaperScore.profile_fit.label("profile_fit"),
            PaperScore.novelty_diversity.label("novelty_diversity"),
            PaperScore.penalties.label("penalties"),
            PaperScore.matched_rules.label("matched_rules"),
            PaperScore.threshold_decision.label("threshold_decision"),
            PaperScore.llm_rerank_delta.label("llm_rerank_delta"),
            PaperScore.llm_rerank_reasons.label("llm_rerank_reasons"),
            PaperScore.created_at.label("score_created_at"),
        )
        .join(
            latest_created,
            (PaperScore.paper_id == latest_created.c.paper_id)
            & (PaperScore.created_at == latest_created.c.created_at),
        )
        .where(PaperScore.workspace_id == workspace_id)
        .subquery()
    )


def _paper_statement(
    current_user: UserOut,
    *,
    enrichment=None,
    score=None,
):
    enrichment = enrichment if enrichment is not None else _latest_enrichment_subquery()
    score = score if score is not None else _latest_score_subquery(current_user.workspace_id)

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
            Paper.created_at,
            enrichment.c.title_zh,
            enrichment.c.abstract_zh,
            enrichment.c.one_line_summary,
            enrichment.c.key_points,
            enrichment.c.method_summary,
            enrichment.c.conclusion_summary,
            enrichment.c.limitations,
            enrichment.c.figure_descriptions,
            score.c.score_id,
            score.c.score_workspace_id,
            score.c.score_profile_id,
            score.c.score_version,
            score.c.total_score,
            score.c.topical_relevance,
            score.c.prestige_priors,
            score.c.actionability,
            score.c.profile_fit,
            score.c.novelty_diversity,
            score.c.penalties,
            score.c.matched_rules,
            score.c.threshold_decision,
            score.c.llm_rerank_delta,
            score.c.llm_rerank_reasons,
            score.c.score_created_at,
            TopicProfile.name.label("profile_name"),
        )
        .outerjoin(enrichment, enrichment.c.paper_id == Paper.id)
        .outerjoin(score, score.c.paper_id == Paper.id)
        .outerjoin(TopicProfile, TopicProfile.id == score.c.score_profile_id)
    )


def _summary_fallback(abstract: str) -> str:
    compact = " ".join(abstract.split())
    if len(compact) <= 180:
        return compact
    return f"{compact[:177].rstrip()}..."


def _figure_descriptions(value: object) -> list[str]:
    if not isinstance(value, list):
        return []

    descriptions: list[str] = []
    for item in value:
        if isinstance(item, str):
            stripped = item.strip()
            if stripped:
                descriptions.append(stripped)
            continue

        if isinstance(item, dict):
            description = item.get("description")
            figure = item.get("figure")
            if isinstance(description, str) and description.strip():
                if isinstance(figure, str) and figure.strip():
                    descriptions.append(f"{figure.strip()}: {description.strip()}")
                else:
                    descriptions.append(description.strip())

    return descriptions


def _serialize_score(row) -> PaperScoreOut:
    matched_rules = [format_rule_payload(item) for item in row.matched_rules or []]
    rerank_reasons = [format_reason_payload(item) for item in row.llm_rerank_reasons or []]

    return PaperScoreOut(
        id=row.score_id,
        paper_id=row.id,
        workspace_id=row.score_workspace_id,
        profile_id=row.score_profile_id,
        score_version=row.score_version,
        total_score=float(row.total_score),
        topical_relevance=float(row.topical_relevance),
        prestige_priors=float(row.prestige_priors),
        actionability=float(row.actionability),
        profile_fit=float(row.profile_fit),
        novelty_diversity=float(row.novelty_diversity),
        penalties=float(row.penalties),
        threshold_decision=row.threshold_decision,
        matched_rules=MatchedRuleGroups(positive=matched_rules, negative=[]),
        llm_rerank_delta=float(row.llm_rerank_delta),
        llm_rerank_reasons=rerank_reasons,
        created_at=row.score_created_at,
    )


def _serialize_paper(row) -> PaperOut:
    summary = row.one_line_summary or _summary_fallback(row.abstract)
    profile_labels = [row.profile_name] if row.profile_name else []

    return PaperOut(
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
        one_line_summary=summary,
        key_points=row.key_points or [],
        method_summary=row.method_summary,
        conclusion_summary=row.conclusion_summary,
        limitations=row.limitations,
        figure_descriptions=_figure_descriptions(row.figure_descriptions),
        profile_labels=profile_labels,
        score=_serialize_score(row) if row.score_id is not None else None,
    )


async def _get_paper_row(session: AsyncSession, paper_id: UUID, current_user: UserOut):
    enrichment = _latest_enrichment_subquery()
    score = _latest_score_subquery(current_user.workspace_id)
    row = (
        await session.execute(
            _paper_statement(current_user, enrichment=enrichment, score=score).where(Paper.id == paper_id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="paper_not_found", message="Paper not found.")
    return row


def _apply_date_window(statement, date_window: str):
    if date_window == "all":
        return statement

    cutoff = datetime.now(timezone.utc) - timedelta(hours=DATE_WINDOW_HOURS[date_window])
    return statement.where(Paper.published_at.is_not(None)).where(Paper.published_at >= cutoff)


@router.get("", response_model=PaginatedResponse[PaperOut])
async def list_papers(
    params: PaperListParams = Depends(),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PaperOut]:
    enrichment = _latest_enrichment_subquery()
    score = _latest_score_subquery(current_user.workspace_id)
    statement = _paper_statement(current_user, enrichment=enrichment, score=score).where(
        score.c.score_id.is_not(None)
    )

    if params.search:
        needle = f"%{params.search.strip()}%"
        statement = statement.where(
            Paper.title.ilike(needle)
            | Paper.abstract.ilike(needle)
            | Paper.authors.cast(Text).ilike(needle)
        )
    if params.category:
        statement = statement.where(Paper.categories.any(params.category))  # type: ignore[arg-type]
    if params.min_score is not None:
        statement = statement.where(score.c.total_score >= params.min_score)

    statement = _apply_date_window(statement, params.date_window)

    total = (await session.execute(select(func.count()).select_from(statement.subquery()))).scalar_one()

    if params.sort == "score_asc":
        statement = statement.order_by(
            score.c.total_score.asc().nullslast(),
            Paper.published_at.desc().nullslast(),
            Paper.created_at.desc(),
        )
    elif params.sort == "newest":
        statement = statement.order_by(Paper.published_at.desc().nullslast(), Paper.created_at.desc())
    elif params.sort == "oldest":
        statement = statement.order_by(Paper.published_at.asc().nullslast(), Paper.created_at.asc())
    else:
        statement = statement.order_by(
            score.c.total_score.desc().nullslast(),
            Paper.published_at.desc().nullslast(),
            Paper.created_at.desc(),
        )

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
    try:
        embedding_provider = create_embedding_provider()
        query_embedding = await embedding_provider.embed_text(q.strip())
    except SemanticSearchError as exc:
        raise APIError(
            status_code=503,
            code="semantic_search_unavailable",
            message=str(exc),
        ) from exc

    query_vector = vector_to_pgvector(query_embedding)
    distance = Paper.embedding.op("<=>")(
        cast(
            bindparam("query_embedding", query_vector),
            Vector(embedding_provider.dimensions),
        )
    )
    base_statement = _paper_statement(current_user).where(Paper.embedding.is_not(None))

    total = (
        await session.execute(
            select(func.count()).select_from(base_statement.subquery())
        )
    ).scalar_one()

    if total == 0:
        params = PaperListParams(page=page, per_page=per_page, search=q)
        return await list_papers(params, current_user, session)

    rows = (
        await session.execute(
            base_statement
            .add_columns(distance.label("distance"))
            .order_by(distance.asc(), Paper.published_at.desc(), Paper.created_at.desc())
            .params(query_embedding=query_vector)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
    ).all()

    return PaginatedResponse[PaperOut](
        items=[_serialize_paper(row) for row in rows],
        total=total,
        page=page,
        per_page=per_page,
    )


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
                Paper.id,
                PaperScore.id.label("score_id"),
                PaperScore.workspace_id.label("score_workspace_id"),
                PaperScore.profile_id.label("score_profile_id"),
                PaperScore.score_version.label("score_version"),
                PaperScore.total_score.label("total_score"),
                PaperScore.topical_relevance.label("topical_relevance"),
                PaperScore.prestige_priors.label("prestige_priors"),
                PaperScore.actionability.label("actionability"),
                PaperScore.profile_fit.label("profile_fit"),
                PaperScore.novelty_diversity.label("novelty_diversity"),
                PaperScore.penalties.label("penalties"),
                PaperScore.matched_rules.label("matched_rules"),
                PaperScore.threshold_decision.label("threshold_decision"),
                PaperScore.llm_rerank_delta.label("llm_rerank_delta"),
                PaperScore.llm_rerank_reasons.label("llm_rerank_reasons"),
                PaperScore.created_at.label("score_created_at"),
            )
            .join(Paper, Paper.id == PaperScore.paper_id)
            .where(PaperScore.paper_id == paper_id)
            .where(PaperScore.workspace_id == current_user.workspace_id)
            .order_by(PaperScore.created_at.desc())
        )
    ).all()

    return [_serialize_score(row) for row in rows]
