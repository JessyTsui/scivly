# Scivly SQL Migrations

Scivly uses raw PostgreSQL migration files with sequential numbering.

## Order

Apply migrations in filename order:

1. `001_initial_schema.sql`
2. `002_pgvector.sql`
3. `003_author_watchlist_created_at.sql`
4. `004_chat_sessions_title.sql`
5. `005_api_keys_is_active.sql`
6. `006_paper_pdf_tracking.sql`
7. `007_billing_stripe.sql`
8. `008_webhooks_secret_hash.sql`

The first migration creates the core relational schema and enables `pgcrypto` for
`gen_random_uuid()`. The second migration enables `pgvector` and adds vector columns to
`topic_profiles` and `papers`. The later migrations backfill API-facing columns that were
missing from the initial scaffold.

## Prerequisites

- PostgreSQL 14 or newer is recommended
- The database role must be allowed to create extensions, or an admin must preinstall:
  - `pgcrypto`
  - `vector`

## Apply Migrations

Use either the checked-in helper script or `psql` directly.

### Recommended helper

```bash
docker compose up -d db redis
./scripts/db.sh migrate
./scripts/db.sh seed
```

### Direct `psql`

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/scivly"

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/001_initial_schema.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/002_pgvector.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/003_author_watchlist_created_at.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/004_chat_sessions_title.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/005_api_keys_is_active.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/006_paper_pdf_tracking.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/007_billing_stripe.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/008_webhooks_secret_hash.sql
```

## Load Demo Seeds

The demo seeds expect the schema to already exist. Apply them in this order:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/seeds/demo_workspace.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/seeds/sample_papers.sql
```

`demo_workspace.sql` creates a demo user, workspace, membership, notification channels, and topic
profiles. `sample_papers.sql` adds paper records plus representative scoring, digest, chat,
billing, webhook, and pipeline rows tied to that demo workspace.

## Idempotency Notes

- Migrations use `IF NOT EXISTS` where PostgreSQL supports it.
- Seed files use fixed UUIDs and `ON CONFLICT` upserts so they can be reapplied safely in local
  development.
- If you change a migration after it has been applied to a shared database, create a new numbered
  migration instead of editing the old file.
