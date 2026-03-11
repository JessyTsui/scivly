from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest

from workers.common.pipeline import Pipeline
from workers.common.task import TaskPayload, TaskType
from workers.pdf.downloader import (
    ArxivRateLimiter,
    DownloadResult,
    LocalPdfStorage,
    PdfDownloadError,
    PdfDownloader,
)
from workers.pdf.steps import DownloadPdfStep

PDF_BYTES = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n"


class FakeRepository:
    def __init__(self) -> None:
        self.downloaded: list[dict[str, object]] = []
        self.failed: list[dict[str, object]] = []

    async def mark_pdf_downloaded(
        self,
        *,
        arxiv_id: str,
        paper_id: UUID | None,
        pdf_path: str,
    ) -> None:
        self.downloaded.append(
            {
                "arxiv_id": arxiv_id,
                "paper_id": paper_id,
                "pdf_path": pdf_path,
                "pdf_status": "stored",
            }
        )

    async def mark_pdf_failed(
        self,
        *,
        arxiv_id: str,
        paper_id: UUID | None,
    ) -> None:
        self.failed.append(
            {
                "arxiv_id": arxiv_id,
                "paper_id": paper_id,
                "pdf_status": "failed",
            }
        )


@dataclass
class FakeClock:
    current: float = 0.0
    sleeps: list[float] = field(default_factory=list)

    def now(self) -> float:
        return self.current

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.current += seconds


def test_fetch_and_store_writes_pdf_and_updates_repository(tmp_path: Path) -> None:
    repository = FakeRepository()
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return httpx.Response(200, content=PDF_BYTES)

    async def run_test() -> tuple[DownloadResult, list[str]]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            downloader = PdfDownloader(
                storage=LocalPdfStorage(tmp_path),
                repository=repository,
                client=client,
                max_attempts=1,
                backoff_base_seconds=0.0,
                rate_limiter=ArxivRateLimiter(interval_seconds=0.0),
            )
            result = await downloader.fetch_and_store(arxiv_id="2503.12345")
            return result, calls

    result, recorded_calls = asyncio.run(run_test())

    stored_path = Path(result.pdf_path)
    assert recorded_calls == ["https://arxiv.org/pdf/2503.12345.pdf"]
    assert stored_path.exists()
    assert stored_path.read_bytes() == PDF_BYTES
    assert result.pdf_status == "stored"
    assert result.size_bytes == len(PDF_BYTES)
    assert repository.downloaded == [
        {
            "arxiv_id": "2503.12345",
            "paper_id": None,
            "pdf_path": result.pdf_path,
            "pdf_status": "stored",
        }
    ]
    assert repository.failed == []


def test_download_pdf_rate_limits_requests(tmp_path: Path) -> None:
    repository = FakeRepository()
    clock = FakeClock(current=100.0)
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return httpx.Response(200, content=PDF_BYTES)

    async def run_test() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            downloader = PdfDownloader(
                storage=LocalPdfStorage(tmp_path),
                repository=repository,
                client=client,
                max_attempts=1,
                backoff_base_seconds=0.0,
                rate_limiter=ArxivRateLimiter(
                    interval_seconds=3.0,
                    now=clock.now,
                    sleep=clock.sleep,
                ),
                sleep=clock.sleep,
            )
            await downloader.download_pdf("2503.12345")
            await downloader.download_pdf("2503.12346")

    asyncio.run(run_test())

    assert calls == [
        "https://arxiv.org/pdf/2503.12345.pdf",
        "https://arxiv.org/pdf/2503.12346.pdf",
    ]
    assert clock.sleeps == [3.0]


def test_fetch_and_store_retries_with_exponential_backoff(tmp_path: Path) -> None:
    repository = FakeRepository()
    clock = FakeClock()
    statuses = [503, 503, 200]

    def handler(_: httpx.Request) -> httpx.Response:
        status_code = statuses.pop(0)
        return httpx.Response(status_code, content=PDF_BYTES)

    async def run_test() -> DownloadResult:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            downloader = PdfDownloader(
                storage=LocalPdfStorage(tmp_path),
                repository=repository,
                client=client,
                max_attempts=3,
                backoff_base_seconds=1.0,
                rate_limiter=ArxivRateLimiter(
                    interval_seconds=0.0,
                    now=clock.now,
                    sleep=clock.sleep,
                ),
                sleep=clock.sleep,
            )
            return await downloader.fetch_and_store(arxiv_id="2503.12345")

    result = asyncio.run(run_test())

    assert result.attempts == 3
    assert clock.sleeps == [1.0, 2.0]
    assert repository.failed == []
    assert len(repository.downloaded) == 1


def test_fetch_and_store_marks_failures_after_retry_budget(tmp_path: Path) -> None:
    repository = FakeRepository()
    clock = FakeClock()

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(503, content=b"temporary error")

    async def run_test() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            downloader = PdfDownloader(
                storage=LocalPdfStorage(tmp_path),
                repository=repository,
                client=client,
                max_attempts=3,
                backoff_base_seconds=1.0,
                rate_limiter=ArxivRateLimiter(
                    interval_seconds=0.0,
                    now=clock.now,
                    sleep=clock.sleep,
                ),
                sleep=clock.sleep,
            )
            await downloader.fetch_and_store(arxiv_id="2503.12345")

    with pytest.raises(PdfDownloadError):
        asyncio.run(run_test())

    assert clock.sleeps == [1.0, 2.0]
    assert repository.downloaded == []
    assert repository.failed == [
        {
            "arxiv_id": "2503.12345",
            "paper_id": None,
            "pdf_status": "failed",
        }
    ]


def test_download_pdf_step_executes_inside_pipeline() -> None:
    class FakeDownloader:
        def __init__(self) -> None:
            self.calls: list[tuple[str, UUID | None]] = []

        async def fetch_and_store(
            self,
            *,
            arxiv_id: str,
            paper_id: UUID | None = None,
        ) -> DownloadResult:
            self.calls.append((arxiv_id, paper_id))
            return DownloadResult(
                arxiv_id=arxiv_id,
                pdf_path="/tmp/pdfs/2503.12345.pdf",
                pdf_status="stored",
                sha256="abc123",
                size_bytes=42,
                attempts=2,
            )

    downloader = FakeDownloader()
    paper_id = uuid4()
    pipeline = Pipeline([DownloadPdfStep(downloader=downloader)])  # type: ignore[arg-type]
    task = TaskPayload(
        task_type=TaskType.FETCH,
        workspace_id=uuid4(),
        paper_id=paper_id,
        idempotency_key="task-fetch-001",
        payload={"arxiv_id": "2503.12345"},
    )

    result = asyncio.run(pipeline.execute_task(task))

    assert downloader.calls == [("2503.12345", paper_id)]
    assert result.result["final"]["pdf_path"] == "/tmp/pdfs/2503.12345.pdf"
    assert result.result["final"]["pdf_status"] == "stored"
    assert result.result["final"]["download_attempts"] == 2
