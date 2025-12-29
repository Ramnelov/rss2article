from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from rss2article.db.models import FeedItemORM, FeedORM, RelevanceORM

log = logging.getLogger(__name__)


async def get_unclassified_feed_entry_ids_by_feed_url(
    session: AsyncSession,
    feed_url: str,
) -> list[str]:

    stmt = (
        select(FeedItemORM.entry_id)
        .join(FeedORM, FeedORM.id == FeedItemORM.feed_id)
        .outerjoin(RelevanceORM, RelevanceORM.feed_item_id == FeedItemORM.id)
        .where(FeedORM.url == feed_url)
        .where(RelevanceORM.id.is_(None))
        .order_by(FeedItemORM.published_at.asc())
    )

    return list(await session.scalars(stmt))


async def upsert_relevance(
    session: AsyncSession,
    feed_item_id: int,
    relevant: bool,
    why: str,
) -> None:

    stmt = (
        insert(RelevanceORM)
        .values(
            feed_item_id=feed_item_id,
            relevant=relevant,
            why=why,
        )
        .on_conflict_do_update(
            index_elements=["feed_item_id"],
            set_={
                "relevant": relevant,
                "why": why,
            },
        )
    )
    await session.execute(stmt)
