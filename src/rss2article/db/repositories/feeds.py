from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from rss2article.db.models import FeedORM


async def get_or_create_feed(session: AsyncSession, url: str) -> FeedORM:
    stmt = (
        insert(FeedORM)
        .values(url=url)
        .on_conflict_do_nothing(index_elements=[FeedORM.url])
        .returning(FeedORM.id)
    )
    inserted_id = await session.scalar(stmt)

    if inserted_id is not None:
        return await session.get(FeedORM, inserted_id)

    existing = await session.scalar(select(FeedORM).where(FeedORM.url == url))
    if existing is None:
        raise RuntimeError("Feed get_or_create failed unexpectedly")
    return existing
