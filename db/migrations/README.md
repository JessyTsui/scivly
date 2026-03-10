# Scivly SQL Migrations

Scivly uses raw PostgreSQL migration files with sequential numbering.

## Order

Apply migrations in filename order:

1. `001_initial_schema.sql`
2. `002_pgvector.sql`

The first migration creates the core relational schema and enables `pgcrypto` for
`gen_random_uuid()`. The second migration enables `pgvector` and adds vector columns to
`topic_profiles` and `papers`.

## Prerequisites

- PostgreSQL 14 or newer is recommended
- The database role must be allowed to create extensions, or an admin must preinstall:
  - `pgcrypto`
  - `vector`

## Apply Migrations

Use `psql` with `ON_ERROR_STOP` enabled so the process exits on the first failure:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/scivly"

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/001_initial_schema.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/002_pgvector.sql
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
