"""PDF download helpers for arXiv full-text processing."""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Any, Awaitable, Callable, Protocol
from uuid import UUID

import httpx

DEFAULT_DATABASE_URL = "postgresql://localhost:5432/scivly"
DEFAULT_ARXIV_PDF_BASE_URL = "https://arxiv.org/pdf"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PDF_STORAGE_PATH = REPO_ROOT / ".data" / "pdfs"
PDF_STATUS_MISSING = "missing"
PDF_STATUS_STORED = "stored"
PDF_STATUS_FAILED = "failed"
SAFE_ARXIV_ID_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")

SleepFn = Callable[[float], Awaitable[None]]
NowFn = Callable[[], float]
AsyncConnectFn = Callable[[str], Awaitable[Any]]


class PdfDownloadError(RuntimeError):
    """Raised when a PDF download or persistence flow cannot complete."""


class RetryablePdfDownloadError(PdfDownloadError):
    """Raised for transient failures that should be retried."""


class NonRetryablePdfDownloadError(PdfDownloadError):
    """Raised for permanent failures that should fail fast."""


class PdfStorage(Protocol):
    async def store(self, *, key: str, content: bytes) -> str:
        """Persist PDF bytes and return the canonical storage path."""


class PaperDownloadRepository(Protocol):
    async def mark_pdf_downloaded(
        self,
        *,
        arxiv_id: str,
        paper_id: UUID | None,
        pdf_path: str,
    ) -> None:
        """Persist successful PDF download metadata."""

    async def mark_pdf_failed(
        self,
        *,
        arxiv_id: str,
        paper_id: UUID | None,
    ) -> None:
        """Persist failed PDF download metadata."""


def sanitize_arxiv_id(arxiv_id: str) -> str:
    candidate = arxiv_id.strip()
    if not candidate:
        raise ValueError("arxiv_id is required")
    return SAFE_ARXIV_ID_PATTERN.sub("_", candidate)


def normalize_database_url(database_url: str) -> str:
    normalized = database_url.strip()
    if normalized.startswith("postgres://"):
        normalized = normalized.replace("postgres://", "postgresql://", 1)
    if normalized.startswith("postgresql+asyncpg://"):
        normalized = normalized.replace("postgresql+asyncpg://", "postgresql://", 1)
    return normalized


def get_worker_database_url() -> str:
    return normalize_database_url(
        os.getenv("SCIVLY_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or DEFAULT_DATABASE_URL
    )


def build_pdf_storage_from_env() -> PdfStorage:
    backend = os.getenv("SCIVLY_PDF_STORAGE_BACKEND", "local").strip().lower()
    if backend in {"s3", "r2"}:
        bucket = os.getenv("SCIVLY_PDF_STORAGE_BUCKET")
        if not bucket:
            raise ValueError("SCIVLY_PDF_STORAGE_BUCKET is required for S3/R2 PDF storage")
        return S3PdfStorage(
            bucket=bucket,
            prefix=os.getenv("SCIVLY_PDF_STORAGE_PREFIX", "arxiv-pdfs"),
            endpoint_url=os.getenv("SCIVLY_PDF_S3_ENDPOINT_URL"),
            region_name=os.getenv("SCIVLY_PDF_S3_REGION"),
        )

    storage_path = Path(
        os.getenv("SCIVLY_PDF_STORAGE_PATH", str(DEFAULT_PDF_STORAGE_PATH))
    ).expanduser()
    return LocalPdfStorage(storage_path)


@dataclass(slots=True)
class DownloadResult:
    arxiv_id: str
    pdf_path: str
    pdf_status: str
    sha256: str
    size_bytes: int
    attempts: int

    def as_payload(self) -> dict[str, Any]:
        return {
            "pdf_path": self.pdf_path,
            "pdf_status": self.pdf_status,
            "pdf_sha256": self.sha256,
            "pdf_size_bytes": self.size_bytes,
            "download_attempts": self.attempts,
        }


class ArxivRateLimiter:
    """Per-process arXiv limiter that enforces at most one request every N seconds."""

    def __init__(
        self,
        *,
        interval_seconds: float = 3.0,
        sleep: SleepFn = asyncio.sleep,
        now: NowFn = monotonic,
    ) -> None:
        self.interval_seconds = interval_seconds
        self._sleep = sleep
        self._now = now
        self._last_request_at: float | None = None
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            current = self._now()
            if self._last_request_at is not None:
                remaining = self.interval_seconds - (current - self._last_request_at)
                if remaining > 0:
                    await self._sleep(remaining)
                    current = self._now()
            self._last_request_at = current


class LocalPdfStorage:
    """Filesystem-backed PDF storage."""

    def __init__(self, root_path: Path | str) -> None:
        self.root_path = Path(root_path).expanduser()

    async def store(self, *, key: str, content: bytes) -> str:
        path = self.root_path / key
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, content)
        return str(path.resolve())


class S3PdfStorage:
    """Object-storage-backed PDF storage for S3 or R2."""

    def __init__(
        self,
        *,
        bucket: str,
        prefix: str = "arxiv-pdfs",
        endpoint_url: str | None = None,
        region_name: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        if client is None:
            try:
                import boto3  # type: ignore[import-untyped,import-not-found]
            except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional dependency state
                raise ModuleNotFoundError(
                    "boto3 is required for S3/R2 PDF storage. Install workers/requirements.txt."
                ) from exc
            client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                region_name=region_name,
            )
        self.client = client

    async def store(self, *, key: str, content: bytes) -> str:
        object_key = "/".join(part for part in (self.prefix, key.lstrip("/")) if part)
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=object_key,
            Body=content,
            ContentType="application/pdf",
        )
        return f"s3://{self.bucket}/{object_key}"


class AsyncpgPaperRepository:
    """Persist PDF tracking fields to the papers table."""

    def __init__(
        self,
        *,
        database_url: str | None = None,
        connect: AsyncConnectFn | None = None,
    ) -> None:
        self.database_url = normalize_database_url(database_url or get_worker_database_url())
        self._connect = connect

    async def mark_pdf_downloaded(
        self,
        *,
        arxiv_id: str,
        paper_id: UUID | None,
        pdf_path: str,
    ) -> None:
        updated = False
        if paper_id is not None:
            updated = await self._execute_update(
                """
                UPDATE papers
                SET pdf_path = $1,
                    pdf_status = 'stored',
                    updated_at = NOW()
                WHERE id = $2
                """,
                pdf_path,
                paper_id,
            )
        if not updated and arxiv_id:
            updated = await self._execute_update(
                """
                UPDATE papers
                SET pdf_path = $1,
                    pdf_status = 'stored',
                    updated_at = NOW()
                WHERE arxiv_id = $2
                """,
                pdf_path,
                arxiv_id,
            )
        if not updated:
            raise LookupError(f"No paper record found for arXiv id {arxiv_id}")

    async def mark_pdf_failed(
        self,
        *,
        arxiv_id: str,
        paper_id: UUID | None,
    ) -> None:
        updated = False
        if paper_id is not None:
            updated = await self._execute_update(
                """
                UPDATE papers
                SET pdf_status = 'failed',
                    updated_at = NOW()
                WHERE id = $1
                """,
                paper_id,
            )
        if not updated and arxiv_id:
            updated = await self._execute_update(
                """
                UPDATE papers
                SET pdf_status = 'failed',
                    updated_at = NOW()
                WHERE arxiv_id = $1
                """,
                arxiv_id,
            )
        if not updated:
            raise LookupError(f"No paper record found for arXiv id {arxiv_id}")

    async def _open_connection(self) -> Any:
        connect = self._connect
        if connect is None:
            try:
                import asyncpg  # type: ignore[import-not-found]
            except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional dependency state
                raise ModuleNotFoundError(
                    "asyncpg is required for paper PDF metadata updates. Install workers/requirements.txt."
                ) from exc
            connect = asyncpg.connect
        return await connect(self.database_url)

    async def _execute_update(self, query: str, *args: object) -> bool:
        connection = await self._open_connection()
        try:
            result = await connection.execute(query, *args)
        finally:
            await connection.close()
        return _updated_row_count(result) > 0


def _updated_row_count(execute_result: str) -> int:
    parts = execute_result.split()
    if len(parts) < 2:
        return 0
    try:
        return int(parts[-1])
    except ValueError:
        return 0


class PdfDownloader:
    """Download, store, and track arXiv PDFs."""

    def __init__(
        self,
        *,
        storage: PdfStorage | None = None,
        repository: PaperDownloadRepository | None = None,
        rate_limiter: ArxivRateLimiter | None = None,
        client: httpx.AsyncClient | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
        user_agent: str = "ScivlyPdfWorker/0.1 (+https://github.com/JessyTsui/scivly)",
        max_attempts: int = 3,
        backoff_base_seconds: float = 1.0,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self.storage = storage or build_pdf_storage_from_env()
        self.repository = repository or AsyncpgPaperRepository()
        self.rate_limiter = rate_limiter or ArxivRateLimiter(
            interval_seconds=float(os.getenv("SCIVLY_PDF_RATE_LIMIT_SECONDS", "3"))
        )
        _base = base_url or os.getenv("SCIVLY_ARXIV_PDF_BASE_URL") or DEFAULT_ARXIV_PDF_BASE_URL
        self.base_url = _base.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent
        self.max_attempts = max(1, max_attempts)
        self.backoff_base_seconds = max(0.0, backoff_base_seconds)
        self._sleep = sleep
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "PdfDownloader":
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None

    async def download_pdf(self, arxiv_id: str) -> bytes:
        content, _ = await self._download_with_retries(arxiv_id)
        return content

    async def fetch_and_store(
        self,
        *,
        arxiv_id: str,
        paper_id: UUID | None = None,
    ) -> DownloadResult:
        normalized_arxiv_id = arxiv_id.strip()
        if not normalized_arxiv_id:
            raise ValueError("arxiv_id is required")

        try:
            content, attempts = await self._download_with_retries(normalized_arxiv_id)
            storage_key = self._build_storage_key(normalized_arxiv_id)
            pdf_path = await self.storage.store(key=storage_key, content=content)
            await self.repository.mark_pdf_downloaded(
                arxiv_id=normalized_arxiv_id,
                paper_id=paper_id,
                pdf_path=pdf_path,
            )
            return DownloadResult(
                arxiv_id=normalized_arxiv_id,
                pdf_path=pdf_path,
                pdf_status=PDF_STATUS_STORED,
                sha256=hashlib.sha256(content).hexdigest(),
                size_bytes=len(content),
                attempts=attempts,
            )
        except Exception:
            try:
                await self.repository.mark_pdf_failed(
                    arxiv_id=normalized_arxiv_id,
                    paper_id=paper_id,
                )
            except Exception:
                pass
            raise

    async def _download_with_retries(self, arxiv_id: str) -> tuple[bytes, int]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await self._download_once(arxiv_id), attempt
            except NonRetryablePdfDownloadError as exc:
                raise PdfDownloadError(str(exc)) from exc
            except RetryablePdfDownloadError as exc:
                last_error = exc
                if attempt == self.max_attempts:
                    break
                await self._sleep(self.backoff_base_seconds * (2 ** (attempt - 1)))

        message = f"Failed to download PDF for {arxiv_id} after {self.max_attempts} attempts"
        if last_error is not None:
            message = f"{message}: {last_error}"
        raise PdfDownloadError(message) from last_error

    async def _download_once(self, arxiv_id: str) -> bytes:
        client = await self._get_client()
        await self.rate_limiter.acquire()

        try:
            response = await client.get(self._build_pdf_url(arxiv_id))
        except httpx.TimeoutException as exc:
            raise RetryablePdfDownloadError(f"Timed out fetching PDF for {arxiv_id}") from exc
        except httpx.TransportError as exc:
            raise RetryablePdfDownloadError(f"Transport error fetching PDF for {arxiv_id}: {exc}") from exc

        if response.status_code == 429 or response.status_code >= 500:
            raise RetryablePdfDownloadError(
                f"arXiv returned {response.status_code} for {arxiv_id}"
            )
        if response.status_code >= 400:
            raise NonRetryablePdfDownloadError(
                f"arXiv returned {response.status_code} for {arxiv_id}"
            )

        return response.content

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": self.user_agent},
            )
            self._owns_client = True
        return self._client

    def _build_pdf_url(self, arxiv_id: str) -> str:
        return f"{self.base_url}/{arxiv_id}.pdf"

    def _build_storage_key(self, arxiv_id: str) -> str:
        safe_arxiv_id = sanitize_arxiv_id(arxiv_id)
        partition = safe_arxiv_id[:4] if safe_arxiv_id[:4].isdigit() else "legacy"
        return f"{partition}/{safe_arxiv_id}.pdf"
