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
    Subscribe to papers and topics, generate translated summaries and figure highlights,
    and get a cleaner personal research workflow.
  </p>
</div>

## Overview

Scivly is being built as an open-source AI research agent for individuals who want a faster way to
follow papers, understand what matters, and keep up with research without stitching together five
different tools.

The core idea is simple: users subscribe to papers, authors, or topics they care about, an agentic
workflow organizes and summarizes new material, the most useful updates get pushed into a daily digest,
and users can keep asking follow-up questions inside the product.

## Positioning

Scivly sits closer to an AI agent or research copilot than a traditional paper database.

- Not just paper storage: it is meant to help users decide what matters
- Not just summarization: it is meant to power recurring personal research workflows
- Not just a search tool: it is designed around subscriptions, digests, and follow-up questions
- Not just hosted SaaS: the public repo is intended to support an open-source, self-hostable base

## What Scivly Is Meant To Do

- Subscribe to papers, authors, and topics that matter to an individual user
- Run agentic research workflows on top of incoming literature
- Generate translated summaries for faster review across languages
- Extract figure and visual highlights for quick scanning
- Deliver personal daily digests and alerts
- Support follow-up questions on top of paper context and prior activity

## Current Status

This repository is in the bootstrap phase.

What exists today:

- the public project brief and repository metadata
- a defined product direction for an open-core personal research product
- a planned architecture spanning frontend, backend, workers, data, and integrations

What is intentionally not public yet:

- production data
- hosted service operations
- private prompt tuning and ranking parameters
- billing internals
- full production pipeline implementations

What that means in practice:

- the vision and public framing are real
- the repo is still early
- the strongest current value is the product direction and open-source foundation

## Planned Architecture

| Layer | Role |
| --- | --- |
| Frontend | AI-native personal research workspace and paper review experience |
| Backend | API surface, orchestration, auth, and application logic |
| Workers | Agentic ingestion, summarization, enrichment, and delivery pipelines |
| Data | Paper metadata, user subscriptions, preferences, and digest state |
| Integrations | Optional external delivery channels and workflow extensions |

## Open Source Direction

Scivly is intended to follow an open-core model.

Public in this repository:

- application code
- worker and pipeline framework
- configuration templates
- self-hostable project skeleton
- developer tooling and automation surfaces

Kept outside the public repository:

- production user data
- internal evaluation assets
- hosted operational configuration
- tuned production prompts and private ranking logic

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

## Star History

<p align="center">
  <a href="https://www.star-history.com/#JessyTsui/scivly&Date">
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=JessyTsui/scivly&type=Date" />
  </a>
</p>

## License

Scivly is licensed under [Apache 2.0](./LICENSE).
