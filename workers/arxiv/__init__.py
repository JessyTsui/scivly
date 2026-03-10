"""Scivly arXiv ingestion and scoring worker."""

from .client import ArxivClient
from .dedup import DeduplicationRecord, deduplicate_papers
from .filters import HardFilterResult, apply_hard_filters
from .models import ArxivPaper, AuthorInfo, ComponentScores, ScoringProfile, ScoringResult
from .scorer import MetadataScorer

__all__ = [
    "ArxivClient",
    "ArxivPaper",
    "AuthorInfo",
    "ComponentScores",
    "DeduplicationRecord",
    "HardFilterResult",
    "MetadataScorer",
    "ScoringProfile",
    "ScoringResult",
    "apply_hard_filters",
    "deduplicate_papers",
]
