from __future__ import annotations

import hashlib
import math
import os
import re
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

import httpx

DEFAULT_EMBEDDING_DIMENSIONS = 1536
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_EMBEDDING_PROVIDER = "hash"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
SEMANTIC_HINTS: dict[str, tuple[str, ...]] = {
    "attention": ("transformer", "sequence"),
    "digest": ("summary", "ranking"),
    "embedding": ("vector", "retrieval"),
    "mechanism": ("method",),
    "memory": ("retrieval", "context"),
    "planning": ("agentic", "reasoning"),
    "retrieval": ("search", "evidence"),
    "robot": ("embodied", "policy"),
    "transformer": ("attention", "sequence"),
}


class EmbeddingProviderError(RuntimeError):
    """Raised when an embedding provider cannot satisfy a request."""


class EmbeddingProvider(ABC):
    provider_name = DEFAULT_EMBEDDING_PROVIDER
    model_name = DEFAULT_EMBEDDING_MODEL

    def __init__(self, *, dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS) -> None:
        self.dimensions = dimensions

    async def embed_text(self, text: str) -> list[float]:
        return (await self.embed_texts([text]))[0]

    @abstractmethod
    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed one or more texts."""


class HashEmbeddingProvider(EmbeddingProvider):
    provider_name = "hash"
    model_name = "hash-v1"

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def _embed_text(self, text: str) -> list[float]:
        tokens = _tokenize(text)
        if not tokens:
            return [0.0] * self.dimensions

        weighted_terms: list[tuple[str, float]] = []
        for token in tokens:
            weighted_terms.append((token, 1.0))
        for first, second in zip(tokens, tokens[1:]):
            weighted_terms.append((f"{first}::{second}", 0.65))

        vector = [0.0] * self.dimensions
        for term, base_weight in weighted_terms:
            for expanded_term, weight_scale in _expand_term(term):
                index, sign = _project_term(expanded_term, self.dimensions)
                vector[index] += base_weight * weight_scale * sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            return vector

        return [round(value / norm, 8) for value in vector]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    provider_name = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        api_base: str,
        model: str = DEFAULT_EMBEDDING_MODEL,
        dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS,
        timeout_seconds: float = 20.0,
    ) -> None:
        super().__init__(dimensions=dimensions)
        self.api_key = api_key
        self.api_base = api_base.rstrip("/")
        self.model_name = model
        self.timeout_seconds = timeout_seconds

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.api_base}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "input": list(texts),
                        "model": self.model_name,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingProviderError(f"Embedding provider request failed: {exc}") from exc

        payload = response.json()
        rows = sorted(payload.get("data", []), key=lambda item: item.get("index", 0))
        if len(rows) != len(texts):
            raise EmbeddingProviderError("Embedding provider returned an unexpected number of vectors.")

        vectors: list[list[float]] = []
        for row in rows:
            embedding = row.get("embedding")
            if not isinstance(embedding, list):
                raise EmbeddingProviderError("Embedding provider returned an invalid vector payload.")
            if len(embedding) != self.dimensions:
                raise EmbeddingProviderError(
                    f"Embedding dimension mismatch: expected {self.dimensions}, got {len(embedding)}."
                )
            vectors.append([float(value) for value in embedding])
        return vectors


def create_embedding_provider() -> EmbeddingProvider:
    provider = os.getenv("SCIVLY_EMBEDDING_PROVIDER", DEFAULT_EMBEDDING_PROVIDER).strip().lower()
    dimensions = int(os.getenv("SCIVLY_EMBEDDING_DIMENSIONS", str(DEFAULT_EMBEDDING_DIMENSIONS)))

    if provider in {"hash", "local"}:
        return HashEmbeddingProvider(dimensions=dimensions)
    if provider == "openai":
        api_key = os.getenv("SCIVLY_EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EmbeddingProviderError("SCIVLY_EMBEDDING_API_KEY must be set for openai embeddings.")
        return OpenAIEmbeddingProvider(
            api_key=api_key,
            api_base=os.getenv("SCIVLY_EMBEDDING_API_BASE", "https://api.openai.com/v1"),
            model=os.getenv("SCIVLY_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
            dimensions=dimensions,
            timeout_seconds=float(os.getenv("SCIVLY_EMBEDDING_TIMEOUT_SECONDS", "20")),
        )

    raise EmbeddingProviderError(f"Unsupported embedding provider: {provider}")


def build_paper_embedding_text(document: Mapping[str, object]) -> str:
    key_points = document.get("key_points")
    key_point_lines: list[str] = []
    if isinstance(key_points, list):
        key_point_lines = [str(item).strip() for item in key_points if str(item).strip()]

    authors = document.get("authors")
    author_names: list[str] = []
    if isinstance(authors, list):
        author_names = [
            str(item.get("name", "")).strip()
            for item in authors
            if isinstance(item, Mapping) and str(item.get("name", "")).strip()
        ]

    categories = document.get("categories")
    category_names: list[str] = []
    if isinstance(categories, list):
        category_names = [str(item).strip() for item in categories if str(item).strip()]

    segments = [
        ("title", _optional_text(document.get("title")), 3),
        ("title_zh", _optional_text(document.get("title_zh")), 2),
        ("summary", _optional_text(document.get("one_line_summary")), 2),
        ("abstract", _optional_text(document.get("abstract")), 1),
        ("abstract_zh", _optional_text(document.get("abstract_zh")), 1),
    ]

    lines: list[str] = []
    for label, value, repeats in segments:
        if not value:
            continue
        for _ in range(repeats):
            lines.append(f"{label}: {value}")

    if key_point_lines:
        lines.extend(f"key_point: {value}" for value in key_point_lines)
    if author_names:
        lines.append("authors: " + ", ".join(author_names))
    if category_names:
        lines.append("categories: " + ", ".join(category_names))

    return "\n".join(lines)


def vector_to_pgvector(vector: Sequence[float]) -> str:
    return "[" + ",".join(f"{float(value):.8f}" for value in vector) + "]"


def _tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def _optional_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _expand_term(term: str) -> list[tuple[str, float]]:
    expanded = [(term, 1.0)]
    if "::" in term:
        return expanded

    for synonym in SEMANTIC_HINTS.get(term, ()):
        expanded.append((synonym, 0.45))
    return expanded


def _project_term(term: str, dimensions: int) -> tuple[int, float]:
    digest = hashlib.blake2b(term.encode("utf-8"), digest_size=16).digest()
    index = int.from_bytes(digest[:8], "big") % dimensions
    sign = 1.0 if digest[8] % 2 == 0 else -1.0
    return index, sign
