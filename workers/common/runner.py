"""Worker runner and CLI for polling task queues."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
from typing import Iterable

from .pipeline import Pipeline, PipelineStep
from .queue import DEFAULT_REDIS_URL, TaskQueue, build_task_queue, normalize_task_type
from .task import TaskType

LOGGER = logging.getLogger(__name__)


class LoggingStep(PipelineStep):
    """Fallback step used by the CLI until concrete workers are registered."""

    def __init__(self, step_type: str | TaskType) -> None:
        super().__init__()
        self.step_type = step_type

    async def execute(self, payload: dict[str, object]) -> dict[str, object]:
        LOGGER.info("Processed %s payload keys=%s", self.normalized_step_type, sorted(payload.keys()))
        return {"handled_by": self.normalized_step_type}


class WorkerRunner:
    """Long-running process that polls a queue and dispatches tasks."""

    def __init__(
        self,
        *,
        queue: TaskQueue,
        pipeline: Pipeline,
        task_types: Iterable[str | TaskType],
        poll_timeout: int = 1,
        idle_sleep_seconds: float = 0.1,
    ) -> None:
        self.queue = queue
        self.pipeline = pipeline
        self.task_types = [normalize_task_type(task_type) for task_type in task_types]
        self.poll_timeout = poll_timeout
        self.idle_sleep_seconds = idle_sleep_seconds
        self._poll_cursor = 0
        self._stop_requested = False

    def request_shutdown(self, *_args: object) -> None:
        LOGGER.info("Shutdown requested, finishing current loop")
        self._stop_requested = True

    async def run_once(self, *, timeout: int | None = None) -> bool:
        dequeue_timeout = self.poll_timeout if timeout is None else timeout
        if not self.task_types:
            return False

        total_task_types = len(self.task_types)
        ordered_task_types = self.task_types[self._poll_cursor :] + self.task_types[: self._poll_cursor]

        for offset, task_type in enumerate(ordered_task_types):
            source_index = (self._poll_cursor + offset) % total_task_types
            timeout_for_type = dequeue_timeout if offset == 0 else 0
            task = await asyncio.to_thread(self.queue.dequeue, task_type, timeout_for_type)
            if task is None:
                continue

            self._poll_cursor = (source_index + 1) % total_task_types
            try:
                result = await self.pipeline.execute_task(task)
            except Exception as exc:
                await asyncio.to_thread(self.queue.nack, str(task.task_id), str(exc))
                LOGGER.exception("Task %s failed", task.task_id)
            else:
                await asyncio.to_thread(self.queue.ack, str(task.task_id), result)
                LOGGER.info("Task %s completed", task.task_id)
            return True

        self._poll_cursor = (self._poll_cursor + 1) % total_task_types
        return False

    async def run_forever(self) -> None:
        self.install_signal_handlers()

        while not self._stop_requested:
            processed = await self.run_once()
            if not processed:
                await asyncio.sleep(self.idle_sleep_seconds)

    def install_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)



def build_default_pipeline(task_types: Iterable[str | TaskType]) -> Pipeline:
    return Pipeline(LoggingStep(task_type) for task_type in task_types)



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scivly worker runner")
    parser.add_argument(
        "--types",
        nargs="+",
        required=True,
        choices=[task_type.value for task_type in TaskType],
        help="Task types to poll and dispatch.",
    )
    parser.add_argument(
        "--queue",
        choices=["memory", "redis"],
        default=os.getenv("SCIVLY_QUEUE_BACKEND", "memory"),
        help="Queue backend to use. Defaults to SCIVLY_QUEUE_BACKEND or memory.",
    )
    parser.add_argument(
        "--redis-url",
        default=os.getenv("REDIS_URL", DEFAULT_REDIS_URL),
        help=(
            "Redis connection URL. Defaults to REDIS_URL or "
            f"{DEFAULT_REDIS_URL} to avoid collisions with local Redis on 6379."
        ),
    )
    parser.add_argument(
        "--poll-timeout",
        type=int,
        default=1,
        help="How long to wait for each queue poll in seconds.",
    )
    return parser


async def _run_from_args(args: argparse.Namespace) -> None:
    queue = build_task_queue(
        backend=args.queue,
        redis_url=args.redis_url,
    )
    pipeline = build_default_pipeline(args.types)
    runner = WorkerRunner(
        queue=queue,
        pipeline=pipeline,
        task_types=args.types,
        poll_timeout=args.poll_timeout,
    )
    await runner.run_forever()



def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(_run_from_args(args))


if __name__ == "__main__":
    main()
