# Codex Parallel Workstreams

This document defines 5 independent workstreams for Codex agents working in separate git worktrees.
Each workstream can start immediately and run in parallel with minimal merge conflicts.

> **Port Warning**: The developer has another project running locally that may occupy common ports
> (3000, 3001, 5432, 6379, 8000, 8080, etc.). All workstreams that start a dev server **MUST** use
> non-default ports and make them configurable via environment variables. Recommended port range for
> Scivly development: **3100-3199** (frontend), **8100-8199** (backend), **6399** (Redis test).

> **Language Convention**: Code, comments, commit messages, docstrings, and API docs must be in
> English. Chat and collaboration may be in Chinese.

> **Branch Naming**: Each workstream should work on its own branch named
> `codex/<workstream-short-name>` (e.g., `codex/db-schema`). Branch off `main`.

> **Key References**: Read `ARCHITECTURE.md`, `AGENTS.md`, and `docs/product/paper-triage-scoring.md`
> before starting. These are the source of truth.

---

## Workstream 1: Database Schema & Migrations

**Branch**: `codex/db-schema`
**Scope**: `db/migrations/`, `db/seeds/`, `backend/app/models/` (SQLAlchemy model stubs only)
**Purpose**: Design and implement the complete PostgreSQL schema for Scivly, including pgvector support for future retrieval features.

### Context

Scivly is a multi-tenant paper intelligence platform. The database must support:
- Multi-tenant workspaces with user membership
- Paper metadata storage with arXiv-first design
- Paper scoring and triage records with full explainability
- Digest scheduling and delivery tracking
- Chat/QA history
- Usage accounting and billing records
- Webhook and API key management

### Task Details

1. **Create a migration framework**
   - Use raw SQL migration files with sequential numbering: `db/migrations/001_initial_schema.sql`, `002_...`, etc.
   - Each migration file should be idempotent (use `IF NOT EXISTS` where possible)
   - Include a `db/migrations/README.md` explaining how to run migrations

2. **Design and implement these table groups** (in one or more migration files):

   **Auth & Tenancy**
   - `users` — id (uuid), email, name, avatar_url, auth_provider, auth_provider_id, created_at, updated_at
   - `workspaces` — id (uuid), name, slug, owner_id (fk users), plan, created_at
   - `workspace_members` — workspace_id, user_id, role (owner/admin/member), joined_at

   **Subscriptions & Interests**
   - `topic_profiles` — id, workspace_id, name, categories (text[]), keywords (text[]), embedding (vector), is_default, created_at
   - `author_watchlist` — id, workspace_id, author_name, arxiv_author_id, notes
   - `notification_channels` — id, workspace_id, channel_type (email/telegram/discord/webhook), config (jsonb), is_active

   **Papers & Scoring**
   - `papers` — id, arxiv_id (unique), version, title, abstract, authors (jsonb), categories (text[]), primary_category, comment, journal_ref, doi, published_at, updated_at, raw_metadata (jsonb), created_at
   - `paper_scores` — id, paper_id (fk), workspace_id (fk), profile_id (fk), score_version, total_score (numeric), topical_relevance (numeric), prestige_priors (numeric), actionability (numeric), profile_fit (numeric), novelty_diversity (numeric), penalties (numeric), matched_rules (jsonb), threshold_decision (text), llm_rerank_delta (numeric), llm_rerank_reasons (jsonb), created_at
   - `paper_enrichments` — id, paper_id (fk), title_zh (text), abstract_zh (text), one_line_summary (text), key_points (jsonb), method_summary (text), conclusion_summary (text), limitations (text), figure_descriptions (jsonb), enrichment_model (text), enrichment_cost (numeric), created_at

   **Digests & Delivery**
   - `digest_schedules` — id, workspace_id, cron_expression, timezone, channel_ids (uuid[]), is_active, created_at
   - `digests` — id, workspace_id, schedule_id, period_start, period_end, paper_ids (uuid[]), content (jsonb), status (draft/sent/failed), created_at
   - `deliveries` — id, digest_id, channel_id, status (queued/sent/failed), attempts, last_error, sent_at, created_at

   **Chat & QA**
   - `chat_sessions` — id, workspace_id, user_id, paper_id (nullable), session_type (paper_qa/digest_qa/general), created_at
   - `chat_messages` — id, session_id (fk), role (user/assistant), content (text), token_count, model, created_at

   **Developer & Billing**
   - `api_keys` — id, workspace_id, name, key_hash, prefix, scopes (text[]), last_used_at, expires_at, created_at
   - `webhooks` — id, workspace_id, url, events (text[]), secret_hash, is_active, created_at
   - `webhook_deliveries` — id, webhook_id, event_type, payload (jsonb), status, attempts, last_error, created_at
   - `usage_records` — id, workspace_id, record_type (api_call/llm_token/pdf_download/delivery), quantity, unit_cost, metadata (jsonb), recorded_at

   **Task Tracking** (for the worker pipeline)
   - `pipeline_tasks` — id, workspace_id, paper_id, task_type (sync/match/fetch/parse/enrich/deliver/index), status (queued/running/completed/failed/dead), idempotency_key (unique), attempts, max_attempts, last_error, cost (numeric), started_at, completed_at, created_at

3. **Enable pgvector**
   - `CREATE EXTENSION IF NOT EXISTS vector;`
   - Add vector columns where needed (topic_profiles.embedding, and a future papers.embedding)

4. **Create seed data** in `db/seeds/`
   - `db/seeds/demo_workspace.sql` — A demo workspace with sample topic profiles
   - `db/seeds/sample_papers.sql` — 5-10 sample arXiv papers with realistic metadata

5. **Create SQLAlchemy model stubs** in `backend/app/models/`
   - One file per table group: `auth.py`, `papers.py`, `digests.py`, `chat.py`, `billing.py`, `pipeline.py`
   - Use SQLAlchemy 2.0 declarative style with `mapped_column`
   - These are stubs for the Backend API workstream to build on — keep them minimal but correct
   - Add an `__init__.py` that imports all models

### File Scope (only touch these paths)

```
db/migrations/001_initial_schema.sql
db/migrations/002_pgvector.sql
db/migrations/README.md
db/seeds/demo_workspace.sql
db/seeds/sample_papers.sql
backend/app/models/__init__.py
backend/app/models/auth.py
backend/app/models/papers.py
backend/app/models/digests.py
backend/app/models/chat.py
backend/app/models/billing.py
backend/app/models/pipeline.py
```

### Acceptance Criteria

- [ ] All migration SQL files are syntactically valid PostgreSQL
- [ ] Tables use UUIDs as primary keys with `gen_random_uuid()` defaults
- [ ] All foreign keys, indexes, and constraints are defined
- [ ] `paper_scores` table matches the scoring design in `docs/product/paper-triage-scoring.md`
- [ ] pgvector extension is enabled and vector columns are defined
- [ ] Seed SQL inserts run without errors on a fresh schema
- [ ] SQLAlchemy models match the SQL schema exactly
- [ ] A `db/migrations/README.md` explains migration order and how to apply them
- [ ] No port usage — this workstream should not start any server process

---

## Workstream 2: Backend API Skeleton

**Branch**: `codex/backend-api`
**Scope**: `backend/` (except `backend/app/models/` which is Workstream 1's territory — define your own Pydantic schemas independently)
**Purpose**: Build the FastAPI application structure with route stubs, Pydantic request/response schemas, middleware, and a working dev server.

### Context

The backend is a FastAPI service that serves all business APIs for the frontend and external consumers. At this stage, we need the skeleton: project structure, route organization, Pydantic schemas, auth middleware stub, error handling, CORS, and health checks. Routes should return mock/placeholder data for now — real DB integration comes later.

### Task Details

1. **Project setup**
   - Create `backend/requirements.txt` with: `fastapi>=0.115`, `uvicorn[standard]>=0.34`, `pydantic>=2.10`, `python-dotenv>=1.1`
   - Create `backend/app/main.py` as the FastAPI entrypoint
   - Create `backend/app/__init__.py`
   - **Port**: The dev server MUST use port **8100** (not 8000) to avoid conflicts with other local projects. Set this in `backend/app/main.py` and document it.

2. **Application structure**
   ```
   backend/
     requirements.txt
     app/
       __init__.py
       main.py              # FastAPI app, CORS, lifespan, mount routers
       config.py             # Settings from env vars using pydantic-settings pattern
       deps.py               # Dependency injection stubs (get_db, get_current_user, etc.)
       middleware/
         __init__.py
         auth.py             # Auth middleware stub (extract user from header, return mock user for now)
         error_handler.py    # Global exception handlers
       routers/
         __init__.py
         health.py           # GET /health, GET /ready
         auth.py             # POST /auth/login, POST /auth/callback, GET /auth/me
         workspaces.py       # CRUD for workspaces
         interests.py        # CRUD for topic profiles, author watchlists
         papers.py           # List/get/search papers, get scores
         digests.py          # List/get/preview digests, manage schedules
         chat.py             # Create session, send message, get history
         webhooks.py         # CRUD for webhooks
         api_keys.py         # CRUD for API keys
         usage.py            # Get usage stats
       schemas/
         __init__.py
         auth.py             # UserOut, LoginRequest, etc.
         workspace.py        # WorkspaceCreate, WorkspaceOut, etc.
         paper.py            # PaperOut, PaperScoreOut, PaperListParams, etc.
         interest.py         # TopicProfileCreate, TopicProfileOut, AuthorWatchlistOut, etc.
         digest.py           # DigestOut, DigestScheduleCreate, etc.
         chat.py             # ChatSessionOut, ChatMessageCreate, etc.
         webhook.py          # WebhookCreate, WebhookOut, etc.
         common.py           # Pagination, ErrorResponse, etc.
       tests/
         __init__.py
         test_health.py      # Test health endpoints
         conftest.py         # pytest fixtures, TestClient setup
   ```

3. **Key implementation details**
   - All routes should return realistic mock data (not empty responses)
   - Use proper HTTP status codes and error responses
   - Implement pagination schema: `{ items: [...], total: int, page: int, per_page: int }`
   - CORS: allow `http://localhost:3100` and `http://localhost:3000` origins
   - Add OpenAPI tags for each router group
   - Health endpoint should return `{ status: "ok", version: "0.1.0" }`

4. **Testing**
   - Write basic tests in `backend/app/tests/test_health.py` using `httpx.AsyncClient` or `TestClient`
   - Tests should verify health endpoint returns 200
   - Add `pytest` and `httpx` to requirements.txt

### Port Configuration

```python
# In main.py or as CLI default:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8100
# The port 8100 is chosen to avoid conflicts with other local projects.
# It can be overridden with: SCIVLY_API_PORT=8100 environment variable.
```

### File Scope (only touch these paths)

```
backend/requirements.txt
backend/app/__init__.py
backend/app/main.py
backend/app/config.py
backend/app/deps.py
backend/app/middleware/__init__.py
backend/app/middleware/auth.py
backend/app/middleware/error_handler.py
backend/app/routers/__init__.py
backend/app/routers/health.py
backend/app/routers/auth.py
backend/app/routers/workspaces.py
backend/app/routers/interests.py
backend/app/routers/papers.py
backend/app/routers/digests.py
backend/app/routers/chat.py
backend/app/routers/webhooks.py
backend/app/routers/api_keys.py
backend/app/routers/usage.py
backend/app/schemas/__init__.py
backend/app/schemas/auth.py
backend/app/schemas/workspace.py
backend/app/schemas/paper.py
backend/app/schemas/interest.py
backend/app/schemas/digest.py
backend/app/schemas/chat.py
backend/app/schemas/webhook.py
backend/app/schemas/common.py
backend/app/tests/__init__.py
backend/app/tests/test_health.py
backend/app/tests/conftest.py
```

### Acceptance Criteria

- [ ] `pip install -r backend/requirements.txt` succeeds
- [ ] `uvicorn app.main:app --port 8100` starts without errors
- [ ] `GET /health` returns `200 { status: "ok" }`
- [ ] `GET /docs` shows Swagger UI with all route groups
- [ ] All route stubs return proper mock responses with correct Pydantic schemas
- [ ] CORS headers are set for localhost origins
- [ ] Auth middleware stub is in place (accepts any Bearer token for now)
- [ ] `pytest backend/app/tests/` passes
- [ ] Server runs on port **8100**, NOT 8000

---

## Workstream 3: arXiv Sync Worker

**Branch**: `codex/arxiv-worker`
**Scope**: `workers/arxiv/`, `workers/common/` (shared utilities only)
**Purpose**: Implement the arXiv paper fetching, deduplication, and metadata scoring pipeline as described in `docs/product/paper-triage-scoring.md`.

### Context

This is the core data ingestion pipeline. It fetches papers from the arXiv API, deduplicates them, applies hard filters, and computes metadata scores using the triage system defined in `docs/product/paper-triage-scoring.md` and `config/reference/paper_triage_defaults.yaml`. At this stage, it should work as a standalone CLI tool that can be tested without the full backend.

### Task Details

1. **Project setup**
   - Create `workers/requirements.txt` with: `httpx>=0.28`, `pyyaml>=6.0`, `pydantic>=2.10`, `numpy>=2.0`, `python-dotenv>=1.1`
   - Create `workers/arxiv/__init__.py`
   - Create `workers/common/__init__.py`

2. **arXiv API client** (`workers/arxiv/client.py`)
   - Implement an async HTTP client for the arXiv API (use `httpx`)
   - Support fetching by category, date range, and search query
   - Parse Atom XML responses into structured Python objects
   - Respect arXiv API rate limits (max 1 request per 3 seconds)
   - Handle pagination for large result sets

3. **Data models** (`workers/arxiv/models.py`)
   - Pydantic models for:
     - `ArxivPaper` — arxiv_id, version, title, abstract, authors (list of AuthorInfo), categories, primary_category, comment, journal_ref, doi, published, updated
     - `AuthorInfo` — name, affiliation (optional)
     - `ScoringResult` — paper_id, total_score, component_scores (dict), matched_rules (list), threshold_decision, explanation
     - `ComponentScores` — topical_relevance, prestige_priors, actionability, profile_fit, novelty_diversity, penalties

4. **Hard filters** (`workers/arxiv/filters.py`)
   - Implement Stage 1 from the scoring design:
     - Category allowlist check
     - Reject withdrawn/errata
     - Reject missing title or abstract
     - Min abstract length check
     - Max title length check
   - Load filter config from `config/reference/paper_triage_defaults.yaml`

5. **Metadata scorer** (`workers/arxiv/scorer.py`)
   - Implement Stage 2 from the scoring design:
     - **Topical relevance** (45 pts): keyword matching against profile, category prior scoring
     - **Prestige priors** (20 pts): author/institution/lab lookup with normalization formula
     - **Actionability** (15 pts): detect code links, benchmarks, venue mentions in comments
     - **Profile fit** (10 pts): match against saved themes and tracked authors
     - **Novelty/diversity** (10 pts): basic same-day dedup scoring
     - **Penalties** (-25 pts): weak abstract, keyword conflicts, etc.
   - Load scoring config from `config/reference/paper_triage_defaults.yaml`
   - Load institution priors from `config/reference/institution_priors.yaml`
   - Load lab priors from `config/reference/lab_priors.yaml`
   - Return structured `ScoringResult` with full explainability

6. **Deduplication** (`workers/arxiv/dedup.py`)
   - Deduplicate by canonical `arxiv_id` (strip version suffix for comparison)
   - Merge cross-listed papers into single records
   - Track version updates

7. **CLI entry point** (`workers/arxiv/cli.py`)
   - A simple CLI that:
     - Fetches recent papers from specified categories
     - Applies hard filters
     - Scores remaining papers
     - Outputs results as JSON to stdout or a file
   - Usage: `python -m workers.arxiv.cli --categories cs.CL cs.AI --days 1 --output results.json`

8. **Tests** (`workers/arxiv/tests/`)
   - `test_filters.py` — test hard filter logic with mock papers
   - `test_scorer.py` — test scoring with known inputs and expected ranges
   - `test_dedup.py` — test deduplication logic
   - Use fixtures with realistic arXiv paper data

### File Scope (only touch these paths)

```
workers/requirements.txt
workers/common/__init__.py
workers/common/config.py          # YAML config loader utility
workers/arxiv/__init__.py
workers/arxiv/client.py
workers/arxiv/models.py
workers/arxiv/filters.py
workers/arxiv/scorer.py
workers/arxiv/dedup.py
workers/arxiv/cli.py
workers/arxiv/tests/__init__.py
workers/arxiv/tests/test_filters.py
workers/arxiv/tests/test_scorer.py
workers/arxiv/tests/test_dedup.py
workers/arxiv/tests/conftest.py
```

### Acceptance Criteria

- [ ] `pip install -r workers/requirements.txt` succeeds
- [ ] `python -m workers.arxiv.cli --categories cs.CL --days 1` fetches real papers and outputs scored JSON
- [ ] Hard filters correctly reject withdrawn, errata, and incomplete papers
- [ ] Scorer produces scores in 0-100 range with per-component breakdown
- [ ] Scoring config is loaded from `config/reference/paper_triage_defaults.yaml` (not hardcoded)
- [ ] Institution and lab priors are loaded from `config/reference/` YAML files
- [ ] Deduplication correctly merges cross-listed papers
- [ ] All scoring results include explainability fields (matched_rules, component_scores, threshold_decision)
- [ ] `pytest workers/arxiv/tests/` passes
- [ ] No web server — this is a CLI/library module only, no port usage

---

## Workstream 4: Worker Infrastructure & Queue

**Branch**: `codex/worker-infra`
**Scope**: `workers/common/`, `workers/digest/` (skeleton only)
**Purpose**: Build the shared worker infrastructure: task queue abstraction, retry logic, pipeline step framework, and a digest worker skeleton.

### Context

From ARCHITECTURE.md section 8: every task must have idempotency keys, retry, timeout, dead-letter, workspace ownership, cost recording, and replayability. The unified status flow is:
`queued -> syncing -> matched -> fetched -> parsed -> enriched -> delivered -> indexed`

This workstream builds the framework that all workers (arxiv, digest, delivery) will use. It should work with Redis as the queue backend but also support a simple in-memory queue for local development without Redis.

### Task Details

1. **Project dependencies**
   - Add to `workers/requirements.txt` (coordinate with Workstream 3 — add lines, don't overwrite):
     `redis>=5.2`, `rq>=2.1` (or keep it simple with raw Redis)
   - If `workers/requirements.txt` already exists from Workstream 3, append your deps to it

2. **Task models** (`workers/common/task.py`)
   - Pydantic models:
     - `TaskPayload` — task_id (uuid), task_type (enum: sync/match/fetch/parse/enrich/deliver/index), workspace_id, paper_id (optional), idempotency_key, payload (dict), created_at
     - `TaskResult` — task_id, status (completed/failed), result (dict), error (optional), cost (numeric), duration_ms
     - `TaskStatus` enum: queued, running, completed, failed, dead

3. **Queue abstraction** (`workers/common/queue.py`)
   - Abstract base class `TaskQueue` with methods:
     - `enqueue(task: TaskPayload) -> str` — returns task ID
     - `dequeue(task_type: str, timeout: int) -> TaskPayload | None`
     - `ack(task_id: str, result: TaskResult)`
     - `nack(task_id: str, error: str)` — increment attempt count, re-queue or dead-letter
     - `get_status(task_id: str) -> TaskStatus`
   - `RedisTaskQueue` — implementation using Redis lists and hashes
   - `InMemoryTaskQueue` — implementation for local dev/testing without Redis
   - Queue selection via `SCIVLY_QUEUE_BACKEND=redis|memory` env var

4. **Pipeline step framework** (`workers/common/pipeline.py`)
   - Base class `PipelineStep`:
     - `step_type: str` — matches task_type enum
     - `max_attempts: int` — default 3
     - `timeout_seconds: int` — default 300
     - `async execute(payload: dict) -> dict` — abstract, override in concrete steps
     - Built-in retry with exponential backoff
     - Built-in timeout handling
     - Cost tracking hook
     - Idempotency check before execution
   - `Pipeline` class that chains steps and manages the status flow

5. **Worker runner** (`workers/common/runner.py`)
   - A worker process that:
     - Connects to the queue
     - Polls for tasks of specified types
     - Dispatches to the correct PipelineStep
     - Handles graceful shutdown on SIGTERM/SIGINT
   - CLI: `python -m workers.common.runner --types sync match --queue memory`
   - **Port**: If Redis is used, connect to `REDIS_URL` from env. Default to `redis://localhost:6399` for development (not 6379, to avoid conflicts with other local projects). Document this clearly.

6. **Digest worker skeleton** (`workers/digest/`)
   - `workers/digest/__init__.py`
   - `workers/digest/assembler.py` — `DigestAssembler` class that:
     - Takes a list of scored papers
     - Groups by topic/category
     - Selects top papers per group
     - Produces a structured digest (title, sections, paper summaries)
     - Returns JSON-serializable digest content
   - `workers/digest/steps.py` — PipelineStep implementations:
     - `AssembleDigestStep` — wraps DigestAssembler
     - `DeliverDigestStep` — stub that logs delivery (real delivery integration later)
   - Keep it simple — no actual email/telegram sending yet

7. **Tests** (`workers/common/tests/`)
   - `test_queue.py` — test InMemoryTaskQueue enqueue/dequeue/ack/nack
   - `test_pipeline.py` — test PipelineStep retry, timeout, idempotency
   - `test_runner.py` — test worker runner with in-memory queue

### File Scope (only touch these paths)

```
workers/common/__init__.py
workers/common/task.py
workers/common/queue.py
workers/common/pipeline.py
workers/common/runner.py
workers/common/tests/__init__.py
workers/common/tests/test_queue.py
workers/common/tests/test_pipeline.py
workers/common/tests/test_runner.py
workers/common/tests/conftest.py
workers/digest/__init__.py
workers/digest/assembler.py
workers/digest/steps.py
workers/digest/tests/__init__.py
workers/digest/tests/test_assembler.py
```

### Acceptance Criteria

- [ ] `InMemoryTaskQueue` passes all queue operation tests (enqueue, dequeue, ack, nack, dead-letter)
- [ ] `PipelineStep` correctly retries failed tasks with exponential backoff
- [ ] `PipelineStep` correctly times out long-running tasks
- [ ] Idempotency key prevents duplicate execution
- [ ] Worker runner can poll and dispatch tasks from in-memory queue
- [ ] `DigestAssembler` produces structured digest from scored paper list
- [ ] `pytest workers/common/tests/ workers/digest/tests/` passes
- [ ] Redis default port is **6399** (not 6379) — documented in code and configurable via `REDIS_URL`
- [ ] No web server — worker processes only, no HTTP port usage

---

## Workstream 5: Frontend User Workspace

**Branch**: `codex/frontend-workspace`
**Scope**: `frontend/` (new pages and components only — do NOT modify existing landing page or admin dashboard)
**Purpose**: Build the user-facing workspace pages: interests configuration, paper feed, digest viewer, and Q&A interface. Install missing UI dependencies from the architecture spec.

### Context

The frontend currently has: landing page, admin dashboard with mock data, and basic components.
What's missing: the actual user workspace where users configure their interests, browse scored papers, view digests, and ask questions about papers. These pages should use mock data for now (no real API calls yet), but the data structures should match what Workstream 2 (Backend API) defines.

### Task Details

1. **Install dependencies**
   - Install packages specified in ARCHITECTURE.md section 10:
     ```
     npm install @tanstack/react-query zod react-hook-form @hookform/resolvers
     ```
   - Install shadcn/ui (follow the shadcn/ui Next.js setup guide — run `npx shadcn@latest init`)
   - After shadcn init, add these components: `button`, `card`, `input`, `textarea`, `select`, `badge`, `dialog`, `tabs`, `separator`, `dropdown-menu`, `toast`
   - **Port**: Configure Next.js dev server to use port **3100** (not 3000). Add to `frontend/package.json` scripts: `"dev": "next dev --port 3100"`. Document this change.

2. **API client layer** (`frontend/lib/api/`)
   - `frontend/lib/api/client.ts` — Base fetch wrapper with:
     - Base URL from `NEXT_PUBLIC_API_URL` env var (default: `http://localhost:8100`)
     - Auth header injection
     - Error handling
     - Type-safe response parsing
   - `frontend/lib/api/papers.ts` — Paper API functions (listPapers, getPaper, getPaperScores)
   - `frontend/lib/api/interests.ts` — Interest API functions (getProfiles, createProfile, etc.)
   - `frontend/lib/api/digests.ts` — Digest API functions (listDigests, getDigest)
   - `frontend/lib/api/types.ts` — TypeScript types matching the Pydantic schemas from Workstream 2

3. **Mock data** (`frontend/lib/mock/`)
   - `frontend/lib/mock/papers.ts` — 10 realistic mock papers with arXiv-style metadata and scores
   - `frontend/lib/mock/profiles.ts` — 2-3 mock topic profiles
   - `frontend/lib/mock/digests.ts` — 2 mock digests with paper lists
   - Mock data should be realistic and match the TypeScript types

4. **Workspace layout** (`frontend/app/workspace/layout.tsx`)
   - Sidebar navigation with sections: Feed, Interests, Digests, Q&A, Settings
   - Workspace switcher in header (mock single workspace for now)
   - Responsive: sidebar collapses on mobile

5. **Pages to build**:

   **Paper Feed** (`frontend/app/workspace/feed/page.tsx`)
   - List of papers with scores, sorted by score descending
   - Each paper card shows: title, authors, score badge, primary category, one-line summary
   - Filter/sort controls: by category, score range, date
   - Click to expand paper details with abstract, full scores breakdown, matched rules

   **Interests** (`frontend/app/workspace/interests/page.tsx`)
   - List of topic profiles with category tags
   - "Add Profile" dialog with form: name, categories (multi-select), keywords (tag input)
   - Author watchlist section: list of tracked authors with add/remove
   - Notification channel configuration (show UI, no real integration)

   **Digest Viewer** (`frontend/app/workspace/digests/page.tsx`)
   - List of past digests with date range and paper count
   - Click to view digest: grouped papers by topic, each with title, score, one-line summary
   - Digest schedule configuration UI

   **Q&A** (`frontend/app/workspace/qa/page.tsx`)
   - Chat-style interface
   - Paper selector: pick a paper to ask about
   - Message input with send button
   - Display mock conversation history
   - Show "powered by" model info

6. **Shared components** (`frontend/components/workspace/`)
   - `PaperCard.tsx` — Reusable paper display card
   - `ScoreBadge.tsx` — Colored badge showing paper score (green/yellow/red by threshold)
   - `CategoryTag.tsx` — arXiv category tag
   - `ProfileForm.tsx` — Topic profile creation/edit form

### File Scope (only touch these paths)

```
frontend/package.json                          # Add dependencies only, don't change existing scripts except dev port
frontend/lib/api/client.ts
frontend/lib/api/papers.ts
frontend/lib/api/interests.ts
frontend/lib/api/digests.ts
frontend/lib/api/types.ts
frontend/lib/mock/papers.ts
frontend/lib/mock/profiles.ts
frontend/lib/mock/digests.ts
frontend/app/workspace/layout.tsx
frontend/app/workspace/feed/page.tsx
frontend/app/workspace/interests/page.tsx
frontend/app/workspace/digests/page.tsx
frontend/app/workspace/qa/page.tsx
frontend/components/workspace/PaperCard.tsx
frontend/components/workspace/ScoreBadge.tsx
frontend/components/workspace/CategoryTag.tsx
frontend/components/workspace/ProfileForm.tsx
frontend/components/ui/*                       # shadcn/ui generated components
frontend/components.json                       # shadcn/ui config
frontend/lib/utils.ts                          # shadcn/ui utility (cn function)
```

### Do NOT Touch

- `frontend/app/page.tsx` (landing page)
- `frontend/app/admin/**` (admin dashboard)
- `frontend/components/SiteHeader.tsx`, `SiteFooter.tsx` (existing components)
- `frontend/app/docs/**` (docs pages)

### Acceptance Criteria

- [ ] `npm install` succeeds with new dependencies
- [ ] `npm run dev` starts on port **3100** (NOT 3000)
- [ ] shadcn/ui is initialized and components are installed
- [ ] `/workspace/feed` shows paper cards with mock data, score badges, and filtering
- [ ] `/workspace/interests` shows topic profiles and author watchlist with add/edit UI
- [ ] `/workspace/digests` shows digest list and detail view
- [ ] `/workspace/qa` shows chat interface with mock conversation
- [ ] Workspace sidebar navigation works across all pages
- [ ] All pages are responsive (desktop + mobile)
- [ ] TypeScript types match the API schema design
- [ ] Mock data is realistic and uses proper arXiv paper metadata
- [ ] No console errors in the browser
- [ ] Existing landing page and admin pages are unaffected

---

## Port Summary

| Service | Default Port | Scivly Dev Port | Env Var |
|---------|-------------|-----------------|---------|
| Next.js frontend | 3000 | **3100** | — (set in package.json) |
| FastAPI backend | 8000 | **8100** | `SCIVLY_API_PORT` |
| Redis | 6379 | **6399** | `REDIS_URL` |
| PostgreSQL | 5432 | **5432** (keep default) | `DATABASE_URL` |

## Dependency Graph

```
Workstream 1 (DB Schema)     ──┐
Workstream 2 (Backend API)   ──┤── All independent, can start simultaneously
Workstream 3 (arXiv Worker)  ──┤
Workstream 4 (Worker Infra)  ──┤
Workstream 5 (Frontend)      ──┘

Post-merge integration order:
  1 (DB) + 2 (API) → wire real DB connections
  1 (DB) + 3 (arXiv) + 4 (Infra) → wire real pipeline
  2 (API) + 5 (Frontend) → wire real API calls
```

## How to Use This Document

1. Create 5 git worktrees from `main`
2. In each worktree, check out the designated branch
3. Give the corresponding workstream section as the prompt to a Codex agent
4. Each agent works independently within its file scope
5. After all 5 complete, merge in order: WS1 → WS2 → WS4 → WS3 → WS5
6. Resolve any minor conflicts (mostly `workers/requirements.txt` and `workers/common/__init__.py`)
