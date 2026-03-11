BEGIN;

ALTER TABLE webhooks
  ADD COLUMN IF NOT EXISTS secret_hash TEXT;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'webhooks'
      AND column_name = 'signing_secret'
  ) THEN
    EXECUTE 'UPDATE webhooks
      SET secret_hash = COALESCE(secret_hash, signing_secret)
      WHERE secret_hash IS NULL';
    EXECUTE 'ALTER TABLE webhooks ALTER COLUMN signing_secret DROP NOT NULL';
  END IF;
END $$;

ALTER TABLE webhooks
  DROP CONSTRAINT IF EXISTS chk_webhooks_secret_hash_nonempty;

ALTER TABLE webhooks
  ADD CONSTRAINT chk_webhooks_secret_hash_nonempty CHECK (length(trim(secret_hash)) > 0);

COMMIT;
