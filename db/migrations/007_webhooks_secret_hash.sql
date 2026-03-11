BEGIN;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'webhooks'
      AND column_name = 'signing_secret'
  ) AND NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'webhooks'
      AND column_name = 'secret_hash'
  ) THEN
    ALTER TABLE webhooks RENAME COLUMN signing_secret TO secret_hash;
  ELSIF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'webhooks'
      AND column_name = 'signing_secret'
  ) AND EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'webhooks'
      AND column_name = 'secret_hash'
  ) THEN
    EXECUTE '
      UPDATE webhooks
      SET secret_hash = COALESCE(NULLIF(secret_hash, ''''), signing_secret)
      WHERE secret_hash IS NULL OR btrim(secret_hash) = ''''
    ';
    ALTER TABLE webhooks DROP COLUMN signing_secret;
  END IF;
END $$;

ALTER TABLE webhooks
  ADD COLUMN IF NOT EXISTS secret_hash TEXT;

UPDATE webhooks
SET secret_hash = 'sha256:legacy'
WHERE secret_hash IS NULL OR btrim(secret_hash) = '';

ALTER TABLE webhooks
  ALTER COLUMN secret_hash SET NOT NULL;

ALTER TABLE webhooks
  DROP CONSTRAINT IF EXISTS chk_webhooks_signing_secret_nonempty;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'chk_webhooks_secret_hash_nonempty'
  ) THEN
    ALTER TABLE webhooks
      ADD CONSTRAINT chk_webhooks_secret_hash_nonempty
      CHECK (length(trim(secret_hash)) > 0);
  END IF;
END $$;

COMMIT;
