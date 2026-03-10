"""Fixtures for worker infrastructure tests."""

from __future__ import annotations

from uuid import uuid4

import pytest

from workers.common.task import TaskPayload, TaskType


@pytest.fixture
def sample_task() -> TaskPayload:
    return TaskPayload(
        task_type=TaskType.SYNC,
        workspace_id=uuid4(),
        paper_id=uuid4(),
        idempotency_key="task-sync-001",
        payload={"source": "arxiv", "categories": ["cs.CL"]},
    )
