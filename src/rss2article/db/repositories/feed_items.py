from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from rss2article.db.models import FeedItemORM
from rss2article.domain.models import FeedItem


async def upsert_feed_item(session: AsyncSession, feed_id: int, item: FeedItem) -> None:
    stmt = (
        insert(FeedItemORM)
        .values(
            feed_id=feed_id,
            entry_id=item.entry_id,
            link=item.link,
            title=item.title,
            author=item.author,
            published_at=item.published_at,
            content_text=item.content_text,
        )
        .on_conflict_do_update(
            index_elements=["feed_id", "entry_id"],
            set_={
                "link": item.link,
                "title": item.title,
                "author": item.author,
                "published_at": item.published_at,
                "content_text": item.content_text,
            },
        )
    )
    await session.execute(stmt)


async def get_feed_items_by_entry_ids(
    session: AsyncSession,
    entry_ids: list[str],
) -> list[FeedItemORM]:
    if not entry_ids:
        return []

    stmt = (
        select(FeedItemORM)
        .where(FeedItemORM.entry_id.in_(entry_ids))
        .order_by(FeedItemORM.published_at.asc())
    )
    return list((await session.scalars(stmt)).all())
