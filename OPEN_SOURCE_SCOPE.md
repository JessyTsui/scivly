# Scivly Open Source Scope

本文件定义 Scivly 的开源边界，避免后续在“哪些东西应该公开、哪些应该只存在于托管版”上反复摇摆。

## 1. 推荐策略

Scivly 适合走 `open-core`。

原因很简单：

- 代码本身适合开源
- 自部署对这类基础设施产品有吸引力
- 真正的长期壁垒不会是仓库代码，而是数据、调优和运营系统

## 2. 建议公开的内容

以下内容建议直接在公开仓库里维护：

### 2.1 应用代码

- `frontend/`
- `backend/`
- `workers/`
- `skills/`

### 2.2 工程基础设施

- 数据库 schema 和 migration
- 配置模板
- 本地开发脚本
- Docker / deployment 模板
- CI 配置

### 2.3 公共文档

- 架构文档
- API 文档
- 自部署文档
- 贡献文档
- 安全文档

### 2.4 替换式能力

- prompt 框架
- provider adapter
- source adapter
- delivery adapter

这些东西公开后，反而更有利于形成生态。

## 3. 不建议公开的内容

以下内容不应进入公开仓库：

### 3.1 生产数据

- 付费用户的订阅配置
- 用户历史行为数据
- 用户私有 digest
- 生产环境生成的论文摘要库

### 3.2 生产优化资产

- 调优后的生产 prompt 细节
- 生产 ranking 参数
- 质量评估集
- 线上 A/B 配置

### 3.3 托管运营资产

- 商业报表
- 风控规则
- 客服/运营工具内部逻辑
- 私有公共资源库运营数据

## 4. 托管版增强能力

如果未来 Scivly 同时提供官方托管服务，建议把下面这些作为托管增强，而不是仓库默认承诺：

- 官方公共精选资源库
- 托管版账单后台
- 内部运营面板
- 更高质量模型路由
- 团队版高级能力

## 5. 对自部署用户应该公开到什么程度

开源项目最怕“看起来开源，实际不可运行”。

所以自部署至少应该能拿到：

- 可运行的前后端代码
- 基础 worker
- 可替换的大模型 provider 配置
- 一个通知渠道的示例
- `.env.example`
- migration
- 最小启动文档

换句话说，开源版必须能跑最小闭环，而不是只放一个壳子。

## 6. 真正的壁垒在哪里

Scivly 长期更可能积累价值的地方是：

1. 高质量的公开论文结构化索引库
2. 用户交互行为数据
3. 命中质量和排序调优经验
4. 稳定的多渠道分发与运营体系
5. 围绕论文问答和摘要的持续迭代

这些都不是别人 `git clone` 一下就能复制的。

## 7. 对外表达建议

当对外介绍时，建议统一成下面这种说法：

> Scivly is open-core. The platform code, pipeline framework, and self-hostable stack are public. Hosted data, tuned production prompts, and managed service operations are not.

## 8. 近期建议

如果你准备认真开源，下一步应该补这些文件：

- `LICENSE`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.env.example`

这样仓库的公开姿态会完整很多。
