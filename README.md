# Scivly

<div align="center">
  <p>
    <img alt="Status" src="https://img.shields.io/badge/status-bootstrap-b7791f">
    <img alt="Open Core" src="https://img.shields.io/badge/model-open--core-0f766e">
    <img alt="AI Agent" src="https://img.shields.io/badge/category-AI%20Agent-111827">
    <img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-1d4ed8">
  </p>
  <h3>Open-source AI research agent for personal paper tracking and daily digests.</h3>
  <p>
    Subscribe to papers, authors, and topics, generate translated summaries and figure highlights,
    and keep up with research through a cleaner personal workflow.
  </p>
</div>

## Overview

Scivly is being built as an open-source AI research agent for individuals who want a faster way to
follow papers, understand what matters, and keep up with research without stitching together a pile
of feeds, PDFs, translation tools, and notes.

The core loop is simple: subscribe to papers, authors, or topics you care about, let an agentic
pipeline monitor new literature, get translated summaries and figure highlights in a daily digest,
and ask follow-up questions when something is worth a deeper read.

## Current Product Focus

- Personal paper subscriptions for topics, authors, and recurring interests
- Agentic paper monitoring and triage on top of incoming literature
- Translated summaries and figure-first highlights for faster scanning
- Daily digests and alerts for individual users
- Follow-up questions on top of paper context and prior activity

## Current Status

This repository is still in the bootstrap phase.

What exists today:

- project documentation and platform scope
- initial repository skeleton for frontend, backend, workers, docs, database, config, scripts, and skills
- public-safe config templates and open-source support files

Current emphasis:

- the public positioning is currently individual-first rather than team-first
- the strongest current value is the product direction and open-source foundation

What is not in the repository yet:

- production data
- private prompt tuning and ranking parameters
- full production pipeline implementations
- billing internals
- deployed service configuration

## Repository Layout

```text
frontend/     Next.js application
backend/      FastAPI service and backend modules
workers/      Paper processing and delivery workers
docs/         Public-safe architecture, API, product, and runbook docs
db/           Migrations and public-safe seed data
skills/       Installable agent skills
config/       Public-safe config defaults and templates
scripts/      Bootstrap and local utility scripts
```

## Core Docs

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SCIVLY_PLAN.md](./SCIVLY_PLAN.md)
- [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)
- [OPEN_SOURCE_SCOPE.md](./OPEN_SOURCE_SCOPE.md)
- [PIPELINE_PATTERN.md](./PIPELINE_PATTERN.md)

## Open Source Direction

Scivly is intended to follow an open-core direction.

Public in this repository:

- application code
- worker and pipeline framework
- installable skill surface
- configuration templates
- self-hostable project skeleton

Kept outside the public repository:

- production user data
- hosted service operations
- tuned production prompts and ranking parameters
- internal evaluation assets

## Why This Project Exists

Individual researchers and curious builders already have more papers than attention. The actual
bottleneck is not access, it is triage, context, and follow-through. Scivly exists to turn raw
literature flow into an AI-assisted personal workflow that helps one person notice important papers
faster and spend less time on repetitive review work.

## Roadmap Themes

- Build the public scaffold for the application, services, workers, and database
- Ship the first agentic paper ingestion and summarization pipeline
- Add digest delivery and follow-up question workflows
- Expose a clean self-hostable foundation for contributors and early adopters

## Suggested GitHub Description

`Open-source AI research agent for subscribing to papers, generating summaries, and shipping daily digests.`

## Suggested Repository Topics

`ai-agent` `open-source` `research-assistant` `paper-tracking` `llm`
`summarization` `translation` `nextjs` `fastapi` `open-core`

## Community

- [Contributing Guide](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)

## Star History

<p align="center">
  <a href="https://www.star-history.com/#JessyTsui/scivly&Date">
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=JessyTsui/scivly&type=Date" />
  </a>
</p>

## License

Scivly is licensed under [Apache 2.0](./LICENSE).
