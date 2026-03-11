"""Pipeline steps for PDF download and parsing."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from workers.common.pipeline import PipelineStep
from workers.common.task import TaskType

from .downloader import PdfDownloader
from .parser import PdfParser


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


class ParsePdfStep(PipelineStep):
    """Parse a downloaded PDF into structured text and figure artifacts."""

    step_type = TaskType.PARSE

    def __init__(self, *, parser: PdfParser | None = None) -> None:
        super().__init__(max_attempts=1, timeout_seconds=180.0, backoff_base_seconds=0.0)
        self.parser = parser or PdfParser()

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        pdf_path = payload.get("pdf_path")
        if not isinstance(pdf_path, str) or not pdf_path.strip():
            raise ValueError("PDF parsing requires a pdf_path")

        arxiv_id = payload.get("arxiv_id")
        parsed_pdf = await self.parser.parse(
            pdf_path=pdf_path,
            paper_id=_coerce_uuid(payload.get("paper_id")),
            arxiv_id=arxiv_id if isinstance(arxiv_id, str) else None,
        )
        return {
            "parsed_pdf": parsed_pdf.as_dict(),
            "pdf_parse_status": "parsed",
            "parsed_figure_count": len(parsed_pdf.figures),
            "parsed_section_count": len(parsed_pdf.sections),
        }
