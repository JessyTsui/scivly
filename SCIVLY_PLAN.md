# Scivly 平台方案

## 1. 项目定位

Scivly 从第一天就按“平台”来设计，不按单机个人工具来设计。

它的目标不是只帮你自己订阅 arXiv，而是做成一个可注册、可付费、可扩展、可集成的研究情报平台：

- 用户可以注册、订阅、续费
- 用户可以配置关注领域、关键词、作者、实验室、高校
- 系统每天自动抓取 arXiv 并生成译文、摘要、结构化解析、关键图片
- 用户可以在站内查看历史记录、消耗记录、额度和账单
- 用户可以通过 Email / Telegram / Discord / Webhook 接收结果
- 用户可以围绕单篇论文或自己的订阅结果发起 chat
- 外部开发者可以通过 API / SDK / skill 接入
- 平台可以有公共资源库，作为内容增长入口

这个方向可以做，但前提是架构一开始就要有平台边界，而不是先写成一个脚本再硬扩展。

## 2. 平台从第一天要具备的边界

Scivly 至少要同时覆盖 5 个表面：

### 2.1 Public Surface

面向未登录用户：

- 官网
- 价格页
- 公共论文资源库
- 示例日报
- API / skill / 自部署说明

### 2.2 User Workspace

面向普通用户：

- 登录注册
- 订阅计划
- 兴趣配置
- 历史日报
- 论文详情
- chat
- API key
- 通知渠道设置
- 使用量和账单

### 2.3 Team / Tenant Surface

面向团队或工作区：

- workspace / organization
- 成员邀请
- 权限
- 共享规则和共享资源库

### 2.4 Operator Surface

面向平台运营：

- 用户管理
- 套餐管理
- 扣费和额度
- 作业监控
- 失败重试
- 内容审核和公共资源库管理

### 2.5 Developer Surface

面向外部开发者和 agent 生态：

- REST API
- Webhook
- SDK
- OpenClaw / skill 集成

如果这五个表面一开始不切清楚，后面会不断发生“这个功能到底属于站内功能、运营功能还是开放能力”的返工。

## 3. 平台优先的 MVP

虽然一开始就做平台，但第一版仍然要收敛。建议上线范围如下：

### 核心用户功能

- 邮箱 / OAuth 登录
- 用户个人 workspace
- 基础套餐和额度
- 兴趣配置
  - 分类
  - 关键词
  - 作者
  - 实验室 / 高校
- 每日定时抓取 arXiv
- 命中论文详情页
  - 中文标题
  - 中文摘要
  - 3 到 5 条重点
  - 方法 / 结论 / 局限
  - 关键图片
- 站内历史记录
- 单篇论文 chat
- 一个主通知渠道
  - 推荐 Telegram 或 Email

### 核心平台功能

- 用户注册与订阅
- 套餐限制和用量记账
- API key
- Webhook
- 公共资源库
- 管理后台
- 作业状态和失败追踪

### 暂时不做

- 太多论文源同时接入
- 复杂推荐模型
- 团队协作里的细粒度审批流
- 自研支付系统
- 移动端 App

## 4. 产品结构建议

平台产品建议分成 4 条产品线：

### 4.1 面向用户的订阅产品

核心价值：

- 帮用户“每天知道今天该看什么论文”

主要页面：

- Dashboard
- Interests
- Digests
- Papers
- Chat
- Usage
- Billing
- Integrations

### 4.2 面向流量的公共资源库

核心价值：

- 让未注册用户也能看一部分精选内容
- 为 SEO、社交传播和转化服务

主要页面：

- 热门主题
- 最近精选
- 公开摘要页
- 公共榜单

### 4.3 面向开发者的开放平台

核心价值：

- 让别人把 Scivly 接到自己的机器人、agent、知识库、workflow 里

主要能力：

- REST API
- SDK
- Webhook
- Skill / Plugin

### 4.4 面向运营的后台系统

核心价值：

- 管用户
- 管套餐
- 管资源消耗
- 管作业状态
- 管公共内容

## 5. 技术路线

## 5.1 后端

推荐：

- `FastAPI`
- `Postgres`
- `Redis`
- `Dramatiq` 或 `Celery`
- `pgvector`
- `S3` 兼容对象存储

原因：

- 论文抓取、PDF 处理、LLM 解析都更适合 Python
- FastAPI 适合内部服务、开放 API、Webhook
- Postgres 能同时承担业务数据、运营数据、向量检索元数据

## 5.2 前端

推荐：

- `Next.js App Router + TypeScript`

理由见 [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)。

## 5.3 统一仓库

建议直接按 monorepo 组织：

```text
repo/
  apps/
    web/
    api/
    worker/
  packages/
    ui/
    config/
    db/
    sdk/
    prompts/
    integrations/
    openclaw-skill/
  docs/
  SCIVLY_PLAN.md
  FRONTEND_ARCHITECTURE.md
  README.md
```

这个结构对平台项目更合适，因为：

- 用户端、管理端、营销站可以共享设计系统
- API SDK 和 OpenClaw skill 有明确位置
- 后端 worker 和开放 API 不会混乱

## 6. 核心系统架构

```text
Next.js Web
  -> public site
  -> public library
  -> app workspace
  -> admin console

FastAPI
  -> auth context sync
  -> workspace API
  -> paper API
  -> chat API
  -> billing / usage API
  -> API key / webhook API

Worker Layer
  -> source sync
  -> matching
  -> PDF fetch
  -> parse
  -> figure extract
  -> LLM enrich
  -> delivery
  -> vector index

Data Layer
  -> Postgres
  -> Redis
  -> S3
  -> pgvector
```

## 7. 稳定自动化方案

平台要稳定，关键不在“多会爬”，而在“任务链能不能持续稳定跑”。

推荐方案：

1. 外部调度器固定时间触发批次任务
2. 批次任务只负责创建 job，不负责串行处理所有步骤
3. 每个处理阶段都是独立 worker
4. 每一步都可以重试、回放、补偿
5. 所有状态都写库

建议 job 状态流：

`queued -> syncing -> matched -> fetched -> parsed -> enriched -> delivered -> indexed`

每个 job 必须有：

- 幂等键
- 最大重试次数
- 超时
- 死信记录
- 错误上下文
- workspace 归属
- 成本记录

这套机制是平台化的底座，不是附属功能。

## 8. 数据源策略

即使平台优先，抓取层仍然要保守。

第一阶段建议：

- 以 arXiv API / RSS / Atom 为主
- 必要时再抓 PDF
- 不以网页浏览器爬虫为主路径

原因：

- 平台要跑得稳，不能把基础链路建立在容易变的 HTML 上
- 论文平台真正难的是“筛选 + 解析 + 输出”，不是“页面怎么抓”

后续再扩展：

- bioRxiv
- Semantic Scholar
- Crossref
- OpenReview

## 9. 用户关注模型

建议从第一天就用“规则 + 记账 + 可解释”方案。

支持四种规则：

- 分类匹配
- 关键词匹配
- 作者匹配
- 机构匹配

每次命中都记录：

- 为什么命中
- 命中了哪条规则
- 命中分数
- 是否进入后续全文解析

这对平台很重要，因为：

- 用户可以理解结果
- 后台可以解释推荐
- 后续可以基于行为数据迭代排序

## 10. 论文处理链

平台版处理链建议拆成 3 层：

### 10.1 Metadata Layer

基于 arXiv 元数据做首轮过滤和基础摘要。

### 10.2 Fulltext Layer

对高优先级论文下载 PDF，提取正文、章节、图片和 caption。

### 10.3 Enrichment Layer

基于 LLM 生成结构化输出：

- 标题翻译
- 摘要翻译
- 一句话总结
- 关键点
- 方法
- 结论
- 局限
- 适合谁看
- 标签
- 图像说明

建议 LLM 输出固定 schema，不要直接产出自由文本。

## 11. 图片策略

第一版只做“抽取和解释”，不做“生成”。

流程建议：

1. 从 PDF 抽图
2. 保留 caption
3. 用规则过滤明显无意义的图
4. 给图打分
5. 选前 1 到 3 张
6. 为每张图生成一句中文解释

这比生成图稳得多，也更适合平台公信力。

## 12. Chat 设计

平台里的 chat 不建议一开始就做成通用 agent。

建议分两种：

### 12.1 Paper Chat

围绕单篇论文问答。

### 12.2 Digest Chat

围绕“今天的日报”问答。

上下文来源：

- metadata
- 结构化摘要
- 正文 chunk
- 图片 caption

检索层建议先用 `pgvector`，不要一开始就引入单独向量数据库。

## 13. 分发与通知

通知必须做成 adapter：

- Email
- Telegram
- Discord
- Webhook

平台内部统一一个 delivery event，然后交给不同 adapter 发送。

这样做的好处是：

- 容易扩展
- 容易重试
- 容易记录渠道成本和成功率

## 14. 用户、租户、计费

平台从第一天就要把“人、工作区、套餐、消耗”拆开。

建议核心模型：

- `users`
- `workspaces`
- `workspace_members`
- `plans`
- `subscriptions`
- `usage_ledgers`
- `api_keys`
- `integrations`

计费建议从一开始就记账，不要等收费时再补。

至少记这些：

- 抓取批次数
- 命中论文数
- PDF 解析次数
- LLM token
- 图片抽取次数
- 推送次数
- chat 次数
- API 调用次数

## 15. 关键业务表建议

除了用户和计费表，论文业务层建议至少有：

- `interests`
- `interest_rules`
- `sources`
- `source_runs`
- `papers`
- `paper_versions`
- `paper_matches`
- `paper_assets`
- `paper_chunks`
- `paper_summaries`
- `digests`
- `digest_items`
- `deliveries`
- `chat_threads`
- `chat_messages`
- `jobs`

## 16. OpenClaw / skill / API 集成

这一块建议从第一天就保留接口，但实现上做薄。

推荐三层能力：

### 16.1 REST API

例如：

- `POST /api/workspaces/:id/interests`
- `GET /api/workspaces/:id/digests`
- `GET /api/papers/:id`
- `POST /api/papers/:id/chat`
- `POST /api/webhooks/test`

### 16.2 Webhook

事件建议：

- `digest.ready`
- `paper.matched`
- `delivery.failed`
- `subscription.changed`

### 16.3 OpenClaw Skill

建议单独做一个薄包放在：

- `packages/openclaw-skill/`

它只做：

- 认证配置
- 查询日报
- 查询论文
- 对论文发问

不要把核心业务逻辑写进 skill 里。

## 17. 公共资源库

既然平台从第一天就成立，公共资源库也应该进入一期设计，但不必做太重。

建议一期能力：

- 展示公开精选论文摘要
- 按主题浏览
- 展示热门榜单
- 支持从公共内容转成个人订阅模板

这部分承担两个职责：

- 内容增长
- 产品转化

## 18. 管理后台

后台最少要覆盖：

### 18.1 运营视角

- 新增用户
- 新增订阅
- 收入
- 活跃 workspace
- API 调用量

### 18.2 系统视角

- 每日抓取量
- 解析成功率
- 推送成功率
- 失败 job
- 死信队列

### 18.3 内容视角

- 公共资源库条目
- 被收藏最多的论文
- 低质量摘要回查

## 19. 开源和商业化边界

平台可以开源，但边界要清楚。

建议：

### 开源

- 抓取与处理流水线
- API
- 基础 Web
- 自部署方案
- 基础 skill / SDK

### 官方托管增强

- 托管服务
- 公共精选资源库
- 官方模型路由
- 团队版能力
- 平台运营后台

## 20. 开发阶段建议

虽然从第一天就做平台，但不是第一天就做完所有页面。

建议按下面顺序推进：

### Phase 1: 平台骨架

- Next.js 前端骨架
- FastAPI API 骨架
- Worker 和队列
- 用户 / workspace / plan / usage 表
- 基础鉴权
- 基础后台

### Phase 2: 论文流水线

- arXiv 接入
- 规则匹配
- PDF 抓取
- 摘要与图片
- 日报生成

### Phase 3: 平台功能闭环

- 历史记录
- 账单与消耗
- 通知渠道
- API key
- Webhook

### Phase 4: 生态扩展

- OpenClaw skill
- 公共资源库增强
- 多源扩展

## 21. 最终建议

你现在既然明确要平台优先，那我建议就不要再用“先做个人工具”的叙事了。

正确的说法应该是：

Scivly 是一个多租户研究情报平台，第一版就包括：

- 用户系统
- 订阅和额度
- 自动化抓取和解析
- 历史库
- 站内 chat
- 通知分发
- API / skill 接口
- 基础后台

但在实现顺序上，仍然要优先把“自动化流水线 + 用户工作区 + 订阅闭环”先做扎实。
