from __future__ import annotations

import argparse
import asyncio

from app.db import ping_database, run_migrations, run_seeds


async def _run(command: str) -> None:
    if command == "check":
        await ping_database()
        print("Database connection OK")
        return

    if command == "migrate":
        executed = await run_migrations()
        print(f"Applied migrations: {', '.join(executed) if executed else 'none'}")
        return

    if command == "seed":
        executed = await run_seeds()
        print(f"Applied seeds: {', '.join(executed) if executed else 'none'}")
        return

    if command == "bootstrap":
        migrations = await run_migrations()
        seeds = await run_seeds()
        print(f"Applied migrations: {', '.join(migrations) if migrations else 'none'}")
        print(f"Applied seeds: {', '.join(seeds) if seeds else 'none'}")
        return

    raise ValueError(f"Unsupported command: {command}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scivly database admin tasks")
    parser.add_argument(
        "command",
        choices=["check", "migrate", "seed", "bootstrap"],
        help="Database operation to run.",
    )
    args = parser.parse_args()
    asyncio.run(_run(args.command))


if __name__ == "__main__":
    main()
