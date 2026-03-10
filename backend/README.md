# Backend Workspace

This directory is reserved for the Scivly API service.

- framework: FastAPI
- primary concerns: auth context, paper APIs, digest APIs, usage tracking, API keys, and billing hooks
- expected subdirectories: `app/`, `tests/`

Keep PDF-heavy and model-heavy processing out of request handlers. Pipeline execution belongs in `workers/`.

