from app.routers import api_keys, auth, chat, digests, health, interests, papers, usage, webhooks, workspaces

ROUTERS = (
    health.router,
    auth.router,
    workspaces.router,
    interests.router,
    papers.router,
    digests.router,
    chat.router,
    webhooks.router,
    api_keys.router,
    usage.router,
)

__all__ = ["ROUTERS"]
