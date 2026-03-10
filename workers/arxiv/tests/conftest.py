from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from workers.arxiv.models import ArxivPaper, AuthorInfo, ScoringProfile


def _long_abstract(text: str) -> str:
    return (
        f"{text} "
        "We provide a detailed empirical study across multiple benchmarks, release code and evaluation "
        "artifacts, and analyze long-context behavior, robustness, and error patterns for modern "
        "language models in realistic retrieval-heavy settings."
    )


@pytest.fixture
def sample_profile() -> ScoringProfile:
    return ScoringProfile(
        name="nlp-watchlist",
        categories=["cs.CL", "cs.AI"],
        keywords=["language model", "retrieval", "reasoning", "benchmark"],
        themes=["long context", "agentic nlp"],
        tracked_authors=["Jane Doe"],
        negative_keywords=["protein folding"],
    )


@pytest.fixture
def high_signal_paper() -> ArxivPaper:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return ArxivPaper(
        arxiv_id="2503.12345",
        version=1,
        title="Long-Context Reasoning Agents for Retrieval-Augmented Language Models",
        abstract=_long_abstract(
            "We introduce a reasoning-centric framework for retrieval-augmented language models with "
            "benchmark-driven evaluation and transparent ablations."
        ),
        authors=[
            AuthorInfo(name="Jane Doe", affiliation="Department of Computer Science, Stanford University"),
            AuthorInfo(name="Alex Li", affiliation="OpenAI"),
        ],
        categories=["cs.CL", "cs.AI"],
        primary_category="cs.CL",
        comment="Code: https://github.com/scivly/retrieval-agents . Accepted to ACL 2026.",
        journal_ref=None,
        doi=None,
        published=now - timedelta(hours=8),
        updated=now - timedelta(hours=4),
    )


@pytest.fixture
def similar_same_day_paper() -> ArxivPaper:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return ArxivPaper(
        arxiv_id="2503.12346",
        version=1,
        title="Reasoning Agents for Retrieval-Augmented Language Models with Long Context",
        abstract=_long_abstract(
            "We study retrieval-augmented language models with long-context reasoning agents and "
            "benchmark analysis across several evaluation suites."
        ),
        authors=[
            AuthorInfo(name="Chris Kim", affiliation="Massachusetts Institute of Technology"),
        ],
        categories=["cs.CL", "cs.AI"],
        primary_category="cs.CL",
        comment="Project page: https://example.com/project",
        journal_ref=None,
        doi=None,
        published=now - timedelta(hours=7),
        updated=now - timedelta(hours=3),
    )


@pytest.fixture
def withdrawn_paper() -> ArxivPaper:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return ArxivPaper(
        arxiv_id="2503.20000",
        version=1,
        title="Withdrawn: A Preliminary Study on Language Models",
        abstract=_long_abstract(
            "This record has been withdrawn but still contains a long placeholder abstract for tests."
        ),
        authors=[AuthorInfo(name="Pat Example", affiliation="University of Somewhere")],
        categories=["cs.CL"],
        primary_category="cs.CL",
        comment="Withdrawn by the authors.",
        journal_ref=None,
        doi=None,
        published=now - timedelta(days=1),
        updated=now - timedelta(days=1),
    )


@pytest.fixture
def short_abstract_paper() -> ArxivPaper:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return ArxivPaper(
        arxiv_id="2503.30000",
        version=1,
        title="Efficient Prompt Compression",
        abstract="A short abstract.",
        authors=[AuthorInfo(name="Sam Example", affiliation="University of Somewhere")],
        categories=["cs.CL"],
        primary_category="cs.CL",
        comment=None,
        journal_ref=None,
        doi=None,
        published=now - timedelta(days=1),
        updated=now - timedelta(days=1),
    )


@pytest.fixture
def versioned_crosslist_papers(high_signal_paper: ArxivPaper) -> list[ArxivPaper]:
    newer = high_signal_paper.model_copy(
        update={
            "arxiv_id": "2503.12345v2",
            "version": 2,
            "categories": ["cs.CL", "cs.AI", "cs.IR"],
            "comment": "Code: https://github.com/scivly/retrieval-agents . Accepted to ACL 2026.",
        }
    )
    older = high_signal_paper.model_copy(
        update={
            "arxiv_id": "2503.12345v1",
            "version": 1,
            "categories": ["cs.CL", "cs.IR"],
            "updated": high_signal_paper.updated - timedelta(hours=2),
        }
    )
    return [older, newer]
