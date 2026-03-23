"""Seed initial data.

Usage:
  python -m scripts.seed
"""

import asyncio

from app.db.session import async_session
from app.db.init_db import init_db


def main() -> None:
    async def _run():
        session = async_session()
        try:
            await init_db(session)
        finally:
            await session.close()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
