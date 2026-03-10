"""Pipeline retry, timeout, and idempotency tests."""

from __future__ import annotations

import asyncio

import pytest

from workers.common.pipeline import PipelineExecutionError, PipelineStep


class FlakyStep(PipelineStep):
    step_type = "sync"

    def __init__(self) -> None:
        super().__init__(max_attempts=3, timeout_seconds=1, backoff_base_seconds=0.0)
        self.calls = 0

    async def execute(self, payload: dict[str, object]) -> dict[str, object]:
        self.calls += 1
        if self.calls < 3:
            raise ValueError("try again")
        return {"attempts": self.calls}


class SlowStep(PipelineStep):
    step_type = "sync"

    def __init__(self) -> None:
        super().__init__(max_attempts=2, timeout_seconds=0.01, backoff_base_seconds=0.0)
        self.calls = 0

    async def execute(self, payload: dict[str, object]) -> dict[str, object]:
        self.calls += 1
        await asyncio.sleep(0.05)
        return {"slow": True}


class CountingStep(PipelineStep):
    step_type = "sync"

    def __init__(self) -> None:
        super().__init__(max_attempts=2, timeout_seconds=1, backoff_base_seconds=0.0)
        self.calls = 0

    async def execute(self, payload: dict[str, object]) -> dict[str, object]:
        self.calls += 1
        return {"call_count": self.calls, "echo": payload.get("source")}


def test_pipeline_step_retries_until_success(sample_task) -> None:
    step = FlakyStep()

    result = asyncio.run(step.run(sample_task))

    assert result.result == {"attempts": 3}
    assert step.calls == 3


def test_pipeline_step_times_out_after_retry_budget(sample_task) -> None:
    step = SlowStep()

    with pytest.raises(PipelineExecutionError) as exc:
        asyncio.run(step.run(sample_task))

    assert "timed out" in str(exc.value)
    assert step.calls == 2


def test_pipeline_step_uses_idempotency_cache(sample_task) -> None:
    step = CountingStep()

    first = asyncio.run(step.run(sample_task))
    second = asyncio.run(step.run(sample_task))

    assert first == second
    assert step.calls == 1
