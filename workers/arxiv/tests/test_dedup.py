from __future__ import annotations

from workers.arxiv.dedup import canonicalize_arxiv_id, deduplicate_papers, extract_version


def test_canonicalize_arxiv_id_strips_version_and_url() -> None:
    assert canonicalize_arxiv_id("https://arxiv.org/abs/2503.12345v7") == "2503.12345"
    assert extract_version("https://arxiv.org/abs/2503.12345v7") == 7


def test_deduplicate_papers_merges_versions_and_crosslists(versioned_crosslist_papers) -> None:
    deduped = deduplicate_papers(versioned_crosslist_papers)

    assert len(deduped) == 1
    record = deduped[0]
    assert record.canonical_id == "2503.12345"
    assert record.merged_versions == [1, 2]
    assert record.paper.version == 2
    assert set(record.paper.categories) == {"cs.CL", "cs.AI", "cs.IR"}
    assert record.source_ids == ["2503.12345v2", "2503.12345v1"]


def test_deduplicate_papers_deduplicates_repeated_source_versions(high_signal_paper) -> None:
    papers = [
        high_signal_paper.model_copy(update={"arxiv_id": "2503.12345v1"}),
        high_signal_paper.model_copy(update={"arxiv_id": "2503.12345v1"}),
    ]

    deduped = deduplicate_papers(papers)

    assert len(deduped) == 1
    assert deduped[0].source_ids == ["2503.12345v1"]
