from collections.abc import Callable
import asyncio
import os

import asyncpg
from fastapi.testclient import TestClient


def _run_sql(statement: str) -> None:
    async def _execute() -> None:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"])
        try:
            await connection.execute(statement)
        finally:
            await connection.close()

    asyncio.run(_execute())


def test_usage_rejects_other_workspace_ids(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    response = client.get(
        "/usage",
        params={"workspace_id": "00000000-0000-0000-0000-000000009999"},
        headers=auth_headers(
            local_user_id="00000000-0000-0000-0000-000000000101",
            workspace_id="00000000-0000-0000-0000-000000000201",
        ),
    )

    assert response.status_code == 403
    assert response.json()["error"] == "workspace_access_denied"


def test_create_chat_session_returns_404_for_unknown_paper(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    response = client.post(
        "/chat/sessions",
        json={
            "workspace_id": "00000000-0000-0000-0000-000000000201",
            "paper_id": "00000000-0000-0000-0000-000000009999",
            "session_type": "paper_qa",
            "title": "Missing paper",
        },
        headers=auth_headers(
            local_user_id="00000000-0000-0000-0000-000000000101",
            workspace_id="00000000-0000-0000-0000-000000000201",
        ),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "paper_not_found"


def test_digest_preview_returns_unique_paper_ids(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    _run_sql(
        """
        INSERT INTO paper_scores (
          id,
          paper_id,
          workspace_id,
          profile_id,
          score_version,
          total_score,
          topical_relevance,
          prestige_priors,
          actionability,
          profile_fit,
          novelty_diversity,
          penalties,
          matched_rules,
          threshold_decision,
          llm_rerank_delta,
          llm_rerank_reasons,
          created_at
        )
        VALUES (
          '00000000-0000-0000-0000-000000009901',
          '00000000-0000-0000-0000-000000001001',
          '00000000-0000-0000-0000-000000000201',
          '00000000-0000-0000-0000-000000000302',
          'v2',
          83.00,
          38.00,
          12.00,
          11.00,
          9.00,
          8.00,
          -1.00,
          '[]'::jsonb,
          'digest_candidate',
          2.00,
          '[]'::jsonb,
          '2026-03-02T05:00:00Z'
        );
        """
    )

    response = client.post(
        "/digests/preview",
        json={
            "workspace_id": "00000000-0000-0000-0000-000000000201",
            "period_start": "2026-03-01T00:00:00Z",
            "period_end": "2026-03-07T23:59:59Z",
            "limit": 5,
        },
        headers=auth_headers(
            local_user_id="00000000-0000-0000-0000-000000000101",
            workspace_id="00000000-0000-0000-0000-000000000201",
        ),
    )

    assert response.status_code == 200
    paper_ids = response.json()["paper_ids"]
    assert len(paper_ids) == len(set(paper_ids))
