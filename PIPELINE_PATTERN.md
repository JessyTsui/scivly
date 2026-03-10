# Pipeline Pattern

Scivly 的论文处理链建议统一采用 `Step Pipeline with Shared Context`。

这个模式和 `/Users/jessytsui/cerul/repo/PIPELINE_PATTERN.md` 的方向一致，但这里按论文平台场景收敛。

## 1. 为什么需要这个模式

Scivly 的核心不是一个单点接口，而是一条长链路：

- 拉取 arXiv
- 匹配规则
- 下载 PDF
- 抽正文
- 抽图片
- 生成摘要
- 生成 digest
- 分发
- 写入检索索引

如果这条链路没有统一模式，后面非常容易变成一堆不可重试、不可回放的脚本。

## 2. 推荐模式

### 2.1 Pipeline Step

每个步骤都拆成独立 step：

- `preprocess(ctx)`
- `process()`
- `postprocess(ctx)`

### 2.2 Shared Context

所有 step 共享一个上下文对象，里面至少包含：

- source run 信息
- workspace 信息
- paper metadata
- PDF 路径
- 抽取文本
- 图片资产
- LLM 输出
- 错误信息

### 2.3 Declarative Steps

一条 pipeline 只是一组有序 step：

```text
FetchMetadataStep
MatchRulesStep
DownloadPdfStep
ParsePdfStep
ExtractFiguresStep
EnrichWithLlmStep
BuildDigestItemStep
DeliverStep
IndexStep
```

### 2.4 Idempotency

每个 step 都能识别：

- 已完成
- 是否可跳过
- 是否需要重试

## 3. 这样设计的好处

- 可读
- 可测试
- 可重试
- 可扩展
- 可回放
- 易于记录成本

## 4. 推荐目录

```text
workers/
  common/
    pipeline/
  arxiv/
    steps/
    context.py
    pipeline.py
  digest/
    steps/
    context.py
    pipeline.py
```

## 5. Scivly 中的两类 pipeline

### 5.1 Ingestion Pipeline

负责论文入库：

- 拉取元数据
- 匹配兴趣规则
- 下载 PDF
- 抽取正文和图片
- 生成结构化摘要

### 5.2 Delivery Pipeline

负责分发：

- 聚合 digest
- 渲染渠道内容
- 调用 Email / Telegram / Discord adapter
- 记录发送结果

## 6. 基本原则

1. 一个 step 只做一件事
2. 不把业务规则写死在 step 框架里
3. 所有外部调用都要有超时和重试
4. 所有状态都要持久化
5. 所有成本都要能记账
