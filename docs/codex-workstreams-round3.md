# Round 3 — Codex Workstream Prompts

> 4 independent worktrees, to be launched in parallel.
> Prerequisites: Round 1 (A1–A3, B1, B3, F1) and Round 2 (B2, C1, E1, G1) fully merged.

---

## Workstream C2 — PDF Parsing & Text Extraction

```
You are working on the Scivly project — an open-source multi-tenant paper intelligence platform.

## Task: C2

Refer to the task spec in `docs/0311-tasks.md` under the section for Task C2: PDF Parsing & Text Extraction.

## Project Context
- Monorepo: `frontend/` (Next.js 16, React 19, port 3100), `backend/` (FastAPI, port 8100), `workers/` (Python pipeline), `db/` (PostgreSQL + pgvector)
- Read `ARCHITECTURE.md` and `CLAUDE.md` for conventions before writing code.
- Branch name: `codex/feat/c2`

## What Already Exists (from Round 2)
- `workers/pdf/downloader.py` — PDF download with arXiv rate limiting, retry/backoff, local + S3/R2 storage (Task C1, merged)
- `workers/pdf/steps.py` — `DownloadPdfStep` pipeline step
- `workers/common/pipeline.py` — Pipeline base class with `PipelineStep`, `TaskPayload`, `TaskType`
- `db/migrations/006_paper_pdf_tracking.sql` — `pdf_path`, `pdf_status`, `pdf_sha256` columns on papers table

## Instructions
1. Read the full task spec for C2 in `docs/0311-tasks.md`
2. Read `ARCHITECTURE.md` (especially section 7.3 "Fulltext Processing") and `CLAUDE.md`
3. Read `workers/pdf/downloader.py` and `workers/pdf/steps.py` to understand the existing PDF pipeline patterns
4. Read `workers/common/pipeline.py` to understand the pipeline step interface
5. Implement `workers/pdf/parser.py` using `pymupdf` (fitz) for text and image extraction
6. Add a `ParsePdfStep` in `workers/pdf/steps.py` that chains after `DownloadPdfStep`
7. Output structured JSON: title, abstract, sections (with headers), references, figures with captions
8. Add `pymupdf` to `workers/requirements.txt`
9. Write tests in `workers/pdf/tests/test_parser.py` covering all "Test" criteria from the spec
10. Make sure `ruff check`, `mypy`, and `pytest` all pass
11. Commit with a clear message, push, and create a PR to `main`
```

---

## Workstream F2 — Public Paper Library

```
You are working on the Scivly project — an open-source multi-tenant paper intelligence platform.

## Task: F2

Refer to the task spec in `docs/0311-tasks.md` under the section for Task F2: Public Paper Library.

## Project Context
- Monorepo: `frontend/` (Next.js 16, React 19, port 3100), `backend/` (FastAPI, port 8100), `workers/` (Python pipeline), `db/` (PostgreSQL + pgvector)
- Read `ARCHITECTURE.md` and `CLAUDE.md` for conventions before writing code.
- Branch name: `codex/feat/f2`

## What Already Exists (from Round 1+2)
- `frontend/app/(public)/` — landing page, pricing, about, signup pages (Task F1, merged)
- `frontend/lib/api/client.ts` — API client with `apiRequest()`, auth token resolution, Zod schema validation
- `frontend/lib/api/papers.ts` — paper API hooks (authenticated, workspace-scoped)
- `backend/app/routers/papers.py` — papers router with list, detail, search, scores endpoints (all auth-required)
- `backend/app/semantic_search.py` — pgvector semantic search implementation (Task E1, merged)
- `backend/app/schemas/paper.py` — `PaperListParams` with sort/search/category/date filters
- `db/migrations/002_pgvector.sql` — vector embeddings table and ANN index

## Instructions
1. Read the full task spec for F2 in `docs/0311-tasks.md`
2. Read `ARCHITECTURE.md` and `CLAUDE.md`
3. Read `frontend/app/(public)/page.tsx` and `frontend/app/(public)/layout.tsx` to understand the public page patterns
4. Read `backend/app/routers/papers.py` and `backend/app/schemas/paper.py` to understand existing paper endpoints
5. Add public (no-auth) paper API endpoints in backend — browse, detail, search
6. Create `frontend/app/(public)/papers/page.tsx` — paper list with filters (title, author, category, date)
7. Create `frontend/app/(public)/papers/[id]/page.tsx` — paper detail page with summary, figures, metadata
8. Add SEO-friendly metadata and URLs
9. Reuse existing `apiRequest()` client without auth token for public endpoints
10. Write backend tests for public paper endpoints
11. Make sure `ruff check`, `mypy`, `pytest`, `tsc --noEmit`, and `next build` all pass
12. Commit with a clear message, push, and create a PR to `main`
```

---

## Workstream F3 — Billing Integration (Stripe)

```
You are working on the Scivly project — an open-source multi-tenant paper intelligence platform.

## Task: F3

Refer to the task spec in `docs/0311-tasks.md` under the section for Task F3: Billing Integration (Stripe).

## Project Context
- Monorepo: `frontend/` (Next.js 16, React 19, port 3100), `backend/` (FastAPI, port 8100), `workers/` (Python pipeline), `db/` (PostgreSQL + pgvector)
- Read `ARCHITECTURE.md` and `CLAUDE.md` for conventions before writing code.
- Branch name: `codex/feat/f3`

## What Already Exists (from Round 1+2)
- `backend/app/middleware/auth.py` — Clerk JWT auth middleware (Task B1, merged)
- `backend/app/routers/usage.py` — usage tracking endpoint (workspace-scoped)
- `backend/app/api_key_auth.py` — API key auth with rate limiting (Task G1, merged)
- `db/migrations/001_initial_schema.sql` — `billing_events`, `usage_logs`, `workspaces` tables already defined
- `frontend/app/(public)/pricing/page.tsx` — static pricing page (Task F1, merged)
- `frontend/app/workspace/settings/page.tsx` — workspace settings page with API keys tab (Task G1, merged)

## Instructions
1. Read the full task spec for F3 in `docs/0311-tasks.md`
2. Read `ARCHITECTURE.md` and `CLAUDE.md`
3. Read `db/migrations/001_initial_schema.sql` to understand `billing_events`, `usage_logs`, and `workspaces` table schemas
4. Read `backend/app/routers/usage.py` and `frontend/app/(public)/pricing/page.tsx` for existing usage/pricing patterns
5. Backend: add `stripe` to `backend/requirements.txt`, implement Stripe webhook handler, subscription CRUD endpoints
6. Backend: implement plan-based usage limits enforcement (Free/Pro tiers)
7. Frontend: wire pricing page to Stripe Checkout, add billing portal link to workspace settings
8. Add a new DB migration for any Stripe-specific columns (e.g. `stripe_customer_id`, `stripe_subscription_id` on workspaces)
9. Write tests with mocked Stripe API calls
10. Make sure `ruff check`, `mypy`, `pytest`, `tsc --noEmit`, and `next build` all pass
11. Commit with a clear message, push, and create a PR to `main`
```

---

## Workstream G2 — Webhook Delivery System

```
You are working on the Scivly project — an open-source multi-tenant paper intelligence platform.

## Task: G2

Refer to the task spec in `docs/0311-tasks.md` under the section for Task G2: Webhook Delivery System.

## Project Context
- Monorepo: `frontend/` (Next.js 16, React 19, port 3100), `backend/` (FastAPI, port 8100), `workers/` (Python pipeline), `db/` (PostgreSQL + pgvector)
- Read `ARCHITECTURE.md` and `CLAUDE.md` for conventions before writing code.
- Branch name: `codex/feat/g2`

## What Already Exists (from Round 1+2)
- `backend/app/routers/webhooks.py` — webhook router stub (CRUD skeleton, no real delivery)
- `backend/app/middleware/auth.py` — Clerk JWT auth middleware (Task B1, merged)
- `backend/app/api_key_auth.py` — API key auth + rate limiting patterns (Task G1, merged)
- `db/migrations/001_initial_schema.sql` — `webhooks` table with `url`, `secret`, `event_types`, `is_active` columns
- `workers/common/pipeline.py` — Pipeline infrastructure with step events
- `workers/common/runner.py` — Task runner for background jobs

## Instructions
1. Read the full task spec for G2 in `docs/0311-tasks.md`
2. Read `ARCHITECTURE.md` and `CLAUDE.md`
3. Read `backend/app/routers/webhooks.py` to understand the existing stub
4. Read `db/migrations/001_initial_schema.sql` to understand the `webhooks` table schema
5. Read `workers/common/pipeline.py` and `workers/common/runner.py` for pipeline event patterns
6. Implement webhook registration, update, delete, and list endpoints (complete the stub)
7. Implement event dispatch: emit events (`paper.matched`, `paper.enriched`, `digest.ready`, `digest.delivered`) from pipeline steps
8. Implement delivery with HMAC-SHA256 signature verification, retry logic (3 attempts, exponential backoff)
9. Add delivery log tracking (sent, failed, retrying) — add a migration if needed for delivery log table
10. Frontend: add webhook management UI in workspace settings (next to API keys tab)
11. Write tests covering registration, dispatch, signature verification, and retry behavior
12. Make sure `ruff check`, `mypy`, `pytest`, `tsc --noEmit`, and `next build` all pass
13. Commit with a clear message, push, and create a PR to `main`
```
