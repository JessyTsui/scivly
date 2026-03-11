from __future__ import annotations

import asyncio
import importlib
import math
import sys

import httpx
import pytest

from workers.index.embedder import (
    EmbeddingProviderError,
    HashEmbeddingProvider,
    OpenAIEmbeddingProvider,
    build_paper_embedding_text,
)


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


def test_build_paper_embedding_text_skips_none_fields() -> None:
    rendered = build_paper_embedding_text(
        {
            "title": "Vector Retrieval for Papers",
            "abstract": "Semantic retrieval for papers.",
            "title_zh": None,
            "abstract_zh": None,
            "one_line_summary": None,
            "authors": [{"name": "Jessy"}],
            "categories": ["cs.IR"],
        }
    )

    assert "None" not in rendered
    assert "title_zh:" not in rendered
    assert "summary:" not in rendered


def test_openai_embedding_provider_wraps_transport_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, *args, **kwargs):
            raise httpx.ConnectError("boom")

    monkeypatch.setattr(httpx, "AsyncClient", FailingAsyncClient)
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        api_base="https://example.com/v1",
        dimensions=8,
    )

    with pytest.raises(EmbeddingProviderError, match="Embedding provider request failed"):
        asyncio.run(provider.embed_text("query"))


def test_workers_index_package_lazy_loads_steps() -> None:
    sys.modules.pop("workers.index", None)
    sys.modules.pop("workers.index.steps", None)

    module = importlib.import_module("workers.index")

    assert "workers.index.steps" not in sys.modules
    assert module.HashEmbeddingProvider is not None
    assert "workers.index.steps" not in sys.modules

    assert module.IndexPapersStep is not None
    assert "workers.index.steps" in sys.modules
