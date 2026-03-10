BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  name TEXT,
  avatar_url TEXT,
  auth_provider TEXT NOT NULL,
  auth_provider_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_users_auth_provider_identity UNIQUE (auth_provider, auth_provider_id),
  CONSTRAINT chk_users_email_nonempty CHECK (length(trim(email)) > 3)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_lower ON users (lower(email));

CREATE OR REPLACE FUNCTION set_updated_at_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_users_set_updated_at ON users;

CREATE TRIGGER trg_users_set_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at_timestamp();

CREATE TABLE IF NOT EXISTS workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  plan TEXT NOT NULL DEFAULT 'free',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_workspaces_slug UNIQUE (slug),
  CONSTRAINT chk_workspaces_name_nonempty CHECK (length(trim(name)) > 0),
  CONSTRAINT chk_workspaces_slug_format CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$')
);

CREATE INDEX IF NOT EXISTS ix_workspaces_owner_id ON workspaces (owner_id);

CREATE TABLE IF NOT EXISTS workspace_members (
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (workspace_id, user_id),
  CONSTRAINT chk_workspace_members_role CHECK (role IN ('owner', 'admin', 'member'))
);

CREATE INDEX IF NOT EXISTS ix_workspace_members_user_id ON workspace_members (user_id);

CREATE TABLE IF NOT EXISTS topic_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  categories TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
  keywords TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_topic_profiles_workspace_name UNIQUE (workspace_id, name),
  CONSTRAINT chk_topic_profiles_name_nonempty CHECK (length(trim(name)) > 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_topic_profiles_default_per_workspace
  ON topic_profiles (workspace_id)
  WHERE is_default;

CREATE INDEX IF NOT EXISTS ix_topic_profiles_categories_gin
  ON topic_profiles
  USING GIN (categories);

CREATE INDEX IF NOT EXISTS ix_topic_profiles_keywords_gin
  ON topic_profiles
  USING GIN (keywords);

CREATE TABLE IF NOT EXISTS author_watchlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  author_name TEXT NOT NULL,
  arxiv_author_id TEXT,
  notes TEXT,
  CONSTRAINT uq_author_watchlist_workspace_author_name UNIQUE (workspace_id, author_name),
  CONSTRAINT uq_author_watchlist_workspace_arxiv_author UNIQUE (workspace_id, arxiv_author_id),
  CONSTRAINT chk_author_watchlist_author_name_nonempty CHECK (length(trim(author_name)) > 0)
);

CREATE INDEX IF NOT EXISTS ix_author_watchlist_workspace_id ON author_watchlist (workspace_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_author_watchlist_workspace_author_name_lower
  ON author_watchlist (workspace_id, lower(author_name));

CREATE TABLE IF NOT EXISTS notification_channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  channel_type TEXT NOT NULL,
  config JSONB NOT NULL DEFAULT '{}'::JSONB,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_notification_channels_id_workspace UNIQUE (id, workspace_id),
  CONSTRAINT chk_notification_channels_type CHECK (
    channel_type IN ('email', 'telegram', 'discord', 'webhook')
  )
);

CREATE INDEX IF NOT EXISTS ix_notification_channels_workspace_active
  ON notification_channels (workspace_id, is_active);

CREATE TABLE IF NOT EXISTS papers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  arxiv_id TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  title TEXT NOT NULL,
  abstract TEXT NOT NULL,
  authors JSONB NOT NULL DEFAULT '[]'::JSONB,
  categories TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
  primary_category TEXT,
  comment TEXT,
  journal_ref TEXT,
  doi TEXT,
  published_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  raw_metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_papers_arxiv_id UNIQUE (arxiv_id),
  CONSTRAINT chk_papers_version_positive CHECK (version > 0),
  CONSTRAINT chk_papers_title_nonempty CHECK (length(trim(title)) > 0),
  CONSTRAINT chk_papers_abstract_nonempty CHECK (length(trim(abstract)) > 0)
);

CREATE INDEX IF NOT EXISTS ix_papers_primary_category ON papers (primary_category);
CREATE INDEX IF NOT EXISTS ix_papers_published_at ON papers (published_at DESC);
CREATE INDEX IF NOT EXISTS ix_papers_updated_at ON papers (updated_at DESC);

CREATE INDEX IF NOT EXISTS ix_papers_categories_gin
  ON papers
  USING GIN (categories);

CREATE INDEX IF NOT EXISTS ix_papers_authors_gin
  ON papers
  USING GIN (authors jsonb_path_ops);

CREATE TABLE IF NOT EXISTS paper_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  profile_id UUID NOT NULL REFERENCES topic_profiles(id) ON DELETE CASCADE,
  score_version TEXT NOT NULL,
  total_score NUMERIC(6, 2) NOT NULL,
  topical_relevance NUMERIC(6, 2) NOT NULL,
  prestige_priors NUMERIC(6, 2) NOT NULL,
  actionability NUMERIC(6, 2) NOT NULL,
  profile_fit NUMERIC(6, 2) NOT NULL,
  novelty_diversity NUMERIC(6, 2) NOT NULL,
  penalties NUMERIC(6, 2) NOT NULL DEFAULT 0,
  matched_rules JSONB NOT NULL DEFAULT '[]'::JSONB,
  threshold_decision TEXT NOT NULL,
  llm_rerank_delta NUMERIC(6, 2) NOT NULL DEFAULT 0,
  llm_rerank_reasons JSONB NOT NULL DEFAULT '[]'::JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_paper_scores_snapshot UNIQUE (paper_id, workspace_id, profile_id, score_version),
  CONSTRAINT chk_paper_scores_threshold_decision CHECK (
    threshold_decision IN (
      'drop',
      'metadata_only',
      'pdf_candidate',
      'rerank_candidate',
      'digest_candidate',
      'source_fetch_candidate'
    )
  ),
  CONSTRAINT chk_paper_scores_total_score_reasonable CHECK (total_score BETWEEN -37 AND 112),
  CONSTRAINT chk_paper_scores_topical_relevance CHECK (topical_relevance BETWEEN 0 AND 45),
  CONSTRAINT chk_paper_scores_prestige_priors CHECK (prestige_priors BETWEEN 0 AND 20),
  CONSTRAINT chk_paper_scores_actionability CHECK (actionability BETWEEN 0 AND 15),
  CONSTRAINT chk_paper_scores_profile_fit CHECK (profile_fit BETWEEN 0 AND 10),
  CONSTRAINT chk_paper_scores_novelty_diversity CHECK (novelty_diversity BETWEEN 0 AND 10),
  CONSTRAINT chk_paper_scores_penalties CHECK (penalties BETWEEN -25 AND 0),
  CONSTRAINT chk_paper_scores_llm_rerank_delta CHECK (llm_rerank_delta BETWEEN -12 AND 12)
);

CREATE INDEX IF NOT EXISTS ix_paper_scores_workspace_created_at
  ON paper_scores (workspace_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_paper_scores_profile_id ON paper_scores (profile_id);
CREATE INDEX IF NOT EXISTS ix_paper_scores_threshold_decision ON paper_scores (threshold_decision);

CREATE TABLE IF NOT EXISTS paper_enrichments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
  title_zh TEXT,
  abstract_zh TEXT,
  one_line_summary TEXT,
  key_points JSONB NOT NULL DEFAULT '[]'::JSONB,
  method_summary TEXT,
  conclusion_summary TEXT,
  limitations TEXT,
  figure_descriptions JSONB NOT NULL DEFAULT '[]'::JSONB,
  enrichment_model TEXT NOT NULL,
  enrichment_cost NUMERIC(12, 6) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_paper_enrichments_paper_model UNIQUE (paper_id, enrichment_model),
  CONSTRAINT chk_paper_enrichments_cost_nonnegative CHECK (enrichment_cost >= 0)
);

CREATE INDEX IF NOT EXISTS ix_paper_enrichments_paper_id ON paper_enrichments (paper_id);

CREATE TABLE IF NOT EXISTS digest_schedules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  cron_expression TEXT NOT NULL,
  timezone TEXT NOT NULL,
  channel_ids UUID[] NOT NULL DEFAULT '{}'::UUID[],
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_digest_schedules_cron_nonempty CHECK (length(trim(cron_expression)) > 0),
  CONSTRAINT chk_digest_schedules_timezone_nonempty CHECK (length(trim(timezone)) > 0)
);

CREATE INDEX IF NOT EXISTS ix_digest_schedules_workspace_active
  ON digest_schedules (workspace_id, is_active);

CREATE TABLE IF NOT EXISTS digests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  schedule_id UUID NOT NULL REFERENCES digest_schedules(id) ON DELETE RESTRICT,
  period_start TIMESTAMPTZ NOT NULL,
  period_end TIMESTAMPTZ NOT NULL,
  paper_ids UUID[] NOT NULL DEFAULT '{}'::UUID[],
  content JSONB NOT NULL DEFAULT '{}'::JSONB,
  status TEXT NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_digests_id_workspace UNIQUE (id, workspace_id),
  CONSTRAINT uq_digests_schedule_window UNIQUE (
    workspace_id,
    schedule_id,
    period_start,
    period_end
  ),
  CONSTRAINT chk_digests_status CHECK (status IN ('draft', 'sent', 'failed')),
  CONSTRAINT chk_digests_period_window CHECK (period_end >= period_start)
);

CREATE INDEX IF NOT EXISTS ix_digests_workspace_status_created_at
  ON digests (workspace_id, status, created_at DESC);

CREATE TABLE IF NOT EXISTS deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  digest_id UUID NOT NULL,
  channel_id UUID NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_deliveries_digest_channel UNIQUE (digest_id, channel_id),
  CONSTRAINT fk_deliveries_digest_workspace FOREIGN KEY (digest_id, workspace_id)
    REFERENCES digests(id, workspace_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_deliveries_channel_workspace FOREIGN KEY (channel_id, workspace_id)
    REFERENCES notification_channels(id, workspace_id)
    ON DELETE RESTRICT,
  CONSTRAINT chk_deliveries_status CHECK (status IN ('queued', 'sent', 'failed')),
  CONSTRAINT chk_deliveries_attempts_nonnegative CHECK (attempts >= 0),
  CONSTRAINT chk_deliveries_sent_at_required CHECK (
    status <> 'sent' OR sent_at IS NOT NULL
  )
);

CREATE INDEX IF NOT EXISTS ix_deliveries_workspace_status_created_at
  ON deliveries (workspace_id, status, created_at DESC);

CREATE TABLE IF NOT EXISTS chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  paper_id UUID REFERENCES papers(id) ON DELETE SET NULL,
  session_type TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_chat_sessions_type CHECK (
    session_type IN ('paper_qa', 'digest_qa', 'general')
  )
);

CREATE INDEX IF NOT EXISTS ix_chat_sessions_workspace_user_created_at
  ON chat_sessions (workspace_id, user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_chat_sessions_paper_id ON chat_sessions (paper_id);

CREATE TABLE IF NOT EXISTS chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  token_count INTEGER NOT NULL DEFAULT 0,
  model TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_chat_messages_role CHECK (role IN ('user', 'assistant')),
  CONSTRAINT chk_chat_messages_token_count_nonnegative CHECK (token_count >= 0),
  CONSTRAINT chk_chat_messages_content_nonempty CHECK (length(trim(content)) > 0)
);

CREATE INDEX IF NOT EXISTS ix_chat_messages_session_created_at
  ON chat_messages (session_id, created_at ASC);

CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  key_hash TEXT NOT NULL,
  prefix TEXT NOT NULL,
  scopes TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
  last_used_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_api_keys_key_hash UNIQUE (key_hash),
  CONSTRAINT chk_api_keys_name_nonempty CHECK (length(trim(name)) > 0),
  CONSTRAINT chk_api_keys_prefix_nonempty CHECK (length(trim(prefix)) > 0)
);

CREATE INDEX IF NOT EXISTS ix_api_keys_workspace_created_at
  ON api_keys (workspace_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_api_keys_scopes_gin
  ON api_keys
  USING GIN (scopes);

CREATE TABLE IF NOT EXISTS webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  events TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
  secret_hash TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_webhooks_workspace_url UNIQUE (workspace_id, url),
  CONSTRAINT chk_webhooks_url_nonempty CHECK (length(trim(url)) > 0),
  CONSTRAINT chk_webhooks_secret_hash_nonempty CHECK (length(trim(secret_hash)) > 0)
);

CREATE INDEX IF NOT EXISTS ix_webhooks_workspace_active
  ON webhooks (workspace_id, is_active);

CREATE INDEX IF NOT EXISTS ix_webhooks_events_gin
  ON webhooks
  USING GIN (events);

CREATE TABLE IF NOT EXISTS webhook_deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::JSONB,
  status TEXT NOT NULL DEFAULT 'queued',
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_webhook_deliveries_status CHECK (status IN ('queued', 'sent', 'failed')),
  CONSTRAINT chk_webhook_deliveries_attempts_nonnegative CHECK (attempts >= 0),
  CONSTRAINT chk_webhook_deliveries_event_type_nonempty CHECK (length(trim(event_type)) > 0)
);

CREATE INDEX IF NOT EXISTS ix_webhook_deliveries_webhook_created_at
  ON webhook_deliveries (webhook_id, created_at DESC);

CREATE TABLE IF NOT EXISTS usage_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  record_type TEXT NOT NULL,
  quantity NUMERIC(12, 4) NOT NULL,
  unit_cost NUMERIC(12, 6) NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_usage_records_type CHECK (
    record_type IN ('api_call', 'llm_token', 'pdf_download', 'delivery')
  ),
  CONSTRAINT chk_usage_records_quantity_positive CHECK (quantity > 0),
  CONSTRAINT chk_usage_records_unit_cost_nonnegative CHECK (unit_cost >= 0)
);

CREATE INDEX IF NOT EXISTS ix_usage_records_workspace_recorded_at
  ON usage_records (workspace_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS pipeline_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  paper_id UUID REFERENCES papers(id) ON DELETE SET NULL,
  task_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  idempotency_key TEXT NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 5,
  last_error TEXT,
  cost NUMERIC(12, 6) NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_pipeline_tasks_workspace_idempotency_key UNIQUE (workspace_id, idempotency_key),
  CONSTRAINT chk_pipeline_tasks_type CHECK (
    task_type IN ('sync', 'match', 'fetch', 'parse', 'enrich', 'deliver', 'index')
  ),
  CONSTRAINT chk_pipeline_tasks_status CHECK (
    status IN ('queued', 'running', 'completed', 'failed', 'dead')
  ),
  CONSTRAINT chk_pipeline_tasks_attempts_nonnegative CHECK (attempts >= 0),
  CONSTRAINT chk_pipeline_tasks_max_attempts_positive CHECK (max_attempts > 0),
  CONSTRAINT chk_pipeline_tasks_cost_nonnegative CHECK (cost >= 0),
  CONSTRAINT chk_pipeline_tasks_started_after_created CHECK (
    started_at IS NULL OR started_at >= created_at
  ),
  CONSTRAINT chk_pipeline_tasks_completed_after_started CHECK (
    completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at
  )
);

CREATE INDEX IF NOT EXISTS ix_pipeline_tasks_workspace_status_created_at
  ON pipeline_tasks (workspace_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_pipeline_tasks_paper_id ON pipeline_tasks (paper_id);

COMMIT;
