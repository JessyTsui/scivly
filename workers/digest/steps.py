"""Digest pipeline step implementations."""

from __future__ import annotations

from typing import Any

from workers.common.pipeline import PipelineStep
from workers.common.task import TaskType

from .assembler import DigestAssembler


class AssembleDigestStep(PipelineStep):
    """Prepare a digest payload from scored papers."""

    step_type = TaskType.DELIVER

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


class DeliverDigestStep(PipelineStep):
    """Delivery stub that records the intended channels and timestamp."""

    step_type = TaskType.DELIVER

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        digest = payload.get("digest")
        if not isinstance(digest, dict):
            raise ValueError("Digest delivery requires assembled digest content")

        channels = payload.get("channels") or ["log"]
        return {
            "delivery": {
                "status": "logged",
                "channels": list(channels),
                "digest_title": digest.get("title"),
            }
        }
