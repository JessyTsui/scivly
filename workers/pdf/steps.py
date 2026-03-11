"""Pipeline steps for PDF download and tracking."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from workers.common.pipeline import PipelineStep
from workers.common.task import TaskType

from .downloader import PdfDownloader


def _coerce_uuid(value: Any) -> UUID | None:
    if value is None or value == "":
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


class DownloadPdfStep(PipelineStep):
    """Fetch a scored arXiv paper PDF and persist its storage metadata."""

    step_type = TaskType.FETCH

    def __init__(self, *, downloader: PdfDownloader | None = None) -> None:
        super().__init__(max_attempts=1, timeout_seconds=180.0, backoff_base_seconds=0.0)
        self.downloader = downloader or PdfDownloader()

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        arxiv_id = payload.get("arxiv_id")
        if not isinstance(arxiv_id, str) or not arxiv_id.strip():
            raise ValueError("PDF download requires an arxiv_id")

        result = await self.downloader.fetch_and_store(
            arxiv_id=arxiv_id,
            paper_id=_coerce_uuid(payload.get("paper_id")),
        )
        return result.as_payload()
