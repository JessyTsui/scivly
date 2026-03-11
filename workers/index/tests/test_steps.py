from __future__ import annotations

import asyncio
from collections.abc import Sequence
from uuid import uuid4

from workers.index.embedder import HashEmbeddingProvider
from workers.index.steps import IndexPapersStep, IndexablePaper, PaperEmbeddingRecord


class InMemoryEmbeddingStore:
    def __init__(self, papers: list[IndexablePaper]) -> None:
        self.papers = papers
        self.fetch_calls: list[dict[str, object]] = []
        self.persisted: list[PaperEmbeddingRecord] = []

    async def fetch_papers(
        self,
        *,
        paper_ids=None,
        limit=None,
        force=False,
    ) -> list[IndexablePaper]:
        self.fetch_calls.append(
            {
                "paper_ids": list(paper_ids) if paper_ids else None,
                "limit": limit,
                "force": force,
            }
        )
        filtered = self.papers
        if paper_ids:
            filtered = [paper for paper in filtered if paper.paper_id in set(paper_ids)]
        if limit is not None:
            filtered = filtered[:limit]
        return filtered

    async def persist_embeddings(self, records: Sequence[PaperEmbeddingRecord]) -> int:
        self.persisted.extend(records)
        return len(records)


def test_index_papers_step_embeds_and_persists_requested_papers() -> None:
    first_id = uuid4()
    second_id = uuid4()
    store = InMemoryEmbeddingStore(
        [
            IndexablePaper(
                paper_id=first_id,
                title="Sparse Transformer Attention Mechanisms",
                abstract="A paper about transformer attention mechanisms.",
                authors=[{"name": "Jessy"}],
                categories=["cs.LG"],
                one_line_summary="Improves efficient sequence attention.",
                key_points=["Windowed attention", "Lower memory use"],
            ),
            IndexablePaper(
                paper_id=second_id,
                title="Robot Policy Distillation",
                abstract="A paper about robot policies.",
                authors=[{"name": "Ada"}],
                categories=["cs.RO"],
            ),
        ]
    )
    step = IndexPapersStep(
        embedding_provider=HashEmbeddingProvider(dimensions=64),
        store=store,
        batch_size=1,
    )

    result = asyncio.run(step.execute({"paper_ids": [str(first_id)]}))

    assert result["indexed_count"] == 1
    assert result["indexed_paper_ids"] == [str(first_id)]
    assert store.fetch_calls == [{"paper_ids": [first_id], "limit": None, "force": False}]
    assert len(store.persisted) == 1
    assert store.persisted[0].paper_id == first_id
    assert len(store.persisted[0].vector) == 64
