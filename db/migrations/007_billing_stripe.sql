BEGIN;

ALTER TABLE workspaces
  ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;

ALTER TABLE workspaces
  ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT;

ALTER TABLE workspaces
  ADD COLUMN IF NOT EXISTS stripe_price_id TEXT;

ALTER TABLE workspaces
  ADD COLUMN IF NOT EXISTS subscription_status TEXT NOT NULL DEFAULT 'free';

ALTER TABLE workspaces
  ADD COLUMN IF NOT EXISTS cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE workspaces
  ADD COLUMN IF NOT EXISTS current_period_end TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS uq_workspaces_stripe_customer_id
  ON workspaces (stripe_customer_id)
  WHERE stripe_customer_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_workspaces_stripe_subscription_id
  ON workspaces (stripe_subscription_id)
  WHERE stripe_subscription_id IS NOT NULL;

ALTER TABLE workspaces
  DROP CONSTRAINT IF EXISTS chk_workspaces_subscription_status;

ALTER TABLE workspaces
  ADD CONSTRAINT chk_workspaces_subscription_status CHECK (
    subscription_status IN (
      'free',
      'trialing',
      'active',
      'past_due',
      'canceled',
      'unpaid',
      'incomplete',
      'incomplete_expired',
      'paused'
    )
  );

UPDATE workspaces
SET subscription_status = 'active'
WHERE plan <> 'free'
  AND subscription_status = 'free';

CREATE TABLE IF NOT EXISTS billing_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
  stripe_event_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  payload JSONB NOT NULL DEFAULT '{}'::JSONB,
  processed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_billing_events_stripe_event_id UNIQUE (stripe_event_id),
  CONSTRAINT chk_billing_events_event_type_nonempty CHECK (length(trim(event_type)) > 0)
);

CREATE INDEX IF NOT EXISTS ix_billing_events_workspace_created_at
  ON billing_events (workspace_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_billing_events_customer_id
  ON billing_events (stripe_customer_id);

CREATE INDEX IF NOT EXISTS ix_billing_events_subscription_id
  ON billing_events (stripe_subscription_id);

ALTER TABLE usage_records
  DROP CONSTRAINT IF EXISTS chk_usage_records_type;

ALTER TABLE usage_records
  ADD CONSTRAINT chk_usage_records_type CHECK (
    record_type IN (
      'api_call',
      'llm_token',
      'pdf_download',
      'delivery',
      'paper_process',
      'digest_sent'
    )
  );

COMMIT;
