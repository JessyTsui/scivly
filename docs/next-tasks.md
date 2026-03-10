# Scivly Next Tasks

> Generated: 2026-03-11
> Status: 5 bootstrap workstreams completed, entering feature pipeline phase.
> Each task is designed to be **independently executable in a worktree**.

---

## Phase A: CI/CD & DevOps Foundation

### Task A1: Frontend CI — Lint, Type-check, Build

**Background**: Frontend (`frontend/`) uses Next.js 16 + TypeScript + Tailwind v4. No CI exists yet; all validation is manual.

**Goal**: Every PR automatically runs `tsc --noEmit`, ESLint, and `next build` to catch regressions before merge.

**Scope**:
- `.github/workflows/frontend-ci.yml`
- Trigger on push/PR when `frontend/**` changes
- Steps: install (pnpm/npm), `tsc --noEmit`, `eslint .`, `next build`
- Cache `node_modules` and `.next/cache`

**Test**:
- Push a branch with a type error → CI fails
- Push a clean branch → CI passes, build artifact is valid

**Done when**: Green check on every PR touching frontend code.

---

### Task A2: Backend CI — Lint, Type-check, Test

**Background**: Backend (`backend/`) is FastAPI + Python 3.11+. Has pytest tests but they're only run locally.

**Goal**: Every PR runs `ruff check`, `mypy`, and `pytest` on backend code.

**Scope**:
- `.github/workflows/backend-ci.yml`
- Trigger on push/PR when `backend/**` or `workers/**` changes
- Steps: setup Python, install deps from `requirements.txt`, `ruff check`, `pytest -x`
- No database required (tests use mocks)

**Test**:
- Introduce a lint violation → CI fails
- All existing tests pass in CI

**Done when**: Backend + worker tests run automatically on every PR.

---

### Task A3: PR Template & Issue Templates

**Background**: No standardized PR or issue templates exist. PRs vary widely in format.

**Goal**: Consistent PR descriptions and issue categorization.

**Scope**:
- `.github/pull_request_template.md` — sections: Summary, Changes, Test Plan, Checklist
- `.github/ISSUE_TEMPLATE/bug_report.yml` — bug form
- `.github/ISSUE_TEMPLATE/feature_request.yml` — feature form

**Test**:
- Create a new PR → template auto-fills
- Create a new issue → template picker shows

**Done when**: Templates appear in GitHub UI.

---

## Phase B: Auth & Real Data Layer

### Task B1: Auth Integration (Clerk or Better Auth)

**Background**: ARCHITECTURE.md specifies Clerk or Better Auth for login and session management. Currently backend has mock auth middleware that returns a stub user. Frontend has no login flow.

**Goal**: Real user signup/login, JWT session, workspace scoping.

**Scope**:
- Backend: replace mock auth middleware with real JWT verification
- Frontend: add sign-in/sign-up pages, session provider, protected routes
- Database: `auth_users` and `workspaces` tables already exist in schema
- Choose Clerk (hosted) or Better Auth (self-hosted) — recommend Clerk for faster bootstrap

**Test**:
- Sign up a new user → workspace auto-created
- Unauthenticated request to `/api/interests` → 401
- Authenticated request → returns user-scoped data

**Done when**: Real login/logout works end-to-end; all workspace API calls are scoped to the authenticated user.

---

### Task B2: Frontend-Backend API Wiring

**Background**: Frontend currently uses mock data (`frontend/lib/mock-*.ts`). Backend has all API endpoints but they return stub data. Need to connect the two.

**Goal**: Frontend fetches real data from backend API instead of mocks.

**Scope**:
- `frontend/lib/api.ts` — replace mock imports with real `fetch()` calls to `http://localhost:8100`
- Environment variable `NEXT_PUBLIC_API_URL` for API base URL
- TanStack Query hooks already exist, just need real fetch functions
- Handle auth token forwarding from frontend to backend
- Error handling and loading states

**Test**:
- Start both frontend (3100) and backend (8100)
- Visit `/workspace/feed` → papers load from backend
- Visit `/workspace/interests` → interests load from backend

**Done when**: All 4 workspace pages render data from the real backend API.

---

### Task B3: Database Connection & Migration Runner

**Background**: SQL migrations exist in `db/migrations/` and SQLAlchemy models in `backend/app/models/`, but backend doesn't connect to a real PostgreSQL database yet. All endpoints return mock data.

**Goal**: Backend connects to PostgreSQL, runs migrations on startup (or via CLI), and queries real data.

**Scope**:
- `backend/app/db.py` — SQLAlchemy async engine + session factory
- Migration runner script (or integrate Alembic)
- Update API routers to query real database instead of returning stubs
- `DATABASE_URL` env var (default: `postgresql://localhost:5432/scivly`)
- Docker Compose for local PostgreSQL + Redis

**Test**:
- `docker compose up db` → PostgreSQL starts
- Run migrations → all tables created
- Seed data → demo workspace and sample papers inserted
- Backend queries return real rows

**Done when**: Backend reads/writes from PostgreSQL; migrations are automated.

---

## Phase C: Paper Processing Pipeline

### Task C1: PDF Download Worker

**Background**: arXiv sync worker (PR #9) scores papers and decides which deserve full-text processing. Papers scoring 55+ need PDF download (per `docs/product/paper-triage-scoring.md`). No PDF download step exists yet.

**Goal**: Worker step that downloads PDFs from arXiv and stores them in local filesystem or S3/R2.

**Scope**:
- `workers/pdf/downloader.py` — download PDF by `arxiv_id`
- Respect arXiv rate limits (1 request per 3 seconds)
- Store to configurable path (local or S3/R2 via `boto3`)
- Pipeline step integration with `workers/common/pipeline.py`
- Update paper record with `pdf_path` and `pdf_status`

**Test**:
- Given an `arxiv_id`, PDF downloads successfully
- Rate limiting works (no 429 responses)
- Failed downloads retry with exponential backoff
- Paper record updated in database

**Done when**: PDF download step runs as part of the worker pipeline; PDFs are stored and tracked.

---

### Task C2: PDF Parsing & Text Extraction

**Background**: After PDF download, need to extract structured text, figures, and captions. This is step 7.3 in ARCHITECTURE.md ("Fulltext Processing").

**Goal**: Extract clean text, figures, and table data from academic PDFs.

**Scope**:
- `workers/pdf/parser.py` — PDF text extraction
- Use `pymupdf` (fitz) or `pdfplumber` for text; `pymupdf` for images
- Extract: title, abstract, sections, references, figures with captions
- Output structured JSON per paper
- Pipeline step integration

**Test**:
- Parse a real arXiv PDF → structured JSON output
- Figures extracted as separate images with captions
- Section headers correctly identified
- Handle multi-column layouts

**Done when**: Given a downloaded PDF, outputs structured text + extracted figures.

---

### Task C3: LLM Enrichment — Translation & Summary

**Background**: ARCHITECTURE.md section 7.4 specifies: title translation, abstract translation, one-sentence summary, key points, methods/conclusions/limitations, figure descriptions. This is the core AI value-add.

**Goal**: Use LLM to generate enriched paper metadata in target language (Chinese by default).

**Scope**:
- `workers/enrich/summarizer.py` — LLM-based enrichment
- Input: parsed paper text (from Task C2)
- Output: translated title, translated abstract, one-sentence summary, key points list, method/conclusion/limitation, figure descriptions
- LLM provider abstraction (OpenAI API compatible — support OpenAI, Anthropic, local)
- Prompt templates in `config/prompts/` (keep out of public repo per open-core policy)
- Cost tracking per paper per workspace
- Pipeline step integration

**Test**:
- Given parsed paper text → enriched output in Chinese
- Token usage tracked and recorded
- Different LLM providers work via config
- Prompt templates are loaded from config

**Done when**: Papers are enriched with translations and summaries; costs are tracked.

---

### Task C4: End-to-End Pipeline Orchestration

**Background**: Individual pipeline steps (sync, score, download, parse, enrich) exist separately. Need to chain them into a single pipeline that processes papers from arXiv to enriched digest candidates.

**Goal**: One command runs the full pipeline: sync → score → download → parse → enrich → store.

**Scope**:
- `workers/pipeline/orchestrator.py` — chain all steps
- Status tracking: `queued → syncing → matched → fetched → parsed → enriched`
- Dead letter queue for permanently failed papers
- Configurable pipeline (skip steps, rerun from any point)
- CLI: `python -m workers.pipeline.run --workspace <id> --from sync`

**Test**:
- Run full pipeline → papers go from arXiv to enriched state
- Paper stuck at `fetched` → rerun from `parsed` step only
- Failed paper → goes to dead letter after max retries
- Each step is idempotent (safe to rerun)

**Done when**: Papers can be processed end-to-end automatically; pipeline status visible in database.

---

## Phase D: Digest & Delivery

### Task D1: Digest Assembly & Formatting

**Background**: `workers/digest/assembler.py` exists with basic assembly logic (from PR #7), but doesn't use real enriched paper data. Need to produce actual digest content.

**Goal**: Generate formatted daily digests from enriched papers.

**Scope**:
- Update `workers/digest/assembler.py` to use real enriched data
- Digest format: HTML email template + in-app JSON
- Group papers by topic/score, include translations and key figures
- Configurable digest frequency (daily/weekly)
- Store digest in database with delivery tracking

**Test**:
- Given 10 enriched papers → digest assembled with grouped sections
- HTML output renders correctly in email clients
- In-app JSON renders in frontend digest viewer
- Empty digest (no papers) → skip or send "no papers" notice

**Done when**: Daily digests are generated from enriched papers with proper formatting.

---

### Task D2: Email Delivery Channel

**Background**: ARCHITECTURE.md lists Email as a delivery channel. No email integration exists.

**Goal**: Send digest emails to users.

**Scope**:
- `workers/deliver/email.py` — email sender
- Use Resend, SendGrid, or AWS SES (recommend Resend for simplicity)
- HTML email template with paper cards, figures, scores
- Delivery status tracking (sent, bounced, failed)
- Unsubscribe link support
- Pipeline step integration

**Test**:
- Send a test digest email → arrives in inbox with correct formatting
- Bounce/failure → recorded in database
- Unsubscribe → future digests skip this user

**Done when**: Users receive daily digest emails; delivery status is tracked.

---

### Task D3: Notification Channels — Telegram & Discord

**Background**: ARCHITECTURE.md specifies Telegram, Discord, and Webhook as additional notification channels.

**Goal**: Send digest notifications to Telegram and Discord.

**Scope**:
- `workers/deliver/telegram.py` — Telegram bot message sender
- `workers/deliver/discord.py` — Discord webhook sender
- Condensed format for chat platforms (title, score, one-sentence summary, link)
- User-configurable channel selection in workspace settings
- Backend API endpoint to manage notification preferences

**Test**:
- Configure Telegram bot → receive digest notification
- Configure Discord webhook → receive digest notification
- Disable a channel → no longer receives notifications

**Done when**: Users can choose Telegram/Discord as notification channels.

---

## Phase E: Chat & Retrieval

### Task E1: Vector Indexing with pgvector

**Background**: Database schema already includes pgvector extension (migration 002). Papers need to be indexed for semantic search and chat.

**Goal**: Index paper embeddings for semantic search.

**Scope**:
- `workers/index/embedder.py` — generate embeddings via OpenAI/local model
- Store embeddings in pgvector columns
- ANN index for fast similarity search
- Backend API: `/api/papers/search?q=...` with semantic search
- Pipeline step: `enriched → indexed`

**Test**:
- Index 100 papers → embeddings stored
- Search "transformer attention mechanism" → relevant papers returned
- Search performance < 200ms for 10k papers

**Done when**: Papers are searchable by semantic similarity; search API endpoint works.

---

### Task E2: Paper Chat (Single Paper Q&A)

**Background**: Frontend has a Q&A page (`/workspace/qa`). Backend has a chat router. Neither connects to real LLM or paper context.

**Goal**: Users can ask questions about a specific paper and get contextual answers.

**Scope**:
- Backend: `/api/chat` endpoint with real LLM integration
- RAG: retrieve relevant paper sections + use as context
- Conversation history per paper per user
- Streaming response support (SSE)
- Frontend: wire up Q&A page to real chat API

**Test**:
- Select a paper → ask "What is the main contribution?" → get contextual answer
- Follow-up question uses conversation history
- Streaming response renders progressively in UI

**Done when**: Users can have multi-turn conversations about papers with contextual AI answers.

---

### Task E3: Digest Chat (Cross-Paper Q&A)

**Background**: Beyond single-paper Q&A, users should be able to ask questions across their digest or paper collection.

**Goal**: Users can ask questions that span multiple papers.

**Scope**:
- Backend: extend chat API to support `scope=digest` or `scope=workspace`
- RAG: retrieve relevant chunks across multiple papers via pgvector
- Context assembly from multiple papers with source attribution
- Frontend: toggle between single-paper and cross-paper chat

**Test**:
- Ask "Compare the approaches in today's transformer papers" → answer cites multiple papers
- Source attribution shows which paper each piece came from
- Works with digest scope (today's papers) and workspace scope (all papers)

**Done when**: Cross-paper Q&A works with source attribution.

---

## Phase F: Public Surface & Platform

### Task F1: Landing Page & Marketing Site

**Background**: Frontend has workspace pages but no public-facing pages. README mentions "Public Surface" including website, pricing, and docs.

**Goal**: Build the public marketing pages.

**Scope**:
- `frontend/app/(public)/page.tsx` — landing page
- `frontend/app/(public)/pricing/page.tsx` — pricing page
- `frontend/app/(public)/about/page.tsx` — about page
- Responsive design, SEO metadata, OG images
- Clear CTA to sign up

**Test**:
- Visit `/` → landing page renders with product description
- Visit `/pricing` → pricing tiers displayed
- Mobile responsive

**Done when**: Public pages are live and link to signup.

---

### Task F2: Public Paper Library

**Background**: ARCHITECTURE.md mentions a "public resource library" as part of the Public Surface. Papers that are public domain should be browsable without login.

**Goal**: Public paper browsing with search.

**Scope**:
- `frontend/app/(public)/papers/page.tsx` — paper list with filters
- `frontend/app/(public)/papers/[id]/page.tsx` — paper detail page
- Backend: public API endpoints (no auth required) for browsing
- Search by title, author, category, date
- SEO-friendly URLs and metadata

**Test**:
- Visit `/papers` → browse papers without login
- Search by keyword → results appear
- Paper detail page shows summary, figures, metadata

**Done when**: Public paper browsing works without authentication.

---

### Task F3: Billing Integration (Stripe)

**Background**: ARCHITECTURE.md specifies Stripe for subscriptions and billing. Database schema has `billing_events` and `usage_logs` tables.

**Goal**: Subscription management with Stripe.

**Scope**:
- Backend: Stripe webhook handler, subscription CRUD
- Frontend: pricing page with Stripe Checkout, billing portal link
- Plans: Free tier, Pro tier (configurable limits)
- Usage tracking: papers processed, LLM tokens used, digests sent
- Enforce limits per plan

**Test**:
- Sign up for free tier → limited to N papers/day
- Upgrade via Stripe Checkout → limits increase
- Usage exceeds limit → graceful degradation (not hard block)

**Done when**: Users can subscribe, upgrade/downgrade, and usage is enforced per plan.

---

## Phase G: Developer & Operator Surface

### Task G1: API Key Management & Rate Limiting

**Background**: Backend has API key router stub. Database has `api_keys` table. No real API key generation or rate limiting.

**Goal**: Users can create API keys and use them to access the REST API with rate limits.

**Scope**:
- Backend: API key generation, validation, revocation
- Rate limiting middleware (per key, per workspace)
- Usage tracking per API key
- Frontend: API key management page in workspace settings

**Test**:
- Create API key → can use it in `Authorization: Bearer <key>` header
- Exceed rate limit → 429 response
- Revoke key → subsequent requests fail

**Done when**: API keys work for programmatic access with rate limiting.

---

### Task G2: Webhook Delivery System

**Background**: Backend has webhook router stub. Database has `webhooks` table. No real webhook delivery.

**Goal**: Users can register webhooks and receive event notifications.

**Scope**:
- Backend: webhook registration, event dispatch, retry logic
- Events: `paper.matched`, `paper.enriched`, `digest.ready`, `digest.delivered`
- Signature verification (HMAC-SHA256)
- Delivery log with retry status
- Frontend: webhook management UI

**Test**:
- Register webhook → receive `paper.matched` event when new paper is scored
- Failed delivery → retried 3 times with exponential backoff
- Verify HMAC signature in receiving endpoint

**Done when**: Webhooks fire on pipeline events with signature verification and retry.

---

### Task G3: Admin / Operator Dashboard

**Background**: ARCHITECTURE.md describes an Operator Surface for user management, subscription management, task monitoring.

**Goal**: Admin dashboard for operators.

**Scope**:
- `frontend/app/(admin)/` — admin pages (protected by admin role)
- User management: list, search, impersonate, disable
- Pipeline monitoring: task status, failure rates, queue depth
- Usage reporting: papers processed, LLM costs, active users
- Backend: admin API endpoints with role-based access

**Test**:
- Admin login → see dashboard with system metrics
- View user list → see usage and subscription status
- View pipeline status → see queued/running/failed tasks

**Done when**: Operators can monitor system health and manage users.

---

## Task Dependency Overview

```
Phase A (CI/CD)          — no dependencies, do first
Phase B (Auth + DB)      — enables all real data features
Phase C (Pipeline)       — depends on B3 (database)
Phase D (Digest)         — depends on C3 (enrichment)
Phase E (Chat)           — depends on C2 (parsing) + B3 (database)
Phase F (Public)         — depends on B1 (auth) for signup
Phase G (Developer/Ops)  — depends on B1 (auth) + B3 (database)
```

Recommended parallel execution:
- **Immediate** (no deps): A1, A2, A3
- **Next** (infra): B1, B2, B3 in parallel
- **Then**: C1 → C2 → C3 → C4 (sequential pipeline)
- **Parallel with C**: D1, E1, F1
- **After C+D**: D2, D3
- **After C+E**: E2, E3
- **Later**: F2, F3, G1, G2, G3
