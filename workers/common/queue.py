"""Queue backends for worker task execution."""

from __future__ import annotations

import json
import os
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Condition
from typing import Deque

from redis import Redis

from .task import TaskPayload, TaskResult, TaskStatus, TaskType

DEFAULT_REDIS_URL = "redis://localhost:6399/0"


def normalize_task_type(task_type: str | TaskType) -> str:
    if isinstance(task_type, TaskType):
        return task_type.value
    return task_type


@dataclass(slots=True)
class QueueEntry:
    task: TaskPayload
    status: TaskStatus = TaskStatus.QUEUED
    attempts: int = 0
    last_error: str | None = None
    result: TaskResult | None = None


class TaskQueue(ABC):
    """Abstract interface for queue backends."""

    def __init__(self, *, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts

    @abstractmethod
    def enqueue(self, task: TaskPayload) -> str:
        """Store a task and enqueue it for execution."""

    @abstractmethod
    def dequeue(self, task_type: str, timeout: int) -> TaskPayload | None:
        """Return the next queued task for the given type, or None on timeout."""

    @abstractmethod
    def ack(self, task_id: str, result: TaskResult) -> None:
        """Mark a task as completed."""

    @abstractmethod
    def nack(self, task_id: str, error: str) -> None:
        """Record a failure, retry the task, or move it to dead-letter state."""

    @abstractmethod
    def get_status(self, task_id: str) -> TaskStatus:
        """Return the current status for a task."""


class InMemoryTaskQueue(TaskQueue):
    """In-memory queue backend for local development and tests."""

    def __init__(self, *, max_attempts: int = 3) -> None:
        super().__init__(max_attempts=max_attempts)
        self._entries: dict[str, QueueEntry] = {}
        self._queues: dict[str, Deque[str]] = defaultdict(deque)
        self._condition = Condition()

    def enqueue(self, task: TaskPayload) -> str:
        task_id = str(task.task_id)
        task_type = normalize_task_type(task.task_type)

        with self._condition:
            self._entries[task_id] = QueueEntry(task=task)
            self._queues[task_type].append(task_id)
            self._condition.notify_all()
        return task_id

    def dequeue(self, task_type: str, timeout: int) -> TaskPayload | None:
        queue_name = normalize_task_type(task_type)
        deadline = time.monotonic() + max(timeout, 0)

        with self._condition:
            while not self._queues[queue_name]:
                remaining = deadline - time.monotonic()
                if timeout <= 0 or remaining <= 0:
                    return None
                self._condition.wait(timeout=remaining)

            task_id = self._queues[queue_name].popleft()
            entry = self._require_entry(task_id)
            entry.status = TaskStatus.RUNNING
            return entry.task.model_copy(deep=True)

    def ack(self, task_id: str, result: TaskResult) -> None:
        with self._condition:
            entry = self._require_entry(task_id)
            entry.result = result
            entry.last_error = result.error
            entry.status = (
                TaskStatus.COMPLETED
                if result.status.value == TaskStatus.COMPLETED.value
                else TaskStatus.FAILED
            )
            self._condition.notify_all()

    def nack(self, task_id: str, error: str) -> None:
        with self._condition:
            entry = self._require_entry(task_id)
            entry.attempts += 1
            entry.last_error = error

            if entry.attempts >= self.max_attempts:
                entry.status = TaskStatus.DEAD
            else:
                entry.status = TaskStatus.QUEUED
                self._queues[normalize_task_type(entry.task.task_type)].append(task_id)
                self._condition.notify_all()

    def get_status(self, task_id: str) -> TaskStatus:
        return self._require_entry(task_id).status

    def get_attempts(self, task_id: str) -> int:
        return self._require_entry(task_id).attempts

    def get_result(self, task_id: str) -> TaskResult | None:
        return self._require_entry(task_id).result

    def get_last_error(self, task_id: str) -> str | None:
        return self._require_entry(task_id).last_error

    def _require_entry(self, task_id: str) -> QueueEntry:
        try:
            return self._entries[task_id]
        except KeyError as exc:
            raise KeyError(f"Task {task_id} was not found") from exc


class RedisTaskQueue(TaskQueue):
    """Redis-backed queue with task metadata tracked in hashes."""

    def __init__(
        self,
        *,
        redis_url: str | None = None,
        max_attempts: int = 3,
        prefix: str = "scivly",
    ) -> None:
        super().__init__(max_attempts=max_attempts)
        self.redis_url = redis_url or os.getenv("REDIS_URL", DEFAULT_REDIS_URL)
        self.prefix = prefix
        self.client = Redis.from_url(self.redis_url, decode_responses=True)

    def enqueue(self, task: TaskPayload) -> str:
        task_id = str(task.task_id)
        task_type = normalize_task_type(task.task_type)
        self.client.hset(
            self._task_key(task_id),
            mapping={
                "payload": task.model_dump_json(),
                "status": TaskStatus.QUEUED.value,
                "attempts": 0,
                "last_error": "",
                "result": "",
                "task_type": task_type,
            },
        )
        self.client.rpush(self._queue_key(task_type), task_id)
        return task_id

    def dequeue(self, task_type: str, timeout: int) -> TaskPayload | None:
        queue_name = self._queue_key(task_type)
        if timeout <= 0:
            task_id = self.client.lpop(queue_name)
            response = (queue_name, task_id) if task_id is not None else None
        else:
            response = self.client.blpop(queue_name, timeout=timeout)
        if response is None:
            return None

        _, task_id = response
        task_key = self._task_key(task_id)
        payload = self.client.hget(task_key, "payload")
        if payload is None:
            return None

        self.client.hset(task_key, mapping={"status": TaskStatus.RUNNING.value})
        return TaskPayload.model_validate_json(payload)

    def ack(self, task_id: str, result: TaskResult) -> None:
        self.client.hset(
            self._task_key(task_id),
            mapping={
                "status": TaskStatus.COMPLETED.value,
                "result": result.model_dump_json(),
                "last_error": result.error or "",
            },
        )

    def nack(self, task_id: str, error: str) -> None:
        task_key = self._task_key(task_id)
        attempts = int(self.client.hincrby(task_key, "attempts", 1))
        task_type = self.client.hget(task_key, "task_type")
        if task_type is None:
            raise KeyError(f"Task {task_id} was not found")

        if attempts >= self.max_attempts:
            self.client.hset(
                task_key,
                mapping={"status": TaskStatus.DEAD.value, "last_error": error},
            )
            self.client.rpush(self._dead_letter_key(task_type), task_id)
            return

        self.client.hset(
            task_key,
            mapping={"status": TaskStatus.QUEUED.value, "last_error": error},
        )
        self.client.rpush(self._queue_key(task_type), task_id)

    def get_status(self, task_id: str) -> TaskStatus:
        status = self.client.hget(self._task_key(task_id), "status")
        if status is None:
            raise KeyError(f"Task {task_id} was not found")
        return TaskStatus(status)

    def _task_key(self, task_id: str) -> str:
        return f"{self.prefix}:task:{task_id}"

    def _queue_key(self, task_type: str | TaskType) -> str:
        return f"{self.prefix}:queue:{normalize_task_type(task_type)}"

    def _dead_letter_key(self, task_type: str | TaskType) -> str:
        return f"{self.prefix}:dead:{normalize_task_type(task_type)}"


def build_task_queue(
    *,
    backend: str | None = None,
    redis_url: str | None = None,
    max_attempts: int = 3,
) -> TaskQueue:
    selected_backend = (backend or os.getenv("SCIVLY_QUEUE_BACKEND", "memory")).lower()
    if selected_backend == "memory":
        return InMemoryTaskQueue(max_attempts=max_attempts)
    if selected_backend == "redis":
        return RedisTaskQueue(redis_url=redis_url, max_attempts=max_attempts)
    raise ValueError(
        "Unsupported queue backend. Expected one of: memory, redis."
    )
