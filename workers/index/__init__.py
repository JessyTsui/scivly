"""Vector indexing workers for semantic retrieval."""

from typing import TYPE_CHECKING, Any

from .embedder import (
    DEFAULT_EMBEDDING_DIMENSIONS,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_PROVIDER,
    EmbeddingProvider,
    HashEmbeddingProvider,
    OpenAIEmbeddingProvider,
    build_paper_embedding_text,
    create_embedding_provider,
    vector_to_pgvector,
)

if TYPE_CHECKING:
    from .steps import IndexPaperRecord, IndexPapersStep, IndexablePaper, PaperEmbeddingRecord, PostgresPaperEmbeddingStore

__all__ = [
    "DEFAULT_EMBEDDING_DIMENSIONS",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_EMBEDDING_PROVIDER",
    "EmbeddingProvider",
    "HashEmbeddingProvider",
    "IndexPaperRecord",
    "IndexPapersStep",
    "IndexablePaper",
    "OpenAIEmbeddingProvider",
    "PaperEmbeddingRecord",
    "PostgresPaperEmbeddingStore",
    "build_paper_embedding_text",
    "create_embedding_provider",
    "vector_to_pgvector",
]

_STEP_EXPORTS = {
    "IndexPaperRecord",
    "IndexPapersStep",
    "IndexablePaper",
    "PaperEmbeddingRecord",
    "PostgresPaperEmbeddingStore",
}


def __getattr__(name: str) -> Any:
    if name in _STEP_EXPORTS:
        from . import steps

        value = getattr(steps, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
