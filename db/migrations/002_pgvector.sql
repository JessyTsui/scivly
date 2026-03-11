BEGIN;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'vector') THEN
    BEGIN
      CREATE EXTENSION IF NOT EXISTS vector;
    EXCEPTION
      WHEN duplicate_object OR unique_violation THEN
        NULL;
    END;
  ELSE
    RAISE NOTICE 'pgvector extension is not installed; skipping vector columns and indexes.';
  END IF;
END
$$;

DO $$
BEGIN
  IF to_regtype('vector') IS NULL THEN
    RETURN;
  END IF;

  ALTER TABLE topic_profiles
    ADD COLUMN IF NOT EXISTS embedding vector(1536);

  ALTER TABLE papers
    ADD COLUMN IF NOT EXISTS embedding vector(1536);

  CREATE INDEX IF NOT EXISTS ix_topic_profiles_embedding_ivfflat
    ON topic_profiles
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

  CREATE INDEX IF NOT EXISTS ix_papers_embedding_ivfflat
    ON papers
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
END
$$;

COMMIT;
