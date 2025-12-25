from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine

from rss2article.db import (  # noqa: F401  (ensures models are imported/registered)
    models,
)
from rss2article.db.base import Base


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
