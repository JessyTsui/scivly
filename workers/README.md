# Workers Workspace

This directory is reserved for Scivly ingestion, enrichment, and delivery workers.

- `arxiv/` for source sync and paper ingestion
- `digest/` for digest assembly and delivery
- `common/` for shared pipeline infrastructure

Workers own batch and document-heavy processing. They should not become a second API surface.

