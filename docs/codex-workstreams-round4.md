# Round 4 — Worktree Prompts

> 3 worktrees, 互相独立可并行
> 端口分配: C3 不需要 dev server | E2 → frontend 3102 / backend 8102 | G3 → frontend 3103 / backend 8103

---

## Worktree 1: wt-c3 — LLM Enrichment (Task C3)

```
你是 Scivly 项目的开发者。当前任务是实现 C3: LLM Enrichment — 用 LLM 对论文做翻译和摘要。

## 项目背景

- Scivly 是一个学术论文智能平台，使用 FastAPI + Next.js + PostgreSQL + Redis
- C2 (PDF Parsing) 已完成，`workers/pdf/parser.py` 输出 `ParsedPdf` dataclass（包含 title, abstract, sections, references, figures, full_text）
- Pipeline 框架在 `workers/common/pipeline.py`，需要继承 `PipelineStep` 并实现 `execute(payload) -> dict`
- 数据库模型 `PaperEnrichment` 已在 `backend/app/models/papers.py`（第114-139行），包含字段: title_zh, abstract_zh, one_line_summary, key_points, method_summary, conclusion_summary, limitations, figure_descriptions, enrichment_model, enrichment_cost
- `workers/common/runner.py` 的 `build_default_pipeline()` 中 `TaskType.ENRICH` 当前映射到 `LoggingStep` 占位（第129-131行），需要替换为真实实现
- `workers/common/task.py` 已定义 `TaskType.ENRICH = "enrich"`
- 环境变量前缀 `SCIVLY_`，参考 `backend/app/config.py`

## 具体要求

1. 创建 `workers/enrich/` 目录结构:
   - `workers/enrich/__init__.py`
   - `workers/enrich/summarizer.py` — LLM enrichment 核心逻辑
   - `workers/enrich/steps.py` — PipelineStep 实现
   - `workers/enrich/prompts.py` — prompt 模板（中文翻译 + 摘要 + 关键点等）

2. `summarizer.py` 实现:
   - LLM provider 抽象层（OpenAI API compatible，支持 OpenAI / Anthropic / 本地模型）
   - 输入: 论文 full_text、title、abstract、sections
   - 输出: title_zh, abstract_zh, one_line_summary, key_points (list[str]), method_summary, conclusion_summary, limitations, figure_descriptions
   - 通过环境变量配置: `SCIVLY_LLM_PROVIDER`, `SCIVLY_LLM_MODEL`, `SCIVLY_LLM_API_BASE`, `SCIVLY_LLM_API_KEY`
   - Token 用量追踪，计算 enrichment_cost

3. `steps.py` 实现:
   - `EnrichPaperStep(PipelineStep)` — step_type = TaskType.ENRICH, emitted_events = ("paper.enriched",)
   - 从 payload 获取 paper_id，从数据库读取 parsed PDF 数据
   - 调用 summarizer 生成 enrichment
   - 将结果写入 `paper_enrichments` 表
   - 用 asyncpg 直接连接数据库（参考 `workers/index/steps.py` 的模式）

4. 更新 `workers/common/runner.py`:
   - 在 `build_default_pipeline()` 中替换 ENRICH 的 LoggingStep 为 `EnrichPaperStep`

5. `prompts.py`:
   - 系统 prompt: 你是学术论文分析助手，精通中英文学术翻译
   - 用户 prompt 模板: 接收论文文本，输出结构化 JSON
   - 输出格式要求明确，用 JSON schema 约束

6. 在 `backend/app/config.py` 的 Settings 类中添加 LLM 相关配置:
   - llm_provider, llm_model, llm_api_base, llm_api_key, llm_max_tokens, llm_temperature

7. 测试:
   - `workers/enrich/tests/test_summarizer.py` — mock LLM 调用，验证输出格式
   - `workers/enrich/tests/test_steps.py` — mock DB + LLM，验证 pipeline step 集成
   - 确保 `pytest workers/enrich/` 通过

做完之后检查一下所有改动，确保代码质量和测试通过，如果没问题就 commit、push 并创建 PR (base: main, title 格式 "C3: Add LLM enrichment worker for paper translation and summarization")。
```

---

## Worktree 2: wt-e2 — Single Paper Q&A (Task E2)

```
你是 Scivly 项目的开发者。当前任务是实现 E2: Single Paper Q&A — 用户可以针对单篇论文进行问答。

## 项目背景

- Scivly 是一个学术论文智能平台，使用 FastAPI + Next.js + PostgreSQL + pgvector + Redis
- E1 (Vector Indexing) 已完成，论文 embedding 存储在 `papers.embedding` 列 (pgvector 1536-dim)
- C2 (PDF Parsing) 已完成，解析后的论文数据可从 `paper_enrichments` 表获取
- 现有 chat router 在 `backend/app/routers/chat.py`，已有 session CRUD + message CRUD，但 `send_message` 端点（第183-249行）返回 placeholder 响应 `"Stored placeholder reply for {paper_title}."`
- 前端 Q&A 页面在 `frontend/app/workspace/qa/page.tsx`，已有 UI 但没接真实 LLM
- Chat models 在 `backend/app/models/chat.py`: ChatSession (workspace_id, paper_id, session_type, title), ChatMessage (session_id, role, content, model)
- 环境变量前缀 `SCIVLY_`，参考 `backend/app/config.py`
- 后端端口默认 8100，前端端口默认 3100

## 端口配置

本 worktree 与其他 worktree 并行运行，使用以下端口:
- 前端: `PORT=3102 npm run dev` (在 frontend/ 目录)
- 后端: `SCIVLY_API_PORT=8102 uvicorn app.main:app --port 8102` (在 backend/ 目录)
- 前端 API 地址: `NEXT_PUBLIC_API_URL=http://localhost:8102`
- 前端 CORS: 后端 `SCIVLY_CORS_ALLOWED_ORIGINS=http://localhost:3102`

## 具体要求

1. 后端 — RAG 检索模块 `backend/app/services/rag.py`:
   - 给定 paper_id + 用户问题，从 paper 的 sections/full_text 中检索相关段落
   - 使用 pgvector 做语义搜索（查询 embedding 与论文 section embeddings 匹配）
   - 如果论文有 enrichment 数据 (title_zh, key_points 等)，也作为上下文
   - 返回 top-k 相关段落作为 LLM context
   - 简单实现: 如果论文只有一个 embedding (整篇论文级别)，则直接用论文全文作为 context

2. 后端 — LLM 对话服务 `backend/app/services/llm_chat.py`:
   - LLM provider 抽象（OpenAI API compatible）
   - 输入: system prompt + 论文 context + 对话历史 + 用户问题
   - 输出: assistant 回复文本
   - 支持 SSE streaming 响应 (Server-Sent Events)
   - 通过环境变量配置: `SCIVLY_LLM_PROVIDER`, `SCIVLY_LLM_MODEL`, `SCIVLY_LLM_API_BASE`, `SCIVLY_LLM_API_KEY`
   - System prompt: 你是论文阅读助手，基于提供的论文内容回答问题，如果论文中没有相关信息请明确告知

3. 后端 — 更新 `backend/app/routers/chat.py`:
   - 修改 `send_message` 端点（第183行），替换 placeholder 为真实 LLM 调用
   - 新增 SSE streaming 端点: `POST /chat/sessions/{session_id}/messages/stream`
   - 加载该 session 对应 paper 的全文和 enrichment 作为 context
   - 加载对话历史（最近 N 条消息）作为上下文
   - 调用 LLM 生成回复，存入 ChatMessage 表
   - 非 streaming 端点保持原有 ChatReplyOut 响应格式

4. 后端 — 在 `backend/app/config.py` 添加 LLM 配置（如果 C3 还没加的话）:
   - llm_provider, llm_model, llm_api_base, llm_api_key

5. 前端 — 更新 `frontend/app/workspace/qa/page.tsx`:
   - 接入真实 chat API，替换 mock 数据
   - 支持 SSE streaming 显示（逐字渲染 assistant 回复）
   - 显示 loading 状态
   - 错误处理（LLM 不可用时友好提示）

6. 测试:
   - `backend/tests/test_chat_llm.py` — mock LLM 调用，验证 RAG context 构建 + 回复生成
   - `backend/tests/test_chat_streaming.py` — 验证 SSE streaming 端点
   - 确保原有 chat session/message CRUD 测试不受影响

做完之后检查一下所有改动，确保代码质量和测试通过，如果没问题就 commit、push 并创建 PR (base: main, title 格式 "E2: Add single paper Q&A with RAG and LLM integration")。
```

---

## Worktree 3: wt-g3 — Admin Dashboard (Task G3)

```
你是 Scivly 项目的开发者。当前任务是实现 G3: Admin Dashboard — 运营管理后台。

## 项目背景

- Scivly 是一个学术论文智能平台，使用 FastAPI + Next.js + PostgreSQL + Redis
- B1 (Auth) 已完成，使用 Clerk，角色系统在 `backend/app/models/auth.py`（WorkspaceMember.role: "owner" | "admin" | "member"）
- B3 (Database) 已完成，SQLAlchemy async 连接
- 前端 admin 页面已存在于 `frontend/app/admin/`，包含 layout.tsx + page.tsx + pipeline/ + qa/ + analytics/ + settings/ + monitors/ + papers/ + digests/ 目录，但**全部使用硬编码 mock 数据**
- 后端没有 admin router，`backend/app/routers/__init__.py` 中未包含 admin 相关路由
- 现有 routers: health, public_papers, auth, workspaces, interests, papers, digests, chat, webhooks, api_keys, billing, usage
- 认证依赖: `get_current_user` 在 `backend/app/deps.py`
- 环境变量前缀 `SCIVLY_`，参考 `backend/app/config.py`

## 端口配置

本 worktree 与其他 worktree 并行运行，使用以下端口:
- 前端: `PORT=3103 npm run dev` (在 frontend/ 目录)
- 后端: `SCIVLY_API_PORT=8103 uvicorn app.main:app --port 8103` (在 backend/ 目录)
- 前端 API 地址: `NEXT_PUBLIC_API_URL=http://localhost:8103`
- 前端 CORS: 后端 `SCIVLY_CORS_ALLOWED_ORIGINS=http://localhost:3103`

## 具体要求

1. 后端 — Admin 权限中间件 `backend/app/deps.py`:
   - 新增 `get_admin_user` 依赖，在 `get_current_user` 基础上验证用户角色为 "owner" 或 "admin"
   - 非 admin 用户返回 403

2. 后端 — Admin Router `backend/app/routers/admin.py`:
   - `GET /admin/stats` — 系统概览统计:
     - 总用户数、活跃用户数（7天内）
     - 总论文数、今日新增论文数
     - Pipeline 各阶段任务数量（queued/running/completed/failed）
     - LLM token 总消耗、本月消耗
   - `GET /admin/users` — 用户列表（分页）:
     - 用户 ID, email, workspace, 角色, 订阅状态, 最后活跃时间
     - 支持搜索 (by email/name)
   - `GET /admin/users/{user_id}` — 用户详情
   - `GET /admin/pipeline/status` — Pipeline 状态:
     - 各 TaskType 的 queued/running/completed/failed 计数
     - 最近失败的任务列表
     - 平均处理时间
   - `GET /admin/pipeline/jobs` — 最近任务列表（分页）
   - `GET /admin/usage/summary` — 使用量汇总:
     - 论文处理量 (daily/weekly/monthly)
     - LLM tokens 消耗趋势
     - 活跃用户趋势
   - 所有端点用 `Depends(get_admin_user)` 保护

3. 后端 — 注册 admin router:
   - 在 `backend/app/routers/__init__.py` 中添加 admin router
   - 确保 admin router 有 prefix="/admin", tags=["Admin"]

4. 前端 — 更新现有 admin 页面，替换 mock 数据为真实 API 调用:
   - `frontend/app/admin/page.tsx` — 主仪表盘，调用 `/admin/stats`
   - `frontend/app/admin/pipeline/page.tsx` — Pipeline 监控，调用 `/admin/pipeline/status` + `/admin/pipeline/jobs`
   - `frontend/app/admin/qa/page.tsx` — Q&A 管理（如果有真实数据则接入，否则保持 placeholder）
   - `frontend/app/admin/analytics/page.tsx` — 使用量分析，调用 `/admin/usage/summary`
   - 使用 TanStack Query (已安装 @tanstack/react-query) 做数据获取
   - 保持现有 UI 布局和样式不变，只替换数据源

5. 前端 — Admin 路由保护:
   - 在 `frontend/app/admin/layout.tsx` 中添加角色检查
   - 非 admin 用户重定向到 workspace 页面

6. 数据库查询:
   - Pipeline 状态查询: 从 Redis queue 或数据库 task log 表获取（如果没有 task log 表，可以先从 papers 表的 status 字段统计）
   - 用户统计: 从 users + workspace_members 表查询
   - 使用量: 从 usage_logs + billing_events 表查询

7. 测试:
   - `backend/tests/test_admin.py` — 测试 admin 端点权限 (admin 可访问, member 返回 403)
   - 测试各统计端点返回正确格式
   - 确保 `pytest backend/tests/test_admin.py` 通过

做完之后检查一下所有改动，确保代码质量和测试通过，如果没问题就 commit、push 并创建 PR (base: main, title 格式 "G3: Add admin dashboard with real backend APIs")。
```
