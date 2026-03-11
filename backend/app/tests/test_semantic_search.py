from __future__ import annotations

import asyncio

import httpx
import pytest

from app.semantic_search import OpenAIEmbeddingProvider, SemanticSearchError, build_paper_embedding_text


def test_build_paper_embedding_text_skips_none_fields() -> None:
    rendered = build_paper_embedding_text(
        {
            "title": "Transformer Attention",
            "abstract": "Attention over long sequences.",
            "title_zh": None,
            "abstract_zh": None,
            "one_line_summary": None,
        }
    )

    assert "None" not in rendered
    assert "title_zh:" not in rendered
    assert "summary:" not in rendered


def test_openai_embedding_provider_wraps_httpx_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, *args, **kwargs):
            raise httpx.ReadTimeout("upstream timeout")

    monkeypatch.setattr(httpx, "AsyncClient", FailingAsyncClient)
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        api_base="https://example.com/v1",
        dimensions=8,
    )

    with pytest.raises(SemanticSearchError, match="Embedding provider request failed"):
        asyncio.run(provider.embed_text("query"))
