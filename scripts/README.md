# Scripts Workspace

This directory is reserved for local automation and bootstrap scripts.

Use it for:

- database initialization helpers
- local development utilities
- repeatable maintenance tasks that belong to the repository
- shared entrypoints such as `scripts/dev.sh`

Prefer checked-in scripts over one-off terminal snippets when the task will be repeated.

## Available entrypoints

- `scripts/dev.sh` for local development startup
- `scripts/db.sh` for database checks, migrations, seeds, and bootstrap helpers
