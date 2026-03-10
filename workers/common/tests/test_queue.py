"""Queue backend tests."""

from __future__ import annotations

from workers.common.queue import InMemoryTaskQueue
from workers.common.task import TaskResult, TaskResultStatus, TaskStatus


def test_inmemory_queue_ack_flow(sample_task) -> None:
    queue = InMemoryTaskQueue()

    task_id = queue.enqueue(sample_task)
    assert queue.get_status(task_id) is TaskStatus.QUEUED

    dequeued = queue.dequeue(sample_task.task_type.value, timeout=0)
    assert dequeued is not None
    assert dequeued.task_id == sample_task.task_id
    assert queue.get_status(task_id) is TaskStatus.RUNNING

    result = TaskResult(
        task_id=sample_task.task_id,
        status=TaskResultStatus.COMPLETED,
        result={"synced": 4},
        duration_ms=12,
    )
    queue.ack(task_id, result)

    assert queue.get_status(task_id) is TaskStatus.COMPLETED
    assert queue.get_result(task_id) == result


def test_inmemory_queue_nack_requeues_then_dead_letters(sample_task) -> None:
    queue = InMemoryTaskQueue(max_attempts=2)
    task_id = queue.enqueue(sample_task)

    first = queue.dequeue(sample_task.task_type.value, timeout=0)
    assert first is not None
    queue.nack(task_id, "temporary failure")

    assert queue.get_status(task_id) is TaskStatus.QUEUED
    assert queue.get_attempts(task_id) == 1
    assert queue.get_last_error(task_id) == "temporary failure"

    second = queue.dequeue(sample_task.task_type.value, timeout=0)
    assert second is not None
    queue.nack(task_id, "permanent failure")

    assert queue.get_status(task_id) is TaskStatus.DEAD
    assert queue.get_attempts(task_id) == 2
    assert queue.dequeue(sample_task.task_type.value, timeout=0) is None
