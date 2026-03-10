"""Worker runner tests."""

from __future__ import annotations

import asyncio

from workers.common.pipeline import Pipeline, PipelineStep
from workers.common.queue import InMemoryTaskQueue, TaskQueue
from workers.common.runner import WorkerRunner
from workers.common.task import TaskPayload, TaskResult, TaskStatus, TaskType


class SyncStep(PipelineStep):
    step_type = "sync"

    def __init__(self) -> None:
        super().__init__(max_attempts=1, timeout_seconds=1, backoff_base_seconds=0.0)

    async def execute(self, payload: dict[str, object]) -> dict[str, object]:
        return {"synced": payload["source"], "paper_count": 2}


class MatchStep(PipelineStep):
    step_type = "match"

    def __init__(self) -> None:
        super().__init__(max_attempts=1, timeout_seconds=1, backoff_base_seconds=0.0)

    async def execute(self, payload: dict[str, object]) -> dict[str, object]:
        return {"matched": payload["source"]}


class SpyQueue(TaskQueue):
    def __init__(self, tasks_by_type: dict[str, list[TaskPayload]]) -> None:
        super().__init__()
        self.tasks_by_type = tasks_by_type
        self.dequeue_calls: list[tuple[str, int]] = []
        self.acked: list[str] = []

    def enqueue(self, task: TaskPayload) -> str:
        self.tasks_by_type.setdefault(task.task_type.value, []).append(task)
        return str(task.task_id)

    def dequeue(self, task_type: str, timeout: int) -> TaskPayload | None:
        self.dequeue_calls.append((task_type, timeout))
        queue = self.tasks_by_type.get(task_type, [])
        return queue.pop(0) if queue else None

    def ack(self, task_id: str, result: TaskResult) -> None:
        self.acked.append(task_id)

    def nack(self, task_id: str, error: str) -> None:
        raise AssertionError(f"Unexpected nack for task {task_id}: {error}")

    def get_status(self, task_id: str) -> TaskStatus:
        return TaskStatus.COMPLETED



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



def test_worker_runner_only_blocks_once_per_cycle(sample_task) -> None:
    match_task = sample_task.model_copy(
        update={
            "task_type": TaskType.MATCH,
            "idempotency_key": "task-match-001",
        }
    )
    queue = SpyQueue({TaskType.MATCH.value: [match_task]})
    pipeline = Pipeline([SyncStep(), MatchStep()])
    runner = WorkerRunner(
        queue=queue,
        pipeline=pipeline,
        task_types=[TaskType.SYNC, TaskType.MATCH],
        poll_timeout=5,
        idle_sleep_seconds=0.0,
    )

    processed = asyncio.run(runner.run_once(timeout=5))

    assert processed is True
    assert queue.dequeue_calls == [(TaskType.SYNC.value, 5), (TaskType.MATCH.value, 0)]
    assert queue.acked == [str(match_task.task_id)]
