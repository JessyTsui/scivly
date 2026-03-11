# Workers Workspace

This directory is reserved for Scivly ingestion, enrichment, and delivery workers.

- `arxiv/` for source sync and paper ingestion
- `pdf/` for PDF download and full-text fetch tracking
- `digest/` for digest assembly and delivery
- `common/` for shared pipeline infrastructure
- `index/` for embedding generation and pgvector indexing

Workers own batch and document-heavy processing. They should not become a second API surface.

The default arXiv triage design is documented in
[`docs/product/paper-triage-scoring.md`](../docs/product/paper-triage-scoring.md). Public-safe seed
priors and thresholds live in [`config/reference/`](../config/reference/README.md).
