# Config Workspace

This directory holds versioned, public-safe runtime config for Scivly.

Rules:

- commit only values that are safe to publish
- keep secrets in the root `.env` file or deployment platform env vars
- prefer structured config files here over growing `.env` with non-secret tuning knobs
- treat env vars as overrides, not the primary store for application behavior

Recommended files:

- `base.yaml` for shared defaults
- `development.yaml` for local-safe overrides
- `production.yaml` for public production-safe overrides

Consumption model:

- backend and workers load `base.yaml` plus one environment file plus env overrides
- frontend server code should read only a whitelisted public subset
- browser code must not read raw files from this directory directly

Do not put secrets here:

- API keys
- database passwords
- auth secrets
- webhook signing secrets
- private tuned prompt contents

