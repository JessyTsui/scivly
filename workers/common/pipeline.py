"""Pipeline framework for retryable worker steps."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from time import perf_counter
from typing import Any, Iterable, Mapping, Protocol, Sequence

from .queue import normalize_task_type
from .task import TaskPayload, TaskResult, TaskResultStatus, TaskType

DEFAULT_STATUS_FLOW = tuple(task_type.value for task_type in TaskType)


class PipelineExecutionError(RuntimeError):
    """Raised when a pipeline step exhausts its retries."""

    def __init__(self, *, step_type: str, task_id: str, error: str, attempts: int) -> None:
        self.step_type = step_type
        self.task_id = task_id
        self.error = error
        self.attempts = attempts
        super().__init__(
            f"Step {step_type} failed for task {task_id} after {attempts} attempts: {error}"
        )


class IdempotencyStore:
    """Simple in-memory idempotency cache keyed by step type and idempotency key."""

    def __init__(self) -> None:
        self._results: dict[str, TaskResult] = {}

    def get(self, step_type: str, idempotency_key: str) -> TaskResult | None:
        result = self._results.get(self._key(step_type, idempotency_key))
        return result.model_copy(deep=True) if result else None

    def set(self, step_type: str, idempotency_key: str, result: TaskResult) -> None:
        self._results[self._key(step_type, idempotency_key)] = result.model_copy(deep=True)

    @staticmethod
    def _key(step_type: str, idempotency_key: str) -> str:
        return f"{step_type}:{idempotency_key}"


class PipelineEventEmitter(Protocol):
    async def emit(
        self,
        *,
        event_type: str,
        task: TaskPayload,
        payload: Mapping[str, Any],
    ) -> None: ...


class PipelineStep(ABC):
    """Base class for a retryable, timeout-aware pipeline step."""

    step_type: str | TaskType
    emitted_events: Sequence[str] = ()
    max_attempts: int = 3
    timeout_seconds: float = 300
    backoff_base_seconds: float = 1.0

    def __init__(
        self,
        *,
        max_attempts: int | None = None,
        timeout_seconds: float | None = None,
        backoff_base_seconds: float | None = None,
    ) -> None:
        if max_attempts is not None:
            self.max_attempts = max_attempts
        if timeout_seconds is not None:
            self.timeout_seconds = timeout_seconds
        if backoff_base_seconds is not None:
            self.backoff_base_seconds = backoff_base_seconds
        self._idempotency_store = IdempotencyStore()

    @property
    def normalized_step_type(self) -> str:
        return normalize_task_type(self.step_type)

    @property
    def idempotency_scope(self) -> str:
        return f"{self.normalized_step_type}:{self.__class__.__name__}"

    def bind_idempotency_store(self, store: IdempotencyStore) -> None:
        self._idempotency_store = store

    async def run(self, task: TaskPayload, payload: Mapping[str, Any] | None = None) -> TaskResult:
        cached = self._idempotency_store.get(
            self.idempotency_scope,
            task.idempotency_key,
        )
        if cached is not None:
            return cached

        execution_payload = dict(task.payload)
        if payload is not None:
            execution_payload.update(payload)
        execution_payload.setdefault("task_id", task.task_id)
        execution_payload.setdefault("task_type", normalize_task_type(task.task_type))
        execution_payload.setdefault("workspace_id", task.workspace_id)
        execution_payload.setdefault("idempotency_key", task.idempotency_key)
        if task.paper_id is not None:
            execution_payload.setdefault("paper_id", task.paper_id)
        last_error = "Unknown pipeline error"

        for attempt in range(1, self.max_attempts + 1):
            started_at = perf_counter()
            try:
                result_payload = await asyncio.wait_for(
                    self.execute(execution_payload),
                    timeout=self.timeout_seconds,
                )
                duration_ms = int((perf_counter() - started_at) * 1000)
                task_result = TaskResult(
                    task_id=task.task_id,
                    status=TaskResultStatus.COMPLETED,
                    result=result_payload,
                    cost=self.calculate_cost(result_payload),
                    duration_ms=duration_ms,
                )
                self._idempotency_store.set(
                    self.idempotency_scope,
                    task.idempotency_key,
                    task_result,
                )
                return task_result
            except asyncio.TimeoutError:
                last_error = (
                    f"Step {self.normalized_step_type} timed out after {self.timeout_seconds} seconds"
                )
            except Exception as exc:
                last_error = str(exc)

            if attempt < self.max_attempts:
                await asyncio.sleep(self.backoff_base_seconds * (2 ** (attempt - 1)))

        raise PipelineExecutionError(
            step_type=self.normalized_step_type,
            task_id=str(task.task_id),
            error=last_error,
            attempts=self.max_attempts,
        )

    def calculate_cost(self, result: Mapping[str, Any]) -> float:
        """Hook for worker steps that need to record runtime cost."""

        cost = result.get("cost")
        if isinstance(cost, (int, float)):
            return float(cost)
        return 0.0

    def build_emitted_event_payload(
        self,
        task: TaskPayload,
        execution_state: Mapping[str, Any],
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "task_id": str(task.task_id),
            "task_type": normalize_task_type(task.task_type),
            "workspace_id": str(task.workspace_id),
            "idempotency_key": task.idempotency_key,
            "step": self.__class__.__name__,
            "state": dict(execution_state),
            "result": dict(result),
        }
        if task.paper_id is not None:
            payload["paper_id"] = str(task.paper_id)
        return payload

    @abstractmethod
    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute the concrete step."""


class Pipeline:
    """Coordinator that dispatches registered steps for each task type."""

    def __init__(
        self,
        steps: Iterable[PipelineStep],
        *,
        status_flow: Sequence[str | TaskType] | None = None,
        idempotency_store: IdempotencyStore | None = None,
        event_emitter: PipelineEventEmitter | None = None,
    ) -> None:
        self.status_flow = tuple(
            normalize_task_type(step_type)
            for step_type in (status_flow or DEFAULT_STATUS_FLOW)
        )
        self.idempotency_store = idempotency_store or IdempotencyStore()
        self.event_emitter = event_emitter
        self._steps_by_type: dict[str, list[PipelineStep]] = defaultdict(list)

        for step in steps:
            step.bind_idempotency_store(self.idempotency_store)
            self._steps_by_type[step.normalized_step_type].append(step)

    def next_task_type(self, task_type: str | TaskType) -> str | None:
        normalized = normalize_task_type(task_type)
        try:
            current_index = self.status_flow.index(normalized)
        except ValueError:
            return None

        next_index = current_index + 1
        if next_index >= len(self.status_flow):
            return None
        return self.status_flow[next_index]

    async def execute_task(self, task: TaskPayload) -> TaskResult:
        task_type = normalize_task_type(task.task_type)
        steps = self._steps_by_type.get(task_type)
        if not steps:
            raise KeyError(f"No pipeline steps registered for task type {task_type}")

        execution_state = dict(task.payload)
        step_results: dict[str, dict[str, Any]] = {}
        total_cost = 0.0
        total_duration_ms = 0
        event_dispatch_errors: list[dict[str, str]] = []

        for step in steps:
            result = await step.run(task, execution_state)
            execution_state.update(result.result)
            step_results[step.__class__.__name__] = result.result
            total_cost += result.cost
            total_duration_ms += result.duration_ms

            if self.event_emitter and step.emitted_events:
                event_payload = step.build_emitted_event_payload(task, execution_state, result.result)
                for event_type in step.emitted_events:
                    try:
                        await self.event_emitter.emit(
                            event_type=event_type,
                            task=task,
                            payload=event_payload,
                        )
                    except Exception as exc:
                        event_dispatch_errors.append({"event_type": event_type, "error": str(exc)})

        return TaskResult(
            task_id=task.task_id,
            status=TaskResultStatus.COMPLETED,
            result={
                "steps": step_results,
                "final": execution_state,
                "next_task_type": self.next_task_type(task_type),
                "event_dispatch_errors": event_dispatch_errors,
            },
            cost=total_cost,
            duration_ms=total_duration_ms,
        )

    async def run_flow(self, task: TaskPayload) -> list[TaskResult]:
        """Run every registered step from the current task type onward."""

        results: list[TaskResult] = []
        execution_state = dict(task.payload)
        current_type = normalize_task_type(task.task_type)

        try:
            start_index = self.status_flow.index(current_type)
        except ValueError:
            start_index = 0

        for task_type in self.status_flow[start_index:]:
            if task_type not in self._steps_by_type:
                continue
            current_task = task.model_copy(update={"task_type": TaskType(task_type), "payload": execution_state})
            result = await self.execute_task(current_task)
            execution_state = result.result["final"]
            results.append(result)

        return results
