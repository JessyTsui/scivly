from app.routers import billing, api_keys, auth, chat, digests, health, interests, papers, usage, webhooks, workspaces

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
    billing.router,
    usage.router,
)

__all__ = ["ROUTERS"]
