BEGIN;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'webhooks'
      AND column_name = 'secret_hash'
  ) AND NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'webhooks'
      AND column_name = 'signing_secret'
  ) THEN
    ALTER TABLE webhooks RENAME COLUMN secret_hash TO signing_secret;
  END IF;
END
$$;

ALTER TABLE webhooks
  DROP CONSTRAINT IF EXISTS chk_webhooks_secret_hash_nonempty;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'chk_webhooks_signing_secret_nonempty'
  ) THEN
    ALTER TABLE webhooks
      ADD CONSTRAINT chk_webhooks_signing_secret_nonempty
      CHECK (length(trim(signing_secret)) > 0);
  END IF;
END
$$;

ALTER TABLE webhook_deliveries
  DROP CONSTRAINT IF EXISTS chk_webhook_deliveries_status;

ALTER TABLE webhook_deliveries
  ADD CONSTRAINT chk_webhook_deliveries_status
  CHECK (status IN ('queued', 'retrying', 'sent', 'failed'));

ALTER TABLE webhook_deliveries
  ADD COLUMN IF NOT EXISTS response_status_code INTEGER;

ALTER TABLE webhook_deliveries
  ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMPTZ;

ALTER TABLE webhook_deliveries
  ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMPTZ;

UPDATE webhook_deliveries
SET last_attempt_at = created_at
WHERE last_attempt_at IS NULL
  AND attempts > 0;

COMMIT;
