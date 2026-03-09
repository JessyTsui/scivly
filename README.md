# Scivly

Personalized paper intelligence platform for researchers and technical teams.

Scivly is being designed as a multi-tenant platform that helps users track papers they care about, generate translated summaries and figure highlights, receive daily digests, and ask follow-up questions inside the product or through external integrations.

## Current Status

This repository is still in the bootstrap phase.

What exists today:

- project documentation and platform scope
- initial repository skeleton for frontend, backend, workers, docs, database, config, scripts, and skills
- public-safe config templates and open-source support files

What is not in the repository yet:

- production data
- private prompt tuning
- real pipeline implementations
- billing logic
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

## Open Source Scope

Scivly is intended to follow an open-core direction.

Public in this repository:

- application code
- worker and pipeline framework
- installable skill surface
- config templates
- self-hostable project skeleton

Not public:

- production user data
- hosted service operations
- tuned production prompts and ranking parameters
- internal evaluation assets

## Community

- [Contributing Guide](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)

## License

This repository is licensed under [Apache 2.0](./LICENSE).
