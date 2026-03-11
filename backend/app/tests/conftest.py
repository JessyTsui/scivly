import asyncio
import os
from collections.abc import Generator
import sys
from pathlib import Path

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


def _bootstrap_database() -> None:
    asyncio.run(run_migrations())
    asyncio.run(truncate_public_tables())
    asyncio.run(run_seeds())
    asyncio.run(close_engine())
    reset_database_state()
    get_settings.cache_clear()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    _bootstrap_database()
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
    asyncio.run(close_engine())
    reset_database_state()
    get_settings.cache_clear()
