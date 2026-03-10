BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;

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

COMMIT;
