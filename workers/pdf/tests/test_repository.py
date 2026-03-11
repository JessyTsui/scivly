from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from workers.pdf.downloader import AsyncpgPaperRepository


class FakeConnection:
    def __init__(self, results: list[str]) -> None:
        self.results = list(results)
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False

    async def execute(self, query: str, *args: object) -> str:
        self.executed.append((query, args))
        return self.results.pop(0)

    async def close(self) -> None:
        self.closed = True


def test_repository_marks_pdf_downloaded_by_arxiv_id() -> None:
    connection = FakeConnection(["UPDATE 1"])
    urls: list[str] = []

    async def connect(url: str) -> FakeConnection:
        urls.append(url)
        return connection

    repository = AsyncpgPaperRepository(
        database_url="postgresql+asyncpg://localhost/scivly",
        connect=connect,
    )

    asyncio.run(
        repository.mark_pdf_downloaded(
            arxiv_id="2503.12345",
            paper_id=None,
            pdf_path="/tmp/pdfs/2503.12345.pdf",
        )
    )

    assert urls == ["postgresql://localhost/scivly"]
    assert connection.closed is True
    assert len(connection.executed) == 1
    assert connection.executed[0][1] == ("/tmp/pdfs/2503.12345.pdf", "2503.12345")
    assert "pdf_status = 'stored'" in connection.executed[0][0]


def test_repository_falls_back_to_arxiv_id_when_paper_lookup_misses() -> None:
    connection = FakeConnection(["UPDATE 0", "UPDATE 1"])
    paper_id = uuid4()

    async def connect(_: str) -> FakeConnection:
        return connection

    repository = AsyncpgPaperRepository(connect=connect)

    asyncio.run(
        repository.mark_pdf_downloaded(
            arxiv_id="2503.12345",
            paper_id=paper_id,
            pdf_path="/tmp/pdfs/2503.12345.pdf",
        )
    )

    assert len(connection.executed) == 2
    assert connection.executed[0][1] == ("/tmp/pdfs/2503.12345.pdf", paper_id)
    assert connection.executed[1][1] == ("/tmp/pdfs/2503.12345.pdf", "2503.12345")


def test_repository_marks_pdf_failure() -> None:
    connection = FakeConnection(["UPDATE 1"])

    async def connect(_: str) -> FakeConnection:
        return connection

    repository = AsyncpgPaperRepository(connect=connect)

    asyncio.run(
        repository.mark_pdf_failed(
            arxiv_id="2503.12345",
            paper_id=None,
        )
    )

    assert connection.closed is True
    assert connection.executed[0][1] == ("2503.12345",)
    assert "pdf_status = 'failed'" in connection.executed[0][0]
    assert "pdf_path = NULL" not in connection.executed[0][0]


def test_repository_raises_when_no_paper_record_matches() -> None:
    connection = FakeConnection(["UPDATE 0"])

    async def connect(_: str) -> FakeConnection:
        return connection

    repository = AsyncpgPaperRepository(connect=connect)

    with pytest.raises(LookupError):
        asyncio.run(
            repository.mark_pdf_downloaded(
                arxiv_id="2503.12345",
                paper_id=None,
                pdf_path="/tmp/pdfs/2503.12345.pdf",
            )
        )
