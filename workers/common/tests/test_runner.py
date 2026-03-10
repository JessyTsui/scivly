"""Worker runner tests."""

from __future__ import annotations

import asyncio

from workers.common.pipeline import Pipeline, PipelineStep
from workers.common.queue import InMemoryTaskQueue
from workers.common.runner import WorkerRunner
from workers.common.task import TaskStatus


class SyncStep(PipelineStep):
    step_type = "sync"

    def __init__(self) -> None:
        super().__init__(max_attempts=1, timeout_seconds=1, backoff_base_seconds=0.0)

    async def execute(self, payload: dict[str, object]) -> dict[str, object]:
        return {"synced": payload["source"], "paper_count": 2}


def test_worker_runner_polls_and_dispatches(sample_task) -> None:
    queue = InMemoryTaskQueue()
    pipeline = Pipeline([SyncStep()])
    runner = WorkerRunner(
        queue=queue,
        pipeline=pipeline,
        task_types=[sample_task.task_type],
        poll_timeout=0,
        idle_sleep_seconds=0.0,
    )

    task_id = queue.enqueue(sample_task)
    processed = asyncio.run(runner.run_once(timeout=0))

    assert processed is True
    assert queue.get_status(task_id) is TaskStatus.COMPLETED

    result = queue.get_result(task_id)
    assert result is not None
    assert result.result["final"]["synced"] == "arxiv"
