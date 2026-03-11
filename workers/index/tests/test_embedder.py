from __future__ import annotations

import asyncio
import math

from workers.index.embedder import HashEmbeddingProvider, build_paper_embedding_text


def test_hash_embedding_provider_is_deterministic() -> None:
    provider = HashEmbeddingProvider(dimensions=32)

    first = asyncio.run(provider.embed_text("Transformer attention mechanism for sequence modeling"))
    second = asyncio.run(provider.embed_text("Transformer attention mechanism for sequence modeling"))

    assert first == second
    assert len(first) == 32
    assert math.isclose(sum(value * value for value in first), 1.0, rel_tol=1e-6)


def test_build_paper_embedding_text_prefers_enrichment_fields() -> None:
    document = {
        "title": "Agentic Retrieval for Long-Horizon Scientific Planning",
        "abstract": "A retrieval stack for scientific planning.",
        "title_zh": "面向长周期科研规划的 Agentic Retrieval",
        "abstract_zh": "一个用于科研规划的检索系统。",
        "one_line_summary": "Combines search, critique, and synthesis for better planning.",
        "key_points": ["Profile-aware evidence selection", "Bounded retrieval cost"],
        "authors": [{"name": "Maya Chen"}],
        "categories": ["cs.CL", "cs.AI"],
    }

    rendered = build_paper_embedding_text(document)

    assert rendered.count("title: Agentic Retrieval for Long-Horizon Scientific Planning") == 3
    assert "title_zh: 面向长周期科研规划的 Agentic Retrieval" in rendered
    assert "summary: Combines search, critique, and synthesis for better planning." in rendered
    assert "key_point: Profile-aware evidence selection" in rendered
    assert "authors: Maya Chen" in rendered
