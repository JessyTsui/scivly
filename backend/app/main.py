from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import close_engine, run_migrations
from app.middleware import AuthContextMiddleware, register_exception_handlers
from app.routers import ROUTERS


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.run_migrations_on_startup:
        await run_migrations()
    app.state.started = True
    yield
    app.state.started = False
    await close_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="FastAPI service for the Scivly paper intelligence platform.",
        lifespan=lifespan,
        openapi_tags=[
            {"name": "Health", "description": "Liveness and readiness checks."},
            {"name": "Public Papers", "description": "Public library browsing and search endpoints."},
            {"name": "Auth", "description": "Authentication and session context."},
            {"name": "Workspaces", "description": "Workspace CRUD endpoints."},
            {"name": "Interests", "description": "Topic profiles and author watchlists."},
            {"name": "Papers", "description": "Paper search, detail, and scoring endpoints."},
            {"name": "Digests", "description": "Digest preview and schedule management."},
            {"name": "Chat", "description": "Paper and digest chat sessions."},
            {"name": "Webhooks", "description": "Webhook configuration endpoints."},
            {"name": "API Keys", "description": "Developer API key management."},
            {"name": "Billing", "description": "Stripe subscriptions, checkout, portal, and usage limits."},
            {"name": "Usage", "description": "Workspace usage and billing summaries."},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AuthContextMiddleware)
    register_exception_handlers(app)

    for router in ROUTERS:
        app.include_router(router)

    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    # Default dev port is 8100 to avoid conflicts with other local projects.
    # Override with SCIVLY_API_PORT if a different backend port is needed.
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
    )
