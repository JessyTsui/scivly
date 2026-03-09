# Contributing to Scivly

Thanks for your interest in contributing.

Scivly is still in an early bootstrap phase. The main goal right now is to keep the repository easy to evolve while establishing clear contribution boundaries.

## Before You Start

Please keep these points in mind:

- public repository content should be written in English
- code, comments, commit messages, API payloads, and public-facing docs should be written in English
- internal strategy notes, private prompts, evaluation assets, and user data do not belong in this repository
- major architectural changes should be discussed before implementation

## Development Scope

Scivly is a platform product. Contributions should fit one of these areas:

- `frontend/`: landing pages, public library, user workspace, admin UI
- `backend/`: auth context, paper APIs, usage tracking, billing hooks
- `workers/`: source sync, PDF processing, summary generation, delivery pipelines
- `db/`: migrations and public-safe seed data
- `skills/`: installable agent skill surface

Please do not introduce a second primary stack or duplicate business logic across multiple surfaces.

## Repository Structure

```text
frontend/     Next.js application
backend/      FastAPI service and backend modules
workers/      Paper processing and delivery workers
docs/         Public project docs
db/           Migrations and public-safe seeds
skills/       Installable agent skills
config/       Public-safe config defaults
scripts/      Local scripts and bootstrap helpers
```

## Branches

Use `main` as the source branch for new work.

Recommended naming:

- `feature/...`
- `fix/...`
- `docs/...`
- `chore/...`
- `refactor/...`

Agent-created branches may use the `codex/` prefix.

## Commits

Write commit messages in short, imperative English.

Examples:

- `Add initial worker skeleton`
- `Document open-core scope`
- `Create config templates`

Try to keep each commit focused on one logical concern.

## Pull Requests

Please keep PRs:

- focused
- reviewable
- limited to one main objective

PRs should include:

- a short summary
- affected directories
- any new env vars or config changes
- testing status
- screenshots for UI changes when relevant
- request/response examples for API changes when relevant

If tests are missing, say so explicitly.

## Security and Sensitive Material

Do not commit:

- secrets
- `.env` files
- production exports
- private prompts
- user data
- internal evaluation sets
- internal fundraising or strategy materials

Public-safe runtime defaults belong in `config/`. Secrets belong in `.env` or deployment platform env vars.

## Code Style

- Python: `snake_case`, 4-space indentation
- TypeScript / JSON / YAML: 2-space indentation
- React components: `PascalCase`
- keep business logic out of UI pages when possible
- keep media-heavy and batch processing inside `workers/`, not API handlers

## Testing

There is no repo-wide test command yet.

When adding real modules, include tests alongside them whenever practical:

- Python tests: `test_*.py`
- web tests: `*.test.ts` or `*.test.tsx`

Prioritize coverage for:

- request validation
- usage accounting
- pipeline step idempotency
- authentication paths
- retrieval helpers

## License

By contributing, you agree that your contributions will be licensed under the repository's [Apache 2.0](./LICENSE) license.

