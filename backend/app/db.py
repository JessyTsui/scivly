from __future__ import annotations

from collections.abc import AsyncIterator, Iterable
from pathlib import Path

import asyncpg
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

DEFAULT_POSTGRES_USER = "postgres"
REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "db" / "migrations"
SEEDS_DIR = REPO_ROOT / "db" / "seeds"

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def normalize_database_url(database_url: str, *, driver: str | None = None) -> str:
    url = make_url(database_url)
    backend = url.get_backend_name()

    if backend not in {"postgres", "postgresql"}:
        return database_url

    target_driver = "postgresql"
    if driver == "asyncpg":
        target_driver = "postgresql+asyncpg"
    elif "+" in url.drivername:
        target_driver = url.drivername

    if url.username is None:
        url = url.set(username=DEFAULT_POSTGRES_USER)

    return url.set(drivername=target_driver).render_as_string(hide_password=False)


def get_sqlalchemy_database_url() -> str:
    return normalize_database_url(get_settings().database_url, driver="asyncpg")


def get_asyncpg_database_url() -> str:
    return normalize_database_url(get_settings().database_url, driver="postgresql")


def get_engine() -> AsyncEngine:
    global _engine, _session_factory

    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            get_sqlalchemy_database_url(),
            echo=settings.database_echo,
            pool_pre_ping=True,
        )
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory

    if _session_factory is None:
        get_engine()

    assert _session_factory is not None
    return _session_factory


async def get_db_session() -> AsyncIterator[AsyncSession]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def ping_database() -> None:
    engine = get_engine()
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def get_database_status() -> str:
    try:
        await ping_database()
    except Exception:
        return "unavailable"
    return "ok"


def list_sql_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.sql") if path.is_file())


async def execute_sql_files(paths: Iterable[Path]) -> list[str]:
    connection = await asyncpg.connect(get_asyncpg_database_url())
    executed: list[str] = []
    try:
        for path in paths:
            await connection.execute(path.read_text(encoding="utf-8"))
            executed.append(path.name)
    finally:
        await connection.close()

    return executed


async def run_migrations() -> list[str]:
    return await execute_sql_files(list_sql_files(MIGRATIONS_DIR))


async def run_seeds() -> list[str]:
    return await execute_sql_files(list_sql_files(SEEDS_DIR))


async def truncate_public_tables() -> None:
    connection = await asyncpg.connect(get_asyncpg_database_url())
    try:
        table_rows = await connection.fetch(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename ASC
            """
        )
        if not table_rows:
            return

        table_list = ", ".join(f'public."{row["tablename"]}"' for row in table_rows)
        await connection.execute(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE")
    finally:
        await connection.close()


async def close_engine() -> None:
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()

    _engine = None
    _session_factory = None


def reset_database_state() -> None:
    global _engine, _session_factory
    _engine = None
    _session_factory = None
