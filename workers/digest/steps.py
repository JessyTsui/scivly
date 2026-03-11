"""Digest pipeline step implementations."""

from __future__ import annotations

from typing import Any, Mapping

from workers.common.pipeline import PipelineStep
from workers.common.task import TaskType

from .assembler import DigestAssembler


class AssembleDigestStep(PipelineStep):
    """Prepare a digest payload from scored papers."""

    step_type = TaskType.DELIVER
    emitted_events = ("digest.ready",)

    def __init__(self, *, assembler: DigestAssembler | None = None) -> None:
        super().__init__()
        self.assembler = assembler or DigestAssembler()

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        papers = payload.get("papers")
        if not isinstance(papers, list):
            raise ValueError("Digest assembly requires a papers list")

        digest = self.assembler.assemble(
            papers,
            workspace_name=str(payload.get("workspace_name", "Scivly")),
        )
        return {
            "digest": digest,
            "selected_paper_count": digest["summary"]["paper_count"],
        }

    def build_emitted_event_payload(
        self,
        task,
        execution_state: Mapping[str, Any],
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        payload = super().build_emitted_event_payload(task, execution_state, result)
        digest = execution_state.get("digest")
        if isinstance(digest, dict):
            payload["digest"] = digest
            payload["paper_count"] = digest.get("summary", {}).get("paper_count")
        return payload


class DeliverDigestStep(PipelineStep):
    """Delivery stub that records the intended channels and timestamp."""

    step_type = TaskType.DELIVER
    emitted_events = ("digest.delivered",)

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        digest = payload.get("digest")
        if not isinstance(digest, dict):
            raise ValueError("Digest delivery requires assembled digest content")

        channels = self._normalize_channels(payload.get("channels"))
        return {
            "delivery": {
                "status": "logged",
                "channels": channels,
                "digest_title": digest.get("title"),
            }
        }

    def build_emitted_event_payload(
        self,
        task,
        execution_state: Mapping[str, Any],
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        payload = super().build_emitted_event_payload(task, execution_state, result)
        digest = execution_state.get("digest")
        delivery = result.get("delivery")
        if isinstance(digest, dict):
            payload["digest"] = digest
        if isinstance(delivery, dict):
            payload["delivery"] = delivery
        return payload

    def _normalize_channels(self, value: Any) -> list[str]:
        if value is None:
            return ["log"]
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, tuple, set)):
            return [str(channel) for channel in value]
        raise ValueError("Digest delivery channels must be a string or a list of strings")
