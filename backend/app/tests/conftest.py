import asyncio
import os
from collections.abc import Callable, Generator
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5432/scivly")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.config import get_settings  # noqa: E402
from app.db import close_engine, reset_database_state, run_migrations, run_seeds, truncate_public_tables  # noqa: E402
from app.main import create_app  # noqa: E402

TEST_AUTH_SECRET = "scivly-test-secret-1234567890-abcdef"


def _database_is_reachable() -> bool:
    import asyncpg  # noqa: F811

    async def _try_connect() -> None:
        conn = await asyncpg.connect(os.environ.get("DATABASE_URL", "postgresql://localhost:5432/scivly"))
        await conn.close()

    try:
        asyncio.run(_try_connect())
        return True
    except (OSError, asyncpg.PostgresError):
        # OSError covers connection refused / host unreachable.
        # PostgresError covers missing database, invalid role, etc.
        return False


def _bootstrap_database() -> None:
    asyncio.run(run_migrations())
    asyncio.run(truncate_public_tables())
    asyncio.run(run_seeds())
    asyncio.run(close_engine())
    reset_database_state()
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def auth_config(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setenv("SCIVLY_AUTH_JWT_SECRET", TEST_AUTH_SECRET)
    monkeypatch.setenv("SCIVLY_AUTH_AUTHORIZED_PARTIES", "http://localhost:3100")
    get_settings.cache_clear()

    try:
        yield
    finally:
        get_settings.cache_clear()


_db_reachable: bool | None = None


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    global _db_reachable
    if _db_reachable is None:
        _db_reachable = _database_is_reachable()
    if not _db_reachable:
        pytest.skip("PostgreSQL is not reachable")
    _bootstrap_database()
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
    asyncio.run(close_engine())
    reset_database_state()
    get_settings.cache_clear()


@pytest.fixture()
def issue_token() -> Callable[..., str]:
    def _issue_token(
        *,
        sub: str = "user_test",
        azp: str = "http://localhost:3100",
        **claims: object,
    ) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": sub,
            "sid": f"sess_{sub}",
            "azp": azp,
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            **claims,
        }
        return jwt.encode(payload, TEST_AUTH_SECRET, algorithm="HS256")

    return _issue_token


@pytest.fixture()
def auth_headers(issue_token: Callable[..., str]) -> Callable[..., dict[str, str]]:
    def _auth_headers(**claims: object) -> dict[str, str]:
        return {"Authorization": f"Bearer {issue_token(**claims)}"}

    return _auth_headers
