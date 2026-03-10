from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuthorInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    affiliation: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Author name cannot be empty")
        return cleaned

    @field_validator("affiliation")
    @classmethod
    def validate_affiliation(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ArxivPaper(BaseModel):
    model_config = ConfigDict(extra="forbid")

    arxiv_id: str
    version: int = Field(default=1, ge=1)
    title: str
    abstract: str
    authors: list[AuthorInfo] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    primary_category: str
    comment: str | None = None
    journal_ref: str | None = None
    doi: str | None = None
    published: datetime
    updated: datetime

    @field_validator("arxiv_id", "title", "abstract", "primary_category")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty")
        return cleaned

    @field_validator("comment", "journal_ref", "doi")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        categories: list[str] = []
        for category in value:
            cleaned = category.strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                categories.append(cleaned)
        return categories


class ComponentScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topical_relevance: float = 0.0
    prestige_priors: float = 0.0
    actionability: float = 0.0
    profile_fit: float = 0.0
    novelty_diversity: float = 0.0
    penalties: float = 0.0


class ScoringProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "default"
    categories: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    tracked_authors: list[str] = Field(default_factory=list)
    negative_keywords: list[str] = Field(default_factory=list)

    @field_validator("categories", "keywords", "themes", "tracked_authors", "negative_keywords")
    @classmethod
    def normalize_string_lists(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        items: list[str] = []
        for item in value:
            cleaned = item.strip()
            lowered = cleaned.lower()
            if cleaned and lowered not in seen:
                seen.add(lowered)
                items.append(cleaned)
        return items


class ScoringResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paper_id: str
    total_score: float = Field(ge=0.0, le=100.0)
    component_scores: ComponentScores
    matched_rules: list[str] = Field(default_factory=list)
    threshold_decision: str
    explanation: str
