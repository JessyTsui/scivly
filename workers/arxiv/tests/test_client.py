from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from workers.arxiv.client import ArxivClient
from workers.arxiv.models import ArxivPaper, AuthorInfo


ATOM_FEED = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2503.99999v2</id>
    <updated>2026-03-10T10:00:00Z</updated>
    <published>2026-03-10T09:00:00Z</published>
    <title>Test Paper</title>
    <summary>Long enough summary for the parser test entry.</summary>
    <author>
      <name>Jane Doe</name>
      <arxiv:affiliation>Stanford University</arxiv:affiliation>
    </author>
    <arxiv:primary_category term="cs.CL" />
    <category term="cs.CL" />
    <category term="cs.AI" />
    <arxiv:comment>Code: https://github.com/example/test</arxiv:comment>
  </entry>
  <entry>
    <id>bad-id</id>
    <updated>2026-03-10T10:00:00Z</updated>
    <published>2026-03-10T09:00:00Z</published>
    <title>Broken Entry</title>
    <summary>Should be skipped without aborting the whole feed.</summary>
    <author>
      <name>Broken Author</name>
    </author>
    <arxiv:primary_category term="cs.CL" />
    <category term="cs.CL" />
  </entry>
</feed>
"""


def test_parse_feed_skips_malformed_entries() -> None:
    client = ArxivClient()

    papers = client._parse_feed(ATOM_FEED)

    assert len(papers) == 1
    assert papers[0].arxiv_id == "2503.99999"
    assert papers[0].version == 2
    assert papers[0].authors[0].affiliation == "Stanford University"


def test_filter_by_date_respects_bounds() -> None:
    client = ArxivClient()
    papers = client._parse_feed(ATOM_FEED)

    filtered = client._filter_by_date(
        papers,
        date_from=datetime(2026, 3, 10, 8, 30, tzinfo=timezone.utc),
        date_to=datetime(2026, 3, 10, 9, 30, tzinfo=timezone.utc),
    )

    assert len(filtered) == 1
    assert filtered[0].published == datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc)


def test_search_continues_pagination_when_first_filtered_page_is_empty() -> None:
    class StubClient(ArxivClient):
        def __init__(self) -> None:
            super().__init__(base_url="https://example.invalid")
            self.calls: list[int] = []

        async def _fetch_page(self, *, search_query: str, start: int, max_results: int) -> str:
            self.calls.append(start)
            return f"page-{start}"

        def _parse_feed(self, xml_payload: str) -> list[ArxivPaper]:
            if xml_payload == "page-0":
                return [
                    ArxivPaper(
                        arxiv_id="2503.50000",
                        version=1,
                        title="Future Paper",
                        abstract="A future-dated paper that should be filtered out.",
                        authors=[AuthorInfo(name="Future Author")],
                        categories=["cs.CL"],
                        primary_category="cs.CL",
                        comment=None,
                        journal_ref=None,
                        doi=None,
                        published=datetime(2026, 3, 11, 10, 0, tzinfo=timezone.utc),
                        updated=datetime(2026, 3, 11, 10, 0, tzinfo=timezone.utc),
                    )
                ]
            return [
                ArxivPaper(
                    arxiv_id="2503.50001",
                    version=1,
                    title="Current Paper",
                    abstract="A current paper that should survive the date filter.",
                    authors=[AuthorInfo(name="Current Author")],
                    categories=["cs.CL"],
                    primary_category="cs.CL",
                    comment=None,
                    journal_ref=None,
                    doi=None,
                    published=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
                    updated=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
                )
            ]

    client = StubClient()
    papers = asyncio.run(
        client.search(
            categories=["cs.CL"],
            date_from=datetime(2026, 3, 10, 0, 0, tzinfo=timezone.utc),
            date_to=datetime(2026, 3, 10, 23, 59, tzinfo=timezone.utc),
            max_results=1,
            page_size=1,
        )
    )

    assert client.calls == [0, 1]
    assert [paper.arxiv_id for paper in papers] == ["2503.50001"]
