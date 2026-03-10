from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Final
from urllib.parse import urlencode
from xml.etree import ElementTree

import httpx
from pydantic import ValidationError

from .dedup import canonicalize_arxiv_id, extract_version
from .models import ArxivPaper, AuthorInfo


ATOM_NS: Final = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _text_or_none(element: ElementTree.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    text = element.text.strip()
    return text or None


class ArxivClient:
    def __init__(
        self,
        *,
        base_url: str = "https://export.arxiv.org/api/query",
        timeout: float = 30.0,
        user_agent: str = "ScivlyArxivWorker/0.1 (+https://github.com/JessyTsui/scivly)",
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.user_agent = user_agent
        self._last_request_at: float | None = None
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "ArxivClient":
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent},
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def search(
        self,
        *,
        categories: list[str] | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        query: str | None = None,
        max_results: int = 100,
        page_size: int = 100,
    ) -> list[ArxivPaper]:
        if not categories and not query:
            raise ValueError("At least one category or query must be provided")

        papers: list[ArxivPaper] = []
        start = 0
        remaining = max_results

        while remaining > 0:
            batch_size = min(page_size, remaining)
            xml_payload = await self._fetch_page(
                search_query=self._build_search_query(
                    categories=categories or [],
                    date_from=date_from,
                    date_to=date_to,
                    query=query,
                ),
                start=start,
                max_results=batch_size,
            )
            raw_batch = self._parse_feed(xml_payload)
            raw_batch_size = len(raw_batch)
            batch = raw_batch
            if date_from or date_to:
                batch = self._filter_by_date(batch, date_from=date_from, date_to=date_to)
            if not batch:
                if raw_batch_size == 0:
                    break
                if date_from and raw_batch and max(paper.published for paper in raw_batch) < date_from:
                    break
                if raw_batch_size < batch_size:
                    break
                start += raw_batch_size
                continue
            papers.extend(batch)
            if raw_batch_size < batch_size:
                break
            start += raw_batch_size
            remaining = max_results - len(papers)

        return papers[:max_results]

    async def fetch_recent(
        self,
        *,
        categories: list[str],
        days: int,
        query: str | None = None,
        max_results: int = 100,
    ) -> list[ArxivPaper]:
        date_to = datetime.now(timezone.utc)
        date_from = date_to.replace(microsecond=0) - timedelta(days=days)
        return await self.search(
            categories=categories,
            date_from=date_from,
            date_to=date_to,
            query=query,
            max_results=max_results,
        )

    async def _fetch_page(self, *, search_query: str, start: int, max_results: int) -> str:
        client = self._client
        if client is None:
            client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
            )
            self._client = client

        await self._respect_rate_limit()
        params = {
            "search_query": search_query,
            "start": str(start),
            "max_results": str(max_results),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        response = await client.get(f"{self.base_url}?{urlencode(params)}")
        response.raise_for_status()
        loop = asyncio.get_running_loop()
        self._last_request_at = loop.time()
        return response.text

    async def _respect_rate_limit(self) -> None:
        if self._last_request_at is None:
            return
        loop = asyncio.get_running_loop()
        elapsed = loop.time() - self._last_request_at
        if elapsed < 3.0:
            await asyncio.sleep(3.0 - elapsed)

    def _build_search_query(
        self,
        *,
        categories: list[str],
        date_from: datetime | None,
        date_to: datetime | None,
        query: str | None,
    ) -> str:
        clauses: list[str] = []
        if categories:
            category_clause = " OR ".join(f"cat:{category}" for category in categories)
            clauses.append(f"({category_clause})")
        if query:
            sanitized = " ".join(query.replace('"', " ").split())
            clauses.append(f'all:"{sanitized}"')
        if date_from or date_to:
            start = (date_from or datetime(1991, 1, 1, tzinfo=timezone.utc)).strftime("%Y%m%d%H%M")
            end = (date_to or datetime.now(timezone.utc)).strftime("%Y%m%d%H%M")
            clauses.append(f"submittedDate:[{start} TO {end}]")
        return " AND ".join(clauses)

    def _filter_by_date(
        self,
        papers: list[ArxivPaper],
        *,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[ArxivPaper]:
        filtered: list[ArxivPaper] = []
        for paper in papers:
            if date_from and paper.published < date_from:
                continue
            if date_to and paper.published > date_to:
                continue
            filtered.append(paper)
        return filtered

    def _parse_feed(self, xml_payload: str) -> list[ArxivPaper]:
        root = ElementTree.fromstring(xml_payload)
        papers: list[ArxivPaper] = []
        for entry in root.findall("atom:entry", ATOM_NS):
            raw_id = _text_or_none(entry.find("atom:id", ATOM_NS))
            title = _text_or_none(entry.find("atom:title", ATOM_NS))
            abstract = _text_or_none(entry.find("atom:summary", ATOM_NS))
            updated = _text_or_none(entry.find("atom:updated", ATOM_NS))
            published = _text_or_none(entry.find("atom:published", ATOM_NS))
            if not raw_id or not title or not abstract or not updated or not published:
                continue
            try:
                authors = []
                for author in entry.findall("atom:author", ATOM_NS):
                    name = _text_or_none(author.find("atom:name", ATOM_NS))
                    if not name:
                        continue
                    affiliation = _text_or_none(author.find("arxiv:affiliation", ATOM_NS))
                    authors.append(AuthorInfo(name=name, affiliation=affiliation))

                categories = [
                    category.attrib["term"].strip()
                    for category in entry.findall("atom:category", ATOM_NS)
                    if category.attrib.get("term")
                ]
                primary_category = entry.find("arxiv:primary_category", ATOM_NS)
                primary_term = primary_category.attrib.get("term") if primary_category is not None else None
                primary_category_value = primary_term or (categories[0] if categories else "")
                if not primary_category_value:
                    continue

                papers.append(
                    ArxivPaper(
                        arxiv_id=canonicalize_arxiv_id(raw_id),
                        version=extract_version(raw_id),
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        categories=categories,
                        primary_category=primary_category_value,
                        comment=_text_or_none(entry.find("arxiv:comment", ATOM_NS)),
                        journal_ref=_text_or_none(entry.find("arxiv:journal_ref", ATOM_NS)),
                        doi=_text_or_none(entry.find("arxiv:doi", ATOM_NS)),
                        published=_parse_datetime(published),
                        updated=_parse_datetime(updated),
                    )
                )
            except (TypeError, ValidationError, ValueError):
                continue
        return papers
