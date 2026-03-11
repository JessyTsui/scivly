from app.routers import (
    api_keys,
    auth,
    billing,
    chat,
    digests,
    health,
    interests,
    papers,
    public_papers,
    usage,
    webhooks,
    workspaces,
)

ROUTERS = (
    health.router,
    public_papers.router,
    auth.router,
    workspaces.router,
    interests.router,
    papers.router,
    digests.router,
    chat.router,
    webhooks.router,
    api_keys.router,
    billing.router,
    usage.router,
)

__all__ = ["ROUTERS"]
