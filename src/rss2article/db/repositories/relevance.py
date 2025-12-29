from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rss2article.db.models import FeedItemORM, FeedORM, RelevanceORM


async def get_unclassified_feed_entry_ids_by_feed_url(
    session: AsyncSession,
    feed_url: str,
) -> list[int]:

    stmt = (
        select(FeedItemORM.entry_id)
        .join(FeedORM, FeedORM.id == FeedItemORM.feed_id)
        .outerjoin(RelevanceORM, RelevanceORM.feed_item_id == FeedItemORM.id)
        .where(FeedORM.url == feed_url)
        .where(RelevanceORM.id.is_(None))
        .order_by(FeedItemORM.published_at.asc())
    )

    return list(await session.scalars(stmt))
