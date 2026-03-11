BEGIN;

INSERT INTO papers (
  id,
  arxiv_id,
  version,
  title,
  abstract,
  authors,
  categories,
  primary_category,
  comment,
  journal_ref,
  doi,
  published_at,
  updated_at,
  raw_metadata,
  created_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000001001',
    '2603.00001',
    1,
    'Agentic Retrieval for Long-Horizon Scientific Planning',
    'We introduce an agentic retrieval stack that decomposes scientific planning into iterative search, critique, and synthesis steps. The system improves benchmarked long-context planning quality while keeping retrieval cost bounded through profile-aware evidence selection.',
    '[
      {"name":"Maya Chen","affiliation":"Scivly Research"},
      {"name":"Sara Hooker","affiliation":"Cohere"},
      {"name":"Luis Romero","affiliation":"University of Washington"}
    ]'::jsonb,
    ARRAY['cs.CL', 'cs.AI'],
    'cs.CL',
    'Code: https://github.com/scivly-labs/agentic-retrieval',
    NULL,
    '10.48550/arXiv.2603.00001',
    '2026-03-02T02:00:00Z',
    '2026-03-02T02:00:00Z',
    '{"source":"arXiv","license":"arXiv non-exclusive"}'::jsonb,
    '2026-03-02T02:01:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001002',
    '2603.00002',
    2,
    'Benchmarking Practical Post-Training Recipes for Open Reasoning Models',
    'This paper compares supervised fine-tuning, rejection sampling, and lightweight preference optimization for open reasoning models under fixed compute budgets. We release ablations, prompt traces, and evaluation harnesses for reproducibility.',
    '[
      {"name":"Jin Park","affiliation":"KAIST"},
      {"name":"Elena Petrova","affiliation":"Hugging Face"},
      {"name":"Arjun Patel","affiliation":"Stanford University"}
    ]'::jsonb,
    ARRAY['cs.LG', 'cs.CL'],
    'cs.LG',
    'Accepted to ICLR 2026 workshop; code and datasets included.',
    'ICLR 2026 Workshop on Open Foundation Models',
    '10.48550/arXiv.2603.00002',
    '2026-03-03T05:30:00Z',
    '2026-03-04T01:10:00Z',
    '{"source":"arXiv","pdf_url":"https://arxiv.org/pdf/2603.00002"}'::jsonb,
    '2026-03-03T05:31:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001003',
    '2603.00003',
    1,
    'World Models for Embodied Multimodal Agents in Cluttered Homes',
    'We study world-model pretraining for household robot agents that act from video, language, and proprioception. Our method improves long-horizon manipulation success, especially on tasks that require temporal credit assignment and sparse feedback.',
    '[
      {"name":"Chelsea Finn","affiliation":"Stanford University"},
      {"name":"Robin Liu","affiliation":"Google DeepMind"},
      {"name":"Nina Rossi","affiliation":"University of Toronto"}
    ]'::jsonb,
    ARRAY['cs.RO', 'cs.CV', 'cs.AI'],
    'cs.RO',
    'Project page: https://embodied.example/world-model-home',
    NULL,
    '10.48550/arXiv.2603.00003',
    '2026-03-04T08:15:00Z',
    '2026-03-04T08:15:00Z',
    '{"source":"arXiv","assets":["video","policy-checkpoints"]}'::jsonb,
    '2026-03-04T08:16:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001004',
    '2603.00004',
    1,
    'Structured Figure Extraction for Faster Research Digests',
    'We present a deterministic PDF pipeline for extracting figure-caption pairs, chart descriptions, and method diagrams from scientific papers. The pipeline uses layout heuristics instead of a large multimodal model for the first pass, reducing cost while preserving coverage.',
    '[
      {"name":"Tara Singh","affiliation":"Scivly Research"},
      {"name":"Ben Turner","affiliation":"Allen Institute for AI"}
    ]'::jsonb,
    ARRAY['cs.DL', 'cs.IR'],
    'cs.DL',
    'Open-source implementation and benchmark scripts are included.',
    NULL,
    '10.48550/arXiv.2603.00004',
    '2026-03-05T06:45:00Z',
    '2026-03-05T06:45:00Z',
    '{"source":"arXiv","artifacts":["figures","captions","layouts"]}'::jsonb,
    '2026-03-05T06:46:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001005',
    '2603.00005',
    1,
    'Diverse Daily Digest Ranking with Topic-Aware Clustering',
    'This work proposes a daily digest ranker that combines profile matching with novelty clustering to reduce same-day duplicates. It improves click-through and save rates in a personalized research monitoring workflow without increasing delivery volume.',
    '[
      {"name":"Mina Alvarez","affiliation":"University of Washington"},
      {"name":"Kai Nakamura","affiliation":"Anthropic"},
      {"name":"Luca Moretti","affiliation":"ETH Zurich"}
    ]'::jsonb,
    ARRAY['cs.IR', 'cs.AI', 'cs.CL'],
    'cs.IR',
    'Companion dataset and evaluation notebook released.',
    NULL,
    '10.48550/arXiv.2603.00005',
    '2026-03-06T03:20:00Z',
    '2026-03-06T03:20:00Z',
    '{"source":"arXiv","evaluation":"digest-ranking-v1"}'::jsonb,
    '2026-03-06T03:21:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001006',
    '2603.00006',
    1,
    'Low-Cost QA Memory for Paper-Centric Assistant Sessions',
    'We describe a lightweight retrieval memory for paper-centric assistant sessions that preserves reasoning traces, quote boundaries, and user follow-up state. The design improves answer grounding while keeping storage costs predictable for multi-tenant deployments.',
    '[
      {"name":"Irene Zhou","affiliation":"Scivly Research"},
      {"name":"Mateo Silva","affiliation":"University of Cambridge"}
    ]'::jsonb,
    ARRAY['cs.CL', 'cs.IR'],
    'cs.CL',
    'Includes latency and token accounting analysis.',
    NULL,
    '10.48550/arXiv.2603.00006',
    '2026-03-06T11:00:00Z',
    '2026-03-06T11:00:00Z',
    '{"source":"arXiv","focus":"chat-memory"}'::jsonb,
    '2026-03-06T11:01:00Z'
  )
ON CONFLICT (id) DO UPDATE SET
  arxiv_id = EXCLUDED.arxiv_id,
  version = EXCLUDED.version,
  title = EXCLUDED.title,
  abstract = EXCLUDED.abstract,
  authors = EXCLUDED.authors,
  categories = EXCLUDED.categories,
  primary_category = EXCLUDED.primary_category,
  comment = EXCLUDED.comment,
  journal_ref = EXCLUDED.journal_ref,
  doi = EXCLUDED.doi,
  published_at = EXCLUDED.published_at,
  updated_at = EXCLUDED.updated_at,
  raw_metadata = EXCLUDED.raw_metadata,
  created_at = EXCLUDED.created_at;

INSERT INTO paper_scores (
  id,
  paper_id,
  workspace_id,
  profile_id,
  score_version,
  total_score,
  topical_relevance,
  prestige_priors,
  actionability,
  profile_fit,
  novelty_diversity,
  penalties,
  matched_rules,
  threshold_decision,
  llm_rerank_delta,
  llm_rerank_reasons,
  created_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000001101',
    '00000000-0000-0000-0000-000000001001',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000000301',
    'v1',
    81.50,
    38.00,
    12.50,
    11.00,
    9.00,
    8.00,
    -2.00,
    '[
      {"type":"keyword","value":"agentic retrieval","weight":10},
      {"type":"category","value":"cs.CL","weight":8},
      {"type":"author_watch","value":"Sara Hooker","weight":4}
    ]'::jsonb,
    'digest_candidate',
    5.00,
    '[
      {"reason":"Abstract clearly targets long-horizon planning for scientific workflows."}
    ]'::jsonb,
    '2026-03-02T03:00:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001102',
    '00000000-0000-0000-0000-000000001002',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000000301',
    'v1',
    78.00,
    34.50,
    13.50,
    13.00,
    8.00,
    7.00,
    -3.00,
    '[
      {"type":"keyword","value":"post-training","weight":9},
      {"type":"comment","value":"ICLR 2026 workshop","weight":5}
    ]'::jsonb,
    'digest_candidate',
    5.00,
    '[
      {"reason":"Strong reproducibility signals and relevant post-training comparison."}
    ]'::jsonb,
    '2026-03-04T02:00:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001103',
    '00000000-0000-0000-0000-000000001003',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000000302',
    'v1',
    74.00,
    35.00,
    12.00,
    10.00,
    8.00,
    7.00,
    -2.00,
    '[
      {"type":"keyword","value":"world model","weight":10},
      {"type":"author_watch","value":"Chelsea Finn","weight":4}
    ]'::jsonb,
    'rerank_candidate',
    4.00,
    '[
      {"reason":"Embodied household setting is highly aligned with the workspace robotics profile."}
    ]'::jsonb,
    '2026-03-04T09:00:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001104',
    '00000000-0000-0000-0000-000000001005',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000000301',
    'v1',
    66.50,
    31.00,
    8.50,
    9.00,
    9.00,
    9.00,
    0.00,
    '[
      {"type":"keyword","value":"daily digest","weight":8},
      {"type":"keyword","value":"topic-aware clustering","weight":7}
    ]'::jsonb,
    'rerank_candidate',
    0.00,
    '[]'::jsonb,
    '2026-03-06T04:00:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001105',
    '00000000-0000-0000-0000-000000001006',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000000301',
    'v1',
    61.00,
    30.00,
    7.00,
    8.00,
    8.00,
    8.00,
    0.00,
    '[
      {"type":"keyword","value":"paper-centric assistant","weight":8},
      {"type":"keyword","value":"token accounting","weight":4}
    ]'::jsonb,
    'pdf_candidate',
    0.00,
    '[]'::jsonb,
    '2026-03-06T12:00:00Z'
  )
ON CONFLICT (id) DO UPDATE SET
  paper_id = EXCLUDED.paper_id,
  workspace_id = EXCLUDED.workspace_id,
  profile_id = EXCLUDED.profile_id,
  score_version = EXCLUDED.score_version,
  total_score = EXCLUDED.total_score,
  topical_relevance = EXCLUDED.topical_relevance,
  prestige_priors = EXCLUDED.prestige_priors,
  actionability = EXCLUDED.actionability,
  profile_fit = EXCLUDED.profile_fit,
  novelty_diversity = EXCLUDED.novelty_diversity,
  penalties = EXCLUDED.penalties,
  matched_rules = EXCLUDED.matched_rules,
  threshold_decision = EXCLUDED.threshold_decision,
  llm_rerank_delta = EXCLUDED.llm_rerank_delta,
  llm_rerank_reasons = EXCLUDED.llm_rerank_reasons,
  created_at = EXCLUDED.created_at;

INSERT INTO paper_enrichments (
  id,
  paper_id,
  title_zh,
  abstract_zh,
  one_line_summary,
  key_points,
  method_summary,
  conclusion_summary,
  limitations,
  figure_descriptions,
  enrichment_model,
  enrichment_cost,
  created_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000001201',
    '00000000-0000-0000-0000-000000001001',
    '面向长程科研规划的代理式检索',
    '本文提出一种面向科研规划任务的代理式检索系统，通过迭代式搜索、批判和综合，在控制检索成本的同时提升长上下文规划质量。',
    'An agentic retrieval loop improves scientific planning without expensive full-text processing for every candidate.',
    '[
      "Profile-aware retrieval keeps evidence selection bounded.",
      "Iterative critique improves multi-step planning quality."
    ]'::jsonb,
    'The system alternates between search, retrieval compression, and planning refinement.',
    'It outperforms static retrieval baselines on long-horizon planning benchmarks.',
    'The paper evaluates only a limited set of scientific planning tasks.',
    '[
      {"figure":"Figure 2","description":"End-to-end retrieval and planning loop with critique checkpoints."}
    ]'::jsonb,
    'gpt-4.1-mini',
    0.084000,
    '2026-03-02T03:30:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001202',
    '00000000-0000-0000-0000-000000001003',
    '面向杂乱家庭环境的具身多模态智能体世界模型',
    '本文研究具身机器人在家庭场景中的世界模型预训练，结合视频、语言与本体感觉信号，显著提升长程操作任务的成功率。',
    'World-model pretraining improves household robot policies in cluttered real-world settings.',
    '[
      "Multimodal pretraining boosts sparse-feedback tasks.",
      "The gains are largest on temporal credit assignment benchmarks."
    ]'::jsonb,
    'A shared latent world model conditions robot actions on video, language, and proprioception.',
    'The method improves long-horizon manipulation success in cluttered-home evaluations.',
    'Generalization outside household settings is not yet measured.',
    '[
      {"figure":"Figure 3","description":"Comparison of household task rollouts with and without world-model pretraining."}
    ]'::jsonb,
    'gpt-4.1-mini',
    0.092000,
    '2026-03-04T09:15:00Z'
  )
ON CONFLICT (id) DO UPDATE SET
  paper_id = EXCLUDED.paper_id,
  title_zh = EXCLUDED.title_zh,
  abstract_zh = EXCLUDED.abstract_zh,
  one_line_summary = EXCLUDED.one_line_summary,
  key_points = EXCLUDED.key_points,
  method_summary = EXCLUDED.method_summary,
  conclusion_summary = EXCLUDED.conclusion_summary,
  limitations = EXCLUDED.limitations,
  figure_descriptions = EXCLUDED.figure_descriptions,
  enrichment_model = EXCLUDED.enrichment_model,
  enrichment_cost = EXCLUDED.enrichment_cost,
  created_at = EXCLUDED.created_at;

INSERT INTO digests (
  id,
  workspace_id,
  schedule_id,
  period_start,
  period_end,
  paper_ids,
  content,
  status,
  created_at
)
VALUES (
  '00000000-0000-0000-0000-000000001301',
  '00000000-0000-0000-0000-000000000201',
  '00000000-0000-0000-0000-000000000601',
  '2026-03-06T00:00:00Z',
  '2026-03-07T00:00:00Z',
  ARRAY[
    '00000000-0000-0000-0000-000000001001'::uuid,
    '00000000-0000-0000-0000-000000001002'::uuid,
    '00000000-0000-0000-0000-000000001003'::uuid
  ],
  '{
    "headline":"3 papers worth reading today",
    "sections":[
      {"title":"Foundation models","paper_ids":["00000000-0000-0000-0000-000000001001","00000000-0000-0000-0000-000000001002"]},
      {"title":"Embodied agents","paper_ids":["00000000-0000-0000-0000-000000001003"]}
    ]
  }'::jsonb,
  'sent',
  '2026-03-07T08:00:00Z'
)
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  schedule_id = EXCLUDED.schedule_id,
  period_start = EXCLUDED.period_start,
  period_end = EXCLUDED.period_end,
  paper_ids = EXCLUDED.paper_ids,
  content = EXCLUDED.content,
  status = EXCLUDED.status,
  created_at = EXCLUDED.created_at;

INSERT INTO deliveries (
  id,
  workspace_id,
  digest_id,
  channel_id,
  status,
  attempts,
  last_error,
  sent_at,
  created_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000001401',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000001301',
    '00000000-0000-0000-0000-000000000501',
    'sent',
    1,
    NULL,
    '2026-03-07T08:00:10Z',
    '2026-03-07T08:00:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001402',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000001301',
    '00000000-0000-0000-0000-000000000502',
    'sent',
    1,
    NULL,
    '2026-03-07T08:00:18Z',
    '2026-03-07T08:00:00Z'
  )
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  digest_id = EXCLUDED.digest_id,
  channel_id = EXCLUDED.channel_id,
  status = EXCLUDED.status,
  attempts = EXCLUDED.attempts,
  last_error = EXCLUDED.last_error,
  sent_at = EXCLUDED.sent_at,
  created_at = EXCLUDED.created_at;

INSERT INTO chat_sessions (
  id,
  workspace_id,
  user_id,
  paper_id,
  title,
  session_type,
  created_at
)
VALUES (
  '00000000-0000-0000-0000-000000001501',
  '00000000-0000-0000-0000-000000000201',
  '00000000-0000-0000-0000-000000000101',
  '00000000-0000-0000-0000-000000001001',
  'Agentic retrieval paper QA',
  'paper_qa',
  '2026-03-07T09:00:00Z'
)
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  user_id = EXCLUDED.user_id,
  paper_id = EXCLUDED.paper_id,
  title = EXCLUDED.title,
  session_type = EXCLUDED.session_type,
  created_at = EXCLUDED.created_at;

INSERT INTO chat_messages (
  id,
  session_id,
  role,
  content,
  token_count,
  model,
  created_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000001601',
    '00000000-0000-0000-0000-000000001501',
    'user',
    'What makes the agentic retrieval planner different from a standard RAG pipeline?',
    22,
    'gpt-4.1-mini',
    '2026-03-07T09:00:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000001602',
    '00000000-0000-0000-0000-000000001501',
    'assistant',
    'It repeatedly searches, critiques retrieved evidence, and refines the plan instead of doing a single retrieve-then-generate pass.',
    31,
    'gpt-4.1-mini',
    '2026-03-07T09:00:03Z'
  )
ON CONFLICT (id) DO UPDATE SET
  session_id = EXCLUDED.session_id,
  role = EXCLUDED.role,
  content = EXCLUDED.content,
  token_count = EXCLUDED.token_count,
  model = EXCLUDED.model,
  created_at = EXCLUDED.created_at;

INSERT INTO api_keys (
  id,
  workspace_id,
  name,
  key_hash,
  prefix,
  scopes,
  last_used_at,
  expires_at,
  is_active,
  created_at
)
VALUES (
  '00000000-0000-0000-0000-000000001701',
  '00000000-0000-0000-0000-000000000201',
  'Demo SDK Key',
  'sha256:demo-sdk-key-hash',
  'scv_demo',
  ARRAY['papers:read', 'digests:read', 'chat:write'],
  '2026-03-07T10:10:00Z',
  '2026-09-01T00:00:00Z',
  TRUE,
  '2026-03-01T08:30:00Z'
)
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  name = EXCLUDED.name,
  key_hash = EXCLUDED.key_hash,
  prefix = EXCLUDED.prefix,
  scopes = EXCLUDED.scopes,
  last_used_at = EXCLUDED.last_used_at,
  expires_at = EXCLUDED.expires_at,
  is_active = EXCLUDED.is_active,
  created_at = EXCLUDED.created_at;

INSERT INTO webhooks (
  id,
  workspace_id,
  url,
  events,
  signing_secret,
  is_active,
  created_at
)
VALUES (
  '00000000-0000-0000-0000-000000001801',
  '00000000-0000-0000-0000-000000000201',
  'https://api.example.dev/scivly/events',
  ARRAY['digest.delivered', 'paper.matched'],
  'whsec_demo_webhook_secret',
  TRUE,
  '2026-03-01T08:40:00Z'
)
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  url = EXCLUDED.url,
  events = EXCLUDED.events,
  signing_secret = EXCLUDED.signing_secret,
  is_active = EXCLUDED.is_active,
  created_at = EXCLUDED.created_at;

INSERT INTO webhook_deliveries (
  id,
  webhook_id,
  event_type,
  payload,
  status,
  attempts,
  last_error,
  created_at
)
VALUES (
  '00000000-0000-0000-0000-000000001901',
  '00000000-0000-0000-0000-000000001801',
  'digest.delivered',
  '{
    "digest_id":"00000000-0000-0000-0000-000000001301",
    "workspace_id":"00000000-0000-0000-0000-000000000201",
    "status":"sent"
  }'::jsonb,
  'sent',
  1,
  NULL,
  '2026-03-07T08:00:20Z'
)
ON CONFLICT (id) DO UPDATE SET
  webhook_id = EXCLUDED.webhook_id,
  event_type = EXCLUDED.event_type,
  payload = EXCLUDED.payload,
  status = EXCLUDED.status,
  attempts = EXCLUDED.attempts,
  last_error = EXCLUDED.last_error,
  created_at = EXCLUDED.created_at;

INSERT INTO usage_records (
  id,
  workspace_id,
  record_type,
  quantity,
  unit_cost,
  metadata,
  recorded_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000002001',
    '00000000-0000-0000-0000-000000000201',
    'llm_token',
    1850,
    0.000002,
    '{"paper_id":"00000000-0000-0000-0000-000000001001","model":"gpt-4.1-mini"}'::jsonb,
    '2026-03-02T03:31:00Z'
  ),
  (
    '00000000-0000-0000-0000-000000002002',
    '00000000-0000-0000-0000-000000000201',
    'delivery',
    2,
    0.001500,
    '{"digest_id":"00000000-0000-0000-0000-000000001301","channels":["email","discord"]}'::jsonb,
    '2026-03-07T08:00:30Z'
  )
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  record_type = EXCLUDED.record_type,
  quantity = EXCLUDED.quantity,
  unit_cost = EXCLUDED.unit_cost,
  metadata = EXCLUDED.metadata,
  recorded_at = EXCLUDED.recorded_at;

INSERT INTO pipeline_tasks (
  id,
  workspace_id,
  paper_id,
  task_type,
  status,
  idempotency_key,
  attempts,
  max_attempts,
  last_error,
  cost,
  started_at,
  completed_at,
  created_at
)
VALUES
  (
    '00000000-0000-0000-0000-000000002101',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000001001',
    'enrich',
    'completed',
    'enrich:2603.00001:v1',
    1,
    3,
    NULL,
    0.084000,
    '2026-03-02T03:10:00Z',
    '2026-03-02T03:31:00Z',
    '2026-03-02T03:09:30Z'
  ),
  (
    '00000000-0000-0000-0000-000000002102',
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000001003',
    'deliver',
    'completed',
    'deliver:digest:2026-03-07',
    1,
    5,
    NULL,
    0.003000,
    '2026-03-07T08:00:00Z',
    '2026-03-07T08:00:20Z',
    '2026-03-07T07:59:50Z'
  )
ON CONFLICT (id) DO UPDATE SET
  workspace_id = EXCLUDED.workspace_id,
  paper_id = EXCLUDED.paper_id,
  task_type = EXCLUDED.task_type,
  status = EXCLUDED.status,
  idempotency_key = EXCLUDED.idempotency_key,
  attempts = EXCLUDED.attempts,
  max_attempts = EXCLUDED.max_attempts,
  last_error = EXCLUDED.last_error,
  cost = EXCLUDED.cost,
  started_at = EXCLUDED.started_at,
  completed_at = EXCLUDED.completed_at,
  created_at = EXCLUDED.created_at;

COMMIT;
