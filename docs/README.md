# Docs

这个目录用于放 Scivly 的公共文档。

建议布局：

- `architecture/`：公开架构说明
- `api/`：API 文档
- `product/`：产品说明和用例
- `runbooks/`：部署、运维、值班、排障

Current public-safe product docs:

- [`product/paper-triage-scoring.md`](./product/paper-triage-scoring.md): metadata-first scoring,
  rerank, and escalation design for the arXiv pipeline
- [`../config/reference/README.md`](../config/reference/README.md): versioned scoring defaults and
  editable institution and lab dictionaries

不要把这些内容放进这里：

- 生产 prompt 细节
- 付费用户数据
- 内部运营策略
- 私有评测集
