from __future__ import annotations

from workers.arxiv.scorer import MetadataScorer


def test_metadata_scorer_returns_explainable_result(sample_profile, high_signal_paper) -> None:
    scorer = MetadataScorer(profile=sample_profile)

    result = scorer.score_paper(high_signal_paper, cohort=[high_signal_paper])

    assert 0 <= result.total_score <= 100
    assert result.total_score >= 60
    assert result.threshold_decision in {"llm_rerank", "digest_candidate", "source_fetch"}
    assert result.matched_rules
    assert result.component_scores.topical_relevance > 15
    assert result.component_scores.actionability > 5
    assert "Final decision" in result.explanation


def test_duplicate_context_reduces_novelty_and_applies_penalty(
    sample_profile,
    high_signal_paper,
    similar_same_day_paper,
) -> None:
    scorer = MetadataScorer(profile=sample_profile)

    solo = scorer.score_paper(high_signal_paper, cohort=[high_signal_paper])
    clustered = scorer.score_paper(high_signal_paper, cohort=[high_signal_paper, similar_same_day_paper])

    assert clustered.component_scores.novelty_diversity <= solo.component_scores.novelty_diversity
    assert clustered.total_score <= solo.total_score


def test_negative_keyword_profile_conflict_applies_penalty(sample_profile, high_signal_paper) -> None:
    paper = high_signal_paper.model_copy(
        update={
            "abstract": high_signal_paper.abstract + " The work also studies protein folding workloads.",
        }
    )
    scorer = MetadataScorer(profile=sample_profile)

    result = scorer.score_paper(paper, cohort=[paper])

    assert result.component_scores.penalties < 0
    assert "penalty:keyword_profile_conflict" in result.matched_rules


def test_actionability_comment_only_signals_do_not_trigger_from_abstract(
    sample_profile,
    high_signal_paper,
) -> None:
    paper = high_signal_paper.model_copy(
        update={
            "comment": None,
            "abstract": (
                high_signal_paper.abstract
                + " We discuss implementation details extensively but do not release code."
            ),
        }
    )
    scorer = MetadataScorer(profile=sample_profile)

    result = scorer.score_paper(paper, cohort=[paper])

    assert "actionability:code_release_in_comment" not in result.matched_rules
    assert "actionability:project_page_in_comment" not in result.matched_rules
