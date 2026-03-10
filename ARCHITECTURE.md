# Scivly Architecture

本文件是 Scivly 的主架构文档，用来统一项目边界、仓库组织、系统组件、处理流水线、开放接口和开源边界。

它参考了 `/Users/jessytsui/cerul/repo` 的文档组织方式，但按 Scivly 的论文情报平台场景重新收敛。

## 1. 一句话定义

**Scivly 是一个多租户论文情报平台。**

它帮助用户持续跟踪自己关注的论文领域、关键词、作者、实验室和高校，并通过自动化流水线完成：

- 抓取
- 过滤
- 翻译
- 结构化摘要
- 关键图片提取
- 分发
- 站内问答

## 2. 产品表面

Scivly 从第一天就按平台来设计，至少包含四个产品表面：

### 2.1 Public Surface

- 官网
- 价格页
- 公共资源库
- 公共论文详情页
- 开发者入口

### 2.2 User Workspace

- 兴趣配置
- 每日 digest
- 论文详情
- chat
- API key
- 通知渠道
- 用量和账单

### 2.3 Operator Surface

- 用户管理
- 套餐和订阅
- 用量记账
- 任务监控
- 公共资源库管理

### 2.4 Developer Surface

- REST API
- Webhook
- SDK
- OpenClaw / skill

## 3. 总体架构

```text
Clients
  -> Public site
  -> User workspace
  -> Admin console
  -> Skill / API clients

Next.js Web
  -> marketing
  -> library
  -> app
  -> admin

FastAPI
  -> auth context
  -> interests API
  -> papers API
  -> digest API
  -> chat API
  -> billing / usage API
  -> webhooks / api keys

Worker Plane
  -> source sync
  -> match
  -> pdf fetch
  -> parse
  -> enrich
  -> deliver
  -> index

Data Layer
  -> Postgres
  -> Redis
  -> pgvector
  -> S3 / R2
```

## 4. 运行时组件

| 组件 | 推荐技术 | 职责 |
| --- | --- | --- |
| Web App | Next.js App Router | 官网、资源库、用户端、后台 |
| API Server | FastAPI | 业务 API、鉴权上下文、用量、Webhook |
| Worker | Python | 抓取、解析、摘要、图片、分发 |
| Queue | Redis | 任务队列、重试、缓冲 |
| DB | Postgres + pgvector | 业务数据、检索数据、记账 |
| Object Storage | S3 / R2 | PDF、图片、导出文件 |
| Billing | Stripe | 订阅、结算、Portal |
| Auth | Clerk 或 Better Auth | 登录、workspace、会话 |

## 5. 设计原则

1. Platform-first：从第一天就是多租户平台，不是脚本拼接。
2. API-first：前端、skill、未来 SDK 复用同一套后端能力。
3. Step Pipeline：所有论文处理流程统一成可重试、可回放的步骤链。
4. Open-core：代码开源，生产数据和托管增强不公开。
5. Single-source docs：主架构文档只维护一份。

## 6. 推荐仓库结构

```text
repo/
  frontend/          Next.js app
  backend/           FastAPI service
  workers/           paper processing workers
  db/                migrations and seeds
  docs/              public-safe docs
  config/            config templates
  scripts/           bootstrap scripts
  skills/            installable skills
  ARCHITECTURE.md
  FRONTEND_ARCHITECTURE.md
  OPEN_SOURCE_SCOPE.md
  PIPELINE_PATTERN.md
```

`cerul` 的目录划分很适合作为 Scivly 的参考，因为它把“平台组件”和“公共文档边界”分得很清楚。Scivly 也应该尽量保持这种结构，而不是一开始就把所有逻辑塞进一个 `app/` 目录。

## 7. 核心数据流

### 7.1 Source Sync

- 按分类、关键词或时间窗口拉取 arXiv feed / API
- 写入原始论文元数据
- 做 `arxiv_id` 和版本去重

### 7.2 Matching

- 用 workspace 规则做匹配和打分
- 记录命中原因
- 只让高优先级论文进入全文处理

### 7.3 Fulltext Processing

- 下载 PDF
- 抽取正文
- 抽取图片和 caption
- 进行结构化清洗

### 7.4 Enrichment

- 标题翻译
- 摘要翻译
- 一句话总结
- 关键点
- 方法 / 结论 / 局限
- 图像说明

### 7.5 Delivery

- 生成 digest
- 通过 Email / Telegram / Discord / Webhook 分发
- 记录送达状态和失败重试

### 7.6 Retrieval

- 写入向量索引
- 支持单篇 chat 和 digest chat

## 8. 任务系统要求

Scivly 的难点不在页面，而在自动化链路稳定性。

每个任务都必须具备：

- 幂等键
- 重试
- 超时
- 死信
- workspace 归属
- 成本记录
- 可回放

建议统一状态流：

`queued -> syncing -> matched -> fetched -> parsed -> enriched -> delivered -> indexed`

## 9. 对外接口策略

优先级顺序：

1. REST API
2. Webhook
3. Skill
4. SDK

MCP 不是第一阶段主接口。如果未来需要，也应作为现有 API 的薄适配层。

## 10. 前端架构

前端不承担核心业务逻辑。

边界建议：

- `frontend/`：页面、交互、SSR、后台
- `backend/`：业务规则、API、记账
- `workers/`：抓取、解析、摘要、分发

前端框架和库选择见 [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)。

## 11. 开源边界

Scivly 建议走 open-core。

简化版边界：

### 公开

- Web 前端代码
- API 代码
- worker / pipeline 框架
- skill / SDK
- 数据库 schema
- 本地开发与部署模板

### 不公开

- 生产摘要数据
- 用户行为数据
- 托管版运营后台中的内部配置
- 生产 prompt 调优细节
- 付费用户的私有资源库

完整说明见 [OPEN_SOURCE_SCOPE.md](./OPEN_SOURCE_SCOPE.md)。

## 12. 推荐部署方式

当前建议：

- `frontend/` 部署到 Vercel
- `backend/` 和 `workers/` 独立部署
- PDF / 图片可以放到 R2

这样能兼顾：

- Next.js 的部署便利
- Python worker 的稳定运行
- 存储成本控制

## 13. 近期交付顺序

1. 搭建仓库骨架和文档结构
2. 完成用户 / workspace / plan / usage 基础模型
3. 接入 arXiv 同步和规则匹配
4. 跑通摘要、图片和 digest
5. 加入通知渠道和 chat
6. 暴露 API 与 skill 集成

## 14. 文档关系

- [ARCHITECTURE.md](./ARCHITECTURE.md)：主架构文档
- [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)：前端选型
- [OPEN_SOURCE_SCOPE.md](./OPEN_SOURCE_SCOPE.md)：开源边界
- [PIPELINE_PATTERN.md](./PIPELINE_PATTERN.md)：流水线模式
- [SCIVLY_PLAN.md](./SCIVLY_PLAN.md)：产品/平台方案草稿
