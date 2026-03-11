BEGIN;

INSERT INTO users (
  id,
  email,
  name,
  avatar_url,
  auth_provider,
  auth_provider_id,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000101',
  'demo@scivly.dev',
  'Scivly Demo',
  'https://images.scivly.dev/avatars/demo.png',
  'demo',
  'demo-user-101',
  '2026-03-01T08:00:00Z',
  '2026-03-01T08:00:00Z'
)
ON CONFLICT (id) DO UPDATE SET
  email = EXCLUDED.email,
  name = EXCLUDED.name,
  avatar_url = EXCLUDED.avatar_url,
  auth_provider = EXCLUDED.auth_provider,
  auth_provider_id = EXCLUDED.auth_provider_id,
  updated_at = EXCLUDED.updated_at;

INSERT INTO workspaces (
  id,
  name,
  slug,
  owner_id,
  plan,
  created_at
)
VALUES (
  '00000000-0000-0000-0000-000000000201',
  'Scivly Demo Workspace',
  'scivly-demo',
  '00000000-0000-0000-0000-000000000101',
  'pro',
  '2026-03-01T08:05:00Z'
)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  slug = EXCLUDED.slug,
  owner_id = EXCLUDED.owner_id,
  plan = EXCLUDED.plan;

INSERT INTO workspace_members (
  workspace_id,
  user_id,
  role,
  joined_at
)
VALUES (
  '00000000-0000-0000-0000-000000000201',
  '00000000-0000-0000-0000-000000000101',
  'owner',
  '2026-03-01T08:06:00Z'
)
ON CONFLICT (workspace_id, user_id) DO UPDATE SET
  role = EXCLUDED.role,
  joined_at = EXCLUDED.joined_at;

INSERT INTO topic_profiles (
  id,
  workspace_id,
  name,
  categories,
  keywords,
  is_default,
  created_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000000301',
    '00000000-0000-0000-0000-000000000201',
    'Core Foundation Models',
    ARRAY['cs.CL', 'cs.LG', 'stat.ML'],
    ARRAY['agentic reasoning', 'language model', 'retrieval augmented generation', 'post-training'],
    TRUE,
    '2026-03-01T08:10:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000000302',
    '00000000-0000-0000-0000-000000000201',
    'Embodied and Vision Agents',
    ARRAY['cs.CV', 'cs.RO', 'cs.AI'],
    ARRAY['vision-language action model', 'robot policy', 'world model', 'multimodal planning'],
    FALSE,
    '2026-03-01T08:11:00Z'
  )
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  name = EXCLUDED.name,
  categories = EXCLUDED.categories,
  keywords = EXCLUDED.keywords,
  is_default = EXCLUDED.is_default,
  created_at = EXCLUDED.created_at;

INSERT INTO author_watchlist (
  id,
  workspace_id,
  author_name,
  arxiv_author_id,
  notes,
  created_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000000401',
    '00000000-0000-0000-0000-000000000201',
    'Sara Hooker',
    'sara-hooker',
    'Tracks practical model evaluation and robustness work.',
    '2026-03-01T08:13:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000000402',
    '00000000-0000-0000-0000-000000000201',
    'Chelsea Finn',
    'chelsea-finn',
    'Tracks embodied learning and robot policy research.',
    '2026-03-01T08:14:00Z'
  )
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  author_name = EXCLUDED.author_name,
  arxiv_author_id = EXCLUDED.arxiv_author_id,
  notes = EXCLUDED.notes,
  created_at = EXCLUDED.created_at;

INSERT INTO notification_channels (
  id,
  workspace_id,
  channel_type,
  config,
  is_active
)
VALUES
  (
    '00000000-0000-0000-0000-000000000501',
    '00000000-0000-0000-0000-000000000201',
    'email',
    '{"address":"demo@scivly.dev","daily_summary":true}'::jsonb,
    TRUE
  ),
  (
    '00000000-0000-0000-0000-000000000502',
    '00000000-0000-0000-0000-000000000201',
    'discord',
    '{"webhook_url":"https://discord.example/scivly-demo","channel":"#paper-digest"}'::jsonb,
    TRUE
  ),
  (
    '00000000-0000-0000-0000-000000000503',
    '00000000-0000-0000-0000-000000000201',
    'webhook',
    '{"endpoint":"https://api.example.dev/scivly/webhooks/demo","signature_version":"v1"}'::jsonb,
    TRUE
  )
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  channel_type = EXCLUDED.channel_type,
  config = EXCLUDED.config,
  is_active = EXCLUDED.is_active;

INSERT INTO digest_schedules (
  id,
  workspace_id,
  cron_expression,
  timezone,
  channel_ids,
  is_active,
  created_at
)
VALUES (
  '00000000-0000-0000-0000-000000000601',
  '00000000-0000-0000-0000-000000000201',
  '0 8 * * *',
  'Asia/Shanghai',
  ARRAY[
    '00000000-0000-0000-0000-000000000501'::uuid,
    '00000000-0000-0000-0000-000000000502'::uuid
  ],
  TRUE,
  '2026-03-01T08:12:00Z'
)
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  cron_expression = EXCLUDED.cron_expression,
  timezone = EXCLUDED.timezone,
  channel_ids = EXCLUDED.channel_ids,
  is_active = EXCLUDED.is_active;

COMMIT;
