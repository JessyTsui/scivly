import asyncio
import os

import asyncpg
from fastapi.testclient import TestClient

from workers.index.embedder import HashEmbeddingProvider
from workers.index.steps import IndexPapersStep

PAPER_ID_WITH_ENRICHMENT = "00000000-0000-0000-0000-000000001001"


def _run_sql(statement: str) -> None:
    async def _execute() -> None:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"])
        try:
            await connection.execute(statement)
        finally:
            await connection.close()

    asyncio.run(_execute())


def test_public_papers_list_is_accessible_without_auth(client: TestClient) -> None:
    response = client.get("/public/papers", params={"per_page": 3})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 6
    assert payload["page"] == 1
    assert payload["per_page"] == 3
    assert len(payload["items"]) == 3
    assert "score" not in payload["items"][0]


def test_public_paper_detail_exposes_enrichment_and_figures(client: TestClient) -> None:
    response = client.get(f"/public/papers/{PAPER_ID_WITH_ENRICHMENT}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title_zh"] == "面向长程科研规划的代理式检索"
    assert payload["figures"] == [
        {
            "label": "Figure 2",
            "description": "End-to-end retrieval and planning loop with critique checkpoints.",
        }
    ]
    assert payload["one_line_summary"].startswith("An agentic retrieval loop improves scientific planning")


def test_public_papers_author_category_and_date_filters(client: TestClient) -> None:
    _run_sql(
        """
        INSERT INTO papers (
          id,
          arxiv_id,
          version,
          title,
          abstract,
          authors,
          categories,
          primary_category,
          published_at,
          updated_at,
          raw_metadata,
          created_at
        )
        VALUES (
          '00000000-0000-0000-0000-000000009801',
          '2603.99801',
          1,
          'Fresh Public Library Entry',
          'A synthetic paper inserted during tests to verify public date-window filtering.',
          '[{"name":"Recent Researcher","affiliation":"Scivly QA"}]'::jsonb,
          ARRAY['cs.AI'],
          'cs.AI',
          now(),
          now(),
          '{"source":"arXiv"}'::jsonb,
          now()
        );
        """
    )

    response = client.get(
        "/public/papers",
        params={
            "author": "Recent Researcher",
            "category": "cs.AI",
            "date_window": "24h",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == "00000000-0000-0000-0000-000000009801"


def test_public_semantic_search_returns_relevant_papers(client: TestClient) -> None:
    asyncio.run(
        IndexPapersStep(
            embedding_provider=HashEmbeddingProvider(),
        ).execute({"force": True})
    )

    response = client.get(
        "/public/papers/search",
        params={"q": "agentic scientific planning retrieval"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 6
    assert payload["items"]
    top_titles = [item["title"] for item in payload["items"][:5]]
    assert any("Agentic Retrieval" in title for title in top_titles)
