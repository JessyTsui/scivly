from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.deps import get_current_user
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut
from app.schemas.common import PaginatedResponse
from app.schemas.paper import PaperAuthor, PaperListParams, PaperOut, PaperScoreOut

router = APIRouter(prefix="/papers", tags=["Papers"])

PAPERS = {
    UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"): PaperOut(
        id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        arxiv_id="2603.01234",
        version=1,
        title="Coordinating Long-Horizon Tool Agents with Sparse Self-Critique",
        abstract="We present a metadata-first agent framework for long-horizon research tasks.",
        authors=[
            PaperAuthor(name="Alex Chen", affiliation="Scivly Research"),
            PaperAuthor(name="Mina Park", affiliation="Open Systems Lab"),
        ],
        categories=["cs.AI", "cs.CL"],
        primary_category="cs.AI",
        published_at=datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 3, 9, 4, 0, tzinfo=timezone.utc),
        comment="8 pages, 4 figures, code forthcoming",
        doi=None,
        one_line_summary="A practical control loop for research agents that only escalates expensive steps when needed.",
    ),
    UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"): PaperOut(
        id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        arxiv_id="2603.04567",
        version=2,
        title="Benchmarking Vision-Language Policies for Low-Latency Robotics",
        abstract="We benchmark VLA policies across latency-sensitive tabletop manipulation tasks.",
        authors=[
            PaperAuthor(name="Jordan Lee", affiliation="Robotics Institute"),
            PaperAuthor(name="Priya Raman", affiliation="Embodied Intelligence Lab"),
        ],
        categories=["cs.RO", "cs.CV"],
        primary_category="cs.RO",
        published_at=datetime(2026, 3, 7, 10, 15, tzinfo=timezone.utc),
        updated_at=datetime(2026, 3, 8, 2, 0, tzinfo=timezone.utc),
        comment="Project page available",
        doi="10.48550/arXiv.2603.04567",
        one_line_summary="Latency-aware evaluation reveals where current VLA policies break under deployment constraints.",
    ),
}

PAPER_SCORES = {
    UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"): [
        PaperScoreOut(
            id=UUID("abababab-abab-abab-abab-abababababab"),
            paper_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            workspace_id=UUID("22222222-2222-2222-2222-222222222222"),
            profile_id=UUID("55555555-5555-5555-5555-555555555555"),
            score_version="v0.1.0",
            total_score=78.0,
            topical_relevance=38.0,
            prestige_priors=9.0,
            actionability=12.0,
            profile_fit=9.0,
            novelty_diversity=8.0,
            penalties=2.0,
            threshold_decision="digest_candidate",
            matched_rules=["keyword:tool use", "category:cs.AI", "comment:code forthcoming"],
            llm_rerank_delta=4.0,
            llm_rerank_reasons=["Abstract clearly distinguishes planner and executor roles."],
            created_at=datetime(2026, 3, 9, 5, 30, tzinfo=timezone.utc),
        )
    ],
    UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"): [
        PaperScoreOut(
            id=UUID("cdcdcdcd-cdcd-cdcd-cdcd-cdcdcdcdcdcd"),
            paper_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            workspace_id=UUID("22222222-2222-2222-2222-222222222222"),
            profile_id=UUID("66666666-6666-6666-6666-666666666666"),
            score_version="v0.1.0",
            total_score=71.0,
            topical_relevance=34.0,
            prestige_priors=11.0,
            actionability=11.0,
            profile_fit=8.0,
            novelty_diversity=9.0,
            penalties=2.0,
            threshold_decision="rerank",
            matched_rules=["keyword:policy learning", "category:cs.RO", "comment:project page"],
            llm_rerank_delta=2.0,
            llm_rerank_reasons=["Benchmark coverage maps well to robotics monitoring profile."],
            created_at=datetime(2026, 3, 8, 6, 0, tzinfo=timezone.utc),
        )
    ],
}


def _get_paper(paper_id: UUID) -> PaperOut:
    paper = PAPERS.get(paper_id)
    if paper is None:
        raise APIError(status_code=404, code="paper_not_found", message="Paper not found.")
    return paper


@router.get("", response_model=PaginatedResponse[PaperOut])
def list_papers(
    params: PaperListParams = Depends(),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[PaperOut]:
    items = list(PAPERS.values())
    if params.query:
        needle = params.query.lower()
        items = [
            paper
            for paper in items
            if needle in paper.title.lower() or needle in paper.abstract.lower()
        ]
    if params.category:
        items = [paper for paper in items if params.category in paper.categories]
    if params.sort == "published_at":
        items = sorted(items, key=lambda paper: paper.published_at, reverse=True)
    else:
        items = sorted(
            items,
            key=lambda paper: PAPER_SCORES.get(paper.id, [])[0].total_score if PAPER_SCORES.get(paper.id) else 0,
            reverse=True,
        )

    start = (params.page - 1) * params.per_page
    end = start + params.per_page
    return PaginatedResponse[PaperOut](
        items=items[start:end],
        total=len(items),
        page=params.page,
        per_page=params.per_page,
    )


@router.get("/search", response_model=PaginatedResponse[PaperOut])
def search_papers(
    q: str = Query(min_length=2, max_length=160),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[PaperOut]:
    params = PaperListParams(page=page, per_page=per_page, query=q)
    return list_papers(params, _)


@router.get("/{paper_id}", response_model=PaperOut)
def get_paper(paper_id: UUID, _: UserOut = Depends(get_current_user)) -> PaperOut:
    return _get_paper(paper_id)


@router.get("/{paper_id}/scores", response_model=list[PaperScoreOut])
def get_paper_scores(paper_id: UUID, _: UserOut = Depends(get_current_user)) -> list[PaperScoreOut]:
    _get_paper(paper_id)
    return PAPER_SCORES.get(paper_id, [])
