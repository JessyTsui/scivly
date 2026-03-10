from __future__ import annotations

from workers.arxiv.filters import apply_hard_filters, evaluate_hard_filters


def test_hard_filters_reject_withdrawn_papers(withdrawn_paper) -> None:
    result = evaluate_hard_filters(withdrawn_paper)

    assert result.passed is False
    assert "withdrawn_or_errata" in result.reasons


def test_hard_filters_reject_short_abstract(short_abstract_paper) -> None:
    result = evaluate_hard_filters(short_abstract_paper)

    assert result.passed is False
    assert "abstract_too_short" in result.reasons


def test_apply_hard_filters_keeps_high_signal_papers(high_signal_paper) -> None:
    passed, rejected = apply_hard_filters([high_signal_paper])

    assert passed == [high_signal_paper]
    assert rejected == []
