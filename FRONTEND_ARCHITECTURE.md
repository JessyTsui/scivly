# Scivly 前端架构选择

## 1. 最终结论

Scivly 的前端我建议直接选：

- `Next.js App Router`
- `TypeScript`
- `Tailwind CSS v4`
- `shadcn/ui`
- `Radix Primitives`
- `TanStack Query`
- `TanStack Table`
- `React Hook Form`
- `Zod`
- `Apache ECharts`
- `Lucide`

如果你接受更快上线、并且能接受一部分 SaaS 依赖，鉴权和订阅建议优先选：

- `Clerk`

如果你更在意完全自托管和开源控制权，则替代方案是：

- `Better Auth + Stripe`

## 2. 为什么选 Next.js

Scivly 不是一个单纯后台，而是一个同时包含下面四类页面的平台：

- 官网和价格页
- 公共资源库
- 登录后的用户工作区
- 运营后台

对这种产品，`Next.js App Router` 是最合适的单一前端框架，原因有四个：

### 2.1 一个框架覆盖四种页面类型

Next.js 适合：

- SEO 页
- SSR 内容页
- 高交互 dashboard
- 后台管理页

Scivly 不需要为了官网和后台拆两套前端。

### 2.2 App Router 适合平台信息架构

Next.js 官方文档当前仍将 App Router 作为基于 React 新特性的主路由体系，支持 Server Components、Suspense 和 Server Functions。

这对 Scivly 很有用，因为：

- 公共资源库和论文详情适合 SSR
- Dashboard 可以做流式加载
- 路由分层适合 `marketing / app / admin / docs`

### 2.3 对平台功能支持完整

Next.js 在同一代码库里就能处理：

- 登录后的 session 页面
- 支付成功 / 失败页
- SEO 页面
- Webhook 回调壳层
- OpenGraph、sitemap、metadata

### 2.4 生态成熟

Scivly 需要的几乎所有前端基础能力，Next.js 生态都有成熟方案：

- auth
- billing
- forms
- table
- chart
- design system

## 3. 为什么不是其他方案

### 3.1 不是 React + Vite

Vite 很好，但 Scivly 需要：

- SSR / SEO
- 公共资源库
- 营销站
- 用户端和后台共存

如果用 Vite，你还要额外拼很多平台能力。

### 3.2 不是 Nuxt

Nuxt 也能做，但你后端主栈已经更偏 Python + React 生态，继续往 React/Next 走，后面接 shadcn、Clerk、TanStack、文档和招聘都更顺。

### 3.3 不是分两个前端

不建议一开始拆成：

- 一个官网
- 一个 dashboard

因为：

- 设计系统会复制
- 鉴权边界会复杂
- 公共资源库和用户库容易分裂

一期更合理的是一个 `apps/web`，内部用 route groups 切页面域。

## 4. 前端项目结构建议

```text
apps/
  web/
    app/
      (marketing)/
      (library)/
      (app)/
      (admin)/
      api/
    components/
    lib/
    styles/
packages/
  ui/
  config/
  types/
```

推荐的路由分区：

- `(marketing)`：首页、价格页、介绍页
- `(library)`：公共资源库、公开论文页
- `(app)`：用户工作区
- `(admin)`：运营后台

这样做的好处是：

- 统一设计系统
- 统一 session
- 统一监控
- 统一埋点

## 5. UI 基础栈

## 5.1 样式

推荐：

- `Tailwind CSS v4`

原因：

- 当前官方已经把 v4 作为简化安装和零配置方向推进
- 很适合快速建立平台化 design system
- 对 dashboard、表格、卡片、响应式支持成熟

## 5.2 组件层

推荐：

- `shadcn/ui`
- `Radix Primitives`

这两层组合适合 Scivly，因为：

- `shadcn/ui` 不把你锁进黑盒组件库
- `Radix` 强调可访问性、可定制和无样式 primitive
- 后面无论用户端还是后台，都能共用同一个组件系统

## 5.3 图标

推荐：

- `Lucide`

原因：

- 简洁
- 一致性好
- 很适合 SaaS 和后台风格

## 6. 数据获取和状态管理

推荐：

- 首选 `Server Components`
- 高交互数据页使用 `TanStack Query`

策略不要搞反：

- 首屏列表、公共详情页尽量走服务端渲染
- 过滤、分页、后台操作、轮询状态用 Query

这样可以减少客户端状态复杂度。

不要一开始就上 Redux。

Scivly 这种产品真正复杂的是服务端状态，不是前端全局状态。

## 7. 表格、图表、表单

### 7.1 表格

推荐：

- `TanStack Table`

原因：

- 无头设计，适合自定义平台 UI
- 很适合 jobs、usage、billing、papers 这种数据密集表格

### 7.2 图表

推荐：

- `Apache ECharts`

原因：

- 官方支持 20+ 图表类型
- 适合运营后台、趋势图、配额消耗、来源分析
- 可访问性支持也比很多轻量图表库更完整

### 7.3 表单

推荐：

- `React Hook Form`
- `Zod`

原因：

- React Hook Form 适合性能敏感表单
- Zod 适合把前端验证和 TypeScript schema 对齐
- 很适合兴趣配置、通知渠道设置、账单资料等页面

## 8. 鉴权和订阅

这里给你两个选项。

## 8.1 默认推荐：Clerk

如果目标是尽快把平台上线，我建议优先用 `Clerk`。

理由：

- 官方文档已有 Organizations，多租户路径清楚
- 官方支持 Billing
- 官方支持 Next.js，也有 Python SDK 可供后端使用
- 对登录、组织、权限、订阅的接入速度非常快

适合你当前阶段，因为你明确要平台优先，而不是慢慢自己补这些基础设施。

### Clerk 的代价

- 有平台依赖
- 自定义边界不如完全自建自由
- 当前官方 Billing 仍有一些限制，例如文档里明确提到 custom pricing 还不完整，税务 / VAT 能力也不是全覆盖

所以如果你预计很快做复杂企业销售和特殊计费，后面可能还是要转回自建 billing。

## 8.2 开源控制优先：Better Auth + Stripe

如果你更重视开源、自托管和长期控制权，可以选：

- `Better Auth`
- `Stripe`

原因：

- Better Auth 官方已有 organization 插件
- 更接近“自己的 auth 栈”
- 对开源用户和自部署用户更友好

代价也很清楚：

- 你自己要承担更多集成和维护工作
- 你要自己把订阅、配额、Webhook、后台逻辑真正做完

## 8.3 我的结论

如果 Scivly 的目标是尽快跑出平台闭环：

- 先上 `Clerk`

如果 Scivly 的目标是更纯的开源平台和可自托管控制：

- 选 `Better Auth + Stripe`

以你当前的描述，我更偏向：

- 托管版默认 `Clerk`
- 自部署版后续支持 `Better Auth`

## 9. 设计系统方向

Scivly 不应该做成普通 SaaS 仪表盘视觉。

建议视觉方向：

- 风格：`editorial research + data workspace`
- 气质：专业、安静、可信，不花哨
- 关键词：科学出版感、情报面板、数据工作台

### 推荐字体

- 标题：`Space Grotesk`
- 正文：`IBM Plex Sans`
- 等宽：`IBM Plex Mono`

### 推荐主色

- 背景：暖白或冷灰，不要纯白
- 主色：深蓝灰
- 强调色：青蓝或橙黄，只占少量

不要走默认紫色 SaaS 风格。

## 10. 主要页面建议

## 10.1 用户端

- Dashboard
- Interests
- Digests
- Papers
- Paper Chat
- Integrations
- Usage
- Billing
- API Keys

## 10.2 公共站点

- Home
- Pricing
- Public Library
- Public Paper
- Docs

## 10.3 后台

- Overview
- Users
- Workspaces
- Plans
- Usage Ledger
- Jobs
- Deliveries
- Public Content

## 11. 前后端边界

前端不要承担核心业务。

建议边界：

- `Next.js` 负责页面、会话、SSR、表单和交互
- `FastAPI` 负责业务规则、任务触发、计费记录、对外 API
- `worker` 负责抓取、解析、摘要、推送

即使 Next.js 支持 Route Handlers，也不要把论文处理核心逻辑堆进前端工程。

## 12. 一期落地建议

如果现在就开始搭前端，一期我建议直接这样定：

### 必选

- `Next.js App Router`
- `TypeScript`
- `Tailwind CSS v4`
- `shadcn/ui`
- `Radix`
- `TanStack Query`
- `TanStack Table`
- `React Hook Form`
- `Zod`
- `Lucide`

### 视图层组织

- 一个 `apps/web`
- 四个 route groups：`marketing / library / app / admin`
- 一个共享 `packages/ui`

### 鉴权和订阅

- 快速商业化：`Clerk`
- 自托管优先：`Better Auth + Stripe`

## 13. 我建议的最终技术选择

如果现在让我直接拍板，我会这样选：

- 前端框架：`Next.js App Router`
- 样式系统：`Tailwind CSS v4`
- 组件体系：`shadcn/ui + Radix`
- 数据状态：`Server Components + TanStack Query`
- 表格：`TanStack Table`
- 图表：`Apache ECharts`
- 表单校验：`React Hook Form + Zod`
- 图标：`Lucide`
- 鉴权和订阅：`Clerk`

这套组合最适合你现在这条路线：

- 一开始就做平台
- 同时要有官网、公共资源库、用户端、后台
- 还要尽快把订阅、额度、账单、集成做出来
